"""Offline upper-bound contract tests. Fixtures do not verify any real provider."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('token_preflight', ROOT / 'scripts/token_preflight.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class TokenPreflightTests(unittest.TestCase):
    def setUp(self):
        self.policy = dict(revision='fixture-1', max_input_tokens=8000,
                           max_output_tokens=1500, max_context_tokens=12000,
                           max_run_tokens=16000, max_calls=3, safety_margin_tokens=512,
                           review_above_tokens=9000,
                           required_scope_ids=['run:fixture', 'project:fixture'])
        self.plan = dict(policy_revision='fixture-1', provider='fixture', model='fixture-model',
                         calls=[dict(id='call-1', full_input_tokens_upper_bound=1000,
                                     generation_tokens_upper_bound=500)])
        self.scopes = [dict(id=s, revision='fixture-budget-1', max_tokens=20000,
                            spent_tokens=1000, reserved_tokens=2000)
                       for s in self.policy['required_scope_ids']]
        self.capability = dict(verified=True, input_bound_verified=True,
                               output_limit_enforced=True, reasoning_covered=True,
                               provider='fixture', model='fixture-model',
                               model_context_tokens=32000, max_generation_tokens=8000)

    def check(self):
        result = guard.assess(self.plan, self.policy, self.scopes, self.capability)
        self.assertFalse(result['dispatch_performed'])
        self.assertFalse(result['dispatch_authorized'])
        self.assertFalse(result['reservation_created'])
        self.assertFalse(result['monetary_cap_enforced'])
        return result

    def test_finite_fixture_has_reserved_generation_and_margin(self):
        result = self.check()
        self.assertEqual(result['decision'], 'within_policy')
        self.assertEqual(result['aggregate_token_upper_bound'], 1500)
        self.assertEqual(result['context_requirements'][0]['tokens'], 2012)

    def test_unknown_or_invalid_policy_is_not_unlimited(self):
        for value in (None, True, -1, 1.5, float('inf')):
            with self.subTest(value=value):
                self.policy['max_input_tokens'] = value
                self.assertEqual(self.check()['decision'], 'blocked')

    def test_context_and_output_require_verified_mechanisms(self):
        for flag in ('verified', 'input_bound_verified', 'output_limit_enforced', 'reasoning_covered'):
            with self.subTest(flag=flag):
                self.capability[flag] = False
                self.assertIn('capability_upper_bound_unverified', self.check()['reason_codes'])
                self.capability[flag] = True

    def test_unknown_input_is_not_estimated_from_bytes(self):
        self.plan['calls'][0]['full_input_tokens_upper_bound'] = None
        result = self.check()
        self.assertIn('call_upper_bound_unknown', result['reason_codes'])
        self.assertIsNone(result['aggregate_token_upper_bound'])

    def test_input_output_and_smaller_model_context_hard_caps(self):
        for field, value, reason in (
            ('max_input_tokens', 999, 'input_hard_cap'),
            ('max_output_tokens', 499, 'output_hard_cap'),
            ('max_context_tokens', 2011, 'context_hard_cap'),
        ):
            with self.subTest(field=field):
                original = self.policy[field]
                self.policy[field] = value
                self.assertIn(reason, self.check()['reason_codes'])
                self.policy[field] = original
        self.capability['model_context_tokens'] = 2011
        self.assertIn('context_hard_cap', self.check()['reason_codes'])

    def test_provider_generation_bound_can_be_smaller(self):
        self.capability['max_generation_tokens'] = 499
        self.assertIn('output_hard_cap', self.check()['reason_codes'])

    def test_review_threshold_does_not_override_hard_caps(self):
        self.policy['review_above_tokens'] = 1499
        self.assertEqual(self.check()['decision'], 'requires_risk_approval')
        self.policy['max_run_tokens'] = 1499
        result = self.check()
        self.assertEqual(result['decision'], 'blocked')
        self.assertIn('run_token_hard_cap', result['reason_codes'])

    def test_all_child_and_retry_calls_consume_the_same_total(self):
        child = copy.deepcopy(self.plan['calls'][0])
        child['id'] = 'child-1'
        retry = copy.deepcopy(child)
        retry['id'] = 'retry-1'
        self.plan['calls'].extend([child, retry])
        self.policy['max_run_tokens'] = 4499
        result = self.check()
        self.assertEqual(result['aggregate_token_upper_bound'], 4500)
        self.assertIn('run_token_hard_cap', result['reason_codes'])
        self.policy['max_calls'] = 2
        self.assertIn('call_count_hard_cap', self.check()['reason_codes'])

    def test_outstanding_unknown_reservation_is_not_released(self):
        self.scopes[1]['max_tokens'] = 4499
        result = self.check()
        self.assertIn('budget_hard_cap:project:fixture', result['reason_codes'])
        self.assertEqual(self.scopes[1]['reserved_tokens'], 2000)

    def test_missing_or_duplicate_parent_budget_is_rejected(self):
        original = copy.deepcopy(self.scopes)
        self.scopes.pop()
        self.assertEqual(self.check()['decision'], 'blocked')
        self.scopes = original + [copy.deepcopy(original[0])]
        self.assertIn('duplicate_budget_scope', self.check()['reason_codes'])

    def test_unknown_usage_is_never_zero(self):
        self.scopes[0]['spent_tokens'] = None
        reasons = self.check()['reason_codes']
        self.assertIn('budget_snapshot_unknown', reasons)
        self.assertNotIn('required_budget_scope_missing', reasons)

    def test_scope_order_does_not_change_admission_or_omit_a_parent(self):
        before = self.check()
        self.scopes.reverse()
        after = self.check()
        self.assertEqual(before['decision'], after['decision'])
        self.assertEqual(before['aggregate_token_upper_bound'], after['aggregate_token_upper_bound'])

    def test_stale_model_or_policy_binding_is_rejected(self):
        self.plan['model'] = 'other-model'
        self.plan['policy_revision'] = 'old-policy'
        reasons = self.check()['reason_codes']
        self.assertIn('model_binding_unknown_or_mismatch', reasons)
        self.assertIn('policy_revision_missing_or_stale', reasons)

    def test_duplicate_calls_and_empty_manifest_are_not_free(self):
        self.plan['calls'] *= 2
        self.assertIn('duplicate_call_identity', self.check()['reason_codes'])
        self.plan['calls'] = []
        self.assertIn('bounded_call_manifest_required', self.check()['reason_codes'])

    def test_assessment_changes_with_plan_budget_or_model(self):
        before = self.check()['assessment_digest']
        self.scopes[0]['reserved_tokens'] += 1
        self.assertNotEqual(before, self.check()['assessment_digest'])
        self.plan['calls'][0]['full_input_tokens_upper_bound'] += 1
        self.assertNotEqual(before, self.check()['assessment_digest'])

    def test_malformed_snapshot_fails_closed(self):
        result = guard.assess({}, {}, None, {})
        self.assertEqual(result['decision'], 'blocked')
        self.assertFalse(result['dispatch_authorized'])

    def test_s02_remains_blocked_without_inference_or_fake_token_count(self):
        result = guard.s02_assessment()
        self.assertTrue(result['package_hashes_match'])
        self.assertEqual(result['execution_status'], 'not_run')
        self.assertEqual(result['assessment']['decision'], 'blocked')
        self.assertIsNone(result['assessment']['aggregate_token_upper_bound'])
        self.assertFalse(result['assessment']['dispatch_performed'])


if __name__ == '__main__':
    unittest.main()

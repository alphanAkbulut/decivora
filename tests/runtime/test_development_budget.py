"""Shared development admission across batches; offline HTTP double only."""
import copy
import unittest

import test_openai_transport as fixtures
from packages.capture.openai_transport import PilotTransport, fingerprint


class DevelopmentBudgetTests(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.PilotTransportTests()
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.manifest = dict(self.fx.manifest, max_http_attempts=200, max_cost_microusd=3000000,
                             budget_scope='decivora-development-2026-10-19-usd3',
                             prior_usage=dict(dispatches=10, http_attempts=20, cost_microusd=24165,
                                              evidence_sha256='a' * 64))

    def transport(self, manifest=None, post=None):
        return PilotTransport(self.fx.root / 'development.sqlite', manifest=manifest or self.manifest,
                              key_file=self.fx.key, post=post or self.fx.post)

    def test_prior_usage_and_new_model_calls_share_one_root(self):
        first = dict(self.manifest, payloads=[fingerprint(self.fx.payload)])
        self.transport(first)(self.fx.payload)
        second = dict(self.manifest, payloads=[fingerprint(self.fx.other)])
        transport = self.transport(second)
        transport(self.fx.other)
        snapshot = transport.snapshot()
        self.assertEqual(snapshot['dispatches'], 12)
        self.assertEqual(snapshot['http_attempts'], 24)
        self.assertEqual(snapshot['committed_microusd'], 24165 + 55 + 1100)

    def test_baseline_cannot_reset_on_new_batch_or_restart(self):
        self.transport()
        changed = copy.deepcopy(self.manifest)
        changed['prior_usage']['cost_microusd'] = 0
        self.fx.assert_code('pilot_policy_changed', lambda: self.transport(changed))
        changed = dict(self.manifest, max_cost_microusd=2999999)
        self.fx.assert_code('pilot_policy_changed', lambda: self.transport(changed))

    def test_admission_limits_include_old_http_attempts(self):
        manifest = dict(self.manifest, max_http_attempts=21)
        self.fx.assert_code('pilot_budget_exceeded', lambda: self.transport(manifest)(self.fx.payload))
        self.assertFalse(self.fx.calls)

    def test_prior_generation_allowance_cannot_be_bypassed_with_new_source(self):
        manifest = copy.deepcopy(self.manifest)
        manifest['prior_usage']['dispatches'] = 100
        manifest['prior_usage']['http_attempts'] = 200
        self.fx.assert_code('pilot_budget_exceeded', lambda: self.transport(manifest)(self.fx.payload))
        self.assertFalse(self.fx.calls)

    def test_prior_money_is_subtracted_before_network(self):
        manifest = dict(self.manifest, max_cost_microusd=25000)
        self.fx.assert_code('pilot_budget_exceeded', lambda: self.transport(manifest)(self.fx.payload))
        self.assertFalse(self.fx.calls)

    def test_bare_manifest_cannot_silently_get_development_limits(self):
        self.fx.assert_code('pilot_manifest_invalid', lambda: self.transport(dict(self.fx.manifest, max_http_attempts=200)))

    def test_unknown_one_batch_freezes_other_batch(self):
        def timeout(*args):
            raise TimeoutError()
        self.assertRaises(TimeoutError, self.transport(post=timeout), self.fx.payload)
        another = dict(self.manifest, payloads=[fingerprint(self.fx.other)])
        self.fx.assert_code('pilot_review_required', lambda: self.transport(another)(self.fx.other))


if __name__ == '__main__':
    unittest.main()

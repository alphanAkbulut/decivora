import copy
import hashlib
import json
import unittest

from protocol import canonical
from project_review_next import CONTEXT, review_projects
from receiver_next import FORMAT, evaluate
from receiver_smoke import ROOT


class TestNextProjectReview(unittest.TestCase):
    def setUp(self):
        folder = ROOT / 'examples/receiver-next-smoke'
        self.request = json.loads((folder / 'request.json').read_text())
        self.oracle = json.loads((folder / 'expected.json').read_text())
        self.output = dict(format=FORMAT, request_id=self.request['request_id'],
                           responses=copy.deepcopy(self.oracle['responses']))
        views = self.request['source_snapshot']['views']
        self.p1, self.p2 = [v['binding']['project_id'] for v in views]
        self.context = json.loads((folder / 'review-context.fixture.json').read_text())
        self.assertEqual(self.context['format'], CONTEXT)

    def review(self, output=None):
        return review_projects(self.request, canonical(self.output if output is None else output), self.context)

    def test_valid_draft_retains_known_question_and_separate_ambiguity(self):
        result = self.review()
        self.assertEqual([p['status'] for p in result['projects']], ['ready_for_review', 'needs_clarification'])
        item = result['projects'][1]
        self.assertEqual(item['review']['readback']['question_id'], 'Q_UI')
        self.assertEqual(item['clarifications'][0]['message_id'], 'N02-m04')
        self.assertEqual(item['clarifications'][0]['request_id'], self.request['request_id'])
        self.assertFalse(result['quality_scored'])
        self.assertFalse(result['execution_authorized'])

    def test_local_type_error_preserves_valid_other_project_without_repair(self):
        self.output['responses'][1]['readback']['reported_test_results'][0]['criterion_revision'] = '2'
        before = canonical(self.output)
        result = self.review()
        self.assertEqual([p['status'] for p in result['projects']], ['ready_for_review', 'invalid_project_output'])
        self.assertEqual(canonical(self.output), before)
        self.assertEqual(result['projects'][1]['clarifications'], [])
        self.assertEqual(result['projects'][1]['diagnostics'][0]['kind'], 'technical_output_error')

    def test_source_action_error_is_local_but_quality_scorer_stays_strict(self):
        self.output['responses'][0]['next_actions'].append(dict(
            action='request_target_verification', message_id='N01-m04', question_id=None))
        result = self.review()
        self.assertEqual(result['projects'][0]['status'], 'invalid_project_output')
        self.assertEqual(result['projects'][1]['status'], 'needs_clarification')
        with self.assertRaises(ValueError):
            evaluate(self.request, canonical(self.output), self.oracle)

    def test_false_approval_verification_and_duplicate_answer_are_local_rejections(self):
        for field in ('approved_real_decision', 'task_verified', 'duplicate'):
            bad = copy.deepcopy(self.output)
            rb = bad['responses'][0]['readback']
            if field == 'duplicate':
                rb['answer_states'].append(copy.deepcopy(rb['answer_states'][0]))
            else:
                rb[field] = True
            with self.subTest(field=field):
                result = self.review(bad)
                self.assertEqual(result['projects'][0]['status'], 'invalid_project_output')
                self.assertIsNotNone(result['projects'][1]['review'])

    def test_missing_and_clean_abstention_are_not_success(self):
        self.output['responses'][1].update(status='abstain', readback=None, next_actions=[])
        self.assertEqual(self.review()['projects'][1]['status'], 'awaiting_context')
        self.output['responses'].pop()
        self.assertEqual(self.review()['projects'][1]['status'], 'missing_output')
        self.output['responses'] = []
        self.assertEqual(self.review()['status'], 'awaiting_resolution')

    def test_abstain_with_data_is_never_repaired(self):
        self.output['responses'][1]['status'] = 'abstain'
        result = self.review()
        self.assertEqual(result['projects'][1]['status'], 'invalid_project_output')
        self.assertIsNotNone(self.output['responses'][1]['readback'])

    def test_atomic_waiting_blocks_both_and_keeps_clarification(self):
        self.context['atomic_groups'] = [[self.p1, self.p2]]
        result = self.review()
        self.assertTrue(all(p['status'] == 'blocked_atomic_group' and p['review'] is None for p in result['projects']))
        self.assertEqual(result['projects'][1]['clarifications'][0]['message_id'], 'N02-m04')
        self.assertEqual(result['status'], 'awaiting_resolution')

    def test_shared_envelope_errors_fail_before_partial_review(self):
        for raw in ('{"format":1,"format":2}', ' ' * 32769,
                    canonical(dict(self.output, format='decivora-receiver-review-1')),
                    canonical(dict(self.output, request_id='old')), canonical(dict(self.output, extra=True))):
            with self.subTest(raw=raw[:60]), self.assertRaises(ValueError):
                review_projects(self.request, raw, self.context)

    def test_all_identities_preflight_before_any_row_review(self):
        for field in ('project_id', 'package_digest', 'duplicate'):
            bad = copy.deepcopy(self.output)
            if field == 'duplicate':
                bad['responses'][1] = copy.deepcopy(bad['responses'][0])
            else:
                bad['responses'][1][field] = 'foreign'
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.review(bad)

    def test_revoked_access_checked_before_json_parse(self):
        self.context['projects'][self.p2]['review_access'] = False
        with self.assertRaisesRegex(ValueError, 'review access'):
            review_projects(self.request, 'not json', self.context)

    def test_incomplete_context_and_stale_binding_fail_globally(self):
        saved = copy.deepcopy(self.context)
        del self.context['projects'][self.p2]
        with self.assertRaises(ValueError):
            self.review()
        self.context = saved
        self.context['projects'][self.p1]['current_binding']['package_digest'] = 'stale'
        with self.assertRaises(ValueError):
            self.review()

    def test_bad_group_membership_types_and_overlap_fail(self):
        for groups in ([[self.p1]], [[self.p1, 'foreign']], [[self.p1, self.p1]],
                       [[self.p1, self.p2], [self.p1, self.p2]], 'all'):
            self.context['atomic_groups'] = groups
            with self.subTest(groups=groups), self.assertRaises(ValueError):
                self.review()

    def test_saved_v1_actual_raw_is_rejected_without_translation(self):
        raw = (ROOT / 'docs/quality/model-runs/receiver-001-response.txt').read_text()
        with self.assertRaisesRegex(ValueError, 'wire-2 envelope'):
            review_projects(self.request, raw, self.context)

    def test_no_input_mutation_stable_output_and_exact_raw_digest(self):
        saved = canonical(dict(request=self.request, context=self.context, output=self.output))
        result = self.review()
        self.assertEqual(result, self.review())
        self.assertEqual(saved, canonical(dict(request=self.request, context=self.context, output=self.output)))
        self.assertEqual(result['raw_sha256'], hashlib.sha256(canonical(self.output).encode()).hexdigest())
        for field in ('model_dispatches', 'paid_api_calls', 'canonical_mutations'):
            self.assertEqual(result[field], 0)


if __name__ == '__main__':
    unittest.main()

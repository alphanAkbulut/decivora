"""Immutable saved native run, not a new model invocation or quality pass."""
import hashlib
import json
import unittest

from project_review_next import review_projects
from receiver_next import evaluate
from receiver_smoke import ROOT

RAW_SHA = '3e72906a5f34c00863e64245b954f443fd200f4502352b051788df1e605c101a'


class TestRecordedNextReceiverRun(unittest.TestCase):
    def setUp(self):
        folder = ROOT / 'examples/receiver-next-smoke'
        self.raw = (ROOT / 'docs/quality/model-runs/receiver-002-response.txt').read_text()
        self.request = json.loads((folder / 'request.json').read_text())
        self.oracle = json.loads((folder / 'expected.json').read_text())
        self.context = json.loads((folder / 'review-context.fixture.json').read_text())

    def test_saved_full_raw_keeps_literals_and_missing_required_field(self):
        self.assertEqual(hashlib.sha256(self.raw.encode()).hexdigest(), RAW_SHA)
        output = json.loads(self.raw)
        self.assertNotIn('next_actions', output['responses'][0])
        self.assertIs(output['responses'][0]['readback']['approved_real_decision'], False)
        self.assertIsNone(output['responses'][1]['next_actions'][1]['question_id'])
        self.assertEqual(output['responses'][1]['next_actions'][-1]['question_id'], 'Q_UI')
        with self.assertRaisesRegex(ValueError, 'schema oneOf'):
            evaluate(self.request, self.raw, self.oracle)

    def test_both_project_errors_stay_unreviewed_and_report_reproduces(self):
        report = json.loads((ROOT / 'docs/quality/receiver-002-results.json').read_text())
        review = review_projects(self.request, self.raw, self.context)
        self.assertEqual(review, report['project_review'])
        self.assertEqual([p['status'] for p in review['projects']],
                         ['invalid_project_output', 'invalid_project_output'])
        self.assertTrue(all(p['review'] is None for p in review['projects']))
        self.assertEqual(report['score']['status'], 'invalid_contract')
        self.assertIsNone(report['score']['readback_score'])
        self.assertIsNone(report['score']['action_score'])
        self.assertEqual(report['raw_sha256'], RAW_SHA)
        self.assertEqual(report['canonical_mutations'], 0)

    def test_exact_permission_consumed_and_usage_not_invented(self):
        auth = json.loads((ROOT / 'examples/receiver-next-smoke/authorization.json').read_text())
        self.assertEqual(auth['request_id'], self.request['request_id'])
        self.assertEqual(auth['prompt_sha256'], self.request['prompt_sha256'])
        self.assertEqual(auth['actual_submission_attempts'], 1)
        self.assertEqual(auth['actual_outputs'], 1)
        self.assertEqual(auth['remaining_submission_attempts'], 0)
        self.assertFalse(auth['paid_api_allowed'])
        self.assertFalse(auth['followup_inference_allowed'])
        self.assertEqual(auth['permission_source']['question_item_id'],
                         '["request_user_input_async","call_09754e4cdaa6416caba50d3a50ffd73e",0]')
        report = json.loads((ROOT / 'docs/quality/receiver-002-results.json').read_text())
        self.assertIsNone(report['usage']['provider_total_tokens'])
        self.assertEqual(report['usage']['token_overrun_status'], 'not_evaluable')
        self.assertFalse(report['next_model_dispatch_authorized'])
        self.assertFalse(report['human_gold'])


if __name__ == '__main__':
    unittest.main()

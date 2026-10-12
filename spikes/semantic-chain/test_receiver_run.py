import hashlib
import json
import unittest
from pathlib import Path

from receiver_smoke import ROOT,evaluate

RAW_SHA='f17e134b68bec39cf7d5539cc812db7a87bd970a851aa30ecf2b43aaeaac4b03'


class TestRecordedReceiverRun(unittest.TestCase):
    def test_first_native_output_is_valid_json_but_invalid_abstention_not_repaired(self):
        raw=(ROOT/'docs/quality/model-runs/receiver-001-response.txt').read_text()
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),RAW_SHA)
        output=json.loads(raw)
        # Full-message retrieval retains literal null/false; summary is not the raw authority.
        self.assertIs(output['responses'][0]['readback']['task_verified'],False)
        self.assertIsNone(output['responses'][1]['next_actions'][1]['question_id'])
        self.assertEqual(output['responses'][1]['status'],'abstain')
        self.assertIsNotNone(output['responses'][1]['readback'])
        self.assertEqual(output['responses'][1]['readback']['reported_test_results'][0]['criterion_revision'],'2')
        request=json.loads((ROOT/'examples/receiver-smoke/request.json').read_text())
        oracle=json.loads((ROOT/'examples/receiver-smoke/expected.json').read_text())
        with self.assertRaisesRegex(ValueError,'invalid receiver abstention'):
            evaluate(request,raw,oracle)
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),RAW_SHA)

    def test_permission_consumed_and_result_keeps_usage_unknown_and_quality_open(self):
        auth=json.loads((ROOT/'examples/receiver-smoke/authorization.json').read_text())
        self.assertEqual(auth['actual_submission_attempts'],1)
        self.assertEqual(auth['actual_outputs'],1)
        self.assertEqual(auth['remaining_submission_attempts'],0)
        self.assertFalse(auth['paid_api_allowed'])
        result=json.loads((ROOT/'docs/quality/receiver-001-results.json').read_text())
        self.assertEqual(result['score']['status'],'invalid_contract')
        self.assertIsNone(result['score']['readback_score'])
        self.assertIsNone(result['score']['action_score'])
        self.assertEqual(result['canonical_mutations'],0)
        self.assertIsNone(result['usage']['provider_total_tokens'])
        self.assertEqual(result['usage']['token_overrun_status'],'not_evaluable')
        self.assertFalse(result['transport_diagnostic']['wait_snapshot_equal_full_message'])
        self.assertFalse(result['transport_diagnostic']['wait_snapshot_json_valid'])
        self.assertEqual(result['configured_model'],'gpt-6-luna')
        self.assertFalse(result['human_gold'])


if __name__=='__main__':unittest.main()

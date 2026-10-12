import copy
import hashlib
import json
import unittest

from protocol import canonical, digest
from receiver_contract import schema_for, shape_check, validate
from receiver_smoke import ROOT, FORMAT, evaluate

EXAMPLES = ROOT / 'examples/receiver-contract'


class TestReceiverContract(unittest.TestCase):
    def setUp(self):
        self.request = json.loads((ROOT / 'examples/receiver-smoke/request.json').read_text())
        self.valid = json.loads((EXAMPLES / 'valid-review.json').read_text())

    def rejected(self, output, reason=None):
        with self.assertRaisesRegex(ValueError, reason or '.'):
            validate(self.request, canonical(output))

    def test_authored_example_preserves_known_question_and_ambiguous_record(self):
        before = copy.deepcopy(self.request)
        result = validate(self.request, canonical(self.valid))
        self.assertEqual(result['status'], 'validated_review_only')
        self.assertTrue(result['response_coverage_complete'])
        self.assertEqual(result['canonical_mutations'], 0)
        self.assertEqual(result['model_dispatches'], 0)
        self.assertEqual(self.request, before)
        rb = self.valid['responses'][1]['readback']
        self.assertEqual(rb['question_id'], 'Q_UI')
        self.assertIn({'message_id': 'N02-m04', 'status': 'needs_clarification'}, rb['answer_states'])

    def test_schema_export_is_bound_and_matches_saved_schema(self):
        schema = schema_for(self.request)
        self.assertEqual(schema, json.loads((EXAMPLES / 'response.schema.json').read_text()))
        self.assertEqual(schema['properties']['request_id']['const'], self.request['request_id'])
        self.assertEqual(len(schema['properties']['responses']['items']['oneOf']), 4)
        shape_check(self.valid, schema)

    def test_abstention_with_data_or_actions_is_rejected(self):
        for field in ('readback', 'next_actions'):
            bad = copy.deepcopy(self.valid)
            row = bad['responses'][1]
            row['status'] = 'abstain'
            if field == 'readback':
                row['next_actions'] = []
            else:
                row['readback'] = None
            self.rejected(bad, 'schema')

    def test_clean_abstention_is_safe_but_incomplete_not_quality_success(self):
        output = copy.deepcopy(self.valid)
        output['responses'][1].update(status='abstain', readback=None, next_actions=[])
        self.assertFalse(validate(self.request, canonical(output))['response_coverage_complete'])
        oracle = json.loads((ROOT / 'examples/receiver-smoke/expected.json').read_text())
        self.assertEqual(evaluate(self.request, canonical(output), oracle)['status'], 'incomplete')

    def test_revision_boolean_float_string_and_zero_are_not_coerced(self):
        for revision in ('2', True, 2.0, 0, -1):
            bad = copy.deepcopy(self.valid)
            bad['responses'][1]['readback']['reported_test_results'][0]['criterion_revision'] = revision
            self.rejected(bad)

    def test_ambiguous_record_does_not_erase_known_question(self):
        bad = copy.deepcopy(self.valid)
        bad['responses'][1]['readback'].update(question_id=None, question_revision=None, question_state='unknown')
        self.rejected(bad, 'known current question')

    def test_future_plan_in_source_is_not_an_eligible_preserved_record(self):
        bad = copy.deepcopy(self.valid)
        bad['responses'][0]['next_actions'].append(dict(type='request_target_verification', message_id='N01-m04', question_id=None))
        self.rejected(bad, 'preserved record')

    def test_stale_answer_ambiguous_question_and_wrong_record_actions_rejected(self):
        for index, change in ((0, dict(type='request_selection_confirmation')),
                              (1, dict(question_id='Q_RELEASE')),
                              (2, dict(type='preserve_history')),
                              (3, dict(type='preserve_history'))):
            bad = copy.deepcopy(self.valid)
            if index == 0:
                bad['responses'][0]['next_actions'][0].update(change)
            else:
                bad['responses'][1]['next_actions'][index].update(change)
            self.rejected(bad, 'action contradicts')

    def test_false_approval_verified_uploaded_or_not_run_to_passed_rejected(self):
        for field, value in (('approved_real_decision', True), ('task_verified', True), ('upload_verification', 'observed_verified')):
            bad = copy.deepcopy(self.valid)
            bad['responses'][1]['readback'][field] = value
            self.rejected(bad)
        bad = copy.deepcopy(self.valid)
        bad['responses'][1]['readback']['reported_test_results'][0]['result'] = 'passed'
        self.rejected(bad, 'selected evidence')

    def test_foreign_project_source_stale_package_and_execution_action_rejected(self):
        changes = [('project_id', 'foreign'), ('package_digest', '0' * 64)]
        for field, value in changes:
            bad = copy.deepcopy(self.valid)
            bad['responses'][0][field] = value
            self.rejected(bad)
        for field, value in (('message_id', 'foreign-message'), ('type', 'execute_shell')):
            bad = copy.deepcopy(self.valid)
            bad['responses'][0]['next_actions'][0][field] = value
            self.rejected(bad)

    def test_duplicate_project_record_and_extra_fields_rejected(self):
        for kind in ('project', 'record', 'extra'):
            bad = copy.deepcopy(self.valid)
            if kind == 'project':
                bad['responses'][1] = copy.deepcopy(bad['responses'][0])
            elif kind == 'record':
                bad['responses'][0]['next_actions'].append(dict(type='preserve_history', message_id='N01-m01', question_id='Q_STORE'))
            else:
                bad['execute'] = True
            self.rejected(bad)

    def test_stale_request_and_duplicate_json_keys_rejected(self):
        bad = copy.deepcopy(self.request)
        bad['views'][0]['binding']['authz_revision'] += 1
        with self.assertRaisesRegex(ValueError, 'stale receiver source contract'):
            validate(bad, canonical(self.valid))
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            validate(self.request, '{"format":"x","format":"y"}')

    def test_missing_actions_remain_quality_failure_not_auto_completed(self):
        missing = copy.deepcopy(self.valid)
        missing['responses'][1]['next_actions'] = []
        self.assertTrue(validate(self.request, canonical(missing))['response_coverage_complete'])
        oracle = json.loads((ROOT / 'examples/receiver-smoke/expected.json').read_text())
        score = evaluate(self.request, canonical(missing), oracle)
        self.assertEqual(score['status'], 'failed_draft')
        self.assertEqual(score['action_score']['false_negative'], 4)

    def test_frozen_run_still_rejected_raw_and_prompt_unchanged(self):
        raw = (ROOT / 'docs/quality/model-runs/receiver-001-response.txt').read_text()
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), 'f17e134b68bec39cf7d5539cc812db7a87bd970a851aa30ecf2b43aaeaac4b03')
        self.rejected(json.loads(raw))
        prompt = (ROOT / 'examples/receiver-smoke/prompt.txt').read_bytes()
        self.assertEqual(hashlib.sha256(prompt).hexdigest(), 'a4a636ecd53aee80ea74ef21608e26cdb50cc65f1f1da434a9cf9294d2073b6b')

    def test_unsupported_schema_keyword_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'unsupported schema keyword'):
            shape_check(self.valid, {'type': 'object', 'pattern': 'unsupported'})

    def test_saved_invalid_examples_are_rejected(self):
        invalid = json.loads((EXAMPLES / 'invalid-reviews.json').read_text())
        for case in invalid:
            with self.subTest(case=case['case_id']):
                self.rejected(case['response'], case['error_contains'])


if __name__ == '__main__':
    unittest.main()

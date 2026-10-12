import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from protocol import canonical
from receiver_next import FORMAT, MAX_BYTES, SOURCE_REQUEST_SHA, prepare, parts, validate_response, evaluate
from receiver_smoke import ROOT

FOLDER = ROOT / 'examples/receiver-next-smoke'


class TestReceiverNext(unittest.TestCase):
    def setUp(self):
        self.request = prepare()
        self.oracle = json.loads((FOLDER / 'expected.json').read_text())
        self.reply = dict(format=FORMAT, request_id=self.request['request_id'], responses=copy.deepcopy(self.oracle['responses']))

    def reject(self, reply=None):
        with self.assertRaises(ValueError):
            validate_response(self.request, canonical(self.reply if reply is None else reply))

    def test_saved_request_and_prompt_are_exact_and_deterministic(self):
        self.assertEqual(self.request, prepare())
        self.assertEqual(self.request, json.loads((FOLDER / 'request.json').read_text()))
        self.assertEqual(self.request['prompt'].encode(), (FOLDER / 'prompt.txt').read_bytes())
        self.assertEqual(self.request['prompt_bytes'], 8089)

    def test_prepare_reads_only_three_allowlisted_source_files_no_oracle_or_scorer(self):
        original = Path.read_bytes
        allowed = {ROOT / 'examples/receiver-smoke/request.json',
                   ROOT / 'examples/resume-compact-smoke/N01-readable.json',
                   ROOT / 'examples/resume-compact-smoke/N02-readable.json'}
        reads = set()
        def bounded(path):
            self.assertIn(path, allowed)
            reads.add(path)
            return original(path)
        with patch.object(Path, 'read_bytes', bounded):
            self.assertEqual(prepare(), self.request)
        self.assertEqual(reads, allowed)

    def test_all_eight_messages_and_records_preserved_without_quote_tables(self):
        self.assertEqual(sum(len(p['source_messages']) for p in self.request['projects']), 8)
        self.assertEqual(sum(len(p['records']) for p in self.request['projects']), 6)
        for view, projection in zip(self.request['source_snapshot']['views'], self.request['projects']):
            self.assertEqual(projection['source_messages'], view['source_messages'])
            self.assertEqual(projection['fixture_state'], view['fixture_state'])
            self.assertEqual(projection['question_presentations'], view['selected_context']['question_presentations'])
            self.assertEqual(projection['coverage'], view['coverage'])
            for record, projected in zip(view['preserved_records'], projection['records']):
                for field in ('message_id', 'kind', 'attributes'):
                    self.assertEqual(projected[field], record[field])
        self.assertNotIn('review_status', self.request['prompt'])
        self.assertNotIn('expected.json', self.request['prompt'])

    def test_shared_machine_schema_has_two_typed_branches_bound_to_new_identity(self):
        schema = self.request['schema']
        self.assertEqual(schema, json.loads((FOLDER / 'response.schema.json').read_text()))
        self.assertEqual(len(schema['properties']['responses']['items']['oneOf']), 2)
        self.assertEqual(schema['properties']['request_id']['const'], self.request['request_id'])
        self.assertEqual(schema['properties']['format']['const'], FORMAT)
        self.assertNotEqual(self.request['request_id'], self.request['source_snapshot']['prior_request_id'])

    def test_scripted_positive_only_evaluator_harness_not_model_success(self):
        result = evaluate(self.request, canonical(self.reply), self.oracle)
        self.assertEqual(result['status'], 'passed_draft')
        self.assertEqual(result['action_score'], dict(true_positive=6, false_positive=0, false_negative=0))
        self.assertFalse(result['human_gold'])
        self.assertEqual(result['model_dispatches'], 0)
        self.assertIsNone(result['usage'])

    def test_missing_project_and_clean_abstention_are_incomplete(self):
        self.reply['responses'][1].update(status='abstain', readback=None, next_actions=[])
        self.assertEqual(evaluate(self.request, canonical(self.reply), self.oracle)['status'], 'incomplete')
        self.reply['responses'].pop()
        self.assertEqual(evaluate(self.request, canonical(self.reply), self.oracle)['status'], 'incomplete')

    def test_abstain_with_readback_or_actions_rejected(self):
        for field in ('readback', 'next_actions'):
            bad = copy.deepcopy(self.reply)
            bad['responses'][1]['status'] = 'abstain'
            if field == 'readback':
                bad['responses'][1]['next_actions'] = []
            else:
                bad['responses'][1]['readback'] = None
            self.reject(bad)

    def test_revision_strings_floats_bools_and_nonpositive_values_rejected(self):
        for value in ('2', 2.0, True, 0, -1):
            bad = copy.deepcopy(self.reply)
            bad['responses'][1]['readback']['reported_test_results'][0]['criterion_revision'] = value
            self.reject(bad)

    def test_future_plan_and_stale_selection_are_not_actions(self):
        bad = copy.deepcopy(self.reply)
        bad['responses'][0]['next_actions'].append(dict(type='request_target_verification', message_id='N01-m04', question_id=None))
        self.reject(bad)
        self.reply['responses'][0]['next_actions'][0]['type'] = 'request_selection_confirmation'
        self.reject()

    def test_ambiguous_answer_does_not_erase_current_question_or_gain_question_id(self):
        bad = copy.deepcopy(self.reply)
        bad['responses'][1]['readback'].update(question_id=None, question_revision=None, question_state='unknown')
        self.reject(bad)
        self.reply['responses'][1]['next_actions'][1]['question_id'] = 'Q_RELEASE'
        self.reject()

    def test_foreign_duplicate_project_and_package_pair_mismatch_rejected(self):
        for kind in ('foreign', 'duplicate', 'pair'):
            bad = copy.deepcopy(self.reply)
            if kind == 'foreign':
                bad['responses'][1]['project_id'] = 'foreign'
            elif kind == 'duplicate':
                bad['responses'][1] = copy.deepcopy(bad['responses'][0])
            else:
                bad['responses'][1]['package_digest'] = bad['responses'][0]['package_digest']
            self.reject(bad)

    def test_duplicate_answer_criterion_and_action_rejected(self):
        for field in ('answer_states', 'reported_test_results', 'next_actions'):
            bad = copy.deepcopy(self.reply)
            row = bad['responses'][1]
            target = row[field] if field == 'next_actions' else row['readback'][field]
            target.append(copy.deepcopy(target[0]))
            self.reject(bad)

    def test_false_approval_verification_and_not_run_pass_rejected(self):
        for field, value in (('approved_real_decision', True), ('task_verified', True), ('upload_verification', 'observed_verified')):
            bad = copy.deepcopy(self.reply)
            bad['responses'][1]['readback'][field] = value
            self.reject(bad)
        self.reply['responses'][1]['readback']['reported_test_results'][0]['result'] = 'passed'
        self.reject()

    def test_request_prompt_source_and_schema_tamper_rejected(self):
        for field in ('prompt', 'schema', 'projects', 'source_snapshot'):
            bad = copy.deepcopy(self.request)
            if field == 'prompt':
                bad[field] += ' changed'
            elif field == 'schema':
                bad[field]['properties']['format']['const'] = 'other'
            elif field == 'projects':
                bad[field][0]['source_messages'][0]['text'] = 'changed'
            else:
                bad[field]['views'][0]['binding']['authz_revision'] += 1
            with self.assertRaisesRegex(ValueError, 'snapshot changed'):
                validate_response(bad, canonical(self.reply))

    def test_actual_source_file_and_subquote_changes_are_rejected(self):
        original = Path.read_bytes
        def changed(path):
            value = original(path)
            return value + b' ' if path.name == 'N01-readable.json' else value
        with patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'readable source changed'):
            prepare()
        snapshot = copy.deepcopy(self.request['source_snapshot'])
        snapshot['views'][0]['preserved_records'][0]['quote'] = 'SQLite'
        with self.assertRaisesRegex(ValueError, 'whole-message quotes'):
            parts(snapshot)

    def test_byte_limit_is_not_expanded_or_truncated(self):
        for limit in (8088, MAX_BYTES + 1, '8192', True):
            with self.assertRaises(ValueError):
                prepare(max_bytes=limit)
        self.assertEqual(prepare(max_bytes=8089)['prompt'], self.request['prompt'])
        self.assertFalse(self.request['hard_token_cap_verified'])
        self.assertFalse(self.request['hard_context_cap_verified'])

    def test_frozen_old_request_raw_and_wrong_version_stay_unchanged_rejected(self):
        self.assertEqual(hashlib.sha256((ROOT / 'examples/receiver-smoke/request.json').read_bytes()).hexdigest(), SOURCE_REQUEST_SHA)
        raw = (ROOT / 'docs/quality/model-runs/receiver-001-response.txt').read_text()
        self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(), 'f17e134b68bec39cf7d5539cc812db7a87bd970a851aa30ecf2b43aaeaac4b03')
        with self.assertRaises(ValueError):
            validate_response(self.request, raw)
        self.reply['format'] = 'decivora-receiver-review-1'
        self.reject()

    def test_cli_never_overwrites_and_prepare_rejects_expected_input(self):
        script = Path(__file__).with_name('receiver_next.py')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'existing.json'
            target.write_text('keep')
            completed = subprocess.run([sys.executable, '-B', str(script), 'prepare', '--out', str(target)], capture_output=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(target.read_text(), 'keep')
        completed = subprocess.run([sys.executable, '-B', str(script), 'prepare', '--expected', str(FOLDER / 'expected.json')], capture_output=True)
        self.assertNotEqual(completed.returncode, 0)

    def test_manifest_hashes_and_no_dispatch_authorization(self):
        manifest = json.loads((FOLDER / 'manifest.json').read_text())
        for path, expected in manifest['file_sha256'].items():
            self.assertEqual(hashlib.sha256((FOLDER / path).read_bytes()).hexdigest(), expected)
        self.assertFalse(manifest['dispatch_authorized'])
        self.assertEqual(manifest['authorization_status'], 'not_granted')
        self.assertEqual(manifest['actual_submissions'], 0)
        self.assertFalse(manifest['paid_api_allowed'])

    def test_oracle_not_gold_and_missing_actions_not_complete(self):
        wrong = dict(self.oracle, review_status='human_gold')
        with self.assertRaises(ValueError):
            evaluate(self.request, canonical(self.reply), wrong)
        self.reply['responses'][1]['next_actions'] = []
        result = evaluate(self.request, canonical(self.reply), self.oracle)
        self.assertEqual(result['status'], 'failed_draft')
        self.assertEqual(result['action_score']['false_negative'], 4)


if __name__ == '__main__':
    unittest.main()

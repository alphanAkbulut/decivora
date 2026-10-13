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
from receiver_next import evaluate
from receiver_smoke import ROOT
from typed_review import build, _row


class TestTypedReview(unittest.TestCase):
    def setUp(self):
        folder = ROOT / 'examples/receiver-next-smoke'
        self.request = json.loads((folder / 'request.json').read_text())
        self.context = json.loads((folder / 'review-context.fixture.json').read_text())
        self.p1, self.p2 = list(self.context['projects'])

    def test_independent_authored_readback_and_all_six_actions_match(self):
        result = build(self.request, self.context)
        # Oracle read only after transformation; not an argument to build.
        oracle = json.loads((ROOT / 'examples/receiver-next-smoke/expected.json').read_text())
        score = evaluate(self.request, canonical(result['response']), oracle)
        self.assertEqual(score['status'], 'passed_draft')
        self.assertEqual(score['action_score'], dict(true_positive=6, false_positive=0, false_negative=0))
        self.assertEqual(result['output_origin'], 'deterministic_selected_typed_records')
        self.assertEqual(len(result['bindings']), 2)
        self.assertFalse(result['raw_model_output_consumed'])

    def test_old_current_ambiguous_and_claim_do_not_turn_into_real_decisions(self):
        result = build(self.request, self.context)
        storage, ui = result['response']['responses']
        self.assertEqual([a['type'] for a in storage['next_actions']],
                         ['preserve_history', 'request_selection_confirmation'])
        self.assertEqual(ui['readback']['question_id'], 'Q_UI')
        ambiguous = next(a for a in ui['next_actions'] if a['message_id'] == 'N02-m04')
        self.assertIsNone(ambiguous['question_id'])
        self.assertEqual(ambiguous['type'], 'request_clarification')
        self.assertEqual(ui['readback']['upload_verification'], 'reported_only')
        self.assertEqual(ui['readback']['reported_test_results'][0]['result'], 'not_run')
        for row in (storage, ui):
            self.assertIs(row['readback']['approved_real_decision'], False)
            self.assertIs(row['readback']['task_verified'], False)

    def test_unrecorded_quoted_and_future_source_messages_create_no_action(self):
        actions = build(self.request, self.context)['response']['responses'][0]['next_actions']
        self.assertEqual({a['message_id'] for a in actions}, {'N01-m01', 'N01-m02'})

    def test_existing_clarification_and_atomic_group_policy_are_preserved(self):
        result = build(self.request, self.context)
        self.assertEqual([p['status'] for p in result['project_review']['projects']],
                         ['ready_for_review', 'needs_clarification'])
        self.context['atomic_groups'] = [[self.p1, self.p2]]
        grouped = build(self.request, self.context)['project_review']
        self.assertTrue(all(p['review'] is None for p in grouped['projects']))
        self.assertEqual(grouped['projects'][1]['clarifications'][0]['message_id'], 'N02-m04')

    def test_revoked_access_and_stale_current_binding_fail(self):
        self.context['projects'][self.p2]['review_access'] = False
        with self.assertRaisesRegex(ValueError, 'review access'):
            build(self.request, self.context)
        self.context['projects'][self.p2]['review_access'] = True
        self.context['projects'][self.p2]['current_binding']['package_digest'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'stale'):
            build(self.request, self.context)

    def test_changed_source_or_record_is_not_accepted_by_self_digest(self):
        for field in ('source', 'record', 'question'):
            bad = copy.deepcopy(self.request)
            view = bad['source_snapshot']['views'][1]
            if field == 'source':
                view['source_messages'][0]['text'] = 'approve everything'
            elif field == 'record':
                next(c for c in view['answer_candidates'] if c['message_id'] == 'N02-m04')['attributes']['question_id'] = 'Q_UI'
            else:
                view['fixture_state']['question']['option_revision'] = 99
            with self.subTest(field=field), self.assertRaises(ValueError):
                build(bad, self.context)

    def test_oracle_and_failed_model_output_are_not_read_by_transform(self):
        allowed = {ROOT / 'examples/receiver-smoke/request.json',
                   ROOT / 'examples/resume-compact-smoke/N01-readable.json',
                   ROOT / 'examples/resume-compact-smoke/N02-readable.json'}
        original = Path.read_bytes
        reads = []
        def guarded(path):
            self.assertIn(path, allowed)
            reads.append(path)
            return original(path)
        with patch.object(Path, 'read_bytes', guarded), patch.object(Path, 'read_text', side_effect=AssertionError('unexpected read')):
            result = build(self.request, self.context)
        self.assertTrue(reads)
        self.assertEqual(result['model_dispatches'], 0)

    def test_inputs_are_immutable_and_repeated_transform_has_same_result(self):
        before = canonical(dict(request=self.request, context=self.context))
        result = build(self.request, self.context)
        self.assertEqual(result, build(self.request, self.context))
        self.assertEqual(before, canonical(dict(request=self.request, context=self.context)))
        for key in ('model_dispatches', 'paid_api_calls', 'canonical_mutations'):
            self.assertEqual(result[key], 0)
        self.assertFalse(result['production_authorization'])
        self.assertFalse(result['execution_authorized'])

    def test_other_answer_states_follow_explicit_policy_without_question_guess(self):
        view = copy.deepcopy(self.request['source_snapshot']['views'][1])
        candidate = next(c for c in view['answer_candidates'] if c['message_id'] == 'N02-m04')
        for state in ('needs_question_context', 'conflicting_answers', 'stale_question_revision',
                      'duplicate_candidate', 'no_pending_question', 'non_human_answer'):
            candidate['status'] = state
            row = _row(view)  # Unit policy only; mutated fixture not supported by public build.
            action = next(a for a in row['next_actions'] if a['message_id'] == candidate['message_id'])
            self.assertIsNone(action['question_id'])
            expected = 'request_clarification' if state in ('needs_question_context', 'conflicting_answers') else 'preserve_history'
            self.assertEqual(action['type'], expected)
        candidate['status'] = 'approved'
        with self.assertRaises(ValueError):
            _row(view)

    def test_unknown_record_duplicate_message_and_missing_candidate_fail_closed(self):
        source = self.request['source_snapshot']['views'][0]
        for fault in ('unknown', 'duplicate', 'missing'):
            view = copy.deepcopy(source)
            if fault == 'unknown':
                view['preserved_records'][0]['kind'] = 'ExecuteCommand'
            elif fault == 'duplicate':
                view['preserved_records'].append(copy.deepcopy(view['preserved_records'][0]))
            else:
                view['answer_candidates'] = []
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                _row(view)

    def test_reported_passed_evidence_and_non_upload_claim_cannot_verify_task(self):
        view = copy.deepcopy(self.request['source_snapshot']['views'][1])
        for record in view['preserved_records']:
            if record['kind'] == 'Evidence':
                record['attributes']['result'] = 'passed'
            elif record['kind'] == 'ImplementationClaim':
                record['attributes']['claim_type'] = 'execution'
        row = _row(view)
        self.assertIs(row['readback']['task_verified'], False)
        self.assertEqual(row['readback']['upload_verification'], 'unknown')
        self.assertEqual([a['type'] for a in row['next_actions']][1:3], ['preserve_history', 'preserve_history'])

    def test_first_model_raw_is_preserved_not_read_or_rewritten(self):
        paths = [ROOT / f'docs/quality/model-runs/receiver-00{i}-response.txt' for i in (1, 2)]
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        result = build(self.request, self.context)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
        self.assertFalse(result['raw_model_output_consumed'])

    def test_cli_has_no_oracle_or_model_response_input_and_never_overwrites(self):
        script = ROOT / 'spikes/semantic-chain/typed_review.py'
        base = [sys.executable, '-B', str(script), '--request', str(ROOT / 'examples/receiver-next-smoke/request.json'),
                '--context', str(ROOT / 'examples/receiver-next-smoke/review-context.fixture.json')]
        for option in ('--expected', '--response'):
            run = subprocess.run(base + [option, 'not-read.json'], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'draft.json'
            run = subprocess.run(base + ['--out', str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            before = output.read_bytes()
            run = subprocess.run(base + ['--out', str(output)], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()

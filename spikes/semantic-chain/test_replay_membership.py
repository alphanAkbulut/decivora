import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from replay_membership import replay, apply_fixture_impact, ROOT, HERE, Chain


class TestSavedMembershipChain(unittest.TestCase):
    def test_actual_saved_candidates_connect_without_claim_or_partial_false_done(self):
        result = replay()
        self.assertEqual(result['checkpoint_score']['status'], 'passed')
        self.assertEqual(len(result['checkpoints']), 13)
        self.assertEqual(result['raw_sha256'], 'e3941c35f39cdf4117bec100e01249a6eb3ec23b82b263e9998d8371ffc862da')
        self.assertEqual(result['checkpoints']['decision']['decision'], 'D_SQLITE')
        self.assertEqual(result['checkpoints']['decision']['task_statuses'], ['todo'])
        self.assertEqual(result['checkpoints']['selection_retry']['canonical_mutations'], 0)
        self.assertEqual(result['checkpoints']['reported_evidence']['evidence'], {})
        for point in ('reported_evidence', 'old_target', 'wrong_content', 'current_target', 'partial'):
            self.assertFalse(result['checkpoints'][point]['verified'])
        self.assertTrue(result['checkpoints']['complete']['verified'])
        self.assertTrue(result['checkpoints']['restore']['same_projection'])
        self.assertTrue(result['checkpoints']['restore']['same_event_count'])
        self.assertEqual(result['checkpoints']['ambiguous']['canonical_mutations'], 0)
        self.assertEqual(result['new_model_dispatches'], 0)
        self.assertFalse(result['production_runtime'])
        self.assertFalse(result['human_gold'])
        self.assertFalse(result['remote_upload_verified'])
        self.assertEqual([r['status'] for r in result['bounded_local_reads']], ['mismatch', 'mismatch', 'observed_match'])
        self.assertTrue(all(not r['task_verified'] for r in result['bounded_local_reads']))

    def test_rebinding_request_or_question_rejected_before_chain_creation(self):
        fixture = json.loads((HERE/'fixtures/membership-chain-scenario.json').read_text())
        for field in ('request_id', 'project_id', 'options'):
            bad = copy.deepcopy(fixture)
            if field == 'options':
                bad['question']['options'] = {'A':'markdown', 'B':'sqlite'}
            else:
                bad[field] = 'other'
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                p = Path(d)/'fixture.json'; p.write_text(json.dumps(bad))
                with patch('replay_membership.Chain', side_effect=AssertionError('must not create events')):
                    with self.assertRaises(ValueError): replay(scenario_path=p)

    def test_changed_first_output_bytes_and_original_v1_are_not_repaired(self):
        raw = (ROOT/'docs/quality/model-runs/membership-002-response.txt').read_text()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'raw.txt'; p.write_text(raw+'\n')
            for path in (p, ROOT/'docs/quality/model-runs/membership-001-response.txt'):
                with self.subTest(path=path.name), patch('replay_membership.Chain', side_effect=AssertionError('must not create events')):
                    with self.assertRaises(ValueError): replay(response_path=path)

    def test_separate_selection_receipt_is_required_and_bound(self):
        fixture = json.loads((HERE/'fixtures/membership-chain-scenario.json').read_text())
        for field, value in [('authenticated',False), ('project_id','prj_release'),
                             ('source_sha256','stale'), ('option_revision',2)]:
            bad = copy.deepcopy(fixture); bad['selection_receipt'][field] = value
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                p = Path(d)/'fixture.json'; p.write_text(json.dumps(bad))
                with patch('replay_membership.observe', side_effect=AssertionError('no target read before selection')):
                    with self.assertRaises(PermissionError): replay(scenario_path=p)

    def test_impact_permission_and_changed_graph_cannot_close_tasks(self):
        fixture = json.loads((HERE/'fixtures/membership-chain-scenario.json').read_text())
        with tempfile.TemporaryDirectory() as d:
            chain = Chain(Path(d)/'events.db')
            try:
                chain.dispatch('seed', fixture['seed'], 'human', 0, 'seed')
                chain.dispatch('ask', fixture['question'], 'human', 1, 'ask')
                chain.dispatch('answer', dict(question_id='Q_STORE',option_revision=1,option='B'), 'human', 2, 'answer')
                before = chain.snapshot()
                for field, value in [('authenticated',False),('permission','decision.approve'),('project_id','prj_release')]:
                    bad = dict(fixture['impact_receipt'], **{field:value})
                    with self.subTest(field=field), self.assertRaises(PermissionError):
                        apply_fixture_impact(chain, 'prj_memory', bad)
                    self.assertEqual(chain.snapshot(), before)
                chain.dispatch('add_reason', dict(task='sync',expr={'any':['D_MARKDOWN','D_SQLITE']}), 'human', 3, 'new-reason')
                changed = chain.snapshot()
                for receipt in (fixture['impact_receipt'], dict(fixture['impact_receipt'],base_revision=4)):
                    with self.assertRaises(ValueError): apply_fixture_impact(chain, 'prj_memory', receipt)
                    self.assertEqual(chain.snapshot(), changed)
            finally:
                chain.close()

    def test_missing_independent_expectations_remain_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'expectations.json'; p.write_text('{}')
            self.assertEqual(replay(expected_path=p)['checkpoint_score']['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()

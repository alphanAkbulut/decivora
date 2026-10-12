import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'decision-chain'))
from chain import Chain
from bridge import collect_proposals, apply_selection, propose
from protocol import prepare, canonical
from collect_membership import run


def request_output(items):
    source = dict(synthetic=True, project_id='p', session_id='late', messages=[
        dict(message_id=f'm{i}', source_revision=1, text=text, actor=dict(type=actor))
        for i, (text, actor, attrs) in enumerate(items)])
    request = prepare(source)
    records = [dict(message_id=f'm{i}', kind='AnswerRecord', entity_key='shared-key',
                    start=0, end=len(text), quote=text, attributes=attrs)
               for i, (text, actor, attrs) in enumerate(items)]
    return request, dict(format='decivora-candidates-1', request_id=request['request_id'],
                         status='ok', records=records)


def attrs(option='A', revision=2, question='Q'):
    return dict(question_id=question, option_id=option, presentation_revision=revision)


class TestProposalCollection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.chain = Chain(Path(self.tmp.name) / 'events.db')
        self.addCleanup(self.chain.close)
        self.chain.dispatch('seed', dict(decision='old', active=['old'], tasks={},
                            criteria=['rollback']), 'human', 0, 'seed')
        self.chain.dispatch('ask', dict(question_id='Q', option_revision=2,
                            options={'A': 'sqlite', 'B': 'postgres'}), 'human', 1, 'ask')
        self.before = self.chain.snapshot()

    def collect(self, items):
        request, response = request_output(items)
        report = collect_proposals(self.chain, request, canonical(response), 'p')
        self.assertEqual(self.chain.snapshot(), self.before)
        self.assertEqual(report['canonical_mutations'], 0)
        return request, response, report

    def test_old_current_and_ambiguous_separate_without_history_loss(self):
        req, output, report = self.collect([
            ('Old B', 'human_owner', attrs('B', 1)),
            ('Current A', 'human_owner', attrs()), ('B.', 'human_owner', {})])
        by_mid = {e['candidate']['message_id']: e for e in report['answer_candidates']}
        self.assertEqual([by_mid[f'm{i}']['status'] for i in range(3)],
                         ['stale_question_revision', 'pending_trusted_selection', 'needs_clarification'])
        self.assertEqual(len(report['preserved_records']), 3)
        self.assertEqual(len({e['candidate_id'] for e in report['answer_candidates']}), 3)
        self.assertEqual(propose(self.chain, req, canonical(output))['status'], 'unmatched_or_ambiguous')

    def test_conflicting_current_answers_never_last_wins(self):
        req, output, report = self.collect([
            ('A', 'human_owner', attrs()), ('B', 'human_owner', attrs('B'))])
        self.assertEqual({e['status'] for e in report['answer_candidates']}, {'conflicting_answers'})
        self.assertTrue(all(e['proposal'] is None for e in report['answer_candidates']))
        output['records'].reverse()
        reversed_report = collect_proposals(self.chain, req, canonical(output), 'p')
        self.assertEqual(report['answer_candidates'], reversed_report['answer_candidates'])

    def test_alias_duplicates_preserved_and_blocked_exact_duplicates_rejected(self):
        req, output, _ = self.collect([('A', 'human_owner', attrs())])
        alias = copy.deepcopy(output['records'][0]); alias['entity_key'] = 'alias'
        output['records'].append(alias)
        report = collect_proposals(self.chain, req, canonical(output), 'p')
        self.assertEqual(len(report['answer_candidates']), 2)
        self.assertEqual({e['status'] for e in report['answer_candidates']}, {'duplicate_candidate'})
        self.assertTrue(all(e['proposal'] is None for e in report['answer_candidates']))
        output['records'][-1]['entity_key'] = 'shared-key'
        with self.assertRaises(ValueError):
            collect_proposals(self.chain, req, canonical(output), 'p')
        self.assertEqual(self.chain.snapshot(), self.before)

    def test_future_other_question_and_nonhuman_need_context_or_authority(self):
        _, _, report = self.collect([
            ('future', 'human_owner', attrs(revision=3)),
            ('other', 'human_owner', attrs(question='OTHER')),
            ('agent A', 'assistant', attrs())])
        self.assertEqual({e['status'] for e in report['answer_candidates']},
                         {'needs_question_context', 'non_human_answer'})
        self.assertTrue(all(e['proposal'] is None for e in report['answer_candidates']))

    def test_whole_response_validation_and_explicit_project_scope_fail_closed(self):
        req, output = request_output([('A', 'human_owner', attrs())])
        for change in ('foreign_project', 'quote', 'model_authority', 'source'):
            request, response = copy.deepcopy(req), copy.deepcopy(output)
            scope = 'other' if change == 'foreign_project' else 'p'
            if change == 'quote': response['records'][0]['quote'] = 'not in source'
            if change == 'model_authority': response['records'][0]['attributes']['approved'] = True
            if change == 'source': request['source']['session_id'] = 'changed'
            with self.assertRaises((ValueError, PermissionError)):
                collect_proposals(self.chain, request, canonical(response), scope)
        self.assertEqual(self.chain.snapshot(), self.before)

    def test_abstention_empty_and_no_pending_are_distinct(self):
        req, output = request_output([('A', 'human_owner', attrs())])
        empty = dict(output, records=[])
        self.assertEqual(collect_proposals(self.chain, req, canonical(empty), 'p')['status'], 'no_answer_candidates')
        self.assertEqual(collect_proposals(self.chain, req, canonical(dict(empty, status='abstain')), 'p')['status'], 'needs_context')
        self.chain.dispatch('answer', dict(question_id='Q', option_revision=2,
                            option='A', source_session='fixture'), 'human', 2, 'fixture-only')
        state = self.chain.snapshot()
        report = collect_proposals(self.chain, req, canonical(output), 'p')
        self.assertEqual(report['answer_candidates'][0]['status'], 'no_pending_question')
        self.assertEqual(self.chain.snapshot(), state)

    def test_separate_bound_receipt_required_and_retry_idempotent(self):
        req, output, report = self.collect([('A', 'human_owner', attrs())])
        proposal = report['answer_candidates'][0]['proposal']
        with self.assertRaises(PermissionError):
            apply_selection(self.chain, req, proposal, {}, 'p')
        self.assertEqual(self.chain.snapshot(), self.before)
        receipt = {k: proposal[k] for k in ('project_id', 'source_sha256', 'message_id',
                   'question_id', 'option_revision', 'option', 'base_revision')}
        receipt.update(authenticated=True, permission='decision.approve')
        wrong = dict(receipt, message_id='other')
        with self.assertRaises(PermissionError):
            apply_selection(self.chain, req, proposal, wrong, 'p')
        first = apply_selection(self.chain, req, proposal, receipt, 'p')
        self.assertEqual(apply_selection(self.chain, req, proposal, receipt, 'p'), first)
        self.assertEqual(self.chain.snapshot()['revision'], 3)
        self.assertEqual(self.chain.snapshot()['decision'], 'sqlite')

    def test_saved_real_output_diagnostic_no_dispatch(self):
        result = run()
        statuses = [{e['candidate']['message_id']: e['status']
                     for e in r['collection']['answer_candidates']} for r in result['results']]
        self.assertEqual(statuses, [
            {'N01-m01': 'stale_question_revision', 'N01-m02': 'pending_trusted_selection'},
            {'N02-m01': 'pending_trusted_selection', 'N02-m04': 'needs_clarification'}])
        self.assertEqual([len(r['collection']['preserved_records']) for r in result['results']], [2, 4])
        self.assertTrue(all(r['projection_unchanged'] and r['question_still_pending'] for r in result['results']))
        self.assertEqual(result['model_dispatches'], 0)
        self.assertEqual(result['selection_dispatches'], 0)

    def test_same_choice_distinct_sources_and_stale_base_do_not_double_apply(self):
        req, _, report = self.collect([
            ('First A', 'human_owner', attrs()), ('Again A', 'human_owner', attrs())])
        proposals = [e['proposal'] for e in report['answer_candidates']]
        self.assertNotEqual(proposals[0]['proposal_digest'], proposals[1]['proposal_digest'])
        def receipt(p):
            return dict({k: p[k] for k in ('project_id', 'source_sha256', 'message_id',
                'question_id', 'option_revision', 'option', 'base_revision')},
                authenticated=True, permission='decision.approve')
        apply_selection(self.chain, req, proposals[0], receipt(proposals[0]), 'p')
        state = self.chain.snapshot()
        with self.assertRaises(ValueError):
            apply_selection(self.chain, req, proposals[1], receipt(proposals[1]), 'p')
        self.assertEqual(self.chain.snapshot(), state)


if __name__ == '__main__': unittest.main()

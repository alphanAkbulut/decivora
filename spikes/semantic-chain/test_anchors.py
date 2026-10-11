import copy
import json
import unittest
import sys
import tempfile
import subprocess
from pathlib import Path

from anchors import anchor, prepare_quotes, unique_span
from candidate_eval import evaluate_candidates
from protocol import canonical, prepare, validate
from bridge import propose

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'spikes/decision-chain'))
from chain import Chain


def request(text='🙂 Önceki Q_STORE için B.', actor='human_owner'):
    return prepare(dict(synthetic=True, project_id='p', session_id='late', messages=[dict(
        message_id='m', source_revision=1, text=text, actor=dict(type=actor))]))


def output(req, kind='AnswerRecord', attrs=None):
    packet = prepare_quotes(req)
    return dict(format=packet['format'], request_id=req['request_id'],
        contract_id=packet['contract_id'], status='ok', records=[dict(message_id='m',
        kind=kind, entity_key='provisional', quote=req['source']['messages'][0]['text'],
        attributes=attrs if attrs is not None else dict(question_id='Q_STORE',
            option_id='B', presentation_revision=1))])


def rubric(req, out):
    # Test helper only; recorded expectations are separately authored in fixtures.
    return dict(format='decivora-candidate-rubric-1', request_id=req['request_id'],
        review_status='authored_draft', expected=[{k: r[k] for k in
        ('message_id', 'kind', 'quote', 'attributes')} for r in out['records']])


class TestAnchors(unittest.TestCase):
    def setUp(self):
        self.req = request(); self.out = output(self.req)

    def test_quote_contract_is_separate_and_stable(self):
        original = copy.deepcopy(self.req)
        first = prepare_quotes(self.req)
        self.assertEqual(first, prepare_quotes(self.req))
        self.assertNotIn('start', first['response_contract']['records'][0])
        self.assertEqual(self.req, original)
        first['source']['messages'][0]['text'] = 'changed'
        self.assertEqual(self.req, original)

    def test_unicode_position_and_candidate_only(self):
        self.out['records'][0]['quote'] = 'Q_STORE'
        result = anchor(self.req, canonical(self.out))
        # One emoji, one space, six letters in Önceki, one space = nine codepoints.
        self.assertEqual(result['response']['records'][0]['start'], 9)
        self.assertEqual(result['canonical_mutations'], 0)
        self.assertEqual(result['validation']['records'][0]['lifecycle'], 'candidate')

    def test_missing_empty_repeated_overlapping_and_normalization(self):
        for text, quote in [('abc', ''), ('abc', 'd'), ('x x', 'x'),
                            ('aaaa', 'aa'), ('é', 'e\u0301')]:
            with self.subTest(text=text, quote=quote), self.assertRaises(ValueError):
                unique_span(text, quote)

    def test_whole_batch_atomic_and_raw_unchanged(self):
        original = copy.deepcopy(self.out)
        self.out['records'].append(dict(self.out['records'][0], quote='not present'))
        raw = canonical(self.out)
        with self.assertRaises(ValueError): anchor(self.req, raw)
        self.assertEqual(canonical(self.out), raw)
        self.assertEqual(original['records'][0], self.out['records'][0])

    def test_stale_source_prompt_and_contract(self):
        for field in ('source', 'prompt'):
            changed = copy.deepcopy(self.req)
            if field == 'source': changed[field]['messages'][0]['source_revision'] = 2
            else: changed[field] += 'changed'
            with self.assertRaises(ValueError): anchor(changed, canonical(self.out))
        for change in [dict(request_id='other'), dict(contract_id='other')]:
            with self.assertRaises(ValueError):
                anchor(self.req, canonical(dict(self.out, **change)))

    def test_extra_offsets_unknown_message_and_schema(self):
        for change in [dict(start=0), dict(message_id='elsewhere'), dict(kind='Unknown')]:
            out = copy.deepcopy(self.out); out['records'][0].update(change)
            with self.assertRaises(ValueError): anchor(self.req, canonical(out))

    def test_nested_authority_rejected(self):
        for attrs in [dict(accepted=True), dict(x=[dict(verified=True)]), dict(command='run')]:
            with self.assertRaises(ValueError):
                anchor(self.req, canonical(output(self.req, attrs=attrs)))

    def test_byte_record_attribute_and_duplicate_bounds(self):
        with self.assertRaises(ValueError): anchor(self.req, ' ' * 131073)
        for n in (2, 65):
            out = dict(self.out, records=self.out['records'] * n)
            with self.assertRaises(ValueError): anchor(self.req, canonical(out))
        with self.assertRaises(ValueError):
            anchor(self.req, canonical(output(self.req, attrs=dict(x='a' * 4097))))

    def test_duplicate_json_keys_and_nonfinite(self):
        for text in ['{"format":"a","format":"b"}', '{"x":NaN}']:
            with self.assertRaises(ValueError): anchor(self.req, text)

    def test_abstention_preserves_missing_context(self):
        out = dict(self.out, status='abstain', records=[])
        result = anchor(self.req, canonical(out))
        self.assertEqual(result['validation']['coverage'], 'abstained')
        with self.assertRaises(ValueError):
            anchor(self.req, canonical(dict(self.out, status='abstain')))

    def test_legacy_import_explicit_and_only_offsets_change(self):
        out = dict(self.out, format='decivora-candidates-1'); out.pop('contract_id')
        out['records'][0].update(start=999, end=-1)
        raw = canonical(out)
        with self.assertRaises(ValueError): anchor(self.req, raw)
        result = anchor(self.req, raw, legacy=True)
        repaired = result['response']['records'][0]
        for field in ['kind', 'attributes', 'quote', 'entity_key', 'message_id']:
            self.assertEqual(repaired[field], out['records'][0][field])
        self.assertNotEqual(result['raw_sha256'], result['derived_sha256'])
        self.assertEqual(out['records'][0]['start'], 999)
        out['records'][0]['start'] = True
        with self.assertRaises(ValueError): anchor(self.req, canonical(out), legacy=True)

    def test_recorded_s02_original_still_fails(self):
        req = json.loads((ROOT/'examples/model-smoke/s02-request.json').read_text())
        raw = (ROOT/'docs/quality/model-runs/s02-002-response.txt').read_text()
        with self.assertRaises(ValueError): validate(req, raw)
        result = anchor(req, raw, legacy=True)
        self.assertEqual(len(result['validation']['records']), 11)
        self.assertEqual(len(result['changes']), 10)
        self.assertEqual(result['raw_sha256'],
            'ce4988233436a23c5ec6530f3182163d84c8863d4fea0642bd3673f213fab963')


class TestCandidateEvaluation(unittest.TestCase):
    def setUp(self):
        self.req = request(); self.out = output(self.req); self.rubric = rubric(self.req, self.out)
        self.derived = anchor(self.req, canonical(self.out))['response']

    def test_exact_candidate_fields_and_explicit_unscored(self):
        score = evaluate_candidates(self.req, self.derived, self.rubric)
        self.assertEqual((score['true_positive'], score['false_positive'], score['false_negative']), (1,0,0))
        self.assertEqual(score['review_status'], 'authored_draft')
        self.assertIn('authority', score['unscored'])

    def test_changed_association_false_positive_and_missing(self):
        self.derived['records'][0]['attributes']['option_id'] = 'A'
        score = evaluate_candidates(self.req, self.derived, self.rubric)
        self.assertEqual((score['true_positive'], score['false_positive'], score['false_negative']), (0,1,1))

    def test_canonical_decision_is_not_answer_projection(self):
        self.derived['records'][0]['kind'] = 'Decision'
        self.assertEqual(evaluate_candidates(self.req, self.derived, self.rubric)['true_positive'], 0)

    def test_duplicates_do_not_inflate_recall(self):
        self.derived['records'].append(dict(self.derived['records'][0], entity_key='other'))
        score = evaluate_candidates(self.req, self.derived, self.rubric)
        self.assertEqual((score['true_positive'], score['false_positive']), (1,1))

    def test_empty_and_abstained_not_false_pass(self):
        for status in ['ok', 'abstain']:
            score = evaluate_candidates(self.req, dict(self.derived, status=status, records=[]), self.rubric)
            self.assertEqual(score['false_negative'], 1)
            self.assertIsNone(score['precision'])
            self.assertEqual(score['status'], 'incomplete' if status == 'abstain' else 'evaluated')

    def test_invalid_oracle_binding_authority_duplicate_and_quote(self):
        for change in [dict(request_id='stale'), dict(review_status='invented')]:
            with self.assertRaises(ValueError):
                evaluate_candidates(self.req, self.derived, dict(self.rubric, **change))
        for mutate in ['authority', 'duplicate', 'quote']:
            r = copy.deepcopy(self.rubric)
            if mutate == 'authority': r['expected'][0]['attributes']['verified'] = True
            elif mutate == 'duplicate': r['expected'] *= 2
            else: r['expected'][0]['quote'] = 'not in source'
            with self.assertRaises(ValueError): evaluate_candidates(self.req, self.derived, r)


class TestContractIntegration(unittest.TestCase):
    def test_cli_prepares_and_derives_without_overwriting(self):
        cli = ROOT/'spikes/semantic-chain/anchor_cli.py'
        req = ROOT/'examples/model-smoke/s02-request.json'
        raw = ROOT/'docs/quality/model-runs/s02-002-response.txt'
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)/'derived.json'
            args = [sys.executable, '-B', str(cli), 'derive', '--request', str(req),
                    '--response', str(raw), '--legacy', '--out', str(dest)]
            first = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            result = json.loads(dest.read_text())
            self.assertEqual(result['model_calls'], 0)
            original = dest.read_bytes()
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertEqual(dest.read_bytes(), original)
            prepared = subprocess.run([sys.executable, '-B', str(cli), 'prepare',
                '--request', str(req)], capture_output=True, text=True)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            self.assertEqual(json.loads(prepared.stdout)['dispatch'], 'not_run')

    def test_authored_cases_leave_canonical_state_unchanged(self):
        cases = json.loads((ROOT/'spikes/semantic-chain/fixtures/candidate-contract-cases.json').read_text())
        for case in cases['cases']:
            with self.subTest(case=case['id']), tempfile.TemporaryDirectory() as directory:
                chain = Chain(Path(directory)/'events.db')
                self.addCleanup(chain.close)
                chain.dispatch('seed', dict(decision='markdown', active=['markdown'],
                    tasks={}, criteria=['upload']), 'human', 0, 'seed')
                chain.dispatch('ask', dict(question_id='Q_STORE', option_revision=1,
                    options=dict(A='markdown', B='sqlite')), 'human', 1, 'ask')
                before = chain.snapshot()
                req = prepare(case['source']); packet = prepare_quotes(req)
                out = dict(format=packet['format'], request_id=req['request_id'],
                    contract_id=packet['contract_id'], status='ok', records=case['scripted_records'])
                derived = anchor(req, canonical(out))
                expected = dict(format='decivora-candidate-rubric-1', request_id=req['request_id'],
                    review_status=cases['review_status'], expected=case['expected_candidates'])
                score = evaluate_candidates(req, derived['response'], expected)
                self.assertEqual((score['false_positive'], score['false_negative']), (0, 0))
                proposal = propose(chain, req, canonical(derived['response']))
                self.assertEqual(proposal['status'], case['expected_proposal_status'])
                self.assertEqual(proposal['canonical_mutations'], case['expected_canonical_mutations'])
                self.assertEqual(chain.snapshot(), before)


if __name__ == '__main__': unittest.main()

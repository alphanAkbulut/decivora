"""Reproduce offline adapter evidence; stdout only, no inference, oracle repair or writes."""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from anchors import anchor, prepare_quotes
from candidate_eval import evaluate_candidates
from protocol import canonical, prepare, validate
from bridge import propose

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'spikes/decision-chain'))
from chain import Chain


def run():
    paths = ['spikes/semantic-chain/anchors.py', 'spikes/semantic-chain/anchor_cli.py',
        'spikes/semantic-chain/candidate_eval.py', 'spikes/semantic-chain/test_anchors.py',
        'spikes/semantic-chain/run_anchor_checks.py',
        'spikes/semantic-chain/fixtures/candidate-contract-cases.json',
        'examples/model-smoke/s02-request.json', 'docs/quality/model-runs/s02-002-response.txt']
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    req = json.loads((ROOT/paths[-2]).read_text())
    raw = (ROOT/paths[-1]).read_text()
    try:
        validate(req, raw)
    except ValueError as error:
        original = dict(status='rejected', error=str(error))
    else:
        raise AssertionError('historical output unexpectedly valid')
    derived = anchor(req, raw, legacy=True)
    fixtures = json.loads((ROOT/paths[-3]).read_text())
    cases = []
    for case in fixtures['cases']:
        request = prepare(case['source']); packet = prepare_quotes(request)
        scripted = dict(format=packet['format'], request_id=request['request_id'],
            contract_id=packet['contract_id'], status='ok', records=case['scripted_records'])
        response = anchor(request, canonical(scripted))['response']
        rubric = dict(format='decivora-candidate-rubric-1', request_id=request['request_id'],
            review_status=fixtures['review_status'], expected=case['expected_candidates'])
        score = evaluate_candidates(request, response, rubric)
        with tempfile.TemporaryDirectory() as directory:
            chain = Chain(Path(directory)/'events.db')
            try:
                chain.dispatch('seed', dict(decision='markdown', active=['markdown'], tasks={},
                    criteria=['upload']), 'human', 0, 'seed')
                chain.dispatch('ask', dict(question_id='Q_STORE', option_revision=1,
                    options=dict(A='markdown', B='sqlite')), 'human', 1, 'ask')
                before = chain.snapshot()
                proposal = propose(chain, request, canonical(response))
                unchanged = chain.snapshot() == before
            finally:
                chain.close()
        assert proposal['status'] == case['expected_proposal_status'] and unchanged
        assert score['false_positive'] == score['false_negative'] == 0
        cases.append(dict(case_id=case['id'], request_id=request['request_id'],
            score=score, proposal_status=proposal['status'], canonical_state_unchanged=unchanged))
    return dict(format='decivora-anchor-checks-1', scope='offline_adapter_and_scripted_contract',
        hashes=hashes, original=original, derived=dict(request_id=derived['request_id'],
        raw_sha256=derived['raw_sha256'], derived_sha256=derived['derived_sha256'],
        replaced_offsets=len(derived['changes']), validated_candidates=len(derived['validation']['records'])),
        fixture_cases=cases, model_calls=0, canonical_mutations=0,
        usage=None, semantic_quality='not_measured', production_release_gate='open')


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2, allow_nan=False))

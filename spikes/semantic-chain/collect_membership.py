"""Offline multi-answer diagnostics from immutable MEMBERSHIP-003; no model or selection."""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'decision-chain'))
from chain import Chain
from bridge import collect_proposals
from membership_typed import derive_typed
from protocol import canonical, strict_json

ROOT = Path(__file__).resolve().parents[2]
RAW_SHA = '0adebd7574175b5c2b4508b926930da78a6ba61947ea79028b8695a1e2ebf3cb'
# Authored fixture current state, not an inference or actual user approval.
QUESTIONS = [('Q_STORE', 2, {'A': 'D_SQLITE', 'B': 'D_POSTGRES'}),
             ('Q_UI', 1, {'A': 'board', 'B': 'timeline'})]


def run():
    request_path = ROOT / 'examples/adversarial-smoke/requests.json'
    raw_path = ROOT / 'docs/quality/model-runs/membership-003-response.txt'
    raw = raw_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != RAW_SHA:
        raise ValueError('saved model output changed')
    requests = strict_json(request_path.read_text())
    derived = derive_typed(requests, raw.decode('utf-8'))
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (request, item) in enumerate(zip(requests, derived['derived'])):
            chain = Chain(Path(tmp) / f'{i}.db')
            try:
                chain.dispatch('seed', dict(decision='fixture_initial', active=['fixture_initial'],
                    tasks={}, criteria=['rollback', 'migration']), 'human', 0, 'seed')
                qid, revision, options = QUESTIONS[i]
                chain.dispatch('ask', dict(question_id=qid, option_revision=revision,
                    options=options), 'human', 1, 'ask')
                before = chain.snapshot()
                report = collect_proposals(chain, request, canonical(item['response']),
                                           request['source']['project_id'])
                same = chain.snapshot() == before
                if not same:
                    raise AssertionError('collector changed fixture projection')
                results.append(dict(collection=report, projection_unchanged=same,
                                    question_still_pending=chain.snapshot()['question']['state'] == 'pending'))
            finally:
                chain.close()
    paths = ['spikes/semantic-chain/bridge.py', 'spikes/semantic-chain/collect_membership.py',
             'spikes/semantic-chain/protocol.py', 'spikes/semantic-chain/membership_typed.py',
             'examples/adversarial-smoke/requests.json',
             'docs/quality/model-runs/membership-003-response.txt']
    return dict(experiment_id='PROPOSAL-COLLECTION-001', source_run='MEMBERSHIP-003',
                raw_sha256=RAW_SHA, results=results, canonical_mutations=0,
                model_dispatches=0, selection_dispatches=0, paid_api_calls=0,
                production_runtime=False, single_current_question_per_fixture=True,
                expected_statuses_authored=True, human_gold=False,
                hashes={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', help='new report path; existing files are never overwritten')
    args = parser.parse_args()
    body = json.dumps(run(), ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.out:
        with Path(args.out).open('x', encoding='utf-8') as stream:
            stream.write(body)
    else:
        print(body, end='')

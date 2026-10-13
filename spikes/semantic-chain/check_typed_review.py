"""Independent saved draft comparison; no provider call or raw-output repair."""
import hashlib
import json

from protocol import canonical
from receiver_next import evaluate
from receiver_smoke import ROOT
from typed_review import build, VERSION


def check():
    folder = ROOT / 'examples/receiver-next-smoke'
    request = json.loads((folder / 'request.json').read_text())
    context = json.loads((folder / 'review-context.fixture.json').read_text())
    paths = [ROOT / f'docs/quality/model-runs/receiver-00{i}-response.txt' for i in (1, 2)]
    raw_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    generated = build(request, context)  # Source-only transformation before reading oracle.
    oracle = json.loads((folder / 'expected.json').read_text())
    draft_score = evaluate(request, canonical(generated['response']), oracle)
    if draft_score['status'] != 'passed_draft' or draft_score['action_score'] != dict(true_positive=6, false_positive=0, false_negative=0):
        raise ValueError('deterministic typed review differs from independent draft expectations')
    if any(hashlib.sha256(p.read_bytes()).hexdigest() != raw_hashes[str(p.relative_to(ROOT))] for p in paths):
        raise ValueError('historical model raw changed')
    files = ['spikes/semantic-chain/' + n for n in ('typed_review.py', 'test_typed_review.py', 'check_typed_review.py')]
    files += ['examples/receiver-next-smoke/' + n for n in ('request.json', 'review-context.fixture.json', 'expected.json')]
    return dict(status='passed_local_typed_transform', version=VERSION,
        generated_review=generated, independent_authored_draft_comparison=draft_score,
        historical_raw_sha256_unchanged=raw_hashes,
        file_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
        tested_scope='two exposed synthetic snapshots; six already typed records',
        human_gold=False, holdout=False, model_quality='not_evaluated_by_this_transform',
        semantic_extraction='not_implemented_by_this_transform',
        model_dispatches=0, paid_api_calls=0, canonical_mutations=0, usage=None,
        token_or_money_savings='not_measured; no new inference needed for this transformation')


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2, allow_nan=False))

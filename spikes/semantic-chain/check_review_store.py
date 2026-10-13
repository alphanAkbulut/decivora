"""Reproduce local durable snapshot example; never opens a user transcript/database."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile

from receiver_smoke import ROOT
from review_store import ReviewStore, VERSION


def check():
    folder = ROOT / 'examples/receiver-next-smoke'
    request = json.loads((folder / 'request.json').read_text())
    context = json.loads((folder / 'review-context.fixture.json').read_text())
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'review.sqlite'
        store = ReviewStore(path)
        try:
            receipt = store.store(request, context)
            duplicate = store.store(request, context)
            before = store.current(request, context)
        finally:
            store.close()
        store = ReviewStore(path)
        try:
            resumed = store.current(request, context)
            if resumed != before or duplicate['record_id'] != receipt['record_id'] or duplicate['duplicate'] is not True:
                raise ValueError('restart/idempotency example failed')
            changed = copy.deepcopy(context)
            changed['atomic_groups'] = [list(context['projects'])]
            stale_view = store.current(request, changed)
            if stale_view['status'] != 'current_snapshot_not_stored' or stale_view['review'] is not None:
                raise ValueError('older context promoted to current')
            changed['projects'][list(context['projects'])[0]]['review_access'] = False
            try:
                store.current(request, changed)
            except ValueError:
                revoked_rejected = True
            else:
                raise ValueError('revoked context read allowed')
        finally:
            store.close()
    files = ['spikes/semantic-chain/' + n for n in ('review_store.py', 'test_review_store.py', 'check_review_store.py')]
    files += ['examples/receiver-next-smoke/' + n for n in ('request.json', 'review-context.fixture.json')]
    return dict(status='passed_local_review_persistence', version=VERSION,
        first_receipt=receipt, duplicate_receipt=duplicate, resumed_review=resumed,
        changed_context_view=stale_view, revoked_access_rejected=revoked_rejected,
        file_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
        tested_scope='temporary SQLite database; two fixed synthetic projects; restart, not power-loss recovery',
        input_origin='model-reported typed source facts plus caller authority fixture',
        canonical_mutations=0, model_dispatches=0, paid_api_calls=0,
        production_authorization=False, human_gold=False,
        human_reply_resolution='not_implemented', host_capture='not_tested', usage=None)


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2, allow_nan=False))

"""Reproduce a synthetic explicit delayed reply, restart and conflict; no inference."""
import hashlib
import json
from pathlib import Path
import tempfile

from protocol import digest
from receiver_smoke import ROOT
from reply_store import ReplyStore, VERSION


def check():
    request = json.loads((ROOT / 'examples/receiver-next-smoke/request.json').read_text())
    context = json.loads((ROOT / 'examples/receiver-next-smoke/review-context.fixture.json').read_text())
    reply = json.loads((ROOT / 'examples/durable-reply-smoke/reply.fixture.json').read_text())
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'reply.sqlite'
        store = ReplyStore(path)
        try:
            record = store.snapshots.store(request, context)['record_id']
            before = store.pending(request, context, record)
            cid = before['clarifications'][0]['descriptor']['clarification_id']
            receipt = store.receive(request, context, record, cid, reply)
            duplicate = store.receive(request, context, record, cid, reply)
        finally:
            store.close()
        store = ReplyStore(path)
        try:
            after = store.pending(request, context, record)
            if before['clarifications'][0]['status'] != 'awaiting_reply' or after['clarifications'][0]['status'] != 'pending_trusted_selection':
                raise ValueError('late reply failed to associate after restart')
            if after['clarifications'][0]['approved_real_decision'] or after['clarifications'][0]['clarification_resolved']:
                raise ValueError('reply escalated into approval')
            other = dict(reply, source_message_id='late-human-02', option_id='A', text='For Q_UI revision 1, A: board.')
            other['source_sha256'] = digest({k: other[k] for k in ('source_message_id', 'source_revision', 'text', 'actor_type')})
            store.receive(request, context, record, cid, other)
            conflict = store.pending(request, context, record)
            if conflict['clarifications'][0]['status'] != 'conflicting_reply_proposals':
                raise ValueError('contradictory replies silently selected')
        finally:
            store.close()
    paths = ['spikes/semantic-chain/' + p for p in ('reply_store.py', 'test_reply_store.py', 'check_reply_store.py')]
    paths += ['examples/durable-reply-smoke/reply.fixture.json', 'examples/receiver-next-smoke/request.json',
              'examples/receiver-next-smoke/review-context.fixture.json']
    return dict(status='passed_local_durable_reply_proposals', version=VERSION,
        pending_before=before, reply_receipt=receipt, duplicate_receipt=duplicate,
        pending_after_reopen=after, conflicting_replies=conflict,
        file_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
        scope='two pinned synthetic projects; explicit transport fixture fields, not text inference',
        actual_human_approval=False, canonical_mutations=0, model_dispatches=0, paid_api_calls=0,
        production_authorization=False, host_capture='not_tested', usage=None)


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2, allow_nan=False))

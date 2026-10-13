"""P0 durable explicit reply proposals; human actor/access are transport fixtures.

No free-text guessing, canonical approval, task execution, or model dispatch.
Adds its own versioned append-only table to a validated P0 review snapshot DB.
"""
import argparse
import copy
import json
from pathlib import Path

from protocol import canonical, digest, strict_json
from project_review import clarification_records
from project_review_next import check_context
from review_store import ReviewStore

VERSION = 'durable-clarification-reply-1'


def associate_reply(request, context, clarification_id, reply):
    views = check_context(request, context)
    fields = {'clarification_id', 'project_id', 'question_id', 'question_revision', 'option_id',
              'source_message_id', 'source_revision', 'text', 'actor_type', 'source_sha256'}
    if not isinstance(reply, dict) or set(reply) != fields or len(canonical(reply).encode()) > 4096:
        raise ValueError('invalid explicit reply fields or byte limit')
    source = {k: reply[k] for k in ('source_message_id', 'source_revision', 'text', 'actor_type')}
    if (reply['actor_type'] != 'human_owner' or type(reply['source_revision']) is not int
            or reply['source_revision'] < 1 or type(reply['source_message_id']) is not str
            or not reply['source_message_id'] or type(reply['text']) is not str or not reply['text']
            or reply['source_sha256'] != digest(source)):
        raise ValueError('invalid human-fixture reply source')
    pid = reply['project_id']
    if type(pid) is not str or pid not in views or reply['clarification_id'] != clarification_id:
        raise ValueError('foreign clarification reply')
    view = views[pid]
    pending = {p['clarification_id']: p for p in clarification_records(request, view)}
    if clarification_id not in pending:
        raise ValueError('unknown/stale clarification id')
    if (type(reply['question_revision']) is not int or reply['question_revision'] < 1
            or type(reply['question_id']) is not str or type(reply['option_id']) is not str):
        raise ValueError('invalid question association types')
    choices = [p for p in pending[clarification_id]['question_presentations']
               if p['question_id'] == reply['question_id'] and p['revision'] == reply['question_revision']
               and reply['option_id'] in p['options']]
    if len(choices) != 1:
        raise ValueError('stale/unknown question revision or option')
    current = view['fixture_state'].get('question')
    matches = current and current['question_id'] == reply['question_id']
    if matches and (current['option_revision'] != reply['question_revision'] or current['state'] != 'pending'):
        raise ValueError('question changed or already resolved')
    return dict(format=VERSION, request_id=request['request_id'], context_sha256=digest(context),
        binding=copy.deepcopy(view['binding']), clarification_id=clarification_id, project_id=pid,
        question_id=reply['question_id'], question_revision=reply['question_revision'], option_id=reply['option_id'],
        source_message_id=reply['source_message_id'], source_revision=reply['source_revision'], source_sha256=reply['source_sha256'],
        status='pending_trusted_selection' if matches else 'needs_question_context',
        clarification_resolved=False, approved_real_decision=False,
        execution_authorized=False, production_authorization=False)


def source_key(reply):
    return digest({k: reply[k] for k in ('project_id', 'source_message_id', 'source_revision')})


class ReplyStore:
    def __init__(self, path):
        self.snapshots = ReviewStore(path)
        self.conn = self.snapshots.conn
        try:
            self.conn.execute('PRAGMA foreign_keys=ON')
            self.conn.execute('BEGIN IMMEDIATE')
            names = {r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'reply_meta' not in names:
                if 'reply_proposals' in names:
                    raise ValueError('partial reply schema not supported')
                self.conn.execute('CREATE TABLE reply_meta(version TEXT NOT NULL)')
                self.conn.execute('INSERT INTO reply_meta VALUES(?)', (VERSION,))
                self.conn.execute('''CREATE TABLE reply_proposals(seq INTEGER PRIMARY KEY,
                    source_key TEXT NOT NULL UNIQUE, record_id TEXT NOT NULL REFERENCES reviews(record_id),
                    clarification_id TEXT NOT NULL, payload_sha256 TEXT NOT NULL, payload TEXT NOT NULL)''')
                for action in ('UPDATE', 'DELETE'):
                    self.conn.execute(f"CREATE TRIGGER replies_no_{action.lower()} BEFORE {action} ON reply_proposals BEGIN SELECT RAISE(ABORT,'append-only reply proposal'); END;")
            versions = self.conn.execute('SELECT version FROM reply_meta').fetchall()
            if len(versions) != 1 or versions[0][0] != VERSION:
                raise ValueError('unsupported reply schema version')
            self.conn.execute('COMMIT')
        except BaseException:
            if self.conn.in_transaction:
                self.conn.execute('ROLLBACK')
            self.snapshots.close()
            raise

    def close(self):
        self.snapshots.close()

    def _current(self, request, context, record_id):
        snapshot = self.snapshots.current(request, context)
        if snapshot['status'] != 'current_review_snapshot' or snapshot['record_id'] != record_id:
            raise ValueError('reply requires stored current snapshot')
        return snapshot['review']

    def _payload(self, request, context, record_id, clarification_id, reply):
        self._current(request, context, record_id)
        association = associate_reply(request, context, clarification_id, reply)
        return dict(record_id=record_id, reply=copy.deepcopy(reply), association=association)

    def _checked(self, row, request, context, record_id):
        body = strict_json(row['payload'])
        if not isinstance(body, dict) or set(body) != {'record_id', 'reply', 'association'}:
            raise ValueError('stored reply payload invalid')
        expected = self._payload(request, context, record_id, row['clarification_id'], body['reply'])
        if (row['record_id'] != record_id or canonical(body) != canonical(expected)
                or row['payload_sha256'] != digest(body) or row['source_key'] != source_key(body['reply'])):
            raise ValueError('stored reply binding or integrity mismatch')
        return body

    def receive(self, request, context, record_id, clarification_id, reply):
        body = self._payload(request, context, record_id, clarification_id, reply)
        key = source_key(reply)
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            old = self.conn.execute('SELECT * FROM reply_proposals WHERE source_key=?', (key,)).fetchone()
            if old is not None:
                stored = self._checked(old, request, context, record_id)
                if canonical(stored) != canonical(body):
                    raise ValueError('source reply idempotency conflict')
            else:
                self.conn.execute('INSERT INTO reply_proposals(source_key,record_id,clarification_id,payload_sha256,payload) VALUES(?,?,?,?,?)',
                    (key, record_id, clarification_id, digest(body), canonical(body)))
            self.conn.execute('COMMIT')
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise
        return dict(format=VERSION, reply_receipt_id=key, duplicate=old is not None,
            association=body['association'], canonical_mutations=0, model_dispatches=0, paid_api_calls=0)

    def pending(self, request, context, record_id):
        review = self._current(request, context, record_id)
        rows = self.conn.execute('SELECT * FROM reply_proposals WHERE record_id=? ORDER BY seq', (record_id,)).fetchall()
        receipts = [self._checked(r, request, context, record_id) for r in rows]
        items = []
        for project in review['project_review']['projects']:
            for descriptor in project['clarifications']:
                answers = [r['association'] for r in receipts if r['association']['clarification_id'] == descriptor['clarification_id']]
                selections = {(a['question_id'], a['question_revision'], a['option_id']) for a in answers}
                status = 'awaiting_reply'
                if len(selections) > 1:
                    status = 'conflicting_reply_proposals'
                elif answers:
                    status = 'pending_trusted_selection' if all(a['status'] == 'pending_trusted_selection' for a in answers) else 'needs_question_context'
                items.append(dict(descriptor=descriptor, status=status, answer_proposals=answers,
                                  clarification_resolved=False, approved_real_decision=False))
        return dict(format=VERSION, record_id=record_id, clarifications=items,
            canonical_mutations=0, model_dispatches=0, paid_api_calls=0,
            execution_authorized=False, production_authorization=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['receive', 'pending'])
    parser.add_argument('--db', required=True, type=Path)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--context', required=True, type=Path)
    parser.add_argument('--record-id', required=True)
    parser.add_argument('--reply', type=Path)
    args = parser.parse_args()
    if not args.db.exists():
        parser.error('existing stored review DB required')
    request, context = strict_json(args.request.read_text()), strict_json(args.context.read_text())
    check_context(request, context)  # No DB extension for revoked input.
    if (args.action == 'receive') != (args.reply is not None):
        parser.error('receive requires reply; pending does not read one')
    store = ReplyStore(args.db)
    try:
        if args.action == 'receive':
            reply = strict_json(args.reply.read_text(), max_bytes=4096)
            result = store.receive(request, context, args.record_id, reply['clarification_id'], reply)
        else:
            result = store.pending(request, context, args.record_id)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    finally:
        store.close()

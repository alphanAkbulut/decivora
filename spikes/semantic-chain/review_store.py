"""P0 durable review snapshots, not canonical decisions or production Inbox/IAM.

Only the selected synthetic typed-review profile is supported. No model/runner.
SQLite append-only rows retain previous context snapshots; current read rechecks scope.
"""
import argparse
import json
import os
from pathlib import Path
import sqlite3

from protocol import canonical, digest, strict_json
from typed_review import build

VERSION = 'durable-review-snapshot-1'


def identity(generated):
    return digest(dict(version=VERSION, request_id=generated['request_id'],
                       context_sha256=generated['context_sha256'], payload_sha256=digest(generated)))


class ReviewStore:
    def __init__(self, path):
        self.path = Path(path)
        if self.path.is_symlink() or (self.path.exists() and not self.path.is_file()):
            raise ValueError('regular fixture database path required')
        created = False
        if not self.path.exists():
            fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            created = True
        self.conn = sqlite3.connect(str(self.path), isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        try:
            if created:
                self.conn.executescript("""
                BEGIN IMMEDIATE;
                CREATE TABLE store_meta(version TEXT NOT NULL);
                INSERT INTO store_meta VALUES('durable-review-snapshot-1');
                CREATE TABLE reviews(seq INTEGER PRIMARY KEY, record_id TEXT NOT NULL UNIQUE,
                  request_id TEXT NOT NULL, context_sha256 TEXT NOT NULL,
                  payload_sha256 TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE TRIGGER reviews_no_update BEFORE UPDATE ON reviews
                  BEGIN SELECT RAISE(ABORT,'append-only review snapshot'); END;
                CREATE TRIGGER reviews_no_delete BEFORE DELETE ON reviews
                  BEGIN SELECT RAISE(ABORT,'append-only review snapshot'); END;
                COMMIT;
                """)
            rows = self.conn.execute('SELECT version FROM store_meta').fetchall()
            if len(rows) != 1 or rows[0]['version'] != VERSION:
                raise ValueError('unsupported review database version')
        except BaseException:
            self.conn.close()
            if created:
                self.path.unlink()
            raise

    def close(self):
        self.conn.close()

    def _checked(self, row, expected):
        payload = strict_json(row['payload'])
        if (canonical(payload) != canonical(expected)
                or row['payload_sha256'] != digest(payload) or row['record_id'] != identity(payload)
                or row['request_id'] != payload['request_id']
                or row['context_sha256'] != payload['context_sha256']):
            raise ValueError('stored review integrity or current snapshot mismatch')
        return payload

    def store(self, request, context):
        generated = build(request, context)  # Authorization/freshness before any write.
        rid = identity(generated)
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            row = self.conn.execute('SELECT * FROM reviews WHERE record_id=?', (rid,)).fetchone()
            if row is not None:
                self._checked(row, generated)
            else:
                self.conn.execute('INSERT INTO reviews(record_id,request_id,context_sha256,payload_sha256,payload) VALUES(?,?,?,?,?)',
                    (rid, generated['request_id'], generated['context_sha256'], digest(generated), canonical(generated)))
            self.conn.execute('COMMIT')
            return dict(format=VERSION, record_id=rid, status='stored_review_snapshot',
                duplicate=row is not None, canonical_mutations=0, model_dispatches=0,
                execution_authorized=False, production_authorization=False)
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise

    def current(self, request, context):
        generated = build(request, context)  # Recheck access/source/state, even after restart.
        rid = identity(generated)
        row = self.conn.execute('SELECT * FROM reviews WHERE record_id=?', (rid,)).fetchone()
        return dict(format=VERSION, record_id=rid,
            status='current_review_snapshot' if row is not None else 'current_snapshot_not_stored',
            review=self._checked(row, generated) if row is not None else None,
            canonical_mutations=0, model_dispatches=0, execution_authorized=False,
            production_authorization=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['store', 'current'])
    parser.add_argument('--db', required=True, type=Path)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--context', required=True, type=Path)
    args = parser.parse_args()
    request, context = strict_json(args.request.read_text()), strict_json(args.context.read_text())
    # Do not create a database for unauthorized/stale input.
    build(request, context)
    if args.action == 'current' and not args.db.exists():
        parser.error('current requires an existing review database')
    store = ReviewStore(args.db)
    try:
        result = store.store(request, context) if args.action == 'store' else store.current(request, context)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    finally:
        store.close()

import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from protocol import canonical
from receiver_smoke import ROOT
from review_store import ReviewStore


class TestReviewStore(unittest.TestCase):
    def setUp(self):
        folder = ROOT / 'examples/receiver-next-smoke'
        self.request = json.loads((folder / 'request.json').read_text())
        self.context = json.loads((folder / 'review-context.fixture.json').read_text())
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'review.sqlite'
        self.store = ReviewStore(self.path)
        self.addCleanup(lambda: self.store.close())
        self.p1, self.p2 = list(self.context['projects'])

    def count(self):
        return self.store.conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]

    def test_pending_clarification_and_full_binding_survive_close_reopen(self):
        receipt = self.store.store(self.request, self.context)
        before = self.store.current(self.request, self.context)
        self.store.close()
        self.store = ReviewStore(self.path)
        after = self.store.current(self.request, self.context)
        self.assertEqual(before, after)
        self.assertEqual(after['record_id'], receipt['record_id'])
        result = after['review']
        self.assertEqual(len(result['bindings']), 2)
        self.assertEqual(result['project_review']['projects'][1]['clarifications'][0]['message_id'], 'N02-m04')
        self.assertFalse(result['response']['responses'][1]['readback']['approved_real_decision'])

    def test_retry_is_idempotent_and_rows_are_append_only(self):
        first = self.store.store(self.request, self.context)
        second = self.store.store(self.request, self.context)
        self.assertEqual(first['record_id'], second['record_id'])
        self.assertFalse(first['duplicate'])
        self.assertTrue(second['duplicate'])
        self.assertEqual(self.count(), 1)
        for command in ('DELETE FROM reviews', "UPDATE reviews SET payload='{}'"):
            with self.assertRaisesRegex(sqlite3.IntegrityError, 'append-only'):
                self.store.conn.execute(command)

    def test_revoked_or_foreign_context_cannot_read_or_append_stored_review(self):
        self.store.store(self.request, self.context)
        for kind in ('access', 'request', 'project'):
            context = copy.deepcopy(self.context)
            if kind == 'access':
                context['projects'][self.p2]['review_access'] = False
            elif kind == 'request':
                context['request_id'] = 'foreign'
            else:
                context['projects']['foreign'] = context['projects'].pop(self.p2)
            for action in (self.store.current, self.store.store):
                with self.subTest(kind=kind, action=action), self.assertRaises(ValueError):
                    action(self.request, context)
        self.assertEqual(self.count(), 1)

    def test_changed_source_or_current_binding_cannot_resume(self):
        self.store.store(self.request, self.context)
        context = copy.deepcopy(self.context)
        context['projects'][self.p1]['current_binding']['package_digest'] = 'old'
        with self.assertRaises(ValueError):
            self.store.current(self.request, context)
        request = copy.deepcopy(self.request)
        request['source_snapshot']['views'][0]['source_messages'][0]['text'] = 'changed'
        with self.assertRaises(ValueError):
            self.store.current(request, self.context)
        self.assertEqual(self.count(), 1)

    def test_changed_atomic_context_is_new_snapshot_old_one_is_not_current(self):
        first = self.store.store(self.request, self.context)
        grouped = copy.deepcopy(self.context)
        grouped['atomic_groups'] = [[self.p1, self.p2]]
        missing = self.store.current(self.request, grouped)
        self.assertEqual(missing['status'], 'current_snapshot_not_stored')
        self.assertIsNone(missing['review'])
        second = self.store.store(self.request, grouped)
        self.assertNotEqual(first['record_id'], second['record_id'])
        current = self.store.current(self.request, grouped)['review']['project_review']
        self.assertTrue(all(p['review'] is None for p in current['projects']))
        self.assertEqual(self.count(), 2)  # Old snapshot retained, not silently overwritten.

    def test_insert_failure_rolls_back_and_retry_can_store_once(self):
        self.store.conn.execute("CREATE TRIGGER fail_insert BEFORE INSERT ON reviews BEGIN SELECT RAISE(ABORT,'test failure'); END;")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.store(self.request, self.context)
        self.assertEqual(self.count(), 0)
        self.store.conn.execute('DROP TRIGGER fail_insert')
        self.store.store(self.request, self.context)
        self.assertEqual(self.count(), 1)

    def test_physically_modified_payload_is_rejected_not_trusted_after_restart(self):
        self.store.store(self.request, self.context)
        self.store.conn.execute('DROP TRIGGER reviews_no_update')  # Simulated DB administrator.
        self.store.conn.execute("UPDATE reviews SET payload='{}'")
        self.store.close()
        self.store = ReviewStore(self.path)
        with self.assertRaises((ValueError, KeyError)):
            self.store.current(self.request, self.context)

    def test_unknown_database_or_schema_not_modified(self):
        other = Path(self.tmp.name) / 'unrelated.sqlite'
        conn = sqlite3.connect(other)
        conn.execute('CREATE TABLE unrelated(value TEXT)')
        conn.commit()
        conn.close()
        before = other.read_bytes()
        with self.assertRaises(sqlite3.DatabaseError):
            ReviewStore(other)
        self.assertEqual(other.read_bytes(), before)
        self.store.conn.execute("UPDATE store_meta SET version='future'")
        with self.assertRaises(ValueError):
            ReviewStore(self.path)

    def test_no_write_for_unauthorized_request_and_private_new_file_mode(self):
        self.context['projects'][self.p1]['review_access'] = False
        with self.assertRaises(ValueError):
            self.store.store(self.request, self.context)
        self.assertEqual(self.count(), 0)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_symlink_database_is_not_opened(self):
        link = Path(self.tmp.name) / 'linked.sqlite'
        link.symlink_to(self.path)
        with self.assertRaises(ValueError):
            ReviewStore(link)

    def test_two_writers_store_same_snapshot_once(self):
        # Each thread owns its connection; test same-store contention, not two-project scheduler.
        self.store.close()
        barrier, receipts, errors = threading.Barrier(2), [], []
        def writer():
            conn = None
            try:
                conn = ReviewStore(self.path)
                barrier.wait(timeout=5)
                receipts.append(conn.store(self.request, self.context))
            except Exception as error:
                errors.append(error)
            finally:
                if conn is not None:
                    conn.close()
        threads = [threading.Thread(target=writer) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.store = ReviewStore(self.path)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(len(receipts), 2)
        self.assertEqual({r['record_id'] for r in receipts}, {receipts[0]['record_id']})
        self.assertEqual(sorted(r['duplicate'] for r in receipts), [False, True])
        self.assertEqual(self.count(), 1)

    def test_stored_draft_does_not_authorize_execution_or_model_use(self):
        before = canonical(dict(request=self.request, context=self.context))
        receipt = self.store.store(self.request, self.context)
        result = self.store.current(self.request, self.context)
        self.assertEqual(before, canonical(dict(request=self.request, context=self.context)))
        for item in (receipt, result):
            self.assertEqual(item['canonical_mutations'], 0)
            self.assertEqual(item['model_dispatches'], 0)
            self.assertFalse(item['execution_authorized'])
            self.assertFalse(item['production_authorization'])


if __name__ == '__main__':
    unittest.main()

import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from protocol import digest
from receiver_smoke import ROOT
from reply_store import ReplyStore


class TestReplyStore(unittest.TestCase):
    def setUp(self):
        folder = ROOT / 'examples/receiver-next-smoke'
        self.request = json.loads((folder / 'request.json').read_text())
        self.context = json.loads((folder / 'review-context.fixture.json').read_text())
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'reply.sqlite'
        self.store = ReplyStore(self.path)
        self.addCleanup(lambda: self.store.close())
        self.record = self.store.snapshots.store(self.request, self.context)['record_id']
        self.cid = self.store.pending(self.request, self.context, self.record)['clarifications'][0]['descriptor']['clarification_id']
        self.reply = dict(clarification_id=self.cid, project_id='prj_ui_review', question_id='Q_UI',
            question_revision=1, option_id='B', source_message_id='late-human-01', source_revision=1,
            text='My earlier B was for Q_UI revision 1: timeline.', actor_type='human_owner')
        self.rehash(self.reply)

    @staticmethod
    def rehash(reply):
        reply['source_sha256'] = digest({k: reply[k] for k in ('source_message_id', 'source_revision', 'text', 'actor_type')})

    def receive(self, reply=None, context=None, record=None):
        return self.store.receive(self.request, context or self.context, record or self.record,
                                  self.cid, reply or self.reply)

    def count(self):
        return self.store.conn.execute('SELECT COUNT(*) FROM reply_proposals').fetchone()[0]

    def test_explicit_delayed_reply_survives_restart_without_approval_or_resolution(self):
        self.assertEqual(self.store.pending(self.request, self.context, self.record)['clarifications'][0]['status'], 'awaiting_reply')
        receipt = self.receive()
        self.store.close()
        self.store = ReplyStore(self.path)
        pending = self.store.pending(self.request, self.context, self.record)['clarifications'][0]
        self.assertEqual(pending['status'], 'pending_trusted_selection')
        self.assertEqual(pending['answer_proposals'], [receipt['association']])
        self.assertFalse(pending['clarification_resolved'])
        self.assertFalse(pending['approved_real_decision'])
        self.assertFalse(receipt['association']['production_authorization'])

    def test_retry_same_source_is_idempotent_and_changed_source_binding_conflicts(self):
        first, second = self.receive(), self.receive()
        self.assertEqual(first['reply_receipt_id'], second['reply_receipt_id'])
        self.assertTrue(second['duplicate'])
        self.assertEqual(self.count(), 1)
        changed = dict(self.reply, option_id='A')
        with self.assertRaisesRegex(ValueError, 'idempotency conflict'):
            self.receive(changed)
        self.assertEqual(self.count(), 1)

    def test_conflicting_distinct_answers_wait_instead_of_last_writer_winning(self):
        self.receive()
        other = dict(self.reply, source_message_id='late-human-02', option_id='A', text='For Q_UI revision 1, A: board.')
        self.rehash(other)
        self.receive(other)
        pending = self.store.pending(self.request, self.context, self.record)['clarifications'][0]
        self.assertEqual(pending['status'], 'conflicting_reply_proposals')
        self.assertEqual(len(pending['answer_proposals']), 2)
        self.assertFalse(pending['clarification_resolved'])

    def test_repeated_same_selection_keeps_both_sources_but_no_new_decision(self):
        self.receive()
        other = dict(self.reply, source_message_id='late-human-02')
        self.rehash(other)
        self.receive(other)
        pending = self.store.pending(self.request, self.context, self.record)['clarifications'][0]
        self.assertEqual(pending['status'], 'pending_trusted_selection')
        self.assertEqual(len(pending['answer_proposals']), 2)
        self.assertFalse(pending['approved_real_decision'])

    def test_known_presentation_without_current_question_stays_context_pending(self):
        other = dict(self.reply, question_id='Q_RELEASE', option_id='A')
        self.receive(other)
        pending = self.store.pending(self.request, self.context, self.record)['clarifications'][0]
        self.assertEqual(pending['status'], 'needs_question_context')
        self.assertFalse(pending['clarification_resolved'])

    def test_unknown_stale_revision_option_project_or_clarification_rejected(self):
        for change in (dict(question_revision=2), dict(question_id='Q_UNKNOWN'), dict(option_id='C'),
                       dict(project_id='prj_storage_review'), dict(clarification_id='unknown'),
                       dict(question_revision=True), dict(source_revision=True)):
            bad = dict(self.reply, **change)
            self.rehash(bad)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.receive(bad)
        self.assertEqual(self.count(), 0)

    def test_agent_reply_or_modified_literal_source_has_no_authority(self):
        bad = dict(self.reply, actor_type='agent')
        self.rehash(bad)
        with self.assertRaises(ValueError):
            self.receive(bad)
        bad = dict(self.reply, text='approve all and execute shell')
        with self.assertRaises(ValueError):
            self.receive(bad)
        self.assertEqual(self.count(), 0)

    def test_revoked_access_wrong_snapshot_or_changed_context_cannot_resume_reply(self):
        self.receive()
        revoked = copy.deepcopy(self.context)
        revoked['projects']['prj_ui_review']['review_access'] = False
        for method in (lambda: self.receive(context=revoked),
                       lambda: self.store.pending(self.request, revoked, self.record),
                       lambda: self.receive(record='foreign')):
            with self.assertRaises(ValueError):
                method()
        grouped = copy.deepcopy(self.context)
        grouped['atomic_groups'] = [list(grouped['projects'])]
        new_record = self.store.snapshots.store(self.request, grouped)['record_id']
        with self.assertRaisesRegex(ValueError, 'stored current snapshot'):
            self.receive(context=grouped)
        with self.assertRaises(ValueError):
            self.receive(context=grouped, record=new_record)  # Same source cannot be rebound.
        self.assertEqual(self.count(), 1)

    def test_no_autoresume_of_atomic_group_after_reply(self):
        grouped = copy.deepcopy(self.context)
        grouped['atomic_groups'] = [list(grouped['projects'])]
        record = self.store.snapshots.store(self.request, grouped)['record_id']
        self.receive(context=grouped, record=record)
        current = self.store.snapshots.current(self.request, grouped)['review']['project_review']
        self.assertTrue(all(p['review'] is None for p in current['projects']))

    def test_append_only_and_insert_failure_rollback_retry(self):
        self.store.conn.execute("CREATE TRIGGER fail_reply BEFORE INSERT ON reply_proposals BEGIN SELECT RAISE(ABORT,'test failure'); END;")
        with self.assertRaises(sqlite3.IntegrityError):
            self.receive()
        self.assertEqual(self.count(), 0)
        self.store.conn.execute('DROP TRIGGER fail_reply')
        self.receive()
        for sql in ('DELETE FROM reply_proposals', "UPDATE reply_proposals SET payload='{}'"):
            with self.assertRaisesRegex(sqlite3.IntegrityError, 'append-only'):
                self.store.conn.execute(sql)

    def test_database_payload_tamper_rejected_after_reopen(self):
        self.receive()
        self.store.conn.execute('DROP TRIGGER replies_no_update')
        self.store.conn.execute("UPDATE reply_proposals SET payload='{}'")
        self.store.close()
        self.store = ReplyStore(self.path)
        with self.assertRaises(ValueError):
            self.store.pending(self.request, self.context, self.record)

    def test_shape_and_size_errors_never_append(self):
        for change in (dict(extra='approve'), dict(text='x' * 4097), dict(question_id=None)):
            bad = dict(self.reply, **change)
            self.rehash(bad)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.receive(bad)
        self.assertEqual(self.count(), 0)

    def test_original_snapshot_and_inputs_not_overwritten_by_answer(self):
        before = self.store.snapshots.current(self.request, self.context)
        request, context, reply = copy.deepcopy(self.request), copy.deepcopy(self.context), copy.deepcopy(self.reply)
        self.receive()
        self.assertEqual(before, self.store.snapshots.current(self.request, self.context))
        self.assertEqual(request, self.request)
        self.assertEqual(context, self.context)
        self.assertEqual(reply, self.reply)

    def test_two_writers_receive_same_reply_once(self):
        self.store.close()
        barrier, receipts, errors = threading.Barrier(2), [], []
        def writer():
            store = None
            try:
                store = ReplyStore(self.path)
                barrier.wait(timeout=5)
                receipts.append(store.receive(self.request, self.context, self.record, self.cid, self.reply))
            except Exception as error:
                errors.append(error)
            finally:
                if store is not None:
                    store.close()
        threads = [threading.Thread(target=writer) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.store = ReplyStore(self.path)
        self.assertFalse(any(t.is_alive() for t in threads))
        self.assertEqual(errors, [])
        self.assertEqual(len(receipts), 2)
        self.assertEqual(sorted(r['duplicate'] for r in receipts), [False, True])
        self.assertEqual(self.count(), 1)


if __name__ == '__main__':
    unittest.main()

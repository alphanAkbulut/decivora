"""T05 durable project snapshot tests, no source/model or production IAM."""
from dataclasses import replace
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
import subprocess
import sys

from packages.domain.project_binding import AccessScope, SessionKey
from packages.domain.source_event import ContractError, validate_source_event
from packages.storage.project_store import ProjectStore

ROOT = Path(__file__).resolve().parents[2]


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'projects.sqlite'
        self.owner = AccessScope('workspace', 'owner', frozenset({'p1', 'p2'}), frozenset({'p1', 'p2'}))
        self.reader = replace(self.owner, principal_id='reader', readable_projects=frozenset({'p1'}), writable_projects=frozenset())
        self.key = SessionKey('manual', 'account', 'session_fixture', 'epoch')

    def create(self, store):
        store.command(self.owner, 'c1', 'create', 'p1', name='İsim')
        store.command(self.owner, 'c2', 'create', 'p2', name='İsim')

    def count(self, store):
        return store.connection.execute('SELECT count(*) FROM snapshots').fetchone()[0]

    def assert_code(self, code, operation):
        with self.assertRaises(ContractError) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)

    def test_restart_preserves_same_name_projects_rebind_and_historical_resolution(self):
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
            store.command(self.owner, 'b1', 'bind', 'p1', key=self.key, base_revision=0)
            store.command(self.owner, 'b2', 'bind', 'p2', key=self.key, base_revision=1)
        with ProjectStore(self.path, 'workspace') as store:
            self.assertEqual([p.name for p in store.query(self.owner, 'list')], ['İsim', 'İsim'])
            event = validate_source_event(dict(json.loads((ROOT / 'examples/runtime/source-event.json').read_text()), project_id='p1'))
            result = store.query(self.owner, 'resolve', self.key, event, binding_revision=1)
            self.assertEqual(result.project_id, 'p1')
            self.assertEqual([b.project_id for b in store.query(self.owner, 'history', self.key)], ['p1', 'p2'])

    def test_retry_after_reopen_is_idempotent_and_different_content_conflicts(self):
        with ProjectStore(self.path, 'workspace') as store:
            result = store.command(self.owner, 'c1', 'create', 'p1', name='İsim')
        with ProjectStore(self.path, 'workspace') as store:
            self.assertEqual(result, store.command(self.owner, 'c1', 'create', 'p1', name='İsim'))
            self.assert_code('idempotency_conflict', lambda: store.command(self.owner, 'c1', 'create', 'p1', name='different'))
            self.assertEqual(self.count(store), 1)

    def test_queries_writes_and_cached_retry_check_current_scope(self):
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
            self.assert_code('forbidden', lambda: store.query(self.reader, 'get', 'p2'))
            self.assert_code('forbidden', lambda: store.command(self.reader, 'c2', 'create', 'p2', name='İsim'))
            self.assertEqual([p.project_id for p in store.query(self.reader, 'list')], ['p1'])
            other = replace(self.owner, workspace_id='other')
            self.assert_code('forbidden', lambda: store.query(other, 'list'))
            self.assertEqual(self.count(store), 2)

    def test_stale_writer_on_second_connection_does_not_overwrite(self):
        with ProjectStore(self.path, 'workspace') as first, ProjectStore(self.path, 'workspace') as second:
            self.create(first)
            first.command(self.owner, 'u1', 'update', 'p1', base_revision=1, name='New')
            self.assert_code('stale_base', lambda: second.command(self.owner, 'u2', 'update', 'p1', base_revision=1, name='Lost'))
            self.assertEqual(second.query(self.owner, 'get', 'p1').name, 'New')
            self.assertEqual(self.count(first), 3)

    def test_forced_insert_failure_rolls_back_and_same_request_can_retry(self):
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
            store.connection.executescript("CREATE TRIGGER force_failure BEFORE INSERT ON snapshots BEGIN SELECT RAISE(ABORT,'fixture'); END;")
            self.assert_code('storage_failure', lambda: store.command(self.owner, 'u1', 'update', 'p1', base_revision=1, name='New'))
            self.assertFalse(store.connection.in_transaction)
            self.assertEqual(store.query(self.owner, 'get', 'p1').revision, 1)
            store.connection.execute('DROP TRIGGER force_failure')
            result = store.command(self.owner, 'u1', 'update', 'p1', base_revision=1, name='New')
            self.assertEqual(result['revision'], 2)

    def test_sql_update_and_delete_cannot_modify_snapshot_history(self):
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
            for sql in ('DELETE FROM snapshots', "UPDATE snapshots SET state='{}'", 'DELETE FROM metadata'):
                with self.assertRaises(sqlite3.IntegrityError):
                    store.connection.execute(sql)
            self.assertEqual(self.count(store), 2)

    def test_unknown_database_and_workspace_are_not_migrated_or_overwritten(self):
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE unrelated(secret TEXT)')
        before = self.path.read_bytes()
        self.assert_code('storage_unavailable', lambda: ProjectStore(self.path, 'workspace'))
        self.assertEqual(self.path.read_bytes(), before)
        self.path.unlink()
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
        before = self.path.read_bytes()
        self.assert_code('unsupported_storage', lambda: ProjectStore(self.path, 'other'))
        self.assertEqual(self.path.read_bytes(), before)

    def test_private_file_and_known_symlink_or_directory_rejected(self):
        with ProjectStore(self.path, 'workspace'):
            self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        link = Path(self.temp.name) / 'link'
        link.symlink_to(self.path)
        self.assert_code('storage_unavailable', lambda: ProjectStore(link, 'workspace'))
        self.assert_code('storage_unavailable', lambda: ProjectStore(Path(self.temp.name), 'workspace'))

    def test_rebind_retry_does_not_bypass_revoked_old_project_permission(self):
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
            store.command(self.owner, 'b1', 'bind', 'p1', key=self.key, base_revision=0)
            store.command(self.owner, 'b2', 'bind', 'p2', key=self.key, base_revision=1)
            revoked = replace(self.owner, readable_projects=frozenset({'p2'}), writable_projects=frozenset({'p2'}))
            self.assert_code('forbidden', lambda: store.command(revoked, 'b2', 'bind', 'p2', key=self.key, base_revision=1))
            self.assertEqual(self.count(store), 4)

    def test_tampered_state_is_rejected_on_reopen(self):
        with ProjectStore(self.path, 'workspace') as store:
            self.create(store)
            store.connection.execute('DROP TRIGGER snapshots_no_update')
            store.connection.execute("UPDATE snapshots SET state='{}' WHERE seq=2")
        self.assert_code('storage_corrupt', lambda: ProjectStore(self.path, 'workspace'))

    def test_cli_restart_demo_reports_real_database_writes_without_source_receipt(self):
        run = subprocess.run([sys.executable, '-S', '-B', '-m', 'apps.hub', 'project-store-demo'],
                             cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertTrue(result['restart_preserved'])
        self.assertTrue(result['idempotent_retry'])
        self.assertEqual(result['committed_commands'], 4)
        self.assertFalse(result['durable_source_receipt'])


if __name__ == '__main__':
    unittest.main()

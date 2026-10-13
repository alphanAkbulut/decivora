"""Local authority revision and revocation, not login or team IAM certification."""
from pathlib import Path
import tempfile
import unittest
import json
import subprocess
import sys

from packages.domain.project_binding import AccessScope
from packages.domain.source_event import ContractError
from packages.storage.local_authority import LocalAuthorityStore
from packages.storage.project_store import ProjectStore


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'local.sqlite'

    def assert_code(self, code, operation):
        with self.assertRaises(ContractError) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)

    def configure(self, store):
        owner = store.issue_scope('owner')
        store.replace_grant(owner, 'owner', kind='human', readable=frozenset({'p1'}),
                            writable=frozenset({'p1'}), active=True, base_revision=1)
        owner = store.issue_scope('owner')
        store.command(owner, 'create', 'create', 'p1', name='Private')
        store.replace_grant(owner, 'agent', kind='agent', readable=frozenset({'p1'}),
                            writable=frozenset({'p1'}), active=True, base_revision=2)

    def test_revocation_blocks_old_read_write_and_cached_retry_without_mutation(self):
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner') as store:
            self.configure(store)
            agent = store.issue_scope('agent')
            store.command(agent, 'agent_update', 'update', 'p1', base_revision=1, name='Updated')
            owner = store.issue_scope('owner')
            store.replace_grant(owner, 'agent', kind='agent', readable=frozenset(),
                                writable=frozenset(), active=False, base_revision=3)
            for op in (lambda: store.query(agent, 'get', 'p1'),
                       lambda: store.command(agent, 'agent_update', 'update', 'p1', base_revision=1, name='Updated'),
                       lambda: store.command(agent, 'new', 'update', 'p1', base_revision=2, name='Unauthorized')):
                self.assert_code('stale_authority', op)
            self.assert_code('forbidden', lambda: store.issue_scope('agent'))
            self.assertEqual(store.query(store.issue_scope('owner'), 'get', 'p1').name, 'Updated')

    def test_issued_scope_cannot_be_forged_or_reused_on_another_instance(self):
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner') as first:
            self.configure(first)
            real = first.issue_scope('agent')
            fake = AccessScope(real.workspace_id, real.principal_id, real.readable_projects, real.writable_projects)
            self.assert_code('untrusted_scope', lambda: first.query(fake, 'get', 'p1'))
            with LocalAuthorityStore(self.path, 'workspace') as second:
                self.assert_code('untrusted_scope', lambda: second.query(real, 'get', 'p1'))
                self.assertEqual(second.query(second.issue_scope('agent'), 'get', 'p1').name, 'Private')

    def test_agent_cannot_manage_grants_and_owner_cannot_be_disabled(self):
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner') as store:
            self.configure(store)
            options = dict(kind='human', readable=frozenset(), writable=frozenset(), active=True, base_revision=3)
            self.assert_code('forbidden', lambda: store.replace_grant(store.issue_scope('agent'), 'intruder', **options))
            self.assert_code('owner_protected', lambda: store.replace_grant(store.issue_scope('owner'), 'owner', **dict(options, active=False)))
            self.assertEqual(store.revision(), 3)

    def test_revocation_survives_reopen_and_stale_scope_on_other_connection_is_rejected(self):
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner') as first:
            self.configure(first)
            with LocalAuthorityStore(self.path, 'workspace') as second:
                stale = second.issue_scope('agent')
                first.replace_grant(first.issue_scope('owner'), 'agent', kind='agent', readable=frozenset(),
                                    writable=frozenset(), active=False, base_revision=3)
                self.assert_code('stale_authority', lambda: second.query(stale, 'get', 'p1'))
        with LocalAuthorityStore(self.path, 'workspace') as store:
            self.assertEqual(store.revision(), 4)
            self.assert_code('forbidden', lambda: store.issue_scope('agent'))

    def test_existing_legacy_profile_not_upgraded_and_owner_cannot_be_replaced(self):
        with ProjectStore(self.path, 'workspace'):
            pass
        original = self.path.read_bytes()
        self.assert_code('unsupported_authority', lambda: LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner'))
        self.assertEqual(original, self.path.read_bytes())
        self.path.unlink()
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner'):
            pass
        original = self.path.read_bytes()
        self.assert_code('unsupported_authority', lambda: LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='other'))
        self.assertEqual(original, self.path.read_bytes())

    def test_grant_insert_failure_rolls_back_without_revoking_old_scope(self):
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner') as store:
            self.configure(store)
            agent = store.issue_scope('agent')
            db = store._store.connection
            db.executescript("CREATE TRIGGER fail_grant BEFORE INSERT ON authority_versions BEGIN SELECT RAISE(ABORT,'fixture'); END;")
            self.assert_code('storage_failure', lambda: store.replace_grant(store.issue_scope('owner'), 'agent',
                kind='agent', readable=frozenset(), writable=frozenset(), active=False, base_revision=3))
            self.assertEqual(store.revision(), 3)
            self.assertEqual(store.query(agent, 'get', 'p1').name, 'Private')

    def test_changed_grant_requires_new_scope_and_read_only_remains_read_only(self):
        with LocalAuthorityStore(self.path, 'workspace', bootstrap_owner='owner') as store:
            self.configure(store)
            previous = store.issue_scope('agent')
            store.replace_grant(store.issue_scope('owner'), 'agent', kind='agent', readable=frozenset({'p1'}),
                                writable=frozenset(), active=True, base_revision=3)
            self.assert_code('stale_authority', lambda: store.query(previous, 'get', 'p1'))
            current = store.issue_scope('agent')
            self.assertEqual(store.query(current, 'get', 'p1').name, 'Private')
            self.assert_code('forbidden', lambda: store.command(current, 'u', 'update', 'p1', base_revision=1, name='No'))

    def test_cli_revokes_prepared_context_and_reopens_without_model_call(self):
        root = Path(__file__).resolve().parents[2]
        run = subprocess.run([sys.executable, '-S', '-B', '-m', 'apps.hub', 'authority-demo'],
                             cwd=root, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertTrue(result['revocation_survived_restart'])
        self.assertTrue(result['stale_read_rejected'])
        self.assertTrue(result['stale_write_rejected'])
        self.assertTrue(result['project_unchanged'])
        self.assertEqual(result['model_dispatches'], 0)


if __name__ == '__main__':
    unittest.main()

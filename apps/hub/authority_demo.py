"""Synthetic local owner/agent revocation demo; no account/login integration."""
from pathlib import Path
import tempfile

from packages.domain.source_event import ContractError
from packages.storage.local_authority import LocalAuthorityStore


def run_demo():
    with tempfile.TemporaryDirectory(prefix='decivora-authority-demo-') as directory:
        path = Path(directory) / 'local.sqlite'
        with LocalAuthorityStore(path, 'workspace_demo', bootstrap_owner='owner_demo') as store:
            store.replace_grant(store.issue_scope('owner_demo'), 'owner_demo', kind='human',
                readable=frozenset({'p1'}), writable=frozenset({'p1'}), active=True, base_revision=1)
            owner = store.issue_scope('owner_demo')
            store.command(owner, 'create', 'create', 'p1', name='Sentetik proje')
            store.replace_grant(owner, 'agent_demo', kind='agent', readable=frozenset({'p1'}),
                writable=frozenset({'p1'}), active=True, base_revision=2)
            agent = store.issue_scope('agent_demo')
            store.query(agent, 'get', 'p1')
            store.replace_grant(store.issue_scope('owner_demo'), 'agent_demo', kind='agent',
                readable=frozenset(), writable=frozenset(), active=False, base_revision=3)
            outcomes = []
            for operation in (lambda: store.query(agent, 'get', 'p1'),
                lambda: store.command(agent, 'denied_update', 'update', 'p1', base_revision=1, name='Denied')):
                try:
                    operation()
                except ContractError as error:
                    outcomes.append(error.code)
                else:
                    raise RuntimeError('Revocation did not block the prepared operation.')
            if outcomes != ['stale_authority', 'stale_authority']:
                raise RuntimeError('Unexpected revocation outcome.')
        with LocalAuthorityStore(path, 'workspace_demo') as store:
            try:
                store.issue_scope('agent_demo')
            except ContractError as error:
                revoked = error.code == 'forbidden'
            else:
                revoked = False
            if not revoked:
                raise RuntimeError('Revocation did not survive restart.')
            unchanged = store.query(store.issue_scope('owner_demo'), 'get', 'p1').revision == 1
    return dict(status='passed_local_authority_demo', authentication='trusted_local_fixture_only',
        stale_read_rejected=True, stale_write_rejected=True, revocation_survived_restart=True,
        project_unchanged=unchanged, authority_revision=4, source_capture=False, model_dispatches=0)

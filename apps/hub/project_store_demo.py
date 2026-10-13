"""Fixed synthetic restart demo using an isolated temporary SQLite file."""
from pathlib import Path
import tempfile

from packages.domain.project_binding import AccessScope, SessionKey
from packages.storage.project_store import ProjectStore


def run_demo():
    owner = AccessScope('workspace_demo', 'owner_demo', frozenset({'p1', 'p2'}), frozenset({'p1', 'p2'}))
    key = SessionKey('manual', 'account_demo', 'session_demo', 'epoch_demo')
    with tempfile.TemporaryDirectory(prefix='decivora-project-demo-') as directory:
        path = Path(directory) / 'projects.sqlite'
        with ProjectStore(path, owner.workspace_id) as store:
            first = store.command(owner, 'create_p1', 'create', 'p1', name='Aynı isim')
            store.command(owner, 'create_p2', 'create', 'p2', name='Aynı isim')
            store.command(owner, 'bind_p1', 'bind', 'p1', key=key, base_revision=0)
            store.command(owner, 'bind_p2', 'bind', 'p2', key=key, base_revision=1)
        with ProjectStore(path, owner.workspace_id) as store:
            repeated = store.command(owner, 'create_p1', 'create', 'p1', name='Aynı isim')
            projects = store.query(owner, 'list')
            history = store.query(owner, 'history', key)
            rows = store.connection.execute('SELECT count(*) FROM snapshots').fetchone()[0]
            if first != repeated or rows != 4 or len(projects) != 2 or [b.project_id for b in history] != ['p1', 'p2']:
                raise RuntimeError('Restart/idempotency demonstration failed.')
    return dict(status='passed_synthetic_project_store_demo', storage='temporary_sqlite',
        restart_preserved=True, idempotent_retry=True, project_count=2, binding_revisions=2,
        committed_commands=4, temporary_demo_removed=True, real_source_capture=False,
        production_authentication=False, durable_source_receipt=False, model_dispatches=0)

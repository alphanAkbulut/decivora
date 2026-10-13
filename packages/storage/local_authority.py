"""Persisted local permission revisions; no login/OAuth or external token verifier.

Only the trusted local caller may issue a scope for an authenticated principal.
Scope objects are bound to this open store instance, not accepted from JSON.
"""
import json
from pathlib import Path
import sqlite3

from packages.domain.project_binding import AccessScope, identifier
from packages.domain.source_event import ContractError
from .project_store import ProjectStore, canonical, digest

FORMAT = 'decivora-local-authority-1'


class LocalAuthorityStore:
    def __init__(self, path, workspace_id, *, bootstrap_owner=None):
        exists = Path(path).exists() or Path(path).is_symlink()
        if not exists and bootstrap_owner is None:
            raise ContractError('owner_required', 'Explicit local owner required for new authority storage.')
        if bootstrap_owner is not None:
            identifier(bootstrap_owner)
        self._store = ProjectStore(path, workspace_id)
        self._issued = {}
        self.workspace_id = workspace_id
        db = self._store.connection
        try:
            if not exists:
                db.executescript('''BEGIN IMMEDIATE;
                    CREATE TABLE authority_meta(format TEXT NOT NULL, owner_id TEXT NOT NULL);
                    CREATE TABLE authority_versions(revision INTEGER PRIMARY KEY, state TEXT NOT NULL, digest TEXT NOT NULL);
                    CREATE TRIGGER authority_no_update BEFORE UPDATE ON authority_versions BEGIN SELECT RAISE(ABORT,'immutable authority'); END;
                    CREATE TRIGGER authority_no_delete BEFORE DELETE ON authority_versions BEGIN SELECT RAISE(ABORT,'immutable authority'); END;
                    CREATE TRIGGER owner_no_update BEFORE UPDATE ON authority_meta BEGIN SELECT RAISE(ABORT,'immutable owner'); END;
                    CREATE TRIGGER owner_no_delete BEFORE DELETE ON authority_meta BEGIN SELECT RAISE(ABORT,'immutable owner'); END;
                ''')
                db.execute('INSERT INTO authority_meta VALUES (?,?)', (FORMAT, bootstrap_owner))
                raw = canonical({bootstrap_owner: dict(kind='human', readable=[], writable=[], active=True)})
                db.execute('INSERT INTO authority_versions VALUES (1,?,?)', (raw, digest(raw)))
                db.execute('COMMIT')
            rows = db.execute('SELECT format, owner_id FROM authority_meta').fetchall()
            if len(rows) != 1 or rows[0][0] != FORMAT:
                raise ContractError('unsupported_authority', 'Authority metadata is incompatible.')
            self.owner_id = identifier(rows[0][1])
            if bootstrap_owner is not None and bootstrap_owner != self.owner_id:
                raise ContractError('owner_conflict', 'Existing owner cannot be replaced during open.')
            self._current()
            self._store._scope_guard = self._validate_scope
        except (ContractError, sqlite3.Error):
            self.close()
            raise ContractError('unsupported_authority', 'Authority profile is unavailable; no legacy upgrade performed.') from None

    def close(self):
        self._issued.clear()
        self._store.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _current(self):
        row = self._store.connection.execute('SELECT revision,state,digest FROM authority_versions ORDER BY revision DESC LIMIT 1').fetchone()
        if row is None or digest(row[1]) != row[2]:
            raise ContractError('authority_corrupt', 'Authority state failed integrity validation.')
        try:
            state = json.loads(row[1])
            if type(state) is not dict or canonical(state) != row[1] or self.owner_id not in state:
                raise ValueError()
            for principal, grant in state.items():
                identifier(principal)
                if set(grant) != {'kind', 'readable', 'writable', 'active'} or grant['kind'] not in ('human', 'agent') or type(grant['active']) is not bool:
                    raise ValueError()
                for key in ('readable', 'writable'):
                    if type(grant[key]) is not list or len(grant[key]) != len(set(grant[key])):
                        raise ValueError()
                    for project in grant[key]:
                        identifier(project)
        except (ValueError, TypeError, KeyError, ContractError):
            raise ContractError('authority_corrupt', 'Authority state is structurally invalid.') from None
        return row[0], state

    def issue_scope(self, principal_id):
        """Trusted LOCAL authentication adapter entry; never expose as anonymous API."""
        identifier(principal_id)
        revision, state = self._current()
        grant = state.get(principal_id)
        if grant is None or not grant['active']:
            raise ContractError('forbidden', 'Principal is unavailable or inactive.')
        scope = AccessScope(self.workspace_id, principal_id, frozenset(grant['readable']), frozenset(grant['writable']))
        # Old scopes are already stale after any revision change; do not retain them.
        self._issued = {k: v for k, v in self._issued.items() if v[1] == revision}
        if len(self._issued) >= 1024:
            raise ContractError('context_limit', 'Local context limit reached; close and reopen the store.')
        self._issued[id(scope)] = (scope, revision)
        return scope

    def _validate_scope(self, scope):
        issued = self._issued.get(id(scope))
        if issued is None or issued[0] is not scope:
            raise ContractError('untrusted_scope', 'Scope was not issued by this local authority instance.')
        revision, state = self._current()
        if issued[1] != revision:
            raise ContractError('stale_authority', 'Permissions changed; obtain a fresh authorized context.')
        grant = state.get(scope.principal_id)
        if grant is None or not grant['active']:
            raise ContractError('forbidden', 'Principal is unavailable or inactive.')

    def replace_grant(self, owner_scope, principal_id, *, kind, readable, writable, active, base_revision):
        identifier(principal_id)
        if kind not in ('human', 'agent') or type(active) is not bool or type(base_revision) is not int:
            raise ContractError('invalid_grant', 'Invalid local grant fields.')
        if type(readable) is not frozenset or type(writable) is not frozenset:
            raise ContractError('invalid_grant', 'Grant project sets must be immutable.')
        for project in readable | writable:
            identifier(project)
        db = self._store.connection
        try:
            db.execute('BEGIN IMMEDIATE')
            self._validate_scope(owner_scope)
            revision, state = self._current()
            if owner_scope.principal_id != self.owner_id or state[owner_scope.principal_id]['kind'] != 'human':
                raise ContractError('forbidden', 'Only the local human owner can manage grants.')
            if revision != base_revision:
                raise ContractError('stale_authority', 'Authority revision changed; refresh before managing grants.')
            if principal_id == self.owner_id and (kind != 'human' or not active):
                raise ContractError('owner_protected', 'Local owner identity cannot be disabled or converted to an agent.')
            state[principal_id] = dict(kind=kind, readable=sorted(readable), writable=sorted(writable), active=active)
            raw = canonical(state)
            if len(raw.encode('utf-8')) > 65536:
                raise ContractError('authority_quota', 'Local authority state exceeds the development limit.')
            db.execute('INSERT INTO authority_versions VALUES (?,?,?)', (revision + 1, raw, digest(raw)))
            db.execute('COMMIT')
            return revision + 1
        except (ContractError, sqlite3.Error) as error:
            if db.in_transaction:
                db.execute('ROLLBACK')
            if isinstance(error, ContractError):
                raise
            raise ContractError('storage_failure', 'Grant change was not committed.') from None

    def revision(self):
        return self._current()[0]

    def command(self, scope, *args, **kwargs):
        return self._store.command(scope, *args, **kwargs)

    def query(self, scope, *args, **kwargs):
        return self._store.query(scope, *args, **kwargs)

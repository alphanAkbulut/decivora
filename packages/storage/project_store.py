"""T05 local append-only project snapshots, not the T07 knowledge event store.

Single selected private SQLite file, bounded history snapshots, injected scope.
No source payloads, credentials, auth service or model calls.
"""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat

from packages.domain.project_binding import Binding, Project, ProjectRegistry, SessionKey, identifier
from packages.domain.source_event import ContractError

FORMAT = 'decivora-project-store-1'
MAX_STATE_BYTES = 1048576


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class ProjectStore:
    def __init__(self, path, workspace_id):
        self.workspace_id = identifier(workspace_id)
        self.path = Path(path)
        self.connection = None
        self._scope_guard = None
        created = False
        try:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
            except FileExistsError:
                info = self.path.lstat()
                if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode):
                    raise ContractError('storage_unavailable', 'Selected storage must be a regular file.')
            else:
                os.close(fd)
                created = True
            from packages.storage.private_files import restrict_sqlite_files
            restrict_sqlite_files(self.path)
            self.connection = sqlite3.connect(self.path, timeout=2, isolation_level=None)
            if created:
                self.connection.executescript('''BEGIN IMMEDIATE;
                    CREATE TABLE metadata(format TEXT NOT NULL, workspace_id TEXT NOT NULL);
                    CREATE TABLE snapshots(seq INTEGER PRIMARY KEY, command_id TEXT NOT NULL UNIQUE,
                        principal_id TEXT NOT NULL, command_digest TEXT NOT NULL,
                        result TEXT NOT NULL, result_digest TEXT NOT NULL,
                        state TEXT NOT NULL, state_digest TEXT NOT NULL);
                    CREATE TRIGGER snapshots_no_update BEFORE UPDATE ON snapshots BEGIN
                        SELECT RAISE(ABORT, 'immutable snapshot'); END;
                    CREATE TRIGGER snapshots_no_delete BEFORE DELETE ON snapshots BEGIN
                        SELECT RAISE(ABORT, 'immutable snapshot'); END;
                    CREATE TRIGGER metadata_no_update BEFORE UPDATE ON metadata BEGIN
                        SELECT RAISE(ABORT, 'immutable metadata'); END;
                    CREATE TRIGGER metadata_no_delete BEFORE DELETE ON metadata BEGIN
                        SELECT RAISE(ABORT, 'immutable metadata'); END;
                    ''')
                self.connection.execute('INSERT INTO metadata VALUES (?,?)', (FORMAT, self.workspace_id))
                self.connection.execute('COMMIT')
            else:
                rows = self.connection.execute('SELECT format, workspace_id FROM metadata').fetchall()
                if rows != [(FORMAT, self.workspace_id)]:
                    raise ContractError('unsupported_storage', 'Storage format or workspace is incompatible.')
            self.connection.execute('PRAGMA synchronous=FULL')
            self._load()
        except ContractError:
            self.close()
            raise
        except (OSError, sqlite3.Error, ValueError, TypeError):
            self.close()
            raise ContractError('storage_unavailable', 'Selected storage is unavailable or incompatible.') from None

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _load(self):
        row = self.connection.execute('SELECT state,state_digest FROM snapshots ORDER BY seq DESC LIMIT 1').fetchone()
        registry = ProjectRegistry(self.workspace_id)
        if row is None:
            return registry
        raw, sha = row
        if len(raw.encode('utf-8')) > MAX_STATE_BYTES or digest(raw) != sha:
            raise ContractError('storage_corrupt', 'Stored project state failed integrity validation.')
        try:
            value = json.loads(raw)
            if set(value) != {'projects', 'bindings'} or canonical(value) != raw:
                raise ValueError()
            for p in value['projects']:
                if set(p) != {'project_id', 'name', 'revision', 'archived'}:
                    raise ValueError()
                identifier(p['project_id'])
                registry._name(p['name'])
                if type(p['revision']) is not int or p['revision'] < 1 or type(p['archived']) is not bool or p['project_id'] in registry._projects:
                    raise ValueError()
                registry._projects[p['project_id']] = Project(**p)
            for group in value['bindings']:
                if set(group) != {'key', 'history'}:
                    raise ValueError()
                key = SessionKey(**group['key'])
                if key in registry._bindings or not group['history']:
                    raise ValueError()
                history = []
                for index, b in enumerate(group['history'], 1):
                    if set(b) != {'project_id', 'revision', 'bound_by'} or type(b['revision']) is not int or b['revision'] != index or b['project_id'] not in registry._projects:
                        raise ValueError()
                    identifier(b['bound_by'])
                    history.append(Binding(key=key, **b))
                registry._bindings[key] = tuple(history)
        except (ValueError, TypeError, KeyError, ContractError):
            raise ContractError('storage_corrupt', 'Stored project state failed structural validation.') from None
        return registry

    @staticmethod
    def _state(registry):
        groups = []
        for key in sorted(registry._bindings, key=lambda k: canonical(asdict(k))):
            groups.append(dict(key=asdict(key), history=[dict(project_id=b.project_id,
                revision=b.revision, bound_by=b.bound_by) for b in registry._bindings[key]]))
        raw = canonical(dict(projects=[asdict(registry._projects[p]) for p in sorted(registry._projects)], bindings=groups))
        if len(raw.encode('utf-8')) > MAX_STATE_BYTES:
            raise ContractError('storage_quota_exceeded', 'Project snapshot exceeds the development storage limit.')
        return raw

    def command(self, scope, command_id, operation, project_id, **arguments):
        """Retry same ID/actor/content returns prior result; auth checked on every call."""
        identifier(command_id)
        if operation not in ('create', 'update', 'bind'):
            raise ContractError('invalid_command', 'Unsupported project command.')
        registry = ProjectRegistry(self.workspace_id)
        registry._scope(scope, project_id, write=True)
        normalized = dict(arguments)
        if 'key' in normalized:
            if type(normalized['key']) is not SessionKey:
                raise ContractError('invalid_session', 'Explicit source session key required.')
            normalized['key'] = asdict(normalized['key'])
        try:
            request_sha = digest(canonical(dict(operation=operation, project_id=project_id, arguments=normalized)))
        except (TypeError, ValueError, UnicodeError):
            raise ContractError('invalid_command', 'Project command must contain valid structured arguments.') from None
        try:
            self.connection.execute('BEGIN IMMEDIATE')
            if self._scope_guard is not None:
                self._scope_guard(scope)
            registry = self._load()
            if operation == 'bind':
                # Retry must not reveal/move an earlier project after revocation.
                for b in registry.history(scope, arguments['key']):
                    registry._scope(scope, b.project_id, write=True)
            existing = self.connection.execute('SELECT principal_id,command_digest,result,result_digest FROM snapshots WHERE command_id=?', (command_id,)).fetchone()
            if existing:
                if existing[:2] != (scope.principal_id, request_sha):
                    raise ContractError('idempotency_conflict', 'Command identity is already used for different content.')
                if digest(existing[2]) != existing[3]:
                    raise ContractError('storage_corrupt', 'Stored command result failed integrity validation.')
                result = json.loads(existing[2])
            else:
                if operation == 'create':
                    obj = registry.create(scope, project_id, **arguments)
                elif operation == 'update':
                    obj = registry.update(scope, project_id, **arguments)
                else:
                    args = dict(arguments)
                    key = args.pop('key')
                    obj = registry.bind(scope, key, project_id, **args)
                result = asdict(obj)
                state = self._state(registry)
                serialized_result = canonical(result)
                self.connection.execute('INSERT INTO snapshots(command_id,principal_id,command_digest,result,result_digest,state,state_digest) VALUES (?,?,?,?,?,?,?)',
                    (command_id, scope.principal_id, request_sha, serialized_result, digest(serialized_result), state, digest(state)))
            self.connection.execute('COMMIT')
            return result
        except (ContractError, sqlite3.Error, TypeError, KeyError, ValueError) as error:
            if self.connection.in_transaction:
                self.connection.execute('ROLLBACK')
            if isinstance(error, ContractError):
                raise
            raise ContractError('storage_failure', 'Project command was not committed; retry only with the same identity.') from None

    def query(self, scope, operation, *args, **kwargs):
        if operation not in ('get', 'list', 'history', 'resolve'):
            raise ContractError('invalid_query', 'Unsupported project query.')
        ProjectRegistry(self.workspace_id)._scope(scope)
        try:
            self.connection.execute('BEGIN IMMEDIATE')
            if self._scope_guard is not None:
                self._scope_guard(scope)
            registry = self._load()
            result = getattr(registry, operation)(scope, *args, **kwargs)
            self.connection.execute('COMMIT')
            return result
        except (ContractError, sqlite3.Error) as error:
            if self.connection.in_transaction:
                self.connection.execute('ROLLBACK')
            if isinstance(error, ContractError):
                raise
            raise ContractError('storage_failure', 'Project query is unavailable.') from None

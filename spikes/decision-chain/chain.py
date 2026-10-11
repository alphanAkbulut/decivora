"""Fixture-only P0 decision/impact/evidence experiment. Not a production service."""
import hashlib
import json
import sqlite3
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def applicability(expr, active):
    if expr is None:
        return None
    if isinstance(expr, str):
        return expr in active
    operator, children = next(iter(expr.items()))
    values = [applicability(item, active) for item in children]
    if not values or operator not in ('all', 'any'):
        return None
    if operator == 'all':
        return False if False in values else (True if all(v is True for v in values) else None)
    return True if True in values else (False if all(v is False for v in values) else None)


def initial():
    return dict(revision=0, decision=None, question=None, tasks={}, active=[],
                artifact=None, observation=None, criteria=[], evidence={}, verified=False)


def project(state, command, payload):
    """Pure projector: no IO, model, verifier dispatch or source parsing."""
    if command == 'seed':
        state.update(payload)
    elif command == 'ask':
        state['question'] = dict(payload, state='pending')
    elif command == 'answer':
        state['decision'] = state['question']['options'][payload['option']]
        state['active'] = [state['decision'], 'security']
        state['question']['state'] = 'resolved'
    elif command == 'add_reason':
        state['tasks'][payload['task']]['expr'] = payload['expr']
    elif command == 'impact':
        for task, action in payload['actions'].items():
            state['tasks'][task]['status'] = action
    elif command == 'expect':
        state['artifact'] = payload
        state['observation'] = None
        state['evidence'] = {}
        state['verified'] = False
    elif command == 'observe':
        artifact = state['artifact']
        if payload.get('availability') != 'read':
            status = payload.get('availability', 'unknown')
        elif any(payload.get(k) != artifact[k] for k in ('artifact_revision', 'ref', 'path')):
            status = 'stale'
        elif payload['sha256'] != artifact['sha256']:
            status = 'mismatch'
        else:
            status = 'observed_match'
        state['observation'] = dict(payload, status=status)
        state['verified'] = False
    elif command == 'verify':
        state['evidence'].update(payload['criteria'])
        state['verified'] = bool(state['criteria']) and (
            state['observation'] is not None and state['observation']['status'] == 'observed_match'
            and all(state['evidence'].get(c) == 'passed' for c in state['criteria']))
    return state


class Chain:
    # Roles are trusted synthetic transport fixtures, not an IAM implementation.
    PERMISSIONS = {'human': {'seed', 'ask', 'answer', 'add_reason', 'impact', 'expect'},
                   'observer': {'observe'}, 'verifier': {'verify'}}

    def __init__(self, path):
        self.path = Path(path)
        self.conn = sqlite3.connect(str(path), isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY, schema_version INTEGER NOT NULL,
          request_key TEXT NOT NULL UNIQUE, request_digest TEXT NOT NULL,
          actor TEXT NOT NULL, command TEXT NOT NULL, payload TEXT NOT NULL,
          previous_digest TEXT NOT NULL, digest TEXT NOT NULL);
        CREATE TRIGGER IF NOT EXISTS event_no_update BEFORE UPDATE ON events
          BEGIN SELECT RAISE(ABORT,'append-only'); END;
        CREATE TRIGGER IF NOT EXISTS event_no_delete BEFORE DELETE ON events
          BEGIN SELECT RAISE(ABORT,'append-only'); END;
        """)

    def close(self):
        self.conn.close()

    def snapshot(self):
        state, previous = initial(), ''
        for row in self.conn.execute('SELECT * FROM events ORDER BY seq'):
            if row['schema_version'] != 1:
                raise ValueError('unsupported event schema')
            payload = json.loads(row['payload'])
            content = dict(seq=row['seq'], schema_version=1, request_key=row['request_key'],
                           request_digest=row['request_digest'], actor=row['actor'],
                           command=row['command'], payload=payload, previous_digest=previous)
            if row['previous_digest'] != previous or row['digest'] != digest(content):
                raise ValueError('event integrity mismatch')
            state = project(state, row['command'], payload)
            state['revision'] = row['seq']
            previous = row['digest']
        return state

    def preview(self):
        state = self.snapshot()
        impact = {}
        for task, item in state['tasks'].items():
            valid = applicability(item['expr'], state['active'])
            impact[task] = 'retained' if valid is True else ('obsolete_candidate' if valid is False else 'review_unknown')
        result = dict(base_revision=state['revision'], impact=impact,
                      graph_digest=digest({k:v['expr'] for k,v in state['tasks'].items()}))
        result['preview_digest'] = digest(result)
        return result

    def dispatch(self, command, payload, actor, base_revision, key):
        request = digest(dict(command=command, payload=payload, actor=actor, base_revision=base_revision))
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            old = self.conn.execute('SELECT * FROM events WHERE request_key=?',(key,)).fetchone()
            if old:
                if old['request_digest'] != request:
                    raise ValueError('idempotency conflict')
                self.conn.execute('COMMIT')
                return old['seq']
            if command not in self.PERMISSIONS.get(actor, set()):
                raise PermissionError('fixture authority denied')
            state = self.snapshot()
            if state['revision'] != base_revision:
                raise ValueError('stale base revision')
            if command == 'seed' and state['revision'] != 0:
                raise ValueError('already initialized')
            if command == 'ask' and state['question'] and state['question']['state'] == 'pending':
                raise ValueError('question already pending')
            if command == 'answer':
                question = state['question']
                if not question or question['state'] != 'pending' or (
                    payload['question_id'], payload['option_revision']) != (
                        question['question_id'], question['option_revision']):
                    raise ValueError('stale or unmatched answer')
                if payload['option'] not in question['options']:
                    raise ValueError('unknown option')
            if command == 'impact':
                preview = self.preview()
                if payload['preview_digest'] != preview['preview_digest']:
                    raise ValueError('stale graph preview')
                for task, action in payload['actions'].items():
                    permitted = {'retained': {'retained'}, 'review_unknown': {'review'},
                                 'obsolete_candidate': {'obsolete','review','retained'}}
                    if action not in permitted[preview['impact'][task]]:
                        raise ValueError('unsupported impact closure')
            if command == 'verify':
                if not state['artifact'] or payload['artifact_revision'] != state['artifact']['artifact_revision']:
                    raise ValueError('stale artifact evidence')
                if set(payload['criteria']) - set(state['criteria']):
                    raise ValueError('unknown acceptance criterion')
                if set(payload['criteria'].values()) - {'passed','failed','unknown','not_run'}:
                    raise ValueError('invalid verification status')
            if command == 'observe' and state['artifact'] is None:
                raise ValueError('no expected artifact')
            # Project before append to reject invalid commands without partial events.
            project(json.loads(canonical(state)), command, payload)
            last = self.conn.execute('SELECT digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
            record = dict(seq=state['revision']+1, schema_version=1, request_key=key,
                          request_digest=request, actor=actor, command=command, payload=payload,
                          previous_digest=last['digest'] if last else '')
            self.conn.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)',
                              (record['seq'],1,key,request,actor,command,canonical(payload),
                               record['previous_digest'],digest(record)))
            self.conn.execute('COMMIT')
            return record['seq']
        except BaseException:
            self.conn.execute('ROLLBACK')
            raise

    def backup(self, target):
        target = Path(target)
        if target.exists():
            raise FileExistsError('backup target must be new')
        destination = sqlite3.connect(str(target))
        try:
            self.conn.backup(destination)
        finally:
            destination.close()
        restored = Chain(target)
        try:
            if digest(restored.snapshot()) != digest(self.snapshot()):
                raise ValueError('backup projection mismatch')
        finally:
            restored.close()
        return digest(self.snapshot())


def read_target(path, artifact_revision, ref, relative_path):
    try:
        content = Path(path).read_bytes()
        return dict(availability='read',sha256=hashlib.sha256(content).hexdigest(),
                    artifact_revision=artifact_revision, ref=ref, path=relative_path)
    except FileNotFoundError:
        return dict(availability='missing', artifact_revision=artifact_revision,ref=ref,path=relative_path)
    except PermissionError:
        return dict(availability='unknown', artifact_revision=artifact_revision,ref=ref,path=relative_path)

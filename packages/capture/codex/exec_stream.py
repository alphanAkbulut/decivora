"""Durable, bounded capture of completed public assistant messages.

Consumes caller-supplied snapshots of one explicitly selected `codex exec --json`
stream. Does not start Codex, read files, call a model, or approve task changes.
"""
import hashlib
import json

from packages.capture.conversations import ConversationService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError

MAX_STREAM_BYTES = 1048576
MAX_LINE_BYTES = 65536
EVENTS = {'thread.started', 'turn.started', 'turn.completed', 'turn.failed',
          'item.started', 'item.updated', 'item.completed', 'error'}
ITEMS = {'agent_message', 'reasoning', 'command_execution', 'file_change',
         'mcp_tool_call', 'collab_tool_call', 'web_search', 'todo_list', 'error'}


def _fail(code='invalid_codex_stream'):
    # Never reflect source text, tool output or provider errors into diagnostics.
    raise ContractError(code, 'Selected Codex stream failed its bounded capture contract.')


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _fail()
        result[key] = value
    return result


def parse_snapshot(raw, thread):
    """Replay a bounded prefix deterministically; unfinished last line is pending."""
    if type(raw) is not bytes or len(raw) > MAX_STREAM_BYTES:
        _fail('capture_limit')
    complete = raw.rfind(b'\n') + 1
    if len(raw) - complete > MAX_LINE_BYTES:
        _fail('capture_limit')
    messages = {}; started = False; active = False; turn = 0; failed = False
    ignored = 0; unsupported_items = 0
    for line in raw[:complete].splitlines():
        if not line or len(line) > MAX_LINE_BYTES:
            _fail()
        try:
            event = json.loads(line.decode('utf-8'), object_pairs_hook=_object,
                               parse_constant=lambda _: _fail())
        except (ValueError, UnicodeError, RecursionError):
            _fail()
        if type(event) is not dict or type(event.get('type')) is not str or event['type'] not in EVENTS:
            _fail('unsupported_codex_event')
        kind = event['type']
        if kind == 'thread.started':
            if started or event.get('thread_id') != thread:
                _fail('capture_binding_mismatch')
            started = True
            continue
        if not started or failed:
            _fail()
        if kind == 'error':
            failed = True; active = False
        elif kind == 'turn.started':
            if active:
                _fail()
            turn += 1; active = True
        elif kind in ('turn.completed', 'turn.failed'):
            if not active:
                _fail()
            active = False
            failed = kind == 'turn.failed'
        else:
            if not active or type(event.get('item')) is not dict:
                _fail()
            item = event['item']
            if type(item.get('type')) is not str:
                _fail()
            if item.get('type') not in ITEMS:
                unsupported_items += 1
                continue
            if kind != 'item.completed' or item['type'] != 'agent_message':
                ignored += 1
                continue
            identifier(item.get('id'))
            text = item.get('text')
            if type(text) is not str or not text.strip():
                _fail('capture_message_limit')
            try:
                if len(text.encode('utf-8')) > 12000:
                    _fail('capture_message_limit')
            except UnicodeError:
                _fail()
            key = (turn, item['id'])
            if key in messages and messages[key] != text:
                _fail('capture_item_conflict')
            messages[key] = text
    return dict(messages=messages, cursor=complete, pending_bytes=len(raw)-complete,
                stream_sha256=hashlib.sha256(raw[:complete]).hexdigest(),
                state='Failed' if failed else 'Waiting for turn end' if active else 'Idle' if turn else 'Waiting for turn',
                ignored_events=ignored, unsupported_items=unsupported_items)


class CodexExecCapture:
    def __init__(self, core):
        self.core = core
        self.sources = ConversationService(core)

    def capabilities(self):
        return dict(source_surface='codex_exec_jsonl', automatic_discovery=False,
                    transcript_access='completed public assistant messages only',
                    user_messages=False, desktop_sessions=False, reasoning=False,
                    historical_backfill='selected bounded stream prefix only',
                    model_dispatch=False, max_stream_bytes=MAX_STREAM_BYTES)

    def connect(self, scope, project, *, capture_id, thread_id, provider_version, consent):
        for value in (capture_id, thread_id, provider_version):
            identifier(value)
        if consent is not True:
            _fail('capture_consent_required')
        with self.core.transaction():
            self.core.scope(scope, project, write=True, human=True)
            self.core.active(scope, project)
            old = self._binding(project, capture_id)
            binding = dict(id=capture_id, thread_id=thread_id, provider_version=provider_version,
                           actor=scope.principal_id, authority_revision=self.core.authority.revision())
            if old:
                if old != binding or self._disconnected(project, capture_id):
                    _fail('capture_binding_conflict')
                return old
            if len(self.sources._rows(project, 'codex_capture_connected')) >= 32:
                _fail('capture_limit')
            self.sources._put(scope, project, 'codex_capture_connected', binding)
            return binding

    def _binding(self, project, capture_id):
        return next((v for v in self.sources._rows(project, 'codex_capture_connected') if v['id'] == capture_id), None)

    def _disconnected(self, project, capture_id):
        return any(v['id'] == capture_id for v in self.sources._rows(project, 'codex_capture_disconnected'))

    def _authorize(self, scope, project, capture_id):
        self.core.scope(scope, project, write=True, human=True)
        self.core.active(scope, project)
        binding = self._binding(project, capture_id)
        if not binding or self._disconnected(project, capture_id) or binding['actor'] != scope.principal_id or binding['authority_revision'] != self.core.authority.revision():
            _fail('capture_consent_required')
        return binding

    def collect(self, scope, project, *, capture_id, snapshot):
        identifier(capture_id)
        with self.core.transaction():
            binding = self._authorize(scope, project, capture_id)
            parsed = parse_snapshot(snapshot, binding['thread_id'])
            previous = next((v for v in reversed(self.sources._rows(project, 'codex_capture_collected')) if v['id'] == capture_id), None)
            if previous:
                if parsed['cursor'] < previous['cursor'] or hashlib.sha256(snapshot[:previous['cursor']]).hexdigest() != previous['stream_sha256']:
                    _fail('capture_prefix_changed')
                if parsed['cursor'] == previous['cursor'] and parsed['pending_bytes'] == previous['pending_bytes']:
                    return previous
            source_ids = []
            for (turn, item), text in parsed.pop('messages').items():
                provenance = dict(id=capture_id, thread_id=binding['thread_id'], turn=turn,
                                  item_id=item, provider_version=binding['provider_version'],
                                  observed_actor='assistant', coverage='partial')
                source = self.sources._ingest(scope, project, text=text, capture=provenance, in_transaction=True)
                source_ids.append(source['id'])
            receipt = dict(id=capture_id, **parsed, source_ids=source_ids, coverage='partial',
                           missing=['user_messages', 'desktop_sessions', 'host_continuity_not_verified'])
            # Sources and cursor share a transaction: failure cannot acknowledge lost data.
            self.sources._put(scope, project, 'codex_capture_collected', receipt)
            return receipt

    def disconnect(self, scope, project, *, capture_id):
        identifier(capture_id)
        with self.core.transaction():
            self.core.scope(scope, project, write=True, human=True)
            self.core.active(scope, project)
            if not self._binding(project, capture_id):
                _fail('capture_consent_required')
            if not self._disconnected(project, capture_id):
                self.sources._put(scope, project, 'codex_capture_disconnected', dict(id=capture_id))
            return dict(id=capture_id, state='Disconnected')

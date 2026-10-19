"""Read only a selected thread's bounded persisted turn page; no agent execution."""
from packages.capture.codex.exec_stream import CodexExecCapture, _fail
from packages.domain.project_binding import identifier
from packages.privacy.secrets import redact_text
from packages.storage.project_store import canonical, digest

MAX_TURNS = 10
IGNORED = {'reasoning','commandExecution','fileChange','mcpToolCall','dynamicToolCall',
           'collabToolCall','webSearch','imageView','enteredReviewMode','exitedReviewMode',
           'contextCompaction','plan','functionCallOutput'}


def public_messages(page):
    """Keep roles and item identity; never retain private tool/reasoning bodies."""
    if type(page) is not dict or type(page.get('data')) is not list or len(page['data']) > MAX_TURNS:
        _fail('invalid_codex_page')
    transport_counts={key:page.get(key,0) for key in ('item_pages','ignored_private_items','capture_unsupported_items')}
    if any(type(v) is not int or not 0<=v<=32 for v in transport_counts.values()): _fail('invalid_codex_page')
    messages = []; seen = set(); turns = set(); skipped = 0; active = 0; incomplete=0
    for turn in reversed(page['data']):  # read request is newest first
        if type(turn) is not dict: _fail('invalid_codex_page')
        identifier(turn.get('id'))
        if turn['id'] in turns: _fail('capture_item_conflict')
        turns.add(turn['id'])
        status = turn.get('status')
        partial=page.get('capture_transport')=='decivora-codex-item-pages-1' and turn.get('capture_items_truncated') is True
        if turn.get('itemsView','full') != 'full' and not partial: _fail('capture_incomplete_page')
        incomplete+=partial
        if status not in ('completed','interrupted','failed','inProgress'):
            _fail('invalid_codex_page')
        if type(turn.get('items')) is not list or len(turn['items']) > 256:
            _fail('capture_limit')
        active += status == 'inProgress'
        for item in turn['items']:
            if type(item) is not dict or type(item.get('type')) is not str:
                _fail('invalid_codex_page')
            kind = item['type']
            if kind not in ('userMessage','agentMessage'):
                skipped += kind not in IGNORED
                continue
            # Active-turn agent text may still be changing; capture it after terminal read.
            if kind == 'agentMessage' and status == 'inProgress': continue
            identifier(item.get('id'))
            key = (turn['id'], item['id'])
            if key in seen: _fail('capture_item_conflict')
            seen.add(key)
            if kind == 'agentMessage': text = item.get('text')
            else:
                content = item.get('content')
                if type(content) is not list or len(content) > 64: _fail('invalid_codex_page')
                parts = []
                for part in content:
                    if type(part) is not dict: _fail('invalid_codex_page')
                    if part.get('type') == 'text':
                        if type(part.get('text')) is not str: _fail('invalid_codex_page')
                        parts.append(part['text'])
                    else: skipped += 1
                text = '\n'.join(parts)
                if not text.strip(): continue
            if type(text) is not str or not text.strip(): _fail('invalid_codex_page')
            try:
                if len(text.encode()) > 12000: _fail('capture_message_limit')
            except UnicodeError: _fail('invalid_codex_page')
            messages.append(dict(turn_id=turn['id'], item_id=item['id'],
                                 observed_actor='human' if kind == 'userMessage' else 'assistant', text=text))
    if type(page.get('nextCursor')) not in (str, type(None)): _fail('invalid_codex_page')
    return dict(messages=messages, older_turns_omitted=page.get('nextCursor') is not None,
                active_turns=active, unsupported_items=skipped+transport_counts['capture_unsupported_items'],incomplete_item_turns=incomplete,
                item_pages=transport_counts['item_pages'],ignored_private_items=transport_counts['ignored_private_items'])


class CodexAppServerCapture(CodexExecCapture):
    surface = 'codex_app_server'

    def capabilities(self):
        return dict(source_surface=self.surface, user_messages=True, reasoning=False,
                    desktop_sessions='selected thread availability requires host verification',
                    automatic_discovery=False, model_dispatch=False, max_turns=MAX_TURNS)

    def collect(self, scope, project, *, capture_id, client, limit=MAX_TURNS):
        identifier(capture_id)
        if type(limit) is not int or not 1<=limit<=MAX_TURNS: _fail('capture_limit')
        # Scope validated before any source read. No host request inside a transaction.
        with self.core.read_snapshot():
            binding = self._authorize(scope, project, capture_id)
        page = client.read_turns(binding['thread_id'], limit=limit)
        parsed = public_messages(page)
        # Persist sanitized public content only; provider metadata/error bodies stay out.
        with self.core.transaction():
            current = self._authorize(scope, project, capture_id)
            if current != binding: _fail('capture_binding_mismatch')
            old = next((v for v in reversed(self.sources._rows(project, 'codex_app_server_collected')) if v['id'] == capture_id), None)
            fingerprints = dict(old['fingerprints']) if old else {}
            ids = []; incoming = parsed.pop('messages')
            for message in incoming:
                key = digest(canonical([message['turn_id'], message['item_id']]))
                safe_text, _ = redact_text(message['text'])
                sha = digest(canonical(dict(message,text=safe_text)))
                if key in fingerprints and fingerprints[key] != sha:
                    _fail('capture_item_changed')
                provenance = dict(id=capture_id, thread_id=binding['thread_id'],
                    turn_id=message['turn_id'], item_id=message['item_id'],
                    provider_version=binding['provider_version'], source_surface=self.surface,
                    observed_actor=message['observed_actor'], coverage='partial')
                source = self.sources._ingest(scope, project, text=message['text'], capture=provenance, in_transaction=True)
                fingerprints[key] = sha; ids.append(source['id'])
            if len(fingerprints) > 32: _fail('capture_limit')
            receipt = dict(id=capture_id, source_ids=ids, fingerprints=fingerprints, **parsed,
                           coverage='partial', missing=['bounded_history','non_text_content','host_continuity_not_verified'])
            if old != receipt:
                self.sources._put(scope, project, 'codex_app_server_collected', receipt)
            return receipt

"""Page-atomic selected-thread capture; network reads never hold a DB transaction."""
from copy import deepcopy

from packages.capture.codex.app_server import public_messages
from packages.capture.codex.exec_stream import _fail
from packages.domain.project_binding import identifier
from packages.storage.project_store import digest

ACTION = 'codex_app_server_checkpoint'


def latest(adapter, project, capture_id):
    return next((v for v in reversed(adapter.sources._rows(project, ACTION))
                 if v['id'] == capture_id), None)


def collect_incremental(adapter, scope, project, *, capture_id, client, limit):
    with adapter.core.read_snapshot():
        binding = adapter._authorize(scope, project, capture_id)
        before = latest(adapter, project, capture_id)
    profile = client.profile_ref
    identifier(profile)
    if before and before['profile_ref'] != profile: _fail('capture_binding_mismatch')
    metadata = client.read_metadata(binding['thread_id'], limit=limit)
    # Validate identities, status and bounds before persisting metadata. No text required.
    if type(metadata) is not dict or type(metadata.get('data')) is not list or len(metadata['data']) > limit:
        _fail('invalid_codex_page')
    turns = metadata['data']; statuses = {}
    for turn in turns:
        if type(turn) is not dict: _fail('invalid_codex_page')
        identifier(turn.get('id'))
        if turn['id'] in statuses or turn.get('status') not in ('completed','interrupted','failed','inProgress'):
            _fail('invalid_codex_page')
        statuses[turn['id']] = turn['status']
    if type(metadata.get('nextCursor')) not in (str, type(None)): _fail('invalid_codex_page')
    # An unfinished selected batch cannot silently fall out of the newest-turn window.
    if before and any(not t['done'] for t in before['turns']):
        selected = deepcopy(before['turns'])
        for turn in selected:
            if turn['status'] == 'inProgress' and turn['id'] not in statuses:
                _fail('capture_pending_turn_unavailable')
            if turn['id'] in statuses: turn['status'] = statuses[turn['id']]
    else:
        old = {t['id']: t for t in before['turns']} if before else {}
        selected = [deepcopy(old[t['id']]) if t['id'] in old else
                    dict(id=t['id'], status=t['status'], cursor=None, last_item_id=None,
                         done=False, pending_assistant=False, cursor_hashes=[], ignored_private_items=0, unsupported_items=0)
                    for t in reversed(turns)]
        for turn in selected: turn['status'] = statuses[turn['id']]
    state = dict(id=capture_id, profile_ref=profile, revision=(before['revision'] if before else 0)+1,
                 turns=selected, coverage='partial', older_turns_omitted=metadata.get('nextCursor') is not None)

    def commit(expected, updated, parsed=None):
        with adapter.core.transaction():
            if adapter._authorize(scope, project, capture_id) != binding: _fail('capture_binding_mismatch')
            if latest(adapter, project, capture_id) != expected: _fail('capture_checkpoint_stale')
            receipt = adapter._persist(scope, project, capture_id, binding, parsed, profile_ref=profile) if parsed is not None else None
            adapter.sources._put(scope, project, ACTION, updated)
            return receipt

    commit(before, state)
    pages = 0; source_ids = []; last_receipt = None
    per_turn = min(16, 32 // max(1, len(selected)))
    for index in range(len(selected)):
        for _ in range(per_turn):
            current = state['turns'][index]
            if current['done']: break
            with adapter.core.read_snapshot():
                if adapter._authorize(scope, project, capture_id) != binding: _fail('capture_binding_mismatch')
                if latest(adapter, project, capture_id) != state: _fail('capture_checkpoint_stale')
            result = client.read_item_page(binding['thread_id'], current['id'], cursor=current['cursor'])
            next_cursor = result['next_cursor']
            if next_cursor is not None:
                hashed = digest(next_cursor)
                if hashed in current['cursor_hashes']: _fail('invalid_codex_cursor')
                if len(current['cursor_hashes']) >= 256: _fail('capture_limit')
            pending = current['status'] == 'inProgress' and any(i['type']=='agentMessage' for i in result['items'])
            normalized = dict(data=[dict(id=current['id'],status=current['status'],items=result['items'])],
                              nextCursor=metadata.get('nextCursor'), item_pages=1,
                              ignored_private_items=result['ignored_private_items'],
                              capture_unsupported_items=result['capture_unsupported_items'])
            parsed = public_messages(normalized)
            updated = deepcopy(state); target = updated['turns'][index]
            target['pending_assistant'] = pending
            if not pending:
                target['ignored_private_items'] += result['ignored_private_items']
                target['unsupported_items'] += result['capture_unsupported_items']
            if not pending:
                target['last_item_id'] = result['last_item_id'] or target['last_item_id']
                # An active EOF must be revisited; terminal EOF alone closes this frontier.
                target['done'] = next_cursor is None and current['status'] != 'inProgress'
                if next_cursor is not None:
                    target['cursor'] = next_cursor
                    target['cursor_hashes'].append(digest(next_cursor))
            updated['revision'] += 1
            last_receipt = commit(state, updated, parsed)
            state = updated; pages += 1; source_ids.extend(last_receipt['source_ids'])
            if pending or next_cursor is None: break
    return dict(id=capture_id, source_ids=list(dict.fromkeys(source_ids)), coverage='partial',
                item_pages=pages, checkpoint_revision=state['revision'],
                pending_turns=sum(not t['done'] for t in state['turns']),
                pending_assistant_turns=sum(t['pending_assistant'] for t in state['turns']),
                older_turns_omitted=state['older_turns_omitted'],
                ignored_private_items=sum(t['ignored_private_items'] for t in state['turns']),
                unsupported_items=sum(t['unsupported_items'] for t in state['turns']),
                missing=['bounded_history','non_text_content','host_continuity_not_verified'])

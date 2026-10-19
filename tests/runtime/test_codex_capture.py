"""Synthetic public CLI wire examples; no Codex process or model is started."""
import json
from contextlib import redirect_stdout
import io
from pathlib import Path
import unittest
import test_questions as fixtures
from packages.capture.codex.exec_stream import CodexExecCapture, parse_snapshot, MAX_STREAM_BYTES
from packages.capture.dialogue_review import DialogueReviewService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace
from scripts.capture_codex_exec import main, selected_snapshot


def wire(*events):
    return b''.join((json.dumps(e)+'\n').encode() for e in events)


def stream(text='Add a backup test.', item='item_1'):
    return wire(dict(type='thread.started', thread_id='thread_1'), dict(type='turn.started'),
                dict(type='item.completed', item=dict(type='agent_message', id=item, text=text)))


class CodexCaptureTests(unittest.TestCase):
    def setUp(self):
        fixtures.QuestionTests.setUp(self)
        self.adapter = CodexExecCapture(self.core)
        self.connect()

    def connect(self):
        return self.adapter.connect(self.owner, 'p', capture_id='capture_1',
                                    thread_id='thread_1', provider_version='fixture-1', consent=True)

    def collect(self, raw=None):
        return self.adapter.collect(self.owner, 'p', capture_id='capture_1', snapshot=stream() if raw is None else raw)

    def test_capture_without_turn_end_is_durable_redacted_and_not_applied(self):
        result = self.collect(stream('Add backup test. password=example-sensitive-password'))
        self.assertEqual(result['state'], 'Waiting for turn end')
        source = self.adapter.sources.view(self.owner, 'p')['imports'][0]['source']
        self.assertEqual(source['source_kind'], 'codex_exec_jsonl')
        self.assertEqual(source['capture']['observed_actor'], 'assistant')
        self.assertNotIn('example-sensitive-password', json.dumps(source))
        self.assertEqual(self.core.records(self.owner, 'p')['records'], [])
        self.assertEqual(self.adapter.sources.analyze(self.owner, 'p', source['id'])['model_calls'], 0)

    def test_retry_restart_and_turn_end_do_not_duplicate_source(self):
        first = self.collect(); self.assertEqual(first, self.collect())
        with Workspace(self.path, 'w') as core:
            owner = core.authority.issue_scope('owner')
            self.assertEqual(CodexExecCapture(core).collect(owner, 'p', capture_id='capture_1', snapshot=stream()), first)
        ended = self.collect(stream()+wire(dict(type='turn.completed', usage={})))
        self.assertEqual(ended['state'], 'Idle')
        self.assertEqual(ended['source_ids'], first['source_ids'])
        self.assertEqual(len(self.adapter.sources.view(self.owner, 'p')['imports']), 1)

    def test_partial_line_waits_and_append_captures_completed_message(self):
        raw = stream(); result = self.collect(raw[:-5])
        self.assertEqual(result['source_ids'], [])
        self.assertGreater(result['pending_bytes'], 0)
        self.assertEqual(len(self.collect(raw)['source_ids']), 1)

    def test_rewritten_or_truncated_prefix_rejected_preserves_accepted_source(self):
        self.collect()
        for raw in (stream('A changed message.'), stream()[:20]):
            with self.subTest(raw_length=len(raw)), self.assertRaises(ContractError):
                self.collect(raw)
        self.assertEqual(len(self.adapter.sources.view(self.owner, 'p')['imports']), 1)

    def test_ignored_reasoning_tools_and_provider_error_never_persist(self):
        raw = wire(dict(type='thread.started', thread_id='thread_1'), dict(type='turn.started'))
        for kind in ('reasoning', 'command_execution', 'mcp_tool_call'):
            raw += wire(dict(type='item.completed', item=dict(id='private', type=kind, text='DO-NOT-PERSIST', aggregated_output='DO-NOT-PERSIST')))
        raw += wire(dict(type='turn.failed', error=dict(message='DO-NOT-PERSIST')))
        self.assertEqual(self.collect(raw)['state'], 'Failed')
        self.assertNotIn('DO-NOT-PERSIST', str(self.core.db.execute('SELECT ref FROM audit').fetchall()))

    def test_wrong_session_foreign_scope_missing_consent_disconnect(self):
        with self.assertRaises(ContractError):
            self.collect(stream().replace(b'thread_1', b'thread_2'))
        with self.assertRaises(ContractError):
            self.adapter.collect(self.owner, 'other', capture_id='capture_1', snapshot=stream())
        with self.assertRaises(ContractError):
            self.adapter.connect(self.owner, 'p', capture_id='no', thread_id='thread_1', provider_version='v1', consent=False)
        self.collect(); self.adapter.disconnect(self.owner, 'p', capture_id='capture_1')
        with self.assertRaises(ContractError): self.collect()
        self.assertEqual(len(self.adapter.sources.view(self.owner, 'p')['imports']), 1)

    def test_duplicate_item_conflict_unknown_event_and_limits_fail_closed(self):
        for raw in (stream()+wire(dict(type='item.completed', item=dict(id='item_1', type='agent_message', text='Different'))),
                    stream()+wire(dict(type='invented.event')), b'x'*(MAX_STREAM_BYTES+1),
                    b'{"type":"thread.started","type":"turn.started"}\n',
                    wire(dict(type=[])), stream()+wire(dict(type='item.completed', item=dict(type=[])))):
            with self.subTest(length=len(raw)), self.assertRaises(ContractError): self.collect(raw)
        self.assertEqual(self.adapter.sources._rows('p', 'codex_capture_collected'), [])

    def test_item_identity_preserves_same_text_from_two_turns(self):
        raw = stream()+wire(dict(type='turn.completed', usage={}), dict(type='turn.started'),
                            dict(type='item.completed', item=dict(type='agent_message', id='item_1', text='Add a backup test.')))
        self.assertEqual(len(set(self.collect(raw)['source_ids'])), 2)

    def test_storage_failure_rolls_back_source_and_cursor(self):
        self.core.db.execute("CREATE TRIGGER capture_fail BEFORE INSERT ON audit WHEN NEW.action='codex_capture_collected' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError): self.collect()
        self.assertEqual(self.adapter.sources._rows('p', 'conversation_imported'), [])
        self.assertEqual(self.adapter.sources._rows('p', 'codex_capture_collected'), [])

    def test_current_authority_revision_required(self):
        a = self.core.authority
        a.replace_grant(self.owner, 'agent', kind='agent', readable=frozenset({'p'}), writable=frozenset({'p'}), active=True, base_revision=a.revision())
        self.owner = a.issue_scope('owner')
        with self.assertRaises(ContractError): self.collect()
        with self.assertRaises(ContractError):
            self.adapter.collect(a.issue_scope('agent'), 'p', capture_id='capture_1', snapshot=stream())

    def test_capture_to_existing_review_to_explicit_task_accept(self):
        receipt = self.collect(); source_id = receipt['source_ids'][0]
        source = self.adapter.sources._source('p', source_id)
        review = DialogueReviewService(self.core)
        request = review.prepare(self.owner, 'p', source_id=source_id)
        self.assertEqual(request['request']['source']['capture']['observed_actor'], 'assistant')
        response = dict(source_id=source_id, source_sha256=source['sha256'], context_sha256=request['context_sha256'],
                        coverage='partial', candidates=[dict(type='Task', title='Backup test', quote='Add a backup test.', intent='planned')], status_changes=[])
        with self.assertRaises(ContractError):
            review.import_response(self.owner, 'p', source_id=source_id, response_text=json.dumps(dict(response, coverage='complete')))
        analysis = review.import_response(self.owner, 'p', source_id=source_id, response_text=json.dumps(response))
        self.assertEqual(self.core.records(self.owner, 'p')['records'], [])
        self.adapter.sources.accept(self.owner, 'p', source_id=source_id, key='capture_accept',
                                    selected=[analysis['candidates'][0]['id']], base_revision=request['request']['context']['knowledge_revision'])
        self.assertEqual(len(self.core.records(self.owner, 'p')['records']), 1)

    def test_capabilities_do_not_claim_desktop_or_user_messages(self):
        caps = self.adapter.capabilities()
        self.assertFalse(caps['desktop_sessions']); self.assertFalse(caps['user_messages'])
        self.assertFalse(caps['model_dispatch'])
        parsed = parse_snapshot(stream()+wire(dict(type='item.completed', item=dict(type='new_host_item'))), 'thread_1')
        self.assertEqual(parsed['unsupported_items'], 1)

    def test_selected_file_cli_import_and_disconnect(self):
        path = Path(self.temp.name)/'selected.jsonl'; path.write_bytes(stream())
        args = ['--db', str(self.path), '--workspace', 'w', '--principal', 'owner', '--project', 'p', '--capture-id', 'capture_cli']
        with redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(args+['--snapshot', str(path), '--thread-id', 'thread_1', '--provider-version', 'fixture-1', '--consent']), 0)
        self.assertEqual(json.loads(out.getvalue())['coverage'], 'partial')
        self.assertEqual(len(self.adapter.sources.view(self.owner, 'p')['imports']), 1)
        with redirect_stdout(io.StringIO()): self.assertEqual(main(args+['--disconnect']), 0)
        link = path.with_suffix('.link'); link.symlink_to(path)
        with self.assertRaises(OSError): selected_snapshot(link)

    def test_capacity_failure_preserves_previous_receipt_and_new_batch_is_atomic(self):
        first = self.collect()
        for n in range(30): self.adapter.sources.ingest(self.owner, 'p', text='Source '+str(n))
        raw = stream()+wire(dict(type='item.completed', item=dict(type='agent_message', id='two', text='Second message.')),
                            dict(type='item.completed', item=dict(type='agent_message', id='three', text='Third message.')))
        with self.assertRaises(ContractError): self.collect(raw)
        self.assertEqual(len(self.adapter.sources.view(self.owner, 'p')['imports']), 31)
        self.assertEqual(self.adapter.sources._rows('p', 'codex_capture_collected'), [first])

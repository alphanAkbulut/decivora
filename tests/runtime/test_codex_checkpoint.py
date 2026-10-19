"""Synthetic selected-turn continuation, no user's host or provider calls."""
import json
import unittest
from unittest.mock import patch
import test_questions as fixtures
from packages.capture.codex.app_server import CodexAppServerCapture
from packages.capture.codex.checkpoint import latest
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace


class PagedClient:
    profile_ref = 'fixture_profile'

    def __init__(self, count=20):
        self.count=count; self.calls=[]; self.status='completed'; self.fail_at=None
        self.on_read=None; self.turns=None

    def read_metadata(self, thread_id, *, limit):
        return dict(data=self.turns if self.turns is not None else [dict(id='turn_1',status=self.status)],nextCursor=None)

    def read_item_page(self, thread_id, turn_id, *, cursor):
        n=int(cursor or '0'); self.calls.append((turn_id,n))
        if self.on_read: self.on_read(n)
        if n==self.fail_at: raise ContractError('codex_read_timeout','Synthetic timeout')
        # Only two public items; long excluded history must still progress.
        item=dict(id='item_'+str(n),type='userMessage',content=[dict(type='text',text='Add backup support.')]) if n==0 else dict(id='item_'+str(n),type='agentMessage',text='Backup work is planned.') if n==self.count-1 else None
        return dict(items=[item] if item else [],next_cursor=str(n+1) if n+1<self.count else None,
                    last_item_id='item_'+str(n),ignored_private_items=int(item is None),capture_unsupported_items=0)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        fixtures.QuestionTests.setUp(self)
        self.adapter=CodexAppServerCapture(self.core)
        self.adapter.connect(self.owner,'p',capture_id='capture_1',thread_id='thread_1',provider_version='fixture-1',consent=True)

    def run_capture(self, client, capture_id='capture_1'):
        return self.adapter.collect(self.owner,'p',capture_id=capture_id,client=client,limit=1)

    def test_page_budget_restart_resumes_and_does_not_reread_completed_batch(self):
        client=PagedClient(); first=self.run_capture(client)
        self.assertEqual(first['item_pages'],16); self.assertEqual(first['pending_turns'],1)
        self.assertEqual(latest(self.adapter,'p','capture_1')['turns'][0]['cursor'],'16')
        with Workspace(self.path,'w') as core:
            adapter=CodexAppServerCapture(core)
            second=adapter.collect(core.authority.issue_scope('owner'),'p',capture_id='capture_1',client=client,limit=1)
        self.assertEqual(second['item_pages'],4); self.assertEqual(second['pending_turns'],0)
        self.assertEqual([n for _,n in client.calls],list(range(20)))
        self.assertEqual(self.run_capture(client)['item_pages'],0)
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),2)

    def test_later_timeout_preserves_accepted_page_and_cursor(self):
        client=PagedClient(); client.fail_at=1
        with self.assertRaises(ContractError): self.run_capture(client)
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),1)
        self.assertEqual(latest(self.adapter,'p','capture_1')['turns'][0]['cursor'],'1')
        client.fail_at=None; self.run_capture(client)
        self.assertEqual(client.calls[2],('turn_1',1))

    def test_checkpoint_failure_rolls_back_corresponding_source(self):
        original=self.adapter.sources._put
        def put(scope, project, action, value):
            if action=='codex_app_server_checkpoint' and value['revision']>1:
                raise ContractError('fixture_rollback','Synthetic rollback')
            return original(scope,project,action,value)
        with patch.object(self.adapter.sources,'_put',side_effect=put),self.assertRaises(ContractError):
            self.run_capture(PagedClient())
        self.assertEqual(self.adapter.sources._rows('p','conversation_imported'),[])
        self.assertIsNone(latest(self.adapter,'p','capture_1')['turns'][0]['cursor'])

    def test_active_assistant_is_revisited_after_terminal_transition(self):
        client=PagedClient(2); client.status='inProgress'
        first=self.run_capture(client)
        self.assertEqual(first['pending_assistant_turns'],1)
        self.assertEqual(latest(self.adapter,'p','capture_1')['turns'][0]['cursor'],'1')
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),1)
        client.status='completed'; final=self.run_capture(client)
        self.assertEqual(final['pending_turns'],0); self.assertEqual(client.calls[-1],('turn_1',1))
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),2)

    def test_new_binding_deduplicates_local_profile_origin_and_records_receipt(self):
        self.run_capture(PagedClient(2)); self.adapter.disconnect(self.owner,'p',capture_id='capture_1')
        self.adapter.connect(self.owner,'p',capture_id='capture_2',thread_id='thread_1',provider_version='fixture-2',consent=True)
        receipt=self.run_capture(PagedClient(2),'capture_2')
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),2)
        self.assertEqual(len(receipt['source_ids']),2)
        self.assertEqual(self.adapter.sources._rows('p','codex_app_server_collected')[-1]['id'],'capture_2')
        with self.assertRaises(ContractError): self.run_capture(PagedClient(2))
        other=PagedClient(2); other.profile_ref='different_profile'
        with self.assertRaises(ContractError): self.run_capture(other,'capture_2')

    def test_revocation_during_next_read_keeps_only_previous_accepted_page(self):
        client=PagedClient()
        def revoke(n):
            if n==1: self.adapter.disconnect(self.owner,'p',capture_id='capture_1')
        client.on_read=revoke
        with self.assertRaises(ContractError): self.run_capture(client)
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),1)
        self.assertEqual(latest(self.adapter,'p','capture_1')['turns'][0]['cursor'],'1')

    def test_concurrent_checkpoint_change_fences_stale_page(self):
        client=PagedClient()
        def race(n):
            state=latest(self.adapter,'p','capture_1'); state['revision']+=1
            with self.core.transaction(): self.adapter.sources._put(self.owner,'p','codex_app_server_checkpoint',state)
        client.on_read=race
        with self.assertRaises(ContractError) as error: self.run_capture(client)
        self.assertEqual(error.exception.code,'capture_checkpoint_stale')
        self.assertEqual(self.adapter.sources._rows('p','conversation_imported'),[])

    def test_pending_completed_turn_retained_when_newest_window_moves(self):
        client=PagedClient(); self.run_capture(client)
        client.turns=[]
        receipt=self.run_capture(client)
        self.assertEqual(receipt['pending_turns'],0)
        self.assertEqual(client.calls[-1],('turn_1',19))
        self.assertNotIn('text',json.dumps(latest(self.adapter,'p','capture_1')))

    def test_active_missing_turn_and_cursor_cycle_stop_without_silent_reset(self):
        client=PagedClient(2); client.status='inProgress'; self.run_capture(client)
        client.turns=[]
        with self.assertRaises(ContractError) as error: self.run_capture(client)
        self.assertEqual(error.exception.code,'capture_pending_turn_unavailable')
        self.assertEqual(latest(self.adapter,'p','capture_1')['turns'][0]['cursor'],'1')

    def test_backup_restore_preserves_source_and_frontier_without_external_dispatch(self):
        client=PagedClient(); self.run_capture(client)
        backup=self.path.with_name('checkpoint-backup.sqlite')
        manifest=self.core.backup(self.owner,backup)
        self.assertEqual(manifest['external_dispatches'],0)
        restored=Workspace.restore(backup,self.path.with_name('checkpoint-restored.sqlite'),manifest)
        try:
            adapter=CodexAppServerCapture(restored)
            self.assertEqual(latest(adapter,'p','capture_1')['turns'][0]['cursor'],'16')
            result=adapter.collect(restored.authority.issue_scope('owner'),'p',capture_id='capture_1',client=client,limit=1)
            self.assertEqual(result['item_pages'],4)
            self.assertEqual(len(adapter.sources._rows('p','conversation_imported')),2)
        finally: restored.close()

    def test_incremental_capture_over_32_public_items_keeps_old_origin_change_guard(self):
        class ManyMessages(PagedClient):
            def read_item_page(inner,thread_id,turn_id,*,cursor):
                result=super().read_item_page(thread_id,turn_id,cursor=cursor)
                n=int(cursor or '0')
                result.update(items=[dict(id='item_'+str(n),type='userMessage',content=[dict(type='text',text='Public message '+str(n))])],ignored_private_items=0)
                return result
        client=ManyMessages(50)
        for _ in range(4):self.run_capture(client)
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),50)
        receipt=self.adapter.sources._rows('p','codex_app_server_collected')[-1]
        self.assertEqual(len(receipt['fingerprints']),32)
        self.adapter.disconnect(self.owner,'p',capture_id='capture_1')
        self.adapter.connect(self.owner,'p',capture_id='capture_2',thread_id='thread_1',provider_version='fixture-2',consent=True)
        other=ManyMessages(50);original=other.read_item_page
        def changed(*args,**kwargs):
            result=original(*args,**kwargs);result['items'][0]['content'][0]['text']='Changed historical text';return result
        other.read_item_page=changed
        with self.assertRaises(ContractError) as error:self.run_capture(other,'capture_2')
        self.assertEqual(error.exception.code,'capture_item_changed')
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),50)

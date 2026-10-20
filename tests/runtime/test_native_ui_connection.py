"""Synthetic local native host; no Codex subprocess, real chat or external API."""
from contextlib import contextmanager
from pathlib import Path
import tempfile,time,unittest,uuid
from unittest.mock import patch
from apps.local_ui.server import LocalApp
from packages.capture.codex.ui_connection import UIConnectionService,NativeConnector
from packages.domain.source_event import ContractError

class NativeUIConnectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'workspace.sqlite';self.calls=[];self.after_read=None
        @contextmanager
        def client(thread):
            self.calls.append(thread);test=self
            class Client:
                def read_turns(self,thread_id,limit):
                    if test.after_read:test.after_read()
                    return dict(data=[dict(id='turn_one',status='completed',items=[dict(id='human_one',type='userMessage',content=[dict(type='text',text='Synthetic restore task; not started.')]),dict(id='private_one',type='reasoning',text='Private fixture never stored')])],nextCursor=None)
            yield Client()
        self.connector=NativeConnector('fixture','host_fixture',client);self.app=LocalApp(self.path,native_connector=self.connector)
        self.config=dict(action='connect_codex_source',capture_id='native_one',thread_id='thread_one',expires_at=int(time.time())+600,max_reads=2,turn_limit=2,consent=True)
    def connect(self,**overrides):return self.app.command(dict(self.config,**overrides))
    def read(self,record=None,**overrides):
        record=record or self.record
        return self.app.command(dict(dict(action='read_codex_source',capture_id=record['id'],configuration_sha256=record['configuration_sha256'],read_id='read_'+uuid.uuid4().hex,consent=True),**overrides))
    def test_connect_does_not_read_and_separate_read_is_private_bounded_and_deduplicated(self):
        self.record=self.connect();self.assertEqual(self.calls,[])
        view=self.app.state()['native_connections'];self.assertEqual(view['items'][0]['status'],'Connected')
        a=self.read();b=self.read();self.assertEqual(a['source_count'],1);self.assertEqual(b['source_count'],1)
        state=self.app.state();self.assertEqual(state['native_connections']['items'][0]['status'],'Limit reached');self.assertEqual(len(state['conversation_review']['imports']),1);self.assertEqual(state['tasks'],[])
        self.assertNotIn('Private fixture',str(state));self.assertEqual(self.calls,['thread_one','thread_one'])
        with self.assertRaises(ContractError):self.read()
        reopened=LocalApp(self.path,native_connector=self.connector);self.assertEqual(reopened.state()['native_connections']['items'][0]['reads'],2);self.assertEqual(len(self.calls),2)
    def test_missing_consent_caps_duplicate_and_exact_revision_before_host_read(self):
        for changes in [dict(consent=False),dict(max_reads=0),dict(turn_limit=11),dict(expires_at=0)]:
            with self.assertRaises(ContractError):self.connect(**changes)
        self.record=self.connect()
        with self.assertRaises(ContractError):self.connect(capture_id='duplicate')
        with self.assertRaises(ContractError):self.read(configuration_sha256='0'*64)
        with self.assertRaises(ContractError):self.read(consent=False)
        self.assertEqual(self.calls,[])
    def test_expiry_host_change_and_disconnect_block_before_host_read(self):
        self.record=self.connect()
        with patch('time.time',return_value=self.record['expires_at']+1):
            with self.assertRaises(ContractError):self.read()
        other=LocalApp(self.path,native_connector=NativeConnector('fixture','another_host',self.connector.open_client))
        with self.assertRaises(ContractError):other.command(dict(action='read_codex_source',capture_id=self.record['id'],configuration_sha256=self.record['configuration_sha256'],read_id='read_changed_host',consent=True))
        self.app.command(dict(action='disconnect_codex_source',capture_id=self.record['id']))
        with self.assertRaises(ContractError):self.read()
        self.assertEqual(self.calls,[])
    def test_revoke_during_host_read_prevents_source_commit(self):
        self.record=self.connect();self.after_read=lambda:self.app.command(dict(action='disconnect_codex_source',capture_id=self.record['id']))
        with self.assertRaises(ContractError):self.read()
        self.assertEqual(self.app.state()['conversation_review']['total'],0)
        self.assertEqual(self.app.state()['native_connections']['items'][0]['last_result']['status'],'Read failed')
    def test_expiry_during_read_prevents_source_commit(self):
        self.record=self.connect();clock=patch('time.time',return_value=self.record['expires_at']+1)
        self.after_read=clock.start
        try:
            with self.assertRaises(ContractError):self.read()
        finally:clock.stop()
        self.assertEqual(self.app.state()['conversation_review']['total'],0)
    def test_unfinished_claim_stops_recovery_and_authority_change_is_not_renewal(self):
        self.record=self.connect()
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');service=UIConnectionService(core,self.connector)
            with core.transaction():service.sources._put(owner,'personal',service.START,dict(id='native_one',read_id='interrupted',recorded_at=time.time()))
        with self.assertRaises(ContractError) as error:self.read()
        self.assertEqual(error.exception.code,'capture_review_required');self.assertEqual(self.calls,[])
        with self.app.core() as core:
            a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision())
        self.assertEqual(self.app.state()['native_connections']['items'][0]['status'],'Permission changed')
        with self.assertRaises(ContractError):self.read()
    def test_setup_failure_rolls_back_binding_and_network_failure_uses_a_durable_read(self):
        from packages.capture.conversations import ConversationService
        original=ConversationService._put
        def broken(service,scope,project,action,value):
            if action==UIConnectionService.CONFIG:raise RuntimeError('injected after binding')
            return original(service,scope,project,action,value)
        with patch.object(ConversationService,'_put',broken):
            with self.assertRaises(RuntimeError):self.connect()
        with self.app.core() as core:
            self.assertEqual(UIConnectionService(core).rows('personal','codex_capture_connected'),[])
        self.record=self.connect()
        self.after_read=lambda:(_ for _ in ()).throw(OSError('Private host details must not escape'))
        with self.assertRaises(ContractError):self.read()
        item=self.app.state()['native_connections']['items'][0]
        self.assertEqual(item['reads'],1);self.assertEqual(item['last_result']['code'],'codex_host_unavailable')
        self.assertNotIn('Private host details',str(item))

    def test_duplicate_read_command_returns_receipt_without_second_host_read(self):
        self.record=self.connect();one=self.read(read_id='same_command');two=self.read(read_id='same_command')
        self.assertEqual(one,two);self.assertEqual(self.calls,['thread_one'])
        self.assertEqual(self.app.state()['native_connections']['items'][0]['reads'],1)

    def test_default_and_test_environment_do_not_implicitly_enable_host(self):
        offline=LocalApp(self.path)
        with self.assertRaises(ContractError):offline.command(self.config)
        with self.assertRaises(ContractError):LocalApp(Path(self.temp.name)/'test.sqlite',environment='test',native_connector=self.connector)
        self.assertEqual(self.calls,[])

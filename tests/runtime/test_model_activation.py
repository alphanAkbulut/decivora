"""Durable activation gates over real local command/queue paths, fake model only."""
import json,time,unittest
from unittest.mock import patch
import test_granted_extractors as fixtures
from apps.local_ui.server import LocalApp
from packages.capture.model_activation import ModelActivationService,ManagedResponsesFactory
from packages.capture.conversations import ConversationService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class ModelActivationTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixtures.GrantedExtractorTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.app=LocalApp(self.fx.path,extractor_factory=ManagedResponsesFactory(self.fx.factory,'activation_one'))
        self.expiry=min(g['expires_at'] for g,_ in self.fx.entries)
        self.create=dict(action='create_model_activation',activation_id='activation_one',grant_ids=[g['id'] for g,_ in self.fx.entries],expires_at=self.expiry,reason='Explicit synthetic setup; no real data/network.')
        self.record=self.app.command(self.create)

    def change(self,state,record=None):
        record=record or self.record
        result=self.app.command(dict(action='change_model_activation',activation_id=record['id'],base_revision=record['revision'],configuration_sha256=record['configuration_sha256'],state=state,reason='Synthetic lifecycle test.'))
        self.record=result;return result

    def process(self,limit=1):return self.app.command(dict(action='process_conversation_queue',limit=limit))

    def test_default_pause_then_active_dispatch_then_pause_resume_and_revoke(self):
        self.assertEqual(self.record['state'],'Paused');self.assertEqual(self.process()['attempted'],0);self.assertEqual(self.fx.calls,[])
        self.change('Active');self.assertEqual(self.process()['attempted'],1)
        self.change('Paused');self.assertEqual(self.process()['attempted'],0);self.assertEqual(len(self.fx.calls),1)
        self.change('Active');self.assertEqual(self.process()['attempted'],1);self.assertEqual(len(self.fx.calls),2)
        self.change('Revoked')
        with self.assertRaises(ContractError):self.change('Active')
        self.assertEqual(self.app.state()['tasks'],[])
        view=self.app.state()['model_activations'];self.assertEqual(view['items'][0]['effective_state'],'Revoked')
        operations=self.app.operations_view();self.assertTrue(any(r['action']=='change_model_activation' for r in operations['runs']))
        self.assertNotIn('Please add',json.dumps(operations))

    def test_pause_after_factory_selection_prevents_admission_and_does_not_reserve(self):
        self.change('Active')
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');grant=self.fx.entries[0][0]
            extractor=self.app.extractor_factory.bind_scope(core,owner,'personal')(self.fx.sources[0],grant)
            self.change('Paused')
            with self.assertRaises(ContractError) as error:ConversationService(core).analyze(owner,'personal',self.fx.sources[0]['id'],extractor)
            self.assertEqual(error.exception.code,'activation_inactive')
            self.assertEqual(ConversationService(core)._rows('personal','conversation_analysis_started'),[])
        self.assertEqual(self.fx.calls,[])

    def test_previously_selected_extractor_stays_stale_after_pause_resume(self):
        self.change('Active')
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner')
            extractor=self.app.extractor_factory.bind_scope(core,owner,'personal')(self.fx.sources[0],self.fx.entries[0][0])
            self.change('Paused');self.change('Active')
            with self.assertRaises(ContractError):ConversationService(core).analyze(owner,'personal',self.fx.sources[0]['id'],extractor)
        self.assertEqual(self.fx.calls,[])

    def test_stale_configuration_revision_and_foreign_project_cannot_apply(self):
        original=dict(self.record);self.change('Active')
        with self.assertRaises(ContractError):self.change('Paused',original)
        body=dict(action='change_model_activation',activation_id=self.record['id'],base_revision=self.record['revision'],configuration_sha256='0'*64,state='Revoked',reason='Fixture')
        with self.assertRaises(ContractError):self.app.command(body)
        with self.assertRaises(ContractError):self.app.command(dict(project_id='foreign',command=self.create))
        self.assertEqual(self.fx.calls,[])

    def test_expiry_and_authority_change_do_not_silently_renew(self):
        self.change('Active')
        with patch('packages.capture.model_activation.time.time',return_value=self.expiry+1):
            self.assertEqual(self.app.state()['model_activations']['items'][0]['effective_state'],'Expired')
            self.assertEqual(self.process()['attempted'],0)
        with self.app.core() as core:
            a=core.authority;owner=a.issue_scope('local_owner')
            a.replace_grant(owner,'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision())
        self.assertEqual(self.app.state()['model_activations']['items'][0]['effective_state'],'Permission changed')
        self.assertEqual(self.process()['attempted'],0)
        with self.assertRaises(ContractError):
            self.change('Paused');self.change('Active')
        self.assertEqual(self.fx.calls,[])

    def test_create_is_idempotent_no_new_grant_and_cannot_expand_expiry(self):
        self.assertEqual(self.app.command(self.create),self.record)
        for fields in (dict(expires_at=self.expiry+1),dict(grant_ids=['unknown']),dict(grant_ids=[]),dict(grant_ids=[self.create['grant_ids'][0]]*2)):
            with self.assertRaises(ContractError):self.app.command(dict(self.create,activation_id='another',**fields))
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');self.assertEqual(len(ConversationService(core)._rows('personal','conversation_dispatch_authorized')),2)
            a=core.authority;a.replace_grant(owner,'agent',kind='agent',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision())
            with self.assertRaises(ContractError):ModelActivationService(core).create(a.issue_scope('agent'),'personal',**{k:v for k,v in self.create.items() if k!='action'})
        self.assertEqual(self.fx.calls,[])

    def test_restart_backup_restore_preserves_revoked_history(self):
        self.change('Active');self.change('Revoked')
        app=LocalApp(self.fx.path,extractor_factory=self.app.extractor_factory);self.assertEqual(app.state()['model_activations']['items'][0]['state'],'Revoked')
        with app.core() as core:
            owner=core.authority.issue_scope('local_owner');backup=self.fx.path.with_name('backup.sqlite');manifest=core.backup(owner,backup)
        with Workspace.restore(backup,self.fx.path.with_name('restored.sqlite'),manifest) as core:
            owner=core.authority.issue_scope('local_owner');service=ModelActivationService(core)
            self.assertEqual(service.view(owner,'personal')['items'][0]['effective_state'],'Revoked');self.assertEqual(len(service._history('personal')),3)

    def test_audit_failure_rolls_back_activation_state(self):
        with self.app.core() as core:
            core.db.execute("CREATE TRIGGER deny_activation BEFORE INSERT ON audit WHEN NEW.action='conversation_model_activation' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.change('Active')
        self.assertEqual(self.app.state()['model_activations']['items'][0]['state'],'Paused');self.assertEqual(self.fx.calls,[])

    def test_missing_activation_waits_without_constructing_provider(self):
        app=LocalApp(self.fx.path,extractor_factory=ManagedResponsesFactory(lambda *args:self.fail('Must not construct a provider'),'missing'))
        self.assertEqual(app.command(dict(action='process_conversation_queue',limit=2))['attempted'],0)
        self.assertEqual(self.fx.calls,[])

    def test_inflight_response_is_retained_after_pause_but_next_source_waits(self):
        from packages.capture.granted_extractors import GrantedResponsesFactory
        self.change('Active')
        def send(payload):
            self.change('Paused')
            return self.fx.send(payload)
        app=LocalApp(self.fx.path,extractor_factory=ManagedResponsesFactory(GrantedResponsesFactory([(grant,send) for grant,_ in self.fx.entries]),'activation_one'))
        result=app.command(dict(action='process_conversation_queue',limit=2))
        self.assertEqual(result['attempted'],1);self.assertEqual(len(self.fx.calls),1)
        self.assertEqual(result['outcomes'][0]['status'],'Ready for review')
        self.assertEqual(result['queue']['counts'],{'Ready for review':1,'Waiting for model':1})

    def test_unmanaged_legacy_route_cannot_bypass_a_saved_pause(self):
        app=LocalApp(self.fx.path,extractor_factory=self.fx.factory)
        result=app.command(dict(action='process_conversation_queue',limit=2))
        self.assertEqual(result['outcomes'][0]['code'],'activation_required');self.assertEqual(self.fx.calls,[])
        self.change('Active');self.change('Revoked')
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner')
            extractor=self.fx.factory(self.fx.sources[0],self.fx.entries[0][0])
            with self.assertRaises(ContractError):ConversationService(core).analyze(owner,'personal',self.fx.sources[0]['id'],extractor)
        self.assertEqual(self.fx.calls,[])

    def test_http_activation_and_queue_keep_session_csrf_and_separate_review(self):
        from apps.local_ui.server import make_server
        import threading,urllib.request,urllib.error
        server=make_server(self.fx.path,extractor_factory=self.app.extractor_factory)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            headers={'Content-Type':'application/json','Origin':server.origin,'Cookie':'decivora_session='+server.app.cookie,'X-CSRF-Token':server.app.csrf}
            body=dict(action='change_model_activation',activation_id=self.record['id'],base_revision=self.record['revision'],configuration_sha256=self.record['configuration_sha256'],state='Active',reason='Synthetic HTTP control test')
            def call(body,headers):
                request=urllib.request.Request(server.origin+'/api/command',data=json.dumps(body).encode(),headers=headers,method='POST')
                try:
                    with urllib.request.urlopen(request) as response:return response.status,json.load(response)
                except urllib.error.HTTPError as response:return response.code,json.load(response)
            self.assertEqual(call(body,{'Content-Type':'application/json','Origin':server.origin})[0],403)
            self.assertEqual(call(body,dict(headers,**{'X-CSRF-Token':''}))[0],403)
            status,response=call(body,headers);self.assertEqual(status,200);self.assertEqual(response['state'],'Active')
            status,response=call(dict(action='process_conversation_queue',limit=2),headers)
            self.assertEqual(status,200);self.assertEqual(response['attempted'],2);self.assertEqual(len(self.fx.calls),2)
            self.assertEqual(server.app.state()['tasks'],[])
        finally:server.shutdown();server.server_close();thread.join(timeout=2)

    def test_full_control_history_freezes_new_dispatch_instead_of_leaving_active(self):
        self.change('Active')
        with self.app.core() as core:
            service=ModelActivationService(core);owner=core.authority.issue_scope('local_owner')
            for _ in range(510):service.sources._put(owner,'personal',service.ACTION,self.record)
        self.assertEqual(self.app.state()['model_activations']['items'][0]['effective_state'],'History capacity reached')
        self.assertEqual(self.process()['attempted'],0)
        with self.assertRaises(ContractError):self.change('Paused')
        self.assertEqual(self.fx.calls,[])

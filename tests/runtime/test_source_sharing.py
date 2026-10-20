"""Source sharing and first-task scope over a fake local transport; no API/key."""
from pathlib import Path
import json,tempfile,time,unittest
from unittest.mock import patch
from apps.local_ui.server import LocalApp
from packages.capture.source_sharing import SharingProfile,SourceSharingService
from packages.capture.conversations import ConversationService
from packages.domain.source_event import ContractError

class SourceSharingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'workspace.sqlite';self.calls=[]
        def send(payload):
            self.calls.append(payload);request=json.loads(payload['input']);source=request['source']
            output=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=request['context_sha256'],coverage='partial',candidates=[dict(type='Task',title='Restore check',quote=source['text'],intent='proposed')],status_changes=[],answer_proposals=[],relation_proposals=[],question_proposals=[],clarification_proposals=[])
            return dict(status='completed',usage=dict(total_tokens=100),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])
        self.profile=SharingProfile('fixture',('fixture-model',),int(time.time())+3600,10000,2000,3000000,200,100000,'a'*64,send)
        self.app=LocalApp(self.path,sharing_profile=self.profile)
        self.source=self.app.command(dict(action='import_conversation',text='Add a restore check; not started.'))['source']
    def prepare(self):
        return self.app.command(dict(action='prepare_source_sharing',source_id=self.source['id'],model='fixture-model',max_output_tokens=1000,reserved_tokens=11000,expires_at=int(time.time())+600,reason='Explicit synthetic data/context review'))
    def approve(self,prepared):return self.app.command(dict(action='approve_source_sharing',plan_id=prepared['plan']['id'],consent=True))
    def activate(self,grant):
        activation=self.app.command(dict(action='create_model_activation',activation_id='sharing_active',grant_ids=[grant['grant_id']],expires_at=int(time.time())+300,reason='Synthetic activation'))
        self.app.command(dict(action='change_model_activation',activation_id=activation['id'],base_revision=activation['revision'],configuration_sha256=activation['configuration_sha256'],state='Active',reason='Separate synthetic activation'))
    def test_preview_approval_activation_dispatch_and_first_scope_are_separate(self):
        prepared=self.prepare();self.assertEqual(prepared['preview']['source']['text'],self.source['text']);self.assertEqual(self.calls,[])
        receipt=self.approve(prepared);self.assertEqual(receipt,self.approve(prepared));self.assertEqual(self.calls,[])
        self.assertEqual(self.app.command(dict(action='analyze_conversation',source_id=self.source['id']))['status'],'Waiting for model')
        self.activate(receipt);analysis=self.app.command(dict(action='analyze_conversation',source_id=self.source['id']));self.assertEqual(analysis['status'],'Ready for review');self.assertEqual(len(self.calls),1);self.assertEqual(self.app.state()['tasks'],[])
        applied=self.accept_scope('approved');self.assertEqual(applied['knowledge_revision'],self.app.state()['snapshot']);task=self.app.state()['tasks'][0];self.assertEqual(task['acceptance']['current']['version'],1);self.assertFalse(task['workflow']['verification']['passed']);self.assertEqual(task['lane'],'To Do')
        self.assertTrue(all(r['status']=='not_run' for r in task['workflow']['verification']['results']))
    def accept_scope(self,mode):
        state=self.app.state();cid=state['conversation_review']['imports'][0]['candidates'][0]['id']
        review=dict(candidate=cid,mode=mode,criteria=['Restore check is present.'] if mode=='approved' else [],dod=['Evidence is reviewed.'] if mode=='approved' else [],clarification='Which restore case must be checked?' if mode=='clarify' else '',reason='Human fixture scope review')
        body=dict(action='accept_candidates',source_id=self.source['id'],key='scope_accept',selected=[cid],base_revision=state['snapshot'],scope_reviews=[review])
        result=self.app.command(body);self.assertEqual(self.app.command(body),result);return result
    def test_missing_scope_creates_linked_clarification_without_extra_task_or_contract(self):
        self.activate(self.approve(self.prepare()));self.app.command(dict(action='analyze_conversation',source_id=self.source['id']));self.accept_scope('clarify')
        state=self.app.state();self.assertEqual(len(state['tasks']),1);self.assertIsNone(state['tasks'][0]['acceptance']['current']);self.assertEqual(len(state['task_clarifications']),1);self.assertEqual(state['task_clarifications'][0]['task'],state['tasks'][0]['id']);self.assertEqual(state['task_clarifications'][0]['origin'],'first_task_human_scope_review')
    def test_stale_context_or_expiry_cannot_create_grant_or_budget(self):
        prepared=self.prepare();self.app.command(dict(action='create_task',title='Changed context',description='Synthetic context change'))
        with self.assertRaises(ContractError):self.approve(prepared)
        with self.app.core() as core:
            self.assertEqual(core.db.execute('SELECT count(*) FROM run_budgets').fetchone()[0],0)
            self.assertEqual(ConversationService(core)._rows('personal','conversation_dispatch_authorized'),[])
        with patch('time.time',return_value=self.profile.expires_at+1):
            with self.assertRaises(ContractError):self.prepare()
        self.assertEqual(self.calls,[])
    def test_approval_audit_failure_rolls_back_budget_and_grant(self):
        prepared=self.prepare();original=ConversationService._put
        def broken(service,scope,project,action,value):
            if action==SourceSharingService.APPROVAL:raise RuntimeError('injected approval failure')
            return original(service,scope,project,action,value)
        with patch.object(ConversationService,'_put',broken):
            with self.assertRaises(RuntimeError):self.approve(prepared)
        with self.app.core() as core:
            self.assertEqual(core.db.execute('SELECT count(*) FROM run_budgets').fetchone()[0],0);self.assertEqual(ConversationService(core)._rows('personal','conversation_dispatch_authorized'),[])
        self.assertEqual(self.calls,[])
    def test_scope_failure_rolls_back_new_task_and_contract(self):
        self.activate(self.approve(self.prepare()));self.app.command(dict(action='analyze_conversation',source_id=self.source['id']));state=self.app.state();cid=state['conversation_review']['imports'][0]['candidates'][0]['id']
        with self.assertRaises(ContractError):self.app.command(dict(action='accept_candidates',source_id=self.source['id'],key='bad_scope',selected=[cid],base_revision=state['snapshot'],scope_reviews=[dict(candidate=cid,mode='approved',criteria=['One criterion'],dod=[],clarification='',reason='Incomplete contract')]))
        self.assertEqual(self.app.state()['tasks'],[])
    def test_dynamic_activation_supports_bounded_worker_pass(self):
        self.activate(self.approve(self.prepare()));activation=self.app.state()['model_activations']['items'][0]
        loop=self.app.command(dict(action='create_processing_loop',loop_id='dynamic_loop',activation_id=activation['id'],activation_sha256=activation['configuration_sha256'],max_passes=1,max_sources_per_pass=1,max_total_sources=1,interval_seconds=1,expires_at=int(time.time())+100,reason='Explicit synthetic worker plan'))
        self.assertEqual(self.calls,[])
        result=self.app.command(dict(action='run_processing_pass',loop_id=loop['id'],configuration_sha256=loop['configuration_sha256']))
        self.assertEqual(result['attempted'],1);self.assertEqual(len(self.calls),1)
        self.assertEqual(self.app.state()['tasks'],[])

    def test_changed_trusted_policy_cannot_reuse_old_source_consent(self):
        from dataclasses import replace
        self.activate(self.approve(self.prepare()))
        changed=LocalApp(self.path,sharing_profile=replace(self.profile,policy_sha256='c'*64))
        self.assertEqual(changed.command(dict(action='analyze_conversation',source_id=self.source['id']))['status'],'Waiting for model')
        self.assertEqual(self.calls,[])
    def test_scope_audit_failure_rolls_back_task_and_criteria(self):
        self.activate(self.approve(self.prepare()));self.app.command(dict(action='analyze_conversation',source_id=self.source['id']))
        original=ConversationService._put
        def broken(service,scope,project,action,value):
            if action=='conversation_candidates_applied':raise RuntimeError('injected final audit failure')
            return original(service,scope,project,action,value)
        with patch.object(ConversationService,'_put',broken):
            with self.assertRaises(RuntimeError):self.accept_scope('approved')
        self.assertEqual(self.app.state()['tasks'],[])
        with self.app.core() as core:self.assertEqual(core.db.execute("SELECT count(*) FROM events WHERE kind='acceptance_contract'").fetchone()[0],0)
    def test_scope_replay_cannot_change_prior_human_decision(self):
        self.activate(self.approve(self.prepare()));self.app.command(dict(action='analyze_conversation',source_id=self.source['id']));self.accept_scope('approved')
        with self.app.core() as core:
            receipt=ConversationService(core)._rows('personal','conversation_candidates_applied')[0]
        changed=dict(receipt['scope_reviews'][0],reason='Changed human review')
        with self.assertRaises(ContractError):self.app.command(dict(action='accept_candidates',source_id=self.source['id'],key='scope_accept',selected=receipt['selected'],base_revision=receipt['base_revision'],scope_reviews=[changed]))
    def test_ui_cannot_raise_policy_caps_or_select_an_unapproved_model(self):
        body=dict(action='prepare_source_sharing',source_id=self.source['id'],model='unapproved-model',max_output_tokens=1000,reserved_tokens=11000,expires_at=int(time.time())+100,reason='Unsupported model')
        with self.assertRaises(ContractError):self.app.command(body)
        with self.assertRaises(ContractError):self.app.command(dict(body,model='fixture-model',max_cost_microusd=999999999))
        self.assertEqual(self.calls,[])

    def test_restart_preserves_consent_and_requires_activation(self):
        prepared=self.prepare();self.approve(prepared);reopened=LocalApp(self.path,sharing_profile=self.profile)
        self.assertEqual(len(reopened.state()['model_sharing']['approvals']),1);self.assertEqual(reopened.command(dict(action='analyze_conversation',source_id=self.source['id']))['status'],'Waiting for model');self.assertEqual(self.calls,[])

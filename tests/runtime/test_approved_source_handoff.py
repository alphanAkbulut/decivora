"""Explicit approved-source queue handoff. Scripted transport, no external API."""
import json,threading,time,unittest
from dataclasses import replace
from unittest.mock import patch
import test_source_sharing as fixture
from apps.local_ui.server import LocalApp
from packages.capture.conversations import ConversationService
from packages.capture.model_activation import ModelActivationService
from packages.capture.processing_queue import ConversationQueue
from packages.domain.source_event import ContractError

class ApprovedSourceHandoffTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixture.SourceSharingTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.app=self.fx.app;self.prepared=self.fx.prepare();self.plan=self.prepared['plan'];self.calls=self.fx.calls
    def approve(self):return self.fx.approve(self.prepared)
    def start(self,app=None,plan=None):return (app or self.app).command(dict(action='analyze_approved_source',plan_id=(plan or self.plan)['id'],start=True))
    def test_approval_is_separate_and_explicit_start_queues_one_proposal_without_task_apply(self):
        self.approve();self.assertEqual(self.calls,[]);self.assertEqual(self.app.state()['model_activations']['items'],[])
        result=self.start();self.assertEqual((result['attempted'],result['status']),(1,'Ready for review'));self.assertFalse(result['canonical_apply'])
        self.assertEqual(len(self.calls),1);self.assertEqual(self.app.state()['tasks'],[])
        self.assertEqual(self.start()['attempted'],0);self.assertEqual(len(self.calls),1)
        self.assertEqual(self.app.state()['conversation_review']['imports'][0]['status'],'Ready for review')
        self.assertEqual(self.app.operations_view()['runs'][0]['action'],'analyze_approved_source')
    def test_exact_approved_plan_is_used_even_when_a_newer_grant_exists(self):
        self.approve()
        second=self.app.command(dict(action='prepare_source_sharing',source_id=self.plan['source'],model='fixture-model',max_output_tokens=500,reserved_tokens=10500,expires_at=int(time.time())+300,reason='Separate alternative output limit'))
        self.app.command(dict(action='approve_source_sharing',plan_id=second['plan']['id'],consent=True))
        self.assertEqual(self.start()['status'],'Ready for review')
        self.assertEqual(self.calls[0]['max_output_tokens'],1000)
        self.assertEqual(len(self.calls),1)

    def test_unapproved_source_or_start_false_cannot_activate_or_dispatch(self):
        for body in (dict(action='analyze_approved_source',plan_id=self.plan['id'],start=True),dict(action='analyze_approved_source',plan_id=self.plan['id'],start=False)):
            with self.assertRaises(ContractError):self.app.command(body)
        self.assertEqual(self.calls,[]);self.assertEqual(self.app.state()['model_activations']['items'],[])
    def test_next_captured_message_stays_pending_until_its_own_exact_consent(self):
        self.approve()
        with self.app.core() as core:
            scope=core.authority.issue_scope('local_owner')
            new=ConversationService(core)._ingest(scope,'personal',text='I started the restore check.',capture=dict(source_surface='codex_app_server',id='selected',thread_id='thread_two',turn_id='turn_two',item_id='item_two',observed_actor='user'))
        self.start();self.assertEqual(len(self.calls),1)
        items={i['source']['id']:i for i in self.app.state()['conversation_review']['imports']}
        self.assertEqual(items[new['id']]['status'],'Waiting for model')
        self.assertEqual(items[new['id']]['candidates'],[]);self.assertEqual(self.app.state()['tasks'],[])
    def test_stale_context_or_policy_cannot_start_and_does_not_leave_activation(self):
        self.approve();self.app.command(dict(action='create_task',title='New context',description='Separate human task'))
        with self.assertRaises(ContractError):self.start()
        self.assertEqual(self.calls,[]);self.assertEqual(self.app.state()['model_activations']['items'],[])
        changed=LocalApp(self.fx.path,sharing_profile=replace(self.fx.profile,policy_sha256='c'*64))
        with self.assertRaises(ContractError):self.start(changed)
        self.assertEqual(self.calls,[])
    def test_expiry_and_foreign_project_cannot_dispatch(self):
        self.approve()
        with patch('time.time',return_value=self.plan['expires_at']+1):
            with self.assertRaises(ContractError):self.start()
        with self.assertRaises(ContractError):self.app.command(dict(project_id='foreign',command=dict(action='analyze_approved_source',plan_id=self.plan['id'],start=True)))
        self.assertEqual(self.calls,[])
    def test_unfinished_claim_cannot_be_retried_after_restart(self):
        self.approve()
        with self.app.core() as core:
            scope=core.authority.issue_scope('local_owner')
            with core.transaction():ConversationService(core)._put(scope,'personal','conversation_analysis_started',dict(source=self.plan['source']))
        reopened=LocalApp(self.fx.path,sharing_profile=self.fx.profile)
        with self.assertRaisesRegex(ContractError,'unfinished'):self.start(reopened)
        self.assertEqual(self.calls,[]);self.assertEqual(reopened.state()['model_activations']['items'],[])
    def test_manual_pause_or_revoke_is_not_undone_by_repeated_start(self):
        self.approve()
        with patch.object(ConversationQueue,'process',return_value=dict(outcomes=[],attempted=0,status='Waiting for grant')):self.start()
        a=self.app.state()['model_activations']['items'][0]
        self.app.command(dict(action='change_model_activation',activation_id=a['id'],base_revision=a['revision'],configuration_sha256=a['configuration_sha256'],state='Paused',reason='Human pauses before external dispatch'))
        with self.assertRaises(ContractError):self.start()
        self.assertEqual(self.calls,[])
        a=self.app.state()['model_activations']['items'][0]
        self.app.command(dict(action='change_model_activation',activation_id=a['id'],base_revision=a['revision'],configuration_sha256=a['configuration_sha256'],state='Revoked',reason='Human revokes before external dispatch'))
        with self.assertRaises(ContractError):self.start()
        self.assertEqual(self.calls,[])
    def test_activation_failure_rolls_back_setup_without_provider_call(self):
        self.approve()
        with patch.object(ModelActivationService,'_transition',side_effect=ContractError('storage_failure','Synthetic transition failure')):
            with self.assertRaises(ContractError):self.start()
        self.assertEqual(self.calls,[]);self.assertEqual(self.app.state()['model_activations']['items'],[])
    def test_failed_model_response_is_preserved_not_retried(self):
        def send(payload):self.calls.append(payload);return dict(status='completed',usage=dict(total_tokens=10),output=[])
        self.approve();app=LocalApp(self.fx.path,sharing_profile=replace(self.fx.profile,send=send))
        self.assertEqual(self.start(app)['status'],'Analysis failed');self.assertEqual(len(self.calls),1)
        result=self.start(app);self.assertEqual((result['attempted'],result['status']),(0,'Analysis failed'));self.assertEqual(len(self.calls),1)
    def test_concurrent_second_start_cannot_dispatch_twice(self):
        entered=threading.Event();release=threading.Event();results=[];original=self.fx.profile.send
        def send(payload):entered.set();self.assertTrue(release.wait(5));return original(payload)
        self.approve();app=LocalApp(self.fx.path,sharing_profile=replace(self.fx.profile,send=send))
        thread=threading.Thread(target=lambda:results.append(self.start(app)));thread.start()
        try:
            self.assertTrue(entered.wait(3))
            with self.assertRaises(ContractError):self.start(app)
        finally:release.set();thread.join(5)
        self.assertFalse(thread.is_alive());self.assertEqual(results[0]['status'],'Ready for review');self.assertEqual(len(self.calls),1)
    def test_same_task_in_next_source_is_reviewed_without_duplicate_or_automatic_apply(self):
        original=self.fx.profile.send
        def send(payload):
            request=json.loads(payload['input']);tasks=request['context']['tasks']
            if not tasks:return original(payload)
            self.calls.append(payload);source=request['source']
            output=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=request['context_sha256'],coverage='partial',candidates=[],status_changes=[dict(task_id=tasks[0]['id'],stage='In Progress',quote=source['text'])],answer_proposals=[],relation_proposals=[],question_proposals=[],clarification_proposals=[])
            return dict(status='completed',usage=dict(total_tokens=100),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])
        self.app=LocalApp(self.fx.path,sharing_profile=replace(self.fx.profile,send=send));self.fx.app=self.app
        self.approve();self.start();self.fx.accept_scope('approved');task=self.app.state()['tasks'][0]['id']
        second=self.app.command(dict(action='import_conversation',text='I started the restore check.'))['source']
        prepared=self.app.command(dict(action='prepare_source_sharing',source_id=second['id'],model='fixture-model',max_output_tokens=1000,reserved_tokens=11000,expires_at=int(time.time())+300,reason='Explicit second synthetic source'))
        self.app.command(dict(action='approve_source_sharing',plan_id=prepared['plan']['id'],consent=True));self.start(plan=prepared['plan'])
        state=self.app.state();self.assertEqual(len(state['tasks']),1);self.assertEqual(state['tasks'][0]['lane'],'To Do')
        item=next(i for i in state['conversation_review']['imports'] if i['source']['id']==second['id']);proposal=item['status_changes'][0];self.assertEqual(proposal['task_id'],task)
        self.app.command(dict(action='review_dialogue_status',source_id=second['id'],proposal_id=proposal['id'],decision='accept',key='human_start_review',reason='Separate scripted human review',scope_reviewed=True))
        self.assertEqual(self.app.state()['tasks'][0]['lane'],'In Progress');self.assertEqual(len(self.calls),2)

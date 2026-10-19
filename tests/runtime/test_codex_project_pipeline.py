"""Selected real capture/queue code with fake provider; never semantic model proof."""
import json,time,unittest
import test_codex_app_server as fx
from packages.capture.codex.project_pipeline import CodexProjectPipeline
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.processing_queue import ConversationQueue
from packages.capture.granted_extractors import GrantedResponsesFactory
from packages.domain.source_event import ContractError
class ProjectPipelineTests(unittest.TestCase):
    def setUp(self):
        self.f=fx.AppServerCaptureTests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.core=self.f.core;self.owner=self.f.owner;self.pipe=CodexProjectPipeline(self.core);self.calls=[]
    def tick(self,**kw):return self.pipe.tick(self.owner,'p',capture_id='app_capture',client=fx.Client(),**kw)
    def grant(self,source,key):
        p=DialogueReviewService(self.core).prepare(self.owner,'p',source_id=source['id'])
        return ConversationService(self.core).authorize_analysis(self.owner,'p',source_id=source['id'],key=key,root_run='pipeline',reserved_tokens=12000,provider='OpenAI Responses configured transport',model='fixture',max_output_tokens=2000,expires_at=int(time.time())+300,reason='Synthetic pipeline test grant only.',context_sha256=p['context_sha256'])
    def send(self,payload):
        self.calls.append(payload);request=json.loads(payload['input']);s=request['source'];out=dict(source_id=s['id'],source_sha256=s['sha256'],context_sha256=request['context_sha256'],coverage='partial',candidates=[],status_changes=[],answer_proposals=[],relation_proposals=[],question_proposals=[])
        return dict(status='completed',usage=dict(total_tokens=100),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(out))])])
    def test_capture_without_provider_or_grant_does_not_dispatch(self):
        r=self.tick();self.assertTrue(r['human_text_observed']);self.assertEqual(r['processing']['attempted'],0);self.assertEqual(len(r['capture']['source_ids']),2);self.assertEqual(self.calls,[])
    def test_selected_capture_queue_does_not_process_other_source_even_with_valid_grant(self):
        s=ConversationService(self.core);other=s.ingest(self.owner,'p',text='An unrelated project message.');self.tick();selected=s._rows('p','conversation_imported')[1];self.core.create_budget(self.owner,'p','pipeline',24000)
        factory=GrantedResponsesFactory([(self.grant(other,'unrelated'),self.send),(self.grant(selected,'selected'),self.send)])
        r=self.tick(extractor_factory=factory,source_limit=2);self.assertEqual(r['processing']['attempted'],1);self.assertEqual(len(self.calls),1);self.assertEqual(json.loads(self.calls[0]['input'])['source']['id'],selected['id']);self.assertEqual(r['canonical_mutations'],0);self.assertEqual(len(r['review_ready']),1)
    def test_assistant_only_native_shape_warns_without_parsing_function_output(self):
        value=fx.page();value['data'][0]['items']=[dict(type='functionCallOutput',id='bridge',output='PRIVATE INPUT NOT A USER MESSAGE'),dict(type='agentMessage',id='assistant',text='I started the task.')]
        r=self.pipe.tick(self.owner,'p',capture_id='app_capture',client=fx.Client(value));self.assertFalse(r['human_text_observed']);self.assertIn('human_text_not_observed_do_not_claim_full_dialogue',r['warnings']);self.assertNotIn('PRIVATE INPUT',json.dumps(ConversationService(self.core).view(self.owner,'p')))
    def test_revoked_capture_stops_before_queue_transport(self):
        self.f.adapter.disconnect(self.owner,'p',capture_id='app_capture')
        with self.assertRaises(ContractError):self.tick(extractor_factory=lambda *a:self.fail('No transport after revoke'))
    def test_invalid_source_filter_and_pass_limit_fail_before_dispatch(self):
        for ids in ('all',['same','same'],[None]):
            with self.assertRaises(ContractError):ConversationQueue(self.core).process(self.owner,'p',source_ids=ids)
        with self.assertRaises(ContractError):self.tick(source_limit=11)
    def test_empty_selection_never_dispatches_other_pending_project_sources(self):
        self.assertEqual(ConversationQueue(self.core).process(self.owner,'p',source_ids=[],extractor_factory=lambda *a:self.fail('No selected source'))['attempted'],0)

class CompletionGuidanceTests(unittest.TestCase):
    def setUp(self):
        import test_dialogue_review
        self.f=test_dialogue_review.DialogueReviewTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
    def test_done_claim_suggests_review_handoff_but_does_not_apply_done(self):
        f=self.f;task=f.fx.task;f.fx.s.transition(f.owner,'p',task=task,task_version=1,base_revision=0,stage='In Progress',reason='Synthetic start',key='start')
        request=f.prepare('I finished the existing task, tests not run.');p=f.load(f.output(request,stage='Done'))['status_changes'][0]
        proposal=f.sources.view(f.owner,'p')['imports'][0]['status_changes'][0];g=proposal['workflow_guidance'];self.assertEqual(g['reported_stage'],'Done');self.assertEqual(g['suggested_review_stage'],'In Review');self.assertFalse(g['verification_passed']);self.assertFalse(g['automatic_transition'])
        with self.assertRaises(ContractError):f.review(p,scope_reviewed=True)
        self.assertEqual(f.fx.s.view(f.owner,'p',task)['stage'],'In Progress')

class ProviderFailureReceiptTests(unittest.TestCase):
    def test_safe_error_code_survives_without_exception_text_and_no_retry(self):
        import test_granted_extractors as f
        from apps.local_ui.server import LocalApp
        fixture=f.GrantedExtractorTests();fixture.setUp();self.addCleanup(fixture.doCleanups);calls=[]
        def fail(payload):calls.append(1);raise ContractError('provider_connection_unknown','PRIVATE_CREDENTIAL_OR_RESPONSE')
        factory=GrantedResponsesFactory([(fixture.entries[0][0],fail)])
        app=LocalApp(fixture.path,extractor_factory=factory);result=app.command(dict(action='process_conversation_queue',limit=2));self.assertEqual(result['attempted'],1)
        item=app.state()['conversation_review']['imports'][0]['analysis'];self.assertEqual(item['failure_code'],'provider_connection_unknown');self.assertEqual(item['failure_stage'],'provider_call');self.assertNotIn('PRIVATE_CREDENTIAL',json.dumps(item));self.assertEqual(item['budget_status'],'unknown')
        app.command(dict(action='process_conversation_queue',limit=2));self.assertEqual(calls,[1])

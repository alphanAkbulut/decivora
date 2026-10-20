"""Two selected host protocol fixtures; no real chats, model or paid API.

Scripted proposals verify capture/context/approval plumbing, not semantics.
"""
import json,unittest
import test_dialogue_journeys as journey_fx
import test_codex_project_pipeline as pipeline_fx
import test_codex_checkpoint as checkpoint_fx
from packages.capture.codex.project_pipeline import CodexProjectPipeline
from packages.capture.codex.app_server import CodexAppServerCapture
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.conversations import ConversationService
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace


def page(text,number=1,role='human'):
    item=dict(id='i_'+str(number),type='userMessage',content=[dict(type='text',text=text)]) if role=='human' else dict(id='i_'+str(number),type='agentMessage',text=text)
    return dict(data=[dict(id='t_'+str(number),status='completed',items=[item])],nextCursor=None)


class MultiChatTests(unittest.TestCase):
    def setUp(self):
        self.fx=journey_fx.DialogueJourneyTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.core=self.fx.core;self.owner=self.fx.owner;self.adapter=self.fx.adapter;self.pipe=CodexProjectPipeline(self.core)
        self.adapter.connect(self.owner,'p',capture_id='chat_b',thread_id='thread_two',provider_version='fixture',consent=True)
    def test_two_threads_share_only_accepted_project_task_and_status(self):
        task=self.fx.create_from_dialogue()
        a=journey_fx.Client(page('Arayüz rengini sonra konuşalım.',2))
        b=journey_fx.Client(page('Yedek geri yükleme kontrolüne başladım.'))
        result=self.pipe.tick_selected(self.owner,'p',selections=[dict(capture_id='journey',client=a),dict(capture_id='chat_b',client=b)])
        self.assertEqual(result['processing']['attempted'],0);self.assertEqual(result['errors'],[])
        self.assertEqual(result['canonical_mutations'],0)
        sid=result['captures'][1]['receipt']['source_ids'][0]
        request=self.fx.prepare(sid);context=request['request']['context']
        self.assertEqual(context['tasks'][0]['id'],task)
        self.assertEqual(context['capture_context']['messages'],[])
        self.assertNotIn('Arayüz rengini sonra konuşalım.',json.dumps(context))
        result=self.fx.output(sid,request,statuses=[dict(task_id=task,stage='In Progress',quote='Yedek geri yükleme kontrolüne başladım.')])
        self.assertEqual(TaskWorkflowService(self.core).view(self.owner,'p',task)['stage'],'To Do')
        self.fx.review.review_status(self.owner,'p',source_id=sid,proposal_id=result['status_changes'][0]['id'],decision='accept',key='chat_b_start',reason='Scripted separate human scope review')
        sid_a=self.fx.message('Diğer sohbette başladığımız kontrolün durumu?')
        self.assertEqual(self.fx.prepare(sid_a)['request']['context']['tasks'][0]['stage'],'In Progress')
        self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)
        with Workspace(self.fx.f.path,'w') as reopened:
            self.assertEqual(TaskWorkflowService(reopened).view(reopened.authority.issue_scope('owner'),'p',task)['stage'],'In Progress')
    def test_delayed_answer_in_second_thread_uses_shared_question_not_first_transcript(self):
        from packages.domain.questions import QuestionService
        qs=QuestionService(self.core)
        qs.present(self.owner,'p',question='Q_STORE',base_revision=0,text='Depolama?',options=[dict(id='files',label='Dosya'),dict(id='sqlite',label='SQLite')],reason='Scripted first-chat review')
        receipt=self.adapter.collect(self.owner,'p',capture_id='chat_b',client=journey_fx.Client(page('Önceki Q_STORE için SQLite ile devam.')))
        sid=receipt['source_ids'][0];prepared=self.fx.prepare(sid);source=self.fx.sources._source('p',sid)
        self.assertEqual(prepared['request']['context']['questions'][0]['id'],'Q_STORE')
        output=dict(source_id=sid,source_sha256=source['sha256'],context_sha256=prepared['context_sha256'],coverage='partial',candidates=[],status_changes=[],answer_proposals=[dict(question_id='Q_STORE',question_revision=1,option_id='sqlite',quote=source['text'])])
        analysis=self.fx.review.import_response(self.owner,'p',source_id=sid,response_text=json.dumps(output))
        self.assertEqual(qs.view(self.owner,'p')['questions'][0]['status'],'Open')
        self.fx.review.review_answer(self.owner,'p',source_id=sid,proposal_id=analysis['answer_proposals'][0]['id'],decision='accept',key='second_chat_answer',reason='Scripted source-bound review')
        self.assertEqual(qs.view(self.owner,'p')['questions'][0]['selection'],'sqlite')
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
    def test_cross_chat_change_invalidates_old_proposal_before_apply(self):
        task=self.fx.create_from_dialogue()
        receipt=self.adapter.collect(self.owner,'p',capture_id='chat_b',client=journey_fx.Client(page('Yedek geri yükleme kontrolüne başladım.')))
        sid=receipt['source_ids'][0];prepared=self.fx.prepare(sid)
        result=self.fx.output(sid,prepared,statuses=[dict(task_id=task,stage='In Progress',quote='Yedek geri yükleme kontrolüne başladım.')])
        TaskWorkflowService(self.core).transition(self.owner,'p',task=task,task_version=1,base_revision=0,stage='In Progress',reason='Separate first-chat human review',key='first_chat_start')
        with self.assertRaises(ContractError):self.fx.review.review_status(self.owner,'p',source_id=sid,proposal_id=result['status_changes'][0]['id'],decision='accept',key='stale_chat_b',reason='Old snapshot must not apply')

    def test_no_selected_binding_permission_reads_no_host(self):
        a=journey_fx.Client(page('A'));b=journey_fx.Client(page('B'));a.calls=[];b.calls=[]
        def read(client):
            def f(*args,**kw):client.calls.append(1);return client.page
            return f
        a.read_turns=read(a);b.read_turns=read(b)
        self.adapter.disconnect(self.owner,'p',capture_id='chat_b')
        with self.assertRaises(ContractError):self.pipe.tick_selected(self.owner,'p',selections=[dict(capture_id='journey',client=a),dict(capture_id='chat_b',client=b)])
        self.assertEqual(a.calls+b.calls,[])
    def test_one_host_failure_does_not_discard_other_host_sources(self):
        class Broken:
            def read_turns(self,*args,**kw):raise ContractError('codex_read_timeout','PRIVATE_BODY')
        result=self.pipe.tick_selected(self.owner,'p',selections=[dict(capture_id='journey',client=Broken()),dict(capture_id='chat_b',client=journey_fx.Client(page('B için yedek kontrolü ekleyelim.')))])
        self.assertEqual(result['errors'],[dict(capture_id='journey',code='codex_read_timeout')])
        self.assertEqual(result['captures'][1]['status'],'captured');self.assertEqual(result['selected_source_count'],1)
        self.assertNotIn('PRIVATE_BODY',json.dumps(result))
    def test_duplicate_native_thread_selection_is_rejected(self):
        self.adapter.connect(self.owner,'p',capture_id='alias',thread_id='thread_one',provider_version='fixture',consent=True)
        with self.assertRaises(ContractError):self.pipe.tick_selected(self.owner,'p',selections=[dict(capture_id='journey',client=journey_fx.Client(page('A'))),dict(capture_id='alias',client=journey_fx.Client(page('B')))])
    def test_unaccepted_other_chat_proposal_is_not_canonical_memory(self):
        sid=self.fx.message('Atlas için bir kontrol ekleyelim.')
        self.fx.output(sid,self.fx.prepare(sid),candidates=[dict(type='Task',title='Kontrol',quote='bir kontrol ekleyelim.',intent='planned')])
        result=self.adapter.collect(self.owner,'p',capture_id='chat_b',client=journey_fx.Client(page('O kontrole başladım.')))
        context=self.fx.prepare(result['source_ids'][0])['request']['context']
        self.assertEqual(context['tasks'],[]);self.assertEqual(context['capture_context']['messages'],[])
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
    def test_shared_source_cap_does_not_reset_for_each_thread(self):
        f=pipeline_fx.ProjectPipelineTests();f.setUp();self.addCleanup(f.doCleanups)
        f.pipe.capture.connect(f.owner,'p',capture_id='other',thread_id='thread_2',provider_version='fixture',consent=True)
        from test_codex_app_server import Client
        selections=[dict(capture_id='app_capture',client=Client()),dict(capture_id='other',client=Client())]
        f.pipe.tick_selected(f.owner,'p',selections=selections)
        sources=ConversationService(f.core)._rows('p','conversation_imported');f.core.create_budget(f.owner,'p','pipeline',48000)
        from packages.capture.granted_extractors import GrantedResponsesFactory
        factory=GrantedResponsesFactory([(f.grant(s,'g_'+str(i)),f.send) for i,s in enumerate(sources)])
        result=f.pipe.tick_selected(f.owner,'p',selections=selections,extractor_factory=factory,source_limit=1)
        self.assertEqual(result['processing']['attempted'],1);self.assertEqual(len(f.calls),1)


class RebindingContextTests(unittest.TestCase):
    def setUp(self):
        self.fx=checkpoint_fx.CheckpointTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.core=self.fx.core;self.owner=self.fx.owner;self.adapter=self.fx.adapter
    def test_rebinding_same_native_origin_preserves_prior_text_without_duplicates(self):
        client=checkpoint_fx.PagedClient(count=2);first=self.fx.run_capture(client)
        self.adapter.disconnect(self.owner,'p',capture_id='capture_1')
        self.adapter.connect(self.owner,'p',capture_id='reconnected',thread_id='thread_1',provider_version='fixture-1',consent=True)
        class Next(checkpoint_fx.PagedClient):
            def read_item_page(self,thread_id,turn_id,*,cursor):
                result=super().read_item_page(thread_id,turn_id,cursor=cursor)
                for item in result['items']:item['id']='next_'+item['id']
                return result
        newer=Next(count=2);newer.turns=[dict(id='turn_2',status='completed')]
        receipt=self.fx.run_capture(newer,capture_id='reconnected')
        context=DialogueReviewService(self.core).prepare(self.owner,'p',source_id=receipt['source_ids'][0])['request']['context']
        self.assertEqual([x['source_id'] for x in context['capture_context']['messages']],first['source_ids'])
        self.assertEqual(len(ConversationService(self.core)._rows('p','conversation_imported')),4)
    def test_other_profile_and_other_thread_are_not_raw_context(self):
        self.fx.run_capture(checkpoint_fx.PagedClient(count=2))
        self.adapter.connect(self.owner,'p',capture_id='different_profile',thread_id='thread_1',provider_version='fixture-1',consent=True)
        other=checkpoint_fx.PagedClient(count=2);other.profile_ref='other_profile'
        receipt=self.fx.run_capture(other,capture_id='different_profile')
        context=DialogueReviewService(self.core).prepare(self.owner,'p',source_id=receipt['source_ids'][0])['request']['context']
        self.assertEqual(context['capture_context']['messages'],[])

class SelectedCaptureCLITests(unittest.TestCase):
    def test_two_explicit_threads_wire_read_and_no_model(self):
        from contextlib import redirect_stdout
        import io
        import test_codex_app_server as f
        from scripts.capture_codex_threads import main
        fx=f.AppServerCaptureTests();fx.setUp();self.addCleanup(fx.doCleanups)
        executable,log=fx.fake_binary()
        args=['--db',str(fx.path),'--workspace','w','--principal','owner','--project','p','--provider-version','fixture','--codex-executable',str(executable),'--selection','cli_a=thread_a','--selection','cli_b=thread_b','--consent']
        with redirect_stdout(io.StringIO()) as out:self.assertEqual(main(args),0)
        result=json.loads(out.getvalue());self.assertEqual(result['model_calls'],0)
        self.assertEqual(result['result']['selected_source_count'],4)
        self.assertTrue(all(c['human_text_observed'] for c in result['result']['captures']))
        calls=[json.loads(line)['request'] for line in log.read_text().splitlines()]
        self.assertTrue(all(c.get('method') in ('initialize','initialized','thread/turns/list','thread/items/list') for c in calls))
        self.assertEqual({c['params']['threadId'] for c in calls if c['method']=='thread/turns/list'},{'thread_a','thread_b'})

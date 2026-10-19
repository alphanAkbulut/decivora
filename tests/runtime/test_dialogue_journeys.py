"""Multi-turn production capture/context/review code, scripted outputs only.

These tests prove plumbing and guards, never model understanding or accuracy.
"""
import json, unittest
import test_questions as fx
from packages.capture.codex.app_server import CodexAppServerCapture
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.dialogue_trace import DialogueTraceService
from packages.capture.conversations import ConversationService
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class Client:
    def __init__(self, page): self.page=page
    def read_turns(self, thread_id, *, limit): return self.page

class DialogueJourneyTests(unittest.TestCase):
    def setUp(self):
        self.f=fx.QuestionTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.core=self.f.core;self.owner=self.f.owner;self.sources=ConversationService(self.core)
        self.adapter=CodexAppServerCapture(self.core);self.review=DialogueReviewService(self.core)
        self.adapter.connect(self.owner,'p',capture_id='journey',thread_id='thread_one',provider_version='fixture',consent=True)
        self.ids=[]
    def message(self, text, role='human'):
        n=len(self.ids);item=dict(id='item_'+str(n),type='userMessage',content=[dict(type='text',text=text)]) if role=='human' else dict(id='item_'+str(n),type='agentMessage',text=text)
        page=dict(data=[dict(id='turn_'+str(n),status='completed',items=[item])],nextCursor=None)
        result=self.adapter.collect(self.owner,'p',capture_id='journey',client=Client(page))
        self.ids.append(result['source_ids'][0]);return self.ids[-1]
    def prepare(self, source):return self.review.prepare(self.owner,'p',source_id=source)
    def output(self, source, prepared, *, candidates=None, statuses=None):
        stored=self.sources._source('p',source)
        out=dict(source_id=source,source_sha256=stored['sha256'],context_sha256=prepared['context_sha256'],coverage='partial',candidates=candidates or [],status_changes=statuses or [],answer_proposals=[],relation_proposals=[],question_proposals=[])
        return self.review.import_response(self.owner,'p',source_id=source,response_text=json.dumps(out))
    def create_from_dialogue(self):
        sid=self.message('Atlas için yedek geri yükleme kontrolü ekleyelim; henüz başlamadım.')
        prepared=self.prepare(sid);result=self.output(sid,prepared,candidates=[dict(type='Task',title='Yedek geri yükleme kontrolü',quote='yedek geri yükleme kontrolü ekleyelim; henüz başlamadım.',intent='planned')])
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
        applied=self.sources.accept(self.owner,'p',source_id=sid,key='create_backup',selected=[result['candidates'][0]['id']],base_revision=prepared['request']['context']['knowledge_revision'])
        task=next(iter(applied['temp_ids'].values()))
        # Separate scripted operator scope approval, never inferred from chat.
        criterion=lambda cid:dict(id=cid,statement='Restore check independently reviewed',method='human_review',required=True,applicable=True,applicability_reason='')
        plan=self.core.plan(self.owner,'p','acceptance_scope',[dict(op='acceptance_contract',task=task,task_version=1,base_contract=0,criteria=[criterion('AC1')],dod=[criterion('DOD1')],reason='Scripted operator approves test scope',acknowledged_changes=[])])
        self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        return task
    def test_topic_switch_task_start_and_unverified_finish_have_one_lineage(self):
        task=self.create_from_dialogue()
        self.message('Bu arada arayüzün rengini sonra konuşalım.')
        self.message('Renk kararını erteledik.', 'assistant')
        started=self.message('Yedek geri yükleme kontrolüne başladım.', 'assistant')
        prepared=self.prepare(started);context=prepared['request']['context']
        self.assertEqual(context['tasks'][0]['id'],task)
        self.assertEqual(len(context['capture_context']['messages']),3)
        result=self.output(started,prepared,statuses=[dict(task_id=task,stage='In Progress',quote='Yedek geri yükleme kontrolüne başladım.')])
        self.assertEqual(TaskWorkflowService(self.core).view(self.owner,'p',task)['stage'],'To Do')
        self.review.review_status(self.owner,'p',source_id=started,proposal_id=result['status_changes'][0]['id'],decision='accept',key='start_review',reason='Scripted test operator review')
        self.message('Son durumu nedir?')
        finished=self.message('Yedek geri yükleme kontrolünü bitirdim; testleri çalıştırmadım.', 'assistant')
        result=self.output(finished,self.prepare(finished),statuses=[dict(task_id=task,stage='Done',quote='Yedek geri yükleme kontrolünü bitirdim; testleri çalıştırmadım.')])
        with self.assertRaises(ContractError):
            self.review.review_status(self.owner,'p',source_id=finished,proposal_id=result['status_changes'][0]['id'],decision='accept',key='false_done',reason='Scripted claim only',scope_reviewed=True)
        trace=DialogueTraceService(self.core).view(self.owner,'p',source_ids=self.ids)
        self.assertEqual(len(trace['entries']),6)
        self.assertEqual(trace['entries'][0]['record_links'][0]['record_id'],task)
        self.assertEqual(trace['entries'][3]['status_proposals'][0]['review_state'],'Applied')
        last=trace['entries'][-1]['status_proposals'][0]
        self.assertEqual((last['task_id'],last['reported_stage'],last['current_stage']),(task,'Done','In Progress'))
        self.assertFalse(last['verification_passed']);self.assertEqual(trace['model_calls'],0)
        with Workspace(self.f.path,'w') as reopened:
            saved=DialogueTraceService(reopened).view(reopened.authority.issue_scope('owner'),'p',source_ids=self.ids)
            self.assertEqual(saved,trace)
    def test_long_gap_omits_old_text_but_keeps_accepted_task(self):
        task=self.create_from_dialogue()
        for i in range(8):self.message('Başka konu '+str(i)+': renk ve yazı tipi sonra değerlendirilecek.')
        current=self.message('Önceki kontrol için devam ediyorum.')
        context=self.prepare(current)['request']['context'];history=context['capture_context']
        self.assertEqual(len(history['messages']),6);self.assertTrue(history['older_messages_omitted'])
        self.assertNotIn(self.ids[0],[m['source_id'] for m in history['messages']])
        self.assertEqual(context['tasks'][0]['id'],task)
        self.assertLessEqual(sum(len(m['text'].encode()) for m in history['messages']),6000)
    def test_context_window_enforces_byte_bound_with_unicode(self):
        for i in range(3):self.message(str(i)+' '+('şğüöı'*900))
        source=self.message('Devam edelim.')
        history=self.prepare(source)['request']['context']['capture_context']
        self.assertLessEqual(sum(len(m['text'].encode()) for m in history['messages']),6000)
        self.assertTrue(any(m['truncated'] for m in history['messages']))
    def test_profile_and_thread_context_do_not_mix(self):
        common=dict(source_surface='codex_app_server',id='journey',thread_id='thread_one',observed_actor='human')
        self.sources._ingest(self.owner,'p',text='Other installation context.',capture=dict(common,turn_id='foreign',item_id='foreign',profile_ref='a'*64))
        source=self.message('Only this selected installation.')
        self.assertNotIn('Other installation context.',json.dumps(self.prepare(source)))
    def test_trace_is_masked_scoped_bounded_and_read_only(self):
        source=self.message('password=example-sensitive-password')
        before=self.core.db.execute('SELECT count(*) FROM audit').fetchone()[0]
        trace=DialogueTraceService(self.core).view(self.owner,'p',source_ids=[source])
        self.assertNotIn('example-sensitive-password',json.dumps(trace))
        self.assertEqual(before,self.core.db.execute('SELECT count(*) FROM audit').fetchone()[0])
        for ids in ([],[source,source],[source]*26):
            with self.assertRaises(ContractError):DialogueTraceService(self.core).view(self.owner,'p',source_ids=ids)
        with self.assertRaises(ContractError):DialogueTraceService(self.core).view(self.owner,'other',source_ids=[source])

if __name__=='__main__':unittest.main()

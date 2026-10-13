import unittest,json
import test_questions
from packages.capture.conversations import ConversationService,anchored
from packages.capture.responses_extractor import ResponsesExtractor,request_payload
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace
from pathlib import Path

TEXT='We should add a backup test. We chose SQLite. Please ask which output language to use.'
class Extractor:
    authorized=True;provider='fixture; no real model'
    def __init__(self):self.calls=0
    def __call__(self,source):
        self.calls+=1
        return dict(source_id=source['id'],source_sha256=source['sha256'],coverage='complete',candidates=[dict(type='Task',title='Backup test',quote='We should add a backup test.',intent='planned'),dict(type='Decision',title='Storage choice',quote='We chose SQLite.',intent='reported'),dict(type='PendingDecision',title='Output language',quote='Please ask which output language to use.',intent='proposed')])
class ConversationTests(unittest.TestCase):
    setUp=test_questions.QuestionTests.setUp
    def source(self,text=TEXT):self.service=ConversationService(self.core);return self.service.ingest(self.owner,'p',text=text)
    def test_real_manual_text_is_not_relabelled_synthetic_and_no_model_default(self):
        source=self.source();self.assertEqual(source['source_kind'],'manual_paste');result=self.service.analyze(self.owner,'p',source['id']);self.assertEqual(result['status'],'Waiting for model');self.assertEqual(self.core.records(self.owner,'p')['records'],[])
    def test_import_dedup_restart_and_backup(self):
        source=self.source();self.assertEqual(source,self.source())
        with Workspace(self.path,'w') as c:self.assertEqual(ConversationService(c).view(c.authority.issue_scope('owner'),'p')['imports'][0]['source']['sha256'],source['sha256'])
        b=Path(self.temp.name)/'backup.sqlite';m=self.core.backup(self.owner,b)
        with Workspace.restore(b,Path(self.temp.name)/'restore.sqlite',m) as c:self.assertEqual(ConversationService(c).view(c.authority.issue_scope('owner'),'p')['imports'][0]['source']['text'],TEXT)
    def test_provider_fixture_to_review_to_explicit_task_accept(self):
        source=self.source();model=Extractor();result=self.service.analyze(self.owner,'p',source['id'],model);self.assertEqual(len(result['candidates']),3);self.assertEqual(self.core.records(self.owner,'p')['records'],[])
        view=self.service.view(self.owner,'p');chosen=view['imports'][0]['candidates'][0]['id'];r=self.service.accept(self.owner,'p',source_id=source['id'],key='accept',selected=[chosen],base_revision=view['knowledge_revision']);self.assertEqual(len(r['event_sequences']),1);self.assertEqual(self.core.records(self.owner,'p')['records'][0]['body']['type'],'Task')
        self.assertEqual(r,self.service.accept(self.owner,'p',source_id=source['id'],key='accept',selected=[chosen],base_revision=view['knowledge_revision']));self.service.analyze(self.owner,'p',source['id'],model);self.assertEqual(model.calls,1)
    def test_no_grant_no_dispatch(self):
        source=self.source();model=Extractor();model.authorized=False
        with self.assertRaises(ContractError):self.service.analyze(self.owner,'p',source['id'],model)
        self.assertEqual(model.calls,0)
    def test_fabricated_quote_rejects_whole_batch(self):
        source=self.source();output=Extractor()(source);output['candidates'][1]['quote']='invented'
        with self.assertRaises(ContractError):anchored(source,output)
    def test_ambiguous_quote_rejected_and_positions_computed_in_code(self):
        source=self.source(TEXT+' We chose SQLite.');output=Extractor()(source)
        with self.assertRaises(ContractError):anchored(source,output)
        source=self.source();output=anchored(source,Extractor()(source));c=output['candidates'][1];self.assertEqual(source['text'][c['start']:c['end']],c['quote'])
    def test_failed_provider_never_retries(self):
        source=self.source();model=Extractor()
        def bad(source):raise RuntimeError('Fixture failure')
        model.__class__=type('Bad',(Extractor,),{'__call__':bad});self.assertEqual(self.service.analyze(self.owner,'p',source['id'],model)['status'],'Analysis failed');self.assertEqual(self.service.analyze(self.owner,'p',source['id'],model)['status'],'Analysis failed')
    def test_stale_comparison_and_rejected_intent_are_not_applied(self):
        source=self.source();result=self.service.analyze(self.owner,'p',source['id'],Extractor());cid=result['candidates'][0]['id']
        with self.assertRaises(ContractError):self.service.accept(self.owner,'p',source_id=source['id'],key='accept',selected=[cid],base_revision=999)
    def test_accept_audit_failure_rolls_back_task(self):
        source=self.source();result=self.service.analyze(self.owner,'p',source['id'],Extractor());self.core.db.execute("CREATE TRIGGER fail_accept BEFORE INSERT ON audit WHEN NEW.action='conversation_candidates_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.service.accept(self.owner,'p',source_id=source['id'],key='accept',selected=[result['candidates'][0]['id']],base_revision=0)
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
    def test_oversize_and_foreign_project_denied(self):
        with self.assertRaises(ContractError):self.source('a'*12001)
        with self.assertRaises(ContractError):ConversationService(self.core).ingest(self.owner,'other',text=TEXT)
    def test_payload_and_response_parser_do_not_grant_or_execute_tools(self):
        source=self.source();payload=request_payload(source,model='chosen-model',max_output_tokens=512);self.assertFalse(payload['store']);self.assertEqual(payload['tools'],[])
        output=Extractor()(source);response=dict(status='completed',output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])]);adapter=ResponsesExtractor(lambda p:response,model='chosen-model',max_output_tokens=512,authorized=True);self.assertEqual(adapter(source),output)
        response['status']='incomplete'
        with self.assertRaises(ContractError):adapter(source)

    def test_exact_duplicate_attaches_source_without_second_task(self):
        source=self.source();result=self.service.analyze(self.owner,'p',source['id'],Extractor());self.service.accept(self.owner,'p',source_id=source['id'],key='first',selected=[result['candidates'][0]['id']],base_revision=0)
        other=self.source('Context changed. '+TEXT);result=self.service.analyze(self.owner,'p',other['id'],Extractor());view=self.service.view(self.owner,'p');self.assertEqual(view['imports'][1]['candidates'][0]['comparison']['recommendation'],'attach_source');r=self.service.accept(self.owner,'p',source_id=other['id'],key='second',selected=[result['candidates'][0]['id']],base_revision=1)
        self.assertEqual(r['event_sequences'],[]);self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)
    def test_invalid_model_output_preserved_with_unknown_usage(self):
        source=self.source()
        class Invalid(Extractor):
            def __call__(self,source):
                result=super().__call__(source);result['candidates'][0]['quote']='Invented source';return result
        result=self.service.analyze(self.owner,'p',source['id'],Invalid());self.assertEqual(result['status'],'Analysis failed');self.assertIn('Invented source',result['raw_output']);self.assertIsNone(result['usage'])
    def test_two_connections_do_not_dispatch_same_source_twice(self):
        import threading
        source=self.source();ready=threading.Event();finish=threading.Event();errors=[]
        class Slow(Extractor):
            def __call__(self,source):ready.set();finish.wait(timeout=5);return super().__call__(source)
        model=Slow()
        def run():
            try:
                with Workspace(self.path,'w') as c:ConversationService(c).analyze(c.authority.issue_scope('owner'),'p',source['id'],model)
            except Exception as e:errors.append(e)
        t=threading.Thread(target=run);t.start();self.assertTrue(ready.wait(timeout=5))
        with self.assertRaises(ContractError):self.service.analyze(self.owner,'p',source['id'],model)
        finish.set();t.join(timeout=5);self.assertEqual(errors,[]);self.assertEqual(model.calls,1)

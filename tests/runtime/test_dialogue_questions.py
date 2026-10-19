"""Dialogue question draft -> human presentation -> delayed answer; no real model."""
import json,unittest
from pathlib import Path
import test_questions as fixtures
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService,response_schema
from packages.capture.dialogue_questions import DialogueQuestionService,validate
from packages.domain.questions import QuestionService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class DialogueQuestionTests(unittest.TestCase):
    TEXT='Which storage should we use? Options: SQLite; PostgreSQL.'
    def setUp(self):
        fixtures.QuestionTests.setUp(self);self.sources=ConversationService(self.core);self.dialogue=DialogueReviewService(self.core);self.drafts=DialogueQuestionService(self.core)
        self.source=self.sources.ingest(self.owner,'p',text=self.TEXT)
        self.prepared=self.dialogue.prepare(self.owner,'p',source_id=self.source['id'])
    def output(self):
        return dict(source_id=self.source['id'],source_sha256=self.source['sha256'],context_sha256=self.prepared['context_sha256'],coverage='partial',candidates=[],status_changes=[],answer_proposals=[],relation_proposals=[],question_proposals=[dict(question_text='Which storage should we use?',options=['SQLite','PostgreSQL'],quote=self.TEXT)])
    def load(self,output=None):
        return self.dialogue.import_response(self.owner,'p',source_id=self.source['id'],response_text=json.dumps(self.output() if output is None else output))
    def review(self,proposal,decision='accept',key='review_question'):
        return self.drafts.review(self.owner,'p',source_id=self.source['id'],proposal_id=proposal['id'],decision=decision,key=key,reason='Human checked the question, choices and source.')

    def test_draft_is_not_a_presented_question_until_separate_human_review(self):
        analysis=self.load();draft=analysis['question_proposals'][0]
        self.assertEqual(self.s.view(self.owner,'p')['questions'],[])
        view=self.sources.view(self.owner,'p')['imports'][0]['question_proposals'][0];self.assertEqual(view['state'],'Pending')
        receipt=self.review(draft);self.assertEqual(receipt['state'],'Presented');self.assertFalse(receipt['canonical_apply'])
        q=self.s.view(self.owner,'p')['questions'][0];self.assertEqual(q['status'],'Open');self.assertIsNone(q['selection'])
        self.assertEqual(q['source_kind'],'dialogue_review');self.assertEqual(q['responder'],'owner');self.assertEqual(q['provenance']['source_sha256'],self.source['sha256'])
        self.assertEqual([o['id'] for o in q['options']],['option_1','option_2'])
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])

    def test_delayed_answer_uses_the_presented_question_revision_and_keeps_decision_separate(self):
        draft=self.load()['question_proposals'][0];self.review(draft)
        text='For '+draft['question_id']+', choose PostgreSQL.'
        source=self.sources.ingest(self.owner,'p',text=text);prepared=self.dialogue.prepare(self.owner,'p',source_id=source['id'])
        self.assertEqual(prepared['request']['context']['questions'][0]['id'],draft['question_id'])
        output=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=prepared['context_sha256'],coverage='partial',candidates=[],status_changes=[],relation_proposals=[],question_proposals=[],answer_proposals=[dict(question_id=draft['question_id'],question_revision=1,option_id='option_2',quote=text)])
        analysis=self.dialogue.import_response(self.owner,'p',source_id=source['id'],response_text=json.dumps(output))
        self.assertEqual(self.s.view(self.owner,'p')['questions'][0]['status'],'Open')
        receipt=self.dialogue.review_answer(self.owner,'p',source_id=source['id'],proposal_id=analysis['answer_proposals'][0]['id'],decision='accept',key='late_answer',reason='Human confirmed the exact late answer.')
        self.assertEqual(receipt['state'],'Recorded');q=self.s.view(self.owner,'p')['questions'][0]
        self.assertEqual(q['status'],'Answered');self.assertEqual(q['selection'],'option_2');self.assertEqual(self.core.records(self.owner,'p')['records'],[])

    def test_defer_reject_and_idempotent_final_review(self):
        draft=self.load()['question_proposals'][0]
        self.review(draft,'defer','later');self.assertEqual(self.s.view(self.owner,'p')['questions'],[])
        receipt=self.review(draft);self.assertEqual(self.review(draft),receipt)
        self.assertEqual(len(self.s.view(self.owner,'p')['questions']),1)
        with self.assertRaises(ContractError):self.review(draft,'reject','other')
        with self.assertRaises(ContractError):self.review(draft,'reject','review_question')

    def test_reject_never_presents_or_answers(self):
        draft=self.load()['question_proposals'][0];self.review(draft,'reject')
        self.assertEqual(self.s.view(self.owner,'p')['questions'],[])
        self.assertEqual(self.sources.view(self.owner,'p')['imports'][0]['question_proposals'][0]['state'],'Rejected')
        with self.assertRaises(ContractError):self.review(draft,'accept','new_key')

    def test_fabricated_choices_text_and_untrusted_authority_fields_are_rejected(self):
        for values in (dict(options=['SQLite','Redis']),dict(question_text='Should production be deleted?'),dict(responder='agent'),dict(options=['SQLite','sqlite '])):
            output=self.output();output['question_proposals'][0].update(values)
            with self.assertRaises(ContractError):self.load(output)
        self.assertEqual(self.s.view(self.owner,'p')['questions'],[])

    def test_ambiguous_duplicate_questions_or_source_quotes_are_not_guessed(self):
        output=self.output();output['question_proposals']*=2
        with self.assertRaises(ContractError):self.load(output)
        repeated=self.sources.ingest(self.owner,'p',text=self.TEXT+' '+self.TEXT)
        with self.assertRaises(ContractError):validate(repeated,self.output()['question_proposals'])
        with self.assertRaises(ContractError):validate(self.source,self.output()['question_proposals']*33)

    def test_current_duplicate_question_blocks_presentation_without_silent_merge(self):
        draft=self.load()['question_proposals'][0]
        self.s.present(self.owner,'p',question='manual_existing',base_revision=0,text=draft['question_text'],options=draft['options'])
        with self.assertRaises(ContractError) as error:self.review(draft)
        self.assertEqual(error.exception.code,'question_duplicate')
        view=self.sources.view(self.owner,'p')['imports'][0]['question_proposals'][0]
        self.assertEqual(view['existing_question_matches'],['manual_existing']);self.assertEqual(view['state'],'Pending')

    def test_question_and_source_review_receipt_rollback_together(self):
        draft=self.load()['question_proposals'][0]
        self.core.db.execute("CREATE TRIGGER fail_question_review BEFORE INSERT ON audit WHEN NEW.action='conversation_question_reviewed' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.review(draft)
        self.assertEqual(self.s.view(self.owner,'p')['questions'],[]);self.assertEqual(self.sources._rows('p',self.drafts.ACTION),[])

    def test_scope_and_agent_cannot_present_the_question(self):
        draft=self.load()['question_proposals'][0]
        with self.assertRaises(ContractError):self.drafts.review(self.owner,'foreign',source_id=self.source['id'],proposal_id=draft['id'],decision='accept',key='bad_project',reason='Fixture')
        a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision())
        with self.assertRaises(ContractError):self.drafts.review(a.issue_scope('agent'),'p',source_id=self.source['id'],proposal_id=draft['id'],decision='accept',key='bad_actor',reason='Fixture')
        self.assertEqual(self.s.view(a.issue_scope('owner'),'p')['questions'],[])

    def test_restart_backup_restore_preserves_question_provenance_and_pending_state(self):
        draft=self.load()['question_proposals'][0];self.review(draft)
        backup=Path(self.temp.name)/'question-backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restored.sqlite',manifest) as core:
            owner=core.authority.issue_scope('owner');question=QuestionService(core).view(owner,'p')['questions'][0]
            self.assertEqual(question['status'],'Open');self.assertEqual(question['provenance']['proposal'],draft['id'])
            self.assertEqual(ConversationService(core).view(owner,'p')['imports'][0]['question_proposals'][0]['state'],'Presented')

    def test_legacy_response_remains_accepted_without_question_fields(self):
        output=self.output();output.pop('question_proposals');self.assertEqual(self.load(output)['question_proposals'],[])
        self.assertIn('question_proposals',response_schema()['required'])

    def test_question_capacity_does_not_partially_create_a_review_receipt(self):
        draft=self.load()['question_proposals'][0]
        for i in range(100):self.s.present(self.owner,'p',question='existing_'+str(i),base_revision=0,text='Other question '+str(i),options=[dict(id='a',label='Yes'),dict(id='b',label='No')])
        with self.assertRaises(ContractError) as error:self.review(draft)
        self.assertEqual(error.exception.code,'question_limit');self.assertEqual(len(self.s.view(self.owner,'p')['questions']),100)
        self.assertEqual(self.sources._rows('p',self.drafts.ACTION),[])

    def test_http_review_requires_session_csrf_and_writes_question_atomically(self):
        import tempfile,threading,urllib.request,urllib.error
        from apps.local_ui.server import make_server
        with tempfile.TemporaryDirectory() as temp:
            server=make_server(Path(temp)/'http.sqlite')
            with server.app.core() as core:
                owner=core.authority.issue_scope('local_owner');service=ConversationService(core)
                source=service.ingest(owner,'personal',text=self.TEXT)
                prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
                output=self.output();output.update(source_id=source['id'],source_sha256=source['sha256'],context_sha256=prepared['context_sha256'])
                draft=DialogueReviewService(core).import_response(owner,'personal',source_id=source['id'],response_text=json.dumps(output))['question_proposals'][0]
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                headers={'Content-Type':'application/json','Origin':server.origin,'Cookie':'decivora_session='+server.app.cookie,'X-CSRF-Token':server.app.csrf}
                body=dict(action='review_dialogue_question',source_id=source['id'],proposal_id=draft['id'],decision='accept',key='http_question',reason='Synthetic human review')
                def call(body,headers):
                    request=urllib.request.Request(server.origin+'/api/command',data=json.dumps(body).encode(),headers=headers,method='POST')
                    try:
                        with urllib.request.urlopen(request) as response:return response.status,json.load(response)
                    except urllib.error.HTTPError as response:return response.code,json.load(response)
                self.assertEqual(call(body,{'Content-Type':'application/json','Origin':server.origin})[0],403)
                self.assertEqual(call(body,dict(headers,**{'X-CSRF-Token':''}))[0],403)
                self.assertEqual(server.app.state()['question_inbox']['questions'],[])
                status,result=call(body,headers);self.assertEqual(status,200);self.assertEqual(result['state'],'Presented')
                self.assertEqual(call(body,headers)[1],result)
                with server.app.core() as core:
                    owner=core.authority.issue_scope('local_owner')
                    self.assertEqual(len(QuestionService(core).view(owner,'personal')['questions']),1)
                    self.assertEqual(core.records(owner,'personal')['records'],[])
                self.assertTrue(any(r['action']=='review_dialogue_question' for r in server.app.operations_view()['runs']))
            finally:server.shutdown();server.server_close();thread.join(timeout=2)

    def test_configured_provider_response_schema_flows_to_question_draft_not_auto_presentation(self):
        import tempfile,time
        from apps.local_ui.server import LocalApp
        from packages.capture.granted_extractors import GrantedResponsesFactory
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'configured.sqlite';app=LocalApp(path);calls=[]
            with app.core() as core:
                owner=core.authority.issue_scope('local_owner');service=ConversationService(core)
                source=service.ingest(owner,'personal',text=self.TEXT)
                prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
                core.create_budget(owner,'personal','question_test',12000)
                grant=service.authorize_analysis(owner,'personal',source_id=source['id'],key='question_grant',root_run='question_test',reserved_tokens=12000,provider='OpenAI Responses configured transport',model='fixture',max_output_tokens=2000,expires_at=int(time.time())+3600,reason='Synthetic isolated provider test.',context_sha256=prepared['context_sha256'])
            def send(payload):
                calls.append(payload);request=json.loads(payload['input'])
                self.assertIn('question_proposals',payload['text']['format']['schema']['required'])
                output=self.output();output.update(source_id=source['id'],source_sha256=source['sha256'],context_sha256=request['context_sha256'])
                return dict(status='completed',usage=dict(total_tokens=100),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])
            app=LocalApp(path,extractor_factory=GrantedResponsesFactory([(grant,send)]))
            result=app.command(dict(action='process_conversation_queue',limit=1))
            self.assertEqual(result['attempted'],1);self.assertEqual(len(calls),1);self.assertEqual(result['outcomes'][0]['status'],'Ready for review',result)
            with app.core() as core:
                owner=core.authority.issue_scope('local_owner');draft=ConversationService(core).view(owner,'personal')['imports'][0]['question_proposals'][0]
                self.assertEqual(draft['state'],'Pending');self.assertEqual(QuestionService(core).view(owner,'personal')['questions'],[])
            app.command(dict(action='review_dialogue_question',source_id=source['id'],proposal_id=draft['id'],decision='accept',key='configured_review',reason='Human checked the synthetic draft.'))
            with app.core() as core:self.assertEqual(len(QuestionService(core).view(core.authority.issue_scope('local_owner'),'personal')['questions']),1)

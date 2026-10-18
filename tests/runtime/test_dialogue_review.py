"""Conversation-to-task/status integration; outputs are synthetic, not semantic proof."""
import json,unittest
from pathlib import Path
import test_task_workflow as fixtures
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService,response_schema
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class DialogueReviewTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixtures.WorkflowTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.core=self.fx.core;self.owner=self.fx.owner;self.service=DialogueReviewService(self.core);self.sources=ConversationService(self.core)
    def prepare(self,text='I started the existing task. Add a restore test.'):
        self.source=self.sources.ingest(self.owner,'p',text=text)
        return self.service.prepare(self.owner,'p',source_id=self.source['id'])
    def output(self,request,stage='In Progress',candidates=None,task=None):
        return dict(source_id=self.source['id'],source_sha256=self.source['sha256'],context_sha256=request['context_sha256'],coverage='complete',candidates=candidates or [],status_changes=[dict(task_id=task or self.fx.task,stage=stage,quote=self.source['text'].split(' Add')[0])])
    def load(self,output):return self.service.import_response(self.owner,'p',source_id=self.source['id'],response_text=json.dumps(output))
    def review(self,proposal,decision='accept',key='review',**kw):return self.service.review_status(self.owner,'p',source_id=self.source['id'],proposal_id=proposal['id'],decision=decision,key=key,reason='Human reviewed exact source and current task',**kw)
    def test_task_creation_and_status_claim_from_one_dialogue_are_separately_reviewed(self):
        request=self.prepare();output=self.output(request,candidates=[dict(type='Task',title='Restore test',quote='Add a restore test.',intent='planned')]);analysis=self.load(output)
        self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'To Do');self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)
        self.sources.accept(self.owner,'p',source_id=self.source['id'],key='new_task',selected=[analysis['candidates'][0]['id']],base_revision=request['request']['context']['knowledge_revision'])
        self.assertEqual(len(self.core.records(self.owner,'p')['records']),2)
        self.review(analysis['status_changes'][0]);self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'In Progress')
        record=self.core.records(self.owner,'p')['records'];new=next(r for r in record if r['id']!=self.fx.task);self.assertEqual(self.fx.s.view(self.owner,'p',new['id'])['stage'],'To Do')
    def test_import_and_apply_retries_are_one_effect(self):
        request=self.prepare();output=self.output(request);first=self.load(output);self.assertEqual(self.load(output),first)
        receipt=self.review(first['status_changes'][0]);self.assertEqual(self.review(first['status_changes'][0]),receipt)
        self.assertEqual(len(self.fx.s.view(self.owner,'p',self.fx.task)['history']),1)
        with self.assertRaises(ContractError):self.review(first['status_changes'][0],decision='reject')
    def test_done_claim_cannot_bypass_current_evidence_or_scope_review(self):
        self.fx.ready_for_verification();request=self.prepare('I finished the existing task.');output=self.output(request,stage='Done');proposal=self.load(output)['status_changes'][0]
        with self.assertRaises(ContractError):self.review(proposal,scope_reviewed=True)
        self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'Awaiting Verification')
        self.fx.evidence('AC1');self.fx.evidence('DOD1')
        with self.assertRaises(ContractError):self.review(proposal,scope_reviewed=True)
        fresh=self.service.prepare(self.owner,'p',source_id=self.source['id']);new=self.load(self.output(fresh,stage='Done'))['status_changes'][0]
        self.assertNotEqual(new['id'],proposal['id'])
        with self.assertRaises(ContractError):self.review(new,key='current_done')
        self.review(new,key='current_done',scope_reviewed=True);self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'Done')
        self.assertEqual(len(self.sources._rows('p','conversation_analysis_finished')),2)
    def test_stale_workflow_or_task_context_blocks_apply(self):
        request=self.prepare();analysis=self.load(self.output(request));self.fx.stage('Backlog')
        self.assertTrue(self.sources.view(self.owner,'p')['imports'][0]['status_changes'][0]['stale'])
        with self.assertRaises(ContractError):self.review(analysis['status_changes'][0])
        self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'Backlog')
    def test_context_change_between_request_and_import_is_rejected(self):
        request=self.prepare();self.fx.stage('Backlog')
        with self.assertRaises(ContractError):self.load(self.output(request))
        self.assertEqual(self.sources.view(self.owner,'p')['imports'][0]['status'],'Waiting for model')
    def test_multiple_independent_task_updates_in_one_response_can_both_apply(self):
        second=self.fx.create('Second task');self.fx.contract(second);request=self.prepare('I started the existing task. I started the second task.')
        output=self.output(request);output['status_changes'][0]['quote']='I started the existing task.';output['status_changes'].append(dict(task_id=second,stage='In Progress',quote='I started the second task.'))
        proposals=self.load(output)['status_changes'];self.review(proposals[0]);self.review(proposals[1],key='second_review')
        self.assertEqual(self.fx.s.view(self.owner,'p',second)['stage'],'In Progress')
    def test_ambiguous_two_claims_for_same_task_reject_whole_response(self):
        request=self.prepare();output=self.output(request);output['status_changes'].append(dict(output['status_changes'][0],stage='Done'))
        with self.assertRaises(ContractError):self.load(output)
        self.assertEqual(self.sources._rows('p','conversation_analysis_finished'),[])
    def test_false_source_quote_unknown_task_or_unsupported_stage_is_not_imported(self):
        request=self.prepare()
        for field,value in [('quote','Invented source'),('task_id','foreign_task'),('stage','Cancelled'),('stage','Blocked')]:
            output=self.output(request);output['status_changes'][0][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ContractError):self.load(output)
        self.assertEqual(self.sources._rows('p','conversation_analysis_finished'),[])
    def test_reject_and_defer_preserve_claim_without_workflow_mutation(self):
        request=self.prepare();proposal=self.load(self.output(request))['status_changes'][0]
        self.review(proposal,decision='defer');self.assertEqual(self.sources.view(self.owner,'p')['imports'][0]['status_changes'][0]['state'],'Deferred')
        self.review(proposal,decision='reject',key='reject');self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['history'],[])
        with self.assertRaises(ContractError):self.review(proposal,key='closed')
    def test_review_receipt_failure_rolls_back_stage(self):
        request=self.prepare();proposal=self.load(self.output(request))['status_changes'][0]
        self.core.db.execute("CREATE TRIGGER fail_dialogue_review BEFORE INSERT ON audit WHEN NEW.action='conversation_status_reviewed' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.review(proposal)
        self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['history'],[])
    def test_agent_and_foreign_project_cannot_import_or_apply(self):
        request=self.prepare();output=self.output(request);proposal=self.load(output)['status_changes'][0]
        a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision());agent=a.issue_scope('agent')
        with self.assertRaises(ContractError):self.service.import_response(agent,'p',source_id=self.source['id'],response_text=json.dumps(output))
        with self.assertRaises(ContractError):self.service.prepare(agent,'p',source_id=self.source['id'])
        self.owner=a.issue_scope('owner')
        with self.assertRaises(ContractError):self.review(proposal)
        with self.assertRaises(ContractError):self.service.prepare(self.owner,'foreign',source_id=self.source['id'])
    def test_restart_and_restore_preserve_proposals_and_review(self):
        request=self.prepare();proposal=self.load(self.output(request))['status_changes'][0];self.review(proposal)
        backup=Path(self.fx.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.fx.temp.name)/'restored.sqlite',manifest) as restored:
            owner=restored.authority.issue_scope('owner');item=ConversationService(restored).view(owner,'p')['imports'][0]
            self.assertEqual(item['status_changes'][0]['state'],'Applied');self.assertEqual(DialogueReviewService(restored).workflow.view(owner,'p',self.fx.task)['stage'],'In Progress')
    def test_invalid_json_duplicates_and_fabricated_context_are_rejected(self):
        request=self.prepare();output=self.output(request)
        texts=['{"a":1,"a":2}',json.dumps(dict(output,context_sha256='invented')),'```json\n'+json.dumps(output)+'\n```']
        for text in texts:
            with self.subTest(text=text[:30]),self.assertRaises(ContractError):self.service.import_response(self.owner,'p',source_id=self.source['id'],response_text=text)
    def test_schema_is_published_and_matches_response_contract(self):
        published=json.loads((Path(__file__).resolve().parents[2]/'manifests/dialogue-review-response.schema.json').read_text());published.pop('$schema');self.assertEqual(published,response_schema())
    def test_start_claim_does_not_bypass_missing_acceptance_or_blocker(self):
        from packages.domain.task_blockers import TaskBlockerService
        TaskBlockerService(self.core).set(self.owner,'p',task=self.fx.task,task_version=1,base_revision=0,blocked=True,reason='Unavailable input',next_action='Wait for input',gate='start',waiting_kind='input')
        request=self.prepare();proposal=self.load(self.output(request))['status_changes'][0]
        with self.assertRaises(ContractError):self.review(proposal)
        self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'To Do')

    def test_configured_provider_uses_same_context_schema_and_status_review(self):
        import time
        from packages.capture.responses_extractor import ResponsesExtractor
        request=self.prepare();output=self.output(request);calls=[]
        def send(payload):
            calls.append(payload)
            self.assertFalse(self.core.db.in_transaction)
            return dict(status='completed',usage={'total_tokens':50},output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])
        extractor=ResponsesExtractor(send,model='fixture-model',max_output_tokens=100,authorized=True,grant_id='dialogue_grant',dialogue_review=True)
        self.core.create_budget(self.owner,'p','dialogue_run',1000)
        self.sources.authorize_analysis(self.owner,'p',source_id=self.source['id'],key='dialogue_grant',root_run='dialogue_run',reserved_tokens=1000,provider=extractor.provider,model=extractor.model,max_output_tokens=100,expires_at=int(time.time())+3600,reason='Synthetic source and current task context; no actual provider',context_sha256=request['context_sha256'])
        schema=json.loads((Path(__file__).resolve().parents[2]/'manifests/conversation-dispatch-grant.schema.json').read_text())
        grant=self.sources._rows('p','conversation_dispatch_authorized')[-1];self.assertEqual(set(grant),set(schema['properties']));self.assertEqual(grant['context_sha256'],request['context_sha256'])
        result=self.sources.analyze(self.owner,'p',self.source['id'],extractor)
        self.assertEqual(result['status'],'Ready for review');self.assertEqual(result['budget_status'],'settled');self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]['text']['format']['schema'],response_schema())
        self.assertEqual(json.loads(calls[0]['input'])['context'],request['request']['context'])
        self.assertIsNone(extractor.dialogue_request) # shared extractor is not mutated
        self.review(result['status_changes'][0]);self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'In Progress')

    def test_source_only_dispatch_grant_cannot_share_task_context(self):
        import time
        from packages.capture.responses_extractor import ResponsesExtractor
        self.prepare();calls=[];extractor=ResponsesExtractor(lambda payload:calls.append(payload),model='fixture-model',max_output_tokens=100,authorized=True,grant_id='source_only',dialogue_review=True)
        self.core.create_budget(self.owner,'p','source_run',1000)
        self.sources.authorize_analysis(self.owner,'p',source_id=self.source['id'],key='source_only',root_run='source_run',reserved_tokens=1000,provider=extractor.provider,model=extractor.model,max_output_tokens=100,expires_at=int(time.time())+3600,reason='Only source text, no task context')
        with self.assertRaises(ContractError) as error:self.sources.analyze(self.owner,'p',self.source['id'],extractor)
        self.assertEqual(error.exception.code,'model_grant_required');self.assertEqual(calls,[])

    def test_primary_context_contains_decisions_questions_and_recorded_relations(self):
        from packages.domain.questions import QuestionService
        decision=self.fx.apply([dict(op='create',id='d',body=dict(type='Decision',title='Storage choice',description='SQLite chosen because local-first operation is required'))])['temp_ids']['d']
        self.fx.apply([dict(op='link',origin=self.fx.task,target=decision,kind='required_by')])
        QuestionService(self.core).present(self.owner,'p',question='Q_STORE',base_revision=0,text='Which storage should replace it?',options=[dict(id='a',label='Keep SQLite'),dict(id='b',label='Change storage')],task=self.fx.task)
        request=self.prepare();context=request['request']['context']
        self.assertEqual(context['format'],'decivora-dialogue-context-2')
        self.assertEqual(context['records'][0]['id'],decision)
        self.assertIn('local-first',context['records'][0]['description_excerpt'])
        self.assertEqual(context['questions'][0]['id'],'Q_STORE');self.assertEqual(context['questions'][0]['status'],'Open')
        self.assertTrue(any(r['origin']==self.fx.task and r['target']==decision and r['kind']=='required_by' and r['state']=='asserted' for r in context['relations']))
        self.assertFalse(context['coverage']['raw_other_conversations_included'])
        self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'To Do')

    def test_question_answer_after_preparation_invalidates_old_context_response(self):
        from packages.domain.questions import QuestionService
        q=QuestionService(self.core);q.present(self.owner,'p',question='Q_STORE',base_revision=0,text='Choose storage?',options=[dict(id='a',label='Keep'),dict(id='b',label='Change')])
        request=self.prepare();q.answer(self.owner,'p',request_id='late',question='Q_STORE',revision=1,option='b')
        with self.assertRaises(ContractError) as caught:self.load(self.output(request))
        self.assertEqual(caught.exception.code,'stale_context')
        fresh=self.service.prepare(self.owner,'p',source_id=self.source['id'])
        self.assertEqual(fresh['request']['context']['questions'][0]['selection'],'b')
        self.assertEqual(fresh['request']['context']['questions'][0]['status'],'Answered')
        self.assertEqual(self.sources._rows('p','question_decision_applied'),[])

    def test_context_marks_description_excerpt_instead_of_claiming_full_history(self):
        self.fx.apply([dict(op='create',id='r',body=dict(type='Requirement',title='Long requirement',description='x'*1500))])
        request=self.prepare();record=request['request']['context']['records'][0]
        self.assertEqual(len(record['description_excerpt']),1024);self.assertTrue(record['description_truncated'])
        self.assertFalse(request['request']['context']['coverage']['source_history_included'])

    def test_analyze_readback_returns_latest_external_analysis_revision(self):
        request=self.prepare();first=self.load(self.output(request))
        self.fx.stage('Backlog');fresh=self.service.prepare(self.owner,'p',source_id=self.source['id']);second=self.load(self.output(fresh,stage='To Do'))
        self.assertNotEqual(first['context_sha256'],second['context_sha256'])
        self.assertEqual(self.sources.analyze(self.owner,'p',self.source['id']),second)

"""Source-bound external model response import and reviewed workflow proposals.

No network, credentials, inference or authority is supplied by this module.
"""
import json
from packages.capture.conversations import ConversationService, anchored, output_schema
from packages.domain.source_event import ContractError
from packages.domain.project_binding import identifier
from packages.domain.task_workflow import TaskWorkflowService, STAGES
from packages.storage.project_store import canonical, digest


def response_schema():
    schema=output_schema()
    schema['properties'].update(context_sha256={'type':'string'},status_changes={
        'type':'array','maxItems':32,'items':{'type':'object','additionalProperties':False,
        'required':['task_id','stage','quote'],'properties':{'task_id':{'type':'string'},
        'stage':{'type':'string','enum':list(STAGES)},'quote':{'type':'string'}}}})
    schema['required']=list(schema['properties'])
    return schema


class DialogueReviewService:
    def __init__(self,core):
        self.core=core
        self.sources=ConversationService(core)
        self.workflow=TaskWorkflowService(core)

    def _task_digest(self,project,task,view):
        return digest(canonical(dict(workflow=view,context=self.workflow._context_component(project,task))))

    def _tasks(self,scope,project):
        rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 101',(self.core.workspace,project)).fetchall()
        if len(rows)>100:raise ContractError('comparison_limit','Narrow the project before preparing a complete dialogue review.')
        tasks=[]
        for rid,version,raw in rows:
            body=json.loads(raw)
            if body['type']!='Task':continue
            view=self.workflow.view(scope,project,rid)
            tasks.append(dict(id=rid,version=version,title=body['title'],description_excerpt=body['description'][:512],description_truncated=len(body['description'])>512,
                stage=view['stage'],workflow_revision=view['revision'],workflow_sha256=self._task_digest(project,rid,view),
                contract_version=view['verification']['contract_version'],verification_passed=view['verification']['passed'],
                start_blocked=view['assessment']['start_blocked'],finish_blocked=view['assessment']['finish_blocked']))
        return tasks

    def _context(self,scope,project):
        """One bounded, scoped memory snapshot for both import and provider paths."""
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        tasks=self._tasks(scope,project)
        rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 101',(self.core.workspace,project)).fetchall()
        records=[]
        for rid,version,raw in rows:
            body=json.loads(raw)
            if body['type']=='Task':continue
            records.append(dict(id=rid,version=version,type=body['type'],title=body['title'],description_excerpt=body['description'][:1024],description_truncated=len(body['description'])>1024))
        from packages.domain.questions import QuestionService
        questions=QuestionService(self.core).view(scope,project)['questions']
        if len(questions)>64:raise ContractError('context_limit','Question context exceeds the local complete-snapshot bound.')
        questions=[{k:q[k] for k in ('id','revision','text','options','task','status','selection','state_revision')} for q in questions]
        rows=self.core.db.execute('SELECT origin,target,kind,revision,state,valid_from,valid_to FROM edges WHERE workspace=? AND project=? ORDER BY origin,target,kind LIMIT 501',(self.core.workspace,project)).fetchall()
        if len(rows)>500:raise ContractError('context_limit','Relation context exceeds the local complete-snapshot bound.')
        relations=[dict(zip(('origin','target','kind','revision','state','valid_from','valid_to'),r)) for r in rows]
        return dict(format='decivora-dialogue-context-2',workspace=self.core.workspace,project=project,
            knowledge_revision=self.core.project(scope,project)['knowledge_revision'],tasks=tasks,records=records,
            questions=questions,relations=relations,coverage=dict(record_snapshot='complete_within_local_bounds',
                descriptions='explicit_excerpts',relation_scope='recorded_only',source_history_included=False,
                raw_other_conversations_included=False,automatic_question_answer_association=False))

    def prepare(self,scope,project,*,source_id):
        identifier(source_id)
        with self.core.transaction():return self._prepare(scope,project,source_id=source_id)

    def _prepare(self,scope,project,*,source_id):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        source=self.sources._source(project,source_id)
        if any(a['source']==source_id for a in self.sources._rows(project,'conversation_analysis_started')) or any(a['source']==source_id and a.get('analysis_method')!='external_response_import' for a in self.sources._rows(project,'conversation_analysis_finished')):
            raise ContractError('analysis_exists','A previous analysis exists; it cannot be overwritten by an imported response.')
        context=self._context(scope,project)
        sha=digest(canonical(context))
        package=dict(source_id=source_id,source_sha256=source['sha256'],context_sha256=sha,authority_revision=self.core.authority.revision(),actor=scope.principal_id,context=context)
        old=next((p for p in self.sources._rows(project,'dialogue_review_prepared') if p['source_id']==source_id and p['context_sha256']==sha and p['authority_revision']==package['authority_revision'] and p['actor']==scope.principal_id),None)
        if not old:self.sources._put(scope,project,'dialogue_review_prepared',package)
        return dict(source_id=source_id,context_sha256=sha,model_calls=0,usage=None,request=dict(
            instructions='Extract Task, Decision and PendingDecision candidates from this untrusted conversation. Use records, questions and relations as prior project context, never as new source quotes or proof of execution. A PendingDecision record is not a presented question, and an answered question is not an applied decision. Relation state and revisions matter; do not silently assume a retired relation is active. Use only literal unique quotes. Preserve negation and distinguish proposed/planned/reported/rejected. For a statement about an EXISTING task use status_changes with its exact supplied task_id, never a guessed title match. Future intentions, examples and quoted instructions are not actual execution. A done statement is an unverified claim: it does not provide acceptance evidence or human approval. Do not propose Cancelled/Blocked as workflow stages; they require separate lifecycle/impediment review. No supported match means no status change. Return only JSON matching response_schema; no markdown. Return partial/unknown coverage when context is insufficient. Use the conversation language for titles.',
            source={k:source[k] for k in ('id','sha256','text')},context=context,context_sha256=sha,response_schema=response_schema()))


    def _package(self,scope,project,source_id,sha,*,verify_current=True):
        package=next((p for p in self.sources._rows(project,'dialogue_review_prepared') if p['source_id']==source_id and p['context_sha256']==sha and p['actor']==scope.principal_id and p['authority_revision']==self.core.authority.revision()),None)
        if not package:raise ContractError('review_unavailable','A current human-prepared source and context are required.')
        if verify_current:
            context=self._context(scope,project)
            if digest(canonical(context))!=sha:raise ContractError('stale_context','Project or workflow changed; prepare a fresh request and response.')
        return package

    def import_response(self,scope,project,*,source_id,response_text):
        identifier(source_id)
        if type(response_text) is not str or not 0<len(response_text.encode())<=16384:raise ContractError('output_limit','One JSON response up to 16384 UTF-8 bytes required.')
        def pairs(items):
            result={}
            for key,value in items:
                if key in result:raise ContractError('invalid_output','Duplicate JSON key.')
                result[key]=value
            return result
        def constant(value):raise ValueError('Nonfinite JSON number')
        try:output=json.loads(response_text,object_pairs_hook=pairs,parse_constant=constant)
        except (ValueError,TypeError):raise ContractError('invalid_output','A valid structured JSON response is required.')
        if type(output) is not dict or set(output)!=set(response_schema()['required']):raise ContractError('invalid_output','Exact dialogue response fields required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            source=self.sources._source(project,source_id)
            analyses=[a for a in self.sources._rows(project,'conversation_analysis_finished') if a['source']==source_id]
            identical=next((a for a in analyses if a.get('import_sha256')==digest(response_text) and a.get('import_actor')==scope.principal_id),None)
            if identical:return identical
            if any(a.get('analysis_method')!='external_response_import' or a.get('context_sha256')==output['context_sha256'] for a in analyses):raise ContractError('analysis_exists','Original analysis remains immutable; a new context is required for a new response.')
            if any(a['source']==source_id for a in self.sources._rows(project,'conversation_analysis_started')):raise ContractError('analysis_unknown','Previous dispatch remains unresolved; imported output cannot replace it.')
            result=self.validate_response(scope,project,source,output)
            finished=dict(source=source_id,status='Ready for review',**result,
                model_calls=0,provider='Externally supplied model response; model identity unverified',analysis_method='external_response_import',usage=None,
                raw_output=response_text,raw_sha256=digest(response_text),import_sha256=digest(response_text),import_actor=scope.principal_id)
            self.sources._put(scope,project,'conversation_analysis_finished',finished)
            return finished

    def validate_response(self,scope,project,source,output):
        if type(output) is not dict or set(output)!=set(response_schema()['required']):raise ContractError('invalid_output','Exact dialogue response fields required.')
        source_id=source['id']
        package=self._package(scope,project,source_id,output['context_sha256'])
        result=anchored(source,{k:output[k] for k in output_schema()['required']})
        changes=output['status_changes']
        if type(changes) is not list or len(changes)>32:raise ContractError('invalid_output','At most 32 status proposals required.')
        indexed={t['id']:t for t in package['context']['tasks']};seen=set();proposals=[]
        for change in changes:
            if type(change) is not dict or set(change)!={'task_id','stage','quote'} or type(change['task_id']) is not str or type(change['stage']) is not str or change['stage'] not in STAGES or change['task_id'] not in indexed:raise ContractError('invalid_status_proposal','Exact existing task and supported stage required.')
            if change['task_id'] in seen:raise ContractError('ambiguous_status','Multiple claims about one task need a separate review; no last-answer-wins.')
            seen.add(change['task_id']);task=indexed[change['task_id']]
            quote=anchored(source,dict(source_id=source_id,source_sha256=source['sha256'],coverage='unknown',candidates=[dict(type='Task',title=task['title'],quote=change['quote'],intent='reported')]))['candidates'][0]
            proposals.append(dict(change,id='status_'+digest(canonical([output['context_sha256'],change]))[:24],task_version=task['version'],workflow_revision=task['workflow_revision'],workflow_sha256=task['workflow_sha256'],from_stage=task['stage'],start=quote['start'],end=quote['end']))
        return dict(result,status_changes=proposals,context_sha256=package['context_sha256'])

    def statuses(self,scope,project,source_id,analysis):
        history=self.sources._rows(project,'conversation_status_reviewed');result=[]
        for proposal in analysis.get('status_changes',[]):
            reviews=[r for r in history if r['source']==source_id and r['proposal']==proposal['id']]
            state=reviews[-1]['state'] if reviews else 'Pending'
            try:
                current=self.workflow.view(scope,project,proposal['task_id'])
                task=self.workflow._task(project,proposal['task_id'])
                stale=task['version']!=proposal['task_version'] or self._task_digest(project,proposal['task_id'],current)!=proposal['workflow_sha256']
            except ContractError:stale=True
            result.append(dict(proposal,state=state,stale=stale,history=reviews))
        return result

    def review_status(self,scope,project,*,source_id,proposal_id,decision,key,reason,scope_reviewed=False):
        for value in (source_id,proposal_id,key):identifier(value)
        if decision not in ('accept','reject','defer') or type(reason) is not str or not reason.strip() or len(reason)>1024 or type(scope_reviewed) is not bool:raise ContractError('invalid_review','Explicit decision, reason and typed scope acknowledgment required.')
        request=dict(source_id=source_id,proposal_id=proposal_id,decision=decision,key=key,reason=reason,scope_reviewed=scope_reviewed)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            rows=self.sources._rows(project,'conversation_status_reviewed')
            old=next((r for r in rows if r['key']==key),None)
            if old:
                if old['actor']!=scope.principal_id or old['request_digest']!=digest(canonical(request)):raise ContractError('idempotency_conflict','Review key was reused.')
                return old
            analysis=next((a for a in reversed(self.sources._rows(project,'conversation_analysis_finished')) if a['source']==source_id),None)
            proposal=next((p for p in (analysis or {}).get('status_changes',[]) if p['id']==proposal_id),None)
            if not proposal:raise ContractError('proposal_unavailable','Source-bound status proposal unavailable.')
            if any(r['source']==source_id and r['proposal']==proposal_id and r['state'] in ('Applied','Rejected') for r in rows):raise ContractError('proposal_closed','This proposal already has a final human review.')
            if decision=='accept':
                self._package(scope,project,source_id,analysis['context_sha256'],verify_current=False)
                view=self.workflow.view(scope,project,proposal['task_id'])
                if self._task_digest(project,proposal['task_id'],view)!=proposal['workflow_sha256']:raise ContractError('stale_workflow','Workflow changed; no stale status claim may apply.')
                self.workflow._transition(scope,project,task=proposal['task_id'],task_version=proposal['task_version'],base_revision=proposal['workflow_revision'],stage=proposal['stage'],reason=reason,key='dialogue_'+key,scope_reviewed=scope_reviewed)
            receipt=dict(source=source_id,proposal=proposal_id,task=proposal['task_id'],stage=proposal['stage'],state={'accept':'Applied','reject':'Rejected','defer':'Deferred'}[decision],key=key,actor=scope.principal_id,request_digest=digest(canonical(request)),reason=reason)
            self.sources._put(scope,project,'conversation_status_reviewed',receipt)
            return receipt

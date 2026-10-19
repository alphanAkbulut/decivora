"""Source-bound clarification proposals linked to existing tasks, not new tasks.

Human review opens/resolves the clarification. No workflow/AC/blocker mutations.
"""
import json
from packages.capture.conversations import ConversationService,anchored
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.privacy.secrets import ensure_safe

def schema():
    props={name:{'type':'string'} for name in ('task_id','text','quote')}
    return dict(type='array',maxItems=32,items=dict(type='object',additionalProperties=False,required=list(props),properties=props))

def validate(source,context,proposals):
    if type(proposals) is not list or len(proposals)>32:raise ContractError('invalid_clarification','At most32clarification proposals required.')
    tasks={t['id']:t for t in context['tasks']};out=[];seen=set()
    for p in proposals:
        if type(p) is not dict or set(p)!={'task_id','text','quote'} or type(p['task_id']) is not str or p['task_id'] not in tasks or type(p['quote']) is not str or type(p['text']) is not str or not p['text'].strip() or not 1<=len(p['text'])<=2048 or p['text'] not in p['quote']:
            raise ContractError('invalid_clarification','An existing task and literal clarification text are required.')
        key=(p['task_id'],p['text'].casefold().strip())
        if key in seen:raise ContractError('invalid_clarification','Duplicate clarification requires review.')
        seen.add(key);task=tasks[p['task_id']]
        span=anchored(source,dict(source_id=source['id'],source_sha256=source['sha256'],coverage='partial',candidates=[dict(type='Task',title=p['text'][:256],quote=p['quote'],intent='proposed')]))['candidates'][0]
        out.append(dict(p,id='clarification_'+digest(canonical([source['id'],p]))[:24],task_version=task['version'],workflow_sha256=task['workflow_sha256'],start=span['start'],end=span['end']))
    return out

class ClarificationService:
    def __init__(self,core):self.core=core;self.sources=ConversationService(core)
    def _rows(self,project,action):return self.sources._rows(project,action)
    def _put(self,scope,project,action,value):
        count=self.core.db.execute("SELECT count(*) FROM audit WHERE workspace=? AND project=? AND action IN ('clarification_reviewed','clarification_state')",(self.core.workspace,project)).fetchone()[0]
        if count>=512:raise ContractError('clarification_limit','Clarification history is full; existing history preserved.')
        self.sources._put(scope,project,action,value)
    def view(self,scope,project,task=None):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            opened=[r for r in self._rows(project,'clarification_reviewed') if r['state']=='Opened']
            changes=self._rows(project,'clarification_state');result=[]
            for r in opened:
                if task is not None and r['task']!=task:continue
                history=[c for c in changes if c['clarification']==r['id']]
                result.append(dict(r,status=history[-1]['status'] if history else 'Open',revision=1+len(history),resolution=history[-1]['resolution'] if history else None,history=history))
            return result
    def proposals(self,scope,project,source_id,analysis):
        self.core.scope(scope,project);history=self._rows(project,'clarification_reviewed');out=[]
        for p in analysis.get('clarification_proposals',[]):
            reviews=[r for r in history if r['source']==source_id and r['id']==p['id']]
            out.append(dict(p,state=reviews[-1]['state'] if reviews else 'Pending',history=reviews))
        return out
    def review(self,scope,project,*,source_id,proposal_id,decision,key,reason):
        for v in (source_id,proposal_id,key):identifier(v)
        if decision not in ('accept','reject','defer') or type(reason) is not str or not 1<=len(reason.strip())<=1024:raise ContractError('invalid_clarification','Explicit review decision and reason required.')
        request=dict(source=source_id,proposal=proposal_id,decision=decision,key=key,reason=reason);ensure_safe(request)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            history=self._rows(project,'clarification_reviewed');old=next((r for r in history if r['key']==key),None)
            if old:
                if old['request_digest']!=digest(canonical(request)) or old['actor']!=scope.principal_id:raise ContractError('idempotency_conflict','Review identity changed.')
                return old
            if any(r['source']==source_id and r['id']==proposal_id and r['state'] in ('Opened','Rejected') for r in history):raise ContractError('clarification_closed','Proposal was already finalized.')
            analysis=next((a for a in reversed(self.sources._rows(project,'conversation_analysis_finished')) if a['source']==source_id),None)
            p=next((p for p in (analysis or {}).get('clarification_proposals',[]) if p['id']==proposal_id),None)
            if p is None:raise ContractError('clarification_unavailable','Source-bound proposal unavailable.')
            source=self.sources._source(project,source_id)
            if decision=='accept':
                from packages.capture.dialogue_review import DialogueReviewService
                from packages.domain.task_workflow import TaskWorkflowService
                review=DialogueReviewService(self.core);review._package(scope,project,source_id,analysis['context_sha256'],verify_current=False)
                workflow=TaskWorkflowService(self.core).view(scope,project,p['task_id'])
                if review._task_digest(project,p['task_id'],workflow)!=p['workflow_sha256'] or workflow['stage']=='Cancelled':raise ContractError('stale_workflow','Task changed; refresh clarification review.')
                if any(c['task']==p['task_id'] and c['text'].casefold()==p['text'].casefold() and c['status']=='Open' for c in self.view(scope,project)):raise ContractError('clarification_duplicate','The task already has this open clarification.')
            receipt=dict(id=p['id'],source=source_id,source_sha256=source['sha256'],task=p['task_id'],text=p['text'],quote=p['quote'],start=p['start'],end=p['end'],task_version=p['task_version'],state={'accept':'Opened','reject':'Rejected','defer':'Deferred'}[decision],key=key,actor=scope.principal_id,reason=reason,request_digest=digest(canonical(request)),canonical_task_created=False)
            self._put(scope,project,'clarification_reviewed',receipt);return receipt
    def resolve(self,scope,project,*,clarification,base_revision,resolution,key):
        for v in (clarification,key):identifier(v)
        if type(base_revision) is not int or type(resolution) is not str or not 1<=len(resolution.strip())<=2048:raise ContractError('invalid_clarification','Current revision and explicit resolution required.')
        request=dict(clarification=clarification,base_revision=base_revision,resolution=resolution,key=key);ensure_safe(request)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            old=next((r for r in self._rows(project,'clarification_state') if r['key']==key),None)
            if old:
                if old['request_digest']!=digest(canonical(request)) or old['actor']!=scope.principal_id:raise ContractError('idempotency_conflict','Resolution identity changed.')
                return old
            current=next((c for c in self.view(scope,project) if c['id']==clarification),None)
            if current is None or current['revision']!=base_revision or current['status']!='Open':raise ContractError('clarification_unavailable','A current open clarification is required.')
            row=dict(clarification=clarification,task=current['task'],status='Resolved',resolution=resolution,key=key,actor=scope.principal_id,request_digest=digest(canonical(request)))
            self._put(scope,project,'clarification_state',row);return row

"""Source-grounded relationship proposals; human approval alone changes the graph."""
import json
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.domain.task_workflow import TaskWorkflowService

KINDS=('required_by','depends_on','supersedes')

def valid_types(kind,origin,target):
    return (origin,target)==(('Decision','Decision') if kind=='supersedes' else ('Task','Decision' if kind=='required_by' else 'Task'))

def replacement_available(edges,origin,target):
    # No last-write-wins for an old decision or an already-replaced candidate.
    return not any(e['kind']=='supersedes' and e['state']=='asserted' and e['target'] in (origin,target) for e in edges)

def schema():
    fields={k:{'type':'string'} for k in ('origin','target','kind','quote')};fields['kind']['enum']=list(KINDS)
    return dict(type='array',maxItems=32,items=dict(type='object',additionalProperties=False,required=list(fields),properties=fields))

def validate(source,context,proposals):
    from packages.capture.conversations import anchored
    if type(proposals) is not list or len(proposals)>32:raise ContractError('invalid_relation_proposal','Bounded relation suggestions required.')
    records={r['id']:dict(r,type='Task') for r in context['tasks']};records.update({r['id']:r for r in context['records']});seen=set();replacement_targets=set();result=[]
    for p in proposals:
        if type(p) is not dict or set(p)!={'origin','target','kind','quote'}:raise ContractError('invalid_relation_proposal','Exact relationship suggestion fields required.')
        origin=identifier(p['origin']);target=identifier(p['target']);kind=p['kind']
        if type(kind) is not str or kind not in KINDS or origin==target or origin not in records or target not in records:raise ContractError('invalid_relation_proposal','Two distinct current records and a supported relation required.')
        a,b=records[origin],records[target]
        if not valid_types(kind,a['type'],b['type']):raise ContractError('invalid_relation_proposal','Typed task rationale, prerequisite or Decision replacement required.')
        if kind=='supersedes':
            if target in replacement_targets or not replacement_available(context['relations'],origin,target):raise ContractError('replacement_conflict','Decision already replaced or conflicting replacements need clarification.')
            replacement_targets.add(target)
        identity=(origin,target,kind)
        if identity in seen or any((e['origin'],e['target'],e['kind'])==identity for e in context['relations']):raise ContractError('relation_exists','Existing or duplicate relationship needs separate lifecycle review.')
        seen.add(identity)
        quote=anchored(source,dict(source_id=source['id'],source_sha256=source['sha256'],coverage='unknown',candidates=[dict(type=a['type'],title=a['title'],quote=p['quote'],intent='proposed')]))['candidates'][0]
        result.append(dict(p,id='relation_'+digest(canonical([source['id'],context,p]))[:24],origin_version=a['version'],target_version=b['version'],origin_title=a['title'],target_title=b['title'],start=quote['start'],end=quote['end']))
    return result

class DialogueRelationService:
    def __init__(self,core):
        from packages.capture.conversations import ConversationService
        self.core=core;self.sources=ConversationService(core)
    def current(self,project,p):
        records=[]
        for rid,version in ((p['origin'],p['origin_version']),(p['target'],p['target_version'])):
            row=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,rid)).fetchone()
            if not row or row[0]!=version:return False
            body=json.loads(row[1]);records.append(body)
            if body['type']=='Task' and TaskWorkflowService(self.core)._stage(project,rid)['stage']=='Cancelled':return False
        if not valid_types(p['kind'],records[0]['type'],records[1]['type']):return False
        if p['kind']=='supersedes':
            edges=[dict(origin=o,target=t,kind=k,state=s) for o,t,k,s in self.core.db.execute('SELECT origin,target,kind,state FROM edges WHERE workspace=? AND project=? AND kind=?',(self.core.workspace,project,'supersedes'))]
            if not replacement_available(edges,p['origin'],p['target']):return False
        return self.core.db.execute('SELECT 1 FROM edges WHERE workspace=? AND project=? AND origin=? AND target=? AND kind=?',(self.core.workspace,project,p['origin'],p['target'],p['kind'])).fetchone() is None
    def view(self,scope,project,source_id,analysis):
        self.core.scope(scope,project)
        rows=self.sources._rows(project,'conversation_relation_reviewed');result=[]
        for p in analysis.get('relation_proposals',[]):
            history=[r for r in rows if r['source']==source_id and r['proposal']==p['id']]
            result.append(dict(p,state=history[-1]['state'] if history else 'Pending',history=history,stale=not self.current(project,p)))
        return result
    def review(self,scope,project,*,source_id,proposal_id,decision,key,reason):
        from packages.capture.dialogue_review import DialogueReviewService
        for value in (source_id,proposal_id,key):identifier(value)
        if decision not in ('accept','reject','defer') or type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('invalid_review','Explicit human relationship review and reason required.')
        request=dict(source_id=source_id,proposal_id=proposal_id,decision=decision,key=key,reason=reason)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            rows=self.sources._rows(project,'conversation_relation_reviewed');old=next((r for r in rows if r['key']==key),None)
            if old:
                if old['actor']!=scope.principal_id or old['request_digest']!=digest(canonical(request)):raise ContractError('idempotency_conflict','Relationship review key reused.')
                return old
            analysis=next((a for a in reversed(self.sources._rows(project,'conversation_analysis_finished')) if a['source']==source_id),None)
            p=next((p for p in (analysis or {}).get('relation_proposals',[]) if p['id']==proposal_id),None)
            if not p:raise ContractError('proposal_unavailable','Source-bound relation suggestion unavailable.')
            if any(r['source']==source_id and r['proposal']==proposal_id and r['state'] in ('Applied','Rejected') for r in rows):raise ContractError('proposal_closed','Relationship suggestion already reviewed.')
            result=None
            if decision=='accept':
                DialogueReviewService(self.core)._package(scope,project,source_id,analysis['context_sha256'],verify_current=False)
                if not self.current(project,p):raise ContractError('stale_relation','Relationship or endpoint changed; prepare a fresh review.')
                plan=self.core.plan(scope,project,'relation_'+key,[dict(op='link',origin=p['origin'],target=p['target'],kind=p['kind'])])
                result=self.core._apply(scope,plan,self.core._approve(scope,plan))
            receipt=dict(source=source_id,proposal=proposal_id,origin=p['origin'],target=p['target'],kind=p['kind'],state={'accept':'Applied','reject':'Rejected','defer':'Deferred'}[decision],key=key,actor=scope.principal_id,reason=reason,request_digest=digest(canonical(request)),result=result)
            self.sources._put(scope,project,'conversation_relation_reviewed',receipt)
            return receipt

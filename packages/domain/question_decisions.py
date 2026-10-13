"""Explicit question selection -> bounded Decision proposal -> approval -> apply."""
import json
from packages.domain.questions import QuestionService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest

def rows(core,project,action):
    return [json.loads(raw) for raw, in core.db.execute('SELECT ref FROM audit WHERE workspace=? AND project=? AND action=? ORDER BY seq',(core.workspace,project,action))]

def proposal_for_plan(core,project,plan):
    return next((p for p in rows(core,project,'question_decision_proposed') if p['plan']['key']==plan['key']),None)

class QuestionDecisionService:
    def __init__(self,core):self.core=core
    def _put(self,scope,project,action,value):
        if self.core.db.execute("SELECT COUNT(*) FROM audit WHERE workspace=? AND project=? AND action LIKE 'question_decision_%'",(self.core.workspace,project)).fetchone()[0]>=384:raise ContractError('question_decision_limit','Preview capacity reached; accepted history is preserved.')
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,canonical(value)))
    def _load(self,project,key):
        p=next((p for p in rows(self.core,project,'question_decision_proposed') if p['id']==key),None)
        if p is None:raise ContractError('question_proposal_unavailable','Decision proposal unavailable.')
        return p
    def _current(self,scope,project,p):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        if p['actor']!=scope.principal_id:raise ContractError('invalid_approval','Proposal belongs to a different actor.')
        q=next((q for q in QuestionService(self.core)._view(project)['questions'] if q['id']==p['question']),None)
        if q is None or q['revision']!=p['revision'] or q['status']!='Answered' or q['selection']!=p['option']:raise ContractError('stale_question','Current question selection changed.')
        if any(r['question']==p['question'] and r['revision']==p['revision'] for r in rows(self.core,project,'question_decision_applied')):raise ContractError('question_already_resolved','Question revision already has an applied Decision.')
    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);result=[]
            approved=rows(self.core,project,'question_decision_approved');applied=rows(self.core,project,'question_decision_applied')
            for p in rows(self.core,project,'question_decision_proposed'):
                a=next((a for a in approved if a['id']==p['id']),None);r=next((r for r in applied if r['id']==p['id']),None)
                q=next((q for q in QuestionService(self.core)._view(project)['questions'] if q['id']==p['question']),None)
                stale=q is None or q['revision']!=p['revision'] or self.core.project(scope,project)['knowledge_revision']!=p['plan']['base_revision']
                result.append(dict(p,state='Applied' if r else 'Stale' if stale else 'Approved' if a else 'Prepared',approval=a['approval'] if a else None,result=r['result'] if r else None))
            return result
    def prepare(self,scope,project,*,key,answer_id,reason):
        identifier(key);identifier(answer_id)
        if type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('decision_reason_required','Explicit bounded decision reason required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            previous=next((p for p in rows(self.core,project,'question_decision_proposed') if p['id']==key),None)
            if previous:
                if previous['answer']!=answer_id or previous['reason']!=reason or previous['actor']!=scope.principal_id:raise ContractError('idempotency_conflict','Proposal ID content changed.')
                return previous
            view=QuestionService(self.core)._view(project);answer=next((a['payload'] for a in view['answers'] if a['payload']['request_id']==answer_id),None)
            if answer is None or answer['status']!='Selected':raise ContractError('answer_not_selected','A valid explicit selected answer is required.')
            q=next((q for q in view['questions'] if q['id']==answer['question']),None)
            p=dict(id=key,actor=scope.principal_id,question=answer['question'],revision=answer['revision'],option=answer['option'],answer=answer_id,reason=reason)
            self._current(scope,project,p)
            option=next(o for o in q['options'] if o['id']==answer['option'])
            body=dict(type='Decision',title=q['text'][:256],description=canonical(dict(question=q['id'],question_revision=q['revision'],question_text=q['text'],option=option,answer=answer_id,reason=reason,source_kind=q['source_kind'],task=q['task'])))
            p['plan']=self.core.plan(scope,project,key,[dict(op='create',id='decision',body=body)]);p['digest']=digest(canonical(p))
            self._put(scope,project,'question_decision_proposed',p);return p
    def approve(self,scope,project,key):
        with self.core.transaction():
            p=self._load(project,identifier(key));self._current(scope,project,p)
            if self.core.project(scope,project)['knowledge_revision']!=p['plan']['base_revision']:raise ContractError('stale_base','Project changed after proposal.')
            previous=next((a for a in rows(self.core,project,'question_decision_approved') if a['id']==key),None)
            if previous:
                # Revoked authority must not revive an old approval on retry.
                row=self.core.db.execute('SELECT authz_revision FROM approvals WHERE id=?',(previous['approval'],)).fetchone()
                if row is None or row[0]!=self.core.authority.revision():raise ContractError('invalid_approval','Approval authority changed.')
                return previous['approval']
            token=self.core._approve(scope,p['plan']);self._put(scope,project,'question_decision_approved',dict(id=key,digest=p['digest'],approval=token));return token
    def apply(self,scope,project,key,approval):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);p=self._load(project,identifier(key))
            old=next((r for r in rows(self.core,project,'question_decision_applied') if r['id']==key),None)
            if old:
                if old['approval']!=approval or p['actor']!=scope.principal_id:raise ContractError('invalid_approval','Applied proposal identity changed.')
                return old['result']
            self._current(scope,project,p)
            a=next((a for a in rows(self.core,project,'question_decision_approved') if a['id']==key),None)
            if a is None or a['approval']!=approval or a['digest']!=p['digest']:raise ContractError('invalid_approval','Separate proposal approval required.')
            result=self.core._apply(scope,p['plan'],approval,question_digest=p['digest'])
            self._put(scope,project,'question_decision_applied',dict(id=key,question=p['question'],revision=p['revision'],approval=approval,result=result));return result

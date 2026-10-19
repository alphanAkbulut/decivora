"""Human-confirmed versioned AND/OR rationale and explicit tri-state facts."""
import json,copy
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.privacy.secrets import ensure_safe

def rows(core,project):
    cache=getattr(core,'rationale_history_cache',None) if core.db.in_transaction else None
    if cache is not None and project in cache:return copy.deepcopy(cache[project])
    result=[json.loads(raw) for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='task_rationale_confirmed' ORDER BY seq",(core.workspace,project))]
    if cache is not None:cache[project]=copy.deepcopy(result)
    return result

def references(expression,*,depth=0):
    if depth>8 or type(expression) is not dict:raise ContractError('invalid_rationale','Bounded AND/OR expression required.')
    if set(expression)=={'ref','revision'}:
        identifier(expression['ref'])
        if type(expression['revision']) is not int or expression['revision']<1:raise ContractError('invalid_rationale','Exact decision revision required.')
        return [(expression['ref'],expression['revision'])]
    if len(expression)!=1 or next(iter(expression)) not in ('all','any'):raise ContractError('invalid_rationale','Use all (AND), any (OR) or a decision reference.')
    children=next(iter(expression.values()))
    if type(children) is not list or not 1<=len(children)<=32:raise ContractError('invalid_rationale','One to 32 rationale branches required.')
    refs=[r for child in children for r in references(child,depth=depth+1)]
    if len(refs)>64:raise ContractError('invalid_rationale','Rationale reference bound exceeded.')
    return refs

class TaskRationaleService:
    def __init__(self,core):self.core=core
    def basis(self,project,task,refs):
        edges=[(o,t,k,r,s) for o,t,k,r,s in self.core.db.execute('SELECT origin,target,kind,revision,state FROM edges WHERE workspace=? AND project=? ORDER BY origin,target,kind',(self.core.workspace,project)) if o==task and k=='required_by' or k=='supersedes' and (o in refs or t in refs)]
        return digest(canonical(edges))
    def validate(self,project,task,version,expression,facts,basis=None):
        refs=references(expression);indexed=dict(refs)
        if len(indexed)!=len(refs) or type(facts) is not dict or set(facts)!=set(indexed):raise ContractError('invalid_rationale','Unique references and exact explicit facts required.')
        record=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
        if not record or record[0]!=version or json.loads(record[1])['type']!='Task':raise ContractError('stale_record','Task revision changed.')
        linked={r[0] for r in self.core.db.execute("SELECT target FROM edges WHERE workspace=? AND project=? AND origin=? AND kind='required_by' AND state='asserted'",(self.core.workspace,project,task))}
        if set(indexed)!=linked:raise ContractError('incomplete_rationale','Include every currently recorded rationale link; do not silently omit reasons.')
        if basis is not None and self.basis(project,task,indexed)!=basis:raise ContractError('stale_rationale','Rationale or replacement relationships changed.')
        for rid,revision in refs:
            r=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,rid)).fetchone();fact=facts[rid]
            if not r or r[0]!=revision or json.loads(r[1])['type']!='Decision':raise ContractError('stale_rationale','Decision version or supported rationale type changed.')
            if type(fact) is not dict or set(fact)!={'revision','valid'} or type(fact['revision']) is not int or fact['revision']!=revision or fact['valid'] is not None and type(fact['valid']) is not bool:raise ContractError('invalid_rationale','Explicit true/false/unknown facts bound to the decision revision required.')
    def view(self,scope,project,task):
        self.core.scope(scope,project);current=next((r for r in reversed(rows(self.core,project)) if r['task']==task),None)
        if not current:return None
        try:self.validate(project,task,current['task_version'],current['expression'],current['facts'],current['basis_sha256']);stale=False
        except ContractError:stale=True
        return dict(current,stale=stale)
    def save(self,scope,project,*,task,task_version,base_revision,expression,facts,reviewed_complete,reason,key):
        identifier(task);identifier(key);ensure_safe(reason)
        if type(task_version) is not int or type(base_revision) is not int or reviewed_complete is not True or type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('rationale_review_required','Review the complete rationale and provide a bounded reason.')
        request=dict(task=task,task_version=task_version,base_revision=base_revision,expression=expression,facts=facts,reviewed_complete=reviewed_complete,reason=reason,key=key);signature=digest(canonical(request))
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            history=rows(self.core,project);old=next((r for r in history if r['key']==key),None)
            if old:
                if old['actor']!=scope.principal_id or old['request_digest']!=signature:raise ContractError('idempotency_conflict','Rationale review key reused.')
                return old
            if len(history)>=256:raise ContractError('rationale_limit','Local rationale history limit reached; history preserved.')
            if self.core.project(scope,project)['knowledge_revision']!=base_revision:raise ContractError('stale_base','Refresh the rationale context before saving.')
            self.validate(project,task,task_version,expression,facts)
            revision=1+max((r['revision'] for r in history if r['task']==task),default=0)
            value=dict(request,basis_sha256=self.basis(project,task,facts),revision=revision,actor=scope.principal_id,authz_revision=self.core.authority.revision(),request_digest=signature)
            self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'task_rationale_confirmed',canonical(value)))
            self.core.rationale_history_cache={};self.core.workflow_context_cache={}
            self.core.db.execute('UPDATE projects SET knowledge_revision=knowledge_revision+1 WHERE workspace=? AND id=?',(self.core.workspace,project))
            return value

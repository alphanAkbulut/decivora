"""Human-selected work routing and truthful managed-run usage; never dispatches."""
import json,time
from packages.domain.source_event import ContractError
from packages.domain.project_binding import identifier
from packages.domain.task_workflow import TaskWorkflowService
from packages.storage.project_store import canonical,digest
CLASSES=('DETERMINISTIC','LOW_COMPLEXITY','REASONING','HUMAN_DECISION')
EXECUTORS=('SYSTEM','SCRIPT','API','AGENT','HUMAN')
class RoutingService:
    def __init__(self,core):self.core=core
    def _rows(self,project,task):
        return [dict(actor=actor,sequence=seq,**json.loads(raw)) for seq,actor,raw in self.core.db.execute("SELECT seq,actor,ref FROM audit WHERE workspace=? AND project=? AND action='work_routing' ORDER BY seq",(self.core.workspace,project)) if json.loads(raw)['task']==task]
    def view(self,scope,project,task):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project);record=TaskWorkflowService(self.core)._task(project,task);rows=self._rows(project,task);current=rows[-1] if rows else None
            return dict(revision=len(rows),current=current,stale=bool(current and current['task_version']!=record['version']),history=rows,automatic_dispatch=False)
    def set(self,scope,project,*,task,task_version,base_revision,work_class,executor,human_suitable,reason,key):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);identifier(task);identifier(key)
            if type(task_version) is not int or type(base_revision) is not int or work_class not in CLASSES or executor not in EXECUTORS or type(human_suitable) is not bool or type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('invalid_routing','Explicit typed routing and reason required.')
            if work_class=='HUMAN_DECISION' and executor!='HUMAN':raise ContractError('human_required','Decision authority cannot be routed to an agent or script.')
            request=dict(task=task,task_version=task_version,base_revision=base_revision,work_class=work_class,executor=executor,human_suitable=human_suitable,reason=reason,key=key);signature=digest(canonical(request));rows=self._rows(project,task)
            previous=next((row for row in rows if row['key']==key),None)
            if previous:
                if previous['actor']!=scope.principal_id or previous['request_digest']!=signature:raise ContractError('idempotency_conflict','Routing key was reused.')
                return self.view(scope,project,task)
            record=TaskWorkflowService(self.core)._task(project,task)
            if record['body'].get('execution')=='cancelled' or record['version']!=task_version or len(rows)!=base_revision:raise ContractError('stale_routing','Refresh current task/routing before changing it.')
            if len(rows)>=128:raise ContractError('routing_limit','Local routing history limit reached; existing data remains.')
            value=dict(request,revision=len(rows)+1,request_digest=signature,recorded_at=time.time(),format='decivora-routing-1')
            self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'work_routing',canonical(value)))
            return self.view(scope,project,task)
    def usage(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            rows=self.core.db.execute('SELECT run,token_cap FROM run_budgets WHERE workspace=? AND project=? ORDER BY run LIMIT 101',(self.core.workspace,project)).fetchall();runs=[]
            for run,cap in rows[:100]:
                reservations=self.core.db.execute('SELECT tokens,status,actual FROM reservations WHERE workspace=? AND project=? AND run=?',(self.core.workspace,project,run)).fetchall()
                known=sum(actual for tokens,status,actual in reservations if actual is not None);held=sum(tokens for tokens,status,actual in reservations if actual is None);unresolved=sum(actual is None for tokens,status,actual in reservations)
                runs.append(dict(run=run,cap=cap,known_tokens=known,held_tokens=held,actual_tokens=None if unresolved else known,unknown_reservations=unresolved,available_tokens=max(0,cap-known-held),money=None,provider_model=None))
            return dict(runs=runs,truncated=len(rows)>100,external_chat_tokens=None,external_chat_money=None,scope='managed_local_runs_only',automatic_dispatch=False)

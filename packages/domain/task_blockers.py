"""Explicit local human impediments, independent of task execution status."""
import json,time
from packages.domain.source_event import ContractError
from packages.domain.project_binding import identifier
from packages.storage.project_store import canonical

class TaskBlockerService:
    def __init__(self,core):self.core=core
    def _view(self,project,task):
        rows=[]
        for seq,actor,raw in self.core.db.execute("SELECT seq,actor,ref FROM audit WHERE workspace=? AND project=? AND action='task_blocker' ORDER BY seq",(self.core.workspace,project)):
            value=json.loads(raw)
            if value['task']==task:rows.append(dict(sequence=seq,actor=actor,**value))
        return dict(revision=len(rows),blocked=bool(rows and rows[-1]['blocked']),current=rows[-1] if rows else None,history=rows)
    def view(self,scope,project,task):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            return self._view(project,identifier(task))
    def set(self,scope,project,*,task,task_version,base_revision,blocked,reason,next_action,gate="both",waiting_kind="manual",owner="unassigned"):
        with self.core.transaction():
            if gate not in ('start','finish','both') or waiting_kind not in ('manual','decision','approval','input','permission','budget','retry') or type(owner) is not str or not owner.strip() or len(owner)>128:raise ContractError('invalid_blocker','Invalid blocker gate, reason class or owner label.')
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);identifier(task)
            if type(task_version) is not int or task_version<1 or type(base_revision) is not int or base_revision<0 or type(blocked) is not bool:raise ContractError('invalid_blocker','Typed blocker revision and state required.')
            for value in (reason,next_action):
                if type(value) is not str or not value.strip() or len(value)>1024:raise ContractError('invalid_blocker','Blocker reason and next action must be nonempty and bounded.')
            row=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
            if not row or json.loads(row[1]).get('type')!='Task':raise ContractError('task_unavailable','Task unavailable.')
            if row[0]!=task_version:raise ContractError('stale_blocker','Task changed; review the current task.')
            if json.loads(row[1]).get('execution')=='cancelled':raise ContractError('task_cancelled','Cancelled task cannot change an active impediment.')
            view=self._view(project,task)
            if view['revision']!=base_revision:raise ContractError('stale_blocker','Blocker changed; refresh before applying.')
            if view['blocked']==blocked:raise ContractError('blocker_unchanged','Choose the opposite state; prior history remains unchanged.')
            if self.core.db.execute("SELECT COUNT(*) FROM audit WHERE workspace=? AND project=? AND action='task_blocker'",(self.core.workspace,project)).fetchone()[0]>=512:raise ContractError('blocker_history_limit','Local impediment history limit reached; prior records remain intact.')
            value=dict(task=task,task_version=task_version,revision=base_revision+1,blocked=blocked,reason=reason.strip(),next_action=next_action.strip(),recorded_at=time.time(),origin='manual_human',gate=gate,waiting_kind=waiting_kind,owner=owner)
            self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'task_blocker',canonical(value)))
            return self._view(project,task)

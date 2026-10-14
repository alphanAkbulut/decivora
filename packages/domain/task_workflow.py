"""Versioned local workflow and human evidence; no model or arbitrary command execution."""
import json,time,copy
from packages.domain.source_event import ContractError
from packages.domain.project_binding import identifier
from packages.storage.project_store import canonical,digest
from packages.domain.acceptance import history as contracts
from packages.domain.task_blockers import TaskBlockerService

STAGES=('Backlog','To Do','In Progress','In Review','Awaiting Verification','Done')
TRANSITIONS={'Backlog':{'To Do'},'To Do':{'Backlog','In Progress'},'In Progress':{'In Review'},'In Review':{'In Progress','Awaiting Verification'},'Awaiting Verification':{'In Progress','In Review','Done'},'Done':{'In Progress'}}
RESULTS={'passed','failed','pending','not_run','unknown'}

class TaskWorkflowService:
    def __init__(self,core):self.core=core
    def _task(self,project,task):
        identifier(task)
        row=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
        if not row or json.loads(row[1])['type']!='Task':raise ContractError('task_unavailable','Task unavailable.')
        return dict(id=task,version=row[0],body=json.loads(row[1]))
    def _rows(self,project,task,action):
        # Only the current owned read snapshot may reuse audit data. Writes and
        # later queries always read current rows; authority checks remain intact.
        cache=getattr(self.core,'workflow_audit_read_cache',None)
        key=(project,action)
        if cache is not None and key in cache:return copy.deepcopy(cache[key].get(task,[]))
        groups={}
        for seq,actor,raw in self.core.db.execute('SELECT seq,actor,ref FROM audit WHERE workspace=? AND project=? AND action=? ORDER BY seq',(self.core.workspace,project,action)):
            value=json.loads(raw);groups.setdefault(value['task'],[]).append(dict(sequence=seq,actor=actor,**value))
        if cache is not None:cache[key]=groups
        return copy.deepcopy(groups.get(task,[]))
    def _save(self,scope,project,action,value):
        count=self.core.db.execute("SELECT count(*) FROM audit WHERE workspace=? AND project=? AND action IN ('task_stage','criterion_evidence')",(self.core.workspace,project)).fetchone()[0]
        if count>=2048:raise ContractError('workflow_history_limit','Local workflow history limit reached; existing records remain intact.')
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,canonical(value)))
    def _verification(self,project,task):
        record=self._task(project,task);cs=contracts(self.core,project,task);contract=cs[-1] if cs else None
        evidence=sorted(self._rows(project,task,'criterion_evidence')+self._rows(project,task,'file_criterion_evidence'),key=lambda r:r['sequence']);rows=[]
        if contract:
            for criterion in contract['contract']['criteria']+contract['contract']['dod']:
                candidates=[e for e in evidence if e['criterion']==criterion['id']]
                latest=candidates[-1] if candidates else None
                file_unknown=False
                current=bool(latest and latest['task_version']==record['version'] and latest['contract_version']==contract['version'])
                if current and criterion['method']=='file_check':
                    from packages.verification.files import FileVerificationService
                    file_state=FileVerificationService(self.core).current(project,task,criterion['id'],latest) if latest.get('authority')=='local_file_observer' else False
                    file_unknown=file_state is None;current=file_state is True
                result='unknown' if file_unknown else 'stale' if latest and not current else latest['status'] if current else 'not_run'
                rows.append(dict(criterion,status=result,evidence=latest))
        stale=bool(contract and contract['contract']['task_version']!=record['version'])
        required=[r for r in rows if r['required'] and r['applicable']]
        # No vacuous Done: at least one applicable required acceptance/DoD item.
        passed=bool(contract and not stale and required and all(r['status']=='passed' for r in required))
        return dict(contract_version=contract['version'] if contract else 0,stale=stale,results=rows,passed=passed,history=evidence)
    def _context_component(self,project,task):
        cache=getattr(self.core,'workflow_context_cache',{})
        if project not in cache:
            edges=self.core.db.execute('SELECT origin,target,kind,revision,state,valid_from,valid_to FROM edges WHERE workspace=? AND project=? LIMIT 1001',(self.core.workspace,project)).fetchall()
            rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? LIMIT 2001',(self.core.workspace,project)).fetchall()
            complete=len(edges)<=1000 and len(rows)<=2000
            cache[project]=dict(complete=complete,edges=edges,records={rid:[version,digest(body)] for rid,version,body in rows})
            self.core.workflow_context_cache=cache
        data=cache[project]
        if not data['complete']:return dict(complete=False,records=[],relations=[],knowledge_revision=self.core.db.execute('SELECT knowledge_revision FROM projects WHERE workspace=? AND id=?',(self.core.workspace,project)).fetchone()[0])
        reached={task};pending=[task];out={};replacement={}
        for e in data['edges']:
            if e[4]=='asserted':
                out.setdefault(e[0],[]).append(e[1])
                if e[2]=='supersedes':replacement.setdefault(e[1],[]).append(e[0])
        while pending:
            rid=pending.pop()
            for neighbor in out.get(rid,[])+replacement.get(rid,[]):
                if neighbor not in reached:reached.add(neighbor);pending.append(neighbor)
        relations=sorted(e for e in data['edges'] if e[0] in reached or e[2]=='supersedes' and e[1] in reached)
        return dict(complete=True,records=[dict(id=rid,record=data['records'].get(rid)) for rid in sorted(reached)],relations=relations)
    def _legacy_context_changed(self,project,task,done):
        context=self._context_component(project,task)
        if not context['complete']:return True
        reached={r['id'] for r in context['records']}
        for approval, in self.core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='apply' AND seq>?",(self.core.workspace,project,done['sequence'])).fetchall():
            command=self.core.db.execute('SELECT command_key FROM approvals WHERE id=? AND workspace=? AND project=?',(approval,self.core.workspace,project)).fetchone()
            if not command:continue
            result=self.core.db.execute('SELECT result FROM commands WHERE workspace=? AND project=? AND key=?',(self.core.workspace,project,command[0])).fetchone()
            if not result:continue
            for seq in json.loads(result[0])['event_sequences']:
                row=self.core.db.execute('SELECT payload FROM events WHERE workspace=? AND project=? AND seq=?',(self.core.workspace,project,seq)).fetchone()
                if not row:continue
                op=json.loads(row[0])
                if op['op'] in ('link','end_link'):
                    if op['origin'] in reached or op['kind']=='supersedes' and op['target'] in reached:return True
                elif op.get('id',op.get('task')) in reached:return True
        return False
    def _completion_basis(self,project,task,*,legacy=False):
        from packages.domain.questions import QuestionService
        dependencies=[]
        for target,revision in self.core.db.execute("SELECT target,revision FROM edges WHERE workspace=? AND project=? AND origin=? AND kind='depends_on' AND state='asserted' ORDER BY target",(self.core.workspace,project,task)):
            row=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,target)).fetchone()
            dependencies.append(dict(target=target,revision=revision,record=list(row) if row else None,stages=self._rows(project,target,'task_stage'),evidence=self._rows(project,target,'criterion_evidence'),contracts=contracts(self.core,project,target)))
        questions=[q for q in QuestionService(self.core)._view(project)['questions'] if q.get('task')==task]
        value=dict(record=self._task(project,task),contracts=contracts(self.core,project,task),evidence=self._rows(project,task,'criterion_evidence'),blocker=TaskBlockerService(self.core)._view(project,task),dependencies=dependencies,questions=questions,question_resolutions=[json.loads(raw) for raw, in self.core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='question_decision_applied'",(self.core.workspace,project)) if json.loads(raw).get('question') in {q['id'] for q in questions}])
        if not legacy:value.update(context_component=self._context_component(project,task),evidence=value['evidence']+self._rows(project,task,'file_criterion_evidence'),file_bindings=self._rows(project,task,'file_criterion_binding'))
        return digest(canonical(value))

    def _stage(self,project,task):
        record=self._task(project,task);rows=self._rows(project,task,'task_stage')
        lifecycle=self.core.db.execute("SELECT version,payload FROM events WHERE workspace=? AND project=? AND stream=? AND kind='task_lifecycle' ORDER BY seq DESC LIMIT 1",(self.core.workspace,project,task)).fetchone()
        floor=lifecycle[0] if lifecycle else 0
        current=[r for r in rows if r['task_version']>=floor]
        stage=current[-1]['stage'] if current else 'To Do'
        origin='workflow' if current else 'legacy_default'
        if not current and not lifecycle:
            starts=self._rows(project,task,'task_work_started')
            if starts:stage='In Progress';origin='legacy_start'
        if record['body'].get('execution')=='cancelled':stage='Cancelled';origin='lifecycle'
        elif not current and lifecycle:origin='lifecycle_reopened'
        verification=self._verification(project,task)
        # New evidence failure or changed task/contract invalidates CURRENT success.
        if stage=='Done' and (not verification['passed'] or current[-1]['contract_version']!=verification['contract_version'] or current[-1].get('completion_basis')!=self._completion_basis(project,task,legacy=current[-1].get('format')=='decivora-task-stage-1') or current[-1].get('format')=='decivora-task-stage-1' and self._legacy_context_changed(project,task,current[-1])):stage='Awaiting Verification';origin='completion_stale'
        return dict(stage=stage,revision=len(rows),origin=origin,history=rows,verification=verification)
    def _assessment(self,project,task):
        record=self._task(project,task);manual=TaskBlockerService(self.core)._view(project,task);blockers=[]
        if manual['blocked']:
            c=manual['current'];blockers.append(dict(kind=c.get('waiting_kind','manual'),gate=c.get('gate','both'),reason=c['reason'],next_action=c['next_action'],owner=c.get('owner','unassigned'),source='manual_human',since=c['recorded_at']))
        dependencies=[]
        for target,revision in self.core.db.execute("SELECT target,revision FROM edges WHERE workspace=? AND project=? AND origin=? AND kind='depends_on' AND state='asserted'",(self.core.workspace,project,task)):
            try:
                other=self._task(project,target);passed=self._verification(project,target)['passed'] and self._stage(project,target)['stage']=='Done'
                item=dict(id=target,title=other['body']['title'],revision=revision,status='satisfied' if passed else 'pending',gate='finish')
            except ContractError:item=dict(id=target,revision=revision,status='unknown',gate='finish')
            dependencies.append(item)
            if item['status']!='satisfied':blockers.append(dict(kind='dependency',gate='finish',reason='Prerequisite has no current verified completion.',next_action='Review the linked prerequisite.',owner='unassigned',source=target,status=item['status']))
        from packages.domain.questions import QuestionService
        applied={json.loads(raw)['id'] for raw, in self.core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='question_decision_applied'",(self.core.workspace,project))}
        resolved={(json.loads(raw)['question'],json.loads(raw)['revision']) for raw, in self.core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='question_decision_proposed'",(self.core.workspace,project)) if json.loads(raw)['id'] in applied}
        for q in QuestionService(self.core)._view(project)['questions']:
            if q.get('task')==task and (q['status'] in ('Open','Deferred') or q['status']=='Answered' and (q['id'],q['revision']) not in resolved):
                blockers.append(dict(kind='approval' if q['status']=='Answered' else 'decision',gate='finish',reason=q['text'],next_action='Approve and apply the linked decision.' if q['status']=='Answered' else 'Answer the linked decision question.',owner='unassigned',source=q['id']))
        blocks=[r[0] for r in self.core.db.execute("SELECT origin FROM edges WHERE workspace=? AND project=? AND target=? AND kind='depends_on' AND state='asserted'",(self.core.workspace,project,task))]
        if not self._context_component(project,task)['complete']:blockers.append(dict(kind='context',gate='finish',reason='Recorded context exceeds local assessment bounds.',next_action='Review or narrow context before completion.',owner='unassigned',source='recorded_context_limit'))
        start=any(b['gate'] in ('start','both') for b in blockers);finish=any(b["gate"] in ("finish","both") for b in blockers)
        return dict(blocked=bool(blockers),start_blocked=start,finish_blocked=finish,blockers=blockers,dependencies=dependencies,blocks=blocks,readiness='Blocked' if start else 'Needs Review' if dependencies and any(d['status']=='unknown' for d in dependencies) else 'Ready' if contracts(self.core,project,task) and not self._verification(project,task)['stale'] else 'Needs Review',coverage='recorded_relations_only')
    def view(self,scope,project,task):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            return dict(self._stage(project,task),assessment=self._assessment(project,task))
    def transition(self,scope,project,*,task,task_version,base_revision,stage,reason,key,scope_reviewed=False):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);identifier(key)
            if stage not in STAGES or type(scope_reviewed) is not bool or type(task_version) is not int or type(base_revision) is not int:raise ContractError('invalid_workflow','Typed workflow state and revision required.')
            if type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('invalid_workflow','Explicit transition reason required.')
            request=dict(task=task,task_version=task_version,base_revision=base_revision,stage=stage,reason=reason,key=key,scope_reviewed=scope_reviewed)
            rows=self._rows(project,task,'task_stage');old=next((r for r in rows if r['key']==key),None)
            if old:
                if old['actor']!=scope.principal_id or old['request_digest']!=digest(canonical(request)):raise ContractError('idempotency_conflict','Workflow identity was reused.')
                return self.view(scope,project,task)
            record=self._task(project,task);current=self._stage(project,task)
            if record['version']!=task_version or current['revision']!=base_revision:raise ContractError('stale_workflow','Task or workflow changed; refresh.')
            if stage not in TRANSITIONS.get(current['stage'],set()):raise ContractError('invalid_transition','This workflow transition is not available.')
            verification=current['verification'];assessment=self._assessment(project,task)
            if stage=='In Progress':
                if not verification['contract_version'] or verification['stale']:raise ContractError('acceptance_required','Approve current acceptance criteria before starting work.')
                if assessment['start_blocked']:raise ContractError('task_blocked','Resolve start-gate impediments first.')
            if stage=='Done':
                if not verification['passed']:raise ContractError('verification_required','All required current AC/DoD evidence must pass.')
                if assessment['finish_blocked']:raise ContractError('task_blocked','Resolve completion-gate impediments first.')
                if not scope_reviewed:raise ContractError('scope_review_required','Explicit current scope/impact review acknowledgment required.')
            self._save(scope,project,'task_stage',dict(task=task,task_version=task_version,stage=stage,revision=base_revision+1,reason=reason,key=key,request_digest=digest(canonical(request)),contract_version=verification['contract_version'],recorded_at=time.time(),format='decivora-task-stage-2',basis_version=2,completion_basis=self._completion_basis(project,task) if stage=='Done' else None))
            return self.view(scope,project,task)
    def evidence(self,scope,project,*,task,task_version,contract_version,criterion,status,reference,note,key):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);identifier(key);identifier(criterion)
            if status not in RESULTS or type(task_version) is not int or type(contract_version) is not int:raise ContractError('invalid_evidence','Typed evidence status and versions required.')
            for value in (reference,note):
                if type(value) is not str or not value.strip() or len(value)>1024:raise ContractError('invalid_evidence','Bounded evidence reference and observation note required.')
            request=dict(task=task,task_version=task_version,contract_version=contract_version,criterion=criterion,status=status,reference=reference,note=note,key=key)
            old=next((r for r in self._rows(project,task,'criterion_evidence') if r['key']==key),None)
            if old:
                if old['actor']!=scope.principal_id or old['request_digest']!=digest(canonical(request)):raise ContractError('idempotency_conflict','Evidence identity was reused.')
                return self.view(scope,project,task)
            record=self._task(project,task);v=self._verification(project,task)
            if record['body'].get('execution')=='cancelled' or self._stage(project,task)['stage'] not in ('In Review','Awaiting Verification','Done'):raise ContractError('evidence_stage_required','Evidence review requires an implementation handoff.')
            if record['version']!=task_version or v['contract_version']!=contract_version or v['stale']:raise ContractError('stale_evidence','Evidence must bind current task and acceptance revisions.')
            row=next((r for r in v['results'] if r['id']==criterion),None)
            if row is None or row['method']!='human_review':raise ContractError('verifier_required','This endpoint only supports explicitly authorized human-review criteria; automatic/file runner is not enabled.')
            self._save(scope,project,'criterion_evidence',dict(request,request_digest=digest(canonical(request)),recorded_at=time.time(),authority='local_human_review',format='decivora-criterion-evidence-1'))
            return self.view(scope,project,task)

"""Human-selected decision retirement hypothesis; persisted review with separately approved task changes."""
import json
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.domain.task_workflow import TaskWorkflowService

class DecisionImpactService:
    def __init__(self,core):self.core=core
    def preview(self,scope,project,*,decision,decision_version,base_revision,key,rationale_tasks=None,decision_active=False):
        identifier(decision);identifier(key)
        if type(decision_version) is not int or type(base_revision) is not int:raise ContractError('invalid_request','Typed snapshot revisions required.')
        if type(decision_active) is not bool or rationale_tasks is not None and (type(rationale_tasks) is not list or len(rationale_tasks)>16):raise ContractError('invalid_rationale','Bounded explicit rationale task revisions required.')
        rationale_tasks=[] if rationale_tasks is None else rationale_tasks
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            if self.core.project(scope,project)['knowledge_revision']!=base_revision:raise ContractError('stale_base','Refresh the selected decision context.')
            rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 1001',(self.core.workspace,project)).fetchall()
            if len(rows)>1000:raise ContractError('impact_limit','Decision preview exceeds the local record limit.')
            records={rid:(version,json.loads(body)) for rid,version,body in rows}
            selected=records.get(decision)
            if not selected or selected[1]['type']!='Decision' or selected[0]!=decision_version:raise ContractError('stale_trigger','Selected decision revision unavailable.')
            confirmed=set()
            for item in rationale_tasks:
                if type(item) is not dict or set(item)!={'task','task_version'} or type(item['task_version']) is not int:raise ContractError('invalid_rationale','Exact task revision required.')
                task=identifier(item['task']);record=records.get(task)
                if task in confirmed or not record or record[1]['type']!='Task' or record[0]!=item['task_version']:raise ContractError('invalid_rationale','Unique current task revisions required.')
                edge=self.core.db.execute("SELECT 1 FROM edges WHERE workspace=? AND project=? AND origin=? AND target=? AND kind='required_by' AND state='asserted'",(self.core.workspace,project,task,decision)).fetchone()
                if not edge:raise ContractError('invalid_rationale','Confirm only an existing task required_by decision relationship.')
                confirmed.add(task)
            from packages.domain.task_rationale import TaskRationaleService
            rationale_service=TaskRationaleService(self.core)
            stored={rid:rationale_service.view(scope,project,rid) for rid,(version,body) in records.items() if body['type']=='Task'}
            # Conflicting explicit facts across tasks are unknown, never last-write-wins.
            fact_values={}
            for value in stored.values():
                if value and not value['stale']:
                    for ref,fact in value['facts'].items():fact_values.setdefault(ref,set()).add(fact['valid'])
            annotations={};before={};after={}
            workflow=TaskWorkflowService(self.core)
            for rid,(version,body) in records.items():
                if body['type']=='Task':
                    rationale=stored[rid];expression=rationale['expression'] if rationale and not rationale['stale'] else dict(any=[dict(ref=decision,revision=decision_version)]) if rid in confirmed and rationale is None else None
                    annotations[rid]=dict(version=version,required_when=expression,historically_completed=workflow.view(scope,project,rid)['stage']=='Done',replacement=None)
                else:
                    values=fact_values.get(rid,set());known=next(iter(values)) if len(values)==1 else None
                    before[rid]=dict(revision=version,valid=not decision_active if rid==decision else known)
                    after[rid]=dict(revision=version,valid=decision_active if rid==decision else known)
        # Knowledge/authority/record/source guards are rechecked in the persisted
        # preview transaction. No inferred AND/OR justification or mutation.
        return self.core.impact_preview(scope,project,key,dict(record=decision,version=decision_version,kind='decision_approved' if decision_active else 'decision_superseded'),annotations,before,after,expected_revision=base_revision)

    def prepare_task_updates(self,scope,project,*,key,impact_run,updates):
        """Human-edited scope changes; preview never supplies guessed cancellation."""
        from packages.domain.review import ReviewService
        identifier(key);identifier(impact_run)
        if type(updates) is not list or not 1<=len(updates)<=16:raise ContractError('invalid_update','Select one to sixteen explicit task edits.')
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            impact=self.core.impact_run(scope,project,impact_run)
            if impact['stale']:raise ContractError('stale_impact','Refresh the impact before proposing task edits.')
            affected={p['record'] for p in impact['result']['proposals']};seen=set();groups=[]
            for index,update in enumerate(updates):
                if type(update) is not dict or set(update)!={'task','task_version','description'}:raise ContractError('invalid_update','Exact task revision and proposed description required.')
                task=identifier(update['task'])
                if task in seen or task not in affected:raise ContractError('invalid_update','A unique affected task must be selected.')
                seen.add(task)
                if type(update['task_version']) is not int or type(update['description']) is not str or not update['description'].strip() or len(update['description'])>8192:raise ContractError('invalid_update','Bounded task scope and typed revision required.')
                record=TaskWorkflowService(self.core)._task(project,task)
                if record['version']!=update['task_version']:raise ContractError('stale_record','Task changed after the impact preview.')
                if record['body'].get('execution')=='cancelled':raise ContractError('task_cancelled','Reopening requires a separate lifecycle review.')
                if record['body']['description']==update['description']:raise ContractError('unchanged_scope','Change the proposed scope before preparing a review.')
                groups.append(dict(id='edit_'+str(index+1),depends_on=[],records=[task],operations=[dict(op='update',id=task,base_version=record['version'],body=dict(record['body'],description=update['description']))]))
        # ReviewService rechecks the current impact snapshot in its own write TX.
        return ReviewService(self.core).create(scope,project,key,impact_run,groups)

    def prepare_lifecycle(self,scope,project,*,key,impact_run,tasks,state,reason):
        """Explicit lifecycle proposals use the existing current-impact review gate."""
        from packages.domain.review import ReviewService
        identifier(key);identifier(impact_run)
        if state not in ('cancelled','todo') or type(reason) is not str or not reason.strip() or len(reason)>1024 or type(tasks) is not list or not 1<=len(tasks)<=16:raise ContractError('invalid_lifecycle','Bounded task selection, state and explicit reason required.')
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            impact=self.core.impact_run(scope,project,impact_run)
            if impact['stale'] or impact['result']['coverage']!='complete_snapshot':raise ContractError('stale_impact','Complete current impact required before lifecycle review.')
            proposals={p['record']:p for p in impact['result']['proposals']};seen=set();ops=[]
            for item in tasks:
                if type(item) is not dict or set(item)!={'task','task_version'} or type(item['task_version']) is not int:raise ContractError('invalid_lifecycle','Exact task revision required.')
                task=identifier(item['task']);record=TaskWorkflowService(self.core)._task(project,task);proposal=proposals.get(task)
                if task in seen or record['version']!=item['task_version'] or not proposal or proposal['record_version']!=record['version']:raise ContractError('stale_record','Unique affected current task revisions required.')
                seen.add(task)
                if proposal['preserve_historical_completion'] or (state=='cancelled' and (record['body'].get('execution')=='cancelled' or proposal['action']!='obsolete_candidate' or proposal['after'] is not False)) or (state=='todo' and (record['body'].get('execution')!='cancelled' or proposal['after'] is not True)):raise ContractError('lifecycle_review','Explicit obsolete proof or valid reopening rationale required.')
                ops.append(dict(op='task_lifecycle',id=task,base_version=record['version'],state=state,reason=reason,impact_run=impact_run))
            groups=[dict(id='lifecycle',depends_on=[],records=sorted(seen),operations=ops)]
        return ReviewService(self.core).create(scope,project,key,impact_run,groups)

    def reviews(self,scope,project):
        from packages.domain.review import ReviewService,_rows
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            service=ReviewService(self.core);packets=_rows(self.core,project,'review_created')[-8:]
            selections=_rows(self.core,project,'review_selected');approvals=_rows(self.core,project,'review_approved');applied=_rows(self.core,project,'review_applied');decisions=_rows(self.core,project,'review_decision');result=[]
            for packet in packets:
                events=[r for r in decisions if r['packet']==packet['id']]
                chosen=next((r for r in reversed(selections) if r['packet']==packet['id'] and r['decision_revision']==len(events)),None)
                done=next((r for r in applied if r['packet']==packet['id']),None)
                approval=next((r for r in approvals if chosen and r['id']==chosen['id']),None)
                stale=False
                try:service._current(scope,project,packet)
                except ContractError:stale=True
                state='Applied' if done else 'Rejected' if events and events[-1]['action']=='reject' else 'Stale' if stale else 'Approved' if approval else 'Selected' if chosen else 'Deferred' if events and events[-1]['action']=='defer' else 'Prepared'
                original_scopes={}
                for group in packet['groups']:
                    for op in group['operations']:
                        if op.get('op')!='update':continue
                        row=self.core.db.execute("SELECT payload FROM events WHERE workspace=? AND project=? AND stream=? AND version<=? AND kind IN ('create','update') ORDER BY version DESC LIMIT 1",(self.core.workspace,project,op['id'],op['base_version'])).fetchone()
                        original_scopes[op['id']]=json.loads(row[0])['body']['description'] if row else None
                result.append(dict(packet=packet,state=state,original_scopes=original_scopes,selection=chosen['id'] if chosen else None,selected=chosen['groups'] if chosen else [],approval=approval['approval'] if approval else None,result=done['result'] if done else None))
            return result

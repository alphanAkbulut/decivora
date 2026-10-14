"""Human-selected decision retirement hypothesis; persisted review, never cancellation."""
import json
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.domain.task_workflow import TaskWorkflowService

class DecisionImpactService:
    def __init__(self,core):self.core=core
    def preview(self,scope,project,*,decision,decision_version,base_revision,key):
        identifier(decision);identifier(key)
        if type(decision_version) is not int or type(base_revision) is not int:raise ContractError('invalid_request','Typed snapshot revisions required.')
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            if self.core.project(scope,project)['knowledge_revision']!=base_revision:raise ContractError('stale_base','Refresh the selected decision context.')
            rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 1001',(self.core.workspace,project)).fetchall()
            if len(rows)>1000:raise ContractError('impact_limit','Decision preview exceeds the local record limit.')
            records={rid:(version,json.loads(body)) for rid,version,body in rows}
            selected=records.get(decision)
            if not selected or selected[1]['type']!='Decision' or selected[0]!=decision_version:raise ContractError('stale_trigger','Selected decision revision unavailable.')
            annotations={};before={};after={}
            workflow=TaskWorkflowService(self.core)
            for rid,(version,body) in records.items():
                if body['type']=='Task':
                    annotations[rid]=dict(version=version,required_when=None,historically_completed=workflow.view(scope,project,rid)['stage']=='Done',replacement=None)
                else:
                    before[rid]=dict(revision=version,valid=True if rid==decision else None)
                    after[rid]=dict(revision=version,valid=False if rid==decision else None)
        # Knowledge/authority/record/source guards are rechecked in the persisted
        # preview transaction. No inferred AND/OR justification or mutation.
        return self.core.impact_preview(scope,project,key,dict(record=decision,version=decision_version,kind='decision_superseded'),annotations,before,after,expected_revision=base_revision)

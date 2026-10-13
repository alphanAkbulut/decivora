"""Versioned AC/DoD contracts; human changes are explicit, results stay not_run."""
import json
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest

METHODS={'automatic_test','file_check','human_review'}
def stream(task):return 'acceptance_'+digest(task)[:24]

def validate(op):
    from packages.storage.workspace import integer
    if type(op) is not dict or set(op)!={'op','task','task_version','base_contract','criteria','dod','reason','acknowledged_changes'} or op['op']!='acceptance_contract':raise ContractError('invalid_acceptance','Exact versioned acceptance fields required.')
    identifier(op['task']);integer(op['task_version'],1);integer(op['base_contract'])
    if type(op['reason']) is not str or not op['reason'].strip() or len(op['reason'])>1024:raise ContractError('invalid_acceptance','Explicit bounded approval/change reason required.')
    ids=set()
    for key,limit in (('criteria',32),('dod',16)):
        if type(op[key]) is not list or not 1<=len(op[key])<=limit:raise ContractError('invalid_acceptance','Nonempty bounded AC and DoD required.')
        for row in op[key]:
            if type(row) is not dict or set(row)!={'id','statement','method','required','applicable','applicability_reason'}:raise ContractError('invalid_acceptance','Exact criterion fields required.')
            rid=identifier(row['id'])
            if rid in ids:raise ContractError('invalid_acceptance','Criterion IDs must be unique across AC and DoD.')
            ids.add(rid)
            if type(row['statement']) is not str or not row['statement'].strip() or len(row['statement'])>512 or row['method'] not in METHODS or type(row['required']) is not bool or type(row['applicable']) is not bool or type(row['applicability_reason']) is not str or len(row['applicability_reason'])>512:
                raise ContractError('invalid_acceptance','Typed statement/method/applicability required.')
            if not row['applicable'] and not row['applicability_reason'].strip():raise ContractError('invalid_acceptance','Not applicable requires an explicit reason.')
    if type(op['acknowledged_changes']) is not list or len(op['acknowledged_changes'])>48 or any(type(v) is not str for v in op['acknowledged_changes']) or len(set(op['acknowledged_changes']))!=len(op['acknowledged_changes']):raise ContractError('invalid_acceptance','Unique acknowledged changed criterion IDs required.')

def history(core,project,task):
    return [dict(sequence=seq,version=version,contract=json.loads(raw)) for seq,version,raw in core.db.execute("SELECT seq,version,payload FROM events WHERE workspace=? AND project=? AND stream=? AND kind='acceptance_contract' ORDER BY seq",(core.workspace,project,stream(task)))]

def check(core,project,op):
    validate(op)
    row=core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,project,op['task'])).fetchone()
    if row is None or row[0]!=op['task_version'] or json.loads(row[1])['type']!='Task':raise ContractError('stale_task','Acceptance must bind the current Task version.')
    old=history(core,project,op['task'])
    if (old[-1]['version'] if old else 0)!=op['base_contract']:raise ContractError('stale_acceptance','Acceptance revision changed.')
    if old:
        before={r['id']:r for r in old[-1]['contract']['criteria']+old[-1]['contract']['dod']}
        after={r['id']:r for r in op['criteria']+op['dod']}
        changed={rid for rid,r in before.items() if after.get(rid)!=r}
        if not changed.issubset(set(op['acknowledged_changes'])):raise ContractError('acceptance_diff_required','Changed/removed criteria require explicit diff acknowledgment.')
    return op['base_contract']+1

class AcceptanceService:
    def __init__(self,core):self.core=core
    def view(self,scope,project,task):
        identifier(task)
        with self.core.read_snapshot():
            self.core.scope(scope,project)
            row=self.core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
            if row is None or json.loads(row[1])['type']!='Task':raise ContractError('task_unavailable','Task unavailable.')
            rows=history(self.core,project,task);latest=rows[-1] if rows else None
            return dict(task=task,history=rows,current=latest,stale=bool(latest and latest['contract']['task_version']!=row[0]),results=[dict(id=r['id'],status='not_run') for r in latest['contract']['criteria']+latest['contract']['dod']] if latest else [],completed=False)
    def start(self,scope,project,task):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            from packages.domain.task_blockers import TaskBlockerService
            if TaskBlockerService(self.core)._view(project,task)['blocked']:raise ContractError('task_blocked','Resolve the recorded impediment before starting work.')
            contract=self.view(scope,project,task)
            if contract['current'] is None or contract['stale']:raise ContractError('acceptance_required','Approve current acceptance criteria before starting work.')
            row=self.core.db.execute('SELECT body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
            if json.loads(row[0]).get('execution')=='cancelled':raise ContractError('task_cancelled','Cancelled task cannot start.')
            ref=canonical(dict(task=task,contract_version=contract['current']['version'],task_version=contract['current']['contract']['task_version']))
            if not self.core.db.execute("SELECT 1 FROM audit WHERE workspace=? AND project=? AND action='task_work_started' AND ref=?",(self.core.workspace,project,ref)).fetchone():
                self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'task_work_started',ref))
            return dict(implementation_claim='in_progress',completed=False)

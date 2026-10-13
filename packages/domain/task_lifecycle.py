"""Explicit Task cancellation/reopening guards; history and edges are preserved."""
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError


def operation(op):
    from packages.storage.workspace import integer
    if type(op) is not dict or set(op)!={'op','id','base_version','state','reason','impact_run'} or op['op']!='task_lifecycle':
        raise ContractError('invalid_lifecycle','Exact revision-bound lifecycle operation required.')
    identifier(op['id']);identifier(op['impact_run']);integer(op['base_version'],1)
    if op['state'] not in ('cancelled','todo') or type(op['reason']) is not str or not op['reason'].strip() or len(op['reason'])>1024:
        raise ContractError('invalid_lifecycle','Explicit state and bounded reason required.')


def transition(body,op):
    operation(op)
    if body.get('type')!='Task':raise ContractError('invalid_lifecycle','Only a Task can change execution state.')
    old=body.get('execution','todo')
    if (old,op['state']) not in (('todo','cancelled'),('cancelled','todo')):
        raise ContractError('invalid_lifecycle','Lifecycle transition does not match current task state.')
    return dict(body,execution=op['state'])


def guard(core,project,operations,bound):
    import json
    from packages.domain.review import ReviewService
    requested=[op for op in operations if type(op) is dict and op.get('op')=='task_lifecycle']
    if not requested:return
    if bound is None:raise ContractError('review_approval_required','Task lifecycle requires a separately approved current impact review.')
    service=ReviewService(core);selection=service._load(project,'review_selected',bound['id'])
    packet=service._load(project,'review_created',selection['packet'])
    impact=core._impact_run(project,packet['impact_run'])['result']
    if impact['coverage']!='complete_snapshot':raise ContractError('incomplete_impact','Incomplete impact cannot authorize task lifecycle.')
    proposals={p['record']:p for p in impact['proposals']}
    for op in requested:operation(op)
    cancelled={op['id'] for op in requested if op['state']=='cancelled'}
    for op in requested:
        operation(op)
        row=core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,project,op['id'])).fetchone()
        if row is None or row[0]!=op['base_version']:raise ContractError('stale_record','Task version changed.')
        transition(json.loads(row[1]),op)
        if op['state']=='cancelled':
            from packages.domain.task_workflow import TaskWorkflowService
            if TaskWorkflowService(core)._stage(project,op['id'])['stage']=='Done':raise ContractError('lifecycle_review','Verified current completion must not be relabeled as cancellation.')
        proposal=proposals.get(op['id'])
        if op['impact_run']!=packet['impact_run'] or proposal is None or proposal['record_version']!=op['base_version'] or proposal['preserve_historical_completion']:
            raise ContractError('invalid_lifecycle','Task transition is not bound to its current impact proposal.')
        changed_facts={v.get('id') for v in operations if type(v) is dict and v.get('op') in ('update','task_lifecycle')}
        if any(v['ref'] in changed_facts for v in proposal.get('justification_facts',[])):
            raise ContractError('lifecycle_review','The same command changes a rationale revision; apply that change and prepare a fresh impact first.')
        if op['state']=='todo':
            if proposal['after'] is not True:raise ContractError('lifecycle_review','Reopening requires an explicitly valid current rationale.')
            continue
        if proposal['action']!='obsolete_candidate' or proposal['after'] is not False:
            raise ContractError('lifecycle_review','Cancellation requires a complete obsolete candidate, not a missing rationale.')
        facts={v['ref']:v['valid'] for v in proposal.get('justification_facts',[])}
        reason_edges=core.db.execute("SELECT target,kind FROM edges WHERE workspace=? AND project=? AND origin=? AND state='asserted' AND kind IN ('required_by','implements','part_of')",(core.workspace,project,op['id'])).fetchall()
        reason_edges.extend((v.get('target'),v.get('kind')) for v in operations if type(v) is dict and v.get('op')=='link' and v.get('origin')==op['id'] and v.get('kind') in ('required_by','implements','part_of'))
        for target,kind in reason_edges:
            if kind=='part_of':
                parent=core.db.execute('SELECT body FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,project,target)).fetchone()
                if target not in cancelled and (parent is None or json.loads(parent[0]).get('execution')!='cancelled'):
                    raise ContractError('lifecycle_blocker','A current parent still requires this child task.')
            elif facts.get(target) is not False:
                raise ContractError('lifecycle_blocker','An active or unknown requirement is outside the false-rationale proof.')
        downstream=core.db.execute("SELECT e.origin,r.body FROM edges e JOIN records r ON r.workspace=e.workspace AND r.project=e.project AND r.id=e.origin WHERE e.workspace=? AND e.project=? AND e.target=? AND e.kind='depends_on' AND e.state='asserted'",(core.workspace,project,op['id'])).fetchall()
        for v in operations:
            if type(v) is dict and v.get('op')=='link' and v.get('target')==op['id'] and v.get('kind')=='depends_on':
                row=core.db.execute('SELECT body FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,project,v['origin'])).fetchone()
                downstream.append((v['origin'],row[0] if row else '{}'))
        for origin,body in downstream:
            if origin not in cancelled and json.loads(body).get('execution')!='cancelled':
                raise ContractError('lifecycle_blocker','A current downstream task still depends on this task.')

"""First-task human scope review; no invented acceptance or verification."""
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest

def validate(reviews,candidates,selected):
    if type(reviews) is not list or len(reviews)>32:raise ContractError('invalid_acceptance','Bounded first-task reviews required.')
    wanted={cid for cid in selected if cid in candidates and candidates[cid]['type']=='Task' and candidates[cid]['comparison']['recommendation']=='review_new'}
    indexed={}
    for r in reviews:
        if type(r) is not dict or set(r)!={'candidate','mode','criteria','dod','clarification','reason'} or type(r['candidate']) is not str or r['candidate'] not in wanted or r['candidate'] in indexed:raise ContractError('invalid_acceptance','One explicit scope review per new selected Task required.')
        if r['mode'] not in ('approved','clarify') or type(r['reason']) is not str or not 1<=len(r['reason'].strip())<=1024:raise ContractError('invalid_acceptance','Explicit first-task scope mode and reason required.')
        for name,limit in [('criteria',32),('dod',16)]:
            if type(r[name]) is not list or len(r[name])>limit or any(type(s) is not str or not 1<=len(s.strip())<=512 for s in r[name]):raise ContractError('invalid_acceptance','Bounded observable criterion statements required.')
        if type(r['clarification']) is not str or len(r['clarification'])>2048:raise ContractError('invalid_acceptance','Bounded clarification required.')
        if r['mode']=='approved' and (not r['criteria'] or not r['dod'] or r['clarification']):raise ContractError('invalid_acceptance','Both acceptance and completion criteria must be explicitly approved.')
        if r['mode']=='clarify' and (r['criteria'] or r['dod'] or not r['clarification'].strip()):raise ContractError('invalid_acceptance','Missing scope remains a clarification; never a partial acceptance contract.')
        indexed[r['candidate']]=r
    if set(indexed)!=wanted:raise ContractError('invalid_acceptance','Review scope for every new selected Task.')
    return indexed

def apply(core,scope,project,source,key,created,reviews):
    summaries=[];sequences=[]
    for cid,r in reviews.items():
        task=created[cid]
        if r['mode']=='approved':
            def rows(values,prefix):return [dict(id=prefix+str(i+1),statement=s,method='human_review',required=True,applicable=True,applicability_reason='') for i,s in enumerate(values)]
            op=dict(op='acceptance_contract',task=task,task_version=1,base_contract=0,criteria=rows(r['criteria'],'AC'),dod=rows(r['dod'],'DOD'),reason=r['reason'],acknowledged_changes=[])
            plan=core.plan(scope,project,'scope_'+digest(canonical([key,cid]))[:24],[op]);receipt=core._apply(scope,plan,core._approve(scope,plan));sequences.extend(receipt['event_sequences'])
            summaries.append(dict(task=task,mode='approved',contract_version=1,verified=False))
        else:
            from packages.capture.clarifications import ClarificationService
            request=dict(source=source['id'],task=task,text=r['clarification'],reason=r['reason'])
            receipt=dict(id='scope_question_'+digest(canonical(request))[:24],source=source['id'],source_sha256=source['sha256'],task=task,text=r['clarification'],quote=None,start=None,end=None,task_version=1,state='Opened',key='scope_'+digest(canonical([key,cid]))[:24],actor=scope.principal_id,reason=r['reason'],request_digest=digest(canonical(request)),canonical_task_created=False,origin='first_task_human_scope_review')
            ClarificationService(core)._put(scope,project,'clarification_reviewed',receipt)
            summaries.append(dict(task=task,mode='clarify',clarification=receipt['id'],verified=False))
    return dict(items=summaries,event_sequences=sequences)

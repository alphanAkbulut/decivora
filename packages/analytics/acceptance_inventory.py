"""Check evidence references for all 14 MVP criteria, never grant release approval."""
import hashlib
from pathlib import Path
from packages.domain.source_event import ContractError
CRITERIA=tuple('AC-'+str(i).zfill(2) for i in range(1,15))

def template():return dict(format='decivora-acceptance-inventory-1',checks=[dict(id=k,status='not_run',reason='End-to-end acceptance evidence not supplied.',evidence=[]) for k in CRITERIA])

def assess(root,manifest):
    root=Path(root).resolve()
    if type(manifest) is not dict or set(manifest)!={'format','checks'} or manifest['format']!='decivora-acceptance-inventory-1' or type(manifest['checks']) is not list or len(manifest['checks'])!=14:raise ContractError('invalid_acceptance_inventory','Exact 14-criterion evidence inventory required.')
    seen=set();result=[]
    for check in manifest['checks']:
        if type(check) is not dict or set(check)!={'id','status','reason','evidence'} or check['id'] not in CRITERIA or check['id'] in seen or check['status'] not in ('passed','failed','not_run','partial') or type(check['reason']) is not str or not check['reason'].strip() or len(check['reason'])>1024 or type(check['evidence']) is not list or len(check['evidence'])>32:raise ContractError('invalid_acceptance_inventory','Unique bounded checks and explicit result reasons required.')
        seen.add(check['id']);references=[]
        if check['status']=='passed' and not check['evidence']:raise ContractError('evidence_required','A declared pass requires referenced evidence; tests alone do not establish product acceptance.')
        for ref in check['evidence']:
            if type(ref) is not dict or set(ref)!={'path','sha256'} or type(ref['path']) is not str or not ref['path'] or len(ref['path'])>512 or type(ref['sha256']) is not str or len(ref['sha256'])!=64:raise ContractError('invalid_acceptance_inventory','Exact relative evidence path and SHA256 required.')
            relative=Path(ref['path'])
            if relative.is_absolute() or '..' in relative.parts or '\\' in ref['path']:raise ContractError('invalid_acceptance_inventory','Evidence must remain inside the selected repository.')
            target=root/relative
            if any(p.is_symlink() for p in [target,*[root/Path(*relative.parts[:i]) for i in range(1,len(relative.parts))]]):raise ContractError('invalid_acceptance_inventory','Symlink evidence is not allowed.')
            if not target.resolve().is_relative_to(root):raise ContractError('invalid_acceptance_inventory','Evidence escapes repository.')
            if not target.is_file():state='missing'
            elif target.stat().st_size>2097152:state='oversize'
            else:state='current' if hashlib.sha256(target.read_bytes()).hexdigest()==ref['sha256'] else 'stale'
            references.append(dict(path=ref['path'],state=state))
        effective='stale' if any(r['state']!='current' for r in references) else check['status']
        result.append(dict(id=check['id'],declared_status=check['status'],effective_status=effective,evidence=references))
    return dict(format='decivora-acceptance-reference-report-1',checks=result,all_declared_passes_current=all(r['effective_status']=='passed' for r in result),semantic_quality_verified=False,human_acceptance_verified=False,release_authorized=False,model_calls=0,note='Validates reference integrity only. Declared results and human approval must be independently reviewed.')

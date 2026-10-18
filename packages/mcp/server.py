"""Bounded MCP 2025-06-18 stdio subset with pre-provisioned AGENT authority."""
import argparse,base64,hashlib,hmac,json,secrets,sys,time
from pathlib import Path
from packages.storage.workspace import Workspace,TYPES
from packages.storage.project_store import canonical,digest
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
VERSION='2025-06-18'
MAX_LINE=32768
MAX_OUTPUT=16384

def fields(value,required,optional=()):
    if type(value) is not dict or not set(required)<=set(value) or set(value)-set(required)-set(optional):raise ContractError('invalid_arguments','Exact tool fields required.')
def integer(value,lo,hi):
    if type(value) is not int or not lo<=value<=hi:raise ContractError('invalid_arguments','Bounded integer required.')
def schema(properties,required):return dict(type='object',properties=properties,required=required,additionalProperties=False)
S=dict(type='string',minLength=1,maxLength=128)
I=dict(type='integer',minimum=1)
TOOLS=[
 dict(name='get_project_brief',description='Bounded current records, not exhaustive context.',inputSchema=schema(dict(project_id=S,budget=dict(type='integer',minimum=1024,maximum=4096)),['project_id']),annotations=dict(readOnlyHint=True,openWorldHint=False)),
 dict(name='query_records',description='Scoped current record previews with revision-bound cursor.',inputSchema=schema(dict(project_id=S,limit=dict(type='integer',minimum=1,maximum=25),filters=schema(dict(type=dict(enum=sorted(TYPES))),[]),cursor=dict(type=['string','null'])),['project_id']),annotations=dict(readOnlyHint=True,openWorldHint=False)),
 dict(name='get_record',description='Get an exact current record version; no raw SQL.',inputSchema=schema(dict(project_id=S,id=S,revision=I),['project_id','id','revision']),annotations=dict(readOnlyHint=True,openWorldHint=False)),
 dict(name='submit_changeset',description='Persist a create-only draft proposal; human approval and application are separate.',inputSchema=schema(dict(project_id=S,key=S,base_revision=dict(type='integer',minimum=0),operations=dict(type='array',minItems=1,maxItems=16,items=schema(dict(op=dict(enum=['create']),id=S,body=dict(type='object')),['op','id','body']))),['project_id','key','base_revision','operations']),annotations=dict(readOnlyHint=False,destructiveHint=False,openWorldHint=False)),
 dict(name='submit_evidence',description='Record an untrusted agent execution claim, never verified criterion evidence.',inputSchema=schema(dict(project_id=S,key=S,task=S,task_version=I,status=dict(enum=['claimed','failed','unknown']),reference=dict(type='string',minLength=1,maxLength=1024),note=dict(type='string',minLength=1,maxLength=1024)),['project_id','key','task','task_version','status','reference','note']),annotations=dict(readOnlyHint=False,destructiveHint=False,openWorldHint=False))]
class Server:
    def __init__(self,path,workspace,principal):
        self.path=Path(path);identifier(workspace);identifier(principal)
        if not self.path.is_file():raise ContractError('storage_unavailable','An existing selected database is required.')
        self.workspace=workspace;self.principal=principal;self.initialized=False;self.ready=False;self.cursor_key=secrets.token_bytes(32);self.call_window=int(time.monotonic()//60);self.call_count=0
    def _scope(self,core,project,write=False):
        scope=core.authority.issue_scope(self.principal);_,grants=core.authority._current()
        if grants[self.principal]['kind']!='agent':raise ContractError('agent_required','MCP accepts a pre-provisioned agent identity, never a human owner.')
        core.scope(scope,project,write=write);core.active(scope,project);return scope
    def _visible(self,core,scope,project,rid):
        all_cache=getattr(core,'mcp_visibility_cache',{});key=(scope.principal_id,project,core.authority.revision());cache=all_cache.get(key)
        if cache is None:
            blocked={r[0] for r in core.db.execute('SELECT record FROM record_sources WHERE workspace=? AND project=?',(core.workspace,project)).fetchall()}
            for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_candidates_applied'",(core.workspace,project)).fetchall():
                receipt=json.loads(raw);blocked.update(receipt.get('result',{}).get('temp_ids',{}).values())
                for row in receipt.get('attached',[]):
                    for match in row.get('matches',[]):
                        target=match.get('record_id',match.get('id')) if type(match) is dict else match
                        if not target:return False
                        blocked.add(target)
            # Conversation-derived edges inherit source privacy; a public endpoint
            # does not make the private rationale safe for another agent.
            for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_relation_reviewed'",(core.workspace,project)).fetchall():
                receipt=json.loads(raw)
                if receipt.get('state')=='Applied':blocked.update((receipt['origin'],receipt['target']))
            edges=core.db.execute('SELECT origin,target FROM edges WHERE workspace=? AND project=? LIMIT 501',(core.workspace,project)).fetchall()
            if len(edges)>500:return False
            changed=True
            while changed:
                changed=False
                for a,b in edges:
                    if a in blocked or b in blocked:
                        before=len(blocked);blocked.update((a,b));changed=changed or len(blocked)!=before
            all_cache[key]=blocked;core.mcp_visibility_cache=all_cache;cache=blocked
        return rid not in cache
    def _records(self,core,scope,project):
        rows=core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 501',(core.workspace,project)).fetchall()
        return [dict(id=rid,version=v,body=json.loads(raw)) for rid,v,raw in rows[:500] if self._visible(core,scope,project,rid)]
    def _cursor(self,value):
        raw=canonical(value).encode();return base64.urlsafe_b64encode(raw).decode()+'.'+hmac.new(self.cursor_key,raw,hashlib.sha256).hexdigest()
    def _read_cursor(self,token):
        try:
            if type(token) is not str or len(token)>2048:raise ValueError()
            a,b=token.split('.');raw=base64.urlsafe_b64decode(a)
            if not hmac.compare_digest(b,hmac.new(self.cursor_key,raw,hashlib.sha256).hexdigest()):raise ValueError()
            return json.loads(raw)
        except Exception:raise ContractError('stale_cursor','Cursor changed or server restarted; resync.') from None
    def call(self,name,args):
        window=int(time.monotonic()//60)
        if window!=self.call_window:self.call_window=window;self.call_count=0
        if self.call_count>=60:raise ContractError('mcp_rate_limited','Local process tool-call limit reached; no new operation admitted.')
        self.call_count+=1
        names={t['name'] for t in TOOLS}
        if name not in names:raise ContractError('unknown_tool','Tool unavailable.')
        required=next(t['inputSchema']['required'] for t in TOOLS if t['name']==name);optional=next(set(t['inputSchema']['properties'])-set(required) for t in TOOLS if t['name']==name);fields(args,required,optional)
        project=identifier(args['project_id'])
        with Workspace(self.path,self.workspace) as core:
            scope=self._scope(core,project,write=name in ('submit_changeset','submit_evidence'))
            if name=='submit_changeset':
                identifier(args['key']);integer(args['base_revision'],0,9223372036854775807)
                from packages.domain.agent_proposals import AgentProposalService
                plan=AgentProposalService(core).submit(scope,project,key=args['key'],base_revision=args['base_revision'],operations=args['operations'])
                return dict(proposal=plan,approved=False,applied=False,canonical_mutations=0)
            if name=='submit_evidence':
                identifier(args['key']);identifier(args['task']);integer(args['task_version'],1,9223372036854775807)
                if args['status'] not in ('claimed','failed','unknown') or any(type(args[k]) is not str or not args[k].strip() or len(args[k])>1024 for k in ('reference','note')):raise ContractError('invalid_arguments','Bounded untrusted execution claim required.')
                with core.transaction():
                    if not self._visible(core,scope,project,args['task']):raise ContractError('record_unavailable','Record unavailable.')
                    from packages.domain.task_workflow import TaskWorkflowService
                    core.scope(scope,project,write=True);core.active(scope,project);record=TaskWorkflowService(core)._task(project,args['task'])
                    if record['version']!=args['task_version']:raise ContractError('stale_task','Claim must bind the current task.')
                    previous=core.db.execute("SELECT actor,ref FROM audit WHERE workspace=? AND project=? AND action='agent_execution_reported'",(core.workspace,project)).fetchall()
                    signature=digest(canonical(args));old=next((json.loads(raw) for actor,raw in previous if json.loads(raw)['key']==args['key']),None)
                    if old:
                        if old['principal']!=self.principal or old['request_digest']!=signature:raise ContractError('idempotency_conflict','Claim key was reused.')
                        return dict(recorded=True,verified=False,canonical_mutations=0)
                    if len(previous)>=512:raise ContractError('claim_limit','Local claim history limit reached.')
                    core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.workspace,project,self.principal,'agent_execution_reported',canonical(dict(args,principal=self.principal,request_digest=signature,authority='untrusted_agent_report'))))
                    return dict(recorded=True,verified=False,canonical_mutations=0)
            with core.read_snapshot():
                core.scope(scope,project);core.active(scope,project);snapshot=core.project(scope,project)['knowledge_revision'];auth=core.authority.revision()
                if name=='get_record':
                    identifier(args['id']);integer(args['revision'],1,9223372036854775807);row=core.db.execute('SELECT version,body FROM records WHERE workspace=? AND project=? AND id=?',(self.workspace,project,args['id'])).fetchone()
                    if not row or not self._visible(core,scope,project,args['id']):raise ContractError('record_unavailable','Record unavailable.')
                    if row[0]!=args['revision']:raise ContractError('stale_record','Only the exact current record revision is available here.')
                    body=json.loads(row[1]);result=dict(id=args['id'],version=row[0],body=body,knowledge_revision=snapshot,authority_revision=auth)
                    if body['type']=='Task':
                        from packages.domain.task_workflow import TaskWorkflowService
                        current=TaskWorkflowService(core).view(scope,project,args['id']);result['execution_state']=dict(stage=current['stage'],verification_passed=current['verification']['passed'],coverage='recorded_relations_only',file_observation_available=False)
                    return result
                rows=self._records(core,scope,project)
                if name=='query_records':
                    limit=args.get('limit',10);integer(limit,1,25);filters=args.get('filters',{});fields(filters,[],['type'])
                    if filters.get('type') is not None and filters['type'] not in TYPES:raise ContractError('invalid_arguments','Unsupported record type filter.')
                    if filters.get('type'):rows=[r for r in rows if r['body']['type']==filters['type']]
                    after=''
                    if args.get('cursor') is not None:
                        c=self._read_cursor(args['cursor']);expected=dict(workspace=self.workspace,principal=self.principal,project=project,snapshot=snapshot,authority=auth,limit=limit,filters=filters)
                        if {k:c.get(k) for k in expected}!=expected:raise ContractError('stale_cursor','Cursor access or project revision changed.')
                        after=c['after']
                    rows=[r for r in rows if r['id']>after];page=rows[:limit]
                    previews=[dict(id=r['id'],version=r['version'],type=r['body']['type'],title=r['body']['title']) for r in page]
                    cursor=self._cursor(dict(workspace=self.workspace,principal=self.principal,project=project,snapshot=snapshot,authority=auth,limit=limit,filters=filters,after=page[-1]['id'])) if len(rows)>limit else None
                    return dict(records=previews,next_cursor=cursor,knowledge_revision=snapshot,authority_revision=auth,coverage='bounded_authorized_scan_500',coverage_complete=False,raw_sources_included=False)
                budget=args.get('budget',2048);integer(budget,1024,4096)
                brief=dict(project_id=project,knowledge_revision=snapshot,authority_revision=auth,coverage='bounded_authorized_scan_500',context_truncated=True,records=[],raw_sources_included=False)
                for row in rows:
                    item=dict(id=row['id'],version=row['version'],type=row['body']['type'],title=row['body']['title'],description=row['body']['description'][:128],description_truncated=len(row['body']['description'])>128)
                    if len(canonical(dict(brief,records=brief['records']+[item])).encode())>budget:break
                    brief['records'].append(item)
                return brief
    def handle(self,request):
        rid=request.get('id') if type(request) is dict else None
        def error(code,message):return dict(jsonrpc='2.0',id=rid,error=dict(code=code,message=message))
        if type(request) is not dict or request.get('jsonrpc')!='2.0' or type(request.get('method')) is not str or type(rid) not in (str,int,type(None)) or type(rid) is bool:return error(-32600,'Invalid request')
        method=request['method'];params=request.get('params',{})
        if method=='notifications/initialized' and rid is None:
            if self.initialized:self.ready=True
            return None
        if rid is None:return None
        try:
            if method=='initialize':
                if self.initialized:return error(-32600,'Already initialized')
                fields(params,['protocolVersion','capabilities','clientInfo'])
                if type(params['capabilities']) is not dict or type(params['clientInfo']) is not dict:return error(-32602,'Invalid initialize params')
                self.initialized=True;return dict(jsonrpc='2.0',id=rid,result=dict(protocolVersion=VERSION,capabilities=dict(tools=dict(listChanged=False)),serverInfo=dict(name='decivora-local',version='0.1.0')))
            if method=='ping':return dict(jsonrpc='2.0',id=rid,result={})
            if not self.ready:return error(-32000,'Initialization required')
            if method=='tools/list':result=dict(tools=TOOLS)
            elif method=='tools/call':
                fields(params,['name','arguments'],['_meta']);value=self.call(params['name'],params['arguments']);text=canonical(value)
                if len(text.encode())>MAX_OUTPUT:raise ContractError('output_limit','Result exceeds local output limit; request smaller scope.')
                result=dict(content=[dict(type='text',text=text)],isError=False)
            else:return error(-32601,'Method unavailable')
            return dict(jsonrpc='2.0',id=rid,result=result)
        except ContractError as exc:return dict(jsonrpc='2.0',id=rid,result=dict(content=[dict(type='text',text=canonical(dict(error=exc.code,message=str(exc))))],isError=True))
        except Exception:return error(-32602,'Invalid params')
def reject_duplicates(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate')
        result[key]=value
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--database',type=Path,required=True);parser.add_argument('--workspace',required=True);parser.add_argument('--principal',required=True);a=parser.parse_args()
    try:server=Server(a.database,a.workspace,a.principal)
    except ContractError:print('Selected MCP database or identity unavailable.',file=sys.stderr);return 2
    while True:
        line=sys.stdin.buffer.readline(MAX_LINE+1)
        if not line:break
        if len(line)>MAX_LINE or not line.endswith(b'\n'):
            print(canonical(dict(jsonrpc='2.0',id=None,error=dict(code=-32600,message='Input framing limit exceeded'))),flush=True);return 2
        try:r=server.handle(json.loads(line.decode('utf-8'),object_pairs_hook=reject_duplicates,parse_constant=lambda _:(_ for _ in ()).throw(ValueError())))
        except Exception:r=dict(jsonrpc='2.0',id=None,error=dict(code=-32700,message='Parse error'))
        if r is not None:print(canonical(r),flush=True)
    return 0
if __name__=='__main__':raise SystemExit(main())

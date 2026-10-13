"""Runnable local UI. Loopback, ephemeral session, CSRF/origin checks, explicit writes."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
import json,secrets,threading,uuid,webbrowser,argparse,time,sys
from packages.storage.workspace import Workspace
from packages.storage.project_store import canonical
from packages.domain.acceptance import AcceptanceService
from packages.domain.task_blockers import TaskBlockerService
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.questions import QuestionService
from packages.domain.question_decisions import QuestionDecisionService
from packages.domain.source_event import ContractError
from packages.capture.conversations import ConversationService

ROOT=Path(__file__).parent
class LocalApp:
    def __init__(self,path,extractor=None):
        self.extractor=extractor
        self.path=Path(path);fresh=not self.path.exists();self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.cookie=secrets.token_urlsafe(32);self.csrf=secrets.token_urlsafe(32);self.bootstrap=secrets.token_urlsafe(32);self.backup_lock=threading.Lock();self.rate_lock=threading.Lock();self.window=0;self.writes=0
        with Workspace(self.path,'local_ui_workspace',owner='local_owner' if fresh else None) as core:
            if fresh:
                a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=1)
                core.create_project(a.issue_scope('local_owner'),'personal','Benim projem');self.path.chmod(0o600)
    def core(self):return Workspace(self.path,'local_ui_workspace')
    def backup_bundle(self,body):
        if type(body) is not dict or set(body)!={'acknowledge_private_data'} or body['acknowledge_private_data'] is not True:
            raise ContractError('backup_ack_required','Explicit acknowledgment of private backup contents required.')
        if not self.backup_lock.acquire(blocking=False):raise ContractError('backup_busy','Another backup is already running.')
        try:
            from packages.storage.local_backup import create_bundle
            with self.core() as core:
                owner=core.authority.issue_scope('local_owner');core.scope(owner,'personal');core.active(owner,'personal')
                return create_bundle(core,owner)
        finally:self.backup_lock.release()
    def state(self):
        with self.core() as core,core.read_snapshot():
            owner=core.authority.issue_scope('local_owner');core.scope(owner,'personal');core.active(owner,'personal')
            project=core.project(owner,'personal')
            rows=core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 101',(core.workspace,'personal')).fetchall()
            tasks=[]
            for rid,version,raw in rows[:100]:
                body=json.loads(raw)
                if body['type']!='Task':continue
                workflow=TaskWorkflowService(core).view(owner,'personal',rid)
                tasks.append(dict(id=rid,version=version,body=body,acceptance=AcceptanceService(core).view(owner,'personal',rid),workflow=workflow,blocker=TaskBlockerService(core).view(owner,'personal',rid),lane=workflow['stage']))
            task_sources={}
            for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_candidates_applied'",(core.workspace,'personal')):
                receipt=json.loads(raw)
                for rid in receipt['result'].get('temp_ids',{}).values():task_sources.setdefault(rid,[]).append(receipt['source'])
                for attachment in receipt.get('attached',[]):
                    for match in attachment['matches']:
                        rid=match['id'] if isinstance(match,dict) else match
                        task_sources.setdefault(rid,[]).append(receipt['source'])
            return dict(task_sources=task_sources,conversation_review=ConversationService(core).view(owner,'personal'),model_ready=self.extractor is not None,project=project,tasks=tasks,records=[dict(id=rid,version=v,body=json.loads(raw)) for rid,v,raw in rows[:100]],question_inbox=QuestionService(core).view(owner,'personal'),decision_proposals=QuestionDecisionService(core).view(owner,'personal'),truncated=len(rows)>100,snapshot=project['knowledge_revision'],workflow_preset=list(__import__('packages.domain.task_workflow',fromlist=['STAGES']).STAGES),capabilities=dict(manual_tasks=True,versioned_acceptance=True,automatic_capture=False,semantic_extraction=False,verified_completion=True,verification_methods=['human_review'],automatic_verifier=False),csrf=self.csrf)
    def command(self,body):
        if type(body) is not dict or body.get('action') not in ('link_dependency','workflow_transition','criterion_evidence','task_blocker','create_task','acceptance','start','ask_question','answer_question','prepare_decision','approve_decision','apply_decision','question_state','associate_answer','revise_question','import_conversation','analyze_conversation','accept_candidates'):raise ContractError('invalid_request','Unknown UI action.')
        with self.core() as core:
            owner=core.authority.issue_scope('local_owner');action=body['action']
            if action=='link_dependency':
                if set(body)!={'action','task','target','base_revision','key'}:raise ContractError('invalid_request','Exact dependency approval fields required.')
                with core.transaction():
                    core.scope(owner,'personal',write=True,human=True);core.active(owner,'personal')
                    service=TaskWorkflowService(core);service._task('personal',body['task']);service._task('personal',body['target'])
                    from packages.storage.project_store import digest
                    signature=digest(canonical(body))
                    prior=next((json.loads(raw) for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='task_dependency_approved'",(core.workspace,'personal')) if json.loads(raw)['key']==body['key']),None)
                    if prior:
                        if prior['signature']!=signature:raise ContractError('idempotency_conflict','Dependency identity changed.')
                        return prior['result']
                    if type(body['base_revision']) is not int or body['base_revision']!=core.project(owner,'personal')['knowledge_revision']:raise ContractError('stale_base','Refresh the dependency preview.')
                    if service._stage('personal',body['task'])['stage']=='Cancelled':raise ContractError('task_cancelled','Cancelled task cannot add an active dependency.')
                    plan=core.plan(owner,'personal',body['key'],[dict(op='link',origin=body['task'],target=body['target'],kind='depends_on')])
                    result=core._apply(owner,plan,core._approve(owner,plan))
                    core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(core.workspace,'personal',owner.principal_id,'task_dependency_approved',canonical(dict(key=body['key'],signature=signature,result=result))))
                    return result
            if action in ('workflow_transition','criterion_evidence'):
                fields={'action','task','task_version','base_revision','stage','reason','key','scope_reviewed'} if action=='workflow_transition' else {'action','task','task_version','contract_version','criterion','status','reference','note','key'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact workflow/evidence fields required.')
                service=TaskWorkflowService(core)
                return (service.transition if action=='workflow_transition' else service.evidence)(owner,'personal',**{k:v for k,v in body.items() if k!='action'})
            if action=='task_blocker':
                if set(body) not in ({'action','task','task_version','base_revision','blocked','reason','next_action'},{'action','task','task_version','base_revision','blocked','reason','next_action','gate','waiting_kind','owner'}):raise ContractError('invalid_request','Exact blocker fields required.')
                return TaskBlockerService(core).set(owner,'personal',**{k:v for k,v in body.items() if k!='action'})
            if action in ('import_conversation','analyze_conversation','accept_candidates'):
                service=ConversationService(core)
                if action=='import_conversation':
                    if set(body)!={'action','text'}:raise ContractError('invalid_request','Exact conversation fields required.')
                    source=service.ingest(owner,'personal',text=body['text'])
                    return dict(source=source,analysis=service.analyze(owner,'personal',source['id'],self.extractor))
                if action=='analyze_conversation':
                    if set(body)!={'action','source_id'}:raise ContractError('invalid_request','Exact source ID required.')
                    return service.analyze(owner,'personal',body['source_id'],self.extractor)
                if set(body)!={'action','source_id','key','selected','base_revision'}:raise ContractError('invalid_request','Exact candidate review required.')
                return service.accept(owner,'personal',**{k:v for k,v in body.items() if k!='action'})
            if action=='question_state':
                if set(body)!={'action','request_id','question','revision','base_state','status','reason'}:raise ContractError('invalid_request','Exact lifecycle fields required.')
                return QuestionService(core).transition(owner,'personal',**{k:v for k,v in body.items() if k!='action'})
            if action=='associate_answer':
                if set(body)!={'action','request_id','answer_id'}:raise ContractError('invalid_request','Exact association fields required.')
                return QuestionService(core).associate(owner,'personal',request_id=body['request_id'],answer_id=body['answer_id'])
            if action=='revise_question':
                if set(body)!={'action','question','base_revision','text','options','task','reason'}:raise ContractError('invalid_request','Exact revision fields required.')
                return QuestionService(core).present(owner,'personal',**{k:v for k,v in body.items() if k!='action'})
            if action in ('prepare_decision','approve_decision','apply_decision','question_state','associate_answer','revise_question'):
                fields={'action','key','answer_id','reason'} if action=='prepare_decision' else {'action','key'} if action=='approve_decision' else {'action','key','approval'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact decision fields required.')
                service=QuestionDecisionService(core)
                if action=='prepare_decision':return service.prepare(owner,'personal',key=body['key'],answer_id=body['answer_id'],reason=body['reason'])
                if action=='approve_decision':return dict(approval=service.approve(owner,'personal',body['key']))
                return service.apply(owner,'personal',body['key'],body['approval'])
            if action=='ask_question':
                if set(body) not in ({'action','request_id','text','options'},{'action','request_id','text','options','task'}):raise ContractError('invalid_request','Exact question fields required.')
                return QuestionService(core).present(owner,'personal',question=body['request_id'],base_revision=0,text=body['text'],options=body['options'],task=body.get('task'))
            if action=='answer_question':
                if set(body)!={'action','request_id','question','revision','option'}:raise ContractError('invalid_request','Exact answer fields required.')
                return QuestionService(core).answer(owner,'personal',**{k:v for k,v in body.items() if k!='action'})
            if action=='create_task':
                if set(body)!={'action','title','description'}:raise ContractError('invalid_request','Exact task fields required.')
                ops=[dict(op='create',id='task',body=dict(type='Task',title=body['title'],description=body['description']))]
            elif action=='start':
                if set(body)!={'action','task'}:raise ContractError('invalid_request','Exact start fields required.')
                return AcceptanceService(core).start(owner,'personal',body['task'])
            else:
                if set(body)!={'action','task','task_version','base_contract','criteria','dod','reason','acknowledged_changes'}:raise ContractError('invalid_request','Exact acceptance fields required.')
                ops=[dict({k:v for k,v in body.items() if k!='action'},op='acceptance_contract')]
            plan=core.plan(owner,'personal','ui_'+uuid.uuid4().hex,ops);token=core.approve(owner,plan)
            return core.apply(owner,plan,token)

def make_server(path,port=0,extractor=None):
    app=LocalApp(path,extractor=extractor)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def answer(self,code,body,kind='application/json',cookie=False):
            raw=json.dumps(body,ensure_ascii=False).encode() if kind=='application/json' else body
            self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if cookie:self.send_header('Set-Cookie','decivora_session='+app.cookie+'; HttpOnly; SameSite=Strict; Path=/')
            self.end_headers();self.wfile.write(raw)
        def gate(self,write=False):
            if len(self.headers.get_all('Host',[]))!=1 or self.headers['Host']!=self.server.expected_host:return False
            if self.headers.get('Origin') and self.headers['Origin']!=self.server.origin:return False
            if write and self.headers.get('Origin')!=self.server.origin:return False
            return True
        def authenticated(self):
            cookie=SimpleCookie()
            try:cookie.load(self.headers.get('Cookie',''))
            except Exception:return False
            value=cookie.get('decivora_session');return bool(value and secrets.compare_digest(value.value,app.cookie))
        def do_GET(self):
            if not self.gate():return self.answer(403,dict(error='origin_denied'))
            if self.path in ('/','/app.js','/i18n.js','/locales.js','/workspace.css'):
                file=ROOT/('index.html' if self.path=='/' else self.path[1:]);return self.answer(200,file.read_bytes(),'text/html; charset=utf-8' if self.path=='/' else 'text/css' if self.path=='/workspace.css' else 'application/javascript')
            if self.path!='/api/state':return self.answer(404,dict(error='not_found'))
            if not self.authenticated():return self.answer(401,dict(error='session_required'))
            try:self.answer(200,app.state())
            except Exception:self.answer(503,dict(error='storage_unavailable'))
        def do_POST(self):
            if not self.gate(write=True):return self.answer(403,dict(error='origin_denied'))
            if self.path=='/api/session':
                if not secrets.compare_digest(self.headers.get('Authorization',''),'Bearer '+app.bootstrap):return self.answer(401,dict(error='session_required'))
                self.close_connection=True
                return self.answer(200,dict(csrf=app.csrf),cookie=True)
            if self.path not in ('/api/command','/api/shutdown','/api/backup'):return self.answer(404,dict(error='not_found'))
            if not self.authenticated() or not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),app.csrf):return self.answer(403,dict(error='session_or_csrf_required'))
            if self.path=='/api/shutdown':
                self.answer(200,dict(status='stopping'));threading.Thread(target=self.server.shutdown,daemon=True).start();return
            with app.rate_lock:
                window=int(time.monotonic()//60)
                if app.window!=window:app.window=window;app.writes=0
                if app.writes>=30:return self.answer(429,dict(error='rate_limited'))
                app.writes+=1
            length=self.headers.get('Content-Length','')
            if not length.isdecimal() or not 0<int(length)<=32768 or self.headers.get('Content-Type')!='application/json':return self.answer(413,dict(error='bounded_json_required'))
            try:
                body=json.loads(self.rfile.read(int(length)))
                if self.path=='/api/backup':return self.answer(200,app.backup_bundle(body),'application/zip')
                result=app.command(body);self.answer(200,result)
            except ContractError as e:self.answer(409,dict(error=e.code,message=str(e)))
            except (ValueError,TypeError,KeyError):self.answer(400,dict(error='invalid_request'))
            except Exception:self.answer(503,dict(error='storage_unavailable'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.daemon_threads=True;server.expected_host='127.0.0.1:'+str(server.server_port);server.origin='http://'+server.expected_host;server.app=app
    return server

def main():
    if sys.version_info[:2]!=(3,12):raise SystemExit('Bu sürüm Python 3.12 gerektiriyor.')
    parser=argparse.ArgumentParser();parser.add_argument('--data-dir',type=Path,default=Path(__file__).resolve().parents[3]/'decivora-local-data');parser.add_argument('--port',type=int,default=0);parser.add_argument('--no-browser',action='store_true');args=parser.parse_args()
    server=make_server(args.data_dir/'workspace.sqlite',args.port)
    print('Decivora local preview: '+server.origin+' — close with Ctrl+C. No model/API calls.',flush=True)
    if not args.no_browser:webbrowser.open(server.origin+'/#'+server.app.bootstrap)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()

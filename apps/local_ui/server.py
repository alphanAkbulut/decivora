"""Runnable local UI. Loopback, ephemeral session, CSRF/origin checks, explicit writes."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from pathlib import Path
import json,secrets,threading,uuid,webbrowser,argparse,time,sys
from packages.storage.workspace import Workspace
from packages.storage.project_store import canonical
from packages.domain.acceptance import AcceptanceService
from packages.domain.questions import QuestionService
from packages.domain.question_decisions import QuestionDecisionService
from packages.domain.source_event import ContractError

ROOT=Path(__file__).parent
class LocalApp:
    def __init__(self,path):
        self.path=Path(path);fresh=not self.path.exists();self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.cookie=secrets.token_urlsafe(32);self.csrf=secrets.token_urlsafe(32);self.bootstrap=secrets.token_urlsafe(32);self.rate_lock=threading.Lock();self.window=0;self.writes=0
        with Workspace(self.path,'local_ui_workspace',owner='local_owner' if fresh else None) as core:
            if fresh:
                a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=1)
                core.create_project(a.issue_scope('local_owner'),'personal','Benim projem');self.path.chmod(0o600)
    def core(self):return Workspace(self.path,'local_ui_workspace')
    def state(self):
        with self.core() as core:
            owner=core.authority.issue_scope('local_owner');records=core.records(owner,'personal',limit=100)
            started={json.loads(raw)['task'] for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='task_work_started'",(core.workspace,'personal'))}
            tasks=[]
            for r in records['records']:
                if r['body']['type']!='Task':continue
                acceptance=AcceptanceService(core).view(owner,'personal',r['id'])
                tasks.append(dict(r,acceptance=acceptance,lane='Cancelled' if r['body'].get('execution')=='cancelled' else 'In Progress' if r['id'] in started else 'To Do'))
            return dict(project=core.project(owner,'personal'),tasks=tasks,question_inbox=QuestionService(core).view(owner,'personal'),decision_proposals=QuestionDecisionService(core).view(owner,'personal'),truncated=records['truncated'],capabilities=dict(manual_tasks=True,versioned_acceptance=True,automatic_capture=False,semantic_extraction=False,verified_completion=False),csrf=self.csrf)
    def command(self,body):
        if type(body) is not dict or body.get('action') not in ('create_task','acceptance','start','ask_question','answer_question','prepare_decision','approve_decision','apply_decision','question_state','associate_answer','revise_question'):raise ContractError('invalid_request','Unknown UI action.')
        with self.core() as core:
            owner=core.authority.issue_scope('local_owner');action=body['action']
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
                if set(body)!={'action','request_id','text','options'}:raise ContractError('invalid_request','Exact question fields required.')
                return QuestionService(core).present(owner,'personal',question=body['request_id'],base_revision=0,text=body['text'],options=body['options'])
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

def make_server(path,port=0):
    app=LocalApp(path)
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
            if self.path in ('/','/app.js'):
                file=ROOT/('index.html' if self.path=='/' else 'app.js');return self.answer(200,file.read_bytes(),'text/html; charset=utf-8' if self.path=='/' else 'application/javascript')
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
            if self.path not in ('/api/command','/api/shutdown'):return self.answer(404,dict(error='not_found'))
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
                body=json.loads(self.rfile.read(int(length)));result=app.command(body);self.answer(200,result)
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

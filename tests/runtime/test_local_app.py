"""Local UI HTTP boundary and persistent commands; no external network/API."""
from pathlib import Path
import tempfile,threading,json,unittest,time
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from apps.local_ui.server import make_server,LocalApp

class LocalAppTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'app.sqlite';self.server=make_server(self.path);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.addCleanup(self.stop)
        self.origin=self.server.origin;self.headers={'Origin':self.origin,'Cookie':'decivora_session='+self.server.app.cookie,'X-CSRF-Token':self.server.app.csrf,'Content-Type':'application/json'}
    def stop(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
    def call(self,path,body=None,headers=None):
        req=Request(self.origin+path,data=json.dumps(body).encode() if body is not None else None,headers=self.headers if headers is None else headers)
        try:
            with urlopen(req,timeout=5) as r:return r.status,json.loads(r.read()) if r.headers['Content-Type']=='application/json' else r.read(),dict(r.headers)
        except HTTPError as e:return e.code,json.loads(e.read()),dict(e.headers)
    def test_unauthenticated_reads_and_cross_origin_writes_denied(self):
        self.assertEqual(self.call('/api/state',headers={})[0],401)
        self.assertEqual(self.call('/api/command',dict(action='start',task='x'),dict(self.headers,Origin='https://evil.example'))[0],403)
        self.assertEqual(self.call('/api/command',{},dict(self.headers,**{'X-CSRF-Token':''}))[0],403)
    def test_bad_host_and_unknown_path_denied(self):
        self.assertEqual(self.call('/api/state',headers=dict(self.headers,Host='evil.example'))[0],403)
        self.assertEqual(self.call('/../../workspace.sqlite')[0],404)
    def test_session_cookie_is_http_only_and_strict_and_no_cors(self):
        code,body,headers=self.call('/api/session',{},dict(Origin=self.origin,Authorization='Bearer '+self.server.app.bootstrap))
        self.assertEqual(code,200);self.assertIn('HttpOnly',headers['Set-Cookie']);self.assertIn('SameSite=Strict',headers['Set-Cookie']);self.assertNotIn('Access-Control-Allow-Origin',headers)
    def test_task_persists_after_restart_and_not_false_done(self):
        self.assertEqual(self.call('/api/command',dict(action='create_task',title='Actual manual task',description='Persistent'))[0],200)
        state=LocalApp(self.path).state();self.assertEqual(state['tasks'][0]['lane'],'To Do');self.assertFalse(state['tasks'][0]['acceptance']['completed'])
    def test_real_http_acceptance_start_flow(self):
        self.call('/api/command',dict(action='create_task',title='Task',description='Scope'));task=self.call('/api/state')[1]['tasks'][0]
        self.assertEqual(self.call('/api/command',dict(action='start',task=task['id']))[0],409)
        row=lambda rid:dict(id=rid,statement='Observed result',method='human_review',required=True,applicable=True,applicability_reason='')
        command=dict(action='acceptance',task=task['id'],task_version=task['version'],base_contract=0,criteria=[row('AC1')],dod=[row('DOD1')],reason='Explicit owner approval',acknowledged_changes=[])
        self.assertEqual(self.call('/api/command',command)[0],200);self.assertEqual(self.call('/api/command',dict(action='start',task=task['id']))[0],200)
        task=self.call('/api/state')[1]['tasks'][0];self.assertEqual(task['lane'],'In Progress');self.assertFalse(task['acceptance']['completed'])
    def test_shell_action_and_extra_fields_do_not_write(self):
        self.assertEqual(self.call('/api/command',dict(action='shell',command='no'))[0],409)
        self.assertEqual(self.call('/api/command',dict(action='create_task',title='Task',description='',project='foreign'))[0],409)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])
    def test_authenticated_write_rate_limit_preserves_existing_state(self):
        self.server.app.window=int(time.monotonic()//60);self.server.app.writes=30
        self.assertEqual(self.call('/api/command',dict(action='create_task',title='Over limit',description=''))[0],429)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])

    def test_private_new_db_and_default_scaffold_has_no_server_side_effects(self):
        self.assertEqual(self.path.stat().st_mode&0o777,0o600)
        self.assertFalse(self.call('/api/state')[1]['capabilities']['semantic_extraction'])

    def test_question_http_flow_and_reload_preserve_selection(self):
        body=dict(action='ask_question',request_id='Q1',text='Storage?',options=[dict(id='sqlite',label='SQLite'),dict(id='files',label='Files')])
        self.assertEqual(self.call('/api/command',body)[0],200)
        self.assertEqual(self.call('/api/state')[1]['question_inbox']['questions'][0]['status'],'Open')
        answer=dict(action='answer_question',request_id='a1',question='Q1',revision=1,option='sqlite')
        code,result,_=self.call('/api/command',answer);self.assertEqual(code,200);self.assertEqual(result['status'],'Selected');self.assertFalse(result['canonical_apply'])
        self.assertEqual(LocalApp(self.path).state()['question_inbox']['questions'][0]['selection'],'sqlite')
        self.assertEqual(self.call('/api/command',answer)[1],result)

"""Durable safe telemetry and environment separation; no real source/model calls."""
import hashlib,json,os,sqlite3,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from apps.local_ui.server import LocalApp,make_server
from packages.operations.local import LocalOperations,MAX_RUNS,identity_from_scope
from packages.domain.source_event import ContractError

class OperationsTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'workspace.sqlite';self.app=LocalApp(self.path)
 def create(self):return self.app.command(dict(action='create_task',title='PRIVATE_SOURCE',description='PRIVATE_PROMPT sk-secret-value'))
 def test_successful_trace_has_project_scoped_real_boundary_timings_and_no_text(self):
  self.create();view=self.app.operations_view();self.assertTrue(view['persistent']);self.assertTrue(view['available']);self.assertEqual(len(view['runs']),1)
  run=view['runs'][0];self.assertEqual(run['action'],'create_task');self.assertEqual(run['outcome'],'succeeded');self.assertGreaterEqual(run['duration_ms'],0)
  self.assertEqual([s['stage'] for s in run['stages']],['authorize_project','execute_command']);self.assertEqual(run['stages'][1]['component'],'tasks')
  self.assertNotIn('PRIVATE',json.dumps(view));self.assertNotIn('sk-secret',json.dumps(view));self.assertEqual(self.app.operations.path.stat().st_mode&0o777,0o600)
 def test_failed_command_and_http_errors_survive_restart_without_exception_or_url_text(self):
  with self.assertRaises(ContractError):self.app.command(dict(action='start',task='missing'))
  self.app.record_error('/private/sk-secret','credential-sk-secret');self.app.record_error('/api/command','acceptance_required');self.app.record_error('/api/command','acceptance_required')
  view=LocalApp(self.path).operations_view();self.assertEqual(view['runs'][0]['outcome'],'failed');self.assertEqual(view['runs'][0]['code'],'application_error')
  self.assertTrue(any(e['count']==2 and e['code']=='acceptance_required' for e in view['errors']));self.assertNotIn('sk-secret',json.dumps(view));self.assertTrue(any(e['endpoint']=='other' for e in view['errors']))
 def test_unknown_incomplete_run_after_process_restart_is_not_success(self):
  run=self.app.operations.begin('personal','create_task');view=LocalApp(self.path).operations_view();self.assertEqual(view['runs'][0]['id'],run);self.assertEqual(view['runs'][0]['outcome'],'unknown');self.assertIsNone(view['runs'][0]['duration_ms'])
 def test_reading_diagnostics_does_not_mutate_canonical_database_or_make_new_runs(self):
  self.create()
  with self.app.core() as core:before=list(core.db.iterdump())
  runs=self.app.operations_view()['runs']
  for _ in range(3):self.assertEqual(self.app.operations_view()['runs'],runs)
  with self.app.core() as core:self.assertEqual(list(core.db.iterdump()),before)
 def test_telemetry_failure_does_not_undo_domain_success_and_is_visible(self):
  with patch.object(self.app.operations,'_connect',side_effect=sqlite3.OperationalError('SECRET')):self.create()
  self.assertEqual(len(self.app.state()['tasks']),1);view=self.app.operations_view();self.assertFalse(view['available']);self.assertGreater(view['lost_this_process'],0);self.assertNotIn('SECRET',json.dumps(view))
 def test_bounded_telemetry_retention_does_not_remove_domain_history(self):
  self.create()
  for _ in range(MAX_RUNS+2):
   run=self.app.operations.begin('personal','create_task');self.app.operations.finish(run,time.monotonic())
  with sqlite3.connect(self.app.operations.path) as db:self.assertEqual(db.execute('SELECT count(*) FROM op_runs').fetchone()[0],MAX_RUNS)
  self.assertGreater(self.app.operations_view()['evicted']['runs_evicted'],0);self.assertEqual(len(self.app.state()['tasks']),1)
 def test_cross_project_visibility_and_revoked_grant(self):
  with self.app.core() as core:
   authority=core.authority;owner=authority.issue_scope('local_owner');authority.replace_grant(owner,'local_owner',kind='human',readable=frozenset({'personal','other'}),writable=frozenset({'personal','other'}),active=True,base_revision=authority.revision());core.create_project(authority.issue_scope('local_owner'),'other','Private other')
  self.create();self.assertEqual(self.app.operations_view('other')['runs'],[])
  with self.app.core() as core:
   a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'other'}),writable=frozenset({'other'}),active=True,base_revision=a.revision())
  with self.assertRaises(ContractError):self.app.operations_view('personal')
 def test_environment_separation_and_connections_disabled(self):
  testpath=Path(self.temp.name)/'test'/'workspace.sqlite';test=LocalApp(testpath,environment='test');test.command(dict(action='create_task',title='Synthetic test',description='Test only'))
  self.assertEqual(self.app.state()['tasks'],[]);self.assertEqual(test.state()['environment'],'test')
  for path,environment in [(self.path,'test'),(testpath,'local')]:
   with self.assertRaises(ContractError):LocalApp(path,environment=environment)
  with self.assertRaises(ContractError):LocalApp(Path(self.temp.name)/'bad'/'workspace.sqlite',environment='test',extractor=lambda x:x)
 def test_existing_unmarked_database_is_not_adopted_as_test(self):
  other=Path(self.temp.name)/'unknown.sqlite';other.write_bytes(b'existing private data')
  with self.assertRaises(ContractError):LocalApp(other,environment='test')
  self.assertEqual(other.read_bytes(),b'existing private data')
 def test_unsafe_operation_log_path_is_not_opened(self):
  target=Path(self.temp.name)/'private.txt';target.write_text('KEEP');link=Path(self.temp.name)/'link.sqlite';link.symlink_to(target);log=LocalOperations(link);self.assertFalse(log.available);self.assertEqual(target.read_text(),'KEEP')
 def test_real_http_operations_requires_session_and_preserves_trace_header(self):
  import test_local_app as http
  fixture=http.LocalAppTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  self.assertEqual(fixture.call('/api/operations',headers={})[0],401)
  self.assertEqual(fixture.call('/api/operations',headers=dict(fixture.headers,Origin='https://foreign.example'))[0],403)
  code,value,headers=fixture.call('/api/command',dict(action='create_task',title='Fixture',description='Synthetic'));self.assertEqual(code,200)
  trace=headers.get('X-Decivora-Operation-ID');self.assertTrue(trace.startswith('op_'));data=fixture.call('/api/operations')[1];self.assertTrue(any(r['id']==trace for r in data['runs']))
  self.assertEqual(fixture.call('/api/operations?project_id=unknown')[0],409)
 def test_test_launcher_starts_marked_isolated_environment_without_connections(self):
  import subprocess,selectors,sys
  root=Path(__file__).resolve().parents[2];target=Path(self.temp.name)/'launched-test'
  launcher=[str(root/'Decivora Test.command')] if sys.platform=='darwin' else [sys.executable,'-B','-m','apps.local_ui.server','--environment','test']
  process=subprocess.Popen(launcher+['--data-dir',str(target),'--port','0','--no-browser'],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   selector=selectors.DefaultSelector();selector.register(process.stdout,selectors.EVENT_READ);self.assertTrue(selector.select(5),'Test launcher did not start');line=process.stdout.readline();selector.close();self.assertIn('Decivora test preview:',line)
   from urllib.request import urlopen
   origin=line.split('preview: ',1)[1].split(' — ',1)[0]
   with urlopen(origin,timeout=5) as response:html=response.read().decode()
   self.assertIn('>TEST</p>',html);self.assertTrue((target/'workspace.sqlite.environment.json').exists());self.assertEqual(self.app.state()['tasks'],[])
  finally:process.terminate();process.communicate(timeout=5)
 def test_normal_and_test_sessions_coexist_in_same_browser_cookie_jar(self):
  import threading,http.cookiejar
  from urllib.request import build_opener,HTTPCookieProcessor,Request
  local=make_server(Path(self.temp.name)/'normal'/'workspace.sqlite');test=make_server(Path(self.temp.name)/'separate-test'/'workspace.sqlite',environment='test');threads=[]
  try:
   for server in (local,test):
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();threads.append(thread)
   jar=http.cookiejar.CookieJar();opener=build_opener(HTTPCookieProcessor(jar))
   for server in (local,test):
    opener.open(Request(server.origin+'/api/session',data=b'{}',headers={'Origin':server.origin,'Authorization':'Bearer '+server.app.bootstrap}),timeout=5).close()
   self.assertEqual({cookie.name for cookie in jar},{'decivora_session','decivora_test_session'})
   for server,environment in ((local,'local'),(test,'test')):
    with opener.open(server.origin+'/api/state',timeout=5) as response:self.assertEqual(json.load(response)['environment'],environment)
  finally:
   for server in (local,test):server.shutdown();server.server_close()
   for thread in threads:thread.join(timeout=3)
 def test_operations_projection_matches_published_field_contract(self):
  root=Path(__file__).resolve().parents[2];schema=json.loads((root/'manifests/local-operations.schema.json').read_text());self.create();value=self.app.operations_view()
  self.assertLessEqual(set(schema['required']),set(value));self.assertEqual(set(value),set(schema['properties']))
  run=value['runs'][0];expected=schema['properties']['runs']['items'];self.assertEqual(set(run),set(expected['required']));self.assertEqual(set(run['stages'][0]),set(expected['properties']['stages']['items']['required']))

 def test_identity_is_trusted_preflight_not_client_actor(self):
  self.create();first=self.app.operations_view()['runs'][0]['identity']
  with self.app.core() as core:
   self.assertEqual(first,dict(workspace=core.workspace,actor_id='local_owner',actor_type='human',authz_revision=core.authority.revision()))
  with self.assertRaises(ContractError):self.app.command(dict(action='create_task',title='Spoof',description='Fixture',actor_id='attacker'))
  self.assertEqual(self.app.operations_view()['runs'][0]['identity'],first);self.assertEqual(len(self.app.state()['tasks']),1)
  self.assertEqual(LocalApp(self.path).operations_view()['runs'][0]['identity'],first)
 def test_identity_rejects_forged_stale_and_wrong_project_scopes(self):
  from packages.domain.project_binding import AccessScope
  with self.app.core() as core:
   a=core.authority;owner=a.issue_scope('local_owner')
   forged=AccessScope(core.workspace,'local_owner',owner.readable_projects,owner.writable_projects)
   for scope,project in ((forged,'personal'),(owner,'forbidden_project')):
    with self.assertRaises(ContractError):identity_from_scope(core,scope,project)
   a.replace_grant(owner,'fixture_agent',kind='agent',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision())
   with self.assertRaises(ContractError):identity_from_scope(core,owner,'personal')
   agent=a.issue_scope('fixture_agent');identity=identity_from_scope(core,agent,'personal');self.assertEqual(identity['actor_type'],'agent');self.assertEqual(identity['actor_id'],'fixture_agent');self.assertEqual(identity['authz_revision'],a.revision())
   a.replace_grant(a.issue_scope('local_owner'),'fixture_agent',kind='agent',readable=frozenset(),writable=frozenset(),active=False,base_revision=a.revision())
   with self.assertRaises(ContractError):identity_from_scope(core,agent,'personal')
 def test_additive_legacy_migration_does_not_invent_identity_or_rewrite_history(self):
  self.create();before=self.app.operations_view()['runs'][0]
  with sqlite3.connect(self.app.operations.path) as db:
   history=db.execute('SELECT * FROM op_runs').fetchall();db.execute('DROP TABLE op_identities')
  reopened=LocalApp(self.path);after=reopened.operations_view()['runs'][0]
  self.assertIsNone(after['identity']);self.assertEqual(after['stages'],before['stages'])
  with sqlite3.connect(self.app.operations.path) as db:self.assertEqual(db.execute('SELECT * FROM op_runs').fetchall(),history)
  self.assertIsNone(LocalApp(self.path).operations_view()['runs'][0]['identity'])
 def test_identity_insert_failure_is_atomic_and_does_not_undo_domain_result(self):
  with sqlite3.connect(self.app.operations.path) as db:db.execute("CREATE TRIGGER reject_identity BEFORE INSERT ON op_identities BEGIN SELECT RAISE(ABORT,'PRIVATE'); END")
  self.create();self.assertEqual(len(self.app.state()['tasks']),1);view=self.app.operations_view();self.assertEqual(view['runs'],[]);self.assertGreater(view['lost_this_process'],0);self.assertNotIn('PRIVATE',json.dumps(view))
  with sqlite3.connect(self.app.operations.path) as db:self.assertEqual(db.execute('SELECT count(*) FROM op_identities').fetchone()[0],0)
 def test_identity_eviction_cascades_and_new_revision_does_not_relabel_old_run(self):
  self.create();original=self.app.operations_view()['runs'][0]
  with self.app.core() as core:
   a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'fixture_agent',kind='agent',readable=frozenset({'personal'}),writable=frozenset(),active=True,base_revision=a.revision())
  self.create();runs=self.app.operations_view()['runs'];self.assertGreater(runs[0]['identity']['authz_revision'],original['identity']['authz_revision']);self.assertEqual(runs[1]['identity'],original['identity'])
  for _ in range(MAX_RUNS):
   run=self.app.operations.begin('personal','create_task',identity=runs[0]['identity']);self.app.operations.finish(run,time.monotonic())
  with sqlite3.connect(self.app.operations.path) as db:
   self.assertEqual(db.execute('SELECT count(*) FROM op_identities').fetchone()[0],MAX_RUNS);self.assertIsNone(db.execute('SELECT run FROM op_identities WHERE run=?',(original['id'],)).fetchone());self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])

"""Scheduled native capture with a synthetic host; no model or actual chat."""
import threading,time,unittest
from unittest.mock import patch
import test_native_ui_connection as fixtures
from apps.local_ui.server import LocalApp
from packages.capture.codex.capture_loop import CaptureLoopService
from packages.domain.source_event import ContractError

class CaptureLoopTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.NativeUIConnectionTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups);self.app=self.fx.app;self.addCleanup(self.app.capture_worker.shutdown);self.connection=self.fx.connect()
  self.params=dict(action='create_capture_loop',loop_id='schedule',capture_id=self.connection['id'],capture_sha256=self.connection['configuration_sha256'],max_ticks=2,interval_seconds=1,expires_at=self.connection['expires_at']-10,reason='Explicit synthetic selected chat polling')
 def create(self,**changes):return self.app.command(dict(self.params,**changes))
 def tick(self,c):
  with self.app.core() as core:return CaptureLoopService(core,self.fx.connector).tick(core.authority.issue_scope('local_owner'),'personal',loop_id=c['id'],configuration_sha256=c['configuration_sha256'])
 def test_plan_ticks_dedup_limits_restart(self):
  c=self.create();self.assertEqual(self.fx.calls,[]);self.assertEqual(self.tick(c)['status'],'Captured');self.assertEqual(self.tick(c)['status'],'Waiting for interval')
  with patch('time.time',return_value=time.time()+2):self.assertEqual(self.tick(c)['status'],'Captured')
  self.assertEqual(self.tick(c)['status'],'Limit reached');self.assertEqual(len(self.fx.calls),2);self.assertEqual(self.app.state()['conversation_review']['total'],1);self.assertEqual(self.app.state()['tasks'],[])
  again=LocalApp(self.fx.path,native_connector=self.fx.connector);self.addCleanup(again.capture_worker.shutdown);self.assertEqual(again.state()['capture_loops']['items'][0]['status'],'Limit reached');self.assertFalse(again.state()['capture_worker']['active']);self.assertEqual(len(self.fx.calls),2)
 def test_cannot_expand_reset_or_duplicate_plan(self):
  for changes in [dict(max_ticks=3),dict(expires_at=self.connection['expires_at']+1),dict(capture_sha256='a'*64),dict(interval_seconds=float('nan')),dict(max_ticks=True)]:
   with self.subTest(changes=changes),self.assertRaises(ContractError):self.create(**changes)
  c=self.create();self.assertEqual(c,self.create())
  with self.assertRaises(ContractError):self.create(max_ticks=1)
  with self.assertRaises(ContractError):self.create(loop_id='other')
  self.assertEqual(self.fx.calls,[])
 def test_terminal_stop_before_start(self):
  c=self.create();self.app.command(dict(action='stop_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],reason='Owner stopped before start'))
  with self.assertRaises(ContractError):self.app.command(dict(action='start_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],consent=True))
  self.assertEqual(self.fx.calls,[])
 def test_start_consent_digest_and_expiry(self):
  c=self.create()
  for change in [dict(consent=False),dict(configuration_sha256='a'*64)]:
   with self.assertRaises(ContractError):self.app.command(dict(dict(action='start_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],consent=True),**change))
  with patch('time.time',return_value=c['expires_at']+1):
   with self.assertRaises(ContractError):self.tick(c)
  self.assertEqual(self.fx.calls,[])
 def test_disconnect_blocks_host(self):
  c=self.create();self.app.command(dict(action='disconnect_codex_source',capture_id=self.connection['id']))
  with self.assertRaises(ContractError):self.tick(c)
  self.assertEqual(self.fx.calls,[])
 def test_failed_read_not_retried(self):
  c=self.create();self.fx.after_read=lambda:(_ for _ in ()).throw(ContractError('codex_read_failed','Synthetic failure'))
  with self.assertRaises(ContractError):self.tick(c)
  with self.assertRaises(ContractError):self.tick(c)
  self.assertEqual(len(self.fx.calls),1);self.assertEqual(self.app.state()['capture_loops']['items'][0]['status'],'Review required')
 def test_unfinished_claim_blocks_restart(self):
  c=self.create();self.fx.after_read=lambda:(_ for _ in ()).throw(RuntimeError('Synthetic crash'))
  with self.assertRaises(RuntimeError):self.tick(c)
  self.assertEqual(self.app.state()['capture_loops']['items'][0]['status'],'Unfinished read')
  with self.assertRaises(ContractError):self.tick(c)
  self.assertEqual(len(self.fx.calls),1)
 def test_stop_inflight_prevents_checkpoint_and_other_worker(self):
  c=self.create();entered=threading.Event();release=threading.Event();self.addCleanup(release.set)
  def wait():entered.set();release.wait(3)
  self.fx.after_read=wait;self.app.command(dict(action='start_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],consent=True));self.assertTrue(entered.wait(3))
  try:
   self.assertTrue(self.app.operations_view()['native_capture']);self.assertTrue(self.app.state()['native_connections']['automatic_capture'])
   other=LocalApp(self.fx.path,native_connector=self.fx.connector);self.addCleanup(other.capture_worker.shutdown)
   with self.assertRaises(ContractError):other.command(dict(action='start_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],consent=True))
   with self.assertRaises(ContractError):self.fx.read(self.connection)
   with self.assertRaises(ContractError):self.app.command(dict(action='stop_capture_loop',loop_id=c['id'],configuration_sha256='wrong',reason='Wrong digest must not cancel worker'))
   self.assertFalse(self.app.capture_worker.event.is_set());self.app.command(dict(action='stop_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],reason='Stop during read'))
  finally:release.set();self.app.capture_worker.thread.join(3)
  self.assertEqual(self.app.state()['conversation_review']['total'],0);self.assertFalse(self.app.state()['capture_worker']['active']);self.assertEqual(self.app.state()['capture_loops']['items'][0]['status'],'Stopped')
 def test_worker_no_model_content_free_log(self):
  c=self.create(max_ticks=1);self.app.command(dict(action='start_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],consent=True));self.app.capture_worker.thread.join(3);self.assertFalse(self.app.capture_worker.thread.is_alive());s=self.app.state();self.assertEqual(s['capture_loops']['items'][0]['ticks'],1);self.assertEqual(s['tasks'],[]);self.assertEqual(s['model_sharing']['approvals'],[])
  logs=self.app.operations_view();self.assertIn('capture_tick',str(logs));self.assertNotIn('Synthetic restore task',str(logs))

 def test_worker_cancel_before_checkpoint_does_not_write_source(self):
  c=self.create();entered=threading.Event();release=threading.Event();self.addCleanup(release.set)
  def wait():entered.set();release.wait(3)
  self.fx.after_read=wait;self.app.command(dict(action='start_capture_loop',loop_id=c['id'],configuration_sha256=c['configuration_sha256'],consent=True));self.assertTrue(entered.wait(3))
  self.app.capture_worker.cancel('personal',c['id']);release.set();self.app.capture_worker.thread.join(3)
  self.assertEqual(self.app.state()['conversation_review']['total'],0);self.assertEqual(self.app.state()['capture_loops']['items'][0]['status'],'Review required')

 def test_eligible_schedule_does_not_auto_resume_on_restart(self):
  c=self.create();self.tick(c);again=LocalApp(self.fx.path,native_connector=self.fx.connector);self.addCleanup(again.capture_worker.shutdown)
  self.assertEqual(again.state()['capture_loops']['items'][0]['ticks'],1);self.assertFalse(again.state()['capture_worker']['active']);self.assertEqual(len(self.fx.calls),1)
 def test_authority_change_prevents_tick(self):
  c=self.create()
  with self.app.core() as core:
   a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision())
  with self.assertRaises(ContractError):self.tick(c)
  self.assertEqual(self.fx.calls,[]);self.assertEqual(self.app.state()['capture_loops']['items'][0]['status'],'Permission changed')

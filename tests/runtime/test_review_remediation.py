"""Review regressions use the public service path; no paid transport."""
import hashlib,time,unittest
from pathlib import Path
from unittest.mock import patch
import test_task_workflow as workflow_fixtures
from packages.domain.task_blockers import TaskBlockerService
from packages.domain.work_routing import RoutingService
from packages.domain.source_event import ContractError
from packages.capture.conversations import ConversationService
from packages.capture.responses_extractor import ResponsesExtractor
from packages.verification.files import FileChecker,FileVerificationService
class ReviewRemediationTests(unittest.TestCase):
 def setUp(self):
  self.f=workflow_fixtures.WorkflowTests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.core=self.f.core;self.owner=self.f.owner
 def test_prerequisite_invalidation_propagates_through_done_chain(self):
  for mode in ('blocker','file','checker_unavailable'):
   with self.subTest(mode=mode):
    f=workflow_fixtures.WorkflowTests();f.setUp()
    try:
     a=f.task;b=f.create('Prerequisite');f.contract(b);f.apply([dict(op='link',origin=a,target=b,kind='depends_on')])
     if mode!='blocker':
      root=Path(f.temp.name)/'root';root.mkdir();target=root/'result';target.write_bytes(b'expected');f.core.file_checker=FileChecker(root);checks=FileVerificationService(f.core);f.contract(b,base=1,method='file_check')
      for cid in ('AC1','DOD1'):checks.bind(f.owner,'p',task=b,task_version=1,contract_version=2,criterion=cid,path='result',expected_sha256=hashlib.sha256(b'expected').hexdigest(),reason='Synthetic exact file',key='b'+cid)
      f.ready_for_verification(b)
      for cid in ('AC1','DOD1'):checks.run(f.owner,'p',task=b,task_version=1,contract_version=2,criterion=cid,binding_revision=1,key='r'+cid)
      f.stage('Done',b,scope_reviewed=True)
     else:f.complete(b)
     f.complete(a);c=f.create('Downstream');f.contract(c);f.apply([dict(op='link',origin=c,target=a,kind='depends_on')])
     if mode=='blocker':TaskBlockerService(f.core).set(f.owner,'p',task=b,task_version=1,base_revision=0,blocked=True,reason='Prerequisite invalidated',next_action='Recheck prerequisite',gate='both')
     elif mode=='file':target.write_bytes(b'changed')
     else:f.core.file_checker=None
     self.assertEqual(f.s.view(f.owner,'p',b)['stage'],'Awaiting Verification');self.assertEqual(f.s.view(f.owner,'p',a)['stage'],'Awaiting Verification')
     with self.assertRaises(ContractError):f.complete(c)
     self.assertEqual(f.s._rows('p',a,'task_stage')[-1]['stage'],'Done')
     if mode=='blocker':
      TaskBlockerService(f.core).set(f.owner,'p',task=b,task_version=1,base_revision=1,blocked=False,reason='Rechecked prerequisite',next_action='Review current scope',gate='both')
      f.stage('Done',b,scope_reviewed=True);f.stage('Done',a,scope_reviewed=True);self.assertEqual(f.stage('Done',c,scope_reviewed=True)['stage'],'Done')
    finally:f.doCleanups()
 def test_overrun_is_durable_and_blocks_new_root_reservation(self):
  c=self.core;c.create_budget(self.owner,'p','r',100);c.reserve(self.owner,'p','r','first',10)
  for _ in range(2):
   with self.assertRaises(ContractError) as e:c.settle(self.owner,'p','r','first',1000)
   self.assertEqual(e.exception.code,'usage_overrun')
  self.assertEqual(c.db.execute('SELECT status,actual FROM reservations').fetchone(),('overrun',1000))
  self.assertEqual(c.db.execute("SELECT count(*) FROM audit WHERE action='budget_usage_recorded'").fetchone()[0],1)
  c.create_budget(self.owner,'p','newrun',100)
  for run in ('r','newrun'):
   with self.assertRaises(ContractError) as e:c.reserve(self.owner,'p',run,'next',1)
   self.assertEqual(e.exception.code,'budget_review_required')
  self.assertTrue(RoutingService(c).usage(self.owner,'p')['dispatch_blocked'])
  with self.assertRaises(ContractError):c.settle(self.owner,'p','r','first',None)
 def extractor(self,usage=None):
  core=self.core
  class Controlled:
   authorized=True;provider='controlled offline';model='fixture';max_output_tokens=40;calls=0;grant_id=None
   def __call__(self,source):
    self.calls+=1;self.reserved=core.db.execute('SELECT status FROM reservations WHERE key=?',('analysis_'+source['id'],)).fetchone()[0]
    return dict(source_id=source['id'],source_sha256=source['sha256'],coverage='partial',candidates=[])
  x=Controlled();x.usage=usage;return x
 def setup_dispatch(self,x):
  s=ConversationService(self.core);source=s.ingest(self.owner,'p',text='Synthetic bounded source.')
  self.core.create_budget(self.owner,'p','modelrun',1000)
  s.authorize_analysis(self.owner,'p',source_id=source['id'],key='grant',root_run='modelrun',reserved_tokens=100,provider=x.provider,model=x.model,max_output_tokens=x.max_output_tokens,expires_at=int(time.time())+3600,reason='Explicit fixture grant; no network')
  x.grant_id='grant';return s,source
 def test_no_grant_means_no_dispatch(self):
  x=self.extractor();s=ConversationService(self.core);source=s.ingest(self.owner,'p',text='Synthetic source')
  with self.assertRaises(ContractError):s.analyze(self.owner,'p',source['id'],x)
  self.assertEqual(x.calls,0)
 def test_reserve_before_send_actual_settlement_and_free_replay(self):
  x=self.extractor(dict(total_tokens=60));s,source=self.setup_dispatch(x);first=s.analyze(self.owner,'p',source['id'],x)
  self.assertEqual(x.reserved,'reserved');self.assertEqual(first['budget_status'],'settled');self.assertEqual(self.core.db.execute('SELECT actual FROM reservations').fetchone()[0],60)
  self.assertEqual(first,s.analyze(self.owner,'p',source['id'],x));self.assertEqual(x.calls,1)
 def test_unknown_usage_keeps_reservation(self):
  x=self.extractor();s,source=self.setup_dispatch(x);r=s.analyze(self.owner,'p',source['id'],x);self.assertEqual(r['budget_status'],'unknown');self.assertEqual(self.core.db.execute('SELECT status,actual,tokens FROM reservations').fetchone(),('unknown',None,100))
  self.core.settle(self.owner,'p','modelrun','analysis_'+source['id'],None);self.assertEqual(self.core.db.execute("SELECT count(*) FROM audit WHERE action='budget_usage_recorded'").fetchone()[0],1)
 def test_overrun_from_analysis_is_visible_and_durable(self):
  x=self.extractor(dict(total_tokens=800));s,source=self.setup_dispatch(x);r=s.analyze(self.owner,'p',source['id'],x);self.assertEqual(r['budget_status'],'overrun');self.assertEqual(self.core.db.execute('SELECT status,actual FROM reservations').fetchone(),('overrun',800));self.assertTrue(RoutingService(self.core).usage(self.owner,'p')['dispatch_blocked'])
 def test_model_change_and_expiry_prevent_send(self):
  x=self.extractor();s,source=self.setup_dispatch(x);x.model='other'
  with self.assertRaises(ContractError):s.analyze(self.owner,'p',source['id'],x)
  x.model='fixture'
  with patch('packages.capture.conversations.time.time',return_value=time.time()+7200):
   with self.assertRaises(ContractError):s.analyze(self.owner,'p',source['id'],x)
  self.assertEqual(x.calls,0);self.assertEqual(self.core.db.execute('SELECT count(*) FROM reservations').fetchone()[0],0)
 def test_audit_failure_rolls_back_reservation_before_dispatch(self):
  x=self.extractor();s,source=self.setup_dispatch(x);self.core.db.execute("CREATE TRIGGER fail_start BEFORE INSERT ON audit WHEN NEW.action='conversation_analysis_started' BEGIN SELECT RAISE(ABORT,'synthetic'); END")
  with self.assertRaises(ContractError):s.analyze(self.owner,'p',source['id'],x)
  self.assertEqual(x.calls,0);self.assertEqual(self.core.db.execute('SELECT count(*) FROM reservations').fetchone()[0],0)
 def test_source_output_cap_and_authority_changes_deny_dispatch(self):
  x=self.extractor();s,source=self.setup_dispatch(x)
  other=s.ingest(self.owner,'p',text='Other synthetic source')
  with self.assertRaises(ContractError):s.analyze(self.owner,'p',other['id'],x)
  x.max_output_tokens=41
  with self.assertRaises(ContractError):s.analyze(self.owner,'p',source['id'],x)
  x.max_output_tokens=40;a=self.core.authority;a.replace_grant(self.owner,'another',kind='agent',readable=frozenset({'p'}),writable=frozenset(),active=True,base_revision=a.revision())
  with self.assertRaises(ContractError):s.analyze(a.issue_scope('owner'),'p',source['id'],x)
  self.assertEqual(x.calls,0)
 def test_transport_timeout_clears_previous_usage(self):
  def fail(_):raise TimeoutError('Synthetic timeout')
  x=ResponsesExtractor(fail,model='fixture',max_output_tokens=100,authorized=True);x.usage=dict(total_tokens=1)
  with self.assertRaises(TimeoutError):x(dict(id='s',sha256='x',text='Synthetic'))
  self.assertIsNone(x.usage)

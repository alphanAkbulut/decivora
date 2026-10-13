"""Exact approved-file checks; no command execution or implicit source grant."""
import unittest,hashlib,os
from pathlib import Path
import test_task_workflow as fixtures
from packages.verification.files import FileChecker,FileVerificationService,MAX_BYTES
from packages.domain.source_event import ContractError
class FileTests(unittest.TestCase):
 def setUp(self):
  self.f=fixtures.WorkflowTests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.core=self.f.core;self.owner=self.f.owner;self.task=self.f.task;self.root=Path(self.f.temp.name)/'root';self.root.mkdir();self.file=self.root/'output.txt';self.file.write_bytes(b'expected');self.sha=hashlib.sha256(b'expected').hexdigest();self.core.file_checker=FileChecker(self.root);self.s=FileVerificationService(self.core);self.f.contract(self.task,base=1,method='file_check');self.n=0
 def bind(self,criterion='AC1',**kw):
  self.n+=1;args=dict(task=self.task,task_version=1,contract_version=2,criterion=criterion,path='output.txt',expected_sha256=self.sha,reason='This criterion is exactly this approved file content, not app behavior.',key='bind'+str(self.n));args.update(kw);return self.s.bind(self.owner,'p',**args)
 def check(self,criterion='AC1',revision=1,**kw):
  self.n+=1;args=dict(task=self.task,task_version=1,contract_version=2,criterion=criterion,binding_revision=revision,key='check'+str(self.n));args.update(kw);return self.s.run(self.owner,'p',**args)
 def test_file_hash_pass_requires_separate_current_criteria_and_completion(self):
  self.bind();self.bind('DOD1');self.f.ready_for_verification();self.assertEqual(self.check()['status'],'passed')
  with self.assertRaises(ContractError):self.f.stage('Done',scope_reviewed=True)
  self.check('DOD1');self.assertEqual(self.f.stage('Done',scope_reviewed=True)['stage'],'Done');self.file.write_bytes(b'changed');self.assertEqual(self.f.s.view(self.owner,'p',self.task)['stage'],'Awaiting Verification');self.assertEqual(self.check()['status'],'failed');self.assertEqual(self.f.s._rows('p',self.task,'task_stage')[-1]['stage'],'Done')
 def test_implementation_handoff_and_expected_hash_are_not_inferred(self):
  self.bind(expected_sha256=hashlib.sha256(b'wrong expectation').hexdigest())
  with self.assertRaises(ContractError):self.check()
  self.f.ready_for_verification();self.assertEqual(self.check()['status'],'failed')
 def test_symlink_traversal_directory_and_fifo_cannot_read(self):
  outside=Path(self.f.temp.name)/'outside';outside.write_text('Private outside content');(self.root/'link').symlink_to(outside);(self.root/'dir').mkdir();os.mkfifo(self.root/'pipe')
  for path in ['../outside','/etc/passwd','link','dir','pipe','dir/../output.txt']:
   with self.assertRaises(ContractError):self.core.file_checker.observe(path)
 def test_large_file_and_missing_target_preserve_unknown_and_failure(self):
  self.bind();self.f.ready_for_verification();self.file.write_bytes(b'x'*(MAX_BYTES+1));self.assertEqual(self.check()['status'],'unknown');self.file.unlink();self.assertEqual(self.check()['status'],'failed')
 def test_agent_cannot_bind_and_unconfigured_root_never_scans(self):
  self.core.file_checker=None
  with self.assertRaises(ContractError):self.bind()
  self.core.file_checker=FileChecker(self.root);a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision());self.owner=a.issue_scope('agent')
  with self.assertRaises(ContractError):self.bind()
 def test_changed_binding_contract_and_root_invalidate_old_observation(self):
  self.bind();self.f.ready_for_verification();self.check();self.bind(expected_sha256=hashlib.sha256(b'new content').hexdigest());self.assertEqual(self.f.s.view(self.owner,'p',self.task)['verification']['results'][0]['status'],'stale')
  with self.assertRaises(ContractError):self.check(revision=1)
  self.f.contract(self.task,base=2,method='file_check')
  with self.assertRaises(ContractError):self.check(revision=2)
 def test_observation_retry_is_receipt_not_new_execution(self):
  self.bind();self.f.ready_for_verification();first=self.check(key='same');again=self.check(key='same');self.assertEqual(first['observation'],again['observation']);self.assertEqual(len(self.s._rows('p','file_criterion_evidence')),1)
 def test_replaced_root_and_restored_unconfigured_checker_fail_closed(self):
  self.bind();self.f.ready_for_verification();self.check();old=self.root.with_name('oldroot');self.root.rename(old);self.root.mkdir();(self.root/'output.txt').write_bytes(b'expected')
  with self.assertRaises(ContractError):self.core.file_checker.observe('output.txt')
  self.core.file_checker=None;self.assertEqual(self.f.s.view(self.owner,'p',self.task)['verification']['results'][0]['status'],'unknown')

 def test_snapshot_read_ceiling_never_becomes_a_false_pass(self):
  rows=[dict(id='F'+str(i),statement='Exact independently selected file',method='file_check',required=True,applicable=True,applicability_reason='') for i in range(17)]
  dod=dict(id='DOD1',statement='Manual scope review',method='human_review',required=True,applicable=True,applicability_reason='')
  self.f.apply([dict(op='acceptance_contract',task=self.task,task_version=1,base_contract=2,criteria=rows,dod=[dod],reason='Explicit bounded-read test',acknowledged_changes=['AC1','DOD1'])]);self.f.ready_for_verification()
  for i,row in enumerate(rows):
   path='file'+str(i)+'.txt';(self.root/path).write_bytes(b'expected');self.s.bind(self.owner,'p',task=self.task,task_version=1,contract_version=3,criterion=row['id'],path=path,expected_sha256=self.sha,reason='Exact bytes only',key='b'+str(i));self.s.run(self.owner,'p',task=self.task,task_version=1,contract_version=3,criterion=row['id'],binding_revision=1,key='r'+str(i))
  view=self.f.s.view(self.owner,'p',self.task);self.assertFalse(view['verification']['passed']);self.assertEqual(view['verification']['results'][16]['status'],'unknown');self.assertTrue(self.core.file_read_limit_reached)

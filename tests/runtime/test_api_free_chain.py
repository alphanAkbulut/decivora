"""One deterministic receipt-to-file-evidence correction and offline recovery chain."""
import unittest,hashlib
from pathlib import Path
import test_conversations as fixtures
from packages.domain.task_workflow import TaskWorkflowService
from packages.verification.files import FileChecker,FileVerificationService
from packages.storage.workspace import Workspace
class ApiFreeChainTests(unittest.TestCase):
 def test_source_candidate_approval_file_done_correction_and_recovery(self):
  f=fixtures.ConversationTests();f.setUp();self.addCleanup(f.doCleanups);source=f.source();extractor=fixtures.Extractor();candidates=f.service.analyze(f.owner,'p',source['id'],extractor)['candidates'];view=f.service.view(f.owner,'p');result=f.service.accept(f.owner,'p',source_id=source['id'],key='humanaccept',selected=[candidates[0]['id']],base_revision=view['knowledge_revision']);task=next(iter(result['temp_ids'].values()));root=Path(f.temp.name)/'approved';root.mkdir();artifact=root/'output.txt';artifact.write_bytes(b'approved fixture');f.core.file_checker=FileChecker(root)
  row=lambda rid:dict(id=rid,statement='Approved exact fixture bytes',method='file_check',required=True,applicable=True,applicability_reason='');plan=f.core.plan(f.owner,'p','ac',[dict(op='acceptance_contract',task=task,task_version=1,base_contract=0,criteria=[row('AC1')],dod=[row('DOD1')],reason='Exact check scope approved',acknowledged_changes=[])]);f.core.apply(f.owner,plan,f.core.approve(f.owner,plan));w=TaskWorkflowService(f.core);v=FileVerificationService(f.core)
  for i,stage in enumerate(('In Progress','In Review','Awaiting Verification')):w.transition(f.owner,'p',task=task,task_version=1,base_revision=i,stage=stage,reason='Fixture handoff',key='stage'+str(i))
  for criterion in ('AC1','DOD1'):
   v.bind(f.owner,'p',task=task,task_version=1,contract_version=1,criterion=criterion,path='output.txt',expected_sha256=hashlib.sha256(b'approved fixture').hexdigest(),reason='Criterion means exactly these bytes',key='bind'+criterion);v.run(f.owner,'p',task=task,task_version=1,contract_version=1,criterion=criterion,binding_revision=1,key='run'+criterion)
  w.transition(f.owner,'p',task=task,task_version=1,base_revision=3,stage='Done',reason='Current scope and all file criteria reviewed',key='done',scope_reviewed=True);artifact.write_bytes(b'changed fixture');self.assertEqual(w.view(f.owner,'p',task)['stage'],'Awaiting Verification');v.run(f.owner,'p',task=task,task_version=1,contract_version=1,criterion='AC1',binding_revision=1,key='failedrun');self.assertEqual(w.view(f.owner,'p',task)['verification']['results'][0]['status'],'failed')
  backup=Path(f.temp.name)/'backup.sqlite';manifest=f.core.backup(f.owner,backup)
  with Workspace.restore(backup,Path(f.temp.name)/'restored.sqlite',manifest) as restored:
   owner=restored.authority.issue_scope('owner');self.assertEqual(fixtures.ConversationService(restored).view(owner,'p')['imports'][0]['source']['text'],fixtures.TEXT);self.assertFalse(TaskWorkflowService(restored).view(owner,'p',task)['verification']['passed']);self.assertEqual(TaskWorkflowService(restored)._rows('p',task,'task_stage')[-1]['stage'],'Done');self.assertEqual(restored.projection_digest(owner,'p'),manifest['projection_digests']['p'])
  self.assertEqual(extractor.calls,1) # Explicit fixture call, zero external models.

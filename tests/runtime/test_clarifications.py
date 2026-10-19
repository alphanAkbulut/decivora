import json,unittest
import test_dialogue_review as fixtures
from packages.capture.clarifications import ClarificationService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class ClarificationTests(unittest.TestCase):
 def setUp(self):
  self.f=fixtures.DialogueReviewTests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.service=ClarificationService(self.f.core)
 def proposal(self):
  f=self.f;request=f.prepare('Önce kontrolün kapsamını netleştirelim.')
  output=f.output(request);output['status_changes']=[];output['clarification_proposals']=[dict(task_id=f.fx.task,text=f.source['text'],quote=f.source['text'])]
  result=f.load(output);return result['clarification_proposals'][0]
 def accept(self,p,key='clarify'):
  f=self.f;return self.service.review(f.owner,'p',source_id=f.source['id'],proposal_id=p['id'],decision='accept',key=key,reason='Human reviewed task-linked clarification')
 def test_open_resolve_restart_preserves_task_and_history(self):
  p=self.proposal();f=self.f;before=f.fx.s.view(f.owner,'p',f.fx.task);records=f.core.records(f.owner,'p')['records'];opened=self.accept(p)
  self.assertFalse(opened['canonical_task_created']);self.assertEqual(self.accept(p),opened)
  self.assertEqual(f.core.records(f.owner,'p')['records'],records);self.assertEqual(f.fx.s.view(f.owner,'p',f.fx.task),before)
  row=self.service.view(f.owner,'p')[0];self.assertEqual(row['status'],'Open')
  fresh=f.service._context(f.owner,'p');self.assertEqual(fresh['clarifications'][0]['id'],p['id'])
  self.service.resolve(f.owner,'p',clarification=p['id'],base_revision=1,resolution='Kapsam yalnız örnek dosya geri yüklemesidir.',key='resolve')
  with Workspace(f.fx.path,'w') as core:self.assertEqual(ClarificationService(core).view(core.authority.issue_scope('owner'),'p')[0]['status'],'Resolved')
  with self.assertRaises(ContractError):self.service.resolve(f.owner,'p',clarification=p['id'],base_revision=1,resolution='Another scope',key='stale')
  backup=f.fx.path.parent/'clarification-backup.sqlite';manifest=f.core.backup(f.owner,backup)
  with Workspace.restore(backup,f.fx.path.parent/'clarification-restored.sqlite',manifest) as restored:self.assertEqual(ClarificationService(restored).view(restored.authority.issue_scope('owner'),'p')[0]['status'],'Resolved')
 def test_unknown_task_nonliteral_and_invalid_fields_rejected(self):
  f=self.f;req=f.prepare('Scope question.');out=f.output(req);out['status_changes']=[]
  for p in [dict(task_id='missing',text='Scope question.',quote='Scope question.'),dict(task_id=f.fx.task,text='invented',quote='Scope question.'),dict(task_id=[],text='Scope question.',quote='Scope question.')]:
   out['clarification_proposals']=[p]
   with self.assertRaises(ContractError):f.load(out)
  self.assertEqual(self.service.view(f.owner,'p'),[])
 def test_stale_task_and_unauthorized_review_do_not_open(self):
  p=self.proposal();f=self.f;f.fx.stage('In Progress')
  with self.assertRaises(ContractError):self.accept(p)
  with self.assertRaises(ContractError):self.service.view(f.owner,'other')
  self.assertEqual(self.service.view(f.owner,'p'),[])
  a=f.core.authority;a.replace_grant(f.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision())
  with self.assertRaises(ContractError):self.service.review(a.issue_scope('agent'),'p',source_id=f.source['id'],proposal_id=p['id'],decision='accept',key='agent_review',reason='Agent cannot approve')
 def test_audit_failure_rolls_back_clarification_only(self):
  p=self.proposal();f=self.f
  f.core.db.execute("CREATE TRIGGER fail_clarification BEFORE INSERT ON audit WHEN NEW.action='clarification_reviewed' BEGIN SELECT RAISE(ABORT,'fixture'); END")
  with self.assertRaises(Exception):self.accept(p)
  self.assertEqual(self.service.view(f.owner,'p'),[]);self.assertEqual(len(f.core.records(f.owner,'p')['records']),1)

if __name__=='__main__':unittest.main()

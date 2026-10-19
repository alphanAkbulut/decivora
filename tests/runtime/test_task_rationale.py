"""Persisted AND/OR and tri-state facts, no model invocation."""
import unittest,json
import test_task_workflow as fixtures
from packages.domain.task_rationale import TaskRationaleService
from packages.domain.decision_impact import DecisionImpactService
from packages.domain.source_event import ContractError

class TaskRationaleTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.WorkflowTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups);self.core=self.fx.core;self.owner=self.fx.owner;self.task=self.fx.task;self.service=TaskRationaleService(self.core)
  result=self.fx.apply([dict(op='create',id=k,body=dict(type='Decision',title=k,description='Recorded reason')) for k in ['a','b']]);self.a=result['temp_ids']['a'];self.b=result['temp_ids']['b'];self.fx.apply([dict(op='link',origin=self.task,target=k,kind='required_by') for k in (self.a,self.b)])
 def save(self,mode='all',b=True,key='rationale',**kw):
  request=dict(task=self.task,task_version=1,base_revision=self.core.project(self.owner,'p')['knowledge_revision'],expression={mode:[dict(ref=r,revision=1) for r in (self.a,self.b)]},facts={self.a:dict(revision=1,valid=True),self.b:dict(revision=1,valid=b)},reviewed_complete=True,reason='Human reviewed all current recorded reasons',key=key);request.update(kw);self.request=request;return self.service.save(self.owner,'p',**request)
 def impact(self,key='impact'):
  result=DecisionImpactService(self.core).preview(self.owner,'p',decision=self.a,decision_version=1,base_revision=self.core.project(self.owner,'p')['knowledge_revision'],key=key);return next(p for p in result['proposals'] if p['record']==self.task)
 def test_and_becomes_false_when_one_reason_is_retired(self):
  self.save();p=self.impact();self.assertTrue(p['before']);self.assertFalse(p['after']);self.assertEqual(self.fx.s.view(self.owner,'p',self.task)['stage'],'To Do')
 def test_or_survives_when_other_reason_is_explicitly_valid(self):
  self.save('any');p=self.impact();self.assertTrue(p['before']);self.assertTrue(p['after'])
 def test_or_unknown_reason_is_not_automatic_false(self):
  self.save('any',b=None);self.assertIsNone(self.impact()['after'])
 def test_cannot_omit_known_reason_or_invent_fact(self):
  with self.assertRaises(ContractError):self.save(expression=dict(any=[dict(ref=self.a,revision=1)]),facts={self.a:dict(revision=1,valid=True)})
  self.assertIsNone(self.service.view(self.owner,'p',self.task))
 def test_review_acknowledgment_and_current_knowledge_required(self):
  for kw in [dict(reviewed_complete=False),dict(base_revision=0),dict(task_version=99)]:
   with self.subTest(kw=kw),self.assertRaises(ContractError):self.save(**kw)
 def test_duplicate_and_integer_validity_are_rejected(self):
  for kw in [dict(expression=dict(any=[dict(ref=self.a,revision=1),dict(ref=self.a,revision=1)])),dict(facts={self.a:dict(revision=1,valid=1),self.b:dict(revision=1,valid=True)})]:
   with self.assertRaises(ContractError):self.save(**kw)
 def test_stale_rationale_is_unknown_not_replaced_by_single_reason_checkbox(self):
  self.save('any');self.fx.apply([dict(op='update',id=self.b,base_version=1,body=dict(type='Decision',title='Changed',description='Changed reason'))]);self.assertTrue(self.service.view(self.owner,'p',self.task)['stale']);self.assertIsNone(self.impact()['after'])
 def test_retry_and_history_and_old_impact_invalidation(self):
  first=self.save();self.assertEqual(self.service.save(self.owner,'p',**self.request),first);self.impact('old_impact');self.save('any',key='second');self.assertEqual(self.service.view(self.owner,'p',self.task)['revision'],2)
  self.assertTrue(self.core.impact_run(self.owner,'p','old_impact')['stale'])
 def test_done_requires_reverification_after_rationale_change(self):
  self.save();self.fx.complete();self.save('any',key='changed');view=self.fx.s.view(self.owner,'p',self.task);self.assertEqual(view['stage'],'Awaiting Verification');self.assertTrue(any(h['stage']=='Done' for h in view['history']))
 def test_rationale_write_failure_rolls_back_revision_and_history(self):
  before=list(self.core.db.iterdump());self.core.db.execute("CREATE TRIGGER fail_rationale BEFORE INSERT ON audit WHEN NEW.action='task_rationale_confirmed' BEGIN SELECT RAISE(ABORT,'fixture'); END")
  with self.assertRaises(ContractError):self.save()
  self.assertEqual([s for s in self.core.db.iterdump() if 'CREATE TRIGGER fail_rationale' not in s],before)
 def test_nested_expression_uses_existing_three_valued_kernel(self):
  self.save(expression=dict(any=[dict(all=[dict(ref=self.a,revision=1),dict(ref=self.b,revision=1)])]));self.assertFalse(self.impact()['after'])
 def test_agent_cannot_confirm_human_rationale(self):
  self.save();request=self.request;a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision())
  with self.assertRaises(ContractError):self.service.save(a.issue_scope('agent'),'p',**dict(request,key='agent'))

 def test_replacement_edge_invalidates_previously_confirmed_validity_assumptions(self):
  self.save('any');new=self.fx.apply([dict(op='create',id='new',body=dict(type='Decision',title='Replacement',description='New choice')),dict(op='link',origin='new',target=self.b,kind='supersedes')]);self.assertTrue(self.service.view(self.owner,'p',self.task)['stale']);self.assertIsNone(self.impact()['after'])
 def test_backup_restore_preserves_rationale_and_expression(self):
  from pathlib import Path
  from packages.storage.workspace import Workspace
  self.save('any');backup=Path(self.fx.temp.name)/'rationale-backup.sqlite';manifest=self.core.backup(self.owner,backup)
  with Workspace.restore(backup,Path(self.fx.temp.name)/'rationale-restored.sqlite',manifest) as core:
   value=TaskRationaleService(core).view(core.authority.issue_scope('owner'),'p',self.task);self.assertFalse(value['stale']);self.assertIn('any',value['expression'])

 def test_rationale_read_cache_does_not_leak_mutations_or_stale_snapshot(self):
  self.save('any')
  with self.core.read_snapshot():
   first=self.service.view(self.owner,'p',self.task);first['facts'][self.a]['valid']=False
   self.assertTrue(self.service.view(self.owner,'p',self.task)['facts'][self.a]['valid'])
  self.save('all',key='new_snapshot');self.assertIn('all',self.service.view(self.owner,'p',self.task)['expression'])

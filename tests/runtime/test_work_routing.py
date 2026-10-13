"""Routing is a label, not an execution grant; unknown consumption stays unknown."""
import unittest
import test_task_workflow as fixture_tests
from packages.domain.work_routing import RoutingService
from packages.domain.source_event import ContractError
class RoutingTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixture_tests.WorkflowTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups);self.core=self.fixture.core;self.owner=self.fixture.owner;self.task=self.fixture.task;self.s=RoutingService(self.core)
 def route(self,**kw):
  args=dict(task=self.task,task_version=1,base_revision=0,work_class='DETERMINISTIC',executor='HUMAN',human_suitable=True,reason='Human can review a simple check',key='r1');args.update(kw);return self.s.set(self.owner,'p',**args)
 def test_routing_persists_retry_without_dispatch_and_stale_key_rejected(self):
  first=self.route();self.assertEqual(first,self.route());self.assertFalse(first['automatic_dispatch']);self.assertEqual(first['current']['executor'],'HUMAN')
  with self.assertRaises(ContractError):self.route(executor='AGENT')
  self.assertEqual(self.fixture.s.view(self.owner,'p',self.task)['stage'],'To Do')
 def test_human_decision_cannot_be_routed_to_agent(self):
  with self.assertRaises(ContractError):self.route(work_class='HUMAN_DECISION',executor='AGENT')
  self.assertEqual(self.s.view(self.owner,'p',self.task)['revision'],0)
 def test_task_update_requires_new_routing_review(self):
  self.route();self.fixture.apply([dict(op='update',id=self.task,base_version=1,body=dict(type='Task',title='Changed task',description='Changed scope'))]);self.assertTrue(self.s.view(self.owner,'p',self.task)['stale'])
  with self.assertRaises(ContractError):self.route(key='r2',base_revision=1)
 def test_unknown_usage_holds_reservation_and_does_not_become_zero(self):
  self.core.create_budget(self.owner,'p','run',100);self.core.reserve(self.owner,'p','run','child1',60);self.core.settle(self.owner,'p','run','child1',None)
  usage=self.s.usage(self.owner,'p');run=usage['runs'][0];self.assertIsNone(run['actual_tokens']);self.assertEqual(run['held_tokens'],60);self.assertEqual(run['available_tokens'],40);self.assertIsNone(usage['external_chat_tokens']);self.assertIsNone(run['money'])
  with self.assertRaises(ContractError):self.core.reserve(self.owner,'p','run','child2',50)
  self.core.settle(self.owner,'p','run','child1',20);run=self.s.usage(self.owner,'p')['runs'][0];self.assertEqual(run['actual_tokens'],20);self.assertEqual(run['held_tokens'],0)
 def test_agent_cannot_change_human_routing(self):
  a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision());self.owner=a.issue_scope('agent')
  with self.assertRaises(ContractError):self.route()
 def test_usage_project_isolation(self):
  with self.assertRaises(ContractError):self.s.usage(self.owner,'foreign')

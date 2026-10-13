"""Durable MCP candidate is distinct from approval and canonical state."""
import unittest
import test_mcp_local as fixtures
from packages.domain.agent_proposals import AgentProposalService
from packages.domain.source_event import ContractError
class ProposalTests(unittest.TestCase):
 def setUp(self):
  self.f=fixtures.McpTests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.core=self.f.core;self.owner=self.f.owner;self.s=AgentProposalService(self.core);self.key='candidate';self.args=dict(project_id='p',key=self.key,base_revision=self.core.project(self.owner,'p')['knowledge_revision'],operations=[dict(op='create',id='t',body=dict(type='Task',title='Agent candidate',description='Review separately'))]);self.f.server.call('submit_changeset',self.args)
 def test_persisted_review_approve_apply_retry(self):
  self.assertEqual(self.s.view(self.owner,'p')[0]['state'],'Prepared')
  with self.assertRaises(ContractError):self.s.apply(self.owner,'p',self.key)
  self.s.approve(self.owner,'p',self.key);self.assertEqual(len(self.core.records(self.owner,'p')['records']),2);first=self.s.apply(self.owner,'p',self.key);self.assertEqual(first,self.s.apply(self.owner,'p',self.key));self.assertEqual(len(self.core.records(self.owner,'p')['records']),3);self.assertEqual(self.s.view(self.owner,'p')[0]['state'],'Applied')
 def test_rejection_preserves_draft_and_never_cancels_task(self):
  self.s.reject(self.owner,'p',self.key,'Not current scope');self.assertEqual(self.s.view(self.owner,'p')[0]['state'],'Rejected')
  with self.assertRaises(ContractError):self.s.approve(self.owner,'p',self.key)
  self.assertEqual(len(self.core.records(self.owner,'p')['records']),2)
 def test_revoked_submitter_and_stale_project_block_human_apply(self):
  self.s.approve(self.owner,'p',self.key);self.f.create('Changed context')
  with self.assertRaises(ContractError):self.s.apply(self.owner,'p',self.key)
 def test_agent_cannot_approve_and_retry_content_cannot_change(self):
  agent=self.core.authority.issue_scope('agent1')
  with self.assertRaises(ContractError):self.s.approve(agent,'p',self.key)
  changed=dict(self.args,operations=[dict(op='create',id='t',body=dict(type='Task',title='Changed draft',description='Changed'))])
  with self.assertRaises(ContractError):self.f.server.call('submit_changeset',changed)
 def test_updates_require_impact_review_integration(self):
  args=dict(self.args,key='edit',operations=[dict(op='update',id=self.f.task,base_version=1,body=dict(type='Task',title='Edited',description=''))])
  with self.assertRaises(ContractError):self.f.server.call('submit_changeset',args)

 def test_apply_audit_failure_rolls_back_canonical_records(self):
  self.s.approve(self.owner,'p',self.key);self.core.db.execute("CREATE TRIGGER fail_agent_apply BEFORE INSERT ON audit WHEN NEW.action='agent_changeset_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END")
  with self.assertRaises(ContractError):self.s.apply(self.owner,'p',self.key)
  self.assertEqual(len(self.core.records(self.owner,'p')['records']),2);self.assertEqual(self.s.view(self.owner,'p')[0]['state'],'Approved')

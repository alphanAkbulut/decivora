"""Conversation relation bridge; synthetic outputs, no model dispatch."""
import json,unittest
from pathlib import Path
import test_task_workflow as fixtures
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.dialogue_relations import DialogueRelationService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace
from packages.domain.decision_impact import DecisionImpactService

class DialogueRelationTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.WorkflowTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups);self.core=self.fx.core;self.owner=self.fx.owner;self.sources=ConversationService(self.core);self.dialogue=DialogueReviewService(self.core);self.relations=DialogueRelationService(self.core)
  self.decision=self.fx.apply([dict(op='create',id='d',body=dict(type='Decision',title='SQLite storage',description='Use SQLite'))])['temp_ids']['d']
 def prepare(self,target=None,kind='required_by'):
  self.source=self.sources.ingest(self.owner,'p',text='The existing task is required because of the SQLite storage decision.')
  request=self.dialogue.prepare(self.owner,'p',source_id=self.source['id']);self.output=dict(source_id=self.source['id'],source_sha256=self.source['sha256'],context_sha256=request['context_sha256'],coverage='complete',candidates=[],status_changes=[],answer_proposals=[],relation_proposals=[dict(origin=self.fx.task,target=target or self.decision,kind=kind,quote=self.source['text'])]);return self.output
 def load(self):return self.dialogue.import_response(self.owner,'p',source_id=self.source['id'],response_text=json.dumps(self.output))['relation_proposals'][0]
 def review(self,p,decision='accept',key='review_relation'):
  return self.relations.review(self.owner,'p',source_id=self.source['id'],proposal_id=p['id'],decision=decision,key=key,reason='Human confirmed exact source, direction and record revisions')
 def test_relation_is_only_added_after_human_review_and_feeds_impact(self):
  self.prepare();p=self.load();self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],0);receipt=self.review(p);self.assertEqual(self.review(p),receipt)
  self.assertEqual(self.core.db.execute('SELECT origin,target,kind,state FROM edges').fetchone(),(self.fx.task,self.decision,'required_by','asserted'))
  base=self.core.project(self.owner,'p')['knowledge_revision'];impact=DecisionImpactService(self.core).preview(self.owner,'p',decision=self.decision,decision_version=1,base_revision=base,key='relation_impact')
  self.assertTrue(any(item['record']==self.fx.task for item in impact['proposals']));self.assertEqual(self.fx.s.view(self.owner,'p',self.fx.task)['stage'],'To Do')
  self.assertEqual(self.sources.view(self.owner,'p')['imports'][0]['relation_proposals'][0]['state'],'Applied')
 def test_reject_and_defer_leave_graph_unchanged(self):
  self.prepare();p=self.load();self.review(p,'defer');self.review(p,'reject','reject');self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],0)
  with self.assertRaises(ContractError):self.review(p,key='closed')
 def test_wrong_quote_type_direction_and_unknown_record_rejected(self):
  self.prepare();base=json.loads(json.dumps(self.output))
  for changes in [dict(quote='fabricated'),dict(origin=self.decision,target=self.fx.task),dict(target='foreign_record'),dict(kind='supersedes'),dict(origin=self.fx.task,target=self.fx.task)]:
   self.output=json.loads(json.dumps(base));self.output['relation_proposals'][0].update(changes)
   with self.subTest(changes=changes),self.assertRaises(ContractError):self.load()
  self.assertEqual(self.sources._rows('p','conversation_analysis_finished'),[])
 def test_duplicate_or_preexisting_even_ended_edge_is_not_silently_reactivated(self):
  self.prepare();self.output['relation_proposals']*=2
  with self.assertRaises(ContractError):self.load()
  self.fx.apply([dict(op='link',origin=self.fx.task,target=self.decision,kind='required_by')]);self.fx.apply([dict(op='end_link',origin=self.fx.task,target=self.decision,kind='required_by',base_version=1,state='ended')]);self.prepare()
  with self.assertRaises(ContractError):self.load()
 def test_changed_endpoint_version_blocks_old_proposal(self):
  self.prepare();p=self.load();self.fx.apply([dict(op='update',id=self.decision,base_version=1,body=dict(type='Decision',title='Changed decision',description='Remote storage'))])
  with self.assertRaises(ContractError):self.review(p)
  self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],0)
 def test_same_edge_added_elsewhere_blocks_old_review(self):
  self.prepare();p=self.load();self.fx.apply([dict(op='link',origin=self.fx.task,target=self.decision,kind='required_by')])
  with self.assertRaises(ContractError):self.review(p)
  self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],1)
 def test_receipt_write_failure_rolls_back_edge_events_and_approval(self):
  self.prepare();p=self.load();before=list(self.core.db.iterdump());self.core.db.execute("CREATE TRIGGER fail_relation_receipt BEFORE INSERT ON audit WHEN NEW.action='conversation_relation_reviewed' BEGIN SELECT RAISE(ABORT,'fixture'); END")
  with self.assertRaises(ContractError):self.review(p)
  self.assertEqual([s for s in self.core.db.iterdump() if 'CREATE TRIGGER fail_relation_receipt' not in s],before)
 def test_dependency_cycle_cannot_commit(self):
  second=self.fx.create('Prerequisite');self.prepare(target=second,kind='depends_on');p=self.load();self.fx.apply([dict(op='link',origin=second,target=self.fx.task,kind='depends_on')])
  with self.assertRaises(ContractError):self.review(p)
  self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],1)
 def test_unrelated_change_does_not_block_independent_review(self):
  self.prepare();p=self.load();self.fx.create('Unrelated task');self.review(p);self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],1)
 def test_agent_foreign_project_and_changed_authority_cannot_apply(self):
  self.prepare();p=self.load();a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision())
  with self.assertRaises(ContractError):self.relations.review(a.issue_scope('agent'),'p',source_id=self.source['id'],proposal_id=p['id'],decision='accept',key='agent',reason='Not human')
  self.owner=a.issue_scope('owner')
  with self.assertRaises(ContractError):self.review(p)
  with self.assertRaises(ContractError):self.relations.view(self.owner,'foreign',self.source['id'],{})
 def test_restore_preserves_source_provenance_and_graph(self):
  self.prepare();p=self.load();self.review(p);backup=Path(self.fx.temp.name)/'relation-backup.sqlite';manifest=self.core.backup(self.owner,backup)
  with Workspace.restore(backup,Path(self.fx.temp.name)/'restored-relation.sqlite',manifest) as core:
   owner=core.authority.issue_scope('owner');item=ConversationService(core).view(owner,'p')['imports'][0]['relation_proposals'][0];self.assertEqual(item['state'],'Applied');self.assertEqual(item['history'][0]['actor'],'owner');self.assertEqual(item['history'][0]['source'],self.source['id']);self.assertEqual(core.db.execute('SELECT count(*) FROM edges').fetchone()[0],1)

 def test_private_relation_does_not_leak_through_preexisting_public_records_to_mcp(self):
  from packages.mcp.server import Server
  a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset(),active=True,base_revision=a.revision());self.owner=a.issue_scope('owner');self.fx.owner=self.owner
  agent=a.issue_scope('agent');server=Server(self.fx.path,self.core.workspace,'agent')
  self.assertTrue(server._visible(self.core,agent,'p',self.fx.task));self.prepare();p=self.load();self.review(p)
  with self.core.read_snapshot():
   self.assertFalse(server._visible(self.core,agent,'p',self.fx.task));self.assertFalse(server._visible(self.core,agent,'p',self.decision))

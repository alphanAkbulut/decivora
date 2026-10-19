"""Source capacity and bounded reads on temporary databases; no host/model calls."""
import base64,json,unittest
from pathlib import Path
from unittest.mock import patch
import test_questions as fixtures
from packages.capture.conversations import ConversationService
from packages.capture.processing_queue import ConversationQueue
from packages.capture import source_pages
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class SourcePageTests(unittest.TestCase):
 def setUp(self):
  fixtures.QuestionTests.setUp(self);self.service=ConversationService(self.core)
 def seed(self,count):
  return [self.service.ingest(self.owner,'p',text='Synthetic source '+str(i)+' — '+'x'*160) for i in range(count)]
 def test_thousand_sources_paged_without_loss_capacity_and_indexed_exact_lookup(self):
  sources=self.seed(1000);first=self.service.view(self.owner,'p');self.assertEqual(first['total'],1000);self.assertEqual(len(first['imports']),25)
  seen=[];cursor=None
  while True:
   page=self.service.view(self.owner,'p',cursor=cursor)
   seen.extend(i['source']['id'] for i in page['imports']);cursor=page['next_cursor']
   if cursor is None:break
  self.assertEqual(seen,[s['id'] for s in sources]);self.assertEqual(len(set(seen)),1000)
  self.assertEqual(self.service.ingest(self.owner,'p',text=sources[0]['text'])['id'],sources[0]['id'])
  with self.assertRaises(ContractError):self.service.ingest(self.owner,'p',text='Capacity overflow source')
  self.assertEqual(source_pages.count(self.core,'p'),1000)
  plan=self.core.db.execute("EXPLAIN QUERY PLAN SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND json_extract(ref,'$.id')=?",('w','p',sources[-1]['id'])).fetchall()
  self.assertTrue(any('conversation_source_id' in str(row) for row in plan))
  queue=ConversationQueue(self.core).view(self.owner,'p');self.assertEqual(queue['total'],1000);self.assertEqual(len(queue['items']),25);self.assertTrue(queue['items_truncated']);self.assertEqual(queue['counts'],{'Waiting for model':1000})
 def test_snapshot_page_does_not_shift_when_new_source_arrives(self):
  sources=self.seed(30);first=self.service.view(self.owner,'p');self.service.ingest(self.owner,'p',text='A new arrival after snapshot')
  second=self.service.view(self.owner,'p',cursor=first['next_cursor'])
  self.assertEqual([s['source']['id'] for s in second['imports']],[s['id'] for s in sources[25:]])
  self.assertIsNone(second['next_cursor']);self.assertEqual(self.service.view(self.owner,'p')['total'],31)
 def test_source_ids_and_indexes_survive_backup_restore(self):
  sources=self.seed(35);backup=self.path.with_name('sources-backup.sqlite');manifest=self.core.backup(self.owner,backup)
  with Workspace.restore(backup,self.path.with_name('sources-restored.sqlite'),manifest) as core:
   service=ConversationService(core);owner=core.authority.issue_scope('owner');first=service.view(owner,'p');last=service.view(owner,'p',cursor=first['next_cursor'])
   self.assertEqual(last['imports'][-1]['source']['id'],sources[-1]['id']);self.assertTrue(core.db.execute("SELECT 1 FROM sqlite_master WHERE name='conversation_source_id'").fetchone())
 def test_invalid_foreign_project_and_fabricated_anchor_cursors_are_rejected(self):
  self.seed(30);cursor=self.service.view(self.owner,'p')['next_cursor'];a=self.core.authority
  a.replace_grant(self.owner,'owner',kind='human',readable=frozenset({'p','q'}),writable=frozenset({'p','q'}),active=True,base_revision=a.revision());self.owner=a.issue_scope('owner');self.core.create_project(self.owner,'q','Other')
  with self.assertRaises(ContractError):self.service.view(self.owner,'q',cursor=cursor)
  bad=json.loads(base64.urlsafe_b64decode(cursor));bad['after']=bad['ceiling']-1
  for value in ('', 'not-base64!', 'a'*513, base64.urlsafe_b64encode(json.dumps(bad).encode()).decode()):
   with self.subTest(cursor=value[:20]),self.assertRaises(ContractError):self.service.view(self.owner,'p',cursor=value)
 def test_read_is_side_effect_free_and_selected_page_does_not_parse_all_source_bodies(self):
  self.seed(60);before=list(self.core.db.iterdump())
  original=self.service._rows
  def rows(project,action):
   if action=='conversation_imported':self.fail('Page read loaded the whole source history')
   return original(project,action)
  with patch.object(self.service,'_rows',side_effect=rows):self.assertEqual(len(self.service.view(self.owner,'p')['imports']),25)
  self.assertEqual(list(self.core.db.iterdump()),before)
 def test_ui_http_pages_require_session_and_do_not_accept_foreign_query_fields(self):
  import test_local_app
  fixture=test_local_app.LocalAppTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  self.assertEqual(fixture.call('/api/conversations',headers={})[0],401)
  for i in range(30):fixture.server.app.command(dict(action='import_conversation',text='UI source '+str(i)))
  code,first,_=fixture.call('/api/conversations');self.assertEqual(code,200);self.assertEqual(first['total'],30);self.assertEqual(len(first['imports']),25)
  from urllib.parse import quote
  code,last,_=fixture.call('/api/conversations?cursor='+quote(first['next_cursor']));self.assertEqual(code,200);self.assertEqual(len(last['imports']),5)
  self.assertEqual(fixture.call('/api/conversations?limit=500')[0],400)
  self.assertEqual(fixture.call('/api/conversations?cursor=invalid')[0],409)
  self.assertEqual(fixture.call('/api/conversations?source_id=source_missing')[0],409)
  self.assertEqual(fixture.call('/api/conversations?source_id=source_missing&cursor=invalid')[0],400)

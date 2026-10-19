"""Real source/store/worker/review wiring; all provider output is synthetic."""
import json,time,unittest
from pathlib import Path
import test_questions as fixtures
from packages.capture.conversations import ConversationService
from packages.capture.processing_queue import ConversationQueue
from packages.capture.responses_extractor import ResponsesExtractor
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace
from apps.local_ui.server import LocalApp

class QueueTests(unittest.TestCase):
 def setUp(self):
  fixtures.QuestionTests.setUp(self);self.sources=ConversationService(self.core);self.queue=ConversationQueue(self.core);self.calls=[]
 def source(self,text='Please add backup support.'):
  return self.sources.ingest(self.owner,'p',text=text)
 def grant(self,source,unknown=False):
  run='run_'+source['id'];key='grant_'+source['id'];self.core.create_budget(self.owner,'p',run,8000)
  def send(payload):
   self.assertFalse(self.core.db.in_transaction);self.calls.append(payload)
   output=dict(source_id=source['id'],source_sha256=source['sha256'],coverage='partial',candidates=[dict(type='Task',title='Backup support',quote=source['text'],intent='planned')])
   return dict(status='completed',usage=None if unknown else dict(total_tokens=100),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])
  model=ResponsesExtractor(send,model='fixture',max_output_tokens=512,authorized=True,grant_id=key)
  self.sources.authorize_analysis(self.owner,'p',source_id=source['id'],key=key,root_run=run,reserved_tokens=8000,provider=model.provider,model=model.model,max_output_tokens=512,expires_at=int(time.time())+3600,reason='Synthetic fixture; no external network.')
  return model
 def test_source_outbox_atomic_dedup_and_read_only_progress(self):
  source=self.source();self.source();rows=self.sources._rows('p','conversation_enqueued');self.assertEqual(len(rows),1)
  self.assertNotIn('text',rows[0]);before=list(self.core.db.iterdump());view=self.queue.view(self.owner,'p')
  self.assertEqual(view['counts'],{'Waiting for model':1});self.assertEqual(view['items'][0]['source_id'],source['id'])
  self.assertNotIn(source['text'],json.dumps(view));self.assertEqual(list(self.core.db.iterdump()),before)
 def test_outbox_write_failure_rolls_back_source(self):
  self.core.db.execute("CREATE TRIGGER fail_queue BEFORE INSERT ON audit WHEN NEW.action='conversation_enqueued' BEGIN SELECT RAISE(ABORT,'fixture'); END")
  with self.assertRaises(ContractError):self.source()
  self.assertEqual(self.sources._rows('p','conversation_imported'),[])
 def test_no_configuration_or_grant_never_constructs_or_dispatches_provider(self):
  self.source();self.assertEqual(self.queue.process(self.owner,'p')['attempted'],0)
  self.queue.process(self.owner,'p',extractor_factory=lambda *args:self.fail('No grant; no factory call'))
  self.assertEqual(self.calls,[])
 def test_capture_queue_provider_proposal_then_separate_human_task_accept(self):
  source=self.source();model=self.grant(source)
  result=self.queue.process(self.owner,'p',extractor_factory=lambda *args:model)
  self.assertEqual(result['queue']['counts'],{'Ready for review':1});self.assertEqual(len(self.calls),1)
  self.assertEqual(self.core.records(self.owner,'p')['records'],[])
  view=self.sources.view(self.owner,'p');candidate=view['imports'][0]['candidates'][0]
  self.sources.accept(self.owner,'p',source_id=source['id'],key='human_accept',selected=[candidate['id']],base_revision=view['knowledge_revision'])
  self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)
  self.assertEqual(self.queue.view(self.owner,'p')['applied_sources'],1)
  self.queue.process(self.owner,'p',extractor_factory=lambda *args:self.fail('Finished source re-dispatched'))
  self.assertEqual(len(self.calls),1)
 def test_unknown_started_receipt_not_retried(self):
  source=self.source();self.grant(source)
  with self.core.transaction():self.sources._put(self.owner,'p','conversation_analysis_started',dict(source=source['id']))
  self.assertEqual(self.queue.view(self.owner,'p')['counts'],{'Analysis unknown':1})
  self.queue.process(self.owner,'p',extractor_factory=lambda *args:self.fail('Unknown source retried'))
 def test_batch_limit_and_unknown_usage_stop_additional_work(self):
  first=self.source();second=self.source('Please add a restore test.');models={first['id']:self.grant(first,True),second['id']:self.grant(second)}
  result=self.queue.process(self.owner,'p',extractor_factory=lambda source,grant:models[source['id']],limit=2)
  self.assertEqual(result['attempted'],1);self.assertEqual(len(self.calls),1)
  self.assertEqual(result['queue']['counts']['Waiting for model'],1)
 def test_source_outbox_and_review_progress_survive_backup_restore(self):
  self.source();backup=self.path.with_name('queue-backup.sqlite');manifest=self.core.backup(self.owner,backup)
  with Workspace.restore(backup,self.path.with_name('queue-restore.sqlite'),manifest) as core:
   view=ConversationQueue(core).view(core.authority.issue_scope('owner'),'p');self.assertEqual(view['total'],1);self.assertTrue(view['items'][0]['durable_outbox'])
 def test_scope_and_limit_cannot_expand_queue_pass(self):
  for limit in (0,11,True):
   with self.assertRaises(ContractError):self.queue.process(self.owner,'p',limit=limit)
  with self.assertRaises(ContractError):self.queue.view(self.owner,'foreign')
 def test_ui_command_and_operations_progress_do_not_activate_model(self):
  app=LocalApp(Path(self.temp.name)/'ui.sqlite')
  app.command(dict(action='import_conversation',text='Please add a backup test.'))
  result=app.command(dict(action='process_conversation_queue',limit=1))
  self.assertEqual(result['status'],'Waiting for model');self.assertEqual(app.state()['tasks'],[])
  operations=app.operations_view();self.assertEqual(operations['conversation_queue']['total'],1)
  self.assertNotIn('Please add',json.dumps(operations));self.assertTrue(any(v['action']=='process_conversation_queue' for v in operations['runs']))
 def test_worker_reaches_authorized_source_beyond_first_ui_page_and_accepts_it(self):
  for i in range(30):self.source('Unconfigured source '+str(i))
  target=self.source('Please add restore support.');model=self.grant(target)
  self.assertEqual(len(self.sources.view(self.owner,'p')['imports']),25)
  result=self.queue.process(self.owner,'p',extractor_factory=lambda source,grant:model)
  self.assertEqual(result['attempted'],1);self.assertEqual(len(self.calls),1)
  selected=self.sources.view(self.owner,'p',source_id=target['id']);candidate=selected['imports'][0]['candidates'][0]
  self.sources.accept(self.owner,'p',source_id=target['id'],key='accept_last_source',selected=[candidate['id']],base_revision=selected['knowledge_revision'])
  self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)

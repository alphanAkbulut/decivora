"""Synthetic credentials only; no real secret, provider or user-data scan."""
import json,os,sqlite3,unittest
from pathlib import Path
from unittest.mock import patch
import test_questions as fixtures
from packages.capture.conversations import ConversationService,anchored
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.responses_extractor import request_payload
from packages.privacy.secrets import redact_text,redact_value,ensure_safe,MASK
from packages.storage.project_store import canonical,digest
from packages.storage.workspace import Workspace
from packages.domain.source_event import ContractError

SECRET='sk-proj-'+('Z9testonly'*5)
class SecretPrivacyTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.QuestionTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups);self.core=self.fx.core;self.owner=self.fx.owner;self.sources=ConversationService(self.core)
 def test_storage_and_backup_contain_only_redacted_source_with_matching_hash_and_quote(self):
  text='Q_STORE chose SQLite. password="synthetic pass phrase" API_KEY='+SECRET
  source=self.sources.ingest(self.owner,'p',text=text);self.assertNotIn(SECRET,source['text']);self.assertNotIn('synthetic pass phrase',source['text']);self.assertEqual(source['sha256'],digest(source['text']));self.assertFalse(source['redaction']['original_retained'])
  output=dict(source_id=source['id'],source_sha256=source['sha256'],coverage='complete',candidates=[dict(type='Decision',title='Storage',quote='Q_STORE chose SQLite.',intent='reported')]);candidate=anchored(source,output)['candidates'][0];self.assertEqual(source['text'][candidate['start']:candidate['end']],candidate['quote'])
  dump='\n'.join(self.core.db.iterdump());self.assertNotIn(SECRET,dump);self.assertNotIn('synthetic pass phrase',dump);backup=Path(self.fx.temp.name)/'safe-backup.sqlite';manifest=self.core.backup(self.owner,backup)
  with Workspace.restore(backup,Path(self.fx.temp.name)/'safe-restored.sqlite',manifest) as core:self.assertNotIn(SECRET,'\n'.join(core.db.iterdump()))
  for path in self.fx.path.parent.glob('*.sqlite*'):
   if path.is_file():self.assertNotIn(SECRET.encode(),path.read_bytes())
 def test_redacted_dedup_does_not_hash_or_distinguish_original_password(self):
  a=self.sources.ingest(self.owner,'p',text='Choice SQLite. password=alpha-secret');b=self.sources.ingest(self.owner,'p',text='Choice SQLite. password=beta-secret');self.assertEqual(a,b);self.assertEqual(len(self.sources._rows('p','conversation_imported')),1)
 def test_plain_project_ids_and_password_reset_discussion_remain_intact(self):
  text='Q_STORE TASK-123 event_id=evt_42 project_id=my_project. Implement password reset and token budget limits.'
  self.assertEqual(redact_text(text),(text,{}));self.assertEqual(redact_value(dict(source_id='source_123',context_sha256='abc',authority_revision=2)),dict(source_id='source_123',context_sha256='abc',authority_revision=2))
 def test_cookie_bearer_url_jwt_private_key_and_multilingual_assignments_are_redacted(self):
  values=['Cookie: session=synthetic-cookie; token=other-cookie','Authorization: Bearer synthetic-auth-token','postgres://user:synthetic-url-password@db.local/name','eyJabcdefghijk.abcdefghijkl.abcdefghijkl','-----BEGIN PRIVATE KEY-----\nSYNTHETIC-KEY\n-----END PRIVATE KEY-----','şifre: "synthetic turkish phrase"','client_secret=synthetic-client-secret']
  for value in values:
   with self.subTest(value=value.split(':')[0]):
    sanitized,counts=redact_text(value);self.assertTrue(counts);self.assertIn(MASK,sanitized);self.assertEqual(redact_text(sanitized),(sanitized,{}));ensure_safe(sanitized)
 def test_escaped_json_secret_response_rejected_without_raw_or_hash_retention(self):
  source=self.sources.ingest(self.owner,'p',text='Choose SQLite.');service=DialogueReviewService(self.core);prepared=service.prepare(self.owner,'p',source_id=source['id'])
  output=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=prepared['context_sha256'],coverage='complete',candidates=[dict(type='Task',title='api_key='+SECRET,quote='Choose SQLite.',intent='planned')],status_changes=[],answer_proposals=[],relation_proposals=[])
  escaped=json.dumps(output).replace('sk-proj-',r'\u0073k-proj-')
  with self.assertRaises(ContractError) as error:service.import_response(self.owner,'p',source_id=source['id'],response_text=escaped)
  self.assertEqual(error.exception.code,'sensitive_content');self.assertNotIn(SECRET,str(error.exception));self.assertEqual(self.sources._rows('p','conversation_analysis_finished'),[])
 def test_sensitive_model_output_never_retains_raw_even_on_failed_analysis(self):
  import test_conversations,time
  source=self.sources.ingest(self.owner,'p',text=test_conversations.TEXT)
  class BadExtractor(test_conversations.Extractor):
   def __call__(self,source):return dict(api_key=SECRET)
  extractor=BadExtractor();self.core.create_budget(self.owner,'p','privacy_run',10000);self.sources.authorize_analysis(self.owner,'p',source_id=source['id'],key='privacy_grant',root_run='privacy_run',reserved_tokens=1000,provider=extractor.provider,model=extractor.model,max_output_tokens=512,expires_at=int(time.time())+1000,reason='Synthetic test');extractor.max_output_tokens=512;extractor.grant_id='privacy_grant'
  result=self.sources.analyze(self.owner,'p',source['id'],extractor);self.assertEqual(result['status'],'Analysis failed');self.assertNotIn('raw_output',result);self.assertNotIn('raw_sha256',result);self.assertNotIn(SECRET,'\n'.join(self.core.db.iterdump()))
 def test_legacy_source_is_blocked_at_model_preparation_without_rewriting_history(self):
  text='Legacy password=synthetic-old-secret';source=dict(id='legacy',sha256=digest(text),text=text,source_kind='manual_paste',actor='owner',received_at=1,revision=1)
  self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',('w','p','owner','conversation_imported',canonical(source)))
  with self.assertRaises(ContractError):DialogueReviewService(self.core).prepare(self.owner,'p',source_id='legacy')
  with self.assertRaises(ContractError):request_payload(source,model='fixture',max_output_tokens=128)
  self.assertEqual(self.sources._source('p','legacy'),source);self.assertIn('synthetic-old-secret','\n'.join(self.core.db.iterdump()))
 def test_database_and_existing_sidecars_are_owner_only_after_open(self):
  if os.name!='posix':self.skipTest('POSIX permissions only')
  from packages.storage.private_files import restrict_sqlite_files
  target=Path(self.fx.temp.name)/'permissions.sqlite';target.write_bytes(b'');target.chmod(0o644);sidecar=Path(str(target)+'-wal');sidecar.write_bytes(b'');sidecar.chmod(0o666);restrict_sqlite_files(target)
  self.assertEqual(target.stat().st_mode&0o777,0o600);self.assertEqual(sidecar.stat().st_mode&0o777,0o600)
  target.chmod(0o400);restrict_sqlite_files(target);self.assertEqual(target.stat().st_mode&0o777,0o400)
  link=Path(self.fx.temp.name)/'unsafe.sqlite';link.symlink_to(target)
  with self.assertRaises(OSError):restrict_sqlite_files(link)
 def test_native_scaffold_rejects_secret_text_but_keeps_session_identity_contract(self):
  from packages.domain.source_event import SourceEvent,FORMAT
  from packages.domain.project_binding import SessionKey
  key=SessionKey('fixture','account','session_1','epoch_1');self.core.bind(self.owner,key,'p',0)
  event=SourceEvent(FORMAT,'event_1','p','session_1',1,'human','password=synthetic-native-secret',True)
  with self.assertRaises(ContractError):self.core.receive(self.owner,key,event,1)
  self.assertEqual(self.core.db.execute('SELECT count(*) FROM sources').fetchone()[0],0)
  from dataclasses import replace
  self.core.receive(self.owner,key,replace(event,text='Safe Q_STORE task context'),1);self.assertEqual(self.core.db.execute('SELECT count(*) FROM sources').fetchone()[0],1)
 def test_manual_domain_and_question_secret_writes_rejected_before_commit(self):
  from packages.domain.questions import QuestionService
  with self.assertRaises(ContractError):QuestionService(self.core).present(self.owner,'p',question='unsafe',base_revision=0,text='Password='+SECRET,options=[dict(id='a',label='A'),dict(id='b',label='B')])
  with self.assertRaises(ContractError):self.core.plan(self.owner,'p','unsafe_record',[dict(op='create',id='t',body=dict(type='Task',title='Unsafe',description='api_key='+SECRET))])
  self.assertNotIn(SECRET,'\n'.join(self.core.db.iterdump()))

 def test_markdown_multiline_password_and_incomplete_private_key_do_not_escape(self):
  for text in ['password=`synthetic multi word secret`','password="line one\nline two"','-----BEGIN PRIVATE KEY-----\nsynthetic-unfinished-key']:
   safe,counts=redact_text(text);self.assertTrue(counts);ensure_safe(safe);self.assertEqual(redact_text(safe),(safe,{}))
 def test_http_import_source_display_request_and_operations_do_not_return_synthetic_secret(self):
  import test_local_app as http
  fixture=http.LocalAppTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
  code,value,_=fixture.call('/api/command',dict(action='import_conversation',text='Choose SQLite. password="'+SECRET+'"'));self.assertEqual(code,200);self.assertNotIn(SECRET,json.dumps(value));source=value['source'];self.assertIn(MASK,source['text'])
  code,prepared,_=fixture.call('/api/command',dict(action='prepare_dialogue_review',source_id=source['id']));self.assertEqual(code,200);self.assertNotIn(SECRET,json.dumps(prepared));self.assertIn(MASK,prepared['request']['source']['text'])
  for path in ('/api/state','/api/operations'):
   code,value,_=fixture.call(path);self.assertEqual(code,200);self.assertNotIn(SECRET,json.dumps(value))
  code,value,_=fixture.call('/api/command',dict(action='create_task',title='Unsafe',description='api_key='+SECRET));self.assertNotEqual(code,200);self.assertNotIn(SECRET,json.dumps(value))

 def test_legacy_secret_record_cannot_leave_exact_mcp_read_or_project_brief(self):
  from packages.mcp.server import Server
  body=dict(type='Decision',title='Legacy decision',description='api_key='+SECRET)
  self.core.db.execute('INSERT INTO records VALUES (?,?,?,?,?)',('w','p','legacy_record',1,canonical(body)))
  a=self.core.authority;a.replace_grant(self.owner,'privacy_agent',kind='agent',readable=frozenset({'p'}),writable=frozenset(),active=True,base_revision=a.revision())
  server=Server(self.fx.path,'w','privacy_agent')
  for name,args in [('get_record',dict(project_id='p',id='legacy_record',revision=1)),('get_project_brief',dict(project_id='p')),('query_records',dict(project_id='p'))]:
   with self.subTest(name=name),self.assertRaises(ContractError) as error:server.call(name,args)
   self.assertEqual(error.exception.code,'sensitive_content');self.assertNotIn(SECRET,str(error.exception))

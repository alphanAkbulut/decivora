"""Real stdio subprocess plus authority/cursor/proposal/claim negative checks."""
import unittest,tempfile,json,subprocess,sys
from pathlib import Path
from packages.storage.workspace import Workspace
from packages.mcp.server import Server,TOOLS,VERSION
from packages.domain.source_event import ContractError
class McpTests(unittest.TestCase):
 def setUp(self):
  from test_conversations import install_fixture_analysis_grants
  fixture=install_fixture_analysis_grants();fixture.start();self.addCleanup(fixture.stop)
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'mcp.sqlite';self.core=Workspace(self.path,'w',owner='owner');self.addCleanup(self.core.close);a=self.core.authority
  for principal,kind,projects in [('owner','human',{'p','q'}),('agent1','agent',{'p'}),('agent2','agent',{'p'})]:a.replace_grant(a.issue_scope('owner'),principal,kind=kind,readable=frozenset(projects),writable=frozenset(projects),active=True,base_revision=a.revision())
  self.owner=a.issue_scope('owner');self.core.create_project(self.owner,'p','Project');self.core.create_project(self.owner,'q','Other');self.server=Server(self.path,'w','agent1');self.i=0;self.task=self.create('First');self.create('Second')
 def create(self,title):
  self.i+=1;p=self.core.plan(self.owner,'p','create'+str(self.i),[dict(op='create',id='t',body=dict(type='Task',title=title,description='Private canonical scope'))]);return self.core.apply(self.owner,p,self.core.approve(self.owner,p))['temp_ids']['t']
 def test_five_tools_and_real_stdio_initialization_query_and_shutdown(self):
  messages=[dict(jsonrpc='2.0',id=1,method='initialize',params=dict(protocolVersion=VERSION,capabilities={},clientInfo=dict(name='fixture',version='1'))),dict(jsonrpc='2.0',method='notifications/initialized'),dict(jsonrpc='2.0',id=2,method='tools/list'),dict(jsonrpc='2.0',id=3,method='tools/call',params=dict(name='query_records',arguments=dict(project_id='p',limit=1)))]
  result=subprocess.run([sys.executable,'-B','-m','packages.mcp.server','--database',str(self.path),'--workspace','w','--principal','agent1'],input=''.join(json.dumps(m)+'\n' for m in messages),text=True,capture_output=True,timeout=10)
  self.assertEqual(result.returncode,0,result.stderr);rows=[json.loads(line) for line in result.stdout.splitlines()];self.assertEqual(len(rows),3);self.assertEqual(len(rows[1]['result']['tools']),5);self.assertFalse(rows[2]['result']['isError']);self.assertEqual(len(json.loads(rows[2]['result']['content'][0]['text'])['records']),1)
 def test_uninitialized_sql_and_human_identity_denied(self):
  self.assertIn('error',self.server.handle(dict(jsonrpc='2.0',id=1,method='tools/list')))
  with self.assertRaises(ContractError):Server(self.path,'w','owner').call('query_records',dict(project_id='p'))
  with self.assertRaises(ContractError):self.server.call('sql',dict(project_id='p'))
 def test_cross_project_and_caller_identity_override_denied(self):
  with self.assertRaises(ContractError):self.server.call('query_records',dict(project_id='q'))
  with self.assertRaises(ContractError):self.server.call('query_records',dict(project_id='p',principal='owner'))
 def test_signed_cursor_revision_and_limit_bound(self):
  first=self.server.call('query_records',dict(project_id='p',limit=1));cursor=first['next_cursor'];self.assertTrue(cursor)
  second=self.server.call('query_records',dict(project_id='p',limit=1,cursor=cursor));self.assertNotEqual(first['records'][0]['id'],second['records'][0]['id'])
  for args in [dict(project_id='p',limit=2,cursor=cursor),dict(project_id='p',limit=1,cursor=cursor+'x')]:
   with self.assertRaises(ContractError):self.server.call('query_records',args)
  self.create('Third')
  with self.assertRaises(ContractError):self.server.call('query_records',dict(project_id='p',limit=1,cursor=cursor))
 def test_revoked_agent_stops_reading(self):
  a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'agent1',kind='agent',readable=frozenset(),writable=frozenset(),active=False,base_revision=a.revision())
  with self.assertRaises(ContractError):self.server.call('query_records',dict(project_id='p'))
 def test_brief_byte_budget_and_exact_record_version(self):
  brief=self.server.call('get_project_brief',dict(project_id='p',budget=1024));self.assertLessEqual(len(json.dumps(brief,separators=(',',':'),ensure_ascii=False).encode()),1024);self.assertTrue(brief['context_truncated']);self.assertFalse(brief['raw_sources_included'])
  self.assertEqual(self.server.call('get_record',dict(project_id='p',id=self.task,revision=1))['version'],1)
  with self.assertRaises(ContractError):self.server.call('get_record',dict(project_id='p',id=self.task,revision=2))
 def test_agent_proposal_requires_human_apply_then_second_agent_sees_result(self):
  revision=self.core.project(self.owner,'p')['knowledge_revision'];args=dict(project_id='p',key='agentproposal',base_revision=revision,operations=[dict(op='create',id='t',body=dict(type='Task',title='Proposed by agent',description='Human must approve'))]);result=self.server.call('submit_changeset',args)
  self.assertFalse(result['approved']);self.assertEqual(result['canonical_mutations'],0);self.assertEqual(len(self.core.records(self.owner,'p')['records']),2)
  owner=self.core.authority.issue_scope('owner');self.core.apply(owner,result['proposal'],self.core.approve(owner,result['proposal']))
  records=Server(self.path,'w','agent2').call('query_records',dict(project_id='p'))['records'];self.assertTrue(any(r['title']=='Proposed by agent' for r in records))
 def test_agent_claim_is_not_human_verified_evidence_and_retry_is_safe(self):
  args=dict(project_id='p',key='claim',task=self.task,task_version=1,status='claimed',reference='Agent report',note='Agent says work ended');self.assertFalse(self.server.call('submit_evidence',args)['verified']);self.assertEqual(self.server.call('submit_evidence',args)['canonical_mutations'],0)
  self.assertEqual(self.core.db.execute("SELECT count(*) FROM audit WHERE action='criterion_evidence'").fetchone()[0],0)
  with self.assertRaises(ContractError):self.server.call('submit_evidence',dict(args,status='verified'))
 def test_stdio_duplicate_json_and_oversize_lines_do_not_dispatch(self):
  command=[sys.executable,'-B','-m','packages.mcp.server','--database',str(self.path),'--workspace','w','--principal','agent1']
  for payload in ['{"jsonrpc":"2.0","id":1,"id":2,"method":"ping"}\n','x'*32769+'\n']:
   r=subprocess.run(command,input=payload,text=True,capture_output=True,timeout=10);response=json.loads(r.stdout.splitlines()[0]);self.assertIn('error',response)

 def test_private_conversation_derived_record_is_not_shared_by_project_grant(self):
  import test_conversations as c
  service=c.ConversationService(self.core);source=service.ingest(self.owner,'p',text=c.TEXT);candidate=service.analyze(self.owner,'p',source['id'],c.Extractor())['candidates'][0];view=service.view(self.owner,'p');result=service.accept(self.owner,'p',source_id=source['id'],key='privateaccept',selected=[candidate['id']],base_revision=view['knowledge_revision']);rid=next(iter(result['temp_ids'].values()))
  records=self.server.call('query_records',dict(project_id='p'))['records'];self.assertFalse(any(r['id']==rid for r in records))
  with self.assertRaises(ContractError):self.server.call('get_record',dict(project_id='p',id=rid,revision=1))

 def test_cursor_cannot_move_to_another_authorized_project_or_filter(self):
  a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'agent1',kind='agent',readable=frozenset({'p','q'}),writable=frozenset({'p','q'}),active=True,base_revision=a.revision());self.owner=a.issue_scope('owner')
  cursor=self.server.call('query_records',dict(project_id='p',limit=1))['next_cursor']
  for args in [dict(project_id='q',limit=1,cursor=cursor),dict(project_id='p',limit=1,cursor=cursor,filters=dict(type='Decision'))]:
   with self.assertRaises(ContractError):self.server.call('query_records',args)
 def test_tool_output_budget_does_not_return_an_oversized_record(self):
  plan=self.core.plan(self.owner,'p','unicode',[dict(op='create',id='t',body=dict(type='Task',title='Large UTF8 record',description='文'*8192))]);result=self.core.apply(self.owner,plan,self.core.approve(self.owner,plan));rid=result['temp_ids']['t'];self.server.ready=True
  response=self.server.handle(dict(jsonrpc='2.0',id=1,method='tools/call',params=dict(name='get_record',arguments=dict(project_id='p',id=rid,revision=1))));self.assertTrue(response['result']['isError']);self.assertEqual(json.loads(response['result']['content'][0]['text'])['error'],'output_limit')

 def test_duplicate_private_source_attachment_does_not_break_unrelated_queries(self):
  import test_conversations as c
  service=c.ConversationService(self.core)
  for index,text in enumerate([c.TEXT,'Extra context. '+c.TEXT]):
   source=service.ingest(self.owner,'p',text=text);candidate=service.analyze(self.owner,'p',source['id'],c.Extractor())['candidates'][0];view=service.view(self.owner,'p');service.accept(self.owner,'p',source_id=source['id'],key='private'+str(index),selected=[candidate['id']],base_revision=view['knowledge_revision'])
  rows=self.server.call('query_records',dict(project_id='p'))['records'];self.assertEqual(len(rows),2);self.assertFalse(any(row['title']=='Backup test' for row in rows))

 def test_private_connected_context_cannot_leak_via_a_public_task(self):
  import test_conversations as c
  service=c.ConversationService(self.core);source=service.ingest(self.owner,'p',text=c.TEXT);candidate=service.analyze(self.owner,'p',source['id'],c.Extractor())['candidates'][0];result=service.accept(self.owner,'p',source_id=source['id'],key='sourceaccept',selected=[candidate['id']],base_revision=self.core.project(self.owner,'p')['knowledge_revision']);private=next(iter(result['temp_ids'].values()));plan=self.core.plan(self.owner,'p','connect',[dict(op='link',origin=self.task,target=private,kind='depends_on')]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
  rows=self.server.call('query_records',dict(project_id='p'))['records'];self.assertFalse(any(r['id']==self.task for r in rows));self.assertEqual(len(rows),1)

 def test_process_rate_limit_preserves_prior_records_and_refuses_new_admission(self):
  self.server.call_count=60
  with self.assertRaises(ContractError):self.server.call('query_records',dict(project_id='p'))
  self.assertEqual(len(self.core.records(self.owner,'p')['records']),2)

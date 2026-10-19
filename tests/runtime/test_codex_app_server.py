"""Controlled protocol fixtures; never reads an installed Codex user's chats."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import test_questions as fixtures
from packages.capture.codex.app_server import CodexAppServerCapture, public_messages
from packages.capture.codex.exec_stream import CodexExecCapture
from packages.capture.codex.read_client import ReadOnlyAppServer
from packages.capture.dialogue_review import DialogueReviewService
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace
from scripts.capture_codex_thread import main


def page(status='completed'):
    return dict(data=[dict(id='turn_1',status=status,items=[
        dict(id='user_1',type='userMessage',content=[dict(type='text',text='Please add a backup test.')]),
        dict(id='assistant_1',type='agentMessage',text='I will add a backup test.'),
        dict(id='reasoning_1',type='reasoning',content=['PRIVATE-BODY'])])],nextCursor=None)


class Client:
    def __init__(self,value=None): self.value=page() if value is None else value; self.calls=[]
    def read_turns(self,thread_id,*,limit): self.calls.append((thread_id,limit)); return self.value


class AppServerCaptureTests(unittest.TestCase):
    def setUp(self):
        fixtures.QuestionTests.setUp(self)
        self.adapter=CodexAppServerCapture(self.core)
        self.adapter.connect(self.owner,'p',capture_id='app_capture',thread_id='thread_1',provider_version='fixture-1',consent=True)

    def collect(self,client=None):
        return self.adapter.collect(self.owner,'p',capture_id='app_capture',client=client or Client())

    def test_both_roles_source_provenance_and_existing_task_review_bridge(self):
        receipt=self.collect(); self.assertEqual(len(receipt['source_ids']),2)
        sources=self.adapter.sources.view(self.owner,'p')['imports']
        self.assertEqual({v['source']['capture']['observed_actor'] for v in sources},{'human','assistant'})
        source=sources[0]['source']; self.assertEqual(source['source_kind'],'codex_app_server')
        review=DialogueReviewService(self.core); prepared=review.prepare(self.owner,'p',source_id=source['id'])
        self.assertEqual(prepared['request']['source']['capture']['observed_actor'],'human')
        output=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=prepared['context_sha256'],coverage='partial',status_changes=[],candidates=[dict(type='Task',title='Backup test',quote=source['text'],intent='planned')])
        result=review.import_response(self.owner,'p',source_id=source['id'],response_text=json.dumps(output))
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
        self.adapter.sources.accept(self.owner,'p',source_id=source['id'],key='accept_capture_task',selected=[result['candidates'][0]['id']],base_revision=prepared['request']['context']['knowledge_revision'])
        self.assertEqual(len(self.core.records(self.owner,'p')['records']),1)

    def test_retry_restart_and_changed_item_detection(self):
        original=self.collect(); self.assertEqual(self.collect(),original)
        with Workspace(self.path,'w') as core:
            self.assertEqual(CodexAppServerCapture(core).collect(core.authority.issue_scope('owner'),'p',capture_id='app_capture',client=Client()),original)
        altered=page(); altered['data'][0]['items'][0]['content'][0]['text']='A changed request.'
        with self.assertRaises(ContractError): self.collect(Client(altered))
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),2)

    def test_active_turn_keeps_user_and_defers_unfinished_assistant(self):
        first=self.collect(Client(page('inProgress'))); self.assertEqual(len(first['source_ids']),1)
        self.assertEqual(first['active_turns'],1)
        self.assertEqual(len(self.collect()['source_ids']),2)

    def test_nearby_context_is_bounded_and_excludes_other_capture(self):
        receipt=self.collect()
        review=DialogueReviewService(self.core)
        prepared=review.prepare(self.owner,'p',source_id=receipt['source_ids'][1])
        nearby=prepared['request']['context']['capture_context']['messages']
        self.assertEqual([m['source_id'] for m in nearby],[receipt['source_ids'][0]])
        self.assertEqual(nearby[0]['observed_actor'],'human')
        self.assertLessEqual(sum(len(m['text'].encode()) for m in nearby),6000)
        self.adapter.sources.ingest(self.owner,'p',text='Unrelated manual conversation.')
        again=review.prepare(self.owner,'p',source_id=receipt['source_ids'][1])
        self.assertEqual(again['context_sha256'],prepared['context_sha256'])
        self.assertNotIn('Unrelated manual conversation.',json.dumps(again))

    def test_privacy_redaction_counts_and_nontext_coverage(self):
        data=page(); data['nextCursor']='older'; data['data'][0]['items'][0]['content']=[dict(type='text',text='password=example-sensitive-password'),dict(type='image',url='PRIVATE-BODY')]
        result=self.collect(Client(data)); self.assertTrue(result['older_turns_omitted'])
        self.assertEqual(result['unsupported_items'],1)
        serialized=str(self.core.db.execute('SELECT ref FROM audit').fetchall())
        self.assertNotIn('example-sensitive-password',serialized); self.assertNotIn('PRIVATE-BODY',serialized)
        source=self.adapter.sources._source('p',result['source_ids'][0]); self.assertTrue(source['redaction']['counts'])

    def test_scope_and_surface_checked_before_host_read(self):
        client=Client()
        with self.assertRaises(ContractError): self.adapter.collect(self.owner,'foreign',capture_id='app_capture',client=client)
        self.assertEqual(client.calls,[])
        with self.assertRaises(ContractError): CodexExecCapture(self.core).collect(self.owner,'p',capture_id='app_capture',snapshot=b'')
        self.adapter.disconnect(self.owner,'p',capture_id='app_capture')
        with self.assertRaises(ContractError): self.collect(client)
        self.assertEqual(client.calls,[])

    def test_permission_change_during_read_blocks_commit(self):
        a=self.core.authority
        class RevokingClient:
            def read_turns(inner,thread_id,*,limit):
                a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p'}),writable=frozenset(),active=True,base_revision=a.revision())
                return page()
        with self.assertRaises(ContractError): self.collect(RevokingClient())
        self.assertEqual(self.adapter.sources._rows('p','conversation_imported'),[])

    def test_invalid_unknown_and_oversized_inputs_are_explicit(self):
        bad=page(); bad['data'][0]['items'].append(dict(type='unrecognized'))
        self.assertEqual(public_messages(bad)['unsupported_items'],1)
        for value in ({},dict(data=[{}],nextCursor=None),dict(data=[page()['data'][0]]*11,nextCursor=None),
                      dict(data=[dict(page()['data'][0],itemsView='summary')],nextCursor=None)):
            with self.assertRaises(ContractError): self.collect(Client(value))
        with self.assertRaises(ContractError):
            public_messages(dict(data=[dict(id='t',status='completed',items=[dict(id='a',type='agentMessage',text='x'*12001)])],nextCursor=None))

    def test_failure_rolls_back_all_message_sources(self):
        self.core.db.execute("CREATE TRIGGER capture_fail BEFORE INSERT ON audit WHEN NEW.action='codex_app_server_collected' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError): self.collect()
        self.assertEqual(self.adapter.sources._rows('p','conversation_imported'),[])

    def fake_binary(self,delay=False):
        executable=Path(self.temp.name)/'fake-codex'; log=Path(self.temp.name)/'calls.jsonl'
        executable.write_text('#!'+sys.executable+'\nimport json,sys,os,time\n'+
            'for line in sys.stdin:\n v=json.loads(line)\n with open('+repr(str(log)) +",'a') as h: h.write(json.dumps(dict(request=v,credential_inherited='OPENAI_API_KEY' in os.environ))+'\\n')\n"+
            " if v['method']=='initialized': continue\n"+
            (" if v['method']=='thread/turns/list': time.sleep(1)\n" if delay else '')+
            " result={} if v['method']=='initialize' else "+repr(page())+"\n print(json.dumps(dict(id=v['id'],result=result)),flush=True)\n")
        executable.chmod(0o700); return executable,log

    def test_stdio_wire_handshake_read_only_methods_and_no_credential_environment(self):
        executable,log=self.fake_binary()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'do-not-inherit'}):
            with ReadOnlyAppServer(executable,'thread_1',cwd=self.temp.name) as client:
                self.assertEqual(client.read_turns('thread_1',limit=10),page())
                with self.assertRaises(ContractError): client.read_turns('other',limit=10)
        calls=[json.loads(v) for v in log.read_text().splitlines()]
        self.assertEqual([v['request']['method'] for v in calls],['initialize','initialized','thread/turns/list'])
        self.assertFalse(any(v['credential_inherited'] for v in calls))
        self.assertEqual(calls[-1]['request']['params'],dict(threadId='thread_1',limit=10,sortDirection='desc',itemsView='full'))

    def test_timeout_closes_child_without_retry(self):
        executable,log=self.fake_binary(delay=True)
        with ReadOnlyAppServer(executable,'thread_1',cwd=self.temp.name) as client:
            client.timeout=.05
            with self.assertRaises(ContractError): client.read_turns('thread_1',limit=10)
        self.assertIsNotNone(client.process.poll())
        self.assertEqual(sum(json.loads(v)['request']['method']=='thread/turns/list' for v in log.read_text().splitlines()),1)

    def test_cli_bounded_polling_uses_real_transport_against_synthetic_child(self):
        executable,_=self.fake_binary()
        args=['--db',str(self.path),'--workspace','w','--principal','owner','--project','p','--capture-id','cli_capture',
              '--thread-id','thread_1','--provider-version','fixture-1','--codex-executable',str(executable),'--consent','--polls','2','--interval','.25']
        with redirect_stdout(io.StringIO()) as out: self.assertEqual(main(args),0)
        lines=[json.loads(v) for v in out.getvalue().splitlines()]
        self.assertEqual(lines[0]['source_ids'],lines[1]['source_ids'])
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),2)

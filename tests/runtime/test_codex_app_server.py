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
        for limit in (0,11,True):
            with self.assertRaises(ContractError):self.adapter.collect(self.owner,'p',capture_id='app_capture',client=client,limit=limit)
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

    def fake_binary(self,delay=False,metadata_pad=0):
        executable=Path(self.temp.name)/'fake-codex'; log=Path(self.temp.name)/'calls.jsonl'
        executable.write_text('#!'+sys.executable+'\nimport json,sys,os,time\n'+
            'for line in sys.stdin:\n v=json.loads(line)\n with open('+repr(str(log)) +",'a') as h: h.write(json.dumps(dict(request=v,credential_inherited='OPENAI_API_KEY' in os.environ))+'\\n')\n"+
            " if v['method']=='initialized': continue\n"+
            (" if v['method']=='thread/turns/list': time.sleep(1)\n" if delay else '')+
            " source="+repr(page())+"\n"+
            " if v['method']=='initialize': result={}\n"+
            " elif v['method']=='thread/turns/list': result=dict(data=[dict(id='turn_1',status='completed',items=[],itemsView='notLoaded')],nextCursor=None)\n"+
            " elif v['method']=='thread/items/list':\n  n=int(v['params'].get('cursor','0')); result=dict(data=[dict(turnId='turn_1',item=source['data'][0]['items'][n])],nextCursor=str(n+1) if n<2 else None)\n"+
            " else: raise RuntimeError('Forbidden method')\n"+
            (" if v['method']=='thread/turns/list': result['padding']='x'*"+str(metadata_pad)+"\n" if metadata_pad else '')+
            " print(json.dumps(dict(id=v['id'],result=result)),flush=True)\n")
        executable.chmod(0o700); return executable,log

    def test_stdio_wire_handshake_read_only_methods_and_no_credential_environment(self):
        executable,log=self.fake_binary()
        with patch.dict(os.environ,{'OPENAI_API_KEY':'do-not-inherit'}):
            with ReadOnlyAppServer(executable,'thread_1',cwd=self.temp.name) as client:
                result=client.read_turns('thread_1',limit=10)
                self.assertEqual([i['type'] for i in result['data'][0]['items']],['userMessage','agentMessage'])
                self.assertEqual(result['ignored_private_items'],1)
                self.assertNotIn('PRIVATE-BODY',json.dumps(result))
                with self.assertRaises(ContractError): client.read_turns('other',limit=10)
        calls=[json.loads(v) for v in log.read_text().splitlines()]
        self.assertEqual([v['request']['method'] for v in calls],['initialize','initialized','thread/turns/list']+['thread/items/list']*3)
        self.assertFalse(any(v['credential_inherited'] for v in calls))
        self.assertEqual(calls[2]['request']['params'],dict(threadId='thread_1',limit=10,sortDirection='desc',itemsView='notLoaded'))
        self.assertTrue(all(v['request']['params']['limit']==1 and v['request']['params']['turnId']=='turn_1' for v in calls[3:]))

    def test_timeout_closes_child_without_retry(self):
        executable,log=self.fake_binary(delay=True)
        with ReadOnlyAppServer(executable,'thread_1',cwd=self.temp.name) as client:
            client.timeout=.05
            with self.assertRaises(ContractError): client.read_turns('thread_1',limit=10)
        self.assertIsNotNone(client.process.poll())
        self.assertEqual(sum(json.loads(v)['request']['method']=='thread/turns/list' for v in log.read_text().splitlines()),1)

    def test_real_failure_shape_keeps_one_mib_guard_and_no_accepted_source(self):
        executable,_=self.fake_binary(metadata_pad=1048577)
        with ReadOnlyAppServer(executable,'thread_1',cwd=self.temp.name) as client:
            with self.assertRaises(ContractError) as error: self.collect(client)
            self.assertEqual(error.exception.code,'capture_limit')
        self.assertEqual(self.adapter.sources._rows('p','conversation_imported'),[])

    def test_paged_private_bodies_do_not_accumulate_and_gaps_are_explicit(self):
        reader=ReadOnlyAppServer.__new__(ReadOnlyAppServer);reader.thread_id='thread_1';reader.request_id=0;calls=[]
        def request(number,method,params):
            calls.append((method,params))
            if method=='thread/turns/list':return dict(data=[dict(id='t2',status='completed'),dict(id='t1',status='completed')],nextCursor='older')
            i=int(params.get('cursor','0'))
            item=dict(id='item_'+str(i),type='userMessage',content=[dict(type='text',text='Add backup.')]) if i==0 else dict(id='item_'+str(i),type='newPrivateKind' if i==1 else 'commandExecution',aggregatedOutput='PRIVATE-BODY'*8000)
            return dict(data=[dict(turnId=params['turnId'],item=item)],nextCursor=str(i+1))
        reader._request=request
        result=reader.read_turns('thread_1',limit=2)
        self.assertEqual(len(calls),33);self.assertTrue(all(t['capture_items_truncated'] for t in result['data']))
        self.assertNotIn('PRIVATE-BODY',json.dumps(result));self.assertLess(len(json.dumps(result)),2000)
        receipt=self.collect(Client(result));self.assertEqual(receipt['incomplete_item_turns'],2);self.assertEqual(len(receipt['source_ids']),2)
        self.assertEqual(receipt['item_pages'],32);self.assertEqual(receipt['unsupported_items'],2)

    def test_cross_turn_item_or_repeated_cursor_stops(self):
        reader=ReadOnlyAppServer.__new__(ReadOnlyAppServer);reader.thread_id='thread_1';reader.request_id=0
        for mode in ('foreign','repeat'):
            def request(number,method,params):
                if method=='thread/turns/list':return dict(data=[dict(id='t',status='completed')])
                return dict(data=[dict(turnId='foreign' if mode=='foreign' else 't',item=dict(type='reasoning'))],nextCursor='repeat')
            reader._request=request
            with self.subTest(mode=mode),self.assertRaises(ContractError):reader.read_turns('thread_1',limit=1)

    def test_cli_bounded_polling_uses_real_transport_against_synthetic_child(self):
        executable,_=self.fake_binary()
        args=['--db',str(self.path),'--workspace','w','--principal','owner','--project','p','--capture-id','cli_capture',
              '--thread-id','thread_1','--provider-version','fixture-1','--codex-executable',str(executable),'--consent','--polls','2','--interval','.25']
        with redirect_stdout(io.StringIO()) as out: self.assertEqual(main(args),0)
        lines=[json.loads(v) for v in out.getvalue().splitlines()]
        self.assertEqual(len(lines[0]['source_ids']),2)
        self.assertEqual(lines[1]['source_ids'],[])
        self.assertEqual(lines[1]['item_pages'],0)
        from packages.operations.local import LocalOperations
        runs=LocalOperations(self.path.with_suffix('.operations.sqlite')).view('p')['runs']
        self.assertEqual(len(runs),2)
        self.assertTrue(all(r['action']=='native_capture' and r['outcome']=='succeeded' for r in runs))
        self.assertNotIn('backup test',json.dumps(runs))
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_enqueued')),2)
        self.assertEqual(len(self.adapter.sources._rows('p','conversation_imported')),2)

    def test_native_cli_failed_capture_is_in_persistent_operations_without_source_text(self):
        executable,_=self.fake_binary(metadata_pad=1048577)
        args=['--db',str(self.path),'--workspace','w','--principal','owner','--project','p','--capture-id','failed_cli_capture',
              '--thread-id','thread_1','--provider-version','fixture-1','--codex-executable',str(executable),'--consent']
        with redirect_stdout(io.StringIO()) as out:self.assertEqual(main(args),1)
        self.assertEqual(json.loads(out.getvalue())['code'],'capture_limit')
        from packages.operations.local import LocalOperations
        runs=LocalOperations(self.path.with_suffix('.operations.sqlite')).view('p')['runs']
        self.assertEqual(runs[0]['code'],'capture_limit');self.assertEqual(runs[0]['outcome'],'failed')
        self.assertEqual(runs[0]['identity']['actor_id'],'owner')
        self.assertNotIn('PRIVATE-BODY',json.dumps(runs))

"""Saved-source runner with synthetic local sources, fake HTTP and private temporary DBs."""
import copy,json,tempfile,time,unittest
from pathlib import Path
from apps.local_ui.server import LocalApp
from packages.capture.conversations import ConversationService
from packages.capture.openai_transport import PRICE_REVISION,PilotTransport
from scripts.run_saved_conversation_pilot import prepare,run,bounded_manifest

class SavedSourcePilotTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.folder=Path(temp.name)
        self.app=LocalApp(self.folder/'original.sqlite');self.batch=self.folder/'batch';self.policy=self.folder/'policy.json';self.ledger=self.folder/'ledger.sqlite';self.calls=[]
        policy=dict(approval_ref='synthetic-test-root',price_revision=PRICE_REVISION,expires_at=int(time.time())+3600,max_http_attempts=200,max_cost_microusd=3000000,max_input_tokens=10000,max_output_tokens=2000,budget_scope='decivora-development-2026-10-19-usd3',prior_usage=dict(dispatches=20,http_attempts=40,cost_microusd=49592,evidence_sha256='a'*64))
        self.policy.write_text(json.dumps(policy));self.key=self.folder/'key';self.key.write_text('sk-'+'x'*30);self.key.chmod(0o600)
        for i in range(6):self.app.command(dict(action='import_conversation',text='Please add synthetic backup test '+str(i)+'.'))
        with self.app.core() as core:self.before=list(core.db.iterdump())

    def post(self,path,payload,key):
        self.calls.append(path)
        if path.endswith('input_tokens'):return dict(object='response.input_tokens',input_tokens=100)
        data=json.loads(payload['input']);s=data['source']
        output=dict(source_id=s['id'],source_sha256=s['sha256'],context_sha256=data['context_sha256'],coverage='partial',candidates=[dict(type='Task',title='Backup test',quote=s['text'],intent='planned')],status_changes=[],answer_proposals=[],relation_proposals=[])
        return dict(status='completed',usage=dict(input_tokens=100,output_tokens=20,total_tokens=120,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0)),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])

    def prepared(self):return prepare(self.batch,approval_ref='synthetic-test-real-data-scope',source_db=self.app.path,policy_file=self.policy)

    def test_six_source_copy_shares_old_budget_and_never_modifies_original(self):
        packet=self.prepared();self.assertEqual(self.calls,[]);self.assertLessEqual(packet['worst_case_microusd'],250000)
        result=run(self.batch,key_file=self.key,ledger=self.ledger,post=self.post)
        self.assertEqual(result['attempted'],6);self.assertEqual(len(self.calls),12)
        self.assertEqual(result['queue']['counts'],{'Ready for review':6});self.assertFalse(result['auto_apply'])
        self.assertEqual(result['shared_budget']['dispatches'],26);self.assertEqual(result['shared_budget']['http_attempts'],52)
        self.assertGreater(result['shared_budget']['committed_microusd'],49592)
        run(self.batch,key_file=self.key,ledger=self.ledger,post=lambda *args:self.fail('Retry'))
        with self.app.core() as core:self.assertEqual(list(core.db.iterdump()),self.before)
        self.assertFalse(self.app.state()['model_ready']);self.assertEqual(self.app.state()['tasks'],[])

    def test_wrong_model_batch_size_or_expiry_is_not_admitted(self):
        policy=json.loads(self.policy.read_text());payload=dict(model='gpt-6-luna',max_output_tokens=2000)
        for rows in ([],[payload]*7,[dict(payload,model='gpt-6.1-sol')],[payload,payload]):
            with self.assertRaises(ValueError):bounded_manifest(policy,rows)
        with self.assertRaises(ValueError):bounded_manifest(dict(policy,expires_at=0),[payload])

    def test_changed_context_stops_before_any_http(self):
        self.prepared()
        from packages.storage.workspace import Workspace
        with Workspace(self.batch/'pilot.sqlite','local_ui_workspace') as core:
            owner=core.authority.issue_scope('local_owner')
            p=core.plan(owner,'personal','changed',[dict(op='create',id='new',body=dict(type='Task',title='Changed',description='Changed context'))]);core.apply(owner,p,core.approve(owner,p))
        with self.assertRaises(ValueError):run(self.batch,key_file=self.key,ledger=self.ledger,post=self.post)
        self.assertEqual(self.calls,[])

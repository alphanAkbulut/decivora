"""Four-case runner controls using fake HTTP, never semantic evidence."""
import json,tempfile,time,unittest
from pathlib import Path
from scripts.run_dialogue_batch import prepare,run,task_role
from packages.capture.openai_transport import PRICE_REVISION

class DialogueBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.key=self.root/'key';self.key.write_text('sk-'+'x'*30);self.key.chmod(0o600)
        self.policy=dict(approval_ref='synthetic-fixture',price_revision=PRICE_REVISION,expires_at=int(time.time())+3600,max_http_attempts=200,max_cost_microusd=3000000,max_input_tokens=10000,max_output_tokens=2000,budget_scope='decivora-development-2026-10-19-usd3',prior_usage=dict(dispatches=0,http_attempts=0,cost_microusd=0,evidence_sha256='a'*64))
        self.policy_path=self.root/'policy.json';self.policy_path.write_text(json.dumps(self.policy));self.calls=[]
    def post(self,path,payload,key):
        self.calls.append(path)
        if path.endswith('input_tokens'):return dict(object='response.input_tokens',input_tokens=300)
        request=json.loads(payload['input']);source=request['source'];capture=source['capture'];cid=capture['thread_id'];step=int(capture['item_id'].split('_m')[1]);context=request['context']
        self.assertNotIn('expectations',request);self.assertEqual(len(context.get('capture_context',{}).get('messages',[])),step-1)
        self.assertTrue(all(int(m['item_id'].split('_m')[1])<step for m in context['capture_context']['messages']))
        result=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=request['context_sha256'],coverage='partial',candidates=[],status_changes=[],answer_proposals=[],relation_proposals=[],question_proposals=[])
        if step==1 and cid!='J04':
            titles=['Yedek geri yükleme testi']+(['Yedek alma testi'] if cid=='J03' else [])
            result['candidates']=[dict(type='Task',title=t,quote=source['text'],intent='planned') for t in titles]
        stage={('J01',4):'In Progress',('J01',6):'Done',('J02',5):'In Progress',('J03',5):'In Progress'}.get((cid,step))
        if stage:result['status_changes']=[dict(task_id=next(t['id'] for t in context['tasks'] if task_role(t['title'])=='restore'),stage=stage,quote=source['text'])]
        if cid=='J04' and step in (1,2):result['question_proposals']=[dict(question_text=source['text'],options=['dosya','SQLite'] if step==1 else ['pano','liste'],quote=source['text'])]
        if cid=='J04' and step==5:
            q=next(q for q in context['questions'] if 'Q_STORE' in q['text']);opt=next(o for o in q['options'] if o['label']=='SQLite');result['answer_proposals']=[dict(question_id=q['id'],question_revision=q['revision'],option_id=opt['id'],quote=source['text'])]
        return dict(status='completed',usage=dict(input_tokens=300,output_tokens=50,total_tokens=350,input_tokens_details=dict(cached_tokens=0,cache_write_tokens=0)),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(result))])])
    def test_sequential_four_cases_context_guards_and_no_repeat(self):
        folder=self.root/'batch';plan=prepare(folder,self.policy_path);self.assertEqual(len(plan['cases']),4)
        report=run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=self.post)
        self.assertEqual(report['dispatches'],24);self.assertEqual(len(self.calls),48);self.assertIsNone(report['stopped'])
        self.assertTrue(all(c['verdict']=='passed_draft_checks' for c in report['cases']))
        self.assertEqual(report['cases'][0]['turns'][-1]['canonical_stages']['restore'],'In Progress')
        self.assertIn(report['cases'][0]['turns'][-1]['done_guard_code'],('invalid_transition','verification_required','acceptance_required'))
        self.assertEqual(sorted(q['status'] for q in report['cases'][3]['questions']),['Answered','Open'])
        from scripts.report_dialogue_batch import build
        public=build(folder)
        self.assertEqual(len(public['cases']),4);self.assertEqual(public['http_budget_slots_delta'],48)
        self.assertEqual(len(self.calls),48)  # Reporting cannot dispatch or read a credential.
        self.assertEqual(run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=self.post),report);self.assertEqual(len(self.calls),48)
    def test_unknown_stops_batch_and_does_not_start_other_cases(self):
        folder=self.root/'batch';prepare(folder,self.policy_path)
        def fail(*args):self.calls.append('failed');raise TimeoutError('private diagnostic')
        report=run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=fail)
        self.assertEqual(report['dispatches'],1);self.assertTrue(report['budget_after']['frozen'])
        self.assertEqual(report['not_run'],['J02','J03','J04']);self.assertEqual(self.calls,['failed'])
        self.assertNotIn('private diagnostic',json.dumps(report))
    def test_reviewed_unread14_continuation_never_retries_unknown_turn(self):
        import hashlib
        from packages.capture.openai_transport import PilotTransport,fingerprint
        folder=self.root/'batch';plan=prepare(folder,self.policy_path)
        def stop_at_reviewed_point(path,payload,key):
            if path.endswith('/responses'):
                source=json.loads(payload['input'])['source']
                if source['capture']['item_id']=='J02_m4':
                    self.calls.append(path);raise TimeoutError('private')
            return self.post(path,payload,key)
        base=run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=stop_at_reviewed_point)
        self.assertEqual(base['dispatches'],10)
        before_hash=hashlib.sha256((folder/'report.json').read_bytes()).hexdigest()
        payload=json.loads((folder/'J02_m4.request.json').read_text())['payload']
        transport=PilotTransport(self.root/'ledger',manifest=dict(plan['root_policy'],payloads=[fingerprint(payload)]),key_file=self.key,post=self.post)
        packet=transport.review_packet();transport.accept_reserved_unknown(fingerprint(payload),snapshot_sha256=packet['snapshot_sha256'],approval_ref='fixture-continued-reserve')
        with self.assertRaises(ValueError):run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=self.post,continuation_approval='owner-approved-reserve-retained-unread14',continuation_base_sha256='0'*64)
        report=run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=self.post,continuation_approval='owner-approved-reserve-retained-unread14',continuation_base_sha256=before_hash)
        self.assertEqual(report['dispatches'],14);self.assertEqual(report['cumulative_dispatches'],24)
        self.assertEqual(len(self.calls),48);self.assertIsNone(report['stopped'])
        self.assertEqual(report['cases'][1]['verdict'],'incomplete')
        self.assertEqual(report['cases'][2]['verdict'],'passed_draft_checks')
        self.assertEqual(hashlib.sha256((folder/'report.json').read_bytes()).hexdigest(),before_hash)

    def test_j04_only_plan_has_six_calls_and_never_replays_prior_unknowns(self):
        import hashlib
        from packages.capture.openai_transport import PilotTransport,fingerprint
        folder=self.root/'batch';plan=prepare(folder,self.policy_path)
        def send_until(failed_id):
            def send(path,payload,key):
                if path.endswith('/responses') and json.loads(payload['input'])['source']['capture']['item_id']==failed_id:
                    self.calls.append(path);raise TimeoutError()
                return self.post(path,payload,key)
            return send
        def review_unknown(message):
            payload=json.loads((folder/(message+'.request.json')).read_text())['payload']
            transport=PilotTransport(self.root/'ledger',manifest=dict(plan['root_policy'],payloads=[fingerprint(payload)]),key_file=self.key)
            packet=transport.review_packet();transport.accept_reserved_unknown(fingerprint(payload),snapshot_sha256=packet['snapshot_sha256'],approval_ref='fixture-explicit-'+message)
        run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=send_until('J02_m4'))
        review_unknown('J02_m4')
        base=hashlib.sha256((folder/'report.json').read_bytes()).hexdigest()
        mid=run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=send_until('J03_m6'),continuation_approval='owner-approved-reserve-retained-unread14',continuation_base_sha256=base)
        self.assertEqual(mid['dispatches'],8)
        review_unknown('J03_m6')
        mid_hash=hashlib.sha256((folder/'continuation-report.json').read_bytes()).hexdigest()
        final=run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=self.post,continuation_approval='owner-approved-reserve-retained-J04only6',continuation_base_sha256=mid_hash)
        self.assertEqual(final['dispatches'],6);self.assertEqual(final['cumulative_dispatches'],24)
        self.assertEqual(len(self.calls),48);self.assertEqual(final['not_run'],[])
        self.assertEqual(final['cases'][1]['verdict'],'incomplete');self.assertEqual(final['cases'][2]['verdict'],'incomplete')
        self.assertEqual(final['cases'][3]['verdict'],'passed_draft_checks')
        self.assertEqual(hashlib.sha256((folder/'continuation-report.json').read_bytes()).hexdigest(),mid_hash)

    def test_expired_approval_is_not_renewed(self):
        self.policy_path.write_text(json.dumps(dict(self.policy,expires_at=1)));folder=self.root/'batch';prepare(folder,self.policy_path)
        with self.assertRaises(ValueError):run(folder,ledger_path=self.root/'ledger',key_file=self.key,post=self.post)
        self.assertEqual(self.calls,[])

if __name__=='__main__':unittest.main()

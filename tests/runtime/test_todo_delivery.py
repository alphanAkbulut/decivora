"""Independent negative/positive tests for concrete TODO development slices."""
import base64,copy,hashlib,json,subprocess,sys,unittest
from pathlib import Path
import test_questions as fixtures
from packages.capture.claude_code.hooks import ClaudeHookCapture,parse,MAX_PACKET_BYTES
from packages.capture.conversations import ConversationService,anchored
from packages.capture.responses_extractor import source_envelope
from packages.domain.source_event import ContractError
from packages.reconciliation.orphan_audit import OrphanAudit
from packages.analytics.paired_cost import compare
from packages.verification.github_commit import GitHubCommitObserver
from packages.storage.workspace import Workspace

class ClaudeHookTests(unittest.TestCase):
    def setUp(self):
        fixtures.QuestionTests.setUp(self);self.adapter=ClaudeHookCapture(self.core)
        self.binding=dict(capture_id='claude_selected',session_id='session_one',cwd='/synthetic/project',provider_version='fixture_1',consent=True)
        self.adapter.connect(self.owner,'p',**self.binding)
    def packet(self,**fields):return json.dumps(dict(dict(session_id='session_one',cwd='/synthetic/project',hook_event_name='UserPromptSubmit',prompt='Please implement a backup.'),**fields)).encode()
    def collect(self,raw=None,delivery='one'):return self.adapter.collect(self.owner,'p',capture_id='claude_selected',delivery_id=delivery,raw=self.packet() if raw is None else raw)
    def sources(self):return ConversationService(self.core).view(self.owner,'p')['imports']
    def test_public_user_and_assistant_text_are_queued_with_partial_provenance(self):
        self.collect();self.collect(self.packet(hook_event_name='Stop',last_assistant_message='I implemented the backup.'),'two')
        sources=self.sources();self.assertEqual(len(sources),2);self.assertEqual({s['source']['capture']['observed_actor'] for s in sources},{'user','assistant'})
        self.assertTrue(all(s['source']['source_kind']=='claude_code_hook' for s in sources));self.assertEqual(len(ConversationService(self.core)._rows('p','conversation_enqueued')),2)
        self.assertEqual(self.core.records(self.owner,'p')['records'],[])
        for item in sources:
            source=item['source'];self.assertEqual(source_envelope(source)['capture'],source['capture'])
            with self.assertRaises(ContractError):anchored(source,dict(source_id=source['id'],source_sha256=source['sha256'],coverage='complete',candidates=[]))
    def test_prior_selected_hook_context_is_bounded_and_role_preserved(self):
        from packages.capture.dialogue_review import DialogueReviewService
        self.collect()
        # A different capture surface with the same local IDs is never prior context.
        ConversationService(self.core)._ingest(self.owner,'p',text='Foreign surface private note',capture=dict(source_surface='codex_app_server',id='claude_selected',thread_id='session_one',turn_id='foreign',item_id='foreign',observed_actor='user'))
        receipt=self.collect(self.packet(hook_event_name='Stop',last_assistant_message='I will use SQLite.'),'two')
        context=DialogueReviewService(self.core).prepare(self.owner,'p',source_id=receipt['source'])['request']['context']
        self.assertEqual(len(context['capture_context']['messages']),1)
        message=context['capture_context']['messages'][0];self.assertEqual(message['observed_actor'],'user');self.assertIsNone(message['turn_id'])
        self.assertEqual(context['coverage']['source_history_included'],'bounded_selected_capture')

    def test_retry_is_idempotent_and_same_delivery_changed_content_conflicts(self):
        first=self.collect();self.assertEqual(first,self.collect());self.assertEqual(len(self.sources()),1)
        with self.assertRaises(ContractError):self.collect(self.packet(prompt='Different prompt'))
        self.assertEqual(len(self.sources()),1)
    def test_repeated_text_with_different_delivery_retains_distinct_occurrences(self):
        self.collect();self.collect(delivery='two');self.assertEqual(len(self.sources()),2)
    def test_missing_assistant_text_is_not_healthy_complete_capture(self):
        r=self.collect(self.packet(hook_event_name='Stop'));self.assertEqual(r['state'],'Assistant text unavailable');self.assertIsNone(r['source']);self.assertEqual(self.sources(),[])
    def test_bound_session_and_cwd_cannot_be_changed_by_hook(self):
        for fields in (dict(session_id='foreign'),dict(cwd='/other')):
            with self.assertRaises(ContractError):self.collect(self.packet(**fields))
        self.assertEqual(self.sources(),[])
    def test_consent_foreign_scope_revoke_and_reconnect_fail_closed(self):
        with self.assertRaises(ContractError):self.adapter.connect(self.owner,'p',**dict(self.binding,capture_id='new',consent=False))
        with self.assertRaises(ContractError):self.adapter.collect(self.owner,'foreign',capture_id='claude_selected',delivery_id='one',raw=self.packet())
        self.adapter.disconnect(self.owner,'p',capture_id='claude_selected')
        with self.assertRaises(ContractError):self.collect()
        with self.assertRaises(ContractError):self.adapter.connect(self.owner,'p',**self.binding)
    def test_authz_revision_change_invalidates_local_binding(self):
        a=self.core.authority;a.replace_grant(self.owner,'owner',kind='human',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision())
        self.owner=a.issue_scope('owner')
        with self.assertRaises(ContractError):self.collect()
    def test_private_tools_paths_and_unknown_hooks_are_not_ingested(self):
        self.collect(self.packet(transcript_path='/do/not/read/private.jsonl',tool_result='PRIVATE_TOOL_OUTPUT',thinking='PRIVATE_REASONING'))
        saved=json.dumps(self.sources());self.assertNotIn('PRIVATE_TOOL_OUTPUT',saved);self.assertNotIn('PRIVATE_REASONING',saved);self.assertNotIn('/do/not/read',saved)
        with self.assertRaises(ContractError):self.collect(self.packet(hook_event_name='PostToolUse'),'tool')
    def test_secrets_are_redacted_before_source_storage(self):
        secret='sk-proj-'+'SYNTHETIC9'*4;self.collect(self.packet(prompt='password="'+secret+'"'))
        saved=json.dumps(self.sources());self.assertNotIn(secret,saved);self.assertIn('[REDACTED]',saved)
    def test_bad_packet_duplicate_json_and_bounds_fail_without_partial_writes(self):
        for raw in (b'{}',b'{"session_id":"a","session_id":"b"}',b'\xff',b'['*10000,b'x'*(MAX_PACKET_BYTES+1),self.packet(prompt='x'*12001),self.packet(prompt='\ud800'),self.packet(cwd='/\ud800')):
            with self.assertRaises(ContractError):self.collect(raw)
        self.assertEqual(self.sources(),[])
    def test_source_queue_and_hook_receipt_rollback_together(self):
        self.core.db.execute("CREATE TRIGGER fail_hook BEFORE INSERT ON audit WHEN NEW.action='claude_hook_received' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.collect()
        self.assertEqual(self.sources(),[]);self.assertEqual(ConversationService(self.core)._rows('p','conversation_enqueued'),[])
    def test_backup_restore_preserves_binding_and_dedup(self):
        r=self.collect();p=Path(self.temp.name)/'backup.sqlite';m=self.core.backup(self.owner,p)
        with Workspace.restore(p,Path(self.temp.name)/'restored.sqlite',m) as core:
            receipt=ClaudeHookCapture(core).collect(core.authority.issue_scope('owner'),'p',capture_id='claude_selected',delivery_id='one',raw=self.packet());self.assertEqual(receipt,r)
    def test_cli_collection_is_silent_and_does_not_install_settings(self):
        p=self.core.db.execute('PRAGMA database_list').fetchone()[2]
        args=[sys.executable,'-B','scripts/capture_claude_hook.py','--db',p,'--workspace',self.core.workspace,'--principal','owner','--project','p','--capture-id','claude_selected','--mode','collect','--delivery-id','cli_one']
        result=subprocess.run(args,input=self.packet(),capture_output=True);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout,b'');self.assertEqual(result.stderr,b'')
        result=subprocess.run(args,input=b'private bad input',capture_output=True);self.assertEqual(result.returncode,1);self.assertEqual(result.stdout,b'');self.assertNotIn(b'private',result.stderr)

class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.data=b'Synthetic evidence\n';self.calls=[];self.body=dict(type='file',path='docs/check.md',encoding='base64',size=len(self.data),content=base64.b64encode(self.data).decode(),sha=hashlib.sha1(b'blob '+str(len(self.data)).encode()+b'\0'+self.data).hexdigest())
        self.args=dict(repository='owner/repo',commit='a'*40,path='docs/check.md',expected_sha256=hashlib.sha256(self.data).hexdigest())
        self.observer=GitHubCommitObserver(self.fetch)
    def fetch(self,url):self.calls.append(url);return dict(self.body)
    def test_exact_commit_match_is_not_acceptance_or_branch_freshness(self):
        r=self.observer.observe(**self.args);self.assertEqual(r['status'],'content_match');self.assertFalse(r['acceptance_verified']);self.assertEqual(r['branch_freshness'],'not_checked');self.assertTrue(self.calls[0].endswith('?ref='+'a'*40))
    def test_mismatch_preserves_observation_not_done(self):
        self.assertEqual(self.observer.observe(**dict(self.args,expected_sha256='b'*64))['status'],'content_mismatch')
    def test_path_commit_repository_injection_never_calls_transport(self):
        for fields in (dict(repository='https://private/path'),dict(repository='../repo'),dict(commit='main'),dict(path='../secret'),dict(path='/secret'),dict(path='file\nAuthorization: value')):
            with self.assertRaises(ContractError):self.observer.observe(**dict(self.args,**fields))
        self.assertEqual(self.calls,[])
    def test_bad_response_encoding_blob_size_and_path_are_rejected(self):
        original=dict(self.body)
        for fields in (dict(type='dir'),dict(content='!!!'),dict(sha='0'*40),dict(size=True),dict(size=2000000),dict(path='other'),dict(encoding='none')):
            self.body=dict(original,**fields)
            with self.assertRaises(ContractError):self.observer.observe(**self.args)
    def test_transport_timeout_is_unknown_and_no_retry(self):
        def fetch(url):self.calls.append(url);raise TimeoutError('PRIVATE_PROVIDER_MESSAGE')
        r=GitHubCommitObserver(fetch).observe(**self.args);self.assertEqual(r['status'],'unknown');self.assertNotIn('PRIVATE_PROVIDER_MESSAGE',json.dumps(r));self.assertEqual(len(self.calls),1)

class OrphanTests(unittest.TestCase):
    def setUp(self):
        fixtures.QuestionTests.setUp(self)
        plan=self.core.plan(self.owner,'p','fixture',[dict(op='create',id='task',body=dict(type='Task',title='Task',description='Synthetic')),dict(op='create',id='reason',body=dict(type='Decision',title='Reason',description='Synthetic'))]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
    def test_unlinked_task_requires_review_not_automatic_obsolete(self):
        before=self.core.db.total_changes;r=OrphanAudit(self.core).run(self.owner,'p');self.assertEqual(self.core.db.total_changes,before);self.assertEqual(len(r['findings']),1);self.assertFalse(r['findings'][0]['auto_cancel']);self.assertEqual(r['canonical_mutations'],0)
    def test_active_rationale_removes_structural_finding_and_scope_is_checked(self):
        rows=self.core.records(self.owner,'p')['records'];task=next(r['id'] for r in rows if r['body']['type']=='Task');reason=next(r['id'] for r in rows if r['body']['type']=='Decision');plan=self.core.plan(self.owner,'p','link',[dict(op='link',origin=task,target=reason,kind='required_by')]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan));self.assertEqual(OrphanAudit(self.core).run(self.owner,'p')['findings'],[])
        with self.assertRaises(ContractError):OrphanAudit(self.core).run(self.owner,'foreign')

class PairedCostTests(unittest.TestCase):
    def rows(self):return [dict(case_id='case1',arm=arm,cost_microusd=cost,quality_passed=True,input_tokens=100,output_tokens=20,model=arm,price_snapshot_id='fixture_only') for arm,cost in [('baseline',100),('candidate',60)]]
    def test_equal_quality_cost_savings(self):
        r=compare(self.rows());self.assertEqual(r['savings_microusd'],40);self.assertEqual(r['savings_percent'],40);self.assertFalse(r['invoice_verified']);self.assertFalse(r['quality_labels_verified'])
    def test_quality_regression_cannot_be_reported_as_savings(self):
        rows=self.rows();rows[1]['quality_passed']=False;r=compare(rows);self.assertIsNone(r['savings_microusd']);self.assertEqual(r['quality_regressions'],['case1'])
    def test_unknown_cost_and_quality_are_not_zero_or_pass(self):
        rows=self.rows();rows[1]['cost_microusd']=None;rows[1]['quality_passed']=None;r=compare(rows);self.assertIsNone(r['cost_microusd']['candidate']);self.assertIsNone(r['savings_percent'])
    def test_unpaired_duplicates_negative_bool_and_missing_fields_rejected(self):
        rows=self.rows()
        for values in (rows[:1],rows+rows,[],[dict(rows[0],cost_microusd=-1),rows[1]],[dict(rows[0],cost_microusd=True),rows[1]],[dict(rows[0],extra='unknown'),rows[1]]):
            with self.assertRaises(ContractError):compare(values)

class AcceptanceInventoryTests(unittest.TestCase):
    def test_missing_evidence_is_not_accepted_mvp(self):
        import tempfile
        from packages.analytics.acceptance_inventory import assess,template
        with tempfile.TemporaryDirectory() as temp:
            report=assess(temp,template());self.assertEqual(len(report['checks']),14);self.assertFalse(report['all_declared_passes_current']);self.assertFalse(report['release_authorized'])
    def test_declared_passes_bind_exact_content_and_do_not_grant_human_authority(self):
        import tempfile
        from packages.analytics.acceptance_inventory import assess,template
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'evidence.json';p.write_text('{}');m=template()
            for row in m['checks']:row.update(status='passed',reason='Synthetic reference fixture, not actual acceptance',evidence=[dict(path=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())])
            r=assess(temp,m);self.assertTrue(r['all_declared_passes_current']);self.assertFalse(r['human_acceptance_verified']);self.assertFalse(r['release_authorized'])
            p.write_text('{"new":1}');self.assertTrue(all(r['effective_status']=='stale' for r in assess(temp,m)['checks']))
    def test_duplicate_criteria_pass_without_evidence_and_escape_are_rejected(self):
        import tempfile
        from packages.analytics.acceptance_inventory import assess,template
        with tempfile.TemporaryDirectory() as temp:
            m=template();m['checks'][1]['id']='AC-01'
            with self.assertRaises(ContractError):assess(temp,m)
            m=template();m['checks'][0]['status']='passed'
            with self.assertRaises(ContractError):assess(temp,m)
            m['checks'][0]['evidence']=[dict(path='../private',sha256='0'*64)]
            with self.assertRaises(ContractError):assess(temp,m)
    def test_symlink_and_missing_evidence_are_not_trusted(self):
        import tempfile
        from packages.analytics.acceptance_inventory import assess,template
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'link';p.symlink_to('/does/not/exist');m=template();m['checks'][0]['evidence']=[dict(path='link',sha256='0'*64)]
            with self.assertRaises(ContractError):assess(temp,m)
            m['checks'][0]['evidence'][0]['path']='missing';self.assertEqual(assess(temp,m)['checks'][0]['effective_status'],'stale')

class LocalPackageTests(unittest.TestCase):
    def test_adapter_entrypoints_ship_without_database_keys_or_transcripts(self):
        import tempfile,zipfile,importlib.util
        spec=importlib.util.spec_from_file_location('package_preview',Path('scripts/package_local_preview.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'local.zip';module.build(p)
            with zipfile.ZipFile(p) as archive:
                names=archive.namelist();self.assertIn('Decivora-local/scripts/capture_claude_hook.py',names);self.assertIn('Decivora-local/packages/capture/claude_code/hooks.py',names)
                self.assertFalse(any(n.endswith(('.sqlite','.jsonl','.env')) or '/secrets/' in n for n in names))

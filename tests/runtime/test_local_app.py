"""Local UI HTTP boundary and persistent commands; no external network/API."""
from pathlib import Path
import tempfile,threading,json,unittest,time
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from apps.local_ui.server import make_server,LocalApp

class LocalAppTests(unittest.TestCase):
    def test_decision_impact_http_is_separate_from_task_mutation(self):
        with self.server.app.core() as core:
            owner=core.authority.issue_scope('local_owner')
            plan=core.plan(owner,'personal','impact_seed',[dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='Synthetic')),dict(op='create',id='t',body=dict(type='Task',title='Dependent',description='Synthetic')),dict(op='link',origin='t',target='d',kind='required_by')])
            ids=core.apply(owner,plan,core.approve(owner,plan))['temp_ids'];revision=core.project(owner,'personal')['knowledge_revision']
        request=dict(action='preview_decision_change',decision=ids['d'],decision_version=1,base_revision=revision,key='http_impact')
        code,result,_=self.call('/api/command',request);self.assertEqual(code,200);self.assertEqual(result['canonical_mutations'],0)
        state=self.call('/api/state')[1];self.assertEqual(state['snapshot'],revision);self.assertEqual(state['tasks'][0]['lane'],'To Do');self.assertEqual(len(state['impact_reviews']),1)
        self.assertEqual(self.call('/api/command',dict(request,base_revision=revision-1))[0],409)

    def setUp(self):
        from test_conversations import install_fixture_analysis_grants
        fixture=install_fixture_analysis_grants();fixture.start();self.addCleanup(fixture.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'app.sqlite';self.server=make_server(self.path);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.addCleanup(self.stop)
        self.origin=self.server.origin;self.headers={'Origin':self.origin,'Cookie':'decivora_session='+self.server.app.cookie,'X-CSRF-Token':self.server.app.csrf,'Content-Type':'application/json'}
    def stop(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
    def call(self,path,body=None,headers=None):
        req=Request(self.origin+path,data=json.dumps(body).encode() if body is not None else None,headers=self.headers if headers is None else headers)
        try:
            with urlopen(req,timeout=5) as r:return r.status,json.loads(r.read()) if r.headers['Content-Type']=='application/json' else r.read(),dict(r.headers)
        except HTTPError as e:return e.code,json.loads(e.read()),dict(e.headers)
    def test_unauthenticated_reads_and_cross_origin_writes_denied(self):
        self.assertEqual(self.call('/api/state',headers={})[0],401)
        self.assertEqual(self.call('/api/command',dict(action='start',task='x'),dict(self.headers,Origin='https://evil.example'))[0],403)
        self.assertEqual(self.call('/api/command',{},dict(self.headers,**{'X-CSRF-Token':''}))[0],403)
    def test_locale_assets_allowlisted_and_unknown_files_denied(self):
        for path in ('/i18n.js','/locales.js'):
            code,body,headers=self.call(path,headers={})
            self.assertEqual(code,200);self.assertIn(b'Decivora',body)
            self.assertIn('javascript',headers['Content-Type'])
        self.assertEqual(self.call('/server.py')[0],404)
        self.assertEqual(self.call('/locales.js/../server.py')[0],404)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])

    def test_bad_host_and_unknown_path_denied(self):
        self.assertEqual(self.call('/api/state',headers=dict(self.headers,Host='evil.example'))[0],403)
        self.assertEqual(self.call('/../../workspace.sqlite')[0],404)
    def test_session_cookie_is_http_only_and_strict_and_no_cors(self):
        code,body,headers=self.call('/api/session',{},dict(Origin=self.origin,Authorization='Bearer '+self.server.app.bootstrap))
        self.assertEqual(code,200);self.assertIn('HttpOnly',headers['Set-Cookie']);self.assertIn('SameSite=Strict',headers['Set-Cookie']);self.assertNotIn('Access-Control-Allow-Origin',headers)
    def test_task_persists_after_restart_and_not_false_done(self):
        self.assertEqual(self.call('/api/command',dict(action='create_task',title='Actual manual task',description='Persistent'))[0],200)
        state=LocalApp(self.path).state();self.assertEqual(state['tasks'][0]['lane'],'To Do');self.assertFalse(state['tasks'][0]['acceptance']['completed'])
    def test_real_http_acceptance_start_flow(self):
        self.call('/api/command',dict(action='create_task',title='Task',description='Scope'));task=self.call('/api/state')[1]['tasks'][0]
        self.assertEqual(self.call('/api/command',dict(action='start',task=task['id']))[0],409)
        row=lambda rid:dict(id=rid,statement='Observed result',method='human_review',required=True,applicable=True,applicability_reason='')
        command=dict(action='acceptance',task=task['id'],task_version=task['version'],base_contract=0,criteria=[row('AC1')],dod=[row('DOD1')],reason='Explicit owner approval',acknowledged_changes=[])
        self.assertEqual(self.call('/api/command',command)[0],200);self.assertEqual(self.call('/api/command',dict(action='start',task=task['id']))[0],200)
        task=self.call('/api/state')[1]['tasks'][0];self.assertEqual(task['lane'],'In Progress');self.assertFalse(task['acceptance']['completed'])
    def test_shell_action_and_extra_fields_do_not_write(self):
        self.assertEqual(self.call('/api/command',dict(action='shell',command='no'))[0],409)
        self.assertEqual(self.call('/api/command',dict(action='create_task',title='Task',description='',project='foreign'))[0],409)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])
    def test_authenticated_write_rate_limit_preserves_existing_state(self):
        self.server.app.window=int(time.monotonic()//60);self.server.app.writes=30
        self.assertEqual(self.call('/api/command',dict(action='create_task',title='Over limit',description=''))[0],429)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])

    def test_private_new_db_and_default_scaffold_has_no_server_side_effects(self):
        self.assertEqual(self.path.stat().st_mode&0o777,0o600)
        self.assertFalse(self.call('/api/state')[1]['capabilities']['semantic_extraction'])

    def test_question_http_flow_and_reload_preserve_selection(self):
        body=dict(action='ask_question',request_id='Q1',text='Storage?',options=[dict(id='sqlite',label='SQLite'),dict(id='files',label='Files')])
        self.assertEqual(self.call('/api/command',body)[0],200)
        self.assertEqual(self.call('/api/state')[1]['question_inbox']['questions'][0]['status'],'Open')
        answer=dict(action='answer_question',request_id='a1',question='Q1',revision=1,option='sqlite')
        code,result,_=self.call('/api/command',answer);self.assertEqual(code,200);self.assertEqual(result['status'],'Selected');self.assertFalse(result['canonical_apply'])
        self.assertEqual(LocalApp(self.path).state()['question_inbox']['questions'][0]['selection'],'sqlite')
        self.assertEqual(self.call('/api/command',answer)[1],result)

    def test_http_decision_requires_separate_approval_and_apply(self):
        self.call('/api/command',dict(action='ask_question',request_id='Q1',text='Storage?',options=[dict(id='sqlite',label='SQLite'),dict(id='files',label='Files')]))
        self.call('/api/command',dict(action='answer_question',request_id='a1',question='Q1',revision=1,option='sqlite'))
        self.assertEqual(self.call('/api/command',dict(action='prepare_decision',key='d1',answer_id='a1',reason='Persistent data'))[0],200)
        self.assertEqual(self.call('/api/command',dict(action='apply_decision',key='d1',approval='forged'))[0],409)
        token=self.call('/api/command',dict(action='approve_decision',key='d1'))[1]['approval']
        self.assertEqual(self.call('/api/state')[1]['decision_proposals'][0]['state'],'Approved')
        self.assertEqual(self.call('/api/command',dict(action='apply_decision',key='d1',approval=token))[0],200)
        self.assertEqual(self.call('/api/state')[1]['decision_proposals'][0]['state'],'Applied')
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])

    def test_http_orphan_reassociation_and_cancelled_answer(self):
        self.assertEqual(self.call('/api/command',dict(action='answer_question',request_id='a1',question='Q1',revision=1,option='sqlite'))[1]['status'],'Unmatched')
        self.call('/api/command',dict(action='ask_question',request_id='Q1',text='Storage?',options=[dict(id='sqlite',label='SQLite'),dict(id='files',label='Files')]))
        self.assertEqual(self.call('/api/command',dict(action='associate_answer',request_id='link',answer_id='a1'))[1]['status'],'Selected')
        self.assertEqual(self.call('/api/command',dict(action='question_state',request_id='cancel',question='Q1',revision=1,base_state=0,status='Cancelled',reason='Stopped'))[0],200)
        self.assertEqual(self.call('/api/command',dict(action='answer_question',request_id='a2',question='Q1',revision=1,option='files'))[1]['status'],'Cancelled')

    def test_actual_manual_import_waits_without_configured_model(self):
        code,result,_=self.call('/api/command',dict(action='import_conversation',text='Please add a backup test.'))
        self.assertEqual(code,200);self.assertEqual(result['analysis']['status'],'Waiting for model');state=self.call('/api/state')[1];self.assertFalse(state['model_ready']);self.assertEqual(state['tasks'],[]);self.assertEqual(len(state['conversation_review']['imports']),1)
    def test_fixture_extractor_import_review_to_board(self):
        from test_conversations import Extractor,TEXT
        self.server.app.extractor=Extractor();result=self.call('/api/command',dict(action='import_conversation',text=TEXT))[1];self.assertEqual(result['analysis']['status'],'Ready for review')
        state=self.call('/api/state')[1];candidate=state['conversation_review']['imports'][0]['candidates'][0]
        self.assertEqual(self.call('/api/command',dict(action='accept_candidates',source_id=result['source']['id'],key='accept',selected=[candidate['id']],base_revision=state['conversation_review']['knowledge_revision']))[0],200)
        task=self.call('/api/state')[1]['tasks'][0];self.assertEqual(task['lane'],'To Do');self.assertFalse(task['acceptance']['completed'])

    def test_dependency_http_approval_retry_and_cycle(self):
        self.call('/api/command',dict(action='create_task',title='A',description=''))
        self.call('/api/command',dict(action='create_task',title='B',description=''))
        state=self.call('/api/state')[1];a,b=[t['id'] for t in state['tasks']]
        command=dict(action='link_dependency',task=a,target=b,base_revision=state['snapshot'],key='dep1')
        first=self.call('/api/command',command);self.assertEqual(first[0],200);self.assertEqual(self.call('/api/command',command)[1],first[1])
        view=self.call('/api/state')[1];by_id={t['id']:t for t in view['tasks']}
        self.assertEqual(by_id[a]['workflow']['assessment']['dependencies'][0]['id'],b)
        self.assertIn(a,by_id[b]['workflow']['assessment']['blocks'])
        cycle=dict(action='link_dependency',task=b,target=a,base_revision=view['snapshot'],key='dep2')
        self.assertEqual(self.call('/api/command',cycle)[0],409)
    def test_workflow_http_extra_fields_and_fake_verifier_denied(self):
        self.call('/api/command',dict(action='create_task',title='A',description=''))
        task=self.call('/api/state')[1]['tasks'][0]
        command=dict(action='workflow_transition',task=task['id'],task_version=1,base_revision=0,stage='Done',reason='Agent says done',key='fake',scope_reviewed=True)
        self.assertEqual(self.call('/api/command',command)[0],409)
        self.assertEqual(self.call('/api/command',dict(command,project='other'))[0],409)
        self.assertEqual(self.call('/api/state')[1]['tasks'][0]['lane'],'To Do')

    def test_private_backup_http_restore_round_trip_and_no_source_mutation(self):
        import io,zipfile,hashlib
        from packages.storage.local_backup import inspect_bundle
        self.call('/api/command',dict(action='create_task',title='Backup fixture task',description='Private scope'))
        self.call('/api/command',dict(action='import_conversation',text='Private backup source fixture marker'))
        self.call('/api/command',dict(action='ask_question',request_id='backup_question',text='Keep this scope?',options=[dict(id='yes',label='Keep'),dict(id='no',label='Review')]))
        before=self.call('/api/state')[1]
        code,raw,headers=self.call('/api/backup',dict(acknowledge_private_data=True))
        self.assertEqual(code,200);self.assertEqual(headers['Content-Type'],'application/zip')
        checked=inspect_bundle(raw);self.assertTrue(checked['restore_checked']);self.assertEqual(checked['external_dispatches'],0)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            self.assertEqual(set(z.namelist()),{'workspace.sqlite','manifest.json'})
            self.assertEqual(hashlib.sha256(z.read('workspace.sqlite')).hexdigest(),checked['manifest']['sha256'])
            self.assertNotIn(self.server.app.cookie.encode(),z.read('workspace.sqlite'))
            self.assertNotIn(self.server.app.bootstrap.encode(),z.read('workspace.sqlite'))
            self.assertIn(b'Private backup source fixture marker',z.read('workspace.sqlite'))
            self.assertIn(b'Keep this scope?',z.read('workspace.sqlite'))
        after=self.call('/api/state')[1];self.assertEqual(before['tasks'],after['tasks']);self.assertEqual(before['snapshot'],after['snapshot'])
    def test_backup_ack_scope_auth_and_get_denied(self):
        self.assertEqual(self.call('/api/backup')[0],404)
        self.assertEqual(self.call('/api/backup',dict(acknowledge_private_data=True),{'Origin':self.origin,'Content-Type':'application/json'})[0],403)
        for body in ({},{'acknowledge_private_data':False},{'acknowledge_private_data':True,'path':'/tmp/arbitrary'}):self.assertEqual(self.call('/api/backup',body)[0],409)
        self.assertEqual(self.call('/api/backup',dict(acknowledge_private_data=True),dict(self.headers,Origin='https://other.example'))[0],403)
        self.assertEqual(self.call('/api/backup',dict(acknowledge_private_data=True),dict(self.headers,**{'X-CSRF-Token':''}))[0],403)
    def test_backup_busy_limit_and_current_acl_fail_closed(self):
        self.server.app.backup_lock.acquire()
        try:self.assertEqual(self.call('/api/backup',dict(acknowledge_private_data=True))[1]['error'],'backup_busy')
        finally:self.server.app.backup_lock.release()
        self.server.app.window=int(time.monotonic()//60);self.server.app.writes=30
        self.assertEqual(self.call('/api/backup',dict(acknowledge_private_data=True))[0],429)
        self.server.app.writes=0
        with self.server.app.core() as core:
            a=core.authority;owner=a.issue_scope('local_owner');a.replace_grant(owner,'local_owner',kind='human',readable=frozenset(),writable=frozenset(),active=True,base_revision=a.revision())
        self.assertEqual(self.call('/api/backup',dict(acknowledge_private_data=True))[0],409)
    def test_backup_cannot_export_another_workspace_from_same_file(self):
        from packages.storage.workspace import Workspace
        with self.server.app.core() as core:
            core.db.execute("INSERT INTO core_meta SELECT format,'foreign_workspace',schema_version FROM core_meta LIMIT 1")
        code,result,_=self.call('/api/backup',dict(acknowledge_private_data=True));self.assertEqual(code,409);self.assertEqual(result['error'],'unsupported_storage')
    def test_offline_backup_inspection_rejects_corruption_extra_paths_and_bomb(self):
        import io,zipfile
        from packages.storage.local_backup import inspect_bundle,MAX_DATABASE_BYTES
        from packages.domain.source_event import ContractError
        code,valid,_=self.call('/api/backup',dict(acknowledge_private_data=True));self.assertEqual(code,200)
        with zipfile.ZipFile(io.BytesIO(valid)) as z:database=z.read('workspace.sqlite');manifest=z.read('manifest.json')
        for name,data in [('corrupt',b'changed'),('../workspace.sqlite',database),('workspace.sqlite',b'x'*(MAX_DATABASE_BYTES+1))]:
            out=io.BytesIO()
            with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:z.writestr(name,data);z.writestr('manifest.json',manifest)
            with self.assertRaises(ContractError):inspect_bundle(out.getvalue())
        with self.assertRaises(ContractError):inspect_bundle(b'not a zip')

    def test_file_check_http_recipe_and_criterion_results(self):
        import hashlib
        from packages.verification.files import FileChecker
        root=Path(self.temp.name)/'approved-root';root.mkdir();(root/'output.txt').write_bytes(b'approved');self.server.app.file_checker=FileChecker(root)
        self.call('/api/command',dict(action='create_task',title='File criterion',description='Exact file content only'));task=self.call('/api/state')[1]['tasks'][0];row=lambda rid:dict(id=rid,statement='Expected exact file content',method='file_check',required=True,applicable=True,applicability_reason='')
        self.assertEqual(self.call('/api/command',dict(action='acceptance',task=task['id'],task_version=1,base_contract=0,criteria=[row('AC1')],dod=[row('DOD1')],reason='Check coverage approved',acknowledged_changes=[]))[0],200)
        self.call('/api/command',dict(action='start',task=task['id']))
        self.assertEqual(self.call('/api/command',dict(action='workflow_transition',task=task['id'],task_version=1,base_revision=1,stage='In Review',reason='Implementation handed off',key='handoff',scope_reviewed=False))[0],200)
        for rid in ('AC1','DOD1'):
            self.assertEqual(self.call('/api/command',dict(action='bind_file_check',task=task['id'],task_version=1,contract_version=1,criterion=rid,path='output.txt',expected_sha256=hashlib.sha256(b'approved').hexdigest(),reason='This criterion means exactly this file hash',key='bind'+rid))[0],200)
            code,result,_=self.call('/api/command',dict(action='run_file_check',task=task['id'],task_version=1,contract_version=1,criterion=rid,binding_revision=1,key='check'+rid));self.assertEqual(code,200);self.assertEqual(result['status'],'passed')
        current=self.call('/api/state')[1]['tasks'][0];self.assertTrue(current['workflow']['verification']['passed']);self.assertFalse(current['acceptance']['completed'])
        (root/'output.txt').write_bytes(b'changed');self.assertFalse(self.call('/api/state')[1]['tasks'][0]['workflow']['verification']['passed'])
    def test_mcp_proposal_http_review_is_separate_and_agent_role_guarded(self):
        from packages.mcp.server import Server
        with self.server.app.core() as core:
            a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'coding_agent',kind='agent',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision());revision=core.project(a.issue_scope('local_owner'),'personal')['knowledge_revision']
        Server(self.path,'local_ui_workspace','coding_agent').call('submit_changeset',dict(project_id='personal',key='draft',base_revision=revision,operations=[dict(op='create',id='t',body=dict(type='Task',title='Agent draft',description='Human review required'))]))
        self.assertEqual(self.call('/api/state')[1]['agent_proposals'][0]['state'],'Prepared');self.assertEqual(self.call('/api/state')[1]['tasks'],[])
        self.assertEqual(self.call('/api/command',dict(action='apply_agent_proposal',key='draft'))[0],409)
        self.assertEqual(self.call('/api/command',dict(action='approve_agent_proposal',key='draft'))[0],200);self.assertEqual(self.call('/api/state')[1]['tasks'],[])
        self.assertEqual(self.call('/api/command',dict(action='apply_agent_proposal',key='draft'))[0],200);self.assertEqual(len(self.call('/api/state')[1]['tasks']),1)

    def test_recent_health_errors_are_bounded_and_never_store_request_text(self):
        marker='sensitive_payload_marker'
        self.call('/api/command',dict(action='unknown',text=marker))
        for i in range(30):self.call('/private/'+marker+str(i))
        health=self.call('/api/state')[1]['health'];self.assertFalse(health['persistent']);self.assertEqual(len(health['recent_errors']),25);self.assertNotIn(marker,json.dumps(health));self.assertTrue(all(e['endpoint']=='other' for e in health['recent_errors']))

    def test_project_selection_scope_is_explicit_and_tabs_do_not_share_an_active_project(self):
        with self.server.app.core() as core:
            a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal','other'}),writable=frozenset({'personal','other'}),active=True,base_revision=a.revision());core.create_project(a.issue_scope('local_owner'),'other','Same name')
        self.assertEqual(self.call('/api/command',dict(project_id='other',command=dict(action='create_task',title='Other task',description='Only other')))[0],200)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[]);self.assertEqual(self.call('/api/state?project_id=other')[1]['tasks'][0]['body']['title'],'Other task')
        self.assertEqual(len(self.call('/api/state')[1]['project_choices']),2)
        self.assertEqual(self.call('/api/state?project_id=foreign')[0],409)
        self.assertEqual(self.call('/api/state?project_id=other&project_id=personal')[0],400)
        self.assertEqual(self.call('/api/command',dict(project_id='foreign',command=dict(action='create_task',title='Denied',description='')))[0],409)
        self.assertEqual(self.call('/api/state')[1]['tasks'],[])
    def test_project_envelope_extra_fields_and_cross_project_task_id_rejected(self):
        self.call('/api/command',dict(action='create_task',title='Personal task',description=''));task=self.call('/api/state')[1]['tasks'][0]
        with self.server.app.core() as core:
            a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal','other'}),writable=frozenset({'personal','other'}),active=True,base_revision=a.revision());core.create_project(a.issue_scope('local_owner'),'other','Other')
        self.assertEqual(self.call('/api/command',dict(project_id='other',command=dict(action='start',task=task['id'])))[0],409)
        self.assertEqual(self.call('/api/command',dict(project_id='other',command=dict(action='create_task',title='A',description=''),approved=True))[0],409)
        self.assertEqual(self.call('/api/state?project_id=other')[1]['tasks'],[])

    def test_duplicate_source_attachment_preserves_task_links_without_breaking_state(self):
        from test_conversations import Extractor,TEXT
        self.server.app.extractor=Extractor()
        for index,text in enumerate([TEXT,'Extra context. '+TEXT]):
            code,response,_=self.call('/api/command',dict(action='import_conversation',text=text));self.assertEqual(code,200);state=self.call('/api/state')[1];source=response['source']['id'];cid=response['analysis']['candidates'][0]['id']
            self.assertEqual(self.call('/api/command',dict(action='accept_candidates',source_id=source,key='review'+str(index),selected=[cid],base_revision=state['snapshot']))[0],200)
        code,state,_=self.call('/api/state');self.assertEqual(code,200);self.assertEqual(len(state['tasks']),1);self.assertEqual(len(state['task_sources'][state['tasks'][0]['id']]),2)

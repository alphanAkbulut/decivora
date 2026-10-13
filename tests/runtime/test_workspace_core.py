"""Normalized local core acceptance with real SQLite/restart/rollback, synthetic data."""
from dataclasses import replace
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from packages.domain.project_binding import SessionKey
from packages.domain.source_event import ContractError,validate_source_event
from packages.storage.workspace import Workspace
from packages.capture.extraction import validate_candidates,lexical_context,semantic_dispatch
from packages.reconciliation.core import reconcile

ROOT=Path(__file__).resolve().parents[2]


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'core.sqlite'
        self.core=Workspace(self.path,'workspace',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority
        a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=1)
        self.owner=a.issue_scope('owner')
        self.core.create_project(self.owner,'p1','Aynı proje');self.core.create_project(self.owner,'p2','Aynı proje')
        self.key=SessionKey('manual','account','session_fixture','epoch')
        self.event=validate_source_event(dict(json.loads((ROOT/'examples/runtime/source-event.json').read_text()),project_id='p1'))

    def assert_code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)

    def apply(self,ops,key='command'):
        plan=self.core.plan(self.owner,'p1',key,ops)
        approval=self.core.approve(self.owner,plan)
        return self.core.apply(self.owner,plan,approval),plan,approval

    def body(self,title='İş',description='Kaynaklı açıklama'):
        return dict(type='Task',title=title,description=description)

    def test_normalized_composite_foreign_key_blocks_cross_workspace_binding(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.core.db.execute("INSERT INTO bindings VALUES ('other','manual','account','session','epoch',1,'p1','owner')")
        self.assertEqual(self.core.db.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_same_names_and_archive_revision_survive_reopen(self):
        self.core.update_project(self.owner,'p1',base_revision=1,name='Yeni',archived=True)
        self.assert_code('stale_base',lambda:self.core.update_project(self.owner,'p1',base_revision=1,name='Lost'))
        with Workspace(self.path,'workspace') as reopened:
            owner=reopened.authority.issue_scope('owner')
            self.assertTrue(reopened.project(owner,'p1')['archived'])
            self.assertEqual(reopened.project(owner,'p2')['name'],'Aynı proje')

    def test_pinning_new_binding_does_not_move_prior_receipt(self):
        self.core.bind(self.owner,self.key,'p1',0)
        first=self.core.receive(self.owner,self.key,self.event,1)
        self.core.bind(self.owner,self.key,'p2',1)
        second=self.core.receive(self.owner,self.key,replace(self.event,event_id='new',project_id='p2'),2)
        self.assertEqual((first['project'],first['binding_revision']),('p1',1))
        self.assertEqual((second['project'],second['binding_revision']),('p2',2))
        self.assertEqual(self.core.source(self.owner,first['seq'])['project'],'p1')

    def test_unbound_and_mismatch_are_durable_quarantine_without_project_mutation(self):
        first=self.core.receive(self.owner,self.key,self.event,1)
        self.assertEqual(first['status'],'quarantined')
        self.core.bind(self.owner,self.key,'p2',0)
        second=self.core.receive(self.owner,self.key,replace(self.event,event_id='second'),2)
        self.assertEqual(second['reason'],'project_mismatch')
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM jobs').fetchone()[0],0)
        self.assertEqual(self.core.project(self.owner,'p1')['knowledge_revision'],0)
        with Workspace(self.path,'workspace') as other:
            self.assertIsNone(other.source(other.authority.issue_scope('owner'),first['seq'])['project'])

    def test_same_event_dedup_different_message_same_text_and_conflict(self):
        self.core.bind(self.owner,self.key,'p1',0)
        one=self.core.receive(self.owner,self.key,self.event,1)
        retry=self.core.receive(self.owner,self.key,self.event,1)
        two=self.core.receive(self.owner,self.key,replace(self.event,event_id='second'),2)
        self.assertEqual(one['seq'],retry['seq']);self.assertTrue(retry['duplicate'])
        self.assertNotEqual(one['seq'],two['seq'])
        self.assert_code('source_conflict',lambda:self.core.receive(self.owner,self.key,replace(self.event,text='Changed'),1))

    def test_source_and_job_insert_are_atomic_when_disk_write_fails(self):
        self.core.bind(self.owner,self.key,'p1',0)
        self.core.db.executescript("CREATE TRIGGER job_fail BEFORE INSERT ON jobs BEGIN SELECT RAISE(ABORT,'fixture disk failure'); END;")
        self.assert_code('storage_failure',lambda:self.core.receive(self.owner,self.key,self.event,1))
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM sources').fetchone()[0],0)
        self.core.db.execute('DROP TRIGGER job_fail')
        self.assertTrue(self.core.receive(self.owner,self.key,self.event,1)['durable_receipt'])

    def test_out_of_order_frontier_does_not_skip_missing_receipt_or_failed_job(self):
        self.core.bind(self.owner,self.key,'p1',0)
        self.core.receive(self.owner,self.key,replace(self.event,event_id='second'),2)
        self.assertEqual(self.core.frontier(self.owner,self.key,'p1')['received'],0)
        self.core.receive(self.owner,self.key,self.event,1)
        lease=self.core.lease(self.owner,'p1',now=0)
        self.core.finish(self.owner,lease,{'note':'observed processing only'},now=1)
        frontier=self.core.frontier(self.owner,self.key,'p1')
        self.assertEqual(frontier['received'],2);self.assertEqual(frontier['processed'],0)
        lease=self.core.lease(self.owner,'p1',now=2)
        self.core.finish(self.owner,lease,{},now=3)
        self.assertEqual(self.core.frontier(self.owner,self.key,'p1')['processed'],2)

    def test_fencing_expiry_and_bounded_retry_block_old_worker(self):
        self.core.bind(self.owner,self.key,'p1',0);self.core.receive(self.owner,self.key,self.event,1)
        old=self.core.lease(self.owner,'p1',now=0,ttl=5)
        new=self.core.lease(self.owner,'p1',now=5,ttl=5)
        self.assert_code('stale_lease',lambda:self.core.finish(self.owner,old,{},now=6))
        self.core.finish(self.owner,new,{},now=6,success=False,retry_delay=2)
        self.assertIsNone(self.core.lease(self.owner,'p1',now=7))
        third=self.core.lease(self.owner,'p1',now=8,ttl=1)
        failed=self.core.lease(self.owner,'p1',now=9,max_attempts=3)
        self.assertEqual(failed['status'],'failed')
        self.assert_code('stale_lease',lambda:self.core.finish(self.owner,third,{},now=9))

    def test_queue_limit_rejects_new_work_without_erasing_accepted_source(self):
        self.core.bind(self.owner,self.key,'p1',0);self.core.receive(self.owner,self.key,self.event,1,queue_limit=1)
        self.assert_code('queue_full',lambda:self.core.receive(self.owner,self.key,replace(self.event,event_id='second'),2,queue_limit=1))
        self.assertEqual(self.core.frontier(self.owner,self.key,'p1')['received'],1)

    def test_rotation_epoch_does_not_reuse_binding_or_source_identity(self):
        self.core.bind(self.owner,self.key,'p1',0);one=self.core.receive(self.owner,self.key,self.event,1)
        other=replace(self.key,source_epoch='rotated')
        two=self.core.receive(self.owner,other,self.event,1)
        self.assertNotEqual(one['seq'],two['seq']);self.assertEqual(two['reason'],'project_unbound')

    def test_create_link_temp_ids_and_replay_have_same_projection_digest(self):
        ops=[dict(op='link',origin='a',target='b',kind='depends_on'),dict(op='create',id='a',body=self.body('A')),dict(op='create',id='b',body=self.body('B'))]
        result,_,_=self.apply(ops)
        self.assertEqual(len(result['event_sequences']),3)
        before=self.core.projection_digest(self.owner,'p1')
        self.assertEqual(self.core.replay(self.owner,'p1')['digest'],before)
        self.assertEqual(self.core.replay(self.owner,'p1')['model_dispatches'],0)

    def test_invalid_link_rolls_back_records_events_audit_and_command(self):
        ops=[dict(op='create',id='a',body=self.body()),dict(op='link',origin='a',target='missing',kind='related_to')]
        plan=self.core.plan(self.owner,'p1','bad',ops);approval=self.core.approve(self.owner,plan)
        self.assert_code('storage_failure',lambda:self.core.apply(self.owner,plan,approval))
        for table in ('records','edges','events','commands'):
            self.assertEqual(self.core.db.execute('SELECT count(*) FROM '+table).fetchone()[0],0)
        self.assertEqual(self.core.project(self.owner,'p1')['knowledge_revision'],0)

    def test_key_digest_double_submit_and_stale_second_writer(self):
        result,plan,approval=self.apply([dict(op='create',id='a',body=self.body())])
        self.assertEqual(self.core.apply(self.owner,plan,approval),result)
        changed=self.core.plan(self.owner,'p1','command',[dict(op='create',id='b',body=self.body())])
        token=self.core.approve(self.owner,changed)
        self.assert_code('idempotency_conflict',lambda:self.core.apply(self.owner,changed,token))
        p1=self.core.plan(self.owner,'p1','one',[dict(op='create',id='b',body=self.body('B'))])
        p2=self.core.plan(self.owner,'p1','two',[dict(op='create',id='c',body=self.body('C'))])
        a1=self.core.approve(self.owner,p1);a2=self.core.approve(self.owner,p2)
        self.core.apply(self.owner,p1,a1)
        with Workspace(self.path,'workspace') as second:
            self.assert_code('stale_base',lambda:second.apply(second.authority.issue_scope('owner'),p2,a2))

    def test_agent_cannot_approve_or_copy_human_approval_to_apply(self):
        a=self.core.authority
        a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p1'}),writable=frozenset({'p1'}),active=True,base_revision=2)
        self.owner=a.issue_scope('owner');agent=a.issue_scope('agent')
        plan=self.core.plan(agent,'p1','agent_plan',[dict(op='create',id='a',body=self.body())])
        self.assert_code('human_approval_required',lambda:self.core.approve(agent,plan))
        approval=self.core.approve(self.owner,plan)
        self.assert_code('human_approval_required',lambda:self.core.apply(agent,plan,approval))

    def test_revocation_blocks_source_read_and_old_approval(self):
        plan=self.core.plan(self.owner,'p1','plan',[dict(op='create',id='a',body=self.body())]);approval=self.core.approve(self.owner,plan)
        a=self.core.authority
        a.replace_grant(self.owner,'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=2)
        self.assert_code('stale_authority',lambda:self.core.apply(self.owner,plan,approval))
        self.owner=a.issue_scope('owner')
        self.assert_code('invalid_approval',lambda:self.core.apply(self.owner,plan,approval))

    def test_update_versions_append_events_instead_of_erasing_history(self):
        result,_,_=self.apply([dict(op='create',id='a',body=self.body())]);record=result['temp_ids']['a']
        self.apply([dict(op='update',id=record,base_version=1,body=self.body('New'))],key='update')
        self.assertEqual(self.core.records(self.owner,'p1')['records'][0]['version'],2)
        with self.assertRaises(sqlite3.IntegrityError):self.core.db.execute('DELETE FROM events')
        with self.assertRaises(sqlite3.IntegrityError):self.core.db.execute("UPDATE events SET kind='bad'")
        before=self.core.projection_digest(self.owner,'p1')
        self.assertEqual(self.core.replay(self.owner,'p1')['digest'],before)

    def test_cross_project_record_and_link_access_are_denied(self):
        result,_,_=self.apply([dict(op='create',id='a',body=self.body())]);record=result['temp_ids']['a']
        plan=self.core.plan(self.owner,'p2','foreign',[dict(op='update',id=record,base_version=1,body=self.body())])
        approval=self.core.approve(self.owner,plan)
        self.assert_code('stale_record',lambda:self.core.apply(self.owner,plan,approval))
        a=self.core.authority
        a.replace_grant(self.owner,'reader',kind='human',readable=frozenset({'p2'}),writable=frozenset(),active=True,base_revision=2)
        reader=a.issue_scope('reader')
        self.assert_code('forbidden',lambda:self.core.records(reader,'p1'))

    def test_backup_restore_payload_and_projection_manifest(self):
        self.core.bind(self.owner,self.key,'p1',0);receipt=self.core.receive(self.owner,self.key,self.event,1)
        self.apply([dict(op='create',id='a',body=self.body())])
        target=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,target)
        restored_path=Path(self.temp.name)/'restored.sqlite'
        with Workspace.restore(target,restored_path,manifest) as restored:
            owner=restored.authority.issue_scope('owner')
            self.assertEqual(restored.source(owner,receipt['seq'])['event'].text,self.event.text)
            self.assertEqual(restored.projection_digest(owner,'p1'),self.core.projection_digest(self.owner,'p1'))
            self.assertEqual(restored.replay(owner,'p1')['external_dispatches'],0)
        self.assert_code('backup_invalid',lambda:Workspace.restore(target,Path(self.temp.name)/'bad.sqlite',dict(manifest,sha256='bad')))

    def test_abrupt_process_exit_rolls_back_uncommitted_source(self):
        # Actual child-process termination, not an in-process mock of COMMIT.
        program="import sqlite3,os,sys;db=sqlite3.connect(sys.argv[1]);db.execute('BEGIN IMMEDIATE');db.execute(\"INSERT INTO audit(workspace,project,actor,action,ref) VALUES ('workspace','p1','owner','uncommitted','x')\");os._exit(17)"
        run=subprocess.run([sys.executable,'-B','-c',program,str(self.path)],capture_output=True,timeout=10)
        self.assertEqual(run.returncode,17)
        self.assertEqual(self.core.db.execute("SELECT count(*) FROM audit WHERE action='uncommitted'").fetchone()[0],0)

    def test_untrusted_extraction_missing_source_span_truncation_and_dispatch_guard(self):
        output=dict(source_event_id=self.event.event_id,source_revision=1,coverage='partial',candidates=[dict(type='Task',quote=self.event.text,start=0,end=len(self.event.text))])
        self.assertEqual(validate_candidates(self.event,output)['coverage'],'partial')
        self.assert_code('stale_source',lambda:validate_candidates(self.event,dict(output,source_revision=2)))
        invalid=dict(output,candidates=[dict(type='Task',quote='invented',start=0,end=2)])
        self.assert_code('invalid_span',lambda:validate_candidates(self.event,invalid))
        self.assert_code('model_dispatch_disabled',semantic_dispatch)
        self.apply([dict(op='create',id='a',body=self.body('same')),dict(op='create',id='b',body=self.body('same'))])
        records=self.core.records(self.owner,'p1')['records']
        self.assertTrue(lexical_context(records,'same',limit=1)['truncated'])

    def test_reconciliation_duplicate_refinement_no_overwrite_or_auto_revival(self):
        self.apply([dict(op='create',id='a',body=self.body('Idea','Description'))])
        existing=self.core.records(self.owner,'p1')['records']
        candidate=dict(type='Task',title='IDEA',description='Description',source_ref='source_1',intent='proposed')
        self.assertEqual(reconcile(candidate,existing)['recommendation'],'attach_source')
        self.assertEqual(reconcile(dict(candidate,description='New assertion'),existing)['recommendation'],'review_relationship')
        self.assertEqual(reconcile(dict(candidate,intent='rejected'),existing)['canonical_mutations'],0)
        self.assertEqual(existing,self.core.records(self.owner,'p1')['records'])

    def test_scoped_cursor_pagination_and_revision_changes(self):
        self.apply([dict(op='create',id='a',body=self.body('A')),dict(op='create',id='b',body=self.body('B'))])
        first=self.core.records(self.owner,'p1',limit=1)
        second=self.core.records(self.owner,'p1',limit=1,cursor=first['next_cursor'])
        self.assertNotEqual(first['records'][0]['id'],second['records'][0]['id'])
        self.assert_code('stale_cursor',lambda:self.core.records(self.owner,'p2',limit=1,cursor=first['next_cursor']))
        self.apply([dict(op='create',id='c',body=self.body('C'))],key='later')
        self.assert_code('stale_cursor',lambda:self.core.records(self.owner,'p1',limit=1,cursor=first['next_cursor']))

    def test_unknown_command_schema_and_unknown_event_fail_closed(self):
        plan=self.core.plan(self.owner,'p1','bad_version',[dict(op='create',id='a',body=self.body())])
        self.assert_code('invalid_change',lambda:self.core.approve(self.owner,dict(plan,format='future')))
        self.core.db.execute("INSERT INTO events(workspace,project,stream,version,kind,payload) VALUES ('workspace','p1','x',1,'future','{}')")
        self.assert_code('unsupported_event',lambda:self.core.replay(self.owner,'p1'))

    def test_audit_failure_rolls_back_approved_apply(self):
        plan=self.core.plan(self.owner,'p1','audit',[dict(op='create',id='a',body=self.body())]);approval=self.core.approve(self.owner,plan)
        self.core.db.executescript("CREATE TRIGGER audit_fail BEFORE INSERT ON audit WHEN NEW.action='apply' BEGIN SELECT RAISE(ABORT,'fixture'); END;")
        self.assert_code('storage_failure',lambda:self.core.apply(self.owner,plan,approval))
        self.assertEqual(self.core.records(self.owner,'p1')['records'],[])
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM events').fetchone()[0],0)

    def test_shared_parent_budget_atomic_reservations_and_unknown_usage(self):
        self.core.create_budget(self.owner,'p1','root',100)
        one=self.core.reserve(self.owner,'p1','root','child_a',60)
        self.assertEqual(self.core.reserve(self.owner,'p1','root','child_a',60),one)
        with Workspace(self.path,'workspace') as other:
            owner=other.authority.issue_scope('owner')
            self.assert_code('budget_exceeded',lambda:other.reserve(owner,'p1','root','child_b',50))
        self.core.settle(self.owner,'p1','root','child_a',None)
        self.assert_code('budget_exceeded',lambda:self.core.reserve(self.owner,'p1','root','retry',50))
        self.assert_code('idempotency_conflict',lambda:self.core.reserve(self.owner,'p1','root','child_a',20))
        self.core.settle(self.owner,'p1','root','child_a',20)
        self.assertEqual(self.core.reserve(self.owner,'p1','root','child_b',80)['reserved'],80)
        self.assert_code('settlement_conflict',lambda:self.core.settle(self.owner,'p1','root','child_a',0))

    def test_rate_limit_preserves_twenty_receipts_and_reopens_after_window(self):
        self.core.bind(self.owner,self.key,'p1',0)
        for i in range(20):self.core.receive(self.owner,self.key,replace(self.event,event_id='e'+str(i)),i+1,now=0)
        self.assert_code('rate_limited',lambda:self.core.receive(self.owner,self.key,replace(self.event,event_id='next'),21,now=0))
        self.assertEqual(self.core.frontier(self.owner,self.key,'p1')['received'],20)
        self.assertTrue(self.core.receive(self.owner,self.key,replace(self.event,event_id='next'),21,now=60)['durable_receipt'])

    def test_database_rejects_source_binding_project_mismatch(self):
        self.core.bind(self.owner,self.key,'p1',0)
        with self.assertRaises(sqlite3.IntegrityError):
            self.core.db.execute("INSERT INTO sources(workspace,provider,account,session,epoch,event_id,source_revision,position,project,binding_revision,payload,hash,status,reason) VALUES ('workspace','manual','account','session_fixture','epoch','bad',1,1,'p2',1,'{}','x','accepted_pending','')")

    def test_canonical_graph_cycle_is_rejected_before_commit(self):
        ops=[dict(op='create',id='a',body=self.body('A')),dict(op='create',id='b',body=self.body('B')),
             dict(op='link',origin='a',target='b',kind='depends_on'),dict(op='link',origin='b',target='a',kind='depends_on')]
        self.assert_code('graph_cycle',lambda:self.apply(ops))
        self.assertEqual(self.core.records(self.owner,'p1')['records'],[])
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM events').fetchone()[0],0)

    def test_scoped_graph_uses_knowledge_revision_and_never_invents_verification(self):
        result,_,_=self.apply([dict(op='create',id='a',body=self.body())])
        graph=self.core.graph(self.owner,'p1')
        self.assertEqual(graph.revision,1)
        self.assertFalse(graph.assessment(result['temp_ids']['a'])['ready'])

    def test_one_project_queue_cannot_take_all_two_project_pilot_capacity(self):
        self.core.bind(self.owner,self.key,'p1',0)
        for i in range(100):
            self.core.receive(self.owner,self.key,replace(self.event,event_id='q'+str(i)),i+1,now=i//20*60)
        self.assert_code('project_queue_full',lambda:self.core.receive(self.owner,self.key,replace(self.event,event_id='overflow'),101,now=360))
        other=replace(self.key,session_id='session_other')
        self.core.bind(self.owner,other,'p2',0)
        receipt=self.core.receive(self.owner,other,replace(self.event,project_id='p2',session_id='session_other'),1,now=360)
        self.assertTrue(receipt['durable_receipt'])

    def test_job_lease_is_bound_to_current_worker_identity(self):
        self.core.bind(self.owner,self.key,'p1',0);self.core.receive(self.owner,self.key,self.event,1)
        lease=self.core.lease(self.owner,'p1',now=0)
        a=self.core.authority
        a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p1'}),writable=frozenset({'p1'}),active=True,base_revision=2)
        self.assert_code('stale_lease',lambda:self.core.finish(a.issue_scope('agent'),lease,{},now=1))

    def test_finding_prompt_instruction_source_links_survive_replay(self):
        self.core.bind(self.owner,self.key,'p1',0);receipt=self.core.receive(self.owner,self.key,self.event,1)
        ops=[dict(op='create',id=kind.lower(),body=dict(type=kind,title=kind,description='Source-bound'),source_seq=receipt['seq']) for kind in ('Finding','Prompt','DocumentInstruction')]
        self.apply(ops)
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM record_sources').fetchone()[0],3)
        before=self.core.projection_digest(self.owner,'p1')
        self.assertEqual(self.core.replay(self.owner,'p1')['digest'],before)

    def test_integrated_cli_runs_five_core_areas_without_model_or_provider(self):
        run=subprocess.run([sys.executable,'-S','-B','-m','apps.hub','core-demo'],cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout)
        self.assertTrue(result['replay_matches']);self.assertTrue(result['restore_matches'])
        self.assertTrue(result['processing_frontier']['complete'])
        self.assertEqual(result['reconciliation'],'attach_source')
        self.assertFalse(result['real_semantic_extraction'])

    def test_new_root_run_cannot_bypass_aggregate_workspace_budget(self):
        self.core.create_budget(self.owner,'p1','root_a',100000)
        self.core.create_budget(self.owner,'p2','root_b',100000)
        self.core.reserve(self.owner,'p1','root_a','call',100000)
        self.assert_code('workspace_budget_exceeded',lambda:self.core.reserve(self.owner,'p2','root_b','other',1))

    def test_legacy_authority_profile_is_not_silently_upgraded(self):
        from packages.storage.local_authority import LocalAuthorityStore
        legacy=Path(self.temp.name)/'legacy.sqlite'
        with LocalAuthorityStore(legacy,'workspace',bootstrap_owner='owner'):pass
        before=legacy.read_bytes()
        self.assert_code('unsupported_storage',lambda:Workspace(legacy,'workspace'))
        self.assertEqual(legacy.read_bytes(),before)

    def test_ended_edge_preserves_historical_sequence_and_replay(self):
        ops=[dict(op='create',id='a',body=self.body('A')),dict(op='create',id='b',body=self.body('B')),
             dict(op='link',origin='a',target='b',kind='depends_on')]
        first,_,_=self.apply(ops)
        a,b=first['temp_ids']['a'],first['temp_ids']['b']
        self.apply([dict(op='end_link',origin=a,target=b,kind='depends_on',base_version=1,state='ended')],key='end')
        self.assertEqual(self.core.graph(self.owner,'p1').prerequisites(a),[])
        historical=self.core.historical_edges(self.owner,'p1',first['event_sequences'][-1])
        self.assertEqual(historical[0]['state'],'asserted')
        self.assertEqual(self.core.db.execute('SELECT state,revision FROM edges').fetchone(),('ended',2))
        before=self.core.projection_digest(self.owner,'p1')
        self.assertEqual(self.core.replay(self.owner,'p1')['digest'],before)

    def test_invalidated_edge_is_not_deleted_and_stale_end_rejected(self):
        first,_,_=self.apply([dict(op='create',id='a',body=self.body('A')),dict(op='create',id='b',body=self.body('B')),
                             dict(op='link',origin='a',target='b',kind='required_by')])
        op=dict(op='end_link',origin=first['temp_ids']['a'],target=first['temp_ids']['b'],kind='required_by',base_version=1,state='invalidated')
        self.apply([op],key='invalidate')
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],1)
        self.assert_code('stale_edge',lambda:self.apply([op],key='stale_end'))


if __name__=='__main__':unittest.main()

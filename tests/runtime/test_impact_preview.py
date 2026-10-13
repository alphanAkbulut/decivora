"""Impact oracle and persisted snapshot boundaries; no model/API or canonical apply."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch
from packages.impact.graph import DependencyGraph
from packages.impact.preview import preview
from packages.domain.source_event import ContractError,validate_source_event
from packages.domain.project_binding import SessionKey
from packages.storage.workspace import Workspace

ROOT=Path(__file__).resolve().parents[2]

def fixture():
    source=json.loads((ROOT/'examples/impact-scenario.json').read_text())
    def convert(x):
        if type(x) is str:return dict(ref=x,revision=1)
        if type(x) is dict:return {k:[convert(v) for v in values] for k,values in x.items()}
        return None
    metadata={rid:dict(version=1,type='Decision' if rid.startswith('DEC') else 'Requirement',required_when=None,historically_completed=False,replacement=None) for rid in source['facts_after']}
    for row in source['records']:
        metadata[row['id']]=dict(version=1,type='Task',required_when=convert(row['required_when']),historically_completed=row.get('verification')=='passed',replacement='DEC_DB' if row['id']=='T2' else None)
    graph=DependencyGraph({r:{} for r in metadata},complete=True)
    before={r:dict(revision=1,valid=True) for r in source['facts_after']}
    after={r:dict(revision=1,valid=v) for r,v in source['facts_after'].items()}
    return graph,dict(record='DEC_MD',version=1,kind='decision_superseded'),metadata,before,after

class PureImpactTests(unittest.TestCase):
    def run_preview(self,**kwargs):return preview(*fixture(),**kwargs)
    def code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)
    def test_existing_six_case_oracle(self):
        result=self.run_preview();actual={r['record']:r for r in result['proposals']}
        self.assertEqual({r:actual[r]['action'] for r in ('T1','T2','T3','T4','T5','T6')},dict(T1='review',T2='update',T3='obsolete_candidate',T4='keep',T5='update',T6='review'))
        self.assertTrue(actual['T1']['preserve_historical_completion']);self.assertEqual(actual['T4']['counter_evidence'],['REQ_IMPORT'])
        self.assertEqual(result['canonical_mutations'],0)
    def test_truncation_preserves_frontier_and_downgrades_destructive_suggestions(self):
        result=self.run_preview(max_nodes=2)
        self.assertEqual(result['coverage'],'incomplete');self.assertTrue(result['frontier'])
        self.assertTrue(all(r['action']=='review' for r in result['proposals']))
    def test_edge_limit_and_incomplete_capture_do_not_hide_unknown(self):
        g,t,r,b,a=fixture();result=preview(g,t,r,b,a,max_edges=1)
        self.assertEqual(result['coverage'],'incomplete');self.assertTrue(result['frontier'])
        g.complete=False;result=preview(g,t,r,b,a)
        self.assertTrue(all(row['action']=='review' for row in result['proposals']))
    def test_dependency_only_path_does_not_propagate_obsolete(self):
        g,t,r,b,a=fixture();g.add('T6','T3','depends_on')
        result=preview(g,t,r,b,a);row=next(v for v in result['proposals'] if v['record']=='T6')
        self.assertEqual(row['action'],'review');self.assertIn('depends_on',[edge['kind'] for edge in row['reason_path']])
    def test_unknown_remaining_or_condition_prevents_obsolete(self):
        g,t,r,b,a=fixture();a.pop('REQ_IMPORT')
        row=next(v for v in preview(g,t,r,b,a)['proposals'] if v['record']=='T4')
        self.assertEqual(row['action'],'review');self.assertIsNone(row['after'])
    def test_stale_fact_and_trigger_rejected(self):
        g,t,r,b,a=fixture();a['DEC_MD']['revision']=2
        self.code('stale_fact',lambda:preview(g,t,r,b,a));a['DEC_MD']['revision']=1;t['version']=2
        self.code('stale_trigger',lambda:preview(g,t,r,b,a))
    def test_cycles_terminate_and_input_is_not_mutated(self):
        g,t,r,b,a=fixture();g.add('T3','T4','required_by');g.add('T4','T3','required_by')
        snapshot=deepcopy((r,b,a));result=preview(g,t,r,b,a)
        self.assertEqual(len(result['visited']),len(set(result['visited'])));self.assertEqual((r,b,a),snapshot)
    def test_negative_boolean_and_excessive_limits_rejected(self):
        self.code('impact_limit',lambda:self.run_preview(max_nodes=True))
        self.code('impact_limit',lambda:self.run_preview(max_edges=5001))
    def test_executable_impact_demo_checks_oracle_and_restore(self):
        run=subprocess.run([sys.executable,'-B','-m','apps.hub','impact-demo'],cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)
        result=json.loads(run.stdout)
        self.assertEqual(result['cases']['T3'],'obsolete_candidate')
        self.assertTrue(result['domain_unchanged']);self.assertTrue(result['restore_matches'])
        self.assertFalse(result['task_changes_applied'])

    def test_missing_record_metadata_is_rejected(self):
        g,t,r,b,a=fixture();r.pop('T6')
        self.code('invalid_snapshot',lambda:preview(g,t,r,b,a))

class PersistedImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'impact.sqlite';self.core=Workspace(self.path,'workspace',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=1);self.owner=a.issue_scope('owner')
        for p in ('p1','p2'):self.core.create_project(self.owner,p,p)
        plan=self.core.plan(self.owner,'p1','seed',[dict(op='create',id='decision',body=dict(type='Decision',title='Storage',description='Manual')),dict(op='create',id='task',body=dict(type='Task',title='Sync',description='Manual'))])
        result=self.core.apply(self.owner,plan,self.core.approve(self.owner,plan));self.ids=result['temp_ids'];d=self.ids['decision'];task=self.ids['task']
        self.trigger=dict(record=d,version=1,kind='decision_superseded')
        self.notes={task:dict(version=1,required_when=dict(any=[dict(ref=d,revision=1)]),historically_completed=False,replacement=None)}
        self.before={d:dict(revision=1,valid=True)};self.after={d:dict(revision=1,valid=False)}
    def code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)
    def run_preview(self,run_id='impact',**kwargs):
        return self.core.impact_preview(self.owner,'p1',run_id,self.trigger,self.notes,self.before,self.after,**kwargs)
    def test_preview_retry_restart_and_no_domain_mutation(self):
        before=self.core.projection_digest(self.owner,'p1');result=self.run_preview()
        self.assertEqual(result,self.run_preview());self.assertEqual(result['proposals'][0]['action'],'obsolete_candidate')
        self.assertEqual(before,self.core.projection_digest(self.owner,'p1'))
        with Workspace(self.path,'workspace') as other:
            stored=other.impact_run(other.authority.issue_scope('owner'),'p1','impact')
            self.assertFalse(stored['stale']);self.assertEqual(stored['result'],result)
        self.assertEqual(self.core.db.execute("SELECT count(*) FROM audit WHERE action='impact_preview'").fetchone()[0],1)
    def test_new_or_edge_invalidates_previous_impact_even_if_task_is_unchanged(self):
        self.run_preview();plan=self.core.plan(self.owner,'p1','edge',[dict(op='link',origin=self.ids['task'],target=self.ids['decision'],kind='required_by')]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        self.assertTrue(self.core.impact_run(self.owner,'p1','impact')['stale'])
        self.code('stale_impact',self.run_preview)
    def test_source_receipt_changes_coverage_without_knowledge_revision(self):
        result=self.run_preview();key=SessionKey('manual','account','session_fixture','epoch')
        event=validate_source_event(dict(json.loads((ROOT/'examples/runtime/source-event.json').read_text()),project_id='p1'))
        self.core.bind(self.owner,key,'p1',0);self.core.receive(self.owner,key,event,1)
        self.assertEqual(self.core.project(self.owner,'p1')['knowledge_revision'],result['knowledge_revision'])
        self.code('stale_impact',self.run_preview)
        self.assertEqual(self.run_preview('fresh')['coverage'],'incomplete')
    def test_missing_source_position_prevents_complete_impact(self):
        key=SessionKey('manual','account','session_fixture','epoch')
        event=validate_source_event(dict(json.loads((ROOT/'examples/runtime/source-event.json').read_text()),project_id='p1'))
        self.core.bind(self.owner,key,'p1',0);self.core.receive(self.owner,key,event,2)
        lease=self.core.lease(self.owner,'p1',now=0);self.core.finish(self.owner,lease,{},now=1)
        self.assertEqual(self.run_preview()['coverage'],'incomplete')

    def test_quarantine_is_incomplete_coverage_not_empty_success(self):
        key=SessionKey('manual','account','session_fixture','epoch')
        event=validate_source_event(dict(json.loads((ROOT/'examples/runtime/source-event.json').read_text()),project_id='p1'))
        self.core.receive(self.owner,key,event,1)
        self.assertEqual(self.run_preview()['coverage'],'incomplete')
        self.assertEqual(self.run_preview()['proposals'][0]['action'],'review')
    def test_foreign_annotation_and_changed_run_input_rejected(self):
        self.run_preview();self.after[self.ids['decision']]['valid']=True
        self.code('idempotency_conflict',self.run_preview)
        self.notes['foreign']=dict(version=1,required_when=None,historically_completed=False,replacement=None)
        self.code('invalid_snapshot',lambda:self.run_preview('other'))
    def test_archive_and_authority_change_invalidate_run(self):
        self.run_preview();self.core.update_project(self.owner,'p1',base_revision=1,name='p1',archived=True)
        self.code('project_archived',self.run_preview)
        self.assertTrue(self.core.impact_run(self.owner,'p1','impact')['stale'])
    def test_read_permission_revocation_and_foreign_project_do_not_leak_run(self):
        self.run_preview();self.code('impact_unavailable',lambda:self.core.impact_run(self.owner,'p2','impact'))
        a=self.core.authority;a.replace_grant(self.owner,'owner',kind='human',readable=frozenset({'p2'}),writable=frozenset({'p2'}),active=True,base_revision=a.revision());self.owner=a.issue_scope('owner')
        self.code('forbidden',lambda:self.core.impact_run(self.owner,'p1','impact'))
    def test_audit_insert_failure_does_not_store_half_run(self):
        self.core.db.execute("CREATE TRIGGER fail_impact BEFORE INSERT ON audit WHEN NEW.action='impact_preview' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        self.code('storage_failure',self.run_preview)
        self.assertIsNone(self.core._impact_run('p1','impact'))
    def test_preview_survives_backup_restore_and_replay(self):
        result=self.run_preview();backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restore.sqlite',manifest) as restored:
            self.assertEqual(restored.impact_run(restored.authority.issue_scope('owner'),'p1','impact')['result'],result)
    def test_stale_record_annotation_and_boolean_version_rejected(self):
        self.notes[self.ids['task']]['version']=2
        self.code('stale_record',self.run_preview)
        self.notes[self.ids['task']]['version']=True
        self.code('invalid_snapshot',self.run_preview)

if __name__=='__main__':unittest.main()

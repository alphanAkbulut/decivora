"""Review approval and atomic application boundaries on real SQLite synthetic data."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
import subprocess
import sys
import unittest
from unittest.mock import patch
from packages.domain.review import ReviewService
from packages.storage.workspace import Workspace
from packages.domain.project_binding import SessionKey
from packages.domain.source_event import ContractError,validate_source_event

ROOT=Path(__file__).resolve().parents[2]
class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'core.sqlite';self.core=Workspace(self.path,'workspace',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=1);self.owner=a.issue_scope('owner')
        for p in ('p1','p2'):self.core.create_project(self.owner,p,p)
        self.body=dict(type='Task',title='Sync',description='Before')
        plan=self.core.plan(self.owner,'p1','seed',[dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='Old')),dict(op='create',id='t',body=self.body)])
        ids=self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))['temp_ids'];self.d=ids['d'];self.t=ids['t']
        self.core.impact_preview(self.owner,'p1','impact',dict(record=self.d,version=1,kind='decision_superseded'),{self.t:dict(version=1,required_when=dict(any=[dict(ref=self.d,revision=1)]),historically_completed=False,replacement=None)},{self.d:dict(revision=1,valid=True)},{self.d:dict(revision=1,valid=False)})
        self.service=ReviewService(self.core)
        self.groups=[dict(id='create',depends_on=[],records=[self.t],operations=[dict(op='create',id='new',body=dict(self.body,title='Replacement'))]),dict(id='link',depends_on=['create'],records=[self.t],operations=[dict(op='link',origin=self.t,target='new',kind='related_to')]),dict(id='update',depends_on=[],records=[self.t],operations=[dict(op='update',id=self.t,base_version=1,body=dict(self.body,description='After'))])]
        self.service.create(self.owner,'p1','review','impact',self.groups)
    def code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)
    def select(self,groups=None):return self.service.select(self.owner,'p1','review','selection',groups or ['update'])
    def test_compare_selection_and_approval_are_not_application(self):
        before=self.core.projection_digest(self.owner,'p1')
        self.assertEqual(self.service.compare(self.owner,'p1','review')['canonical_mutations'],0)
        self.select();self.service.approve(self.owner,'p1','selection')
        self.assertEqual(before,self.core.projection_digest(self.owner,'p1'))
    def test_partial_selection_applies_only_selected_group_and_is_idempotent(self):
        selected=self.select();token=self.service.approve(self.owner,'p1','selection')
        self.assertEqual(token,self.service.approve(self.owner,'p1','selection'))
        result=self.service.apply(self.owner,'p1','selection',token)
        self.assertEqual(result,self.service.apply(self.owner,'p1','selection',token))
        self.assertEqual(len(self.core.records(self.owner,'p1')['records']),2)
        self.assertEqual(len(result['event_sequences']),1)
        self.assertEqual(selected['groups'],['update'])
    def test_missing_declared_and_implicit_dependency_is_rejected(self):
        self.code('dependent_selection',lambda:self.select(['link']))
        groups=deepcopy(self.groups);groups[1]['depends_on']=[]
        self.service.create(self.owner,'p1','implicit','impact',groups)
        self.code('dependent_selection',lambda:self.service.select(self.owner,'p1','implicit','x',['link']))
    def test_create_and_link_group_apply_together(self):
        self.select(['create','link']);token=self.service.approve(self.owner,'p1','selection')
        result=self.service.apply(self.owner,'p1','selection',token)
        self.assertEqual(len(result['event_sequences']),2);self.assertEqual(len(self.core.records(self.owner,'p1')['records']),3)
    def test_generic_apply_cannot_bypass_review_source_guard(self):
        selected=self.select();token=self.service.approve(self.owner,'p1','selection')
        self.code('review_approval_required',lambda:self.core.apply(self.owner,selected['plan'],token))
    def test_source_receipt_after_approval_invalidates_apply(self):
        self.select();token=self.service.approve(self.owner,'p1','selection')
        key=SessionKey('manual','account','session_fixture','epoch');self.core.bind(self.owner,key,'p1',0)
        event=validate_source_event(dict(json.loads((ROOT/'examples/runtime/source-event.json').read_text()),project_id='p1'))
        self.core.receive(self.owner,key,event,1)
        self.code('stale_impact',lambda:self.service.apply(self.owner,'p1','selection',token))
        self.assertEqual(self.core.records(self.owner,'p1')['records'][0]['version'],1)
    def test_new_graph_edge_after_approval_invalidates_apply(self):
        self.select();token=self.service.approve(self.owner,'p1','selection')
        plan=self.core.plan(self.owner,'p1','edge',[dict(op='link',origin=self.t,target=self.d,kind='required_by')]);self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
        self.code('stale_impact',lambda:self.service.apply(self.owner,'p1','selection',token))
    def test_policy_change_invalidates_approval(self):
        self.select();token=self.service.approve(self.owner,'p1','selection')
        with patch('packages.domain.review.POLICY','future-policy'):
            self.code('stale_policy',lambda:self.service.apply(self.owner,'p1','selection',token))
    def test_reject_preserves_record_and_prevents_accept(self):
        before=self.core.projection_digest(self.owner,'p1')
        event=self.service.decide(self.owner,'p1','review','reject','reject')
        self.assertEqual(event,self.service.decide(self.owner,'p1','review','reject','reject'))
        self.code('review_rejected',self.select)
        self.assertEqual(before,self.core.projection_digest(self.owner,'p1'))
    def test_defer_invalidates_old_selection_and_explicit_new_selection_can_resume(self):
        self.select();token=self.service.approve(self.owner,'p1','selection')
        self.service.decide(self.owner,'p1','review','defer','defer')
        self.code('stale_review',lambda:self.service.apply(self.owner,'p1','selection',token))
        self.service.select(self.owner,'p1','review','new_selection',['update'])
        new=self.service.approve(self.owner,'p1','new_selection');self.service.apply(self.owner,'p1','new_selection',new)
    def test_agent_cannot_select_approve_apply_or_reject(self):
        self.select();token=self.service.approve(self.owner,'p1','selection')
        a=self.core.authority;a.replace_grant(self.owner,'agent',kind='agent',readable=frozenset({'p1'}),writable=frozenset({'p1'}),active=True,base_revision=a.revision());agent=a.issue_scope('agent')
        self.assertIn('packet',self.service.compare(agent,'p1','review'))
        for fn in (lambda:self.service.select(agent,'p1','review','x',['update']),lambda:self.service.approve(agent,'p1','selection'),lambda:self.service.apply(agent,'p1','selection',token),lambda:self.service.decide(agent,'p1','review','x','reject')):self.code('human_approval_required',fn)
    def test_audit_failure_rolls_back_entire_domain_application(self):
        self.select();token=self.service.approve(self.owner,'p1','selection');before=self.core.projection_digest(self.owner,'p1')
        self.core.db.execute("CREATE TRIGGER fail_review BEFORE INSERT ON audit WHEN NEW.action='review_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        self.code('storage_failure',lambda:self.service.apply(self.owner,'p1','selection',token))
        self.assertEqual(before,self.core.projection_digest(self.owner,'p1'))
        self.assertIsNone(self.service._load('p1','review_applied','selection'))
    def test_restart_backup_restore_and_history_preserve_selected_review(self):
        self.select();token=self.service.approve(self.owner,'p1','selection')
        with Workspace(self.path,'workspace') as opened:
            ReviewService(opened).apply(opened.authority.issue_scope('owner'),'p1','selection',token)
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restore.sqlite',manifest) as restored:
            service=ReviewService(restored);owner=restored.authority.issue_scope('owner')
            self.assertEqual(service.apply(owner,'p1','selection',token)['status'],'applied')
    def test_cycles_changed_identity_and_cross_project_queries_rejected(self):
        groups=deepcopy(self.groups);groups[0]['depends_on']=['link']
        self.code('review_cycle',lambda:self.service.create(self.owner,'p1','cycle','impact',groups))
        self.code('idempotency_conflict',lambda:self.service.create(self.owner,'p1','review','impact',groups))
        self.code('review_unavailable',lambda:self.service.compare(self.owner,'p2','review'))
    def test_reject_after_application_requires_new_compensating_change(self):
        self.select();token=self.service.approve(self.owner,'p1','selection');self.service.apply(self.owner,'p1','selection',token)
        self.code('review_applied',lambda:self.service.decide(self.owner,'p1','review','late','reject'))

    def test_unknown_operation_is_rejected_before_review_is_persisted(self):
        groups=deepcopy(self.groups);groups[0]['operations']=[dict(op='shell',command='untrusted')]
        self.code('invalid_operation',lambda:self.service.create(self.owner,'p1','bad','impact',groups))
        self.assertIsNone(self.service._load('p1','review_created','bad'))

    def test_executable_demo_separates_approval_and_application(self):
        result=subprocess.run([sys.executable,'-B','-m','apps.hub','review-demo'],cwd=ROOT,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        output=json.loads(result.stdout)
        self.assertTrue(output['unchanged_until_separate_apply']);self.assertTrue(output['retry_same_result'])
        self.assertFalse(output['task_completion_verified'])

    def test_two_simultaneous_connections_produce_one_application(self):
        self.select();token=self.service.approve(self.owner,'p1','selection');barrier=threading.Barrier(2)
        def worker():
            with Workspace(self.path,'workspace') as core:
                owner=core.authority.issue_scope('owner');barrier.wait(timeout=5)
                return ReviewService(core).apply(owner,'p1','selection',token)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(worker) for _ in range(2)];results=[f.result(timeout=10) for f in futures]
        self.assertEqual(results[0],results[1]);self.assertEqual(self.core.db.execute('SELECT count(*) FROM events').fetchone()[0],3)

if __name__=='__main__':unittest.main()

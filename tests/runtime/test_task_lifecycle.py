"""Cancellation is an approved versioned event, never edge deletion or completion."""
from pathlib import Path
import json
import tempfile
import subprocess
import sys
import unittest
from packages.domain.review import ReviewService
from packages.storage.workspace import Workspace
from packages.domain.source_event import ContractError

class TaskLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'core.sqlite';self.core=Workspace(self.path,'workspace',owner='owner');self.addCleanup(self.core.close)
        a=self.core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p1','p2'}),writable=frozenset({'p1','p2'}),active=True,base_revision=1);self.owner=a.issue_scope('owner')
        for p in ('p1','p2'):self.core.create_project(self.owner,p,p)
        body=dict(type='Task',title='Sync',description='History')
        self.ids=self.apply([dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='Manual')),dict(op='create',id='t',body=body),dict(op='create',id='other',body=dict(body,title='Other')),dict(op='create',id='req',body=dict(type='Requirement',title='Keep',description='Still required'))],'seed')['temp_ids']
        self.d=self.ids['d'];self.t=self.ids['t'];self.other=self.ids['other'];self.req=self.ids['req'];self.service=ReviewService(self.core)
    def code(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)
    def apply(self,ops,key):
        plan=self.core.plan(self.owner,'p1',key,ops);return self.core.apply(self.owner,plan,self.core.approve(self.owner,plan))
    def version(self,task):return next(r['version'] for r in self.core.records(self.owner,'p1')['records'] if r['id']==task)
    def prepare(self,run='impact',state='cancelled',tasks=None,extra=False,valid_after=None,completed=False,additional_ops=None):
        tasks=tasks or [self.t]
        refs=[dict(ref=self.d,revision=1)]
        if extra:refs.append(dict(ref=self.req,revision=1))
        annotations={task:dict(version=self.version(task),required_when=dict(any=refs),historically_completed=completed,replacement=None) for task in tasks}
        before={self.d:dict(revision=1,valid=state=='cancelled')};after={self.d:dict(revision=1,valid=(state=='todo' if valid_after is None else valid_after))}
        if extra:
            before[self.req]=dict(revision=1,valid=True);after[self.req]=dict(revision=1,valid=True)
        self.core.impact_preview(self.owner,'p1',run,dict(record=self.d,version=1,kind='decision_superseded'),annotations,before,after)
        groups=[dict(id='lifecycle',depends_on=[],records=tasks,operations=[dict(op='task_lifecycle',id=task,base_version=self.version(task),state=state,reason='Explicit manual approved rationale',impact_run=run) for task in tasks]+(additional_ops or []))]
        self.service.create(self.owner,'p1',run+'_review',run,groups)
        selected=self.service.select(self.owner,'p1',run+'_review',run+'_selection',['lifecycle']);token=self.service.approve(self.owner,'p1',run+'_selection')
        return selected,token
    def cancel(self,**kwargs):
        selected,token=self.prepare(**kwargs);return self.service.apply(self.owner,'p1',selected['id'],token)
    def test_cancel_preserves_task_edges_and_history_without_done(self):
        self.apply([dict(op='link',origin=self.t,target=self.d,kind='required_by')],'edge')
        self.cancel();history=self.core.task_history(self.owner,'p1',self.t)
        self.assertEqual(history['execution'],'cancelled');self.assertEqual(history['events'][0]['state'],'cancelled')
        self.assertEqual(self.core.db.execute('SELECT state FROM edges').fetchone()[0],'asserted')
        self.assertEqual(len(self.core.records(self.owner,'p1')['records']),4)
        self.assertFalse(self.core.graph(self.owner,'p1').assessment(self.t)['ready'])
        self.assertNotIn(self.t,[r['task'] for r in self.core.graph(self.owner,'p1').rank()])
    def test_edge_ending_does_not_cancel_task(self):
        self.apply([dict(op='link',origin=self.t,target=self.d,kind='required_by')],'edge')
        old,old_token=self.prepare()
        group=dict(id='end_edge',depends_on=[],records=[self.t],operations=[dict(op='end_link',origin=self.t,target=self.d,kind='required_by',base_version=1,state='ended')])
        self.service.create(self.owner,'p1','end_review','impact',[group]);self.service.select(self.owner,'p1','end_review','end_selection',['end_edge'])
        token=self.service.approve(self.owner,'p1','end_selection');self.service.apply(self.owner,'p1','end_selection',token)
        self.code('stale_impact',lambda:self.service.apply(self.owner,'p1',old['id'],old_token))
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'todo')
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['events'],[])
    def test_compensating_reopen_appends_history_instead_of_erasing_cancellation(self):
        self.cancel();selected,token=self.prepare(run='reopen',state='todo');self.service.apply(self.owner,'p1',selected['id'],token)
        history=self.core.task_history(self.owner,'p1',self.t)
        self.assertEqual(history['execution'],'todo');self.assertEqual([r['state'] for r in history['events']],['cancelled','todo']);self.assertEqual(self.version(self.t),3)
    def test_unrelated_metadata_update_cannot_reopen_cancelled_task(self):
        self.cancel();self.apply([dict(op='update',id=self.t,base_version=2,body=dict(type='Task',title='Changed',description='Metadata only'))],'metadata')
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'cancelled')
        self.code('invalid_lifecycle',lambda:self.apply([dict(op='update',id=self.t,base_version=3,body=dict(type='Decision',title='Bypass',description='No'))],'convert'))
    def test_generic_human_approval_is_not_lifecycle_approval(self):
        op=dict(op='task_lifecycle',id=self.t,base_version=1,state='cancelled',reason='Not bound',impact_run='none')
        self.code('review_approval_required',lambda:self.apply([op],'bare'))
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'todo')
    def test_live_or_justification_prevents_cancellation(self):
        selected,token=self.prepare(extra=True)
        self.code('lifecycle_review',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
    def test_active_requirement_outside_recorded_expression_prevents_cancellation(self):
        self.apply([dict(op='link',origin=self.t,target=self.req,kind='required_by')],'requirement')
        selected,token=self.prepare()
        self.code('lifecycle_blocker',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
    def test_downstream_dependency_prevents_silent_cancellation(self):
        self.apply([dict(op='link',origin=self.other,target=self.t,kind='depends_on')],'dependent')
        selected,token=self.prepare()
        self.code('lifecycle_blocker',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(self.core.task_history(self.owner,'p1',self.other)['execution'],'todo')
    def test_explicitly_approved_batch_can_cancel_both_independently_obsolete_tasks(self):
        self.apply([dict(op='link',origin=self.other,target=self.t,kind='depends_on')],'dependent')
        self.cancel(tasks=[self.t,self.other])
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'cancelled')
        self.assertEqual(self.core.task_history(self.owner,'p1',self.other)['execution'],'cancelled')
    def test_parent_relationship_prevents_silent_child_cancellation(self):
        self.apply([dict(op='link',origin=self.t,target=self.other,kind='part_of')],'parent')
        selected,token=self.prepare()
        self.code('lifecycle_blocker',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
    def test_replay_restart_backup_restore_and_idempotency_preserve_state(self):
        selected,token=self.prepare();result=self.service.apply(self.owner,'p1',selected['id'],token)
        self.assertEqual(result,self.service.apply(self.owner,'p1',selected['id'],token))
        before=self.core.projection_digest(self.owner,'p1');self.assertEqual(self.core.replay(self.owner,'p1')['digest'],before)
        with Workspace(self.path,'workspace') as opened:self.assertEqual(opened.task_history(opened.authority.issue_scope('owner'),'p1',self.t)['execution'],'cancelled')
        backup=Path(self.temp.name)/'backup.sqlite';manifest=self.core.backup(self.owner,backup)
        with Workspace.restore(backup,Path(self.temp.name)/'restore.sqlite',manifest) as restored:self.assertEqual(restored.task_history(restored.authority.issue_scope('owner'),'p1',self.t)['execution'],'cancelled')
    def test_audit_failure_rolls_back_lifecycle_and_version(self):
        selected,token=self.prepare();before=self.core.projection_digest(self.owner,'p1')
        self.core.db.execute("CREATE TRIGGER fail_lifecycle BEFORE INSERT ON audit WHEN NEW.action='review_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        self.code('storage_failure',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(before,self.core.projection_digest(self.owner,'p1'));self.assertEqual(self.version(self.t),1)
    def test_history_query_is_scoped_and_non_task_is_rejected(self):
        self.code('task_unavailable',lambda:self.core.task_history(self.owner,'p2',self.t))
        self.code('task_unavailable',lambda:self.core.task_history(self.owner,'p1',self.d))
    def test_repeated_same_state_does_not_masquerade_as_compensation(self):
        self.cancel();selected,token=self.prepare(run='bad_reopen',state='cancelled')
        # A same-state operation cannot masquerade as a compensating event.
        self.code('invalid_lifecycle',lambda:self.service.apply(self.owner,'p1',selected['id'],token))

    def test_reopening_with_false_new_rationale_is_rejected(self):
        self.cancel();selected,token=self.prepare(run='invalid_reopen',state='todo',valid_after=False)
        self.code('lifecycle_review',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'cancelled')

    def test_historical_completion_is_not_rewritten_as_cancellation(self):
        selected,token=self.prepare(completed=True)
        self.code('invalid_lifecycle',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['events'],[])

    def test_executable_cancel_and_compensating_demo(self):
        root=Path(__file__).resolve().parents[2]
        run=subprocess.run([sys.executable,'-B','-m','apps.hub','lifecycle-demo'],cwd=root,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr);result=json.loads(run.stdout)
        self.assertEqual(result['history_states'],['cancelled','todo']);self.assertTrue(result['relationship_preserved'])
        self.assertFalse(result['task_completion_verified'])

    def test_same_changeset_new_requirement_link_cannot_bypass_cancellation_guard(self):
        selected,token=self.prepare(additional_ops=[dict(op='link',origin=self.t,target=self.req,kind='required_by')])
        self.code('lifecycle_blocker',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'todo')
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],0)

    def test_same_changeset_new_downstream_link_cannot_bypass_cancellation_guard(self):
        selected,token=self.prepare(additional_ops=[dict(op='link',origin=self.other,target=self.t,kind='depends_on')])
        self.code('lifecycle_blocker',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(self.core.db.execute('SELECT count(*) FROM edges').fetchone()[0],0)

    def test_same_changeset_changed_rationale_revision_requires_fresh_impact(self):
        selected,token=self.prepare(additional_ops=[dict(op='update',id=self.d,base_version=1,body=dict(type='Decision',title='Changed basis',description='New revision'))])
        self.code('lifecycle_review',lambda:self.service.apply(self.owner,'p1',selected['id'],token))
        self.assertEqual(self.version(self.d),1);self.assertEqual(self.core.task_history(self.owner,'p1',self.t)['execution'],'todo')

if __name__=='__main__':unittest.main()

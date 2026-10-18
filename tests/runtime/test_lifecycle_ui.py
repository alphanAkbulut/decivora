"""Human-confirmed single-decision rationale -> separate lifecycle review commands."""
import tempfile,unittest
from pathlib import Path
from apps.local_ui.server import LocalApp
from packages.domain.source_event import ContractError

class LifecycleUICommandsTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.app=LocalApp(Path(temp.name)/'workspace.sqlite')
        self.ids=self.seed([dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='Synthetic decision')),dict(op='create',id='t',body=dict(type='Task',title='Sync',description='Synthetic task')),dict(op='create',id='other',body=dict(type='Task',title='Other',description='Independent')),dict(op='link',origin='t',target='d',kind='required_by')],'seed')['temp_ids']
    def seed(self,ops,key):
        with self.app.core() as core:
            scope=core.authority.issue_scope('local_owner');p=core.plan(scope,'personal',key,ops);return core.apply(scope,p,core.approve(scope,p))
    def task(self):return next(t for t in self.app.state()['tasks'] if t['id']==self.ids['t'])
    def preview(self,key='impact',active=False,confirmed=True):
        return self.app.command(dict(action='preview_decision_change',decision=self.ids['d'],decision_version=1,base_revision=self.app.state()['snapshot'],key=key,decision_active=active,rationale_tasks=[dict(task=self.ids['t'],task_version=self.task()['version'])] if confirmed else []))
    def prepare(self,run='impact',key='review',state='cancelled'):
        return self.app.command(dict(action='prepare_task_lifecycle',key=key,impact_run=run,tasks=[dict(task=self.ids['t'],task_version=self.task()['version'])],state=state,reason='Human reviewed this decision as the sole task justification'))
    def select_approve(self,key='review'):
        self.app.command(dict(action='select_impact_changes',key=key,selection_id=key+'_selection',selected=['lifecycle']))
        return self.app.command(dict(action='approve_impact_changes',selection_id=key+'_selection'))['approval']
    def apply(self,token,key='review'):return self.app.command(dict(action='apply_impact_changes',selection_id=key+'_selection',approval=token))
    def test_cancel_and_reopen_are_separate_approved_history_preserving_events(self):
        result=self.preview();self.assertEqual(next(p for p in result['proposals'] if p['record']==self.ids['t'])['action'],'obsolete_candidate')
        self.prepare();token=self.select_approve();self.assertEqual(self.task()['lane'],'To Do');receipt=self.apply(token);self.assertEqual(receipt,self.apply(token));self.assertEqual(self.task()['lane'],'Cancelled')
        self.preview(key='restore',active=True);self.prepare(run='restore',key='reopen',state='todo');self.apply(self.select_approve('reopen'),'reopen')
        task=self.task()
        self.assertEqual(task['lane'],'To Do');self.assertEqual([e['state'] for e in task['lifecycle']['events']],['cancelled','todo']);self.assertEqual(task['version'],3)
        self.assertTrue(any(e['kind']=='required_by' and e['state']=='asserted' for e in self.app.state()['relations']))
        self.assertEqual(LocalApp(self.app.path).state()['tasks'],self.app.state()['tasks'])
    def test_missing_rationale_is_not_obsolete_or_reopen_authority(self):
        self.preview(confirmed=False)
        with self.assertRaises(ContractError):self.prepare()
        self.assertEqual(self.task()['lane'],'To Do')
    def test_confirming_unlinked_or_stale_or_duplicate_task_is_rejected(self):
        base=dict(action='preview_decision_change',decision=self.ids['d'],decision_version=1,base_revision=self.app.state()['snapshot'],key='bad',decision_active=False)
        for tasks in [[dict(task=self.ids['other'],task_version=1)],[dict(task=self.ids['t'],task_version=2)],[dict(task=self.ids['t'],task_version=1)]*2]:
            with self.subTest(tasks=tasks),self.assertRaises(ContractError):self.app.command(dict(base,rationale_tasks=tasks))
    def test_unreviewed_or_stale_approval_cannot_apply(self):
        self.preview();self.prepare()
        with self.assertRaises(ContractError):self.apply('invented')
        token=self.select_approve();self.app.command(dict(action='import_conversation',text='A new requirement arrived after the approval.'))
        with self.assertRaises(ContractError):self.apply(token)
        self.assertEqual(self.task()['lane'],'To Do')
    def test_other_requirement_and_downstream_guards_are_not_bypassed(self):
        self.seed([dict(op='link',origin=self.ids['other'],target=self.ids['t'],kind='depends_on')],'dependency');self.preview();self.prepare();token=self.select_approve()
        with self.assertRaises(ContractError) as error:self.apply(token)
        self.assertEqual(error.exception.code,'lifecycle_blocker');self.assertEqual(self.task()['version'],1)
    def test_extra_active_requirement_blocks_cancellation(self):
        self.seed([dict(op='create',id='req',body=dict(type='Requirement',title='Keep sync',description='Still needed')),dict(op='link',origin=self.ids['t'],target='req',kind='required_by')],'requirement');self.preview();self.prepare();token=self.select_approve()
        with self.assertRaises(ContractError):self.apply(token)
        self.assertEqual(self.task()['lane'],'To Do')
    def test_explicit_rationale_link_requires_recorded_decision_and_current_snapshot(self):
        request=dict(action='link_task_rationale',task=self.ids['other'],target=self.ids['d'],base_revision=self.app.state()['snapshot'],key='rationale')
        receipt=self.app.command(request);self.assertEqual(receipt,self.app.command(request))
        self.assertTrue(any(e['origin']==self.ids['other'] and e['target']==self.ids['d'] and e['kind']=='required_by' for e in self.app.state()['relations']))
        with self.assertRaises(ContractError):self.app.command(dict(request,key='bad',target=self.ids['t'],base_revision=self.app.state()['snapshot']))
        with self.assertRaises(ContractError):self.app.command(dict(request,key='stale'))
    def test_unsupported_resolution_and_typed_revision_rejected(self):
        self.preview()
        with self.assertRaises(ContractError):self.prepare(state='duplicate')
        with self.assertRaises(ContractError):self.app.command(dict(action='preview_decision_change',decision=self.ids['d'],decision_version=1,base_revision=self.app.state()['snapshot'],key='bool',decision_active='false',rationale_tasks=[]))

"""Impact-to-review/apply application commands on isolated persistent storage."""
import tempfile,unittest
from pathlib import Path
from apps.local_ui.server import LocalApp
from packages.domain.source_event import ContractError
class ImpactChangeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.app=LocalApp(Path(self.temp.name)/'workspace.sqlite')
        with self.app.core() as core:
            scope=core.authority.issue_scope('local_owner');p=core.plan(scope,'personal','seed',[dict(op='create',id='d',body=dict(type='Decision',title='Storage',description='SQLite')),dict(op='create',id='t',body=dict(type='Task',title='Storage task',description='Old task scope')),dict(op='link',origin='t',target='d',kind='required_by')]);self.ids=core.apply(scope,p,core.approve(scope,p))['temp_ids'];self.revision=core.project(scope,'personal')['knowledge_revision']
        self.app.command(dict(action='preview_decision_change',decision=self.ids['d'],decision_version=1,base_revision=self.revision,key='impact'))
    def prepare(self,**changes):
        request=dict(action='prepare_impact_updates',key='review',impact_run='impact',updates=[dict(task=self.ids['t'],task_version=1,description='Revised task scope after human review')]);request.update(changes);return self.app.command(request)
    def select(self):return self.app.command(dict(action='select_impact_changes',key='review',selection_id='selection',selected=['edit_1']))
    def approve(self):return self.app.command(dict(action='approve_impact_changes',selection_id='selection'))['approval']
    def apply(self,token):return self.app.command(dict(action='apply_impact_changes',selection_id='selection',approval=token))
    def record(self):return next(t for t in self.app.state()['tasks'] if t['id']==self.ids['t'])
    def test_separate_prepare_select_approve_apply_and_retry(self):
        self.prepare();self.assertEqual(self.record()['body']['description'],'Old task scope');self.select();token=self.approve();self.assertEqual(self.record()['version'],1)
        self.assertEqual(self.app.state()['impact_change_reviews'][0]['state'],'Approved')
        result=self.apply(token);self.assertEqual(self.apply(token),result);self.assertEqual(self.record()['version'],2);self.assertEqual(self.record()['body']['description'],'Revised task scope after human review');self.assertEqual(self.app.state()['impact_change_reviews'][0]['state'],'Applied')
        restarted=LocalApp(self.app.path);self.assertEqual(restarted.state()['impact_change_reviews'][0]['state'],'Applied');self.assertEqual(restarted.state()['impact_change_reviews'][0]['original_scopes'][self.ids['t']],'Old task scope')
    def test_no_approval_no_change(self):
        self.prepare();self.select()
        with self.assertRaises(ContractError):self.apply('invented')
        self.assertEqual(self.record()['version'],1)
    def test_project_change_stales_approved_review(self):
        self.prepare();self.select();token=self.approve();self.app.command(dict(action='create_task',title='New scope input',description='Changes the project snapshot'))
        self.assertEqual(self.app.state()['impact_change_reviews'][0]['state'],'Stale')
        with self.assertRaises(ContractError):self.apply(token)
        self.assertEqual(self.record()['version'],1)
    def test_reject_and_defer_do_not_change_task(self):
        self.prepare();self.select();token=self.approve();self.app.command(dict(action='decide_impact_changes',key='review',action_id='defer',decision='defer'))
        self.assertEqual(self.app.state()['impact_change_reviews'][0]['state'],'Deferred')
        with self.assertRaises(ContractError):self.apply(token)
        self.app.command(dict(action='decide_impact_changes',key='review',action_id='reject',decision='reject'));self.assertEqual(self.app.state()['impact_change_reviews'][0]['state'],'Rejected');self.assertEqual(self.record()['version'],1)
    def test_unaffected_duplicate_unchanged_and_forged_lifecycle_edits_rejected(self):
        for update in [dict(task=self.ids['d'],task_version=1,description='Not a task'),dict(task=self.ids['t'],task_version=1,description='Old task scope'),dict(task=self.ids['t'],task_version=2,description='Stale'),dict(task=self.ids['t'],task_version=1,description='Forged',state='cancelled')]:
            with self.subTest(update=update),self.assertRaises(ContractError):self.prepare(updates=[update])
        self.assertEqual(self.record()['version'],1)
    def test_apply_receipt_failure_rolls_back_task(self):
        self.prepare();self.select();token=self.approve()
        with self.app.core() as core:core.db.execute("CREATE TRIGGER stop_review BEFORE INSERT ON audit WHEN NEW.action='review_applied' BEGIN SELECT RAISE(ABORT,'fixture'); END")
        with self.assertRaises(ContractError):self.apply(token)
        self.assertEqual(self.record()['version'],1)

    def test_new_manual_conversation_invalidates_previously_approved_impact(self):
        self.prepare();self.select();token=self.approve()
        self.app.command(dict(action='import_conversation',text='New source changes the pending storage discussion.'))
        self.assertEqual(self.app.state()['impact_change_reviews'][0]['state'],'Stale')
        with self.assertRaises(ContractError):self.apply(token)
        self.assertEqual(self.record()['version'],1)

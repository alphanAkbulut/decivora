import tempfile,unittest
from pathlib import Path
from apps.local_ui.server import LocalApp
from packages.domain.source_event import ContractError

class TaskBlockerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.app=LocalApp(Path(self.temp.name)/'blockers.sqlite')
        self.app.command(dict(action='create_task',title='Task',description='Scope'))
        self.task=self.app.state()['tasks'][0]
    def command(self,**overrides):
        value=dict(action='task_blocker',task=self.task['id'],task_version=self.task['version'],base_revision=0,blocked=True,reason='Access unavailable',next_action='Owner grants read access')
        return self.app.command(dict(value,**overrides))
    def test_block_and_resolve_preserve_lane_and_append_history_after_restart(self):
        self.command();task=LocalApp(self.app.path).state()['tasks'][0]
        self.assertTrue(task['blocker']['blocked']);self.assertEqual(task['lane'],'To Do');self.assertEqual(task['body'],self.task['body'])
        self.command(base_revision=1,blocked=False,reason='Access grant verified',next_action='Resume work')
        current=self.app.state()['tasks'][0]['blocker']
        self.assertFalse(current['blocked']);self.assertEqual(len(current['history']),2);self.assertTrue(current['history'][0]['blocked'])
    def test_stale_or_invalid_input_does_not_overwrite_history(self):
        for override in (dict(reason=''),dict(blocked='true'),dict(task_version=True),dict(next_action='')):
            with self.assertRaises(ContractError):self.command(**override)
        self.command()
        with self.assertRaises(ContractError):self.command(blocked=False)
        self.assertEqual(self.app.state()['tasks'][0]['blocker']['revision'],1)
    def test_blocked_task_cannot_start_and_resolution_does_not_auto_start(self):
        row=lambda rid:dict(id=rid,statement='Review scope',method='human_review',required=True,applicable=True,applicability_reason='')
        self.app.command(dict(action='acceptance',task=self.task['id'],task_version=self.task['version'],base_contract=0,criteria=[row('AC1')],dod=[row('DOD1')],reason='Owner acceptance',acknowledged_changes=[]))
        self.command()
        with self.assertRaises(ContractError) as err:self.app.command(dict(action='start',task=self.task['id']))
        self.assertEqual(err.exception.code,'task_blocked')
        self.command(base_revision=1,blocked=False,reason='Resolved',next_action='Start explicitly')
        self.assertEqual(self.app.state()['tasks'][0]['lane'],'To Do')
        self.app.command(dict(action='start',task=self.task['id']))
        self.command(base_revision=2,reason='New runtime impediment',next_action='Review environment')
        self.assertEqual(self.app.state()['tasks'][0]['lane'],'In Progress')
    def test_unknown_task_and_extra_fields_are_rejected(self):
        with self.assertRaises(ContractError):self.command(task='missing')
        with self.assertRaises(ContractError):self.command(project='other')
        self.assertEqual(self.app.state()['tasks'][0]['blocker']['revision'],0)

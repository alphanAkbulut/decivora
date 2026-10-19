import math,unittest
from unittest.mock import patch
import test_task_blockers as fixture
from packages.domain.blocker_age import assess,THRESHOLD_SECONDS as WEEK
from packages.capture.dialogue_review import DialogueReviewService

class BlockerAgeTests(unittest.TestCase):
    def test_strict_boundary_and_unknown_onset(self):
        a=dict(blocked=True,blockers=[dict(since=100)])
        self.assertFalse(assess(a,now=100+WEEK)['overdue'])
        self.assertTrue(assess(a,now=101+WEEK)['overdue'])
        for since in (None,True,float('nan'),float('inf'),-1,100+WEEK+1):
            result=assess(dict(blocked=True,blockers=[dict(since=since)]),now=100+WEEK)
            self.assertIsNone(result['elapsed_seconds']);self.assertEqual(result['status'],'unknown')
        for now in (True,float('nan'),-1):
            with self.assertRaises(ValueError):assess(a,now=now)
    def test_cancelled_or_resolved_does_not_warn(self):
        a=dict(blocked=True,blockers=[dict(since=1)])
        self.assertEqual(assess(a,cancelled=True,now=2*WEEK)['status'],'inactive')
        self.assertFalse(assess(dict(blocked=False,blockers=[]),now=2*WEEK)['overdue'])
    def test_mixed_known_and_unknown_is_partial(self):
        a=dict(blocked=True,blockers=[dict(since=1),dict(kind='dependency')])
        result=assess(a,now=2*WEEK)
        self.assertTrue(result['overdue']);self.assertEqual(result['unknown_since_count'],1)
        self.assertEqual(result['coverage'],'known_recorded_blockers_only')
    def test_restart_resolution_reblock_and_digest_stability(self):
        f=fixture.TaskBlockerTests();f.setUp();self.addCleanup(f.doCleanups)
        start=1000000
        with patch('time.time',return_value=start):f.command()
        with patch('time.time',return_value=start+WEEK+1):
            state=f.app.state();age=state['tasks'][0]['blocker_age'];self.assertTrue(age['overdue'])
            from apps.local_ui.server import LocalApp
            self.assertTrue(LocalApp(f.app.path).state()['tasks'][0]['blocker_age']['overdue'])
            with f.app.core() as core:
                owner=core.authority.issue_scope('local_owner');service=DialogueReviewService(core)
                before=service._context(owner,'personal')
            # Pure duration sampling cannot stale an otherwise unchanged review.
        with patch('time.time',return_value=start+WEEK+3600):
            f.app.state()
            with f.app.core() as core:
                after=DialogueReviewService(core)._context(core.authority.issue_scope('local_owner'),'personal')
            self.assertEqual(before,after)
            f.command(base_revision=1,blocked=False)
            self.assertEqual(f.app.state()['tasks'][0]['blocker_age']['status'],'inactive')
            f.command(base_revision=2,blocked=True)
            self.assertEqual(f.app.state()['tasks'][0]['blocker_age']['elapsed_seconds'],0)
            self.assertEqual(len(f.app.state()['tasks'][0]['blocker']['history']),3)

if __name__=='__main__':unittest.main()

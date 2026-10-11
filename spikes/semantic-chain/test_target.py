import unittest
from target import assess


class TestTargetScope(unittest.TestCase):
    def setUp(self):
        self.expected=dict(repository='owner/repo',path='bundle.md',ref='selected',artifact_revision=2,sha256='a'*64)
        self.observed=dict(self.expected,availability='read')

    def test_matching_file_never_verifies_task(self):
        self.assertEqual(assess(self.expected,self.observed),dict(status='observed_match',task_verified=False))

    def test_other_repository_or_path_is_not_evidence(self):
        for k in ['repository','path']:
            self.assertEqual(assess(self.expected,dict(self.observed,**{k:'other'}))['status'],'wrong_scope')

    def test_same_bytes_at_old_ref_or_artifact_are_stale(self):
        for change in [dict(ref='old'),dict(artifact_revision=1)]:
            self.assertEqual(assess(self.expected,dict(self.observed,**change))['status'],'stale')
        self.assertEqual(assess(self.expected,dict(self.observed,sha256='b'*64))['status'],'mismatch')

    def test_permission_failure_missing_and_incomplete_stay_distinct(self):
        for availability,status in [('denied','unknown'),('missing','missing'),('unavailable','unknown')]:
            self.assertEqual(assess(self.expected,dict(self.observed,availability=availability))['status'],status)
        self.assertEqual(assess(self.expected,dict(self.observed,sha256=None))['status'],'unknown')

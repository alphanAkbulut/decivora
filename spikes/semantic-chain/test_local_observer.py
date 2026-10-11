import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from local_observer import observe


class TestLocalObserver(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.content = b'approved artifact\n'
        (self.root/'artifact.md').write_bytes(self.content)
        self.sha = hashlib.sha256(self.content).hexdigest()

    def test_match_is_not_task_or_remote_upload_verification(self):
        result = observe(self.root, 'artifact.md', self.sha)
        self.assertEqual(result['status'], 'observed_match')
        self.assertEqual(result['bytes_read'], len(self.content))
        self.assertFalse(result['task_verified'])
        self.assertFalse(result['remote_upload_verified'])
        self.assertEqual(result['model_calls'], 0)
        self.assertNotIn('content', result)

    def test_changed_content_and_missing_not_done(self):
        (self.root/'artifact.md').write_bytes(b'old artifact')
        self.assertEqual(observe(self.root,'artifact.md',self.sha)['status'], 'mismatch')
        self.assertEqual(observe(self.root,'absent.md',self.sha)['status'], 'missing')

    def test_traversal_absolute_and_ambiguous_paths_rejected(self):
        for path in ['../outside', '/tmp/file', './artifact.md', 'x//y', 'x/../artifact.md', 'x\\y', '']:
            with self.subTest(path=path), self.assertRaises(ValueError): observe(self.root,path,self.sha)

    def test_symlink_file_directory_and_root_do_not_follow(self):
        (self.root/'file-link').symlink_to(self.root/'artifact.md')
        (self.root/'dir-link').symlink_to(self.root, target_is_directory=True)
        self.assertEqual(observe(self.root,'file-link',self.sha)['status'], 'unknown')
        self.assertEqual(observe(self.root,'dir-link/artifact.md',self.sha)['status'], 'unknown')
        self.assertEqual(observe(self.root/'dir-link','artifact.md',self.sha)['status'], 'unknown')

    def test_regular_file_and_finite_bounds_required(self):
        (self.root/'folder').mkdir()
        self.assertEqual(observe(self.root,'folder',self.sha)['reason'], 'not_regular_file')
        self.assertEqual(observe(self.root,'artifact.md',self.sha,max_bytes=1)['reason'], 'byte_limit')
        for limit in [0, True, 131073]:
            with self.assertRaises(ValueError): observe(self.root,'artifact.md',self.sha,max_bytes=limit)
        with self.assertRaises(ValueError): observe(self.root,'artifact.md','invalid')

    def test_fifo_does_not_block_or_count_as_file(self):
        os.mkfifo(self.root/'pipe')
        self.assertEqual(observe(self.root,'pipe',self.sha)['reason'], 'not_regular_file')

    def test_permission_error_stays_unknown(self):
        with patch('local_observer.os.open', side_effect=PermissionError) as mocked:
            with patch('local_observer.os.supports_dir_fd', os.supports_dir_fd | {mocked}):
                result = observe(self.root,'artifact.md',self.sha)
        self.assertEqual((result['status'],result['reason']), ('unknown','permission_denied'))

    def test_concurrent_change_never_publishes_match_hash(self):
        original = os.read
        def changing(fd, n):
            data = original(fd,n)
            (self.root/'artifact.md').write_bytes(b'changed')
            return data
        with patch('local_observer.os.read', side_effect=changing):
            result = observe(self.root,'artifact.md',self.sha)
        self.assertEqual(result['reason'], 'changed_during_read')
        self.assertIsNone(result['observed_sha256'])

    def test_replaced_path_during_read_is_unknown(self):
        original = os.read
        def replacing(fd, n):
            data = original(fd,n)
            replacement = self.root/'replacement'
            replacement.write_bytes(b'different inode')
            os.replace(replacement, self.root/'artifact.md')
            return data
        with patch('local_observer.os.read', side_effect=replacing):
            result = observe(self.root,'artifact.md',self.sha)
        self.assertEqual(result['reason'], 'changed_during_read')


if __name__ == '__main__': unittest.main()

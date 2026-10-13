"""Q16 planning regression checks; these do not certify product acceptance."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('check_task_closure', ROOT / 'scripts/check_task_closure.py')
closure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(closure)


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / 'docs/delivery/task-closure.json').read_text())

    def test_current_cross_file_inventory_and_graph_pass(self):
        result = closure.validate(ROOT, self.manifest)
        self.assertEqual(result['main_tasks'], 30)
        self.assertEqual(result['subtasks'], 129)
        self.assertEqual(result['dependency_cycles'], 0)

    def test_reintroducing_parent_downstream_cycle_is_rejected(self):
        row = self.manifest['subtasks']['T05d']
        row.update(classification='task_local', owner='T05', first_use_gate='T05', required_for_parent_closure=True)
        with self.assertRaisesRegex(ValueError, 'cycle'):
            closure.validate(ROOT, self.manifest)

    def test_missing_classification_or_owner_is_rejected(self):
        for key, value in (('classification', 'unknown'), ('owner', 'T99'), ('first_use_gate', 'T99'), ('reason', '')):
            manifest = copy.deepcopy(self.manifest)
            manifest['subtasks']['T05c'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                closure.validate(ROOT, manifest)

    def test_done_with_missing_evidence_or_unfinished_required_child_is_rejected(self):
        bad = copy.deepcopy(self.manifest)
        bad['tasks']['T04']['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'evidence'):
            closure.validate(ROOT, bad)
        bad = copy.deepcopy(self.manifest)
        bad['subtasks']['T04b'].update(classification='task_local', owner='T04', first_use_gate='T04', required_for_parent_closure=True)
        with self.assertRaisesRegex(ValueError, 'unfinished'):
            closure.validate(ROOT, bad)

    def test_unclassified_cross_file_work_or_lost_mvp_criterion_is_rejected(self):
        del self.manifest['subtasks']['T05b']
        with self.assertRaisesRegex(ValueError, 'inventory'):
            closure.validate(ROOT, self.manifest)
        self.setUp()
        self.manifest['mvp_criteria'].pop()
        with self.assertRaisesRegex(ValueError, 'MVP'):
            closure.validate(ROOT, self.manifest)

    def test_closure_does_not_allow_silent_acceptance_or_status_edit(self):
        self.manifest['tasks']['T05']['core_acceptance'] = 'Only startup required'
        with self.assertRaisesRegex(ValueError, 'acceptance'):
            closure.validate(ROOT, self.manifest)
        self.setUp()
        self.manifest['subtasks']['T05c']['status'] = 'DONE'
        with self.assertRaisesRegex(ValueError, 'status'):
            closure.validate(ROOT, self.manifest)


if __name__ == '__main__':
    unittest.main()

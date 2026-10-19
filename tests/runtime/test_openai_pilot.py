"""Real dispatch wiring with an offline HTTP double, not a model benchmark."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from packages.capture.openai_transport import read_key
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PilotWiringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.key = self.root / 'private' / 'key'
        self.setup = load('setup_openai_key')
        self.setup.save_key(self.key, 'sk-' + 'x' * 30)
        self.pilot = load('run_openai_pilot')
        self.folder = self.root / 'pilot'
        self.calls = []

    def post(self, path, payload, key):
        self.calls.append(path)
        if path.endswith('input_tokens'):
            return dict(object='response.input_tokens', input_tokens=1000)
        data = json.loads(payload['input'])
        source = data['source']
        output = dict(source_id=source['id'], source_sha256=source['sha256'],
                      context_sha256=data['context_sha256'], coverage='unknown',
                      candidates=[], status_changes=[], answer_proposals=[], relation_proposals=[])
        return dict(status='completed', error=None,
                    usage=dict(input_tokens=1000, output_tokens=100, total_tokens=1100,
                               input_tokens_details=dict(cached_tokens=0, cache_write_tokens=0),
                               output_tokens_details=dict(reasoning_tokens=0)),
                    output=[dict(type='message', role='assistant', status='completed',
                            content=[dict(type='output_text', text=json.dumps(output))])])

    def test_prepare_is_offline_and_stable(self):
        packet = self.pilot.prepare(self.folder)
        self.assertEqual(len(packet['jobs']), 10)
        self.assertEqual(packet, self.pilot.prepare(self.folder))
        self.assertFalse(self.calls)
        self.assertEqual(packet['manifest']['max_cost_microusd'], 1000000)
        for job in packet['jobs']:
            self.assertEqual(job['expectation_status'], 'AI_authored_not_human_gold')

    def test_network_double_passes_domain_grants_and_review_without_autoapply(self):
        packet = self.pilot.prepare(self.folder)
        result = self.pilot.run(self.folder, self.key, self.post)
        self.assertEqual(len(result['outcomes']), 10)
        self.assertEqual(len(self.calls), 20)
        self.assertEqual(result['shared_budget']['http_attempts'], 20)
        self.assertFalse(result['shared_budget']['frozen'])
        self.assertFalse(result['mvp_acceptance'])
        for job, outcome in zip(packet['jobs'], result['outcomes']):
            self.assertEqual(outcome['result']['status'], 'Ready for review')
            self.assertEqual(outcome['result']['usage']['total_tokens'], 1100)
            with Workspace(self.folder / job['database'], 'pilot') as core:
                scope = core.authority.issue_scope('pilot_owner')
                self.assertEqual(len(core.records(scope, 'synthetic')['records']), 1)
        self.pilot.run(self.folder, self.key, self.post)
        self.assertEqual(len(self.calls), 20)
        # Reporting must use saved usage, never repeat inference or modify receipts/DBs.
        import hashlib
        watched = list(self.folder.glob('*.sqlite')) + list(self.folder.glob('*.result.json'))
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
        report = load('report_openai_pilot').build(self.folder)
        self.assertEqual(report['corrected_estimated_cost_microusd'], 15750)
        self.assertTrue(report['seed_records_unchanged'])
        self.assertFalse(report['mvp_acceptance'])
        self.assertEqual(len(self.calls), 20)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched})

    def test_failure_stops_batch_without_retry(self):
        self.pilot.prepare(self.folder)
        def post(path, payload, key):
            if path.endswith('input_tokens'):
                return self.post(path, payload, key)
            self.calls.append(path)
            raise TimeoutError()
        result = self.pilot.run(self.folder, self.key, post)
        self.assertEqual(len(result['outcomes']), 1)
        self.assertEqual(result['outcomes'][0]['result']['status'], 'Analysis failed')
        self.assertTrue(result['shared_budget']['frozen'])
        self.assertEqual(len(self.calls), 2)
        self.pilot.run(self.folder, self.key, post)
        self.assertEqual(len(self.calls), 2)

    def test_missing_key_has_no_analysis_attempt(self):
        packet = self.pilot.prepare(self.folder)
        with self.assertRaises(FileNotFoundError):
            self.pilot.run(self.folder, self.root / 'missing', self.post)
        first = packet['jobs'][0]
        with Workspace(self.folder / first['database'], 'pilot') as core:
            self.assertEqual(core.db.execute("SELECT COUNT(*) FROM audit WHERE action='conversation_analysis_started'").fetchone()[0], 0)

    def test_key_setup_no_overwrite_no_repo_storage_and_private_mode(self):
        self.assertTrue(read_key(self.key).startswith('sk-'))
        self.assertEqual(self.key.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            self.setup.save_key(self.key, 'sk-' + 'y' * 30)
        with self.assertRaises(ValueError):
            self.setup.save_key(ROOT / 'secrets' / 'must-not-exist', 'sk-' + 'y' * 30)
        with self.assertRaises(ValueError):
            self.setup.save_key(self.root / 'other', 'not-a-key')


if __name__ == '__main__':
    unittest.main()

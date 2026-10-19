"""Offline network doubles: no API key, provider access, or semantic-quality claims."""
import copy
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from packages.capture.openai_transport import PilotTransport, PRICE_REVISION, fingerprint, read_key
from packages.capture.responses_extractor import ResponsesExtractor, request_payload
from packages.domain.source_event import ContractError


class PilotTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.key = self.root / 'key'
        self.key.write_text('sk-' + 'x' * 30)
        self.key.chmod(0o600)
        self.source = dict(id='source_fixture', sha256='a' * 64, text='Add the backup test.')
        self.payload = request_payload(self.source, model='gpt-6-luna', max_output_tokens=2000)
        self.other = copy.deepcopy(self.payload)
        self.other['model'] = 'gpt-6.1-sol'
        self.manifest = dict(approval_ref='synthetic-test-only', price_revision=PRICE_REVISION,
                             expires_at=int(time.time()) + 3600, max_http_attempts=20,
                             max_cost_microusd=1000000, max_input_tokens=10000,
                             max_output_tokens=2000, payloads=[fingerprint(self.payload), fingerprint(self.other)])
        self.calls = []

    def response(self, inp=300, out=50):
        raw = dict(source_id=self.source['id'], source_sha256=self.source['sha256'],
                   coverage='complete', candidates=[dict(type='Task', title='Backup test',
                   quote=self.source['text'], intent='planned')])
        return dict(status='completed', error=None,
                    usage=dict(input_tokens=inp, output_tokens=out, total_tokens=inp + out),
                    output=[dict(type='message', role='assistant', status='completed',
                    content=[dict(type='output_text', text=json.dumps(raw))])])

    def post(self, path, payload, key):
        self.calls.append(path)
        return dict(object='response.input_tokens', input_tokens=300) if path.endswith('input_tokens') else self.response()

    def transport(self, post=None, manifest=None):
        return PilotTransport(self.root / 'pilot.sqlite', manifest=manifest or self.manifest,
                              key_file=self.key, post=post or self.post)

    def assert_code(self, code, method):
        with self.assertRaises(ContractError) as cm:
            method()
        self.assertEqual(cm.exception.code, code)

    def test_exact_payload_count_generate_parser_and_restart(self):
        transport = self.transport()
        extractor = ResponsesExtractor(transport, model='gpt-6-luna', max_output_tokens=2000, authorized=True)
        output = extractor(self.source)
        self.assertEqual(output['candidates'][0]['title'], 'Backup test')
        self.assertEqual(self.calls, ['/v1/responses/input_tokens', '/v1/responses'])
        self.assertEqual(transport.snapshot()['committed_microusd'], 55)
        self.assertFalse(self.transport().snapshot()['frozen'])
        self.assert_code('pilot_retry_denied', lambda: self.transport()(self.payload))
        self.assertEqual(len(self.calls), 2)

    def test_changed_source_or_schema_denied_before_network(self):
        for key in ('input', 'instructions', 'text'):
            changed = copy.deepcopy(self.payload)
            changed[key] = 'different'
            self.assert_code('pilot_payload_denied', lambda: self.transport()(changed))
        self.assertFalse(self.calls)

    def test_policy_cannot_reset_budget_on_restart(self):
        self.transport()
        changed = dict(self.manifest, max_cost_microusd=100)
        self.assert_code('pilot_policy_changed', lambda: self.transport(manifest=changed))

    def test_shared_money_preflight_denies_without_count(self):
        manifest = dict(self.manifest, max_cost_microusd=1000)
        self.assert_code('pilot_budget_exceeded', lambda: self.transport(manifest=manifest)(self.payload))
        self.assertFalse(self.calls)

    def test_http_budget_counts_preflight_and_generation(self):
        manifest = dict(self.manifest, max_http_attempts=2)
        transport = self.transport(manifest=manifest)
        transport(self.payload)
        self.assert_code('pilot_budget_exceeded', lambda: transport(self.other))
        self.assertEqual(len(self.calls), 2)

    def test_count_above_limit_never_generates(self):
        def post(path, payload, key):
            self.calls.append(path)
            return dict(object='response.input_tokens', input_tokens=10001)
        transport = self.transport(post)
        self.assert_code('pilot_input_exceeded', lambda: transport(self.payload))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(transport.snapshot()['states'], ['input_rejected'])
        self.assertGreater(transport.snapshot()['committed_microusd'], 0)

    def test_timeout_freezes_across_models_and_restart(self):
        def post(path, payload, key):
            self.calls.append(path)
            raise TimeoutError('Untrusted provider detail must never enter ledger')
        self.assertRaises(TimeoutError, self.transport(post), self.payload)
        self.assert_code('pilot_review_required', lambda: self.transport()(self.other))
        self.assertEqual(len(self.calls), 1)
        self.assertNotIn(b'Untrusted', (self.root / 'pilot.sqlite').read_bytes())

    def test_missing_usage_and_boolean_usage_freeze(self):
        for value in (None, dict(input_tokens=True, output_tokens=1, total_tokens=2)):
            with self.subTest(usage=value):
                ledger = self.root / ('unknown-' + str(len(str(value))) + '.sqlite')
                def post(path, payload, key):
                    return dict(object='response.input_tokens', input_tokens=300) if path.endswith('input_tokens') else dict(self.response(), usage=value)
                transport = PilotTransport(ledger, manifest=self.manifest, key_file=self.key, post=post)
                self.assert_code('pilot_usage_unknown', lambda: transport(self.payload))
                self.assertTrue(transport.snapshot()['frozen'])

    def test_provider_overrun_keeps_actual_and_blocks_next(self):
        def post(path, payload, key):
            return dict(object='response.input_tokens', input_tokens=300) if path.endswith('input_tokens') else self.response(inp=301)
        transport = self.transport(post)
        self.assert_code('pilot_usage_overrun', lambda: transport(self.payload))
        self.assertEqual(transport.snapshot()['states'], ['overrun'])
        self.assert_code('pilot_review_required', lambda: transport(self.other))

    def test_private_key_file_link_and_permission_rejected(self):
        link = self.root / 'link'
        link.symlink_to(self.key)
        with self.assertRaises(OSError):
            read_key(link)
        self.key.chmod(0o644)
        self.assert_code('credential_file_unsafe', lambda: self.transport()(self.payload))
        self.assertFalse(self.calls)

    def test_parallel_unknown_cannot_bypass_reservation(self):
        entered, release = Event(), Event()
        def post(path, payload, key):
            entered.set()
            release.wait(3)
            raise TimeoutError()
        transport = self.transport(post)
        with ThreadPoolExecutor(max_workers=2) as pool:
            future = pool.submit(transport, self.payload)
            try:
                self.assertTrue(entered.wait(2))
                self.assert_code('pilot_review_required', lambda: self.transport()(self.other))
            finally:
                release.set()
            self.assertRaises(TimeoutError, future.result)

    def test_expired_or_nonfinite_or_unapproved_model_denied(self):
        for changed in (dict(self.manifest, expires_at=0), dict(self.manifest, max_cost_microusd=True),
                        dict(self.manifest, max_http_attempts=21)):
            self.assert_code('pilot_manifest_invalid', lambda: self.transport(manifest=changed))
        altered = dict(self.payload, model='unapproved-model')
        self.assert_code('pilot_payload_denied', lambda: self.transport()(altered))


if __name__ == '__main__':
    unittest.main()

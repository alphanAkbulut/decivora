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

from packages.capture.openai_transport import PilotTransport, PRICE_REVISION, fingerprint, read_key, micro_cost
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
                    usage=dict(input_tokens=inp, output_tokens=out, total_tokens=inp + out,
                               input_tokens_details=dict(cached_tokens=0, cache_write_tokens=0)),
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

    def test_cache_write_and_read_are_disjoint_not_additive(self):
        self.assertEqual(micro_cost('gpt-6.1-sol', 1000, 100, cached_tokens=200, cache_write_tokens=700), 2970)
        self.assertEqual(micro_cost('gpt-6-luna', 1061, 357, cache_write_tokens=1058), 312)

    def test_cold_cache_worst_case_is_reserved_before_count(self):
        # Previous uncached-only admission would have allowed this 42000 limit.
        manifest = dict(self.manifest, max_cost_microusd=42000)
        self.assert_code('pilot_budget_exceeded', lambda: self.transport(manifest=manifest)(self.other))
        self.assertFalse(self.calls)

    def test_missing_cache_details_freezes_without_assuming_zero(self):
        def post(path, payload, key):
            if path.endswith('input_tokens'):
                return dict(object='response.input_tokens', input_tokens=300)
            response = self.response()
            del response['usage']['input_tokens_details']
            return response
        transport = self.transport(post)
        self.assert_code('pilot_usage_unknown', lambda: transport(self.payload))
        self.assertTrue(transport.snapshot()['frozen'])

    def test_overlapping_cache_categories_are_rejected(self):
        def post(path, payload, key):
            if path.endswith('input_tokens'):
                return dict(object='response.input_tokens', input_tokens=300)
            response = self.response()
            response['usage']['input_tokens_details'] = dict(cached_tokens=200, cache_write_tokens=200)
            return response
        transport = self.transport(post)
        self.assert_code('pilot_usage_unknown', lambda: transport(self.payload))
        self.assertTrue(transport.snapshot()['frozen'])

    def test_unpriced_service_tier_freezes(self):
        def post(path, payload, key):
            return dict(object='response.input_tokens', input_tokens=300) if path.endswith('input_tokens') else dict(self.response(), service_tier='priority')
        transport = self.transport(post)
        self.assert_code('pilot_price_unknown', lambda: transport(self.payload))
        self.assertTrue(transport.snapshot()['frozen'])

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

    def test_unknown_review_is_explicit_retains_reserve_and_denies_retry(self):
        def failed(path, payload, key):
            raise TimeoutError('private response content')
        transport = self.transport(failed)
        self.assertRaises(TimeoutError, transport, self.payload)
        original = transport.snapshot()
        packet = transport.review_packet()
        self.assertTrue(packet['can_accept_reserved_continuation'])
        self.assertEqual(packet['unknowns'][0]['diagnostic'],
                         dict(phase='input_count', failure_code='provider_outcome_unknown'))
        self.assert_code('pilot_review_required', lambda: self.transport()(self.other))
        reviewed = transport.accept_reserved_unknown(fingerprint(self.payload),
                    snapshot_sha256=packet['snapshot_sha256'], approval_ref='owner-test-approval')
        self.assertFalse(reviewed['frozen'])
        after = self.transport().snapshot()
        self.assertEqual(after['committed_microusd'], original['committed_microusd'])
        self.assertEqual(after['http_attempts'], original['http_attempts'])
        self.assertEqual(after['states'], ['unknown'])
        self.assertIsNone(reviewed['unknowns'][0]['actual_microusd'])
        self.assert_code('pilot_retry_denied', lambda: self.transport()(self.payload))
        self.transport()(self.other)
        self.assertEqual(len(self.calls), 2)
        self.assertNotIn(b'private response', (self.root/'pilot.sqlite').read_bytes())

    def test_review_cannot_accept_stale_or_invented_or_unsafe_reference(self):
        transport = self.transport(lambda *args: (_ for _ in ()).throw(TimeoutError()))
        self.assertRaises(TimeoutError, transport, self.payload)
        packet = transport.review_packet()
        self.assert_code('pilot_review_stale', lambda: transport.accept_reserved_unknown(
            fingerprint(self.payload), snapshot_sha256='0'*64, approval_ref='owner-test'))
        for identity, ref in [('0'*64, 'owner-test'), (fingerprint(self.payload), 'unsafe\ntext')]:
            self.assert_code('pilot_review_invalid', lambda: transport.accept_reserved_unknown(
                identity, snapshot_sha256=packet['snapshot_sha256'], approval_ref=ref))
        self.assertTrue(transport.snapshot()['frozen'])

    def test_pending_and_overrun_cannot_be_cleared_as_unknown(self):
        transport = self.transport()
        with transport._db() as db:
            db.execute('INSERT INTO dispatch VALUES(?,?,?,?,?,?,?)',
                       (fingerprint(self.payload), 'pending', 2250, 2, None, None, None))
        for state in ('pending', 'overrun'):
            with transport._db() as db:
                db.execute('UPDATE dispatch SET state=?', (state,))
            packet = transport.review_packet()
            self.assertFalse(packet['can_accept_reserved_continuation'])
            self.assert_code('pilot_review_invalid', lambda: transport.accept_reserved_unknown(
                fingerprint(self.payload), snapshot_sha256=packet['snapshot_sha256'], approval_ref='owner-test'))

    def test_generation_error_phase_is_distinct_from_count(self):
        def failed(path, payload, key):
            if path.endswith('input_tokens'):
                return dict(object='response.input_tokens', input_tokens=300)
            raise ContractError('provider_connection_unknown', 'secret raw body')
        transport = self.transport(failed)
        self.assert_code('provider_connection_unknown', lambda: transport(self.payload))
        unknown = transport.review_packet()['unknowns'][0]
        self.assertEqual(unknown['diagnostic'], dict(phase='generation', failure_code='provider_connection_unknown'))
        self.assertIsNone(unknown['actual_microusd'])
        self.assertNotIn(b'secret raw', (self.root/'pilot.sqlite').read_bytes())


if __name__ == '__main__':
    unittest.main()

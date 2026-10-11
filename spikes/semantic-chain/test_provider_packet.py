import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from provider_packet import WIRE, decode, import_response, package, schema
from protocol import canonical, prepare
from anchors import prepare_quotes

ROOT = Path(__file__).resolve().parents[2]


class TestExperiment(unittest.TestCase):
    def setUp(self):
        self.req = prepare(dict(synthetic=True, project_id='p', session_id='s', messages=[dict(
            message_id='m', source_revision=1, text='Q1 için B seçiyorum.', actor=dict(type='human_owner'))]))
        packet = prepare_quotes(self.req)
        self.wire = dict(format=WIRE, request_id=self.req['request_id'], contract_id=packet['contract_id'],
            status='ok', records=[dict(message_id='m', kind='AnswerRecord', entity_key='answer',
                quote='Q1 için B seçiyorum.', attributes_json='{"question_id":"Q1","option_id":"B","presentation_revision":1}')])
        self.response = dict(status='completed', error=None, usage=None, output=[dict(type='message',
            status='completed', role='assistant', content=[dict(type='output_text', text=canonical(self.wire))])])

    def test_package_binds_source_and_never_claims_dispatch_permission(self):
        original = copy.deepcopy(self.req)
        pkg = package(self.req)
        self.assertEqual(pkg, package(self.req))
        self.assertEqual(self.req, original)
        self.assertIsNone(pkg['payload_draft']['model'])
        self.assertIsNone(pkg['payload_draft']['max_output_tokens'])
        self.assertFalse(pkg['manifest']['dispatch_authorized'])
        self.assertEqual(pkg['manifest']['automatic_retries'], 0)
        data = json.loads(pkg['payload_draft']['input'])
        self.assertEqual(set(data), {'request_id','contract_id','source','allowed_kinds'})
        self.assertNotIn('expected', data)
        changed = copy.deepcopy(self.req); changed['source']['messages'][0]['text'] = 'new'
        with self.assertRaises(ValueError): package(changed)

    def test_schema_fixed_keys_and_no_offset_or_authority_properties(self):
        s = schema(self.req)
        def walk(node):
            if node.get('type') == 'object':
                self.assertFalse(node['additionalProperties'])
                self.assertEqual(set(node['required']), set(node['properties']))
                for child in node['properties'].values(): walk(child)
            if 'items' in node: walk(node['items'])
        walk(s)
        props = s['properties']['records']['items']['properties']
        self.assertNotIn('start', props)
        self.assertEqual(props['message_id']['enum'], ['m'])

    def test_nested_attributes_semantics_preserved_and_raw_unchanged(self):
        raw = canonical(self.wire)
        result = decode(self.req, raw)
        attrs = result['response']['records'][0]['attributes']
        self.assertEqual(attrs, {'question_id':'Q1','option_id':'B','presentation_revision':1})
        self.assertEqual(canonical(self.wire), raw)
        self.assertEqual(result['canonical_mutations'], 0)

    def test_bad_inner_json_authority_duplicates_bounds_and_missing_quote_rejected(self):
        for attrs in ['[]', '{"option_id":"A","option_id":"B"}', '{"verified":true}', '{"x":{"approval":true}}', '{"x":"'+'a'*4096+'"}']:
            wire = copy.deepcopy(self.wire); wire['records'][0]['attributes_json'] = attrs
            with self.subTest(attrs=attrs[:30]), self.assertRaises(ValueError): decode(self.req, canonical(wire))
        for changes in [dict(contract_id='stale'), dict(status='abstain'), dict(format='old')]:
            with self.assertRaises(ValueError): decode(self.req, canonical(dict(self.wire, **changes)))
        wire = copy.deepcopy(self.wire); wire['records'][0]['quote'] = 'not present'
        with self.assertRaises(ValueError): decode(self.req, canonical(wire))

    def test_incomplete_output_never_salvaged_and_usage_unknown_not_zero(self):
        for status in ['incomplete','failed','queued']:
            r = import_response(self.req, canonical(dict(self.response, status=status)))
            self.assertEqual(r['status'], 'incomplete')
            self.assertIsNone(r['derived']); self.assertIsNone(r['usage'])
        r = import_response(self.req, canonical(self.response))
        self.assertEqual(r['status'], 'candidate_validated')
        self.assertEqual(r['usage_status'], 'unverified')
        self.assertEqual(r['model_calls'], 0)

    def test_refusal_duplicate_text_tool_call_invalid_wire_fail_closed(self):
        r = copy.deepcopy(self.response)
        r['output'][0]['content'] = [dict(type='refusal', refusal='no')]
        self.assertEqual(import_response(self.req, canonical(r))['status'], 'refused')
        r = copy.deepcopy(self.response); r['output'] *= 2
        self.assertEqual(import_response(self.req, canonical(r))['reason'], 'single_output_text_required')
        r = copy.deepcopy(self.response); r['output'].append(dict(type='function_call'))
        self.assertEqual(import_response(self.req, canonical(r))['status'], 'rejected')

    def test_malformed_provider_arrays_and_stale_request(self):
        for value in [None, {}, 'text']:
            r = dict(self.response, output=value)
            self.assertEqual(import_response(self.req, canonical(r))['status'], 'rejected')
            r = copy.deepcopy(self.response); r['output'][0]['content'] = value
            self.assertEqual(import_response(self.req, canonical(r))['status'], 'rejected')
        req = copy.deepcopy(self.req); req['source']['messages'][0]['source_revision'] = 2
        with self.assertRaises(ValueError): import_response(req, canonical(self.response))
        r = copy.deepcopy(self.response); r['output'][0]['content'][0]['text'] = '{}'
        self.assertEqual(import_response(self.req, canonical(r))['status'], 'rejected')

    def test_cli_no_dispatch_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)/'pkg.json'
            args=[sys.executable,'-B',str(ROOT/'spikes/semantic-chain/provider_packet.py'),'prepare',
                '--request',str(ROOT/'examples/model-smoke/s02-request.json'),'--out',str(dest)]
            run=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            raw=dest.read_bytes()
            self.assertEqual(json.loads(raw)['manifest']['dispatch'],'not_run')
            self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)
            self.assertEqual(dest.read_bytes(),raw)


if __name__ == '__main__': unittest.main()

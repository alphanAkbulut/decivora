"""T04 runtime acceptance; no model/provider/connector dispatch."""
from dataclasses import FrozenInstanceError
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from apps.hub.runtime import ensure_runtime, read_selected_input, runtime_status
from packages.domain.source_event import ContractError, MAX_INPUT_BYTES, SourceEvent, parse_source_event, source_event_schema, validate_source_event

ROOT = Path(__file__).resolve().parents[2]


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads((ROOT / 'examples/runtime/source-event.json').read_text())

    def run_cli(self, *args, cwd=ROOT):
        return subprocess.run([sys.executable, '-S', '-B', '-m', 'apps.hub', *args], cwd=cwd,
                              env={'PYTHONNOUSERSITE': '1'}, capture_output=True, text=True, timeout=10)

    def test_source_contract_preserves_unicode_is_immutable_and_digest_is_stable(self):
        event = parse_source_event(json.dumps(self.sample, ensure_ascii=False).encode())
        self.assertIsInstance(event, SourceEvent)
        self.assertEqual(event.text, self.sample['text'])
        self.assertEqual(event.content_digest(), validate_source_event(self.sample).content_digest())
        with self.assertRaises(FrozenInstanceError):
            event.text = 'approved'

    def test_missing_extra_and_authority_claim_fields_rejected(self):
        for field in self.sample:
            bad = copy.deepcopy(self.sample)
            del bad[field]
            with self.subTest(missing=field), self.assertRaises(ContractError):
                validate_source_event(bad)
        for extra in ('approved', 'permission', 'actor_authenticated', 'execute_command'):
            with self.subTest(extra=extra), self.assertRaises(ContractError):
                validate_source_event(dict(self.sample, **{extra: True}))

    def test_wrong_types_unknown_version_real_input_and_bad_ids_rejected(self):
        variants = [dict(source_revision=True), dict(source_revision=0), dict(source_revision='1'),
                    dict(source_revision=9223372036854775808), dict(format='future'), dict(synthetic=False),
                    dict(synthetic=1), dict(actor_type='admin'), dict(text=''), dict(text=None),
                    dict(project_id=''), dict(project_id='prj\n'), dict(event_id='a' * 129)]
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ContractError):
                validate_source_event(dict(self.sample, **variant))

    def test_duplicate_nonfinite_invalid_utf8_and_deep_json_rejected(self):
        for raw in (b'{"text":"x","text":"y"}', b'{"source_revision":NaN}', b'\xff',
                    b'[' * 1100 + b']' * 1100, b'not-json', b'null'):
            with self.subTest(raw=raw[:20]), self.assertRaises(ContractError):
                parse_source_event(raw)

    def test_byte_and_character_limits_are_fail_closed_without_truncation(self):
        with self.assertRaises(ContractError):
            parse_source_event(b' ' * (MAX_INPUT_BYTES + 1))
        for text in ('x' * 16385, '界' * 12000, '\ud800'):
            with self.subTest(size=len(text)), self.assertRaises(ContractError):
                validate_source_event(dict(self.sample, text=text))

    def test_exported_schema_matches_code_and_manifest_names_real_dependencies(self):
        schema = source_event_schema()
        self.assertEqual(schema, json.loads((ROOT / 'manifests/source-event.schema.json').read_text()))
        schema['properties']['project_id']['maxLength'] = 1
        self.assertEqual(source_event_schema()['properties']['project_id']['maxLength'], 128)
        manifest = json.loads((ROOT / 'manifests/runtime.json').read_text())
        self.assertEqual(manifest['runtime']['ci_python'], '3.12')
        self.assertEqual(manifest['third_party_python_packages'], [])
        self.assertFalse(manifest['provider_dispatch_enabled'])

    def test_status_reports_unimplemented_capabilities_disabled(self):
        status = runtime_status()
        self.assertEqual(status['stage'], 'development_scaffold')
        self.assertTrue(status['capabilities']['source_contract_validation'])
        self.assertTrue(all(not v for k, v in status['capabilities'].items() if k != 'source_contract_validation'))
        self.assertEqual(status['canonical_mutations'], 0)
        self.assertEqual(status['model_dispatches'], 0)

    def test_cli_validates_selected_fixture_without_echoing_raw_source(self):
        run = self.run_cli('validate', '--input', str(ROOT / 'examples/runtime/source-event.json'))
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['status'], 'validated_only')
        self.assertFalse(result['actor_identity_verified'])
        self.assertFalse(result['durable_receipt'])
        self.assertFalse(result['human_approval'])
        self.assertFalse(result['execution_authorized'])
        self.assertNotIn(self.sample['text'], run.stdout)

    def test_invalid_cli_returns_safe_error_without_secrets_or_user_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'private-input.json'
            path.write_text(json.dumps(dict(self.sample, token='SENSITIVE_SENTINEL')))
            run = self.run_cli('validate', '--input', str(path))
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stderr)['error']['code'], 'invalid_fields')
            self.assertNotIn('SENSITIVE_SENTINEL', run.stderr)
            self.assertNotIn(str(path), run.stderr)
            self.assertEqual(run.stdout, '')

    def test_clean_copy_starts_and_validates_with_site_packages_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('apps', 'packages', 'manifests', 'examples/runtime'):
                shutil.copytree(ROOT / folder, root / folder, ignore=shutil.ignore_patterns('__pycache__'))
            before = {str(p.relative_to(root)) for p in root.rglob('*')}
            run = self.run_cli(cwd=root)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout)['version'], '0.1.0-dev')
            run = self.run_cli('validate', '--input', str(root / 'examples/runtime/source-event.json'), cwd=root)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(before, {str(p.relative_to(root)) for p in root.rglob('*')})

    def test_missing_oversize_symlink_or_nonregular_input_is_not_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ContractError):
                read_selected_input(root / 'missing')
            path = root / 'large.json'
            path.write_bytes(b'x' * (MAX_INPUT_BYTES + 1))
            with self.assertRaises(ContractError):
                read_selected_input(path)
            if hasattr(os, 'O_NOFOLLOW'):
                link = root / 'linked'
                link.symlink_to(path)
                with self.assertRaises(ContractError):
                    read_selected_input(link)
            if hasattr(os, 'mkfifo'):
                fifo = root / 'pipe'
                os.mkfifo(fifo)
                with self.assertRaises(ContractError):
                    read_selected_input(fifo)

    def test_unsupported_python_is_rejected_before_runtime_import(self):
        for version in ((3, 9), (3, 11), (3, 13)):
            with self.subTest(version=version), self.assertRaises(ContractError):
                ensure_runtime(version)
        run = subprocess.run([sys.executable, '-S', '-B', '-c',
            "import sys,runpy;sys.version_info=(3,11,0,'final',0);runpy.run_module('apps.hub',run_name='__main__')"],
            cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stderr)['error']['code'], 'unsupported_python')
        self.assertNotIn('Traceback', run.stderr)


if __name__ == '__main__':
    unittest.main()

"""T05c receipt/activation gate fixtures, not a real provider authorization test."""
from dataclasses import asdict, replace
import copy
import json
from pathlib import Path
import unittest
import subprocess
import sys

from packages.domain.connection_authorization import ReviewContext, authorization_schema, review_authorization, validate_authorization
from packages.domain.source_event import ContractError

ROOT = Path(__file__).resolve().parents[2]


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads((ROOT / 'examples/runtime/connection-authorization.json').read_text())
        self.receipt = validate_authorization(self.sample)
        shared = {field: getattr(self.receipt, field) for field in ('workspace_id', 'project_id', 'binding_id',
            'binding_revision', 'source_epoch', 'provider', 'account_id', 'resource_id', 'grantor_id',
            'authz_revision', 'policy_revision', 'source_evidence_ref', 'approval_ref')}
        self.context = ReviewContext(**shared, expected_digest=self.receipt.digest(), source_access_verified=True,
            target_write_verified=True, human_approval_verified=True, audit_available=True,
            source_coverage_verified=True, now=120)

    def test_valid_review_never_activates_or_reads_source(self):
        result = review_authorization(self.receipt, self.context, 'read_source')
        self.assertEqual(result['status'], 'review_ready')
        self.assertFalse(result['connection_activated'])
        self.assertFalse(result['source_read_performed'])
        self.assertEqual(result['model_dispatches'], 0)

    def test_owner_without_source_or_source_without_target_is_denied(self):
        for field in ('source_access_verified', 'target_write_verified', 'human_approval_verified',
                      'source_coverage_verified', 'audit_available'):
            for value in (False, None, 1, 'yes'):
                with self.subTest(field=field, value=value):
                    result = review_authorization(self.receipt, replace(self.context, **{field: value}), 'read_source')
                    self.assertEqual(result['status'], 'review_denied')
                    self.assertIsNone(result['effective_action'])

    def test_cross_project_account_session_epoch_and_stale_revision_are_denied(self):
        for field, value in (('project_id', 'other'), ('workspace_id', 'other'), ('account_id', 'other'),
            ('binding_id', 'other'), ('source_epoch', 'other'), ('grantor_id', 'agent'),
            ('binding_revision', 2), ('authz_revision', 2), ('policy_revision', True), ('approval_ref', 'other')):
            with self.subTest(field=field):
                self.assertEqual(review_authorization(self.receipt, replace(self.context, **{field: value}), 'read_source')['status'], 'review_denied')

    def test_scope_change_digest_and_action_intersection_prevent_implicit_expansion(self):
        altered = replace(self.receipt, externally_granted_actions=('list_resources', 'read_source'))
        self.assertIn('scope_digest_changed', review_authorization(altered, self.context, 'read_source')['reason_codes'])
        result = review_authorization(self.receipt, self.context, 'capture_events')
        self.assertIn('action_not_effective', result['reason_codes'])
        for field in ('requested_actions', 'externally_granted_actions', 'application_allowed_actions'):
            receipt = replace(self.receipt, **{field: ('list_resources',)})
            ctx = replace(self.context, expected_digest=receipt.digest())
            self.assertIn('action_not_effective', review_authorization(receipt, ctx, 'read_source')['reason_codes'])

    def test_expiry_requested_revoked_and_invalid_clock_never_grant_permission(self):
        for now in (99, 200, True, None):
            self.assertEqual(review_authorization(self.receipt, replace(self.context, now=now), 'read_source')['status'], 'review_denied')
        for state in ('requested', 'revoked'):
            receipt = replace(self.receipt, status=state)
            ctx = replace(self.context, expected_digest=receipt.digest())
            self.assertIn('permission_not_granted', review_authorization(receipt, ctx, 'read_source')['reason_codes'])

    def test_payload_approval_or_execution_claims_and_bad_fields_are_rejected(self):
        for field in ('approved', 'authenticated', 'execute_command', 'token'):
            with self.subTest(field=field), self.assertRaises(ContractError):
                validate_authorization(dict(self.sample, **{field: True}))
        variants = [dict(revision=True), dict(binding_revision=0), dict(requested_actions=['execute_code']),
            dict(include_refs=[]), dict(exclude_refs=['resource_demo']), dict(source_from=301),
            dict(expires_at=100), dict(project_id='same name'), dict(application_allowed_actions=['read_source']*2)]
        for variant in variants:
            with self.subTest(variant=variant), self.assertRaises(ContractError):
                validate_authorization(dict(self.sample, **variant))

    def test_unknown_and_untyped_context_cannot_satisfy_trusted_review(self):
        with self.assertRaises(ContractError):
            review_authorization(self.receipt, asdict(self.context), 'read_source')
        with self.assertRaises(ContractError):
            review_authorization(self.receipt, self.context, 'write_target')
        with self.assertRaises(ContractError):
            review_authorization(replace(self.receipt, authz_revision=True), self.context, 'read_source')

    def test_exported_schema_matches_and_lists_are_normalized_without_mutation(self):
        self.assertEqual(authorization_schema(), json.loads((ROOT / 'manifests/connection-authorization.schema.json').read_text()))
        source = copy.deepcopy(self.sample)
        source['requested_actions'] = ['read_source', 'list_resources']
        receipt = validate_authorization(source)
        self.assertEqual(source['requested_actions'], ['read_source', 'list_resources'])
        self.assertEqual(receipt.requested_actions, ('list_resources', 'read_source'))

    def test_cli_fixed_fixture_denies_missing_source_permission_and_stale_context(self):
        run = subprocess.run([sys.executable, '-S', '-B', '-m', 'apps.hub', 'connection-demo'],
                             cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['source_permission_missing'], 'review_denied')
        self.assertEqual(result['stale_authority'], 'review_denied')
        self.assertFalse(result['connection_activated'])
        self.assertFalse(result['source_read_performed'])


if __name__ == '__main__':
    unittest.main()

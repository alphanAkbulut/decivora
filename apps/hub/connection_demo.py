"""Fixed synthetic receipt review, no external permission or connector activation."""
from dataclasses import replace
import json
from pathlib import Path

from packages.domain.connection_authorization import ReviewContext, review_authorization, validate_authorization


def run_demo():
    root = Path(__file__).resolve().parents[2]
    receipt = validate_authorization(json.loads((root / 'examples/runtime/connection-authorization.json').read_text()))
    shared = {field: getattr(receipt, field) for field in ('workspace_id', 'project_id', 'binding_id',
        'binding_revision', 'source_epoch', 'provider', 'account_id', 'resource_id', 'grantor_id',
        'authz_revision', 'policy_revision', 'source_evidence_ref', 'approval_ref')}
    context = ReviewContext(**shared, expected_digest=receipt.digest(), source_access_verified=True,
        target_write_verified=True, human_approval_verified=True, audit_available=True,
        source_coverage_verified=True, now=120)
    allowed = review_authorization(receipt, context, 'read_source')
    source_missing = review_authorization(receipt, replace(context, source_access_verified=False), 'read_source')
    stale = review_authorization(receipt, replace(context, authz_revision=2), 'read_source')
    if (allowed['status'], source_missing['status'], stale['status']) != ('review_ready', 'review_denied', 'review_denied'):
        raise RuntimeError('Synthetic connection review did not meet expectations.')
    return dict(status='passed_connection_contract_demo', context_authority='synthetic_fixture',
        contract_digest=receipt.digest(), valid_review=allowed['status'],
        source_permission_missing=source_missing['status'], stale_authority=stale['status'],
        connection_activated=False, source_read_performed=False, model_dispatches=0)

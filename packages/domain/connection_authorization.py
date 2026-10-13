"""T05c versioned connection permission contract and synthetic review gate.

Payload fields are claims; trusted context comes from separate adapters.
This module never activates capture or performs external reads.
"""
from dataclasses import asdict, dataclass
import hashlib
import json

from .project_binding import identifier
from .source_event import ContractError

FORMAT = 'decivora-connection-authorization-1'
ACTIONS = frozenset({'list_resources', 'read_source', 'capture_events'})


@dataclass(frozen=True, slots=True)
class ConnectionAuthorization:
    format: str
    authorization_id: str
    revision: int
    workspace_id: str
    project_id: str
    binding_id: str
    binding_revision: int
    source_epoch: str
    provider: str
    account_id: str
    resource_id: str
    grantor_id: str
    source_evidence_ref: str
    approval_ref: str
    policy_ref: str
    visibility_ref: str
    retention_ref: str
    egress_ref: str
    authz_revision: int
    policy_revision: int
    requested_actions: tuple[str, ...]
    externally_granted_actions: tuple[str, ...]
    application_allowed_actions: tuple[str, ...]
    include_refs: tuple[str, ...]
    exclude_refs: tuple[str, ...]
    source_from: int
    source_to: int
    approved_at: int
    expires_at: int
    status: str

    def digest(self):
        return hashlib.sha256(canonical(asdict(self)).encode('utf-8')).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def validate_authorization(value):
    fields = set(ConnectionAuthorization.__dataclass_fields__)
    if type(value) is not dict or set(value) != fields:
        raise ContractError('invalid_authorization', 'Permission receipt has missing or unsupported fields.')
    if value['format'] != FORMAT or value['status'] not in ('requested', 'granted', 'revoked'):
        raise ContractError('invalid_authorization', 'Unsupported receipt format or state.')
    identifiers = fields - {'format', 'status', 'revision', 'binding_revision', 'authz_revision', 'policy_revision',
        'source_from', 'source_to', 'approved_at', 'expires_at', 'requested_actions',
        'externally_granted_actions', 'application_allowed_actions', 'include_refs', 'exclude_refs'}
    for field in identifiers:
        identifier(value[field])
    for field in ('revision', 'binding_revision', 'authz_revision', 'policy_revision'):
        if type(value[field]) is not int or not 1 <= value[field] <= 9223372036854775807:
            raise ContractError('invalid_revision', 'Receipt revisions must be positive 64-bit integers.')
    for field in ('source_from', 'source_to', 'approved_at', 'expires_at'):
        if type(value[field]) is not int or not 0 <= value[field] <= 9223372036854775807:
            raise ContractError('invalid_time', 'Receipt time bounds must be nonnegative integer seconds.')
    if value['source_from'] > value['source_to'] or value['approved_at'] >= value['expires_at']:
        raise ContractError('invalid_time', 'Receipt ranges or expiry are invalid.')
    normalized = dict(value)
    for field in ('requested_actions', 'externally_granted_actions', 'application_allowed_actions', 'include_refs', 'exclude_refs'):
        items = value[field]
        if type(items) not in (list, tuple) or len(items) > 32 or any(type(i) is not str for i in items) or len(set(items)) != len(items):
            raise ContractError('invalid_scope', 'Receipt lists must be bounded unique strings.')
        if field.endswith('actions'):
            if not set(items) <= ACTIONS:
                raise ContractError('invalid_scope', 'Unsupported source permission action.')
        else:
            for item in items:
                identifier(item)
        normalized[field] = tuple(sorted(items))
    if not normalized['requested_actions'] or not normalized['include_refs'] or normalized['resource_id'] not in normalized['include_refs']:
        raise ContractError('invalid_scope', 'Explicit resource selection and requested action required.')
    if set(normalized['include_refs']) & set(normalized['exclude_refs']):
        raise ContractError('invalid_scope', 'Selected and excluded resources cannot overlap.')
    if len(canonical(normalized).encode('utf-8')) > 16384:
        raise ContractError('input_too_large', 'Permission receipt exceeds the development size limit.')
    return ConnectionAuthorization(**normalized)


def authorization_schema():
    properties = {}
    for field in ConnectionAuthorization.__dataclass_fields__:
        if field == 'format':
            properties[field] = dict(type='string', const=FORMAT)
        elif field == 'status':
            properties[field] = dict(type='string', enum=['requested', 'granted', 'revoked'])
        elif field.endswith('revision') or field in ('source_from', 'source_to', 'approved_at', 'expires_at'):
            properties[field] = dict(type='integer', minimum=1 if field.endswith('revision') else 0,
                                     maximum=9223372036854775807)
        elif field.endswith('actions') or field in ('include_refs', 'exclude_refs'):
            item = dict(type='string', enum=sorted(ACTIONS)) if field.endswith('actions') else dict(type='string', pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$')
            properties[field] = dict(type='array', items=item, maxItems=32, uniqueItems=True)
        else:
            properties[field] = dict(type='string', pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$')
    return dict(**{'$schema': 'https://json-schema.org/draft/2020-12/schema'}, type='object',
        additionalProperties=False, required=sorted(properties), properties=properties)


@dataclass(frozen=True, slots=True)
class ReviewContext:
    """Trusted adapter fixture snapshot, not an identity/session verification API."""
    expected_digest: str
    workspace_id: str
    project_id: str
    binding_id: str
    binding_revision: int
    source_epoch: str
    provider: str
    account_id: str
    resource_id: str
    grantor_id: str
    authz_revision: int
    policy_revision: int
    source_evidence_ref: str
    approval_ref: str
    source_access_verified: bool
    target_write_verified: bool
    human_approval_verified: bool
    audit_available: bool
    source_coverage_verified: bool
    now: int


def review_authorization(receipt, context, action):
    if type(receipt) is not ConnectionAuthorization or type(context) is not ReviewContext:
        raise ContractError('invalid_review', 'Typed receipt and separate trusted review context required.')
    receipt = validate_authorization(asdict(receipt))
    if type(action) is not str or action not in ACTIONS:
        raise ContractError('invalid_scope', 'Unsupported source permission action.')
    # No original payload approval flag can satisfy these separate checks.
    reasons = []
    if receipt.digest() != context.expected_digest:
        reasons.append('scope_digest_changed')
    for field in ('workspace_id', 'project_id', 'binding_id', 'binding_revision', 'source_epoch',
                  'provider', 'account_id', 'resource_id', 'grantor_id', 'authz_revision',
                  'policy_revision', 'source_evidence_ref', 'approval_ref'):
        expected = getattr(context, field)
        if type(expected) is not type(getattr(receipt, field)) or expected != getattr(receipt, field):
            reasons.append('identity_or_revision_changed')
            break
    for field in ('source_access_verified', 'target_write_verified', 'human_approval_verified',
                  'audit_available', 'source_coverage_verified'):
        if getattr(context, field) is not True:
            reasons.append(field + '_required')
    if type(context.now) is not int or not receipt.approved_at <= context.now < receipt.expires_at:
        reasons.append('permission_expired_or_not_yet_valid')
    if receipt.status != 'granted':
        reasons.append('permission_not_granted')
    if not all(action in getattr(receipt, field) for field in
               ('requested_actions', 'externally_granted_actions', 'application_allowed_actions')):
        reasons.append('action_not_effective')
    return dict(status='review_ready' if not reasons else 'review_denied', reason_codes=reasons,
                effective_action=action if not reasons else None, connection_activated=False,
                source_read_performed=False, model_dispatches=0)

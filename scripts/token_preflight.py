#!/usr/bin/env python3
"""Offline P0 token admission assessment. Never dispatches, authorizes or reserves."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def integer(value, minimum=0):
    return type(value) is int and minimum <= value <= 10**12


def assess(plan, policy, scopes, capability):
    """Assess trusted-caller snapshots; JSON flags do not establish their authority.

    full_input_tokens_upper_bound includes instructions, history, tool schemas and
    provider framing. Generation covers all context/billable reasoning in this P0
    contract. Other metered operations require separate controls. Reservations
    include unknown in-flight consumption; absent amounts are never zero.
    """
    result = dict(decision='blocked', reason_codes=[], aggregate_token_upper_bound=None,
                  context_requirements=[], assessment_digest=None,
                  dispatch_performed=False, dispatch_authorized=False,
                  reservation_created=False, monetary_cap_enforced=False)
    reasons = result['reason_codes']
    if not (isinstance(plan, dict) and isinstance(policy, dict)
            and isinstance(capability, dict) and isinstance(scopes, list)):
        reasons.append('invalid_snapshot')
        return result
    try:
        encoded = json.dumps([plan, policy, scopes, capability], sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode()
    except (TypeError, ValueError, RecursionError):
        reasons.append('invalid_snapshot')
        return result
    if len(encoded) > 32768:
        reasons.append('snapshot_too_large')
        return result
    result['assessment_digest'] = hashlib.sha256(encoded).hexdigest()
    if (not isinstance(policy.get('revision'), str) or not policy['revision']
            or plan.get('policy_revision') != policy['revision']):
        reasons.append('policy_revision_missing_or_stale')
    limits = ('max_input_tokens', 'max_output_tokens', 'max_context_tokens',
              'max_run_tokens', 'max_calls')
    if (any(not integer(policy.get(k), 1) for k in limits)
            or not integer(policy.get('safety_margin_tokens'))
            or not integer(policy.get('review_above_tokens'))):
        reasons.append('finite_policy_required')
    required = policy.get('required_scope_ids')
    required_valid = (isinstance(required, list) and 1 <= len(required) <= 16
                      and all(isinstance(s, str) and s for s in required)
                      and len(set(required)) == len(required))
    if not required_valid:
        reasons.append('required_budget_scopes_unknown')
    if (not isinstance(plan.get('provider'), str) or not plan['provider']
            or not isinstance(plan.get('model'), str) or not plan['model']
            or plan.get('provider') != capability.get('provider')
            or plan.get('model') != capability.get('model')):
        reasons.append('model_binding_unknown_or_mismatch')
    flags = ('verified', 'input_bound_verified', 'output_limit_enforced', 'reasoning_covered')
    if (any(capability.get(k) is not True for k in flags)
            or not integer(capability.get('model_context_tokens'), 1)
            or not integer(capability.get('max_generation_tokens'), 1)):
        reasons.append('capability_upper_bound_unverified')
    calls = plan.get('calls')
    if not isinstance(calls, list) or not 1 <= len(calls) <= 64:
        reasons.append('bounded_call_manifest_required')
    else:
        ids = []
        for call in calls:
            if (not isinstance(call, dict) or not isinstance(call.get('id'), str)
                    or not call['id']
                    or not integer(call.get('full_input_tokens_upper_bound'))
                    or not integer(call.get('generation_tokens_upper_bound'), 1)):
                reasons.append('call_upper_bound_unknown')
                break
            ids.append(call['id'])
        if len(set(ids)) != len(ids):
            reasons.append('duplicate_call_identity')
    scope_ids = []
    if not 1 <= len(scopes) <= 16:
        reasons.append('budget_snapshot_required')
    for scope in scopes:
        if (not isinstance(scope, dict) or not isinstance(scope.get('id'), str)
                or not scope['id']):
            reasons.append('budget_snapshot_unknown')
            continue
        scope_ids.append(scope['id'])
        if (not isinstance(scope.get('revision'), str) or not scope['revision']
                or not integer(scope.get('max_tokens'), 1)
                or not integer(scope.get('spent_tokens'))
                or not integer(scope.get('reserved_tokens'))):
            reasons.append('budget_snapshot_unknown')
    if len(set(scope_ids)) != len(scope_ids):
        reasons.append('duplicate_budget_scope')
    if required_valid and set(scope_ids) != set(required):
        reasons.append('required_budget_scope_missing')
    if reasons:
        result['reason_codes'] = list(dict.fromkeys(reasons))
        return result

    # Each retry/child is a call in the explicit manifest; no cache discount assumed.
    total = 0
    if len(calls) > policy['max_calls']:
        reasons.append('call_count_hard_cap')
    for call in calls:
        inp = call['full_input_tokens_upper_bound']
        gen = call['generation_tokens_upper_bound']
        total += inp + gen
        context = inp + gen + policy['safety_margin_tokens']
        result['context_requirements'].append(dict(call_id=call['id'], tokens=context))
        if inp > policy['max_input_tokens']:
            reasons.append('input_hard_cap')
        if gen > min(policy['max_output_tokens'], capability['max_generation_tokens']):
            reasons.append('output_hard_cap')
        if context > min(policy['max_context_tokens'], capability['model_context_tokens']):
            reasons.append('context_hard_cap')
    result['aggregate_token_upper_bound'] = total
    if total > policy['max_run_tokens']:
        reasons.append('run_token_hard_cap')
    for scope in scopes:
        if scope['spent_tokens'] + scope['reserved_tokens'] + total > scope['max_tokens']:
            reasons.append('budget_hard_cap:' + scope['id'])
    if reasons:
        result['reason_codes'] = list(dict.fromkeys(reasons))
    elif total > policy['review_above_tokens']:
        result['decision'] = 'requires_risk_approval'
        reasons.append('token_review_threshold')
    else:
        result['decision'] = 'within_policy'
    return result


def s02_assessment():
    """Read selected preparation only, not account secrets or corpus oracles."""
    folder = ROOT / 'examples/model-smoke'
    source_policy = json.loads((folder / 's02-policy.json').read_text())
    hashes = {}
    for name, key in (('s02-prompt.txt', 'prompt_sha256'), ('s02-request.json', 'request_sha256')):
        hashes[key] = hashlib.sha256((folder / name).read_bytes()).hexdigest()
    if any(hashes[k] != source_policy[k] for k in hashes):
        raise ValueError('S02 package changed')
    policy = dict(revision='s02-capability-pending', max_calls=source_policy['max_requests'],
                  max_input_tokens=source_policy['max_input_tokens'],
                  max_output_tokens=source_policy['max_output_tokens'],
                  max_context_tokens=source_policy['max_context_tokens'],
                  max_run_tokens=source_policy['max_total_tokens'],
                  safety_margin_tokens=None, review_above_tokens=None,
                  required_scope_ids=['run:S02', 'account:selected'])
    plan = dict(policy_revision=policy['revision'], provider=source_policy['provider'],
                model=source_policy['model'], request_id=source_policy['request_id'],
                source_hashes=hashes, calls=[dict(id='S02-first-output',
                full_input_tokens_upper_bound=source_policy['input_tokens'],
                generation_tokens_upper_bound=source_policy['max_output_tokens'])])
    scopes = [dict(id=s, revision='unknown', max_tokens=None, spent_tokens=None,
                   reserved_tokens=None) for s in policy['required_scope_ids']]
    capability = dict(verified=source_policy['hard_capability_verified'],
                      input_bound_verified=False, output_limit_enforced=False,
                      reasoning_covered=False, provider=source_policy['provider'],
                      model=source_policy['model'], model_context_tokens=None,
                      max_generation_tokens=None)
    return dict(session='S02', package_hashes_match=True, execution_status='not_run',
                assessment=assess(plan, policy, scopes, capability))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--s02', action='store_true', required=True,
                        help='Assess the selected S02 package without calling a provider')
    parser.parse_args()
    print(json.dumps(s02_assessment(), ensure_ascii=False, indent=2))

"""Offline Q14-A review for receiver wire 2; never rewrites raw IDs or format.

Caller access/atomic groups are controlled fixtures, not production authorization.
The strict whole-trial quality scorer remains separate and unchanged.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from protocol import canonical, digest, strict_json
from project_review import clarification_records
from receiver_next import FORMAT, check_request, validate_response

VERSION = 'receiver-project-review-2'
CONTEXT = 'receiver-review-context-fixture-2'


def check_context(request, context):
    check_request(request)
    if (not isinstance(context, dict) or set(context) != {'format', 'request_id', 'projects', 'atomic_groups'}
            or context['format'] != CONTEXT or context['request_id'] != request['request_id']):
        raise ValueError('invalid wire-2 caller context')
    views = {v['binding']['project_id']: v for v in request['source_snapshot']['views']}
    if not isinstance(context['projects'], dict) or set(context['projects']) != set(views):
        raise ValueError('incomplete caller project context')
    for pid, view in views.items():
        local = context['projects'][pid]
        if (not isinstance(local, dict) or set(local) != {'review_access', 'current_binding'}
                or local['review_access'] is not True):
            raise ValueError('review access not granted')
        if canonical(local['current_binding']) != canonical(view['binding']):
            raise ValueError('stale source/state/access binding')
    groups, seen = context['atomic_groups'], set()
    if not isinstance(groups, list) or len(groups) > len(views):
        raise ValueError('invalid atomic groups')
    for group in groups:
        if (not isinstance(group, list) or not 2 <= len(group) <= len(views)
                or any(type(pid) is not str or pid not in views for pid in group)
                or len(set(group)) != len(group) or seen.intersection(group)):
            raise ValueError('invalid/overlapping atomic group')
        seen.update(group)
    return views


def review_projects(request, raw, context):
    views = check_context(request, context)  # Access before parsing/exposing source-derived data.
    output = strict_json(raw, max_bytes=32768)
    if (not isinstance(output, dict) or set(output) != {'format', 'request_id', 'responses'}
            or output['format'] != FORMAT or output['request_id'] != request['request_id']
            or not isinstance(output['responses'], list) or len(output['responses']) > len(views)):
        raise ValueError('invalid shared wire-2 envelope')
    indexed = {}
    for row in output['responses']:
        if not isinstance(row, dict) or type(row.get('project_id')) is not str:
            raise ValueError('unknown project identity')
        pid = row['project_id']
        if (pid not in views or pid in indexed
                or row.get('package_digest') != views[pid]['binding']['package_digest']):
            raise ValueError('foreign/duplicate project or stale package')
        indexed[pid] = row
    results = {}
    for pid, view in views.items():
        item = dict(project_id=pid, package_digest=view['binding']['package_digest'],
                    status='missing_output', review=None, clarifications=[],
                    diagnostics=[dict(kind='missing_model_output', reason='selected project omitted')])
        row = indexed.get(pid)
        if row is not None:
            # Same wire/version/request/row. Only isolate the row for local validation.
            envelope = dict(format=FORMAT, request_id=request['request_id'], responses=[row])
            try:
                validate_response(request, canonical(envelope))
            except ValueError as error:
                item.update(status='invalid_project_output',
                            diagnostics=[dict(kind='technical_output_error', reason=str(error))])
            else:
                if row['status'] == 'abstain':
                    item.update(status='awaiting_context',
                                diagnostics=[dict(kind='model_abstention', reason='no review data supplied')])
                else:
                    pending = clarification_records(request, view)
                    item.update(status='needs_clarification' if pending else 'ready_for_review',
                                review=copy.deepcopy(row), clarifications=pending, diagnostics=[])
        results[pid] = item
    for group in context['atomic_groups']:
        waiting = [pid for pid in group if results[pid]['status'] != 'ready_for_review']
        if waiting:
            for pid in group:
                results[pid]['diagnostics'].append(dict(kind='atomic_group_waiting', project_ids=waiting))
                results[pid].update(status='blocked_atomic_group', review=None)
    items = list(results.values())
    all_ready = all(i['status'] == 'ready_for_review' for i in items)
    any_review = any(i['review'] is not None for i in items)
    return dict(format=VERSION, request_id=request['request_id'], context_sha256=digest(context),
        raw_sha256=hashlib.sha256(raw.encode()).hexdigest(), projects=items,
        status='ready_for_review' if all_ready else ('partial_review' if any_review else 'awaiting_resolution'),
        atomic_groups=copy.deepcopy(context['atomic_groups']), quality_scored=False,
        canonical_mutations=0, model_dispatches=0, paid_api_calls=0,
        execution_authorized=False, production_authorization=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--response', required=True, type=Path)
    parser.add_argument('--context', required=True, type=Path)
    args = parser.parse_args()
    result = review_projects(strict_json(args.request.read_text()), args.response.read_text(),
                             strict_json(args.context.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))

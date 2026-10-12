"""Q14-A offline project isolation and clarification descriptors; no execution.

Context and reply actors are controlled caller fixtures, not production IAM.
Old wire request and whole-output evaluator remain frozen.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from protocol import canonical, digest, strict_json
from receiver_contract import validate
from receiver_smoke import FORMAT, check_request

VERSION = 'receiver-project-review-1'
CONTEXT = 'receiver-review-context-fixture-1'


def check_context(request, context):
    check_request(request)
    if (not isinstance(context, dict) or set(context) != {'format', 'request_id', 'projects', 'atomic_groups'}
            or context['format'] != CONTEXT or context['request_id'] != request['request_id']):
        raise ValueError('invalid caller review context')
    views = {v['binding']['project_id']: v for v in request['views']}
    projects = context['projects']
    if not isinstance(projects, dict) or set(projects) != set(views):
        raise ValueError('incomplete caller project context')
    for pid, view in views.items():
        local = projects[pid]
        if (not isinstance(local, dict) or set(local) != {'review_access', 'current_binding'}
                or local['review_access'] is not True):
            raise ValueError('review access not granted')
        if canonical(local['current_binding']) != canonical(view['binding']):
            raise ValueError('stale source/state/access binding')
    groups = context['atomic_groups']
    if not isinstance(groups, list) or len(groups) > 2:
        raise ValueError('invalid atomic group count')
    seen = set()
    for group in groups:
        if (not isinstance(group, list) or not 2 <= len(group) <= len(views)
                or any(type(pid) is not str or pid not in views for pid in group)
                or len(set(group)) != len(group) or seen.intersection(group)):
            raise ValueError('invalid/overlapping atomic project group')
        seen.update(group)
    return views


def clarification_records(request, view):
    """Stable source-bound proposals; no actual UI delivery, persistence or approval."""
    records = []
    pid = view['binding']['project_id']
    for candidate in view['answer_candidates']:
        if candidate['status'] not in ('needs_clarification', 'needs_question_context', 'conflicting_answers'):
            continue
        presentations = view['selected_context']['question_presentations']
        qid = candidate['attributes'].get('question_id')
        choices = [p for p in presentations if not qid or p['question_id'] == qid]
        key = dict(version=VERSION, request_id=request['request_id'], project_id=pid,
                   package_digest=view['binding']['package_digest'], candidate=candidate,
                   presentations=choices)
        records.append(dict(clarification_id=digest(key), project_id=pid,
            message_id=candidate['message_id'], quote=candidate['quote'],
            status='needs_clarification', reason=candidate['status'],
            question_presentations=copy.deepcopy(choices),
            request_id=request['request_id'], package_digest=view['binding']['package_digest'],
            execution_authorized=False))
    return records


def review_projects(request, raw, context):
    views = check_context(request, context)  # Access before source-derived outputs.
    output = strict_json(raw, max_bytes=32768)
    if (not isinstance(output, dict) or set(output) != {'format', 'request_id', 'responses'}
            or output['format'] != FORMAT or output['request_id'] != request['request_id']
            or not isinstance(output['responses'], list) or len(output['responses']) > len(views)):
        raise ValueError('invalid shared receiver envelope')
    # Validate every identity before allowing any project to be reviewed.
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
        item = dict(project_id=pid, status='missing_output', review=None, clarifications=[],
                    diagnostics=[], package_digest=view['binding']['package_digest'])
        row = indexed.get(pid)
        if row is not None:
            envelope = dict(format=FORMAT, request_id=request['request_id'], responses=[row])
            try:
                validate(request, canonical(envelope))
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
                                review=copy.deepcopy(row), clarifications=pending)
        if item['status'] == 'missing_output':
            item['diagnostics'] = [dict(kind='missing_model_output', reason='selected project omitted')]
        results[pid] = item
    for group in context['atomic_groups']:
        waiting = [pid for pid in group if results[pid]['status'] != 'ready_for_review']
        if waiting:
            for pid in group:
                results[pid]['diagnostics'].append(dict(kind='atomic_group_waiting', project_ids=waiting))
                results[pid]['status'] = 'blocked_atomic_group'
                results[pid]['review'] = None
    items = list(results.values())
    all_ready = all(i['status'] == 'ready_for_review' for i in items)
    any_review = any(i['review'] is not None for i in items)
    return dict(format=VERSION, request_id=request['request_id'],
        context_sha256=digest(context), raw_sha256=hashlib.sha256(raw.encode()).hexdigest(),
        status='ready_for_review' if all_ready else ('partial_review' if any_review else 'awaiting_resolution'),
        projects=items, atomic_groups=copy.deepcopy(context['atomic_groups']),
        quality_scored=False, canonical_mutations=0, model_dispatches=0,
        paid_api_calls=0, execution_authorized=False, production_authorization=False)


def associate_reply(request, context, clarification_id, reply):
    """Explicit delayed human-fixture reply association; never approves/executes."""
    views = check_context(request, context)
    fields = {'clarification_id', 'project_id', 'question_id', 'question_revision',
              'option_id', 'source_message_id', 'source_revision', 'text', 'actor_type', 'source_sha256'}
    if not isinstance(reply, dict) or set(reply) != fields or len(canonical(reply).encode()) > 4096:
        raise ValueError('invalid clarification reply')
    source = {k: reply[k] for k in ('source_message_id', 'source_revision', 'text', 'actor_type')}
    if (reply['actor_type'] != 'human_owner' or type(reply['source_revision']) is not int
            or reply['source_revision'] < 1 or type(reply['source_message_id']) is not str
            or not reply['source_message_id'] or type(reply['text']) is not str or not reply['text']
            or reply['source_sha256'] != digest(source)):
        raise ValueError('invalid human-fixture reply source')
    pid = reply['project_id']
    if type(pid) is not str or pid not in views or reply['clarification_id'] != clarification_id:
        raise ValueError('foreign clarification reply')
    view = views[pid]
    pending = {p['clarification_id']: p for p in clarification_records(request, view)}
    if clarification_id not in pending:
        raise ValueError('unknown/stale clarification id')
    record = pending[clarification_id]
    presentations = record['question_presentations']
    if (type(reply['question_revision']) is not int or reply['question_revision'] < 1
            or type(reply['question_id']) is not str or type(reply['option_id']) is not str):
        raise ValueError('invalid question association type')
    found = [p for p in presentations if p['question_id'] == reply['question_id']
             and p['revision'] == reply['question_revision'] and reply['option_id'] in p['options']]
    if len(found) != 1:
        raise ValueError('stale/unknown question or option')
    current = view['fixture_state'].get('question')
    matches = current and current['question_id'] == reply['question_id']
    if matches and (current['option_revision'] != reply['question_revision'] or current['state'] != 'pending'):
        raise ValueError('question changed or already resolved')
    return dict(format='receiver-clarification-association-fixture-1',
        proposal_id=digest(dict(version=VERSION, request_id=request['request_id'], context_sha256=digest(context), reply=reply)),
        request_id=request['request_id'], context_sha256=digest(context), binding=copy.deepcopy(view['binding']),
        clarification_id=clarification_id, project_id=pid, source_sha256=reply['source_sha256'],
        source_message_id=reply['source_message_id'], source_revision=reply['source_revision'],
        question_id=reply['question_id'], question_revision=reply['question_revision'], option_id=reply['option_id'],
        status='pending_trusted_selection' if matches else 'needs_question_context',
        clarification_resolved=False, approved_real_decision=False, canonical_mutations=0,
        model_dispatches=0, execution_authorized=False, production_authorization=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--response', required=True, type=Path)
    parser.add_argument('--context', required=True, type=Path)
    args = parser.parse_args()
    result = review_projects(strict_json(args.request.read_text()), args.response.read_text(),
                             strict_json(args.context.read_text()))
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))

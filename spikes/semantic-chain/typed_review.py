"""Deterministic P0 review from selected, already typed source facts.

No text extraction, raw model repair, decision application, or provider dispatch.
Only the pinned wire-2 synthetic snapshot is supported; caller access is a fixture.
"""
import argparse
import copy
import json
from pathlib import Path

from protocol import canonical, digest, strict_json
from project_review_next import check_context, review_projects
from receiver_next import FORMAT, validate_response

VERSION = 'deterministic-typed-review-1'


def _row(view):
    question = view['fixture_state'].get('question')
    candidates = {c['message_id']: c for c in view['answer_candidates']}
    actions, evidence, seen = [], [], set()
    upload = False
    for record in view['preserved_records']:
        mid, kind, attributes = record['message_id'], record['kind'], record['attributes']
        if mid in seen:
            raise ValueError('multiple records per message unsupported')
        seen.add(mid)
        qid = None
        if kind == 'AnswerRecord':
            candidate = candidates.get(mid)
            if candidate is None or candidate['attributes'] != attributes:
                raise ValueError('answer candidate binding missing or changed')
            qid = attributes.get('question_id')  # Never use the latest question as a guess.
            status = candidate['status']
            if status == 'pending_trusted_selection':
                action = 'request_selection_confirmation'
            elif status in ('needs_clarification', 'needs_question_context', 'conflicting_answers'):
                action = 'request_clarification'
            elif status in ('stale_question_revision', 'duplicate_candidate', 'no_pending_question', 'non_human_answer'):
                action = 'preserve_history'
            else:
                raise ValueError('unsupported answer status')
        elif kind == 'ImplementationClaim':
            upload = upload or attributes.get('claim_type') == 'upload'
            action = 'request_target_verification' if attributes.get('claim_type') == 'upload' else 'preserve_history'
        elif kind == 'Evidence':
            evidence.append(copy.deepcopy(attributes))
            action = 'request_test_execution_permission' if attributes['result'] == 'not_run' else 'preserve_history'
        else:
            raise ValueError('unsupported typed record kind')
        actions.append(dict(type=action, message_id=mid, question_id=qid))
    return dict(project_id=view['binding']['project_id'], package_digest=view['binding']['package_digest'],
        status='ok', readback=dict(question_id=question['question_id'] if question else None,
            question_revision=question['option_revision'] if question else None,
            question_state=question['state'] if question else 'unknown',
            approved_real_decision=False, task_verified=False,
            upload_verification='reported_only' if upload else 'unknown',
            answer_states=[dict(message_id=c['message_id'], status=c['status']) for c in view['answer_candidates']],
            reported_test_results=evidence), next_actions=actions)


def build(request, context):
    views = check_context(request, context)  # Scope/current binding before returning any data.
    response = dict(format=FORMAT, request_id=request['request_id'],
                    responses=[_row(view) for view in views.values()])
    raw = canonical(response)
    validate_response(request, raw)
    review = review_projects(request, raw, context)
    return dict(format=VERSION, output_origin='deterministic_selected_typed_records',
        input_origin='selected source-bound model-reported records plus fixture state; not independently verified',
        request_id=request['request_id'], context_sha256=digest(context),
        source_snapshot_sha256=digest(request['source_snapshot']), response_value_sha256=digest(response),
        bindings=[copy.deepcopy(v['binding']) for v in views.values()],
        response=response, project_review=review, canonical_mutations=0,
        model_dispatches=0, paid_api_calls=0, raw_model_output_consumed=False,
        production_authorization=False, execution_authorized=False, usage=None,
        new_call_required_for_this_transform=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--context', required=True, type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = build(strict_json(args.request.read_text()), strict_json(args.context.read_text()))
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.out:
        with args.out.open('x') as stream:
            stream.write(text)
    else:
        print(text, end='')

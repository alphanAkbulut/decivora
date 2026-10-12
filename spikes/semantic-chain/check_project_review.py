"""Reproduce Q14-A saved synthetic reviews and delayed reply without dispatch."""
import copy
import hashlib
import json

from protocol import canonical
from project_review import VERSION, associate_reply, review_projects
from receiver_smoke import ROOT


def check():
    folder = ROOT / 'examples/project-review-smoke'
    request = json.loads((ROOT / 'examples/receiver-smoke/request.json').read_text())
    context = json.loads((folder / 'context.fixture.json').read_text())
    valid = (ROOT / 'examples/receiver-contract/valid-review.json').read_text()
    mixed = (folder / 'mixed-response.json').read_text()
    positive = review_projects(request, valid, context)
    mixed_result = review_projects(request, mixed, context)
    if [p['status'] for p in positive['projects']] != ['ready_for_review', 'needs_clarification']:
        raise ValueError('clarification example changed')
    if [p['status'] for p in mixed_result['projects']] != ['ready_for_review', 'invalid_project_output']:
        raise ValueError('mixed project isolation failed')
    pending = positive['projects'][1]['clarifications'][0]
    reply = json.loads((folder / 'delayed-reply.fixture.json').read_text())
    associated = associate_reply(request, context, pending['clarification_id'], reply)
    if associated['status'] != 'pending_trusted_selection' or associated['approved_real_decision'] is not False:
        raise ValueError('delayed reply incorrectly promoted')
    atomic_context = copy.deepcopy(context)
    atomic_context['atomic_groups'] = [[p['project_id'] for p in positive['projects']]]
    atomic = review_projects(request, valid, atomic_context)
    if any(p['review'] is not None for p in atomic['projects']):
        raise ValueError('atomic group split')
    raw = (ROOT / 'docs/quality/model-runs/receiver-001-response.txt').read_text()
    historical = review_projects(request, raw, context)
    if any(p['review'] is not None for p in historical['projects']):
        raise ValueError('first actual failed output salvaged')
    files = [folder / n for n in ('context.fixture.json', 'mixed-response.json', 'delayed-reply.fixture.json')]
    files += [ROOT / 'spikes/semantic-chain' / n for n in
              ('project_review.py', 'test_project_review.py', 'check_project_review.py')]
    return dict(status='passed_local_project_isolation_examples', version=VERSION,
        clarification_review=positive, mixed_review=mixed_result, delayed_reply=associated,
        atomic_review=atomic, first_actual_output_still_rejected=historical,
        file_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        model_quality='not_retested', human_gold=False, production_authorization=False,
        persistent_inbox='not_implemented; descriptors saved only in this offline report',
        host_capture_resume='not_tested', model_dispatches=0, paid_api_calls=0, canonical_mutations=0, usage=None)


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2, allow_nan=False))

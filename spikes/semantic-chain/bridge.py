"""P0 candidate-to-chain bridge. Trusted fixture receipts are not production IAM."""
from protocol import digest, validate, check_request


def propose(chain, request, response_text):
    validated = validate(request, response_text)
    state = chain.snapshot()
    question = state['question']
    answers = [r for r in validated['records'] if r['kind'] == 'AnswerRecord']
    if validated['status'] == 'abstain':
        return dict(status='needs_context', canonical_mutations=0)
    if len(answers) != 1 or not question or question['state'] != 'pending':
        return dict(status='unmatched_or_ambiguous', canonical_mutations=0)
    answer = answers[0]
    attrs = answer['attributes']
    if attrs.get('question_id') != question['question_id'] or (
        attrs.get('presentation_revision') != question['option_revision'] or
        attrs.get('option_id') not in question['options']):
        return dict(status='unmatched_or_stale', canonical_mutations=0)
    proposal = dict(status='pending_trusted_selection', project_id=request['source']['project_id'],
                    request_id=request['request_id'], source_sha256=request['source_sha256'],
                    source_session=request['source']['session_id'], message_id=answer['message_id'],
                    question_id=attrs['question_id'], option_revision=attrs['presentation_revision'],
                    option=attrs['option_id'], base_revision=state['revision'], canonical_mutations=0)
    proposal['proposal_digest'] = digest(proposal)
    return proposal


def apply_selection(chain, request, proposal, trusted_receipt, project_id):
    # Receipt must arrive separately from source text/model JSON, via a trusted fixture caller.
    check_request(request)
    unsigned = {k:v for k,v in proposal.items() if k != 'proposal_digest'}
    if proposal.get('status') != 'pending_trusted_selection' or digest(unsigned) != proposal.get('proposal_digest'):
        raise ValueError('proposal changed or unresolved')
    if project_id != proposal['project_id'] or request['request_id'] != proposal['request_id']:
        raise PermissionError('project or request mismatch')
    mid = proposal['message_id']
    messages = {m['message_id']:m for m in request['source']['messages']}
    if messages[mid]['actor_type'] != 'human_owner':
        raise PermissionError('assistant/agent text cannot approve')
    required = dict(project_id=project_id, source_sha256=proposal['source_sha256'],
                    message_id=mid, question_id=proposal['question_id'],
                    option_revision=proposal['option_revision'], option=proposal['option'],
                    base_revision=proposal['base_revision'])
    if trusted_receipt.get('authenticated') is not True or trusted_receipt.get('permission') != 'decision.approve':
        raise PermissionError('trusted selection missing')
    if any(trusted_receipt.get(k) != v for k,v in required.items()):
        raise PermissionError('selection receipt binding mismatch')
    payload = dict(question_id=proposal['question_id'], option_revision=proposal['option_revision'],
                   option=proposal['option'], source_session=proposal['source_session'])
    key = 'selection-' + proposal['proposal_digest']
    return chain.dispatch('answer', payload, 'human', proposal['base_revision'], key)


def collect_proposals(chain, request, response_text, project_id):
    """Read-only P0 collector for one fixture's current question, not production IAM.

    Validate the entire response before examining candidates. Keep every original
    record; provisional entity keys, source order and text never choose a winner.
    The caller's explicit project scope is a fixture check, not an ACL grant.
    """
    validated = validate(request, response_text)
    if project_id != request['source']['project_id']:
        raise PermissionError('collection project mismatch')
    state = chain.snapshot()
    question = state['question']
    messages = {m['message_id']: m for m in request['source']['messages']}
    entries = []
    for record in validated['records']:
        if record['kind'] != 'AnswerRecord':
            continue
        # A source-based ID does not depend on the model's provisional entity_key.
        identity = dict(request_id=request['request_id'], source_sha256=request['source_sha256'],
                        message_id=record['message_id'], start=record['start'], end=record['end'],
                        kind=record['kind'], attributes=record['attributes'])
        actor = messages[record['message_id']]['actor_type']
        attrs = record['attributes']
        entry = dict(candidate_id=digest(identity), candidate=record,
                     source_actor_type=actor, status='needs_clarification',
                     proposal=None, canonical_mutations=0)
        if not all(k in attrs for k in ('question_id', 'option_id', 'presentation_revision')):
            entry['status'] = 'needs_clarification'
        elif actor != 'human_owner':
            entry['status'] = 'non_human_answer'
        elif not question or question['state'] != 'pending':
            entry['status'] = 'no_pending_question'
        elif attrs['question_id'] != question['question_id']:
            entry['status'] = 'needs_question_context'
        elif attrs['presentation_revision'] < question['option_revision']:
            entry['status'] = 'stale_question_revision'
        elif attrs['presentation_revision'] > question['option_revision']:
            entry['status'] = 'needs_question_context'
        elif attrs['option_id'] not in question['options']:
            entry['status'] = 'needs_clarification'
        else:
            entry['status'] = 'pending_trusted_selection'
        entries.append(entry)

    # Aliased duplicates are visible but cannot become extra approval proposals.
    counts = {}
    for entry in entries:
        cid = entry['candidate_id']
        counts[cid] = counts.get(cid, 0) + 1
    eligible = [e for e in entries if e['status'] == 'pending_trusted_selection']
    conflicting = len({e['candidate']['attributes']['option_id'] for e in eligible}) > 1
    for entry in entries:
        if entry['status'] == 'pending_trusted_selection' and conflicting:
            entry['status'] = 'conflicting_answers'
        elif counts[entry['candidate_id']] > 1:
            entry['status'] = 'duplicate_candidate'
        if entry['status'] == 'pending_trusted_selection':
            attrs = entry['candidate']['attributes']
            proposal = dict(status='pending_trusted_selection', project_id=project_id,
                            request_id=request['request_id'], source_sha256=request['source_sha256'],
                            source_session=request['source']['session_id'],
                            message_id=entry['candidate']['message_id'], question_id=attrs['question_id'],
                            option_revision=attrs['presentation_revision'], option=attrs['option_id'],
                            base_revision=state['revision'], candidate_id=entry['candidate_id'],
                            canonical_mutations=0)
            proposal['proposal_digest'] = digest(proposal)
            entry['proposal'] = proposal
    entries.sort(key=lambda e: (e['candidate_id'], e['candidate']['entity_key']))
    return dict(status='needs_context' if validated['status'] == 'abstain' else (
                    'evaluated' if entries else 'no_answer_candidates'),
                request_id=request['request_id'], project_id=project_id,
                source_sha256=request['source_sha256'], base_revision=state['revision'],
                answer_candidates=entries, preserved_records=validated['records'],
                coverage=validated['coverage'], canonical_mutations=0)

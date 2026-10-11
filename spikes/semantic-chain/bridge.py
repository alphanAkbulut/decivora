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

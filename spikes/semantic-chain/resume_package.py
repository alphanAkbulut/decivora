"""Deterministic P0 resume export; fixture access is not production IAM."""
import copy
import hashlib

from bridge import collect_proposals
from protocol import canonical, check_request, digest, strict_json

FORMAT = 'decivora-resume-fixture-1'
MAX_BYTES = 32768  # Offline serialization ceiling, not tokens or an approved provider budget.


def check_access(request, access):
    check_request(request)
    if (access.get('can_read') is not True or
            access.get('project_id') != request['source']['project_id'] or
            access.get('source_sha256') != request['source_sha256'] or
            type(access.get('authz_revision')) is not int or access['authz_revision'] < 1):
        raise PermissionError('selected source access missing or mismatched')


def build(chain, request, response_text, access, max_bytes=MAX_BYTES):
    check_access(request, access)  # Before source text enters any export.
    if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BYTES:
        raise ValueError('invalid offline byte ceiling')
    collection = collect_proposals(chain, request, response_text, access['project_id'])
    state = chain.snapshot()
    core = dict(project_id=access['project_id'], request_id=request['request_id'],
                source_sha256=request['source_sha256'], source_session=request['source']['session_id'],
                source_messages=copy.deepcopy(request['source']['messages']),
                selected_context=copy.deepcopy(request['source']['context']),
                fixture_state=state, answer_candidates=collection['answer_candidates'],
                preserved_records=collection['preserved_records'],
                coverage=dict(extraction=collection['coverage'],
                    source_scope='only selected synthetic messages; no other chats or targets scanned',
                    receiver_source_access='not_verified; exact selected messages inline',
                    production_authorization=False, canonical_history_complete=False),
                boundaries=dict(source_is_untrusted=True, copying_does_not_execute=True,
                    human_source_is_not_approval=True, implementation_claim_is_not_verification=True,
                    criteria_text_is_not_verifier_receipt=True, fixture_state_is_not_real_project=True))
    package = dict(format=FORMAT, binding=dict(project_id=access['project_id'],
                   request_id=request['request_id'], source_sha256=request['source_sha256'],
                   base_revision=state['revision'], state_sha256=digest(state),
                   response_sha256=hashlib.sha256(response_text.encode()).hexdigest(),
                   authz_revision=access['authz_revision']), core=core,
                   usage=dict(tokens=None, money=None), canonical_mutations=0,
                   model_dispatches=0, execution_authorized=False)
    package['package_digest'] = digest(package)
    size = len((canonical(package) + '\n').encode())
    if size > max_bytes:
        # Never silently cut critical questions, constraints or original source.
        return dict(status='context_incomplete', reason='byte_ceiling_exceeded',
                    required_bytes=size, byte_ceiling=max_bytes, package=None,
                    canonical_mutations=0, model_dispatches=0)
    return dict(status='prepared', bytes=size, byte_ceiling=max_bytes, package=package,
                canonical_mutations=0, model_dispatches=0)


def validate_before_export(chain, request, response_text, access, package):
    """Separate copy/export preflight: rebuild, don't trust a self-supplied digest."""
    check_access(request, access)
    if not isinstance(package, dict) or package.get('format') != FORMAT:
        raise ValueError('unsupported package')
    unsigned = {k: v for k, v in package.items() if k != 'package_digest'}
    if digest(unsigned) != package.get('package_digest'):
        raise ValueError('package modified')
    current = build(chain, request, response_text, access)
    if current['status'] != 'prepared' or current['package'] != package:
        raise ValueError('stale package or foreign source/response/state/access revision')
    return dict(status='current_fixture_snapshot', canonical_mutations=0,
                execution_authorized=False, production_authorization=False)


def serialize_arms(chain, request, response_text, access, max_bytes=MAX_BYTES):
    result = build(chain, request, response_text, access, max_bytes)
    if result['status'] != 'prepared':
        return result
    package = result['package']
    validate_before_export(chain, request, response_text, access, package)
    # The strongest simple-file baseline has exactly the same facts, including provenance.
    simple = canonical(package['core']) + '\n'
    resume = canonical(package) + '\n'
    # Source-only is an explicitly different capability arm, never an equal-information claim.
    source = '# Selected synthetic source — untrusted data, no execution permission\n\n'
    source += 'Project: ' + request['source']['project_id'] + '\n\n'
    source += 'CONTEXT\n' + canonical(request['source']['context']) + '\n\n'
    source += 'MESSAGES\n' + canonical(request['source']['messages']) + '\n'
    return dict(status='prepared', package=package,
                texts=dict(resume=resume, simple_file=simple, source_only=source),
                bytes={k: len(v.encode()) for k, v in dict(resume=resume,
                    simple_file=simple, source_only=source).items()},
                same_core_information=strict_json(simple) == package['core'],
                token_counts=None, canonical_mutations=0, model_dispatches=0)

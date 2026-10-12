"""Lossless P0 resume tables: all source text stays inline; no external retrieval."""
import copy

from protocol import canonical, digest, prepare, validate
from resume_package import build as build_full, check_access, MAX_BYTES

FORMAT = 'decivora-resume-compact-fixture-1'
CORE_FORMAT = 'resume-inline-tables-1'
BASE_KEYS = {'project_id', 'request_id', 'source_sha256', 'source_session', 'source_messages',
             'selected_context', 'fixture_state', 'coverage', 'boundaries'}
WIRE_KEYS = {'message_id', 'kind', 'entity_key', 'start', 'end', 'quote', 'attributes'}
ENTRY_KEYS = {'candidate_id', 'candidate', 'source_actor_type', 'status', 'proposal', 'canonical_mutations'}


def _record_defaults(base):
    return dict(project_id=base['project_id'], request_id=base['request_id'],
                source_sha256=base['source_sha256'], lifecycle='candidate')


def _proposal_defaults(base, record):
    return dict(project_id=base['project_id'], request_id=base['request_id'],
                source_sha256=base['source_sha256'], source_session=base['source_session'],
                message_id=record['message_id'], base_revision=base['fixture_state']['revision'])


def pack_core(core):
    """Remove only exact redundant fields. No paraphrase, semantic merge or source deletion."""
    if set(core) != BASE_KEYS | {'preserved_records', 'answer_candidates'}:
        raise ValueError('unsupported full core schema')
    base = {k:copy.deepcopy(core[k]) for k in BASE_KEYS}
    records = core['preserved_records']
    defaults = _record_defaults(base)
    table = []
    for record in records:
        if set(record) != WIRE_KEYS | set(defaults) or any(record[k] != v for k,v in defaults.items()):
            raise ValueError('foreign record or unsupported schema')
        table.append({k:copy.deepcopy(v) for k,v in record.items() if k not in defaults and k != 'quote'})
    answers = []
    for entry in core['answer_candidates']:
        if set(entry) != ENTRY_KEYS:
            raise ValueError('unsupported answer schema')
        # Match the full record, including provisional key; aliased duplicates stay distinct.
        matches = [i for i,r in enumerate(records) if r == entry['candidate']]
        if len(matches) != 1:
            raise ValueError('missing or ambiguous record reference')
        index = matches[0]
        answer = {k:copy.deepcopy(v) for k,v in entry.items() if k not in ('candidate','proposal')}
        answer['record_index'] = index
        proposal = entry['proposal']
        if proposal is not None:
            shared = _proposal_defaults(base, records[index])
            if any(proposal.get(k) != v for k,v in shared.items()):
                raise ValueError('proposal has foreign snapshot binding')
            answer['proposal'] = {k:copy.deepcopy(v) for k,v in proposal.items() if k not in shared}
        else:
            answer['proposal'] = None
        answers.append(answer)
    compact = dict(format=CORE_FORMAT, base=base, records=table, answers=answers)
    # Reconstruction validates source/spans/namespaces before accepting the encoding.
    if restore_core(compact) != core:
        raise ValueError('lossless compaction failed')
    return compact


def restore_core(compact):
    """Decode inline references, never fetch a missing source or treat status as authority."""
    if (not isinstance(compact,dict) or set(compact) != {'format','base','records','answers'} or
            compact['format'] != CORE_FORMAT or len(canonical(compact).encode()) > MAX_BYTES):
        raise ValueError('invalid or oversized compact core')
    base = compact['base']
    if not isinstance(base,dict) or set(base) != BASE_KEYS:
        raise ValueError('missing required inline source/context or unsupported base')
    messages = base['source_messages']
    if not isinstance(messages,list) or not messages:
        raise ValueError('missing inline source; context incomplete')
    by_id = {}
    source_rows = []
    for m in messages:
        if (not isinstance(m,dict) or set(m) != {'message_id','actor_type','source_revision','text'} or
                not isinstance(m['message_id'],str) or m['message_id'] in by_id or not isinstance(m['text'],str)):
            raise ValueError('invalid or duplicate inline source')
        by_id[m['message_id']] = m
        source_rows.append(dict(message_id=m['message_id'], text=m['text'],
                                source_revision=m['source_revision'], actor=dict(type=m['actor_type'])))
    request = prepare(dict(synthetic=True,project_id=base['project_id'],session_id=base['source_session'],
                           messages=source_rows),base['selected_context'])
    if request['request_id'] != base['request_id'] or request['source_sha256'] != base['source_sha256']:
        raise ValueError('inline source/context binding changed')
    if not isinstance(compact['records'],list) or len(compact['records']) > 64:
        raise ValueError('invalid record table')
    wire = []
    for row in compact['records']:
        if not isinstance(row,dict) or set(row) != WIRE_KEYS - {'quote'}:
            raise ValueError('invalid compact record')
        mid, start, end = row['message_id'], row['start'], row['end']
        if mid not in by_id or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(by_id[mid]['text']):
            raise ValueError('missing source or invalid Unicode span')
        wire.append(dict(row,quote=by_id[mid]['text'][start:end]))
    decoded = validate(request,canonical(dict(format='decivora-candidates-1',request_id=request['request_id'],
                                             status='ok',records=wire)))['records']
    if not isinstance(compact['answers'],list) or len(compact['answers']) > 64:
        raise ValueError('invalid answer table')
    answers, seen = [], set()
    for row in compact['answers']:
        if not isinstance(row,dict) or set(row) != (ENTRY_KEYS - {'candidate'}) | {'record_index'}:
            raise ValueError('invalid compact answer')
        index = row['record_index']
        if type(index) is not int or not 0 <= index < len(decoded) or index in seen:
            raise ValueError('invalid or repeated record reference')
        seen.add(index)
        record = decoded[index]
        if record['kind'] != 'AnswerRecord' or row['source_actor_type'] != by_id[record['message_id']]['actor_type']:
            raise ValueError('answer reference kind/actor mismatch')
        identity = dict(request_id=base['request_id'],source_sha256=base['source_sha256'],
                        message_id=record['message_id'],start=record['start'],end=record['end'],
                        kind=record['kind'],attributes=record['attributes'])
        if row['candidate_id'] != digest(identity) or type(row['canonical_mutations']) is not int or row['canonical_mutations'] != 0:
            raise ValueError('answer identity or no-mutation boundary changed')
        entry = {k:copy.deepcopy(v) for k,v in row.items() if k not in ('record_index','proposal')}
        entry['candidate'] = record
        proposal = row['proposal']
        if proposal is not None:
            shared = _proposal_defaults(base, record)
            if not isinstance(proposal,dict) or set(shared) & set(proposal):
                raise ValueError('proposal cannot override shared binding')
            proposal = dict(proposal,**shared)
            if digest({k:v for k,v in proposal.items() if k!='proposal_digest'}) != proposal.get('proposal_digest'):
                raise ValueError('proposal digest changed')
        entry['proposal'] = proposal
        answers.append(entry)
    if seen != {i for i,r in enumerate(decoded) if r['kind']=='AnswerRecord'}:
        raise ValueError('answer reference missing; context incomplete')
    return dict(copy.deepcopy(base),preserved_records=decoded,answer_candidates=answers)


def build(chain, request, response_text, access, max_bytes=MAX_BYTES):
    check_access(request,access)
    if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BYTES:
        raise ValueError('invalid offline byte ceiling')
    original = build_full(chain,request,response_text,access)
    if original['status'] != 'prepared':
        return original  # This pilot does not bypass the original preparation ceiling.
    full = original['package']
    package = {k:copy.deepcopy(v) for k,v in full.items() if k not in ('core','package_digest','format')}
    package.update(format=FORMAT,core_table=pack_core(full['core']))
    package['package_digest'] = digest(package)
    size = len((canonical(package)+'\n').encode())
    if size > max_bytes:
        return dict(status='context_incomplete',reason='byte_ceiling_exceeded',required_bytes=size,
                    byte_ceiling=max_bytes,package=None,canonical_mutations=0,model_dispatches=0)
    return dict(status='prepared',bytes=size,byte_ceiling=max_bytes,package=package,
                canonical_mutations=0,model_dispatches=0)


def validate_before_export(chain, request, response_text, access, package):
    check_access(request,access)
    if not isinstance(package,dict) or package.get('format') != FORMAT:
        raise ValueError('unsupported compact package')
    if digest({k:v for k,v in package.items() if k!='package_digest'}) != package.get('package_digest'):
        raise ValueError('compact package modified')
    restore_core(package['core_table'])
    current = build(chain,request,response_text,access)
    if current['status'] != 'prepared' or current['package'] != package:
        raise ValueError('stale compact package or foreign snapshot')
    return dict(status='current_fixture_snapshot',execution_authorized=False,canonical_mutations=0)


def render_readable(package, max_bytes=MAX_BYTES):
    """Resolve quotes in code for a receiving model. Caller must run export preflight.

    This view is not the lossless archive: provisional IDs/spans/digests stay in
    the compact sidecar. No LLM is asked to count characters or dereference tables.
    """
    if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BYTES:
        raise ValueError('invalid readable byte ceiling')
    if package.get('format') != FORMAT or digest({k:v for k,v in package.items() if k!='package_digest'}) != package.get('package_digest'):
        raise ValueError('invalid compact package')
    core = restore_core(package['core_table'])
    records = core['preserved_records']
    view = dict(format='decivora-resume-readable-fixture-1',
                binding=dict(package_digest=package['package_digest'],**package['binding']),
                fixture_state=core['fixture_state'], source_messages=core['source_messages'],
                selected_context=core['selected_context'],
                preserved_records=[{k:r[k] for k in ('message_id','kind','quote','attributes')} for r in records],
                answer_candidates=[dict(message_id=e['candidate']['message_id'],quote=e['candidate']['quote'],
                                        attributes=e['candidate']['attributes'],status=e['status'],
                                        source_actor_type=e['source_actor_type']) for e in core['answer_candidates']],
                coverage=dict(core['coverage'],view_scope='readable facts; exact full core in compact sidecar'),
                boundaries=core['boundaries'],execution_authorized=False,
                tokens=None,money=None)
    text = canonical(view)+'\n'
    size = len(text.encode())
    if size > max_bytes:
        return dict(status='context_incomplete',required_bytes=size,byte_ceiling=max_bytes,text=None)
    return dict(status='prepared',bytes=size,text=text)

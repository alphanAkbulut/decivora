"""Validate source-anchored candidates and retrieve bounded exact lexical context.

No free-text inference is claimed; real provider dispatch remains disabled.
"""
from dataclasses import asdict
from packages.domain.source_event import ContractError, validate_source_event
from packages.storage.workspace import TYPES, integer


def validate_candidates(event, output):
    event=validate_source_event(asdict(event))
    if type(output) is not dict or set(output)!={'source_event_id','source_revision','candidates','coverage'}:
        raise ContractError('invalid_output','Explicit extraction envelope required.')
    if output['source_event_id']!=event.event_id or type(output['source_revision']) is not int or output['source_revision']!=event.source_revision:
        raise ContractError('stale_source','Extraction output is not bound to current source.')
    if output['coverage'] not in ('complete','partial','unknown') or type(output['candidates']) is not list or len(output['candidates'])>32:
        raise ContractError('invalid_output','Extraction coverage or candidate limit is invalid.')
    for candidate in output['candidates']:
        if type(candidate) is not dict or set(candidate)!={'type','quote','start','end'} or candidate['type'] not in TYPES:
            raise ContractError('invalid_candidate','Unsupported source candidate.')
        start=integer(candidate['start']);end=integer(candidate['end'])
        if end>len(event.text) or start>=end or type(candidate['quote']) is not str or event.text[start:end]!=candidate['quote']:
            raise ContractError('invalid_span','Candidate quote does not match source coordinates.')
    return dict(status='validated_draft',candidates=output['candidates'],coverage=output['coverage'],canonical_mutations=0)


def lexical_context(records, query, *, limit=5, character_budget=4096):
    integer(limit,1);integer(character_budget,1)
    if limit>20 or character_budget>16384 or type(records) is not list or len(records)>100:
        raise ContractError('context_limit','Retrieval exceeds development bounds.')
    if type(query) is not str or not 1<=len(query)<=256:
        raise ContractError('invalid_query','Bounded retrieval query required.')
    selected=[];used=0;matches=0
    for record in records:
        text=record['body']['title']+' '+record['body']['description']
        if query.casefold() not in text.casefold():continue
        matches+=1
        if len(selected)>=limit or used+len(text)>character_budget:continue
        selected.append(record);used+=len(text)
    return dict(records=selected,truncated=len(selected)<matches,coverage='bounded_lexical_only',model_dispatches=0)


def semantic_dispatch(*_,**__):
    raise ContractError('model_dispatch_disabled','Real semantic extraction requires a separate provider/data/budget grant.')

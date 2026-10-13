"""Deterministic typed-candidate comparison; semantic inference is a separate gate."""
import unicodedata

from packages.domain.source_event import ContractError


def normalized(text):
    if type(text) is not str or not 1<=len(text)<=8192:
        raise ContractError('invalid_text','Bounded candidate text is required.')
    return ' '.join(unicodedata.normalize('NFC',text).casefold().split())


def reconcile(candidate, existing):
    if type(candidate) is not dict or set(candidate)!={'type','title','description','source_ref','intent'}:
        raise ContractError('invalid_candidate','Source-bound typed candidate fields required.')
    from packages.domain.project_binding import identifier
    identifier(candidate['source_ref'])
    if candidate['intent'] not in ('proposed','reported','planned','rejected'):
        raise ContractError('invalid_candidate','Unsupported candidate intent.')
    title=normalized(candidate['title']);description=normalized(candidate['description'])
    if type(existing) is not list or len(existing)>100:
        raise ContractError('comparison_limit','Bounded existing-record list required.')
    matches=[]
    for record in existing:
        if record['body']['type']==candidate['type'] and normalized(record['body']['title'])==title:
            same=normalized(record['body']['description'])==description
            matches.append(dict(record_id=record['id'],relation='exact_duplicate' if same else 'possible_refinement',base_version=record['version']))
    return dict(recommendation='attach_source' if any(m['relation']=='exact_duplicate' for m in matches) else 'review_relationship' if matches else 'review_new',
        matches=matches,source_ref=candidate['source_ref'],rationale='Recorded exact text comparison; similarity is not approval.',
        counter_evidence='No semantic equivalence or conflict has been independently verified.',uncertainty='semantic_relation_unknown',
        canonical_mutations=0,model_dispatches=0)

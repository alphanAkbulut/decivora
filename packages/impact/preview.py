"""Bounded deterministic impact proposals. No approval, mutation or model inference."""
from collections import deque
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from .graph import rationale

TRIGGERS={'decision_superseded','decision_approved','requirement_revised','feature_cancelled','technology_changed'}
REACHABLE={'required_by','implements','depends_on','part_of','refines','conflicts_with'}


def _refs(expression,depth=0):
    if depth>16:raise ContractError('graph_limit','Rationale depth exceeds the local limit.')
    if type(expression) is not dict:return set()
    if set(expression)=={'ref','revision'}:return {identifier(expression['ref'])}
    if len(expression)==1 and next(iter(expression)) in ('any','all'):
        children=next(iter(expression.values()))
        if type(children) is list and len(children)<=64:
            return set().union(*(_refs(c,depth+1) for c in children))
    return set()


def preview(graph,trigger,records,facts_before,facts_after,*,max_nodes=100,max_edges=500):
    """All inputs are an explicit scoped snapshot, not extracted truth.

    Facts describe a hypothetical change at the supplied record revisions. A
    depends_on path can request review but never propagates obsolete on its own.
    """
    if type(trigger) is not dict or set(trigger)!={'record','version','kind'} or trigger['kind'] not in TRIGGERS:
        raise ContractError('invalid_trigger','Typed revision-bound trigger required.')
    changed=identifier(trigger['record'])
    if changed not in graph.nodes or type(trigger['version']) is not int or trigger['version']<1:
        raise ContractError('stale_trigger','Trigger record/version is unavailable.')
    if type(records) is not dict or set(records)!=set(graph.nodes):
        raise ContractError('invalid_snapshot','Record metadata must match the graph snapshot.')
    for rid,record in records.items():
        if type(record) is not dict or set(record)!={'version','type','required_when','historically_completed','replacement'}:
            raise ContractError('invalid_snapshot','Explicit bounded impact metadata required.')
        if type(record['version']) is not int or record['version']<1 or type(record['historically_completed']) is not bool:
            raise ContractError('invalid_snapshot','Record revision/completion metadata invalid.')
        _refs(record['required_when'])
        if record['replacement'] is not None:
            if identifier(record['replacement']) not in records:raise ContractError('invalid_snapshot','Replacement outside selected snapshot.')
    if records[changed]['version']!=trigger['version']:raise ContractError('stale_trigger','Trigger revision changed.')
    for facts in (facts_before,facts_after):
        if type(facts) is not dict or len(facts)>len(records):raise ContractError('invalid_facts','Bounded facts required.')
        for rid,fact in facts.items():
            if rid not in records or type(fact) is not dict or set(fact)!={'revision','valid'}:
                raise ContractError('invalid_facts','Facts must reference this snapshot.')
            if type(fact['revision']) is not int or fact['revision']!=records[rid]['version'] or (fact['valid'] is not None and type(fact['valid']) is not bool):
                raise ContractError('stale_fact','Fact revision/value is invalid.')
    if any(type(n) is not int or n<1 for n in (max_nodes,max_edges)) or max_nodes>1000 or max_edges>5000:
        raise ContractError('impact_limit','Traversal exceeds the local preview ceiling.')
    # Expression references are typed rationale links, even without a redundant edge.
    incoming={rid:[] for rid in records}
    for origin,target,kind in sorted(graph.edges):
        if kind in REACHABLE:incoming[target].append((origin,kind))
    for rid,record in sorted(records.items()):
        for ref in sorted(_refs(record['required_when'])):
            if ref in incoming:incoming[ref].append((rid,'justification'))
    incoming={rid:sorted(set(edges)) for rid,edges in incoming.items()}
    pending=deque([(changed,[])]);visited=[];seen=set();paths={};edges_seen=0;frontier=[]
    while pending:
        rid,path=pending.popleft()
        if rid in seen:continue
        if len(visited)>=max_nodes:
            frontier=[rid]+[r for r,_ in pending if r not in seen];break
        seen.add(rid);visited.append(rid);paths[rid]=path
        links=incoming[rid]
        if edges_seen+len(links)>max_edges:
            frontier=[r for r,_ in links if r not in seen]+[r for r,_ in pending if r not in seen]
            # The unexpanded node is itself part of the remaining work.
            frontier.append(rid);break
        for origin,kind in links:
            edges_seen+=1
            if origin not in seen:pending.append((origin,path+[dict(origin=origin,target=rid,kind=kind)]))
    complete=graph.complete and not frontier
    proposals=[]
    # Unlinked/missing-rationale tasks remain visible as review, never obsolete.
    candidates=sorted(r for r in records if r!=changed and (r in seen or records[r]['required_when'] is None))
    omitted=candidates[max_nodes:];candidates=candidates[:max_nodes]
    if omitted:frontier.extend(omitted);complete=False
    for rid in candidates:
        record=records[rid];expression=record['required_when']
        before=rationale(expression,facts_before);after=rationale(expression,facts_after)
        action='review';reason='Unknown or incomplete rationale requires review.'
        if complete and after is True:
            action='keep';reason='At least one complete recorded justification remains valid.'
        elif complete and before is True and after is False:
            if record['replacement'] is not None:
                action='update';reason='Recorded replacement requires separate scope review.'
            elif type(expression) is dict and set(expression)=={'any'}:
                action='obsolete_candidate';reason='All alternatives in the recorded rationale became false.'
            else:
                action='update';reason='A required condition became false; scope must be reviewed.'
        if record['historically_completed']:
            action='review';reason='Historical completion is preserved; current applicability is separate.'
        if rid not in seen:reason='No known trigger path; missing rationale is not evidence of obsolescence.'
        refs=_refs(expression)
        proposals.append(dict(record=rid,record_version=record['version'],action=action,reason=reason,
            reason_path=paths.get(rid,[]),before=before,after=after,
            counter_evidence=sorted(ref for ref in refs if facts_after.get(ref,{}).get('valid') is True),
            preserve_historical_completion=record['historically_completed'],requires_approval=True))
    return dict(trigger=dict(trigger),knowledge_revision=graph.revision,coverage='complete_snapshot' if complete else 'incomplete',
        visited=visited,frontier=sorted(set(frontier)),source_coverage='complete' if graph.complete else 'incomplete',
        edges_examined=edges_seen,proposals=proposals,canonical_mutations=0,model_dispatches=0,
        semantic_interpretation=False,application_status='preview_only')

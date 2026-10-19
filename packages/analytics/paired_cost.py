"""Paired cost comparison, preserving unknown usage and quality regressions."""
from packages.domain.source_event import ContractError

def compare(rows):
    if type(rows) is not list or not rows or len(rows)>2000:raise ContractError('invalid_comparison','One to 2000 paired measurements required.')
    fields={'case_id','arm','cost_microusd','quality_passed','input_tokens','output_tokens','model','price_snapshot_id'};cases={}
    for row in rows:
        if type(row) is not dict or set(row)!=fields or row['arm'] not in ('baseline','candidate'):raise ContractError('invalid_comparison','Exact paired measurement fields required.')
        for field in ('case_id','model','price_snapshot_id'):
            if type(row[field]) is not str or not row[field].strip() or len(row[field])>128:raise ContractError('invalid_comparison','Bounded source/model/price references required.')
        for field in ('cost_microusd','input_tokens','output_tokens'):
            value=row[field]
            if value is not None and (type(value) is not int or not 0<=value<=10**12):raise ContractError('invalid_comparison','Nonnegative bounded integer measurement or null required.')
        if type(row['quality_passed']) not in (bool,type(None)):raise ContractError('invalid_comparison','Independent quality result or null required.')
        case=cases.setdefault(row['case_id'],{})
        if row['arm'] in case:raise ContractError('invalid_comparison','Duplicate case and arm.')
        case[row['arm']]=dict(row)
    if any(set(case)!= {'baseline','candidate'} for case in cases.values()):raise ContractError('unpaired_comparison','Every case needs both arms; do not silently drop failures.')
    unknown=any(r['cost_microusd'] is None for r in rows)
    totals={arm:None if unknown else sum(c[arm]['cost_microusd'] for c in cases.values()) for arm in ('baseline','candidate')}
    regressions=[key for key,c in cases.items() if c['baseline']['quality_passed'] is True and c['candidate']['quality_passed'] is False]
    quality_equal=all(c['baseline']['quality_passed'] is True and c['candidate']['quality_passed'] is True for c in cases.values())
    comparable=not unknown and quality_equal
    return dict(pairs=len(cases),cost_microusd=totals,quality_regressions=sorted(regressions),quality_gate='passed' if quality_equal else 'not_established',savings_microusd=totals['baseline']-totals['candidate'] if comparable else None,savings_percent=(100*(totals['baseline']-totals['candidate'])/totals['baseline']) if comparable and totals['baseline'] else None,model_calls=0,invoice_verified=False,quality_labels_verified=False,note='Supplied independent labels and price references are inputs, not verified human gold or invoice evidence.')

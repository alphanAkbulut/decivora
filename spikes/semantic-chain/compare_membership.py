"""Same-source lexical versus saved-model development diagnostic; no new inference.

Only shared message/kind/span fields are compared. Attributes/domain/latency/cost
remain outside this comparison. Unsupported baseline kinds remain explicit.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from anchors import anchor, prepare_quotes
from membership_batch import read
from membership_typed import derive_typed
from candidate_eval import evaluate_candidates
from protocol import canonical, strict_json, validate

ROOT = Path(__file__).resolve().parents[2]


def compare(*, requests_path=ROOT/'examples/membership-smoke/requests.json',
            response_path=ROOT/'docs/quality/model-runs/membership-002-response.txt',
            rubrics_path=ROOT/'examples/membership-smoke/candidate-rubrics.json'):
    requests = strict_json(read(requests_path))
    by_id = {r['request_id']:r for r in requests}
    imported = derive_typed(requests, read(response_path))
    if imported['status'] != 'source_validated':
        raise ValueError('incomplete saved model outputs; comparison unavailable')
    responses = {x['request_id']:x['response'] for x in imported['derived']}
    sources = [dict(project_id=r['source']['project_id'],session_id=r['source']['session_id'],
        context=r['source']['context'],messages=[dict(message_id=m['message_id'],text=m['text'],
        source_revision=m['source_revision'],actor=dict(type=m['actor_type']))
        for m in r['source']['messages']]) for r in requests]
    spec = importlib.util.spec_from_file_location('comparison_scorer', ROOT/'scripts/evaluate_corpus.py')
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    lexical_predictions = scorer.lexical(sources)  # Source only; no rubric read yet.
    model_predictions = [{k:row[k] for k in ('project_id','message_id','kind','start','end','quote')}
        for rid,response in responses.items()
        for row in validate(by_id[rid],canonical(response))['records']]
    rubrics = strict_json(read(rubrics_path))
    if not isinstance(rubrics,list) or len(rubrics) != len(requests):
        raise ValueError('one independently bound rubric per request required')
    seen, oracles, review_statuses = set(), [], []
    for rubric in rubrics:
        rid = rubric.get('request_id') if isinstance(rubric,dict) else None
        if not isinstance(rid,str) or rid not in by_id or rid in seen:
            raise ValueError('foreign/duplicate comparison rubric')
        seen.add(rid)
        request = by_id[rid]
        # Validate independent expectations against original source and contract.
        evaluate_candidates(request, responses[rid], rubric)
        review_statuses.append(rubric['review_status'])
        packet = prepare_quotes(request)
        expected = anchor(request, canonical(dict(format=packet['format'],
            request_id=rid,contract_id=packet['contract_id'],status='ok',
            records=[dict(row,entity_key='expected-'+str(i)) for i,row in enumerate(rubric['expected'])])))
        items = [dict(message_id=row['message_id'],records=[dict(kind=row['kind'],
            source_span=dict(start=row['start'],end=row['end']))]) for row in expected['response']['records']]
        oracles.append(dict(project_id=request['source']['project_id'],items=items))
    if any(response['status'] == 'abstain' for response in responses.values()):
        model_status = 'incomplete_abstained'
    else:
        model_status = 'scored_development_only'
    return dict(kind='same_source_membership_comparison',date='2026-10-12',
        status='development_diagnostic_not_release_or_native_benchmark',
        origin_run='MEMBERSHIP-002' if imported['typed_raw_sha256'] ==
            'e3941c35f39cdf4117bec100e01249a6eb3ec23b82b263e9998d8371ffc862da' else None,
        response_origin='known_saved_UI_capture' if imported['typed_raw_sha256'] ==
            'e3941c35f39cdf4117bec100e01249a6eb3ec23b82b263e9998d8371ffc862da' else 'caller_imported_unverified',
        requests=len(requests),source_messages=sum(len(s['messages']) for s in sources),
        request_ids=sorted(by_id),review_statuses=review_statuses,human_gold=False,
        holdout='same_reused_development_messages_not_sealed',
        shared_fields=['project_id','message_id','kind','start','end'],
        predictions=dict(lexical=lexical_predictions,saved_model=model_predictions),
        methods=dict(lexical=dict(status='scored_development_only',
            score=scorer.score(sources,lexical_predictions,oracles),model_dispatches=0),
            saved_model=dict(status=model_status,score=scorer.score(sources,model_predictions,oracles),
                new_model_dispatches=0,actual_model_identity=None,usage=None)),
        capability_differences=dict(lexical_mapped_kinds=['Decision','Task','Idea','ImplementationClaim'],
            lexical_missing_candidate_kinds=['AnswerRecord','Evidence'],
            lexical_claim_actor='assistant only; human upload report not supported by this rule',
            lexical_context_use='context available in shared source; existing rules ignore it',
            semantic_attributes_scored=False),
        input_sha256={label:hashlib.sha256(Path(p).read_bytes()).hexdigest()
            for label,p in [('requests',requests_path),('response',response_path),('rubrics',rubrics_path)]},
        component_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (ROOT/'scripts/evaluate_corpus.py',ROOT/'spikes/spike-0/spike0/extract.py')},
        new_model_dispatches=0,paid_api_requests=0,canonical_mutations=0,
        native_comparison='not_run',latency_comparison='not_measured',cost_comparison='unknown',
        limitations=['Baseline lacks AnswerRecord/Evidence; this is an explicit capability gap, not a general semantic ranking',
            'Saved model output reused after v1 diagnosis; no independent fresh replicate',
            'Attributes, authority, graph, verification and human correction burden not compared',
            'No native tool output, paired inference latency or measured token/cost benefit'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    result = compare()
    body = json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if args.out:
        with args.out.open('x',encoding='utf-8') as stream:
            stream.write(body)
    else:
        print(body,end='')

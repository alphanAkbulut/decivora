"""Prepare source-only requests or evaluate imported responses. Never call a provider."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from protocol import prepare, strict_json, validate

ROOT = Path(__file__).resolve().parents[2]


def requests():
    result = []
    for path in sorted((ROOT/'examples/corpus/sources').glob('*.json')):
        source = strict_json(path.read_text())
        # Only explicitly listed prior source context, not oracle expectations/auth metadata.
        initial = source.get('initial_state', {})
        context = {k:initial[k] for k in ('knowledge_revision', 'question_presentations') if k in initial}
        result.append(prepare(source, context))
    return result


def evaluate(responses):
    # All candidates validate first; oracle is loaded afterwards and never sent to extraction.
    prepared = requests()
    by_id = {}
    for response in responses:
        key = response['request_id']
        if key in by_id: raise ValueError('duplicate response request')
        by_id[key] = response
    ids = {r['request_id'] for r in prepared}
    if set(by_id) - ids: raise ValueError('foreign/stale request response')
    rows, missing, abstained = [], [], []
    for request in prepared:
        rid = request['request_id']
        if rid not in by_id:
            missing.append(rid)
            continue
        output = validate(request, json.dumps(by_id[rid], ensure_ascii=False))
        if output['status'] == 'abstain': abstained.append(rid)
        for record in output['records']:
            rows.append({k:record[k] for k in ('project_id','message_id','kind','start','end','quote')})
    path = ROOT/'scripts/evaluate_corpus.py'
    spec = importlib.util.spec_from_file_location('independent_scorer',path)
    scorer = importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer)
    corpus = ROOT/'examples/corpus'
    sources = [strict_json(p.read_text()) for p in sorted((corpus/'sources').glob('*.json'))]
    oracles = [strict_json(p.read_text()) for p in sorted((corpus/'oracles').glob('*.json'))]
    return dict(kind='imported_model_response_evaluation',
                status='incomplete' if missing or abstained else 'measured_pending_human_and_domain_review',
                requests=len(prepared), received=len(by_id), missing=missing, abstained=abstained,
                score=scorer.score(sources,rows,oracles), canonical_mutations=0,
                automatic_model_dispatch=False, provider=None, model=None, usage=None,
                oracle_status='ai_authored_pending_human_review', holdout='reserved_not_sealed',
                manifest_sha256=hashlib.sha256((corpus/'manifest.json').read_bytes()).hexdigest())


def read_responses(path):
    if path.stat().st_size > 6*131072:
        raise ValueError('response file exceeds batch ceiling')
    text=path.read_text()
    try:
        value=strict_json(text,max_bytes=6*131072)
        rows=value if isinstance(value,list) else [value]
    except json.JSONDecodeError:
        rows=[strict_json(line) for line in text.splitlines() if line.strip()]
    if any(not isinstance(row,dict) for row in rows):
        raise ValueError('response objects required')
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'evaluate'])
    parser.add_argument('--responses', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        payload = '\n'.join(json.dumps(r,ensure_ascii=False) for r in requests()) + '\n'
    else:
        if not args.responses: parser.error('--responses is required')
        responses = read_responses(args.responses)
        payload = json.dumps(evaluate(responses),ensure_ascii=False,indent=2)+'\n'
    if args.out:
        # Never overwrite an existing user/provider evidence file.
        with args.out.open('x',encoding='utf-8') as stream: stream.write(payload)
    else: print(payload, end='')

#!/usr/bin/env python3
"""Source-only lexical baseline and independent one-to-one draft-oracle scorer."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def metric(tp, fp, fn):
    return dict(tp=tp,fp=fp,fn=fn,
                precision=tp/(tp+fp) if tp+fp else None,
                recall=tp/(tp+fn) if tp+fn else None)


def score(sources, predictions, oracles):
    inputs={(s['project_id'],m['message_id']):m['text'] for s in sources for m in s['messages']}
    gold=Counter()
    for oracle in oracles:
        for item in oracle['items']:
            for record in item['records']:
                span=record['source_span']
                gold[(oracle['project_id'],item['message_id'],record['kind'],span['start'],span['end'])]+=1
    actual=Counter()
    for row in predictions:
        key=(row['project_id'],row['message_id'])
        if key not in inputs:
            raise ValueError('prediction outside source/project scope')
        start,end=row['start'],row['end']
        if type(start) is not int or type(end) is not int or not 0<=start<end<=len(inputs[key]):
            raise ValueError('invalid prediction span')
        if row['quote'] != inputs[key][start:end]:
            raise ValueError('prediction quote differs from source span')
        actual[key+(row['kind'],start,end)]+=1
    common=gold&actual
    strict=metric(sum(common.values()),sum((actual-gold).values()),sum((gold-actual).values()))
    def kinds(counter):
        out=Counter()
        for k,n in counter.items():out[k[:3]]+=n
        return out
    g,a=kinds(gold),kinds(actual);c=g&a
    coarse=metric(sum(c.values()),sum((a-g).values()),sum((g-a).values()))
    return dict(strict_span=strict,message_kind_only=coarse,
                critical_domain_gate='incomplete',
                not_scored=['entity identity','attributes','relations','authority','impact','state','target/AC correctness'])


def lexical(sources):
    """Only source messages enter extraction; no oracle/expected state is passed."""
    path=ROOT/'spikes/spike-0/spike0/extract.py'
    spec=importlib.util.spec_from_file_location('fixture_lexical',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    kinds={'decision':'Decision','instruction':'Task','idea':'Idea',
           'incomplete':'Task','impl_claim':'ImplementationClaim'}
    rows=[]
    for source in sources:
        if 'items' in source or 'expected' in source:
            raise ValueError('oracle cannot be extractor input')
        for message in source['messages']:
            role='user' if message['actor']['type']=='human_owner' else 'assistant'
            for record in module.extract(role,message['text']):
                start,end=record['start'],record['end']
                rows.append(dict(project_id=source['project_id'],message_id=message['message_id'],
                  kind=kinds[record['type']],start=start,end=end,quote=message['text'][start:end]))
    return rows


def run():
    corpus=ROOT/'examples/corpus'
    manifest=json.loads((corpus/'manifest.json').read_text())
    sources=[json.loads(p.read_text()) for p in sorted((corpus/'sources').glob('*.json'))]
    predictions=lexical(sources)  # Produced before answer keys are loaded.
    oracles=[json.loads(p.read_text()) for p in sorted((corpus/'oracles').glob('*.json'))]
    return dict(kind='lexical_baseline_against_draft_oracle',status='measured_not_release_pass',
        dataset_manifest_sha256=hashlib.sha256((corpus/'manifest.json').read_bytes()).hexdigest(),
        extractor_sha256=hashlib.sha256((ROOT/'spikes/spike-0/spike0/extract.py').read_bytes()).hexdigest(),
        scorer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        oracle_status='ai_authored_pending_human_review',holdout_status='reserved_not_sealed',
        model_dispatches=0,additional_paid_model_dispatches=0,semantic_llm_test='not_run',
        predictions_count=len(predictions),score=score(sources,predictions,oracles),
        predictions=predictions)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    result=run()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='predictions'},ensure_ascii=False,indent=2))

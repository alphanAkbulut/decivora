"""Read-only feasibility probe for the recorded S02-002 output; no inference or writes.

The in-memory derivative is diagnostic, not an approved/imported model result.
Run from the repository; stdout may be saved as a separate probe evidence record.
"""
import copy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'spikes/semantic-chain'))
from protocol import strict_json, validate, check_request

def exact_anchor(text,quote):
    if not isinstance(quote,str) or not quote: return None
    first=text.find(quote)
    if first<0 or text.find(quote,first+1)>=0: return None
    return first,first+len(quote)

cases=[('abc','b',(1,2)),('x x','x',None),('aaaa','aa',None),('abc','d',None),('abc','',None),('🙂 Türkçe.','Türkçe.',(2,9)),('é','e\u0301',None)]
for text,quote,expected in cases:
    assert exact_anchor(text,quote)==expected,(text,quote)
reqpath=ROOT/'examples/model-smoke/s02-request.json'
rawpath=ROOT/'docs/quality/model-runs/s02-002-response.txt'
req=json.loads(reqpath.read_text());check_request(req)
raw=rawpath.read_text();original=strict_json(raw)
try: validate(req,raw)
except ValueError as exc: original_error=str(exc)
else: raise AssertionError('Original unexpectedly valid')
messages={m['message_id']:m['text'] for m in req['source']['messages']}
derived=copy.deepcopy(original);anchors=[]
for record in derived['records']:
    match=exact_anchor(messages[record['message_id']],record['quote'])
    assert match is not None
    anchors.append(dict(message_id=record['message_id'],start=match[0],end=match[1]))
    record['start'],record['end']=match
result=validate(req,json.dumps(derived,ensure_ascii=False))
assert len(result['records'])==11 and result['canonical_mutations']==0
assert strict_json(raw)==original
report=dict(schema_version=1,kind='offline_source_anchor_feasibility',date='2026-10-11',source_attempt='S02-002',scope='Diagnostic probe; no production adapter or new inference',request_id=req['request_id'],request_sha256=hashlib.sha256(reqpath.read_bytes()).hexdigest(),raw_response_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest(),probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_validation='rejected',original_error=original_error,original_unchanged=True,unique_exact_quote_matches=len(anchors),derived_validation='passed',derived_records=len(result['records']),derived_sha256=hashlib.sha256(json.dumps(derived,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),derived_canonical_mutations=0,new_model_calls=0,oracle_used=False,semantic_scoring='not_run',chain='not_run',edge_checks=dict(count=len(cases),passed=True,cases=['unique substring','repeated quote','overlapping repetitions','missing quote','empty quote','Unicode codepoints','no automatic Unicode normalization']),anchors=anchors,limitations=['n=1 already observed development output; not independent holdout','Derived validation pass is not original model contract success','No semantic correctness, cross-message identity, authority or production proof','Missing/ambiguous quote is rejected, not automatically repaired','No reusable production adapter delivered'])
print(json.dumps(report,ensure_ascii=False,indent=2))

"""Reproduce preparation and scripted scorer checks, not a model trial."""
import copy
import hashlib
import json

from protocol import canonical
from receiver_next import FORMAT, prepare, evaluate
from receiver_smoke import ROOT


def check():
    folder = ROOT / 'examples/receiver-next-smoke'
    request = prepare()
    if request != json.loads((folder / 'request.json').read_text()):
        raise ValueError('saved next request differs')
    if request['prompt'].encode() != (folder / 'prompt.txt').read_bytes():
        raise ValueError('saved next prompt differs')
    manifest = json.loads((folder / 'manifest.json').read_text())
    for name, sha in manifest['file_sha256'].items():
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != sha:
            raise ValueError('new fixture file changed: ' + name)
    oracle = json.loads((folder / 'expected.json').read_text())
    # Explicit scripted positive: oracle copied to response only to test evaluator wiring.
    reply = dict(format=FORMAT, request_id=request['request_id'], responses=copy.deepcopy(oracle['responses']))
    positive = evaluate(request, canonical(reply), oracle)
    reply['responses'][1]['next_actions'] = []
    missing = evaluate(request, canonical(reply), oracle)
    if positive['status'] != 'passed_draft' or missing['status'] != 'failed_draft':
        raise ValueError('scripted evaluator harness failed')
    code = ['receiver_next.py', 'test_receiver_next.py', 'check_receiver_next.py']
    return dict(experiment_id='RECEIVER-002-PREPARATION', status='prepared_not_dispatched',
        request_id=request['request_id'], prompt_sha256=request['prompt_sha256'], prompt_bytes=request['prompt_bytes'],
        prior_prompt_bytes=7950, byte_delta=139, byte_delta_is_not_token_usage=True,
        schema_sha256=request['schema_sha256'], selected_messages=8, preserved_records=6,
        source_read_scope=['examples/receiver-smoke/request.json', 'examples/resume-compact-smoke/N01-readable.json',
                           'examples/resume-compact-smoke/N02-readable.json'],
        scripted_harness_positive=positive, scripted_missing_actions=missing,
        scripted_harness_is_not_model_quality=True, human_gold=False,
        file_sha256=manifest['file_sha256'],
        code_sha256={n: hashlib.sha256((ROOT / 'spikes/semantic-chain' / n).read_bytes()).hexdigest() for n in code},
        actual_model_submissions=0, actual_outputs=0, dispatch_authorized=False, paid_api_calls=0,
        automatic_retries=0, canonical_mutations=0, model_quality='not_run', provider_schema_acceptance='not_run',
        usage=None, cost=None, hard_token_cap_verified=False, hard_context_cap_verified=False)


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2, allow_nan=False))

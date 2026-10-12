"""Reproduce the offline contract examples without model/oracle scoring or writes."""
import hashlib
import json

from protocol import canonical, digest
from receiver_contract import GUARD_VERSION, schema_for, validate
from receiver_smoke import ROOT


def check():
    folder = ROOT / 'examples/receiver-contract'
    request = json.loads((ROOT / 'examples/receiver-smoke/request.json').read_text())
    valid = json.loads((folder / 'valid-review.json').read_text())
    positive = validate(request, canonical(valid))
    schema = schema_for(request)
    if schema != json.loads((folder / 'response.schema.json').read_text()):
        raise ValueError('saved schema drift')
    negatives = []
    for case in json.loads((folder / 'invalid-reviews.json').read_text()):
        try:
            validate(request, canonical(case['response']))
        except ValueError as error:
            if case['error_contains'] not in str(error):
                raise ValueError('wrong rejection for ' + case['case_id']) from error
            negatives.append(dict(case_id=case['case_id'], status='rejected', reason=str(error)))
        else:
            raise ValueError('invalid example accepted: ' + case['case_id'])
    frozen = {
        'examples/receiver-smoke/prompt.txt': 'a4a636ecd53aee80ea74ef21608e26cdb50cc65f1f1da434a9cf9294d2073b6b',
        'examples/receiver-smoke/expected.json': '6e8762caf6dddf0c900b84a87a37bfbea0f21b3e4984fc8771727a9cfbf0277a',
        'docs/quality/model-runs/receiver-001-response.txt': 'f17e134b68bec39cf7d5539cc812db7a87bd970a851aa30ecf2b43aaeaac4b03',
    }
    for path, expected in frozen.items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
            raise ValueError('frozen historical evidence changed: ' + path)
    raw = (ROOT / 'docs/quality/model-runs/receiver-001-response.txt').read_text()
    try:
        validate(request, raw)
    except ValueError:
        raw_status = 'still_rejected_unmodified'
    else:
        raise ValueError('first failed output unexpectedly accepted')
    files = [folder / p for p in ('response.schema.json', 'valid-review.json', 'invalid-reviews.json')]
    files += [ROOT / 'spikes/semantic-chain' / p for p in
              ('receiver_contract.py', 'test_receiver_contract.py', 'check_receiver_contract.py')]
    return dict(status='passed_local_contract_examples', guard_version=GUARD_VERSION,
        request_id=request['request_id'], schema_sha256=digest(schema), valid_review=positive,
        invalid_examples=negatives, frozen_sha256=frozen, first_actual_output=raw_status,
        file_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        schema_validator_scope='only generated keyword subset; not general standards conformance',
        provider_schema_acceptance='not_run', model_quality='not_retested', human_gold=False,
        model_dispatches=0, paid_api_calls=0, canonical_mutations=0, usage=None)


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2, allow_nan=False))

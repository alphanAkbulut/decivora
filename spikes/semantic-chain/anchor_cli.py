"""No-network CLI: prepare quote contract, derive candidates, score a separate rubric."""
import argparse
import json
from pathlib import Path
from anchors import anchor, prepare_quotes
from candidate_eval import evaluate_candidates
from protocol import strict_json


def read(path):
    with Path(path).open('rb') as stream:
        body = stream.read(131073)
    if len(body) > 131072:
        raise ValueError('input file outside byte bound')
    return body.decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'derive'])
    parser.add_argument('--request', required=True)
    parser.add_argument('--response')
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--rubric')
    parser.add_argument('--out')
    args = parser.parse_args()
    req = strict_json(read(args.request))
    if args.action == 'prepare':
        if args.response or args.legacy or args.rubric:
            parser.error('prepare does not accept response/legacy/rubric')
        result = prepare_quotes(req)
    else:
        if not args.response:
            parser.error('derive requires --response')
        result = anchor(req, read(args.response), legacy=args.legacy)
        if args.rubric:
            result['candidate_score'] = evaluate_candidates(req, result['response'],
                                                           strict_json(read(args.rubric)))
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if args.out:
        with Path(args.out).open('x', encoding='utf-8') as stream:
            stream.write(text)
    else:
        print(text, end='')


if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Read existing four-case receipts; no key reads, model calls or regrading."""
import argparse,hashlib,json
from pathlib import Path

def build(folder):
    folder=Path(folder);path=folder/'report.json';report=json.loads(path.read_text())
    if report['case_ids']!=['J01','J02','J03','J04'] or report['human_gold'] is not False:
        raise ValueError('Unexpected batch receipt.')
    cases=[]
    for case in report['cases']:
        turns=[]
        for turn in case['turns']:
            private=folder/(turn['message_id']+'.result.json')
            saved=json.loads(private.read_text())['result']
            if saved['status']!=turn['analysis_status']:raise ValueError('Receipt status mismatch.')
            public={k:turn.get(k) for k in ('message_id','source_sha256','context_sha256','payload_sha256','analysis_status','failure_code','latency_ms','findings','verdict','candidate_types','candidate_titles','status_claims','canonical_stages','done_guard_code','usage')}
            public['private_receipt_sha256']=hashlib.sha256(private.read_bytes()).hexdigest()
            turns.append(public)
        cases.append(dict(case_id=case['case_id'],verdict=case['verdict'],processed_turns=case['processed_turns'],planned_turns=case['planned_turns'],turns=turns,test_operator_actions=case['test_operator_actions'],questions=case['questions']))
    before=report['budget_before'];after=report['budget_after']
    return dict(format='decivora-dialogue-batch-public-1',date='2026-10-20',
        requested_model=report['model'],native_host_test=False,human_gold=False,
        grading='Predeclared AI-authored draft checks; inspect findings before product acceptance.',
        automatic_next_batch=False,cases=cases,not_run=report['not_run'],stopped=report['stopped'],
        dispatches=report['dispatches'],http_budget_slots_delta=None if before is None or after is None else after['http_attempts']-before['http_attempts'],
        local_committed_microusd_delta=None if before is None or after is None else after['committed_microusd']-before['committed_microusd'],
        invoice_verified=False,budget_before=before,budget_after=after,
        private_batch_report_sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);args=p.parse_args();print(json.dumps(build(args.folder),ensure_ascii=False,indent=2))
if __name__=='__main__':main()

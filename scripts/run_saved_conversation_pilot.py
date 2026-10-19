#!/usr/bin/env python3
"""Explicit one-off saved-source pilot; no host reads, automatic apply or retries.

The trusted operator must supply the separately approved real-data reference.
Offline preparation copies the selected DB; the original never receives grants.
Private packets/results/ledger/key remain outside the repository.
"""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.granted_extractors import GrantedResponsesFactory
from packages.capture.openai_transport import PilotTransport,fingerprint,micro_cost
from packages.capture.processing_queue import ConversationQueue
from packages.capture.responses_extractor import request_payload
from packages.privacy.secrets import ensure_safe,redact_text
from packages.storage.workspace import Workspace
from scripts.run_openai_pilot import private_json,KEY

DEFAULT=ROOT.parent/'decivora-local-data'/'saved-source-pilot-001'
POLICY=ROOT.parent/'decivora-local-data'/'openai-development-001'/'approved-root-policy.json'
LEDGER=POLICY.with_name('shared-budget.sqlite')
SOURCE=ROOT.parent/'decivora-test-data'/'workspace.sqlite'


def bounded_manifest(policy,payloads):
    """A finite exact whitelist bounds this batch below $0.25, within the old root.

    At the adopted tariff, each admitted payload reserves worst-case cache-write
    input and full output. No parallel retry or new hash can expand this whitelist.
    The durable root transport rejects repeat hashes and preserves prior spend.
    """
    if not 1<=len(payloads)<=6:raise ValueError('One to six approved sources required.')
    hashes=[];reserve=0
    for payload in payloads:
        if payload['model']!='gpt-6-luna' or payload['max_output_tokens']!=2000:
            raise ValueError('Only the separately approved model/output ceiling is allowed.')
        hashes.append(fingerprint(payload))
        reserve+=micro_cost(payload['model'],10000,2000,cache_write_tokens=10000)
    if len(set(hashes))!=len(hashes) or reserve>250000:
        raise ValueError('Exact batch would exceed the separately approved allowance.')
    if policy['max_input_tokens']!=10000 or policy['max_output_tokens']!=2000 or policy['expires_at']<=time.time():
        raise ValueError('The existing root limits/expiry must remain valid; no renewal here.')
    return dict(policy,payloads=hashes),reserve


def prepare(folder=DEFAULT,*,approval_ref,source_db=SOURCE,policy_file=POLICY):
    if type(approval_ref) is not str or not approval_ref.strip():raise ValueError('Separate real-data owner approval required.')
    folder=Path(folder);folder.mkdir(mode=0o700,parents=True,exist_ok=True)
    packet=folder/'prepared.json'
    if packet.exists():return json.loads(packet.read_text())
    db=folder/'pilot.sqlite'
    fd=os.open(db,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
    # SQLite online backup gives a consistent snapshot without modifying TEST.
    with sqlite3.connect(Path(source_db).resolve().as_uri()+'?mode=ro',uri=True) as src,sqlite3.connect(db) as dest:src.backup(dest)
    jobs=[];payloads=[]
    with Workspace(db,'local_ui_workspace') as core:
        owner=core.authority.issue_scope('local_owner');core.scope(owner,'personal',write=True,human=True)
        sources=ConversationService(core);stored=sources._rows('personal','conversation_imported')
        if len(stored)!=6:raise ValueError('Approval is only for the six already saved messages.')
        for source in stored:
            # Already-redacted source identities/provenance remain intact. Newly
            # detected secrets stop preparation; never send a mismatched old hash.
            if redact_text(source['text'])[0]!=source['text']:raise ValueError('Additional redaction required before preparation.')
            ensure_safe(source)
            prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
            payload=request_payload(source,model='gpt-6-luna',max_output_tokens=2000,dialogue_request=prepared['request'])
            ensure_safe(payload);payloads.append(payload)
            jobs.append(dict(source_id=source['id'],payload_sha256=fingerprint(payload),context_sha256=prepared['context_sha256']))
    manifest,reserve=bounded_manifest(json.loads(Path(policy_file).read_text()),payloads)
    result=dict(format='decivora-saved-source-pilot-1',approval_ref=approval_ref,manifest=manifest,jobs=jobs,
                worst_case_microusd=reserve,batch_ceiling_microusd=250000,automatic_retry=False,auto_apply=False)
    private_json(packet,result);return result


def run(folder=DEFAULT,*,key_file=KEY,ledger=LEDGER,post=None):
    folder=Path(folder);packet=json.loads((folder/'prepared.json').read_text())
    if packet['format']!='decivora-saved-source-pilot-1' or not packet['approval_ref']:raise ValueError('Explicit saved-source permission required.')
    result_file=folder/'result.json'
    if result_file.exists():return json.loads(result_file.read_text())
    with Workspace(folder/'pilot.sqlite','local_ui_workspace') as core:
        owner=core.authority.issue_scope('local_owner');sources=ConversationService(core);payloads=[]
        for job in packet['jobs']:
            source=sources._source('personal',job['source_id'])
            prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
            payload=request_payload(source,model='gpt-6-luna',max_output_tokens=2000,dialogue_request=prepared['request'])
            if fingerprint(payload)!=job['payload_sha256'] or prepared['context_sha256']!=job['context_sha256']:raise ValueError('Prepared source/context changed; no automatic approval.')
            payloads.append(payload)
        policy={k:v for k,v in packet['manifest'].items() if k!='payloads'}
        manifest,reserve=bounded_manifest(policy,payloads)
        if manifest!=packet['manifest'] or reserve!=packet['worst_case_microusd']:raise ValueError('Prepared bounds changed.')
        transport=PilotTransport(ledger,manifest=manifest,key_file=key_file,post=post)
        if transport.snapshot()['frozen']:raise ValueError('Uncertain root usage requires review.')
        core.create_budget(owner,'personal','saved_source_pilot',len(payloads)*12000)
        entries=[]
        for index,job in enumerate(packet['jobs']):
            grant=sources.authorize_analysis(owner,'personal',source_id=job['source_id'],key='saved_source_'+str(index),root_run='saved_source_pilot',reserved_tokens=12000,provider='OpenAI Responses configured transport',model='gpt-6-luna',max_output_tokens=2000,expires_at=manifest['expires_at'],reason=packet['approval_ref'],context_sha256=job['context_sha256'])
            entries.append((grant,transport))
        result=ConversationQueue(core).process(owner,'personal',extractor_factory=GrantedResponsesFactory(entries),limit=len(entries))
        result.update(shared_budget=transport.snapshot(),real_source_approval_ref=packet['approval_ref'],auto_apply=False,semantic_accuracy='requires_human_review',mvp_acceptance=False)
        private_json(result_file,result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--approval-ref');args=p.parse_args()
    if args.prepare==args.run:p.error('Choose exactly one operation.')
    if args.prepare:
        value=prepare(approval_ref=args.approval_ref)
        print(json.dumps(dict(prepared_sources=len(value['jobs']),worst_case_microusd=value['worst_case_microusd'],network_calls=0)))
    else:
        result=run();print(json.dumps(dict(attempted=result['attempted'],outcomes=[r['status'] for r in result['outcomes']],shared_budget=result['shared_budget'],auto_apply=False)))

if __name__=='__main__':
    try:main()
    except Exception:
        print('Saved-source pilot stopped; inspect private receipts. No automatic retry.',file=sys.stderr);raise SystemExit(1)

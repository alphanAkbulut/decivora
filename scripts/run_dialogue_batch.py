#!/usr/bin/env python3
"""One four-case synthetic batch; sequential snapshots, no retries or next batch.

Test-operator actions are scripted, isolated evaluation controls, not human gold.
Oracle labels and future messages never enter provider payloads.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from packages.storage.workspace import Workspace
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.dialogue_questions import DialogueQuestionService
from packages.capture.responses_extractor import ResponsesExtractor,request_payload
from packages.capture.openai_transport import PilotTransport,fingerprint
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.questions import QuestionService
from packages.domain.source_event import ContractError
from run_openai_pilot import private_json,KEY

DATA=ROOT.parent/'decivora-local-data';DEFAULT=DATA/'dialogue-batch-001'
POLICY=DATA/'openai-development-001/approved-root-policy.json'
LEDGER=DATA/'openai-development-001/shared-budget.sqlite'
CASE_IDS=('J01','J02','J03','J04')


def prepare(folder=DEFAULT,policy_path=POLICY):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    path=folder/'plan.json'
    if path.exists():return json.loads(path.read_text())
    source_path=ROOT/'examples/dialogue-journeys/sources.json'
    selected=json.loads(source_path.read_text())['cases'][:4]
    if tuple(c['id'] for c in selected)!=CASE_IDS:raise ValueError('First four case identities changed.')
    policy=json.loads(Path(policy_path).read_text())
    plan=dict(format='decivora-four-dialogue-batch-1',cases=selected,root_policy=policy,
        source_file_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        max_generation_calls=24,max_count_calls=24,model='gpt-6-luna',
        max_input_tokens=10000,max_output_tokens=2000,automatic_retry=False,
        scripted_test_operator=True,human_gold=False,automatic_next_batch=False)
    private_json(path,plan);return plan


def task_role(title):
    title=title.casefold()
    if any(x in title for x in ('geri yükle','restore','restoration')):return 'restore'
    if any(x in title for x in ('alma','yedekleme','backup')):return 'backup'
    return None


def checkpoint(case,step,result,roles):
    """Predeclared strict draft checks, not a semantic judge or host acceptance."""
    findings=[]
    if result['status']!='Ready for review':return ['analysis_failed']
    tasks=[c for c in result['candidates'] if c['type']=='Task']
    if case in ('J01','J02','J03') and step==1:
        expected=['restore','backup'] if case=='J03' else ['restore']
        got=[task_role(c['title']) for c in tasks]
        if sorted(str(x) for x in got)!=sorted(expected):findings.append('initial_task_scope_or_count_mismatch')
    elif tasks:findings.append('unexpected_new_task_candidate')
    expected_stage={('J01',4):'In Progress',('J01',6):'Done',('J02',5):'In Progress',('J03',5):'In Progress'}.get((case,step))
    changes=result.get('status_changes',[])
    if expected_stage:
        if len(changes)!=1 or changes[0]['stage']!=expected_stage or changes[0]['task_id']!=roles.get('restore'):findings.append('existing_task_stage_or_identity_mismatch')
    elif changes:findings.append('unexpected_status_claim')
    if case=='J04' and step in (1,2) and len(result.get('question_proposals',[]))!=1:findings.append('missing_or_ambiguous_question_draft')
    if case=='J04' and step==5 and len(result.get('answer_proposals',[]))!=1:findings.append('missing_or_ambiguous_delayed_answer')
    if case=='J04' and step!=5 and result.get('answer_proposals'):findings.append('unexpected_answer_proposal')
    return findings


def contract(core,owner,task,key):
    row=lambda rid:dict(id=rid,statement='Synthetic restore test independently reviewed',method='human_review',required=True,applicable=True,applicability_reason='')
    plan=core.plan(owner,'synthetic',key,[dict(op='acceptance_contract',task=task,task_version=1,base_contract=0,criteria=[row('AC1')],dod=[row('DOD1')],reason='Scripted test-operator scope; not inferred from model',acknowledged_changes=[])])
    core.apply(owner,plan,core.approve(owner,plan))


def run(folder=DEFAULT,*,ledger_path=LEDGER,key_file=KEY,post=None,progress=None):
    folder=Path(folder);plan=json.loads((folder/'plan.json').read_text())
    if tuple(c['id'] for c in plan['cases'])!=CASE_IDS or plan['max_generation_calls']!=24 or plan['automatic_next_batch'] is not False:raise ValueError('Only the explicitly prepared first four cases may run.')
    if (folder/'report.json').exists():return json.loads((folder/'report.json').read_text())
    # An interrupted batch requires review, never silent rerun/re-seeding.
    if list(folder.glob('J*.sqlite')):raise ValueError('Partial batch exists: inspect receipts before any further dispatch.')
    policy=plan['root_policy']
    if policy['expires_at']<=time.time():raise ValueError('Approval expired; no automatic renewal.')
    results=[];stop=None;before=None;after=None;dispatches=0
    for case in plan['cases']:
        if stop:break
        cid=case['id'];case_rows=[];roles={};actions=[];question_ids={}
        with Workspace(folder/(cid+'.sqlite'),'journey',owner='operator') as core:
            a=core.authority;a.replace_grant(a.issue_scope('operator'),'operator',kind='human',readable=frozenset({'synthetic'}),writable=frozenset({'synthetic'}),active=True,base_revision=1)
            owner=a.issue_scope('operator');core.create_project(owner,'synthetic','Synthetic dialogue '+cid)
            sources=ConversationService(core);review=DialogueReviewService(core)
            for step,message in enumerate(case['messages'],1):
                if dispatches>=24:stop='batch_request_limit';break
                source=sources._ingest(owner,'synthetic',text=message['text'],capture=dict(source_surface='synthetic_dialogue',id='batch_001',thread_id=cid,turn_id=message['id'],item_id=message['id'],observed_actor=message['role'],provider_version='authored-not-native',profile_ref='synthetic_batch_001'))
                prepared=review.prepare(owner,'synthetic',source_id=source['id'])
                payload=request_payload(source,model=plan['model'],max_output_tokens=2000,dialogue_request=prepared['request'])
                transport=PilotTransport(ledger_path,manifest=dict(policy,payloads=[fingerprint(payload)]),key_file=key_file,post=post)
                before=transport.snapshot() if before is None else before
                if transport.snapshot()['frozen']:stop='shared_budget_frozen';break
                stem=cid+'_m'+str(step)
                private_json(folder/(stem+'.request.json'),dict(payload=payload,source_id=source['id'],context_sha256=prepared['context_sha256']))
                core.create_budget(owner,'synthetic',stem,12000)
                extractor=ResponsesExtractor(transport,model=plan['model'],max_output_tokens=2000,authorized=True,grant_id=stem,dialogue_review=True)
                sources.authorize_analysis(owner,'synthetic',source_id=source['id'],key=stem,root_run=stem,reserved_tokens=12000,provider=extractor.provider,model=plan['model'],max_output_tokens=2000,expires_at=policy['expires_at'],reason='First four synthetic dialogue cases only; inherited shared USD3 and no retry.',context_sha256=prepared['context_sha256'])
                started=time.monotonic();result=sources.analyze(owner,'synthetic',source['id'],extractor);dispatches+=1;after=transport.snapshot()
                private_json(folder/(stem+'.result.json'),dict(result=result,budget=after))
                findings=checkpoint(cid,step,result,roles)
                row=dict(message_id=message['id'],source_sha256=source['sha256'],context_sha256=prepared['context_sha256'],payload_sha256=fingerprint(payload),analysis_status=result['status'],failure_code=result.get('failure_code'),latency_ms=round((time.monotonic()-started)*1000),findings=findings,verdict='failed' if findings else 'passed_draft_check',candidate_types=[c['type'] for c in result['candidates']],candidate_titles=[c['title'] for c in result['candidates']],status_claims=[dict(task_id=p['task_id'],stage=p['stage']) for p in result.get('status_changes',[])],usage=result.get('usage'))
                case_rows.append(row)
                if progress:progress(dict(case=cid,turn=step,status=row['analysis_status'],findings=findings))
                if result['status']!='Ready for review' or after['frozen']:
                    stop='analysis_or_usage_requires_review';break
                # Controlled test operator: do not auto-accept arbitrary output.
                if step==1 and cid in ('J01','J02','J03') and not findings:
                    candidates=[c for c in result['candidates'] if c['type']=='Task']
                    accepted=sources.accept(owner,'synthetic',source_id=source['id'],key=stem+'_accept',selected=[c['id'] for c in candidates],base_revision=core.project(owner,'synthetic')['knowledge_revision'])
                    for c in candidates:
                        task=accepted['temp_ids'].get(c['id'])
                        if task:roles[task_role(c['title'])]=task;contract(core,owner,task,stem+'_'+task_role(c['title'])+'_scope')
                    actions.append(dict(turn=step,action='scripted_task_and_scope_review',roles=dict(roles)))
                if cid=='J04' and step in (1,2) and not findings:
                    proposal=result['question_proposals'][0]
                    receipt=DialogueQuestionService(core).review(owner,'synthetic',source_id=source['id'],proposal_id=proposal['id'],decision='accept',key=stem+'_present',reason='Scripted test-operator question presentation')
                    question_ids['store' if step==1 else 'ui']=receipt['question'];actions.append(dict(turn=step,action='scripted_question_presentation',question=receipt['question']))
                if not findings and (cid,step) in (('J01',4),('J02',5),('J03',5)):
                    review.review_status(owner,'synthetic',source_id=source['id'],proposal_id=result['status_changes'][0]['id'],decision='accept',key=stem+'_review',reason='Scripted test-operator review, not independent human gold')
                    actions.append(dict(turn=step,action='scripted_start_review'))
                if cid=='J01' and step==6 and not findings:
                    try:review.review_status(owner,'synthetic',source_id=source['id'],proposal_id=result['status_changes'][0]['id'],decision='accept',key=stem+'_false_done',reason='Negative guard probe; no evidence supplied',scope_reviewed=True)
                    except ContractError as error:row['done_guard_code']=error.code
                    else:row['findings'].append('false_done_applied');row['verdict']='failed'
                if cid=='J04' and step==5 and not findings:
                    answer=result['answer_proposals'][0];q=next((q for q in QuestionService(core).view(owner,'synthetic')['questions'] if q['id']==answer['question_id']),None)
                    if answer['question_id']!=question_ids.get('store') or q is None or not any(opt['id']==answer['option_id'] and 'sqlite' in opt['label'].casefold() for opt in q['options']):
                        row['findings'].append('wrong_delayed_question_or_option');row['verdict']='failed'
                    else:
                        review.review_answer(owner,'synthetic',source_id=source['id'],proposal_id=answer['id'],decision='accept',key=stem+'_answer',reason='Scripted review of exact source-bound selection; no decision application')
                        actions.append(dict(turn=step,action='scripted_answer_review_no_domain_apply'))
                row['canonical_stages']={role:TaskWorkflowService(core).view(owner,'synthetic',task)['stage'] for role,task in roles.items()}
                private_json(folder/(stem+'.evaluated.json'),row)
            results.append(dict(case_id=cid,planned_turns=len(case['messages']),processed_turns=len(case_rows),verdict='incomplete' if len(case_rows)!=len(case['messages']) else 'failed' if any(r['findings'] for r in case_rows) else 'passed_draft_checks',turns=case_rows,test_operator_actions=actions,questions=[dict(id=q['id'],status=q['status'],selection=q['selection']) for q in QuestionService(core).view(owner,'synthetic')['questions']]))
    report=dict(format='decivora-dialogue-batch-result-1',case_ids=list(CASE_IDS),model=plan['model'],cases=results,not_run=[c for c in CASE_IDS if c not in {r['case_id'] for r in results}],stopped=stop,dispatches=dispatches,budget_before=before,budget_after=after,semantic_verdict_authority='strict_AI_authored_draft_checks_require_review',human_gold=False,native_host_test=False,automatic_next_batch=False)
    private_json(folder/'report.json',report);return report


def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--prepare',action='store_true');g.add_argument('--run',action='store_true');p.add_argument('--folder',type=Path,default=DEFAULT);args=p.parse_args()
    if args.prepare:
        value=prepare(args.folder);print(json.dumps(dict(cases=[c['id'] for c in value['cases']],max_generation_calls=24,max_count_calls=24,network_calls=0)))
    else:
        value=run(args.folder,progress=lambda p:print(json.dumps(p),flush=True));print(json.dumps(dict(cases=[dict(case_id=c['case_id'],verdict=c['verdict']) for c in value['cases']],not_run=value['not_run'],stopped=value['stopped'],budget=value['budget_after'])))
if __name__=='__main__':
    try:main()
    except Exception:
        print('Batch stopped. Inspect private receipts; no automatic retry or next batch.',file=sys.stderr);raise SystemExit(1)

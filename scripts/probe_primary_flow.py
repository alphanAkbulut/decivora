"""API-free seam probes using isolated synthetic sources, never user data."""
import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
sys.path[:0]=[str(root),str(root/'tests/runtime')]
import test_conversations as fixtures
from packages.domain.questions import QuestionService
from packages.domain.decision_impact import DecisionImpactService
from packages.mcp.server import Server
f=fixtures.ConversationTests();f.setUp()
try:
 source=f.source();extractor=fixtures.Extractor();analysis=f.service.analyze(f.owner,'p',source['id'],extractor)
 f.service.accept(f.owner,'p',source_id=source['id'],key='probe_accept',selected=[c['id'] for c in analysis['candidates']],base_revision=0)
 records=f.core.records(f.owner,'p')['records'];task=next(r for r in records if r['body']['type']=='Task');decision=next(r for r in records if r['body']['type']=='Decision')
 result=dict(synthetic=True,real_model_calls=0,source_to_records={'count':len(records),'types':sorted(r['body']['type'] for r in records)},pending_decision_question_bridge={'pending_records':sum(r['body']['type']=='PendingDecision' for r in records),'question_inbox_entries':len(QuestionService(f.core).view(f.owner,'p')['questions'])},automatic_relationships={'edges_after_accept':f.core.db.execute('SELECT count(*) FROM edges').fetchone()[0]})
 plan=f.core.plan(f.owner,'p','explicit_fixture_relation',[dict(op='link',origin=task['id'],target=decision['id'],kind='required_by')]);f.core.apply(f.owner,plan,f.core.approve(f.owner,plan))
 before=f.core.projection_digest(f.owner,'p');impact=DecisionImpactService(f.core).preview(f.owner,'p',decision=decision['id'],decision_version=1,base_revision=f.core.project(f.owner,'p')['knowledge_revision'],key='probe_impact');proposal=next(p for p in impact['proposals'] if p['record']==task['id']);result['ui_impact_adapter']={'action':proposal['action'],'after':proposal['after'],'canonical_state_unchanged':f.core.projection_digest(f.owner,'p')==before,'rationale_supplied_by_ui':None}
 a=f.core.authority;a.replace_grant(f.owner,'probe_agent',kind='agent',readable=frozenset({'p'}),writable=frozenset(),active=True,base_revision=a.revision());brief=Server(f.path,'w','probe_agent').call('get_project_brief',dict(project_id='p'))
 result['mcp_private_source_resume']={'canonical_records':len(records),'agent_brief_records':len(brief['records']),'raw_sources_included':brief['raw_sources_included'],'privacy_filter_preserved':True}
 if args.output:args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False))
finally:f.doCleanups()

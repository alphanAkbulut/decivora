"""Published payload fields/enums matched to real local events, not full validator certification."""
import unittest,json
from pathlib import Path
import test_file_verification as fixtures
from packages.domain.work_routing import RoutingService
from packages.mcp.server import TOOLS
class SchemaTests(unittest.TestCase):
 def test_source_model_budget_grant_matches_published_fields(self):
  import time
  from packages.capture.conversations import ConversationService
  f=fixtures.FileTests();f.setUp();self.addCleanup(f.doCleanups)
  service=ConversationService(f.core);source=service.ingest(f.owner,'p',text='Synthetic source approval')
  f.core.create_budget(f.owner,'p','r',100)
  value=service.authorize_analysis(f.owner,'p',source_id=source['id'],key='g',root_run='r',reserved_tokens=80,provider='fixture',model='fixture-model',max_output_tokens=40,expires_at=int(time.time())+60,reason='Synthetic scoped approval')
  schema=json.loads((Path(__file__).resolve().parents[2]/'manifests/conversation-dispatch-grant.schema.json').read_text())
  self.assertEqual(set(value),set(schema['required']));self.assertEqual(set(schema['properties'])-set(value),{'context_sha256'});self.assertFalse(schema['additionalProperties'])

 def test_decision_hypothesis_request_matches_actual_service_arguments(self):
  import inspect
  from packages.domain.decision_impact import DecisionImpactService
  schema=json.loads((Path(__file__).resolve().parents[2]/'manifests/local-decision-impact.schema.json').read_text())
  fields=set(inspect.signature(DecisionImpactService.preview).parameters)-{'self','scope','project'}
  self.assertEqual(set(schema['required']),(fields-{'rationale_tasks','decision_active'})|{'action'})
  self.assertEqual(set(schema['properties']),fields|{'action'})
  self.assertEqual(schema['properties']['action']['const'],'preview_decision_change')
  self.assertFalse(schema['additionalProperties'])

 def test_real_routing_and_file_payloads_match_published_schema_fields(self):
  f=fixtures.FileTests();f.setUp();self.addCleanup(f.doCleanups);f.bind();f.f.ready_for_verification();f.check();RoutingService(f.core).set(f.owner,'p',task=f.task,task_version=1,base_revision=0,work_class='DETERMINISTIC',executor='HUMAN',human_suitable=True,reason='Explicit small work label',key='route')
  root=Path(__file__).resolve().parents[2]
  for action,name in [('work_routing','work-routing'),('file_criterion_binding','file-criterion-binding'),('file_criterion_evidence','file-criterion-evidence')]:
   schema=json.loads((root/'manifests'/f'{name}.schema.json').read_text());rows=f.core.db.execute('SELECT ref FROM audit WHERE action=?',(action,)).fetchall();self.assertTrue(rows)
   for raw, in rows:
    value=json.loads(raw);self.assertEqual(set(value),set(schema['required']));self.assertEqual(set(value),set(schema['properties']))
    for key,prop in schema['properties'].items():
     if 'enum' in prop:self.assertIn(value[key],prop['enum'])
     if 'const' in prop:self.assertEqual(value[key],prop['const'])
  self.assertEqual(json.loads((root/'manifests/local-mcp-tools.json').read_text())['tools'],TOOLS)

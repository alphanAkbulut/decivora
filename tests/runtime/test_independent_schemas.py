"""Published payload fields/enums matched to real local events, not full validator certification."""
import unittest,json
from pathlib import Path
import test_file_verification as fixtures
from packages.domain.work_routing import RoutingService
from packages.mcp.server import TOOLS
class SchemaTests(unittest.TestCase):
 def test_decision_hypothesis_request_matches_actual_service_arguments(self):
  import inspect
  from packages.domain.decision_impact import DecisionImpactService
  schema=json.loads((Path(__file__).resolve().parents[2]/'manifests/local-decision-impact.schema.json').read_text())
  fields=set(inspect.signature(DecisionImpactService.preview).parameters)-{'self','scope','project'}
  self.assertEqual(set(schema['required']),fields|{'action'})
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

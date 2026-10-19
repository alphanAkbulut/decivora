"""Per-source activation through the actual local command path; no real model/network."""
import copy
import json
from pathlib import Path
import tempfile
import time
import unittest
from apps.local_ui.server import LocalApp
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.granted_extractors import GrantedResponsesFactory
from packages.domain.source_event import ContractError


class GrantedExtractorTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'app.sqlite';self.app=LocalApp(self.path);self.entries=[];self.calls=[];self.sources=[]
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');service=ConversationService(core)
            core.create_budget(owner,'personal','batch',24000)
            for index in range(2):
                source=service.ingest(owner,'personal',text='Please add backup test '+str(index)+'.')
                prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
                grant=service.authorize_analysis(owner,'personal',source_id=source['id'],key='grant_'+str(index),root_run='batch',reserved_tokens=12000,provider='OpenAI Responses configured transport',model='fixture',max_output_tokens=2000,expires_at=int(time.time())+3600,reason='Synthetic isolated test; no external request.',context_sha256=prepared['context_sha256'])
                self.entries.append((grant,self.send));self.sources.append(source)
        self.factory=GrantedResponsesFactory(self.entries)

    def send(self,payload):
        self.calls.append(payload);request=json.loads(payload['input']);source=request['source']
        output=dict(source_id=source['id'],source_sha256=source['sha256'],context_sha256=request['context_sha256'],coverage='partial',candidates=[dict(type='Task',title='Backup test',quote=source['text'],intent='planned')],status_changes=[],answer_proposals=[],relation_proposals=[])
        return dict(status='completed',usage=dict(total_tokens=100),output=[dict(type='message',role='assistant',status='completed',content=[dict(type='output_text',text=json.dumps(output))])])

    def test_two_sources_dispatch_through_local_queue_with_distinct_context(self):
        app=LocalApp(self.path,extractor_factory=self.factory)
        self.assertTrue(app.state()['model_ready'])
        result=app.command(dict(action='process_conversation_queue',limit=2))
        self.assertEqual(result['attempted'],2);self.assertEqual(len(self.calls),2)
        self.assertEqual(result['queue']['counts'],{'Ready for review':2})
        self.assertEqual(app.state()['tasks'],[])
        app.command(dict(action='process_conversation_queue',limit=2));self.assertEqual(len(self.calls),2)
        self.assertEqual({json.loads(p['input'])['source']['id'] for p in self.calls},{s['id'] for s in self.sources})

    def test_single_source_command_uses_exact_registered_grant(self):
        app=LocalApp(self.path,extractor_factory=self.factory)
        result=app.command(dict(action='analyze_conversation',source_id=self.sources[1]['id']))
        self.assertEqual(result['status'],'Ready for review');self.assertEqual(len(self.calls),1)
        saved=app.command(dict(action='import_conversation',text='An unapproved new message.'))
        self.assertEqual(saved['analysis']['status'],'Waiting for model');self.assertEqual(len(self.calls),1)

    def test_changed_grant_source_or_expiry_does_not_get_transport(self):
        source=self.sources[0];grant=self.entries[0][0]
        for field,value in [('model','other'),('context_sha256','0'*64),('authority_revision',999),('expires_at',int(time.time())-1),('id','unknown')]:
            modified=copy.deepcopy(grant);modified[field]=value
            self.assertIsNone(self.factory(source,modified))
        self.assertIsNone(self.factory(self.sources[1],grant))
        first=self.factory(source,grant);second=self.factory(source,grant)
        self.assertIsNot(first,second);self.assertEqual(self.calls,[])
        grant['model']='mutated';self.assertIsNone(self.factory(source,grant))

    def test_test_environment_and_duplicate_configuration_stay_disabled(self):
        with self.assertRaises(ContractError):LocalApp(self.path.with_name('test.sqlite'),environment='test',extractor_factory=self.factory)
        with self.assertRaises(ContractError):LocalApp(self.path,extractor=object(),extractor_factory=self.factory)
        with self.assertRaises(ContractError):GrantedResponsesFactory([self.entries[0],self.entries[0]])

    def test_revoked_scope_prevents_factory_dispatch(self):
        app=LocalApp(self.path,extractor_factory=self.factory)
        with app.core() as core:
            a=core.authority;owner=a.issue_scope('local_owner')
            a.replace_grant(owner,'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset(),active=True,base_revision=a.revision())
        with self.assertRaises(ContractError):app.command(dict(action='process_conversation_queue',limit=2))
        self.assertEqual(self.calls,[])

    def test_registered_expiry_and_changed_task_context_block_before_send(self):
        from unittest.mock import patch
        grant=self.entries[0][0]
        with patch('packages.capture.granted_extractors.time.time',return_value=grant['expires_at']+1):
            self.assertIsNone(self.factory(self.sources[0],grant))
        app=LocalApp(self.path,extractor_factory=self.factory)
        with app.core() as core:
            owner=core.authority.issue_scope('local_owner')
            plan=core.plan(owner,'personal','context_change',[dict(op='create',id='task',body=dict(type='Task',title='New context',description='A new approved task.'))])
            core.apply(owner,plan,core.approve(owner,plan))
        with self.assertRaises(ContractError):app.command(dict(action='analyze_conversation',source_id=self.sources[0]['id']))
        self.assertEqual(self.calls,[])

    def test_native_source_envelope_keeps_provenance_and_rejects_tampering(self):
        from packages.capture.responses_extractor import request_payload,source_envelope
        source=dict(self.sources[0],source_kind='codex_app_server',capture=dict(observed_actor='assistant',item_id='item_one',turn_id='turn_one'))
        request=dict(source=source_envelope(source),instructions='Synthetic contract',context={},context_sha256='a'*64,response_schema={})
        payload=request_payload(source,model='fixture',max_output_tokens=2000,dialogue_request=request)
        self.assertEqual(json.loads(payload['input'])['source']['capture']['observed_actor'],'assistant')
        for modification in ('role','missing','text'):
            changed=copy.deepcopy(request)
            if modification=='role':changed['source']['capture']['observed_actor']='user'
            elif modification=='missing':changed['source'].pop('capture')
            else:changed['source']['text']='Changed text'
            with self.assertRaises(ContractError):request_payload(source,model='fixture',max_output_tokens=2000,dialogue_request=changed)

    def test_server_constructor_forwards_factory_without_dispatch(self):
        from apps.local_ui.server import make_server
        server=make_server(self.path,extractor_factory=self.factory)
        try:self.assertIs(server.app.extractor_factory,self.factory)
        finally:server.server_close()
        self.assertEqual(self.calls,[])

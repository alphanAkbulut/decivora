"""Persisted scheduling limits and background integration; all model output is fake."""
import threading,time,unittest
from unittest.mock import patch
import test_model_activation as fixtures
from apps.local_ui.server import LocalApp
from packages.capture.processing_loop import ProcessingLoopService
from packages.capture.model_activation import ManagedResponsesFactory
from packages.capture.granted_extractors import GrantedResponsesFactory
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

class ProcessingLoopTests(unittest.TestCase):
    def setUp(self):
        self.fx=fixtures.ModelActivationTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
        self.app=self.fx.app;self.addCleanup(self.app.processing_worker.shutdown);self.fx.change('Active')
        self.args=dict(action='create_processing_loop',loop_id='loop_one',activation_id=self.fx.record['id'],activation_sha256=self.fx.record['configuration_sha256'],max_passes=4,max_sources_per_pass=1,max_total_sources=2,interval_seconds=.25,expires_at=self.fx.expiry,reason='Explicit synthetic worker fixture; no external API.')
        self.plan=self.app.command(self.args);self.calls=self.fx.fx.calls
    def run_pass(self,app=None):
        return (app or self.app).command(dict(action='run_processing_pass',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256']))
    def stop(self):
        return self.app.command(dict(action='stop_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256'],reason='Explicit test stop.'))
    def start(self):
        return self.app.command(dict(action='start_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256']))
    def changed_app(self,send):
        factory=ManagedResponsesFactory(GrantedResponsesFactory([(grant,send) for grant,_ in self.fx.fx.entries]),self.fx.record['id'])
        app=LocalApp(self.fx.fx.path,extractor_factory=factory);self.addCleanup(app.processing_worker.shutdown);return app

    def test_durable_source_limit_and_interval_do_not_reset_after_restart(self):
        now=time.time()
        with patch('packages.capture.processing_loop.time.time',return_value=now):
            self.assertEqual(self.run_pass()['attempted'],1)
            self.assertEqual(self.run_pass()['status'],'Waiting for interval')
        app=LocalApp(self.fx.fx.path,extractor_factory=self.app.extractor_factory)
        self.assertFalse(app.processing_worker.view('personal')['active'])
        with patch('packages.capture.processing_loop.time.time',return_value=now+10):self.assertEqual(self.run_pass(app)['attempted'],1)
        self.assertEqual(self.run_pass(app)['status'],'Limit reached');self.assertEqual(len(self.calls),2)
        with self.assertRaises(ContractError):self.app.command(dict(self.args,max_total_sources=3))
        self.assertEqual(self.app.state()['tasks'],[])

    def test_create_does_not_start_and_requires_explicit_matching_managed_model(self):
        self.assertEqual(self.calls,[]);self.assertEqual(self.app.command(self.args),self.plan)
        offline=LocalApp(self.fx.fx.path)
        with self.assertRaises(ContractError):self.run_pass(offline)
        with self.assertRaises(ContractError):offline.command(dict(action='start_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256']))
        self.assertEqual(offline.state()['processing_loops']['items'][0]['passes'],0)

    def test_pause_expiry_and_permission_change_never_dispatch(self):
        self.fx.change('Paused')
        with self.assertRaises(ContractError):self.run_pass()
        self.fx.change('Active')
        with patch('packages.capture.processing_loop.time.time',return_value=self.fx.expiry+1):
            with self.assertRaises(ContractError):self.run_pass()
        with self.app.core() as core:
            a=core.authority;owner=a.issue_scope('local_owner');a.replace_grant(owner,'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=a.revision())
        with self.assertRaises(ContractError):self.run_pass()
        self.assertEqual(self.calls,[])

    def test_unfinished_claim_survives_restore_and_is_not_retried(self):
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');service=ProcessingLoopService(core)
            with core.transaction():service._save(owner,'personal',dict(id=self.plan['id'],kind='pass_started',pass_id='crashed_pass',allowance=1,recorded_at=time.time()))
            backup=self.fx.fx.path.with_name('backup.sqlite');manifest=core.backup(owner,backup)
        with Workspace.restore(backup,self.fx.fx.path.with_name('restored.sqlite'),manifest) as core:
            owner=core.authority.issue_scope('local_owner');service=ProcessingLoopService(core)
            result=service.execute_pass(owner,'personal',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256'],registry=self.app.extractor_factory)
            self.assertEqual(result['status'],'Unfinished pass');self.assertEqual(service.view(owner,'personal')['items'][0]['reserved_or_attempted'],1)
        with self.assertRaises(ContractError):self.start()
        self.assertEqual(self.calls,[])

    def test_unknown_usage_finishes_as_review_required_and_does_not_continue(self):
        def send(payload):
            result=self.fx.fx.send(payload);result['usage']=None;return result
        app=self.changed_app(send);result=self.run_pass(app)
        self.assertEqual(result['status'],'Review required');self.assertEqual(len(self.calls),1)
        self.assertEqual(self.run_pass(app)['status'],'Review required');self.assertEqual(len(self.calls),1)

    def test_second_worker_cannot_claim_a_pass_while_model_is_inflight(self):
        entered=threading.Event();release=threading.Event();results=[]
        def send(payload):
            entered.set();self.assertTrue(release.wait(5));return self.fx.fx.send(payload)
        app=self.changed_app(send);thread=threading.Thread(target=lambda:results.append(self.run_pass(app)));thread.start()
        try:
            self.assertTrue(entered.wait(3));self.assertEqual(self.run_pass()['status'],'Unfinished pass')
        finally:release.set();thread.join(3)
        self.assertFalse(thread.is_alive());self.assertEqual(results[0]['attempted'],1);self.assertEqual(len(self.calls),1)

    def test_stop_between_factory_and_admission_prevents_dispatch(self):
        original=self.app.extractor_factory;test=self
        class RaceFactory:
            activation_id=original.activation_id
            def bind_scope(self,core,scope,project):
                base=original.bind_scope(core,scope,project)
                def factory(source,grant):
                    extractor=base(source,grant);test.stop();return extractor
                return factory
        app=LocalApp(self.fx.fx.path,extractor_factory=RaceFactory())
        result=self.run_pass(app);self.assertEqual(result['status'],'Review required');self.assertEqual(self.calls,[])
        self.assertEqual(self.run_pass()['status'],'Stopped')

    def test_inflight_result_survives_stop_without_next_source(self):
        def send(payload):self.stop();return self.fx.fx.send(payload)
        app=self.changed_app(send);result=self.run_pass(app)
        self.assertEqual(result['attempted'],1);self.assertEqual(result['outcomes'][0]['status'],'Ready for review')
        self.assertEqual(self.run_pass()['status'],'Stopped');self.assertEqual(len(self.calls),1)

    def test_explicit_background_worker_runs_to_limit_and_logs_safe_ticks(self):
        self.assertFalse(self.app.state()['processing_worker']['active']);self.start()
        self.app.processing_worker.thread.join(5);self.assertFalse(self.app.processing_worker.thread.is_alive())
        state=self.app.state();self.assertEqual(len(self.calls),2);self.assertEqual(state['processing_worker']['status'],'Limit reached')
        self.assertFalse(state['conversation_queue']['automatic_dispatch']);self.assertEqual(state['tasks'],[])
        operations=self.app.operations_view();self.assertTrue(any(r['action']=='processing_tick' for r in operations['runs']))
        with self.assertRaises(ContractError):self.start()

    def test_background_stop_is_interruptible_and_flags_reflect_live_worker(self):
        entered=threading.Event();release=threading.Event()
        def send(payload):entered.set();self.assertTrue(release.wait(5));return self.fx.fx.send(payload)
        app=self.changed_app(send)
        try:
            app.command(dict(action='start_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256']))
            self.assertTrue(entered.wait(3));self.assertTrue(app.state()['processing_worker']['active']);self.assertTrue(app.operations_view()['background_worker_active'])
            with self.assertRaises(ContractError):app.command(dict(action='start_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256']))
            app.command(dict(action='stop_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256'],reason='Stop while in flight'))
        finally:release.set();app.processing_worker.thread.join(3)
        self.assertFalse(app.processing_worker.thread.is_alive());self.assertEqual(len(self.calls),1)

    def test_bounds_foreign_project_and_config_digest_are_enforced(self):
        for values in (dict(max_passes=0),dict(max_total_sources=True),dict(interval_seconds=float('inf')),dict(expires_at=self.fx.expiry+1)):
            with self.assertRaises(ContractError):self.app.command(dict(self.args,loop_id='invalid',**values))
        with self.assertRaises(ContractError):self.app.command(dict(project_id='foreign',command=self.args))
        with self.assertRaises(ContractError):self.app.command(dict(action='run_processing_pass',loop_id=self.plan['id'],configuration_sha256='0'*64))
        self.assertEqual(self.calls,[])

    def test_pass_limit_with_no_eligible_work_is_durable_and_does_not_call_model(self):
        self.app.command(dict(self.args,loop_id='empty_loop',max_passes=1))
        # Registry may decline transport configuration, but cannot authorize a source.
        class NoTransport:
            activation_id='activation_one'
            def bind_scope(self,*args):return lambda *args:None
        app=LocalApp(self.fx.fx.path,extractor_factory=NoTransport())
        plan=next(r for r in app.state()['processing_loops']['items'] if r['id']=='empty_loop')
        command=dict(action='run_processing_pass',loop_id='empty_loop',configuration_sha256=plan['configuration_sha256'])
        self.assertEqual(app.command(command)['status'],'Waiting for grant')
        self.assertEqual(app.command(command)['status'],'Limit reached');self.assertEqual(self.calls,[])

    def test_http_start_requires_session_and_runs_only_the_explicit_loop(self):
        from apps.local_ui.server import make_server
        import json,urllib.request,urllib.error
        server=make_server(self.fx.fx.path,extractor_factory=self.app.extractor_factory)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        body=dict(action='start_processing_loop',loop_id=self.plan['id'],configuration_sha256=self.plan['configuration_sha256'])
        headers={'Content-Type':'application/json','Origin':server.origin,'Cookie':'decivora_session='+server.app.cookie,'X-CSRF-Token':server.app.csrf}
        def call(headers):
            request=urllib.request.Request(server.origin+'/api/command',data=json.dumps(body).encode(),headers=headers,method='POST')
            try:
                with urllib.request.urlopen(request) as response:return response.status,json.load(response)
            except urllib.error.HTTPError as response:return response.code,json.load(response)
        try:
            self.assertEqual(call({'Content-Type':'application/json','Origin':server.origin})[0],403)
            self.assertIsNone(server.app.processing_worker.thread)
            status,value=call(headers);self.assertEqual(status,200);self.assertEqual(value['status'],'Worker started')
            server.app.processing_worker.thread.join(5);self.assertEqual(len(self.calls),2)
            self.assertEqual(server.app.state()['tasks'],[])
        finally:server.app.processing_worker.shutdown();server.shutdown();server.server_close();thread.join(2)

    def test_transport_label_cannot_expand_the_activation_source_allowlist(self):
        from packages.capture.conversations import ConversationService
        from packages.capture.dialogue_review import DialogueReviewService
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');sources=ConversationService(core)
            source=sources.ingest(owner,'personal',text='Please add an unrelated authorized source.')
            prepared=DialogueReviewService(core).prepare(owner,'personal',source_id=source['id'])
            core.create_budget(owner,'personal','other_run',12000)
            grant=sources.authorize_analysis(owner,'personal',source_id=source['id'],key='other_grant',root_run='other_run',reserved_tokens=12000,provider='OpenAI Responses configured transport',model='fixture',max_output_tokens=2000,expires_at=self.fx.expiry,reason='Synthetic outside-loop source grant',context_sha256=prepared['context_sha256'])
        registry=GrantedResponsesFactory([(grant,self.fx.fx.send)])
        class WrongSource:
            activation_id='activation_one'
            def bind_scope(self,*args):return registry
        app=LocalApp(self.fx.fx.path,extractor_factory=WrongSource());result=self.run_pass(app)
        self.assertEqual(result['status'],'Waiting for grant');self.assertEqual(result['outcomes'],[]);self.assertEqual(self.calls,[])

    def test_loop_control_capacity_freezes_before_new_admission(self):
        with self.app.core() as core:
            owner=core.authority.issue_scope('local_owner');service=ProcessingLoopService(core)
            with core.transaction():
                for _ in range(2047):service.sources._put(owner,'personal',service.ACTION,dict(id='other_loop',kind='stopped',recorded_at=time.time()))
        self.assertEqual(self.app.state()['processing_loops']['items'][0]['status'],'History capacity reached')
        with self.assertRaises(ContractError) as error:self.run_pass()
        self.assertEqual(error.exception.code,'processing_loop_history_limit');self.assertEqual(self.calls,[])

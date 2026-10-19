"""Explicitly started local bounded worker, off by default and never auto-resumed."""
import threading
import time
from packages.capture.processing_loop import ProcessingLoopService
from packages.domain.source_event import ContractError
from packages.operations.local import identity_from_scope,safe_code


class LocalProcessingWorker:
    def __init__(self,app):
        self.app=app;self.lock=threading.Lock();self.thread=None;self.event=threading.Event()
        self.project=None;self.loop_id=None;self.status='Not started';self.code=None

    def view(self,project):
        with self.lock:
            selected=self.project==project
            active=bool(selected and self.thread and self.thread.is_alive())
            return dict(active=active,loop_id=self.loop_id if selected else None,status=self.status if selected else 'Not started',code=self.code if selected else None,automatic_start=False)

    def start(self,core,scope,project,*,loop_id,configuration_sha256):
        core.scope(scope,project,write=True,human=True);core.active(scope,project)
        service=ProcessingLoopService(core);config=service._config(project,loop_id);service._authority(scope,project,config)
        if config['configuration_sha256']!=configuration_sha256:raise ContractError('processing_loop_denied','Exact loop configuration required.')
        state=service._state(project,config)
        if state['stopped'] or state['review_required'] or state['pending']:
            raise ContractError('processing_loop_stopped','Stopped or unfinished loop cannot be automatically started.')
        if state['passes']>=config['max_passes'] or state['reserved_or_attempted']>=config['max_total_sources']:
            raise ContractError('processing_loop_limit','The durable loop limit has already been consumed.')
        registry=self.app.extractor_factory
        if getattr(registry,'activation_id',None)!=config['activation_id'] or not hasattr(registry,'bind_scope'):
            raise ContractError('processing_loop_model_required','Matching managed model configuration is required.')
        with self.lock:
            if self.thread and self.thread.is_alive():raise ContractError('processing_worker_busy','A local worker is already running.')
            self.project=project;self.loop_id=loop_id;self.status='Starting';self.code=None;self.event=threading.Event()
            self.thread=threading.Thread(target=self._run,args=(config,project,registry,self.event),daemon=True,name='decivora-processing')
            self.thread.start()
        return dict(id=loop_id,status='Worker started',automatic_start=False)

    def cancel(self,project,loop_id):
        with self.lock:
            if self.project==project and self.loop_id==loop_id:self.event.set()

    def shutdown(self):
        with self.lock:event=self.event;thread=self.thread
        event.set()
        if thread and thread is not threading.current_thread():thread.join(timeout=2)

    def _run(self,config,project,registry,event):
        status='Stopped';code=None
        try:
            while not event.is_set():
                started=time.monotonic();run=None
                with self.app.core() as core:
                    scope=core.authority.issue_scope(config['actor'])
                    identity=identity_from_scope(core,scope,project)
                    run=self.app.operations.begin(project,'processing_tick',identity=identity)
                    try:
                        with self.app.operations.span(run,1,'extraction','execute_command'):
                            result=ProcessingLoopService(core).execute_pass(scope,project,loop_id=config['id'],configuration_sha256=config['configuration_sha256'],registry=registry)
                    except Exception as error:
                        self.app.operations.finish(run,started,error);raise
                    self.app.operations.finish(run,started)
                status=result['status']
                with self.lock:self.status=status
                if status not in ('Pass finished','Waiting for grant','Waiting for interval'):break
                if event.wait(config['interval_seconds']):status='Stopped';break
        except Exception as error:
            status='Stopped';code=safe_code(getattr(error,'code','application_error'))
        finally:
            with self.lock:self.status=status;self.code=code

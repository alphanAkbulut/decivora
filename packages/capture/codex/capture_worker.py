"""Local finite polling thread. Explicit start only; no model or retry path."""
import threading
import time
from packages.capture.codex.capture_loop import CaptureLoopService
from packages.domain.source_event import ContractError
from packages.operations.local import identity_from_scope,safe_code

class LocalCaptureWorker:
    def __init__(self,app):
        self.app=app;self.lock=threading.Lock();self.thread=None;self.event=threading.Event();self.project=None;self.loop_id=None;self.status='Not started';self.code=None
    def view(self,project):
        with self.lock:
            same=self.project==project
            return dict(active=bool(same and self.thread and self.thread.is_alive()),loop_id=self.loop_id if same else None,status=self.status if same else 'Not started',code=self.code if same else None,automatic_start=False)
    def start(self,core,scope,project,*,loop_id,configuration_sha256,consent):
        if consent is not True:raise ContractError('capture_consent_required','Explicit schedule start required.')
        with core.read_snapshot():
            service=CaptureLoopService(core,self.app.native_connector);config=service.config(project,loop_id);service.authority(scope,project,config);state=service.state(project,config)
            if config['configuration_sha256']!=configuration_sha256:raise ContractError('capture_loop_denied','Exact schedule required.')
            if state['pending'] or state['failed'] or state['stopped']:raise ContractError('capture_loop_stopped','Stopped or unfinished schedule cannot resume automatically.')
            if state['ticks']>=config['max_ticks']:raise ContractError('capture_loop_limit','Schedule already exhausted.')
        with self.lock:
            if self.thread and self.thread.is_alive():raise ContractError('capture_worker_busy','A local capture worker is already running.')
            self.project=project;self.loop_id=loop_id;self.status='Starting';self.code=None;self.event=threading.Event()
            self.thread=threading.Thread(target=self.run,args=(config,project,self.event),daemon=True,name='decivora-capture');self.thread.start()
        return dict(id=loop_id,status='Worker started',automatic_start=False)
    def cancel(self,project,loop_id):
        with self.lock:
            if self.project==project and self.loop_id==loop_id:self.event.set()
    def shutdown(self):
        with self.lock:thread=self.thread;self.event.set()
        if thread and thread is not threading.current_thread():thread.join(timeout=2)
    def run(self,config,project,event):
        status='Stopped';code=None
        try:
            while not event.is_set():
                started=time.monotonic()
                with self.app.core() as core:
                    scope=core.authority.issue_scope(config['actor']);run=self.app.operations.begin(project,'capture_tick',identity=identity_from_scope(core,scope,project))
                    try:
                        with self.app.operations.span(run,1,'capture','execute_command'):
                            result=CaptureLoopService(core,self.app.native_connector).tick(scope,project,loop_id=config['id'],configuration_sha256=config['configuration_sha256'],cancelled=event.is_set)
                    except Exception as error:self.app.operations.finish(run,started,error);raise
                    self.app.operations.finish(run,started)
                    count=CaptureLoopService(core,self.app.native_connector).state(project,config)['ticks']
                status='Limit reached' if result['status']=='Captured' and count>=config['max_ticks'] else result['status']
                with self.lock:self.status=status
                if status not in ('Captured','Waiting for interval'):break
                if event.wait(config['interval_seconds']):status='Stopped';break
        except Exception as error:status='Stopped';code=safe_code(getattr(error,'code','application_error'))
        finally:
            with self.lock:self.status=status;self.code=code

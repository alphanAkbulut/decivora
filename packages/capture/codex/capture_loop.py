"""Durable polling plans over one existing exact capture consent; no model access."""
import time
import uuid
from packages.capture.codex.ui_connection import UIConnectionService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest

class CaptureLoopService:
    ACTION='codex_capture_loop'
    def __init__(self,core,connector=None):
        self.core=core;self.capture=UIConnectionService(core,connector)
    def rows(self,project):return self.capture.rows(project,self.ACTION)
    def config(self,project,loop_id):
        identifier(loop_id)
        row=next((r for r in self.rows(project) if r['id']==loop_id and r['kind']=='configured'),None)
        if row is None:raise ContractError('capture_loop_unavailable','Capture schedule unavailable.')
        return row
    def save(self,scope,project,row):
        if len(self.rows(project))>=2048:raise ContractError('capture_loop_limit','Capture schedule history full; no further reads.')
        self.capture.sources._put(scope,project,self.ACTION,row)
    def state(self,project,config):
        rows=[r for r in self.rows(project) if r['id']==config['id']]
        starts=[r for r in rows if r['kind']=='started'];ends={r['tick_id']:r for r in rows if r['kind']=='finished'}
        return dict(ticks=len(starts),pending=[r for r in starts if r['tick_id'] not in ends],stopped=any(r['kind']=='stopped' for r in rows),failed=any(r.get('status')=='Read failed' for r in ends.values()),last_finished=max((r['recorded_at'] for r in ends.values()),default=0))
    def authority(self,scope,project,config):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        if config['actor']!=scope.principal_id or config['authority_revision']!=self.core.authority.revision():raise ContractError('capture_loop_denied','Capture schedule authority changed.')
        if config['expires_at']<=time.time():raise ContractError('capture_loop_expired','Capture schedule expired.')
        if len(self.rows(project))>=2048:raise ContractError('capture_loop_limit','Capture schedule history full.')
        return self.capture.authorize(scope,project,config['capture_id'],config['capture_sha256'])
    def create(self,scope,project,*,loop_id,capture_id,capture_sha256,max_ticks,interval_seconds,expires_at,reason):
        identifier(loop_id);identifier(capture_id)
        if type(max_ticks) is not int or not 1<=max_ticks<=300 or type(interval_seconds) not in (int,float) or not 1<=interval_seconds<=3600 or type(expires_at) is not int or not time.time()<expires_at or type(reason) is not str or not 1<=len(reason.strip())<=1024:raise ContractError('invalid_capture_loop','Explicit bounded schedule, expiry and reason required.')
        with self.core.transaction():
            self.capture.authorize(scope,project,capture_id,capture_sha256);source=self.capture.config(project,capture_id)
            if source['actor']!=scope.principal_id or expires_at>source['expires_at']:raise ContractError('capture_loop_denied','Owned capture consent and no expiry extension required.')
            config=dict(id=loop_id,kind='configured',capture_id=capture_id,capture_sha256=capture_sha256,max_ticks=max_ticks,interval_seconds=interval_seconds,expires_at=expires_at,reason=reason,actor=scope.principal_id,authority_revision=self.core.authority.revision())
            config['configuration_sha256']=digest(canonical(config))
            old=next((r for r in self.rows(project) if r['id']==loop_id and r['kind']=='configured'),None)
            if old:
                if old!=config:raise ContractError('idempotency_conflict','Capture schedule cannot reset its limits.')
                return old
            starts,_,pending=self.capture.counts(project,capture_id)
            if pending or max_ticks>source['max_reads']-len(starts):raise ContractError('capture_loop_limit','Schedule exceeds remaining read consent or an unfinished read requires review.')
            for other in (r for r in self.rows(project) if r['kind']=='configured' and r['capture_id']==capture_id):
                state=self.state(project,other)
                if not state['stopped'] and not state['failed'] and state['ticks']<other['max_ticks'] and other['expires_at']>time.time():raise ContractError('capture_loop_denied','An existing schedule already owns this connection.')
            self.save(scope,project,config);return config
    def require(self,scope,project,config,tick_id):
        self.authority(scope,project,config);state=self.state(project,config)
        if state['stopped'] or state['failed'] or not any(r['tick_id']==tick_id for r in state['pending']):raise ContractError('capture_loop_stopped','Capture tick no longer has permission.')
    def tick(self,scope,project,*,loop_id,configuration_sha256,cancelled=None):
        with self.core.transaction():
            config=self.config(project,loop_id);self.authority(scope,project,config)
            if config['configuration_sha256']!=configuration_sha256:raise ContractError('capture_loop_denied','Exact capture schedule required.')
            state=self.state(project,config)
            if state['stopped'] or state['failed'] or state['pending']:raise ContractError('capture_loop_stopped','Stopped, failed or unfinished schedule requires review; no retry.')
            if state['ticks']>=config['max_ticks']:return dict(status='Limit reached',id=loop_id)
            if state['ticks'] and time.time()<state['last_finished']+config['interval_seconds']:return dict(status='Waiting for interval',id=loop_id)
            tick_id='capture_tick_'+uuid.uuid4().hex
            self.save(scope,project,dict(id=loop_id,kind='started',tick_id=tick_id,recorded_at=time.time()))
        def guard():
            if cancelled is not None and cancelled():raise ContractError('capture_loop_stopped','Local capture worker stopped before checkpoint.')
            self.require(scope,project,config,tick_id)
        try:
            receipt=self.capture.read_once(scope,project,capture_id=config['capture_id'],configuration_sha256=config['capture_sha256'],read_id=tick_id,consent=True,guard=guard)
        except ContractError as error:
            with self.core.transaction():
                self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
                self.save(scope,project,dict(id=loop_id,kind='finished',tick_id=tick_id,status='Read failed',recorded_at=time.time()))
            raise error
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            self.save(scope,project,dict(id=loop_id,kind='finished',tick_id=tick_id,status='Captured',recorded_at=time.time()))
        return dict(status='Captured',id=loop_id,receipt=receipt)
    def stop(self,scope,project,*,loop_id,configuration_sha256,reason):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);config=self.config(project,loop_id)
            if config['actor']!=scope.principal_id or config['configuration_sha256']!=configuration_sha256 or type(reason) is not str or not 1<=len(reason.strip())<=1024:raise ContractError('capture_loop_denied','Owned exact schedule and stop reason required.')
            if not self.state(project,config)['stopped']:self.save(scope,project,dict(id=loop_id,kind='stopped',reason=reason,recorded_at=time.time()))
            return dict(id=loop_id,status='Stopped')
    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project);items=[]
            for config in (r for r in self.rows(project) if r['kind']=='configured' and r['actor']==scope.principal_id):
                state=self.state(project,config);status='Configured'
                if state['stopped']:status='Stopped'
                elif state['pending']:status='Unfinished read'
                elif state['failed']:status='Review required'
                elif state['ticks']>=config['max_ticks']:status='Limit reached'
                else:
                    try:self.authority(scope,project,config)
                    except ContractError as error:status='Expired' if error.code in ('capture_loop_expired','capture_permission_expired') else 'Permission changed'
                items.append(dict(id=config['id'],capture_id=config['capture_id'],configuration_sha256=config['configuration_sha256'],status=status,ticks=state['ticks'],max_ticks=config['max_ticks'],interval_seconds=config['interval_seconds'],expires_at=config['expires_at']))
            return dict(items=items,automatic_start=False,model_dispatch=False)

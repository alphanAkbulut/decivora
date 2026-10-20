"""Durable, bounded queue passes over an existing managed activation.

No source discovery, grant creation, budget renewal, automatic apply or retry.
A pass claim survives a crash. An unfinished claim blocks a second worker.
"""
import time
import uuid
from packages.capture.conversations import ConversationService
from packages.capture.model_activation import ModelActivationService
from packages.capture.processing_queue import ConversationQueue
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest


class ProcessingLoopService:
    ACTION='conversation_processing_loop'
    def __init__(self,core):
        self.core=core;self.sources=ConversationService(core);self.activations=ModelActivationService(core)

    def _rows(self,project):return self.sources._rows(project,self.ACTION)

    def _config(self,project,loop_id):
        row=next((r for r in self._rows(project) if r['kind']=='configured' and r['id']==loop_id),None)
        if row is None:raise ContractError('processing_loop_unavailable','Processing loop unavailable.')
        return row

    def _save(self,scope,project,value):
        if len(self._rows(project))>=2048:
            raise ContractError('processing_loop_history_limit','Loop control capacity reached; new processing is frozen.')
        self.sources._put(scope,project,self.ACTION,value)

    def _state(self,project,config):
        rows=[r for r in self._rows(project) if r['id']==config['id']]
        starts=[r for r in rows if r['kind']=='pass_started'];ends={r['pass_id']:r for r in rows if r['kind']=='pass_finished'}
        pending=[r for r in starts if r['pass_id'] not in ends]
        used=sum(ends[r['pass_id']]['attempted'] if r['pass_id'] in ends else r['allowance'] for r in starts)
        return dict(passes=len(starts),reserved_or_attempted=used,pending=pending,stopped=any(r['kind']=='stopped' for r in rows),
                    review_required=any(r['kind']=='pass_finished' and r['review_required'] for r in rows))

    def _authority(self,scope,project,config):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        if config['actor']!=scope.principal_id or config['authority_revision']!=self.core.authority.revision():
            raise ContractError('processing_loop_permission_changed','Loop authority changed; no automatic renewal.')
        if config['expires_at']<=time.time():raise ContractError('processing_loop_expired','Loop expired; no automatic renewal.')
        activation=self.activations._current(project,config['activation_id'])
        if activation['configuration_sha256']!=config['activation_sha256']:
            raise ContractError('stale_activation','Loop activation configuration changed.')
        if activation['state']!='Active':raise ContractError('activation_inactive','Loop activation is not active.')
        self.activations._valid_configuration(scope,project,activation)
        if len(self.activations._history(project))>=512 or len(self._rows(project))>=2048:
            raise ContractError('processing_loop_history_limit','Control history full; dispatch frozen.')
        return activation

    def create(self,scope,project,*,loop_id,activation_id,activation_sha256,max_passes,max_sources_per_pass,max_total_sources,interval_seconds,expires_at,reason):
        identifier(loop_id);identifier(activation_id);ModelActivationService._reason(reason)
        for value,ceiling in ((max_passes,300),(max_sources_per_pass,10),(max_total_sources,10)):
            if type(value) is not int or not 1<=value<=ceiling:raise ContractError('invalid_processing_loop','Explicit bounded pass and source limits required.')
        if type(interval_seconds) not in (int,float) or not .25<=interval_seconds<=60 or type(expires_at) is not int or expires_at<=time.time():
            raise ContractError('invalid_processing_loop','Explicit bounded interval and future expiry required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            activation=self.activations._current(project,activation_id)
            if activation['actor']!=scope.principal_id or activation['configuration_sha256']!=activation_sha256 or expires_at>activation['expires_at']:
                raise ContractError('invalid_processing_loop','Exact owned activation and no expiry extension required.')
            self.activations._valid_configuration(scope,project,activation)
            config=dict(id=loop_id,kind='configured',activation_id=activation_id,activation_sha256=activation_sha256,
                actor=scope.principal_id,authority_revision=self.core.authority.revision(),max_passes=max_passes,
                max_sources_per_pass=max_sources_per_pass,max_total_sources=max_total_sources,interval_seconds=interval_seconds,expires_at=expires_at,reason=reason)
            config['configuration_sha256']=digest(canonical(config))
            old=next((r for r in self._rows(project) if r['kind']=='configured' and r['id']==loop_id),None)
            if old:
                if old!=config:raise ContractError('idempotency_conflict','Loop configuration cannot reset its limits.')
                return old
            self._save(scope,project,config);return config

    def stop(self,scope,project,*,loop_id,configuration_sha256,reason):
        identifier(loop_id);ModelActivationService._reason(reason)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            config=self._config(project,loop_id)
            if config['actor']!=scope.principal_id or config['configuration_sha256']!=configuration_sha256:
                raise ContractError('processing_loop_denied','Exact owned loop configuration required.')
            if not self._state(project,config)['stopped']:
                self._save(scope,project,dict(id=loop_id,kind='stopped',actor=scope.principal_id,reason=reason,recorded_at=time.time()))
            return dict(id=loop_id,status='Stopped')

    def require_pass(self,scope,project,loop_id,pass_id,grant):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        config=self._config(project,identifier(loop_id));activation=self._authority(scope,project,config);state=self._state(project,config)
        self.activations.require(scope,project,config['activation_id'],grant,activation['revision'])
        if state['stopped'] or state['review_required'] or not any(p['pass_id']==pass_id for p in state['pending']):
            raise ContractError('processing_loop_stopped','Loop stopped, changed or no longer owns this pass.')
        return config

    def execute_pass(self,scope,project,*,loop_id,configuration_sha256,registry):
        identifier(loop_id)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            config=self._config(project,loop_id);self._authority(scope,project,config)
            if hasattr(registry,'for_activation'):registry=registry.for_activation(config['activation_id'])
            if config['configuration_sha256']!=configuration_sha256:raise ContractError('processing_loop_denied','Exact loop configuration required.')
            state=self._state(project,config)
            if state['stopped']:return dict(id=loop_id,status='Stopped',attempted=0)
            if state['review_required']:return dict(id=loop_id,status='Review required',attempted=0)
            if state['pending']:return dict(id=loop_id,status='Unfinished pass',attempted=0)
            remaining=config['max_total_sources']-state['reserved_or_attempted']
            if state['passes']>=config['max_passes'] or remaining<=0:return dict(id=loop_id,status='Limit reached',attempted=0)
            if state['passes']:
                last=max(r['recorded_at'] for r in self._rows(project) if r['id']==loop_id and r['kind']=='pass_finished')
                if time.time()<last+config['interval_seconds']:return dict(id=loop_id,status='Waiting for interval',attempted=0)
            if getattr(registry,'activation_id',None)!=config['activation_id'] or not hasattr(registry,'bind_scope'):
                raise ContractError('processing_loop_model_required','Matching managed transport must be explicitly configured.')
            pass_id='pass_'+uuid.uuid4().hex;allowance=min(config['max_sources_per_pass'],remaining)
            self._save(scope,project,dict(id=loop_id,kind='pass_started',pass_id=pass_id,allowance=allowance,recorded_at=time.time()))
        # A crash after this claim is intentionally not retried after restart.
        base=registry.bind_scope(self.core,scope,project)
        def factory(source,grant):
            with self.core.read_snapshot():
                try:self.require_pass(scope,project,loop_id,pass_id,grant)
                except ContractError as error:
                    if error.code in ('processing_loop_stopped','activation_inactive','activation_denied','model_grant_required','activation_history_limit','processing_loop_expired','processing_loop_permission_changed','processing_loop_history_limit'):return None
                    raise
            extractor=base(source,grant)
            if extractor is not None:extractor.processing_loop_id=loop_id;extractor.processing_pass_id=pass_id
            return extractor
        try:
            result=ConversationQueue(self.core).process(scope,project,extractor_factory=factory,limit=allowance)
            affected={r['source_id'] for r in result['outcomes']}
            analyses=[r for r in self.sources._rows(project,'conversation_analysis_finished') if r['source'] in affected]
            review=any(r['status']!='Ready for review' for r in result['outcomes']) or any(r.get('budget_status') in ('unknown','overrun') for r in analyses)
            value=dict(id=loop_id,kind='pass_finished',pass_id=pass_id,attempted=result['attempted'],review_required=bool(review),outcomes=result['outcomes'],recorded_at=time.time())
        except Exception:
            # Keep the pessimistic claim if auth/storage no longer permits a receipt.
            with self.core.transaction():
                self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
                self._save(scope,project,dict(id=loop_id,kind='pass_finished',pass_id=pass_id,attempted=allowance,review_required=True,outcomes=[],recorded_at=time.time()))
            raise
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            self._save(scope,project,value)
        return dict(id=loop_id,status='Review required' if review else ('Pass finished' if value['attempted'] else 'Waiting for grant'),attempted=value['attempted'],outcomes=value['outcomes'])

    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project);items=[];history=self._rows(project)
            for config in (r for r in history if r['kind']=='configured'):
                state=self._state(project,config);status='Configured'
                if state['stopped']:status='Stopped'
                elif len(history)>=2048:status='History capacity reached'
                elif state['pending']:status='Unfinished pass'
                elif state['review_required']:status='Review required'
                elif config['expires_at']<=time.time():status='Expired'
                elif config['authority_revision']!=self.core.authority.revision():status='Permission changed'
                elif state['passes']>=config['max_passes'] or state['reserved_or_attempted']>=config['max_total_sources']:status='Limit reached'
                items.append(dict(id=config['id'],activation_id=config['activation_id'],configuration_sha256=config['configuration_sha256'],status=status,
                    passes=state['passes'],reserved_or_attempted=state['reserved_or_attempted'],max_sources_per_pass=config['max_sources_per_pass'],max_passes=config['max_passes'],max_total_sources=config['max_total_sources'],interval_seconds=config['interval_seconds'],expires_at=config['expires_at'],automatic_recovery=False))
            return dict(items=items,creates_grants=False,renews_budget=False)

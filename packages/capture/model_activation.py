"""Persistent control of already-authorized exact source grants.

Activation is not source discovery, data-sharing consent or a new money budget.
It can only narrow existing grants. Pause/revoke fences new analysis admission;
an already admitted external call cannot be recalled.
"""
import time
from packages.capture.conversations import ConversationService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest


class ModelActivationService:
    ACTION='conversation_model_activation'

    def __init__(self,core):
        self.core=core;self.sources=ConversationService(core)

    def _history(self,project):
        return self.sources._rows(project,self.ACTION)

    def _current(self,project,activation_id):
        row=next((v for v in reversed(self._history(project)) if v['id']==activation_id),None)
        if row is None:raise ContractError('activation_unavailable','Model activation unavailable.')
        return row

    def _grant(self,scope,project,grant_id):
        grant=next((g for g in self.sources._rows(project,'conversation_dispatch_authorized') if g['id']==grant_id),None)
        if (grant is None or grant['actor']!=scope.principal_id or
                grant['authority_revision']!=self.core.authority.revision() or grant['expires_at']<=time.time() or
                'context_sha256' not in grant):
            raise ContractError('model_grant_required','A current context-bound human source grant is required.')
        source=self.sources._source(project,grant['source'])
        if source['sha256']!=grant['sha256']:raise ContractError('stale_source','Source grant is stale.')
        return grant

    def _save(self,scope,project,value):
        if len(self._history(project))>=512:
            raise ContractError('activation_history_limit','Activation history is full; existing history is preserved.')
        self.sources._put(scope,project,self.ACTION,value)
        return value

    def create(self,scope,project,*,activation_id,grant_ids,expires_at,reason):
        identifier(activation_id)
        if (type(grant_ids) is not list or not 1<=len(grant_ids)<=10 or
                any(type(g) is not str for g in grant_ids) or len(set(grant_ids))!=len(grant_ids) or
                type(expires_at) is not int or expires_at<=time.time()):
            raise ContractError('invalid_activation','One to ten exact grants and a future expiry are required.')
        for g in grant_ids:identifier(g)
        self._reason(reason)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            grants=[self._grant(scope,project,g) for g in sorted(grant_ids)]
            if any(expires_at>g['expires_at'] for g in grants):
                raise ContractError('invalid_activation','Activation cannot outlive a source grant.')
            config=dict(id=activation_id,actor=scope.principal_id,authority_revision=self.core.authority.revision(),expires_at=expires_at,
                        grants=[dict(id=g['id'],sha256=digest(canonical(g))) for g in grants])
            fingerprint=digest(canonical(config))
            old=next((v for v in self._history(project) if v['id']==activation_id),None)
            if old:
                if old['configuration_sha256']!=fingerprint or old['reason']!=reason:
                    raise ContractError('idempotency_conflict','Activation identity already belongs to a different configuration.')
                return self._current(project,activation_id)
            return self._save(scope,project,dict(**config,configuration_sha256=fingerprint,revision=1,state='Paused',reason=reason,recorded_at=time.time()))

    @staticmethod
    def _reason(reason):
        if type(reason) is not str or not reason.strip() or len(reason)>1024:
            raise ContractError('invalid_activation','A bounded explicit reason is required.')

    def transition(self,scope,project,*,activation_id,base_revision,configuration_sha256,state,reason):
        identifier(activation_id);self._reason(reason)
        if state not in ('Active','Paused','Revoked') or type(base_revision) is not int:
            raise ContractError('invalid_activation','Typed revision and supported activation state required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            current=self._current(project,activation_id)
            if current['actor']!=scope.principal_id:raise ContractError('activation_denied','Only the activation owner can change it.')
            if current['revision']!=base_revision or current['configuration_sha256']!=configuration_sha256:
                raise ContractError('stale_activation','Refresh the exact current activation revision and configuration.')
            if current['state']=='Revoked' or current['state']==state:
                raise ContractError('activation_transition_denied','Revoked activation is terminal; choose a different supported state.')
            if state=='Active':
                self._valid_configuration(scope,project,current)
            value=dict(current,state=state,revision=base_revision+1,reason=reason,recorded_at=time.time())
            return self._save(scope,project,value)

    def _valid_configuration(self,scope,project,current):
        if (current['actor']!=scope.principal_id or current['authority_revision']!=self.core.authority.revision() or
                current['expires_at']<=time.time()):
            raise ContractError('activation_inactive','Activation expired or permission changed; no automatic renewal.')
        for ref in current['grants']:
            if digest(canonical(self._grant(scope,project,ref['id'])))!=ref['sha256']:
                raise ContractError('activation_inactive','Exact source grant changed.')

    def control_required(self,project,grant):
        ref=dict(id=grant['id'],sha256=digest(canonical(grant)))
        return any(ref in row['grants'] for row in self._history(project))

    def require(self,scope,project,activation_id,grant,revision):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        if len(self._history(project))>=512:
            raise ContractError('activation_history_limit','Control history is full; new dispatch is frozen until explicit maintenance.')
        current=self._current(project,identifier(activation_id))
        if current['state']!='Active' or current['revision']!=revision:
            raise ContractError('activation_inactive','Activation paused, revoked or changed before dispatch.')
        self._valid_configuration(scope,project,current)
        if dict(id=grant['id'],sha256=digest(canonical(grant))) not in current['grants']:
            raise ContractError('activation_denied','This exact source grant is not in the activation.')
        return current

    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            latest={};history=self._history(project)
            for row in history:latest[row['id']]=row
            result=[]
            for row in latest.values():
                status=row['state']
                if status!='Revoked' and row['expires_at']<=time.time():status='Expired'
                elif status!='Revoked' and len(history)>=512:status='History capacity reached'
                elif status!='Revoked' and row['authority_revision']!=self.core.authority.revision():status='Permission changed'
                result.append(dict(id=row['id'],revision=row['revision'],state=row['state'],effective_state=status,
                    configuration_sha256=row['configuration_sha256'],expires_at=row['expires_at'],grant_count=len(row['grants']),
                    actor=row['actor'],authority_revision=row['authority_revision']))
            return dict(items=result,background_worker_active=False,creates_grants=False,grants_new_budget=False)


class ManagedResponsesFactory:
    """Trusted transport registry plus durable activation; no external call at bind."""
    def __init__(self,registry,activation_id):
        self.registry=registry;self.activation_id=identifier(activation_id)

    def bind_scope(self,core,scope,project):
        def factory(source,grant):
            service=ModelActivationService(core)
            with core.read_snapshot():
                core.scope(scope,project,write=True,human=True);core.active(scope,project)
                try:
                    current=service._current(project,self.activation_id)
                    service.require(scope,project,self.activation_id,grant,current['revision'])
                except ContractError as error:
                    if error.code in ('activation_unavailable','activation_inactive','activation_denied','activation_history_limit','model_grant_required'):return None
                    raise
            extractor=self.registry(source,grant)
            if extractor is not None:
                extractor.activation_id=self.activation_id;extractor.activation_revision=current['revision']
            return extractor
        return factory

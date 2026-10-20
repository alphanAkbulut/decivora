"""Exact source/context sharing approval, independently from capture and dispatch.

Trusted startup profile supplies transport and existing spending policy. UI cannot
change its money ceiling, credential path, ledger, provider or period.
"""
from dataclasses import dataclass
import time
from packages.capture.conversations import ConversationService
from packages.capture.dialogue_review import DialogueReviewService
from packages.capture.responses_extractor import request_payload,ResponsesExtractor
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.privacy.secrets import ensure_safe

@dataclass(frozen=True)
class SharingProfile:
    id:str
    models:tuple
    expires_at:int
    max_input_tokens:int
    max_output_tokens:int
    max_cost_microusd:int
    max_http_attempts:int
    token_cap:int
    policy_sha256:str
    send:object
    def __post_init__(self):
        identifier(self.id)
        if (type(self.models) is not tuple or not self.models or any(type(m) is not str or not m for m in self.models) or
            any(type(v) is not int or v<=0 for v in (self.expires_at,self.max_input_tokens,self.max_output_tokens,self.max_cost_microusd,self.max_http_attempts,self.token_cap)) or
            self.max_cost_microusd>3000000 or self.max_http_attempts>200 or self.max_input_tokens>10000 or self.max_output_tokens>2000 or self.token_cap>100000 or not callable(self.send)):
            raise ContractError('invalid_model_configuration','Explicit bounded trusted sharing profile required.')
    def summary(self):
        return dict(id=self.id,models=list(self.models),expires_at=self.expires_at,max_input_tokens=self.max_input_tokens,max_output_tokens=self.max_output_tokens,max_cost_microusd=self.max_cost_microusd,max_http_attempts=self.max_http_attempts,token_cap=self.token_cap,policy_sha256=self.policy_sha256,status='Available' if self.expires_at>time.time() else 'Expired')

class SourceSharingService:
    PLAN='source_sharing_prepared';APPROVAL='source_sharing_approved'
    def __init__(self,core,profile=None):self.core=core;self.profile=profile;self.sources=ConversationService(core)
    def rows(self,project,action):return self.sources._rows(project,action)
    def _profile(self):
        if self.profile is None:raise ContractError('sharing_not_configured','A trusted sharing transport profile is required.')
        if self.profile.expires_at<=time.time():raise ContractError('sharing_policy_expired','The existing spending period expired; no automatic renewal.')
        return self.profile
    def _current(self,scope,project,plan):
        profile=self._profile();self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        if plan['actor']!=scope.principal_id or plan['authority_revision']!=self.core.authority.revision() or plan['policy_sha256']!=profile.policy_sha256 or plan['expires_at']<=time.time():raise ContractError('sharing_plan_stale','Sharing scope, authority, policy or expiry changed.')
        package=DialogueReviewService(self.core)._package(scope,project,plan['source'],plan['context_sha256'])
        source=self.sources._source(project,plan['source'])
        request=DialogueReviewService(self.core)._prepare(scope,project,source_id=source['id'])['request']
        payload=request_payload(source,model=plan['model'],max_output_tokens=plan['max_output_tokens'],dialogue_request=request)
        if digest(canonical(payload))!=plan['payload_sha256'] or source['sha256']!=plan['source_sha256']:raise ContractError('sharing_plan_stale','Exact model payload changed; review a new plan.')
        return source,package,payload
    def prepare(self,scope,project,*,source_id,model,max_output_tokens,reserved_tokens,expires_at,reason):
        profile=self._profile()
        if model not in profile.models or type(max_output_tokens) is not int or not 1<=max_output_tokens<=profile.max_output_tokens or type(reserved_tokens) is not int or reserved_tokens!=profile.max_input_tokens+max_output_tokens or type(expires_at) is not int or not time.time()<expires_at<=profile.expires_at or type(reason) is not str or not 1<=len(reason.strip())<=1024:raise ContractError('invalid_model_grant','Explicit model, token scope, expiry and sharing reason within the existing policy are required.')
        with self.core.transaction():
            prepared=DialogueReviewService(self.core)._prepare(scope,project,source_id=source_id);source=self.sources._source(project,source_id)
            payload=request_payload(source,model=model,max_output_tokens=max_output_tokens,dialogue_request=prepared['request'])
            plan=dict(source=source_id,source_sha256=source['sha256'],context_sha256=prepared['context_sha256'],payload_sha256=digest(canonical(payload)),model=model,max_output_tokens=max_output_tokens,reserved_tokens=reserved_tokens,expires_at=expires_at,reason=reason,actor=scope.principal_id,authority_revision=self.core.authority.revision(),policy_sha256=profile.policy_sha256,root_run='sharing_'+profile.policy_sha256[:24])
            ensure_safe(plan);plan['id']='sharing_'+digest(canonical(plan))[:24]
            if not any(p['id']==plan['id'] for p in self.rows(project,self.PLAN)):self.sources._put(scope,project,self.PLAN,plan)
            return dict(plan=plan,preview=prepared['request'],profile=profile.summary(),dispatch_started=False)
    def approve(self,scope,project,*,plan_id,consent):
        identifier(plan_id)
        if consent is not True:raise ContractError('sharing_consent_required','Review the exact source and context before sharing approval.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            plan=next((p for p in self.rows(project,self.PLAN) if p['id']==plan_id),None)
            if plan is None:raise ContractError('review_unavailable','Sharing plan unavailable.')
            old=next((r for r in self.rows(project,self.APPROVAL) if r['id']==plan_id),None)
            if old:
                if old['actor']!=scope.principal_id:raise ContractError('sharing_consent_required','Only the original sharing owner may replay approval.')
                return old
            self._current(scope,project,plan);profile=self._profile()
            row=self.core.db.execute('SELECT token_cap FROM run_budgets WHERE workspace=? AND project=? AND run=?',(self.core.workspace,project,plan['root_run'])).fetchone()
            if row is None:self.core.db.execute('INSERT INTO run_budgets VALUES (?,?,?,?)',(self.core.workspace,project,plan['root_run'],profile.token_cap))
            elif row[0]!=profile.token_cap:raise ContractError('sharing_plan_stale','Existing token budget cannot be reset or enlarged.')
            grant=self.sources._authorize_analysis(scope,project,source_id=plan['source'],key='grant_'+plan_id,root_run=plan['root_run'],reserved_tokens=plan['reserved_tokens'],provider='OpenAI Responses configured transport',model=plan['model'],max_output_tokens=plan['max_output_tokens'],expires_at=plan['expires_at'],reason=plan['reason'],context_sha256=plan['context_sha256'])
            receipt=dict(id=plan_id,grant_id=grant['id'],source=plan['source'],payload_sha256=plan['payload_sha256'],actor=scope.principal_id,dispatch_started=False)
            self.sources._put(scope,project,self.APPROVAL,receipt);return receipt
    def analyze_approved(self,scope,project,*,plan_id,start):
        """Explicit one-source activation + queue pass, never future-source consent.

        Sharing approval alone still does not dispatch. A repeated start may read
        an existing result, but cannot retry an unfinished or failed analysis.
        """
        identifier(plan_id)
        if start is not True:
            raise ContractError('sharing_consent_required','Explicit start of the approved one-source analysis is required.')
        from packages.capture.model_activation import ModelActivationService
        from packages.capture.processing_queue import ConversationQueue
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            plan=next((p for p in self.rows(project,self.PLAN) if p['id']==plan_id and p['actor']==scope.principal_id),None)
            approval=next((a for a in self.rows(project,self.APPROVAL) if a['id']==plan_id and a['actor']==scope.principal_id),None)
            if plan is None or approval is None or approval['source']!=plan['source'] or approval['payload_sha256']!=plan['payload_sha256']:
                raise ContractError('sharing_consent_required','Current human approval of this exact source plan is required.')
            finished=next((a for a in reversed(self.rows(project,'conversation_analysis_finished')) if a['source']==plan['source']),None)
            if finished:
                return dict(source=plan['source'],status=finished['status'],attempted=0,reused_result=True,canonical_apply=False)
            if any(a['source']==plan['source'] for a in self.rows(project,'conversation_analysis_started')):
                raise ContractError('analysis_unknown','An unfinished analysis cannot be retried automatically.')
            self._current(scope,project,plan)
            service=ModelActivationService(self.core)
            activation=service._create(scope,project,activation_id='analysis_'+plan_id,
                grant_ids=[approval['grant_id']],expires_at=plan['expires_at'],reason='Explicit start of one approved source analysis.')
            # Only a newly configured Paused activation can be started here.
            # Replaying this convenience command cannot undo a user's pause/revoke.
            if activation['state']=='Paused' and activation['revision']==1:
                activation=service._transition(scope,project,activation_id=activation['id'],base_revision=1,
                    configuration_sha256=activation['configuration_sha256'],state='Active',reason='Explicit start of one approved source analysis.')
            if activation['state']!='Active':
                raise ContractError('activation_inactive','The existing analysis activation was paused or revoked; review its controls explicitly.')
            service._valid_configuration(scope,project,activation)
        registry=SharingResponsesFactory(self.profile,activation['id'])
        result=ConversationQueue(self.core).process(scope,project,extractor_factory=registry.bind_scope(self.core,scope,project),limit=1,source_ids=[plan['source']],grant_ids=[approval['grant_id']])
        outcome=next((o for o in result['outcomes'] if o['source_id']==plan['source']),None)
        return dict(source=plan['source'],status=outcome['status'] if outcome else result['status'],
                    attempted=result['attempted'],reused_result=False,canonical_apply=False,
                    **({'code':outcome['code']} if outcome and 'code' in outcome else {}))

    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project)
            return dict(profile=self.profile.summary() if self.profile else None,approvals=[r for r in self.rows(project,self.APPROVAL) if r['actor']==scope.principal_id],creates_money_budget=False,automatic_dispatch=False)

class SharingResponsesFactory:
    def __init__(self,profile,activation_id=None):self.profile=profile;self.activation_id=activation_id
    def for_activation(self,activation_id):return SharingResponsesFactory(self.profile,identifier(activation_id))
    def bind_scope(self,core,scope,project):
        def factory(source,grant):
            service=SourceSharingService(core,self.profile)
            try:service._profile()
            except ContractError:return None
            approved=next((r for r in service.rows(project,service.APPROVAL) if r['grant_id']==grant['id'] and r['source']==source['id'] and r['actor']==scope.principal_id),None)
            if approved is None or grant['model'] not in self.profile.models or grant['max_output_tokens']>self.profile.max_output_tokens:return None
            plan=next((p for p in service.rows(project,service.PLAN) if p['id']==approved['id']),None)
            if plan is None or plan['policy_sha256']!=self.profile.policy_sha256:return None
            from packages.capture.model_activation import ModelActivationService
            activation=ModelActivationService(core);latest={r['id']:r for r in activation._history(project)};ref=dict(id=grant['id'],sha256=digest(canonical(grant)))
            options=[r for r in latest.values() if ref in r['grants'] and (self.activation_id is None or self.activation_id==r['id'])]
            for record in reversed(options):
                try:activation.require(scope,project,record['id'],grant,record['revision'])
                except ContractError:continue
                def send(payload):
                    service._profile()
                    if digest(canonical(payload))!=approved['payload_sha256']:raise ContractError('sharing_plan_stale','Payload differs from the human-approved preview.')
                    return self.profile.send(payload)
                extractor=ResponsesExtractor(send,model=grant['model'],max_output_tokens=grant['max_output_tokens'],authorized=True,grant_id=grant['id'],dialogue_review=True)
                extractor.activation_id=record['id'];extractor.activation_revision=record['revision'];return extractor
            return None
        return factory

def profile_from_policy(policy_file,ledger,key_file):
    """Load explicit local policy metadata, never its key or host/network at startup."""
    import json
    from pathlib import Path
    from packages.capture.openai_transport import PilotTransport,PRICE_REVISION,RATES,fingerprint
    policy=json.loads(Path(policy_file).read_text());ensure_safe(policy)
    expected={'approval_ref','price_revision','expires_at','max_http_attempts','max_cost_microusd','max_input_tokens','max_output_tokens','budget_scope','prior_usage'}
    if type(policy) is not dict or set(policy)!=expected or policy['budget_scope']!='decivora-development-2026-10-19-usd3':raise ContractError('invalid_model_configuration','Explicit existing shared development policy required; no new billing scope is inferred.')
    if policy.get('price_revision')!=PRICE_REVISION:raise ContractError('invalid_model_configuration','Explicitly adopted price revision required.')
    policy_sha=digest(canonical(policy))
    def send(payload):return PilotTransport(ledger,manifest=dict(policy,payloads=[fingerprint(payload)]),key_file=key_file)(payload)
    return SharingProfile('configured_policy',tuple(RATES),policy['expires_at'],policy['max_input_tokens'],policy['max_output_tokens'],policy['max_cost_microusd'],policy['max_http_attempts'],100000,policy_sha,send)

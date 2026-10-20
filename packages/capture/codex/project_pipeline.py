"""One selected Codex capture -> already-authorized model queue -> review pass.

Never creates egress grants, starts a host turn, approves proposals or marks Done.
"""
import json
from packages.capture.codex.app_server import CodexAppServerCapture
from packages.capture.conversations import ConversationService
from packages.capture.processing_queue import ConversationQueue
from packages.domain.source_event import ContractError

class CodexProjectPipeline:
    def __init__(self,core):self.core=core;self.capture=CodexAppServerCapture(core)
    def tick_selected(self,scope,project,*,selections,extractor_factory=None,turn_limit=10,source_limit=1):
        """One bounded pass over explicit bindings, with a shared processing cap.

        No discovery, grant creation, background loop or automatic approval.
        A failed host preserves accepted pages and does not suppress another host.
        """
        if type(selections) is not list or not 1<=len(selections)<=4:
            raise ContractError('invalid_request','Select one to four explicit capture bindings.')
        if type(source_limit) is not int or not 1<=source_limit<=10 or type(turn_limit) is not int or not 1<=turn_limit<=10:
            raise ContractError('invalid_request','Bounded aggregate source and per-thread turn limits required.')
        seen=set();ids=set()
        # Preflight every selected binding before any host read or model dispatch.
        with self.core.read_snapshot():
            for selection in selections:
                if type(selection) is not dict or set(selection)!={'capture_id','client'}:
                    raise ContractError('invalid_request','An exact capture ID and local read client are required.')
                cid=selection['capture_id']
                if type(cid) is not str or cid in ids:raise ContractError('invalid_request','Capture selections must be unique.')
                binding=self.capture._authorize(scope,project,cid)
                origin=(getattr(selection['client'],'profile_ref',None),binding['thread_id'])
                if origin in seen:raise ContractError('invalid_request','Select each native conversation once.')
                seen.add(origin);ids.add(cid)
        captures=[];selected=[];errors=[]
        for selection in selections:
            cid=selection['capture_id'];client=selection['client']
            try:
                receipt=self.capture.collect(scope,project,capture_id=cid,client=client,limit=turn_limit)
                session_sources=self._selected_sources(scope,project,cid,client)
                selected.extend(session_sources)
                roles=sorted({s['capture']['observed_actor'] for s in session_sources})
                human=bool(set(roles)&{'human','user'})
                captures.append(dict(capture_id=cid,status='captured',receipt=receipt,public_roles_observed=roles,
                    human_text_observed=human,warnings=[] if human else ['human_text_not_observed_do_not_claim_full_dialogue']))
            except ContractError as error:
                # Codes only: source text and transport exceptions are not logs.
                errors.append(dict(capture_id=cid,code=error.code))
                captures.append(dict(capture_id=cid,status='failed',code=error.code))
        source_ids=list(dict.fromkeys(s['id'] for s in selected))
        result=self._process(scope,project,source_ids,extractor_factory,source_limit)
        return dict(captures=captures,errors=errors,processing=result['processing'],review_ready=result['review_ready'],
            source_scope='explicit_selected_codex_threads',selected_source_count=len(source_ids),
            canonical_mutations=0,automatic_approval=False,automatic_discovery=False,
            coverage='partial',aggregate_source_limit=source_limit)

    def _selected_sources(self,scope,project,capture_id,client):
        profile=getattr(client,'profile_ref',None)
        with self.core.read_snapshot():
            binding=self.capture._authorize(scope,project,capture_id)
            query="SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND json_extract(ref,'$.source_kind')='codex_app_server' AND json_extract(ref,'$.capture.thread_id')=?"
            params=[self.core.workspace,project,binding['thread_id']]
            if profile is None:query+=" AND json_extract(ref,'$.capture.id')=?";params.append(capture_id)
            else:query+=" AND json_extract(ref,'$.capture.profile_ref')=?";params.append(profile)
            selected=[json.loads(raw) for raw, in self.core.db.execute(query+' ORDER BY seq LIMIT 1001',params)]
            if len(selected)>1000:raise ContractError('capture_limit','Selected-session source window requires explicit reconciliation.')
            return selected

    def _process(self,scope,project,ids,extractor_factory,source_limit):
        result=ConversationQueue(self.core).process(scope,project,extractor_factory=extractor_factory,limit=source_limit,source_ids=ids)
        reviews=[];sources=ConversationService(self.core)
        for outcome in result['outcomes']:
            if outcome['status']!='Ready for review':continue
            current=sources.view(scope,project,source_id=outcome['source_id'])['imports'][0]
            reviews.append(dict(source_id=outcome['source_id'],candidate_count=len(current['candidates']),status_changes=current['status_changes'],answer_proposals=current['answer_proposals'],question_proposals=current['question_proposals'],clarification_proposals=current['clarification_proposals']))
        return dict(processing=result,review_ready=reviews)

    def tick(self,scope,project,*,capture_id,client,extractor_factory=None,turn_limit=10,source_limit=1):
        if type(source_limit) is not int or not 1<=source_limit<=10:raise ContractError('invalid_request','One to ten already-authorized model sources per capture pass required.')
        receipt=self.capture.collect(scope,project,capture_id=capture_id,client=client,limit=turn_limit)
        selected=self._selected_sources(scope,project,capture_id,client)
        roles={s['capture']['observed_actor'] for s in selected}
        processed=self._process(scope,project,[s['id'] for s in selected],extractor_factory,source_limit)
        result=processed['processing'];reviews=processed['review_ready']
        human=bool(roles&{'human','user'})
        return dict(capture=receipt,processing=result,review_ready=reviews,source_scope='selected_codex_thread',public_roles_observed=sorted(roles),human_text_observed=human,warnings=[] if human else ['human_text_not_observed_do_not_claim_full_dialogue'],canonical_mutations=0,automatic_approval=False)

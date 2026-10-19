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
    def tick(self,scope,project,*,capture_id,client,extractor_factory=None,turn_limit=10,source_limit=1):
        if type(source_limit) is not int or not 1<=source_limit<=10:raise ContractError('invalid_request','One to ten already-authorized model sources per capture pass required.')
        receipt=self.capture.collect(scope,project,capture_id=capture_id,client=client,limit=turn_limit)
        profile=getattr(client,'profile_ref',None)
        with self.core.read_snapshot():
            binding=self.capture._authorize(scope,project,capture_id)
            query="SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND json_extract(ref,'$.source_kind')='codex_app_server' AND json_extract(ref,'$.capture.thread_id')=?"
            params=[self.core.workspace,project,binding['thread_id']]
            if profile is None:query+=" AND json_extract(ref,'$.capture.id')=?";params.append(capture_id)
            else:query+=" AND json_extract(ref,'$.capture.profile_ref')=?";params.append(profile)
            selected=[json.loads(raw) for raw, in self.core.db.execute(query+' ORDER BY seq LIMIT 1001',params)]
            if len(selected)>1000:raise ContractError('capture_limit','Selected-session source window requires explicit reconciliation.')
        roles={s['capture']['observed_actor'] for s in selected}
        ids=[s['id'] for s in selected]
        result=ConversationQueue(self.core).process(scope,project,extractor_factory=extractor_factory,limit=source_limit,source_ids=ids)
        reviews=[];sources=ConversationService(self.core)
        for outcome in result['outcomes']:
            if outcome['status']!='Ready for review':continue
            current=sources.view(scope,project,source_id=outcome['source_id'])['imports'][0]
            reviews.append(dict(source_id=outcome['source_id'],candidate_count=len(current['candidates']),status_changes=current['status_changes'],answer_proposals=current['answer_proposals'],question_proposals=current['question_proposals'],clarification_proposals=current['clarification_proposals']))
        human=bool(roles&{'human','user'})
        return dict(capture=receipt,processing=result,review_ready=reviews,source_scope='selected_codex_thread',public_roles_observed=sorted(roles),human_text_observed=human,warnings=[] if human else ['human_text_not_observed_do_not_claim_full_dialogue'],canonical_mutations=0,automatic_approval=False)

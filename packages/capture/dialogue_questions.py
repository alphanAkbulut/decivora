"""Source-supported question drafts; only human review presents a durable question."""
from packages.capture.conversations import ConversationService,anchored
from packages.domain.project_binding import identifier
from packages.domain.questions import QuestionService
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.reconciliation.core import normalized


def schema():
    fields=dict(question_text={'type':'string','minLength':1,'maxLength':2048},
                options={'type':'array','minItems':2,'maxItems':8,'items':{'type':'string','minLength':1,'maxLength':512}},
                quote={'type':'string','minLength':1,'maxLength':4096})
    return dict(type='array',maxItems=32,items=dict(type='object',additionalProperties=False,required=list(fields),properties=fields))


def validate(source,proposals):
    if type(proposals) is not list or len(proposals)>32:
        raise ContractError('invalid_question_proposal','At most 32 source-bound question drafts required.')
    result=[];seen=set()
    for proposal in proposals:
        if type(proposal) is not dict or set(proposal)!={'question_text','options','quote'}:
            raise ContractError('invalid_question_proposal','Exact question, option labels and quote required.')
        text=proposal['question_text'];options=proposal['options']
        if (type(text) is not str or not text.strip() or len(text)>2048 or
                type(options) is not list or not 2<=len(options)<=8 or
                any(type(o) is not str or not o.strip() or len(o)>512 for o in options)):
            raise ContractError('invalid_question_proposal','Bounded question and two to eight literal options required.')
        key=normalized(text)
        if key in seen or len({normalized(o) for o in options})!=len(options):
            raise ContractError('ambiguous_question','Duplicate question or indistinguishable options require clarification.')
        seen.add(key)
        quote=anchored(source,dict(source_id=source['id'],source_sha256=source['sha256'],coverage='unknown',candidates=[dict(type='PendingDecision',title=text[:256],quote=proposal['quote'],intent='proposed')]))['candidates'][0]
        if text not in proposal['quote'] or any(o not in proposal['quote'] for o in options):
            raise ContractError('unsupported_question','Question and every option must appear literally in the unique source quote.')
        identity=digest(canonical([source['id'],proposal]))[:24]
        result.append(dict(id='question_proposal_'+identity,question_id='question_'+identity,question_text=text,
            options=[dict(id='option_'+str(i+1),label=label) for i,label in enumerate(options)],quote=proposal['quote'],start=quote['start'],end=quote['end']))
    return result


class DialogueQuestionService:
    ACTION='conversation_question_reviewed'
    def __init__(self,core):
        self.core=core;self.sources=ConversationService(core);self.questions=QuestionService(core)

    def _duplicates(self,project,proposal):
        return [q['id'] for q in self.questions._view(project)['questions']
                if q['id']==proposal['question_id'] or normalized(q['text'])==normalized(proposal['question_text'])]

    def view(self,scope,project,source_id,analysis):
        self.core.scope(scope,project);self.core.active(scope,project)
        history=self.sources._rows(project,self.ACTION);result=[]
        for proposal in analysis.get('question_proposals',[]):
            reviews=[r for r in history if r['source']==source_id and r['proposal']==proposal['id']]
            result.append(dict(proposal,state=reviews[-1]['state'] if reviews else 'Pending',reviews=reviews,existing_question_matches=self._duplicates(project,proposal),canonical_apply=False))
        return result

    def review(self,scope,project,*,source_id,proposal_id,decision,key,reason):
        for value in (source_id,proposal_id,key):identifier(value)
        if decision not in ('accept','reject','defer') or type(reason) is not str or not reason.strip() or len(reason)>1024:
            raise ContractError('invalid_review','Explicit human review and bounded reason required.')
        request=dict(source_id=source_id,proposal_id=proposal_id,decision=decision,key=key,reason=reason)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            history=self.sources._rows(project,self.ACTION);old=next((r for r in history if r['key']==key),None)
            if old:
                if old['actor']!=scope.principal_id or old['request_digest']!=digest(canonical(request)):
                    raise ContractError('idempotency_conflict','Question review key was reused.')
                return old
            analysis=next((r for r in reversed(self.sources._rows(project,'conversation_analysis_finished')) if r['source']==source_id),None)
            proposal=next((p for p in (analysis or {}).get('question_proposals',[]) if p['id']==proposal_id),None)
            if proposal is None:raise ContractError('proposal_unavailable','Source-bound question draft unavailable.')
            if any(r['source']==source_id and r['proposal']==proposal_id and r['state'] in ('Presented','Rejected') for r in history):
                raise ContractError('proposal_closed','Question draft already has a final review.')
            source=self.sources._source(project,source_id);question=None
            if decision=='accept':
                from packages.capture.dialogue_review import DialogueReviewService
                DialogueReviewService(self.core)._package(scope,project,source_id,analysis['context_sha256'],verify_current=False)
                if self._duplicates(project,proposal):
                    raise ContractError('question_duplicate','A matching question already exists; review or revise it explicitly.')
                question=self.questions._present(scope,project,question=proposal['question_id'],base_revision=0,
                    text=proposal['question_text'],options=proposal['options'],reason=reason,
                    provenance=dict(source=source_id,source_sha256=source['sha256'],proposal=proposal_id))
            receipt=dict(source=source_id,proposal=proposal_id,question=proposal['question_id'],question_revision=question['revision'] if question else None,
                state={'accept':'Presented','reject':'Rejected','defer':'Deferred'}[decision],key=key,actor=scope.principal_id,
                request_digest=digest(canonical(request)),reason=reason,canonical_apply=False)
            self.sources._put(scope,project,self.ACTION,receipt);return receipt

"""Authorized manual conversation input and provider-backed candidate review.

No lexical extraction fallback. Unconfigured model stays visibly waiting.
"""
import json,time
from contextlib import nullcontext
from packages.privacy.secrets import redact_text,ensure_safe,POLICY
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.reconciliation.core import reconcile,normalized
from packages.capture import source_pages

KINDS={'Task','Decision','PendingDecision'}
def output_schema():
    def obj(properties):return dict(type='object',properties=properties,required=list(properties),additionalProperties=False)
    candidate=obj(dict(type=dict(type='string',enum=sorted(KINDS)),title=dict(type='string'),quote=dict(type='string'),intent=dict(type='string',enum=['proposed','reported','planned','rejected'])))
    return obj(dict(source_id=dict(type='string'),source_sha256=dict(type='string'),coverage=dict(type='string',enum=['complete','partial','unknown']),candidates=dict(type='array',items=candidate)))

def anchored(source,output):
    if type(output) is not dict or set(output)!={'source_id','source_sha256','coverage','candidates'} or output['source_id']!=source['id'] or output['source_sha256']!=source['sha256']:raise ContractError('stale_source','Output must bind this exact conversation.')
    if output['coverage'] not in ('complete','partial','unknown') or type(output['candidates']) is not list or len(output['candidates'])>32:raise ContractError('invalid_output','Bounded candidates and coverage required.')
    if source.get('source_kind') in ('codex_exec_jsonl','codex_app_server','claude_code_hook') and output['coverage']=='complete':raise ContractError('coverage_overclaim','Bounded capture cannot establish complete conversation coverage.')
    candidates=[];seen=set()
    for item in output['candidates']:
        if type(item) is not dict or set(item)!={'type','title','quote','intent'} or item['type'] not in KINDS or item['intent'] not in ('proposed','reported','planned','rejected'):raise ContractError('invalid_candidate','Exact typed candidate required.')
        if type(item['title']) is not str or not item['title'].strip() or len(item['title'])>256 or type(item['quote']) is not str or not item['quote'] or len(item['quote'])>4096:raise ContractError('invalid_candidate','Bounded title and literal quote required.')
        start=source['text'].find(item['quote'])
        if start<0 or source['text'].find(item['quote'],start+1)>=0:raise ContractError('ambiguous_quote','Quote must occur exactly once; no guessed source position.')
        identity=digest(canonical(item))
        uniqueness=canonical([item['type'],normalized(item['title']),normalized(item['quote'])])
        if uniqueness in seen:raise ContractError('duplicate_candidate','Repeated candidate in one output.')
        seen.add(uniqueness);candidates.append(dict(item,id='candidate_'+identity[:24],start=start,end=start+len(item['quote'])))
    return dict(candidates=candidates,coverage=output['coverage'])

class ConversationService:
    def __init__(self,core):self.core=core
    def _rows(self,project,action):return [json.loads(raw) for raw, in self.core.db.execute('SELECT ref FROM audit WHERE workspace=? AND project=? AND action=? ORDER BY seq',(self.core.workspace,project,action))]
    def _related(self,project,action,ids):
        if not ids:return []
        placeholders=','.join('?' for _ in ids)
        return [json.loads(raw) for raw, in self.core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action=? AND json_extract(ref,'$.source') IN ("+placeholders+") ORDER BY seq",(self.core.workspace,project,action,*ids))]
    def _put(self,scope,project,action,value):
        if len(canonical(value).encode())>65536:raise ContractError('conversation_limit','Conversation artifact exceeds local limit.')
        ensure_safe(value)
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,canonical(value)))
    def _source(self,project,source_id):
        source=source_pages.find(self.core,project,source_id)
        if source is None:raise ContractError('source_unavailable','Conversation unavailable.')
        return source
    def ingest(self,scope,project,*,text):
        return self._ingest(scope,project,text=text)
    def _ingest(self,scope,project,*,text,capture=None,in_transaction=False):
        """Internal adapter bridge; public manual input cannot claim host provenance."""
        if type(text) is not str or not text.strip() or len(text.encode('utf-8'))>12000:raise ContractError('conversation_limit','Nonempty conversation up to 12000 UTF-8 bytes required.')
        if in_transaction and not self.core.db.in_transaction:raise ContractError('transaction_required','Capture source and cursor require one transaction.')
        with nullcontext() if in_transaction else self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            text,redaction_counts=redact_text(text)
            sha=digest(text)
            identity=sha if capture is None else digest(canonical([capture,sha]))
            source_id='source_'+identity[:24]
            source_pages.install_indexes(self.core)
            old=source_pages.find(self.core,project,source_id)
            if old:return old
            if source_pages.count(self.core,project)>=source_pages.SOURCE_CAPACITY:raise ContractError('conversation_limit','Local source capacity reached; accepted sources remain intact.')
            source=dict(id=source_id,sha256=sha,text=text,source_kind='manual_paste' if capture is None else capture.get('source_surface','codex_exec_jsonl'),actor=scope.principal_id,received_at=time.time(),revision=1)
            if capture is not None:source['capture']=capture
            source['redaction']=dict(policy=POLICY,counts=redaction_counts,original_retained=False)
            self._put(scope,project,'conversation_imported',source)
            self._put(scope,project,'conversation_enqueued',dict(source=source_id,sha256=sha,received_at=source['received_at'],status='Pending authorization'))
            return source
    def authorize_analysis(self,scope,project,*,source_id,key,root_run,reserved_tokens,provider,model,max_output_tokens,expires_at,reason,context_sha256=None):
        """Trusted human configuration only; never inferred from source/model text."""
        identifier(source_id);identifier(key);identifier(root_run)
        if type(reserved_tokens) is not int or not 1<=reserved_tokens<=100000 or type(expires_at) is not int or expires_at<=time.time():raise ContractError('invalid_model_grant','Explicit bounded reservation and future expiry required.')
        if type(max_output_tokens) is not int or not 1<=max_output_tokens<=min(8192,reserved_tokens):raise ContractError('invalid_model_grant','Output ceiling must fit the explicit total reservation.')
        for value in (provider,model,reason):
            if type(value) is not str or not value.strip() or len(value)>1024:raise ContractError('invalid_model_grant','Provider, model and data-sharing reason required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);source=self._source(project,source_id)
            ensure_safe(source)
            if not self.core.db.execute('SELECT 1 FROM run_budgets WHERE workspace=? AND project=? AND run=?',(self.core.workspace,project,root_run)).fetchone():raise ContractError('budget_unavailable','Create the explicit shared run budget first.')
            grant=dict(id=key,source=source_id,sha256=source['sha256'],root_run=root_run,reserved_tokens=reserved_tokens,provider=provider,model=model,max_output_tokens=max_output_tokens,expires_at=expires_at,reason=reason,actor=scope.principal_id,authority_revision=self.core.authority.revision())
            if context_sha256 is not None:
                from packages.capture.dialogue_review import DialogueReviewService
                if type(context_sha256) is not str:raise ContractError('invalid_model_grant','Exact prepared context digest required.')
                DialogueReviewService(self.core)._package(scope,project,source_id,context_sha256)
                grant['context_sha256']=context_sha256
            old=next((g for g in self._rows(project,'conversation_dispatch_authorized') if g['id']==key),None)
            if old:
                if old!=grant:raise ContractError('idempotency_conflict','Dispatch grant identity changed.')
                return old
            self._put(scope,project,'conversation_dispatch_authorized',grant);return grant

    def analyze(self,scope,project,source_id,extractor=None):
        identifier(source_id)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);source=self._source(project,source_id)
            ensure_safe(source)
            old=next((a for a in reversed(self._rows(project,'conversation_analysis_finished')) if a['source']==source_id),None)
            if old:return old
            if extractor is None:return dict(source=source_id,status='Waiting for model',reason='Model access and a bounded data/spend grant are not configured.',candidates=[],model_calls=0)
            if getattr(extractor,'authorized',False) is not True:raise ContractError('model_grant_required','Trusted provider/data/budget authorization required.')
            if any(a['source']==source_id for a in self._rows(project,'conversation_analysis_started')):raise ContractError('analysis_unknown','Previous dispatch may have consumed usage; no automatic retry.')
            grant=next((g for g in self._rows(project,'conversation_dispatch_authorized') if g['id']==getattr(extractor,'grant_id',None)),None)
            if not grant or grant['source']!=source_id or grant['sha256']!=source['sha256'] or grant['provider']!=extractor.provider or grant['model']!=getattr(extractor,'model',None) or grant['max_output_tokens']!=getattr(extractor,'max_output_tokens',None) or grant['actor']!=scope.principal_id or grant['authority_revision']!=self.core.authority.revision() or grant['expires_at']<=time.time():raise ContractError('model_grant_required','Current source/provider/model/budget grant required.')
            from packages.capture.model_activation import ModelActivationService
            activation=ModelActivationService(self.core)
            if getattr(extractor,'activation_id',None) is not None:
                activation.require(scope,project,extractor.activation_id,grant,getattr(extractor,'activation_revision',None))
            elif activation.control_required(project,grant):
                raise ContractError('activation_required','This source grant requires its durable activation gate.')
            if getattr(extractor,'processing_loop_id',None) is not None:
                from packages.capture.processing_loop import ProcessingLoopService
                ProcessingLoopService(self.core).require_pass(scope,project,extractor.processing_loop_id,getattr(extractor,'processing_pass_id',None),grant)
            if getattr(extractor,'dialogue_review',False):
                from packages.capture.dialogue_review import DialogueReviewService
                prepared=DialogueReviewService(self.core)._prepare(scope,project,source_id=source_id)
                if grant.get('context_sha256')!=prepared['context_sha256']:raise ContractError('model_grant_required','This grant does not authorize the exact current task context.')
                extractor=extractor.bind_dialogue_request(prepared['request'])
            reservation_key='analysis_'+source_id
            self.core._reserve(scope,project,grant['root_run'],reservation_key,grant['reserved_tokens'])
            self._put(scope,project,'conversation_analysis_started',dict(source=source_id,sha256=source['sha256'],provider=extractor.provider,grant=grant['id'],root_run=grant['root_run'],reservation_key=reservation_key))
        # No network/model within a DB transaction; accepted receipt survives timeout/crash.
        raw_text=None;failure_stage='provider_call'
        try:
            ensure_safe(source)
            raw=extractor(source);failure_stage='response_validation';ensure_safe(raw);raw_text=canonical(raw)
            if len(raw_text.encode())>16384:raise ContractError('output_limit','Model output exceeds bounded local review size.')
            if getattr(extractor,'dialogue_review',False):
                from packages.capture.dialogue_review import DialogueReviewService
                with self.core.read_snapshot():
                    self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
                    result=DialogueReviewService(self.core).validate_response(scope,project,source,raw)
            else:result=anchored(source,raw)
            finished=dict(source=source_id,status='Ready for review',**result,model_calls=1,provider=extractor.provider)
        except Exception as error:
            from packages.operations.local import safe_code
            code=safe_code(error.code if isinstance(error,ContractError) else 'provider_outcome_unknown')
            finished=dict(source=source_id,status='Analysis failed',candidates=[],coverage='unknown',model_calls=1,provider=extractor.provider,failure_code=code,failure_stage=failure_stage,reason='Provider response failed the output/source contract; usage may be unknown.')
        if raw_text is not None:finished.update(raw_output=raw_text if len(raw_text.encode())<=16384 else None,raw_sha256=digest(raw_text))
        finished['usage']=getattr(extractor,'usage',None)
        usage=finished['usage'];actual=usage.get('total_tokens') if type(usage) is dict else None
        if type(actual) is not int or actual<0:actual=None
        try:
            self.core.settle(scope,project,grant['root_run'],reservation_key,actual)
            finished['budget_status']='unknown' if actual is None else 'settled'
        except ContractError as error:
            if error.code!='usage_overrun':raise
            finished['budget_status']='overrun'
        finished['budget_run']=grant['root_run']
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            self._put(scope,project,'conversation_analysis_finished',finished)
        return finished
    def view(self,scope,project,*,cursor=None,limit=source_pages.PAGE_SIZE,source_id=None):
        with self.core.read_snapshot():
            self.core.scope(scope,project);rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 101',(self.core.workspace,project)).fetchall();existing=dict(records=[dict(id=r[0],version=r[1],body=json.loads(r[2])) for r in rows[:100]],truncated=len(rows)>100,knowledge_revision=self.core.project(scope,project)['knowledge_revision']);result=[]
            source_page=source_pages.page(self.core,project,cursor=cursor,limit=limit,source_id=source_id)
            ids=[source['id'] for source in source_page['sources']]
            finished=self._related(project,'conversation_analysis_finished',ids);started=self._related(project,'conversation_analysis_started',ids);applied=self._related(project,'conversation_candidates_applied',ids)
            for source in source_page['sources']:
                analysis=next((a for a in reversed(finished) if a['source']==source['id']),None);candidates=[]
                if analysis:
                    for c in analysis['candidates']:
                        typed=dict(type=c['type'],title=c['title'],description=c['quote'],intent=c['intent'],source_ref=source['id'])
                        candidates.append(dict(c,comparison=reconcile(typed,existing['records']),applied=any(c['id'] in a['selected'] for a in applied if a['source']==source['id'])))
                from packages.capture.dialogue_review import DialogueReviewService
                from packages.capture.dialogue_relations import DialogueRelationService
                from packages.capture.dialogue_questions import DialogueQuestionService
                status_changes=DialogueReviewService(self.core).statuses(scope,project,source['id'],analysis or {})
                result.append(dict(source=source,analysis=analysis,candidates=candidates,relation_proposals=DialogueRelationService(self.core).view(scope,project,source['id'],analysis or {}),status_changes=status_changes,question_proposals=DialogueQuestionService(self.core).view(scope,project,source['id'],analysis or {}),answer_proposals=DialogueReviewService(self.core).answers(scope,project,source['id'],analysis or {}),status=analysis['status'] if analysis else 'Analysis unknown' if any(a['source']==source['id'] for a in started) else 'Waiting for model',comparison_incomplete=existing['truncated']))
            return dict(imports=result,knowledge_revision=existing['knowledge_revision'],automatic_capture=False,total=source_page['total'],next_cursor=source_page['next_cursor'],has_more=source_page['has_more'])
    def accept(self,scope,project,*,source_id,key,selected,base_revision):
        identifier(source_id);identifier(key)
        if type(selected) is not list or not selected or len(selected)>32 or any(type(v) is not str for v in selected) or len(set(selected))!=len(selected):raise ContractError('invalid_selection','Bounded unique candidate IDs required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            old=next((a for a in self._rows(project,'conversation_candidates_applied') if a['key']==key),None)
            if old:
                if old['source']!=source_id or old['selected']!=selected or old['base_revision']!=base_revision:raise ContractError('idempotency_conflict','Review identity changed.')
                return old['result']
            view=self.view(scope,project,source_id=source_id)
            if type(base_revision) is not int or base_revision!=view['knowledge_revision']:raise ContractError('stale_base','Project changed; refresh candidate comparison before accepting.')
            imported=next((i for i in view['imports'] if i['source']['id']==source_id),None)
            if imported is None or imported['status']!='Ready for review' or imported['comparison_incomplete']:raise ContractError('review_unavailable','Complete local comparison and validated output required.')
            indexed={c['id']:c for c in imported['candidates']};ops=[];attached=[];titles=set()
            for cid in selected:
                if cid not in indexed:raise ContractError('invalid_selection','Unknown candidate.')
                c=indexed[cid]
                name=(c['type'],normalized(c['title']))
                if name in titles:raise ContractError('relationship_review_required','Same-title candidates need separate relationship review.')
                titles.add(name)
                if c['applied'] or c['intent']=='rejected':raise ContractError('invalid_selection','Previously processed/rejected candidate cannot be accepted.')
                recommendation=c['comparison']['recommendation']
                if recommendation=='review_relationship':raise ContractError('relationship_review_required','Possible refinement requires separate relationship review; no overwrite.')
                if recommendation=='attach_source':attached.append(dict(candidate=cid,matches=c['comparison']['matches']));continue
                ops.append(dict(op='create',id=cid,body=dict(type=c['type'],title=c['title'],description=c['quote'])))
            result=dict(status='sources_attached',temp_ids={},event_sequences=[])
            if ops:
                plan=self.core.plan(scope,project,key,ops);result=self.core._apply(scope,plan,self.core._approve(scope,plan))
            self._put(scope,project,'conversation_candidates_applied',dict(key=key,source=source_id,selected=selected,base_revision=base_revision,result=result,attached=attached))
            return result

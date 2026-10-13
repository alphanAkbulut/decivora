"""Authorized manual conversation input and provider-backed candidate review.

No lexical extraction fallback. Unconfigured model stays visibly waiting.
"""
import json,time
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.reconciliation.core import reconcile,normalized

KINDS={'Task','Decision','PendingDecision'}
def output_schema():
    def obj(properties):return dict(type='object',properties=properties,required=list(properties),additionalProperties=False)
    candidate=obj(dict(type=dict(type='string',enum=sorted(KINDS)),title=dict(type='string'),quote=dict(type='string'),intent=dict(type='string',enum=['proposed','reported','planned','rejected'])))
    return obj(dict(source_id=dict(type='string'),source_sha256=dict(type='string'),coverage=dict(type='string',enum=['complete','partial','unknown']),candidates=dict(type='array',items=candidate)))

def anchored(source,output):
    if type(output) is not dict or set(output)!={'source_id','source_sha256','coverage','candidates'} or output['source_id']!=source['id'] or output['source_sha256']!=source['sha256']:raise ContractError('stale_source','Output must bind this exact conversation.')
    if output['coverage'] not in ('complete','partial','unknown') or type(output['candidates']) is not list or len(output['candidates'])>32:raise ContractError('invalid_output','Bounded candidates and coverage required.')
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
    def _put(self,scope,project,action,value):
        if len(canonical(value).encode())>65536:raise ContractError('conversation_limit','Conversation artifact exceeds local limit.')
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,canonical(value)))
    def _source(self,project,source_id):
        source=next((s for s in self._rows(project,'conversation_imported') if s['id']==source_id),None)
        if source is None:raise ContractError('source_unavailable','Conversation unavailable.')
        return source
    def ingest(self,scope,project,*,text):
        if type(text) is not str or not text.strip() or len(text.encode('utf-8'))>12000:raise ContractError('conversation_limit','Nonempty conversation up to 12000 UTF-8 bytes required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            sha=digest(text);old=next((s for s in self._rows(project,'conversation_imported') if s['sha256']==sha),None)
            if old:return old
            if len(self._rows(project,'conversation_imported'))>=32:raise ContractError('conversation_limit','Preview supports 32 imports per project; accepted sources remain intact.')
            source=dict(id='source_'+sha[:24],sha256=sha,text=text,source_kind='manual_paste',actor=scope.principal_id,received_at=time.time(),revision=1)
            self._put(scope,project,'conversation_imported',source);return source
    def analyze(self,scope,project,source_id,extractor=None):
        identifier(source_id)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);source=self._source(project,source_id)
            old=next((a for a in self._rows(project,'conversation_analysis_finished') if a['source']==source_id),None)
            if old:return old
            if extractor is None:return dict(source=source_id,status='Waiting for model',reason='Model access and a bounded data/spend grant are not configured.',candidates=[],model_calls=0)
            if getattr(extractor,'authorized',False) is not True:raise ContractError('model_grant_required','Trusted provider/data/budget authorization required.')
            if any(a['source']==source_id for a in self._rows(project,'conversation_analysis_started')):raise ContractError('analysis_unknown','Previous dispatch may have consumed usage; no automatic retry.')
            self._put(scope,project,'conversation_analysis_started',dict(source=source_id,sha256=source['sha256'],provider=extractor.provider))
        # No network/model within a DB transaction; accepted receipt survives timeout/crash.
        raw_text=None
        try:
            raw=extractor(source);raw_text=canonical(raw)
            if len(raw_text.encode())>16384:raise ContractError('output_limit','Model output exceeds bounded local review size.')
            result=anchored(source,raw)
            finished=dict(source=source_id,status='Ready for review',**result,model_calls=1,provider=extractor.provider)
        except Exception:
            finished=dict(source=source_id,status='Analysis failed',candidates=[],coverage='unknown',model_calls=1,provider=extractor.provider,reason='Provider response failed the output/source contract; usage may be unknown.')
        if raw_text is not None:finished.update(raw_output=raw_text if len(raw_text.encode())<=16384 else None,raw_sha256=digest(raw_text))
        finished['usage']=getattr(extractor,'usage',None)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            self._put(scope,project,'conversation_analysis_finished',finished)
        return finished
    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);rows=self.core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 101',(self.core.workspace,project)).fetchall();existing=dict(records=[dict(id=r[0],version=r[1],body=json.loads(r[2])) for r in rows[:100]],truncated=len(rows)>100,knowledge_revision=self.core.project(scope,project)['knowledge_revision']);finished=self._rows(project,'conversation_analysis_finished');started=self._rows(project,'conversation_analysis_started');applied=self._rows(project,'conversation_candidates_applied');result=[]
            for source in self._rows(project,'conversation_imported'):
                analysis=next((a for a in finished if a['source']==source['id']),None);candidates=[]
                if analysis:
                    for c in analysis['candidates']:
                        typed=dict(type=c['type'],title=c['title'],description=c['quote'],intent=c['intent'],source_ref=source['id'])
                        candidates.append(dict(c,comparison=reconcile(typed,existing['records']),applied=any(c['id'] in a['selected'] for a in applied if a['source']==source['id'])))
                result.append(dict(source=source,analysis=analysis,candidates=candidates,status=analysis['status'] if analysis else 'Analysis unknown' if any(a['source']==source['id'] for a in started) else 'Waiting for model',comparison_incomplete=existing['truncated']))
            return dict(imports=result,knowledge_revision=existing['knowledge_revision'],automatic_capture=False)
    def accept(self,scope,project,*,source_id,key,selected,base_revision):
        identifier(source_id);identifier(key)
        if type(selected) is not list or not selected or len(selected)>32 or any(type(v) is not str for v in selected) or len(set(selected))!=len(selected):raise ContractError('invalid_selection','Bounded unique candidate IDs required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            old=next((a for a in self._rows(project,'conversation_candidates_applied') if a['key']==key),None)
            if old:
                if old['source']!=source_id or old['selected']!=selected or old['base_revision']!=base_revision:raise ContractError('idempotency_conflict','Review identity changed.')
                return old['result']
            view=self.view(scope,project)
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

"""Manual, durable question selections. Selection never authorizes domain apply."""
import json,time
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical

class QuestionService:
    def __init__(self,core):self.core=core
    def _rows(self,project):
        return [dict(sequence=seq,actor=actor,action=action,payload=json.loads(raw)) for seq,actor,action,raw in self.core.db.execute("SELECT seq,actor,action,ref FROM audit WHERE workspace=? AND project=? AND action IN ('question_presented','question_answered','question_state','question_answer_associated') ORDER BY seq",(self.core.workspace,project))]
    def _view(self,project):
        questions={};answers=[]
        for row in self._rows(project):
            value=row['payload']
            if row['action']=='question_presented':
                old=questions.get(value['id']);questions[value['id']]=dict(value,status='Open',selection=None,state_revision=0,history=(old['history'] if old else [])+[row])
            elif row['action']=='question_state':
                q=questions.get(value['question'])
                if q and q['revision']==value['revision']:
                    q.update(status=value['status'],state_revision=q['state_revision']+1)
                    q['history'].append(row)
            else:
                answers.append(row)
                if value['status']=='Selected':
                    q=questions.get(value['question'])
                    if q and q['revision']==value['revision']:q.update(status='Answered',selection=value['option'])
        for q in questions.values():
            for item in q['history']:
                if item['action']=='question_presented':item['snapshot_status']='Current' if item['payload']['revision']==q['revision'] else 'Superseded'
        return dict(questions=list(questions.values()),answers=answers,automatic_association=False,canonical_apply=False)
    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.project(scope,project)
            return self._view(project)
    def _save(self,scope,project,action,value):
        if self.core.db.execute("SELECT COUNT(*) FROM audit WHERE workspace=? AND project=? AND action IN ('question_presented','question_answered','question_state','question_answer_associated')",(self.core.workspace,project)).fetchone()[0]>=512:raise ContractError('question_history_limit','Manual preview history capacity reached; accepted records remain intact.')
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,canonical(value)))
    def present(self,scope,project,*,question,base_revision,text,options,task=None,reason=''):
        identifier(question)
        if type(base_revision) is not int or base_revision<0 or type(text) is not str or not text.strip() or len(text)>2048 or type(options) is not list or not 2<=len(options)<=8:raise ContractError('invalid_question','Bounded question and options required.')
        if type(reason) is not str or len(reason)>1024 or (base_revision>0 and not reason.strip()):raise ContractError('question_change_reason','Question revision change requires a bounded reason.')
        ids=set()
        for option in options:
            if type(option) is not dict or set(option)!={'id','label'}:raise ContractError('invalid_question','Exact option ID and label required.')
            identifier(option['id'])
            if option['id'] in ids or type(option['label']) is not str or not option['label'].strip() or len(option['label'])>512:raise ContractError('invalid_question','Unique options with bounded labels required.')
            ids.add(option['id'])
        if task is not None:identifier(task)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            current=next((q for q in self._view(project)['questions'] if q['id']==question),None)
            if current and current['revision']==base_revision+1:
                old=next(r['payload'] for r in reversed(current['history']) if r['action']=='question_presented')
                if old.get('text')==text and old.get('options')==options and old.get('task')==task and old.get('reason','')==reason and current['responder']==scope.principal_id:return old
            if (current['revision'] if current else 0)!=base_revision:raise ContractError('stale_question','Question revision changed.')
            if current is None and len(self._view(project)['questions'])>=100:raise ContractError('question_limit','Manual preview supports 100 questions per project.')
            if task is not None:
                row=self.core.db.execute('SELECT body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
                if row is None or json.loads(row[0])['type']!='Task':raise ContractError('task_unavailable','Selected Task unavailable.')
            value=dict(id=question,revision=base_revision+1,text=text,options=options,task=task,source_kind='manual_ui',responder=scope.principal_id,presented_at=time.time(),reason=reason)
            self._save(scope,project,'question_presented',value)
            return value
    def answer(self,scope,project,*,request_id,question,revision,option):
        for item in (request_id,question,option):identifier(item)
        if type(revision) is not int or revision<1:raise ContractError('invalid_question','Positive question revision required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            view=self._view(project);value=dict(request_id=request_id,question=question,revision=revision,option=option)
            old=next((r for r in view['answers'] if r['payload']['request_id']==request_id),None)
            if old:
                if old['actor']!=scope.principal_id or any(old['payload'][key]!=v for key,v in value.items()):raise ContractError('answer_conflict','Answer request ID was reused with different content.')
                return old['payload']
            q=next((q for q in view['questions'] if q['id']==question),None)
            status=self._status(q,revision,option)
            value.update(status=status,canonical_apply=False,received_at=time.time())
            self._save(scope,project,'question_answered',value)
            return value

    @staticmethod
    def _status(q,revision,option):
        if q is None:return 'Unmatched'
        if q['revision']!=revision:return 'Stale'
        if q['status'] in ('Cancelled','Deferred'):return q['status']
        if option not in {o['id'] for o in q['options']}:return 'Unmatched'
        if q['selection'] is not None:return 'Duplicate' if q['selection']==option else 'Conflict'
        return 'Selected'
    def transition(self,scope,project,*,request_id,question,revision,base_state,status,reason):
        for value in (request_id,question):identifier(value)
        if type(revision) is not int or revision<1 or type(base_state) is not int or base_state<0 or status not in ('Cancelled','Deferred','Resumed') or type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('invalid_question_state','Exact revision, lifecycle and reason required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            request=dict(request_id=request_id,question=question,revision=revision,base_state=base_state,requested=status,reason=reason)
            old=next((r['payload'] for r in self._rows(project) if r['action']=='question_state' and r['payload']['request_id']==request_id),None)
            if old:
                if any(old[k]!=v for k,v in request.items()):raise ContractError('question_state_conflict','Lifecycle request identity changed.')
                return old
            q=next((q for q in self._view(project)['questions'] if q['id']==question),None)
            if q is None or q['revision']!=revision or q['state_revision']!=base_state:raise ContractError('stale_question','Question lifecycle revision changed.')
            if q['status']=='Cancelled' or (status=='Resumed' and q['status']!='Deferred') or (status=='Deferred' and q['status']=='Deferred'):raise ContractError('invalid_question_transition','Lifecycle transition unavailable.')
            request['status']=('Answered' if q['selection'] else 'Open') if status=='Resumed' else status
            self._save(scope,project,'question_state',request);return request
    def associate(self,scope,project,*,request_id,answer_id):
        identifier(request_id);identifier(answer_id)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            view=self._view(project);old=next((r for r in view['answers'] if r['payload']['request_id']==request_id),None)
            if old:
                if old['payload'].get('original_answer')!=answer_id:raise ContractError('answer_conflict','Association ID content changed.')
                return old['payload']
            original=next((r for r in view['answers'] if r['payload']['request_id']==answer_id),None)
            if original is None or original['actor']!=scope.principal_id or original['payload']['status'] not in ('Unmatched','Deferred'):raise ContractError('answer_unavailable','Only own unmatched/deferred answer may be reassessed.')
            source=original['payload'];q=next((q for q in view['questions'] if q['id']==source['question']),None)
            value=dict(request_id=request_id,original_answer=answer_id,question=source['question'],revision=source['revision'],option=source['option'],status=self._status(q,source['revision'],source['option']),canonical_apply=False,received_at=source['received_at'],associated_at=time.time())
            self._save(scope,project,'question_answer_associated',value);return value

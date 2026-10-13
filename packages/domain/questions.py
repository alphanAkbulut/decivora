"""Manual, durable question selections. Selection never authorizes domain apply."""
import json,time
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical

class QuestionService:
    def __init__(self,core):self.core=core
    def _rows(self,project):
        return [dict(sequence=seq,actor=actor,action=action,payload=json.loads(raw)) for seq,actor,action,raw in self.core.db.execute("SELECT seq,actor,action,ref FROM audit WHERE workspace=? AND project=? AND action IN ('question_presented','question_answered') ORDER BY seq",(self.core.workspace,project))]
    def _view(self,project):
        questions={};answers=[]
        for row in self._rows(project):
            value=row['payload']
            if row['action']=='question_presented':
                old=questions.get(value['id']);questions[value['id']]=dict(value,status='Open',selection=None,history=(old['history'] if old else [])+[row])
            else:
                answers.append(row)
                if value['status']=='Selected':
                    q=questions.get(value['question'])
                    if q and q['revision']==value['revision']:q.update(status='Answered',selection=value['option'])
        return dict(questions=list(questions.values()),answers=answers,automatic_association=False,canonical_apply=False)
    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.project(scope,project)
            return self._view(project)
    def _save(self,scope,project,action,value):
        if self.core.db.execute("SELECT COUNT(*) FROM audit WHERE workspace=? AND project=? AND action IN ('question_presented','question_answered')",(self.core.workspace,project)).fetchone()[0]>=512:raise ContractError('question_history_limit','Manual preview history capacity reached; accepted records remain intact.')
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,canonical(value)))
    def present(self,scope,project,*,question,base_revision,text,options,task=None):
        identifier(question)
        if type(base_revision) is not int or base_revision<0 or type(text) is not str or not text.strip() or len(text)>2048 or type(options) is not list or not 2<=len(options)<=8:raise ContractError('invalid_question','Bounded question and options required.')
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
            if (current['revision'] if current else 0)!=base_revision:raise ContractError('stale_question','Question revision changed.')
            if current is None and len(self._view(project)['questions'])>=100:raise ContractError('question_limit','Manual preview supports 100 questions per project.')
            if task is not None:
                row=self.core.db.execute('SELECT body FROM records WHERE workspace=? AND project=? AND id=?',(self.core.workspace,project,task)).fetchone()
                if row is None or json.loads(row[0])['type']!='Task':raise ContractError('task_unavailable','Selected Task unavailable.')
            value=dict(id=question,revision=base_revision+1,text=text,options=options,task=task,source_kind='manual_ui',responder=scope.principal_id,presented_at=time.time())
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
            if q is None:status='Unmatched'
            elif q['revision']!=revision:status='Stale'
            elif option not in {o['id'] for o in q['options']}:status='Unmatched'
            elif q['status']=='Answered':status='Duplicate' if q['selection']==option else 'Conflict'
            else:status='Selected'
            value.update(status=status,canonical_apply=False,received_at=time.time())
            self._save(scope,project,'question_answered',value)
            return value

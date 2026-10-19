"""Runnable local UI. Loopback, ephemeral session, CSRF/origin checks, explicit writes."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from urllib.parse import urlsplit,parse_qs
from packages.domain.project_binding import identifier
from pathlib import Path
import json,secrets,threading,uuid,webbrowser,argparse,time,sys,re
from collections import deque
from packages.storage.workspace import Workspace
from packages.storage.project_store import canonical
from packages.domain.acceptance import AcceptanceService
from packages.domain.task_blockers import TaskBlockerService
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.work_routing import RoutingService
from packages.domain.agent_proposals import AgentProposalService
from packages.domain.decision_impact import DecisionImpactService
from packages.domain.questions import QuestionService
from packages.domain.question_decisions import QuestionDecisionService
from packages.domain.source_event import ContractError
from packages.capture.conversations import ConversationService

ROOT=Path(__file__).parent
class LocalApp:
    def __init__(self,path,extractor=None,verification_root=None,environment='local',*,extractor_factory=None):
        from packages.operations.environment import bind_environment
        bind_environment(path,environment)
        if environment=='test' and (extractor is not None or extractor_factory is not None or verification_root is not None):raise ContractError('test_connection_disabled','Test environment disables model and file-target connections.')
        self.environment=environment;self.cookie_name='decivora_test_session' if environment=='test' else 'decivora_session';self.started_at=time.time();self.started_monotonic=time.monotonic();self.operations_context=threading.local()
        if extractor is not None and extractor_factory is not None:raise ContractError('invalid_model_configuration','Choose one trusted model configuration.')
        self.extractor=extractor;self.extractor_factory=extractor_factory
        from packages.verification.files import FileChecker
        self.file_checker=FileChecker(verification_root) if verification_root is not None else None
        self.path=Path(path);fresh=not self.path.exists();self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.cookie=secrets.token_urlsafe(32);self.csrf=secrets.token_urlsafe(32);self.bootstrap=secrets.token_urlsafe(32);self.health_lock=threading.Lock();self.recent_errors=deque(maxlen=25);self.backup_lock=threading.Lock();self.rate_lock=threading.Lock();self.window=0;self.writes=0
        with Workspace(self.path,'local_ui_workspace',owner='local_owner' if fresh else None) as core:
            if fresh:
                a=core.authority;a.replace_grant(a.issue_scope('local_owner'),'local_owner',kind='human',readable=frozenset({'personal'}),writable=frozenset({'personal'}),active=True,base_revision=1)
                core.create_project(a.issue_scope('local_owner'),'personal','Benim projem');self.path.chmod(0o600)
            # The local service has overlapping readers and one SQLite writer.
            # Configure once at startup, never during a query or transaction.
            mode=core.db.execute('PRAGMA journal_mode=WAL').fetchone()[0]
            if mode!='wal':raise ContractError('storage_configuration_failed','Local concurrent storage profile could not be enabled.')
            self.storage_journal_mode=mode
        from packages.operations.local import LocalOperations
        self.operations=LocalOperations(self.path.with_suffix('.operations.sqlite'))
        from packages.capture.processing_worker import LocalProcessingWorker
        self.processing_worker=LocalProcessingWorker(self)
    def _queue_view(self,core,owner,project):
        from packages.capture.processing_queue import ConversationQueue
        view=ConversationQueue(core).view(owner,project)
        active=self.processing_worker.view(project)['active']
        return dict(view,background_worker_active=active,automatic_dispatch=active)
    def _source_extractor(self,core,owner,project,source_id):
        if self.extractor_factory is None:return self.extractor
        service=ConversationService(core)
        with core.read_snapshot():
            core.scope(owner,project,write=True,human=True);core.active(owner,project)
            source=service._source(project,source_id)
            grants=[g for g in service._rows(project,'conversation_dispatch_authorized')
                    if g['source']==source_id and g['sha256']==source['sha256']
                    and g['actor']==owner.principal_id and g['authority_revision']==core.authority.revision()
                    and g['expires_at']>time.time()]
        factory=self.extractor_factory.bind_scope(core,owner,project) if hasattr(self.extractor_factory,'bind_scope') else self.extractor_factory
        return factory(source,grants[-1]) if grants else None
    def record_error(self,endpoint,code):
        endpoint=endpoint if endpoint in ('/api/state','/api/command','/api/backup','/api/session','/api/shutdown','/api/conversations') else 'other'
        code=code if type(code) is str and re.fullmatch('[a-z_]{1,64}',code) else 'application_error'
        self.operations.error(endpoint,code)
        with self.health_lock:self.recent_errors.append(dict(id='incident_'+uuid.uuid4().hex[:12],endpoint=endpoint,code=code,recorded_at=time.time()))
    def core(self):
        core=Workspace(self.path,'local_ui_workspace');core.file_checker=self.file_checker;return core
    def backup_bundle(self,body):
        if type(body) is not dict or set(body)!={'acknowledge_private_data'} or body['acknowledge_private_data'] is not True:
            raise ContractError('backup_ack_required','Explicit acknowledgment of private backup contents required.')
        if not self.backup_lock.acquire(blocking=False):raise ContractError('backup_busy','Another backup is already running.')
        try:
            from packages.storage.local_backup import create_bundle
            with self.core() as core:
                owner=core.authority.issue_scope('local_owner');core.scope(owner,human=True)
                return create_bundle(core,owner)
        finally:self.backup_lock.release()
    def state(self,selected='personal'):
        with self.core() as core,core.read_snapshot():
            identifier(selected);owner=core.authority.issue_scope('local_owner');core.scope(owner,selected);core.active(owner,selected)
            project=core.project(owner,selected)
            choices=[]
            for pid in sorted(owner.readable_projects):
                entry=core.db.execute('SELECT name,archived FROM projects WHERE workspace=? AND id=?',(core.workspace,pid)).fetchone()
                if entry:choices.append(dict(id=pid,name=entry[0],archived=bool(entry[1])))
            rows=core.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id LIMIT 101',(core.workspace,selected)).fetchall()
            tasks=[]
            for rid,version,raw in rows[:100]:
                body=json.loads(raw)
                if body['type']!='Task':continue
                workflow=TaskWorkflowService(core).view(owner,selected,rid)
                tasks.append(dict(id=rid,version=version,body=body,lifecycle=core.task_history(owner,selected,rid),acceptance=AcceptanceService(core).view(owner,selected,rid),workflow=workflow,file_bindings=__import__('packages.verification.files',fromlist=['FileVerificationService']).FileVerificationService(core).bindings(selected,rid),rationale=__import__('packages.domain.task_rationale',fromlist=['TaskRationaleService']).TaskRationaleService(core).view(owner,selected,rid),routing=RoutingService(core).view(owner,selected,rid),blocker=TaskBlockerService(core).view(owner,selected,rid),lane=workflow['stage']))
                from packages.domain.blocker_age import assess as blocker_age
                tasks[-1]['blocker_age']=blocker_age(workflow['assessment'],cancelled=body.get('execution')=='cancelled')
            task_sources={}
            for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_candidates_applied'",(core.workspace,selected)):
                receipt=json.loads(raw)
                for rid in receipt['result'].get('temp_ids',{}).values():task_sources.setdefault(rid,[]).append(receipt['source'])
                for attachment in receipt.get('attached',[]):
                    for match in attachment['matches']:
                        rid=match.get('record_id',match.get('id')) if isinstance(match,dict) else match
                        if not rid:raise ContractError('source_link_unavailable','Conversation attachment identity is unavailable.')
                        task_sources.setdefault(rid,[]).append(receipt['source'])
            for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_status_reviewed'",(core.workspace,selected)):
                receipt=json.loads(raw)
                if receipt['state']=='Applied':task_sources.setdefault(receipt['task'],[]).append(receipt['source'])
            relations=[dict(origin=o,target=t,kind=k,revision=rev,state=status,valid_from=start,valid_to=end) for o,t,k,rev,status,start,end in core.db.execute('SELECT origin,target,kind,revision,state,valid_from,valid_to FROM edges WHERE workspace=? AND project=? ORDER BY origin,target,kind LIMIT 501',(core.workspace,selected))]
            timeline=[dict(sequence=seq,stream=stream,version=v,kind=kind) for seq,stream,v,kind in core.db.execute('SELECT seq,stream,version,kind FROM events WHERE workspace=? AND project=? ORDER BY seq DESC LIMIT 101',(core.workspace,selected))]
            audit_timeline=[]
            for seq,action,raw in core.db.execute("SELECT seq,action,ref FROM audit WHERE workspace=? AND project=? AND action IN ('conversation_status_reviewed','task_stage','criterion_evidence','file_criterion_evidence','file_criterion_binding','work_routing','agent_changeset_submitted','agent_changeset_approved','agent_changeset_applied','agent_changeset_rejected') ORDER BY seq DESC LIMIT 100",(core.workspace,selected)):
                item=json.loads(raw);audit_timeline.append(dict(sequence=seq,action=action,task=item.get('task'),status=item.get('stage',item.get('status'))))
            impact_reviews=[]
            for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='impact_preview' ORDER BY seq DESC LIMIT 5",(core.workspace,selected)):
                impact_reviews.append(core.impact_run(owner,selected,json.loads(raw)['run_id']))
            with self.health_lock:health=dict(recent_errors=list(self.recent_errors),persistent=False,capabilities=dict(model_configured=(self.extractor is not None or self.extractor_factory is not None),file_checker_configured=self.file_checker is not None,native_capture=False,mcp_host_activation='not_verified'))
            return dict(environment=self.environment,impact_reviews=impact_reviews,impact_change_reviews=DecisionImpactService(core).reviews(owner,selected),selected_project=selected,project_choices=choices,project_writable=selected in owner.writable_projects,health=health,audit_timeline=audit_timeline,agent_proposals=AgentProposalService(core).view(owner,selected),relations=relations[:500],relations_truncated=len(relations)>500,timeline=timeline[:100],timeline_truncated=len(timeline)>100,usage=RoutingService(core).usage(owner,selected),task_sources=task_sources,conversation_queue=self._queue_view(core,owner,selected),conversation_review=ConversationService(core).view(owner,selected),model_ready=(self.extractor is not None or self.extractor_factory is not None),model_activations={**__import__('packages.capture.model_activation',fromlist=['ModelActivationService']).ModelActivationService(core).view(owner,selected),'background_worker_active':self.processing_worker.view(selected)['active']},processing_worker=self.processing_worker.view(selected),processing_loops=__import__('packages.capture.processing_loop',fromlist=['ProcessingLoopService']).ProcessingLoopService(core).view(owner,selected),project=project,tasks=tasks,records=[dict(id=rid,version=v,body=json.loads(raw)) for rid,v,raw in rows[:100]],question_inbox=QuestionService(core).view(owner,selected),decision_proposals=QuestionDecisionService(core).view(owner,selected),truncated=len(rows)>100,snapshot=project['knowledge_revision'],workflow_preset=list(__import__('packages.domain.task_workflow',fromlist=['STAGES']).STAGES),workflow_transitions={stage:[target for target in __import__('packages.domain.task_workflow',fromlist=['STAGES']).STAGES if target in targets] for stage,targets in __import__('packages.domain.task_workflow',fromlist=['TRANSITIONS']).TRANSITIONS.items()},capabilities=dict(manual_tasks=True,versioned_acceptance=True,automatic_capture=False,semantic_extraction=False,verified_completion=True,verification_methods=['human_review']+(['file_check'] if self.file_checker is not None else []),automatic_verifier=False,file_checker_configured=self.file_checker is not None,file_observation_limited=getattr(core,'file_read_limit_reached',False)),csrf=self.csrf)
    def conversation_page(self,selected='personal',cursor=None,source_id=None):
        with self.core() as core,core.read_snapshot():
            identifier(selected);owner=core.authority.issue_scope('local_owner');core.scope(owner,selected);core.active(owner,selected)
            if source_id is not None:identifier(source_id)
            return ConversationService(core).view(owner,selected,cursor=cursor,source_id=source_id)
    def operations_view(self,selected='personal'):
        with self.core() as core,core.read_snapshot():
            identifier(selected);owner=core.authority.issue_scope('local_owner');core.scope(owner,selected,human=True);core.active(owner,selected)
            queue=dict(core.db.execute('SELECT j.status,count(*) FROM jobs j JOIN sources s ON s.seq=j.source_seq WHERE j.project=? AND s.workspace=? GROUP BY j.status',(selected,core.workspace)))
            result=self.operations.view(selected)
            from packages.capture.processing_queue import ConversationQueue
            result['conversation_queue']=self._queue_view(core,owner,selected)
            result.update(environment=self.environment,project=selected,uptime_seconds=round(time.monotonic()-self.started_monotonic,1),application_processes=1,background_worker_active=self.processing_worker.view(selected)['active'],queue=queue,model_configured=(self.extractor is not None or self.extractor_factory is not None),file_checker_configured=self.file_checker is not None,native_capture=False,external_mcp_host='not_verified')
            return result
    def command(self,body):
        from packages.operations.local import ACTIONS,identity_from_scope
        selected='personal';action='unknown';run=None;started=time.monotonic();self.operations_context.last_id=None
        try:
            value=body.get('command') if type(body) is dict and 'project_id' in body else body
            candidate=value.get('action') if type(value) is dict else None
            if candidate!='import_conversation':
                from packages.privacy.secrets import ensure_safe
                ensure_safe(body)
            action=candidate if type(candidate) is str and candidate in ACTIONS else 'unknown'
            if type(body) is dict and 'project_id' in body:selected=body['project_id']
            # Scope resolution happens before associating a trace with a project.
            with self.core() as core:
                identifier(selected);owner=core.authority.issue_scope('local_owner');core.scope(owner,selected,write=True,human=True);core.active(owner,selected)
                trace_identity=identity_from_scope(core,owner,selected)
            run=self.operations.begin(selected,action,identity=trace_identity);self.operations_context.last_id=run
            with self.operations.span(run,1,'authorization','authorize_project'):
                with self.core() as core:core.scope(core.authority.issue_scope('local_owner'),selected,write=True,human=True)
            with self.operations.span(run,2,ACTIONS.get(action,'api'),'execute_command'):result=self._command(body)
        except Exception as error:
            if run:self.operations.finish(run,started,error)
            raise
        else:self.operations.finish(run,started);return result
    def _command(self,body):
        selected='personal'
        if type(body) is dict and 'project_id' in body:
            if set(body)!={'project_id','command'} or type(body['command']) is not dict:raise ContractError('invalid_request','Exact project command envelope required.')
            selected=identifier(body['project_id']);body=body['command']
        if type(body) is not dict or body.get('action') not in ('bind_file_check','run_file_check','approve_agent_proposal','apply_agent_proposal','reject_agent_proposal','prepare_task_lifecycle','prepare_impact_updates','select_impact_changes','approve_impact_changes','apply_impact_changes','decide_impact_changes','preview_decision_change','work_routing','link_task_rationale','link_dependency','workflow_transition','criterion_evidence','task_blocker','create_task','acceptance','start','ask_question','answer_question','prepare_decision','approve_decision','apply_decision','question_state','associate_answer','revise_question','prepare_dialogue_review','import_dialogue_response','review_dialogue_status','review_dialogue_answer','review_dialogue_relation','save_task_rationale','import_conversation','analyze_conversation','process_conversation_queue','accept_candidates','create_model_activation','change_model_activation','create_processing_loop','run_processing_pass','start_processing_loop','stop_processing_loop','review_dialogue_question'):raise ContractError('invalid_request','Unknown UI action.')
        with self.core() as core:
            owner=core.authority.issue_scope('local_owner');action=body['action']
            if action in ('prepare_task_lifecycle','prepare_impact_updates','select_impact_changes','approve_impact_changes','apply_impact_changes','decide_impact_changes'):
                from packages.domain.review import ReviewService
                fields={'prepare_task_lifecycle':{'action','key','impact_run','tasks','state','reason'},'prepare_impact_updates':{'action','key','impact_run','updates'},'select_impact_changes':{'action','key','selection_id','selected'},'approve_impact_changes':{'action','selection_id'},'apply_impact_changes':{'action','selection_id','approval'},'decide_impact_changes':{'action','key','action_id','decision'}}
                if set(body)!=fields[action]:raise ContractError('invalid_request','Exact impact review fields required.')
                service=ReviewService(core)
                if action=='prepare_task_lifecycle':return DecisionImpactService(core).prepare_lifecycle(owner,selected,**{k:v for k,v in body.items() if k!='action'})
                if action=='prepare_impact_updates':return DecisionImpactService(core).prepare_task_updates(owner,selected,**{k:v for k,v in body.items() if k!='action'})
                if action=='select_impact_changes':return service.select(owner,selected,body['key'],body['selection_id'],body['selected'])
                if action=='approve_impact_changes':return dict(approval=service.approve(owner,selected,body['selection_id']))
                if action=='apply_impact_changes':return service.apply(owner,selected,body['selection_id'],body['approval'])
                return service.decide(owner,selected,body['key'],body['action_id'],body['decision'])
            if action=='save_task_rationale':
                if set(body)!={'action','task','task_version','base_revision','expression','facts','reviewed_complete','reason','key'}:raise ContractError('invalid_request','Exact rationale confirmation fields required.')
                from packages.domain.task_rationale import TaskRationaleService
                return TaskRationaleService(core).save(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='preview_decision_change':
                if set(body) not in ({'action','decision','decision_version','base_revision','key'},{'action','decision','decision_version','base_revision','key','rationale_tasks','decision_active'}):raise ContractError('invalid_request','Exact decision-preview fields required.')
                return DecisionImpactService(core).preview(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('bind_file_check','run_file_check'):
                fields={'action','task','task_version','contract_version','criterion','path','expected_sha256','reason','key'} if action=='bind_file_check' else {'action','task','task_version','contract_version','criterion','binding_revision','key'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact local file-check fields required.')
                from packages.verification.files import FileVerificationService
                service=FileVerificationService(core)
                return (service.bind if action=='bind_file_check' else service.run)(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('approve_agent_proposal','apply_agent_proposal','reject_agent_proposal'):
                fields={'action','key','reason'} if action=='reject_agent_proposal' else {'action','key'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact proposal review fields required.')
                service=AgentProposalService(core)
                if action=='approve_agent_proposal':return service.approve(owner,selected,body['key'])
                if action=='apply_agent_proposal':return service.apply(owner,selected,body['key'])
                return service.reject(owner,selected,body['key'],body['reason'])
            if action=='work_routing':
                if set(body)!={'action','task','task_version','base_revision','work_class','executor','human_suitable','reason','key'}:raise ContractError('invalid_request','Exact routing fields required.')
                return RoutingService(core).set(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('link_dependency','link_task_rationale'):
                if set(body)!={'action','task','target','base_revision','key'}:raise ContractError('invalid_request','Exact dependency approval fields required.')
                with core.transaction():
                    core.scope(owner,selected,write=True,human=True);core.active(owner,selected)
                    service=TaskWorkflowService(core);service._task(selected,body['task'])
                    if action=='link_dependency':service._task(selected,body['target'])
                    else:
                        target=core.db.execute('SELECT body FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,selected,identifier(body['target']))).fetchone()
                        if not target or json.loads(target[0])['type']!='Decision':raise ContractError('invalid_rationale','Select a recorded decision in the same project.')
                    from packages.storage.project_store import digest
                    signature=digest(canonical(body));audit_action='task_dependency_approved' if action=='link_dependency' else 'task_rationale_approved'
                    prior=next((json.loads(raw) for raw, in core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action=?",(core.workspace,selected,audit_action)) if json.loads(raw)['key']==body['key']),None)
                    if prior:
                        if prior['signature']!=signature:raise ContractError('idempotency_conflict','Dependency identity changed.')
                        return prior['result']
                    if type(body['base_revision']) is not int or body['base_revision']!=core.project(owner,selected)['knowledge_revision']:raise ContractError('stale_base','Refresh the dependency preview.')
                    if service._stage(selected,body['task'])['stage']=='Cancelled':raise ContractError('task_cancelled','Cancelled task cannot add an active dependency.')
                    plan=core.plan(owner,selected,body['key'],[dict(op='link',origin=body['task'],target=body['target'],kind='depends_on' if action=='link_dependency' else 'required_by')])
                    result=core._apply(owner,plan,core._approve(owner,plan))
                    core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(core.workspace,selected,owner.principal_id,audit_action,canonical(dict(key=body['key'],signature=signature,result=result))))
                    return result
            if action in ('workflow_transition','criterion_evidence'):
                fields={'action','task','task_version','base_revision','stage','reason','key','scope_reviewed'} if action=='workflow_transition' else {'action','task','task_version','contract_version','criterion','status','reference','note','key'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact workflow/evidence fields required.')
                service=TaskWorkflowService(core)
                return (service.transition if action=='workflow_transition' else service.evidence)(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='task_blocker':
                if set(body) not in ({'action','task','task_version','base_revision','blocked','reason','next_action'},{'action','task','task_version','base_revision','blocked','reason','next_action','gate','waiting_kind','owner'}):raise ContractError('invalid_request','Exact blocker fields required.')
                return TaskBlockerService(core).set(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='review_dialogue_relation':
                if set(body)!={'action','source_id','proposal_id','decision','key','reason'}:raise ContractError('invalid_request','Exact relation review fields required.')
                from packages.capture.dialogue_relations import DialogueRelationService
                return DialogueRelationService(core).review(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('prepare_dialogue_review','import_dialogue_response','review_dialogue_status','review_dialogue_answer'):
                from packages.capture.dialogue_review import DialogueReviewService
                fields={'review_dialogue_answer':{'action','source_id','proposal_id','decision','key','reason'},'prepare_dialogue_review':{'action','source_id'},'import_dialogue_response':{'action','source_id','response_text'},'review_dialogue_status':{'action','source_id','proposal_id','decision','key','reason','scope_reviewed'}}
                if set(body)!=fields[action]:raise ContractError('invalid_request','Exact dialogue review fields required.')
                service=DialogueReviewService(core)
                method={'review_dialogue_answer':service.review_answer,'prepare_dialogue_review':service.prepare,'import_dialogue_response':service.import_response,'review_dialogue_status':service.review_status}[action]
                return method(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='review_dialogue_question':
                from packages.capture.dialogue_questions import DialogueQuestionService
                if set(body)!={'action','source_id','proposal_id','decision','key','reason'}:raise ContractError('invalid_request','Exact source-bound question review fields required.')
                return DialogueQuestionService(core).review(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('create_processing_loop','run_processing_pass','start_processing_loop','stop_processing_loop'):
                from packages.capture.processing_loop import ProcessingLoopService
                fields={'action','loop_id','activation_id','activation_sha256','max_passes','max_sources_per_pass','max_total_sources','interval_seconds','expires_at','reason'} if action=='create_processing_loop' else {'action','loop_id','configuration_sha256'}|({'reason'} if action=='stop_processing_loop' else set())
                if set(body)!=fields:raise ContractError('invalid_request','Exact bounded processing loop fields required.')
                service=ProcessingLoopService(core);args={k:v for k,v in body.items() if k!='action'}
                if action=='create_processing_loop':return service.create(owner,selected,**args)
                if action=='start_processing_loop':return self.processing_worker.start(core,owner,selected,**args)
                if action=='stop_processing_loop':
                    result=service.stop(owner,selected,**args);self.processing_worker.cancel(selected,body['loop_id']);return result
                return service.execute_pass(owner,selected,registry=self.extractor_factory,**args)
            if action in ('create_model_activation','change_model_activation'):
                from packages.capture.model_activation import ModelActivationService
                fields={'action','activation_id','grant_ids','expires_at','reason'} if action=='create_model_activation' else {'action','activation_id','base_revision','configuration_sha256','state','reason'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact model activation fields required.')
                service=ModelActivationService(core)
                return (service.create if action=='create_model_activation' else service.transition)(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('import_conversation','analyze_conversation','process_conversation_queue','accept_candidates'):
                service=ConversationService(core)
                if action=='process_conversation_queue':
                    if set(body)!={'action','limit'}:raise ContractError('invalid_request','Exact bounded queue pass required.')
                    from packages.capture.processing_queue import ConversationQueue
                    def factory(source,grant):
                        if self.extractor_factory is not None:
                            configured=self.extractor_factory.bind_scope(core,owner,selected) if hasattr(self.extractor_factory,'bind_scope') else self.extractor_factory
                            return configured(source,grant)
                        if self.extractor is None or getattr(self.extractor,'grant_id',None)!=grant['id']:return None
                        return self.extractor
                    return ConversationQueue(core).process(owner,selected,extractor_factory=factory if (self.extractor is not None or self.extractor_factory is not None) else None,limit=body['limit'])
                if action=='import_conversation':
                    if set(body)!={'action','text'}:raise ContractError('invalid_request','Exact conversation fields required.')
                    source=service.ingest(owner,selected,text=body['text'])
                    return dict(source=source,analysis=service.analyze(owner,selected,source['id'],self._source_extractor(core,owner,selected,source['id'])))
                if action=='analyze_conversation':
                    if set(body)!={'action','source_id'}:raise ContractError('invalid_request','Exact source ID required.')
                    return service.analyze(owner,selected,body['source_id'],self._source_extractor(core,owner,selected,body['source_id']))
                if set(body)!={'action','source_id','key','selected','base_revision'}:raise ContractError('invalid_request','Exact candidate review required.')
                return service.accept(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='question_state':
                if set(body)!={'action','request_id','question','revision','base_state','status','reason'}:raise ContractError('invalid_request','Exact lifecycle fields required.')
                return QuestionService(core).transition(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='associate_answer':
                if set(body)!={'action','request_id','answer_id'}:raise ContractError('invalid_request','Exact association fields required.')
                return QuestionService(core).associate(owner,selected,request_id=body['request_id'],answer_id=body['answer_id'])
            if action=='revise_question':
                if set(body)!={'action','question','base_revision','text','options','task','reason'}:raise ContractError('invalid_request','Exact revision fields required.')
                return QuestionService(core).present(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action in ('prepare_decision','approve_decision','apply_decision','question_state','associate_answer','revise_question'):
                fields={'action','key','answer_id','reason'} if action=='prepare_decision' else {'action','key'} if action=='approve_decision' else {'action','key','approval'}
                if set(body)!=fields:raise ContractError('invalid_request','Exact decision fields required.')
                service=QuestionDecisionService(core)
                if action=='prepare_decision':return service.prepare(owner,selected,key=body['key'],answer_id=body['answer_id'],reason=body['reason'])
                if action=='approve_decision':return dict(approval=service.approve(owner,selected,body['key']))
                return service.apply(owner,selected,body['key'],body['approval'])
            if action=='ask_question':
                if set(body) not in ({'action','request_id','text','options'},{'action','request_id','text','options','task'}):raise ContractError('invalid_request','Exact question fields required.')
                return QuestionService(core).present(owner,selected,question=body['request_id'],base_revision=0,text=body['text'],options=body['options'],task=body.get('task'))
            if action=='answer_question':
                if set(body)!={'action','request_id','question','revision','option'}:raise ContractError('invalid_request','Exact answer fields required.')
                return QuestionService(core).answer(owner,selected,**{k:v for k,v in body.items() if k!='action'})
            if action=='create_task':
                if set(body)!={'action','title','description'}:raise ContractError('invalid_request','Exact task fields required.')
                ops=[dict(op='create',id='task',body=dict(type='Task',title=body['title'],description=body['description']))]
            elif action=='start':
                if set(body)!={'action','task'}:raise ContractError('invalid_request','Exact start fields required.')
                return AcceptanceService(core).start(owner,selected,body['task'])
            else:
                if set(body)!={'action','task','task_version','base_contract','criteria','dod','reason','acknowledged_changes'}:raise ContractError('invalid_request','Exact acceptance fields required.')
                ops=[dict({k:v for k,v in body.items() if k!='action'},op='acceptance_contract')]
            plan=core.plan(owner,selected,'ui_'+uuid.uuid4().hex,ops);token=core.approve(owner,plan)
            return core.apply(owner,plan,token)

def make_server(path,port=0,extractor=None,verification_root=None,environment='local',*,extractor_factory=None):
    app=LocalApp(path,extractor=extractor,verification_root=verification_root,environment=environment,extractor_factory=extractor_factory)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def answer(self,code,body,kind='application/json',cookie=False):
            if code>=400:app.record_error(self.path,body.get('error','application_error') if type(body) is dict else 'application_error')
            from packages.privacy.secrets import redact_value
            raw=json.dumps(redact_value(body),ensure_ascii=False).encode() if kind=='application/json' else body
            self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if getattr(self,'operation_id',None):self.send_header('X-Decivora-Operation-ID',self.operation_id)
            if cookie:self.send_header('Set-Cookie',app.cookie_name+'='+app.cookie+'; HttpOnly; SameSite=Strict; Path=/')
            self.end_headers();self.wfile.write(raw)
        def gate(self,write=False):
            if len(self.headers.get_all('Host',[]))!=1 or self.headers['Host']!=self.server.expected_host:return False
            if self.headers.get('Origin') and self.headers['Origin']!=self.server.origin:return False
            if write and self.headers.get('Origin')!=self.server.origin:return False
            return True
        def authenticated(self):
            cookie=SimpleCookie()
            try:cookie.load(self.headers.get('Cookie',''))
            except Exception:return False
            value=cookie.get(app.cookie_name);return bool(value and secrets.compare_digest(value.value,app.cookie))
        def do_GET(self):
            self.operation_id=None
            if not self.gate():return self.answer(403,dict(error='origin_denied'))
            if self.path in ('/','/app.js','/i18n.js','/locales.js','/workspace.css'):
                file=ROOT/('index.html' if self.path=='/' else self.path[1:]);raw=file.read_bytes()
                if self.path=='/':raw=raw.replace(b'>LOCAL</p>',('>'+app.environment.upper()+'</p>').encode())
                return self.answer(200,raw,'text/html; charset=utf-8' if self.path=='/' else 'text/css' if self.path=='/workspace.css' else 'application/javascript')
            url=urlsplit(self.path)
            if url.path not in ('/api/state','/api/operations','/api/conversations'):return self.answer(404,dict(error='not_found'))
            query=parse_qs(url.query,keep_blank_values=True)
            if set(query)-({'project_id','cursor','source_id'} if url.path=='/api/conversations' else {'project_id'}) or any(len(values)!=1 for values in query.values()):return self.answer(400,dict(error='invalid_request'))
            if not self.authenticated():return self.answer(401,dict(error='session_required'))
            if 'cursor' in query and 'source_id' in query:return self.answer(400,dict(error='invalid_request'))
            try:
                if url.path=='/api/conversations':return self.answer(200,app.conversation_page(query.get('project_id',['personal'])[0],query.get('cursor',[None])[0],query.get('source_id',[None])[0]))
                self.answer(200,(app.state if url.path=='/api/state' else app.operations_view)(query.get('project_id',['personal'])[0]))
            except ContractError as error:self.answer(409,dict(error=error.code))
            except Exception:self.answer(503,dict(error='storage_unavailable'))
        def do_POST(self):
            self.operation_id=None
            if not self.gate(write=True):return self.answer(403,dict(error='origin_denied'))
            if self.path=='/api/session':
                if not secrets.compare_digest(self.headers.get('Authorization',''),'Bearer '+app.bootstrap):return self.answer(401,dict(error='session_required'))
                self.close_connection=True
                return self.answer(200,dict(csrf=app.csrf),cookie=True)
            if self.path not in ('/api/command','/api/shutdown','/api/backup'):return self.answer(404,dict(error='not_found'))
            if not self.authenticated() or not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),app.csrf):return self.answer(403,dict(error='session_or_csrf_required'))
            if self.path=='/api/shutdown':
                self.answer(200,dict(status='stopping'));app.processing_worker.shutdown();threading.Thread(target=self.server.shutdown,daemon=True).start();return
            with app.rate_lock:
                window=int(time.monotonic()//60)
                if app.window!=window:app.window=window;app.writes=0
                if app.writes>=30:return self.answer(429,dict(error='rate_limited'))
                app.writes+=1
            length=self.headers.get('Content-Length','')
            if not length.isdecimal() or not 0<int(length)<=32768 or self.headers.get('Content-Type')!='application/json':return self.answer(413,dict(error='bounded_json_required'))
            try:
                body=json.loads(self.rfile.read(int(length)))
                if self.path=='/api/backup':return self.answer(200,app.backup_bundle(body),'application/zip')
                try:result=app.command(body)
                finally:self.operation_id=getattr(app.operations_context,'last_id',None)
                self.answer(200,result)
            except ContractError as e:self.answer(409,dict(error=e.code,message=str(e)))
            except (ValueError,TypeError,KeyError):self.answer(400,dict(error='invalid_request'))
            except Exception:self.answer(503,dict(error='storage_unavailable'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.daemon_threads=True;server.expected_host='127.0.0.1:'+str(server.server_port);server.origin='http://'+server.expected_host;server.app=app
    return server

def main():
    if sys.version_info[:2]!=(3,12):raise SystemExit('Bu sürüm Python 3.12 gerektiriyor.')
    parser=argparse.ArgumentParser();parser.add_argument('--data-dir',type=Path);parser.add_argument('--environment',choices=('local','test'),default='local');parser.add_argument('--port',type=int,default=0);parser.add_argument('--no-browser',action='store_true');parser.add_argument('--verification-root',type=Path);args=parser.parse_args()
    from packages.operations.environment import DEFAULT_DATA_DIR,TEST_DATA_DIR
    data_dir=args.data_dir or (TEST_DATA_DIR if args.environment=='test' else DEFAULT_DATA_DIR)
    server=make_server(data_dir/'workspace.sqlite',args.port,verification_root=args.verification_root,environment=args.environment)
    print('Decivora '+args.environment+' preview: '+server.origin+' — close with Ctrl+C. No model/API calls.',flush=True)
    if not args.no_browser:webbrowser.open(server.origin+'/#'+server.app.bootstrap)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.app.processing_worker.shutdown();server.server_close()
if __name__=='__main__':main()

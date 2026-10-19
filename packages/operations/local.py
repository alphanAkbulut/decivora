"""Bounded, content-free local diagnostics. Telemetry failure never grants authority."""
from contextlib import contextmanager
from pathlib import Path
import json,os,sqlite3,threading,time,uuid

MAX_RUNS=200
MAX_ERRORS=100
# Never persist exception text, raw action, URL, user prompt, headers or file paths.
CAPTURE_CODES=frozenset('codex_read_timeout codex_read_failed codex_transport_failed codex_transport_closed codex_host_unavailable invalid_codex_page invalid_codex_cursor capture_limit conversation_limit capture_binding_mismatch capture_checkpoint_stale capture_pending_turn_unavailable capture_item_changed capture_disconnected capture_permission_changed capture_consent_required invalid_source_cursor'.split())
ACTIVATION_CODES=frozenset('activation_required activation_unavailable invalid_activation activation_history_limit activation_denied stale_activation activation_transition_denied activation_inactive model_grant_required'.split())
ERROR_CODES=ACTIVATION_CODES|CAPTURE_CODES|frozenset('application_error sensitive_content invalid_request storage_unavailable storage_failure origin_denied session_required session_or_csrf_required not_found rate_limited bounded_json_required acceptance_required verification_required task_blocked stale_workflow stale_record stale_base stale_impact invalid_transition invalid_approval review_unavailable lifecycle_blocker lifecycle_review permission_denied scope_denied inactive_principal'.split())
COMPONENT_ACTIONS={
 'capture':{'import_conversation','native_capture'},
 'extraction':{'create_model_activation','change_model_activation','process_conversation_queue','analyze_conversation','prepare_dialogue_review','import_dialogue_response'},
 'reconciliation':{'accept_candidates','review_dialogue_status','review_dialogue_answer','review_dialogue_relation'},
 'impact':{'preview_decision_change','save_task_rationale','link_task_rationale','link_dependency'},
 'review':{'prepare_impact_updates','prepare_task_lifecycle','select_impact_changes','approve_impact_changes','apply_impact_changes','decide_impact_changes','approve_agent_proposal','apply_agent_proposal','reject_agent_proposal'},
 'questions':{'ask_question','answer_question','prepare_decision','approve_decision','apply_decision','question_state','associate_answer','revise_question'},
 'verification':{'acceptance','start','workflow_transition','criterion_evidence','bind_file_check','run_file_check'},
 'routing':{'work_routing'},'tasks':{'create_task','task_blocker'},
}
ACTIONS={a:c for c,actions in COMPONENT_ACTIONS.items() for a in actions}
ENDPOINTS={'/api/state','/api/command','/api/backup','/api/session','/api/shutdown','/api/operations','/api/conversations'}

def safe_code(value):return value if type(value) is str and value in ERROR_CODES else 'application_error'

def identity_from_scope(core,scope,project):
 """Trusted local preflight attribution, never a JSON actor or approval token."""
 with core.read_snapshot():
  core.scope(scope,project,write=True);core.active(scope,project)
  revision,state=core.authority._current()
  return dict(workspace=core.workspace,actor_id=scope.principal_id,actor_type=state[scope.principal_id]['kind'],authz_revision=revision)

class LocalOperations:
 def __init__(self,path):
  self.path=Path(path);self.session=uuid.uuid4().hex;self.lock=threading.Lock();self.lost=0;self.available=False
  try:
   if self.path.is_symlink():raise OSError('unsafe diagnostics path')
   fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
  except FileExistsError:pass
  except OSError:self.lost+=1;return
  self._write(lambda db:db.executescript('''
   CREATE TABLE IF NOT EXISTS op_runs(id TEXT PRIMARY KEY,session TEXT,project TEXT,action TEXT,component TEXT,started REAL,finished REAL,duration_ms REAL,outcome TEXT,code TEXT);
   CREATE TABLE IF NOT EXISTS op_spans(run TEXT,position INTEGER,component TEXT,stage TEXT,started REAL,finished REAL,duration_ms REAL,outcome TEXT,code TEXT,PRIMARY KEY(run,position),FOREIGN KEY(run) REFERENCES op_runs(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS op_errors(id TEXT PRIMARY KEY,endpoint TEXT,code TEXT,first_seen REAL,last_seen REAL,count INTEGER,UNIQUE(endpoint,code));
   CREATE TABLE IF NOT EXISTS op_meta(key TEXT PRIMARY KEY,value INTEGER);
   CREATE TABLE IF NOT EXISTS op_identities(run TEXT PRIMARY KEY,workspace TEXT NOT NULL,actor_id TEXT NOT NULL,actor_type TEXT NOT NULL,authz_revision INTEGER NOT NULL,FOREIGN KEY(run) REFERENCES op_runs(id) ON DELETE CASCADE);
  '''))
 @contextmanager
 def _connect(self):
  if self.path.is_symlink():raise OSError('unsafe diagnostics path')
  from packages.storage.private_files import restrict_sqlite_files
  restrict_sqlite_files(self.path)
  db=sqlite3.connect(self.path,timeout=.1)
  try:
   db.execute('PRAGMA busy_timeout=100');db.execute('PRAGMA foreign_keys=ON');yield db;db.commit()
  finally:db.close()
 def _write(self,fn):
  with self.lock:
   try:
    with self._connect() as db:fn(db)
    self.available=True;return True
   except (sqlite3.Error,OSError):self.available=False;self.lost+=1;return False
 def begin(self,project,action,*,identity=None):
  if identity is not None:
   from packages.domain.project_binding import identifier
   if type(identity) is not dict or set(identity)!={'workspace','actor_id','actor_type','authz_revision'} or identity['actor_type'] not in ('human','agent') or type(identity['authz_revision']) is not int or identity['authz_revision']<1:raise ValueError('Invalid internal trace identity.')
   identifier(identity['workspace']);identifier(identity['actor_id'])
  run='op_'+uuid.uuid4().hex;action=action if type(action) is str and action in ACTIONS else 'unknown';component=ACTIONS.get(action,'api')
  def write(db):
   db.execute('INSERT INTO op_runs VALUES (?,?,?,?,?,?,?,?,?,?)',(run,self.session,project,action,component,time.time(),None,None,'started',None))
   if identity is not None:db.execute('INSERT INTO op_identities VALUES (?,?,?,?,?)',(run,identity['workspace'],identity['actor_id'],identity['actor_type'],identity['authz_revision']))
   old=[r[0] for r in db.execute('SELECT id FROM op_runs ORDER BY started DESC,id DESC LIMIT -1 OFFSET ?',(MAX_RUNS,))]
   if old:
    db.executemany('DELETE FROM op_spans WHERE run=?',[(r,) for r in old]);db.executemany('DELETE FROM op_runs WHERE id=?',[(r,) for r in old]);db.execute("INSERT INTO op_meta VALUES ('runs_evicted',?) ON CONFLICT(key) DO UPDATE SET value=value+excluded.value",(len(old),))
  self._write(write);return run
 @contextmanager
 def span(self,run,position,component,stage):
  # All labels come from fixed application instrumentation, never source output.
  if component not in set(ACTIONS.values())|{'api','authorization'}:component='api'
  if stage not in {'authorize_project','execute_command'}:stage='execute_command'
  started=time.monotonic();self._write(lambda db:db.execute('INSERT INTO op_spans VALUES (?,?,?,?,?,?,?,?,?)',(run,position,component,stage,time.time(),None,None,'started',None)))
  outcome='succeeded';code=None
  try:yield
  except Exception as error:outcome='failed';code=safe_code(getattr(error,'code',None));raise
  finally:self._write(lambda db:db.execute('UPDATE op_spans SET finished=?,duration_ms=?,outcome=?,code=? WHERE run=? AND position=?',(time.time(),round((time.monotonic()-started)*1000,3),outcome,code,run,position)))
 def finish(self,run,started,error=None):
  self._write(lambda db:db.execute('UPDATE op_runs SET finished=?,duration_ms=?,outcome=?,code=? WHERE id=?',(time.time(),round((time.monotonic()-started)*1000,3),'failed' if error else 'succeeded',safe_code(getattr(error,'code',None)) if error else None,run)))
 def error(self,endpoint,code):
  endpoint=endpoint if endpoint in ENDPOINTS else 'other';code=safe_code(code);now=time.time()
  def write(db):
   db.execute('INSERT INTO op_errors VALUES (?,?,?,?,?,1) ON CONFLICT(endpoint,code) DO UPDATE SET last_seen=excluded.last_seen,count=count+1',('err_'+uuid.uuid4().hex,endpoint,code,now,now))
   old=[r[0] for r in db.execute('SELECT id FROM op_errors ORDER BY last_seen DESC,id DESC LIMIT -1 OFFSET ?',(MAX_ERRORS,))]
   if old:
    db.executemany('DELETE FROM op_errors WHERE id=?',[(r,) for r in old]);db.execute("INSERT INTO op_meta VALUES ('errors_evicted',?) ON CONFLICT(key) DO UPDATE SET value=value+excluded.value",(len(old),))
  self._write(write)
 def view(self,project):
  try:
   # Reading the panel never creates traces or dispatches model/tool work.
   with self.lock,self._connect() as db:
    columns='id,session,action,component,started,finished,duration_ms,outcome,code'.split(',');runs=[]
    for row in db.execute('SELECT '+','.join(columns)+' FROM op_runs WHERE project=? ORDER BY started DESC,id DESC LIMIT 50',(project,)):
     item=dict(zip(columns,row));item['outcome']='unknown' if item['finished'] is None and item['session']!=self.session else item['outcome'];item.pop('session')
     identity=db.execute('SELECT workspace,actor_id,actor_type,authz_revision FROM op_identities WHERE run=?',(item['id'],)).fetchone();item['identity']=dict(zip(('workspace','actor_id','actor_type','authz_revision'),identity)) if identity else None
     names='position,component,stage,started,finished,duration_ms,outcome,code'.split(',');item['stages']=[dict(zip(names,r)) for r in db.execute('SELECT '+','.join(names)+' FROM op_spans WHERE run=? ORDER BY position',(item['id'],))]
     if item['outcome']=='unknown':
      for span in item['stages']:
       if span['finished'] is None:span['outcome']='unknown'
     runs.append(item)
    names='id,endpoint,code,first_seen,last_seen,count'.split(',');errors=[dict(zip(names,r)) for r in db.execute('SELECT '+','.join(names)+' FROM op_errors ORDER BY last_seen DESC LIMIT 25')];meta=dict(db.execute('SELECT key,value FROM op_meta'))
   return dict(available=self.available,lost_this_process=self.lost,persistent=True,runs=runs,errors=errors,evicted=meta,limits=dict(retained_runs=MAX_RUNS,retained_error_groups=MAX_ERRORS,visible_runs=50,visible_error_groups=25),coverage='local_command_boundaries_only')
  except (sqlite3.Error,OSError):
   self.available=False
   return dict(available=False,lost_this_process=self.lost,persistent=True,runs=[],errors=[],evicted={},coverage='unavailable')

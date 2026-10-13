"""Bounded POSIX local file SHA observer with explicitly configured root."""
import hashlib,json,os,re,stat,time
from pathlib import Path
from packages.domain.source_event import ContractError
from packages.domain.project_binding import identifier
from packages.storage.project_store import canonical,digest
MAX_BYTES=1024*1024
class FileChecker:
 def __init__(self,root):
  self.root=Path(root).resolve(strict=True);self.root_id=digest(str(self.root));info=self.root.stat();self.root_identity=(info.st_dev,info.st_ino)
  if not stat.S_ISDIR(info.st_mode):raise ContractError('invalid_root','A selected directory root is required.')
  if not hasattr(os,'O_NOFOLLOW') or not hasattr(os,'O_DIRECTORY'):raise ContractError('verifier_unsupported','This verifier requires POSIX no-follow directory descriptors.')
 def observe(self,path):
  if type(path) is not str or not path or len(path)>256 or '\x00' in path or '\\' in path or ':' in path or path.startswith('/') or any(p in ('','.','..') for p in path.split('/')) or len(path.split('/'))>8:raise ContractError('invalid_target','Bounded relative target below the configured root required.')
  descriptors=[]
  try:
   fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY);descriptors.append(fd)
   for part in self.root.parts[1:]:fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);descriptors.append(fd)
   info=os.fstat(fd)
   if (info.st_dev,info.st_ino)!=self.root_identity:raise ContractError('root_changed','Selected verification root was replaced; reconfigure explicitly.')
   parts=path.split('/')
   for part in parts[:-1]:fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);descriptors.append(fd)
   parent=fd;fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);descriptors.append(fd);before=os.fstat(fd)
   if not stat.S_ISREG(before.st_mode):raise ContractError('invalid_target','Only regular files may be checked.')
   if before.st_size>MAX_BYTES:raise ContractError('file_limit','Local file-check preview limit is 1 MiB.')
   sha=hashlib.sha256();count=0
   while True:
    block=os.read(fd,min(65536,MAX_BYTES-count+1))
    if not block:break
    count+=len(block)
    if count>MAX_BYTES:raise ContractError('file_limit','File grew beyond the local check limit.')
    sha.update(block)
   after=os.fstat(fd);selected=os.stat(parts[-1],dir_fd=parent,follow_symlinks=False)
   stamp=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
   if stamp(before)!=stamp(after) or stamp(after)!=stamp(selected) or count!=after.st_size:raise ContractError('artifact_race','File changed while observing; retry current snapshot.')
   return dict(sha256=sha.hexdigest(),bytes=count,revision=digest(canonical(stamp(after))),root_id=self.root_id,method='sha256_exact_file',observed_at=time.time())
  except FileNotFoundError:raise ContractError('target_missing','Approved target is missing.') from None
  except OSError:raise ContractError('target_unavailable','Approved target is unavailable or contains a symlink.') from None
  finally:
   for fd in reversed(descriptors):os.close(fd)
class FileVerificationService:
 def __init__(self,core):self.core=core
 def _checker(self):
  checker=getattr(self.core,'file_checker',None)
  if checker is None:raise ContractError('verifier_not_configured','Select a trusted local verification root at startup first.')
  return checker
 def _rows(self,project,action):return [dict(actor=actor,sequence=seq,**json.loads(raw)) for seq,actor,raw in self.core.db.execute('SELECT seq,actor,ref FROM audit WHERE workspace=? AND project=? AND action=? ORDER BY seq',(self.core.workspace,project,action))]
 def _contract(self,project,task,task_version,contract_version,criterion):
  from packages.domain.task_workflow import TaskWorkflowService
  from packages.domain.acceptance import history
  record=TaskWorkflowService(self.core)._task(project,task);contracts=history(self.core,project,task);latest=contracts[-1] if contracts else None
  if type(task_version) is not int or type(contract_version) is not int or record['version']!=task_version or not latest or latest['version']!=contract_version or latest['contract']['task_version']!=task_version:raise ContractError('stale_evidence','Current task and criterion contract required.')
  row=next((r for r in latest['contract']['criteria']+latest['contract']['dod'] if r['id']==criterion),None)
  if not row or row['method']!='file_check':raise ContractError('invalid_verifier','Criterion must explicitly select file_check.')
  return record
 def bindings(self,project,task):return [r for r in self._rows(project,'file_criterion_binding') if r['task']==task]
 def bind(self,scope,project,*,task,task_version,contract_version,criterion,path,expected_sha256,reason,key):
  checker=self._checker();identifier(key);identifier(task);identifier(criterion)
  if type(expected_sha256) is not str or not re.fullmatch('[0-9a-f]{64}',expected_sha256) or type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('invalid_binding','Explicit expected hash and check-coverage approval required.')
  if type(path) is not str or not path or len(path)>256 or '\x00' in path or any(p in ('','.','..') for p in path.split('/')) or path.startswith('/') or '\\' in path or ':' in path:raise ContractError('invalid_target','Relative regular-file target required.')
  with self.core.transaction():
   self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);self._contract(project,task,task_version,contract_version,criterion)
   rows=self.bindings(project,task);request=dict(task=task,task_version=task_version,contract_version=contract_version,criterion=criterion,path=path,expected_sha256=expected_sha256,reason=reason,key=key,root_id=checker.root_id);signature=digest(canonical(request));old=next((r for r in rows if r['key']==key),None)
   if old:
    if old['actor']!=scope.principal_id or old['request_digest']!=signature:raise ContractError('idempotency_conflict','Binding key was reused.')
    return old
   if len(rows)>=64:raise ContractError('binding_limit','Local file binding history limit reached.')
   value=dict(request,revision=sum(r['criterion']==criterion for r in rows)+1,request_digest=signature,authority_revision=self.core.authority.revision(),format='decivora-file-binding-1')
   self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'file_criterion_binding',canonical(value)));return value
 def run(self,scope,project,*,task,task_version,contract_version,criterion,binding_revision,key):
  checker=self._checker();identifier(key);identifier(task);identifier(criterion)
  with self.core.read_snapshot():
   self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);record=self._contract(project,task,task_version,contract_version,criterion)
   if record['body'].get('execution')=='cancelled':raise ContractError('task_cancelled','Cancelled task cannot run a verification check.')
   from packages.domain.task_workflow import TaskWorkflowService
   if TaskWorkflowService(self.core)._stage(project,task)['stage'] not in ('In Review','Awaiting Verification','Done'):raise ContractError('evidence_stage_required','Implementation handoff required before checking criterion evidence.')
   bindings=[r for r in self.bindings(project,task) if r['criterion']==criterion];binding=bindings[-1] if bindings else None
   if not binding or type(binding_revision) is not int or binding['revision']!=binding_revision or binding['root_id']!=checker.root_id or binding['authority_revision']!=self.core.authority.revision() or binding['task_version']!=task_version or binding['contract_version']!=contract_version:raise ContractError('stale_binding','Current approved target/check binding required.')
   signature=digest(canonical(dict(task=task,task_version=task_version,contract_version=contract_version,criterion=criterion,binding_revision=binding_revision,key=key)));old=next((r for r in self._rows(project,'file_criterion_evidence') if r['key']==key),None)
   if old:
    if old['actor']!=scope.principal_id or old['request_digest']!=signature:raise ContractError('idempotency_conflict','Observation key was reused.')
    return old
  try:observation=checker.observe(binding['path']);status='passed' if observation['sha256']==binding['expected_sha256'] else 'failed';failure=None
  except ContractError as error:observation=None;status='failed' if error.code=='target_missing' else 'unknown';failure=error.code
  with self.core.transaction():
   self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);self._contract(project,task,task_version,contract_version,criterion)
   latest=[r for r in self.bindings(project,task) if r['criterion']==criterion][-1]
   if latest['request_digest']!=binding['request_digest'] or latest['authority_revision']!=self.core.authority.revision():raise ContractError('stale_binding','Check approval changed during observation.')
   prior=next((r for r in self._rows(project,'file_criterion_evidence') if r['key']==key),None)
   if prior:
    if prior['actor']!=scope.principal_id or prior['request_digest']!=signature:raise ContractError('idempotency_conflict','Observation key was reused.')
    return prior
   if len(self._rows(project,'file_criterion_evidence'))>=512:raise ContractError('evidence_limit','Local observation history limit reached.')
   value=dict(task=task,task_version=task_version,contract_version=contract_version,criterion=criterion,status=status,key=key,binding_revision=binding_revision,request_digest=signature,observation=observation,failure=failure,reference=binding['path'],note='Exact file SHA check only; no application test or deployment claim.',authority='local_file_observer',format='decivora-file-evidence-1')
   self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'file_criterion_evidence',canonical(value)));return value
 def current(self,project,task,criterion,evidence):
  try:
   checker=self._checker();bindings=[r for r in self.bindings(project,task) if r['criterion']==criterion];binding=bindings[-1]
   if binding['root_id']!=checker.root_id or binding['authority_revision']!=self.core.authority.revision() or binding['revision']!=evidence['binding_revision']:return False
   cache=getattr(self.core,'file_observation_cache',{})
   token=(checker.root_id,binding['path'])
   if token not in cache:
    if len(cache)>=16:self.core.file_read_limit_reached=True;return None
    try:cache[token]=checker.observe(binding['path'])
    except ContractError as error:cache[token]=dict(error=error.code)
   self.core.file_observation_cache=cache;observed=cache[token];old=evidence['observation']
   if 'error' in observed:
    if observed['error']==evidence.get('failure'):return True
    return False if observed['error']=='target_missing' else None
   return bool(old and old['sha256']==observed['sha256'] and old['revision']==observed['revision'])
  except ContractError as error:return None if error.code=='verifier_not_configured' else False
  except IndexError:return False

"""Explicit, bounded UI consent over the existing selected-thread capture adapter.

No discovery, host execution from browser input, model grant or auto polling.
"""
import time
from dataclasses import dataclass
from packages.capture.codex.app_server import CodexAppServerCapture
from packages.capture.conversations import ConversationService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest

@dataclass(frozen=True)
class NativeConnector:
    provider_version:str
    host_ref:str
    open_client:object

    def __post_init__(self):
        identifier(self.provider_version);identifier(self.host_ref)
        if not callable(self.open_client):raise ContractError('invalid_request','Trusted native client factory required.')

class UIConnectionService:
    CONFIG='codex_ui_connection'
    START='codex_ui_read_started'
    FINISH='codex_ui_read_finished'
    def __init__(self,core,connector=None):
        self.core=core;self.connector=connector;self.sources=ConversationService(core)
    def rows(self,project,action):return self.sources._rows(project,action)
    def config(self,project,capture_id):
        identifier(capture_id)
        row=next((r for r in self.rows(project,self.CONFIG) if r['id']==capture_id),None)
        if row is None:raise ContractError('capture_consent_required','Selected UI connection unavailable.')
        return row
    def counts(self,project,capture_id):
        starts=[r for r in self.rows(project,self.START) if r['id']==capture_id]
        finished=[r for r in self.rows(project,self.FINISH) if r['id']==capture_id]
        done={r['read_id'] for r in finished}
        return starts,finished,any(r['read_id'] not in done for r in starts)
    def authorize(self,scope,project,capture_id,configuration_sha256):
        binding=CodexAppServerCapture(self.core)._authorize(scope,project,capture_id)
        config=self.config(project,capture_id)
        if config['configuration_sha256']!=configuration_sha256:raise ContractError('capture_binding_mismatch','Refresh the selected connection.')
        if self.connector is None or config['host_ref']!=self.connector.host_ref or config['provider_version']!=self.connector.provider_version:
            raise ContractError('codex_host_unavailable','The exact trusted host is not configured.')
        if config['expires_at']<=time.time():raise ContractError('capture_permission_expired','Selected capture consent expired; no automatic renewal.')
        return binding
    def connect(self,scope,project,*,capture_id,thread_id,expires_at,max_reads,turn_limit,consent):
        if self.connector is None:raise ContractError('codex_host_unavailable','Configure a trusted native host first.')
        if consent is not True:raise ContractError('capture_consent_required','Explicit selected-thread public-text consent required.')
        if type(expires_at) is not int or expires_at<=time.time() or type(max_reads) is not int or not 1<=max_reads<=300 or type(turn_limit) is not int or not 1<=turn_limit<=10:
            raise ContractError('invalid_request','Explicit future expiry, one to 300 reads and one to ten turns required.')
        identifier(capture_id);identifier(thread_id)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            config=dict(id=capture_id,thread_id=thread_id,expires_at=expires_at,max_reads=max_reads,turn_limit=turn_limit,host_ref=self.connector.host_ref,provider_version=self.connector.provider_version,actor=scope.principal_id,authority_revision=self.core.authority.revision())
            config['configuration_sha256']=digest(canonical(config))
            old=next((r for r in self.rows(project,self.CONFIG) if r['id']==capture_id),None)
            if old:
                if old!=config:raise ContractError('capture_binding_conflict','This connection configuration is immutable.')
                CodexAppServerCapture(self.core)._authorize(scope,project,capture_id)
                return old
            for row in self.rows(project,self.CONFIG):
                if row['thread_id']==thread_id and row['host_ref']==config['host_ref'] and row['expires_at']>time.time():
                    try:CodexAppServerCapture(self.core)._authorize(scope,project,row['id'])
                    except ContractError:continue
                    raise ContractError('capture_binding_conflict','This selected chat is already connected in this project.')
            CodexAppServerCapture(self.core)._connect(scope,project,capture_id=capture_id,thread_id=thread_id,provider_version=self.connector.provider_version)
            self.sources._put(scope,project,self.CONFIG,config)
            return config
    def read_once(self,scope,project,*,capture_id,configuration_sha256,read_id,consent):
        identifier(read_id)
        if consent is not True:raise ContractError('capture_consent_required','Confirm this explicit local read.')
        with self.core.transaction():
            self.authorize(scope,project,capture_id,configuration_sha256)
            config=self.config(project,capture_id);starts,finished,pending=self.counts(project,capture_id)
            previous=next((r for r in self.rows(project,self.START) if r['read_id']==read_id),None)
            if previous is not None:
                if previous['id']!=capture_id:raise ContractError('capture_binding_conflict','Read identity belongs to another connection.')
                result=next((r for r in finished if r['read_id']==read_id),None)
                if result is not None:return result
                raise ContractError('capture_review_required','An unfinished read needs review; no automatic retry.')
            if pending:raise ContractError('capture_review_required','An unfinished read needs review; no automatic retry.')
            if len(starts)>=config['max_reads']:raise ContractError('capture_read_limit','The saved read limit has been consumed.')
            self.sources._put(scope,project,self.START,dict(id=capture_id,read_id=read_id,recorded_at=time.time()))
        # The scoped guard runs again before each checkpoint commit (including expiry/revoke).
        service=self
        class ScopedCapture(CodexAppServerCapture):
            def _authorize(self,scope,project,capture_id):
                return service.authorize(scope,project,capture_id,configuration_sha256)
        try:
            with self.connector.open_client(config['thread_id']) as client:
                receipt=ScopedCapture(self.core).collect(scope,project,capture_id=capture_id,client=client,limit=config['turn_limit'])
        except (ContractError,OSError) as error:
            code=error.code if isinstance(error,ContractError) else 'codex_host_unavailable'
            with self.core.transaction():self.sources._put(scope,project,self.FINISH,dict(id=capture_id,read_id=read_id,status='Read failed',code=code,recorded_at=time.time()))
            raise ContractError(code,'Selected chat read stopped; accepted pages remain intact.') from None
        result=dict(id=capture_id,read_id=read_id,status='Captured',coverage='partial',source_count=len(receipt['source_ids']),pending_turns=receipt.get('pending_turns',0),pending_assistant_turns=receipt.get('pending_assistant_turns',0),older_turns_omitted=receipt.get('older_turns_omitted',False),unsupported_items=receipt.get('unsupported_items',0),model_calls=0,recorded_at=time.time())
        with self.core.transaction():self.sources._put(scope,project,self.FINISH,result)
        return result
    def disconnect(self,scope,project,*,capture_id):
        with self.core.read_snapshot():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            if self.config(project,capture_id)['actor']!=scope.principal_id:raise ContractError('capture_consent_required','Only the connection owner may disconnect it.')
        return CodexAppServerCapture(self.core).disconnect(scope,project,capture_id=capture_id)
    def view(self,scope,project):
        with self.core.read_snapshot():
            self.core.scope(scope,project);self.core.active(scope,project);items=[];capture=CodexAppServerCapture(self.core)
            for row in self.rows(project,self.CONFIG):
                if row['actor']!=scope.principal_id:continue
                starts,finished,pending=self.counts(project,row['id']);status='Connected'
                if capture._disconnected(project,row['id']):status='Disconnected'
                elif row['authority_revision']!=self.core.authority.revision():status='Permission changed'
                elif row['expires_at']<=time.time():status='Expired'
                elif pending:status='Unfinished read'
                elif len(starts)>=row['max_reads']:status='Limit reached'
                elif self.connector is None or row['host_ref']!=self.connector.host_ref or row['provider_version']!=self.connector.provider_version:status='Host unavailable'
                items.append(dict(id=row['id'],thread_id=row['thread_id'],configuration_sha256=row['configuration_sha256'],expires_at=row['expires_at'],turn_limit=row['turn_limit'],max_reads=row['max_reads'],reads=len(starts),status=status,last_result=finished[-1] if finished else None))
            return dict(items=items,host_configured=self.connector is not None,provider_version=self.connector.provider_version if self.connector else None,automatic_discovery=False,automatic_capture=False,model_dispatch=False)


def connector_from_paths(executable,provider_version,*,cwd,codex_home=None):
    """Trusted startup configuration only; does not open a subprocess or read a chat."""
    from pathlib import Path
    from packages.capture.codex.read_client import ReadOnlyAppServer
    path=Path(executable)
    if not path.is_absolute() or not path.is_file():raise ContractError('codex_host_unavailable','An explicit installed Codex executable is required.')
    identifier(provider_version)
    host_ref='host_'+digest(canonical([str(path.resolve()),str(Path(codex_home).resolve()) if codex_home else None,provider_version]))
    return NativeConnector(provider_version,host_ref,lambda thread:ReadOnlyAppServer(path,thread,cwd=cwd,codex_home=codex_home))

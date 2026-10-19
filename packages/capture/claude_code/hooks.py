"""Selected-session public text hook ingress, atomically queued and redacted."""
import json
from packages.capture.conversations import ConversationService
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest
from packages.privacy.secrets import redact_text
MAX_PACKET_BYTES=65536

def fail(code):raise ContractError(code,'Selected Claude Code hook could not be captured; no host instruction or model call was issued.')

def validate_cwd(cwd):
    if type(cwd) is not str or not cwd.startswith('/') or len(cwd)>4096 or '\x00' in cwd:fail('invalid_claude_hook')
    try:cwd.encode('utf-8')
    except UnicodeError:fail('invalid_claude_hook')

def parse(raw):
    if type(raw) is not bytes or not 0<len(raw)<=MAX_PACKET_BYTES:fail('claude_hook_limit')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:fail('invalid_claude_hook')
            result[k]=v
        return result
    try:value=json.loads(raw.decode(),object_pairs_hook=pairs,parse_constant=lambda _:fail('invalid_claude_hook'))
    except (ValueError,UnicodeError,RecursionError):fail('invalid_claude_hook')
    if type(value) is not dict or value.get('hook_event_name') not in ('UserPromptSubmit','Stop'):fail('unsupported_claude_hook')
    identifier(value.get('session_id'))
    cwd=value.get('cwd')
    validate_cwd(cwd)
    role='user' if value['hook_event_name']=='UserPromptSubmit' else 'assistant'
    text=value.get('prompt') if role=='user' else value.get('last_assistant_message')
    if text is None and role=='assistant':return value,role,None
    if type(text) is not str or not text.strip():fail('claude_hook_limit')
    try:
        if len(text.encode())>12000:fail('claude_hook_limit')
    except UnicodeError:fail('invalid_claude_hook')
    return value,role,text

class ClaudeHookCapture:
    def __init__(self,core):self.core=core;self.sources=ConversationService(core)
    def _latest(self,project,action,capture_id):return next((r for r in reversed(self.sources._rows(project,action)) if r['id']==capture_id),None)
    def _authorize(self,scope,project,capture_id):
        self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
        binding=self._latest(project,'claude_hook_connected',capture_id)
        if not binding or self._latest(project,'claude_hook_disconnected',capture_id) or binding['actor']!=scope.principal_id or binding['authority_revision']!=self.core.authority.revision():fail('claude_hook_consent_required')
        return binding
    def connect(self,scope,project,*,capture_id,session_id,cwd,provider_version,consent):
        for v in (capture_id,session_id,provider_version):identifier(v)
        if consent is not True:fail('claude_hook_consent_required')
        validate_cwd(cwd)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            value=dict(id=capture_id,thread_id=session_id,cwd_sha256=digest(cwd),provider_version=provider_version,actor=scope.principal_id,authority_revision=self.core.authority.revision())
            old=self._latest(project,'claude_hook_connected',capture_id)
            if old:
                if old!=value or self._latest(project,'claude_hook_disconnected',capture_id):fail('claude_hook_binding_conflict')
                return old
            if len(self.sources._rows(project,'claude_hook_connected'))>=32:fail('claude_hook_limit')
            self.sources._put(scope,project,'claude_hook_connected',value);return value
    def collect(self,scope,project,*,capture_id,delivery_id,raw):
        identifier(capture_id);identifier(delivery_id)
        value,role,text=parse(raw)
        # Never persist a raw secret-bearing packet or its hash. Ignore private fields.
        safe_text=redact_text(text)[0] if text is not None else None
        content_sha256=digest(canonical(dict(event=value['hook_event_name'],thread=value['session_id'],cwd_digest=digest(value['cwd']),role=role,text=safe_text)))
        with self.core.transaction():
            binding=self._authorize(scope,project,capture_id)
            if value['session_id']!=binding['thread_id'] or digest(value['cwd'])!=binding['cwd_sha256']:fail('claude_hook_binding_mismatch')
            receipts=[r for r in self.sources._rows(project,'claude_hook_received') if r['id']==capture_id]
            old=next((r for r in receipts if r['delivery_id']==delivery_id),None)
            if old:
                if old['content_sha256']!=content_sha256:fail('claude_hook_delivery_conflict')
                return old
            if len(receipts)>=2048:fail('claude_hook_limit')
            source=None
            if text is not None:
                provenance=dict(source_surface='claude_code_hook',id=capture_id,thread_id=binding['thread_id'],item_id=delivery_id,observed_actor=role,provider_version=binding['provider_version'],hook_event=value['hook_event_name'],coverage='partial')
                source=self.sources._ingest(scope,project,text=text,capture=provenance,in_transaction=True)
            receipt=dict(id=capture_id,delivery_id=delivery_id,content_sha256=content_sha256,event=value['hook_event_name'],source=source['id'] if source else None,state='Captured' if source else 'Assistant text unavailable',coverage='partial',model_dispatches=0)
            self.sources._put(scope,project,'claude_hook_received',receipt);return receipt
    def disconnect(self,scope,project,*,capture_id):
        identifier(capture_id)
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            if not self._latest(project,'claude_hook_connected',capture_id):fail('claude_hook_consent_required')
            if not self._latest(project,'claude_hook_disconnected',capture_id):self.sources._put(scope,project,'claude_hook_disconnected',dict(id=capture_id))
            return dict(id=capture_id,state='Disconnected')

"""Durable bounded create-only agent proposals, separate trusted human review."""
import json
from packages.storage.project_store import canonical,digest
from packages.domain.source_event import ContractError
from packages.domain.project_binding import identifier
class AgentProposalService:
 def __init__(self,core):self.core=core
 def _rows(self,project,action):return [dict(actor=actor,**json.loads(raw)) for actor,raw in self.core.db.execute('SELECT actor,ref FROM audit WHERE workspace=? AND project=? AND action=? ORDER BY seq',(self.core.workspace,project,action))]
 def _proposal(self,project,key):
  row=next((r for r in self._rows(project,'agent_changeset_submitted') if r['key']==key),None)
  if not row:raise ContractError('proposal_unavailable','Agent proposal unavailable.')
  return row
 def _current(self,scope,project,key):
  self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);p=self._proposal(project,key)
  if any(r['key']==key for r in self._rows(project,'agent_changeset_rejected')):raise ContractError('proposal_rejected','Rejected proposal cannot be applied.')
  if p['authority_revision']!=self.core.authority.revision() or p['plan']['base_revision']!=self.core.project(scope,project)['knowledge_revision']:raise ContractError('stale_proposal','Project or submitting-agent authority changed; obtain a new proposal.')
  agent=self.core.authority.issue_scope(p['actor']);self.core.scope(agent,project,write=True)
  return p
 def submit(self,scope,project,*,key,base_revision,operations):
  with self.core.transaction():
   self.core.scope(scope,project,write=True);self.core.active(scope,project);identifier(key)
   if self.core.authority._current()[1][scope.principal_id]['kind']!='agent':raise ContractError('agent_required','Agent proposal identity required.')
   if type(base_revision) is not int or type(operations) is not list or not 1<=len(operations)<=16:raise ContractError('invalid_proposal','Bounded typed proposal required.')
   if len({op.get('id') for op in operations if type(op) is dict})!=len(operations):raise ContractError('invalid_proposal','Unique temporary IDs required.')
   for op in operations:
    if type(op) is not dict or set(op)!={'op','id','body'} or op['op']!='create':raise ContractError('impact_review_required','This local bridge accepts create-only drafts; edits/cancellation/relations require the impact-review integration.')
    identifier(op['id']);self.core._body(op['body'])
   signature=digest(canonical(dict(key=key,base_revision=base_revision,operations=operations)));old=next((r for r in self._rows(project,'agent_changeset_submitted') if r['key']==key),None)
   if old:
    if old['actor']!=scope.principal_id or old['request_digest']!=signature:raise ContractError('idempotency_conflict','Agent proposal key was reused.')
    return old['plan']
   if len(self._rows(project,'agent_changeset_submitted'))>=128:raise ContractError('proposal_limit','Local agent proposal limit reached; existing proposals remain.')
   if self.core.project(scope,project)['knowledge_revision']!=base_revision:raise ContractError('stale_base','Current project revision changed.')
   plan=self.core.plan(scope,project,key,operations)
   if len(canonical(plan).encode())>12000:raise ContractError('proposal_limit','Draft exceeds bounded MCP preview size; split the proposal.')
   value=dict(key=key,request_digest=signature,plan=plan,authority_revision=self.core.authority.revision(),authority='untrusted_agent_proposal')
   self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'agent_changeset_submitted',canonical(value)));return plan
 def view(self,scope,project):
  with self.core.read_snapshot():
   self.core.scope(scope,project,human=True);self.core.active(scope,project);rows=[];approved=self._rows(project,'agent_changeset_approved');applied=self._rows(project,'agent_changeset_applied');rejected=self._rows(project,'agent_changeset_rejected')
   for p in self._rows(project,'agent_changeset_submitted'):
    status='Applied' if any(r['key']==p['key'] for r in applied) else 'Rejected' if any(r['key']==p['key'] for r in rejected) else 'Approved' if any(r['key']==p['key'] for r in approved) else 'Prepared'
    if status not in ('Applied','Rejected'):
     try:
      if p['authority_revision']!=self.core.authority.revision() or p['plan']['base_revision']!=self.core.project(scope,project)['knowledge_revision']:raise ContractError('stale_proposal','Changed context.')
      self.core.scope(self.core.authority.issue_scope(p['actor']),project,write=True)
     except ContractError:status='Stale'
    rows.append(dict(p,state=status))
   return rows
 def approve(self,scope,project,key):
  with self.core.transaction():
   p=self._current(scope,project,key);old=next((r for r in self._rows(project,'agent_changeset_approved') if r['key']==key),None)
   if old:return dict(approved=True,applied=False)
   token=self.core._approve(scope,p['plan']);self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'agent_changeset_approved',canonical(dict(key=key,approval=token))));return dict(approved=True,applied=False)
 def apply(self,scope,project,key):
  with self.core.transaction():
   self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
   old=next((r for r in self._rows(project,'agent_changeset_applied') if r['key']==key),None)
   if old:return old['result']
   p=self._current(scope,project,key);approval=next((r for r in self._rows(project,'agent_changeset_approved') if r['key']==key),None)
   if not approval:raise ContractError('human_approval_required','Separate trusted human approval required.')
   result=self.core._apply(scope,p['plan'],approval['approval']);self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'agent_changeset_applied',canonical(dict(key=key,result=result))));return result
 def reject(self,scope,project,key,reason):
  with self.core.transaction():
   self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project);self._proposal(project,key)
   if type(reason) is not str or not reason.strip() or len(reason)>1024:raise ContractError('invalid_reason','Explicit bounded rejection reason required.')
   if any(r['key']==key for r in self._rows(project,'agent_changeset_applied')):raise ContractError('already_applied','Applied proposal requires a separate corrective change.')
   old=next((r for r in self._rows(project,'agent_changeset_rejected') if r['key']==key),None)
   if old:
    if old['reason']!=reason:raise ContractError('idempotency_conflict','Rejection reason changed.')
    return dict(rejected=True)
   self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,'agent_changeset_rejected',canonical(dict(key=key,reason=reason))));return dict(rejected=True)

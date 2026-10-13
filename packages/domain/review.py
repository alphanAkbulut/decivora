"""Persisted local review selection and separate human approval; no UI/auth adapter."""
import json
from packages.domain.project_binding import identifier
from packages.domain.source_event import ContractError
from packages.storage.project_store import canonical,digest

POLICY='local-human-review-1'

def _rows(core,project,action):
    return [json.loads(raw) for raw, in core.db.execute('SELECT ref FROM audit WHERE workspace=? AND project=? AND action=? ORDER BY seq',(core.workspace,project,action))]

def review_approval(core,project,token):
    return next((row for row in _rows(core,project,'review_approved') if row['approval']==token),None)

class ReviewService:
    def __init__(self,core):self.core=core
    def _put(self,scope,project,action,payload):
        raw=canonical(payload)
        if len(raw.encode())>65536:raise ContractError('review_limit','Review payload exceeds local limit.')
        self.core.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.core.workspace,project,scope.principal_id,action,raw))
    def _load(self,project,action,key):
        return next((r for r in _rows(self.core,project,action) if r['id']==key),None)
    def _packet(self,scope,project,key):
        self.core.scope(scope,project)
        packet=self._load(project,'review_created',identifier(key))
        if packet is None:raise ContractError('review_unavailable','Review is unavailable.')
        return packet
    def _current(self,scope,project,packet):
        self.core.active(scope,project)
        stored=self.core._impact_run(project,packet['impact_run'])
        if stored is None or stored['result']['digest']!=packet['impact_digest']:
            raise ContractError('stale_review','Impact basis changed.')
        self.core._current_impact(scope,project,stored)
        if stored['result']['coverage']!='complete_snapshot':raise ContractError('incomplete_impact','Incomplete impact cannot authorize task changes.')
        if packet['policy']!=POLICY:raise ContractError('stale_policy','Review policy changed.')
        decisions=[r for r in _rows(self.core,project,'review_decision') if r['packet']==packet['id']]
        if decisions and decisions[-1]['action']=='reject':raise ContractError('review_rejected','Review was rejected; prepare a new review if needed.')
        return stored
    def create(self,scope,project,key,impact_run,groups):
        identifier(key);identifier(impact_run)
        if type(groups) is not list or not 1<=len(groups)<=32:raise ContractError('invalid_review','Bounded operation groups required.')
        raw=canonical(dict(impact_run=impact_run,groups=groups))
        if len(raw.encode())>32768:raise ContractError('review_limit','Review input exceeds local limit.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True);self.core.active(scope,project)
            previous=self._load(project,'review_created',key)
            if previous:
                if previous['input_digest']!=digest(raw) or previous['actor']!=scope.principal_id:raise ContractError('idempotency_conflict','Review identity changed.')
                return previous
            impact=self.core._impact_run(project,impact_run)
            if impact is None:raise ContractError('impact_unavailable','Impact preview required.')
            self.core._current_impact(scope,project,impact)
            ids=set();proposals={r['record'] for r in impact['result']['proposals']}
            for g in groups:
                if type(g) is not dict or set(g)!={'id','depends_on','records','operations'}:raise ContractError('invalid_review','Exact operation group fields required.')
                gid=identifier(g['id'])
                if gid in ids:raise ContractError('invalid_review','Duplicate group ID.')
                ids.add(gid)
                if type(g['depends_on']) is not list or len(g['depends_on'])>32 or any(type(v) is not str for v in g['depends_on']) or len(set(g['depends_on']))!=len(g['depends_on']):raise ContractError('invalid_review','Unique bounded group dependencies required.')
                for dep in g['depends_on']:identifier(dep)
                if type(g['records']) is not list or not g['records'] or any(type(v) is not str for v in g['records']) or any(r not in proposals for r in g['records']):raise ContractError('invalid_review','Groups must identify impact proposals.')
                if type(g['operations']) is not list or not 1<=len(g['operations'])<=64:raise ContractError('invalid_review','Nonempty bounded typed operations required.')
                from packages.storage.workspace import RELATIONS,integer
                for op in g['operations']:
                    if type(op) is not dict or op.get('op') not in ('create','update','link','end_link'):raise ContractError('invalid_operation','Only typed domain operations are allowed.')
                    kind=op['op']
                    fields={'op','id','body'} if kind=='create' else {'op','id','base_version','body'} if kind=='update' else {'op','origin','target','kind'}
                    if kind=='end_link':fields|={'base_version','state'}
                    if set(op)!=fields and not (kind=='create' and set(op)==fields|{'source_seq'}):raise ContractError('invalid_operation','Exact operation fields required.')
                    if kind in ('create','update'):
                        identifier(op['id']);self.core._body(op['body'])
                        if kind=='update':integer(op['base_version'],1)
                        if 'source_seq' in op:integer(op['source_seq'],1)
                    else:
                        identifier(op['origin']);identifier(op['target'])
                        if op['kind'] not in RELATIONS:raise ContractError('invalid_operation','Unknown typed relation.')
                        if kind=='end_link':
                            integer(op['base_version'],1)
                            if op['state'] not in ('ended','invalidated'):raise ContractError('invalid_operation','Unsupported edge lifecycle.')

            indexed={g['id']:g for g in groups};visiting=set();seen=set()
            def visit(gid):
                if gid not in indexed:raise ContractError('invalid_review','Unknown dependent group.')
                if gid in visiting:raise ContractError('review_cycle','Operation group cycle rejected.')
                if gid in seen:return
                visiting.add(gid)
                for dep in indexed[gid]['depends_on']:visit(dep)
                visiting.remove(gid);seen.add(gid)
            for gid in ids:visit(gid)
            packet=dict(id=key,project=project,actor=scope.principal_id,impact_run=impact_run,impact_digest=impact['result']['digest'],input_digest=digest(raw),policy=POLICY,groups=json.loads(raw)['groups'])
            self._put(scope,project,'review_created',packet)
            return packet
    def compare(self,scope,project,key):
        with self.core.read_snapshot():
            packet=self._packet(scope,project,key)
            impact=self.core.impact_run(scope,project,packet['impact_run'])
            return dict(packet=packet,impact=impact,canonical_mutations=0)
    def decide(self,scope,project,key,action_id,action):
        identifier(action_id)
        if action not in ('reject','defer'):raise ContractError('invalid_review','Explicit reject or defer required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True);self.core.active(scope,project)
            packet=self._packet(scope,project,key)
            event=dict(id=action_id,packet=key,action=action,actor=scope.principal_id)
            previous=self._load(project,'review_decision',action_id)
            if previous:
                if previous!=event:raise ContractError('idempotency_conflict','Review action changed.')
                return previous
            if any(r['packet']==key for r in _rows(self.core,project,'review_applied')):raise ContractError('review_applied','Applied review cannot be silently rejected.')
            if any(r['packet']==key and r['action']=='reject' for r in _rows(self.core,project,'review_decision')):raise ContractError('review_rejected','Rejected review requires a new proposal.')
            self._put(scope,project,'review_decision',event);return event
    def select(self,scope,project,key,selection_id,selected):
        identifier(selection_id)
        if type(selected) is not list or not selected or len(selected)>32 or any(type(v) is not str for v in selected) or len(set(selected))!=len(selected):raise ContractError('invalid_selection','Nonempty unique group selection required.')
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True)
            packet=self._packet(scope,project,key);self._current(scope,project,packet)
            groups={g['id']:g for g in packet['groups']}
            if any(g not in groups for g in selected):raise ContractError('invalid_selection','Unknown selected group.')
            if any(dep not in selected for gid in selected for dep in groups[gid]['depends_on']):raise ContractError('dependent_selection','Select every required operation group together.')
            all_created={op.get('id') for g in packet['groups'] for op in g['operations'] if type(op) is dict and op.get('op')=='create'}
            selected_created={op.get('id') for g in packet['groups'] if g['id'] in selected for op in g['operations'] if type(op) is dict and op.get('op')=='create'}
            for g in packet['groups']:
                if g['id'] not in selected:continue
                for op in g['operations']:
                    if type(op) is not dict:raise ContractError('invalid_operation','Typed operation required.')
                    if op.get('op') in ('link','end_link') and any(op.get(field) in all_created-selected_created for field in ('origin','target')):
                        raise ContractError('dependent_selection','Omitted create group is required by a selected reference.')
            # Preserve packet operation ordering; omitted groups never enter the plan.
            operations=[op for g in packet['groups'] if g['id'] in selected for op in g['operations']]
            plan=self.core.plan(scope,project,selection_id,operations)
            result=dict(id=selection_id,packet=key,actor=scope.principal_id,groups=sorted(selected),policy=POLICY,impact_digest=packet['impact_digest'],decision_revision=len([r for r in _rows(self.core,project,'review_decision') if r['packet']==key]),plan=plan)
            result['digest']=digest(canonical(result))
            old=self._load(project,'review_selected',selection_id)
            if old:
                if old!=result:raise ContractError('idempotency_conflict','Selection changed.')
                return old
            self._put(scope,project,'review_selected',result);return result
    def _selection_current(self,project,selection):
        revision=len([r for r in _rows(self.core,project,'review_decision') if r['packet']==selection['packet']])
        if selection['decision_revision']!=revision:
            raise ContractError('stale_review','A review decision changed after selection; choose a fresh selection.')
    def approve(self,scope,project,selection_id):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True)
            selection=self._load(project,'review_selected',identifier(selection_id))
            if selection is None:raise ContractError('review_unavailable','Selection unavailable.')
            packet=self._packet(scope,project,selection['packet']);self._current(scope,project,packet)
            self._selection_current(project,selection)
            if selection['actor']!=scope.principal_id or selection['policy']!=POLICY:raise ContractError('invalid_approval','Selection identity/policy changed.')
            old=next((r for r in _rows(self.core,project,'review_approved') if r['id']==selection_id),None)
            if old:return old['approval']
            token=self.core._approve(scope,selection['plan'])
            self._put(scope,project,'review_approved',dict(id=selection_id,selection_digest=selection['digest'],approval=token,actor=scope.principal_id,policy=POLICY))
            return token
    def apply(self,scope,project,selection_id,approval):
        with self.core.transaction():
            self.core.scope(scope,project,write=True,human=True)
            selection=self._load(project,'review_selected',identifier(selection_id))
            if selection is None:raise ContractError('review_unavailable','Selection unavailable.')
            old=self._load(project,'review_applied',selection_id)
            if old:
                if old['approval']!=approval or old['actor']!=scope.principal_id:raise ContractError('invalid_approval','Applied review identity changed.')
                return old['result']
            packet=self._packet(scope,project,selection['packet']);self._current(scope,project,packet)
            self._selection_current(project,selection)
            bound=review_approval(self.core,project,approval)
            if bound is None or bound['id']!=selection_id or bound['selection_digest']!=selection['digest'] or bound['actor']!=scope.principal_id or bound['policy']!=POLICY:raise ContractError('invalid_approval','Review approval does not bind this selection/policy.')
            result=self.core._apply(scope,selection['plan'],approval,review_digest=selection['digest'])
            self._put(scope,project,'review_applied',dict(id=selection_id,packet=packet['id'],approval=approval,actor=scope.principal_id,result=result))
            return result

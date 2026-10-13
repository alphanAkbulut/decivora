"""Normalized synthetic/local core: projects, receipts/jobs, events and atomic apply.

No network, source discovery, model dispatch or runner. LocalAuthorityStore is
the trusted local identity boundary; this is not a public authentication API.
"""
from dataclasses import asdict
from pathlib import Path
import json
import os
import sqlite3
from contextlib import contextmanager
import uuid
import hashlib

from packages.domain.project_binding import SessionKey, identifier
from packages.domain.source_event import ContractError, validate_source_event
from .local_authority import LocalAuthorityStore
from .project_store import canonical, digest

FORMAT = 'decivora-workspace-core-1'
TYPES = {'Idea','Finding','Risk','Requirement','Task','Prompt','DocumentInstruction','Decision',
         'PendingDecision','Artifact'}
RELATIONS = {'related_to','required_by','depends_on','implements','refines','conflicts_with','supersedes','part_of'}
SCHEMA = '''
CREATE TABLE core_meta(format TEXT NOT NULL, workspace TEXT PRIMARY KEY, schema_version INTEGER NOT NULL);
CREATE TABLE projects(workspace TEXT, id TEXT, name TEXT NOT NULL, revision INTEGER NOT NULL, archived INTEGER NOT NULL DEFAULT 0,
 knowledge_revision INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(workspace,id), FOREIGN KEY(workspace) REFERENCES core_meta(workspace));
CREATE TABLE bindings(workspace TEXT,provider TEXT,account TEXT,session TEXT,epoch TEXT,revision INTEGER,project TEXT,actor TEXT,
 PRIMARY KEY(workspace,provider,account,session,epoch,revision),
 UNIQUE(workspace,provider,account,session,epoch,revision,project),
 FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id));
CREATE TABLE sources(seq INTEGER PRIMARY KEY,workspace TEXT,provider TEXT,account TEXT,session TEXT,epoch TEXT,event_id TEXT,
 source_revision INTEGER,position INTEGER,project TEXT,binding_revision INTEGER,payload TEXT,hash TEXT,status TEXT,reason TEXT,
 UNIQUE(workspace,provider,account,session,epoch,event_id,source_revision),
 UNIQUE(workspace,project,seq),
 UNIQUE(workspace,provider,account,session,epoch,position), FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id),
 FOREIGN KEY(workspace,provider,account,session,epoch,binding_revision) REFERENCES bindings(workspace,provider,account,session,epoch,revision),
 FOREIGN KEY(workspace,provider,account,session,epoch,binding_revision,project) REFERENCES bindings(workspace,provider,account,session,epoch,revision,project));
CREATE TABLE jobs(source_seq INTEGER PRIMARY KEY,project TEXT,status TEXT NOT NULL,attempt INTEGER NOT NULL DEFAULT 0,
 fencing INTEGER NOT NULL DEFAULT 0,lease_until INTEGER NOT NULL DEFAULT 0,due INTEGER NOT NULL DEFAULT 0,result TEXT,lease_actor TEXT NOT NULL DEFAULT '',
 FOREIGN KEY(source_seq) REFERENCES sources(seq));
CREATE TABLE events(seq INTEGER PRIMARY KEY,workspace TEXT,project TEXT,stream TEXT,version INTEGER,kind TEXT,payload TEXT,
 UNIQUE(workspace,project,stream,version), FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id));
CREATE TABLE records(workspace TEXT,project TEXT,id TEXT,version INTEGER,body TEXT,
 PRIMARY KEY(workspace,project,id),FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id));
CREATE TABLE edges(workspace TEXT,project TEXT,origin TEXT,target TEXT,kind TEXT,revision INTEGER,state TEXT,valid_from INTEGER,valid_to INTEGER,
 PRIMARY KEY(workspace,project,origin,target,kind),
 FOREIGN KEY(workspace,project,origin) REFERENCES records(workspace,project,id),
 FOREIGN KEY(workspace,project,target) REFERENCES records(workspace,project,id));
CREATE TABLE record_sources(workspace TEXT,project TEXT,record TEXT,source_seq INTEGER,
 PRIMARY KEY(workspace,project,record,source_seq),
 FOREIGN KEY(workspace,project,record) REFERENCES records(workspace,project,id),
 FOREIGN KEY(workspace,project,source_seq) REFERENCES sources(workspace,project,seq));
CREATE TABLE approvals(id TEXT PRIMARY KEY,workspace TEXT,project TEXT,approver TEXT,digest TEXT,base_revision INTEGER,
 authz_revision INTEGER, command_key TEXT,FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id));
CREATE TABLE commands(workspace TEXT,project TEXT,key TEXT,actor TEXT,digest TEXT,result TEXT,
 PRIMARY KEY(workspace,project,key),FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id));
CREATE TABLE audit(seq INTEGER PRIMARY KEY,workspace TEXT,project TEXT,actor TEXT,action TEXT,ref TEXT);
CREATE TABLE run_budgets(workspace TEXT,project TEXT,run TEXT,token_cap INTEGER,
 PRIMARY KEY(workspace,project,run),FOREIGN KEY(workspace,project) REFERENCES projects(workspace,id));
CREATE TABLE reservations(workspace TEXT,project TEXT,run TEXT,key TEXT,tokens INTEGER,status TEXT,actual INTEGER,
 PRIMARY KEY(workspace,project,run,key),FOREIGN KEY(workspace,project,run) REFERENCES run_budgets(workspace,project,run));
CREATE TABLE admission(workspace TEXT,actor TEXT,window INTEGER,count INTEGER,PRIMARY KEY(workspace,actor,window));
'''


def integer(value, minimum=0):
    if type(value) is not int or not minimum <= value <= 9223372036854775807:
        raise ContractError('invalid_integer','A bounded integer is required.')
    return value


class Workspace:
    def __init__(self, path, workspace, *, owner=None):
        existed = Path(path).exists() or Path(path).is_symlink()
        self.authority = LocalAuthorityStore(path, workspace, bootstrap_owner=owner)
        self.db = self.authority._store.connection
        self.workspace = workspace
        self.db.execute('PRAGMA foreign_keys=ON')
        try:
            if not existed:
                self.db.executescript('BEGIN IMMEDIATE;'+SCHEMA)
                self.db.execute('INSERT INTO core_meta VALUES (?,?,1)',(FORMAT,workspace))
                for table in ('bindings','sources','events','approvals','commands','audit','core_meta'):
                    # Table identifiers are fixed developer constants, never caller text.
                    for operation in ('UPDATE','DELETE'):
                        self.db.execute(f"CREATE TRIGGER {table}_no_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'immutable history'); END")
                self.db.execute('COMMIT')
            if self.db.execute('SELECT format,workspace,schema_version FROM core_meta').fetchall()!=[(FORMAT,workspace,1)]:
                raise ContractError('unsupported_storage','Workspace schema is incompatible.')
            if self.db.execute('PRAGMA foreign_key_check').fetchall():
                raise ContractError('storage_corrupt','Workspace references failed validation.')
        except (ContractError,sqlite3.Error):
            self.close()
            raise ContractError('unsupported_storage','Workspace profile unavailable; no implicit upgrade.') from None

    def close(self):
        self.authority.close()

    def __enter__(self): return self
    def __exit__(self,*_): self.close()

    @contextmanager
    def transaction(self):
        try:
            self.db.execute('BEGIN IMMEDIATE')
            yield
            self.db.execute('COMMIT')
        except Exception as error:
            if self.db.in_transaction: self.db.execute('ROLLBACK')
            if isinstance(error,sqlite3.Error):
                raise ContractError('storage_failure','Workspace transaction was not committed.') from None
            raise

    def scope(self, scope, project=None, *, write=False, human=False):
        self.authority._validate_scope(scope)
        if project is not None:
            identifier(project)
            if project not in (scope.writable_projects if write else scope.readable_projects):
                raise ContractError('forbidden','Selected project is outside current authority.')
        if human:
            _,state=self.authority._current()
            if scope.principal_id!=self.authority.owner_id or state[scope.principal_id]['kind']!='human':
                raise ContractError('human_approval_required','A current local human owner approval is required.')

    def project(self, scope, project):
        self.scope(scope,project)
        row=self.db.execute('SELECT name,revision,archived,knowledge_revision FROM projects WHERE workspace=? AND id=?',(self.workspace,project)).fetchone()
        if row is None: raise ContractError('project_unavailable','Selected project is unavailable.')
        return dict(id=project,name=row[0],revision=row[1],archived=bool(row[2]),knowledge_revision=row[3])

    def create_project(self,scope,project,name):
        from packages.domain.project_binding import ProjectRegistry
        name=ProjectRegistry._name(name)
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            self.db.execute('INSERT INTO projects(workspace,id,name,revision) VALUES (?,?,?,1)',(self.workspace,project,name))
        return self.project(scope,project)

    def update_project(self,scope,project,*,base_revision,name,archived=False):
        from packages.domain.project_binding import ProjectRegistry
        name=ProjectRegistry._name(name);integer(base_revision,1)
        if type(archived) is not bool:raise ContractError('invalid_state','Boolean archive flag required.')
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            if self.project(scope,project)['revision']!=base_revision:raise ContractError('stale_base','Project revision changed.')
            self.db.execute('UPDATE projects SET name=?,archived=?,revision=revision+1 WHERE workspace=? AND id=?',(name,int(archived),self.workspace,project))
        return self.project(scope,project)

    def bind(self,scope,key,project,base_revision):
        if type(key) is not SessionKey: raise ContractError('invalid_session','Explicit session key required.')
        integer(base_revision)
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            current=self.project(scope,project)
            if current['archived']: raise ContractError('project_archived','Project is archived.')
            prefix=(self.workspace,key.provider,key.account_id,key.session_id,key.source_epoch)
            old=self.db.execute('SELECT revision,project FROM bindings WHERE workspace=? AND provider=? AND account=? AND session=? AND epoch=? ORDER BY revision DESC LIMIT 1',prefix).fetchone()
            revision=old[0] if old else 0
            if old: self.scope(scope,old[1],write=True)
            if revision!=base_revision: raise ContractError('stale_binding','Binding revision changed.')
            self.db.execute('INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?)',(*prefix,revision+1,project,scope.principal_id))
        return revision+1

    def receive(self,scope,key,event,position,*,now=0,queue_limit=200):
        """Synthetic manual ingress only: server pins CURRENT binding, no supplied revision."""
        if type(key) is not SessionKey: raise ContractError('invalid_session','Explicit session key required.')
        event=validate_source_event(asdict(event))
        integer(position,1);integer(now);integer(queue_limit,1)
        if key.session_id!=event.session_id: raise ContractError('session_mismatch','Source session mismatch.')
        raw=canonical(asdict(event));sha=digest(raw)
        prefix=(self.workspace,key.provider,key.account_id,key.session_id,key.source_epoch)
        with self.transaction():
            self.scope(scope,event.project_id,write=True)
            prior=self.db.execute('SELECT seq,hash,position,project,binding_revision,status,reason FROM sources WHERE workspace=? AND provider=? AND account=? AND session=? AND epoch=? AND event_id=? AND source_revision=?',(*prefix,event.event_id,event.source_revision)).fetchone()
            if prior:
                if prior[1]!=sha or prior[2]!=position: raise ContractError('source_conflict','Source identity reused with different content or position.')
                if prior[3]: self.scope(scope,prior[3],write=True)
                return dict(seq=prior[0],project=prior[3],binding_revision=prior[4],status=prior[5],reason=prior[6],duplicate=True,durable_receipt=True)
            window=now//60
            count=self.db.execute('SELECT count FROM admission WHERE workspace=? AND actor=? AND window=?',(self.workspace,scope.principal_id,window)).fetchone()
            if count and count[0]>=20:raise ContractError('rate_limited','Local ingress burst limit reached; retry later.')
            self.db.execute('INSERT INTO admission VALUES (?,?,?,1) ON CONFLICT(workspace,actor,window) DO UPDATE SET count=count+1',(self.workspace,scope.principal_id,window))
            if queue_limit>200:raise ContractError('queue_limit','Local queue cap cannot be raised by an ingress caller.')
            if self.db.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','leased','retry_wait')").fetchone()[0]>=queue_limit:
                raise ContractError('queue_full','New ingress not accepted; previously received work remains.')
            if self.db.execute("SELECT count(*) FROM jobs WHERE project=? AND status IN ('queued','leased','retry_wait')",(event.project_id,)).fetchone()[0]>=min(queue_limit,100):
                raise ContractError('project_queue_full','Local project queue share is full; other projects may continue.')
            binding=self.db.execute('SELECT revision,project FROM bindings WHERE workspace=? AND provider=? AND account=? AND session=? AND epoch=? ORDER BY revision DESC LIMIT 1',prefix).fetchone()
            reason='project_unbound' if binding is None else 'project_mismatch' if binding[1]!=event.project_id else ''
            if binding:
                self.scope(scope,binding[1],write=True)
                if self.project(scope,binding[1])['archived']: reason='project_archived'
            project=binding[1] if binding and not reason else None
            revision=binding[0] if binding else None
            if self.db.execute('SELECT coalesce(sum(length(payload)),0) FROM sources').fetchone()[0]+len(raw.encode())>16777216:
                raise ContractError('storage_quota_exceeded','New source exceeds local development quota.')
            cursor=self.db.execute('INSERT INTO sources(workspace,provider,account,session,epoch,event_id,source_revision,position,project,binding_revision,payload,hash,status,reason) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (*prefix,event.event_id,event.source_revision,position,project,revision,raw,sha,'quarantined' if reason else 'accepted_pending',reason))
            seq=cursor.lastrowid
            if project:
                self.db.execute('INSERT INTO jobs(source_seq,project,status,due) VALUES (?,?,?,?)',(seq,project,'queued',now))
        return dict(seq=seq,project=project,binding_revision=revision,status='quarantined' if reason else 'accepted_pending',reason=reason,duplicate=False,durable_receipt=True)

    def frontier(self,scope,key,project):
        if type(key) is not SessionKey:raise ContractError('invalid_session','Explicit session key required.')
        self.scope(scope,project)
        rows=self.db.execute('SELECT s.position,s.project,j.status FROM sources s LEFT JOIN jobs j ON j.source_seq=s.seq WHERE s.workspace=? AND s.provider=? AND s.account=? AND s.session=? AND s.epoch=? ORDER BY s.position',
            (self.workspace,key.provider,key.account_id,key.session_id,key.source_epoch)).fetchall()
        # Session history may cross projects; do not reveal another project's offsets.
        for _,owner,_ in rows:
            if owner: self.scope(scope,owner)
        received={r[0] for r in rows};completed={r[0] for r in rows if r[2]=='succeeded'}
        def contiguous(items):
            n=0
            while n+1 in items:n+=1
            return n
        gaps=max(received,default=0)-len(received)
        return dict(received=contiguous(received),processed=contiguous(completed),complete=received==completed and gaps==0,
                    pending=len(received-completed),missing_positions=gaps)

    def lease(self,scope,project,*,now,ttl=30,max_attempts=3):
        integer(now);integer(ttl,1);integer(max_attempts,1)
        with self.transaction():
            self.scope(scope,project,write=True)
            row=self.db.execute("SELECT source_seq,attempt,fencing FROM jobs WHERE project=? AND due<=? AND (status IN ('queued','retry_wait') OR (status='leased' AND lease_until<=?)) ORDER BY due,source_seq LIMIT 1",(project,now,now)).fetchone()
            if row is None:return None
            seq,attempt,fence=row
            if attempt>=max_attempts:
                self.db.execute("UPDATE jobs SET status='failed',fencing=fencing+1 WHERE source_seq=?",(seq,))
                return dict(source_seq=seq,status='failed')
            self.db.execute("UPDATE jobs SET status='leased',attempt=?,fencing=?,lease_until=?,lease_actor=? WHERE source_seq=?",(attempt+1,fence+1,now+ttl,scope.principal_id,seq))
            return dict(source_seq=seq,project=project,fencing=fence+1,lease_until=now+ttl,attempt=attempt+1)

    def finish(self,scope,lease,result,*,now,success=True,retry_delay=5):
        integer(now);integer(retry_delay,1)
        if type(success) is not bool:raise ContractError('invalid_result','Boolean completion flag required.')
        raw=canonical(result)
        if len(raw.encode())>32768:raise ContractError('result_too_large','Worker result exceeds local limit.')
        with self.transaction():
            self.scope(scope,lease['project'],write=True)
            row=self.db.execute('SELECT project,status,fencing,lease_until,lease_actor FROM jobs WHERE source_seq=?',(lease['source_seq'],)).fetchone()
            if row is None or row!=(lease['project'],'leased',lease['fencing'],lease['lease_until'],scope.principal_id) or now>=row[3]:
                raise ContractError('stale_lease','Worker lease expired or was replaced.')
            self.db.execute('UPDATE jobs SET status=?,result=?,due=? WHERE source_seq=?',('succeeded' if success else 'retry_wait',raw,now+retry_delay,lease['source_seq']))

    def source(self,scope,seq):
        integer(seq,1)
        with self.transaction():
            row=self.db.execute('SELECT project,payload,hash,binding_revision FROM sources WHERE seq=? AND workspace=?',(seq,self.workspace)).fetchone()
            self.scope(scope,human=row is not None and row[0] is None)
            if row is None:raise ContractError('source_unavailable','Selected source is unavailable.')
            if row[0]:self.scope(scope,row[0])
            if digest(row[1])!=row[2]:raise ContractError('source_corrupt','Source payload failed integrity validation.')
            event=validate_source_event(json.loads(row[1]))
            return dict(event=event,project=row[0],binding_revision=row[3])

    def plan(self,scope,project,key,operations):
        self.scope(scope,project,write=True);identifier(key)
        if type(operations) is not list or not 1<=len(operations)<=64:
            raise ContractError('invalid_change','Bounded nonempty operations required.')
        raw=canonical(operations)
        if len(raw.encode())>32768:raise ContractError('change_too_large','Change set exceeds local limit.')
        base=self.project(scope,project)['knowledge_revision']
        plan=dict(format='decivora-change-1',project=project,key=key,base_revision=base,operations=json.loads(raw))
        return dict(plan,digest=digest(canonical(plan)))

    def _check_plan(self,plan):
        if type(plan) is not dict or set(plan)!={'format','project','key','base_revision','operations','digest'} or plan['format']!='decivora-change-1':
            raise ContractError('invalid_change','Unsupported change set fields.')
        identifier(plan['project']);identifier(plan['key']);integer(plan['base_revision'])
        if type(plan['operations']) is not list or not 1<=len(plan['operations'])<=64:
            raise ContractError('invalid_change','Bounded operation list required.')
        if len(canonical(plan).encode('utf-8'))>32768:raise ContractError('change_too_large','Change set exceeds local limit.')
        if digest(canonical({k:v for k,v in plan.items() if k!='digest'}))!=plan['digest']:
            raise ContractError('change_digest_mismatch','Change set content changed after preview.')

    def approve(self,scope,plan):
        self._check_plan(plan)
        with self.transaction():
            self.scope(scope,plan['project'],write=True,human=True)
            if self.project(scope,plan['project'])['knowledge_revision']!=plan['base_revision']:
                raise ContractError('stale_base','Project knowledge changed after preview.')
            approval='approval_'+uuid.uuid4().hex
            self.db.execute('INSERT INTO approvals VALUES (?,?,?,?,?,?,?,?)',(approval,self.workspace,plan['project'],scope.principal_id,plan['digest'],plan['base_revision'],self.authority.revision(),plan['key']))
            self.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.workspace,plan['project'],scope.principal_id,'approve',approval))
        return approval

    def apply(self,scope,plan,approval):
        self._check_plan(plan)
        project=plan['project']
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            prior=self.db.execute('SELECT actor,digest,result FROM commands WHERE workspace=? AND project=? AND key=?',(self.workspace,project,plan['key'])).fetchone()
            if prior:
                if prior[:2]!=(scope.principal_id,plan['digest']):raise ContractError('idempotency_conflict','Command key conflicts with prior content.')
                return json.loads(prior[2])
            expected=(self.workspace,project,scope.principal_id,plan['digest'],plan['base_revision'],self.authority.revision(),plan['key'])
            if self.db.execute('SELECT workspace,project,approver,digest,base_revision,authz_revision,command_key FROM approvals WHERE id=?',(approval,)).fetchone()!=expected:
                raise ContractError('invalid_approval','Approval does not match current identity, scope or authority.')
            if self.project(scope,project)['knowledge_revision']!=plan['base_revision']:
                raise ContractError('stale_base','Project knowledge changed after approval.')
            operations=plan['operations'];temp={}
            for op in operations:
                if type(op) is not dict or op.get('op') not in ('create','update','link','end_link'):
                    raise ContractError('invalid_operation','Only typed create/update/link operations are supported.')
                if op['op']=='create':
                    identifier(op['id'])
                    if op['id'] in temp:raise ContractError('duplicate_temp_id','Temporary ID repeated.')
                    temp[op['id']]='record_'+digest(canonical([self.workspace,project,plan['key'],op['id']]))[:24]
            sequences=[]
            for op in sorted(operations,key=lambda item:item['op'] in ('link','end_link')):
                op=dict(op)
                if op['op']=='create':
                    if set(op) not in ({'op','id','body'},{'op','id','body','source_seq'}):raise ContractError('invalid_operation','Create fields are invalid.')
                    if 'source_seq' in op:integer(op['source_seq'],1)
                    op['id']=temp[op['id']]
                    self._body(op['body'])
                    stream=op['id'];version=1
                elif op['op']=='update':
                    if set(op)!={'op','id','base_version','body'}:raise ContractError('invalid_operation','Update fields are invalid.')
                    identifier(op['id']);integer(op['base_version'],1);self._body(op['body'])
                    record=self.db.execute('SELECT version FROM records WHERE workspace=? AND project=? AND id=?',(self.workspace,project,op['id'])).fetchone()
                    if record is None or record[0]!=op['base_version']:raise ContractError('stale_record','Record version changed.')
                    stream=op['id'];version=record[0]+1
                else:
                    fields={'op','origin','target','kind'} if op['op']=='link' else {'op','origin','target','kind','base_version','state'}
                    if set(op)!=fields or op['kind'] not in RELATIONS:
                        raise ContractError('invalid_operation','Link fields are invalid.')
                    op['origin']=temp.get(op['origin'],op['origin']);op['target']=temp.get(op['target'],op['target'])
                    identifier(op['origin']);identifier(op['target'])
                    previous=self.db.execute('SELECT revision,state FROM edges WHERE workspace=? AND project=? AND origin=? AND target=? AND kind=?',(self.workspace,project,op['origin'],op['target'],op['kind'])).fetchone()
                    if op['op']=='end_link':
                        integer(op['base_version'],1)
                        if previous is None or previous[0]!=op['base_version'] or previous[1]!='asserted' or op['state'] not in ('ended','invalidated'):
                            raise ContractError('stale_edge','Edge revision or requested lifecycle is invalid.')
                    elif previous and previous[1]=='asserted':raise ContractError('edge_conflict','Relationship is already asserted.')
                    stream='edge_'+digest(canonical([op['origin'],op['target'],op['kind']]))[:24];version=previous[0]+1 if previous else 1
                seq=self.db.execute('INSERT INTO events(workspace,project,stream,version,kind,payload) VALUES (?,?,?,?,?,?)',(self.workspace,project,stream,version,op['op'],canonical(op))).lastrowid
                self._project_event(op,project,seq)
                sequences.append(seq)
            # Validate typed graph invariants BEFORE committing canonical events.
            self._graph(project)
            self.db.execute('UPDATE projects SET knowledge_revision=knowledge_revision+1 WHERE workspace=? AND id=?',(self.workspace,project))
            result=dict(status='applied',event_sequences=sequences,temp_ids=temp,knowledge_revision=plan['base_revision']+1)
            self.db.execute('INSERT INTO commands VALUES (?,?,?,?,?,?)',(self.workspace,project,plan['key'],scope.principal_id,plan['digest'],canonical(result)))
            self.db.execute('INSERT INTO audit(workspace,project,actor,action,ref) VALUES (?,?,?,?,?)',(self.workspace,project,scope.principal_id,'apply',approval))
        return result

    @staticmethod
    def _body(body):
        if type(body) is not dict or set(body)!={'type','title','description'} or body['type'] not in TYPES:
            raise ContractError('invalid_record','Unsupported canonical record body.')
        if type(body['title']) is not str or not 1<=len(body['title'])<=256 or type(body['description']) is not str or len(body['description'])>8192:
            raise ContractError('invalid_record','Record text is invalid or exceeds limits.')

    def _project_event(self,op,project,seq):
        if op['op']=='create':
            self.db.execute('INSERT INTO records VALUES (?,?,?,?,?)',(self.workspace,project,op['id'],1,canonical(op['body'])))
            if 'source_seq' in op:self.db.execute('INSERT INTO record_sources VALUES (?,?,?,?)',(self.workspace,project,op['id'],op['source_seq']))
        elif op['op']=='update':
            self.db.execute('UPDATE records SET version=?,body=? WHERE workspace=? AND project=? AND id=?',(op['base_version']+1,canonical(op['body']),self.workspace,project,op['id']))
        elif op['op']=='link':
            self.db.execute("INSERT INTO edges VALUES (?,?,?,?,?,1,'asserted',?,NULL) ON CONFLICT(workspace,project,origin,target,kind) DO UPDATE SET revision=revision+1,state='asserted',valid_from=excluded.valid_from,valid_to=NULL",(self.workspace,project,op['origin'],op['target'],op['kind'],seq))
        else:
            self.db.execute('UPDATE edges SET revision=revision+1,state=?,valid_to=? WHERE workspace=? AND project=? AND origin=? AND target=? AND kind=?',(op['state'],seq,self.workspace,project,op['origin'],op['target'],op['kind']))

    def records(self,scope,project,*,limit=50,cursor=None):
        integer(limit,1)
        if limit>100:raise ContractError('query_limit','Query limit exceeds 100.')
        with self.transaction():
            self.scope(scope,project)
            snapshot=self.project(scope,project)['knowledge_revision'];after=''
            if cursor is not None:
                if type(cursor) is not dict or set(cursor)!={'workspace','project','snapshot','limit','after'} or (cursor['workspace'],cursor['project'],cursor['snapshot'],cursor['limit'])!=(self.workspace,project,snapshot,limit):
                    raise ContractError('stale_cursor','Cursor scope/filter/snapshot changed; refresh the query.')
                after=identifier(cursor['after'])
                if not self.db.execute('SELECT 1 FROM records WHERE workspace=? AND project=? AND id=?',(self.workspace,project,after)).fetchone():
                    raise ContractError('stale_cursor','Cursor record is unavailable.')
            rows=self.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? AND id>? ORDER BY id LIMIT ?',(self.workspace,project,after,limit+1)).fetchall()
            more=len(rows)>limit
            return dict(records=[dict(id=r[0],version=r[1],body=json.loads(r[2])) for r in rows[:limit]],truncated=more,knowledge_revision=snapshot,
                next_cursor=dict(workspace=self.workspace,project=project,snapshot=snapshot,limit=limit,after=rows[limit-1][0]) if more else None)

    def create_budget(self,scope,project,run,token_cap):
        identifier(run);integer(token_cap,1)
        if token_cap>100000:raise ContractError('budget_limit','Local synthetic run cap exceeds the development ceiling.')
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            self.db.execute('INSERT INTO run_budgets VALUES (?,?,?,?)',(self.workspace,project,run,token_cap))

    def reserve(self,scope,project,root_run,key,tokens):
        identifier(root_run);identifier(key);integer(tokens,1)
        with self.transaction():
            self.scope(scope,project,write=True)
            cap=self.db.execute('SELECT token_cap FROM run_budgets WHERE workspace=? AND project=? AND run=?',(self.workspace,project,root_run)).fetchone()
            if cap is None:raise ContractError('budget_unavailable','A human-created shared run budget is required.')
            previous=self.db.execute('SELECT tokens,status,actual FROM reservations WHERE workspace=? AND project=? AND run=? AND key=?',(self.workspace,project,root_run,key)).fetchone()
            if previous:
                if previous[0]!=tokens:raise ContractError('idempotency_conflict','Reservation key changed token amount.')
                return dict(root_run=root_run,key=key,reserved=previous[0],status=previous[1],actual=previous[2])
            used=self.db.execute('SELECT coalesce(sum(CASE WHEN actual IS NULL THEN tokens ELSE actual END),0) FROM reservations WHERE workspace=? AND project=? AND run=?',(self.workspace,project,root_run)).fetchone()[0]
            if used+tokens>cap[0]:raise ContractError('budget_exceeded','Shared root-run budget exhausted; no dispatch performed.')
            total=self.db.execute('SELECT coalesce(sum(CASE WHEN actual IS NULL THEN tokens ELSE actual END),0) FROM reservations WHERE workspace=?',(self.workspace,)).fetchone()[0]
            if total+tokens>100000:raise ContractError('workspace_budget_exceeded','Local workspace reservation ceiling exhausted; a new root run cannot bypass it.')
            self.db.execute('INSERT INTO reservations VALUES (?,?,?,?,?,?,NULL)',(self.workspace,project,root_run,key,tokens,'reserved'))
            return dict(root_run=root_run,key=key,reserved=tokens,status='reserved',actual=None)

    def settle(self,scope,project,root_run,key,actual=None):
        if actual is not None:integer(actual)
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            previous=self.db.execute('SELECT tokens,status,actual FROM reservations WHERE workspace=? AND project=? AND run=? AND key=?',(self.workspace,project,root_run,key)).fetchone()
            if previous is None:raise ContractError('reservation_unavailable','Reservation is unavailable.')
            if previous[1]=='settled':
                if previous[2]!=actual:raise ContractError('settlement_conflict','Settled usage cannot be rewritten.')
                return
            if actual is not None and actual>previous[0]:raise ContractError('usage_overrun','Actual usage exceeds reservation; requires separate review.')
            self.db.execute('UPDATE reservations SET status=?,actual=? WHERE workspace=? AND project=? AND run=? AND key=?',('unknown' if actual is None else 'settled',actual,self.workspace,project,root_run,key))

    def projection_digest(self,scope,project):
        self.scope(scope,project)
        records=self.db.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id',(self.workspace,project)).fetchall()
        edges=self.db.execute('SELECT origin,target,kind,revision,state,valid_from,valid_to FROM edges WHERE workspace=? AND project=? ORDER BY origin,target,kind',(self.workspace,project)).fetchall()
        sources=self.db.execute('SELECT record,source_seq FROM record_sources WHERE workspace=? AND project=? ORDER BY record,source_seq',(self.workspace,project)).fetchall()
        return digest(canonical(dict(records=records,edges=edges,sources=sources)))

    def _graph(self,project):
        from packages.impact.graph import DependencyGraph
        nodes=self.db.execute('SELECT id FROM records WHERE workspace=? AND project=?',(self.workspace,project)).fetchall()
        pending=self.db.execute("SELECT count(*) FROM jobs WHERE project=? AND status!='succeeded'",(project,)).fetchone()[0]
        graph=DependencyGraph({r[0]:{'eligible':False,'verification':'unknown'} for r in nodes},complete=pending==0,
            revision=self.db.execute('SELECT knowledge_revision FROM projects WHERE workspace=? AND id=?',(self.workspace,project)).fetchone()[0]+1)
        for origin,target,kind in self.db.execute("SELECT origin,target,kind FROM edges WHERE workspace=? AND project=? AND state='asserted'",(self.workspace,project)):
            graph.add(origin,target,kind)
        return graph

    def graph(self,scope,project):
        with self.transaction():
            self.scope(scope,project)
            graph=self._graph(project)
            graph.revision=self.project(scope,project)['knowledge_revision']
            return graph

    def historical_edges(self,scope,project,snapshot_seq):
        integer(snapshot_seq)
        with self.transaction():
            self.scope(scope,project)
            edges={}
            for seq,kind,raw in self.db.execute('SELECT seq,kind,payload FROM events WHERE workspace=? AND project=? AND seq<=? ORDER BY seq',(self.workspace,project,snapshot_seq)):
                if kind not in ('link','end_link'):continue
                op=json.loads(raw);key=(op['origin'],op['target'],op['kind'])
                previous=edges.get(key,{})
                edges[key]=dict(origin=key[0],target=key[1],kind=key[2],revision=previous.get('revision',0)+1,
                    state='asserted' if kind=='link' else op['state'],sequence=seq)
            return list(edges.values())

    def replay(self,scope,project):
        with self.transaction():
            self.scope(scope,project,write=True,human=True)
            rows=self.db.execute('SELECT seq,kind,payload FROM events WHERE workspace=? AND project=? ORDER BY seq',(self.workspace,project)).fetchall()
            for _,kind,raw in rows:
                op=json.loads(raw)
                if op.get('op')!=kind or kind not in ('create','update','link','end_link'):
                    raise ContractError('unsupported_event','Unknown event version or kind; replay stopped.')
            self.db.execute('DELETE FROM edges WHERE workspace=? AND project=?',(self.workspace,project))
            self.db.execute('DELETE FROM record_sources WHERE workspace=? AND project=?',(self.workspace,project))
            self.db.execute('DELETE FROM records WHERE workspace=? AND project=?',(self.workspace,project))
            for seq,_,raw in rows:self._project_event(json.loads(raw),project,seq)
            result=self.projection_digest(scope,project)
        return dict(digest=result,events=len(rows),model_dispatches=0,external_dispatches=0)

    def backup(self,scope,target):
        self.scope(scope,human=True)
        for project, in self.db.execute('SELECT id FROM projects WHERE workspace=?',(self.workspace,)):
            self.scope(scope,project)
        target=Path(target)
        fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
        destination=sqlite3.connect(target)
        try:
            self.db.backup(destination)
            if destination.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or destination.execute('PRAGMA foreign_key_check').fetchall():
                raise ContractError('backup_invalid','Backup integrity failed.')
            projections={}
            for project, in destination.execute('SELECT id FROM projects WHERE workspace=?',(self.workspace,)):
                records=destination.execute('SELECT id,version,body FROM records WHERE workspace=? AND project=? ORDER BY id',(self.workspace,project)).fetchall()
                edges=destination.execute('SELECT origin,target,kind,revision,state,valid_from,valid_to FROM edges WHERE workspace=? AND project=? ORDER BY origin,target,kind',(self.workspace,project)).fetchall()
                sources=destination.execute('SELECT record,source_seq FROM record_sources WHERE workspace=? AND project=? ORDER BY record,source_seq',(self.workspace,project)).fetchall()
                projections[project]=digest(canonical(dict(records=records,edges=edges,sources=sources)))
        finally:destination.close()
        return dict(format=FORMAT,workspace=self.workspace,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),projection_digests=projections,external_dispatches=0)

    @classmethod
    def restore(cls,backup,target,manifest):
        """Restore only into a new selected file; source payloads are inside this DB."""
        raw=Path(backup).read_bytes()
        if manifest.get('format')!=FORMAT or hashlib.sha256(raw).hexdigest()!=manifest.get('sha256'):
            raise ContractError('backup_invalid','Backup manifest/content mismatch.')
        identifier(manifest['workspace'])
        fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'wb') as output:output.write(raw)
        try:
            restored=cls(target,manifest['workspace'])
            if restored.db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                restored.close();raise ContractError('backup_invalid','Restored database integrity failed.')
            for payload,sha in restored.db.execute('SELECT payload,hash FROM sources'):
                if digest(payload)!=sha:
                    restored.close();raise ContractError('backup_invalid','Restored source payload is missing or corrupt.')
            projects={p for p, in restored.db.execute('SELECT id FROM projects WHERE workspace=?',(restored.workspace,))}
            if set(manifest.get('projection_digests',{}))!=projects:
                restored.close();raise ContractError('backup_invalid','Backup projection manifest is incomplete.')
            owner=restored.authority.issue_scope(restored.authority.owner_id)
            for project in projects:
                if restored.projection_digest(owner,project)!=manifest['projection_digests'][project]:
                    restored.close();raise ContractError('backup_invalid','Restored projection differs from backup manifest.')
            return restored
        except Exception:
            Path(target).unlink()
            raise

"""Audit-backed indexes and bounded project/snapshot source pagination.

Indexes are additive accelerators in authorized source writes. No source IDs,
payloads, immutable audit rows or SQL storage-format version are rewritten.
"""
import base64,json
from packages.domain.source_event import ContractError
SOURCE_CAPACITY=1000
PAGE_SIZE=25


def install_indexes(core):
    if not core.db.in_transaction:raise ContractError('transaction_required','Source indexes require an authorized write transaction.')
    core.db.execute('CREATE INDEX IF NOT EXISTS conversation_audit_action ON audit(workspace,project,action,seq)')
    core.db.execute("CREATE INDEX IF NOT EXISTS conversation_source_id ON audit(workspace,project,json_extract(ref,'$.id'),seq) WHERE action='conversation_imported'")
    core.db.execute("CREATE INDEX IF NOT EXISTS conversation_source_origin ON audit(workspace,project,json_extract(ref,'$.capture.profile_ref'),json_extract(ref,'$.capture.thread_id'),json_extract(ref,'$.capture.turn_id'),json_extract(ref,'$.capture.item_id')) WHERE action='conversation_imported'")
    for suffix in ('analysis_started','analysis_finished','candidates_applied','enqueued','dispatch_authorized'):
        core.db.execute(f"CREATE INDEX IF NOT EXISTS conversation_{suffix}_source ON audit(workspace,project,json_extract(ref,'$.source'),seq) WHERE action='conversation_{suffix}'")


def count(core,project):
    return core.db.execute("SELECT count(*) FROM audit WHERE workspace=? AND project=? AND action='conversation_imported'",(core.workspace,project)).fetchone()[0]


def find(core,project,source_id):
    row=core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND json_extract(ref,'$.id')=? ORDER BY seq LIMIT 1",(core.workspace,project,source_id)).fetchone()
    return json.loads(row[0]) if row else None


def origin(core,project,profile,thread,turn,item):
    row=core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND json_extract(ref,'$.capture.profile_ref')=? AND json_extract(ref,'$.capture.thread_id')=? AND json_extract(ref,'$.capture.turn_id')=? AND json_extract(ref,'$.capture.item_id')=? ORDER BY seq LIMIT 1",(core.workspace,project,profile,thread,turn,item)).fetchone()
    return json.loads(row[0]) if row else None


def page(core,project,*,cursor=None,limit=PAGE_SIZE,source_id=None):
    if type(limit) is not int or not 1<=limit<=50:raise ContractError('invalid_request','Source page size must be between one and fifty.')
    total=count(core,project)
    if source_id is not None:
        if cursor is not None:raise ContractError('invalid_source_cursor','Choose a page cursor or one exact source.')
        source=find(core,project,source_id)
        if source is None:raise ContractError('source_unavailable','Conversation unavailable.')
        return dict(sources=[source],total=total,next_cursor=None,has_more=False)
    after=0
    ceiling=core.db.execute("SELECT coalesce(max(seq),0) FROM audit WHERE workspace=? AND project=? AND action='conversation_imported'",(core.workspace,project)).fetchone()[0]
    if cursor is not None:
        try:
            if type(cursor) is not str or not 1<=len(cursor)<=512:raise ValueError()
            value=json.loads(base64.b64decode(cursor.encode('ascii'),altchars=b'-_',validate=True))
            if type(value) is not dict or set(value)!={'workspace','project','after','ceiling'} or value['workspace']!=core.workspace or value['project']!=project:raise ValueError()
            after=value['after'];pinned=value['ceiling']
            if type(after) is not int or type(pinned) is not int or not 0<after<=pinned<=ceiling:raise ValueError()
            for seq in (after,pinned):
                if not core.db.execute("SELECT 1 FROM audit WHERE seq=? AND workspace=? AND project=? AND action='conversation_imported'",(seq,core.workspace,project)).fetchone():raise ValueError()
            ceiling=pinned
        except (ValueError,TypeError,KeyError,UnicodeError):
            raise ContractError('invalid_source_cursor','Source cursor does not match this selected project snapshot.') from None
    rows=core.db.execute("SELECT seq,ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND seq>? AND seq<=? ORDER BY seq LIMIT ?",(core.workspace,project,after,ceiling,limit+1)).fetchall()
    more=len(rows)>limit;rows=rows[:limit];next_cursor=None
    if more:next_cursor=base64.urlsafe_b64encode(json.dumps(dict(workspace=core.workspace,project=project,after=rows[-1][0],ceiling=ceiling),separators=(',',':')).encode()).decode()
    return dict(sources=[json.loads(raw) for _,raw in rows],total=total,next_cursor=next_cursor,has_more=more)


def nearby(core,project,source):
    capture=source['capture']
    row=core.db.execute("SELECT seq FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND json_extract(ref,'$.id')=?",(core.workspace,project,source['id'])).fetchone()
    if not row:return []
    rows=core.db.execute("SELECT ref FROM audit WHERE workspace=? AND project=? AND action='conversation_imported' AND seq<? AND json_extract(ref,'$.capture.id')=? AND json_extract(ref,'$.capture.thread_id')=? ORDER BY seq DESC LIMIT 7",(core.workspace,project,row[0],capture['id'],capture['thread_id'])).fetchall()
    return list(reversed([json.loads(raw) for raw, in rows]))


def queue_rows(core,project,*,pending_only=False,limit=50):
    base="""SELECT s.seq,json_extract(s.ref,'$.id') AS id,json_extract(s.ref,'$.source_kind') AS kind,
      json_extract(s.ref,'$.received_at') AS received,
      coalesce((SELECT json_extract(f.ref,'$.status') FROM audit f WHERE f.workspace=s.workspace AND f.project=s.project AND f.action='conversation_analysis_finished' AND json_extract(f.ref,'$.source')=json_extract(s.ref,'$.id') ORDER BY f.seq DESC LIMIT 1),
       CASE WHEN EXISTS(SELECT 1 FROM audit a WHERE a.workspace=s.workspace AND a.project=s.project AND a.action='conversation_analysis_started' AND json_extract(a.ref,'$.source')=json_extract(s.ref,'$.id')) THEN 'Analysis unknown' ELSE 'Waiting for model' END) AS status,
      EXISTS(SELECT 1 FROM audit a WHERE a.workspace=s.workspace AND a.project=s.project AND a.action='conversation_enqueued' AND json_extract(a.ref,'$.source')=json_extract(s.ref,'$.id')) AS enqueued,
      EXISTS(SELECT 1 FROM audit a WHERE a.workspace=s.workspace AND a.project=s.project AND a.action='conversation_candidates_applied' AND json_extract(a.ref,'$.source')=json_extract(s.ref,'$.id')) AS applied
      FROM audit s WHERE s.workspace=? AND s.project=? AND s.action='conversation_imported'"""
    query='SELECT * FROM ('+base+") WHERE status='Waiting for model' ORDER BY seq LIMIT ?" if pending_only else 'SELECT * FROM ('+base+') ORDER BY seq LIMIT ?'
    return [dict(zip(('seq','source_id','source_kind','received_at','status','durable_outbox','applied'),row)) for row in core.db.execute(query,(core.workspace,project,limit))]


def queue_summary(core,project):
    rows=queue_rows(core,project,limit=SOURCE_CAPACITY)
    from collections import Counter
    return dict(total=count(core,project),counts=dict(Counter(r['status'] for r in rows)),
                applied_sources=sum(r['applied'] for r in rows),items=[dict(r,durable_outbox=bool(r['durable_outbox']),applied=bool(r['applied'])) for r in rows[:PAGE_SIZE]],items_truncated=len(rows)>PAGE_SIZE)

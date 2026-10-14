"""Isolated synthetic history/source/graph/read-write load; no provider or live DB."""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,sys,tempfile,threading,time
from collections import Counter
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apps.local_ui.server import make_server
from packages.capture.conversations import ConversationService
from packages.domain.task_workflow import TaskWorkflowService
from packages.domain.decision_impact import DecisionImpactService
from packages.domain.source_event import ContractError
from measure_local_performance import stats

def measure(origin,path,headers,n=20,workers=1):
    if not origin.startswith('http://127.0.0.1:'):raise ValueError('Local fixture only')
    def one(_):
        start=time.perf_counter()
        try:
            with urlopen(Request(origin+path,headers=headers),timeout=10) as response:data=response.read();code=response.status
        except HTTPError as error:data=error.read();code=error.code
        except (TimeoutError,OSError):data=b'';code='transport_failure'
        return (time.perf_counter()-start)*1000,code,len(data)
    one(-1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(one,range(n)))
    passed=[r[0] for r in rows if r[1]==200]
    return dict(path=path,workers=workers,samples=n,status_counts=dict(Counter(str(r[1]) for r in rows)),failed_requests=sum(r[1]!=200 for r in rows),success_timing=stats(passed) if passed else None,all_timing=stats([r[0] for r in rows]),response_bytes_max=max(r[2] for r in rows))

PROFILES=[dict(name='small_mixed',tasks=30,decisions=5,sources=4,source_bytes=1000,history=100,fanout=1),
          dict(name='medium_mixed',tasks=60,decisions=10,sources=12,source_bytes=6000,history=300,fanout=2),
          dict(name='dense_mixed',tasks=100,decisions=10,sources=32,source_bytes=11900,history=900,fanout=3)]

def run(profile,impact_previews=0):
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'synthetic.sqlite';server=make_server(path);app=server.app;seq=0;diagnostics=[]
        original_state=app.state
        def observed_state(*args,**kwargs):
            try:return original_state(*args,**kwargs)
            except Exception as error:
                reason=str(error) if str(error) in ('database is locked','database table is locked') else 'message_not_recorded'
                diagnostics.append(dict(type=type(error).__name__,reason=reason));raise
        app.state=observed_state
        def apply(core,scope,ops):
            nonlocal seq
            seq+=1;plan=core.plan(scope,'personal','fixture_'+str(seq),ops);return core.apply(scope,plan,core.approve(scope,plan))
        setup_start=time.perf_counter()
        with app.core() as core:
            owner=core.authority.issue_scope('local_owner');tasks=[];decisions=[]
            for kind,count,ids in [('Task',profile['tasks'],tasks),('Decision',profile['decisions'],decisions)]:
                for i in range(count):ids.append(apply(core,owner,[dict(op='create',id='r',body=dict(type=kind,title=f'Synthetic {kind} {i}',description='Synthetic bounded scope'))])['temp_ids']['r'])
            edges=0
            for i,task in enumerate(tasks):
                ops=[dict(op='link',origin=task,target=decisions[i%len(decisions)],kind='required_by')]
                ops.extend(dict(op='link',origin=task,target=tasks[i-j],kind='depends_on') for j in range(1,min(i,profile['fanout'])+1))
                apply(core,owner,ops);edges+=len(ops)
            history_start=time.perf_counter()
            for i in range(profile['history']):
                task=tasks[i%len(tasks)];version=core.db.execute('SELECT version FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,'personal',task)).fetchone()[0]
                apply(core,owner,[dict(op='update',id=task,base_version=version,body=dict(type='Task',title='Synthetic revision '+str(i),description='Synthetic context change; old revisions retained.'))])
            history_setup_ms=(time.perf_counter()-history_start)*1000
            service=ConversationService(core)
            source_ids=[]
            for i in range(profile['sources']):
                prefix=f'Synthetic conversation {i}: '
                source_ids.append(service.ingest(owner,'personal',text=prefix+('x'*(profile['source_bytes']-len(prefix))))['id'])
            # Partial criteria/history fixture on five tasks; finish prerequisites remain.
            workflow=TaskWorkflowService(core)
            for i,task in enumerate(tasks[:5]):
                version=workflow._task('personal',task)['version']
                criterion=lambda id:dict(id=id,statement='Synthetic manual criterion',method='human_review',required=True,applicable=True,applicability_reason='')
                apply(core,owner,[dict(op='acceptance_contract',task=task,task_version=version,base_contract=0,criteria=[criterion('AC1')],dod=[criterion('DOD1')],reason='Synthetic criteria fixture',acknowledged_changes=[])])
                for stage in ('In Progress','In Review','Awaiting Verification'):
                    view=workflow.view(owner,'personal',task)
                    workflow.transition(owner,'personal',task=task,task_version=version,base_revision=view['revision'],stage=stage,reason='Synthetic implementation handoff',key=f'stage_{i}_{stage.replace(" ","_")}')
                # Keep contradictory/partial evidence without claiming full task completion.
                for j in range(10):workflow.evidence(owner,'personal',task=task,task_version=version,contract_version=1,criterion='AC1',status='passed' if j%2 else 'failed',reference='Synthetic local review',note='Not real verification',key=f'ev_{i}_{j}')
            counts={table:core.db.execute(f'SELECT count(*) FROM {table} WHERE workspace=? AND project=?',(core.workspace,'personal')).fetchone()[0] for table in ('records','events','audit','edges')}
            received=len(service._rows('personal','conversation_imported'))
            overflow=False
            if profile['sources']==32:
                try:service.ingest(owner,'personal',text='Synthetic overflow attempt')
                except ContractError as error:overflow=error.code=='conversation_limit'
                assert overflow and len(service._rows('personal','conversation_imported'))==32
            oversized=False
            try:service.ingest(owner,'personal',text='x'*12001)
            except ContractError as error:oversized=error.code=='conversation_limit'
            assert oversized
            projection_before=core.projection_digest(owner,'personal')
            for i in range(impact_previews):
                DecisionImpactService(core).preview(owner,'personal',decision=decisions[i%len(decisions)],decision_version=1,base_revision=core.project(owner,'personal')['knowledge_revision'],key='load_impact_'+str(i))
            assert core.projection_digest(owner,'personal')==projection_before
        setup_ms=(time.perf_counter()-setup_start)*1000
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            headers={'Cookie':'decivora_session='+app.cookie,'Origin':server.origin}
            sequential=measure(server.origin,'/api/state',headers,n=20)
            concurrent_read_metrics=measure(server.origin,'/api/state',headers,n=24,workers=4)
            def read(_):
                start=time.perf_counter()
                try:
                    with urlopen(Request(server.origin+'/api/state',headers=headers),timeout=15) as response:state=json.loads(response.read())
                except HTTPError as error:error.read();return (time.perf_counter()-start)*1000,None,error.code
                except (TimeoutError,OSError):return (time.perf_counter()-start)*1000,None,'transport_failure'
                assert state['selected_project']=='personal' and len(state['conversation_review']['imports'])==received
                assert len(state['records'])<=100 and all(task['lane']!='Done' for task in state['tasks'])
                return (time.perf_counter()-start)*1000,state['snapshot'],200
            def writer():
                durations=[]
                with app.core() as core:
                    owner=core.authority.issue_scope('local_owner')
                    for i in range(12):
                        rid=tasks[-1];version=core.db.execute('SELECT version FROM records WHERE workspace=? AND project=? AND id=?',(core.workspace,'personal',rid)).fetchone()[0]
                        start=time.perf_counter();apply(core,owner,[dict(op='update',id=rid,base_version=version,body=dict(type='Task',title='Synthetic concurrent '+str(i),description='Synthetic write concurrent with reads.'))]);durations.append((time.perf_counter()-start)*1000)
                return durations
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
                future=pool.submit(writer);rows=list(pool.map(read,range(24)));writes=future.result(timeout=30)
            snapshot=app.state()
            assert len(snapshot['impact_reviews'])==min(impact_previews,5)
            assert all(item['stale'] for item in snapshot['impact_reviews'])
            with app.core() as core:
                owner=core.authority.issue_scope('local_owner');end_sources=len(ConversationService(core)._rows('personal','conversation_imported'))
                assert end_sources==received
                assessment=TaskWorkflowService(core).view(owner,'personal',tasks[-1])
                assert assessment['assessment']['finish_blocked'] is True and assessment['stage']!='Done'
            revisions=[x[1] for x in rows if x[2]==200]
            return dict(impact_previews_seeded=impact_previews,impact_reviews_returned=len(snapshot['impact_reviews']),impact_reviews_stale_after_write=all(item['stale'] for item in snapshot['impact_reviews']),profile=profile,setup_ms=round(setup_ms,2),history_setup_ms=round(history_setup_ms,2),database_bytes=path.stat().st_size,stored=counts,sources_preserved=end_sources,source_total_bytes=profile['sources']*profile['source_bytes'],returned_tasks=len(snapshot['tasks']),returned_records=len(snapshot['records']),truncated=snapshot['truncated'],sequential=sequential,concurrent_reads=concurrent_read_metrics,read_during_write=dict(all_timing=stats([x[0] for x in rows]),status_counts=dict(Counter(str(x[2]) for x in rows)),failed_requests=sum(x[2]!=200 for x in rows)),writer=stats(writes),observed_snapshot_min=min(revisions) if revisions else None,observed_snapshot_max=max(revisions) if revisions else None,server_exception_counts=[dict(type=t,reason=r,count=n) for (t,r),n in Counter((d['type'],d['reason']) for d in diagnostics).items()],oversized_source_rejected=oversized,source_overflow_rejected=overflow if profile['sources']==32 else None,false_done_count=sum(task['lane']=='Done' for task in snapshot['tasks']),paid_model_calls=0)
        finally:server.shutdown();server.server_close();thread.join(timeout=3)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--impact-previews',type=int,default=0,choices=range(0,33));args=parser.parse_args()
    result=dict(date='2026-10-14',workload='isolated sources, graph, revisions, partial criteria, concurrent reads/writes',model_calls=0,user_database_modified=False,profiles=[])
    for profile in PROFILES:
        row=run(profile,args.impact_previews)
        result['profiles'].append(row);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(profile=profile['name'],sequential=row['sequential']['all_timing'],concurrent=row['concurrent_reads']['all_timing'],read_write_status=row['read_during_write']['status_counts'],diagnostics=row['server_exception_counts'],sources=row['sources_preserved'],records=row['stored']['records'],events=row['stored']['events'],audit=row['stored']['audit'],edges=row['stored']['edges'],truncated=row['truncated'])),flush=True)
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();args.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()

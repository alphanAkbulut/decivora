"""Bounded read-only localhost timings and isolated synthetic UI load; no model calls.

No request/response contents, cookies, paths or credentials are emitted in results.
HTTP measurements include new TCP connection overhead; no internet benchmark.
"""
import argparse,concurrent.futures,cProfile,io,json,math,pstats,statistics,tempfile,threading,time
from pathlib import Path
from urllib.request import Request,urlopen
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from apps.local_ui.server import make_server

def stats(values):
    v=sorted(values)
    return dict(samples=len(v),median_ms=round(statistics.median(v),3),p95_ms=round(v[max(0,math.ceil(.95*len(v))-1)],3),max_ms=round(max(v),3))

def measure(origin,path,headers=None,n=30,workers=1):
    if origin not in ('http://127.0.0.1:53610','http://127.0.0.1:8765') and not origin.startswith('http://127.0.0.1:'):
        raise ValueError('Only localhost permitted')
    def one(_):
        start=time.perf_counter()
        with urlopen(Request(origin+path,headers=headers or {}),timeout=10) as response:
            first=time.perf_counter();data=response.read();end=time.perf_counter()
            return (first-start)*1000,(end-start)*1000,len(data),response.status
    one(0) # warm-up, excluded
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(one,range(n)))
    return dict(path=path,workers=workers,**stats([r[1] for r in rows]),ttfb=stats([r[0] for r in rows]),response_bytes_min=min(r[2] for r in rows),response_bytes_max=max(r[2] for r in rows),statuses=sorted({r[3] for r in rows}))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--session-file',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    meta=json.loads(args.session_file.read_text())
    if meta['origin']!='http://127.0.0.1:53610':raise ValueError('Unexpected live origin')
    # Routine session refresh to the same local application; no permission expansion.
    with urlopen(Request(meta['origin']+'/api/session',data=b'{}',headers={'Origin':meta['origin'],'Authorization':'Bearer '+meta['bootstrap'],'Content-Type':'application/json'}),timeout=5) as response:
        cookie=response.headers['Set-Cookie'].split(';')[0];response.read()
    headers={'Cookie':cookie,'Origin':meta['origin']}
    with urlopen(Request(meta['origin']+'/api/state',headers=headers),timeout=5) as response:state=json.loads(response.read())
    result=dict(date='2026-10-14',measurement='localhost development snapshot',model_calls=0,user_mutations=0,live_task_count=len(state['tasks']),live_truncated=state['truncated'],http=[],synthetic=[])
    for origin,path,h in [('http://127.0.0.1:8765','/',None),('http://127.0.0.1:8765','/api/status',None),(meta['origin'],'/',None),(meta['origin'],'/app.js',None),(meta['origin'],'/api/state',headers)]:
        result['http'].append(dict(surface='tracker' if ':8765' in origin else 'product',**measure(origin,path,h)))
    for origin,path,h in [('http://127.0.0.1:8765','/api/status',None),(meta['origin'],'/api/state',headers)]:
        result['http'].append(dict(surface='tracker' if ':8765' in origin else 'product',**measure(origin,path,h,n=32,workers=4)))
    with tempfile.TemporaryDirectory() as folder:
        server=make_server(Path(folder)/'synthetic.sqlite');thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            current=0
            for count in (10,50,100,150):
                while current<count:
                    server.app.command(dict(action='create_task',title='Synthetic task '+str(current),description='Synthetic performance fixture; not user work.'));current+=1
                snap=server.app.state()
                row=dict(stored_tasks=count,returned_tasks=len(snap['tasks']),truncated=snap['truncated'],http=measure(server.origin,'/api/state',{'Cookie':'decivora_session='+server.app.cookie},n=12))
                profile=cProfile.Profile();profile.enable();server.app.state();profile.disable()
                ranked=pstats.Stats(profile).sort_stats('cumulative')
                functions=sorted(ranked.stats.items(),key=lambda pair:pair[1][3],reverse=True)[:12]
                row['profile_top']=[dict(file=Path(k[0]).name,line=k[1],function=k[2],calls=v[1],cumulative_ms=round(v[3]*1000,3)) for k,v in functions]
                result['synthetic'].append(row)
        finally:server.shutdown();server.server_close();thread.join(timeout=3)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()

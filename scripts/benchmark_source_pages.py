#!/usr/bin/env python3
"""Bounded synthetic SQLite source/page benchmark; never opens a real workspace."""
import argparse,hashlib,json,math,platform,statistics,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from packages.storage.workspace import Workspace
from packages.capture.conversations import ConversationService
from packages.capture.processing_queue import ConversationQueue

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args()
 with tempfile.TemporaryDirectory() as directory:
  path=Path(directory)/'synthetic.sqlite'
  with Workspace(path,'benchmark',owner='owner') as core:
   a=core.authority;a.replace_grant(a.issue_scope('owner'),'owner',kind='human',readable=frozenset({'p'}),writable=frozenset({'p'}),active=True,base_revision=a.revision());scope=a.issue_scope('owner');core.create_project(scope,'p','Synthetic')
   service=ConversationService(core);started=time.perf_counter()
   for i in range(1000):last=service.ingest(scope,'p',text=('Synthetic source '+str(i)+' '+'x'*4096))
   ingest_seconds=time.perf_counter()-started
   def measure(call):
    values=[]
    for _ in range(20):
     start=time.perf_counter();call();values.append((time.perf_counter()-start)*1000)
    return dict(samples=len(values),p50_ms=round(statistics.median(values),3),p95_ms=round(sorted(values)[math.ceil(.95*len(values))-1],3))
   first=service.view(scope,'p');queue=ConversationQueue(core)
   results=dict(first_page=measure(lambda:service.view(scope,'p')),next_page=measure(lambda:service.view(scope,'p',cursor=first['next_cursor'])),exact_source=measure(lambda:service._source('p',last['id'])),queue_metadata=measure(lambda:queue.view(scope,'p')))
   integrity=core.db.execute('PRAGMA integrity_check').fetchone()[0]
   source_count=core.db.execute("SELECT count(*) FROM audit WHERE action='conversation_imported'").fetchone()[0]
  code_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('packages/capture/source_pages.py','packages/capture/conversations.py','packages/capture/processing_queue.py')}
  report=dict(code_sha256=code_hashes,kind='synthetic_source_pagination',date='2026-10-19',sources=source_count,message_bytes_approx=4118,ingest_seconds=round(ingest_seconds,3),db_bytes=path.stat().st_size,integrity=integrity,read_results=results,python=platform.python_version(),platform=platform.system(),model_calls=0,real_sources=0,concurrency=1,scope='Temporary standalone Workspace SQLite; not HTTP/browser/provider latency, concurrency SLA or RPO/RTO. No comparison speedup is inferred.')
 if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report))
 return 0
if __name__=='__main__':raise SystemExit(main())

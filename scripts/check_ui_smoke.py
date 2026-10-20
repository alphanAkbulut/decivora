"""Pinned-browser CI smoke over temporary synthetic servers; never a real provider."""
import argparse,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CASES=[('source-pages',{'DECIVORA_SOURCE_PAGES_UI_FIXTURE':'1','DECIVORA_PROJECT_UI_FIXTURE':'1'}),('rationale',{'DECIVORA_RATIONALE_UI_FIXTURE':'1'}),('dialogue',{'DECIVORA_DIALOGUE_UI_FIXTURE':'1'}),('acceptance-guard',{'DECIVORA_DIALOGUE_UI_FIXTURE':'1'}),('dialogue-questions',{'DECIVORA_DIALOGUE_UI_FIXTURE':'1'}),('workflow',{}),('coverage',{'DECIVORA_COVERAGE_UI_FIXTURE':'1'}),('impact',{'DECIVORA_IMPACT_UI_FIXTURE':'1'}),('lifecycle',{'DECIVORA_IMPACT_UI_FIXTURE':'1'}),('operations',{'DECIVORA_OPERATIONS_UI_FIXTURE':'1'}),('projects',{'DECIVORA_PROJECT_UI_FIXTURE':'1'})]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--all',action='store_true');args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True);results=[]
 cases=CASES+([('localization',{}),('backup',{}),('independent',{}),('file-mcp',{'DECIVORA_FILE_UI_FIXTURE':'1','DECIVORA_MCP_UI_FIXTURE':'1'})] if args.all else [])
 for name,flags in cases:
  dest=(args.output/name).resolve();dest.mkdir(exist_ok=True)
  env=dict(os.environ,**flags,DECIVORA_UI_TEST_SCRIPT='tests/ui-'+name+'.cjs',DECIVORA_SCREENSHOT_DIR=str(dest))
  try:
   p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/check_localization_ui.py')],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120);code=p.returncode;log=p.stdout+p.stderr
  except subprocess.TimeoutExpired as error:code=124;log='Synthetic smoke timed out; no retry.\n'+str(error)
  (dest/'run.log').write_text(log);results.append(dict(case=name,returncode=code));print(name,code,flush=True)
 (args.output/'results.json').write_text(json.dumps(dict(fixtures=True,paid_calls=0,results=results),indent=2)+'\n')
 return int(any(r['returncode'] for r in results))
if __name__=='__main__':raise SystemExit(main())

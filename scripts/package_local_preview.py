"""Build the local UI source ZIP; excludes databases, keys, transcripts and tests."""
from pathlib import Path
import argparse,zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def build(target):
    paths=[ROOT/'Decivora.command',ROOT/'Decivora Test.command',ROOT/'README_LOCAL.md',ROOT/'docs/quality/todo-development-review.md']
    paths += [p for base in ('packages','apps/local_ui') for p in (ROOT/base).rglob('*') if p.is_file() and p.suffix in ('.py','.html','.js','.css') and '__pycache__' not in p.parts]
    if (ROOT/'apps/__init__.py').exists():paths.append(ROOT/'apps/__init__.py')
    # Adapter entrypoints must ship with their package modules; never package keys/data.
    paths += [ROOT/'scripts'/name for name in ('capture_claude_hook.py','capture_codex_exec.py','capture_codex_thread.py','audit_project_memory.py','check_mvp_evidence.py','report_paired_cost.py')]
    target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            if path.is_symlink():raise ValueError('Package sources must not be symlinks.')
            archive.write(path,'Decivora-local/'+str(path.relative_to(ROOT)))
    return dict(artifact=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),files=len(set(paths)),contains_user_data=False)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('target',type=Path);args=parser.parse_args();print(json.dumps(build(args.target)))

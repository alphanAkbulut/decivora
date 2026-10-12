"""Compare lossless inline resume tables to frozen full exports; no receiving model."""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'decision-chain'))
from chain import Chain
from collect_membership import ROOT, QUESTIONS, RAW_SHA
from membership_typed import derive_typed
from protocol import canonical,strict_json,score_checkpoints
from resume_package import validate_before_export as validate_full
from resume_compact import build,restore_core,validate_before_export,render_readable
from compare_resume import inspect_core

HERE=Path(__file__).resolve().parent


def compare():
    request_path=ROOT/'examples/adversarial-smoke/requests.json'
    raw_path=ROOT/'docs/quality/model-runs/membership-003-response.txt'
    raw=raw_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RAW_SHA: raise ValueError('saved raw changed')
    requests=strict_json(request_path.read_text())
    derived=derive_typed(requests,raw.decode())
    if derived['status']!='source_validated': raise ValueError('incomplete saved batch')
    bundles,actual_resume,actual_file,actual_readable,metrics={}, {}, {}, {}, {}
    paths=[request_path,raw_path]
    with tempfile.TemporaryDirectory() as tmp:
        for i,(request,item) in enumerate(zip(requests,derived['derived'])):
            chain=Chain(Path(tmp)/f'{i}.db')
            try:
                chain.dispatch('seed',dict(decision='fixture_initial',active=['fixture_initial'],
                    tasks={},criteria=['rollback','migration']),'human',0,'seed')
                qid,rev,options=QUESTIONS[i]
                chain.dispatch('ask',dict(question_id=qid,option_revision=rev,options=options),'human',1,'ask')
                access=dict(can_read=True,project_id=request['source']['project_id'],
                            source_sha256=request['source_sha256'],authz_revision=1)
                response=canonical(item['response'])
                sid=request['source']['session_id']
                old_path=ROOT/f'examples/resume-smoke/{sid}-resume.json'
                old_state_path=ROOT/f'examples/resume-smoke/{sid}-state.json'
                old_package=strict_json(old_path.read_text())
                old_core=strict_json(old_state_path.read_text())
                validate_full(chain,request,response,access,old_package)
                if old_core!=old_package['core']: raise ValueError('frozen equal-information baseline changed')
                before=chain.snapshot()
                built=build(chain,request,response,access)
                if built['status']!='prepared': raise ValueError('compact preparation incomplete')
                package=built['package']
                validate_before_export(chain,request,response,access,package)
                readable=render_readable(package)
                if readable['status']!='prepared': raise ValueError('readable view incomplete')
                text=canonical(package)+'\n'
                file_text=canonical(package['core_table'])+'\n'
                restored=restore_core(strict_json(text)['core_table'])
                restored_file=restore_core(strict_json(file_text))
                if restored!=old_core or restored_file!=old_core or chain.snapshot()!=before:
                    raise AssertionError('lossy or mutating compaction')
                actual_resume[sid]=inspect_core(restored)
                actual_file[sid]=inspect_core(restored_file)
                view=strict_json(readable['text'])
                # Separate inspection of the receiver-facing view, without table/span decoding.
                readable_core=dict(fixture_state=view['fixture_state'],source_messages=view['source_messages'],
                    preserved_records=view['preserved_records'],answer_candidates=[
                    dict(candidate=dict(message_id=e['message_id']),status=e['status'])
                    for e in view['answer_candidates']])
                actual_readable[sid]=inspect_core(readable_core)
                bundles[sid]=dict(resume=text,simple_file=file_text,readable=readable['text'])
                old_bytes,new_bytes=len(old_path.read_bytes()),len(text.encode())
                metrics[sid]=dict(full_resume_bytes=old_bytes,compact_resume_bytes=new_bytes,
                    bytes_removed=old_bytes-new_bytes,byte_reduction_percent=round(100*(old_bytes-new_bytes)/old_bytes,2),
                    full_simple_file_bytes=len(old_state_path.read_bytes()),compact_simple_file_bytes=len(file_text.encode()),
                    readable_view_bytes=readable['bytes'],
                    exact_core_equal=True,projection_unchanged=True)
                paths.extend([old_path,old_state_path])
            finally: chain.close()
    # This existing independent checklist is not used by the encoder.
    expected_path=HERE/'fixtures/resume-checkpoints.json'
    expected=strict_json(expected_path.read_text())
    paths.extend([expected_path,HERE/'resume_compact.py',HERE/'compare_compact_resume.py',
                  HERE/'resume_package.py',HERE/'bridge.py',HERE/'protocol.py',
                  HERE/'membership_typed.py',ROOT/'spikes/decision-chain/chain.py'])
    return dict(experiment_id='RESUME-COMPACTION-001',origin_run='MEMBERSHIP-003',
        baseline='frozen RESUME-FILE-001 exported files',status='lossless_offline_byte_comparison',
        package_score=score_checkpoints(expected,actual_resume),simple_file_score=score_checkpoints(expected,actual_file),
        readable_score=score_checkpoints(expected,actual_readable),
        actual=dict(resume=actual_resume,simple_file=actual_file,readable=actual_readable),metrics=metrics,
        external_source_reads=0,new_model_dispatches=0,selection_dispatches=0,paid_api_calls=0,
        canonical_mutations=0,production_runtime=False,human_gold=False,
        receiver_model_test='not_run',native_host_test='not_run',token_counts=None,cost=None,
        limitation='Byte reduction only; machine tables decoded in code, resolved readable view not receiving-model tested; no token/accuracy/ROI claim',
        hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),bundles


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path);parser.add_argument('--export-dir',type=Path)
    args=parser.parse_args()
    for path in (args.out,args.export_dir):
        if path is not None and (path.exists() or path.is_symlink()): parser.error('target exists; nothing exported')
    result,bundles=compare()
    if args.export_dir:
        args.export_dir.mkdir()
        for sid,texts in bundles.items():
            for arm,name in [('resume','resume'),('simple_file','state'),('readable','readable')]:
                with (args.export_dir/f'{sid}-{name}.json').open('x') as stream: stream.write(texts[arm])
    body=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if args.out:
        with args.out.open('x') as stream: stream.write(body)
    else: print(body,end='')
    if any(result[k]['status']!='passed' for k in ('package_score','simple_file_score','readable_score')): raise SystemExit(1)

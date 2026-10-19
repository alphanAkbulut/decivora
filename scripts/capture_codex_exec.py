#!/usr/bin/env python3
"""Capture an explicitly selected exec JSONL file into an existing local project.

Never starts Codex or a model. Caller supplies source, project and local identity.
No source discovery, default source paths, credentials, or automatic dispatch.
"""
import argparse
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from packages.capture.codex.exec_stream import CodexExecCapture, MAX_STREAM_BYTES
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace


def selected_snapshot(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ContractError('invalid_capture_file', 'Select a regular JSONL file.')
        value = handle.read(MAX_STREAM_BYTES + 1)
    if len(value) > MAX_STREAM_BYTES:
        raise ContractError('capture_limit', 'Selected JSONL file exceeds the bounded capture size.')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('db', 'workspace', 'principal', 'project', 'capture-id'):
        parser.add_argument('--'+flag, required=True)
    parser.add_argument('--disconnect', action='store_true')
    parser.add_argument('--snapshot')
    parser.add_argument('--thread-id')
    parser.add_argument('--provider-version')
    parser.add_argument('--consent', action='store_true', help='Explicit local source capture only; no model data-sharing grant.')
    args = parser.parse_args(argv)
    if not args.disconnect and not all((args.snapshot, args.thread_id, args.provider_version, args.consent)):
        parser.error('Collection requires --snapshot, --thread-id, --provider-version and --consent.')
    db = Path(args.db)
    if not db.is_file() or db.is_symlink():
        parser.error('Select an existing regular local workspace database.')
    try:
        # Local OS owner CLI, not a network login or tenant-authentication service.
        with Workspace(db, args.workspace) as core:
            scope = core.authority.issue_scope(args.principal)
            adapter = CodexExecCapture(core)
            if args.disconnect:
                result = adapter.disconnect(scope, args.project, capture_id=args.capture_id)
            else:
                adapter.connect(scope, args.project, capture_id=args.capture_id, thread_id=args.thread_id,
                                provider_version=args.provider_version, consent=args.consent)
                result = adapter.collect(scope, args.project, capture_id=args.capture_id,
                                         snapshot=selected_snapshot(args.snapshot))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ContractError, OSError) as error:
        print(json.dumps(dict(status='Capture stopped', code=error.code if isinstance(error, ContractError) else 'capture_file_unavailable')))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

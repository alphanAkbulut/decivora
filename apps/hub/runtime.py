"""One local CLI entry point; no background server, provider, runner or source scan."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import stat
import sys

from . import __version__
from packages.domain.source_event import ContractError, MAX_INPUT_BYTES, parse_source_event

ROOT = Path(__file__).resolve().parents[2]


def ensure_runtime(version=None):
    version = sys.version_info if version is None else version
    if tuple(version[:2]) != (3, 12):
        raise ContractError('unsupported_python', 'This development runtime requires Python 3.12.')


def runtime_status():
    ensure_runtime()
    return dict(application='Decivora', version=__version__, stage='development_scaffold',
        python=sys.version.split()[0], sqlite_available_version=sqlite3.sqlite_version,
        capabilities=dict(source_contract_validation=True, source_capture=False,
            project_binding=False, durable_ingress=False, canonical_storage=False,
            human_authentication=False, human_approval=False, semantic_extraction=False,
            model_dispatch=False, tool_execution=False, network_server=False, product_ui=False),
        synthetic_only=True, canonical_mutations=0, model_dispatches=0)


def read_selected_input(path):
    # Only a caller-selected regular file, bounded read; no transcript discovery.
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        raise ContractError('input_unavailable', 'Selected input file is unavailable.') from None
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise ContractError('invalid_input_file', 'Selected input must be a regular file.')
        if before.st_size > MAX_INPUT_BYTES:
            raise ContractError('input_too_large', 'Selected input exceeds the input byte limit.')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        after = os.fstat(fd)
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ContractError('input_changed', 'Selected input changed during read.')
        return raw
    except OSError:
        raise ContractError('input_unavailable', 'Selected input file could not be read.') from None
    finally:
        os.close(fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Decivora local runtime scaffold')
    parser.add_argument('command', nargs='?', choices=['status', 'validate'], default='status')
    parser.add_argument('--input', type=Path)
    args = parser.parse_args(argv)
    if (args.command == 'validate') != (args.input is not None):
        parser.error('validate requires --input; status does not read source files')
    try:
        ensure_runtime()
        if args.command == 'status':
            result = runtime_status()
        else:
            event = parse_source_event(read_selected_input(args.input))
            result = dict(status='validated_only', format=event.format, source_revision=event.source_revision,
                synthetic=event.synthetic, content_sha256=event.content_digest(),
                actor_identity_verified=False, source_capture=False, durable_receipt=False,
                human_approval=False, canonical_mutations=0, model_dispatches=0,
                execution_authorized=False)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except ContractError as error:
        # Do not echo source text, unknown keys, identifiers, paths or credentials.
        print(json.dumps(dict(status='rejected', error=dict(code=error.code, message=str(error))),
                         ensure_ascii=False), file=sys.stderr)
        return 2

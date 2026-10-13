"""Private local backup bundle: bounded, offline, no active-database overwrite."""
import hashlib,io,json,tempfile,zipfile
from pathlib import Path
from packages.domain.source_event import ContractError
from packages.storage.workspace import Workspace

MAX_DATABASE_BYTES=8*1024*1024
MAX_MANIFEST_BYTES=64*1024
NAMES={'workspace.sqlite','manifest.json'}

def inspect_bundle(raw):
    if type(raw) is not bytes or len(raw)>MAX_DATABASE_BYTES+MAX_MANIFEST_BYTES:
        raise ContractError('backup_limit','Backup bundle exceeds the local preview limit.')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            members=z.infolist()
            if len(members)!=2 or {m.filename for m in members}!=NAMES or any(m.flag_bits&1 for m in members):
                raise ContractError('backup_invalid','Exact unencrypted database and manifest members required.')
            for member in members:
                limit=MAX_DATABASE_BYTES if member.filename=='workspace.sqlite' else MAX_MANIFEST_BYTES
                if member.file_size>limit:raise ContractError('backup_limit','Backup member exceeds the local preview limit.')
            database=z.read('workspace.sqlite');manifest=json.loads(z.read('manifest.json'))
        if type(manifest) is not dict or set(manifest)!={'format','workspace','sha256','projection_digests','external_dispatches'} or manifest['external_dispatches']!=0:
            raise ContractError('backup_invalid','Exact offline backup manifest required.')
        if hashlib.sha256(database).hexdigest()!=manifest['sha256']:
            raise ContractError('backup_invalid','Database checksum differs from manifest.')
        # Restore into a throwaway NEW file; validate sources, events and projections.
        with tempfile.TemporaryDirectory(prefix='decivora-backup-check-') as directory:
            original=Path(directory)/'original.sqlite';original.write_bytes(database);original.chmod(0o600)
            restored=Workspace.restore(original,Path(directory)/'checked.sqlite',manifest)
            try:
                if restored.db.execute('PRAGMA foreign_key_check').fetchall():raise ContractError('backup_invalid','Restored foreign keys failed.')
                if restored.db.execute('SELECT count(*) FROM core_meta').fetchone()[0]!=1:raise ContractError('backup_invalid','Local UI backup must contain one workspace.')
            finally:restored.close()
        return dict(manifest=manifest,restore_checked=True,external_dispatches=0)
    except ContractError:raise
    except Exception as error:raise ContractError('backup_invalid','Backup could not be validated.') from error

def create_bundle(core,scope):
    with core.read_snapshot():
        core.scope(scope,human=True)
        if core.db.execute('SELECT count(*) FROM core_meta').fetchone()[0]!=1:
            raise ContractError('backup_scope','Multi-workspace databases cannot use the local UI backup.')
        size=core.db.execute('PRAGMA page_count').fetchone()[0]*core.db.execute('PRAGMA page_size').fetchone()[0]
        if size>MAX_DATABASE_BYTES:raise ContractError('backup_limit','Database exceeds the 8 MiB local preview backup limit; existing data is unchanged.')
    with tempfile.TemporaryDirectory(prefix='decivora-backup-') as directory:
        target=Path(directory)/'workspace.sqlite';manifest=core.backup(scope,target)
        if target.stat().st_size>MAX_DATABASE_BYTES:raise ContractError('backup_limit','Database grew beyond the local preview backup limit.')
        output=io.BytesIO()
        with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.write(target,'workspace.sqlite');z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False))
        raw=output.getvalue();inspect_bundle(raw)
        # Recheck CURRENT access before returning private bytes, including source ACLs.
        with core.read_snapshot():
            core.scope(scope,human=True)
            for project, in core.db.execute('SELECT id FROM projects WHERE workspace=?',(core.workspace,)).fetchall():core.scope(scope,project)
            for seq, in core.db.execute('SELECT seq FROM sources WHERE workspace=?',(core.workspace,)).fetchall():core.source(scope,seq)
        return raw

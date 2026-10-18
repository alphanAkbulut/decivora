"""Explicit environment labels; test mode never silently adopts an existing DB."""
from pathlib import Path
import json,os
from packages.domain.source_event import ContractError
DEFAULT_DATA_DIR=Path(__file__).resolve().parents[2].parent/'decivora-local-data'
TEST_DATA_DIR=DEFAULT_DATA_DIR.parent/'decivora-test-data'

def bind_environment(path,environment):
 path=Path(path)
 if environment not in ('local','test'):raise ContractError('invalid_environment','Known local/test environment required.')
 if path.is_symlink():raise ContractError('invalid_environment','Database symlinks are not supported by the environment boundary.')
 marker=path.with_suffix(path.suffix+'.environment.json')
 if marker.is_symlink():raise ContractError('invalid_environment','Environment marker must be a regular file.')
 if environment=='test' and path.resolve().parent==DEFAULT_DATA_DIR.resolve():raise ContractError('environment_mismatch','Test mode cannot use the normal local data directory.')
 if marker.exists():
  try:value=json.loads(marker.read_text())
  except (OSError,ValueError):raise ContractError('environment_mismatch','Environment identity unavailable.') from None
  if value!={'environment':environment,'format':'decivora-environment-1'}:raise ContractError('environment_mismatch','Data belongs to a different environment.')
  return
 if environment=='test' and path.exists():raise ContractError('environment_mismatch','Test mode requires a fresh or explicitly marked test database.')
 path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 try:fd=os.open(marker,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 except FileExistsError:return bind_environment(path,environment)
 with os.fdopen(fd,'w') as output:json.dump(dict(environment=environment,format='decivora-environment-1'),output)

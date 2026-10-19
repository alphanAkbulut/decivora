"""Exact-commit read-only content observer. Transport injected by trusted setup.

No default credentials/network; no branch discovery, PR write or task/AC mutation.
"""
import base64,binascii,hashlib,re,time
from urllib.parse import quote
from packages.domain.source_event import ContractError
class GitHubCommitObserver:
    def __init__(self,fetch):
        if not callable(fetch):raise ContractError('provider_config_required','Explicit authorized read-only GitHub transport required.')
        self.fetch=fetch
    def observe(self,*,repository,commit,path,expected_sha256):
        if type(repository) is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}',repository) or any(x in ('.','..') for x in repository.split('/')):raise ContractError('invalid_target','Exact GitHub repository required.')
        if type(commit) is not str or not re.fullmatch('[0-9a-f]{40}',commit) or type(expected_sha256) is not str or not re.fullmatch('[0-9a-f]{64}',expected_sha256):raise ContractError('invalid_target','Immutable commit SHA and expected content digest required.')
        if type(path) is not str or not 0<len(path)<=512 or path.startswith('/') or '\\' in path or any(x in ('','.','..') for x in path.split('/')) or any(ord(c)<32 for c in path):raise ContractError('invalid_target','Bounded repository-relative path required.')
        try:path.encode('utf-8')
        except UnicodeError:raise ContractError('invalid_target','Valid UTF-8 path required.') from None
        endpoint='https://api.github.com/repos/'+repository+'/contents/'+quote(path,safe='/')+'?ref='+commit
        # Exact repository/ref/path is the authorized read surface. Never follow a returned URL.
        try:response=self.fetch(endpoint)
        except (OSError,TimeoutError):return dict(status='unknown',reason='transport_unavailable',repository=repository,commit=commit,canonical_mutations=0)
        if (type(response) is not dict or response.get('type')!='file' or response.get('path')!=path or response.get('encoding')!='base64' or type(response.get('content')) is not str or type(response.get('size')) is not int or not 0<=response['size']<=1048576 or len(response['content'])>1500000):raise ContractError('invalid_observation','Bounded exact GitHub file response required.')
        try:data=base64.b64decode(''.join(response['content'].split()),validate=True)
        except (ValueError,binascii.Error):raise ContractError('invalid_observation','Valid file encoding required.') from None
        if len(data)!=response['size'] or len(data)>1048576:raise ContractError('invalid_observation','Exact bounded file size required.')
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if response.get('sha')!=blob:raise ContractError('invalid_observation','Git blob digest mismatch.')
        actual=hashlib.sha256(data).hexdigest()
        return dict(status='content_match' if actual==expected_sha256 else 'content_mismatch',repository=repository,commit=commit,path=path,blob_sha=blob,sha256=actual,bytes=len(data),observed_at=time.time(),branch_freshness='not_checked',acceptance_verified=False,canonical_mutations=0,method='github_exact_commit_contents',transport_authority='trusted_injected_transport')

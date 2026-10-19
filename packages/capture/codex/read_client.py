"""Bounded stdio client. Only handshake and one selected-thread read are exposed."""
import json
import os
from pathlib import Path
import selectors
import subprocess
import time

from packages.capture.codex.exec_stream import _fail, _object, MAX_STREAM_BYTES
from packages.domain.project_binding import identifier
from packages.capture.codex.app_server import IGNORED


class ReadOnlyAppServer:
    def __init__(self, executable, thread_id, *, cwd, codex_home=None, timeout=5):
        identifier(thread_id)
        if not Path(executable).is_absolute() or not Path(executable).is_file():
            _fail('codex_executable_required')
        if not 0 < timeout <= 30: _fail('invalid_capture_timeout')
        self.thread_id = thread_id; self.timeout = timeout; self.buffer = b''
        self.request_id = 0
        env = {k:os.environ[k] for k in ('HOME','PATH','SYSTEMROOT','TMPDIR') if k in os.environ}
        if codex_home is not None: env['CODEX_HOME'] = str(Path(codex_home).resolve())
        self.process = subprocess.Popen([str(executable), 'app-server', '--listen', 'stdio://'],
            cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, bufsize=0)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.process.stdout, selectors.EVENT_READ)
        try:
            self._request(0, 'initialize', dict(clientInfo=dict(name='decivora_capture',version='0.1.0')))
            self._send(dict(method='initialized',params={}))
        except BaseException:
            self.close(); raise

    def _send(self, value):
        try: self.process.stdin.write((json.dumps(value)+'\n').encode())
        except (BrokenPipeError,OSError): _fail('codex_transport_failed')

    def _request(self, number, method, params):
        self._send(dict(id=number,method=method,params=params))
        deadline = time.monotonic()+self.timeout; received = len(self.buffer)
        while True:
            while b'\n' in self.buffer:
                line,self.buffer = self.buffer.split(b'\n',1)
                try:
                    value = json.loads(line.decode(),object_pairs_hook=_object,parse_constant=lambda _: _fail())
                except (ValueError,UnicodeError,RecursionError): _fail('codex_transport_failed')
                if type(value) is not dict: _fail('codex_transport_failed')
                if 'id' in value:
                    if type(value['id']) is not int or value['id'] != number or 'error' in value or 'method' in value:
                        _fail('codex_read_failed')
                    if type(value.get('result')) is not dict: _fail('codex_transport_failed')
                    return value['result']
            left = deadline-time.monotonic()
            if left <= 0 or not self.selector.select(left): _fail('codex_read_timeout')
            chunk = os.read(self.process.stdout.fileno(),65536)
            if not chunk: _fail('codex_transport_closed')
            received += len(chunk)
            if received > MAX_STREAM_BYTES: _fail('capture_limit')
            self.buffer += chunk

    def read_turns(self, thread_id, *, limit):
        if thread_id != self.thread_id or type(limit) is not int or not 1<=limit<=10:
            _fail('capture_binding_mismatch')
        self.request_id += 1
        metadata = self._request(self.request_id, 'thread/turns/list',
            dict(threadId=self.thread_id, limit=limit, sortDirection='desc', itemsView='notLoaded'))
        if type(metadata.get('data')) is not list or len(metadata['data'])>limit:
            _fail('invalid_codex_page')
        turns=[]; pages=0; ignored=0; unsupported=0
        per_turn=min(16,32//max(1,len(metadata['data'])))
        selected=set()
        for turn in metadata['data']:
            if type(turn) is not dict: _fail('invalid_codex_page')
            identifier(turn.get('id'))
            if turn['id'] in selected or turn.get('status') not in ('completed','interrupted','failed','inProgress'):
                _fail('invalid_codex_page')
            selected.add(turn['id'])
            cursor=None; seen=set(); items=[]
            for _ in range(per_turn):
                self.request_id += 1
                params=dict(threadId=self.thread_id,turnId=turn['id'],limit=1,sortDirection='asc')
                if cursor is not None: params['cursor']=cursor
                result=self._request(self.request_id,'thread/items/list',params)
                pages+=1
                if type(result.get('data')) is not list or len(result['data'])>1:
                    _fail('invalid_codex_page')
                for entry in result['data']:
                    if type(entry) is not dict or entry.get('turnId')!=turn['id'] or type(entry.get('item')) is not dict:
                        _fail('capture_binding_mismatch')
                    item=entry['item']
                    kind=item.get('type')
                    if type(kind) is not str: _fail('invalid_codex_page')
                    if kind in ('userMessage','agentMessage'): items.append(item)
                    else:
                        ignored+=1  # bodies discarded, never returned to the capture layer
                        unsupported+=kind not in IGNORED
                cursor=result.get('nextCursor')
                if cursor is None: break
                if type(cursor) is not str or not cursor or len(cursor)>4096 or cursor in seen:
                    _fail('invalid_codex_cursor')
                seen.add(cursor)
            turns.append(dict(id=turn['id'],status=turn.get('status'),items=items,
                itemsView='full' if cursor is None else 'notLoaded',capture_items_truncated=cursor is not None))
        return dict(data=turns,nextCursor=metadata.get('nextCursor'),
                    capture_transport='decivora-codex-item-pages-1',item_pages=pages,ignored_private_items=ignored,capture_unsupported_items=unsupported)

    def close(self):
        self.selector.close()
        if self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=1)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait()
        for handle in (self.process.stdin,self.process.stdout): handle.close()

    def __enter__(self): return self
    def __exit__(self,*_): self.close()

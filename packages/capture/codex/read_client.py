"""Bounded stdio client. Only handshake and one selected-thread read are exposed."""
import json
import os
from pathlib import Path
import selectors
import subprocess
import time

from packages.capture.codex.exec_stream import _fail, _object, MAX_STREAM_BYTES
from packages.domain.project_binding import identifier


class ReadOnlyAppServer:
    def __init__(self, executable, thread_id, *, cwd, codex_home=None, timeout=5):
        identifier(thread_id)
        if not Path(executable).is_absolute() or not Path(executable).is_file():
            _fail('codex_executable_required')
        if not 0 < timeout <= 30: _fail('invalid_capture_timeout')
        self.thread_id = thread_id; self.timeout = timeout; self.buffer = b''
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
        return self._request(1, 'thread/turns/list',
            dict(threadId=self.thread_id, limit=limit, sortDirection='desc', itemsView='full'))

    def close(self):
        self.selector.close()
        if self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=1)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait()
        for handle in (self.process.stdin,self.process.stdout): handle.close()

    def __enter__(self): return self
    def __exit__(self,*_): self.close()

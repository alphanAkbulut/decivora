"""Opt-in, exact-payload OpenAI pilot transport. No activation at import/startup.

One input-token count and one generation maximum per admitted payload. Both HTTP
attempts consume the shared call ceiling; unknown outcomes retain reservations.
The ledger contains hashes/usage only, never a key, source, or provider error body.
"""
import copy
from contextlib import contextmanager
import hashlib
import http.client
import json
import os
from pathlib import Path
import sqlite3
import ssl
import stat
import time

from packages.domain.source_event import ContractError
from packages.privacy.secrets import ensure_safe
from packages.storage.private_files import restrict_sqlite_files
from packages.storage.project_store import canonical

# USD millionths per token: uncached input, cache read, cache write, output.
# Deployment must explicitly adopt this price revision; never choose a fallback.
PRICE_REVISION = 'openai-standard-cache-aware-2026-10-19'
RATES = {'gpt-6-luna': (0.1, 0.01, 0.125, 0.5),
         'gpt-6.1-sol': (2, 0.1, 2.5, 10)}


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_key(path):
    """Read only the explicitly selected private local file, without following links."""
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) |
                 getattr(os, 'O_NONBLOCK', 0))
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_size > 1024 or
                (os.name == 'posix' and (info.st_uid != os.getuid() or
                 stat.S_IMODE(info.st_mode) & 0o077))):
            raise ContractError('credential_file_unsafe', 'Private owner-only key file required.')
        value = os.read(fd, 1025).decode().strip()
        if not value.startswith('sk-') or not 20 <= len(value) <= 512 or any(c.isspace() for c in value):
            raise ContractError('credential_invalid', 'Invalid API key format; key not displayed.')
        return value
    finally:
        os.close(fd)


def http_post(path, payload, key):
    """Fixed TLS host, no proxy discovery, redirects, retries, or response-body logging."""
    if path not in ('/v1/responses/input_tokens', '/v1/responses'):
        raise ContractError('provider_endpoint_denied', 'Unsupported provider endpoint.')
    connection = http.client.HTTPSConnection('api.openai.com', timeout=45,
                                              context=ssl.create_default_context())
    try:
        connection.request('POST', path, body=canonical(payload).encode(),
                           headers={'Authorization': 'Bearer ' + key,
                                    'Content-Type': 'application/json'})
        response = connection.getresponse()
        if response.status != 200:
            raise ContractError('provider_http_error', 'Provider request failed; no automatic retry.')
        raw = response.read(262145)
        if len(raw) > 262144:
            raise ContractError('provider_response_limit', 'Provider response exceeded the local limit.')
        def pairs(items):
            result = {}
            for name, value in items:
                if name in result:
                    raise ValueError('Duplicate provider JSON key.')
                result[name] = value
            return result
        return json.loads(raw, object_pairs_hook=pairs)
    except ContractError:
        raise
    except TimeoutError:
        raise ContractError('provider_timeout_unknown', 'Provider wait timed out; outcome unknown, no automatic retry.') from None
    except ssl.SSLError:
        raise ContractError('provider_tls_unknown', 'Provider TLS exchange failed; outcome unknown, no automatic retry.') from None
    except (ValueError, UnicodeError):
        raise ContractError('provider_json_invalid', 'Provider JSON could not be decoded; no automatic retry.') from None
    except Exception:
        raise ContractError('provider_connection_unknown', 'Provider outcome unknown; no automatic retry.') from None
    finally:
        connection.close()


def micro_cost(model, input_tokens, output_tokens, *, cached_tokens=0, cache_write_tokens=0):
    from decimal import Decimal, ROUND_CEILING
    for value in (input_tokens, output_tokens, cached_tokens, cache_write_tokens):
        if type(value) is not int or value < 0:
            raise ContractError('pilot_usage_unknown', 'Nonnegative integer token categories required.')
    if cached_tokens + cache_write_tokens > input_tokens:
        raise ContractError('pilot_usage_unknown', 'Cache categories exceed total input tokens.')
    inp, read, write, out = map(lambda value: Decimal(str(value)), RATES[model])
    return int((inp * (input_tokens - cached_tokens - cache_write_tokens) +
                read * cached_tokens + write * cache_write_tokens + out * output_tokens)
               .to_integral_value(rounding=ROUND_CEILING))


class PilotTransport:
    """A local trusted caller supplies the human-approved exact payload manifest.

    This is not a remote authorization API or general account-wide spend limiter.
    Existing ConversationService source/context grants remain independently required.
    """
    def __init__(self, ledger, *, manifest, key_file, post=None):
        self.manifest = copy.deepcopy(manifest)
        expected = {'approval_ref', 'price_revision', 'expires_at', 'max_http_attempts',
                    'max_cost_microusd', 'max_input_tokens', 'max_output_tokens', 'payloads'}
        shared_fields = {'budget_scope', 'prior_usage'}
        shared = type(manifest) is dict and set(manifest) == expected | shared_fields
        if type(manifest) is not dict or (set(manifest) != expected and not shared):
            raise ContractError('pilot_manifest_invalid', 'Exact approved pilot manifest required.')
        ensure_safe(manifest)
        if (not isinstance(manifest['approval_ref'], str) or not manifest['approval_ref'].strip() or
                manifest['price_revision'] != PRICE_REVISION or
                type(manifest['expires_at']) is not int or manifest['expires_at'] <= time.time()):
            raise ContractError('pilot_manifest_invalid', 'Current explicit approval and prices required.')
        for field, ceiling in (('max_http_attempts', 200 if shared else 20),
                               ('max_cost_microusd', 3000000 if shared else 1000000),
                               ('max_input_tokens', 10000), ('max_output_tokens', 2000)):
            value = manifest[field]
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ContractError('pilot_manifest_invalid', 'Pilot limits exceed the approved envelope.')
        hashes = manifest['payloads']
        if (type(hashes) is not list or not 1 <= len(hashes) <= 10 or
                any(type(h) is not str or len(h) != 64 or any(c not in '0123456789abcdef' for c in h) for h in hashes) or
                len(set(hashes)) != len(hashes)):
            raise ContractError('pilot_manifest_invalid', 'Bounded unique exact payload hashes required.')
        self.prior_usage = dict(dispatches=0, http_attempts=0, cost_microusd=0)
        policy = copy.deepcopy(manifest)
        if shared:
            prior = manifest['prior_usage']
            if (manifest['budget_scope'] != 'decivora-development-2026-10-19-usd3' or
                    type(prior) is not dict or set(prior) != {'dispatches', 'http_attempts', 'cost_microusd', 'evidence_sha256'} or
                    any(type(prior.get(k)) is not int or prior[k] < 0 for k in self.prior_usage) or
                    prior['dispatches'] > 100 or prior['http_attempts'] > manifest['max_http_attempts'] or
                    prior['http_attempts'] != 2 * prior['dispatches'] or
                    prior['cost_microusd'] > manifest['max_cost_microusd'] or
                    type(prior['evidence_sha256']) is not str or len(prior['evidence_sha256']) != 64 or
                    any(c not in '0123456789abcdef' for c in prior['evidence_sha256'])):
                raise ContractError('pilot_manifest_invalid', 'Shared owner-approved scope and prior-usage evidence required.')
            self.prior_usage = {k: prior[k] for k in self.prior_usage}
            # New bounded synthetic batches share this immutable root policy.
            # Their exact manifests are recorded below; limits/prior spend cannot reset.
            policy.pop('payloads')
        self.shared = shared
        self.key_file = Path(key_file)
        self.post = http_post if post is None else post
        self.path = Path(ledger)
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not self.path.exists():
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
        restrict_sqlite_files(self.path)
        with self._db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS policy (id INTEGER PRIMARY KEY CHECK(id=1), digest TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS dispatch (hash TEXT PRIMARY KEY, state TEXT NOT NULL, reserved INTEGER NOT NULL, attempts INTEGER NOT NULL, input_tokens INTEGER, output_tokens INTEGER, actual INTEGER)')
            db.execute('CREATE TABLE IF NOT EXISTS batches (digest TEXT PRIMARY KEY, payload_hashes TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS dispatch_diagnostics (hash TEXT PRIMARY KEY, phase TEXT NOT NULL, failure_code TEXT, updated_at INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS unknown_reviews (hash TEXT PRIMARY KEY, snapshot_sha256 TEXT NOT NULL, approval_ref TEXT NOT NULL, reviewed_at INTEGER NOT NULL)')
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT digest FROM policy WHERE id=1').fetchone()
            if previous and previous[0] != fingerprint(policy):
                raise ContractError('pilot_policy_changed', 'Existing pilot ledger cannot adopt a different budget or manifest.')
            db.execute('INSERT OR IGNORE INTO policy VALUES(1, ?)', (fingerprint(policy),))
            db.execute('INSERT OR IGNORE INTO batches VALUES(?, ?)', (fingerprint(manifest), canonical(hashes)))

    @contextmanager
    def _db(self):
        restrict_sqlite_files(self.path)
        db = sqlite3.connect(self.path, timeout=5)
        db.execute('PRAGMA synchronous=FULL')
        try:
            with db:
                yield db
        finally:
            db.close()

    def snapshot(self):
        with self._db() as db:
            rows = db.execute('SELECT state,reserved,attempts,input_tokens,output_tokens,actual,hash FROM dispatch').fetchall()
            reviewed = {r[0] for r in db.execute('SELECT hash FROM unknown_reviews')}
        return dict(dispatches=self.prior_usage['dispatches'] + len(rows),
                    http_attempts=self.prior_usage['http_attempts'] + sum(r[2] for r in rows),
                    committed_microusd=self.prior_usage['cost_microusd'] + sum(r[5] if r[5] is not None else r[1] for r in rows),
                    frozen=any(r[0] in ('pending', 'overrun') or (r[0] == 'unknown' and r[6] not in reviewed) for r in rows),
                    states=[r[0] for r in rows])

    def review_packet(self):
        """Read-only owner review, without keys, payload text or guessed usage.

        An accepted unknown keeps its reservation and original state forever.
        This local trusted-owner method is not an agent/remote approval endpoint.
        """
        with self._db() as db:
            policy = db.execute('SELECT digest FROM policy WHERE id=1').fetchone()[0]
            rows = db.execute('SELECT hash,state,reserved,attempts,input_tokens,output_tokens,actual FROM dispatch ORDER BY hash').fetchall()
            reviews = {r[0]: r[1] for r in db.execute('SELECT hash,approval_ref FROM unknown_reviews')}
            diagnostics = {r[0]: dict(phase=r[1], failure_code=r[2]) for r in db.execute('SELECT hash,phase,failure_code FROM dispatch_diagnostics')}
        snapshot = fingerprint(dict(policy=policy, dispatches=rows, reviews=reviews))
        unresolved = [r for r in rows if r[1] in ('pending', 'overrun') or (r[1] == 'unknown' and r[0] not in reviews)]
        return dict(snapshot_sha256=snapshot, frozen=bool(unresolved),
                    unknowns=[dict(payload_sha256=r[0], state=r[1],
                        reserved_microusd=r[2], http_budget_slots=r[3],
                        actual_microusd=r[6], diagnostic=diagnostics.get(r[0]),
                        continuation_approval_ref=reviews.get(r[0])) for r in rows if r[1] == 'unknown'],
                    can_accept_reserved_continuation=bool(unresolved) and all(r[1] == 'unknown' for r in unresolved))

    def accept_reserved_unknown(self, identity, *, snapshot_sha256, approval_ref):
        """Explicit owner risk acceptance; never refund, retry, or invent usage.

        The host must obtain human approval before calling. A stale packet or
        pending/overrun dispatch cannot be used to clear the stop. All existing
        exact-source, expiry, count and money gates continue to apply.
        """
        if (type(approval_ref) is not str or not 1 <= len(approval_ref) <= 160 or
                any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_:. /-' for c in approval_ref)):
            raise ContractError('pilot_review_invalid', 'A bounded safe owner approval reference is required.')
        ensure_safe(approval_ref)
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            packet = self.review_packet()
            if packet['snapshot_sha256'] != snapshot_sha256:
                raise ContractError('pilot_review_stale', 'Budget changed since owner review.')
            row = next((r for r in packet['unknowns'] if r['payload_sha256'] == identity), None)
            if (not packet['can_accept_reserved_continuation'] or row is None or
                    row['continuation_approval_ref'] is not None):
                raise ContractError('pilot_review_invalid', 'Only an unreviewed unknown can retain its reserve for continuation.')
            db.execute('INSERT INTO unknown_reviews VALUES(?,?,?,?)',
                       (identity, snapshot_sha256, approval_ref, int(time.time())))
        return self.review_packet()

    def _diagnostic(self, identity, phase, failure_code=None):
        with self._db() as db:
            db.execute('INSERT OR REPLACE INTO dispatch_diagnostics VALUES(?,?,?,?)',
                       (identity, phase, failure_code, int(time.time())))

    def __call__(self, payload):
        payload = copy.deepcopy(payload)
        ensure_safe(payload)
        model = payload.get('model')
        expected = {'model', 'instructions', 'input', 'text', 'max_output_tokens', 'store', 'tools', 'stream', 'service_tier'}
        if (set(payload) != expected or model not in RATES or payload['store'] is not False or
                payload['tools'] != [] or payload['stream'] is not False or payload['service_tier'] != 'default' or
                type(payload['input']) is not str or type(payload['instructions']) is not str or
                type(payload['max_output_tokens']) is not int or
                not 1 <= payload['max_output_tokens'] <= self.manifest['max_output_tokens'] or
                len(canonical(payload).encode()) > 100000):
            raise ContractError('pilot_payload_denied', 'Only bounded text-only structured extraction is allowed.')
        identity = fingerprint(payload)
        if identity not in self.manifest['payloads'] or self.manifest['expires_at'] <= time.time():
            raise ContractError('pilot_payload_denied', 'Exact payload not approved or approval expired.')
        # Missing key is a local configuration failure, not a dispatched attempt.
        key = read_key(self.key_file)
        # Cache writes use the highest current input tariff. No cache discount
        # is assumed at admission, even on the first call or a cold prefix.
        reserve = micro_cost(model, self.manifest['max_input_tokens'], payload['max_output_tokens'],
                             cache_write_tokens=self.manifest['max_input_tokens'])
        with self._db() as db:
            db.execute('BEGIN IMMEDIATE')
            rows = db.execute('SELECT state,reserved,attempts,actual FROM dispatch').fetchall()
            reviewed = {r[0] for r in db.execute('SELECT hash FROM unknown_reviews')}
            blocked = db.execute("SELECT hash,state FROM dispatch WHERE state IN ('pending','unknown','overrun')").fetchall()
            if any(state != 'unknown' or identity not in reviewed for identity, state in blocked):
                raise ContractError('pilot_review_required', 'Uncertain or overrun request requires review; dispatch frozen.')
            if db.execute('SELECT 1 FROM dispatch WHERE hash=?', (identity,)).fetchone():
                raise ContractError('pilot_retry_denied', 'This exact request already consumed its attempt.')
            if ((self.shared and self.prior_usage['dispatches'] + len(rows) + 1 > 100) or
                    self.prior_usage['http_attempts'] + sum(r[2] for r in rows) + 2 > self.manifest['max_http_attempts'] or
                    self.prior_usage['cost_microusd'] + sum(r[3] if r[3] is not None else r[1] for r in rows) + reserve > self.manifest['max_cost_microusd']):
                raise ContractError('pilot_budget_exceeded', 'Shared HTTP or money ceiling would be exceeded.')
            # Persist both reserved HTTP slots before either request. Crashes cannot refund them.
            db.execute('INSERT INTO dispatch(hash,state,reserved,attempts) VALUES(?, ?, ?, 2)', (identity, 'pending', reserve))
        try:
            phase = 'input_count'
            self._diagnostic(identity, phase)
            count_payload = {k: payload[k] for k in ('model', 'instructions', 'input', 'text', 'tools')}
            count = self.post('/v1/responses/input_tokens', count_payload, key)
            n = count.get('input_tokens') if type(count) is dict else None
            if type(n) is not int or n < 0 or count.get('object') != 'response.input_tokens':
                raise ContractError('pilot_count_unknown', 'Provider input token count unavailable.')
            if n > self.manifest['max_input_tokens']:
                with self._db() as db:
                    db.execute("UPDATE dispatch SET state='input_rejected',input_tokens=? WHERE hash=?", (n, identity))
                raise ContractError('pilot_input_exceeded', 'Generation not sent: counted input exceeds the approved ceiling.')
            phase = 'generation'
            with self._db() as db:
                db.execute('UPDATE dispatch SET input_tokens=? WHERE hash=?', (n, identity))
            self._diagnostic(identity, phase)
            response = self.post('/v1/responses', payload, key)
            phase = 'usage_validation'
            self._diagnostic(identity, phase)
            usage = response.get('usage') if type(response) is dict else None
            if (type(usage) is not dict or any(type(usage.get(k)) is not int or usage[k] < 0
                    for k in ('input_tokens', 'output_tokens', 'total_tokens')) or
                    usage['total_tokens'] != usage['input_tokens'] + usage['output_tokens']):
                raise ContractError('pilot_usage_unknown', 'Usage unknown; reservation retained and pilot frozen.')
            inp, out = usage['input_tokens'], usage['output_tokens']
            details = usage.get('input_tokens_details')
            if type(details) is not dict or any(type(details.get(k)) is not int or details[k] < 0
                    for k in ('cached_tokens', 'cache_write_tokens')):
                raise ContractError('pilot_usage_unknown', 'Cache accounting missing; reservation retained and pilot frozen.')
            if response.get('service_tier') not in (None, 'default'):
                raise ContractError('pilot_price_unknown', 'Unexpected service tier; no assumed default-rate settlement.')
            cost = micro_cost(model, inp, out, cached_tokens=details['cached_tokens'],
                              cache_write_tokens=details['cache_write_tokens'])
            overrun = inp > n or inp > self.manifest['max_input_tokens'] or out > payload['max_output_tokens'] or cost > reserve
            with self._db() as db:
                db.execute('UPDATE dispatch SET state=?,input_tokens=?,output_tokens=?,actual=? WHERE hash=?',
                           ('overrun' if overrun else 'settled', inp, out, cost, identity))
            if overrun:
                raise ContractError('pilot_usage_overrun', 'Provider exceeded a bound; actual usage saved and pilot frozen.')
            return response
        except Exception as exc:
            from packages.operations.local import safe_code
            self._diagnostic(identity, phase, safe_code(getattr(exc, 'code', 'provider_outcome_unknown')))
            with self._db() as db:
                db.execute("UPDATE dispatch SET state='unknown' WHERE hash=? AND state='pending'", (identity,))
            raise

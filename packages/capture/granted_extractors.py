"""Trusted, exact-grant transport registry; never configured by captured text.

This registry creates per-dispatch adapters only. Existing conversation authority,
context, reservation and transport budget checks remain the dispatch authority.
No key, network call, grant or budget is created by registration or lookup.
"""
import copy
import time
from packages.capture.responses_extractor import ResponsesExtractor
from packages.domain.source_event import ContractError


class GrantedResponsesFactory:
    def __init__(self, entries):
        self._entries = {}
        for grant, send in entries:
            if (type(grant) is not dict or not callable(send) or
                    not isinstance(grant.get('id'), str) or
                    grant['id'] in self._entries or
                    grant.get('provider') != 'OpenAI Responses configured transport' or
                    type(grant.get('context_sha256')) is not str):
                raise ContractError('invalid_model_configuration', 'Unique context-bound trusted grants required.')
            self._entries[grant['id']] = (copy.deepcopy(grant), send)

    def __call__(self, source, grant):
        configured = self._entries.get(grant.get('id'))
        if configured is None:
            return None
        expected, send = configured
        if (grant != expected or source.get('id') != expected['source'] or
                source.get('sha256') != expected['sha256'] or
                expected['expires_at'] <= time.time()):
            return None
        return ResponsesExtractor(send, model=expected['model'],
            max_output_tokens=expected['max_output_tokens'], authorized=True,
            grant_id=expected['id'], dialogue_review=True)

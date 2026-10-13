"""T04 source-event contract for explicitly selected synthetic input only.

Identity fields are claimed source metadata, never verified principals or grants.
This is structural validation; ingress, storage and authorization are later tasks.
"""
import copy
from dataclasses import asdict, dataclass
import hashlib
import json
import re

FORMAT = 'decivora-source-event-1'
MAX_INPUT_BYTES = 32768
MAX_TEXT_CHARACTERS = 16384
ID_PATTERN = r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
ACTOR_TYPES = ('human', 'assistant', 'tool', 'unknown')
FIELDS = {'format', 'event_id', 'project_id', 'session_id', 'source_revision', 'actor_type', 'text', 'synthetic'}


class ContractError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class SourceEvent:
    format: str
    event_id: str
    project_id: str
    session_id: str
    source_revision: int
    actor_type: str
    text: str
    synthetic: bool

    def content_digest(self):
        raw = json.dumps(asdict(self), ensure_ascii=False, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
        return hashlib.sha256(raw).hexdigest()


def source_event_schema():
    identifier = dict(type='string', pattern=ID_PATTERN, minLength=1, maxLength=128)
    return dict(**{'$schema': 'https://json-schema.org/draft/2020-12/schema'},
        type='object', additionalProperties=False, required=sorted(FIELDS),
        properties=dict(format=dict(type='string', const=FORMAT),
            event_id=copy.deepcopy(identifier), project_id=copy.deepcopy(identifier), session_id=copy.deepcopy(identifier),
            source_revision=dict(type='integer', minimum=1, maximum=9223372036854775807),
            actor_type=dict(type='string', enum=list(ACTOR_TYPES)),
            text=dict(type='string', minLength=1, maxLength=MAX_TEXT_CHARACTERS),
            synthetic=dict(type='boolean', const=True)))


def validate_source_event(value):
    if type(value) is not dict or set(value) != FIELDS:
        raise ContractError('invalid_fields', 'Source event has missing or unsupported fields.')
    if value['format'] != FORMAT:
        raise ContractError('unsupported_format', 'Unsupported source event format.')
    if value['synthetic'] is not True:
        raise ContractError('real_input_disabled', 'Only synthetic source input is enabled in this scaffold.')
    for field in ('event_id', 'project_id', 'session_id'):
        if type(value[field]) is not str or re.fullmatch(ID_PATTERN, value[field]) is None:
            raise ContractError('invalid_identity', 'Source identity must be a bounded opaque identifier.')
    revision = value['source_revision']
    if type(revision) is not int or not 1 <= revision <= 9223372036854775807:
        raise ContractError('invalid_revision', 'Source revision must be a positive 64-bit integer.')
    if type(value['actor_type']) is not str or value['actor_type'] not in ACTOR_TYPES:
        raise ContractError('invalid_actor', 'Unsupported claimed source actor type.')
    text = value['text']
    if type(text) is not str or not 1 <= len(text) <= MAX_TEXT_CHARACTERS:
        raise ContractError('invalid_text', 'Source text is missing or exceeds the character limit.')
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError):
        raise ContractError('invalid_encoding', 'Source event must contain valid Unicode JSON.') from None
    if len(encoded) > MAX_INPUT_BYTES:
        raise ContractError('input_too_large', 'Source event exceeds the input byte limit.')
    return SourceEvent(**value)


def parse_source_event(raw):
    if type(raw) is not bytes:
        raise ContractError('invalid_input', 'Source input must be UTF-8 bytes.')
    if len(raw) > MAX_INPUT_BYTES:
        raise ContractError('input_too_large', 'Source input exceeds the input byte limit.')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError('duplicate_key', 'Duplicate JSON field rejected.')
            result[key] = value
        return result
    def constant(_):
        raise ContractError('non_finite_number', 'Non-finite JSON number rejected.')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except ContractError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise ContractError('invalid_json', 'Source input is not valid bounded UTF-8 JSON.') from None
    return validate_source_event(value)

"""Bounded credential detection. Not a complete secret/PII classifier or vault."""
import re
from packages.domain.source_event import ContractError

POLICY='decivora-credential-redaction-1'
MASK='[REDACTED]'
LABEL=r'(?:password|passwd|pwd|parola|şifre|sifre|token|secret|secret[_ -]?key|private[_ -]?key|aws[_ -]?secret[_ -]?access[_ -]?key|api[_ -]?key|client[_ -]?secret|access[_ -]?token|refresh[_ -]?token|session[_ -]?(?:id|token)|authorization|cookie)'
ASSIGN=re.compile(r'(?i)(?<![\w])'+LABEL+r'[\"\u0027]?\s*(?::|=|\bis\b)\s*(?:"(?P<double>[^"]+)"|\u0027(?P<single>[^\u0027]+)\u0027|`(?P<tick>[^`]+)`|(?P<bare>[^\s,;\"\u0027`<>]+))')
PATTERNS=(
 ('credential_header',re.compile(r'(?im)^\s*(?:authorization|cookie|set-cookie)\s*:\s*(?P<header>[^\r\n]+)')),
 ('private_key',re.compile(r'-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----[\s\S]*?(?:-----END (?:[A-Z0-9]+ )?PRIVATE KEY-----|$)')),
 ('bearer',re.compile(r'(?i)\bBearer\s+([A-Za-z0-9._~+/-]{8,}=*)')),
 ('provider_key',re.compile(r'(?<![\w])(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{35})(?![\w])')),
 ('jwt',re.compile(r'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b')),
 ('url_password',re.compile(r'(?i)\b[a-z][a-z0-9+.-]*://[^\s/@:]+:(?P<password>[^\s/@]+)@')),
)
SAFE_VALUES={MASK,'null','none','unknown','unset','redacted'}

def redact_text(text):
    """Return sanitized text and counts only; never keep originals or their hashes."""
    if type(text) is not str:return text,{}
    spans=[]
    for category,pattern in PATTERNS:
        for m in pattern.finditer(text):
            group='header' if category=='credential_header' else 'password' if category=='url_password' else 1 if category=='bearer' else 0
            if m.group(group) not in SAFE_VALUES:spans.append((*m.span(group),category))
    for m in ASSIGN.finditer(text):
        group=next(k for k in ('double','single','tick','bare') if m.group(k) is not None)
        if m.group(group) not in SAFE_VALUES:spans.append((*m.span(group),'credential_assignment'))
    spans.sort(key=lambda x:(x[0],-x[1]));merged=[]
    for start,end,category in spans:
        if merged and start<merged[-1][1]:merged[-1]=(merged[-1][0],max(end,merged[-1][1]),merged[-1][2])
        else:merged.append((start,end,category))
    result=[];cursor=0;counts={}
    for start,end,category in merged:
        result.extend((text[cursor:start],MASK));cursor=end;counts[category]=counts.get(category,0)+1
    result.append(text[cursor:]);return ''.join(result),counts

def redact_value(value):
    """Display-only defense, not a new canonical source or approval payload."""
    if type(value) is str:return redact_text(value)[0]
    if type(value) is list:return [redact_value(v) for v in value]
    if type(value) is dict:
        return {k:(MASK if type(k) is str and re.fullmatch(LABEL,k,re.I) and v not in (None,MASK) else redact_value(v)) for k,v in value.items()}
    return value

def ensure_safe(value):
    if type(value) is str:
        if redact_text(value)[1]:raise ContractError('sensitive_content','Recognized credentials detected; redact the input before continuing.')
    elif type(value) in (dict,list):
        if type(value) is dict:
            for key,item in value.items():
                if type(key) is str and re.fullmatch(LABEL,key,re.I) and item not in (None,MASK):raise ContractError('sensitive_content','Recognized credentials detected; redact the input before continuing.')
                ensure_safe(item)
        else:
            for item in value:ensure_safe(item)

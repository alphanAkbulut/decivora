"""Kural tabanli aday cikarimi (TR+EN). LLM yok.

Beklenen: dusuk recall ve belirgin gurultu. Amac olcmektir.
Eslesme icin metin Turkce diakritiklerden arindirilip kucuk harfe cevrilir
(1:1 karakter eslemesi; span ofsetleri korunur).
"""
import re

_FOLD = str.maketrans({
    "ç": "c", "Ç": "c", "ğ": "g", "Ğ": "g", "ı": "i", "İ": "i",
    "ö": "o", "Ö": "o", "ş": "s", "Ş": "s", "ü": "u", "Ü": "u",
})


def fold(s):
    return s.translate(_FOLD).lower()


ACK_RE = re.compile(
    r"^\W*(tamam|tmm|ok|okay|peki|devam|evet|hayir|olur|anladim|anlasildi|tesekkurler|"
    r"tesekkur ederim|sagol|thanks|thank you|got it|sure|yes|no|done)\W*$")

RULES = [
    # (type, rule_id, rol kisiti, regex(katlanmis metin), aciklama)
    ("decision", "R-DEC", None, re.compile(
        r"\b(karar\w*|decision|decided|we'?ll go with|let'?s go with|going with|"
        r"ile devam|ile gidiyoruz|ile gidelim|secildi|sectik|kabul edildi|kabul ettik|"
        r"onaylandi|approved)\b"), "karar kalibi"),
    ("impl_claim", "R-CLM", "assistant", re.compile(
        r"\b(done|completed|implemented|fixed|finished|all set|tamamlandi|bitti|yaptim|"
        r"eklendi|duzeltildi|hazir|olusturdum|guncelledim|kurdum)\b"),
     "agent tamamlama iddiasi (dogrulanmadi)"),
    ("incomplete", "R-INC", None, re.compile(
        r"\b(todo|fixme|later|not yet|remaining|still need|pending|sonra bak\w*|daha sonra|"
        r"henuz|eksik|kaldi|bekliyor|yapilmadi|acik kaldi|unutma|hatirlat)\b"),
     "yarim/bekleyen is kalibi"),
    ("instruction", "R-INS", "user", re.compile(
        r"^\W*(yap|olustur|ekle|duzelt|yaz|kur|sil|degistir|guncelle|calistir|oku|incele|"
        r"hazirla|implement|create|add|fix|write|build|make|update|remove|delete|run|read|"
        r"check|review|prepare|use|do)\b"), "kullanici talimati (emir kipi)"),
    ("idea", "R-IDE", None, re.compile(
        r"\b(oneri\w*|fikir\w*|ya soyle|yapalim|yapabiliriz|ekleyelim|olsa iyi olur|what if|"
        r"we could|we should|how about|maybe we|consider|proposal|suggest\w*|idea)\b"),
     "fikir/oneri kalibi"),
]
RULE_DESC = {r[1]: r[4] for r in RULES}
SHORT_ANSWER_RE = re.compile(r'^\W*(a|b|c|evet|hayir|yes|no|tamam|ok|okay|peki|olur)\W*$', re.I)
MAX_PER_MESSAGE = 8
MIN_LEN = 12
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _segments(text):
    """(start, end) aralik listesi; kod citlerini atlar."""
    segs = []
    pos = 0
    in_fence = False
    for line in text.split("\n"):
        lstart = pos
        pos += len(line) + 1
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue
        cur = 0
        for part in SENT_SPLIT.split(line):
            i = line.find(part, cur)
            if i < 0:
                continue
            cur = i + len(part)
            segs.append((lstart + i, lstart + i + len(part)))
    return segs


def extract_with_coverage(role, text):
    """Bounded candidate extraction; limited coverage is never hidden."""
    ft = fold(text)
    if role == 'assistant' and ft.strip().strip('.!') in ('done', 'bitti', 'completed'):
        start = len(text) - len(text.lstrip())
        end = len(text.rstrip())
        return [dict(type='impl_claim', rule='R-CLM', start=start, end=end,
                     text=text[start:end])], 'complete_rules'
    if ACK_RE.match(ft.strip()):
        return [], 'complete_rules'
    out = []
    for s, e in _segments(text):
        if e - s < MIN_LEN:
            continue
        seg = ft[s:e]
        for typ, rid, role_only, rx, _desc in RULES:
            if role_only and role != role_only:
                continue
            if rx.search(seg):
                out.append(dict(type=typ, rule=rid, start=s, end=e,
                                text=text[s:e].strip()[:400]))
        if len(out) > MAX_PER_MESSAGE:
            return out[:MAX_PER_MESSAGE], 'limited'
    return out, 'complete_rules'


def extract(role, text):
    return extract_with_coverage(role, text)[0]

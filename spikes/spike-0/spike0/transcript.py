"""Transkript JSONL delta okuyucu (byte ofseti) ve mesaj ayiklama.

Gercek Claude Code transkriptinde (gozlem): satir `type` alani user/assistant/
attachment/system/queue-operation/... olabilir. user/assistant satirlarinda
message.content ya str ya da blok listesidir (text, tool_use, tool_result,
thinking). Yalnizca `text` bloklari alinir; `thinking` (ozel muhakeme) ve arac
sonuclari alinmaz.
"""
import json
import os
import re

MAX_READ = 32 * 1024 * 1024
SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
SKIP_PREFIXES = ("<command-name>", "<local-command-", "<bash-input>", "<bash-stdout>",
                 "[Request interrupted")


def read_delta(path, offset):
    """-> dict(records=[(start,end,rec)], new_offset, size, reset, bad, missing)"""
    out = dict(records=[], new_offset=offset, size=0, reset=False, bad=0, missing=False)
    try:
        size = os.stat(path).st_size
    except (FileNotFoundError, TypeError):
        out["missing"] = True
        return out
    out["size"] = size
    if size < offset:
        offset = 0
        out["reset"] = True
        out["new_offset"] = 0
    if size == offset:
        return out
    with open(path, "rb") as f:
        f.seek(offset)
        data = f.read(min(size - offset, MAX_READ))
    last = data.rfind(b"\n")
    if last < 0:
        if len(data) >= MAX_READ:  # asiri uzun tek satir: atla
            out["new_offset"] = offset + len(data)
            out["bad"] = 1
        return out  # yarim satir: bekle
    complete = data[: last + 1]
    pos = offset
    for line in complete.split(b"\n")[:-1]:
        start = pos
        pos += len(line) + 1
        s = line.strip()
        if not s:
            continue
        try:
            rec = json.loads(s.decode("utf-8"))
        except Exception:
            out["bad"] += 1
            continue
        out["records"].append((start, pos, rec))
    out["new_offset"] = offset + len(complete)
    return out


def to_message(rec):
    """Ham kayit -> mesaj dict (ham metin) ya da None."""
    if not isinstance(rec, dict) or rec.get("type") not in ("user", "assistant"):
        return None
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return None
    role = msg.get("role") or rec.get("type")
    content = msg.get("content")
    parts = []
    if isinstance(content, str):
        parts.append(content)
    elif isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str):
                parts.append(b["text"])
    text = "\n".join(parts)
    text = SYSTEM_REMINDER_RE.sub("", text).strip()
    if not text or text.startswith(SKIP_PREFIXES):
        return None
    return dict(
        uuid=rec.get("uuid"), role=role, text=text, ts=rec.get("timestamp"),
        cwd=rec.get("cwd"), sidechain=bool(rec.get("isSidechain")),
        version=rec.get("version"))


def tail_assistant_texts(path, tail_bytes=262144):
    """Dosya sonundaki assistant metinleri (Stop zamani transkript guncel mi kontrolu)."""
    try:
        size = os.stat(path).st_size
        with open(path, "rb") as f:
            start = max(0, size - tail_bytes)
            f.seek(start)
            data = f.read()
    except Exception:
        return []
    lines = data.split(b"\n")
    if start > 0:
        lines = lines[1:]
    texts = []
    for ln in lines:
        try:
            m = to_message(json.loads(ln.decode("utf-8")))
        except Exception:
            continue
        if m and m["role"] == "assistant":
            texts.append(m["text"])
    return texts

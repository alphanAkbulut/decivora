"""Sentetik fixture uretici (gercek veri YOK). `python3 tests/make_fixtures.py`.

Gercek transkript bicimini taklit eder (type/uuid/sessionId/cwd/message...).
Burst (1000 mesaj) testte uretilir, repoya konmaz.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helpers import FIX, assistant, user, write_jsonl  # noqa: E402

C = "/work/demo"  # cwd; testler bagi kendi tmp dizinine gore kurar


def noise(sid):
    """Gercek transkriptte bulunan ama alinmamasi gereken kayitlar."""
    return [
        {"type": "queue-operation", "operation": "enqueue", "sessionId": sid},
        {"type": "attachment", "uuid": "att-" + sid, "sessionId": sid, "attachment": {"x": 1}},
        {"type": "assistant", "uuid": "tu-" + sid, "sessionId": sid, "cwd": C, "isSidechain": False,
         "message": {"role": "assistant", "content": [
             {"type": "thinking", "thinking": "Karar: bu ozel muhakeme alinmamali"},
             {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}}]}},
        {"type": "user", "uuid": "tr-" + sid, "sessionId": sid, "cwd": C, "isSidechain": False,
         "message": {"role": "user", "content": [
             {"type": "tool_result", "tool_use_id": "t1", "content": "Karar: arac sonucu alinmamali"}]}},
        user("sr-" + sid, sid, C, "<system-reminder>Karar: hatirlatma alinmamali</system-reminder>"),
    ]


FIXTURES = {
    "f01_noop.jsonl": lambda: [
        user("u1", "s1", C, "tamam"), assistant("a1", "s1", C, "Anlaşıldı."),
        user("u2", "s1", C, "devam"), assistant("a2", "s1", C, "Tamam, devam ediyorum."),
        user("u3", "s1", C, "ok"),
    ] + noise("s1"),
    "f05_claim.jsonl": lambda: [
        user("u1", "s5", C, "Hook alıcıyı yaz."),
        assistant("a1", "s5", C, "Hook alıcıyı tamamlandı olarak işaretledim, testler yeşil."),
    ],
    "f06_reversal.jsonl": lambda: [
        user("u1", "s6", C, "Karar: yerel depolama için SQLite kullanacağız."),
        user("u2", "s6", C, "Karar değişti: SQLite yerine Postgres ile devam edelim."),
        user("u3", "s6", C, "Karar: Postgres kullanalım, SQLite'a gerek yok."),
    ],
    "f07_mixed.jsonl": lambda: [
        user("u1", "s7", C, "We'll go with SQLite for now."),
        user("u2", "s7", C, "Karar: kayit icin olay gunlugu ile devam."),
        assistant("a1", "s7", C, "I think we should add a review inbox. Ayrica kararlastirdik ki "
                                 "onay ekrani metin istemeyecek."),
        user("u3", "s7", C, "karar verdik, kuyruk sinirli olacak"),
    ],
    "f08_parallel_s1.jsonl": lambda: [
        user("p1", "par1", C, "Karar: dashboard için React kullanacağız.")],
    "f08_parallel_s2.jsonl": lambda: [
        user("p2", "par2", C, "Karar: dashboard için React yerine Svelte ile devam.")],
    "f08_parallel_s3.jsonl": lambda: [
        user("p3", "par3", C, "Önerim: kartlara kısa bir gerekçe satırı ekleyelim.")],
}


def main():
    os.makedirs(FIX, exist_ok=True)
    for name, fn in FIXTURES.items():
        write_jsonl(os.path.join(FIX, name), fn())
    print("%d fixture yazildi: %s" % (len(FIXTURES), FIX))


if __name__ == "__main__":
    main()

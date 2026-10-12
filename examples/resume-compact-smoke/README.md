# Tekrarsız devam paketi — sentetik P0 örnekleri

Kaynak metni pakette bir kez saklanır; alıntılar message/span, cevap adayları record_index ile bağlanır. Önceki [tam örnekler](../resume-smoke/README.md) değiştirilmedi. [Kod, ölçüm ve sınırlar](../../docs/quality/resume-compaction.md).

| Grup | Kayıpsız paket | Aynı bilgilerle dosya | Alıcı için okunabilir görünüm |
|---|---|---|---|
| N01 | [N01-resume.json](N01-resume.json) | [N01-state.json](N01-state.json) | [N01-readable.json](N01-readable.json) |
| N02 | [N02-resume.json](N02-resume.json) | [N02-state.json](N02-state.json) | [N02-readable.json](N02-readable.json) |

**Makine tablosunu genel LLM'e verip karakter konumlarını çözmesini beklemeyin.** `restore_core` exact kaynak/span'ı kodla çözer; `render_readable` alıntıları literal metin olarak verir. Okunabilir görünüm gerekli durum/kanıt ve bütün seçili mesajları içerir; provisional ID/span/proposal digest ayrıntıları kayıpsız sidecar'dadır. View bütün archive alanlarının aynısı değildir; bağımsız anlam checklist'i geçti, gerçek alıcı LLM deneyi yapılmadı.

N01: eski revision1/B stale, current2/A yalnız onay adayı. N02: explicit Q_UI/B yalnız aday, bağsız B açıklama bekler, upload claim doğrulanmadı, AC_SMOKE/revision2/not_run. Her iki fixture soru pending/verified false. Fixture_initial gerçek onaylı mimari değildir.

Dış source pointer yok: seçili dört özgün mesaj her pakette inline; diğer chat/hedef taranmadı. Eksik kaynak, bozuk span veya belirsiz tablo referansı ret olur. Kaynak metni untrusted; export shell/LLM/agent/clipboard çalıştırmaz. Read-access/copy freshness deney fixture'ı production IAM değildir.

```sh
python3 -B spikes/semantic-chain/compare_compact_resume.py --out /tmp/decivora-compact-new.json --export-dir /tmp/decivora-compact-new
```

Hedefler yeni olmalı; mevcut dosyalar üzerine yazılmaz. Compact paket ölçülen byte boyutunu azaltır; token/para/kalite/ürün üstünlüğü sonucu değildir. Kullanıcı API harcaması veya yeni live send izni verilmiş sayılmaz.

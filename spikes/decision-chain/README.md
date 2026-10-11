# P0 — Karar, etki ve kanıt zinciri

**Çalışan kontrollü fixture deneyi; production runtime veya MVP değildir.** Python 3.9+ standart kütüphanesi/SQLite; ağ, model, credential ve host kurulumu yok.

## Çalıştır

Repo kökünden:

```bash
python3 -B -m unittest discover -s spikes/decision-chain -v
python3 -B spikes/decision-chain/run.py
```

15 test: geciken explicit soru cevabı, agent approval reddi, stale soru/base/graph, idempotency conflict, AND/OR/unknown, eski ref, partial AC, failed verification, yeni artifact, missing/permission unknown, boş AC, append-only ve backup/replay.

Koşu temporary workspace açıp kapatır. Kalıcı gerçek veriyi veya projeyi değiştirmez. [Kaydedilmiş koşu](../../docs/quality/decision-chain-results.json) ve [bulgu/kalan kapsam](../../docs/quality/audit-remediation.md).

## Deney sınırı

Typed command/payload’lar program tarafından verilmiştir; transcript extraction testi değildir. `human/observer/verifier` yalnız güvenilir fixture rolüdür; caller’ın role string’ini belirleyebilmesi production IAM olamaz. `source_session` bağlam metadatasıdır; başka chat’e erişim veya otomatik soru eşleştirme yapılmıyor.

Tek storage kararı/soru senaryosu kullanılır; aktif `security` gerekçesi fixture sabitidir. Genel domain schema/reason graph/API yerine konulamaz. AND/OR/unknown fonksiyonu test edilmiştir; arbitrary/untrusted expression validator değildir. Question option revision ve command base revision kontrol edilir; tam policy/AC revision/expiry/connection-grant sistemi yoktur.

Etki preview digest ve base revision’a bağlıdır. İnsan fixture apply yapana kadar task durumları kapanmaz. `obsolete_candidate`, `review_unknown`, retained ayrı değerlendirilir; bu harness ürün task lifecycle’ının tüm transition’larını sağlamaz.

Yerel byte hash ve `fixture-ref` kontrolü eski/yeni gözlem ayrımını sınar; GitHub adapter değildir. Test/verifier passed/failed sonuçları kontrollü girdidir, gerçek ürün acceptance runner’ı değildir. Bütün gerekli fixture AC’leri ve doğru target gözlemi olmadan verified olmaz.

SQLite event UPDATE/DELETE trigger’ları ve hash chain var; DB yöneticisi tarafından değiştirilemez audit garantisi yoktur. Replay saf projector, model/verifier/dış dispatch içermez. SQLite backup sadece bu tek DB’yi kapsar; production payload bundle, encryption, purge, migration ve recovery T07c/T23a kapsamındadır.

Bu deney T03’ün öğrenme dilimine kanıt verir; T04–T15 veya production ADR’leri tamamlamaz.

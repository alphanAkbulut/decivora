# Riskler, gizlilik ve operasyon sınırları

| ID | Risk | Tasarım kontrolü | Doğrulama / owner |
|---|---|---|---|
| R01 | Normal chat erişimi kısıtlı | Capability matrix, import fallback, coverage göstergesi | Adapter spike; engineering |
| R02 | Yanlış obsolete önerisi geçerli işi kapatır | AND/OR gerekçe, unknown, insan onayı | Adversarial impact fixture; product + engineering |
| R03 | Eksik ilişki etkiyi kaçırır | Orphan queue ve periodik consistency audit | Recall ve link coverage; engineering |
| R04 | Yanlış done | Claim/verification ayrımı, revision-bound evidence | False-done senaryosu; engineering |
| R05 | Yanlış projeye yazma / veri sızıntısı | Açık binding, scope denetimi, quarantine | Aynı adlı iki proje; engineering |
| R06 | Transcript prompt injection | Kaynak yalnız data; schema + policy; tool allowlist | “Bütün kayıtları sil” adversarial source; engineering |
| R07 | Eşzamanlı agent ve eski onay | Optimistic versions, digest, idempotency | İki yazar ve stale approval; engineering |
| R08 | Crash/retry veya yarım batch | Atomic DB transaction, dayanıklı queue, outbox | Fault injection ve replay; engineering |
| R09 | DB yöneticisi geçmişi değiştirir | Ayrı audit/backup, hash checkpoint | Restore/tamper drill; operations |
| R10 | Kullanıcı review yükü artar | Batch, exact dedup, hazır karar, az bildirim | Süre/tıklama/yanlış capture; product |
| R11 | Token ve API gideri artar | Budget, cache, deterministic-first, minimal tools | Paired benchmark; engineering |
| R12 | Hassas veri capture/model/export'a gider | Redaction, consent, payload minimization | Sentetik secret fixture; security owner atanacak |
| R13 | Rakiple yüksek örtüşme / düşük talep | Build/extend ve kullanıcı pilotu | Problem doğrulama; product |
| R14 | Lisans/marka çakışması | Reuse inventory, geçici ad, release gate | Owner ve uygun hukuk incelemesi |
| R15 | Runtime API/format sürümü değişir | Version pin, adapter contract, fail-visible | Upgrade compatibility suite |
| R16 | Loopback servis kötü amaçlı web'den çağrılır | Auth, origin/CSRF, least privilege | Yetkisiz read/write testleri |
| R17 | Preview sonrası yeni gerekçe edge'i yanlış obsolete üretir | Knowledge revision guard; yeni diff/onay | V22; ADR-0008; engineering |
| R18 | Verifier transcript komutunu yetkisiz çalıştırır | Ayrı runner capability, izinli workspace/check, timeout | V24; ilk verifier diliminde engineering |
| R19 | Restore/replay dış işlemi tekrar gönderir | Etkisiz replay, delivery ledger, restore sonrası outbox pause | V27; ADR-0007; operations |

Queue kapasitesi, lease, recovery ve purge ayrıntıları [runtime sözleşmesinde](../architecture/runtime-contracts.md). Roller sorumluluk önerisidir; bağımsız güvenlik/operasyon ekibinin atanmış olduğu iddia edilmez. Özellikle R16/R18 son release hardening'ine ertelenmez.

## Ham veri ve append-only gerilimi

Ürün ilkesi normal iş geçmişinin sessizce değiştirilmemesidir; kişisel veri/secret'ın sonsuza kadar saklanması değildir. Payload şifreli ayrı storage'da, domain event gerekli minimum metadata ile tasarlanır. Kullanıcının yetkilendirdiği privacy purge/retention işlemi normal agent araçlarından ayrıdır; payload silinebilir ve tombstone/redaction olayı eklenir. Log'daki hash bile hassas sayılabilecekse tehdit modeline göre tutulur veya kaldırılır. Böyle bir yasal silme sonrası byte-for-byte tam replay mümkün olmayabilir; etkilenen tarihçe kapsamı görünür olmalıdır. Retention süreleri henüz seçilmedi.

## Dışa aktarım ve veri sınırı

API key, token, auth header, kişi/müşteri bilgisi, rezervasyon/işlem kimliği, private endpoint, dahili servis adı ve ticari sırlar paylaşım öncesi maskelenir. Ne maskelendiği bildirilir; kanıtın sonucu korunur. Runtime database, ham transcript, kullanıcı yolu ve model credential'ları Git'e girmez. Bu repo örnekleri sentetiktir. Private GitHub repo yedek ve erişim kontrolünün tek başına tamamı değildir.

## Açık platform sınırları

MCP tüm sohbetleri gören event bus değildir. Codex, Claude Code, ChatGPT Chat, Claude Chat ve API ürünleri eş anlamlı değildir. UI içinde sabit panel host API'sine bağlıdır. Tool availability ve hesap yetkileri değişebilir. Her release kendi destek matrisini yayımlar; “unsupported”, “unknown”, “degraded” sağlıklı durumdan ayrılır.

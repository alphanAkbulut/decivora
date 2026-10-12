# Riskler, gizlilik ve operasyon sınırları

> [!WARNING]
> **Aktif P0 engeli: R20 — model çıktısının kaynak konumu güvenilir değil.** S02-002'de 10/11 span hatalı; batch reddedildi, semantik ölçüm ve karar zinciri başlamadı. [Deneme geçmişi](../quality/s02-second-attempt-result.md). [Yeni offline adapter](../quality/source-anchor-adapter.md) konumları ayrı türevde çözüyor; gerçek kalite/production kapısı açık. Fixture/unit test başarısı risk kapanışı değildir.

## Gözlenen ve henüz ölçülmeyen öncelikli riskler

High bir engineering etki değerlendirmesidir; istatistiksel olasılık veya kesin başarısızlık oranı değildir. Örnekler n=1 çıktı ve bir ayrı erişim hatasıdır. Observed = gerçekleşti; Unknown/Unmeasured = yeterli kanıt yok; kontrol önerisi = uygulanmış çözüm değil. Aktif işler backlog'a bağlıdır; tek başarısız deney ana task'ı otomatik Blocked/Done yapmaz.

| Risk | Durum / etki | Kanıt | Açık iş / sorumluluk |
|---|---|---|---|
| R20 · Modelin yanlış kaynak konumu üretmesi | Observed / High; T03 geçerli import ve scorer'ı durdurur | S02-002: 10/11 span yanlış, 11 exact quote; [bounded adapter ve 48 suite testi](../quality/source-anchor-adapter.md) engineering mitigasyonu; yeni contract için gerçek semantic/production proof yok | T03/T09 · adapter/negatifler teslim; bağımsız gerçek semantic kalite, ilişkiler ve production entegrasyonu açık; Closed değil |
| R01 · Host erişiminin kesilmesi | Observed; devamlılık/root cause Unknown | S02-001 cloudflare_challenge; S02-002 Chrome'da output geldi, kontrollü browser kıyası yapılmadı | T02/T03 · engineering: capability/coverage/fallback; otomatik retry/izin varsayma |
| R11 · Hesap yolunda token/context/para üst sınırı belirsiz | Unknown / High; sınırsız bütçe izni değil | Web smoke usage null; manuel sınırlı istisna, strict otomatik preflight blocked | T03/T21 · engineering + owner: gerçek cap/telemetri; yeni çağrı için yeni somut izin |
| R02/R04 · Yanlış karar etkisi veya yanlış done | Unmeasured gerçek-model akışı / High | Fixture negatif testleri var; S02-002 bu aşamalara ulaşmadı | T03/T12/T14 · engineering: source bağlamadan sonra ayrı approval/evidence/AC testleri |
| R13 · Kullanıcı değeri ve native araçlara üstünlük | Unmeasured | Kullanıcı örneği problem hipotezi; insan pilotu/native paired kıyas not_run | T03c/T24 · product owner: kalite, düzeltme süresi ve toplam maliyet kıyası |

Risk kapanışı: kanıt → etkilenen iş → düzeltme → anlamlı negatif/pozitif test → kalan sınır kaydı. Kontrolün test edilmesi ile üretimde riskin azalmasının ölçülmesi ayrı tutulur. Otomatik “testler geçti = risk yok” çıkarımı yapılmaz.


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
| R20 | Model kaynak span/offset yanlış üretir; bütün batch kullanım dışı kalır | Message ID + tekil exact quote ile kodda konum; revision binding, ambiguous rejection; strict validator korunur | S02-002 Observed; ANCHOR-ADAPTER-01 offline kod/negatifler teslim; yeni contract gerçek inference ve production doğrulaması açık; T03/T09 |
| R21 | Serbest candidate attributes/tür adları producer ile bridge/scorer sözleşmesini ayırır | Ayrı typed v2 contract, explicit field/type rules, alias/authority retleri; raw ve primary score korunur | MEMBERSHIP-001 Observed: source geçti, exact candidate gate incomplete; [rapor](../quality/membership-001-result.md). [MEMBERSHIP-002](../quality/membership-002-result.md): tek v2 output dört draft adayla eşleşti; dar mitigation, human gold/holdout/production kalite açık; n=1 genel hata oranı değil; T03/T09 |
| R22 | Birden fazla AnswerRecord eski one-answer bridge'i durdurur; source/revision ayrımı kaybolursa yanlış seçim olabilir | Tam response validation ardından source/message/revision bazında read-only proposals; conflict/duplicate/ambiguity korunur, separate receipt gerekir | Observed / P0 mitigation implemented: T03r collector ve102 test/9 yeni, stored MEMBERSHIP-003 replay mutation0. [Kanıt](../quality/proposal-collection.md). Eski API korunur; production çok-soru/response reconciliation açık; T10/T13 |
| R23 | Compact thread status summary null/false veya ham metin biçimini kaybedebilir; model hatası sanılabilir | Raw authority olarak untruncated final_message oku; exact input/text hash/provenance tut, summary'yi onarma veya parser oracle yapma | RECEIVER-001 Observed: waitsnapshot JSONinvalid/fullmessage JSONvalid; ayrı capturediagnostic. [Rapor](../quality/receiver-001-result.md); T03/T06/T09/T22 |
| R24 | Receiver bir ambiguous cevabı tüm proje için abstain yapıp yine readback/actions verir; type ve action scope bozulur | Strict abstention/schema/type/scope gate, source kayıtları ve claim/approval ayrımı; clearer schema synthetic negatives, yeni model izni ayrı | RECEIVER-001 Observed: invalidabstention/stringrevision/extrafutureaction; rawunchanged/no canonicalmutation, model quality açık. [Yerel schema/source guard](../quality/receiver-contract.md) 16 yeni negatif/pozitif test ile tamamlandı; yeni model/provider davranışı sınanmadı. [İlk rapor](../quality/receiver-001-result.md); T03/T09/T18/T24 |

Queue kapasitesi, lease, recovery ve purge ayrıntıları [runtime sözleşmesinde](../architecture/runtime-contracts.md). Roller sorumluluk önerisidir; bağımsız güvenlik/operasyon ekibinin atanmış olduğu iddia edilmez. Özellikle R16/R18 son release hardening'ine ertelenmez.

## Kaynak tüketimi ve kötüye kullanım

İstek seli, agent döngüsü, pahalı batch, storage/log şişmesi ve shared-provider bütçe aşımı için [limit ve kötüye kullanım sözleşmesi](../architecture/resource-limits-and-abuse.md) R06/R08/R11/R16'yı tamamlar. Kontroller ilk ingress/dispatch'te başlar; LIM-01–10 uygulamayla doğrulanacaktır. IP-only ve yalnız istek sayısı yeterli değildir. API limiter; fiziksel DB erişimini veya ağ düzeyinde DDoS'u tek başına engellediği iddiası taşımaz. Meşru burst ve ortak IP için yanlış throttle da ölçülür.

## Ham veri ve append-only gerilimi

Ürün ilkesi normal iş geçmişinin sessizce değiştirilmemesidir; kişisel veri/secret'ın sonsuza kadar saklanması değildir. Payload şifreli ayrı storage'da, domain event gerekli minimum metadata ile tasarlanır. Kullanıcının yetkilendirdiği privacy purge/retention işlemi normal agent araçlarından ayrıdır; payload silinebilir ve tombstone/redaction olayı eklenir. Log'daki hash bile hassas sayılabilecekse tehdit modeline göre tutulur veya kaldırılır. Böyle bir yasal silme sonrası byte-for-byte tam replay mümkün olmayabilir; etkilenen tarihçe kapsamı görünür olmalıdır. Retention süreleri henüz seçilmedi.

## Dışa aktarım ve veri sınırı

API key, token, auth header, kişi/müşteri bilgisi, rezervasyon/işlem kimliği, private endpoint, dahili servis adı ve ticari sırlar paylaşım öncesi maskelenir. Ne maskelendiği bildirilir; kanıtın sonucu korunur. Runtime database, ham transcript, kullanıcı yolu ve model credential'ları Git'e girmez. Bu repo örnekleri sentetiktir. Private GitHub repo yedek ve erişim kontrolünün tek başına tamamı değildir.

## Açık platform sınırları

MCP tüm sohbetleri gören event bus değildir. Codex, Claude Code, ChatGPT Chat, Claude Chat ve API ürünleri eş anlamlı değildir. UI içinde sabit panel host API'sine bağlıdır. Tool availability ve hesap yetkileri değişebilir. Her release kendi destek matrisini yayımlar; “unsupported”, “unknown”, “degraded” sağlıklı durumdan ayrılır.

## Çok kullanıcı ve veri altyapısı ek riskleri

| Risk | Önerilen kontrol / kanıt |
|---|---|
| Workspace rolünden private kaynak sızması | Proje ve kaynak ACL; türetilen summary/citation/count/context kontrolü; MU01/MU05/MU10 |
| İptal edilmiş grant ile queued iş veya dış egress | Authz revision, dispatch/commit kontrolü, quarantine; MU03/MU04/MU18 |
| Agent'ın insan/runner yetkisini taklit etmesi | Ayrı principal/grant; trusted actor; MU02/MU07 |
| Log veya yedekten veri sızması | İlk yazım redaction, ayrı audit erişimi, şifreli backup/key yönetimi; MU08/MU09/MU12 |
| TTL ile kaynak/idempotency kaybı | Raw TTL ile kompakt kimlik ömrü ayrı; review uyarısı; MU11 |
| Audit veya disk arızasında sahte başarı | Yüksek etkili commit audit ile atomik; backpressure; MU08/MU15 |
| Paylaşılan DB/pool üzerinden tenant karışması | Merkezi API, tenant FK, nonowner RLS, pool reset; MU13/MU14 |
| Aynı OS hesabına tam yetkili agent | API ACL fiziksel sınır değildir; ayrı servis hesabı/sandbox/host deployment gerekir |

[Kimlik](../architecture/identity-access.md), [log](../architecture/logging-audit.md), [veri yaşam döngüsü](../architecture/storage-memory-capacity.md) bu risklerin ayrıntılı önerileridir. Mevcut kontrollerin uygulanmış/güvenlik taramasından geçmiş olduğu iddia edilmez.

## Güncel gerçekleşme/rekabet riskleri

- Öneri veya sessizliği insan seçimi; generated dosyayı applied; eski/başka hedef gözlemini current completion sayma: [GAP](../product/intent-to-reality-gap.md), ADR-0011 ve typed target/assessment doğrulaması.
- İlk deneyi geçirmek için sürekli manuel import/kontrol gerektirme: bütün yönetim/setup/bakım süresini baseline'a dahil et; kullanıcıya yeni proje yönetim yükü yaratma.
- Claude Projects ile örtüşmeyi küçümseyip geniş MVP'ye erken yatırım: [güncel yön](../product/current-direction.md), T03 native/extend/build kapısı; ürün iptali de kanıtsız varsayılmaz.
- Prototip, tasarım revizyonu veya mock sonucunu ürün release'i sanma: [versioning](versioning.md) ve ayrı acceptance/test sütunları. Bu kontroller tasarımdır, uygulanmış risk azaltımı değildir.

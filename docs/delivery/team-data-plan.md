# Ekip ve veri altyapısı uygulama planı

**Durum: tasarım tamamlayıcısı; kod ve runtime testleri yapılmadı.** İlk kullanıcı owner, sonra benzer bireysel kullanıcılar. Ekip özellikleri tam vizyonda korunur; bu plan ilk pilotu sessizce SaaS'a dönüştürmez. Temel kimlik/veri sınırları erken; davet ve çok insanlı yönetim daha sonra gelir.

## Şimdi tasarlanan kararlar

- [Tek insan + çok agent / ekip kurulumu](../architecture/agent-and-team-operation.md): görünür işlem kayıtları, parent/run/task ayrımı, capability tablosu, merkezi servis ve hesap yaşam döngüsü. Çok-agent gözlemi çok insanlı ekip sürümünden bağımsız pilotlanır.

- [İnsan/agent kimliği ve rol matrisi](../architecture/identity-access.md): kimin hangi kaynakta ne yapabildiği.
- [Dört kayıt sınıfı](../architecture/logging-audit.md): gözlem, domain geçmişi, güvenlik audit'i ve operasyon logu.
- [Kalıcı/geçici hafıza, retention ve kapasite](../architecture/storage-memory-capacity.md): ne saklanır, ne yeniden üretilir, ne zaman ölçeklenir.
- [Hedefli benchmark](../discovery/collaboration-storage-benchmark.md): hangi belgelenen örüntüyü neden benimsiyoruz.
- [MU01–MU18 kabul planı](../quality/collaboration-validation.md): gözlenebilir hata ve yarış senaryoları.

## P1'de küçük uygulanabilir dilimler

Ana görevler [T01–T30](backlog.md) korunur. Bu alt dilimler ilgili ana görevin kabulüne eklenir; tamamlanmış sayılmaz. Her dilim bir review edilebilir değişiklik; süre taahhüdü yok.

| Dilim / bağımlılık | Somut çıktı | Kabul / kapı |
|---|---|---|
| T05b / T04a,T05a | Kişisel workspace, human/agent ID, compound tenant FK, session binding şeması | Tek owner modu ve cross-project negatif test; MU01 |
| T08b / T05b,T08a | `authorize(action,resource,context)` sınırı, dar grant, authz revision/commit kontrolü | Spoof/revoke/stale run reddi; MU02–MU04/MU06 |
| T06d / T06a,T05b | Receipt/dedup ömrünü raw payload'dan ayır; bounded spool/backpressure | Ack olmayan veri TTL ile kaybolmaz; MU11 |
| T07b / T07a,T08b | Domain command + güvenlik audit atomikliği; güvenli structured logger | Audit arızası mutation'ı durdurur; log secret içermez; MU08/MU09 |
| T18b / T18a,T08b | ACL-aware retrieval/context; personal→project paylaşım proposal'ı | Private özet/citation sızmaz; MU05/MU10 |
| T23c / T23a,T23b | Versioned retention, expiry preview, türev invalidation, purge/restore manifest | TTL ve restore drill; MU11/MU12; OPEN-08 gerçek veri öncesi |
| T23d / T23c | Tutarlı DB+blob snapshot; disk/WAL/backup health; sentetik load harness | Hata ve capacity raporu, ölçülmüş RPO/RTO; MU15/MU16 |
| T24b / T23d,T18b | Bireysel pilot erişim/retention anlaşılabilirliği ve kaynak kaybı ölçümü | Kullanıcı “kim görür/ne silinir?” yanıtını doğru verebilir; kalan sınırlar raporlu |
| T28b / T28,T08b | Dış delivery öncesi güncel connector/actor scope kontrolü | MU18; belirsiz dış sonuç doğru gösterilir; P3'e kadar uygulanmaz |

## Çok-agent ve ekip teslim kapıları

### P1b çok-agent pilotu — ekip hesabı gerektirmez

| Dilim / bağımlılık | Somut çıktı | Kabul |
|---|---|---|
| T02c / T02 | İki izinli oturum/run için kimlik, parent, input, tool, output, usage ve stop capability raporu | AGT-01–03; gerçek host/build; erişilemeyen alan unknown. Q02 yüzey seçimi, gerçek veri/ücret için Q03 |
| T18d / T05b,T08b,T18b,T18c,T02c | Aynı kişisel projede iki agent'ın kaynaklı kaydı, run/task bağları ve sınırlandırılmış context'i | AGT-01–06; duplicate/race/revoke/usage; agent başlatma zorunlu değil |
| T24e / T18d,T24b | Tek owner + iki agent pilotu; sentetik başlangıç, coverage ve kanıt incelemesi | AGT-01–06; false completed yok, görünmeyen input/muhakeme uydurulmaz |

SDK/orchestrator ile aktif execution daha sonraki ROU-02 kapsamıdır. Görevleri takip etmek ve agent'ı başlatmak aynı teslim değildir.

### P4 ekip kurulum ve erişim kapıları

T30 discovery çıktısı bu C-dilimlerinin ihtiyaç/öncelik ve deployment kararını kesinleştirir. P4 uygulaması owner kapsam/işletim kararı ardından gelir; bugünkü dokümantasyon kararı hosted servis satın alma yetkisi değildir.

| Sıra | Teslim | Bağımlılık ve kabul |
|---|---|---|
| C01 | Ekip pilot profili: aynı proje kaç insan/agent, private kaynak, tek/çok workspace, self-host/managed ve identity provider seçimi | T30; açık sorular karara bağlanmış; tehdit/operasyon sınırı belgeli |
| C02 | Merkezi API/Postgres migration ve tenant veri erişim katmanı | C01 + T23d; MU13/MU14; TLS, secret/backup işletimi, nonowner DB rolü |
| C03 | Davet/kabul, rol değişikliği, son owner transferi, offboarding ekranları | C02; MU01/MU17; işlem audit'i ve session/grant revocation |
| C04 | Çok insanlı review policy'si, agent listesi/grant editörü, shared memory UX | C03 + T18b; MU03–MU07/MU10; bağımsız reviewer ve değişiklik önizlemesi |
| C05 | Ekip audit/export, support erişimi, connector sponsor/egress ve purge/restore | C04; MU08/MU09/MU12/MU18; dış etki/belirsizlik doğru |
| C06 | Kotalar, noisy-neighbour testi, çok worker, kapasite ve kurtarma tatbikatı | C05; MU15/MU16; maliyet/operasyon raporu ve ekip release kararı |

C01–C03 ayrıca doğrulanabilir ilk owner bootstrap, ayrı kullanıcı oturumu/giriş/çıkış, hesap kurtarma ve self-host işletim sorumluluklarını içerir. C03/C04 kişisel→ekip aktarım önizlemesi ve rol değişimi/revocation için AGT-07/08'i MU kontrolleriyle birlikte doğrular. Workspace membership, ürünün ticari lisansı ve harici model aboneliği ayrı kavramlardır; paket/SSO/koltuk fiyatı kararı henüz yoktur.

```mermaid
flowchart LR
    P1[P1 Kimlik ve veri sınırları] --> SOLO[Bireysel pilot kanıtı]
    SOLO --> NEED[T30 Ekip gereksinimi ve işletim kararı]
    NEED --> C2[C02 Merkezi veri ve izolasyon]
    C2 --> C3[C03 Üyelik yaşam döngüsü]
    C3 --> C4[C04 İnsan ve agent işbirliği]
    C4 --> C5[C05 Audit ve recovery]
    C5 --> C6[C06 Ölçek ve ekip pilotu]
```

## Karar gerektirenler

Bugün yeni kullanıcı sorusu zorunlu değil: bireysel pilot tercihi mevcut. Ekip aşamasında deployment ve private veri sahipliği; korumalı kararlar için gereken reviewer sayısı; kesin retention/key recovery; hedef kapasite ve işletim bütçesi somut pilot profiliyle seçilecek. Bunlar [OPEN-14–OPEN-16](../governance/open-decisions.md) altında kayıtlıdır. Daha önce sorulan coding/chat yüzeyi ve harici model/veri/bütçe yanıtı bu planla cevaplanmış sayılmaz.

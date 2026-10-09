# Kapsam ve mimari yeniden inceleme

**Tarih: 2026-10-09.** İncelenen başlangıç revision'ı `5e72f737ced3e4f334c118eff82495661a89bdd7`. Yöntem: kaynak sohbetin 14 evresi ve engine terimleriyle repository belgelerini eşleştirme; 32 kapsam maddesini feature/engine/task/test zincirine bağlama; hata/yarış/recovery senaryolarıyla mimariyi masa başında inceleme. Bağımsız LLM değerlendirmesi veya çalışan ürün testi yapılmadı.

## Sonuç

Ana ürün vizyonu ilk pakette korunuyordu. Asıl eksik, bazı kavramların belgeler arasında dağınık kalması ve sistem davranışlarının yeterince uygulanabilir olmamasıydı. Bu revizyon aşağıdaki boşlukları **dokümantasyon düzeyinde** tamamlar. Kaynak sohbetin önemli ürün niyetleri için eşleşme var; gelecekte hiç eksik çıkmayacağı veya runtime güvenilirliği iddia edilmez.

| Bulgu | Önceki durum | Bu revizyondaki karşılık | Uygulama kanıtı |
|---|---|---|---|
| Engine adları parçalı | Reconciliation/verification vardı; Idea Evaluation ve Knowledge Evolution eşlemesi örtüktü | 10 modül ve kaynak alias sözlüğü; kim yazabilir/girdi/çıktı/fallback | T09–T14/T18/T21/T26 bekliyor |
| Özellikler deneyimden kopuktu | Scope tablosu vardı, uçtan uca görünür davranış dağınıktı | 17 kullanıcı özelliği ve ana journey | T19–T24 bekliyor |
| Traceability tam zincir değildi | Scope→task vardı; source→feature→engine→test tek yerde yoktu | 32 satırlı [izlenebilirlik matrisi](traceability.md) | Yalnız belge referansları kontrol edilebilir |
| Graph onay yarışı | Base record revision kontrolü yeni eklenen gerekçe edge'ini kaçırabilirdi | Project knowledge revision guard; ADR-0008 | V22/T12/T13 bekliyor |
| Source alımı ve değerlendirme ack'i | Dayanıklı ack ilkesi vardı; cursor/lease/error ayrıntısı eksikti | İki cursor, contiguous watermark, lease/fencing, bounded retry/quarantine | V19–V21/T06 bekliyor |
| Replay dış etkileri | Replay LLM çağırmaz deniyordu; outbox restore davranışı açık değildi | Yan etkisiz projection replay; restore'da dış delivery durur; ADR-0007 | V27/T15/T23 bekliyor |
| Verification yürütme yetkisi | Evidence revision vardı; transcript komutu çalıştırma sınırı net değildi | Önceden izinli runner, sandbox/timeout, ayrı execution capability | V24/T14 bekliyor |
| Decision-only onayın etkisi | Impact pending olabilirdi; ready işe etkisi ayrıntısızdı | Pending applicability görünür ve yeni yürütme önerisi bloke | V28/T12/T20 bekliyor |
| Query ve proje reassignment | Proje scope ilkesi vardı; cursor ve binding dönemi ayrımı eksikti | Scope-bound cursor, immutable eski binding provenance, transfer ayrı komut | V25/T05/T18 bekliyor |
| Recovery ve purge | Genel backup/retention vardı | Payload/index/cache/export/backup sınırı, migration ve digest kapıları | V26/T23 bekliyor |
| Mimari görsel anlatım | Üç yüksek seviyeli Mermaid vardı | Bağlam, engine, ER, capture, approval race, impact, state ve restore diyagramları | Mermaid gösterimi doküman kontrolü; uygulama kanıtı değil |
| LLM devri / proje yönetimi | AGENTS ve backlog vardı; kısa rol/otorite/anlama kontrolü yoktu | Handoff soru haritası ve tek sayfalık çalışma düzeni | Bağımsız model deneyi yapılmadı |
| Farklılaşma | Benchmark dersleri vardı; yanlışlanabilir ürün tezi ayrıntısızdı | Rakip bazlı sözleşme + altı test edilebilir hipotez | T03/T24 karşılaştırma bekliyor |

## ADR'lerin yeniden değerlendirilmesi

| ADR | Değerlendirme | İşlem |
|---|---|---|
| 0001 Local store | İlk kullanıcı için makul aday; Cortex/mai-mcp/Beads extend sonucu bunu değiştirebilir | Öneri statüsü korundu; T03 kapısı kaldırılmadı |
| 0002 Event/projection | Tarih/current ayrımı kullanıcı ihtiyacını karşılıyor; privacy purge ve admin değişikliği mutlak immutability vaadini sınırlar | 0007 ile recovery ve replay sözleşmesi eklendi |
| 0003 Adapters | Yüzeye özel capability doğru sınır; MCP tüm konuşmayı yakalama çözümü değil | Capability spike zorunlu kaldı; source/job ack 0007'ye bağlandı |
| 0004 Graph | required_by/dependency ayrımı ve üç değerli mantık gerekli; graph eksiksiz varsayılamaz | Snapshot ve yeni-edge concurrency 0008'e bağlandı |
| 0005 Approval/verification | Manuel PM'yi azaltırken yetkiyi koruyor; UI butonu tek başına güvenlik değil | Server identity, evidence authority, karar sonrası pending etkisi netleştirildi |
| 0006 Routing | Deterministic-first doğru ürün ilkesi; ucuz model kalitesi ve tasarruf henüz kanıtlanmadı | Engine sınırları ve mevcut ölçüm kapısı korundu |
| 0007 Durable processing | Bu incelemede önerildi | T06/T07/T15'te fault injection olmadan accepted/implemented olmaz |
| 0008 Snapshot authority | Bu incelemede önerildi | T12/T13 race, T14 runner sınırı ve T24 false-stale ölçümü gerekir |

## Bilerek hâlâ açık kalanlar

- Gerçek provider/build yetenekleri, izinler ve platform erişimi: T02/T16/T17/T25. Kodda bir event adının bulunması destekli API garantisi değildir.
- Stack/sürüm/DDL/transport mapping ve build/extend: T03/T04. Dokümanda aday mimari bulunması kesin teknoloji seçimi değildir.
- Extraction/evaluation doğruluğu, impact recall, kullanıcı yükü, maliyet ve latency: T01/T03/T24. Başarı hedefleri ölçülmüş sonuç değildir.
- Policy varsayılanları, model bütçesi, encryption/retention/backup ve restore hedefleri: OPEN-07/08/10/12/13. Gerçek veri/ücretli model öncesi çözülmeli.
- Takım yetkileri, çok cihaz conflict çözümü ve commercial boundary: P4. MVP'ye sessizce dağıtık sistem kapsamı eklenmedi.
- Lisans, isim/marka ve public release: owner kararı bekliyor. Private repo güncellemesi bunları kararlaştırmaz.
- Anlamı tartışmalı yeni bir kaynak ortaya çıkarsa kapsam matrisi tekrar gözden geçirilir; “eksiksiz” sözcüğü gelecekteki keşfi kapatmaz.

## Bu teslimin doğrulama kapsamı

`scripts/check_docs.py` yerel bağlantılar, fence dengesi, JSON fixture, scope/task/feature/engine/source referans bütünlüğünü denetler. Bu betik doğal dilin anlamını, Mermaid layout'unu veya ürünü test etmez. Diyagram render kontrolü ve GitHub commit sonrası dosya karşılaştırması teslim sırasında ayrıca yapılır; gerçekleşen sonuç [status](../delivery/status.md) içinde kaydedilir. Ham özel transcript repository'ye eklenmez.

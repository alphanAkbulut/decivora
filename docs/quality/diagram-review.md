# Diyagram tutarlılık incelemesi

**Güncel inventory: 19 belgede 40 Mermaid şeması — T13a local review sequence/storage eklendi, 2026-10-13; önceki38 kaynak değişmedi.** Önceki kayıtlar aşağıda tarihsel doğrulama kapsamıyla korunur; eski sayım veya render sonucu değişen çizim için başarı kanıtı değildir.


**Q15-A / T04 güncellemesi (2026-10-13):** roadmap2, current-direction1 ve decision-map teknik1 kaynağı değişti; toplam38/18 aynı.5 blok ağ kapalı cachedMermaid11.17.2 ile render edildi (niyet bloğu aynı);4 güncel kayıt hash/XML/provenance ile değiştirildi, önceki render kayıtları superseded history'de korundu. P0 ölçümleri açıkken koşullu P1a başlangıcı ve accepted Python/SQLite ayrımı gösterilir; ürün release kanıtı değildir.
## Güncel inventory — 2026-10-13

<!-- diagram-inventory:start -->
| Belge | Mermaid sayısı |
|---|---:|
| [README.md](../../README.md) | 1 |
| [ROADMAP.md](../../ROADMAP.md) | 2 |
| [docs/architecture/connection-and-context.md](../../docs/architecture/connection-and-context.md) | 1 |
| [docs/architecture/data-relationships.md](../../docs/architecture/data-relationships.md) | 3 |
| [docs/architecture/diagrams.md](../../docs/architecture/diagrams.md) | 13 |
| [docs/architecture/execution-and-integrations.md](../../docs/architecture/execution-and-integrations.md) | 3 |
| [docs/architecture/identity-access.md](../../docs/architecture/identity-access.md) | 1 |
| [docs/architecture/logging-audit.md](../../docs/architecture/logging-audit.md) | 1 |
| [docs/architecture/overview.md](../../docs/architecture/overview.md) | 1 |
| [docs/architecture/storage-memory-capacity.md](../../docs/architecture/storage-memory-capacity.md) | 1 |
| [docs/delivery/team-data-plan.md](../../docs/delivery/team-data-plan.md) | 1 |
| [docs/product/decision-map.md](../../docs/product/decision-map.md) | 2 |
| [docs/product/graph-experience.md](../../docs/product/graph-experience.md) | 2 |
| [docs/product/intent-to-reality-gap.md](../../docs/product/intent-to-reality-gap.md) | 2 |
| [docs/product/current-direction.md](../../docs/product/current-direction.md) | 1 |
| [docs/quality/membership-002-result.md](membership-002-result.md) | 1 |
| [docs/quality/receiver-contract.md](receiver-contract.md) | 1 |
| [docs/quality/project-review.md](project-review.md) | 1 |
| [docs/architecture/review-runtime.md](../../docs/architecture/review-runtime.md) | 2 |
<!-- diagram-inventory:end -->

## 2026-10-13 — Q14-A proje ayrımı ve geç açıklama cevabı

- [Yeni kod yolu](project-review.md): global identity/current-access preflight, per-project shape/source result, caller atomic-group, stable clarification ve explicit reply association. Eski bütün-output şema değişmedi.
- Yeni kaynak cached Mermaid11.17.2/bundled headless Chrome ile ağ kapalı render edildi. Son SVG XML/title/desc ve16node/17edge kontrolü geçti; final PNG light/desktop görsel inceleme. İlk çizimde eksik güncel-soru-context dalı ikinci kaynak/render ile eklendi; syntax failure yok. İki yerel render, yeni model/API0.
- Önceki37 source/hash/render kayıtları korunur; tüm38 yeniden render edilmiş değildir. GitHub dark/mobile uyumu, gerçek UI, kalıcı Inbox, IAM/adapter veya model kalite kabulü bu görsel testle doğrulanmaz.

## 2026-10-12 — Receiver yerel doğrulama akışı

- [T03w akışı](receiver-contract.md#p0-doğrulama-akışı): değişmez tam çıktı → bounded shape → kimlik/duplicate → kaynak ilişkisi → yalnız review → ayrı scorer. Ret, temiz abstention/incomplete ve failed_draft/passed_draft farklı; insan kararı/hedef/AC mor kesik gelecek dalı, doğrudan onay veya yürütme oku yok.
- Cached Mermaid11.17.2, mevcut bundled Playwright/Chrome ile ağ kapalı geçici headless sayfada yalnız bu kaynak render edildi. 11 düğüm/12 ok, accessible başlık/açıklama ve PNG görseli kontrol edildi. Önceki36 kaynak hash'i aynı; yeniden render edilmiş gibi sunulmaz. GitHub dark/mobil veya her renderer sürümü bu yerel kontrolle doğrulanmış değildir.
- İlk browser render geçti; ek SVG XML okuması renderer'ın HTML `<br>` serialization'ı nedeniyle başarısız oldu. Aynı kaynak ikinci export'ta browser DOM XMLSerializer ile kaydedildi; XML parse/title/node/edge kontrolü geçti. İlk artifact korundu, schema veya model run başarısızlığı diye sınıflanmadı. Source aynı; iki yerel render ve sıfır model/API çağrısı.
- [Render raporu](diagram-render-results.json) incremental provenance ve exact source/SVG hash taşır. SVG/PNG inceleme çıktıları repo dışı yerel artefaktlar; canonical Mermaid Markdown'dadır. Ürün/runtime/model kalitesi testi değildir.

## 2026-10-12 — MEMBERSHIP-002 şeması GitHub'da doğrulandı

- Önceki file:// önizlemesi tarayıcı URL güvenlik politikasıyla engellendi. Bu engel değiştirilmedi; kullanıcı şemanın doğrulanarak yayımlanmasını istedi. Yeni kaynak private `review-membership-002-diagram-87853c5` inceleme branch'inde hazırlandı; ana branch doğrulama tamamlanana kadar korunuyordu.
- Immutable inceleme ref'i `e491fd09590499c27305ec5519281e50fa330bda`: GitHub Preview'de native Mermaid iframe ve `graphics-document document` SVG çıktı gözlendi. Başlık/açıklama ve 15 düğüm / 16 ok kaynakla karşılaştırıldı; syntax/render hata metni görülmedi. Renderer'ın tam sürümü unknown; yerel cached bundle kullanılmadı.
- Kaynak→sözleşme→tek çıktı→kod kontrolü→dört candidate; bağlı/belirsiz cevap, claim/Evidence ve ayrı fixture guard sonuçları incelendi. Model adayından canonical karar/verification'a doğrudan geçiş çizilmedi. Mavi aday, yeşil gözlenen/fixture, sarı açıklama UX ihtiyacı, mor/kesik ok production adımlarıdır.
- Geniş görünümde başlangıç zinciri ve sonuç dalları görsel kontrol edildi; title/desc ve bütün SVG etiketleri DOM'dan okundu. Dark/desktop doğrulaması; tam mobil, her zoom düzeyinde okunabilirlik veya runtime kabul testi değildir. Şema uzun olduğu için GitHub geniş görünüm/zoom kullanılabilir.
- Source SHA-256 ve yerel SVG snapshot hash'i [render raporuna](diagram-render-results.json) ayrı provenance ile eklendi. Önceki 35 kaynak/render satırı değişmeden kaldı; hepsi bu tur tekrar render edilmiş gösterilmedi. Yeni toplam 36 kaynak /16 belge; model raw/rubric değişmedi.
- İnceleme branch'i yalnız çizim kontrolü hazırlığıdır; repository kapsam/enventory kontrolleri tamamlanmış ana commit'te çalıştırılır. Şema doğrulaması semantic model, üretim yetki/target/AC doğruluğu değildir.

## 2026-10-11 — Güncel görsel ve semantik yeniden inceleme

**Başlangıç ref:** `58fc6832f7de4a0d605e2c9887d61dde1ad166ca`. Önceki render sonucu bugünkü stillerin kanıtı sayılmadı. Bütün 34 önceki Mermaid kaynakları güncel domain/runtime/IC ve owner statüleriyle yeniden karşılaştırıldı; hepsine renk profili ve accessible başlık/açıklama eklendi. Karar haritası iki görünüm oldu: toplam **35 kaynak / 15 belge**, 23 flowchart, 4 ER, 7 sequence, 1 state machine.

| Belge / blok | İçerik incelemesi ve güncelleme |
|---|---|
| README / 1 | Source → proposal → yetkili onay → application observation → ayrı AC ayrımı; okunur dikey akış, açıklayıcı oklar, SVG fallback, aşama tablosu ve kısa giriş |
| ROADMAP / 1–2 | Native/extend/build/stop owner kapıları ve P0/P1/P2/P3/P4 korunur; gelecekteki fazlar mor, tamamlanmış faz gibi görünmez |
| Connection/context / 1 | Capture ayrı, MCP query/proposal ayrı; model opsiyonel ve izin/bütçe kontrollü |
| DB relationships / 1–3 | Kimlik/binding/receipt, task/run/AC/DoD/evidence ve application target kardinaliteleri çapraz okundu; fiziksel DB implementasyonu denmez |
| Atlas / 1–13 | Güven sınırı, 10 engine, ER, source/approval sequence, AND/OR, state, restore, agent, soru, blocker, admin, incident incelendi. Engine budget kontrolü E3/E5/E10'a da görünür eklendi; source key alanları belirginleşti |
| Atlas / soru akışı | AnswerRecord → question/option revision/source association → authority kontrolü ayrıldı; geç/belirsiz cevap pending kalır |
| Execution / 1–3 | Numara ve açıklama bandı; boş AC otomatik pass değil, parse error no-op değil, unknown usage korunur. Callback DB receipt → adapter → provider ack olarak düzeltildi |
| Identity / 1 | Ayrı insan/agent kimliği, grant ve commit/egress'te güncel kontrol; renk yetki genişletmez |
| Logging/audit / 1 | Yerel atomik commit ile ayrı dış delivery ayrımı; dispatch policy yerine açık Outbox worker üzerinden gösterildi |
| Overview / 1 | Canonical command/query ve selected target read-back; observation completion yerine geçmez |
| Storage / 1 | 1C izinli arşiv, geçici payload/context, purge ve intake tavanı; sınırsız saklama veya replay dış etki iddiası yok |
| Team/data / 1 | Tek owner/çok-agent ilk kanıt; P4 merkezi ekip gate'i gelecekte |
| Current direction / 1 | T01/T02/T03a-b-c; izinli deney ve owner yatırım kararı henüz yapılmış gösterilmez |
| Decision map / 1–2 | Tabloda olup görselde eksik DEC-10–14 dahil edildi; DEC-01–20 tamamı niyet/öneri ayrımıyla okunur. Oklar task dependency değil düşünce/öneri ilişkisi |
| Graph experience / 1–2 | Cancelled/obsolete/superseded/aktif OR gerekçesi ayrıldı; ilişkiler silinmez, unmet requirement ve stale preview görünür |
| Intent/reality / 1–2 | İnsan seçimi, artifact üretimi, exact target observation, unknown/partial ve AC değerlendirmesi farklı; yeni host brief delivery conditional kalır |

### Gerçek render kontrolü

- Ağ istekleri kapalı geçici Chrome/Playwright ile cached **Mermaid 11.17.2** bundle kullanıldı; yeni paket/dependency veya model çağrısı yapılmadı. Sabit sürüm ve bundle hash [JSON raporunda](diagram-render-results.json).
- Son çalıştırmada **35/35 kaynak render edildi, parser hatası 0**; bütün çıktılarda title/description metadata vardı. Kaynak hash'leri current Markdown bloklarıyla eşleştirildi.
- İlk denemede eklenen dört sequence açıklamasında noktalı virgül parser hatası verdi; daha sonra usage mesajındaki aynı ayırıcı da düzeltildi. Sonucun başarısız denemeleri gizleyip ilk geçişmiş gibi anlatılmaması için burada kayıtlıdır.
- 35 PNG overview/contact sheet olarak görsel tarandı. README, kabul edilmiş karar haritası, hedef uygulama ER ve task-result sequence ayrıca tam görüntüde incelendi. Bu her etikette ölçülmüş overlap/kontrast veya tüm ekran boyutlarında layout testi değildir.
- Sabit açık palette/yerel beyaz sayfa kontrol edildi; SVG'nin iç canvas'ı bazı renderer'larda transparent kalabilir. README export'una açık beyaz background verildi. GitHub dark/mobil ve renderer version uyumu bu local kontrolle kesinleşmiş değildir.
- SVG fallback kaynak ve export hash'i raporda; hand-edited ikinci truth değil. Docs checker rapor coverage/source hash/SVG hash tutarlılığını da kontrol eder; renderer'ı kendisi çalıştırmaz.
- UI/runtime, veri tabanı migration, adapter erişimi, model doğruluğu, SLO veya test oracle başarısı denemesi yapılmadı.

[Ortak sözlük ve hedefli Graphiti/Langfuse sunum benchmark'ı](visual-documentation.md) renk/ok/callout anlamlarını ve mevcut klasör yapısını neden koruduğumuzu açıklar. Logo/badge/source code kopyalanmadı. Yeni public/license/stack kararı alınmadı.

## Önceki revizyonun içerik ve render kaydı

Aşağıdaki 34 sayımı ve GitHub render ref'i bu görsel güncellemeden önceki durumdur.

İçerik incelemesi tüm 34 kaynağı kapsar. Bu revizyonda README (1), roadmap (2), overview (1), atlas bağlam/engine (2) ve decision map (1) olmak üzere **7 mevcut blok güncellendi**. Güncel yönün yatırım akışı ve ER-03 **2 yeni bloktur**; önceki GAP akışları (2) inventory'ye dahil edildi. 25 eski blok kaynak düzeyinde değişmedi; yalnız tarihler veya sürüm görünümü için yeniden çizilmedi.

Onay snapshot/AND-OR/iptal/replay, source/target yetki sınırı, log/storage ve ekip/admin akışları korundu. Atlas ER'si ER-03 ile tamamlanır; bütün relation alanlarını her diagramda tekrar etmek gerekmez. Source alımı, application assessment ve AC/DoD completion aynı durum değildir. İlk prototip tam atlası çalıştırmış sayılmaz.

**Bu revizyonun render kontrolü:** `aaf9cbef1c5a387848a6d75975482b9d09ae9e4a` ref'inde 15 belgedeki 34 Mermaid çıktısının tamamı GitHub Preview üzerinden kontrol edildi. Render edilmiş iframe etiketleri/SVG çıktıları okundu; parse/syntax/render hata mesajı bulunmadı. Güncel roadmap'in faz/yatırım çizimi ayrıca açılıp ekran görüntüsüyle incelendi. Bu kontrol bütün ekran boyutlarında layout, ürün UI veya runtime testi değildir; aşağıdaki önceki sonuçlara dayanmaz.

**2026-10-10.** İnceleme öncesinde 11 belgede 20 Mermaid diyagramı vardı. Hepsi son kararlarla içerik düzeyinde karşılaştırıldı; tamamı zaten günceldi denemez. Aşağıdaki düzeltmelerle 25 diyagram oldu. Şemalar tasarımdır; runtime, tam UI veya benchmark kanıtı değildir.

Referanslar: DEC-15/1C, DEC-16 öneri statüsü, DEC-17 ve yöntem ayrımı; Q04/05 graph/profil tercihi; run/task ve ASK yetki/delivery ayrımı; tenant/ACL, token policy, yeni admin/operasyon isteği. Diyagram okları tek başına yetki veya uygulanmış capability göstermez.

| Dosya | Diyagram sayısı | İnceleme ve sonuç |
|---|---:|---|
| [README](../../README.md) | 1 | Agent çalışma olayları ve task doğrulaması ayrıldı; atlas indeksi güncellendi |
| [Roadmap](../../ROADMAP.md) | 2 | P1b minimal yerel yönetim, P4 ekip/operasyon ayrımı eklendi; faz ve kanıt kapıları korundu |
| [Mimari atlas](../architecture/diagrams.md) | 13 | İlk 8 gözden geçirildi: kaynak/engine, tenant kapsamlı ER, budget/izin kontrollü worker güncellendi. Snapshot onayı, AND/OR, state machine ve replay geçerli kaldı. Run, soru, blocker, admin ve incident için 5 şema eklendi |
| [Genel mimari](../architecture/overview.md) | 1 | MCP query/proposal yanlışlıkla capture ingress'e bağlıydı; ortak policy ve yetkili read yolu düzeltildi |
| [Bağlantı/context](../architecture/connection-and-context.md) | 1 | Capture, MCP ve insan UI ayrımı geçerli; model okları bütçe/izin sözleşmesiyle okunur, değiştirilmedi |
| [Kimlik/yetki](../architecture/identity-access.md) | 1 | İnsan üyelik/grant ve agent run yetki şeması geçerli; yeni admin atlasıyla tamamlandı |
| [Log/audit](../architecture/logging-audit.md) | 1 | Yerel atomik audit ve dış delivery ayrımı geçerli; incident ayrı atlas şemasında |
| [Depolama/hafıza](../architecture/storage-memory-capacity.md) | 1 | Genel payload TTL oku 1C arşivini yanlış kapsayabilirdi; geçici payload ve izinli arşiv ayrıldı, kapasitede sessiz silme yerine intake durması gösterildi |
| [Ekip/veri planı](../delivery/team-data-plan.md) | 1 | Tek insan/çok-agent ve yerel yönetim; P4 operasyon/kota kapıları yansıtıldı |
| [Karar haritası](../product/decision-map.md) | 1 | Eksik DEC-15/16/17 eklendi; kabul/proposed ayrımı, yöntemden bağımsız öncelik ve admin önerisi açık |
| [Graph deneyimi](../product/graph-experience.md) | 2 | İptal/ended ilişkilerin tarihçesi, başka OR gerekçesi, insan review ve stale preview güncel; değiştirilmedi |

## Doğrulama kapsamı

- Bütün Mermaid kaynakları ve ilgili metin sözleşmeleri okundu; inventory sayımıyla 11 dosya / 25 diyagram doğrulandı.
- `python3 scripts/check_docs.py` yerel bağlantı, fence, JSON ve kapsam/görev/AC bütünlüğünü kontrol eder; Mermaid parser veya görsel render testi değildir.
- İçerik commit'i `10bbb0f3a1df5e2dec599f01773372a3a9fb2642` GitHub'a kaydedildi; değişen 16 dosya aynı ref'ten geri okunup yerel içerikle birebir karşılaştırıldı.
- GitHub Preview tarayıcı kontrolünde 11 belgedeki 25 Mermaid çıktısının tamamının iframe içindeki render edilmiş etiketleri okundu; parse/syntax/render hata mesajı bulunmadı. Atlasın yönetim şeması ayrıca ekran görüntüsüyle incelendi. Bu, tüm ekran boyutlarında görsel UX testi veya ürün UI testi değildir.
- Son doküman kontrolü: 64 Markdown, 417 yerel bağlantı; 32 scope, 30 ana görev, 14 MVP kriteri korundu. ADM-01–10 kabul tanımları ayrıca sayıldı; henüz runtime'da çalıştırılmadı.
- ADM-01–10 ve mevcut ASK/AGT/FLOW/MU senaryoları uygulama sırasında çalıştırılacak; bu inceleme onları passed yapmaz.

## Sequence ve ER genişlemesi — 2026-10-10

| Yeni belge | Şema sayısı | Kapsam |
|---|---:|---|
| [Tetikleme ve iletişim](../architecture/execution-and-integrations.md) | 3 sequence | Task sonucu/verification, koşullu LLM ve insan kararı, dış API teslimi/unknown/callback |
| [DB ilişkileri](../architecture/data-relationships.md) | 2 ER | Kaynak/binding/izin makbuzu; task/run/AC/DoD/evidence ilişkileri |

Önceki 25 Mermaid kaynağı bu genişlemede değiştirilmedi. Yeni belgeler TRG-01–12, iletişim matrisi, deney aralıkları ve veri bütünlüğü sözleşmeleriyle çapraz okundu. Yeni toplam 30; bunun 6'sı sequence, 3'ü ER. SEQ-01–08 ve DBR-01–06 planlı runtime kabulüdür; çizim testi bunları passed yapmaz.

Doğrulama: ilk GitHub render denemesinde üç sequence'in mesaj noktalı virgülleri parse hatası üretti; mesaj ayırıcıları düzeltildi. `5a6e24fdb2e00102fb282b49c4bd3502890df59a` içeriğinde üç sequence ve iki ER'nin render edilmiş iframe etiketleri tarayıcıdan okundu; syntax/render hatası kalmadı. Task sonucu sequence'i ayrıca ekran görüntüsüyle incelendi. Önceki 25 için önceki render kanıtı ve kaynak değişmezliği geçerlidir; bu tur bütün ekran boyutlarında görsel test yapılmadı.

Değişen 13 dosya GitHub'dan aynı ref ile geri okunup yerel içerikle eşleşti. Doküman kontrolü geçti: 66 Markdown / 461 yerel bağlantı; 32 scope / 30 ana görev / 14 MVP kriteri korundu. 8 SEQ ve 6 DBR kabul ID'si tekil/sıralı kontrol edildi; bunlar çalışan API, DB migration veya scheduler test sonucu değildir.

## Bakım uygulaması

Karar değişikliği yapan görev ilgili metin, diyagram, backlog ve acceptance etkisini birlikte değerlendirir. Değişmeyen diyagramı sırf tarih yenilemek için çizme. Etkilenen graph/node/edge etiketleri, phase ve accepted/proposed statüsü kontrol edilir; Mermaid render sonucu ayrı raporlanır. Bütün diyagramların sonsuza kadar güncel kalacağı garantisi verilmez.

**Checker regresyon kontrolü:** geçici kopyada README Mermaid label'ı değiştirildiğinde render source hash uyumsuzluğu; SVG byte'ı değiştirildiğinde fallback hash uyumsuzluğu beklenen hata ile reddedildi. Asıl kaynaklar değiştirilmedi. Pozitif docs kontrolü 88 Markdown/931 yerel bağlantı ve 35 Mermaid inventory ile geçti. Recorded render doğrulaması canlı renderer veya ürün testi yerine geçmez.

## T13a runtime görsel kontrolü — 2026-10-13

İki yeni sequence/storage kaynak cached11.17.2, ayrı headless Chrome, dış ağ kapalı render edildi; XML/title/description/hash ve masaüstü görseller kontrol edildi. Storage dikey yerleşime alındı. [Şema ve SVG bağlantıları](../architecture/review-runtime.md), [runtime testlerinden ayrı sınırlar](review-kernel.md). Eski38 kaynak değişmedi ve bu tur tekrar render edilmiş sayılmaz.40source/19belge; ürün UI/mobil kabulü değildir.

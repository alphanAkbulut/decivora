# WrongStack: hedefli kaynak incelemesi ve yeniden kullanım planı

**2026-10-11 — statik inceleme; runtime benchmark değil.** Repository: [WrongStack/WrongStack](https://github.com/WrongStack/WrongStack). Sabit commit: `5234c15b05fe18857d0119eabd3b8a8f910ecc66`. Root manifest bu ref'te `1.0.37`, Node `>=22.19.0`, Bun `>=1.4.3` bildiriyor. Bunlar upstream gereksinimleri; Decivora'nın kabul edilmiş stack'i değildir. Hareketli README/sürüm duyurusu yerine bu ref kullanıldı.

**Sonuç:** WrongStack ciddi bir native/extend alternatifi ve yararlı bileşen kaynağıdır. Önce küçük deterministik parçaları ve sınır sözleşmelerini değerlendirmek önerilir; bütün coding-agent platformunu fork etmek için gerekçe oluşmadı. Decivora'ya bu turda upstream runtime kodu, prompt, asset veya dependency alınmadı. Mevcut repo tasarım aşamasında; kaynakları kullanılmayan bir klasöre koymak çalışan entegrasyon sayılmayacaktı.

## Kanıt seviyesi ve sınır

- **D:** Belge/manifest beyanı. **S:** Belirtilen kaynak veya test tanımı statik okundu. S, V (çalıştırılmış test) değildir; mevcut benchmark D/V/U/O sözlüğüne V eklenmedi.
- Git tree eksiksiz döndü; hedefli dosya/bölümler seçildi. Repo geneli audit, bütün bağımlılıkların lisans taraması veya tüm çağrı zincirlerinin analizi yapılmadı.
- SAGE, verification, MCP policy, requirement coverage, learning/pattern, compaction, budget ve bir UI bileşeni incelendi. Bazı büyük dosyalarda ilgili bölümler okundu; bunların tamamının denetlendiği iddia edilmez.
- Upstream kurulmadı, script/test/agent çalıştırılmadı; provider hesabı veya gerçek proje bağlanmadı. Performans, doğruluk, maliyet ve güvenlik sonuçları `not_run`.
- Test kaynaklarının varlığı ve beklentileri görüldü; bu ref'te CI'nın veya yerel testlerin geçtiği teyit edilmedi.

## Ürün örtüşmesi: kolaylık ve rekabet

| WrongStack'te okunan alan | Kanıt | Decivora açısından sonuç |
|---|---|---|
| SAGE memory; anchor, applicability, revision ve bounded hints | S | Kalıcı/güncel bilgi ve kaynaklı context tek başına farkımız olamaz |
| Requirement intake → spec/task; deterministic lifecycle/coverage | S | Gereksinim→küçük işler ve onaylı scope takibi mevcut alternatiflerde var |
| Completion gate, backing evidence ve DoD dashboard | S | Claim/verified ayrımı ve kanıt görünümü özgünlük iddiası olamaz |
| Director, subagent budget, mailbox, farklı arayüzler | D + seçili budget/protocol/UI S | Ana ajan/alt ajan senaryosu uygulanabilir referans; Decivora'nın kendi orchestrator'u olması şart değil |
| MCP'de read-only/proposal-only sınırı | S | WrongStack dışındaki agent'larla da ilişki kurmayı hedefliyor; “yalnız kendi ajanı” demek yanlış |
| Karar değişimi→AND/OR/unknown gerekçe etkisi; gerçek insan seçimi→exact hedef uygulama→AC zinciri | Bu incelemede uçtan uca test yok | Rakipte yok denemez. H1/H4/H6 ve GAP/RES oracle'ında native/config/extension sonucu ölçülecek |

Decivora'nın hedefi farklı kaynaklarda **konuşulan, seçilen, istenen, uygulanan ve doğrulananı** ayırarak kararın niçin değiştiğini ve hangi işin artık gereksiz olduğunu açıklamak. WrongStack'in incelenen kodu bu hedefin bazı temel parçalarıyla örtüşüyor. Değer iddiamız bu parçaların varlığı değil, kullanıcıya daha az yönetim işiyle birlikte sağlanan sonuçtur. [Farklılaşma](../product/differentiation.md), [güncel yön](../product/current-direction.md) ve [GAP](../product/intent-to-reality-gap.md) otoritedir.

## İşimizi kolaylaştırabilecek parçalar

| Aday / kaynak | Gerçekte okunan davranış | Önerilen alım biçimi ve Decivora görevi | Uyum için gereken |
|---|---|---|---|
| [EvidenceValidator](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/kanban/src/verification/evidence-validator.ts) | Agent/council sonucunda ref sayısı/türü ve aşırı belirsiz özetleri kontrol eder | Küçük kaynak adaptasyonu adayı; T14, T03d | Bizim Evidence schema'sı, locale ve trusted observation zinciri. Ref metni tek başına doğru kanıt değildir |
| [Requirement coverage / DAG integrity](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sdd/src/requirement-coverage.ts) | Eksik/bilinmeyen requirement mapping, yanlış spec, dangling/self/cycle dependency kontrolü | Saf deterministik algoritma adaptasyonu adayı; T11/T15 | Bir task'ın çok requirement karşılaması; aktif spec revision; execution DAG ile tarihsel/gerekçe graph'ını ayır |
| [Validity schema](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage/src/shared/memory-validity.ts) | Koşul metni + sınırlı literal source checks; relative path ve boyut kontrolleri | Küçük validator/schema örüntüsü; T09/T10 | Koşul cümlesi doğru/false diye varsayılmaz; AND/OR/unknown bizim domain kuralına bağlanır |
| [Anchor verification](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage/src/anchors/verify.ts) | File/hash/symbol/git/command availability, stale/unknown; Git blob hashlerini batch alır | Önce örüntü; T14/target adapter | Root/symlink/okuma hatası/izin ayrımı ve exact target ref. Command availability, command çalıştı/test geçti demek değildir |
| [Bounded memory hints](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage/src/retrieval/format.ts) | Revision/tarih/koşul metadata'sı, escaped data, gösterilen memory IDs; tam kayıt satırları | Formatter örüntüsü; T09/T18 | İlk kayıt limitten büyükse upstream bütün satırı geçiriyor. Biz hard cap'te kısa envelope+ref+coverage döndürmeliyiz |
| [MCP policy](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage-mcp/src/policy.ts) | Varsayılan safe/auto görünür; proposal modunda list/propose, review eylemleri validate ile engellenir | Policy wrapper örüntüsü/küçük adaptasyon; T18 | Tool visibility authz değildir. Per-call grant, trusted reviewer, revocation ve server-side action check |
| [On-demand tool schemas](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/tools/src/tool-search.ts) | Sonuç sınırı; ilk beş sonuçta tam schema, diğerlerinde kısa tanım ve omitted işareti | T18/T21'de geniş tool kataloğu oluşursa deney | Beş-tool MVP'de yeni search aracı gereksiz maliyet olabilir; ek round-trip dahil toplam tüketim ve keşif başarısı ölç |
| [Vocabulary routing](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/agents/project-agent-skill-routing.ts) + [LEARNED parser](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/agents/project-agent-capture.ts) | İşaretli blok çıkarımı; explicit skill tag önceliği; kelimeyle candidate skill seçimi, eşleşmezse role-level | Sözlük/pattern önerimize kaynak; T09e/T24o | Learning routing task completion değildir. TR/EN/quote/negation guard, candidate-only ve unmatched yolu korunur |
| [Tool-history compaction](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/execution/compaction-elision.ts) | Eski tool I/O'yu digest/ref'e indirir; tool_use/result ilişkisini ve error flag'i koruyan yollar var | T18 bounded context / resume için örüntü | Biz bağımsız host'un geçmişini değiştiremeyiz. Yalnız kendi paketimizde; kaynak arşivi silinmez; kalite/hard cap testi |
| [Mailbox IPC protocol](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/mailbox-project-server-protocol.ts) + [owner mimarisi](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/docs/mailbox-architecture.md) | Tek owner/project IPC + SQLite belge modeli; source'ta protocol v4 ve request/shutdown token alanları | Önce mimari ders; T04/T06/T18 ve daha sonra ekip keşfi | Owner, actor ve capability ayrı; mevcut event-log replay/retention kurallarımızla otomatik uyum varsayma |
| [SubagentBudget](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/subagent-budget.ts) | Child limitleri, event tabanlı extension/stop, cevapsız negotiation'da stop; cooperative finish | T21 bütçe/cancellation tasarımı için örüntü | Bizim atomik parent/dönem reservation ve unknown usage ledger yerine geçmez; child extension üst bütçeyi açamaz |
| [Verification dashboard](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/webui/src/components/KanbanVerificationDashboard.tsx) | Verified/failed/needs-human/incomplete/unverified ve eksik kanıt/alt göreve bölme satırından task'a geçiş | Özgün UI akışı için referans; T19/T20 | React, app translation, selector, component/style bağımlılıkları var. Ekran/asset kopyası veya çalışmış UX testi değil |

En kolay kaynak adaptasyonu adayları **EvidenceValidator**, **requirement coverage** ve **validity validator**. Importları büyük ölçüde tip/domain bağımlılıkları taşır; uygun stack ve bizim sözleşmemiz seçilirse küçük modüle ayrılabilirler. SAGE paketini komple almak kolay değildir: manifest `@wrongstack/core`, `persistence`, `primitives` bağımlılıkları bildirir. SAGE MCP ayrıca `core/mcp/sage` ister. Kanban `persistence/primitives` kullanır. Boyut, build ve transitif lisans maliyeti henüz hesaplanmadı.

## Körlemesine taşınmaması gereken semantik farklar

1. **EvidenceValidator kaynakları kontrol etmiyor.** Dosya/test/diff referanslarının biçimini değerlendiriyor; hash/ref/issuer/freshness/erişim/gerçek test gözlemi ayrıca gerekebilir. Uzun ama uydurulmuş özet geçebilir; bütün sahte kanıtları yakalar diye sunma.
2. **Completion gate policy farklı.** [Kaynakta](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/kanban/src/verification/completion-gate.ts) legacy soft/off yolları var; soft failure durumunda completed yazılabilen yol mevcut. Managed davranışı ayrıca ayrılıyor. Decivora'nın doğrulanmış completion sözleşmesine bu varsayılanları doğrudan taşıma.
3. **Memory stale ≠ task obsolete.** Dosya hash'i değişmesi bilgi/kanıtı stale yapabilir; task'ın başka geçerli gerekçesi kalıyorsa iptal edilemez. Source literal bulunması semantik doğruluk kanıtı değildir.
4. **Anchor probe hata sınıflaması uyarlanmalı.** Seçili kaynakta stat/realpath hataları stale sonucuna toplanan bir yol var; bizim permission/offline/read-error durumumuz missing kanıtı sayılmamalı. Bu statik semantik farktır, yeniden üretilmiş upstream kusur değildir.
5. **“İlk kayıt tam gelsin” hard limit değildir.** Cümleyi yarıda kesmemek yararlı; aşırı büyük kayıtta kendi hard context cap'imiz, truncation ve ref üzerinden ayrıntı getirme korunmalı.
6. **Learning score nedensel başarı kanıtı değil.** [Kaynak](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/agents/project-agent-learning-structured.ts) applied/wins yanında skipped/control ve lift hesaplar; [host](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/cli/src/fleet/host-learning.ts) cancellation'ı failure saymaz, yeni öğrenimi aynı task'ın başarısıyla ödüllendirmemeye çalışır. Bunlar iyi ölçüm dersleri; gözlemsel attribution randomized causal evaluation yerine geçmez.
7. **Belge/source drift görülüyor.** Mailbox belgesi v3 derken sabit source protocol v4 bildiriyor. README/archived plans, mevcut source ve gerçek çalışma sonucu aynı kanıt değildir. Decivora için contract/schema/ref tutarlılık kontrolü örneğidir; bütün upstream doc'un yanlış olduğu sonucu yok.
8. **Yazılabilir MCP ve öğrenilmiş talimatlar bizim onay modelimiz değil.** Host confirm UX'ine dayanmak güvenilir insan kararı zincirinin tamamı değildir. Agent'ın LEARNED metni canonical policy veya insan approval'a dönüştürülemez. Metin fences tek başına injection'ı kesin önlemez.
9. **Mailbox retention domain audit değildir.** Upstream mesaj TTL/compaction modeli, bizim kabul edilmiş domain geçmişimizi aynı biçimde temizleme yetkisi vermez; receipt/job/transient payload/permanent record ayrımı korunur.

## Üç olası kullanım yolu

| Yol | Ne zaman mantıklı? | Karar kapısı |
|---|---|---|
| WrongStack'i olduğu gibi kullan / yapılandır | Native akış GAP/RES/H1 ihtiyaçlarını kabul edilebilir yönetim yüküyle karşılıyorsa | T03b aynı oracle ve kapsam; sonuç olmadan “yeterli” denmez |
| WrongStack/SAGE üzerinde extension veya izinli source adapter | Memory/review temelini reuse edip eksik domain sözleşmesini sınırlı eforla tamamlamak mümkünse | Source event coverage, authz, incremental capture, export/recovery; event log'un otoritesi açık |
| Bağımsız Decivora + küçük reuse parçaları | Karar-aware domain/platform bağımsızlığının ölçülen değeri entegrasyon maliyetini aşarsa | T03c owner seçimi; T04 stack/lisans inventory; tek modül/PR |

Bu yollar birbirini otomatik dışlamaz: ayrı Decivora, ileride WrongStack'ten gözlem alabilir. Ancak çalışan adapter/MCP interoperability bugün yok. WrongStack kendi agent platformunu işletir; Decivora'nın ilk amacı mevcut agent/chat çalışmasını izlemek ve hafızayı/karar etkisini sunmaktır. Yeni orchestration engine, takım modu veya MVP kapsam genişlemesi kabul edilmedi.

## Lisans ve alım kaydı

[Gerçek LICENSE](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/LICENSE) **MIT**, telif bildirimi **Copyright (c) 2026 ECOSTACK TECHNOLOGY OÜ**. README'deki genel “contributors” ifadesi yerine gerçek notice esas alınır. Metin kodun kullanımı/değiştirilmesi/dağıtılması/ticari kullanımına izin verir; kopyalarda veya substantial portion'da telif ve izin metni korunmalıdır. Bu upstream lisans okumasıdır; seçilecek bütün bileşenlerin/transitif paketlerin uyumu henüz değerlendirilmedi.

Alım öncesi: immutable ref + dosya + dependency listesi + license/notice + değişiklik gerekçesi + hedef modül + test kaydı. Alımda tam ilgili MIT metni ve copyright korunur; THIRD_PARTY_NOTICES gerekli kapsamla hazırlanır. Sırf benchmark okumak kod dağıtımı değildir; bu tur boş bir notice dosyası açılmadı. Logo/marka/asset hakkı veya bütün provider auth yöntemlerinin uygunluğu MIT'den çıkarılmaz. Decivora'nın kendi lisansı hâlâ owner kararıdır. [Alım kapısı](../governance/licensing.md).

## Küçük uygulanabilir dilimler ve kabul

**T03d — PROPOSED / P0**, T03a yöntem + T01 corpus + gerekli çalıştırma/LLM izinlerine bağlı. Ana T03'ü bitmiş yapmaz. İlk sıra aşağıdaki gibidir; sayısal efor/tasarruf taahhüdü yok.

1. **WS-R1: Native/extension fizibilite.** Sabit ref/kurulum ve sadece sentetik kaynak seç. GAP/RES/H1 senaryolarını native/config/custom/unknown sınıflandır. Kurulamaz veya yetki yoksa not_run; unavailable uydurma.
2. **WS-R2: Evidence validator mikro-deneyi.** Stack kararı sonrası yalnız validator+gerekli tip/testleri uyarlama ya da özgün karşılığını yazma seçeneklerini kıyasla. Fake refs/uzun uydurma summary/TR-EN/stale revision/issuer/ref testleri. “Şema geçerli” verified completion üretmez.
3. **WS-R3: Requirement coverage mikro-deneyi.** Missing/unknown/spec mismatch/dangling/cycle + N:M/OR/ended edges. Sadece executable depends_on altgraph DAG kısıtı; bütün karar/tarih graph'ına cycle yasağı koyma.
4. **WS-R4: Context ve pattern mikro-deneyi.** Structured-first, lexical candidate, unmatched fallback; schema exposure/delta/whole-record packing. Yeniden okumalar, ek tool round-trip, çıktı, fallback ve insan review dahil toplam maliyet/kalite baseline'ı.
5. **WS-R5: Karar.** Native kullan / extension / seçilmiş küçük code reuse / özgün build / ek deney seçeneklerinin bakım, bağımlılık, göç ve kullanıcı emeğini raporla. Owner T03c'de seçer; build öncesi kaynak klasörüne bağımsız code dump yok.

| Planlı senaryo | Kabul / yanlış sayılacak sonuç |
|---|---|
| WS-01 False done ve fake backing refs | Reported claim gerçek observation yerine geçmez; ref'li uydurma sonuç verified olmaz |
| WS-02 Kaynak değişimi ve inaccessible hedef | Hash değişimi stale; yetkisiz/offline hedef unknown; otomatik task iptali yok |
| WS-03 İki gerekçeden biri superseded | OR kalan iş korunur; AND etkisi açıklanır; unknown review |
| WS-04 Eksik requirement / N:M / cycle | Omitted requirement görünür; execution cycle reddedilir; historical link yanlış silinmez |
| WS-05 Oversized / malicious / çok dilli context | Hard cap, source ref, revision, data boundary ve eksik coverage korunur |
| WS-06 MCP action/payload spoof ve revoked grant | Schema bypass review/approval üretmez; actor/origin metni authority olmaz |
| WS-07 Child retry/extension ve belirsiz usage | Toplam tavan/rezervasyon bypass yok; unavailable usage sıfıra çevrilmez |
| WS-08 Kullanıcıya dönüş | Eksik kanıt/review/stale bilgiden kaynağa/AC'ye gidilir; manuel yönetim süresi ölçülür |

**Tümü not_run.** Aynı sentetik fixture ve ref'te native/config/extension maliyeti ayrı; unsupported/unknown yüzey coverage'ı görünür. Karşılaştırma modelleri/bütçesi Q03'te izinli olmalı. İlk uygulamalı iş hâlâ T01.

## İncelenen test ve tamamlayıcı kaynaklar

Test tanımları statik okundu: [EvidenceValidator](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/kanban/tests/verification/evidence-validator.test.ts), [coverage/DAG](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sdd/tests/requirement-coverage.test.ts), [conditional validity](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage/tests/memory-validity.test.ts), [MCP policy bypass](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage-mcp/tests/policy.test.ts), [tool pair/Unicode truncation](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/tests/execution/compaction-truncation-integrity.test.ts), [budget heartbeat](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/tests/coordination/subagent-budget-edges.test.ts).

Diğer okunan kaynaklar: [SAGE retrieval ownership](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/docs/sage/retrieval.md), [revision/anchor guarded verify update](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage/src/sqlite-store-verify.ts), [learning cooldown/policy](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/agents/project-agent-learning-policy.ts), [lexical similarity](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/agents/project-agent-learning-entries.ts), [Director belgesi, seçili bölümler](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/docs/director-architecture.md), [root manifest](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/package.json), [SAGE manifest](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage/package.json), [Kanban manifest](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/kanban/package.json), [MCP manifest](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/sage-mcp/package.json). Source kontrollü bulgu, tüm testlerin veya upstream beyanların onayı değildir.

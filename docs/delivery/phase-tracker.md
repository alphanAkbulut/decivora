# Faz bazlı proje ağacı ve takip görünümü

**2026-10-11 — P0 / ürün uygulaması başlamadı.** MVP, P2 ve P3 ayrı bölümlerdedir; tek güncel dosya tutulur. Bu belge mevcut backlog'un gezinme ve takip görünümüdür, yeni scope/bağımsız görev listesi değildir.

**Otorite:** İşin tanımı, ana/alt görev, bağımlılık ve kabul kriterleri [backlog](backlog.md) ve bağlı [ekip/veri planında](team-data-plan.md); gerçekleşen ilerleme/kanıt [status](status.md); ürün çıkış sınırı [MVP](../product/mvp.md) ve [roadmap](../../ROADMAP.md) içindedir. Aşağıdaki 30 ana görev satırı backlog'dan türetilmiştir; doküman kontrolü ID/faz/durum/başlık/ön koşul eşleşmesini denetler. Bunları bağımsız güncelleme.

## Proje ağacı

```text
Decivora
├── P0 — İlk değer ve yatırım doğrulaması [şu an]
│   ├── T01: corpus, oracle ve karşılaştırma protokolü
│   ├── T02: kaynak + hedef erişim fizibilitesi
│   └── T03a → T03b → T03c: yöntem → yetkili deney → yatırım kararı
├── MVP yolu [bağımsız build seçilirse]
│   ├── P1a — Teknik çekirdek [T04–T15]
│   │   ├── Runtime, proje/kimlik, kalıcı alım, event log, policy
│   │   ├── Extraction, reconciliation ve karar bağımlılık grafiği
│   │   └── Impact, insan onayı, kanıt/uygulama ayrımı, teknik kapı
│   └── P1b — Kullanılabilir yerel MVP [T16–T24]
│       ├── İki coding adapter ve minimal MCP
│       ├── Inbox, Board, Graph, Timeline ve devam bağlamı
│       ├── Token/limit görünürlüğü ve temel yerel yönetim
│       └── Import, backup/restore ve kullanıcı kabul pilotu
├── P2 — Süreklilik ve gelişmiş kalite [T25–T27]
│   ├── Chat/cross-provider kaynak fizibilitesi
│   ├── Gelişmiş uzlaştırma/impact ve orphan incelemesi
│   └── GitHub read-only evidence ve host panel deneyi
├── P3 — Ekonomi, kontrollü dış yazım ve release hazırlığı [T28–T29]
│   ├── Maliyet/kalite kıyası ve routing optimizasyonu
│   ├── Ayrı GitHub / Linear / Jira connector dilimleri
│   └── Kurulum, lisans/isim, sentetik demo ve release kapıları
└── P4 — Ekip/cloud/ticari sınırlar [T30 → C01–C06]
    └── Talep, merkezi veri, davet/roller, sync ve ekip işletimi
```

Bu ağaç ürün teslim ağacıdır; çalışan kaynak kodu dizinleri değildir. T03c native/extension/ek deney/durdur sonucunu da seçebilir; o durumda bağımsız T04–T30 yolu otomatik başlamaz.

## P0 — Başlangıç kapısı

| ID | Faz | Durum | Ana iş | Plan ön koşulu |
|---|---|---|---|---|
| T01 | P0 | TODO | Golden corpus ve karşılaştırma protokolü | — |
| T02 | P0 | TODO | İki coding yüzeyinde capability spike | T01 |
| T03 | P0 | TODO | Native/extend/build ve teknoloji kararı | T01,T02 |

Sıradaki **T01**. T01e sözlük/istek/claim örneklerini ekler; T02d tek hedef ve güvenilir seçim sinyalini araştırır; T03a–c [güncel P0 planını](backlog.md) açar. GAP/RES oracle, [Spike-1](spike-1-v1.md) ve native baseline ile ilk değer değerlendirilir. Bu hazırlık tamamlandı veya prototype kodu üretildi demek değildir.

## MVP — P1a ve P1b

**21 ana görev: 12 teknik çekirdek + 9 kullanılabilir MVP.** T04–T24 bağımsız ürün yoludur; P1a tek başına MVP sayılmaz. T03c kararı ve ilgili izin/teknoloji kapıları başlama koşuludur.

### P1a — Teknik çekirdek

| ID | Faz | Durum | Ana iş | Plan ön koşulu |
|---|---|---|---|---|
| T04 | P1a | TODO | Runtime iskeleti ve sözleşme doğrulayıcıları | T03 |
| T05 | P1a | TODO | Proje kimliği ve binding | T04 |
| T06 | P1a | TODO | Source ingress ve checkpoint | T05 |
| T07 | P1a | TODO | Domain log ve projector | T06 |
| T08 | P1a | TODO | Atomic change set ve policy | T07 |
| T09 | P1a | TODO | Extraction ve bounded retrieval | T08 |
| T10 | P1a | TODO | Temel reconciliation | T09 |
| T11 | P1a | TODO | Tipli gerekçe graph | T10 |
| T12 | P1a | TODO | Impact preview ve apply planı | T11 |
| T13 | P1a | TODO | Review işlemi ve güvenilir onay | T12 |
| T14 | P1a | TODO | Evidence ve false-done düzeltmesi | T13 |
| T15 | P1a | TODO | Teknik kanıt kapısı | T14 |

T15 kapısı: import → aday/uzlaştırma → karar etkisi → onay → event/projection → kanıt ve düzeltme. Atomiklik/retry/replay, proje izolasyonu, AND/OR/unknown, stale approval ve false-done kritik kontrollerdir. Tek hedefin read-back gözlemi bütün kabul kriterlerinin geçmesi değildir.

### P1b — Yerel MVP

| ID | Faz | Durum | Ana iş | Plan ön koşulu |
|---|---|---|---|---|
| T16 | P1b | TODO | Claude Code adapter | T15 |
| T17 | P1b | TODO | Codex adapter | T16 |
| T18 | P1b | TODO | Minimal MCP ve cross-agent read | T17 |
| T19 | P1b | TODO | Proje seçimi ve Review Inbox UI | T18 |
| T20 | P1b | TODO | Board, Graph ve Timeline | T19 |
| T21 | P1b | TODO | Routing etiketleri ve usage kaydı | T20 |
| T22 | P1b | TODO | Chat import ve prompt lineage | T21 |
| T23 | P1b | TODO | Backup, export ve yerel güvenlik | T22 |
| T24 | P1b | TODO | MVP kabul ve kullanıcı pilotu | T23 |

P1 temel dil dilimleri T05e/T24p: Unicode/source/ref korunumu ve açık pilot dili. Otomatik çok dil desteği P2 T25a/T26c önerisidir; MVP'de teslim edilmiş sayılmaz.

T24 çıkışı: [AC-01–14](../product/mvp.md), iki ayrı gerçek coding-adapter raporu, source coverage, holdout ve gerçek UI pilotu. Bir adapter başarısızsa “sınırlı pilot” ve açık kapsam kararı gerekir; sessizce tam MVP işaretleme.

### MVP içindeki alt işler

Aşağıdaki gruplar **önemli örneklerdir**, bütün alt görevlerin kopyası değildir. Parent'ın backlog ve team/data planında tanımlanan bütün ilgili dilimleri kendi kabulüyle birlikte tamamlanır. PROPOSED alt dilim kabul edilmiş implementation taahhüdü sayılmaz.

| Grup | Mevcut alt dilim örnekleri | Kanıt ailesi / ayrıntı |
|---|---|---|
| İzin, kimlik, audit, depolama | T05b/c/d, T06d/e/f/g, T07b, T08b/c, T23a–e | [Ekip/veri](team-data-plan.md), MU/ACC/LIM/SEQ/DBR |
| Kaynaklı aday çıkarma ve token | T09b/c/d/e, T10b, T21b/c | [Routing](../architecture/routing-token-economy.md), TOK/TRA/LEX; ücretli model Q03'e bağlı |
| Karar etkisi, iptal, blocker | T11b/c, T12a, T13a/b/c/e, T14a–d | [Verification](../quality/verification.md), GUX/CTX/ASK/GAP/FLOW |
| MCP ve devam paketi | T18a–i, T20h/i | [Connection](../architecture/connection-and-context.md), CON/CHAT/LAG/RES/GAP; host tüketimi varsayılmaz |
| Onay, graph, yönetim ekranları | T19b, T20a–i, T21c, T23e | [Admin](../product/administration-and-operations.md), ADM/GUX/TRA/RES |
| Pilot ve karşılaştırma | T24a–o | İlgili uygulanmış yolların raporları; future/unsupported senaryo not_run kalır |

## Faz 2 — P2

**3 ana görev.** MVP'nin mevcut kalite kapıları korunur; ek kabiliyet platform ve kalite kanıtıyla açılır.

| ID | Faz | Durum | Ana iş | Plan ön koşulu |
|---|---|---|---|---|
| T25 | P2 | TODO | Chat yüzeyleri ve cross-provider adapter araştırması | T24 |
| T26 | P2 | TODO | Gelişmiş reconciliation ve orphan audit | T25 |
| T27 | P2 | TODO | GitHub evidence ve görünür panel deneyi | T26 |

| Çalışma paketi | Planlanan sonuç | Çıkış kanıtı |
|---|---|---|
| Konuşma dili ve yerelleştirme | T25a/T26c PROPOSED: otomatik tespit, mixed/fallback, etkin dilde çıktı, UI katalogları ve çok dilli retrieval | [LANG-01–08](../product/language-and-localization.md); Q12 stratejisi, source/ACL/revision ve kalite/maliyet kanıtı |
| Chat ve sağlayıcılar arası süreklilik | Yüzey başına izin/capability raporu, binding ve source lineage | Gerçek yüzeyde test; documented/verified/unknown ayrımı, manuel fallback açık |
| Gelişmiş uzlaştırma ve impact | Semantic diff, stale/unlink/orphan incelemesi; embedding yalnız ihtiyaç kanıtlıysa | Holdout recall ve false-obsolete regresyonu; toplam bütçe/kalite kıyası |
| Öncelik/ranking deneyi | T26b PROPOSED: açıklanabilir çok faktörlü scoring/what-if | FLOW-16/17 ve mevcut regresyonlar; veri yeterliliği/UX/efor kanıtı olmadan kesin kritik yol iddiası yok |
| GitHub evidence ve panel | Read-only commit/PR kanıtı; ayrı host panel feasibility | Commit freshness/coverage; PR varlığı task done değildir; panel yoksa fallback |

P0/P1a'daki tek hedef uygulama kontrolü T27'nin bütün GitHub evidence entegrasyonunun tamamlandığı anlamına gelmez. Bir sağlayıcının izin vermediği erişimi gerçekleştirmiş sayma. [Ölçüm kapıları](../quality/measurement.md) uygulanabilir kapsamın kanıtını verir; sayısal ürün SLO'su veya takvim seçilmiş değildir.

## Faz 3 — P3

**2 ana görev, connector/release başına küçük teslimler.** T28'in tek satır olması bütün entegrasyonları tek iş yapmaz; ana backlog'un gerektirdiği provider bazlı ayrıştırma korunur.

| ID | Faz | Durum | Ana iş | Plan ön koşulu |
|---|---|---|---|---|
| T28 | P3 | TODO | Maliyet raporu ve kontrollü entegrasyonlar | T27 |
| T29 | P3 | TODO | Public release hazırlığı | T28 |

| Çalışma paketi | Planlanan sonuç | Çıkış kanıtı |
|---|---|---|
| Maliyet ve routing | Fiyat snapshot, nullable usage, model/provider karşılaştırması ve maliyet görünümü | Kalite/coverage eşitliğinde actual tüketim; host bilinmeyen maliyetine sıfır yazma |
| GitHub / Linear / Jira | Her connector için ayrı yetki/scope, outbox ve conflict/delivery planı | T28b/c; retry/idempotency, callback/poll, unknown/reconciliation, izin/revocation |
| Paket ve kurulum | Temiz kurulum, sentetik demo ve contributor rehberi | Temiz ortam testi, secrets ve bağımlılık/lisans inventory |
| Release kararı | İsim/lisans ve dış erişim için somut öneri | Açık owner kararı; T29 tamamlandı diye private repo otomatik public olmaz |

Dış sisteme yazmak kaynak okuma izninin devamı değildir. Her connector'da API/rate-limit maliyeti ve provider istisnaları değerlendirilir. Nihai lisans, isim, hosting ve public release hâlâ açık kararlardır.

## Faz 4 — P4

| ID | Faz | Durum | Ana iş | Plan ön koşulu |
|---|---|---|---|---|
| T30 | P4 | TODO | Ekip/cloud/open-core keşfi | T29 |

C01–C06 ayrıntısı [ekip/veri planında](team-data-plan.md); ekip/cloud özelliklerini yanlışlıkla P2/P3 tamamlandı diye gösterme. Tenant/agent/ACL/audit temellerinin MVP'de bulunması ekip daveti ve hosted servis teslim edildi demek değildir.

## Takip nasıl güncellenecek?

1. Backlog'da işin alt dilimini, ön koşullarını, ilgili AC'leri ve gerçek izinleri kontrol et; yalnız plan sırasını teknik blocker sayma.
2. Aktif işin owner/executor, durum, engel, kanıt ref'i, çalıştırılan test ve sonraki adımını status veya tarihli delivery kaydına yaz. Rol/başlama izni atanmadan hazır olduğunu varsayma.
3. Parent durumunu yalnız bütün ilgili kabul/dilim kanıtıyla güncelle; ana tablonun bu faz görünümünü aynı değişiklikte eşleştir. Doküman hazır olması runtime görevi done yapmaz.
4. Bir task veya fazın kapanışında [AC/DoD ve kaynaklı bağlam](../product/task-context-and-acceptance.md) güncellenir. İptal/erteleme gerekçesi ve tarihçesi korunur.
5. `python3 scripts/check_docs.py` ile ana satırların bu görünümle eşleşmesini kontrol et. Bu statik kontrol uygulama testini veya otomatik project-management servisini çalıştırmaz.

Bugünkü snapshot'ta 30 ana geliştirme görevi TODO; bazı alt dilimler PROPOSED. Tarih, efor taahhüdü ve ilerleme yüzdesi seçilmedi. Görev sayısı zaman veya ürün tamamlanma oranı değildir; güncel gerçekleşme status'tan okunur.

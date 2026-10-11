# Proje ilerleme görünümü

> Otomatik üretilir. Ana kaynak backlog’dur; bu dosyayı elle düzenleme.

**Açık çalışma fazı: P0**

[Canlı yerel ekranı açma ve güncelleme rehberi](progress-guide.md). GitHub bu Markdown görünümünü gösterir; canlı ekran yerel dosyaları izler.

`IN_PROGRESS` açık çalışma kaydıdır; bir agent’ın şu anda çalıştığını göstermez. Plan ön koşulları otomatik teknik blocker değildir. Test sayısı ürün tamamlanma yüzdesi değildir.

| Ana görev durumu | Sayı |
|---|---|
| IN_PROGRESS | 3 |
| TODO | 27 |

## Tamamlanmış küçük teslimler

Alt teslim kapanışı ana görev veya MVP kapanışı değildir. Kabul kapsamı ve kanıt backlog’da kayıtlıdır.

| Alt görev | Ana görev | Durum | Teslim |
|---|---|---|---|
| T03g | T03 | DONE | DONE / P0: bounded quote adapter ve ayrı candidate rubric |
| T03h | T03 | DONE | DONE / P0: gönderimsiz API paket ve saved response import |
| T03i | T03 | DONE | DONE / P0: tek selected local file observer |
| T03j | T03 | DONE | DONE / P0: tek komutluk integrated zincir |

## Açık fazda neler değişti?

Ana görev kapanışı ile hazırlık/kod/ölçüm ilerlemesi ayrıdır. Aşağıdaki kayıtlar backlog'dan gelir; canlı agent etkinliği değildir.

### T01 · Golden corpus ve karşılaştırma protokolü

2026-10-12 · H1 karar seçimi ve ayrı görev etkisi onayı davranışı kullanıcı tarafından onaylandı; [source/oracle hash bağlı partial review](../quality/reviews/h1-behavior.json) kaydedildi. Exact extraction/task impact etiketleri ve corpus bütünü henüz incelenmedi; gold/holdout iddiası yok, oracle değişmedi.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: H2 kısmi kabul kriteri incelemesi soruldu; H3 ve exact candidate/domain etiketleri sırada. İnsan inceleme kuyruğu ve gerçek model kalite ölçümü ayrı kapılar; T01 IN_PROGRESS.

### T02 · İki coding yüzeyinde capability spike

2026-10-11 · Capture kodu: Spike-0 kaynak/session, geciken delta ve kısa cevap kontrolleri 40 fixture testine sahip. Son token-limit çalışması gerçek host kurulumu veya capture testi eklemedi.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: [Hazırlık kapısında](implementation-readiness.md) seçilmiş Codex/Claude host ve scoped grant ile gerçek capability kontrolü. MCP erişimi tam otomatik capture kanıtı değil.

### T03 · Native/extend/build ve teknoloji kararı

2026-10-12 · T03g/T03h/T03i/T03j küçük teslimleri DONE: bounded quote adapter, gönderimsiz API paket/import, tek-file observer ve tek komutluk integrated zincir. 66 semantik suite testi ve yedi checkpoint passed; karar/impact/AC/restore akışı kontrol edildi. [Kapanış kapsamı ve kanıt](../quality/integrated-chain.md). Ana T03 IN_PROGRESS; inference 0, production/semantic kalite kapısı açık.

**Aktif teknik risk:** Observed / High · R20: ham S02-002 10/11 span hatasında reddedildi. Bounded offline adapter teslim; yeni quote-only contract üzerinde gerçek-model kalite/production doğrulaması açık. [Aktif risk kaydı](../governance/risks.md). Provider cap/usage unknown; yeni inference izni yok.

**Denemeler / sonuç:** S02-001: erişim hatası, output yok. S02-002: output var, kaynak konumu reddi. ANCHOR-PROBE-01: 11 exact quote/7 edge kontrolü. ANCHOR-ADAPTER-01: bounded kod ve ayrı rubric/CLI teslim; 10 konum düzeltildi, 11 candidate geçti, 48 suite testi; yeni model çağrısı ve semantik ölçüm yok. [Kanıt ve deneme günlüğü](../quality/s02-second-attempt-result.md).

**Etkilenen iş:** T03 geçerli output/kalite ölçümü açık; T09 production source anchoring/entegrasyonu gerekli; P0 offline adapter teslim. Diğer fixture teslimleri korunur; hiçbir ana görev bu probe nedeniyle kapanmaz.

Sıradaki adım: H1 insan incelemesi → mevcut üyelik üzerinden source-only quote deneyinin route/tek-send/usage sınırını hazırlama. API bakiyesi $0 kullanıcı bildirimi; paid API dispatch yok. Önceki çağrı izinleri tüketildi, yeni sınır/onay gerekecek. Anlam doğruluğu, gerçek grant, graph/target/AC ve native kıyas açık; observer match ana görevi kapatmaz.


## Mevcut teslim parçaları

Bunlar P0 hazırlığı ve kontrollü deney kodudur; tamamlanmış production engine/MVP değildir.

- **Capture ölçüm düzeneği** — Spike-0 kaynak/session kimliği, kapanışsız delta ve kısa cevap gözlemi; production adapter değil; 40 fixture/regresyon testi; gerçek host capability açık
- **Kaynak-only model input’u** — 6 session istek hazırlayıcı; 58 mesaj; source metadata auth ve oracle dışarıda; exact hash/version/proje kimliği; Protocol input/leak/cache/namespace testleri
- **Semantik çıktı sözleşmesi** — JSON envelope, 14 aday türü, Unicode source span, tip/byte/record limiti, duplicate ve abstention; Hatalı/stale/yetki iddialı çıktı reddediliyor
- **Geç cevap bağlantısı** — Model AnswerRecord → pending proposal; ayrı trusted receipt ile karar; task impact apply ayrı; Actor/receipt/project/source/question/base/retry negatifleri
- **Ölçüm ve başarısızlık** — Import edilmiş response → bağımsız span scorer; eksik output/abstention incomplete; yedi state checkpoint için exact scorer; Eksik/yanlış expectation başarı sayılmıyor
- **Zincir proof’u** — Gerçek sentetik source dosyası → scripted contract response → selection → AND/OR/unknown → old target → partial/full AC → restore; [Sonuç](../quality/semantic-readiness-results.json); gerçek inference/target değil
- **Otomasyon ve devir** — Test/CI komutları, mevcut status/backlog ve bu tek hazırlık kaydı; Docs/corpus/anchor + runtime regresyonları
- **Seçili gerçek hedef okuması** — Tek GitHub dokümanı iki immutable ref'te; aynı içerikte eski ref stale, seçili ref observed_match; Repo/path/ref/hash denetimi; task_verified false; ürün adapter veya SQLite uygulama kanıtı değil
- **Geliştirme takip ekranı** — Mevcut parçalar, açık işler, fazlar, AC/alt görevler ve engine görev bağlantıları; açık fazın son ilerleme/kalan adımı kartlarda görünür; 14 tracker testi; tarayıcıda T03 aktif risk/deneme bölümü ve önceki detay/P0 filtre kontrolleri; ürün UI veya canlı agent telemetry değil
- **S02 gönderim ve güvenlik hazırlığı** — İki ayrı onaylı tek gönderim: S02-001 cloudflare_challenge/çıktı yok; S02-002 gerçek output, 10/11 span hatalı, strict ret; her denemede retry 0; [Güncel rapor/ham çıktı](../quality/s02-second-attempt-result.md); kaynak hashleri sabit. JSON parse geçti, scorer/zincir çalışmadı; hard-cap/production limiter doğrulanmadı
- **Kaynak adapter ve candidate rubric** — Bounded exact quote + source/revision contract; explicit legacy türev; candidate/domain beklentileri ayrı; CLI offline; [48 suite testi ve üç scripted case](../quality/source-anchor-adapter.md); gerçek inference/semantic accuracy değil
- **Quote-only API deney paketi** — Strict schema taslağı, source-only payload, pending bütçe/onay manifesti ve saved response importer; [56 semantik test / 8 yeni](../quality/quote-api-package.md); gerçek provider dispatch/schema/kalite not_run
- **Seçilmiş yerel hedef observer** — Tek dosya real filesystem read, bounded no-follow/hash/change kontrolü; source metninden komut çalıştırılmaz; [65 semantik test ve ayrı gerçek yerel gözlem](../quality/local-observer.md); remote upload/task acceptance veya production IAM değil
- **Tek komutluk integrated zincir / T03j DONE** — Quote-only adapter ve bounded observer mevcut decision/impact/AC/restore akışına bağlandı; [66 semantik test ve yedi checkpoint](../quality/integrated-chain.md); T03g/h/i de scoped DONE, ana T03 ve gerçek model kalite kapısı açık
- **Yerel token/bağlam preflight kodu** — Manifestteki bütün çağrıların input/generation/context/run/parent bütçe hesaplaması; unknown/risk/hard cap ayrımı; [17 fixture testi ve S02 no-dispatch sonucu](../quality/token-preflight.md); gerçek para/atomik rezervasyon/provider limiter değil

## Açık karar ve doğrulama kapıları

| Konu | Etkisi | Sonraki adım |
|---|---|---|
| Geçerli gerçek model output’u ve bağımsız ölçüm | Bir gerçek output alındı, strict validator 10/11 kaynak konumu hatasında reddetti; semantik kalite hâlâ not_measured | [Yeni teslim](../quality/source-anchor-adapter.md): bounded adapter/negatifler, quote-only contract ve candidate scorer uygulandı; sırada yetkili gerçek inference ve insan review. Orijinal sonuç korunur, Q03-R5 tüketildi; otomatik tekrar yok, provider token upper bound unknown |
| Gold etiket/adjudication | Kodun çalışmasını değil, kalite skorlarının insan doğruluğu ve release genellemesini sınırlar | [H1 davranışı partial reviewed](../quality/reviews/h1-behavior.json); H2/H3, exact etiketler ve tam kritik set pending |
| Gerçek Codex/Claude capture | Otomatik capture/capability iddiası; MCP tool erişimi full capture değildir | A source import önce; B bağlantı sonraki kapı; gerçek config’e dokunulmadı |
| Native/dosya/resume kıyas | Üstünlük ve T03c yatırım kararı | [Kıyas protokolü](../quality/pilot-comparison-plan.md), not_run |
| Production stack/build | T04–T24 bağımsız ürün başlangıcı | T03c açık; fixture Python/SQLite önerilen üretim stack’i değil |

## Fazlara göre tüm ana işler

| ID | Faz | Durum | İş | Plan ön koşulu | Alt dilim |
|---|---|---|---|---|---|
| T01 | P0 | IN_PROGRESS | Golden corpus ve karşılaştırma protokolü |  | 2 |
| T02 | P0 | IN_PROGRESS | İki coding yüzeyinde capability spike | T01 | 2 |
| T03 | P0 | IN_PROGRESS | Native/extend/build ve teknoloji kararı | T01, T02 | 8 |
| T04 | P1a | TODO | Runtime iskeleti ve sözleşme doğrulayıcıları | T03 | 4 |
| T05 | P1a | TODO | Proje kimliği ve binding | T04 | 4 |
| T06 | P1a | TODO | Source ingress ve checkpoint | T05 | 6 |
| T07 | P1a | TODO | Domain log ve projector | T06 | 2 |
| T08 | P1a | TODO | Atomic change set ve policy | T07 | 2 |
| T09 | P1a | TODO | Extraction ve bounded retrieval | T08 | 4 |
| T10 | P1a | TODO | Temel reconciliation | T09 | 2 |
| T11 | P1a | TODO | Tipli gerekçe graph | T10 | 2 |
| T12 | P1a | TODO | Impact preview ve apply planı | T11 | 1 |
| T13 | P1a | TODO | Review işlemi ve güvenilir onay | T12 | 5 |
| T14 | P1a | TODO | Evidence ve false-done düzeltmesi | T13 | 4 |
| T15 | P1a | TODO | Teknik kanıt kapısı | T14, T07c | 1 |
| T16 | P1b | TODO | Claude Code adapter | T15 | 1 |
| T17 | P1b | TODO | Codex adapter | T16 | 0 |
| T18 | P1b | TODO | Minimal MCP ve cross-agent read | T17 | 7 |
| T19 | P1b | TODO | Proje seçimi ve Review Inbox UI | T18 | 1 |
| T20 | P1b | TODO | Board, Graph ve Timeline | T19 | 9 |
| T21 | P1b | TODO | Routing etiketleri ve usage kaydı | T20 | 2 |
| T22 | P1b | TODO | Chat import ve prompt lineage | T21 | 1 |
| T23 | P1b | TODO | Backup, export ve yerel güvenlik | T22 | 3 |
| T24 | P1b | TODO | MVP kabul ve kullanıcı pilotu | T23 | 15 |
| T25 | P2 | TODO | Chat yüzeyleri ve cross-provider adapter araştırması | T24 | 1 |
| T26 | P2 | TODO | Gelişmiş reconciliation ve orphan audit | T25 | 2 |
| T27 | P2 | TODO | GitHub evidence ve görünür panel deneyi | T26 | 0 |
| T28 | P3 | TODO | Maliyet raporu ve kontrollü entegrasyonlar | T27 | 1 |
| T29 | P3 | TODO | Public release hazırlığı | T28 | 0 |
| T30 | P4 | TODO | Ekip/cloud/open-core keşfi | T29 | 0 |

## Kanıt kapsamı

Kayıt durumu: **stale**; rapor tarihi: 2026-10-11; kayıtlı test sayısı: 91. Kaynak raporun tarihsel model kaydı: not_run; insan gold: pending; native kıyas: not_run. Production runtime: False.

Güncel model denemesi T03 son ilerleme kaydındadır. Bu alan kaynak raporun tarihsel checkpoint’idir. Kod hash kontrolü yalnız raporun listelediği dosyaları kapsar; bütün repo veya güncel CI sonucu değildir. [Kaynak rapor](../quality/semantic-readiness-results.json).

Görev kabul kriterleri, doğrulama ve alt görevler [kanonik backlog](backlog.md) içinde; 10 production engine [engine sözleşmesinde](../architecture/engines.md) planlıdır.

Kaynak fingerprint: `5274579082861404144aa39669e8353206807912d696f19cf62555721d27eeb6`

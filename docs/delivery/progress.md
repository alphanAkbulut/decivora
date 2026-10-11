# Proje ilerleme görünümü

> Otomatik üretilir. Ana kaynak backlog’dur; bu dosyayı elle düzenleme.

**Açık çalışma fazı: P0**

[Canlı yerel ekranı açma ve güncelleme rehberi](progress-guide.md). GitHub bu Markdown görünümünü gösterir; canlı ekran yerel dosyaları izler.

`IN_PROGRESS` açık çalışma kaydıdır; bir agent’ın şu anda çalıştığını göstermez. Plan ön koşulları otomatik teknik blocker değildir. Test sayısı ürün tamamlanma yüzdesi değildir.

| Ana görev durumu | Sayı |
|---|---|
| IN_PROGRESS | 3 |
| TODO | 27 |

## Açık fazda neler değişti?

Ana görev kapanışı ile hazırlık/kod/ölçüm ilerlemesi ayrıdır. Aşağıdaki kayıtlar backlog'dan gelir; canlı agent etkinliği değildir.

### T01 · Golden corpus ve karşılaştırma protokolü

2026-10-11 · Veri hazırlığı: 6 sentetik oturum/58 mesaj ve bağımsız scorer mevcut. Bu son token-limit çalışmasında yeni corpus veya insan gold üretilmedi.

Sıradaki adım: [İnsan inceleme kuyruğu](../quality/human-review-queue.md) ve kritik etiket doğrulaması; gerçek model sonucu ayrıca T03 deneyine eklenecek. T01 henüz kapanmadı.

### T02 · İki coding yüzeyinde capability spike

2026-10-11 · Capture kodu: Spike-0 kaynak/session, geciken delta ve kısa cevap kontrolleri 40 fixture testine sahip. Son token-limit çalışması gerçek host kurulumu veya capture testi eklemedi.

Sıradaki adım: [Hazırlık kapısında](implementation-readiness.md) seçilmiş Codex/Claude host ve scoped grant ile gerçek capability kontrolü. MCP erişimi tam otomatik capture kanıtı değil.

### T03 · Native/extend/build ve teknoloji kararı

2026-10-11 · Deney hazırlığı: S02 gönderim paketi hazır; input/output/context ve toplam bütçe durma kuralları belgelendi. Policy pending_capability_review; gerçek model çalıştırması not_run, üretim limiter kodu yok.

Sıradaki adım: [S02 planı](../quality/s02-account-smoke-plan.md): hesap/model seçimi → limit/dahil kullanım doğrulaması → tek output → bağımsız ölçüm. Sonra native kıyas ve T03c yatırım kararı; retry/ücret izni varsayılmaz.


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
- **Geliştirme takip ekranı** — Mevcut parçalar, açık işler, fazlar, AC/alt görevler ve engine görev bağlantıları; açık fazın son ilerleme/kalan adımı kartlarda görünür; 12 tracker testi ve tarayıcı T03 ayrıntısı/P0 filtresi kontrolü; ürün UI veya canlı agent telemetry değil
- **S02 gönderim ve güvenlik hazırlığı** — Tek S02 kaynak/prompt/policy; bir gönderim, sıfır retry/tools; ayrı token/context hard-cap sözleşmesi ve pending_capability_review; [Hazır plan](../quality/s02-account-smoke-plan.md); paket hash/policy kontrolü geçti. Belge/hazırlık teslimi; gerçek inference ve production limiter not_run

## Açık karar ve doğrulama kapıları

| Konu | Etkisi | Sonraki adım |
|---|---|---|
| Bir gerçek model output’u | Q03-R2 A seçildi; token/context güvenlik eki nedeniyle pending_capability_review. Gerçek output yok; ek API/credit harcaması izni yok | [Gönderim paketi ve sınırlar](../quality/s02-account-smoke-plan.md) hazır. Claude veya ChatGPT/Codex seçimi ve uygulanabilir cap doğrulaması → tek output → ölçüm; model/usage not_run/unknown |
| Gold etiket/adjudication | Kodun çalışmasını değil, kalite skorlarının insan doğruluğu ve release genellemesini sınırlar | Üç [örnek](../quality/human-review-queue.md) ve tam kritik set pending |
| Gerçek Codex/Claude capture | Otomatik capture/capability iddiası; MCP tool erişimi full capture değildir | A source import önce; B bağlantı sonraki kapı; gerçek config’e dokunulmadı |
| Native/dosya/resume kıyas | Üstünlük ve T03c yatırım kararı | [Kıyas protokolü](../quality/pilot-comparison-plan.md), not_run |
| Production stack/build | T04–T24 bağımsız ürün başlangıcı | T03c açık; fixture Python/SQLite önerilen üretim stack’i değil |

## Fazlara göre tüm ana işler

| ID | Faz | Durum | İş | Plan ön koşulu | Alt dilim |
|---|---|---|---|---|---|
| T01 | P0 | IN_PROGRESS | Golden corpus ve karşılaştırma protokolü |  | 2 |
| T02 | P0 | IN_PROGRESS | İki coding yüzeyinde capability spike | T01 | 2 |
| T03 | P0 | IN_PROGRESS | Native/extend/build ve teknoloji kararı | T01, T02 | 4 |
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

Kayıt durumu: **recorded**; rapor tarihi: 2026-10-11; kayıtlı test sayısı: 91. Model: not_run; insan gold: pending; native kıyas: not_run. Production runtime: False.

Kod hash kontrolü yalnız raporun listelediği dosyaları kapsar; bütün repo veya güncel CI sonucu değildir. [Kaynak rapor](../quality/semantic-readiness-results.json).

Görev kabul kriterleri, doğrulama ve alt görevler [kanonik backlog](backlog.md) içinde; 10 production engine [engine sözleşmesinde](../architecture/engines.md) planlıdır.

Kaynak fingerprint: `8340ce99639d0d85185dbb3afbe712284d84b145253b2105974edae9a30ce6c5`

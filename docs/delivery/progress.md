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
| T01g | T01 | DONE | DONE / P0: H1/H2/H3 ilk davranış incelemesi |
| T01h | T01 | DONE | DONE / P0: iki yeni development family ve ayrı kaynak/rubric paket |
| T01i | T01 | DONE | DONE / P0: H4 quoted/planned partial insan review |
| T03g | T03 | DONE | DONE / P0: bounded quote adapter ve ayrı candidate rubric |
| T03h | T03 | DONE | DONE / P0: gönderimsiz API paket ve saved response import |
| T03i | T03 | DONE | DONE / P0: tek selected local file observer |
| T03j | T03 | DONE | DONE / P0: tek komutluk integrated zincir |
| T03k | T03 | DONE | DONE / P0: mevcut üyelik source-only paket ve batch import/score |
| T03l | T03 | DONE | DONE / P0: onaylı MEMBERSHIP-001 tek gönderim ve değişmez ölçüm kaydı |
| T03m | T03 | DONE | DONE / P0: separate typed v2 field/type contract ve offline paket |
| T03n | T03 | DONE | DONE / P0: onaylı MEMBERSHIP-002 gerçek typed çıktı ve ölçüm |
| T03o | T03 | DONE | DONE / P0: gerçek kayıtlı candidate → controlled karar/impact/hedef/AC/restore replay |
| T03p | T03 | DONE | DONE / P0: aynı source'ta lexical ve saved-model dar ölçüm |
| T03q | T03 | DONE | DONE / P0: yeni8-message MEMBERSHIP-003 gerçek typed output ve ölçüm |

## Açık fazda neler değişti?

Ana görev kapanışı ile hazırlık/kod/ölçüm ilerlemesi ayrıdır. Aşağıdaki kayıtlar backlog'dan gelir; canlı agent etkinliği değildir.

### T01 · Golden corpus ve karşılaştırma protokolü

2026-10-12 · Kullanıcı H4 quoted/planned davranışına1-EVET dedi; [hash bağlı review](../quality/reviews/h4-behavior.json) partial case olarak kaydedildi, T01i DONE. Yeni ailede tek model run'ı6 draft candidate/2 scope-no-candidate beklentisiyle eşleşti; corpus/exact gold veya sealed holdout değil, source/rubric değişmedi.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Tam exact label/ikinci review/adjudication ve gerçekten ayrılmış yeni sealed-family kapıları açık; H1–H4 partial behavior tekrar sorulmaz. Yeni inference izni tüketildi; mevcut30 anlamlı kayıt koşulu korunur.

### T02 · İki coding yüzeyinde capability spike

2026-10-11 · Capture kodu: Spike-0 kaynak/session, geciken delta ve kısa cevap kontrolleri 40 fixture testine sahip. Son token-limit çalışması gerçek host kurulumu veya capture testi eklemedi.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: [Hazırlık kapısında](implementation-readiness.md) seçilmiş Codex/Claude host ve scoped grant ile gerçek capability kontrolü. MCP erişimi tam otomatik capture kanıtı değil.

### T03 · Native/extend/build ve teknoloji kararı

2026-10-12 · T03q onaylı MEMBERSHIP-003 tek gerçek output/ölçüm DONE:6 draft aday eşleşti, quoted/planned aday0, old/current revisions veENnot_run korundu.93 semantik test. Whole-batch iki cevapta güvenli blok; explicit per-candidate fixture tanısı stale/current ayrımını no-mutation gösterdi. [Rapor](../quality/membership-003-result.md); R22 reconciliation sınırı görünür.

**Aktif teknik risk:** Observed / High · R20/R21 için MEMBERSHIP-002'de dört quote ve açık attribute contract geçti; mitigation bu küçük development run ile sınırlı, release kalite/genelleme açık. Token/context cap ve usage unknown. [Güncel ölçüm](../quality/membership-002-result.md).

**Denemeler / sonuç:** S02-001 erişim/output yok; S02-002 span reddi; MEMBERSHIP-001 source geçti, draft candidate incomplete. MEMBERSHIP-002 tek yeni onaylı output: dört draft aday eşleşti (TP4/FP0/FN0), source/typed contract passed, guard mutations 0. Önceki ham sonuçlar korunur; paid API/retry 0.

**Etkilenen iş:** T03 gerçek typed/source-bound model çıktısı gördü; T09 contract sınırı için dar kanıt var. Entity/impact/hedef/AC, insan exact label ve native kıyas açık; üretim IAM veya kalite kapısı bu skorla kapanmaz.

Sıradaki adım: R22 için mesaj/soru/revision bazında read-only ayrı öneri toplama sözleşmesi ve stale/ambiguity negatifleri; sonra aynı bilgiyle resume/dosya/native kıyası. Yeni model izni tüketildi; paid API kapalı. Production IAM/criterion revision/lineage, insan gold ve T03c yatırım/stack açık.


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
- **Mevcut üyelik smoke paket/harness / T03k DONE** — 3330-byte source-only prompt, dört mesaj/iki project, ayrı candidate expectations, batch import/score; [72 semantik test / 6 yeni](../quality/membership-smoke-plan.md); hazırlık tarihsel; MEMBERSHIP-001 run tamamlandı, genel kalite/hard cap/usage açık
- **Gerçek üyelik run kaydı ve typed v2 / T03l,T03m DONE** — Bir gerçek output: source doğrulaması passed, candidate gate incomplete; alias/tür sorunu ayrı açık v2 contract ile sınırlandı; [78 semantik test ve run kanıtı](../quality/membership-001-result.md); v2 dispatch 0, primary skor/gold/production gate korunur
- **Gerçek typed v2 ölçümü / T03n DONE** — Tek yeni model output; dört draft aday eşleşti, source/type pass; isolated guards mutation 0; [80 semantik test ve ilk çıktı](../quality/membership-002-result.md); yeni send izni tüketildi, insan gold/production kalite değil
- **Kayıtlı gerçek aday zincir replay / T03o DONE** — V2 raw/source→ayrı receipt→AND/OR impact→eski/güncel içerik→partial/full AC→restore; [13 kontrollü checkpoint,86 semantik/6 yeni test](../quality/membership-chain-replay.md); yeni model/egress0; üretim IAM/criterion revision/lineage değil
- **Yeni development aileleri / T01h DONE** — Sekiz synthetic mesaj/iki source-only request, ayrı draft rubric/manifest/5321-byte prompt; [Hazır paket](../../examples/adversarial-smoke/README.md); source/hash/schema testleri; hazırlık tarihsel; H4 partial review ve MEMBERSHIP-003 gerçekleşti, sealed holdout/gold değil
- **Same-source kıyas / T03p DONE** — Aynı dört mesajda lexical ve saved-model shared span/kind skorları; capability farkı açık; [91 semantik test/5 yeni harness testi](../quality/same-source-comparison.md); yeni model0, native/domain/ekonomi kıyası değil
- **Yeni aile gerçek ölçümü ve H4 review / T03q,T01i DONE** — Onaylı tek çıktı6 draft aday/2 scope-no-candidate; source/type ve partial behavior review hash bağlı; [93 test/guard sonuçları](../quality/membership-003-result.md); whole-batch çok-aday blok, production reconciliation açık, izin tüketildi
- **Yerel token/bağlam preflight kodu** — Manifestteki bütün çağrıların input/generation/context/run/parent bütçe hesaplaması; unknown/risk/hard cap ayrımı; [17 fixture testi ve S02 no-dispatch sonucu](../quality/token-preflight.md); gerçek para/atomik rezervasyon/provider limiter değil

## Açık karar ve doğrulama kapıları

| Konu | Etkisi | Sonraki adım |
|---|---|---|
| Geçerli gerçek model output’u ve bağımsız ölçüm | MEMBERSHIP-003 yeni8mesajda6 draft aday ve2scope-no-candidate geçti; H4 partial review, tamgold/holdout yok | [Yeni run](../quality/membership-003-result.md): çok-aday whole-batch blocked; ayrı tanı source/revision no-mutation, R22 proposal toplama ve native kıyas açık; usage/hard cap unknown |
| Gold etiket/adjudication | Kodun çalışmasını değil, kalite skorlarının insan doğruluğu ve release genellemesini sınırlar | [H1](../quality/reviews/h1-behavior.json) / [H2](../quality/reviews/h2-behavior.json) / [H3](../quality/reviews/h3-behavior.json) behavior review tamamlandı (T01g DONE); exact etiketler ve tam kritik set pending |
| Gerçek Codex/Claude capture | Otomatik capture/capability iddiası; MCP tool erişimi full capture değildir | A source import önce; B bağlantı sonraki kapı; gerçek config’e dokunulmadı |
| Native/dosya/resume kıyas | Üstünlük ve T03c yatırım kararı | [Kıyas protokolü](../quality/pilot-comparison-plan.md), not_run |
| Production stack/build | T04–T24 bağımsız ürün başlangıcı | T03c açık; fixture Python/SQLite önerilen üretim stack’i değil |

## Fazlara göre tüm ana işler

| ID | Faz | Durum | İş | Plan ön koşulu | Alt dilim |
|---|---|---|---|---|---|
| T01 | P0 | IN_PROGRESS | Golden corpus ve karşılaştırma protokolü |  | 5 |
| T02 | P0 | IN_PROGRESS | İki coding yüzeyinde capability spike | T01 | 2 |
| T03 | P0 | IN_PROGRESS | Native/extend/build ve teknoloji kararı | T01, T02 | 15 |
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

Kaynak fingerprint: `1d4ab263bc8ce33028efd2b7dfd313475f05729e1450054d9cff0fe105f3c82e`

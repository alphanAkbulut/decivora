# Kod geliştirme hazırlığı: gerçek blocker ve bağımsız işler

**2026-10-12 · P0.** Kullanıcı insan bağımlılığı olmayan işleri tamamlamamızı, teknik belirsizlikleri somutlaştırmamızı istedi. Bu talep mevcut P0 zincirini geliştirme yetkisidir; ayrı ücret, dış model aktarımı, gerçek host ayarı veya production stack kabulü değildir.

## “Deney” tam olarak ne?

Python kaynak kodu, testler ve ölçüm komutlarıdır. [Spike-0](../../spikes/spike-0/README.md) capture’ı; [karar zinciri](../../spikes/decision-chain/README.md) state/impact/AC’yi; [semantik bağlantı](../../spikes/semantic-chain/README.md) source→model contract→policy→chain sınırını çalıştırır. Kontrollü fixture’lar gerçek model/host yerine kullanıldığında bu raporda açıkça belirtilir.

## Beklemeyen işler: uygulandı

| İş | Çıktı | Doğrulama |
|---|---|---|
| Capture ölçüm düzeneği | Spike-0 kaynak/session kimliği, kapanışsız delta ve kısa cevap gözlemi; production adapter değil | 40 fixture/regresyon testi; gerçek host capability açık |
| Kaynak-only model input’u | 6 session istek hazırlayıcı; 58 mesaj; source metadata auth ve oracle dışarıda; exact hash/version/proje kimliği | Protocol input/leak/cache/namespace testleri |
| Semantik çıktı sözleşmesi | JSON envelope, 14 aday türü, Unicode source span, tip/byte/record limiti, duplicate ve abstention | Hatalı/stale/yetki iddialı çıktı reddediliyor |
| Geç cevap bağlantısı | Model AnswerRecord → pending proposal; ayrı trusted receipt ile karar; task impact apply ayrı | Actor/receipt/project/source/question/base/retry negatifleri |
| Ölçüm ve başarısızlık | Import edilmiş response → bağımsız span scorer; eksik output/abstention incomplete; yedi state checkpoint için exact scorer | Eksik/yanlış expectation başarı sayılmıyor |
| Zincir proof’u | Gerçek sentetik source dosyası → scripted contract response → selection → AND/OR/unknown → old target → partial/full AC → restore | [Sonuç](../quality/semantic-readiness-results.json); gerçek inference/target değil |
| Otomasyon ve devir | Test/CI komutları, mevcut status/backlog ve bu tek hazırlık kaydı | Docs/corpus/anchor + runtime regresyonları |
| Seçili gerçek hedef okuması | Tek GitHub dokümanı iki immutable ref'te; aynı içerikte eski ref stale, seçili ref observed_match | Repo/path/ref/hash denetimi; task_verified false; ürün adapter veya SQLite uygulama kanıtı değil |
| Geliştirme takip ekranı | Mevcut parçalar, açık işler, fazlar, AC/alt görevler ve engine görev bağlantıları; açık fazın son ilerleme/kalan adımı kartlarda görünür | 14 tracker testi; tarayıcıda T03 aktif risk/deneme bölümü ve önceki detay/P0 filtre kontrolleri; ürün UI veya canlı agent telemetry değil |
| S02 gönderim ve güvenlik hazırlığı | İki ayrı onaylı tek gönderim: S02-001 cloudflare_challenge/çıktı yok; S02-002 gerçek output, 10/11 span hatalı, strict ret; her denemede retry 0 | [Güncel rapor/ham çıktı](../quality/s02-second-attempt-result.md); kaynak hashleri sabit. JSON parse geçti, scorer/zincir çalışmadı; hard-cap/production limiter doğrulanmadı |
| Kaynak adapter ve candidate rubric | Bounded exact quote + source/revision contract; explicit legacy türev; candidate/domain beklentileri ayrı; CLI offline | [48 suite testi ve üç scripted case](../quality/source-anchor-adapter.md); gerçek inference/semantic accuracy değil |
| Quote-only API deney paketi | Strict schema taslağı, source-only payload, pending bütçe/onay manifesti ve saved response importer | [56 semantik test / 8 yeni](../quality/quote-api-package.md); gerçek provider dispatch/schema/kalite not_run |
| Seçilmiş yerel hedef observer | Tek dosya real filesystem read, bounded no-follow/hash/change kontrolü; source metninden komut çalıştırılmaz | [65 semantik test ve ayrı gerçek yerel gözlem](../quality/local-observer.md); remote upload/task acceptance veya production IAM değil |
| Tek komutluk integrated zincir / T03j DONE | Quote-only adapter ve bounded observer mevcut decision/impact/AC/restore akışına bağlandı | [66 semantik test ve yedi checkpoint](../quality/integrated-chain.md); T03g/h/i de scoped DONE, ana T03 ve gerçek model kalite kapısı açık |
| Mevcut üyelik smoke paket/harness / T03k DONE | 3330-byte source-only prompt, dört mesaj/iki project, ayrı candidate expectations, batch import/score | [72 semantik test / 6 yeni](../quality/membership-smoke-plan.md); hazırlık tarihsel; MEMBERSHIP-001 run tamamlandı, genel kalite/hard cap/usage açık |
| Gerçek üyelik run kaydı ve typed v2 / T03l,T03m DONE | Bir gerçek output: source doğrulaması passed, candidate gate incomplete; alias/tür sorunu ayrı açık v2 contract ile sınırlandı | [78 semantik test ve run kanıtı](../quality/membership-001-result.md); v2 dispatch 0, primary skor/gold/production gate korunur |
| Gerçek typed v2 ölçümü / T03n DONE | Tek yeni model output; dört draft aday eşleşti, source/type pass; isolated guards mutation 0 | [80 semantik test ve ilk çıktı](../quality/membership-002-result.md); yeni send izni tüketildi, insan gold/production kalite değil |
| Yerel token/bağlam preflight kodu | Manifestteki bütün çağrıların input/generation/context/run/parent bütçe hesaplaması; unknown/risk/hard cap ayrımı | [17 fixture testi ve S02 no-dispatch sonucu](../quality/token-preflight.md); gerçek para/atomik rezervasyon/provider limiter değil |

Bu dilim algoritma/entity linkage/prompt semantik başarısı kanıtı değil. Ürün graph/IAM/API/UI hazır olmadı; model input/output kapısı ve fixture karar bağlantısı gerçekten kodlandı.

**Ek bağımsız kanıt:** [Seçili gerçek GitHub dosyası](../quality/semantic-target-readback.json) iki immutable ref’te okundu; repo/path/ref/hash scope doğrulaması çalıştı. Eski ref aynı içerikte olsa da stale, seçili ref observed_match; task_verified false. Bu ayrı manuel connector readback’i, fixture chain’in gerçek hedefte SQLite uyguladığı anlamına gelmez.

## Kalanlar: kimin neye karar vermesi gerekiyor?

| Konu | Tür | Neden gerekli / neyi durdurur? | Durum |
|---|---|---|---|
| Geçerli gerçek model output’u ve bağımsız ölçüm | Dar development ölçümü var; genelleme ve domain bağlantısı açık | MEMBERSHIP-002 source/typed/dört draft aday geçti; exact insan gold ve kör yeni aile ölçümü yok | [V2 run](../quality/membership-002-result.md): ayrı fixture guard, canonical mutation 0; sırada recorded-output zincir replay ve kıyas. Usage/hard cap unknown |
| Gold etiket/adjudication | İnsan değerlendirmesi | Kodun çalışmasını değil, kalite skorlarının insan doğruluğu ve release genellemesini sınırlar | [H1](../quality/reviews/h1-behavior.json) / [H2](../quality/reviews/h2-behavior.json) / [H3](../quality/reviews/h3-behavior.json) behavior review tamamlandı (T01g DONE); exact etiketler ve tam kritik set pending |
| Gerçek Codex/Claude capture | Seçilmiş sandbox/host ve grant | Otomatik capture/capability iddiası; MCP tool erişimi full capture değildir | A source import önce; B bağlantı sonraki kapı; gerçek config’e dokunulmadı |
| Native/dosya/resume kıyas | Erişilebilir ürün/build, aynı koşullar ve veri izni | Üstünlük ve T03c yatırım kararı | [Kıyas protokolü](../quality/pilot-comparison-plan.md), not_run |
| Production stack/build | Owner yatırım kararı + deney sonucu | T04–T24 bağımsız ürün başlangıcı | T03c açık; fixture Python/SQLite önerilen üretim stack’i değil |

MVP kapsamındaki olay geçmişi, backup, source isolation, yetki/onay ve verification invariant’ları önceden uygulanabilir sözleşmelere bağlandı; doğru runtime/host davranışları testlerle kanıtlanacak. Ekip/cloud ve ileri dil/connector detaylarının tamamını şimdi seçmek gerekmiyor.

## Netleşen teknik yöntemler ve sınırlar

- P0 yöntem: mevcut Python stdlib/SQLite devamı; ek bağımlılık veya ücret yok. Source hazırlama/import adapter sağlayıcı bağımsız; hangi LLM daha iyi sonucu deney belirler.
- İstek kimliği: project/session/messages/source revisions + seçili context + prompt version/hash. Aynı kaynak/prompt/context yeniden kullanılır; değişen kimlikte eski response reddedilir. Canonical mutations model transaction’ı içinde değil.
- Maliyet: 32 KiB input, 64 mesaj/64 aday ve 128 KiB response parse tavanı; 1536 output token önerisi. Bunlar offline sözleşme sınırlarıdır, ölçülmüş tasarruf veya API budget reservation değildir. Provider usage yoksa null.
- Güven: model metadata’sı talimat, ACL veya insan approval’ı değildir. Candidate source ile ayrı trusted selection binding’i eşleşir. Trusted receipt dict yalnız fixture; production authenticated policy channel ayrıca gerekir.
- Tamlık: abstention/eksik inference/parse hatası incomplete/deferred kalır; veri kaynağı saklanır. Typed smoke tüm ürün state/authority kontrollerinin başarı garantisi değildir.

## Sıradaki uygulanabilir adım

[MEMBERSHIP-002](../quality/membership-002-result.md) tek gerçek typed output ile dört development adayını eşleştirdi. Sırada kaydedilmiş adaylardan ayrı fixture receipt ile karar/impact/hedef/AC/restore replay; model ve fixture kanıtları ayrılmalı. Sonra exact label insan review, farklı sealed family ve native/dosya/resume kıyası. Yeni model send onayı tüketildi; offline replay için API bakiyesi gerekmez. T03c production yatırım/stack kararı açık.


**Güncel kaynak düzeltmesi:** [ANCHOR-ADAPTER-01](../quality/source-anchor-adapter.md) önceki offline adapter önerisini kodla tamamladı. Tarihsel deneme sonuçları korunur; quote-only v1/v2 artık gerçek modelde çalıştı; son ölçüm MEMBERSHIP-002, genel kalite kapısı açık. API yöntem önerisi harcama izni değildir.

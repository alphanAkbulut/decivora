# Karar → etki → gerçekleşme: teknik ölçüm protokolü

2026-10-12 — **Ölçüm sözleşmesi; dar P0 harness parçaları çalışıyor, production runtime ve geniş/native ölçüm açık.** [Metrik ve pilot hedefleri](measurement.md) otoritedir. Bu belge hedefleri değiştirmez; nasıl ölçüleceklerini uygulama seviyesinde açıklar. T01/T03a/T03b/T24 kapsamına bağlıdır. Araştırma sonucu değil, kontrollü deney tasarımıdır.

## Net olan, eksik olan

**Güncel uygulama kapsamı:** [13 controlled state checkpoint replay](membership-chain-replay.md) ve [aynı dört kaynakta lexical/kayıtlı-model shared-field kıyası](same-source-comparison.md) çalıştı. Aşağıdaki geniş skor/telemetry/UI/istatistik sözleşmesinin tamamı uygulanmış değildir; aynı development kaynakları, authored_draft, production/human gold/holdout/ekonomi gate açık. Yeni8-message paket hazırlanmış ama gönderilmemiştir.

| Alan | Mevcut netlik | Kalan somut iş |
|---|---|---|
| Problem/hipotez | H1/H3/H4/H6, yanlış onay/kapanış, GAP/RES/LATE oracle'ları tanımlı | Dondurulmuş kaynak etiketleri ve insan oracle incelemesi |
| Kalite hedefleri | Precision/recall, yanlış verified/closure, coverage ve yönetim/token metrikleri var | Uygulamadan gerçek state/event çıktısı, one-to-one matching ve scorer |
| Gerçekleşme kanıtı | Actor, exact repo/ref/path, artifact/AC revision ve unknown/stale ayrımı | T02 target capability; gerçek read-back adapter/izin deneyi |
| Rakip karşılaştırması | Native/config/extension/unknown ve fair baseline var | Aynı fixture'a araç adapter'ı; desteklenmeyen yüzeyin coverage kaydı |
| Telemetry/istatistik | Ölçülecek token/latency ve örneklem sınırı var | Run manifest, instrument edilmiş stage kayıtları, sonuç artifact'i, CI gate |
| Eşik/stack | Pilot eşikleri öneri; production stack seçilmedi | Baseline sonrası owner değerlendirmesi; framework seçimi deney önkoşulu değil |

**Sonuç:** Ölçüm teknik olarak yapılabilir; fakat mevcut prose ve illustrative JSON'dan çalışır ölçüm sistemi var sonucu çıkarılmaz. En önemli açık araştırma her repo'yu daha uzun okumak değil, mevcut sözleşmenin ölçülebilir input/output/kanıt arayüzüne çevrilmesidir.

## 1. Veri seti ve bağımsız doğru sonuç

T01'de en az 6 sentetik oturum/30 anlamlı kayıt şartı korunur. [Tek zincir örneği](../../examples/decision-impact-evaluation-case.json) veri formatı taslağıdır; T01 corpus'unu veya holdout'u tamamlamaz.

Her vaka: case_id, project/session/span, güvenilir actor/selection binding, kaynak sırası ve occurrence/ingest ayrımı, başlangıç decision/task/edge snapshot, target observation ve her kontrol noktasında expected state/effect. Konuşma yeni chat'e geçse de proje kimliği aynı, session kimliği farklıdır. Same-name projeler ve atıfsız “A” cevapları negatif vakaya eklenir.

Oracle, uygulama/model çıktısını görmeden hazırlanır. Quote/negation/plan/claim/human selection ayrı etiketlenir. İlk corpus source-span→typed entity ve relation eşlemesini içerir; serbest metin benzerliği bütün karar doğruluğunun ölçütü değildir. İkinci insan reviewer yoksa tek etiketleyici sınırlaması açık kalır; modelin kendi cevabı gold olarak kullanılamaz. Oracle anlaşmazlığı adjudication sonucu veya unresolved olarak kaydedilir.

Train/tune/holdout bütün session/case gruplarıyla ayrılır. Paraphrase/cross-language türevleri aynı grupta tutulur; aynı hikâyenin kopyası holdout'a sızmaz. Runtime'a expected sonuç verilmez. Oracle/model/prompt/config hash'i sonucu görmeden sabitlenir; tuning sonrası yeni sealed holdout gerekir.

## 2. Katman katman çalıştırma

| Katman | Input → observed output | Scorer ve kanıt |
|---|---|---|
| Capture/extraction | Raw sentetik chat/tool sonucu → typed claim/request/decision/task adayları | Source span/actor/target matching; TP/FP/FN ve duplicate; model kullanılıyorsa holdout |
| Domain/graph | Typed aday + authz/revision + approved değişiklik → event/projection/impact proposal | Saf deterministik truth table, state diff, rationale edge ve authorized transition |
| Target verification | Artifact manifest + immutable target read → observed/mismatch/unknown/partial | Byte veya tanımlı canonical hash, exact ref/path; read receipt ve observer authority |
| Agent devamı | Fresh session + bounded paket → current decision/next action cevabı | Yapısal rubric; yasak eski adım, gerekli bilinmeyen/soru; insan reviewer |
| Uçtan uca/UI | Kaynak→pending→onay→güncel state→görsel görev | Her checkpoint, gerçek tıklama/yanıt, review/correction süresi; sadece API pass UX pass değil |

Typed/domain testi chat extraction başarısını kanıtlamaz; fake target read gerçek provider testini kanıtlamaz. Katman izolasyonu nerede hata olduğunu bulur; uçtan uca zincir doğru davranışın birleştiğini ayrıca doğrular.

## 3. Karar, etki ve kanıt için objektif ölçüm

| Soru / hipotez | Nasıl ölçülür | Kritik hata |
|---|---|---|
| H1: Karar değişince doğru işler bulundu mu? | Aynı graph snapshot'ta gold impacted task set'i ile predicted set karşılaştırılır; action ve reason-path ayrı puanlanır | OR gerekçesi hâlâ doğru olan işi obsolete yapmak; unknown'u false kabul etmek |
| H4: İnsan gerçekten seçti mi? | Selection/question/option revision + authenticated actor + yetki + approval snapshot checkpoint diff | Model claim veya sessizliği insan onayı olarak kaydetmek |
| H4: Gerçekten uygulandı mı? | Immutable hedef gözlemi artifact manifest ve current decision revision'ına bağlanır | Eski bundle/yanlış branch gözlemini current implementation saymak |
| H6: Yeni chat doğru bağlamı kullandı mı? | Fresh session rubric: current decision, application unknown, next action, gerekli kanıt; eski planı canlandırma | Sadece “anladım” cevabını success saymak |
| H3: Kullanıcının yükü azaldı mı? | Aynı görevde setup/izin/import/review/düzeltme/context aktarma ve tekrar soru süresi | Kısa click süresini toplam yönetim tasarrufu saymak |

Önerilen deterministik scorer ayrıntıları:

- **Matching:** Önce proje+source span+record kind+entity key; sonra gold'un izin verdiği ID eşlemesi. Uygulamanın rastgele ürettiği ID'si gold ID'sine eşit olmak zorunda değil. Mapping one-to-one, model çıktılarını gördükten sonra başarı için değiştirilmez. Aynı gold'a iki prediction eşlenirse biri TP, diğeri duplicate FP olur. Meaningful capture ile duplicate oranı birlikte raporlanır.
- **Impact precision = TP/(TP+FP), recall = TP/(TP+FN).** TP yalnız doğru task değil; action-class skorunda doğru review/obsolete/retained eylemi gerekir. Affected-set, action confusion matrix ve rationale-path doğruluğu ayrı sonuçtur. Çoklu gerekçe AND/OR/unknown oracle'ı bağımsız kodla hesaplanır; sistemin kendi traversal'ı scorer olarak çağrılmaz.
- **Traceability:** Kaynak span, accepted karar revision, task/edge revision, approval ve evidence binding zinciri required alan/snapshot doğrulamasıyla kontrol edilir. Hash'in var olması içeriğin doğru veya kaynağın güvenilir olması değildir.
- **Application:** Hedef file existence yeterli değil. Observer exact immutable ref/path ve içerik digest'i verir; newline/canonicalization kuralı fixture'da önceden tanımlıdır. Partial bundle, permission failure ve unseen ref ayrı. Test/deploy çalıştırılmadıysa observed file → verified task dönüşmez.
- **False verified:** Yanlış verified ataması/all verified ataması; ayrıca yanlış verified sayısı/all assessment sayısı ve ham n raporlanır. Hiç verified önerilmezse precision N/A; sistem bu yolla başarılı sayılmaz, verified recall/coverage/abstention ayrıca görünür.
- **History/replay:** Event geçmişinin beklenen digest/projection eşitliği; duplicate submission/replay sonrası tek domain effect, sıfır dış dispatch/model/verifier çağrısı. Hata enjeksiyonu durable receipt öncesi/sonrası ve commit öncesi/sonrası kontrollü noktalarla yapılır. Fixture pass tüm crash durumlarının garantisi değildir.

Domain/kanıt/permission gates kodla kontrol edilir. Açıklama anlamı veya serbest next-action uygunluğu için insan rubric gerekir. LLM-as-judge yalnız opsiyonel yardımcıdır; yetki/onay/gerçek gerçekleşme için hakem olamaz. Judge kullanılacaksa sabit rubric, körleştirilmiş araç adları, order-bias kontrolleri, insanla kalibrasyon, disagreement ve ek token bütçesi kaydedilir; Q03 izni olmadan çağrı yok.

## 4. Run manifest ve telemetry sözleşmesi

Tek run: run_id, case_id/replicate, dataset revision/hash, tool commit/version/config, prompt/model/provider sürümü, oracle/scorer sürümü, connection scope/authz revision, clock/host, target snapshot, limits ve capability mode. Bir baseline'ın doküman claim'i observed output olarak yazılmaz.

Stage kayıtları önerisi: source_receipt_id, session/span, entity/revision, parent_run_id, decision/question/approval ID, graph snapshot, stage, attempt, result_status, started_at/ended_at/duration, usage_class, usage_known, provider_call_id ve evidence_ref/digest. Hassas ham chat/token/credential telemetry'ye eklenmez; sentetik veri veya erişim kontrollü reference kullanılır. [Log sözleşmesi](../architecture/logging-audit.md) geçerlidir; telemetry kanonik authority değildir.

Proposed deney artifact'leri:
- run manifest + item result JSONL: input hash, checkpoint, expected binding, observed output, scorer result, error/not_run reason.
- Event/projection/state diff ve immutable target observation; fake/real egress etiketi.
- Aggregate rapor: TP/FP/FN, action confusion, ham örneklem, coverage, p50/p95, review süresi, known/estimated/unknown usage; başarısız örnekler.
- CI gate özeti: critical invariant pass/fail/incomplete, oracle/scorer coverage. Raw private veri repo'ya konmaz.

Clock için süreler mümkünse aynı process monotonic clock ile ölçülür; dağıtık UTC timestamp'te skew ayrıca raporlanır. Durable ingest→review-ready, source lag, queue wait, processing, network/model ve human wait ayrı; insan bekleme processing p95'ine gizlice eklenmez/çıkarılmaz.

Token maliyeti iki defa sayılmaz: unique provider call/attempt ile parent/child/rerun ilişkisinden aggregate; callback tekrarları dedup. Extraction, embedding/retrieval, tool schema/response, brief, retry ve judge masrafı dahildir. Provider pricing snapshot ve cache/reasoning sınıfları saklanır; estimated ile actual ayrı. Host abonelik toplamı görünmüyorsa yalnız gözlenen ek yük raporlanır. Permission/budget engeli ürün başarı puanından sessiz çıkarılmaz.

## 5. Adil karşılaştırma, istatistik ve küçük örneklem

Aynı case, başlangıç graph, izinli kaynak/target, input sırası ve rubric; uygun native config, minimal extension ve Decivora ayrı koşullar. Unsupported hedef domain'i olan framework için tam ürün “başarısız” etiketi verilmez; component task ayrı. API ile çalışan ortak replay testinden sonra gerçek UI/host kullanımı ayrı ölçülür.

Her run'da scenario execution: pass/fail/not_run; evaluation_error (çalıştı ama puanlayıcı bozuk), unavailable capability ve access denial ayrıca reason olarak tutulur. Evaluator exception/missing score 0 kalite veya pass gibi görünmez; zorunlu scorer yoksa gate **incomplete**. Planned = actual olmayan çıktı; not_run sayısı/coverage bütün raporda görünür.

Başlangıç altı session/30 record yalnız hata bulma örneklemidir; %95 gibi hedeflerin gerçekleşmiş genel doğruluk olduğunu kanıtlamaz. Precision/recall ham n ve paydalarıyla, mümkünse case/session seviyesinde cluster bootstrap güven aralığı ile raporlanır. Aynı session'daki 30 record bağımsız 30 kullanıcı deneyi değildir. Küçük n'de aralık güvenilir değilse bu sınırlama yazılır; sıfır kritik hata gözlenmesi gerçek riskin sıfır olduğunu göstermez.

Model stochastic ise önerilen 3 tekrar ilk varyans taramasıdır; owner ile deneyden önce replicate sayısı/bütçe sabitlenir. Aynı case tekrarını bağımsız kullanıcı sayma. Model/seed mevcutsa kaydet; provider seed determinism varsayma. N-of-1 owner pilotunda eşdeğer senaryoları araç sırası dengelenmiş bloklarla ver; aynı hikâyenin cevabını öğrenme etkisini kaydet. Median paired süre/token farkı ve kalite birlikte gösterilir; tek pilot pazar talebi değildir.

Mevcut [pilot eşikleri](measurement.md) korunur. İnvariant suite'te kanıtsız verified, yetkisiz değişiklik/egress, zararlı closure ve kayıp receipt blocker. Diğer kalite hedefleri ve eş kalite altında yönetim/token faydası baseline ile değerlendirilir. Başarısızlığı gizlemek için payda/holdout/eşik değiştirilmez; ölçüm yoksa owner investment kararı “ek deney” olabilir.

## 6. Hedefli upstream araştırması: ne işe yarar?

2026-10-11 source okuması; aşağıdaki testler **çalıştırılmadı**, source copy/dependency adoption yapılmadı.

| Kaynak | Okunan uygulama örneği | Decivora dersi / sınır |
|---|---|---|
| Graphiti pinned 964bb11d1e7020e3cc67fab244268b0736b6c219 | [Graph-building eval](https://github.com/getzep/graphiti/blob/964bb11d1e7020e3cc67fab244268b0736b6c219/tests/evals/eval_e2e_graph_building.py) + [judge prompt](https://github.com/getzep/graphiti/blob/964bb11d1e7020e3cc67fab244268b0736b6c219/graphiti_core/prompts/eval.py) | Ayrı baseline/candidate graph çıktısı ve evaluator yaklaşımı var; karşılaştırmalı LLM judge insan authority/target kanıt oracle'ı değil. Prompt/kod kopyalanmadı. |
| Langfuse Python SDK pinned bf11ec121479145923ff27b32ec2ad1d06fd2d51 | [experiment.py](https://github.com/langfuse/langfuse-python/blob/bf11ec121479145923ff27b32ec2ad1d06fd2d51/langfuse/experiment.py) + [unit test tanımları](https://github.com/langfuse/langfuse-python/blob/bf11ec121479145923ff27b32ec2ad1d06fd2d51/tests/unit/test_experiment.py) | input/expected_output, item/run evaluator, trace/result ve RegressionError/RunnerContext örüntüleri. Evaluator-error kaydı ve CI incomplete davranışı özellikle kontrol edilmeli. SDK, server core ve ticari özellik lisansını eşitleme. |

**Graphiti örnek sınırı:** Seçili graph-building evaluator'da add_episode_context string listesi, zip'te alınan episodes ise tek string; message=episodes[0] ve previous_messages=episodes[1:] kullanılıyor. Bu bölümün amaçlanan mesaj/history bağını koruyup korumadığı runtime ile doğrulanmadı. zip strict=False ve missing judge verdict için default da oracle/coverage audit gerektirir. Bu, tüm repo'nun benchmark'ı geçersiz veya ürünün hatalı olduğu iddiası değil; örnek evaluator'ı incelemeden kopyalamama gerekçesidir. Bizim case input'u typed span listesi, expected checkpoint ve açık count alignment taşır.

**Langfuse örnek sınırı:** Seçili _run_evaluator kaynak yolu error'ı loglayıp empty evaluation döndürebiliyor; çağrıda raise seçeneği/default ve toplam scorer coverage incelenmelidir. Eksik skorun başarı gibi aggregate edilmemesi bizim gate sözleşmesidir; bu SDK'nin her kullanımdaki davranışı diye genellenmez. Gerçek exporter/CI/platform testi yok.

[Langfuse offline rehberi](https://langfuse.com/docs/evaluation/get-started/offline) dataset→application task→exact evaluator ve trace/export akışını; [core concepts](https://langfuse.com/docs/evaluation/core-concepts) code, human ve judge seçeneklerini belgelemektedir. Pattern araştırması yararlı; Langfuse hesabı/telemetry egress veya ücretli hizmet kararı verilmedi. SDK [MIT LICENSE](https://github.com/langfuse/langfuse-python/blob/bf11ec121479145923ff27b32ec2ad1d06fd2d51/LICENSE) okundu; transitif lisans ve dataset/model hakları alım öncesi açık.

## 7. Gerekli deep dive ve bitiş sınırı

1. **T01f:** Frozen case/checkpoint/identity matching, gold rubric, hata sınıfı ve evaluator contract. Bu belge + örnek yalnız taslak; corpus/holdout tamamlanmalı.
2. **T03f (T03a içinde):** Minimal local harness/adapter arayüzü, critical scorer missing/error gate, observer fake/real ayrımı, run manifest. Önce deterministik katman; ücretli model veya bağlı hesap gerekmeden hazırlanabilecek tasarım. Çalışan harness ayrı görev ve kanıt ister.
3. **T02/T03e:** Exact target gözlemi, kalıcı soru resume, Graphiti supersession ve LiteLLM unknown/cancel/budget closure kaynakları; yalnız ölçümün açık contract soruları için deep dive. Framework benimseme veya bütün repo audit'i önkoşul değil.
4. **T03b/T24q:** Yetkili run, failure/cost/coverage raporu; T03c native/extend/build kararı. Kendini puanlayan model yerine bağımsız oracle; deney geçmediyse düzeltme/ek deney.

Araştırma yeterlilik sınırı: named input/output, bağımsız oracle, observable evidence ve hata/unknown davranışı her zincir halkasında belli olunca ilk uygulama deneyi başlar. Daha fazla repo tarayarak corpus/harness işini ertelemeyiz. T01 sıradaki ana iş, Q03 veri/provider/bütçe ve Q13 adoption tercihleri açıktır; yeni teknoloji/ürün kararı alınmadı.

# Sistem işletim sözleşmeleri

**Öneri; uygulanmadı.** [Domain modeli](domain-model.md) iş anlamlarını, bu belge modüllerin hata/yarış koşullarındaki davranışını tanımlar. Teknoloji seçimi T03'te kesinleşir. Verilen alan ve sonuç kodları HTTP/MCP SDK veya fiziksel SQL şeması değildir.

[Tetik/API/zamanlama matrisi ve sequence'ler](execution-and-integrations.md) bu kuralların çağrı sırasını; [DB ilişki sözleşmesi](data-relationships.md) kardinalite, composite key ve transaction ilişkilerini tamamlar. Sayısal aralıklar fixture adayıdır, seçilmiş runtime varsayılanı değildir.

## 1. Kalıcı alım, işleme ve yeniden deneme

`SourceEnvelope`: schema_version, project_id veya quarantine_ref, provider/account/session kimliği, source_event_id, source_revision, source_epoch, occurred_at, ingested_at, payload_ref/hash, binding_revision, consent_revision, source_span, origin ve correlation_id.

Provider offset'i ile engine işleme cursor'ı ayrıdır. Alım transaction'ı source envelope, güvenli payload referansı, dedup anahtarı ve iş kuyruğu kaydını kalıcı yazar; sonra receipt döner. Adapter kendi okuma offset'ini receipt sonrası ilerletir. Modelden sonuç gelmesi için hook açık tutulmaz. Disk dolu/commit başarısızsa başarı receipt'i verilmez; adapter sınırlandırılmış spool veya açık gap bildirimi kullanır.

İşleme cursor'ı yalnız sonuç ve source→candidate/evaluation mapping kalıcı yazıldığında ilerler. Paralel işlerde tamamlanan aralıklar tutulur; contiguous watermark bir başarısız aralığın üstünden atlamaz. Sonraki aralık ayrı işlenebilir fakat önceki bağımlı bağlam eksikse sonucu `context_incomplete` olur. Session-end gelmese de idle/deadline flush uygulanır.

| Job durumu | Geçiş ve koşul | Kullanıcıya etkisi |
|---|---|---|
| queued | Yetkili source/job transaction'ı | Alındı, henüz işlenmedi |
| leased | Worker kısa lease + attempt/fencing token alır | İşleniyor; lease sonsuz değil |
| succeeded | Geçerli lease ile sonuç atomik yazılır | İşlendi; onaylandı anlamına gelmez |
| retry_wait | Geçici timeout/rate limit/servis hatası | Retry zamanı/attempt görünür; exponential backoff + jitter |
| deferred | Budget, izin veya gerekli karar yok | Sebep ve yeniden başlatma koşulu görünür |
| quarantined | Bozuk şema, belirsiz proje veya kalıcı parse hatası | Diğer işler ilerler; bu aralık kaybolmaz |
| failed | Retry limiti dolmuş veya kalıcı işlem hatası | İnceleme kuyruğu; başarı/no-op sayılmaz |

Lease süresi dolan işi başka worker alabilir; eski worker'ın commit'i fencing token ile reddedilir. Teslim **at-least-once**, domain etkisi idempotenttir; ağ/provider genelinde exactly-once vaadi yoktur. Dead-letter/quarantine kayıtları payload ref, hata sınıfı, engine sürümü ve attempt geçmişi taşır. Yeniden işleme yetkili bir komuttur; önceki başarısızlık silinmez.

Batch aynı project + binding epoch + source continuity sınırında kurulur. Byte/token/message/deadline sınırları vardır. Transcript rotation/truncation yeni epoch/gap yaratır. Hash tüm session kimliğinin yerine geçmez. Sistem kaynaklı export/bildirim `origin=decivora` ve causation taşır; loop prevention uygulanır fakat gerçek kullanıcının yeni cevabı düşürülmez.

## 2. Command, query ve hata sözleşmesi

Command: `command_id`, `project_id`, `actor_ref`, `idempotency_key`, `schema_version`, `base_revisions`, `policy_revision`, `payload`. Kimlik güvenilir transport oturumundan çözülür; payload içindeki `actor=human` yetki sağlamaz. Aynı key + digest sonucu tekrar döndürür; farklı digest `IDEMPOTENCY_CONFLICT` verir.

Query: yetkili project scope, filter, limit, snapshot/cursor ve context budget. Cevap: records, `snapshot_seq`, projection_version, next_cursor, truncated, coverage ve warning_codes. Cursor başka proje/filter/snapshot için kullanılamaz. Stale cursor kontrollü yeniden sorgu ister; offset ile sessiz kayıt atlama olmaz. Aynı snapshot desteği sağlanamıyorsa UI mixed/stale revision'ı gösterir.

| Sonuç kodu | Anlam / davranış |
|---|---|
| ACCEPTED_PENDING | Source/job alındı; canonical karar henüz uygulanmadı |
| APPLIED / ALREADY_APPLIED | Kalıcı command sonucu ve event sequence döner |
| INVALID_INPUT / UNSUPPORTED_SCHEMA | İşlenmedi; validation alanları, raw secret olmadan |
| UNAUTHORIZED / FORBIDDEN | Yetki yok; başka projedeki kaydın varlığı sızdırılmaz |
| PROJECT_UNBOUND | Quarantine/bağlama gerekli; ad benzerliğiyle tahmin yok |
| STALE_BASE / STALE_IMPACT / POLICY_CHANGED | Yeni diff/evaluation gerekli; eski onay yeniden kullanılamaz |
| IDEMPOTENCY_CONFLICT | Aynı anahtar farklı içerikte; yeni istek diye uygulanmaz |
| BUDGET_EXCEEDED / CAPABILITY_UNAVAILABLE | Deferred/unsupported; sessiz ucuz ama yanlış fallback yok |
| RATE_LIMITED / PAYLOAD_TOO_LARGE | İstek hızı veya boyutu aşıldı; admission reddi domain mutasyonu yapmaz; güvenli bekleme/küçültme açıklaması |
| QUEUE_FULL / SERVICE_BUSY / STORAGE_QUOTA_EXCEEDED | Kapasite veya kota nedeniyle yeni kabul yok; önceden alınmış iş silinmez; receipt/coverage durumu açık |
| TEMPORARY_FAILURE / STORAGE_UNAVAILABLE | Retry tavsiyesi; başarı iddiası yok |

Network cevabı kaybolduğunda istemci yeni key üretmek yerine aynı command/key ile durumu sorgular. Schema major uyumsuzluğu açık reddedilir. Transport status mapping T04'te kararlaştırılır; burada var olmayan endpoint dokümante edilmez.

## 3. Approval yetkisi ve graph concurrency

Onay: project_id, changeset_id, operation_digest, dependency_readset veya graph revision, base record revisions, AC revisions, policy revision, approver/session identity. Seçilmiş alt grup yeni proposal digest'i alır; eski onayın kapsamını sessizce genişletmez.

**Eksik eski tasarım riski:** Yalnız değiştirilecek record revision'larını kontrol etmek yetmez. Preview sonrası task'a yeni bir OR gerekçesi eklenebilir; task içeriği aynı kalsa da artık obsolete olmamalıdır. P1 için güvenli basit öneri: decision/requirement/edge/justification değişimlerinde artan **project knowledge revision**. Impact preview bunu taşır. Apply transaction'ı aynı revision'ı bekler; değiştiyse yeni impact preview ve gereken yeni onay hazırlanır. İlgisiz ham source alımı bu revision'ı artırmaz.

Bu kaba koruma yanlış stale oranını artırabilir; T24 bunu ölçer. P2'de read-set/predicate denetimine geçilecekse yeni eklenen edge'leri de yakalayan bir phantom-read koruması gerekir. “Yalnız dokunduğum task değişmedi” yeterli değildir. Read snapshot alındıktan sonra LLM transaction dışında çalışır; apply öncesi optimistic kontrol yapılır.

Karar ve etki aynı change set'te onaylanabilir. Kullanıcı yalnız kararı kabul ederse bilinen etkilenen işler `impact_review_pending` olarak görünür; ready önerisi ve auto verification bu güncel uygunluğu çözümlenene kadar ilerletilmez. Historical completion ayrı kalır. Traversal incomplete ise tamamlanmamış frontier ve kapsama açık gösterilir; tam analiz sonucu diye onaylatılmaz.

İnsan oturumu ile agent token'ı ayrı capability taşır. MVP agent'a scope/decision approve capability vermez. Önceden açık policy ile yetkilendirilmiş mekanik metadata/verification güncellemesi insan review'sundan farklı audit nedeni taşır. UI'daki butonun kendisi yetki sınırı değildir; server aynı kontrolleri uygular.

## 4. Onay, kanıt ve çalıştırma sınırı

Capture etmek, model çağırmak, öneri kabul etmek, kod çalıştırmak ve dış sisteme yazmak ayrı izinlerdir. Transcript'ten çıkarılmış bir test komutu doğrudan shell'de çalıştırılmaz. Verifier yalnız izinli workspace, önceden seçilmiş runner/check tanımı, timeout ve resource limit ile çalışır. Test komutu dependency script çalıştırabileceğinden workspace güveni ayrıca değerlendirilir.

MVP gerektiğinde yalnız mevcut test raporunu ingest edebilir. Kanıtın kimden geldiği ve güven seviyesi saklanır; bir agent'ın imzasız metin raporu trusted verifier sonucu olamaz. Araştırma/UX gibi mekanik test edilemeyen AC için insan değerlendirmesi kanıt türüdür; otomatik doğrulanmış diye etiketlenmez. `not_applicable` yalnız açık gerekçe ve yetkili policy/AC kararıyla kullanılabilir; false-done kısayolu değildir.

Kanıt artifact hash/revision, AC revision, runner/version, environment ve observed_at taşır. Süren test esnasında artifact değişirse eski snapshot sonucu eski revision'a bağlanır. Yeni revision stale kalır. Kanıt geçersizleşince yeni event yazılır; tarihsel sonuç silinmez.

## 5. Depolama, recovery ve veri yaşam döngüsü

Mantıksal veri kümeleri: projects/bindings; source envelopes/payloads; jobs/checkpoints; evaluations/usage; changesets/approvals; immutable domain events; records/versions/edges/evidence projections; outbox/delivery receipts. Bu kümeler ayrı veritabanı veya mikroservis gerektirmez. Project kapsamlı foreign key/unique koşulları storage katmanında da uygulanmalıdır.

Minimal uniqueness: bağlı source için workspace/project/provider/account/session/source_epoch/source_event_id/source_revision; quarantine için sahibinin ACL kapsamına bağlı import kimliği; project/command key; project/stream/version; project/trigger/engine version/input snapshot impact key. Global dedup farklı projelerin özel kaynaklarını birleştirmez. Event sequence event-store tarafından atanır; provider saati sırayı belirlemez.

Başlangıç: schema/projector compatibility denetimi → migration öncesi geri yüklenebilir backup → migration transaction/journal → integrity check → event log ve projection watermark denetimi → expired lease recovery → pending job/outbox resume. Bilinmeyen event sürümü sessiz atlanmaz; upgrade veya diagnostic read-only mode gerekir.

Projection rebuild ayrı staging projection üzerinde yapılır; digest/sequence kontrolü sonrası atomik geçiş tercih edilir. Replay bildirim göndermez, model çağırmaz, verifier/external write tetiklemez; saklı sonuçlardan read model kurar. Normal command'da yaratılmış outbox replay ile yeniden gönderilmez. Outbox delivery ledger ve side-effect modu restore testine dahildir.

Yedek DB ile payload referansları tutarlı snapshot içermelidir; sadece DB dosyasını kopyalamak tamamlanmış backup sayılmaz. Restore sonrası dış yazılar varsayılan durur: uzak sistem ileri gitmiş olabilir. Reconciliation/idempotency kontrolünden sonra devam edilir. RPO/RTO ve backup/retention sıklığı gerçek veri pilotundan önce seçilir; bugün SLA yoktur.

Privacy purge ham payload, arama index'i, embedding/cache, export ve backup retention kapsamını değerlendirir. Event log'da ham özel veri tutulmaması esastır. Purge tombstone/audit kalır; erişilemeyen kaynak `redacted/unavailable` görünür. Hash'in kişisel veri açısından her zaman anonim olduğunu varsayma. Ayrıntılı politika [açık karar OPEN-08](../governance/open-decisions.md).

## 6. Kaynak sınırları ve işletim görünürlüğü

[Limit ve kötüye kullanım sözleşmesi](resource-limits-and-abuse.md) request hızı/burst, eşzamanlılık, byte/iş kotası, maliyet ve DB transaction sınırlarını ayırır. Ortak insan/subagent bütçesi, admission sırası, belirsiz commit, limiter arızası ve admin müdahalesi orada tanımlıdır. Sayısal eşikler açık; temel kontroller ilk ingress'te gerekir.

Her provider/iş için deadline, max_attempts, payload/batch boyutu, input/output token, max_cost, queue capacity, traversal node/edge budget tanımlanır. Değerler fixture/baseline sonrası versioned config olur; sonsuz/unbounded default kullanılmaz. Queue doluysa source drop değil backpressure ve coverage alarmı gerekir. Shutdown yeni lease alımını durdurur; commit edilen iş korunur, kalan lease yeniden alınabilir.

Gözlemlenebilirlik: trace/correlation ile source receipt→job→evaluation→changeset→event→evidence izlenir. Ölçümler ingest lag, oldest queued age, retry/quarantine, incomplete intervals, stale approval oranı, impact frontier, projection lag, false-obsolete, verification freshness, budget ve actual/estimated usage. Loglara transcript, credential ve hassas prompt basılmaz. İnsan okuyabilir tanı export'u redacted olmalıdır.

Bu gereksinimlerin uygulanma sırası [backlog ek sözleşmelerinde](../delivery/backlog.md); doğrulaması V19–V28'de tanımlıdır. Local auth ve runner sınırları son hardening fazına bırakılmaz; ilk dış girdi alan runtime'da başlar.

## Ekip ve kalıcılık tamamlayıcı sözleşmeleri

[Identity/access](identity-access.md) komut/retrieval/dispatch'te authz revision, dar agent grant'i, kişisel kaynak görünürlüğü ve offboarding yarışını tanımlar. [Logging/audit](logging-audit.md) high-impact başarı kaydını atomik; dış teslim sonucunu ayrı yapar. [Storage/memory](storage-memory-capacity.md) durable job ile geçici context, raw TTL ile dedup kimliği, DB snapshot ile blob manifest ve restore ile purge ilişkisini tanımlar. Bunlar önerilen runtime sınırlarıdır; mevcut bir implementasyon değildir. Yerel tek owner modunda da insan/agent ayrımı ve proje izolasyonu atlanmaz.

## Çoklu kaynak frontier'ı ve model risk kapısı

[Çoklu chat/lag sözleşmesi](multi-chat-and-processing-lag.md) receipt ve processing frontier'ı session/epoch bazında tutar; project current durumu tek bir son mesaj zamanıyla hesaplanmaz. Geç gelen/çelişen konuşma güncel onaylı kaydı timestamp ile ezmez. Queue/storage tavanında yeni receipt durur; replay'siz adapter'da gap ihtimali açık gösterilir. Pending ilgili bağlam final impact/ready/verification gibi sunulmaz.

[Token risk onayı](../product/token-risk-and-approval.md) yeni dispatch öncesi assessment/approval tazeliği ve planın kalan tüketim payını bütçe rezervasyonuyla atomik denetler. Yüksek riskte `deferred + token_risk_approval_required`; bilinmeyen güvenli üst sınır veya yetersiz izin/hard-cap için blocked kullanılır. Karar beklemek source receipt'i geri almaz; model onayı domain completion değildir.

## Ortak executable sözleşmeye geçiş

[IC-01–08](implementation-contracts.md) bu sınırların stack'e aktarılırken netleştirilecek serialization, span coordinate, decoder, exact cost/period, target consistency ve completion freshness ayrıntılarını sunar. Öneri statüsündedir; deploy edilmiş API/DB/schema değildir. [TG-01–24 incelemesi](../quality/technical-gap-analysis.md) doküman hatası, teknik detay, owner ve implementasyon/deney açıklarını ayrı kaydeder; ilk kullanım kapıları G0–G6 ile bağlıdır.

## Uygulama notu — T13a local review

[ReviewService](review-runtime.md) current manual T13a dilimini uygular: group dependencies ve subset digest, ayrı owner approval, source/knowledge/authz/policy recheck, atomic command+review audit. Genel Workspace.apply review token ile bu guard'ı atlayamaz. T13b/c/e ve T14 açık; tüm yukarıdaki proposed sözleşmeler uygulanmış sayılmaz.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

[TaskStage](../../manifests/task-stage.schema.json) ve [criterion evidence](../../manifests/criterion-evidence.schema.json) versioned local audit payloadları; schema/SQLformat1 değişmez. [Workflow kodu/sınırlar](../quality/workflow-ui-runtime.md). Stage/verification/approval/job state birbirinden ayrıdır.

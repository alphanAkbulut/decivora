# Uygulamaya geçiş için ortak teknik ayrıntılar

**2026-10-11 · Tasarım önerisi; runtime, wire schema, DB migration veya test sonucu değildir.** [Runtime kuralları](runtime-contracts.md) ve [domain modeli](domain-model.md) otorite olarak korunur. Bu belge aşağıdaki uygulanabilir ayrıntıları önerir; stack/adapter seçimi sonrası T04/T08 ve ilgili görevlerde conformance testleriyle kesinleştirilir. Yeni servis, kütüphane veya ürün kapsamı seçmez. Gerekçeler ve önceki açıklar [teknik inceleme kaydında](../quality/technical-gap-analysis.md).

## IC-01 — Sözleşme sürümü, strict decode ve kaynak koordinatı

Önerilen geliştirme sırası: source envelope → command/query → job/result → proposal/approval → event/evidence → query DTO. Her sınır için required/nullable alanlar, enum, maksimum byte/derinlik/liste uzunluğu, hata kodu ve sürüm uyumluluğu aynı executable schema'dan üretilecek. Mantıksal alan listesi fiziksel DDL veya deploy edilmiş endpoint sayılmaz.

- Bilinmeyen major sürüm reddedilir; mevcut sürümde ek alan kabulü yalnız şemanın açık extension alanlarında olur. Bilinmeyen operation/state'i varsayılan no-op/complete yapma.
- Byte/admission kontrolü pahalı parse'dan önce; parse sonrası derinlik/koleksiyon sınırı, duplicate JSON key ve invalid Unicode kontrolü. Kimlik/grant transport'tan çözülür; payload actor bilgisi gözlenen actor'a dair iddiadır.
- Serbest model cevabı bounded parser → schema → izinli operation → source/span/ID referansı → project scope → revision/AC/policy → domain invariant sırasını geçmeden candidate olamaz. Geçmesi approval veya canonical apply değildir. Bozuk/yarım çıktı parse_error/failed veya bounded retry'dır; “hiç görev yok” sonucu değildir.
- Bir batch'te geçerli bir aday bulunması bütün kaynak aralığının işlendiğini kanıtlamaz. Kısmi sonuçta candidate provenance korunur; tamamlanmayan aralık ve watermark ayrı kalır. Coverage, confidence ile karıştırılmaz.
- Canonical span için öneri: değişmeyen kaynak UTF-8 byte dizisinde başlangıç dahil/bitiş hariç aralık + source revision/hash. Native UTF-16/codepoint/mesaj-alanı selector'ı adapter mapping'iyle ayrıca saklanır. Kesin profil T04'te seçilir; byte sınırı çok baytlı karakteri bölmemeli.
- TR harfleri, emoji, birleşik karakter, CRLF ve code block için source→span→alıntı round-trip testi gerekir. Search için normalleştirilmiş metin ayrı türev olabilir; kaynak byte'ı, offset'i ve kanıt hash'i değiştirme. Kaynak bulunamıyorsa fabricated quote üretme.

**Kapanış:** T04a/T04c ve T09/T10; invalid/oversize/unknown schema/foreign ref/partial output fixture'ları state'i değiştirmez; orijinal source quote birebir geri gelir. Parser birim testleri ve adapter sözleşme testleri farklıdır.

## IC-02 — Digest ve idempotency için tek içerik profili

Mevcut approval/key+digest kuralı korunur. Eksik olan aynı içeriği iki component'in aynı byte dizisine dönüştürmesidir. Öneri: version'lı bir canonicalization profile ve hash algoritması; schema validation sonrasında server üretir, client/model digest'ine güvenmez.

[JSON Canonicalization Scheme, RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) deterministik JSON temsilini tanımlar; informational belgedir, zorunlu seçilmiş ürün standardı değildir. JCS duplicate key'i kabul etmez, Unicode dizisini değiştirmez; yüksek hassasiyetli değerlerin sayı olarak taşınması sınırlarına dikkat çeker. Kaynak metne otomatik NFC uygulamak JCS davranışı değildir. Bu yüzden JCS uyumlu kütüphane ile typed domain serializer alternatifleri, seçilen stack'te aynı golden vektörlerle karşılaştırılmalı. Hâlen kütüphane/algoritma seçilmiş değildir.

Önerilen digest girdisi: workspace/project, schema/profile version, change set kimliği ve revision'ı, **sıralı** operation listesi, base record/AC/knowledge revisions, policy/authz snapshot ve onay kapsamına dahil plan/risk sınırları. Null/absent/default ayrımı şemada çözülür; operasyon sırası değişirse aynı kabul edilmez. Locale, ekrandaki tarih formatı, pagination ve gösterim metni canonical operation'ın yerine geçmez. Array'leri gelişigüzel sıralamak güvenli değildir.

Partial approval yeni change set ve digest üretir. Digest integrity aracıdır; insan kimliğini veya yetkiyi kanıtlamaz. Command idempotency namespace'i scope+operation/key'dir; aynı key+aynı canonical digest önceki sonucu, farklı digest conflict döndürür. Approval digest'i ile raw artifact content hash'i ayrı amaç/sürüm taşır.

**Kapanış:** T04a/T08a/T13; property order farkı aynı digest, operation order/null/AC/policy/scope değişimi uygun farklı digest veya schema rejection üretir. Unicode/precision/duplicate-key vektörleri iki üretici ve server arasında eşleşir. Onay payload'ındaki hash taklidi apply yetkisi vermez.

## IC-03 — Para, token ve parent/child bütçe muhasebesi

[Token sözleşmesindeki](routing-token-economy.md) atomik reserve/dispatch/settle ve unknown usage kuralı değişmez. Ayrıntı önerisi:

1. Para kaydı currency + exact decimal/fixed-point coefficient/scale taşır; binary floating point bütçe otoritesi olmaz. Provider fiyatının hassasiyetine göre scale ve yukarı yuvarlama kuralı T21'de belirlenir. Token sayıları negatif olmayan tamsayıdır; unknown sıfır değildir.
2. Her reservation provider/model/price revision, input-output üst sınırı, plan/approval revision, charge owner ve **budget period ID** ile bağlanır. Period timezone/boundary policy revision'ı taşır. Gün/ay değişti diye unresolved eski reservation silinmez; geç sonuç eski charge kaydına settle edilir.
3. Parent/child/retry/model fan-out aynı charge ağacını kullanır. Alt agent oluşturma yeni tavan yaratmaz. Aynı attempt/provider usage ID iki kez settle olmaz; düzeltilmiş usage yeni reconciliation kaydıdır.
4. Timeout/crash/cancel sonucunda usage bilinmiyorsa reservation tutulur veya açık conservative liability hesabına aktarılır. Lease expiry, provider harcaması bitti kanıtı değildir. Sonraki fiyat sürümü geçmiş charge'ı sessiz yeniden fiyatlamaz.
5. Gerçek tüketim tahmini/reservation'ı aşarsa gerçek tutarı kırpma; overrun görünür, yeni dispatch durur ve fark uzlaştırılır. Provider'da kontrol edemediğimiz harcama için “kesin harcama garantisi” verme. Üst sınır belirlenemeyen riskli çağrı ayrı onayla bile sınırsız açılmaz.
6. Yeni tavan yalnız yetkili budget/policy değişimidir. Risk onayı project/scope, toplam ek tavan, süre ve retry/child kapsamını gösterir; source read veya dış write izni sağlamaz.

**Kapanış:** T21/T21c ve T03f/T24q; eşzamanlı son bakiye, midnight rollover, duplicate settle, cancel-unknown, price revision ve child retry testleri. Actual/estimated/unknown ve model-host tüketimi ayrı raporlanır. Sayısal tavan Q03/OPEN-10/12 kapanmadan gerçek model deneyi yok.

## IC-04 — “Yüklendi” için tutarlı exact target gözlemi

[GAP sözleşmesi](../product/intent-to-reality-gap.md) ve T14d gözlem otoritesini tanımlar. Hedef taraması bütün araçlarda arama değildir: seçilmiş repo/path/ref ve ayrı read izniyle sınırlıdır.

Önerilen observer sonucu: target identity, requested/resolved immutable ref, path, observation ID, observer/version, scope/consent revision, observed_at, content fingerprint türü, requested/observed coverage ve typed outcome. Git branch adı önce bir commit'e çözülür; bütün dosyalar aynı commit'ten okunur. “main şu anda başka commit'te” yeni revision'dır.

Yerelde root/worktree identity ve güvenli path çözümü kontrol edilir. Tek dosya okumasında değişim veya farklı çoklu dosya snapshot'ı ihtimali varsa bounded tekrar/stability kontrolü kullanılır; tutarlı snapshot kanıtlanamadığında partial/unstable gösterilir. Stat zamanı tek başına aynı içerik kanıtı değildir. Snapshot/manifest/hash yaklaşımı T14b/T14d'de seçilir; burada yeni runner izni yok.

Ham artifact byte hash'i, semantic/normalized fingerprint ve beklenen içerik karşılaştırması ayrı alanlardır. CRLF/encoding farkına tolerans varsa onu ayrı verifier policy ve evidence türü açıklar. Eşit görünen açıklama veya aynı dosya adı exact byte eşleşmesi değildir. Beklenen artifact byte'ı yoksa byte equality unknown'dır; path/existence gözlemi yine kendi dar kapsamıyla kaydedilebilir.

Forbidden/offline/timeout/unavailable sonucu **missing** değildir. Tam izinli hedefte başarılı read'in not-found sonucu missing olabilir; bunun bile dünyadaki başka hedefte uygulanmadığı anlamı yoktur. Dosya varlığı test/deploy/AC pass sonucu üretmez. Büyük blob/truncated API cevabı tamamlanmış content comparison sayılmaz.

**Kapanış:** T02d/T14b/T14d; branch move, local concurrent edit, partial file set, line-ending policy, wrong worktree, permission denial ve artifact unavailable fixture'ları. Gerçek host API deneyi yapılmadan mock pass platform erişim kanıtı değildir.

## IC-05 — Completion, graph ve projection freshness

Mevcut AC/DoD/impact kurallarına uygulama ayrıntısı önerileri:

- Boş required AC kümesindeki “all passed” matematiksel sonucu otomatik completion değildir. Task sınıfında gerekli değerlendirme yoksa needs_review/explicit human assessment bekler. Bütün maddeleri not_applicable yapmak yetkili gerekçeli değişim ister; required_count ve applicable_count assessment'te görünür.
- Current completion ilgili task/AC/DoD/decision/evidence revisions ve impact applicability snapshot'ını kullanır. Agent run finished, upload observed veya child done bunların yerine geçmez.
- Apply, UI/read model'in gecikmiş görünümüne dayanmaz. Canonical seq ile projection watermark karşılaştırılır; gerekli read snapshot sağlanamıyorsa retry/deferred/stale sonucu verilir. Graph revision koruması apply transaction'ında tekrar kontrol edilir.
- Bilgi grafiğinin tümü DAG değildir. Yürütme depends_on ve parent/supersedes ilişkileri için ayrı cycle denetimi gerekir. Öneri: canonical yürütme cycle'ını reddet; kaynaktaki cycle adayı gerekçesiyle review'da kalsın. Mevcut “reddet veya bloke inceleme” alternatifinin kesin mapping'i T11'de kararlaştırılacak, sessiz kabul edilmiş sayılmaz.
- Unknown/missing ilişkilerde obsolete yayılımı yapılmaz. Traversal limitini aşan frontier preserved/incomplete kalır. Yeni kaynak/job alımı ile knowledge mutation aynı revision sayacı değildir.

**Kapanış:** T11/T12/T13/T14; boş AC, not_applicable-only, stale projector, OR edge race, typed cycle ve truncated traversal negatifleri. Doğru graph algoritması serbest konuşmadan tüm ilişkilerin yakalandığını kanıtlamaz.

## IC-06 — Yerel UI, MCP ve insan/agent sınırı

[Connection/context](connection-and-context.md) host'a ihtiyaç kadar bilgi sunar; MCP source capture garantisi değildir. Auth sözleşmesi her transport'ta uygulanır. Browser UI için server-side session, mutation CSRF/origin kontrolü; agent transport için ayrı scoped identity önerilir. Bearer token'ı URL/localStorage/log'a koymak varsayılan çözüm değildir. Login/bootstrap/recovery ve secret store seçimi T04b/T05'te hazırlanır. Loopback servisinin başka ağlara açılması MVP varsayımı değildir.

Sabit kaynak olarak incelenen [MCP 2025-11-25 transport belgesi](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports), stdio'da protokol dışı stdout olmamasını; Streamable HTTP'de Origin doğrulaması, yerel bağlama ve auth kontrollerini anlatır. HTTP bağlantısının kopması request cancellation sayılmaz. Bu sürümün her host tarafından desteklendiği veya güncel en son sürüm olduğu iddia edilmez; host/build capability matrisi gerekir.

Tool/query sonucu bounded/paged, ACL filtreli ve revision/coverage bilgili olur. Returned context'in host modeline daha önce verilmiş kopyasını grant revocation ile geri silemeyiz. Yeni retrieval/dispatch durur; eski host oturumuna tazelik uyarısı/delta taşıma ancak gerçekten desteklenen host yeteneği kadardır. “Bütün chat pencereleri sürekli günceldir” garantisi verilmez.

**Kapanış:** T04b/T02/T16/T17/T18; başka Origin/Host, unauthenticated request, replayed credential, stdio protocol pollution, disconnect/cancel ve revoke-after-context fixture'ları. UI butonu agent'a insan approval yetkisi kazandırmaz.

## IC-07 — Recovery, kapasite ve privacy için çalıştırılacak kanıt

[Storage](storage-memory-capacity.md), [limits](resource-limits-and-abuse.md) ve [audit](logging-audit.md) kuralları mevcut. Ek belge kapasite garantisi değildir. T23'te DB+blob manifest, schema/projector version ve event/receipt watermark birlikte doğrulanacak. Restore açılmadan güncel purge/grant state uzlaştırılacak; dış delivery kapalı kalacak.

Fault-injection noktaları: blob staging sonrası, DB commit öncesi/sonrası receipt yanıtı, lease sonucu öncesi, event+projection/outbox transaction'ı, budget dispatch öncesi/sonrası, audit yazımı ve restore cutover. Her noktada “hangi işi aldım dedi, hangi etki kalıcı oldu, hangi maliyet bilinmiyor?” oracle'ı tutulur. Replay sırasında model/verifier/notification/external write sayısı sıfır olmalı.

Load deneyi seçilmiş donanım/DB/model ve event/graph dağılımında request, queue, payload, traversal, context ve telemetry limitlerini birlikte ölçer. p95 tek başına yeterli değildir; drops/gaps, error rate, oldest pending, writer wait, disk/WAL/backup alanı ve fairness raporlanır. İlk gerçek veri öncesi retention, encryption/key recovery ve restore hedefleri OPEN-08/12 ile somutlaşır. Cloud/team identity ve distributed sync P4 kapısıdır.

**Kapanış:** T06/T07/T15/T23 ve MU/ADM/LIM/V senaryoları; yetkili sentetik recovery/load raporu. Normal docs lint veya JSON parse bu testlerin yerine geçmez.

## IC-08 — Conformance ve deney raporu

Her IC için uygulanmış test listesi, fixture/ref, implementation ref, environment, runner/version, observed output, expected oracle, state diff ve outcome kaydedilir. Outcome başlangıçta not_run; failed/incomplete/unsupported ayrı olur. Bu dosyanın varlığı test pass değildir.

Önce typed domain/no-model tests; sonra izinli capture/target capability; sonra kaynak-span extraction; sonra aynı corpus/ref ile fair native/manual/extension/own karşılaştırma. Hata veren scorer sonucu veya eksik kritik checkpoint “zero errors” diye raporlanmaz. [Ölçüm protokolü](../quality/evaluation-protocol.md) gold bağımsızlığı, eşleme, stage/cost ve incomplete gate otoritesidir. Stack kararı verilmeden tüm testleri yeni framework'e taşımak zorunlu değil; T01 golden corpus ilk küçük teslimdir.

Geliştirici sıradaki bağımlılıkları karşılanmış işi alır; IC-01–08 bütün MVP'nin yeni sekiz zorunlu ön görevi değildir. Hangi sınırı ilk kez kullandığında hangi testin kapı olduğunu [incelemedeki gate tablosundan](../quality/technical-gap-analysis.md) seçer.

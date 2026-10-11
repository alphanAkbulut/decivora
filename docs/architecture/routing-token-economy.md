# Intelligent work routing ve token ekonomisi

## İki ayrı etiket ekseni

`work_class`: DETERMINISTIC, LOW_COMPLEXITY, REASONING, HUMAN_DECISION.

`executor`: SYSTEM, SCRIPT, API, AGENT, HUMAN. İnsan basit bir işi üstlenebilir; HUMAN_DECISION yalnız stratejik/yetki kararı içindir. `human_suitable` ve `automation_available` yardımcı etiketleri insan seçeneğini görünür tutar. Bunlar rol/yetki yerine geçmez.

| İş | Nitelik | Tercih edilen yürütme |
|---|---|---|
| Dosya varlığı, JSON şeması, graph traversal | DETERMINISTIC | SYSTEM/SCRIPT |
| GitHub durumunu okuma | DETERMINISTIC | API |
| Standart alanları belgeden aktarma | LOW_COMPLEXITY | Önce parser; gerekirse küçük model |
| Çelişen mimari gerekçeleri yorumlama | REASONING | Bütçeli model evaluation |
| Eski kabul edilmiş kararı değiştirme | HUMAN_DECISION | İnsan onayı; AI analizi yardımcı |
| Basit manuel kontrol / erişilemeyen UI adımı | DETERMINISTIC veya LOW_COMPLEXITY | Kullanıcı tercih ederse HUMAN |

Routing sırası: yetki → risk → gerekli yetenek → deterministik çözüm → ölçülmüş model kalitesi → bütçe → kullanıcı tercihi. Ucuz model uygun kaliteye erişmiyorsa görev zorlanmaz; escalation veya review olur. Routing gelecekte executor başlatabilir; MVP etiketleme ve kayıt temellidir, izinsiz agent orchestration değildir.

## Context on demand

MVP MCP araç adayları: `get_project_brief(project_id, budget)`, `query_records(project_id, filters, cursor, limit)`, `get_record(project_id,id,revision)`, `submit_changeset(project_id,operations,base_revisions,key)`, `submit_evidence(project_id,evidence,key)`. Ayrıntılı graph ve admin araçları ihtiyaçta açılır. İnsan onayı ayrı güvenilir UI kimliği taşır; agent bir alanı `approved=true` göndererek onay veremez.

Brief yalnız current approved decisions, aktif iş, unresolved blockers ve değişiklik delta'sı içerir. Arşiv bağlamı, duplicate/rejected revival için hedefli getirilir. Tool schema boyutu, sonuç boyutu ve conversation context birbirinden ayrı ölçülür. MCP taşıma protokolüdür; kendi başına token tasarrufu garantilemez.

## Maliyet kontrolü

**1C seçiminin ekonomi kuralı:** İzinli geçmişin arşivlenmesi ile modele verilen context ayrıdır. İlk geçmiş çıkarımı maliyetlidir; aynı source/revision için sonucu yeniden kullanıp sonraki çalışmaları delta ve hedefli retrieval ile küçültmeyi hedefleriz. İlk kurulum maliyeti, günlük tüketim, kaynağa dönüş başarısı ve karar/ilişki recall'u ayrı raporlanır. Az token tek başına başarı değildir; eksik bilgiyle yanlış kapanış kabul edilmez. Ayrıntı [Q07](../delivery/decision-brief.md) ve [import sözleşmesinde](connection-and-context.md).

Alt göreve bölme token tasarrufunu garanti etmez. Önerilen child context paketi ana amaç + ilgili onaylı kararlar + child AC/DoD + gerekli bağımlılıklar ve kaynak pointer'larıdır; tüm sibling geçmişi kopyalanmaz. Birden çok işi bölen planlama çağrısı ve tekrar brief maliyetleri de ölçülür. Child/run yaratmak parent/proje/dönem tavanını sıfırlamaz; bölme ve yeniden denemeler aynı kaynak bütçesine bağlanır. UI alt görev/progress işlemleri deterministiktir; her child kapanışında yeni LLM özeti zorunlu olmaz.

- Turn/idle batch, kalıcı cursor, content/revision cache ve hedefli retrieval.
- Cache anahtarı project + record revisions + policy + extractor/prompt/model sürümü; yanlış proje cache paylaşımı yok.
- Her iş için max_input_tokens, max_output_tokens, max_retries, max_cost ve deadline; limitte defer/review, sessiz drop yok.
- Kesilen retrieval ve çıkarılmamış kaynak bölümü kullanıcıya görünür kalır. Bütçe için recall kaybı saklanmaz.
- Aynı kaynak seti ve engine sürümü tekrar değerlendirilirken önce kayıtlı sonuç kullanılır; zorunlu yeniden analiz ayrı run ID alır.

Usage kaydı: provider/model, operation, actual_input/output/cached tokens veya null, estimate ve estimator version, currency, price snapshot date, latency, retry count, deterministic bypass. Abonelik/quota kullanımı sıfır maliyet sayılmaz. Fiyat ve plan değerleri burada sabitlenmez.

Tahmini model maliyeti = birbirini tekrar saymayan faturalama sınıfları için Σ(token adedi × ilgili birim fiyat). Provider'a göre uncached input, cache write/read, output ve reasoning sınıfları eşlenir; örtüşen alanlar iki kez toplanmaz. Cache write maliyeti standart input'tan farklı olabilir; rezervasyon güvenli üst sınırı kullanır. Araç/API bedelleri ayrı eklenir. “Tasarruf” aynı golden corpus ve benzer kaliteye sahip full-context baseline ile karşılaştırılır; varsayımsal fark gerçekleşmiş fatura tasarrufu değildir.

## Hangi tüketim bizim kontrolümüzde?

**Bütün bölüm önerilen sözleşmedir; token tasarrufu ölçülmedi.** Capture'ın dosya/olay okuması, hash/dedup, index sorgusu, graph çizimi/traversal ve event replay normal yazılım işidir; kendiliğinden LLM token'ı gerektirmez. Agent'ın MCP aracını seçmesi ve dönen veriyi okuması ise o host'un model bağlamına ek yük getirebilir. MCP kullanmak “ücretsiz veya sıfır token” demek değildir.

| Tüketim yüzeyi | Kontrolümüz / ölçüm sınırı |
|---|---|
| Yerel deterministik servis | CPU/disk/iş süresi; model çağrısı sayısı bu yolda sıfır hedeflenir |
| Codex/Claude Code'un kendi konuşması | Decivora tool şeması ve sonuç boyutu sınırlandırılır; host'un toplam context'i, reasoning'i, diğer araçları ve plan kotası üzerinde tam kontrol yok |
| Decivora'nın ayrı extraction/evaluation modeli | Çağrı, context, output, retry, concurrency ve bütçe servis tarafından yönetilir; provider/veri izni ayrıca gerekir |
| Embedding/reranker/özet üretimi | Ücretsiz varsayılmaz; ayrı metered operation. Gerekli olduğu ölçülmeden açılmaz |
| UI liste/graph/filtre/zoom | Model çağrısı yok; açıklama üret gibi açık anlamsal işlem ayrı ve görünür |

Mevcut coding aboneliğinin arka plan Decivora analizini otomatik olarak karşılayacağı varsayılmaz. Host modelini genel amaçlı ücretsiz worker gibi çalıştırma planı yoktur. Desteklenen ve açıkça yetkilendirilmiş host akışı ileride ayrı deney olabilir; tool entegrasyonu böyle bir hak vermez. Local model de compute/kurulum maliyeti taşır ve quality gate'den muaftır denmez.

## Çağrı azaltma sırası

1. Kaynağı kalıcı al; source ID/revision/receipt ile aynı parçayı yeniden işleme. No-op/teknik event için model çağırma.
2. Kısa turn/idle grupları oluştur; ardışık partial stream'i her kelimede yeniden özetleme. Önerilen `balanced` profil anlamlı karar/onay anında analizi öne alır. `responsive` daha sık; `manual_semantic` kullanıcı isteğiyle işler. Q05 yanıtına göre profil proje kurulumunda seçilebilir, görevde sınırlandırılmış istisna olabilir ve ileride değiştirilebilir; tek profil bütün kullanıcılara zorlanmaz.
3. Structured MCP önerisi zaten varsa aynı span için ikinci extraction'ı atla; yeni span ve gerçek anlam değişiklikleri korunur. Deterministik filtre emin değilse `needs_semantic_review`; “önemsiz” diye drop etmez.
4. İlgili task/karar/AC ve eski ret gerekçesini index ile getir; bütün proje ve konuşmayı her defasında gönderme. Hedef alt grafikte reason completeness izlenir.
5. Sürüm bağlı kısa özet varsa kullan; sadece değişen parçaları yenile. Özetin üretilmesi de maliyete dahildir. Özet kaynak yerine geçmez, çelişki/yetersizlikte ilgili orijinal span açılır.
6. Aynı evaluation fingerprint hazırsa yetki/tazelik kontrolüyle yeniden kullan; aynı iş için eşzamanlı request'ler single-flight işi paylaşır. Başka principal'a izinsiz sonuç paylaşılmaz.
7. Küçük model ancak corpus'ta yeterli kalite gösterirse kullanılır. Daha güçlü modele geçiş otomatik sonsuz zincir değildir; run/model/cost sınırlarına tabidir.
8. Model yanıtı schema/citation kontrolünden geçer. Hatalı JSON veya transient hata sınırlı yeniden deneme; aynı kaynak için başarısız döngüde circuit breaker ve review/defer.

Cache/fingerprint anahtarı: workspace/project + kaynak/record revision + ACL/authz/policy revision + extractor/prompt/model/config sürümü. `since_revision` ile context delta'sı, invalidation/tombstone ve bounded resync [bağlantı sözleşmesinde](connection-and-context.md) tanımlıdır. Önceki sonuç current olmadan “cache hit” diye doğru kabul edilmez. Sürekli değişen global revision gereksiz cache miss yaratıyorsa seçici dependency fingerprint ancak aynı doğruluk kontrolleriyle optimize edilir.

Provider prompt cache'i ayrı optimizasyondur: aynı içeriği tekrar göndermeyi gereksiz kılmaz; uygulama cache'i gibi model çağrısını kaldırmaz. Hit/indirim ve destek model/provider'a bağlıdır, garanti tasarruf yazılmaz. Sabit tool/prompt bölümlerini kararlı tutma adayı [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) davranışıyla provider deneyi sırasında doğrulanır. Kullanıcıya bağlı hassas içeriği projeler arasında ortak prefix yapma.

## Başlangıç limit profili — deney önerisi

Aşağıdaki sayılar seçilmiş ürün varsayılanı veya ölçülmüş optimum değildir. T01/T09/T18/T21'de kalite ve gecikmeyle birlikte kalibre edilecek. Modelin context/output sınırı daha küçükse daha küçük sınır geçerlidir.

| Parametre | Sentetik ilk deney adayı | Limitte davranış |
|---|---|---|
| Project brief | En çok 800 tahmini token | İlgili karar/iş özeti + eksik kapsam/cursor; tam transcript dönmez |
| Tek MCP read sonucu | En çok 1.500 tahmini token; başlangıç 20 kayıt | Alan seçimi/sayfalama; mandatory ACL/coverage bilgisi kesilmez |
| Tek semantik çağrı input | En çok 8.000 token; tool şeması ve instruction dahil | Bölme + bağlam pointer'ı; gerekçe zinciri tamam değilse final impact sonucu üretme |
| Tek semantik çağrı output | En çok 1.500 provider output token birimi | Truncated sonuç proposal olarak tamamlanmış sayılmaz |
| Semantik run çağrısı | Retry ve escalation dahil en çok 3 çağrı | Kalan iş deferred/review; yeni run bütçeyi sıfırlamaz |
| Aynı çağrının denemesi | İlk deneme + en çok 1 retry; run limitine dahil | Kalıcı hata tekrar denenmez; transient backoff ve durum kaydı |
| Run input/output toplamı | En çok 16.000 input, 3.000 output token | Aynı chunk'ı yeni adla tekrar çağırarak limit aşılmaz |
| Proje semantik concurrency | İlk deneyde 1 aktif çağrı | Diğer işler kalıcı queue; capture ayrı yürür |
| Parasal dönem bütçesi | `unset` = ücretli arka plan çağrısı kapalı | Q03 somut provider/veri/tavan kararı olmadan ücret üretme |

Input/output/total alanlarının provider'ın reasoning/cached token sayımlarıyla eşlemesi adapter'da açıklanır; aynı token iki defa toplanmaz. Tahmin edilen token ile API usage ayrı tutulur. Tokenizer bilinmiyorsa `estimate` etiketi; sert bütçe için güvenli üst sınır hesaplanamayan çağrı otomatik açılmaz. MCP cevap limiti yalnız dönen payload'ı sınırlar; host'un tool döngüsünü veya toplam faturasını garanti sınırladığı iddia edilmez.

Batch'in context'e sığması için kaynak sessiz kesilmez. Chunk manifest ve işlenmemiş remainder frontier kalıcıdır. Birden fazla chunk ayrı ayrı öneriler üretse bile ilişkilerin birleşimi tamamlanmadan full coverage ilan edilmez. Büyük import bütçeyi çok run'a bölerek aşamaz; source manifest ve dönem bütçesi tüm child run'ları kapsar.

## Bütçenin eşzamanlı çağrılarda uygulanması

`BudgetPolicy`: workspace/project, operation/provider/model allowlist, data-egress policy, per-call/run/day/month limitleri, currency, dönem timezone'u, price snapshot/version ve effective_from. Workspace tavanı proje tavanlarının üst sınırıdır; kullanıcı arayüzünde ikisi ayrı görünür. Bütçe artırmak/başka provider'a geçmek ayrı yetki ister. Uyarı eşiği ve hard stop ayrı kavramlardır.

`UsageReservation`: run/job/attempt, idempotency key, reserved üst sınır, billable token sınıfları, status (`reserved/dispatched/settled/unknown/released`), actual usage, estimator ve price revision. Dispatch öncesi güncel erişim ve bütçe kontrol edilir; `spent + outstanding_reservations + worst_case_new <= limit` koşulu aynı DB transaction'ında korunur. Günlük ve aylık sayaçlar aynı çağrıyı kapsar; eşzamanlı worker'lar kalan bakiyeyi iki kez harcayamaz.

Request gönderilmeden kesin hata varsa reservation serbest bırakılabilir. Gönderildikten sonra timeout/worker crash/usage eksikliği ücret alınmadığını kanıtlamaz: reservation `unknown` olarak korunur, provider reconciliation veya yetkili muhasebe düzeltmesi gerekir. Lease sona erdi diye harcanmış olabilecek bütçe otomatik geri verilmez. Retry yeni attempt'tir ve önceki belirsiz tüketimin üzerine rezervasyon gerektirir. Provider fiyatı/token sınıfları/üst limitleri bilinmiyorsa tam parasal hard-cap garantisi verilemez; otomatik dispatch durur veya açıkça seçilmiş token-only policy uygulanır. Bu policy ayrı karar olmadan parasal limitin yerine geçmez.

Bütçe sıfırlandığında eski belirsiz çağrı kaybolmaz; dönem ve dispatch zamanına bağlı muhasebe korunur. Dış provider faturası, host abonelik limiti ve Decivora ölçümü farklı kaynaklardır. Usage düzeltmesi audit'li ek olaydır; geçmiş sayaç sessiz değiştirilmez.

## Limit dolduğunda kullanıcı ne görür?

Kaynak receipt alınabiliyorsa capture devam eder; semantik analiz `budget_deferred` olur. UI “Kaydedildi, henüz analiz edilmedi” der. Pending impact olan iş hazır/verified diye ilerletilmez. Bekleyen kaynak adedi/yaşı, tahmini kalan iş ve izinli seçenekler gösterilir: daha sonra işle, belirli işi öne al, deterministik yolu kullan, insan incelemesi yap veya ayrı onayla bütçeyi değiştir. Sıra önceliği limiti aşma izni değildir.

“Grafiği açtım, token harcandı mı?” sorusuna normal okuma/çizim için hayır; “bu çelişkiyi açıkla” yeni model analizi gerektiriyorsa önceden tüketim sınıfı ve mevcut limit görünür cevabı verilmeli. Detaylı maliyet dashboard'u P3'tür; P1'de limit/unknown/deferred ve temel usage görünürlüğü zorunludur.

## Ölçüm ve kabul

Aynı corpus, görev ve kalite eşiğiyle full-context baseline karşılaştırılır. Provider/model/sürüm, prompt, caching durumu, retry ve reasoning dahil toplam input/output, parasal maliyet, latency, yakalanan kayıt/ilişki recall, yanlış obsolete/false done ve insan review yükü raporlanır. Tasarruf oranı baseline sıfır/unknown ise hesaplanmaz. Token düşerken gerekçe recall düşüyorsa optimizasyon başarılı sayılmaz.

| ID | Kabul kriteri | Görev |
|---|---|---|
| TOK-01 | No-op/duplicate, graph gezme ve event replay LLM çağırmaz | T09b/T20b |
| TOK-02 | Token limitinde eksik kaynak/ilişki görünür, pending iş completed olmaz | T09b/T18c |
| TOK-03 | Aynı input iki worker'da tek evaluation üretir; ACL değişince cache paylaşımı durur | T09b/T21b |
| TOK-04 | Eşzamanlı çağrılar aynı kalan bütçeyi iki kez rezerve edemez | T21b |
| TOK-05 | Timeout/usage unknown reservation'ı erken boşaltmaz; retry ve child run dönem limitine dahildir | T21b |
| TOK-06 | Harici veri/ücret izni unset iken arka plan modeli çağrılmaz; source kayıt durumu doğru | T08b/T21b |
| TOK-07 | Host toplam tüketimi unknown ise sıfır veya garanti tasarruf gösterilmez | T21b/T24c |
| TOK-08 | Baseline kıyasında token/maliyet ile recall, yanlış kapanış ve review yükü birlikte raporlanır | T24c |

Bunlar planlı testlerdir. Gerçek provider kullanım/maliyet testi veya token tasarrufu sonucu henüz yok. Q05 ile profilin kullanıcı tarafından seçilebilir olması kabul edildi; Q03 veri/bütçe yanıtı [karar kuyruğunda](../delivery/decision-brief.md) hâlâ bekliyor.

## Kullanıcının proje ve görev bazında seçimi — Q05

**Kabul edilen ürün davranışı:** Kullanıcı proje başlangıcında nasıl ilerlemek istediğini seçer; proje içinde görev bazlı istisna kullanabilir ve daha sonra yaklaşımı değiştirebilir. `Balanced` önerilen başlangıç seçeneğidir, owner'ın bütün projeler için seçtiği varsayılan değildir.

Kurulumda üç anlaşılır seçenek: **Dengeli** (değişiklikleri grupla; karar/onay gereken işi öne al), **Daha güncel** (daha sık analiz, daha fazla tüketim olasılığı), **Ben istediğimde** (capture sürer; anlamsal analiz açık istekle). Her seçenek beklenen gecikme/tüketim/eksik analiz etkisini açıklar; yüzde tasarruf veya saniye garantisi yoktur. Kullanıcıdan ham token parametreleri seçmesi istenmez.

Etkin ayar = workspace güvenlik/harcama tavanları içinde task override, yoksa proje profili. Task override harcama veya veri çıkışı iznini genişletemez. Görev başında profil rozeti ve `Bu işte değiştir` bulunur; her küçük task için modal zorunlu değildir. Stratejik karar/çok büyük import gibi anlamlı durumda “bu işte daha sık analiz faydalı olabilir” önerisi gösterilebilir; kendiliğinden pahalı profile geçilmez.

Profil değişim önizlemesi mevcut → önerilen ayarı, pending işlerin etkisini ve tahmini maliyet sınıfını gösterir. `Bundan sonraki işler` veya `bekleyen şu işlere de uygula` seçimi açık olur. `effective_from`, policy revision, kapsam, actor ve gerekçe kayıtlıdır. In-flight çağrının oluşmuş olabilecek tüketimi geri alınmaz; yeni dispatch güncel üst sınırları kontrol eder. Daha az otomasyon seçilince queued semantik işler deferred kalır; capture verisi silinmez. Profil değişimi geçmiş muhasebeyi veya completed kanıtını yeniden yazmaz.

Yeterli gözlenmiş veri olduğunda UI “Bu projede şimdiye kadar Dengeli kullanıldı; son dönemde şu kadar bekleyen analiz var” gibi kaynaklı öneri sunabilir. Usage bilinmiyorsa uydurma maliyet/trend çıkarmayacak. Kullanıcı reddettiğinde tekrar tekrar öneri çıkarılmayacak; bildirim sıklığı sınırlı. Q03 tavanı verilmeden kullanıcı Daha güncel seçse de ücretli arka plan API açılmaz.

T21b ek kabulü: project/task inheritance doğru; override hard-cap aşamaz; mode switch queued/in-flight işleri doğru gösterir; otomatik pahalı escalation olmaz. T24c profillerin kalite/gecikme/tüketimini aynı corpus ile karşılaştırır.

## Büyük veya belirsiz tüketim için ek onay

[Yüksek token riski ve ek onay](../product/token-risk-and-approval.md) bütçe dolmadan önce de büyük import, tekrar context, fan-out, retry ve belirsiz toplamı değerlendirir. Deterministik preflight → policy içinde olağan iş / insan risk onayı / hard-cap nedeniyle blocked ayrımı; onay kapsamı, stale kontrolü ve koşu sırasında yeni dispatch durdurma burada tanımlıdır. Onay bütçe veya veri izni yaratmaz; child/run bölme toplamı sıfırlamaz. TRA-01–10 planlıdır; T09d/T19b/T24k ilk model dispatch kapısını ve UX'i tamamlar.

[Çoklu chat ve lag](multi-chat-and-processing-lag.md) ortak proje kayıtlarına hedefli retrieval, session başına frontier ve bounded catch-up kullanır. Geride kalmak bütün chat geçmişini pahalı bir çağrıyla yeniden işleme yetkisi değildir.

## Sözlük/pattern ile ön eleme önerisi

[Metin adayları ve deney planı](lexical-prefilter.md), mevcut parser-first ve structured duplicate bypass yaklaşımını detaylandırır. Sürümlü TR/EN sözlük + bağlam guard'ları ucuz aday saptama içindir; kelime eşleşmesi task completion veya işlem yetkisi değildir. Yapılandırılmış sinyal varsa ikinci extraction önlenebilir, fakat assistant raporu yine kanıt/onay sayılmaz.

İlk yöntem shadow modda ölçülür. Eşleşmeyen içerik sırf keyword yok diye atılmaz; fallback, insan review ve ek output/schema maliyeti toplam tüketimde sayılır. İlk cevap üretme maliyetini azaltma iddiası yok. Sözlük ancak aynı kalite/coverage koşulunda toplam çağrı/token ve kullanıcı yükünü düşürürse ekonomik başarıdır. LEX-01–08 planlı; gerçek model pattern analizi ve tasarruf sonucu yok.

## Dil tespiti ve çeviri ekonomisi

[Dil sözleşmesinde](../product/language-and-localization.md) ilk tercih açık çıktı dili veya hafif yerel detector adayıdır; yalnız dil tespiti için varsayılan LLM çağrısı yok. Gerekli extraction/generation çağrısı doğrudan etkin dilde üretebilir; İngilizce ara çıktı + ayrı çeviri çağrısı varsayılan değil. Dil/karakter sayısı aynı token maliyetini garanti etmez; provider/model/locale bazlı input-output/retry ve kalite ölçülür.

Sabit UI metinleri locale kataloglarından çizilir. Tüm geçmişi çevirme, çok dilli embedding/reranking veya çok dilli türev üretme ayrı ihtiyaç/egress/bütçe ve risk onayı gerektirir. Cache language/policy revision'a bağlı, source ACL korunur; model kapalıyken fallback/coverage görünür. P2 otomasyon önerisi T25a/T26c ve LANG-01–08 ile ölçülecek; tasarruf sonucu yok.

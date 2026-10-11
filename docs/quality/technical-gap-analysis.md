# Teknik boşluk analizi ve kapanış kaydı

**İnceleme: 2026-10-11 · Başlangıç ref: `669c6e3ebd56ea232fb259b124ad476957c7107c`.** Kullanıcı önce ölçüm ayrıntılarını, ardından bütün akıştaki diğer boşlukları ve neden incelendiğini kalıcı kaydetmemizi istedi. Bu dosya o incelemenin izidir; yeni model/oturum bağlamı buradan kurtarabilir. Canonical gereksinim, ADR, backlog veya uygulama kanıtının yerine geçmez. Tek güncel belge seti korunur; eski tasarımlar Git ref'inden okunur.

## 1. Sonuç ve kanıt sınırı

Ürünün esas domain kuralları büyük ölçüde belgelenmiş: capture/karar/uygulama ayrımı, append-only history, AND/OR/unknown, scope/ACL, kalıcı sorular, geç yanıt, insan onayı, receipt/processing ayrımı, parent/child bütçesi, replay ve privacy lifecycle. İnceleme bunları yokmuş gibi yeniden keşfetmedi.

**İki doğrulanmış doküman hatası düzeltildi:** T24p iki farklı alt göreve verilmişti; ölçüm satırı ve güncel referansları T24q oldu, dil T24p/T25a bağı korunur. Source dedup tarifleri scope/epoch bakımından farklıydı; event/runtime tarifleri DB ilişkileriyle hizalandı. İlk hata önceki ölçüm belge güncellemesinde oluşmuştu. Eski status kaydı değiştirilmez; düzeltme yeni kayıtla açıklanır.

Diğer bulguların bir bölümü mevcut ilkeleri executable sözleşmeye dönüştürme ayrıntısı, bir bölümü zaten backlog'da bekleyen implementasyon/deney, bir bölümü owner kararıdır. [IC-01–08](../architecture/implementation-contracts.md) teknik ayrıntı önerilerini tamamlar. Bunlar accepted ADR, çalışan schema/DB/API veya test pass değildir. Ürün henüz documentation/discovery aşamasındadır; “bütün açıklar kapandı”, güvenli/ölçeklenebilir veya üstün olduğu sonucu çıkmaz.

### Yöntem ve kapsam

- Non-truncated remote tree ve local mirror üzerinden **93 metin dosyasının envanteri** ve referans/başlık/ID taraması; local metin toplamı 912.928 karakter. Sayı modelin her satırı semantik olarak denetlediği anlamına gelmez.
- Domain, runtime, event/reconciliation ve ilgili veri/izin/budget/storage/connection sözleşmeleri hedefli çapraz okundu; soru, task AC/DoD, graph, UI/operations, çoklu chat, dil, engine, backlog ve ölçüm bağları karşılaştırıldı. Büyük belgelerde ilgili bölüm odaklı okuma yapıldı.
- Değiştirilecek 15 mevcut dosya başlangıç commit'inden tekrar alınarak mirror ile birebir karşılaştırıldı. Diğer dosyaların tümü için bu tur birebir remote doğrulaması yapıldığı iddia edilmez.
- Çakışan alt görev ID'leri read-only taramayla yeniden üretildi. Bu yüzden test betiğinin yetersizliği varsayım değil gözlenen bulgudur.
- Birincil [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) ve [MCP transport 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) belgeleri hedefli okundu. Bunların uygulanma profili öneridir; bu MCP sürümünün her host'ta desteklendiği varsayılmaz.
- Bu tur geniş upstream repo taraması, upstream kod çalıştırma, runtime/security penetration testi, gerçek transcript import, provider/model çağrısı veya lisans hukuki görüşü yapılmadı. Önceki [Graphiti/Langfuse source incelemesinin](../discovery/ecosystem-research.md#ölçüm-yöntemi-için-hedefli-takip--2026-10-11) sabit ref ve kapsamı kendi kaydında; burada bütün upstream kodlarının tekrar denetlendiği iddia edilmez.
- Yeni Mermaid topolojisi gerekmedi: component/faz/otorite değişmedi. Mevcut 34 source block korunur; source inventory kontrolü rendering veya runtime proof değildir.

### Durum nasıl okunacak?

**Belge durumu ve ürün durumu ayrı eksenlerdir.** “Düzeltildi” yalnız açıklaması yapılan doc/checker hatası için; “ayrıntı önerildi” engineering review/test bekler; “bekliyor” owner/uygulama/ölçüm kapısı kapanmamış demektir. Tüm ürün conformance sonuçları şu anda **not_run**. Aşağıdaki liste 24 inceleme kaydıdır; 24 yeni engine veya 24 yeni ana görev değildir.

## 2. Uçtan uca bulgu ve kapanış matrisi

| ID / sınıf | Kanıt ve neden incelendi? | Bu tur yapılan / halen açık | Kapanış kanıtı ve sahip görev |
|---|---|---|---|
| TG-01 · Doc conflict | [Backlog](../delivery/backlog.md) dil ve yeni ölçüm tablolarında aynı T24p; checker yalnız ana görevleri tekil kontrol ediyordu. Devralan LLM yanlış işe bağlanabilirdi | **Düzeltildi:** ölçüm T24q, dil T24p değişmedi; canonical subtask definition uniqueness kontrolü eklendi | Docs lint + geçici kopyaya duplicate enjekte edildiğinde fail; ürün testi değildir |
| TG-02 · Doc conflict | [Event log](../architecture/event-log.md) source key epoch/scope'u eksik anlatırken [DB ilişkileri](../architecture/data-relationships.md) ekliyordu. Session rotation farklı olayı birleştirebilir | **Düzeltildi:** scope/session/epoch/event/revision açık; quarantine owner ACL'si ayrı, content hash kimlik değildir | T05/T06d; same ID across scope/epoch, import tekrar ve binding fixture. Runtime not_run |
| TG-03 · Spec detail | [Runtime](../architecture/runtime-contracts.md) alan/enum/hata listesi mantıksal; executable schema, null/absent, DTO ve physical FK mapping seçilmedi | IC-01 önerisi; bu bilinçli stack kapısını doküman hatası sayma | T04a/T04c/T05; schema conformance + DB constraint + transport mapping |
| TG-04 · Spec detail | Source span/revision korunuyor fakat UTF-8 byte/codepoint/UTF-16 koordinat profili ortak değil. TR/emoji yanlış alıntıya neden olabilir | IC-01 adapter mapping/round-trip ayrıntısı önerildi; profil/library seçimi açık | T04/T09/T10; multilingual exact source quote, CRLF, invalid boundary negatifleri |
| TG-05 · Spec detail | Approval digest var, ortak serializer/canonicalization yok. Aynı UI preview farklı byte/hash üretebilir; array sırası anlamlı | IC-02 profil, girdiler, null/array/Unicode ve server üretimi önerildi; JCS dependency seçilmedi | T08a/T13; iki component golden digest, değişen operation/AC/scope conflict |
| TG-06 · Spec detail | [Reconciliation](../architecture/reconciliation-impact.md) kaynaklı JSON ister; truncation/duplicate-key/foreign ID/unknown operation için tek decoder sözleşmesi eksik | IC-01 strict pipeline ve partial coverage önerildi. Schema geçişi authority değildir | T09/T10/T08; bozuk/yarım çıktıda no-op veya auto apply yok; source interval kaybolmaz |
| TG-07 · Spec detail | [Token ekonomi](../architecture/routing-token-economy.md) reserve/settle var; decimal hassasiyet ve ay sınırı/geç usage/pricing revision ayrıntısı ortak değil | IC-03 exact amount, period/price revision, duplicate settlement ve unknown liability önerildi | T21/T21c; concurrency, rollover, retry/child, cancel unknown, overrun negatifleri |
| TG-08 · Spec detail | [GAP](../product/intent-to-reality-gap.md) exact hedef şartını koyuyor; değişen branch/çoklu local dosya okuması bütün snapshot'ı kanıtlamayabilir | IC-04 immutable Git ref ve unstable/partial observer ayrıntısı; algoritma seçimi/test bekler | T02d/T14b/T14d; branch move, concurrent edit, yanlış worktree ve eksik artifact |
| TG-09 · Spec detail | [Task context](../product/task-context-and-acceptance.md) gerekli AC/DoD ister; boş required set'in otomatik all-pass olması belirtilmemiş | IC-05 empty/applicable count ve explicit human assessment önerisi | T14/T20; boş AC/not_applicable-only completion oluşturmaz |
| TG-10 · Spec detail | [Runtime](../architecture/runtime-contracts.md) snapshot/stale bilgili; gecikmiş projection ile command readiness kontrolünün uygulama sınırı net değil | IC-05 canonical seq/watermark ve apply guard önerisi | T12/T13/T18; stale read model ve OR edge race onayı geçmez |
| TG-11 · Spec detail | [Domain](../architecture/domain-model.md) yürütme cycle'ı reddet veya bloke review der; tek wire mapping seçilmedi | IC-05 canonical reject + candidate review önerisi; bilgi graph'ı DAG'a zorlanmaz | T11; dependency/parent/supersedes cycle ayrı, related_to döngüsü yasak sayılmaz |
| TG-12 · Capability pending | [Adapters](../architecture/capture-adapters.md) conditional yetenekler; event adı veya MCP desteği transcript/actor/access garantisi değil | Mevcut T02 kapısı korunur; IC-06 host/build/transport ayrımı eklendi. Q02-R1 A ilk yol seçildi, B sonraki hedef; host/OS/capture kanıtı açık | T02/T16/T17; seçilen sürümde event/log/export, actor/revision, gap ve permission kanıtı |
| TG-13 · Implementation pending | [Identity](../architecture/identity-access.md) ve T04b local auth'ı ister; login/bootstrap/cookie/agent secret/session recovery çalışan tasarım değil | IC-06 browser ve agent ayrımı önerildi. Auth skip “local olduğu için güvenli” sayılamaz | T04b/T05/T08b; unauth/Origin/Host/spoof/revoke testleri; gerçek özel veri öncesi |
| TG-14 · Implementation pending | [Çoklu chat](../architecture/multi-chat-and-processing-lag.md) iki frontier/fencing/bounded queue tanımlar; admission/crash/gap işleyicileri kodlanmadı | IC-07 fault injection noktaları ve receipt oracle'ı hazır. Hızlı konuşma kayıpsız işleme vaadi yok | T06/T07/T15; commit/ack crash, holes, queue full, stale lease; V19–V21/LIM |
| TG-15 · Implementation pending | [Pending sorular](../product/pending-questions-and-late-answers.md) late/orphan/ambiguous ve approval ayrımını kapsıyor; resolver/UX yok | Tasarım boşluğu değil implementasyon borcu. Geç A cevabı güncel seçeneği otomatik onaylamaz | T13e/T18e/T24f; out-of-order/option revision/two A-B questions/source ACL fixture'ları |
| TG-16 · Implementation pending | [Agent/team](../architecture/agent-and-team-operation.md) human/agent yetki ayrımı var; gerçek orchestrator event/task correlation denenmedi | Hidden reasoning okunabilir sayılmaz; capability yoksa run metadata/report dar coverage | T02/T05/T08/T30; forged delegation, fan-out ancestry, child run ≠ task verified, human approval route |
| TG-17 · Implementation pending | [Memory/resume](../product/resume-package-and-memory.md) source/archive/delta ve ACL açık; host'a verilmiş context'i revoke sonrası geri silemez | IC-06 teslimden sonraki kontrol sınırı açık. Geçerli cache bile host otomatik güncel demek değil | T18/T18h/T25; revocation/delta/resync + fresh-session test; Q11 teslim yolu açık |
| TG-18 · Implementation pending | [UI/operations](../product/administration-and-operations.md), graph/approval/task tabs belgeli; gerçek UI DTO/state/error/freshness akışı yok | Mevcut UX kuralları korunur. Observer unknown/missing/stale ve rejected/cancelled/obsolete gösterimi test ister | T19–T24; tıklama/keyboard/state akışı, before-after, pending question, effective AC/evidence |
| TG-19 · Owner + implementation | [Storage](../architecture/storage-memory-capacity.md) DB/blob/TTL/purge/restore tanımlar; encryption/key recovery ve gerçek retention policy seçilmedi | IC-07 kanıt planı. 1C kaynak koruma sonsuz disk veya süresiz saklama onayı değildir | OPEN-08/12 + T23c/T23d; key loss, WAL/blob/tombstone/grant restore; özel veri öncesi |
| TG-20 · Owner + load measurement | [Limits](../architecture/resource-limits-and-abuse.md) ve storage S0/S1 aday eşikler; donanım/traffic/SLO ve limit default'ları kalibre değil | IC-07 sonlu profil/load raporu. DB migration model latency'yi otomatik çözmez | OPEN-12/16 + T04d/T06f/T23d; sustained burst/fairness/disk/queue/error+p95 ve gap |
| TG-21 · Future phase | Ekip/P4 planı var; çok kullanıcı login/invite/offboarding, PostgreSQL isolation, admin erişimi ve cloud deployment uygulanmadı | Tek owner içinde agent kimliği P1'de kalır; remote multi-human/distributed sync MVP'ye sessiz eklenmez | T30 + C/MU planı; OPEN-14/15; ikinci cihaz/kullanıcı ihtiyacında team gate |
| TG-22 · Measurement pending | [Protokol](evaluation-protocol.md) ve CHAIN-01 yalnız illustrative; 7 checkpoint büyük corpus/holdout veya gerçek scorer değil | IC-08 katman sırası; native/manual/config/extension/own aynı oracle/ref ile kıyaslanır | T01f/T03f/T24q; bağımsız gold, scorer error=incomplete, real target ve cost/latency/review kanıtı |
| TG-23 · Research/owner pending | [Kod alım değerlendirmesi](../discovery/code-reuse-assessment.md) ve [ekosistem](../discovery/ecosystem-research.md) pinned kaynak/örnek gösteriyor; tam export/dependency/lisans closure ve Q13 seçim yok | Geniş tarama yerine seçilen küçük adayın conformance+license closure'ı; upstream özellik ürün üstünlüğü kanıtı değil | T03d/T03e/T03f; exact package/file/transitive notices/security fit, aynı negatif oracle; Q13 |
| TG-24 · Delivery check limitation | Docs lint link/ID/scope kontrolü, doğal dil tutarlılığı ve release/eval doğruluğu değil. TG-01 pass aldığı halde vardı | Duplicate check genişletildi; bu analiz expected failure/decision/evidence ayrımını devre ekledi | Her sınır değişiminde hedefli semantic review + implementation tests; “lint geçti, ürün eksiksiz” denmez |

## 3. Kapılar: hangisi gerçekten neyi engeller?

| Kapı | Kullanıldığı ilk adım | Gerekli kanıt / açık soru | Beklemeden yapılabilecek |
|---|---|---|---|
| G0 · Deney tanımı | T01 → T02d → T03a | Golden case/ref, kapsam ve stage oracle; Q02-R1 A seçildi, somut kaynak/hedef ve izinler açık | Sentetik corpus, typed oracle/spec; nihai production stack gerektirmez |
| G1 · İlk dış kaynak | Capture/target/API sınırı ilk çalıştığında | IC-01/06, finite ingress, exact selected source/target, capability ve source/read grant | Mock adapter, permission denial/receipt fixture |
| G2 · İlk model dispatch | Her ücretli/harici model çağrısı öncesi | Q03 somut provider/veri/tavan; IC-03 + egress ve risk policy | No-model code oracle, model output sentetik decoder fixture |
| G3 · Canonical apply/complete | İlk approval apply veya verified sonucu | IC-02/04/05, human authority, AC/evidence/revision ve transaction oracle | Candidate preview/negative cases; gerçek tamamlandı iddiası yok |
| G4 · İlk gerçek özel veri | Private transcript/evidence saklandığında | OPEN-08/12 retention/key/backup; ACL/redaction/purge/recovery deneyi | Sentetik load/fault planı, policy önerisi |
| G5 · Yatırım kararı | T03c/pilot değerlendirmesi | TG-22 fair baseline + critical failure + quality/cost/review + risk; owner build/extend/stop | Kaynaklı hipotez ve sınırlı prototip önerisi |
| G6 · Ekip/uzak cihaz | P4 merkezi servis veya remote multi-user | Identity/member lifecycle, project isolation, admin sınırı, restore/capacity, deployment | Mantıksal rol/ER/MU planı; distributed DB/sync başlatılmaz |

G0–G6 her zaman tek doğrusal release sırası değildir; G2 kullanılmayan no-model prototipi engellemez. G1/G3'ün ilgili güvenlik ve authority kontrolü ilk kullanımda gerekir, P3 hardening'e ertelenmez. Gelecek ekip gap'i bütün P0'ı durdurmaz. Prototype sentetik/mock ise neyi taklit ettiği raporda görünür.

## 4. Neden bu kaynaklara baktık, ne aldık?

| Kaynak ve derinlik | Cevaplamak istediğimiz | Çıkarım / yapılmayan |
|---|---|---|
| Kendi repo, başlangıç immutable ref; envanter + hedefli normatif çapraz okuma | Ürün ilkesi kodun ortak sözleşmesine dönüşüyor mu? Aynı ID/state/key belgeler arasında aynı mı? | İki doc defect gözlendi; serializer/coordinate/money/snapshot sınırları için IC önerileri. Runtime bug veya tam semantik audit değil |
| RFC 8785, birincil specification, 2026-10-11 | Aynı approval içeriğinden tekrarlanabilir digest nasıl üretilecek? | Canonicalizer seçenekleri ve golden vektör ihtiyacı; kütüphane/standard adoption yok. IC-02 teknik notu |
| MCP 2025-11-25 transport, birincil specification, 2026-10-11 | Local/HTTP/stdio güven sınırı ve disconnect semantiği nedir? | IC-06 host capability/transport sınırı; MCP bütün sohbeti izleyen otomatik bus sayılmadı |
| Graphiti değerlendirme kaynakları, önceki pinned hedefli okuma | Gold/context/judge bağları bağımsız mı? Hazır scorer örneği taşınabilir mi? | [Önceki raporda](../discovery/ecosystem-research.md) scope/ref; typed authority/target oracle ayrı. Bütün Graphiti kodu veya runtime bug taraması yapılmadı |
| Langfuse SDK experiment/test kaynakları, önceki pinned hedefli okuma | Evaluator hata/eksik skorunu nasıl raporlar? Human/code/model scoring nasıl ayrılır? | Aynı önceki rapor/protokol; critical missing score bizim gate'te incomplete. Platform başarısı veya otomatik truth judge benimsenmedi |
| Diğer benchmark/reuse kayıtları, bu tur referans kontrolü | Aynı çözümü yeniden icat ediyor muyuz, native/extension yeterli olabilir mi? | T03c ve Q13 korunur; geniş repo keşfi veya yeni adoption kararı yok |

Research stop kuralı: seçilen ilk sınır için candidate+authority+error+closure test açıklanabiliyorsa daha geniş taramayı bırak; ilgili fixture/deneye geç. Kaynak “iyi örüntü” gösterir; bizim invariant'a uyumu test etmeden alınmaz. Kopyalama, lisans ve citation stratejisi [licensing](../governance/licensing.md) otoritesindedir.

## 5. Owner'a adım adım sorulacaklar

Cevabı verilmiş Q01/Q04/Q05/Q07/Q09/Q10/Q12 tekrar açılmaz. Engineering serializer, Unicode offset veya DB constraint seçimini soyut A/B kararı diye kullanıcıya yüklemez; conformance önerisi/testi hazırlar. Aşağıdaki sıra görüşme kuyruğudur; cevaplanmış madde durumu ayrıca gösterilir.

1. **Q02-R1 / cevaplandı, 2026-10-11:** Kullanıcı maliyet odağıyla A'yı (açıkça aktarılan Claude/ChatGPT parçası + tek read-only uygulama hedefi) ilk pilot için seçti; B Codex coding oturumu + tek repo sonrasında görülmek isteniyor. C seçilmedi, alternatif korunur. A capture entegrasyonuna bağımlı olmadan değeri sınar; en düşük maliyet iddiası ölçülmedi. MCP bağlam/öneri bağlantısı B için bir adımdır, otomatik transcript capture kanıtı değildir. Somut kaynak/hedef/host/OS ve izinler açık; bu ilk yol tercihini tekrar sorma.
2. **Q03 / somut veri ve maliyet:** Seçilen kaynak için no-model/sentetik başlangıç mı, ayıklanmış gerçek parça hangi provider'a hangi tavanla gönderilebilir mi? Öneri ve exact veri kapsamı önceden hazırlanır; genel “API kullanabiliriz” tüm konuşma/ücret izni olmaz.
3. **OPEN-08/12 / saklama-kurtarma:** Gerçek veri önce retention, purge/export/backup ve key-loss trade-off'larını somut küçük planla sor. 1C kaybı önleme tercihi korunur.
4. **Q11 ve Q06 / devam ve context export:** İlk deney önizle/kopyala mı; milestone context Markdown otomatik mi? UI/export örneğiyle sor; host başlatma veya Git push ayrı yetkidir.
5. **Q08 / subtask:** Parent AC korunarak öneriyle bölme mi, yalnız talep mi? Split preview ve fayda/bedel hazırlandıktan sonra sor.
6. **Q13 / reuse yolu:** Native/config/extension ile küçük reuse/own implementation'ı aynı oracle sonucu ve package/license closure'la birlikte sun; tüm platform fork'ı soyut varsayılan olmaz.
7. **OPEN-09/16 / pilot kararı:** Ölçümden sonra gerçek hata/review/maliyet ve incomplete oranlarıyla başarı/stop eşiğini kararlaştır; mevcut yüzde hedeflerini yapılmış taahhüt sayma.
8. Public release/lisans/commercial/team kapsamı ilgili faza gelince somut seçenekle sor; bugünkü docs güncellemesi izin oluşturmaz.

Q02-R1 cevabı [decision brief](../delivery/decision-brief.md) ve ilgili pilot planlarına işlendi; yeni bağımsız ürün kararı ID'si değildir. Sıradaki odak Q03'ün ilk deneyde ek ücretli model API'si gerekip gerekmediği kısmıdır. Öneri sentetik/elle etiketli fixture + deterministik kontrolle başlamak; serbest metin extraction başarısını bununla iddia etmemek. Kullanıcı soruları düz metin seçenekleriyle gösterilir; widget kaybolduğu için kayıt dosyada da korunur. Cevap/izin eksikse ilgili dispatch veya gerçek veri okuma kapısı pending kalır.

## 6. Sonraki oturumun kurtarma ve kapanış prosedürü

1. [Status](../delivery/status.md) ve [handoff](../delivery/llm-handoff.md) ile başlayıp bu dosyanın source ref'ini doğrula. Tarihsel bulguyu bugünkü runtime state sanma.
2. İlgili TG kaydından IC ve canonical task'a git. Yeni source/code/owner cevabı varsa önceki finding'i silmek yerine tarihli update ekle.
3. Her kapanış kaydı: finding ID, neden, source/input ref, değişen implementation/doc ref, test/runner/environment, expected-observed outcome, doc status, runtime status, decision/permission status ve kalan risk taşır. Link/JSON pass yalnız doc status'ü kapatır.
4. Revisit tetikleri: schema/stack/transport değişimi, yeni provider/host build, source format/epoch değişimi, pricing/policy revizyonu, ilk gerçek private veri, ilk remote user, purge/restore, yeni false closure/approval veya scorer error.
5. Bir TG kapanınca tüm proje “done” olmaz. Canonical task kabulü ve scoped evidence'i [backlog](../delivery/backlog.md) taşır; checklist'in kendisi completion authority değildir.

### Bu belge tesliminin doğrulaması

Doküman kontrolü ve duplicate-ID için negatif regresyon kontrolü teslimde çalıştırılır; gerçek sonuç status/final raporuna yazılır. IC-01–08/TG runtime testleri **not_run**; yeni dependency, model/API çağrısı veya çalışan prototip yok. Yeni çizim oluşturulmadığı için diagram source inventory dışında render iddiası yok. GitHub commit ve read-back yalnız belge teslim kanıtıdır.

**Gerçekleşen yerel kontrol:** doküman betiği geçti: 87 Markdown, 893 yerel bağlantı, 32 scope, 30 ana görev, 14 MVP AC, 17 feature, 10 engine; 34 Mermaid/15 belge inventory eşleşti. Geçici repo kopyasında bilerek ikinci T24p definition eklenince checker hata verdi; asıl dosyalar bu negatif testte değiştirilmedi. 24 tekil TG ve 8 IC bölüm kimliği, T24p dil/T24q ölçüm ayrımı ve T25a dil bağı ayrıca doğrulandı. Bu sonuçlar runtime testi değildir. Remote teslim sonucu commit/read-back raporunda ayrıca belirtilir.

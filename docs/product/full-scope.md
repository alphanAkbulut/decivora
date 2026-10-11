# Tam kapsam — kalıcı yetenek envanteri

Tüm satırlar **planlanmıştır**; bu belge çalışan özellik listesi değildir. P0 keşif, P1a teknik kanıt, P1b MVP, P2 kapsam genişletme, P3 maliyet/entegrasyon, P4 ekip/ürünleşme. Ayrıntılı görev eşlemesi [backlog](../delivery/backlog.md) içindedir.

Kullanıcı deneyimi [özellik kataloğunda](feature-catalog.md); konuşma→özellik→engine→görev→doğrulama eşlemesi [izlenebilirlik matrisinde](../quality/traceability.md). Bunlar kapsamı daraltmaz veya uygulanmışlık statüsünü değiştirmez.

| ID | Korunan yetenek / iş kuralı | İlk teslim / genişleme | Kabul işareti |
|---|---|---|---|
| CAP-01 | Fikir, finding, risk, gereksinim, task, prompt, belge talimatı, karar ve bekleyen karar yakalama | P1a/P1b | Kaynak mesajı olan tipli aday kayıt |
| CAP-02 | Pasif Claude Code ve Codex adapter'ları | P0 araştırma; P1b iki ayrı doğrulama | Her yüzeyin sürüm ve olay kapsaması raporlu |
| CAP-03 | ChatGPT→Codex ve Claude Chat→Claude Code sürekliliği | P1b açık aktarım; P2 otomasyon | Kaynak/prompt/hedef execution bağı korunur |
| CAP-04 | Sağlayıcılar arası sohbet hafızası, import ve gelecekte izinli kısayol/eklenti | P2 | Aktarım türü otomatik veya manuel diye açık gösterilir |
| CAP-05 | Incremental checkpoint, toplu capture, ilişki koruma, crash/retry | P1a | Tekrar import ek kayıt üretmez; yarım change set kalmaz |
| PRJ-01 | Çoklu proje, repo olmadan araştırma, değişmeyen kimlik ve binding | P1a/P1b | Aynı adlı iki projenin verisi karışmaz |
| KNO-01 | Kaynak ve sürüm taşıyan canonical knowledge; active/history ayrımı | P1a | Eski karar tarihçede, onaylı yenisi aktif |
| KNO-02 | Duplicate, refinement, contradiction, supersession, rejected revival uzlaştırması | P1a temel; P2 semantik | Gerekçeli diff; belirsiz merge otomatik uygulanmaz |
| KNO-03 | Idea evaluation; destek ve karşı kanıt, belirsizlik | P1b/P2 | Tek bir “doğruluk puanı” yerine değerlendirme kaydı |
| GRF-01 | Tipli ilişkiler ve karar farkındalıklı dependency graph | P1a/P1b | Her task'ın neden var olduğu izlenir |
| GRF-02 | Çoklu gerekçe ve AND/OR koşulları; eksik ilişki taraması | P1a/P2 | Bir gerekçesi kalan iş yanlış iptal olmaz |
| IMP-01 | Impact triggers ve hedefli alt grafikte yeniden değerlendirme | P1a | Karar değişince keep/update/review/obsolete önerileri |
| IMP-02 | Gereksinim, teknoloji, özellik iptali, kanıt geçersizliği ve prompt eskimesi etkileri | P1b/P2 | Değişikliğin downstream çıktıları izlenir |
| APR-01 | Hazır başlık/açıklama/AC; çoktan seçmeli ve toplu onay, ertele, reddet, karşılaştır | P1b | Kullanıcı metin yazmadan değişikliği karara bağlar |
| APR-02 | Decision Pending, unutulan onay ve bekleyen iş kuyruğu | P1b | Konu/alternatif/kaynak/bloklanan işler görünür |
| VER-01 | Claimed/implemented/verified ayrımı, dosya/test/commit/PR kanıtı | P1a temel; P2 geniş | Kanıt yoksa verified olamaz |
| VER-02 | Kanıt tazeliği, başarısız test sonrası reopening, kısmi ilerleme | P1b | Kabul kriteri değişince eski test yeterli sayılmaz |
| AUD-01 | Append-only olaylar, projection, compensating event, audit ve backup | P1a/P1b | Replay aynı sonucu verir; agent geçmişi değiştiremez |
| UX-01 | Project selector, Inbox/Review, Board, Graph, Timeline | P1b | Aynı seçili kayda tüm görünümlerden ulaşılır |
| UX-02 | Knowledge health, coverage, next-ready task, arama, filtre | P1b temel; P2 geniş | Bekleyen/yarım/eski/unknown açıkça ayrılır |
| UX-03 | Çalışma ekranı yanında kalıcı görünürlük, IDE paneli ve uygulama entegrasyonu | P2 araştırma | Host desteği kanıtlı; tarayıcı paneli fallback |
| ROU-01 | İş niteliği ile yürütücüyü ayrı etiketleme, insan için basit iş seçeneği | P1b | HUMAN ve HUMAN_DECISION aynı alan değildir |
| ROU-02 | Risk/yetenek/bütçe bazlı deterministic/API/model/insan routing | P2/P3 | Basit kontrol modele gitmez; limitte durur |
| CST-01 | Minimal MCP, delta context, cache, batch, retrieval budget | P1a/P1b | LLM input ve tool overhead ayrı ölçülür |
| CST-02 | Tahmini/gerçek token, model, fiyat sürümü, tasarruf raporu | P1b telemetry; P3 rapor | Bilinmeyen kullanım sıfır gösterilmez |
| INT-01 | GitHub kanıt bağlantısı, Linear/Jira ve diğer dış sistemler | P2 read; P3 write | Yetkili outbox, tekrar/çatışma kontrolü |
| INT-02 | Agent'lar arası ortak hafıza ve execution lineage | P1b temel MCP; P2 geniş | Bir agent'ın kaydı diğerinde aynı sürümle okunur |
| GOV-01 | Veri minimizasyonu, onay, proje izolasyonu, injection savunması | P1a/P1b | Kaynak metni sistem komutu olarak yürütülmez |
| GOV-02 | İhracat/taşınabilirlik, retention ve silme istisnası | P1b/P2 | Runtime private; export anlaşılır ve yeniden alınabilir |
| TEAM-01 | Takım/organizasyon; insan/agent yetkileri, davet/offboarding, özel/ortak hafıza, cloud sync, enterprise audit, managed automation | P1 kimlik temeli; P4 ekip | ADR-0009/0010; MU01–MU18 ve C01–C06 ekip kapıları; onaylı policy/işletim |
| OSS-01 | Açık kaynak çekirdek, iyi demo, kurulum, katkı ve olası open core | P3/P4 | Public release ayrı kullanıcı kararı |
| EVAL-01 | Benchmark, golden corpus, pilot, yönetim yükü ve yanlış öneri ölçümü | P0 ve tüm fazlar | Sonuç, sürüm ve örneklemle yayımlanır |

“Otomatik task kapanışı” VER-01 ve policy sınırlarıyla mümkündür; scope kararlarını kendi başına alma anlamına gelmez. “Universal” hedef kapsamı anlatır, bugün mevcut platform erişimi iddiası değildir.

INT-02 tek insanın çok-agent çalışmasını da kapsar; TEAM-01 yalnız insan sayısına indirgenmez. [Agent ve ekip işletimi](../architecture/agent-and-team-operation.md) run/task ayrımını, gözlem erişimini ve ürünü ekibine kuran kullanıcının akışını detaylandırır. P1b temel çok-agent takip pilotu; P2/P3 yetkili execution genişlemesi; P4 çok insanlı kurulum/üyelik/işletim kapıları korunur. Özel iç muhakeme erişimi ürünün ön koşulu değildir.

Ekip isteğinin ayrıntısı yeni bir ürün değildir: TEAM-01, PRJ-01, GOV-01/02, AUD-01, APR-01 ve INT-02 kapsamlarını açar. [Fazlı plan](../delivery/team-data-plan.md) rol/agent yönetimi, log sınıfları, DB kapasitesi ve hafıza ömrünü işlere bağlar. Cloud/offline sync tam kapsamda kalır; bugünkü DB migration tasarımı sync'in uygulanmış olduğu anlamına gelmez.

## Açıklanabilir task ranking takip kapsamı

2026-10-10 kullanıcı talebi mevcut GRF-01/APR-02/UX-02/ROU-01 içinde korunur: 40+ ilerlemeyen task'ın nedenleri, blocker/dependency, business/product value, critical path veri yeterliliği, aging, effort, uncertainty, context readiness ve risk; downstream impact explanation ve next actionable; owner/admin ve önceden yetkili üst agent için board. [Ayrıntı, seçenekler ve kabul](priority-and-flow.md). MVP deterministik öneri/board, Faz 2 context-aware scoring/simülasyon/UX adayı; nihai faz feasibility kanıtına bağlıdır. Rank canonical priority değildir; insan PO scope/value ve karar haklarını korur. Bu doküman kaydı çalışan özellik veya yeni otonomi yetkisi değildir.

## Bekleyen işe devam ve dış hafıza deneyi

2026-10-11 yapıştırılan konuşma; F04/F08/F11/F13 ve KNO-01/02, APR-02, UX-02, CST-01/02, GOV kapsamını ayrıntılandırır. [Devam paketi](resume-package-and-memory.md) kaynağı, yapılmış/claim/unknown ayrımını, kalan AC/DoD, güncel karar ve next-action'ı taşır. [Spike-1 v1](../delivery/spike-1-v1.md) temiz oturumda memory yeterliliğini ölçen öneridir; “unutuldu” yerine kaynaklı yaş/kanıt/coverage etiketi kullanır. A önizle/kopyala başlangıç önerisi, B host başlatma ayrı capability/izin araştırmasıdır. Mevcut tam vizyon ve MVP daraltılmadı; Wedge-0 yeniden adlandırması kabul edilmiş karar değildir.

## Güncel ilk odak ve gerçekleşme ayrımı

[Tasarım revizyonu 03](current-direction.md), mevcut KNO/APR/VER/INT/UX/EVAL kapsamını **öneri→güvenilir seçim→artifact→exact hedef uygulaması→güncel uygunluk** üzerinden sınar. [GAP sözleşmesi](intent-to-reality-gap.md) generated/reported/observed/unknown ve test/deploy ayrımını; [ADR-0011](../architecture/adr/0011-target-application-evidence.md) teknik veri karşılığını tanımlar. 32 scope maddesi korunur; bu yeni ana feature/engine değildir.

P0 deneyinde tek hedef read-back mock/sentetik veya açıkça izinli seçilmiş adapter olabilir. Bu, bütün GitHub entegrasyonunu P2'den taşımaz, pasif capture başarısını varsaymaz veya P1b iki-adapter kabulünü kaldırmaz. İlk yatırım kararı native/extend/build/durdur sonucuna açıktır; ürün iptali kabul edilmedi.

## Konuşma dili ve çok dilli proje içeriği

2026-10-11 kullanıcı talebi CAP-01/03/04,KNO-01/02,APR-01,UX-01/02,CST-01/02,EVAL-01 kapsamında korunur: insan konuşmasının dilini dikkate alan not/görev/karar/AC/DoD/devam çıktıları; kaynak dili, üretim dili ve UI locale ayrımı. [Dil sözleşmesi](language-and-localization.md) P1 temel source/metadata ve açık pilot dili, P2 otomatik tespit/mixed fallback/yerelleştirme/çok dilli kalite planını tanımlar. Dil değişimi eski karar/kanıtı sessiz çevirmez; toplu çeviri ayrı izin/bütçe ister. Q12-A kabul edildi: sabit proje çıktı dili, insan onaylı değişim önerisi; bütün dillerde destek veya tasarruf kanıtı yok. 32 scope korunur.

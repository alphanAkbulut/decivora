# Mevcut durum

2026-10-11 — **Discovery / Product Definition**.

| Alan | Durum |
|---|---|
| Kaynak konuşma derlemesi, vizyon/MVP/karar haritası | Bu dokümantasyon paketinde hazırlanmış |
| Mimari, ADR, görev ve kabul planları | Öneri; uygulama kanıtı yok |
| Benchmark | Birincil belge incelemesi; runtime karşılaştırma bekliyor |
| Uygulama / adapter / dashboard | Başlanmadı |
| Model doğruluğu / tasarruf / kullanıcı talebi | Ölçülmedi |
| Lisans ve nihai marka | Karar bekliyor |

**Sıradaki iş: T01** — golden corpus ve kanıt şablonunu hazırlamak; ardından T02 adapter fizibilitesi. T03a geçici deney yöntemi, T03b yetkili prototip/native kıyas, T03c sonuç sonrası yatırım kararıdır; production uygulama bağımsız build seçilirse ilgili kapıdan sonra gelir. Bu paketin GitHub'da bulunması ürün MVP'sinin tamamlandığını göstermez.

## İlerleme kaydetme düzeni

### 2026-10-11 — Öneri, gerçek kullanıcı seçimi ve hedef uygulama ayrımı

- Kullanıcının dosya üretimi/yükleme bilinmeyeni [ürün sözleşmesine](../product/intent-to-reality-gap.md) dönüştürüldü: karar, artifact, exact hedefe uygulama ve acceptance evidence ayrı; reported/observed/unknown, partial ve stale davranışları tanımlandı.
- İki tamamlayıcı Mermaid akışı, GAP-01–10 ve T14d/T18i/T20i/T24n planlandı; T01 oracle ve T03 native/extension karşılaştırmasına bağlandı. Yeni engine/scope veya otomatik bağlantı/upload yetkisi yok.
- [Claude Projects incelemesi](../discovery/claude-projects-overlap.md), ciddi memory/koordinasyon örtüşmesini ve 17 Eylül tanıtımı ile bildirilen 9 Ekim erişim yayılımını ayırır. Orijinal X kaynağı 403; rollout tarihi ikincil teyit düzeyinde, bütün hesaplar/genel erişim iddiası yok.
- Uygulama, target adapter, gerçek kullanıcı/LLM deneyi ve GAP testleri not_run. Doküman kontrolü geçti: 73 Markdown, 552 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. GAP-01–10, dört alt dilim ve iki Mermaid kaynak bloğu kontrol edildi; görsel render yapılmadı. Sıradaki T01 ve açık owner tercihleri korunur.

### 2026-10-11 — Devam paketi ve hafıza yeterliliği taslağı

- Yapıştırılan konuşmadan [devam paketi](../product/resume-package-and-memory.md) ve [Spike-1 v1](spike-1-v1.md) hazırlandı: yaş/kanıt/coverage, güncel karar/AC, source provenance, copy/launch ayrımı ve clean-session baseline kıyası.
- T20h/T18h/T24m, S1-01–06 ve RES-01–08 planlandı. Q11 ilk düğme tercihi açık; A kopyala öneri, B capability araştırması. Wedge/MVP yeniden tanımı yapılmadı; bu repo main'inde Spike-0 runtime/prototipi bulunmadı.
- Yalnız tasarım ve deney protokolü; gerçek oturum, model, clipboard veya UI testi yapılmadı. Tam vizyon, ana görev/MVP kriterleri ve sıradaki T01 korunur.
- Doküman kontrolü geçti: 71 Markdown, 532 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. RES-01–08 ve S1-01–06 kimlikleri kontrol edildi; senaryolar not_run.

### 2026-10-11 — Token riski onayı, çoklu chat ve işleme gecikmesi

- [Ek token risk onayı](../product/token-risk-and-approval.md): deterministik risk tespiti, sınırlı plan onayı, unknown/hard-cap ayrımı ve koşu sırasında yeni çağrıyı durdurma. T09d/T19b/T24k ve TRA-01–10 planlandı.
- [Çoklu chat/lag](../architecture/multi-chat-and-processing-lag.md): session/span binding, kaynak→konu→task/karar ilişkisi, çelişki/geç mesaj, ACL-aware context, frontier/queue/gap ve yük ölçümü. T05d/T10b/T06g/T18g/T24l; CHAT-01–06/LAG-01–06 planlandı.
- Teknik tasarım ve test planıdır; model/host erişimi, runtime, hız, tasarruf ve UI testi yapılmadı. Ana 32 scope/30 görev/14 MVP kriteri korunur; T01 sıradaki iş. Q03 ve sayısal kapasite/risk eşikleri açık kalır.
- Doküman kontrolü geçti: 69 Markdown, 507 yerel bağlantı; TRA/CHAT/LAG için 22 planlı senaryo kimliği doğrulandı. Bunlar runtime test sonucu değildir; mevcut diyagramlar değiştirilmedi.

### 2026-10-10 — Q10-A kaynak keşfi tercihi kabul edildi

- Kullanıcı seçili öneriye “1a ile devam” dedi: ayrı metadata/listeleme izni varsa yeni kaynak için bağlama önerisi; seçilmeden ve gerekli onaylar tamamlanmadan içerik okuma veya takip yok. Manuel bağlantı alternatifi korunur.
- Karar/gerekçe, bağlantı, tetikleme, backlog ve ACC-02 güncellendi. Önceki ilerleme kayıtlarındaki Q10 bekleme durumu bu yeni kayıtla kapanır; Q07/1C ve diğer açık izin/bütçe kararları değişmez.
- Ürün tercihi belgelendi; gerçek hesap keşfi, yeni bağlantı, runtime veya provider testi yapılmadı. T01 sıradaki iş olarak kalır.

### 2026-10-10 — İşlem limitleri ve kötüye kullanım tasarımı

- [Limit sözleşmesi](../architecture/resource-limits-and-abuse.md): rate/burst, concurrency, byte/iş kotası, token/harcama ve DB transaction sınırları ayrıldı. Ortak insan/subagent bütçesi, receipt koruyan admission, limiter arızası, bounded log ve admin açıklamaları tanımlandı.
- T04d/T06f/T08c/T24j ve LIM-01–10 planlandı; OWASP API4, RFC 6585 ve SQLite birincil belgeleri incelendi. Mekanizmalar öneri, eşikler OPEN-12/16 ölçüm kapısında; Q03 harcama/egress izni açık kalır.
- Mevcut 30 Mermaid diyagramının topolojisi değiştirilmedi; ek sözleşme yeni servis/engine gerektirmez. Runtime, yük/saldırı testi veya çalışan limiter yok; T01 sıradaki hazırlık olarak kalıyor.
- Doküman kontrolü geçti: 67 Markdown, 483 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. LIM-01–10 kimlikleri kontrol edildi; senaryolar not_run. Eşzamanlı ranking güncellemesi korunarak birleştirildi.

### 2026-10-10 — Biriken işler için açıklanabilir ranking tasarımı

- [Ranking sözleşmesi](../product/priority-and-flow.md): 40+ task senaryosu, sekiz faktör, ilerlememe nedenleri, next actionable ve downstream etki açıklaması; canonical priority / önerilen rank / teknik execution order ayrıldı.
- Admin/owner etkin proje yetkisiyle; üst agent yalnız önceden verilmiş grant içinde teknik planı düzenleyebilir. Scope/value ve korunan karar hakları insan Product Owner'da; öneri otomatik plan değişikliği değildir.
- MVP deterministik blocker/dependency + basit board; P2 context-aware scoring/simülasyon/UX feasibility adayı. T11c/T20e/T24d ayrıntılandırıldı, T26b PROPOSED eklendi; FLOW-09–17 planlandı, FLOW-01–08 ve ana görev bağımlılıkları korundu. DEC-17'nin kabul tarihi 2026-10-09 olarak kaldı; teknik ağırlık/eşik/faz kesinleşmedi.
- Yalnız doküman değişikliği; feature, runtime, UI veya scoring deneyi yapılmadı. T01 sıradaki iş; açık kararlar ve 14 MVP kriteri korunuyor. Doküman kontrolü geçti: 66 Markdown, 471 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Sekiz hedef belge dışında değişiklik olmadığı ve FLOW-01–08/ana görev bağımlılıklarının korunduğu ayrıca kontrol edildi; planlı FLOW senaryoları not_run.

### 2026-10-10 — Sequence, DB ilişkileri ve tetikleme/zamanlama sözleşmesi

- [İletişim belgesi](../architecture/execution-and-integrations.md): 12 tetikleyici, sistem/API matrisi, olay odaklı işleme ve profil/polling/retry deney aralıkları; task doğrulama, koşullu LLM ve dış teslim için üç sequence.
- [DB ilişkileri](../architecture/data-relationships.md): bağlantı/izin ve task/run/kanıt için iki ER; N:M input/kanıt, composite key, revision, transaction ve indeks adayları. Toplam 30 Mermaid şeması; kesin DDL veya çalışan API yok.
- T04c/T06e/T09c/T14c/T18f/T24i/T28c ve SEQ-01–08/DBR-01–06 planlandı. Sayısal süreler ölçülmemiş adaydır; Q02/Q03/Q06/Q08/Q10 açık kalır. T01 sıradaki hazırlık; runtime/DB/provider testleri yapılmadı.

### 2026-10-10 — Proje erişimi, izin makbuzu ve bağlantı soruları

- Kaynak hesabı/OS yetkisi, hedef projeye bağlantı ekleme yetkisi ve agent grant'i ayrı tanımlandı. Sürümlü ConnectionAuthorization, requested/granted/effective scope, kurulumda altı soru ve proje bazlı “Bağlantılar ve izinler” görünümü belgelendi.
- Yeni kaynak, scope/egress artışı, kaynak transferi, path kaçışı, karışık transcript, revocation ve kayıtların sonraki kullanımı açıklandı. T05c/T16b/T20g/T24h ile ACC-01–08 planlandı; metadata keşfi için Q10 seçenekleri hazır, cevap bekliyor.
- Mevcut 25 Mermaid şeması değiştirilmedi; bağlantı/policy sınırlarının metinsel sözleşmesi ayrıntılandırıldı. Runtime, provider izin deneyi veya yeni görsel render testi yapılmadı. Hesap bağlantısı, yetki genişletme, gerçek veri aktarımı ve ücret yok; T01 sıradaki iş olarak kalıyor.

### 2026-10-10 — Diyagram incelemesi ve yönetim/operasyon tasarımı

- 11 belgedeki 20 Mermaid şeması son kararlarla karşılaştırıldı; 1C arşiv/TTL, eksik DEC-15–17, MCP routing ve tenant ER kapsamı düzeltildi. Run, soru, blocker, admin ve incident için beş şema eklendi: toplam 25. Ayrıntı [inceleme kaydında](../quality/diagram-review.md).
- [Yönetim sözleşmesi](../product/administration-and-operations.md) yerel/kurulum admin'i, workspace/proje rolleri, platform operatörü, günlük kullanıcı, agent ve olası L1 desteği ayırır. Incident, güvenli müdahale, versioned parametre ve miras/tavan kuralları; T20f/T21c/T23e/T24g ve ADM-01–10 planlandı.
- Lisans, hosting, veri erişimi ve ticari paket ayrı kararlardır. OSI/AGPL/Apache kaynakları tekrar okundu. Repo private kalır; lisans, ücretli provider, kullanıcı hesabı veya hosted servis oluşturulmadı. P1b minimal yerel yönetim, P4 ekip/platform konsolu önerisi; runtime/test sonucu değil.
- Doküman kontrolü ve diagram inventory çalıştırıldı; son kontrol kapsamı inceleme kaydında. T01 hâlâ sıradaki uygulamalı hazırlık; açık lisans/retention/host/bütçe kararları bu tasarımla kapanmadı.

### 2026-10-10 — Scrum, PMI ve genel bağımlılık yönetimi ayrımı

- Scrum çerçevesi, PMI mesleki kuruluşu ve yöntemden bağımsız bağımlılık/engel kavramları ayrıldı. Önceki Scrum Alliance atfı tek sahiplik/kaynak gibi yorumlanmayacak şekilde açıklandı; DEC-17'nin kabul edilmiş ilkesi korunuyor.
- Ürün çekirdeği, kendi geliştirme ritmimiz ve müşterinin yöntemi ayrı katmanlarda açıklandı. Farklı süreçlere uyarlanabilirlik konumlandırması önerildi; tam Scrum/PMBOK uyumu, kritik yol veya yeni yöntem modları taahhüt edilmedi.
- PMI birincil kaynakları okundu; Scrum kaynakları tekrar kontrol edildi. Ürün kodu/öncelik algoritması değişmedi, runtime veya yöntem uyum testi yapılmadı. T01 sıradaki uygulamalı hazırlık olarak kalıyor.
- Doküman kontrolü geçti: 62 Markdown, 374 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Beş belgede kavram ve kaynak atfı netleştirildi.

### 2026-10-10 — Subagent soru ve karar mekanizması

- Bilgi/görüş isteği, yetki içi teknik seçim ve korunan insan kararı ayrıldı. Parent/uzman agent danışması onay yetkisine dönüşmez; önceki geçerli karar tekrar sorulmadan kaynaklı kullanılabilir.
- Soru/cevap/approval/delivery/resume/task verification ayrı; timeout, parent kaybı, stale/conflict, ACL, döngü/bütçe ve gözlem-only host istisnaları yazıldı. Yalnız cevaba bağımlı iş bekler; dış process'in durduğu teyitsiz söylenmez.
- T13e/T18e/T24f ve ASK-01–08 planlandı; insan review ilkesi değiştirilmedi. Host kurulumu, messaging, agent execution veya runtime testi yapılmadı. T01 sıradaki hazırlık; önceki açık tercihler korunuyor.
- Doküman kontrolü geçti: 62 Markdown, 371 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Sekiz ASK senaryosu planlı kabul tanımıdır, çalışmış test sonucu değildir.

### 2026-10-10 — Karar gerekçelerinin kaynakla eşlenmesi

- Proje yönetim planında DEC-17 için kullanıcı ihtiyacı, karar sahibi/tarihi, kaynak yaklaşımı, Decivora uyarlaması, seçim gerekçesi, bedel ve doğrulama aynı kayıtta eşlendi. Kaynak kontrolünün kullanıcı yönlendirmesinden sonra yapıldığı ve formal Scrum uyumu iddiası olmadığı açık.
- Karar haritasına gerekçe belgeleri indeksi ve kayıt standardı eklendi. Kayıtsız geçmiş gerekçeler uydurulmadı; sonradan yapılan karşılaştırma tarihsel seçenek sunumu gibi gösterilmedi. Ürün kapsamı/karar statüsü değişmedi.
- Doküman kontrolü geçti: 62 Markdown, 366 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Runtime veya bağımsız LLM anlama testi yapılmadı.

### 2026-10-09 — Tek insanın çok agent'ı ve ekip kurulumu

- İnsan sayısı, agent sayısı ve execution yetkisi ayrı eksenler olarak belgelendi. Mevcut INT-02/TEAM-01 kapsamında tek owner + iki agent için T02c/T18d/T24e; ekip kurulum/hesap/davet için C01–C04 ayrıntıları eklendi.
- Resmî Codex SDK, OpenAI reasoning ve Claude Code hook belgeleri okundu. Girdi/parent/tool/artifact/usage coverage, gözlemci/aktör kimliği, private muhakeme sınırı, run başarı/task doğrulama ayrımı, duplicate/revoke/race ve usage toplamı tasarlandı. Agent veya provider kurulmadı.
- Self-host/managed seçenekleri, merkezi servis/ayrı hesaplar, private kaynak paylaşımı, bootstrap/recovery/offboarding ve kişisel→ekip geçişi belgelendi. Hosting/SSO/ticari lisans seçilmedi; bireysel pilot ve T01 sıradaki hazırlık olarak kaldı.
- AGT-01–08 planlıdır; uygulama, gerçek çok-agent çalışması veya ekip giriş testi yapılmadı. Q02/Q03 ve OPEN-14–16 mevcut karar kapılarıdır.
- Doküman kontrolü geçti: 62 Markdown, 362 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Yeni sekiz AGT senaryosu uygulama kabul planıdır, test sonucu değildir.

### 2026-10-09 — Product Owner yaklaşımı ve blocker önceliği

- Q09/DEC-17 kabul edildi: ilerlemeyi engelleyen işler/kararlar ve downstream gecikmesi önce; değer/hedef/risk odaklı çevik çalışma. Bildirim kanalı/sıklığı ve formal Sprint takvimi seçilmedi; Q08 ayrı açık.
- Scrum Guide ve Scrum Alliance kaynakları incelendi; çerçeve, uygulama rehberi ve bireysel pilot uyarlaması ayrıldı. AGENTS ve kısa yönetim planı güncellendi; sertifika/uygunluk iddiası yok.
- Öncelik/akış belgesi, blocker ile ready ayrımı, benzersiz etki hesabı, ACL/unknown/stale, karar yetkisi, inbox ve öğrenme ölçümleri yazıldı. T11c/T20e/T24d ve sekiz FLOW kabul senaryosu planlandı; runtime veya bildirim servisi yok.
- T01 sıradaki uygulamalı hazırlık olarak kaldı; dokümantasyon corpus/adapter testlerinin tamamlandığı anlamına gelmez.
- Doküman kontrolü geçti: 61 Markdown, 348 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Sekiz FLOW tanımı ve değişen belgelerin bölüm yapısı ayrıca kontrol edildi. Bunlar runtime, Scrum uygunluğu veya bildirim testi değildir.

### 2026-10-09 — 1C kararı ve alt görev önerisi

- Kullanıcı Q07/1C'yi kabul etti: izinli/erişilebilir geçmişi aktif işlere öncelik vererek aşamalı işleme. 1A/1B seçenekleri ve seçilmeme nedenleri korundu; DEC-15, import, token ve retention belgelerine işlendi. Geçici ham payload için eski 30 gün önerisi 1C kaynak arşivinden ayrıldı; OPEN-08 kesin süre/kapasite kararı açık.
- Q08 için isteğe bağlı alt göreve bölme önizlemesi, parent/child kimliği, AC/kanıt eşlemesi, part_of, atomik onay, iptal ve tamamlama kuralları önerildi. Anlamlı child + küçük adımlarda checklist önerisi henüz varsayılan kullanıcı kararı değil. DEC-16 ve T13d/T20d öneri olarak kaldı; T22b kabul edilen geçmiş davranışının uygulama dilimi.
- Doküman kontrolü geçti: 60 Markdown, 331 yerel bağlantı; mevcut 32 scope, 30 ana görev ve 14 MVP kriteri korundu. Yeni sözleşme senaryoları planlıdır; runtime veya yeni Mermaid render testi yapılmadı.
- Q02/Q03/Q06 ve yeni Q08/Q09 açık; gerçek kaynak aktarımı, ücretli model, çalışan task bölme veya yeni runtime testi yok. T01 sıradaki uygulamalı hazırlık olarak korunuyor.

### 2026-10-09 — Bağlantı, token ve iş bağlamı

- MCP/capture/insan UI ayrımı, bir defalık kurulum, tools-only health, delta brief/resync, disconnect ve sağlayıcı build kapıları ayrıntılandırıldı. OpenAI/Claude resmî kaynakları belge düzeyinde kontrol edildi; gerçek kurulum yapılmadı.
- Host model tüketimi ile kendi arka plan analizimiz ayrıldı. No-op/duplicate bypass, sınırlı context, sürümlü cache, retry/escalation ve atomik bütçe rezervasyonu; bilinmeyen usage ve deferred UI davranışı yazıldı. Fiyat/tasarruf iddiası veya ücretli çağrı yok.
- Kullanıcı Q04 ile güncel işler + seçili iş bağlamını; Q05 ile proje/görev bazlı, sonradan değiştirilebilir analiz profilini seçti. Olgunlaşma hikâyesi, AC/DoD ve test matrisi istendi; task context/acceptance sözleşmesi eklendi. Q06 otomatik Markdown üretimi, Q02 yüzey/OS ve Q03 gerçek veri/bütçe ayrı açık sorular.
- Görev iptali, obsolete ve relationship ended/invalidated ayrıldı; geçmiş bağlantıları silmeyen graph sözlüğü ve üç yeni Mermaid şeması eklendi. AC/DoD başlamadan versiyonlu; completion güncel kanıta bağlı.
- CON/TOK/GUX/CTX kapsamında 30 planlı senaryo ve küçük görev dilimleri eklendi. Doküman kontrolü geçti: 60 Markdown, 319 yerel bağlantı; mevcut 32 scope, 30 ana görev, 14 MVP AC korundu. Runtime, maliyet veya tıklanabilir UI testi yapılmadı. T01 sıradaki uygulamalı hazırlık olarak kaldı.
- İçerik commit'i `451c85bd382114d236245f4d17b89d2333ba5121`: 22 değişen dosya GitHub'dan geri okunup yerel içerikle birebir eşleşti. Üç yeni Mermaid diyagramı GitHub'da render edildi; iptal/karar ilişkileri diyagramı görsel olarak da incelendi. Bu kontrol gerçek graph UI veya model maliyet testi değildir.



### 2026-10-09 — Çok kullanıcı, log ve hafıza planı

- Linear/GitHub/OpenFGA, Cortex/mai-mcp, Letta legacy kavramları ve SQLite/PostgreSQL/OTel birincil belgeleri üzerinden hedefli benchmark hazırlandı; ürünler kurularak IAM veya yük kıyası yapılmadı.
- Workspace/project üyeliği, insan/agent principal, süreli grant, authz revision, private/shared türev bilgi, davet/offboarding ve reviewer policy tasarımı eklendi. İlk bireysel pilot korundu.
- Source/domain/security audit/operational telemetry ayrımı; SQLite başlangıcı, merkezi ekip PostgreSQL adayı, blob/secret sınırı, retention/backup/purge ve sentetik kapasite profilleri belgelendi.
- ADR-0009/0010 önerileri, P1 alt görevleri, P4 C01–C06 ekip dilimleri ve 18 MU kabul senaryosu eklendi. README, AGENTS, scope, roadmap, handoff ve izlenebilirlik bağlandı.
- Doküman kontrolü geçti: 57 Markdown, 264 yerel bağlantı, 32 scope, 30 ana görev, 14 MVP AC; 28 V + 18 MU planlı senaryo. Bunlar runtime test sonucu değildir.
- Ana içerik commit'i `6c659c1367e9618a76efc537fb409a6c2d66796e`: 33 değişen dosya GitHub'dan geri okunup yerel içerikle birebir eşleşti. Repository private olarak tekrar doğrulandı. Dört yeni Mermaid diyagramı GitHub'da render edildi; audit akışı görsel olarak da incelendi. Son incelemede gizli gerekçelerin impact analizinde yanlış obsolete üretmemesi netleştirildi.
- Sayısal retention/SLO/RPO/RTO önerileri ve ekip deployment/reviewer seçenekleri açık karar olarak kaldı. Uygulama ve gerçek veri/ücretli API deneyi yapılmadı. T01 hâlâ sıradaki uygulamalı hazırlık.



### 2026-10-09 — Kullanıcı araştırması ve pilot soruları

- Owner ilk pilotu kendi bireysel kullanımıyla, sonra benzer kullanıcılarla ilerletmeyi seçti. Coding/chat yüzeyleri + hedef OS ve harici API/veri/bütçe sınırı soruldu; henüz cevap gelmedi. Karar durumu [soru kaydında](decision-brief.md).
- Yedi kamuya açık issue/tartışma kaynağı ve iki Linear resmî belgesi incelendi. İki kapalı issue'nun bakımcı düzeltme açıklamaları okundu; tarihsel yakınmalar güncel rakip kusuru olarak sunulmadı.
- [Kullanıcı araştırması](../discovery/user-research.md), şikâyet→hipotez→ürün davranışı→ölçüm zincirini ve ürünü terk ettirebilecek durumları kaydeder. [Benchmark bulguları](../discovery/benchmark-findings.md) belge incelemesi ile runtime deneyi arasındaki sınırı ve doldurulmamış sonuç şablonunu gösterir.
- Linear'ın otomatik taslak kabiliyetleri karşılaştırmaya eklendi; farklılaşma genel AI task üretimi yerine gerekçeli karar etkisi ve yönetim yükü üzerinde netleştirildi. No-op, onboarding ve projeye dönüş ölçümleri mevcut scope'a bağlandı.
- Dokümantasyon kontrolü geçti; runtime benchmark, kullanıcı görüşmesi ve ücretli/gerçek veri deneyi yapılmadı. T01 corpus henüz tamamlanmadı; sıradaki uygulamalı hazırlık olarak kalıyor.

### 2026-10-09 — İkinci kapsam ve mimari incelemesi

- Kaynak konuşmanın 14 evresi ve engine adları tekrar eşleştirildi; 32 scope satırı için kaynak→özellik→engine→görev→kontrol matrisi eklendi.
- 17 kullanıcı özelliği, 10 engine/alias sözlüğü, sekiz mimari diyagram, genişletilmiş roadmap, farklılaşma hipotezleri, LLM handoff ve kısa proje yönetim planı hazırlandı.
- ADR-0007/0008 önerileri; graph snapshot yarışı, durable processing, verifier yetkisi ve etkisiz replay sözleşmeleri eklendi. 30 ana göreve küçük alt dilimler bağlandı; zorunlu test planı V01–V28 oldu.
- Yerel doküman kontrolü geçti: 46 Markdown, 150 yerel bağlantı, 32 scope, 30 ana görev, 14 MVP AC, 17 feature, 10 engine ve 14 kaynak evresi referansları tutarlı.
- Ana içerik commit'i `4b29c19fcb5a9cfef5a25b2de3d790a49a65468f`: değişen 29 dosya GitHub'dan geri okunup yerel içerikle birebir karşılaştırıldı; tamamı eşleşti. Repository private olarak doğrulandı.
- GitHub üzerinde atlasın sekiz ve roadmap'in iki Mermaid diyagramı render edildi; render hata mesajı görülmedi. Sistem bağlamı ve onay yarışı diyagramları görsel olarak da incelendi. Bu kontrol uygulama davranışını doğrulamaz.
- Uygulama geliştirilmedi; engine/adapter/test suite çalıştırılmadı. Bağımsız LLM anlama deneyi yapılmadı. T01 hâlâ sıradaki görev.

İnceleme: [bulgular ve açık kalanlar](../quality/completeness-review.md). Teknik önerilerin eklenmesi onları owner tarafından kabul edilmiş mimari karar yapmaz.

Her görev sonunda görev ID, değişen dosyalar, AC karşılığı, çalıştırılan kontrol ve sonuç, açık engel ve bir sonraki görev buraya veya tarihli delivery kaydına eklenir. ADR statüsü gerçek karar olmadan accepted yapılmaz. Tamamlanma yalnız somut kanıtla kaydedilir. Geçici ilerleme ve branch isimleri AGENTS.md içine yazılmaz.

## Korunacak alanlar

Başka kullanıcı projeleri bu repo için pilot olarak kendiliğinden bağlanmaz/değiştirilmez. Kaynak transcript ve credentials repoya konmaz. Doküman düzenlemesi ürünü çalıştırma, ücretli API kullanma veya public release yetkisi değildir.

## Tasarım revizyonu 03 — güncel durum özeti

**2026-10-11:** [Güncel yön](../product/current-direction.md) ilk karşılaştırma odağını gerçek seçim/artifact/hedef uygulama/devam bağlamı olarak toplar. Tam vizyon ve P1b MVP korunur; projenin iptal edilmesi veya bağımsız build'e geçiş kabul edilmiş değil. Bu tur belgeleme/tutarlılık güncellemesidir, prototip/runtime başlamadı.

76 başlangıç dosyası remote/local eşleşmesiyle tarandı; diagram/şema/ADR/giriş/analiz/delivery etkileri çapraz incelendi. ApplicationTarget/Expectation/Observation/Assessment ve ER-03/ADR-0011, T02d/T03a–c yatırım sırası, GAP JSON oracle ve tek canonical set sürüm düzeni eklendi. Tasarım revizyonu 03 product v3 değildir; v2/v3 kopyaları oluşturulmadı.

Sıradaki **T01**; ardından source/tek target capability ve sınırlı yöntem önerisi. T03b prototype/native deney ancak yetkili kapsamda; T03c sonuç sonrası yatırım kararı. Q02/Q03/Q06/Q08/Q11 ve sayısal/stack/lisans kararları açık. Prototip, native benchmark, gerçek LLM/adapter/DB/UI/migration/test sonucu not_run.

Bu teslimin içerik commit'i `aaf9cbef1c5a387848a6d75975482b9d09ae9e4a`: 42 değişen/yeni dosya aynı ref'ten GitHub üzerinden geri okundu ve local içerikle birebir eşleşti. Doküman kontrolü geçti: 76 Markdown, 658 yerel bağlantı; 32 scope, 30 ana görev, 14 MVP kriteri, 17 feature ve 10 engine korundu. JSON/ID/diyagram inventory kontrolü geçti. Hatalı fixture implemented işareti, yanlış inventory sayısı ve tanımsız GAP ID'si geçici kopyalarda reddedildi.

15 belgedeki 34 Mermaid çıktısının tamamı GitHub Preview üzerinden render edilmiş SVG/etiket düzeyinde kontrol edildi; syntax/render hatası görülmedi. Güncel roadmap ayrıca ekran görüntüsüyle incelendi. Bu kontrol ürünün DB, API, agent, model veya tıklanabilir UI davranışını doğrulamaz. Kontrol kaydı değişiklikleri ayrıca küçük bir doküman commit'inde tutulur; ürün release'i oluşturulmadı.

## 2026-10-11 — Token önlemleri ve sözlük/pattern önerisi

Yedi token önlemi mevcut routing/connection/risk belgelerinde kontrol edildi: batch/delta, structured bypass, revision bağlı cache, kaynaklı özet, parent/dönem bütçesi ve yüksek tüketim onayı mevcut tasarımda var. Uygulama veya tasarruf kanıtı yok.

[Lexical prefilter](../architecture/lexical-prefilter.md) önerisi eklendi: 20 elle hazırlanmış sentetik TR/EN örnek, versiyonlu küçük rule config adayı, guard/actor/target/provenance, structured-first/shadow/unmatched yolu ve üç ekonomik karşılaştırma. T01e/T09e/T24o ve LEX-01–08 planlı; gerçek transcript/model sıklık analizi yapılmadı. Keyword completion, insan approval, shell/write veya doğrulanmış hedef gözlemi üretemez. 10 engine ve 30 ana görev korunur; yeni DB veya kabul edilmiş stack yok.

Bu teslim yalnız dokümantasyon değişikliğidir; mevcut 34 Mermaid kaynak bloğu değiştirilmedi. Sıradaki T01, Q03 gerçek veri/ücretli model kapısı ve mevcut açık owner kararları korunur. Doküman kontrolü geçti: 77 Markdown, 672 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri ve 34 Mermaid inventory korundu. LEX-01–08 tekil/sıralı ve T01e/T09e/T24o referansları ayrıca kontrol edildi. Commit sonrası içerik read-back teslimde ayrıca doğrulanır; LEX senaryoları runtime'da not_run kalır.

## 2026-10-11 — Faz bazlı proje ağacı ve takip

Kullanıcı güncel planın MVP, P2 ve P3 olarak ayrı takip edilip edilmediğini sordu. [Tek faz takip görünümü](phase-tracker.md) eklendi: P0 hazırlık kapısı, MVP için P1a 12 + P1b 9 ana görev, P2 üç ana görev, P3 iki ana görev ve korunan P4 ekip hattı. Her fazın teslim/çıkış kanıtı ve küçük alt iş örnekleri kaynak backlog'a bağlıdır. T03 ana indeks başlığı mevcut native/extend/build detay başlığıyla eşleştirildi; ön koşullar/kapsam değiştirilmedi.

Ana görev ID/faz/durum/başlık/ön koşulları doküman betiğiyle backlog'a eşleştirilir; ikinci bağımsız backlog veya v2/v3 kopyası yaratılmadı. README/roadmap/start-here/backlog bu görünümü işaret eder. Bütün runtime ana görevleri TODO, aday alt dilimler PROPOSED; uygulama, model veya yeni UI testi yok. Mevcut 34 Mermaid kaynak bloğu değiştirilmedi. Sıradaki T01 ve owner karar kapıları korunur.

Teslim kontrolü geçti: 78 Markdown, 693 yerel bağlantı; 30 ana görev satırı faz/durum/başlık/ön koşul düzeyinde backlog ile eşleşti. Geçici kopyada yanlış DONE durumu kontrol tarafından reddedildi; gerçek dosyalarda böyle bir değişiklik yapılmadı. 32 scope/14 MVP kriteri/10 engine ve 34 Mermaid inventory korundu. Bu statik denetim çalışan proje takip uygulaması veya ürün test sonucu değildir.

## 2026-10-11 — Konuşma dili ve İngilizce dışındaki kullanıcılar

Kullanıcı konuşma dilini tespit edip not/proje çıktısını o dilde üretme ihtiyacını ekledi; maliyetli otomasyonun P2'de olabileceğini belirtti. [Dil sözleşmesi](../product/language-and-localization.md), P1 source/Unicode/metadata/açık pilot dili, P2 otomatik tespit/mixed fallback/locale katalogları/cross-language kalite planını önerir. Source/üretim/UI dili ayrıdır; kod/kanıt/ref korunur, eski kayıtlar sessiz çevrilmez. Q12 proje dili değişim önerisi (A) veya session bazlı dil (B) açık; A teknik öneridir, kullanıcı seçimi değil.

T05e/T24p/T25a/T26c ve LANG-01–08 mevcut parent kapsamına bağlandı. Detector/model/library veya yeni DB/engine seçilmedi; gerçek veri/model/translation görevi çalıştırılmadı. Bütün dil desteği veya token tasarrufu ölçülmedi. 30 ana görev/P1b 14 AC korunur; faz takip görünümü P2 dil satırıyla tamamlandı. Mevcut 34 Mermaid kaynak bloğu değiştirilmedi; sıradaki T01 ve Q03 erişim/bütçe kapısı korunur.

Doküman kontrolü geçti: 79 Markdown, 711 yerel bağlantı; 30 ana görev faz/durum/ön koşul görünümüyle eşleşti, 32 scope/14 AC/17 feature/10 engine ve 34 Mermaid inventory korundu. LANG-01–08 tanım/referansları, dört alt görev ve tek Q12 açık soru kaydı kontrol edildi. Detector/model/çeviri/UI deneyi yapılmadı; planlı dil kabulü not_run.

## 2026-10-11 — WrongStack kaynak ve yeniden kullanım incelemesi

Kullanıcı WrongStack'in yararlı açık kaynak parçalarını araştırmayı istedi. [Immutable inceleme](../discovery/wrongstack-review.md), commit `5234c15b05fe18857d0119eabd3b8a8f910ecc66` gerçek MIT LICENSE/manifest, seçili kaynak/test tanımları, memory/verification/MCP/pattern/budget/IPC ve bir DoD UI bileşeni üzerinden hazırlandı. EvidenceValidator, requirement coverage, validity schema ilk küçük reuse adayları; native/extension seçeneği ve semantik uyum farkları kaydedildi. Repo geneli audit, CI veya çalışma testi yapılmadı.

Benchmark/bulgu/farklılaşma/lisans/kaynak/lexical/README ve T03d planı güncellendi; 30 ana görev, 10 engine, MVP ve sıradaki T01 korundu. Kod/prompt/asset/runtime dependency alınmadı, yeni orchestration kararı verilmedi. WS-01–08 not_run; performans/token tasarrufu ve çalışan entegrasyon iddiası yok. Q03 ve stack/lisans karar kapıları açık. Doküman kontrolü geçti: 80 Markdown, 727 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri/17 feature/10 engine ve 34 Mermaid inventory korundu. WS-01–08 sırası ve pinned kaynak yolları ayrıca kontrol edildi. Mermaid kaynakları değiştirilmedi; yeni render/runtime testi yapılmadı. Remote teslim read-back sonucu kullanıcı raporunda ayrıca belirtilecek.

## 2026-10-11 — Q12-A çıktı dili tercihi kabul edildi

Kullanıcı seçili A önerisine “a ile devam et” yanıtını verdi. DEC-20/Q12-A kaydedildi: sabit proje çıktı dili, farklı sohbet dili için öneri, ret/yanıtsız durumda mevcut dili koruma, yetkili insan kabulünde yeni policy revision ve sonraki üretim; eski notları otomatik çevirmeme. B alternatifi/gerekçe/bedel dil ve soru kaydında korundu. Önceki dil keşfi kaydı o zamanki açık durumu anlatır; bu kayıt tercihi kapatır.

Dil sözleşmesi, scope/catalog/domain/roadmap/phase/backlog/verification/traceability ve açık kararlar eşleştirildi; karar haritasının mevcut Mermaid bloğuna DEC-20 eklendi. 30 ana görev/10 engine/MVP/P1-P2 ayrımı ve sıradaki T01 korunur. Detector/LLM/çeviri/UI çalıştırılmadı; LANG senaryoları not_run. Q03/stack/lisans ve diğer owner tercihleri bu yanıtla kapanmaz.
Doküman kontrolü geçti: 80 Markdown, 730 yerel bağlantı; 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 34 Mermaid inventory korundu. Güncel Q12 kayıtları kabul edilmiş A ile eşleşti; eski açık durum yalnız tarihsel keşif kaydında bırakıldı. Mermaid render ve runtime/dil model testleri yapılmadı.

## 2026-10-11 — Q12 örneği, cevapsız sorular ve geç yanıt bağlamı

Kullanıcı Q12-A seçimini gecikmeli vermesini ürünün canlı problemi olarak gösterdi. [Kalıcı soru/geç cevap sözleşmesi](../product/pending-questions-and-late-answers.md), explicit ID/selected source/option snapshot bağını, iki A/B sorusundaki ambiguity'yi, answered/associated/approved/applied ayrımını, timeout/stale/expiry, soru öncesi ingest ve ACL/replay/coverage istisnalarını somutlaştırdı. Q12-A/DEC-20 gerçek seçimi korunur; bu sohbetin işlenmesi Decivora otomatik adapter/test kanıtı değildir.

Approval UX, soru/domain/çoklu chat, verification/traceability ve README bağlandı. Önceki belgelerde referanslanan fakat backlog teslim satırı bulunmayan T13e/T18e/T24f eksikliği giderildi. LATE-01–08 planlı; yeni engine/ana görev, reminder servisi, ücret veya erişim kararı yok. Hatırlatma kanalı/sıklığı açık; uygulama içi pending/brief önerisi ve bağımsız iş ilerlemesi korunur. Sıradaki T01; runtime/parser/LLM/host/UI sonuçları not_run.

Doküman kontrolü geçti: 81 Markdown, 746 yerel bağlantı; 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 34 Mermaid inventory korundu. Sekiz LATE kabul ID'si ve üç soru alt dilimi ayrıca kontrol edildi. Mevcut Mermaid kaynakları değişmedi; runtime veya render testi yapılmadı.

## 2026-10-11 — Ürün değerlendirme vakası ve repo geneli kod adayları

Kullanıcı README'ye yazmadan ürün değerlendirme/mindset anlatısı ve bütün upstream kod alanlarında somut kullanım önerisi istedi. Ayrı [portföy vaka çalışması](../portfolio/product-evaluation-case-study.md), owner/AI katkısı, problem evrimi, gerçek karar/alternatif/bedel, güçlü taraflar ve eksik kanıtları toplar. Çalışan ürün/üstünlük/gelir/token tasarrufu iddiası yok; private repo ve yayın izni değişmedi. README değiştirilmedi.

[Kod/teknoloji değerlendirmesi](../discovery/code-reuse-assessment.md) sabit upstream ref'te 39 manifest ve 9.657 kod dosyasının yapısal envanterini; R01–24 kaynak/hedef/uyarlama/kabul adaylarını ve paket kapanışını sunar. 2.203.270 satır test/fixture/declaration/yorum dahil; bütün satırların semantik denetimi değildir. Yeni governance append-only event/receipt/verifier/grant ve Kanban contract graph/core decision/rationale bulguları önceki hedefli benchmark'ı genişletti; eski ref-only/soft-gate bulguları bütün platforma genellenmedi. Tam source, upstream script/install veya runtime dependency alınmadı.

Benchmark/farklılaşma/lisans/kaynak/handoff ve öneri T03d WS-R2/3 kapsamı güncellendi. Q13 A/B/C somut araştırma seçenekleri açık; owner seçimi yok. T01 sırası, 30 ana görev TODO, 10 engine, tam vizyon ve MVP korunur; nihai stack/alıma geçiş/gerçek veri/ücret kararı verilmedi.

Doküman kontrolü geçti: 83 Markdown, 791 yerel bağlantı; 32 scope/30 ana görev/14 MVP AC ve 34 mevcut Mermaid inventory korundu. Envanter betiği yalnız kaynak okuyup metadata üretti; upstream kod/test/model/agent çalıştırılmadı. Yeni Mermaid bloğu yok; render/runtime/native benchmark sonucu not_run. Envanter tekrarında CSV/JSON birebir aynı çıktı; 39 manifest alanı, 35 paket ve R01–24 eşleşti. İndekslenen 9.657 kod dosyası immutable Git tree blob hashleriyle birebir eşleşti. Kaynak kimliği/yapısal kontrol davranış testi değildir; remote commit/read-back teslimde doğrulanır.

## 2026-10-11 — Ekosistem araştırma görevi ve ilk tarama

Kullanıcı WrongStack dışında projelerden de yararlanmak istedi. [T03e araştırma kartı](../discovery/ecosystem-research.md), 10 immutable aday/root lisans, beş seçili source incelemesi ve [makine okunur kayıt](../discovery/ecosystem-candidates.json) hazırlandı. ER-R1 masa başı belge çıktısı mevcut; ER-R2–4 derin closure/deney/owner önerisi TODO. Graphiti, LangGraph, LiteLLM ilk derin inceleme adayları; OpenFGA/Cedar ekip modeli, Temporal distributed ihtiyaç kapısında.

Benchmark/farklılaşma/lisans ve devir belgeleri karşı kanıtla genişletildi. Source D/S, runtime V değil; ER-T1–5, accuracy/token/latency sonuçları not_run/null. Yeni dependency, kaynak kod kopyası, install, paid bağlantı veya mimari kabulü yok. Q13, 30 ana görev, T01 sonraki iş ve README korunur. Doküman kontrolü geçti: 84 Markdown, 817 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri/17 feature/10 engine ve 34 Mermaid kaynak bloğu korundu. Pinned kaynak kayıtları ayrıca kontrol edildi; runtime veya diyagram render testi yapılmadı. Commit sonrası hedeften içerik doğrulaması ayrı teslim kontrolüdür.

## 2026-10-11 — Teknik ölçüm protokolü ve hedefli evaluator incelemesi

Kullanıcı karar→etki→gerçekleşme farkının teknik olarak nasıl ölçüleceğini sordu. [Protokol](../quality/evaluation-protocol.md), bağımsız frozen oracle, one-to-one entity/span matching, checkpoint/action/path scoring, exact target binding, stage telemetry, quality/cost/coverage ve incomplete gate'i ayrıntılandırdı. [CHAIN-01 taslağı](../../examples/decision-impact-evaluation-case.json) yedi checkpoint/dört negatif varyant; illustrative/not_run, T01 corpus/holdout veya uygulama değil. T01f/T03f/T24p TODO; T01 ana sıra ve Q03/Q13 korunur.

Graphiti evaluator/judge ve ayrı Langfuse Python SDK experiment/test/license hedefli okundu. Source örneğinin kendi gold/verdict/error bağını denetleme ihtiyacı kaydedildi; bütün source audit'i, upstream test başarısızlığı veya runtime üstünlük iddiası yok. Yeni dependency, model çağrısı, paid telemetry, mimari karar ve kod kopyası yok. Doküman kontrolü geçti: 85 Markdown/833 yerel bağlantı; 32 scope, 30 ana görev, 14 MVP kriteri, 17 feature, 10 engine ve 34 Mermaid kaynak bloğu korundu. CHAIN-01 ID/ref, not_run/null ve mock sınırları veri kontrolünde doğrulandı; scorer/ürün runtime testi veya Mermaid render yapılmadı. Ölçüm harness'i uygulanmadı.

## 2026-10-11 — Teknik boşluk analizi, sözleşme ayrıntıları ve görev kimliği düzeltmesi

Kullanıcı bütün akıştaki boşlukları ve neden neyi incelediğimizi kalıcı belgelememizi istedi. [TG-01–24 analiz kaydı](../quality/technical-gap-analysis.md) başlangıç ref/yöntem/kanıt sınırı, iki somut doc conflict, teknik ayrıntı önerileri, implementasyon/capability/owner/ölçüm açıkları, first-use G0–G6 kapıları ve adım adım soru kuyruğunu tutar. [IC-01–08](../architecture/implementation-contracts.md) strict wire/source span, canonical digest, exact budget/period, target consistency, empty AC/projection freshness ve transport/recovery/test raporu ayrıntılarını önerir. Accepted ADR, code/DB/API veya yeni dependency değildir.

**Düzeltme geçmişi:** önceki ölçüm güncellemesinde T24p zaten dil görevi için tanımlıyken ikinci kez ölçüme verilmişti; ölçüm **T24q**, dil **T24p** olarak ayrıldı. Önceki status kaydı o anki teslimi anlatır ve korunur. Güncel ölçüm referansları düzeltildi; checker canonical subtask definition tekrarını da reddeder. Event/runtime source key scope/epoch tarifi DB ilişkileriyle hizalandı; runtime dedup uygulanmadı.

Q02-R1 ilk pilot kaynak yolu A/B/C cevap bekler; öneri A kullanıcı seçimi değildir. Q03/Q06/Q08/Q11/Q13 ve OPEN policy/stack/permission kapıları korunur. İlk T01 ve 30 ana görev TODO; 32 scope/17 feature/10 engine/14 MVP AC ve 34 mevcut Mermaid bloğu değişmedi. README ve başka projeler değiştirilmedi. Runtime, model, gerçek adapter/target, load/restore/UI veya security testleri not_run. Doküman teslimi ve checker negatif testi ayrıca doğrulanır.

Teslim kontrolü: doküman betiği geçti; 87 Markdown/893 yerel bağlantı, 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 34 Mermaid/15 belge inventory korundu. Ayrı geçici repo kopyasına T24p duplicate definition enjekte edildi; checker beklenen hata ile reddetti, asıl repo değiştirilmedi. 24 tekil TG kaydı/8 IC bölümü ve dil T24p→T25a bağı ayrıca kontrol edildi. Bunlar doc/checker kanıtı; ürün conformance sonuçları not_run. Remote commit/read-back ayrıca teslimde doğrulanır.

## 2026-10-11 — Bütün Mermaid'lerin görsel ve içerik incelemesi

Kullanıcı çalışma aşamasını ve README dahil tüm Mermaid'lerin güncel/eksiksiz incelenmesini, anlamlı renk/label ve daha iyi belge sunumunu istedi. **Aşama hâlâ keşif, ürün tanımı ve teknik tasarım**; uygulama/pilot/build/stack seçimi yapılmadı. 24 TG bulgusu dokümantasyon/implementation/deney/owner ayrımıyla geçerli; render bunları runtime düzeyinde kapatmaz.

34 önceki şemanın tamamı semantik karşılaştırma ve görsel güncellemeye alındı. Karar haritasında eksik DEC-10–14 görselleştirildi; kabul edilmiş niyet ve teknik öneriler iki görünüm oldu. Yeni toplam **35 Mermaid / 15 belge**; 23 flowchart, 4 ER, 7 sequence, 1 state. Ortak renkler, metin etiketi, accTitle/accDescr, numaralı sequence/açıklama bandı eklendi. Atlas budget kontrolü/late answer association/source key, callback receipt ve outbox worker çizimi netleştirildi.

README aşama tablosu/kısa rol girişleri/açılır tam indeks ve üretilmiş SVG fallback kazandı; dosyalar taşınmadı. [Görsel sözlük](../quality/visual-documentation.md) iki pinned upstream README/tree incelemesinden alınan sunum örüntülerini ve sınırını tutar. Asset/logo/kod kopyası, runtime dependency veya public/license kararı yok.

Ağ kapalı yerel Mermaid 11.17.2/Chrome render: **35/35 başarı, 0 son parser hatası**; bütün SVG'lerde accessible title/description. 35 görüntü contact sheet'te, dört temsilci ayrıca tam görüntüde incelendi. İlk başarısız ayırıcı denemeleri [inceleme kaydında](../quality/diagram-review.md) korunur; [JSON raporu](../quality/diagram-render-results.json) source ve SVG hashlerini taşır. Checker live render yapmaz; kayıt/current source uyumunu kontrol eder. GitHub dark/mobil/renderer uyumu ve gerçek ürün UI/erişilebilirlik/runtime testleri bu local kontrolle kanıtlanmış değildir. Q02-R1 ilk soru pending; Q03 ve diğer açık owner kararları korunur. Remote teslim ayrıca read-back ile doğrulanır.

Teslim kontrolü geçti: 88 Markdown/931 yerel bağlantı, 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 35 Mermaid/15 belge inventory. Geçici kopyada Mermaid kaynağı değiştirilince stale render hash, SVG değiştirilince stale fallback hash kontrolü beklenen şekilde reddetti; asıl dosyalar değiştirilmedi. Local yayın metinleri 22 hedef dosyayla birebir karşılaştırıldı. Bunlar doküman/render kanıtıdır; uygulama testleri not_run kalır.

# Mevcut durum

2026-10-10 — **Discovery / Product Definition**.

| Alan | Durum |
|---|---|
| Kaynak konuşma derlemesi, vizyon/MVP/karar haritası | Bu dokümantasyon paketinde hazırlanmış |
| Mimari, ADR, görev ve kabul planları | Öneri; uygulama kanıtı yok |
| Benchmark | Birincil belge incelemesi; runtime karşılaştırma bekliyor |
| Uygulama / adapter / dashboard | Başlanmadı |
| Model doğruluğu / tasarruf / kullanıcı talebi | Ölçülmedi |
| Lisans ve nihai marka | Karar bekliyor |

**Sıradaki iş: T01** — golden corpus ve kanıt şablonunu hazırlamak; ardından T02 adapter fizibilitesi. İlk üretim kodu T03'te build/extend ve stack kapısından sonra gelir. Bu paketin GitHub'da bulunması ürün MVP'sinin tamamlandığını göstermez.

## İlerleme kaydetme düzeni

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

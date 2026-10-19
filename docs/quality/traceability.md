# Konuşma → kapsam → engine → görev → doğrulama

Bu tablo **tasarım izlenebilirliğidir; uygulanmışlık kanıtı değildir**. E01–E14 kaynak evreleri [evrim belgesinde](../discovery/evolution.md); F01–F17 [özellik kataloğunda](../product/feature-catalog.md); ENG-01–10 [engine haritasında](../architecture/engines.md); T01–30 [backlog'da](../delivery/backlog.md); V01–28 [doğrulama planında](verification.md) tanımlıdır. Aynı kaynak birden fazla kapsam satırını doğurabilir.

| Kapsam | Kaynak evre | Kullanıcı özelliği | Engine / yüzey | Teslim görevi | Kontrol / kabul kanıtı |
|---|---|---|---|---|---|
| CAP-01 | E01,E04,E06 | F03 | ENG-01,ENG-02 | T06,T09 | AC-03; tür ve span corpus değerlendirmesi |
| CAP-02 | E04,E06,E10 | F02 | ENG-01 | T02,T16,T17 | AC-11; V11 |
| CAP-03 | E10,E11 | F08 | ENG-01,ENG-02,ENG-07 | T22,T25 | AC-11; V16 |
| CAP-04 | E06,E10 | F08 | ENG-01,ENG-02 | T22,T25 | CAP-04 kabul işareti; permission/lineage raporu |
| CAP-05 | E09,E10 | F02 | ENG-01,ENG-07 | T06,T08 | AC-02/14; V01,V02,V19,V20,V21 |
| PRJ-01 | E06 | F01 | ENG-01,ENG-06 | T05 | AC-01; V18,V25 |
| KNO-01 | E07,E10 | F04 | ENG-03,ENG-07 | T07 | AC-10; V12,V14 |
| KNO-02 | E04,E07,E09 | F04 | ENG-03 | T10,T26 | KNO-02 kabul işareti; V12; holdout precision/recall |
| KNO-03 | E06,E07 | F05 | ENG-04 | T10,T26 | KNO-03 kabul işareti; gerekçe ve karşı kanıt örneklem review |
| GRF-01 | E01,E03,E12 | F06 | ENG-05 | T11 | AC-05; V05,V06,V22 |
| GRF-02 | E12,E13 | F06 | ENG-05,ENG-10 | T11,T26 | AC-05; V05,V06 |
| IMP-01 | E12 | F06 | ENG-05 | T12 | AC-05; V07,V22,V28 |
| IMP-02 | E09,E12 | F06 | ENG-05,ENG-08 | T12,T26 | IMP-02 kabul işareti; V08,V16,V28 |
| APR-01 | E10,E11 | F07 | ENG-06 | T08,T13,T19 | AC-06/07; V03,V04,V15,V23 |
| APR-02 | E10,E11 | F07,F11 | ENG-06,ENG-10 | T13,T19 | AC-12; V09 |
| VER-01 | E02,E04,E06 | F09 | ENG-08 | T14,T27 | AC-04; V08,V24 |
| VER-02 | E02,E10,E12 | F09 | ENG-08 | T14 | AC-08; V08,V24 |
| AUD-01 | E09,E10,E12 | F14 | ENG-07 | T07,T15,T23 | AC-10; V14,V17,V26,V27 |
| UX-01 | E02,E03,E07 | F10 | UI,ENG-07,ENG-10 | T19,T20 | AC-07/09; snapshot ve gerçek UI akışı |
| UX-02 | E02,E06,E10 | F11 | ENG-10 | T20,T26 | UX-02 kabul işareti; V09,V11; ready oracle |
| UX-03 | E02,E09 | F15 | UI | T27 | UX-03 kabul işareti; gerçek host panel/fallback testi |
| ROU-01 | E13 | F12 | ENG-09 | T21 | AC-13; insan uygunluk etiketlerinin ayrı testi |
| ROU-02 | E03,E13 | F12 | ENG-09 | T28 | ROU-02 kabul işareti; yetki/kalite/bütçe routing deneyi |
| CST-01 | E03,E04,E09 | F13 | ENG-09,ENG-10 | T09,T18 | AC-13; V13; bounded retrieval/tool token ölçümü |
| CST-02 | E03,E08,E13 | F13 | ENG-09 | T21,T28 | CST-02 kabul işareti; usage null ve eşit kalite maliyet kıyası |
| INT-01 | E01,E05,E13 | F15 | ENG-06,ENG-08 | T27,T28 | INT-01 kabul işareti; outbox retry/conflict ve V27 |
| INT-02 | E06,E09,E10 | F08 | ENG-01,ENG-10 | T18,T22,T25 | INT-02 kabul işareti; iki agent aynı project/revision |
| GOV-01 | E06,E09,E10 | F01,F14 | ENG-01,ENG-06,ENG-08 | T05,T08,T14,T23 | AC-01; V10,V18,V23,V24,V25 |
| GOV-02 | E10,E13 | F14 | ENG-07,ENG-10 | T23 | GOV-02 kabul işareti; V26 |
| TEAM-01 | E13 | F16 | ENG-06,ENG-07; ADR-0009/0010 | T05,T08,T18,T23,T30 | MU01–MU18; C01–C06 ekip kapıları; sync ayrıca P4 tasarımı |
| OSS-01 | E12,E13,E14 | F16 | Yönetişim | T29 | OSS-01 kabul işareti; owner/lisans/isim/kurulum kapısı |
| EVAL-01 | E05,E08,E09,E10,E14 | F17 | ENG-01,ENG-02,ENG-03,ENG-04,ENG-05,ENG-06,ENG-07,ENG-08,ENG-09,ENG-10 | T01,T03,T15,T24 | Holdout, karşılaştırmalı pilot ve faz raporları |

“Kabul işareti” [full-scope](../product/full-scope.md) satırının gözlenebilir beklentisidir. P2–P4 detay testleri ilgili görevde genişletilir; ileri faz satırında V numarası bulunmaması testin yapılmış veya gereksiz olduğu anlamına gelmez. Yeni scope maddesi bu matrise eklenmeden kaybolmuş sayılır; yalnız bir kelimenin dokümanda geçmesi semantik kapsam kanıtı değildir.

## Güncel ekip/veri isteğinin alt eşlemesi

**Sequence/DB/API/tetikleme takip isteği (2026-10-10):** CAP-05,PRJ-01,VER-01/02,APR-01,AUD-01,CST-01/02,INT-01/02 / F01,F08,F09,F13,F14,F15 → [TRG ve API/zamanlama](../architecture/execution-and-integrations.md), [ER/DB bütünlüğü](../architecture/data-relationships.md) → T04c,T06e,T09c,T14c,T18f,T24i,T28c / SEQ-01–08 ve DBR-01–06. Üç yeni sequence ve iki ER; planlı kontroller, gerçek API veya runtime sonucu değil.

**Proje erişimi ve izin kaynağı takip isteği (2026-10-10):** PRJ-01,CAP-02/05,GOV-01,TEAM-01,AUD-01 / F01,F02,F14,F16 → [proje erişim sözleşmesi](../architecture/connection-and-context.md#proje-erişim-sözleşmesi-ve-izin-ekranı) → T05c,T16b,T20g,T24h ve C03/C05 / ACC-01–08. Kaynak/hedef izinleri, grantor ve scope makbuzu, bağlantı envanteri ve kurulum soruları; Q10-A kabul edildi (2026-10-10): ayrı listeleme izniyle öneri; seçim ve gerekli onay olmadan içerik/takip yok. ACC-02 bu ayrımı kapsar. Yeni gerçek bağlantı/yetki oluşturulmadı.

**Yönetim ve diyagram takip isteği (2026-10-10):** TEAM-01,GOV-01,AUD-01,CST-01/02,UX-02,OSS-01 / F11,F13,F14,F16 → [admin/operasyon sözleşmesi](../product/administration-and-operations.md), [lisans ayrımı](../governance/licensing.md), [diyagram incelemesi](diagram-review.md) → T20f,T21c,T23e,T24g ve C03/C05/C06 / ADM-01–10. Günlük kullanıcı, kurulum admin'i, platform operatörü, L1 destek ve paket ayrı; uygulama/lisans kabulü veya yeni runtime benchmark değildir.

**Subagent soru/karar takip isteği (2026-10-10):** APR-01/02,INT-02,GOV-01,UX-02 / F07,F08,F11,F16 → [soru yönlendirme sözleşmesi](../architecture/agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider), [approval UX](../product/approval-ux.md) → T13e,T18e,T24f / ASK-01–08. Bilgi/görüş, yetki içi seçim ve insan kararı ayrımı mevcut yetki ilkesinin açılımıdır; provider messaging veya auto-resume desteği varmış gibi gösterilmez.

**Çok-agent ve ekip kurulumu takip isteği:** INT-02,CAP-02/05,PRJ-01,VER-01,CST-02,GOV-01,TEAM-01 / F08,F09,F13,F16 → [gözlem/işletim sözleşmesi](../architecture/agent-and-team-operation.md) → T02c,T18d,T24e ve C01–C04 / AGT-01–08. Tek insanın çok agent'ı, çok insan üyeliği ve agent execution orchestration ayrı teslimlerdir; özel muhakeme erişimi varsayılmaz. Senaryolar planlıdır.

E01–E14 orijinal kaynak konuşmanın evreleridir; sonraki kullanıcı talebi bu tarihsel kaydı değiştirmez. 2026-10-09 isteği mevcut kapsamı aşağıdaki şekilde detaylandırır:

| İstek | Scope / feature | Tasarım | İş / kontrol |
|---|---|---|---|
| Çok insan ve agent yetkileri | TEAM-01,PRJ-01,GOV-01 / F01,F16 | [Kimlik/rol](../architecture/identity-access.md), ADR-0009 | T05b,T08b,T18b; C01–C04; MU01–MU07,MU10,MU17 |
| Log ve audit | AUD-01,GOV-01 / F14 | [Kayıt sınıfları](../architecture/logging-audit.md) | T07b,C05; MU08/MU09/MU18 |
| DB ve kapasite | AUD-01,TEAM-01 / F14,F16 | [Storage/scale](../architecture/storage-memory-capacity.md), ADR-0010 | T23d,C02/C06; MU13–MU16 |
| Geçici ve kalıcı hafıza | KNO-01,CST-01,GOV-02,INT-02 / F04,F08,F13,F14 | [Retention ve ACL](../architecture/storage-memory-capacity.md) | T06d,T18b,T23c; MU05/MU10–MU12 |
| Başka araçlardan yararlanma | EVAL-01 / F17 | [Hedefli benchmark](../discovery/collaboration-storage-benchmark.md) | T03,T30; belge bulguları, runtime sonuç değil |

Alt işler [team-data-plan](../delivery/team-data-plan.md), MU senaryoları [collaboration-validation](collaboration-validation.md) içindedir; ana 32 scope/30 task sayısını yapay olarak artırmaz.

## Bağlantı, token ve graph takip isteği

**2026-10-10 limit/kötüye kullanım isteği:** CAP-05,CST-01/02,AUD-01,GOV-01,TEAM-01 → ENG-01/06/07/09 ve admin yüzeyi → [limit sözleşmesi](../architecture/resource-limits-and-abuse.md) → T04d/T06f/T08c/T24j, C06 → LIM-01–10. İhtiyaç kullanıcıdan; mekanizma/eşik önerisi ile çalışan kontrol ayrıdır. Ana scope/engine sayısını artırmaz.

**Q09/DEC-17 takip kararı:** GRF-01,APR-02,UX-02,ROU-01 / F11,F12 → ENG-05/06/09/10 → [öncelik ve akış](../product/priority-and-flow.md) → T11c,T20e,T24d / FLOW-01–08. Kabul edilen öncelik ilkesi; algoritma/UX öneridir, uygulama veya ölçüm yoktur. [Yönetim planı](../delivery/project-management.md) Scrum kaynaklarını ve bireysel çalışma uyarlamasını ayırır.

| Mevcut kapsam / özellik | Ayrıntı | İş / kontrol |
|---|---|---|
| CAP-02/05,INT-02 / F02,F08 | [Bağlantı ve context](../architecture/connection-and-context.md) | T02b,T06,T16,T17,T18c; CON-01–08 |
| CST-01/02,ROU-02 / F12,F13 | [Token/bütçe sözleşmesi](../architecture/routing-token-economy.md) | T09b,T18c,T21b,T24c; TOK-01–08; AC-13 |
| GRF-01/02,APR-01,UX-01,AUD-01 / F06,F07,F10,F14 | [Graph ve iptal UX](../product/graph-experience.md) | T11b,T13b,T20b; GUX-01–08; AC-05/06/09/10 |

Orijinal 32 scope korunur. Q04/Q05 tercihleri teknik öneriden ve doğrulanmış davranıştan ayrı [karar kuyruğunda](../delivery/decision-brief.md) tutulur.

Kullanıcı Q04 cevabında olgunlaşma hikâyesi ve AC/DoD/test görünürlüğünü istedi: KNO-01,APR-01,VER-01/02,AUD-01,UX-01 / F04,F07,F09,F10,F14 → [context ve acceptance](../product/task-context-and-acceptance.md) → T13c,T14b,T20c / CTX-01–06. Q05 cevabı CST-01/02,ROU-02 kapsamındaki proje/görev profil seçimini netleştirdi; bütçe/veri izni sağlamadı.

**2026-10-10 ranking takip talebi:** Kaynak, kullanıcının “İlişki Kontrolü ve Kanıt Doğrulaması” devamındaki doğrudan dokümantasyon isteğidir; 40+ ilerlemeyen iş senaryosu ölçüm değildir. DEC-17 → GRF-01/APR-02/UX-02/ROU-01 ve F11/F12 → ENG-05/06/09/10 → [ranking sözleşmesi](../product/priority-and-flow.md) → MVP T11c/T20e/T24d, P2 adayı T26b → FLOW-09–17 ve mevcut FLOW-01–08 regresyonları. Value/scope/karar insan PO'da, üst agent teknik sıra yetkisi mevcut grant ile sınırlı; öneri canonical priority değişimi değildir. Planlı kabul tanımlarıdır, uygulama veya test sonucu değildir.

**2026-10-11 yüksek token riski takip isteği:** CST-01/02,APR-01,GOV-01,ROU-02 → ENG-06/09 → [risk/onay sözleşmesi](../product/token-risk-and-approval.md) → T09d/T19b/T24k → TRA-01–10. İhtiyaç kabul edildi; mekanizma/eşik öneri, uygulama/test yok.

**2026-10-11 farklı chat'ler ve hızlı konuşma isteği:** CAP-01/02/05,PRJ-01,KNO-01/02,CST-01,UX-01 → ENG-01/02/03/06/07/09 → [çoklu chat/lag](../architecture/multi-chat-and-processing-lag.md) → T05d/T10b/T06g/T18g/T24l → CHAT-01–06/LAG-01–06. Kaynak bağlama, görev çıkarımı, ortak hafıza ve backlog gecikmesi ayrıdır; yeni scope/engine veya ölçülmüş kapasite iddiası yok.

**2026-10-11 yapıştırılan devam paketi/hafıza konuşması:** KNO-01/02,APR-02,UX-02,CST-01/02,GOV-01 ve F04/F08/F11/F13 → ENG-03/06/07/09/10 → [devam paketi](../product/resume-package-and-memory.md) / [Spike-1 v1](../delivery/spike-1-v1.md) → T20h/T18h/T24m ve S1-01–06 → RES-01–08. Aktarılan assistant önerileri proposed; Spike-0/Projects iddiaları ve hafıza başarısı doğrulanmış sonuç değildir. Q11 açık; tam kapsam korunur.

**2026-10-11 kullanıcının dosya/yükleme ve gerçek karar örneği:** KNO-01/02,APR-01,VER-01/02,INT-02,UX-01,CST-01 ve F04/F07/F08/F09/F10/F13 → ENG-03/06/07/08/10 → [niyet→gerçekleşme](../product/intent-to-reality-gap.md) → T01,T03,T14d,T18i,T20i,T24n → GAP-01–10. Kullanıcı problemi bildirdi; yaygınlık/Claude failure reproduction yok; mekanizma öneri ve kontroller not_run. [Projects rekabet incelemesi](../discovery/claude-projects-overlap.md) EVAL-01/F17/T03/T24'e girdi; farklılaşma doğrulanmış sonuç değildir.

**2026-10-11 son evrimin repo genelinde tutarlılığı isteği:** DEC-18 ihtiyacı / DEC-19 proposed yatırım yolu → KNO/APR/VER/INT/UX/EVAL mevcut kapsamı → [güncel yön](../product/current-direction.md), [ADR-0011](../architecture/adr/0011-target-application-evidence.md), ApplicationExpectation/Target/Observation/Assessment ve ER-03 → T01/T02d/T03a–c + üretim T14d/T18i/T20i/T24n → GAP-01–10/RES, DBR/SEQ regresyonları. [Versioning](../governance/versioning.md) doküman düzenidir; product v3 veya runtime kararı değil. 32 scope,17 feature,10 engine,14 orijinal kaynak evresi korunur.

**2026-10-11 sözlük/pattern ve token takip isteği:** Kullanıcı işlem iddiası/kullanıcıdan istek metinlerinin kelime/pattern analizini sordu. CAP-01/05,CST-01/02,VER-01,APR-01 → ENG-02/03/06/08/09/10 → [lexical ön eleme](../architecture/lexical-prefilter.md) ve [token sözleşmesi](../architecture/routing-token-economy.md) → T01e/T09e/T24o → LEX-01–08. İhtiyaç ve teknik öneri ayrı; kural dosyası/DB tablosu seçim önerisi, doğrudan işlem/onay yok. Gerçek model çıktısı sıklık/pattern araştırması, runtime parser ve tasarruf ölçümü not_run. Orijinal 32 scope/30 ana görev/10 engine korunur.

**2026-10-11 konuşma dili takip isteği:** Kullanıcı İngilizce dışındaki konuşmalardan aynı dilde not/proje çıktısı üretimini ve maliyetli otomasyonun P2 adaylığını istedi. CAP-01/03/04,KNO-01/02,APR-01,UX-01/02,CST-01/02,EVAL-01 → F03/F04/F07/F08/F10/F13/F17 → ENG-01/02/03/06/07/09/10 → [dil/yerelleştirme](../product/language-and-localization.md) → T05e/T24p temel, T25a/T26c P2 → LANG-01–08. Q12-A sabit proje dili/değişim önerisi kabul edildi; veri/model/bütçe yetkisi veya bütün dil desteği kabul edilmiş sayılmaz. Orijinal 32 scope/30 task/17 feature/10 engine korunur.

**2026-10-11 Q12 geç cevap örneği:** Kullanıcı cevap verilmese sorunun unutulacağını ve geciken yanıtın eski bağlamına bağlanması gerektiğini belirtti. APR-01/02,KNO-01/02,CAP-01/05,UX-01/02,GOV-01 → F03/F04/F07/F11 → ENG-01/02/03/06/07/10 → [bekleyen soru/geç cevap](../product/pending-questions-and-late-answers.md) → T01,T13e,T18e,T19,T20i,T24f → ASK-01–08/LATE-01–08. İhtiyaç kullanıcıdan; mekanizma teknik öneri, kaynak coverage/platform/model yeteneği ve test sonucu değil. Önceden atıf verilen üç alt dilim backlog'a somutlaştırıldı; orijinal 32 scope/30 ana görev korunur.

**2026-10-12 receiver sözleşmesi ve doküman/diyagram takip isteği:** Kullanıcı yerel build devamını ve repo/şema güncelliğini istedi. EVAL-01,KNO-01/02,APR-01,VER-01,CST-01/02 → ENG-03/06/09/10 → P0 T03u/v/w → [ilk gerçek başarısız çıktı](receiver-001-result.md), [yerel schema/source guard](receiver-contract.md), [37-source inventory](diagram-review.md).16 yeni test/6 invalid örnek source/action/question/abstention/type sınırını doğrular; raw/prompt/oracle ve önceki36 Mermaid kaynağı aynı. Production T09/T13/T18/T24, model/native/gold/ROI ve T03c yatırım kapıları açık; scoped guard veya diagram render bu kapıları kapatmaz. Yeni kaynak evresi/scope/engine eklenmedi.

## R24 sonrası tipli dönüşüm kanıtı

ROU-01/CST-01/APR-01 → E13/F12/F13/F07 → ENG-09/ENG-06 → T03aa. [Kod ve doğrulama](typed-review.md), zaten yapılandırılmış source-bound kayıtların tekrar modelle üretilmesini bu iki P0 fixture'da kaldırır. T09 extraction, T13 production approval ve T21 usage görevleri bununla complete sayılmaz; yeni ürün kapsamı veya engine status değişimi değildir.

19Ekim kaynak/model yönetim alt kanıtı: CAP-02/03 ve APR-01/T09/T17/T19/T21 için [kalıcı activation backend](../architecture/model-activation-runtime.md), API/queue/admission ve revoke/restore/legacy-bypass kontrolleri. Yeni feature veya task değil; gerçek kaynak paylaşımı ve ücret onayı ayrı kalır.

19Ekim finite worker kanıtı: CAP-02/03, APR-01 ve CST-01/T09/T17/T19/T21 için [kalıcı loop/pass admission](../architecture/model-activation-runtime.md#kalıcı-sınırlı-işleme-döngüsü--sonraki-backend-teslimi), restart caps, unknown kullanım durması ve HTTP/thread testleri. Yeni kaynak veya ücret onayı çıkarılmaz.

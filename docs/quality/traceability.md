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

**Q09/DEC-17 takip kararı:** GRF-01,APR-02,UX-02,ROU-01 / F11,F12 → ENG-05/06/09/10 → [öncelik ve akış](../product/priority-and-flow.md) → T11c,T20e,T24d / FLOW-01–08. Kabul edilen öncelik ilkesi; algoritma/UX öneridir, uygulama veya ölçüm yoktur. [Yönetim planı](../delivery/project-management.md) Scrum kaynaklarını ve bireysel çalışma uyarlamasını ayırır.

| Mevcut kapsam / özellik | Ayrıntı | İş / kontrol |
|---|---|---|
| CAP-02/05,INT-02 / F02,F08 | [Bağlantı ve context](../architecture/connection-and-context.md) | T02b,T06,T16,T17,T18c; CON-01–08 |
| CST-01/02,ROU-02 / F12,F13 | [Token/bütçe sözleşmesi](../architecture/routing-token-economy.md) | T09b,T18c,T21b,T24c; TOK-01–08; AC-13 |
| GRF-01/02,APR-01,UX-01,AUD-01 / F06,F07,F10,F14 | [Graph ve iptal UX](../product/graph-experience.md) | T11b,T13b,T20b; GUX-01–08; AC-05/06/09/10 |

Orijinal 32 scope korunur. Q04/Q05 tercihleri teknik öneriden ve doğrulanmış davranıştan ayrı [karar kuyruğunda](../delivery/decision-brief.md) tutulur.

Kullanıcı Q04 cevabında olgunlaşma hikâyesi ve AC/DoD/test görünürlüğünü istedi: KNO-01,APR-01,VER-01/02,AUD-01,UX-01 / F04,F07,F09,F10,F14 → [context ve acceptance](../product/task-context-and-acceptance.md) → T13c,T14b,T20c / CTX-01–06. Q05 cevabı CST-01/02,ROU-02 kapsamındaki proje/görev profil seçimini netleştirdi; bütçe/veri izni sağlamadı.

# Ardışık uygulanabilir backlog

MVP, P2 ve P3 için ayrı tablolar ve ürün teslim ağacı [faz takip görünümünde](phase-tracker.md) bulunur. Ana görev tanım/durum/ön koşulu burada tutulur; görünüm aynı değişiklikte eşleştirilir.

Q09/DEC-17 uyarınca engeli kaldıran uygulanabilir adım önce değerlendirilir. T01–T30 başlangıç teslim sırasıdır; bütün ön koşullar doğrulanmış teknik blocker gibi graph'a otomatik alınmaz. Refinement gerçek teknik/izin gate'i ile plan sırasını ayırır; kalite kapıları korunur. [Öncelik ve akış](../product/priority-and-flow.md) GRF-01/APR-02/UX-02/ROU-01 kapsamını detaylandırır.

| Yeni alt dilim / bağımlılık | Teslim / durum | Kabul |
|---|---|---|
| T11c / T11 | TODO / P1a: başlangıç-bitiş gate'i, blocker assessment, revision bağlı traversal, benzersiz downstream | FLOW-01–04/09–11/14; deterministik rank, aging ve neden/next actionable; eksik graph/ACL/context yanlış ready veya tamlık üretmez |
| T20e / T11c,T13,T20 | TODO / P1b: açıklamalı öncelik, inbox/board/graph ve sıra değişimi review'u | FLOW-05–08/12–15; canonical priority/rank/execution order ayrı, grant kontrollü board; stale/override, tekrar bildirim ve bağımsız iş |
| T24d / T20e,T24 | TODO / P1b: sentetik oracle ve owner pilotu | FLOW-01–15; 40+ sentetik task; zorunlu sette yanlış ready/yetkisiz mutation 0; bekleme, next-action seçimi ve uyarı yükü baseline |

T01 corpus FLOW örneklerini de içerir. Bildirim kanalı/sıklığı açıkken yalnız uygulama içi sıra hazırlanır. Alt dilimler planlıdır, uygulanmadı.

**T01/T02/T03 IN_PROGRESS; diğer 27 ana görev TODO.** P0 deney kodu var; hiçbir ana görev kapanmadı. [Audit düzeltme kaydı](../quality/audit-remediation.md) kanıt/kalan kapsamı ayırır. İlk [corpus hazırlığı](../quality/baseline.md) somut veri çıktısıdır; bu plan ürün uygulamasını gerçekleştirmiş değildir. Her görevi küçük bir PR/çalışma dilimi olarak ele al; büyük keşif satırlarını belirtilen yüzey/connector bazında ayrı alt görevlere böl. Tahminler takvim taahhüdü değil iş parçalama boyutudur. Görev kapanışı: değişiklik + AC kanıtı + ilgili kontrol + status güncellemesi. [Roadmap](../../ROADMAP.md) fazları, [MVP](../product/mvp.md) AC'leri tanımlar.

[Engine haritası](../architecture/engines.md), [runtime sözleşmeleri](../architecture/runtime-contracts.md) ve bu belgenin sonundaki **sistem sözleşmesi alt dilimleri** ilgili görevlerin kapsamına dahildir. “1 küçük PR” üst sınır taahhüdü değildir; bu alt dilimleri sırayla tamamla. 30 ana görev korunmuştur; güvenlik/veri bütünlüğü ayrıntıları son faza ertelenmez.

| ID | Faz | Ön koşul | Görev |
|---|---|---|---|
| T01 | P0 | — | Golden corpus ve karşılaştırma protokolü |
| T02 | P0 | T01 | İki coding yüzeyinde capability spike |
| T03 | P0 | T01,T02 | Native/extend/build ve teknoloji kararı |
| T04 | P1a | T03 | Runtime iskeleti ve sözleşme doğrulayıcıları |
| T05 | P1a | T04 | Proje kimliği ve binding |
| T06 | P1a | T05 | Source ingress ve checkpoint |
| T07 | P1a | T06 | Domain log ve projector |
| T08 | P1a | T07 | Atomic change set ve policy |
| T09 | P1a | T08 | Extraction ve bounded retrieval |
| T10 | P1a | T09 | Temel reconciliation |
| T11 | P1a | T10 | Tipli gerekçe graph |
| T12 | P1a | T11 | Impact preview ve apply planı |
| T13 | P1a | T12 | Review işlemi ve güvenilir onay |
| T14 | P1a | T13 | Evidence ve false-done düzeltmesi |
| T15 | P1a | T14,T07c | Teknik kanıt kapısı |
| T16 | P1b | T15 | Claude Code adapter |
| T17 | P1b | T16 | Codex adapter |
| T18 | P1b | T17 | Minimal MCP ve cross-agent read |
| T19 | P1b | T18 | Proje seçimi ve Review Inbox UI |
| T20 | P1b | T19 | Board, Graph ve Timeline |
| T21 | P1b | T20 | Routing etiketleri ve usage kaydı |
| T22 | P1b | T21 | Chat import ve prompt lineage |
| T23 | P1b | T22 | Backup, export ve yerel güvenlik |
| T24 | P1b | T23 | MVP kabul ve kullanıcı pilotu |
| T25 | P2 | T24 | Chat yüzeyleri ve cross-provider adapter araştırması |
| T26 | P2 | T25 | Gelişmiş reconciliation ve orphan audit |
| T27 | P2 | T26 | GitHub evidence ve görünür panel deneyi |
| T28 | P3 | T27 | Maliyet raporu ve kontrollü entegrasyonlar |
| T29 | P3 | T28 | Public release hazırlığı |
| T30 | P4 | T29 | Ekip/cloud/open-core keşfi |

## T01 — Golden corpus ve karşılaştırma protokolü

- **Durum / faz:** IN_PROGRESS / P0. **Bağımlılık:** —. **Kapsam ID:** EVAL-01.
- **İş:** En az 30 anlamlı kayıt içeren 6 sentetik oturum; iki proje, ret, partial done, karar değişimi ve bekleyen onay; beklenen tip/ilişki/durumları etiketle. Ek no-op ve sıfır expansion örnekleriyle gereksiz task üretimini de değerlendir; 30 anlamlı kaydın yerine no-op sayma.
- **Kabul:** Her örneğin source span'ı ve beklenen sonucu var; model geliştirmede kullanılmayan holdout ayrılmış; kişisel veri yok.
- **Doğrulama:** Corpus şema kontrolü ve insan örneklem incelemesi.
- **Hazırlanan çıktı:** [Corpus](../../examples/corpus/README.md), [baseline hazırlığı](../quality/baseline.md), `scripts/check_corpus.py`. 6 oturum/2 proje, 58 mesaj/66 annotation/46 farklı KnowledgeRecord ve 7 no-new-record; kaynak/oracle ayrı, aile split ve Unicode span hashleri denetlendi. Etiketler AI taslağı; insan review'u pending, sealed holdout yok. Ürün testleri not_run.
- **Kalan kapanış:** İnsan örneklem/etiket incelemesi, tam karşılaştırma koşulları, T01e/T01f ayrıntıları ve FLOW/authority/crash fixture kapsamı; yalnız veri kontrolüyle T01 complete yapılmaz.
- **Boyut:** 1 küçük oturum.
- **Son ilerleme:** 2026-10-13 · T01g/H1-H3 ve T01i/H4 partial davranış review tamamlandı; source/rubric/cevap kayıtları korunur. T03y receiver hazırlığı tamamlandı; bu T01 exact gold/adjudication/holdout kapanışı değildir.
- **Sıradaki adım:** Exact kaynak/etiket inceleme ve adjudication kuyruğundaki kalanları küçük örneklerle tamamla; human gold/holdout gate açık. Receiver isteği tekrar hazırlanmayacak: T03y DONE, Q03-R6 yalnız yeni model run onayı bekliyor.


### İlk üç davranış incelemesi kapanışı

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T01g / — | DONE / P0: H1/H2/H3 ilk davranış incelemesi | Üç açık insan yanıtı, soru/açıklama/kapsam ve source/oracle hash bağlı ayrı review kayıtları mevcut; [kuyruk](../quality/human-review-queue.md). Exact candidate etiketleri, tam oracle/adjudication/gold/holdout bu kapanışın dışında |
| T01h / T01g | DONE / P0: iki yeni development family ve ayrı kaynak/rubric paket | Sekiz sentetik mesaj/iki proje; eski-güncel soru revision,quoted/planned,EN claim/not_run/ambiguous; hash/source/schema consistency ve5 harness testi; [paket](../../examples/adversarial-smoke/README.md). İnsan exact gold/holdout/gerçek inference değil |
| T01i / T01h | DONE / P0: H4 quoted/planned partial insan review | Kullanıcı1-EVET, source/rubric hash ve explicit kapsam [review kaydında](../quality/reviews/h4-behavior.json); tam6label/gold/holdout veya dispatch yetkisi değil |

## T02 — İki coding yüzeyinde capability spike

- **Durum / faz:** IN_PROGRESS / P0. **Bağımlılık:** T01. **Kapsam ID:** CAP-02.
- **İş:** Claude Code ve Codex'in kurulu/test edilebilir sürümlerini kaydet; izinli hook/transcript olayını izole fixture'da gözle.
- **Kabul:** Her yüzey için version, olay, payload, izin, truncation ve coverage raporu var; erişilemeyenler unsupported/unknown.
- **Doğrulama:** Yeni mesaj, final output, tool failure, kapanışsız session ve offline deneyi.
- **Beklenen dosya alanı:** `docs/discovery/adapter-feasibility.md` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Yüzey başına küçük deney.
- **Son ilerleme:** 2026-10-13 · Salt okunur host inventory: PATH Codex CLI0.162.0-alpha.17.2 version çıktı; sandbox alias yazımını reddetti. Claude command PATH'te yok, installation unknown. Capture40fixture korunur; gerçek hook/session/transcript veya model çalıştırılmadı.
- **Sıradaki adım:** [Hazırlık kapısında](implementation-readiness.md) seçilmiş Codex/Claude host ve scoped grant ile gerçek capability kontrolü. MCP erişimi tam otomatik capture kanıtı değil.

## T03 — Native/extend/build ve teknoloji kararı

- **Durum / faz:** IN_PROGRESS / P0. **Bağımlılık:** T01,T02. **Kapsam ID:** EVAL-01.
- **İş:** [Güncel yön](../product/current-direction.md) uyarınca yeni Claude Projects, [WrongStack](../discovery/wrongstack-review.md) ve mevcut Cortex/Tracker/mai-mcp/Beads adaylarını aynı oracle'ın uygun bölümünde karşılaştır. T03a geçici deney yöntemi/stack kapsamı, T03b yetkili sınırlı prototip + native baseline, T03c owner yatırım/production stack kararı olarak sırayla ilerle; lisans ve kurulum etkisini incele. [Benchmark bulgularındaki](../discovery/benchmark-findings.md) güncel yapılandırma ve sonuç şablonunu kullan; [şikâyet araştırmasındaki](../discovery/user-research.md) düzeltme/karşı kanıtı atlama.
- **Kabul:** Native/config/custom/unknown matrisi, GAP/RES sonuçları ve kullanıcı yönetim yükü kanıtı var; native/extend/build/ek deney/durdur seçenekleri gerekçeli. Owner kararı ilgili ADR'lere işlenir; deneme yapılamayanlar not_run. T03a prototype yöntemi production stack onayı değildir; build seçilmeden T04 başlamaz.
- **Doğrulama:** Versiyonlu rapor ve owner karar kaydı; test yapılmadıysa kapı açık kalır.
- **Beklenen dosya alanı:** `docs/discovery/pilot-comparison.md; docs/architecture/adr/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Karşılaştırma başına küçük deney.
- **Risk durumu:** Observed / High · R23/R24: ilk receiver tam çıktı JSON geçerli, abstention/type/record-action contract failed. T03w/x/y yerel guard ve yeni istek hazır; gerçek yeniden ölçüm henüz yok. Usage/hard cap unknown; [ilk run](../quality/receiver-001-result.md), [yeni öneri](../quality/receiver-next-plan.md).
- **Denemeler / sonuç:** S02 erişim/span failure, MEMBERSHIP-001 incomplete, MEMBERSHIP-002/003 dar typed/source draft eşleşmeleri. RECEIVER-001 invalid_contract/unscored; RECEIVER-002 actual tek run invalid_contract/unscored; missing next_actions ve ambiguous soru bağlama ret. R22 multi-answer fixture düzeltmesi T03r DONE; eski run hataları korunur, güncel teknik engel diye tekrar sunulmaz.
- **Etkilenen iş:** T03 semantik receiver kalite, gerçek capture/native kıyas ve T03c yatırım/stack kapıları açık. T03y istek/scorer ve T03x bağımsız review fixture kodu DONE; insan gold/gerçek hedef/production IAM/UI kabulü değildir.
- **Son ilerleme:** 2026-10-13 · T03ac [kalıcı explicit reply proposal](../quality/reply-store.md) DONE;14 yeni/248 semantik test. Late source binding/restart/dedup/conflict/current-context/atomic no-resume; gerçek approval, UI/IAM/semantik reply parsing yok. Actual receiver raw aynı, yeni model/API0; Q03-R6 tüketildi.
- **Sıradaki adım:** RECEIVER-002 tek run tamamlandı/invalid_contract; Q03-R6 tüketildi, yeniden izin bekleyen iş değil. T03aa typed/source-bound readback/action taslağı tamamlandı, tekrar hazırlanmaz; ilk raw/strict scorer değiştirilmez. Sıradaki owner kararı [Q15 koşullu build geçişi](build-transition-proposal.md): T04 bağımlılığı/runtime seçimini incele; cevap gelmeden mevcut gate değişmez. T01 exact label/T02 capture/T03 native-ROI ölçümleri ayrıca açık kalır. Yeni model dispatch yetkisi yok; production/native/gold/ROI/T03c açık.


### T03 altında tamamlanan küçük teslimler

Ana gate'in tamamlanması bu tabloyla değişmez. DONE yalnız belirtilen teslim scope ve kabul koşuluna aittir; production/model/native testleri T03f/T03b'de açık kalır.

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03g / T03f | DONE / P0: bounded quote adapter ve ayrı candidate rubric | Negatif source/type/authority/stale/duplicate kontrolleri passed; immutable raw korunur; [kanıt](../quality/source-anchor-adapter.md). Gerçek model quality kapsam dışı |
| T03h / T03g | DONE / P0: gönderimsiz API paket ve saved response import | Schema/payload/source sınırı, refusal/incomplete/unknown ve no-overwrite testleri passed; [kanıt](../quality/quote-api-package.md). Provider/schema acceptance ve bütçe enforcement kapsam dışı |
| T03i / T03f | DONE / P0: tek selected local file observer | Dokuz negatif/pozitif test ve önceki belgeyle gerçek local hash match; [kanıt](../quality/local-observer.md). GitHub upload/AC/production IAM kapsam dışı |
| T03j / T03g,T03i | DONE / P0: tek komutluk integrated zincir | Quote-only → ayrı seçim → AND/OR impact → bounded local read → partial/full AC → restore; yedi checkpoint ve 66 suite testi passed; [kanıt](../quality/integrated-chain.md). Model/gerçek grant/remote target kapsam dışı |
| T03k / T03g,T03h | DONE / P0: mevcut üyelik source-only paket ve batch import/score | Dört synthetic mesaj, iki ayrı proje/contract, oracle dışarıda; 6 negatif/pozitif test ve 72 suite passed; [plan/kanıt](../quality/membership-smoke-plan.md). Gerçek model send/usage/accuracy kapsam dışı |
| T03l / T03k | DONE / P0: onaylı MEMBERSHIP-001 tek gönderim ve değişmez ölçüm kaydı | Raw UI-copy hash, iki source binding/üç quote pass; exact candidate gate incomplete ve no-mutation guard kaydedildi; [run](../quality/membership-001-result.md). Başarı/kabul gate'i bu kapanışla kapanmaz |
| T03m / T03l | DONE / P0: separate typed v2 field/type contract ve offline paket | Dört typed negatif/pozitif test, ayrı contract ID ve 4708-byte prompt; 78 suite passed; [v2/kanıt](../quality/membership-001-result.md). Gerçek v2 model davranışı not_run; no semantic alias repair |
| T03n / T03m | DONE / P0: onaylı MEMBERSHIP-002 gerçek typed çıktı ve ölçüm | Tek gönderim, dört authored_draft aday eşleşti, source/type/hash pass; iki ayrı guard no-mutation ve iki yeni regresyon testi, 80 suite passed; [run](../quality/membership-002-result.md). Human gold/production/domain doğruluğu kapsam dışı |
| T03o / T03n | DONE / P0: gerçek kayıtlı candidate → controlled karar/impact/hedef/AC/restore replay | Kendi request/source kimliği, bağımsız fixture receipt ve13 authored checkpoint; 6 negatif/pozitif test, 86 suite passed; [rapor](../quality/membership-chain-replay.md). Yeni inference/production IAM/remote uygulama/human gold değil |
| T03p / T03o | DONE / P0: aynı source'ta lexical ve saved-model dar ölçüm | Dört mesaj/iki request, shared span/kind skorları, source-only extraction ve capability farkı kaydı;5 yeni harness testi/91 suite passed; [rapor](../quality/same-source-comparison.md). Genel/native/domain/para üstünlük değil |
| T03q / T03p,T01h | DONE / P0: yeni8-message MEMBERSHIP-003 gerçek typed output ve ölçüm | Tek onaylı send/retry0,6 draft aday/2 scope-no-candidate,source/hash/type pass; whole-batch ve per-candidate no-mutation guard/93suite; [sonuç](../quality/membership-003-result.md). Çok-aday production reconcile/human gold/native/cost gate değil |
| T03r / T03q | DONE / P0: birden fazla source-bound cevap için read-only öneri koleksiyonu | Eski/current/ambiguous ayrı; conflict/duplicate/agent/foreign/stale/no-mutation ve separate receipt negatifleri;9 yeni test/102 suite; [rapor](../quality/proposal-collection.md). Kalıcı çok-soru production reconcile veya model kalite gate değil |
| T03s / T03r | DONE / P0: deterministic kaynak bağlı resume ve eşit bilgiyle dosya serialization kıyası | İki temsil aynı core/checklist, stale source/state/access/tamper/byte/no-overwrite;8 yeni test/110 suite; [rapor](../quality/resume-file-comparison.md). Gerçek alıcı model/native/user burden/production RES gate değil |
| T03t / T03s | DONE / P0: kayıpsız inline source/record table ve çözülmüş readable model view | Frozen core exact, üç temsil aynı authored checklist;11 yeni test/121 suite; byte azalması ve missing source/stale/reference/no-truncation negatifleri; [rapor](../quality/resume-compaction.md). Model/token/production/native gate değil |
| T03u / T03t | DONE / P0: bounded fresh-session receiver request ve bağımsız saved-output evaluator hazırlığı | 7950byte kaynak-only prompt, ayrı authored oracle,13 yeni test/134suite; strict source/schema/critical negative/incomplete/no-dispatch; [plan](../quality/receiver-smoke-plan.md). Gerçek send/not_run, gold/kalite gate değil |
| T03v / T03u | DONE / P0: tek configured Luna/Low native run ve first-output kanıtı | Dispatch öncesi belge/permission, actualraw immutable/fullmessagecapture, invalidabstention ret/2regression/136suite, tokenunknown; [sonuç](../quality/receiver-001-result.md). Model kabul/gold/production gate değil |
| T03w / T03v | DONE / P0: offline strict shape schema ve kaynak bağlı receiver guard |16 yeni/152 semantik test;6 incelenebilir invalid örnek, known-question/ambiguous/type/record-action/false-evidence retleri; [rapor](../quality/receiver-contract.md). Eski raw/prompt/oracle/evaluator aynı; model/provider kabulü yeniden test edilmedi |

### T03 altında son küçük uygulama

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03x / T03w | DONE / P0: Q14-A bağımsız proje review ve açıklama cevabı descriptor |20 yeni/172 semantik test; valid diğer proje korunur, technical/missing/abstain/ambiguous görünür; global source/access/kimlik ret ve atomic-group birlikte bekleme; explicit late/stale/agent/source/idempotent association. [Rapor](../quality/project-review.md). Frozen raw/scorer unchanged, model/API/mutation0; durable Inbox/UI/IAM/host resume kapsam dışı |

### T03 altında tamamlanan yeni deney hazırlığı

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03y / T03x | DONE / P0: yeni source-only receiver isteği ve ortak makine schema/scorer |20 yeni/192 semantik test;8 exactsource/6record,8089byte/8192tavan, hermetik3file preparation, typed/source/duplicate/abstention/no-overwrite. [Plan](../quality/receiver-next-plan.md). Actualsend0/izin yok, provider/model/gold/ROI kapısı açık; eski raw/prompt/scorer aynı |

### T03 altında tamamlanan wire-2 inceleme yolu

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03z / T03y | DONE / P0: wire-2 için Q14-A bağımsız proje incelemesi |14 yeni/206 semantik test; global identity/access/source preflight, local type/source error, clean/invalid abstain/missing, atomic bekleme, immutable v1 ret. [Rapor](../quality/project-review-next.md). Strict kalite scorer aynı; model/API/mutation0, durable Inbox/late-reply uygulama/production kapsam dışı |

### T03 altında tamamlanan model çağrısız tipli dönüşüm

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03aa / T03z | DONE / P0: selected typed record'dan readback ve safe action taslağı |13 yeni/222 semantik test;6record bağımsız authored kıyas, null ambiguous binding, access/freshness/atomic/no-oracle/no-raw/no-overwrite. [Rapor](../quality/typed-review.md). Yeni inference0; free-text extraction/human gold/IAM/production kabulü değil |

### T03 altında tamamlanan kalıcı inceleme snapshot

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03ab / T03aa | DONE / P0: SQLite inceleme snapshot deposu |12 yeni/234 semantik test; restart aynı pending descriptor, current scope/access, unique/dedup/rollback/append-only/tamper/two-writer. [Rapor](../quality/review-store.md). Human reply resolution/UI/production IAM/backup/crash ayrı; canonical mutation/model0 |

### T03 altında tamamlanan kalıcı explicit cevap önerisi

| Alt görev / ön koşul | Durum / teslim | Kabul ve doğrulama |
|---|---|---|
| T03ac / T03ab | DONE / P0: persisted clarification'a explicit source-bound reply proposal |14 yeni/248 semantik test; current record/CID/question revision/source, restart/unique/retry/conflict/actor/access/rollback/tamper/two-writer. [Rapor](../quality/reply-store.md). Actual approval/resolved/job resume/semantic parsing/production IAM yok |

## T04 — Runtime iskeleti ve sözleşme doğrulayıcıları

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T03. **Kapsam ID:** PRJ-01,AUD-01.
- **İş:** Onaylı stack için domain/storage sınırı, package sürümleri, lisans envanteri ve test komutları oluştur.
- **Kabul:** Tek yerel başlatma yolu; sentetik input dışında veri yok; CI/test komutları belgelendi.
- **Doğrulama:** Temiz kurulum ve schema-invalid payload reddi.
- **Beklenen dosya alanı:** `apps/hub/; packages/domain/; manifests` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T05 — Proje kimliği ve binding

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T04. **Kapsam ID:** PRJ-01,GOV-01.
- **İş:** Project CRUD kapsamını minimum tut; değişmeyen ID, session binding ve quarantine uygula.
- **Kabul:** Aynı adlı projeler ayrılır; belirsiz binding yazma yapmaz; query de scope denetler.
- **Doğrulama:** AC-01; çapraz proje read/write reddi.
- **Beklenen dosya alanı:** `packages/domain/; packages/storage/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T06 — Source ingress ve checkpoint

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T05. **Kapsam ID:** CAP-01,CAP-05.
- **İş:** Normalize source zarfı, safe payload ref, kalıcı ack, source dedup ve cursor tut.
- **Kabul:** Aynı event iki kez bir etki; aynı metin farklı mesajda korunur; crash cursor atlatmaz.
- **Doğrulama:** AC-02, AC-14; retry/rotation/truncation.
- **Beklenen dosya alanı:** `packages/capture/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T07 — Domain log ve projector

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T06. **Kapsam ID:** AUD-01,KNO-01.
- **İş:** Event append, optimistic stream version, projection ve replay uygula.
- **Kabul:** UPDATE/DELETE event API yok; replay aynı digest; migration sürümü kayıtlı.
- **Doğrulama:** AC-10; crash ve late-event testleri.
- **Beklenen dosya alanı:** `packages/storage/; packages/domain/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T08 — Atomic change set ve policy

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T07. **Kapsam ID:** APR-01,CAP-05.
- **İş:** Temp ID çözümü, create/link atomicity, digest/base revision ve idempotency uygula.
- **Kabul:** Yarım graph oluşmaz; key/digest çakışması conflict; agent onay taklit edemez.
- **Doğrulama:** AC-03, AC-06; iki yazar ve double submit.
- **Beklenen dosya alanı:** `packages/domain/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T09 — Extraction ve bounded retrieval

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T08. **Kapsam ID:** CAP-01,CST-01.
- **İş:** Önce fixture/deterministic extractor; ardından gerçek serbest metinden kaynaklı tip/karar/görev/soru/ilişki adayları çıkaran çalışan extraction yolu. Provider arayüzü, FTS ve source span doğrulama; Q03-R1 yalnız ilk no-model dilimin sırasıdır, otomatik extraction'ı opsiyonel yapmaz.
- **Kabul:** Desteksiz model sonucu canonical state yazamaz; truncation ve missing source görünür. Önceden etiketli/mock adayların işlenmesi otomatik anlam çıkarımının tamamlandığı sayılmaz; yöntem ve kapsam belirtilir.
- **Doğrulama:** CAP tipleri ve invalid structured output fixture; gerçek extractor/holdout ölçümü T03f/T24q kapısına bağlanır. İzin/bütçe eksikse test not_run/blocked, fixture pass ile kapanmaz.
- **Beklenen dosya alanı:** `packages/capture/; packages/reconciliation/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T10 — Temel reconciliation

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T09. **Kapsam ID:** KNO-02,KNO-03.
- **İş:** Exact duplicate, related/refines/conflict/rejected revival önerisi ve evaluation kaydı.
- **Kabul:** Aynı fikir tekrar task olmaz; onaylı karar doğrudan overwrite edilmez.
- **Doğrulama:** Golden corpus precision/recall; new-is-not-true senaryosu.
- **Beklenen dosya alanı:** `packages/reconciliation/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T11 — Tipli gerekçe graph

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T10. **Kapsam ID:** GRF-01,GRF-02.
- **İş:** required_by/dependency ayrımı, AND/OR/unknown evaluator ve cycle kontrolü.
- **Kabul:** OR kalan gerekçeyi korur; boş gerekçe unknown; supersession cycle reddi.
- **Doğrulama:** Truth table ve examples/impact-scenario.json oracle.
- **Beklenen dosya alanı:** `packages/impact/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T12 — Impact preview ve apply planı

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T11. **Kapsam ID:** IMP-01,IMP-02.
- **İş:** Trigger/version bazlı bounded traversal, reason path ve etki proposals üret.
- **Kabul:** Keep/update/review/obsolete gerekçeli; tamamlanmış geçmiş korunur; eksik frontier görünür.
- **Doğrulama:** AC-05; missing-link ve traversal-limit.
- **Beklenen dosya alanı:** `packages/impact/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T13 — Review işlemi ve güvenilir onay

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T12. **Kapsam ID:** APR-01,APR-02.
- **İş:** Accept/reject/defer/compare, digest-bound approval ve dependent operation group ekle.
- **Kabul:** Serbest metin gerektirmez; stale/double approval güvenli; partial selection referansları bozmaz.
- **Doğrulama:** AC-06/07; stale approval ve role testleri.
- **Beklenen dosya alanı:** `apps/hub/; packages/domain/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T14 — Evidence ve false-done düzeltmesi

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T13. **Kapsam ID:** VER-01,VER-02.
- **İş:** AC/artifact revision-bound evidence, claim ve verification state ekle.
- **Kabul:** Agent done sözü verified olmaz; failed test yeni event ile reopen eder.
- **Doğrulama:** AC-04/08; eski commit kanıtı ve partial AC.
- **Beklenen dosya alanı:** `packages/verification/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T15 — Teknik kanıt kapısı

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T14,T07c. **Kapsam ID:** EVAL-01,AUD-01.
- **İş:** Sentetik uçtan uca senaryoyu ve restore/replay'i çalıştır; sonuçları kaydet.
- **Kabul:** Import→impact→onay→state→düzeltme zinciri kanıtlı; başarısız kriter gizlenmez.
- **Doğrulama:** AC-01..08/10/14 ve adversarial set.
- **Beklenen dosya alanı:** `docs/quality/poc-results.md` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 kontrol oturumu.

## T16 — Claude Code adapter

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T15. **Kapsam ID:** CAP-02.
- **İş:** T02'de kanıtlanan sürüm/yüzey için adapter; consent, binding, queue ve coverage UI data.
- **Kabul:** Gerçek fixture session otomatik yakalanır; başarısız hook sağlıklı sayılmaz.
- **Doğrulama:** Adapter sözleşme suite; sürüm kayıtlı.
- **Beklenen dosya alanı:** `packages/capture/claude-code/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T17 — Codex adapter

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T16. **Kapsam ID:** CAP-02.
- **İş:** T02 sonuçlarına göre desteklenen yüzeye ayrı adapter; varsayımsal hook adı kullanma.
- **Kabul:** Desteklenen Codex yüzeyi açık; aynı session retry ve eksik capture raporlu.
- **Doğrulama:** Adapter sözleşme suite; CLI/desktop ayrımı.
- **Beklenen dosya alanı:** `packages/capture/codex/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T18 — Minimal MCP ve cross-agent read

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T17. **Kapsam ID:** INT-02,CST-01.
- **İş:** 5 temel tool, proje yetkisi, cursor/limit, bounded brief; write yalnız proposal/evidence.
- **Kabul:** Bir agent kaydını diğeri aynı project/revision ile okur; admin SQL exposed değil.
- **Doğrulama:** AC-01/13; tool schema token ölçümü.
- **Beklenen dosya alanı:** `packages/mcp/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T19 — Proje seçimi ve Review Inbox UI

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T18. **Kapsam ID:** UX-01,APR-01.
- **İş:** Project selector, prepared cards, PendingDecision ve coverage göstergesi.
- **Kabul:** Metin yazmadan happy-path review; keyboard erişimi ve error/empty/loading state.
- **Doğrulama:** AC-07/12/14; gerçek browser flow.
- **Beklenen dosya alanı:** `apps/web/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T20 — Board, Graph ve Timeline

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T19. **Kapsam ID:** UX-01,UX-02.
- **İş:** Aynı projection revision üstünden üç görünüm; active/history ve list fallback.
- **Kabul:** Aynı kaydın durumu tutarlı; graph reason path; historical done korunur.
- **Doğrulama:** AC-09; dar ekran/uzun metin/keyboard.
- **Beklenen dosya alanı:** `apps/web/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T21 — Routing etiketleri ve usage kaydı

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T20. **Kapsam ID:** ROU-01,CST-02.
- **İş:** Class/executor/human-suitable, deterministic bypass, nullable usage ve limit.
- **Kabul:** İnsan basit işi seçebilir; unknown usage 0 değil; limit aşımı deferred.
- **Doğrulama:** AC-13; budget/retry/cached kullanım.
- **Beklenen dosya alanı:** `packages/domain/; apps/web/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T22 — Chat import ve prompt lineage

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T21. **Kapsam ID:** CAP-03,CAP-04.
- **İş:** İzinli metin/export importu, message refs, prompt→execution→artifact ilişkisi.
- **Kabul:** Chat→Code aktarımı izlenir; manuel import otomatik capture diye gösterilmez. Q07/1C izinli geçmiş manifest'i, aktif iş önceliği, kalan coverage ve tarihsel öneri ayrımı T22b ile doğrulanır.
- **Doğrulama:** AC-03/11; tekrar import ve farklı source IDs.
- **Beklenen dosya alanı:** `packages/capture/import/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T23 — Backup, export ve yerel güvenlik

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T22. **Kapsam ID:** AUD-01,GOV-01,GOV-02.
- **İş:** Loopback auth/origin, backup/restore, export, payload retention policy ve redaction kontrolleri.
- **Kabul:** Secret fixture dışa çıkmaz; backup restore digest eşleşir; unauthorized request reddedilir.
- **Doğrulama:** R05/R06/R09/R12/R16 suite.
- **Beklenen dosya alanı:** `apps/hub/; packages/storage/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük PR.

## T24 — MVP kabul ve kullanıcı pilotu

- **Durum / faz:** TODO / P1b. **Bağımlılık:** T23. **Kapsam ID:** EVAL-01.
- **İş:** AC-01..14, iki adapter, gerçek otomatik extractor ile holdout corpus ve management overhead pilotu. Semantik extraction testi zorunludur; fixture/code sonucu yerine geçmez.
- **Kabul:** Tüm zorunlu kapılar geçer veya sınırlı pilot adıyla açık istisna kararı; MVP iddiası kanıta bağlı.
- **Doğrulama:** Ölçüm planı; gerçek tıklama ve source coverage.
- **Beklenen dosya alanı:** `docs/quality/mvp-results.md` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 ölçüm oturumu.

## T25 — Chat yüzeyleri ve cross-provider adapter araştırması

- **Durum / faz:** TODO / P2. **Bağımlılık:** T24. **Kapsam ID:** CAP-03,CAP-04,INT-02.
- **İş:** ChatGPT Chat/Claude Chat izinlerini ayrı test et; aynı sağlayıcı ve cross-provider binding'i genişlet.
- **Kabul:** Her yüzeyde documented/verified/unsupported ayrımı; kaynak taşıma zinciri bozulmaz.
- **Doğrulama:** Permission/plan değişikliği ve revoked access.
- **Beklenen dosya alanı:** `docs/discovery/; packages/capture/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Yüzey başına küçük görev.

## T26 — Gelişmiş reconciliation ve orphan audit

- **Durum / faz:** TODO / P2. **Bağımlılık:** T25. **Kapsam ID:** KNO-02,GRF-02,IMP-02.
- **İş:** Embedding yalnız baseline gerekçelendirirse; unlink/stale/refinement audit ve semantic diff.
- **Kabul:** İyileşme holdout ile ölçülür; unsupported certainty yok.
- **Doğrulama:** Recall/false obsolete regresyonu ve bütçe eşitliği.
- **Beklenen dosya alanı:** `packages/reconciliation/; packages/impact/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Özellik başına küçük görev.

## T27 — GitHub evidence ve görünür panel deneyi

- **Durum / faz:** TODO / P2. **Bağımlılık:** T26. **Kapsam ID:** VER-01,UX-03.
- **İş:** Önce read-only commit/PR kanıtı; ayrıca host izinleriyle panel fizibilitesi.
- **Kabul:** PR varlığı AC geçişi sayılmaz; panel olmayan host'ta açık fallback.
- **Doğrulama:** Commit freshness ve host UI testi.
- **Beklenen dosya alanı:** `packages/verification/; docs/discovery/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** İki ayrı küçük görev.

## T28 — Maliyet raporu ve kontrollü entegrasyonlar

- **Durum / faz:** TODO / P3. **Bağımlılık:** T27. **Kapsam ID:** ROU-02,CST-02,INT-01.
- **İş:** Routing optimizasyonu, fiyat snapshot, yetkili outbox sync; GitHub/Linear/Jira ayrı connector görevleri.
- **Kabul:** Quality eşitliğinde maliyet raporu; retry external duplicate üretmez; scope açık.
- **Doğrulama:** Paired benchmark, webhook/conflict/permission testleri.
- **Beklenen dosya alanı:** `packages/integrations/; apps/web/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Connector başına ayrı PR.

## T29 — Public release hazırlığı

- **Durum / faz:** TODO / P3. **Bağımlılık:** T28. **Kapsam ID:** OSS-01.
- **İş:** Lisans/isim kararı, temiz kurulum, sentetik demo, contributor rehberi ve release checklist.
- **Kabul:** Public için explicit owner onayı; test edilmeyen claim yok; dependency/license inventory tam.
- **Doğrulama:** Temiz makine kurulumu, demo, secrets ve docs kontrolü.
- **Beklenen dosya alanı:** `docs/governance/; release belgeleri` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Küçük release görevleri.

## T30 — Ekip/cloud/open-core keşfi

- **Durum / faz:** TODO / P4. **Bağımlılık:** T29. **Kapsam ID:** TEAM-01.
- **İş:** Talep görüşmeleri, RBAC, conflict/sync, kurumsal audit ve commercial boundary ADR taslakları.
- **Kabul:** Ürün kanıtı olmadan multi-tenant migration başlamaz; kapsam/izin/lisans kararı ayrı.
- **Doğrulama:** Threat model ve tenant isolation planı; pilot talep kanıtı.
- **Beklenen dosya alanı:** `docs/product/; docs/architecture/adr/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Önce keşif.

## Sistem sözleşmesi alt dilimleri

Bu ek, 2026-10-09 mimari incelemesinde bulunan boşlukları mevcut görevlere bağlar. Her alt dilim **TODO**; parent görev ancak bütün ilgili dilimler ve kendi AC'leri geçince kapanır. Sıra parent backlog sırası, sonra a→b→c'dir. “Kanıt” sütunu beklenen çıktıdır, mevcut test sonucu değildir.

| Alt dilim / parent | Küçük uygulanabilir iş | Kabul kriteri / doğrulama | Dosya alanı |
|---|---|---|---|
| T04a / T04 | Versioned envelope/command/query şemaları ve error taxonomy | Unsupported schema ve invalid input state değiştirmez; snapshot/cursor alanları şema testli | domain |
| T04b / T04 | İlk network ingress için loopback/auth/origin ve bounded config | Yetkisiz kaynak/command reddedilir; payload/queue limiti tanımlı; V10/V23 | hub/capture |
| T05a / T05 | Immutable project binding epoch ve quarantine | Binding değişimi yeni event'leri etkiler; geçmiş transfer ayrı correction; V18/V25 | domain/storage |
| T06a / T06 | Source+job atomic receipt ve ingest cursor | Disk/response kaybı senaryoları V19 geçer | capture/storage |
| T06b / T06 | Worker lease/fencing ve job transitions | Expired worker sonuç yazamaz; V20 geçer | capture/storage |
| T06c / T06 | Processing intervals, idle flush, bounded retry/quarantine | Boşluk üstünden watermark atlamaz; V11/V21 ve rotation geçer | capture |
| T07a / T07 | Replay mode ve projector version gate | Bilinmeyen event sessiz atlanmaz; replay aynı digest, sıfır dış yan etki; V14/V27 | storage |
| T07c / T06,T07a | **TODO / P1a:** Minimal çekirdek DB+payload backup/restore | Tutarlı checkpoint, source payload manifest/hash, event sequence ve projection digest; boş hedefe restore, eksik/uyumsuz veri fail closed; replay sıfır dış dispatch; V17/V27. T15a bunu sınar; T23a migration/privacy/export/operasyon kapsamını tamamlar | storage |
| T08a / T08 | Command identity, key/digest ve policy capability | Aynı key güvenli; spoofed human reddi; V03/V23 | domain/hub |
| T10a / T10 | Idea Evaluation için gerekçe ve karşı kanıt alanları | New-is-not-true; kaynak yetersizse uncertainty; ret gerekçesi korunur; V12 | reconciliation |
| T12a / T12 | ImpactRun snapshot, visited/frontier ve knowledge revision | Yeni OR edge eski preview'yu stale yapar; V22 ve limit testi | impact/storage |
| T13a / T13 | Onay token'ı snapshot/policy/digest ile bağla | Partial selection yeni digest; iki onay tek effect; V04/V15/V23 | hub/domain |
| T14a / T14 | Evidence authority ve izinli runner arayüzü | Transcript komutu otomatik çalışmaz; artifact/AC race stale; V24 | verification |
| T15a / T15 | Crash/restore/replay proof dilimi | V19–V24/V27/V28 uygulanabilir çekirdek yollarında raporlu; başarısız test kapıyı bloke eder | quality fixtures |
| T18a / T18 | Scope/snapshot-bound query cursor ve context limits | Başka projeye cursor taşınamaz; truncated sonuç açık; V25 | mcp/storage |
| T20a / T20 | Health ve ready oracle | Pending impact/unknown prerequisite ready olmaz; aynı snapshot UI; V28 | domain/web |
| T23a / T23 | DB+payload tutarlı backup/migration/restore | Hash/sequence/digest kanıtı, uyumsuz schema guard, dış delivery varsayılan durur; V17/V27 | storage |
| T23b / T23 | Payload purge ve türev cache/export retention akışı | Redaction/tombstone izlenir; ilgili index/cache/backup politikası V26 ile kanıtlı | storage/governance |
| T24a / T24 | Yeni güvenilirlik ve UX ölçümleri | V19–V28 MVP yollarında raporlu; false-stale, pending age ve no-text review yükü ölçülmüş | quality |

T07c erken restore teslimidir; T15 ve T15a kapanış için T07c kanıtını zorunlu tutar. P0 fixture backup testi bu production işi kapatmaz; payload bundle/migration/runner/izin kapsamı henüz yok. T23, erken auth/runner sınırlarının ilk kez eklendiği görev değildir; önceki kontrolleri restore/privacy açısından tamamlar. Dış connector'a özgü V27 teslim senaryoları T28'de ayrıca çalıştırılır. Gelecek capability henüz uygulanmıyorsa `not_run + faz` yazılır; mevcut MVP invariant'ı bu gerekçeyle atlanmaz.

## Çok kullanıcılı tasarım ve veri yaşam döngüsü alt işleri

Tek owner + çok-agent kayıt pilotu **T02c → T18d → T24e** olarak [team/data planında](team-data-plan.md) ayrıdır; çok insanlı C01–C06 teslimini beklemek gerekmez. [AGT-01–08](../architecture/agent-and-team-operation.md) kimlik, input/parent eksikliği, concurrency, revoke, usage ve ekip kurulumunu kapsar. Bu plan takip/gözlem içindir; bütün agent'ları yönetebilen çalışan orchestration iddiası yoktur.

[Team/data plan](team-data-plan.md) bu backlog'un parçasıdır: T05b kimlik/tenant, T08b grant/revocation, T06d durable dedup, T07b audit/log, T18b kaynak ACL/retrieval, T23c retention/purge, T23d backup/kapasite, T24b pilot anlaşılabilirliği, T28b dış yetki. Bağımlılık ve kabul kriterleri oradaki tabloda, MU01–MU18 kontrolleri [doğrulama belgesindedir](../quality/collaboration-validation.md).

T30 ekip discovery çıktısı ardından C01–C06 dilimleri merkezi veri, davet/offboarding, review, audit ve ölçek uygulamasını açar. Bu dilimler P4 planıdır; tamamlandı veya P1 MVP'ye eklenmiş sayılmaz.

## Bağlantı, token kontrolü ve graph alt dilimleri

Bunlar mevcut ana görevlerin detaylarıdır; yeni servis veya bağımsız ürün kararı değildir. CON/TOK/GUX senaryoları henüz çalıştırılmadı.

| Alt dilim / bağımlılık | Somut teslim | Kabul |
|---|---|---|
| T02b / T02 | Seçilen host/build MCP+hook+transcript capability raporu; tools-only/remote smoke test | [CON-01/02/07](../architecture/connection-and-context.md); Q02 yanıtı gerçek yüzey seçimini belirler |
| T09b / T06,T09 | No-op/structured duplicate bypass; chunk manifest; evaluation fingerprint | [TOK-01/02/03](../architecture/routing-token-economy.md); recall ölçümü; model hatası no-op olmaz |
| T11b / T07,T11 | Edge revision, ended/invalidated ve sequence geçerliliği | [GUX-03](../product/graph-experience.md); replay, current traversal ve knowledge revision |
| T13b / T11b,T13 | Task cancel ve edge ending için farklı impact preview/compensating olay | GUX-02/05/08; aktif gereksinim veya downstream iş sessiz kapanmaz |
| T18c / T18a,T18b | Kısa brief, since_revision/tombstone, bounded resync ve ayrıntı getir | CON-04/05 ve TOK-02; ACL/coverage bilgisi token kırpmasında kaybolmaz |
| T20b / T11b,T13b,T19 | Graph durum sözlüğü, seçili task bağlamı, history/diff ve liste alternatifi | GUX-01–08; gerçek klavye/tıklama testi; graph gezmede sıfır model çağrısı |
| T21b / T08b,T09b,T21 | Usage sınıfları, dönem/run limitleri, atomik reservation ve unknown settlement | TOK-03–07; eşzamanlı harcama, timeout/retry ve limit-deferred testleri |
| T24c / T18c,T20b,T21b | Eşit corpus/kalite ile maliyet ve graph anlaşılabilirliği pilotu | TOK-08 + GUX; token azalırken recall/false closure korunmalı |

T16/T17 kurulum/kaldırma akışları CON-03/06/08'i içerir. T09b model dispatch'i başlamadan önce minimum budget/data-egress guard bulunmalı; T21b tam dönem/usage arayüzünü tamamlar. Ücretli model yokken sentetik/fake provider testleriyle budget concurrency doğrulanabilir; gerçek provider harcaması için Q03 gerekir.

### Bağlam hikâyesi ve DoD dilimleri

| Alt dilim / bağımlılık | Teslim | Kabul |
|---|---|---|
| T13c / T08,T13 | İş öncesi versioned AC/DoD hazırlama/onay; applicability gerekçesi | [CTX-03](../product/task-context-and-acceptance.md); sonuca göre sessiz kriter düşürme yok |
| T14b / T13c,T14 | AC/DoD→evidence matrisi ve current completion predicate | CTX-04; failed/not_run/stale/unknown farklı, parent bağımsız kontrol edilir |
| T20c / T07,T14b,T20b | Ana task context snapshot, evrim sekmesi, template ve seçilen export yolu | CTX-01/02/05/06; duplicate trigger/ACL/export failure ve reopen |

T20c ilk sürümde deterministik kaynaklı şablondur; modelle anlatı güzelleştirme opsiyonel ve bütçeli kalır. Otomatik Markdown Q06'ya bağlıdır; kullanıcı reposuna otomatik commit/push yetkisi çıkarılmaz.

### İzinli geçmiş ve isteğe bağlı görev bölme

| Alt dilim / bağımlılık | Teslim / durum | Gözlenebilir kabul |
|---|---|---|
| T22b / T06,T09b,T18c,T21b,T22 | **TODO / P1b:** kabul edilen Q07/1C için kaynak manifest'i ve checkpoint; aktif iş önceliği; geçmiş intake öncesi OPEN-08 retention kapısı | [1C sözleşmesi](../architecture/connection-and-context.md): tekrar import, restart, eski kararın geç gelmesi, eksik coverage, bütçe defer ve işlenmemiş arşiv korunumu |
| T13d / Q08,T11b,T13c | **PROPOSED / P1b:** isteğe bağlı split önizlemesi, part_of, AC eşlemesi ve atomik onay | [Split sözleşmesi](../product/task-context-and-acceptance.md): cycle/ACL/stale/retry/yarım işlem; mevcut parent/kanıt korunur |
| T20d / Q08,T13d,T14b,T20b | **PROPOSED / P1b:** parent/child liste+graph, sayım ve iptal/blocked görünümü | Gerekli child iptali başarı sayılmaz; tüm child'lar passed olsa da parent AC/DoD eksikse completed olmaz; değişen payda ve toplam bütçe görünür |

Q08 yanıtı beklerken T13d/T20d tamamlandı veya kesin MVP taahhüdü sayılmaz; mevcut kapsamın önerilen ayrıntısıdır. T22b gerçek veri veya ücretli analiz izni içermez. T24c geçmiş import ilk maliyetini günlük tüketimden ayırıp aynı kalite ölçütleriyle raporlar.

## Yönetim merkezi ve hata takibi alt dilimleri

2026-10-10 takip isteği; tümü **TODO / önerilen P1b ayrıntısı**, çalışan panel değildir. [Yönetim sözleşmesi](../product/administration-and-operations.md) ve ADM-01–10 uygulanacak. Ana 30 görevin kapsamlı alt dilimleridir; yeni motor/servis değildir.

| Dilim / bağımlılık | Küçük teslim | Kabul |
|---|---|---|
| T20f / T07b,T08b,T20a | Owner yerel sağlık/hata görünümü; sıradan kullanıcı için güvenli hata ve referans | ADM-01/05/06; rol negatif API ve temel UI akışı, incident kapanınca task değişmez |
| T21c / T08b,T21b | Parametre sicili; miras/etkin değer, tavan, config önizleme ve revision/audit | ADM-03/04; concurrent config, rollback ve in-flight reservation testi |
| T23e / T20f,T21c,T23c,T23d | Kapsamlı pause/retry, bounded hata kaydı, yedek/recovery görünümü | ADM-07/08/09; disk/audit arızası, archive TTL ve sıfır replay yan etkisi |
| T24g / T20f,T21c,T23e | Owner “neden bekliyor/ne değiştirebilirim?” pilotu ve yerel admin negatif fixture'ları | ADM-01/03–10 uygulanabilir P1 yolları; hosted/L1 kısmı C05/C06'ya açık not_run |

P4 C03/C05/C06 [ekip planında](team-data-plan.md) gerçek çok-kullanıcı yönetimi, platform konsolu, süreli destek ve kotaları tamamlar. ADM-02 ve ADM-10'un hosted kısmı o kapılarda test edilir. T20f ölçülen temel incident görünümüyle sınırlıdır; tam ticketing/on-call entegrasyonu MVP değildir.

## Proje bağlantısı ve izin makbuzu alt dilimleri

**TODO; önerilen sözleşme, runtime kanıtı yok.** [ConnectionAuthorization ve kurulum soruları](../architecture/connection-and-context.md#proje-erişim-sözleşmesi-ve-izin-ekranı) mevcut PRJ-01/CAP/GOV/TEAM kapsamını açar. Q10-A kabul edildi: ayrı listeleme izniyle öneri, seçim/onay sonrasında içerik ve takip. Kaynak allowlist'i ve iki taraflı yetki kontrolü gereklidir; T16b capability ayrımını, T20g öneri/manuel seçim UX'ini, T24h genişletilmiş ACC-02'yi doğrular. Gerçek keşif izni verilmiş veya özellik uygulanmış sayılmaz.

| Dilim / bağımlılık | Somut teslim | Kabul |
|---|---|---|
| T05c / T05b | P1a kaynak/hedef binding ve versioned izin makbuzu şeması; grantor/active gate kural fixture'ı | ACC-01/03/07'nin veri/kural örnekleri; gerçek activation yetki/audit entegrasyonu T08b/T07b sonrasında |
| T16b / T02b,T05c,T08b,T07b,T16 | P1b adapter kaynak allowlist/path sınırı; requested/granted/effective scope; activation/disconnect kontrolü | ACC-01–07 uçtan uca; T17 diğer coding yüzeyinde aynı sözleşmeyi doğrular |
| T20g / T05c,T16b,T20f | P1b proje bağlantı envanteri, kurulum soruları ve izin farkı önizlemesi | ACC-07/08; owner “hangi kaynak, kim izin verdi, ne yapabilir?” yanıtını ekrandan bulur |
| T24h / T16b,T17,T20g | Yerel/sentetik erişim oracle ve UX pilotu | ACC-01–08 uygulanabilir yollar; provider revocation/metadata desteği ayrı raporlu |

P4 C03/C05 aynı sözleşmeyi farklı kaynak sahibi ve ekip yöneticisiyle doğrular. Gerçek provider grant, hesap bağlantısı veya veri aktarımı ilgili somut izinler olmadan yapılmaz. T05c çekirdek sözleşmesi yeni veri ingestion'ından önce, UI görünümü P1b'de gelir.

## Tetikleme, zamanlama ve veri ilişkileri dilimleri

**TODO / önerilen ayrıntılar.** [API/sequence ve TRG sicili](../architecture/execution-and-integrations.md), [DB ilişkileri](../architecture/data-relationships.md) mevcut modülleri tamamlar; fiziksel şema T03 kapısından sonra. Aralıklar deney adayı, fake clock/provider sonuçları gerçek entegrasyon sonucu değildir.

| Dilim / bağımlılık | Küçük teslim | Kabul ve faz |
|---|---|---|
| T04c / T04a | Source, command, trigger ve async result şemaları; ER composite key/N:M ilişki kontratı | P1a: DBR-01/02/03 fixture tanımı; HTTP/MCP mapping seçilen transport'ta açık |
| T06e / T04c,T06a,T06b,T06c | Kalıcı due jobs, kaçan wake-up taraması, max-wait/fairness ve replay suppression | P1a: SEQ-03/04/08, DBR-04; domain commit entegrasyonu T07/T08'de, erken scheduler ücretli çağrı açmaz |
| T09c / T06e,T09b | TRG-02 deterministik bypass, profil ve izin/rezervasyon kapısından koşullu semantik dispatch | P1a/P1b profil tamamlaması: SEQ-02/03/05/06; no-op/duplicate/manual mod çağrı sayacı; minimum bütçe guard önce |
| T14c / T14a,T14b,T08b | Run sonucu→evidence→AC/DoD assessment→completion command akışı | P1a: SEQ-01/06, DBR-02/03; parent ve stale kanıt; runner yoksa not_run |
| T18f / T18c,T06e | Query/result/notification cursor ve reconnect contract fixture | P1b: SEQ-02/08; UI fallback policy, stale görünümü; host otomatik tool çağırır varsayımı yok |
| T24i / T09c,T14c,T18f,T21b,T23a | Fake-clock/crash/replay/ilişki corpus'u ve izinli gerçek yüzey raporu | P1b: SEQ-01–06/08 + DBR-01–06; P3 dış teslim SEQ-07 açık not_run |
| T28c / T28b | Outbox→API→callback/poll korelasyonu, unknown reconciliation ve endpoint sözleşmesi | P3: SEQ-05/07, DBR-04; provider bazında idempotency/Retry-After/permission kanıtı |

T04c fiziksel DB'yi erken seçmez; T05–T08 seçilmiş stack'te FK/unique/transaction kısıtlarını uygular. Güncel AC/DoD ve zorunlu review'lar task sonucunda policy katmanında denetlenir; event veya model cevabı doğrudan executor başlatmaz. T23/C02 migration ve restore DBR-05/06'yı kendi fazlarında tekrar doğrular.

## Ranking feasibility ve Faz 2 dilimi — 2026-10-10

Mevcut T11c/T20e/T24d MVP dilimleri [ranking sözleşmesi](../product/priority-and-flow.md) ile ayrıntılandırıldı; TODO durumları ve ana T01–T30 bağımlılıkları korunur. T01 planlanan FLOW-09–17 fixture taslağını içerir; bu kayıt fixture veya runtime testinin üretildiği anlamına gelmez. T20e apply entegrasyonu için T08b grant ve T07b audit hazır olmalıdır; parent T20/T24 sırası bu kapıları atlamaz.

| Alt görev / bağımlılık | Statü ve teslim | Kabul / feasibility kanıtı |
|---|---|---|
| T26b / T24d,T26,T18c,T21b | **PROPOSED / P2 adayı:** context-aware, açıklanabilir çok faktörlü scoring, critical-path veri yeterliliği, what-if ve gelişmiş ranking UX deneyi | FLOW-16–17 + FLOW-01–15 regresyonu; factor contribution/unknown, veri kalitesi, deterministik baseline kıyası, süre/maliyet/UX ölçümü, go/no-go ve fallback |

P2 yerleşimi takvim veya uygulama taahhüdü değildir. Faz yalnız feasibility sonucuyla kesinleşir: veri/izin/context erişimi, kalite, ölçülen efor/maliyet ve 40+ görevde anlaşılabilirlik. Eksik süre/takvimle kesin gecikme hesabı yapılmaz. Scope/value kararını PO verir; scoring veya simülasyon canonical planı değiştirmez. Rollout shadow öneri → yetkili MVP board → feasibility sonrası P2; hata halinde manuel canonical sıraya dönüş. Feature kodu bu dokümantasyon görevinin kapsamı dışındadır.

## İşlem limitleri ve kötüye kullanım dilimleri

**TODO / teknik öneri; uygulanmadı.** [Limit sözleşmesi](../architecture/resource-limits-and-abuse.md) mevcut kaynak/izin/maliyet kontrollerini tamamlar. Temel koruma T24 pilotuna ertelenmez; her dilim kendi negatif testleriyle teslim edilir.

| Dilim / bağımlılık | Küçük teslim | Kabul ve faz |
|---|---|---|
| T04d / T04b,T04c | Sonlu request/body/burst/concurrency config, erken admission, güvenli hata/transport eşlemesi | P1a ilk ingress: LIM-01/03/04 temel fixture; input limitleri pahalı parse/LLM'den önce, ret domain mutasyonu yapmaz |
| T06f / T04d,T06d,T06e,T05b | Bounded queue/storage admission, scope adaleti, restart sayaç ve receipt/backpressure | P1a: LIM-05/08/09 yerel kısmı; receipt sonrası iş kaybolmaz, replay yan etkisiz |
| T08c / T06f,T08b,T07b | Principal/proje/workspace toplamı, parent-run bütçesi, DB transaction sınırı ve limiter arıza davranışı | P1a: LIM-02/06/07/08 sentetik; ilk model dispatch'i bu minimum rezervasyon guard'ına bağlı, T21b raporlama/settlement'i tamamlar |
| T24j / T08c,T21b,T21c,T23e | Etkin limit/ret/rezervasyon admin görünümü ve tekrar üretilebilir limit-aşımı pilot raporu | P1b: LIM-01–10 uygulanabilir yerel yollar; eşikler, ortam, yanlış throttle ve sıfır izinsiz LLM kanıtı; P4 parçaları not_run |

T08c/T09b ilk model dispatch'inde provider/account ortak çıkış sınırını ve 429/retry davranışını da uygular. T28c bunu P3 dış yazma connector'larına taşır; C06 dağıtık atomik sayaç, tenant yük izolasyonu ve hosted ağ sınırını P4'te doğrular. T04/T06 temel ilkeleri, T08c tam kimlik/maliyet entegrasyonunu sağlar; deployment bu kapıları atlayamaz. Sayısal eşikler OPEN-12/16 ile seçilecek; ücretli veya dış sisteme yük testi yetkisi verilmiş değildir.

## Yüksek token riski ve ek onay dilimleri — 2026-10-11

**TODO / önerilen teknik sözleşme.** Kullanıcının ek onay ihtiyacı [risk belgesinde](../product/token-risk-and-approval.md) kayıtlıdır; gerçek ücret/provider yetkisi değildir.

| Dilim / bağımlılık | Teslim | Kabul ve faz |
|---|---|---|
| T09d / T09b,T08c | Deterministik assessment, toplam plan tahmini, reason codes ve dispatch risk kapısı | P1a: TRA-01–07/09 çekirdek fixture; missing policy/unknown cap otomatik dispatch açmaz; ilk gerçek model çağrısından önce |
| T19b / T09d,T19,T08b,T07b | Yetkili insan risk kartı, sınırlı plan approval ve audit; ertele/reddet/küçült | P1b: TRA-05/06/08/10; stale/revoked/duplicate; UI hazır değilken yüksek riskli iş bekler |
| T24k / T19b,T21b,T21c | Risk corpus'u, yanlış uyarı/tahmin sapması ve onay yükü pilot raporu | P1b: TRA-01–10; gerçek provider yalnız ayrı izinle, aksi halde sentetik/not_run |

T09b'nin minimum bütçe guard'ı korunur; T09d bunun risk değerlendirmesini tamamlar. T21c sayısal risk policy'sini, T21b usage/unknown muhasebesini sağlar. Normal, önceden yetkili düşük riskli işler her seferinde onay istemez. Eşikler ölçüm kapısında, kod henüz yok.

## Çoklu chat bağlamı ve işleme gecikmesi — 2026-10-11

[Çoklu chat/lag](../architecture/multi-chat-and-processing-lag.md) mevcut CAP/PRJ/KNO/CST kapsamını açar; yeni engine veya sınırsız otomasyon değildir. T01 corpus'a bir projenin birden çok chat'te ilerlemesi eklenir; T02 adapter raporu session kimliği, mesaj revision'ı ve replay/gap kabiliyetini belirtir.

| Dilim / bağımlılık | Teslim | Kabul ve faz |
|---|---|---|---|
| T05d / T05c,T08b | Session/span binding, konu segmenti ve kaynak→aday→record ilişki sözleşmesi | P1a: CHAT-01/04/05; seçilmemiş session, karışık proje, yanlış binding düzeltmesi ve ACL |
| T10b / T10,T05d | Chat'ler arası duplicate/refinement/conflict ve geç kaynak reconciliation corpus'u | P1a: CHAT-02/03/04; kaynaklar korunur, benzerlik tek başına merge/approval değildir |
| T06g / T06f | Session frontier, max-wait flush, bounded catch-up ve gap/lag ölçümü | P1a: LAG-01–05 sentetik/crash; queue dolunca sahte receipt ve sessiz source drop yok |
| T18g / T18c,T10b,T20g,T06g | Bounded proje context/delta ve chat→task kaynak görünümü; stale/coverage UX | P1b: CHAT-05/06, LAG-06; host desteklenmiyorsa sync/stop iddiası yok |
| T24l / T18g,T06g,T24k | Çoklu chat + burst/uzun yük + geciken provider/onay corpus raporu | P1b: CHAT-01–06/LAG-01–06; hız ile kalite, ACL, coverage ve token birlikte; eşik/ortam kayıtlı |

Adapter gerçek erişim testi T02/T16/T17'de; sentetik yük sonucu provider kapasitesi garantisi değildir. Kapasite hedefi OPEN-12/16'da pilot öncesi seçilir. UI tamamlanana kadar trace/cursor çıktısıyla çekirdek kontroller doğrulanır; yüksek riskli catch-up izinsiz model çağrısı açmaz.

## Devam paketi ve hafıza yeterliliği — 2026-10-11

**PROPOSED / not_started.** [Spike-1 v1](spike-1-v1.md) altı ardışık deney adımını ve [ürün sözleşmesi](../product/resume-package-and-memory.md) RES-01–08 kabulünü tanımlar. Yapıştırılan metindeki Spike-0 iddiaları doğrulanmadı; çalışan prototip bağımlılığı kabul edilmez. T01/T02/T03 kapıları ve sıradaki T01 korunur.

| Dilim / bağımlılık | Teslim | Kabul / faz |
|---|---|---|
| T20h / T20e,T14b,T06g | Bekleyen işler için kaynaklı yaş/kanıt/coverage görünümü ve ertele/incele | P1b adayı: RES-01/05; yaş tek başına unutuldu/obsolete/priority değildir |
| T18h / T18g,T14b,T08b,T09d | Revision/ACL bağlı deterministic resume şablonu, bounded önizle/kopyala; Q11 tercihi doğrultusunda | P1b adayı: RES-02–07; copy model/runner başlatmaz, kritik eksik context görünür; yeni özet metered gate'e tabidir |
| T24m / T20h,T18h,T24l | Fresh-session oracle, prompt/paket/full-source koşulları ve izinli deney raporu | RES-08 + RES-01–07 regresyonları; model/gerçek veri izni yoksa yalnız hazır sentetik protokol + not_run |

S1-01–06 deney adları ana 30 göreve yeni task sayısı eklemez. Ayrı sentetik prototype stack kapısından sonra incelenebilir; üretim entegrasyonu yukarıdaki bağımlılıklara bağlıdır. Q11-A kopyala önerisi, B başlatma capability araştırması açık; hiçbir düğme execution, egress, ücret veya scope iznini sessiz genişletmez.

## Konuşmadan gerçekleşen işe geri bildirim — 2026-10-11

**Önerilen alt dilimler / TODO.** [Ürün sözleşmesi](../product/intent-to-reality-gap.md) mevcut F07/F08/F09/F10'u somutlaştırır. T01 corpus GAP-01–10 için kaynak/oracle içerir; T03'te [Claude Projects karşılaştırması](../discovery/claude-projects-overlap.md) build/extend kararına girdi olur. T01 sıradaki görevdir.

| Dilim / bağımlılık | Teslim | Kabul / faz |
|---|---|---|
| T14d / T14b,T05c,T08b | Artifact expected-effect ve exact hedefe bağlı read-back assessment; human reported ayrı | P1a: GAP-01/03/04/05/07/10; gözlem AC/deploy yerine geçmez; yetkisiz okuma/yazma yok |
| T18i / T18h,T14d,T10b | Güncel context'te kabul/uygulama/unknown ve alternatiflerin kaynağı | P1b: GAP-02/05/06/09; host desteklenmiyorsa teslim/kullanım garantisi yok |
| T20i / T20h,T14d,T13 | Karar ve teslim durumu ayrı görünüm; ön koşul olduğunda odaklı durum sorusu | P1b: GAP-03/08/10; tekrarlı nag/model çağrısı yok; independent işler açık |
| T24n / T18i,T20i,T24m | Aynı sentetik görevden fresh-session + dış hedef belirsizliği karşılaştırması | GAP-01–10; yanlış kabul/uygulama ataması, süre, soru, token/API istekleri; izin yoksa not_run |

İlk local veya GitHub adapter'ı T02/T03 capability seçimine bağlıdır; gelecekteki GitHub evidence T27 kapsamı kaybolmaz. Bu plan yeni hesap bağlantısı veya otomatik upload yetkisi değildir.

## Güncel P0 yatırım kapısı — tasarım revizyonu 03

T01 ilk hazır iş olarak korunur; GAP/RES sentetik oracle örnekleri geniş corpus'un yerine geçmez. Prototip kodlaması bu dokümantasyon turunda başlamadı. [Deney planı](spike-1-v1.md) aynı dosyada günceldir; yeni v2/v3 kopyası yok.

| Dilim / bağımlılık | Teslim / durum | Kabul |
|---|---|---|
| T02d / T01 | IN_PROGRESS (manuel target + synthetic measurement; gerçek host kısmi): selected kaynak, trustworthy human selection ve tek local/repo target capability | [READBACK-01](../quality/first-target-readback.md) tek GitHub dokümanında manuel happy-path eşleşmesi; otomatik capability, missing/permission/partial/stale ve kaynak coverage henüz not_run. Capture/target izinleri ayrı; ücret/erişim ayrıca |
| T03a / T01,T02d | IN_PROGRESS: kullanıcı yetkili P0 fixture yöntemi, Python stdlib/SQLite, paid dispatch yok; production stack/lisans açık | Native baseline koşulları, GAP/RES oracle, input/target izni, sınırlar ve cleanup; production ADR accepted değil |
| T03b / T03a | IN_PROGRESS: yetkilendirilmiş typed zincir + lexical baseline çalıştı; semantik/native deneyi açık | GAP-01–10 + uygulanabilir RES; API/UI/LLM sonuçları ayrı, not_run gizlenmez; gerçek host/capture test edilmeden otomatik vaat yok |
| T03c / T03b,T02 | TODO: sonuç, yönetim/kurulum/bakım maliyeti ve yatırım seçenekleri | Owner native/extend/build/ek deney/durdur kararı; build'de production stack ADR ve T04 kapısı, native/extend'de uygun teslim planı |

T02'nin iki coding yüzeyi kapsamı korunur; prototip tek hedefle sınırlı olabilir. T14d/T18i/T20i/T24n üretim entegrasyonunun bağımlılıklarıdır; P0 prototip bütün bu görevlerin tamamlandığını iddia etmez. T03b çalıştırma onayı/veri veya bütçe izni bu tabloyla oluşmaz.

## Sözlük/pattern takip isteği — 2026-10-11

Aşağıdaki dilimler ENG-02'nin mevcut kapsamını açar; yeni ana görev/engine oluşturmaz. Tasarım [lexical-prefilter](../architecture/lexical-prefilter.md) içindedir. Sözlük yapma önerisi kabul edilmiş parser/DB/otomatik işlem kararı değildir.

| Alt dilim / bağımlılık | Teslim / durum | Kabul ve doğrulama |
|---|---|---|
| T01e / T01 | TODO / P0: TR/EN claim/request/negation/quote/future/implicit karar etiketleri ve holdout; izin varsa ayrıca redakte gerçek çıktı örneklemi | LEX-01–04/07; örnekler source span/actor taşır, gerçek veri yoksa sıklık/tasarruf unknown; mevcut corpus şartı korunur |
| T09e / T01e,T09b,T09c | PROPOSED / P1a: sürümlü rule config, guard'lar ve structured-first candidate yolu; shadow mode, bounded matcher ve provenance dedup | LEX-01–06/08; unmatched içerik kaybolmaz, hiçbir keyword doğrudan command/onay üretmez; negatif örneklerle runtime test gerekir |
| T24o / T09e,T24 | TODO / P1b: uygun batch baseline / lexical+fallback / structured-first hibrit kıyası | LEX-07/08; aynı holdout/kalite/coverage; bütün token/çağrı/false-done/review ve bakım yükü; ücretli model için Q03 ayrıca |

20 sentetik örnek analizi bir parser testi veya gerçek LLM çıktı araştırması değildir. T01 sonraki iş olarak kalır; ön eleme kaliteyi düşürüyorsa bypass kapatılır veya yalnız yardımcı aday etiketi olarak tutulur.

## Konuşma dili ve yerelleştirme — 2026-10-11

Kullanıcı language-aware not/proje içeriği istedi; maliyetli otomasyon P2'ye bırakılabilir. [Dil tasarımı](../product/language-and-localization.md) teknik öneridir. Ana 30 görev ve fazları korunur; yeni ana görev/engine yok. P1 yalnız temel yapı/açık pilot dili, P2 otomatik çok dilli davranış; Q12-A kabul edildi: proje çıktı dili sabit, farklı sohbet dilinde yalnız değişim önerisi; onaysız geçiş ve eski notların otomatik çevirisi yok.

| Alt dilim / bağımlılık | Teslim / durum | Kabul / faz |
|---|---|---|
| T05e / T05,T04c | PROPOSED / P1a: source/record dil metadata'sı ve sürümlü output policy; Unicode/source/ref korunumu | LANG-01/04/07; şema provenance alanları, ayrı UI locale; fiziksel stack seçimi ayrıca |
| T24p / T05e,T24 | TODO / P1b: açık pilot dili ve source/ref korunumu fixture'ı | LANG-01/04/05/07/08 uygulanabilir temel yollar; otomatik çok dil/mixed kalite P2 not_run, 14 MVP AC korunur |
| T25a / T24p,T25,T05e | PROPOSED / P2: hafif detector, mixed/short fallback, insan dili odaklı öneri ve kabul edilmiş Q12-A policy | LANG-01–03/08; Q12-A dil önerisi/ret/yanıtsız/onay ve revision yolları; seçilen diller/model/host için destek matrisi |
| T26c / T25a,T26,T20,T18c,T21b | PROPOSED / P2: etkin dilde çıkarım/brief, locale katalogları, cross-language reconciliation/retrieval; kontrollü türev çeviri | LANG-01–08; holdout/quality-cost-recall ve kullanıcı review; bütün geçmişi yeniden çevirmeme, egress/usage/ACL kapıları |

T01 corpus'a TR/EN, kısa/mixed, alıntı/kod ve dil değişimi örnekleri eklenir; gerçek dil/model başarısı bugün not_run. Yeni language policy veya locale seçmek veri/model/shell/dış yazma izni vermez. Ekipte kullanıcı UI locale'i ortak canonical dili kendiliğinden değiştirmez. P2 kabulü olmayan otomatik çok dilli davranış P1 parent task kapanışının tamamlanmış özelliği sayılmaz.

## WrongStack reuse araştırması — T03 alt dilimi

**T03d — PROPOSED / P0. Bağımlılık: T01,T03a; çalıştırılan kapsamın erişim/model/bütçe yetkisi.** [Sabit ref araştırması](../discovery/wrongstack-review.md) belge çıktısıdır; bu runtime alt dilimi tamamlanmadı. T03b native/extension ve T03c yatırım kararı sırası korunur.

- **İş:** WS-R1 native fizibilite; WS-R2 küçük evidence/coverage/validity validator; WS-R3 governance/graph contract; WS-R4 bounded context/pattern deneyi; WS-R5 reuse/native/extension/build önerisi. [R01–24 kod/teknoloji raporundaki](../discovery/code-reuse-assessment.md) küçük modülleri governance paket/port ve native/extension seçenekleriyle karşılaştır; scope/notice/bağımlılık/semantik uyum görünür. Stack kararı olmadan kullanılmayan source klasörü açma.
- **Kabul:** Pinned ref/path/notice/dependency/semantik fark/target modül kaydı; WS-01–08, GAP/RES/H1 aynı oracle'da native/config/custom/unknown ve pass/fail/not_run. Fake refs, inaccessible target, OR gerekçe, oversized context ve child bütçe istisnaları görünür. Kaynak/test tanımı okundu diye V/pass yazılmaz.
- **Doğrulama:** Yetkili izole sentetik deney; uygulanacak modül için kendi sözleşme testleri; bütün round-trip/fallback/review maliyeti. T03c owner kararı olmadan production stack değişmez. 30 ana görev ve MVP kapsamı korunur.

## Kalıcı sorular ve geç cevap eşlemesi — 2026-10-11

Kullanıcının Q12'ye geç verdiği yanıt [somut sözleşmede](../product/pending-questions-and-late-answers.md) kaydedildi. Önceki belgelerde geçen T13e/T18e/T24f için bu backlog'da ayrı teslim satırları bulunmadığı görüldü; mevcut referanslar aşağıda tamamlandı. Yeni ana görev/engine veya geniş orchestration yetkisi değildir.

| Alt dilim / bağımlılık | Teslim / durum | Kabul |
|---|---|---|
| T13e / T13,T07,T08,T05 | TODO / P1a: kalıcı QuestionRequest/PendingDecision bağı, option/presentation snapshot, AnswerRecord ve atomic/revision-bound çözüm | ASK-01–06/08 + LATE-01–07 uygulanabilir core; silence/timeout approval değil; ID/ref ve authority ayrı; candidate/unmatched cevap korunur |
| T18e / T13e,T18,T06 | TODO / P1b: host soru/cevap metadata coverage, exact reply/selection normalizasyonu ve delivery capability | ASK-07 + LATE-02/06/07/08; read/propose/execution farklı; metadata yoksa açık manual fallback; teslim/resume unsupported ise iddia yok |
| T24f / T13e,T18e,T19,T20i,T24 | TODO / P1b: sentetik delayed-answer oracle ve ilgili pending Inbox/brief akışı doğrulaması | ASK-01–08 + LATE-01–08; iki A/B sorusu, changed options, cancel/conflict/retry/restart/gap; yanlış human approval engelleyici regresyon |

T01 corpus Q12 benzeri sentetik vakalar içerir; özel transcript import edilmez. T19/T20i UI, T18g/T18h bounded context açık soruları ve yanıt eşleme durumunu gösterir. P2 bütçeli semantic association kalitesi T25/T26'nın aday refinement'ıdır; tüm platformlarda P1 otomatik eşleme garantisi yok. Ana görev statü/bağımlılıkları değişmedi; bu dilimler ve bütün kontroller not_run.

## Ekosistem bileşen araştırması — T03 alt dilimi

**T03e — TODO / P0 (ilk masa başı tarama belgesi mevcut; derin inceleme ve deney tamamlanmadı).** Kullanıcı WrongStack dışındaki adayların araştırılmasını istedi. Salt okunur keşif için runtime önkoşulu yok; deney için T01,T02,T03a ve gereken erişim/model/bütçe yetkisi. [Araştırma kartı](../discovery/ecosystem-research.md), [10 pinned aday](../discovery/ecosystem-candidates.json).

- **İş:** ER-R1 bounded keşif DOC_COMPLETE; ER-R2 Graphiti/LangGraph/LiteLLM export/dependency/contract closure TODO; ER-R3 native/config/extension/port/own deney önerisi TODO; ER-R4 kanıtlı adoption önerisi TODO. Ekip modeline ihtiyaç varsa OpenFGA/Cedar; distributed gerekçesi varsa Temporal. Her aday zorunlu runtime dependency değildir.
- **Kabul:** gerçek lisans/exception, immutable source path, source→mevcut task/contract, uyarlama maliyeti ve bilinmeyenler. ER-T1–5 not_run; ölçülmeyen metrik null; managed/OSS ve component/product ayrımı. En iyi native baseline korunur. Üç odaklı closure'dan sonra karar için yeterli kanıt varsa tarama durur.
- **Korunan kapı:** yeni mimari/stack/kod alımı owner adoption kararı gerektirir; Q13 ve T03d kapanmadı. 30 ana görev korunur; T01 IN_PROGRESS, diğer 29 TODO; bu alt dilim MVP'den önce on framework kurma talimatı değildir.

## Karar→etki→gerçekleşme ölçüm alt dilimleri

[Teknik protokol](../quality/evaluation-protocol.md) mevcut EVAL-01 ve H1/H3/H4/H6 sözleşmelerinin nasıl sınanacağını açıklar; yeni ürün engine/scope/stack yok. [CHAIN-01 veri taslağı](../../examples/decision-impact-evaluation-case.json) not_run, T01 corpus ve holdout tamamlandı sayılmaz.

| Alt dilim / bağımlılık | Teslim / durum | Gözlenebilir kabul |
|---|---|---|
| T01f / T01 | IN_PROGRESS / P0 (draft oracle + bağımsız source-span scorer; insan/critical domain kapsamı açık): frozen checkpoint/identity/source-span oracle, bağımsız rubric ve error taxonomy | 6 session/30 meaningful kayıt şartı korunur; positive/negative authority/AND/OR/unknown/verified coverage; scenario-family holdout, reviewer ve hash kaydı |
| T03f / T01f,T02,T03a | IN_PROGRESS / P0 (P0 harness/scorer kısmi; gerçek adapter/telemetry açık): sınırlı deney harness/adapter ve scorer contract'ı; T03a içinde tasarım, T03b içinde yetkili uygulama | One-to-one matching, critical evaluation_error→incomplete, mock/real observer, run manifest, failure/unknown/coverage/payda raporu; framework/production ADR seçilmiş sayılmaz |
| T24q / T03f,T24 | TODO / P1b: domain/extraction/target/fresh-session/UI zinciri kabul raporu; T03b'de yalnız erken örneklem | Aynı revision/case ile native/config/extension/own, critical wrong approval/verified/closure 0 hedefi, kalite+maliyet+review süresi; not_run/permission/gap sonuçtan çıkarılmaz |

Deep dive ölçümün açık contract sorularıyla sınırlıdır; T03e araştırması T01/harness işini ertelemek için sınırsız repo incelemesine dönüşmez. Q03 model/veri/bütçe ve Q13 kod alımı açık; gerçek provider veya ücretli model bu dokümanla yetkilendirilmez. 30 ana görev korunur; T01 IN_PROGRESS, diğer 29 TODO.

## Teknik boşluk kapanışları — 2026-10-11

[Ayrıntılı TG incelemesi](../quality/technical-gap-analysis.md) ve [IC önerileri](../architecture/implementation-contracts.md) aşağıdaki mevcut görevlerin kabul kanıtını ayrıntılandırır. Yeni 24 task veya bütün P0'ın önüne 8 engine eklenmez; first-use gate geçerlidir. Ana görev durumları değişmedi. **Düzeltme:** dil T24p/T25a bağı korunur; ölçüm alt görevi T24q'dur.

| Mevcut görev alanı | İlave kapanış yüzeyi | Durum |
|---|---|---|
| T04a/T04c, T09/T10 | IC-01; executable schema/error/Unicode span, bounded strict decoder ve partial source coverage | Öneri; implementasyon/test not_run |
| T08a/T13 | IC-02; server canonical digest, golden vectors, unknown/null/operation ordering ve scope/revision | Öneri; implementasyon/test not_run |
| T21/T21c | IC-03; exact money, price/period revision, rollover/unknown/duplicate settlement/child budget | Öneri; Q03 ve sonlu config kapısı korunur |
| T02d/T14b/T14d | IC-04; immutable target ref, concurrent local read/partial/permission/missing ayrımı | Öneri; gerçek capability/read izni gerekir |
| T11/T12/T13/T14 | IC-05; empty AC, typed cycle mapping, projection freshness/OR edge race | Öneri; accepted enum/policy değil |
| T04b/T05/T08b/T16/T17/T18 | IC-06; browser/agent auth, transport ve revoke-after-context sınırı | Öneri; ilk external ingress öncesi ilgili kontrol |
| T06/T07/T15/T23 | IC-07; receipt/commit/lease/budget/audit fault injection ve privacy/key/restore/load | Mevcut implementation borcu; policy kararı açık |
| T01f/T03f/T24q | IC-08; frozen oracle ve katman/gerçek-target/native fair baseline | TODO; örnek/veri lint'i runtime ölçüm değildir |

TG-01/02 belge düzeltmeleri runtime görevlerini complete yapmaz. TG-12–23 capability/owner/implementation/measurement kapanışı ilgili canonical task ve scoped evidence ile yapılır.


## Audit sonrası P0 kanıtı ve restore bağımlılığı

[2026-10-11 düzeltme kaydı](../quality/audit-remediation.md), source/code hash’li [sonuç](../quality/audit-remediation-results.json), [insan review kuyruğu](../quality/human-review-queue.md) ve [ortak kıyas planı](../quality/pilot-comparison-plan.md). T01/T02/T03 kısmi bağımsız deneyleri IN_PROGRESS; mevcut ön koşullar ana kapı **kapanışı** içindir. İnsan gold tamamlanmadan fixture kodu hazırlanabilir; gold/native/model kalitesi varmış gibi ana görev kapatılamaz. T07c minimal production restore, T15 proof, T23 operasyon/migration/purge; fixture SQLite backup bu işlerin completion’ı değildir.


## İnsan kararından bağımsız P0 bağlantı teslimi — 2026-10-11

T03f/T03b kısmi kod teslimi: [source-only request, output validator, candidate bridge, evaluator ve checkpoint kodu](../../spikes/semantic-chain/README.md) uygulandı. T01f gold/human ve T03c production yatırım kapıları kapanmadı. [Hazırlık/blocker matrisi](implementation-readiness.md) teknik işi gerçek erişim/model/maliyet ve insan kalite incelemesinden ayırır. Bu işler için bütün gold veya future fazların tamamlanması beklenmez. 28 yeni test ve [sonuç](../quality/semantic-readiness-results.json); sonraki gerçek model dispatch/not_run/usage sınırı açık. AI-authored S02 candidate draft contract/import proof’udur; model kalite benchmark’ı değildir.

T03f/T03b ek P0 dilimi: [token/context preflight](../quality/token-preflight.md) ve 17 fixture testi uygulandı. Mevcut S02 hashleri değişmedi; unknown cap/bütçe blocked sonucunu veriyor, gerçek inference yok. T09d/T21b/T21c için çağrı öncesi hesaplama örüntüsü sınandı; gerçek adapter, trusted policy, atomik reservation, para ve dispatch enforcement işleri TODO kalır. Rapor [ayrı sonuç kaydı](../quality/token-preflight-results.json) taşır.

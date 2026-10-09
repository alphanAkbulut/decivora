# Ardışık uygulanabilir backlog

Q09/DEC-17 uyarınca engeli kaldıran uygulanabilir adım önce değerlendirilir. T01–T30 başlangıç teslim sırasıdır; bütün ön koşullar doğrulanmış teknik blocker gibi graph'a otomatik alınmaz. Refinement gerçek teknik/izin gate'i ile plan sırasını ayırır; kalite kapıları korunur. [Öncelik ve akış](../product/priority-and-flow.md) GRF-01/APR-02/UX-02/ROU-01 kapsamını detaylandırır.

| Yeni alt dilim / bağımlılık | Teslim / durum | Kabul |
|---|---|---|
| T11c / T11 | TODO / P1a: başlangıç-bitiş gate'i, blocker assessment, revision bağlı traversal, benzersiz downstream | FLOW-01–04; eksik graph/ACL/unknown yanlış ready veya tamlık üretmez |
| T20e / T11c,T13,T20 | TODO / P1b: açıklamalı öncelik, inbox/board/graph ve sıra değişimi review'u | FLOW-05–08; stale/override, tekrar bildirim, yetki ve bağımsız iş |
| T24d / T20e,T24 | TODO / P1b: sentetik oracle ve owner pilotu | FLOW-01–08; zorunlu sette yanlış ready 0; bekleme/uyarı yükü baseline |

T01 corpus FLOW örneklerini de içerir. Bildirim kanalı/sıklığı açıkken yalnız uygulama içi sıra hazırlanır. Alt dilimler planlıdır, uygulanmadı.

Bütün görevler **TODO**. Bu plan uygulamayı gerçekleştirmiş değildir. Her görevi küçük bir PR/çalışma dilimi olarak ele al; büyük keşif satırlarını belirtilen yüzey/connector bazında ayrı alt görevlere böl. Tahminler takvim taahhüdü değil iş parçalama boyutudur. Görev kapanışı: değişiklik + AC kanıtı + ilgili kontrol + status güncellemesi. [Roadmap](../../ROADMAP.md) fazları, [MVP](../product/mvp.md) AC'leri tanımlar.

[Engine haritası](../architecture/engines.md), [runtime sözleşmeleri](../architecture/runtime-contracts.md) ve bu belgenin sonundaki **sistem sözleşmesi alt dilimleri** ilgili görevlerin kapsamına dahildir. “1 küçük PR” üst sınır taahhüdü değildir; bu alt dilimleri sırayla tamamla. 30 ana görev korunmuştur; güvenlik/veri bütünlüğü ayrıntıları son faza ertelenmez.

| ID | Faz | Ön koşul | Görev |
|---|---|---|---|
| T01 | P0 | — | Golden corpus ve karşılaştırma protokolü |
| T02 | P0 | T01 | İki coding yüzeyinde capability spike |
| T03 | P0 | T01,T02 | Build/extend ve teknoloji kararı |
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
| T15 | P1a | T14 | Teknik kanıt kapısı |
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

- **Durum / faz:** TODO / P0. **Bağımlılık:** —. **Kapsam ID:** EVAL-01.
- **İş:** En az 30 anlamlı kayıt içeren 6 sentetik oturum; iki proje, ret, partial done, karar değişimi ve bekleyen onay; beklenen tip/ilişki/durumları etiketle. Ek no-op ve sıfır expansion örnekleriyle gereksiz task üretimini de değerlendir; 30 anlamlı kaydın yerine no-op sayma.
- **Kabul:** Her örneğin source span'ı ve beklenen sonucu var; model geliştirmede kullanılmayan holdout ayrılmış; kişisel veri yok.
- **Doğrulama:** Corpus şema kontrolü ve insan örneklem incelemesi.
- **Beklenen dosya alanı:** `examples/corpus/; docs/quality/baseline.md` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** 1 küçük oturum.

## T02 — İki coding yüzeyinde capability spike

- **Durum / faz:** TODO / P0. **Bağımlılık:** T01. **Kapsam ID:** CAP-02.
- **İş:** Claude Code ve Codex'in kurulu/test edilebilir sürümlerini kaydet; izinli hook/transcript olayını izole fixture'da gözle.
- **Kabul:** Her yüzey için version, olay, payload, izin, truncation ve coverage raporu var; erişilemeyenler unsupported/unknown.
- **Doğrulama:** Yeni mesaj, final output, tool failure, kapanışsız session ve offline deneyi.
- **Beklenen dosya alanı:** `docs/discovery/adapter-feasibility.md` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Yüzey başına küçük deney.

## T03 — Build/extend ve teknoloji kararı

- **Durum / faz:** TODO / P0. **Bağımlılık:** T01,T02. **Kapsam ID:** EVAL-01.
- **İş:** Cortex/Tracker/mai-mcp ve Beads alternatifi için aynı corpus denemesini hazırla; lisans ve kurulum etkisini incele; seçenek öner. [Benchmark bulgularındaki](../discovery/benchmark-findings.md) güncel yapılandırma ve sonuç şablonunu kullan; [şikâyet araştırmasındaki](../discovery/user-research.md) düzeltme/karşı kanıtı atlama.
- **Kabul:** Native/config/custom/unknown matrisi ve maliyet/kalite kanıtı var; owner kararı ADR-0001/0003'e işlenir; deneme yapılamayanlar açık.
- **Doğrulama:** Versiyonlu rapor ve owner karar kaydı; test yapılmadıysa kapı açık kalır.
- **Beklenen dosya alanı:** `docs/discovery/pilot-comparison.md; docs/architecture/adr/` (henüz oluşmamış yollar uygulama sırasında açılır).
- **Boyut:** Karşılaştırma başına küçük deney.

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
- **İş:** Önce fixture/deterministic extractor; provider arayüzü, FTS ve source span doğrulama.
- **Kabul:** Desteksiz model sonucu canonical state yazamaz; truncation ve missing source görünür.
- **Doğrulama:** CAP tipleri ve invalid structured output fixture.
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

- **Durum / faz:** TODO / P1a. **Bağımlılık:** T14. **Kapsam ID:** EVAL-01,AUD-01.
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
- **İş:** AC-01..14, iki adapter, holdout corpus ve management overhead pilotu.
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

T23, erken auth/runner sınırlarının ilk kez eklendiği görev değildir; önceki kontrolleri restore/privacy açısından tamamlar. Dış connector'a özgü V27 teslim senaryoları T28'de ayrıca çalıştırılır. Gelecek capability henüz uygulanmıyorsa `not_run + faz` yazılır; mevcut MVP invariant'ı bu gerekçeyle atlanmaz.

## Çok kullanıcılı tasarım ve veri yaşam döngüsü alt işleri

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

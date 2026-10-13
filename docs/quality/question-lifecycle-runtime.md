# Soru yaşam döngüsü ve geç cevap eşleme

2026-10-13 — manuel yerel owner profili; T13e In Progress. [Kod](../../packages/domain/questions.py), [karar guard](../../packages/domain/question_decisions.py), [HTTP/UI](../../apps/local_ui/server.py), [istek şeması](../../manifests/question-lifecycle.schema.json). Yeni ana görev/engine/model çağrısı yok.

## Uygulanan davranış

Open/Answered→Deferred→Resumed ve Cancelled geçişleri reason/question revision/base state revision ile atomiktir. Cancelled terminaldir; tekrar açmak yeni gerekçeli soru revision'ı ister. Yeni revision önceki snapshot'ı Superseded history olarak korur, eski option seçimini yeni sürüme taşımaz. İlk veya revision sunumunun aynı identity/content retry'ı duplicate history yaratmaz; farklı içerik stale/conflict olarak reddedilir.

Question state değişimi canonical Decision veya Task'ı silmez. Defer→resume bile proposal'ın state_revision dayanağını değiştirir; eski approval uygulanamaz, yeni proposal/onay gerekir. Applied karar receipt'i tarihsel kanıt olarak korunur.

Sorudan önce gelen cevap Unmatched kalır. Soru geldikten sonra yetkili owner explicit `associate_answer` ister: mevcut exact question ID/revision/option yeniden kontrol edilir; yeni question_answer_associated assessment original_answer'a bağlanır. Eski cevap payload'ı değişmez. Deferred/stale/cancelled/conflicting sonuç seçime zorlanmaz. Yeniden eşleme kendi başına canonical Decision üretmez; ayrı prepare/approve/apply devam eder. Kaynak manuel, external host provenance/semantic matching iddiası yok.

Mevcut audit tablosuna question_state/question_answer_associated append-only kayıtları eklendi. SQL schema1 aynı; mevcut backup/restore tüm geçmişi taşır. Aynı512 history cap bu kayıtları da sayar; yeni write ret, eski kabul kaybı yok. İşlem ACL/current local human owner/active project gerektirir. Şema artifact'ı JSON olarak parse edildi; davranış runtime validator/testlerle sınandı, bağımsız JSON Schema engine conformance iddiası yok.

## Kanıt

13 yeni test;221runtime test geçti. Cancel/late answer, defer/resume/reassociation, orphan-first, changed revision, presentation retry, stale state, cancelled resume denial, no old approval revival, orphan→proposal, HTTP boundary, association rollback, restore history ve iki bağlantıda farklı cevap için Selected+Conflict sınandı. Gerçek tarayıcıda mevcut Task/AC/start ve Decision apply akışı; ardından defer→resume→cancel→reload ve Applied Decision korunumu geçti. [Kaynak hashli sonuç](question-lifecycle-results.json). Önceki kaynak hash/test raporları tarihsel kalır.

## Açık kabul

Bu teslim manuel owner lifecycle'ını tamamlar. Full ASK/LATE kapsamının agent kaynaklı soru yönlendirme, bilgi/görüş/approval ayrımı, policy kullanımı ve external source/presentation normalizasyonuyla eşlemesi ayrıca kontrol edilmeli; T13e/ana T13 otomatik Done sayılmadı. Gerçek adapter/MCP/source coverage T18e, pilot T24f altında açık. Background notification/host resume yok. T14 gerçek evidence/Done sıradaki çekirdek modüldür.

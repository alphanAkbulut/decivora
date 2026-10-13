# Cevaptan ayrı onaylı karar kaydına

2026-10-13 — mevcut T13e içinde çalışan yerel dilim; ana T13/T13e In Progress. [Altı kod paketinin](../delivery/build-delivery-plan.md) birinci paketi devam ediyor. Yeni task ID yok.

[QuestionDecisionService](../../packages/domain/question_decisions.py) mevcut soru snapshot'ındaki Selected AnswerRecord'tan kaynaklı Decision önerisi hazırlar. Gerekçe zorunludur. Prepare, approve ve apply ayrı UI düğmeleri/HTTP işlemleridir. Hazırlama ve onay canonical records/event üretmez; apply tek Decision create event'i ve resolution audit kaydını aynı transaction içinde yazar. Task durumları ve graph değişmez; task iptali/dış işlem onayı bu karardan çıkarılmaz.

## Teknik sözleşme

- `question_decision_proposed`: proposal ID, owner, exact question ID/revision/option/answer, reason, immutable plan/digest.
- `question_decision_approved`: proposal digest ile bound mevcut core approval. Identity/project/knowledge/authz/key kontrolleri korunur.
- `question_decision_applied`: exact question revision→canonical Decision ID, approval ve command receipt. Aynı soru sürümü yalnız bir defa çözülür; başka proposal ikinci Decision üretemez.
- Karar description'ı manual question/option snapshot, answer ID, gerekçe ve varsa task bağını içerir. External transcript/span/source receipt uydurulmaz; provenance `manual_ui`dır. Canonical body mevcut üç alanlı schema ile uyumludur; SQL schema1 değişmez.
- Apply'da soru/selection ve project/authz güncelliği tekrar kontrol edilir. Generic Workspace.apply aynı proposal planını current question guard'ı atlayarak uygulayamaz. Yeni bağımsız generic insan kararı, bu soru çözümünün receipt'i sayılmaz.
- Eşzamanlı write'lar SQLite transaction ile tek etkiye iner. Applied retry current yetkili owner'a aynı receipt'i verir, yeni side effect üretmez. Soru sonradan değişse bile geçmiş uygulanma receipt'i silinmez.
- 384 proposal/approval/resolution audit kaydı geliştirme profilinin tavanıdır; yeni kayıt reddedilir, kabul edilen geçmiş silinmez. Model, shell, dış delivery, ücretli API çağrısı yok.

## Doğrulama

10 yeni domain testi +1 gerçek HTTP testi; tüm208runtime test geçti. Separate prepare/approve/apply, fake approval, revised question, generic bypass, project stale, duplicate resolution, atomic audit rollback, restore/replay, agent/revocation ve iki eşzamanlı bağlantı tek effect sınandı. 46 geliştirme tracker testi ayrıca kontrol edilir.

Gerçek tarayıcıda soru→seçenek→gerekçe→öneri→onay→uygulama→reload çalıştı; mevcut Task/AC/start akışı korunur, Done kartı0. [Kaynak hashli sonuç](question-decision-results.json). Önceki [manuel soru raporu](pending-question-runtime.md) ilk dilimin tarihsel test/hash kanıtıdır; eski hashleri yeni kaynak gibi sunmayız.

## Kalanlar

T13e'nin cancel/superseded/defer, external presentation/source ref normalizasyonu ve orphan yeniden eşleme kabulü açık. T18e capture/MCP ve T24f gerçek/pilot soru coverage kapıları ayrıdır. Bu akış ilk tam ürün MVP kabulü veya gerçek host semantic matching değildir. Sonraki yerel iş kalan soru lifecycle; sonra T14 kriter bazlı gerçek evidence/Done ve T15 bütün zincir. Full review Inbox/graph/task impact apply UI de ilgili mevcut görevlerde açık kalır.

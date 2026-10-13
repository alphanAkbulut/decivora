# Kalıcı manuel soru ve geç cevap dilimi

2026-10-13 — **T13e In Progress; tam soru/karar sözleşmesi tamamlanmadı.** [Altı teslim planının](../delivery/build-delivery-plan.md) ilk kod parçası. Yeni ana görev yok; T13/T19/T20 devam eder.

[QuestionService](../../packages/domain/questions.py) ve [testleri](../../tests/runtime/test_questions.py), mevcut [yerel server](../../apps/local_ui/server.py) ve [arayüz](../../apps/local_ui/app.js) güncellendi. UI'da soru/2–8 seçenek kalıcı tutulur, seçenek seçilir, yeniden açılınca aynı soru ve cevap görünür. Kalıcı seçenek ID/revision ile explicit geç yanıt; zaman geçti diye soru düşmez. Bare “A” canonical option ID değildir, Unmatched kalır.

SQLite mevcut audit içinde question_presented ve question_answered kayıtları; silme/overwrite yok. Question snapshot history, current read/write ACL, local human owner, project archive guard, request retry/conflict ve atomic write korunur. Selected cevabı canonical Decision/Task/graph veya permission apply üretmez. History cap512 ve question cap100 yerel geliştirme sınırıdır; kabul edilmiş geçmiş silinmez. Kaynak manual_ui; gerçek host/message/ref veya LLM inference iddiası yok. Answer received_at manuel alım zamanıdır, harici source-created zamanı bilinmiyor.

## Doğrulama

12 yeni test:11 domain +1 HTTP. Restart, exact geç yanıt, stale option revision, unknown soru/harf, retry/duplicate/conflict, agent/scope denial, write rollback, backup/restore, history capacity ve invalid options. Mevcut uygulama regresyonu ayrıca çalıştırılır; test sayısı ürün yüzde tamamlanması değildir. Tam197runtime test geçti. 46 tracker testi de geçti. Gerçek tarayıcıda görev→kriter onayı→başlangıç→reload regresyonu ve soru→SQLite seçimi→reload akışı geçti; desktop/mobile görünümü incelendi. [Kaynak hashli sonuç](pending-question-results.json).

## Kalan kabul

Canonical Decision/Approval proposal bağlantısı ve ayrı apply, explicit source/presentation refs, cancelled/superseded/deferred, orphan yeniden eşleme, eşzamanlı farklı bağlantı testi, presentation retry ve tam ASK/LATE kabulü açık. Agent proposal/capture/MCP bu manuel owner profilinde yok. Hiçbir Task bu cevapla otomatik Done/Cancelled olmaz. Bu dilim ana T13/T13e kapanışı değildir; verifier/Done T14 sırada. Yeni ücretli model/API/gerçek transcript çağrısı yapılmadı.

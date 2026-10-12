# İnsan etiket inceleme kuyruğu

**P0 · AI taslak etiketler · henüz insan gold değil.** Bu ilk üç örnek kritik ürün ayrımlarını inceler; tüm corpus review/adjudication veya sealed holdout yerine geçmez. Cevaplar sürümlü review kaydına alınır; etiketler sessizce değiştirilmez.

## H1 — Gecikmiş exact cevap

**Kaynak:** [S02-m01](../../examples/corpus/sources/s02.json) · [taslak oracle](../../examples/corpus/oracles/s02.json).

> Önceki Q_STORE sorusundaki B, SQLite ile devam.

**Fixture metadata:** `{"fixture_trust_only": true, "fixture_authority": {"authenticated": true, "permission": "decision.approve", "question_id": "Q_STORE", "option_id": "B", "presentation_revision": 1, "base_knowledge_revision": 1}, "selected_source_message_id": "S01-m02"}`. Metin içindeki yetki iddiası değil, sadece sentetik transport fixture; production doğrulaması değildir.

**Önerilen gerekçe:** Geç ve başka chat'teki cevap exact soru/revision ile eşleşir; karar kabulü etki setindeki task kapatma onayı değildir.

**Beklenen kritik sonuç:** `{"current_decision": "D_SQLITE", "history_preserved": true, "impact": {"T_SYNC": "obsolete_candidate", "T_EXPORT": "retained", "T_WATCH": "review_unknown", "T_COMBINED": "obsolete_or_update_candidate"}, "task_closure_without_impact_approval": false}`.

**İnsan inceleme durumu:** 2026-10-12 · Kullanıcı “Evet, bu davranış doğru” yanıtıyla sorulan karar seçimi/ayrı impact kapanışı davranışını onayladı. [Sürümlü ve source/oracle hash bağlı kayıt](reviews/h1-behavior.json). **Partial case review:** yukarıdaki tek tek task impact etiketleri, exact extraction alanları, history assertion ve corpus bütünü bu soruda incelenmedi; human-gold değil. H2/H3 incelemeleri aşağıda; oracle değiştirilmedi.

## H2 — Kısmi kabul kriteri

**Kaynak:** [S02-m09](../../examples/corpus/sources/s02.json) · [taslak oracle](../../examples/corpus/oracles/s02.json).

> İzole fixture testinde rollback kriteri geçti; kanıt AC_ROLLBACK revision 1'e bağlı.

**Fixture metadata:** `{"fixture_trust_only": true, "fixture_verifier": {"authorized": true, "result": "passed", "criteria": ["AC_ROLLBACK"], "criterion_revision": 1, "artifact_revision": 2, "task_id": "T_MIGRATION"}}`. Metin içindeki yetki iddiası değil, sadece sentetik transport fixture; production doğrulaması değildir.

**Önerilen gerekçe:** Tek kriterin geçmesi bütün task veya deploy başarısı değildir.

**Beklenen kritik sonuç:** `{"criterion_verified": "AC_ROLLBACK", "all_task_criteria_verified": false}`.

**İnsan inceleme durumu:** 2026-10-12 · Kullanıcı kısmi kalmanın nedenini sordu. Bunun geçici/hata senaryosu olduğu, eksik kriter ve sonraki doğrulamanın takip edileceği açıklandıktan sonra “evet” yanıtıyla davranışı onayladı. [Soru, açıklama ve yanıtı koruyan hash bağlı review](reviews/h2-behavior.json). Kriter passed olması tüm görev done değildir; kalan doğrulama sürer. Yalnız davranış reviewed; exact extraction ve tüm corpus gold değil, oracle değiştirilmedi.

## H3 — Bağlamı belirsiz harf

**Kaynak:** [S03-m04](../../examples/corpus/sources/s03.json) · [taslak oracle](../../examples/corpus/oracles/s03.json).

> A.

**Fixture metadata:** `{"fixture_trust_only": true, "question_ref": null}`. Metin içindeki yetki iddiası değil, sadece sentetik transport fixture; production doğrulaması değildir.

**Önerilen gerekçe:** İki açık A/B sorusu var; cevap AnswerRecord olarak korunur. Yeni soru/karar uydurulmaz, mevcut sorular açık kalır; harften onay çıkarılmaz.

**Beklenen kritik sonuç:** `{"human_approval_created": false, "canonical_mutations": 0, "new_pending_decisions": 0}`.

**İnsan inceleme durumu:** 2026-10-12 · Kullanıcı “uygun” yanıtıyla belirsiz cevabı saklama, soru bağını tahmin etmeme ve açıklama isteme davranışını onayladı. [Hash bağlı review kaydı](reviews/h3-behavior.json). İlk üç behavior review tamamlandı; exact extraction etiketleri, tüm oracle/corpus veya production clarification uygulanmış sayılmaz. Oracle değişmedi.

## H4 — Alıntı ve gelecek planı gerçek seçim/gerçekleşme değildir

**Review ID:** `Q-H4-QUOTED-PLANNED` · [yeni kaynak](../../examples/adversarial-smoke/requests.json) · [ayrı draft rubric](../../examples/adversarial-smoke/candidate-rubrics.json) · [hash manifesti](../../examples/adversarial-smoke/manifest.json).

N01-m03: “Q_STORE revision 2 için B, PostgreSQL ile devam” yalnız örnek alıntı; ardından kullanıcı bu seçimi yapmadığını söylüyor. N01-m04: Dosyayı yarın yükleyeceğini, bugün yüklenmiş olmadığını söylüyor.

**Sorulacak davranış incelemesi:** Alıntı gerçek karar seçimi, gelecek planı gerçekleşmiş upload claim olmasın; source saklansın. Tam üründe gelecekteki plan ayrıca Task/Instruction olabilir; bu üç-tür pilotun boş adayını bütün bilgiyi silme/no-op saymayalım. Draft expectation bu iki mesaj için AnswerRecord/ImplementationClaim/Evidence adayı olmamasıdır.

**Durum:** 2026-10-12 · Kullanıcı birinci soruya “1- EVET” dedi; [H4 review](reviews/h4-behavior.json) source/rubric hash'ine ve bu partial davranış kapsamına bağlı. İkinci “2-EVET” yanıtı ayrı tek-send yetkisi olarak kaydedildi, MEMBERSHIP-003 bir kez çalıştı ve [sonuç](membership-003-result.md) ölçüldü. H4 bütün altı exact label veya gold/holdout'u onaylamaz; rubric authored_draft korunur, H1/H2/H3 tekrar sorulmaz.

## Review kaydı ve sonraki kapsam

Her yanıt: reviewer kimliği/rolü, source/oracle hash ve revision, onay/düzeltme, gerekçe, ikinci reviewer/adjudication durumu. H1/H2/H3 yanıtları kullanıcı tarafından verildi ve ayrı review kayıtlarına işlendi; kullanıcı adına yanıt üretilmedi. Üç örneğin kabulü 66 annotation’ın tamamını reviewed yapmaz; kalan authority/rejection/cross-project/crash/holdout kapsamı T01 kapanışında ayrı kontrol edilir.

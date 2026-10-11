# İnsan etiket inceleme kuyruğu

**P0 · AI taslak etiketler · henüz insan gold değil.** Bu ilk üç örnek kritik ürün ayrımlarını inceler; tüm corpus review/adjudication veya sealed holdout yerine geçmez. Cevaplar sürümlü review kaydına alınır; etiketler sessizce değiştirilmez.

## H1 — Gecikmiş exact cevap

**Kaynak:** [S02-m01](../../examples/corpus/sources/s02.json) · [taslak oracle](../../examples/corpus/oracles/s02.json).

> Önceki Q_STORE sorusundaki B, SQLite ile devam.

**Fixture metadata:** `{"fixture_trust_only": true, "fixture_authority": {"authenticated": true, "permission": "decision.approve", "question_id": "Q_STORE", "option_id": "B", "presentation_revision": 1, "base_knowledge_revision": 1}, "selected_source_message_id": "S01-m02"}`. Metin içindeki yetki iddiası değil, sadece sentetik transport fixture; production doğrulaması değildir.

**Önerilen gerekçe:** Geç ve başka chat'teki cevap exact soru/revision ile eşleşir; karar kabulü etki setindeki task kapatma onayı değildir.

**Beklenen kritik sonuç:** `{"current_decision": "D_SQLITE", "history_preserved": true, "impact": {"T_SYNC": "obsolete_candidate", "T_EXPORT": "retained", "T_WATCH": "review_unknown", "T_COMBINED": "obsolete_or_update_candidate"}, "task_closure_without_impact_approval": false}`.

**İnsan inceleme durumu:** 2026-10-12 · Kullanıcı “Evet, bu davranış doğru” yanıtıyla sorulan karar seçimi/ayrı impact kapanışı davranışını onayladı. [Sürümlü ve source/oracle hash bağlı kayıt](reviews/h1-behavior.json). **Partial case review:** yukarıdaki tek tek task impact etiketleri, exact extraction alanları, history assertion ve corpus bütünü bu soruda incelenmedi; human-gold değil. H2/H3 pending; oracle değiştirilmedi.

## H2 — Kısmi kabul kriteri

**Kaynak:** [S02-m09](../../examples/corpus/sources/s02.json) · [taslak oracle](../../examples/corpus/oracles/s02.json).

> İzole fixture testinde rollback kriteri geçti; kanıt AC_ROLLBACK revision 1'e bağlı.

**Fixture metadata:** `{"fixture_trust_only": true, "fixture_verifier": {"authorized": true, "result": "passed", "criteria": ["AC_ROLLBACK"], "criterion_revision": 1, "artifact_revision": 2, "task_id": "T_MIGRATION"}}`. Metin içindeki yetki iddiası değil, sadece sentetik transport fixture; production doğrulaması değildir.

**Önerilen gerekçe:** Tek kriterin geçmesi bütün task veya deploy başarısı değildir.

**Beklenen kritik sonuç:** `{"criterion_verified": "AC_ROLLBACK", "all_task_criteria_verified": false}`.

**İnsan inceleme durumu:** pending. Doğru / düzeltme + gerekçe kaydedilecek.

## H3 — Bağlamı belirsiz harf

**Kaynak:** [S03-m04](../../examples/corpus/sources/s03.json) · [taslak oracle](../../examples/corpus/oracles/s03.json).

> A.

**Fixture metadata:** `{"fixture_trust_only": true, "question_ref": null}`. Metin içindeki yetki iddiası değil, sadece sentetik transport fixture; production doğrulaması değildir.

**Önerilen gerekçe:** İki açık A/B sorusu var; cevap AnswerRecord olarak korunur. Yeni soru/karar uydurulmaz, mevcut sorular açık kalır; harften onay çıkarılmaz.

**Beklenen kritik sonuç:** `{"human_approval_created": false, "canonical_mutations": 0, "new_pending_decisions": 0}`.

**İnsan inceleme durumu:** pending. Doğru / düzeltme + gerekçe kaydedilecek.

## Review kaydı ve sonraki kapsam

Her yanıt: reviewer kimliği/rolü, source/oracle hash ve revision, onay/düzeltme, gerekçe, ikinci reviewer/adjudication durumu. Bu tur kullanıcı adına yanıt üretilmedi. Üç örneğin kabulü 66 annotation’ın tamamını reviewed yapmaz; kalan authority/rejection/cross-project/crash/holdout kapsamı T01 kapanışında ayrı kontrol edilir.

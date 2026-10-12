# İki yeni development ailesi — MEMBERSHIP-003 çalıştırıldı

**Güncel run:** Kullanıcı H4 için1-EVET ve tek-send için2-EVET dedi; [onay](authorization.json) tüketildi. [MEMBERSHIP-003 sonucu](../../docs/quality/membership-003-result.md): tek output,6 draft candidate eşleşmesi ve2 scope-no-candidate vaka. Aşağıdaki plan/manifest/hazırlık anlatımı çağrı öncesi snapshot'tır; source/rubric/prompt/plan/hashler değiştirilmedi. H4 partial review bütün label'ları gold yapmaz.

**T01h DONE yalnız paket hazırlığı.** İki yeni project/session ailesi, sekiz sentetik mesaj; eski corpus/ilk dört mesaj değiştirilmedi. Aynı typed v2 sözleşmesi: yalnız AnswerRecord/ImplementationClaim/Evidence. Bu veri hazırlayan agent'a açık olduğundan sealed/blind holdout değildir. Etiketler authored_draft; insan review/adjudication açık.

[Kaynak-only requests](requests.json) · [exact source-only prompt](prompt.txt) · [ayrı taslak beklentiler](candidate-rubrics.json) · [hash/scope manifesti](manifest.json) · [izin bekleyen plan](plan.json).

| Mesaj | Sınanan ayrım | Taslak beklenti |
|---|---|---|
| N01-m01 | Eski soru revision1 / B | AnswerRecord Q_STORE/B/revision1; tarihsel bağ korunur, current seçimi sayılmaz |
| N01-m02 | Güncel revision2 / A | AnswerRecord Q_STORE/A/revision2; candidate, onay yetkisi değil |
| N01-m03 | Alıntı içinde olumlu karar, dışında açık ret | Bu dar üç-tür pilotta gerçek seçim adayı yok; kaynak saklanır |
| N01-m04 | “Yarın yükleyeceğim”, bugün yüklenmiş değil | Gerçekleşmiş upload claim yok; kaynak saklanır, tam üründe gelecek Task/Instruction olabilir |
| N02-m01 | İngilizce exact seçim | AnswerRecord Q_UI/B/revision1 |
| N02-m02 | İngilizce upload iddiası | ImplementationClaim upload; hedef/AC kanıtı değil |
| N02-m03 | İngilizce not-run kriter raporu | Evidence AC_SMOKE/revision2/not_run; passed veya tamamlandı değil |
| N02-m04 | İki soru sunumu ve yalnız B | AnswerRecord attributes={}; soru tahmin edilmez |

N01'in iki soru sürümünde B farklı anlamdadır; eski cevap current revision'a sessizce taşınmamalıdır. N02'de onay/selection receipt yok; önceki metin bir soruyu canonical resolved yapmış varsayılmaz. Bu paket domain/reconciliation/tenant policy'yi çalıştırmaz; primary candidate ölçümüyle bu alanları karıştırma. Alıntı/gelecek planı için hiçbir proje bilgisi yok demiyoruz: yalnız bu pilotun üç candidate türünde gerçekleşmiş seçim/upload sayılmıyor.

## Çağrı öncesi sınır snapshot’ı — izin artık tüketildi

**Aşağıdaki pending/sent0 bilgisi hazırlık anına aittir; güncel sonuç ve tüketim yukarıdaki run/onay kaydındadır.** MEMBERSHIP-003-PROPOSED: mevcut ChatGPT üyeliği, boş geçici/kişiselleştirilmemiş normal Chrome sohbeti, tek gönderim ve ilk çıktı, retry/regenerate/model değişimi/tool/subagent yok, paid API yok. Prompt5321 UTF8 byte; byte token sayısı değildir. 2048 output token soft talimat; kesin token/context cap ve usage bilinmiyor, üyelik kotası kullanılabilir. Eski tek-send izinleri tüketildi. H4 davranış review ve bu yeni paketin tek-send onayı bekliyor; hiç gönderilmedi.

`prepare_typed(requests)` prompt/hash'i yeniden üretir; source/rubric/schema consistency testleri inference doğruluğu değildir. Manifestte input/prompt/plan hash'leri bulunur. Onaydan sonra ilk raw değişmeden saklanmalı; contract/source doğrulaması ve ayrı rubric scorer kullanılmalı. Missing/abstain/exception incomplete veya evaluation_error; kalite pass sayılmaz. Tam gold için exact label ve ikinci review/holdout işi ayrıca açık.

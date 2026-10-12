# MEMBERSHIP-003 — yeni sekiz mesajda ilk gerçek çıktı

**2026-10-12 · T03q DONE yalnız bu tek run'ın ölçüm/kayıt teslimi.** Kullanıcı “1- EVET / 2-EVET” ile iki ayrı soruya yanıt verdi: [H4 partial behavior review](reviews/h4-behavior.json) ve [tek-send onayı](../../examples/adversarial-smoke/authorization.json). H4 incelemesi bütün six-label gold veya dispatch izni değildir; ikinci açık onay bu tek gönderimde tüketildi. Normal Chrome boş geçici/kişiselleştirilmemiş ChatGPT, Instant UI etiketi. Submission1/output1/retry0/paid API0. Backend, usage/para ve kesin token/context cap unknown; soft2048 çıktı talimatı hard cap değildir.

[İlk ham UI Copy metni](model-runs/membership-003-response.txt) · [makine ölçümü ve guard probe](membership-003-results.json) · [dondurulmuş input](../../examples/adversarial-smoke/prompt.txt) · [önceden authored rubric](../../examples/adversarial-smoke/candidate-rubrics.json).

## Yeni örneklerde gözlenenler

| Kaynak | Beklenti / gözlenen sonuç |
|---|---|
| N01-m01 | Eski Q_STORE revision1/B, AnswerRecord olarak korundu; current revision'a taşınmadı |
| N01-m02 | Güncel Q_STORE revision2/A, ayrı AnswerRecord olarak korundu |
| N01-m03 | Alıntı + açık “bu seçimi yapmadım” ifadesinden gerçek seçim adayı üretilmedi |
| N01-m04 | Gelecekteki yükleme planı gerçekleşmiş upload claim sayılmadı |
| N02-m01 | İngilizce exact Q_UI/revision1/B cevabı bağlandı |
| N02-m02 | İngilizce upload ifadesi yalnız ImplementationClaim upload |
| N02-m03 | İngilizce test yapılmadı ifadesi Evidence AC_SMOKE/revision2/not_run; passed sayılmadı |
| N02-m04 | Belirsiz B adayı attributes={} ile korundu; soru tahmin edilmedi |

Altı quote ve iki source/request/typed contract binding geçti. **N01 TP2/FP0/FN0; N02 TP4/FP0/FN0**, toplam6 authored_draft expectation eşleşmesi. N01-m03/m04 için bu dar üç-tür scope'ta aday sayısı0; kaynaklar input içinde aynen korunur. Tam üründe gelecekteki plan Task/Instruction olabilir; bunu tüm bilgi no-op veya kayıt silme diye yorumlama.

Bu iki yeni aile önceki dört mesajdan farklıdır; fakat hazırlayan agent'a açık development örnekleri, sealed/blind holdout değildir. H4 davranışı insan onaylıdır; altı exact kind/quote/attribute tuple ve corpus bütünü human-gold değildir. Provisional entity_key, ilişkiler, authority, gerçek target/AC, maliyet ve native üstünlük skorlanmadı. Bir UI run'ı/genel n=1 kalite veya bağımsız sekiz kullanıcı sonucu iddiası yok.

## Soru sürümü ve çok-aday sınırı

İki ayrı SQLite fixture'da current question explicit seçildi (N01 Q_STORE revision2, N02 Q_UI revision1). Bütün response üzerinde mevcut bridge iki AnswerRecord gördüğünde **unmatched_or_ambiguous** döndürdü; projection değişmedi. Bu güvenli ama sınırlı P0 davranış, otomatik çok-aday reconciliation değildir.

Tanı için original request/quote/attributes korunarak her AnswerRecord ayrı response subset'inde mevcut propose fonksiyonuna verildi. Bu, raw düzeltmesi veya gizli seçim politikası değildir; raporda per-candidate diagnostic olarak işaretlidir:

| Tanı | Sonuç |
|---|---|
| N01 eski revision1 cevabı / current2 | unmatched_or_stale; mutation0 |
| N01 current2 cevabı | pending_trusted_selection; mutation0 |
| N02 explicit Q_UI cevabı | pending_trusted_selection; mutation0 |
| N02 bağsız B | unmatched_or_stale; mutation0 |

Hiçbir selection/impact/verify uygulanmadı. Modelin doğru extraction'ı bütün batch'i production karar pipeline'ında otomatik işleyebildiğimizi göstermez. [R22](../governance/risks.md) mevcut T10/T13'e bağlı: mesaj/soru/revision bazında ayrı öneriler, eskiyi history'de koruma, ambiguity ve trusted receipt bağını kaybetmeme. “Son cevap kazanır” veya operator'süz tek-aday seçimi benimsenmedi. Model N01 iki cevapta aynı Q_STORE entity_key verdi; bunlar provisional, kalıcı AnswerRecord identity eşleme kuralı ayrıca gerekir.

## Tekrar ölçüm ve kanıt

```sh
python3 -B spikes/semantic-chain/membership_typed.py derive --requests examples/adversarial-smoke/requests.json --response docs/quality/model-runs/membership-003-response.txt --out /tmp/membership-003-replay.json
python3 -B -m unittest discover -s spikes/semantic-chain -p test_membership_typed.py -v
```

Komutlar yeni model isteği göndermez; output yolu yeni olmalı. **93 semantik test passed**, iki yeni saved-output/guard regresyonu dahil: exact raw hash/negation/old-current/not_run, draft/gold ayrımı, whole-batch block ve explicit subset no-mutation. Raw2555UTF8byte, SHA-256 `0adebd7574175b5c2b4508b926930da78a6ba61947ea79028b8695a1e2ebf3cb`. UI Copy clipboard byte'larıdır, provider transport byte'ları değil. Özel conversation URL/ID repo'ya taşınmadı; screenshot yerelde repo dışında. Ham çıktı, prompt, manifest, rubric veya eski run sonuçları onarılmadı/değiştirilmedi.

## Kapanış ve sonraki iş

H4 partial review T01i scoped DONE; actual single-run evidence T03q scoped DONE. Ana T01/T03 açık; production stack ve T04 başlamadı. Yeni model izni tüketildi; otomatik retry/yeni inference yok. Sıradaki bağımsız iş R22 için candidate/mesaj/revision bazında read-only proposal toplama sözleşmesi ve stale/ambiguity negatifleri; ardından aynı bilgiyle resume/dosya/native kıyası. Üretim state mutation/IAM/target/AC sınırını bu yeni tanıyla kapatma.

# MEMBERSHIP-001 — ilk gerçek quote-only çıktı

> Bu kayıt v1 girişiminin tarihsel ölçümüdür. Sonradan ayrı onayla çalıştırılan v2 için [MEMBERSHIP-002](membership-002-result.md) raporuna bak; aşağıdaki v1 ham çıktı/skor ve hazırlık bilgileri korunur.

**2026-10-12 · Tek UI gönderimi, tek ilk çıktı, retry 0.** Kullanıcı kesin token/context cap'in doğrulanmadığı riskini açıkça kabul etti; [onay kaydı](../../examples/membership-smoke/authorization.json) bu girişimde tüketildi. Mevcut normal Chrome ChatGPT hesabında boş geçici/kişiselleştirilmemiş oturum; UI model etiketi **Instant, 3 seçenek arasında 1. sırada**. Gerçek model sürümü, token/kota ve parasal maliyet unknown. Paid API çağrısı açılmadı. Model tools/subagent kullanımına talimat verilmedi; UI'de tool çıktısı gözlenmedi, gizli provider işlemleri hakkında kesin sayı iddia edilmez.

[Ham UI-copy çıktı](model-runs/membership-001-response.txt) · [makine ölçümü ve guard probe](membership-001-results.json) · [önceden hazırlanan input](../../examples/membership-smoke/prompt.txt). UI clipboard biçimi byte-preserved kaydedildi; provider'ın transport byte'ları değildir. Accessibility text'te görünen çift boşluklar clipboard'da yoktu; import için clipboard metni kullanıldı. Ham veri elle düzeltilmedi. Private conversation ID/URL repo raporuna taşınmadı; screenshot yerelde repo dışında tutuldu.

## Gözlenen sonuç

| Alan | Sonuç | Sınır |
|---|---|---|
| Transport | İlk output geldi; JSON ve iki request/contract binding doğru | n=1; future erişim veya model kararlılığı garantisi değil |
| Exact source | Üç candidate quote kaynakla eşleşti; span kodda hesaplandı | Kaynak konumu engeli bu run'da yok; bütün future output'lar için başarı değil |
| H1 geç cevap | Q_STORE/B/SQLite doğru sözlerle çıktı; `question_revision`, `selected_option` kullandı | Bridge `presentation_revision`, `option_id` ister; otomatik alias onarımı yapılmadı, proposal unmatched_or_stale |
| Upload claim | Tür Execution; attributes action=reported_upload, target=unspecified | Draft expectation ImplementationClaim; modelin gözlenmiş upload iddia ettiği söylenemez, ama typed sınıf uyuşmadı |
| H2 criterion | Evidence, isolated_fixture/reported_result=passed/AC_ROLLBACK revision 1 | Alan adları farklı; gerçek verifier/AC kanıtı değil, bütün task done olmadı |
| H3 belirsiz A | abstain, records=[] | Yanlış soruya bağlamadı; draft rubric'in istediği AnswerRecord eksik, değerlendirme incomplete |
| Domain guard | Kontrollü fixture'da H1 unmatched_or_stale, H3 needs_context; projection unchanged | Gerçek production IAM/domain execution testi değil |

**Birincil exact candidate skor:** S02 TP=0 / FP=3 / FN=3; S03 TP=0 / FP=0 / FN=1, abstained. Toplam TP=0 / FP=3 / FN=4; genel gate **incomplete**. Bu sayıların “ürün %0 doğru” anlamı yoktur: expectations authored_draft, insan review yalnız davranışları onayladı; exact tür/attributes/spans için human-gold yok. Başarılı quote kontrolünü semantik/domain başarısı diye sunma. Post-hoc nitel yorum primary score'un yerine geçmez.

## Kök neden ayrımı ve alınan ders

- **Gözlenen:** v1 prompt yalnız serbest `attributes:{}` örneği ve tür adları veriyor; ihtiyaç duyulan association field adlarını/tür semantik sınırını açıkça söylemiyor. Model kendi adlarını üretti. Bu, caller–producer sözleşmesinde belgelenmiş eksik; modelin bütün anlam hatalarının açıklaması değil.
- **Gözlenen:** “bağlam yetersizse abstain” talimatı, “cevap var ama hangi soru bilinmiyor” durumunu ayırmıyor. H3'te güvenli abstention yaptı, fakat taslak candidate preservation beklentisini karşılamadı. Source A metni paket içinde korunuyor; candidate ve clarification UX ayrı.
- **Korunan:** Beklentiler veya geçmiş raw değiştirilmedi; alanları `selected_option→option_id` diye sessizce map etmedik, Execution'ı Claim'e çevirmedik. Source/type/authority validation gevşetilmedi. İlk girişimden sonra yeni send veya retry yapılmadı.
- **Yöntem:** Modelden beklenen alan ve enum anlamlarını açık, sürümlü contract ile sun; byte/span/kimliği kod doğrulasın; unknown/abstain'i pass sayma. Bu ders [ortak kanıta dayalı rehberin](../governance/evidence-first-development.md) “sözleşmeyi çağrıdan önce sabitle” ilkesinin somut örneğidir; global config bu tur değiştirilmedi.

## Offline düzeltme: ayrı v2 contract hazır

`membership_typed.py`: yeni `decivora-membership-batch-2`, attribute_contract_id; bu dar pilotta AnswerRecord / ImplementationClaim / Evidence için açık alanlar ve tür açıklaması. AnswerRecord ya üç association alanıyla ya belirsizse boş attributes ile gelir; yanlış field/alias/boolean revision/authority/Execution reddedilir. Evidence.result metindeki raporu taşır, verification authority değildir. Source spans için mevcut adapter korunur. Sadece envelope formatının kontrollü projection'ı yapılır; candidate semantics onarılmaz.

[4708-byte v2 prompt](../../examples/membership-smoke-v2/prompt.txt) · [v2 planı](../../examples/membership-smoke-v2/plan.json). Aynı dört development kaynak mesajı; yeni experiment prompt'a draft rubric verilmez. V2 status **offline_prepared_not_authorized**, submissions 0. Üç candidate kind'ı bu pilotun sınırıdır; ürünün diğer knowledge türleri tam vizyonda korunur.

```sh
python3 -B spikes/semantic-chain/membership_typed.py prepare --requests examples/membership-smoke/requests.json
```

**78 semantik suite testi passed**: iki gerçek output regresyon testi ve dört typed contract testi eklendi. Bunlar ikinci canlı model deneyi değildir. Orijinal v1 raw yeni v2 başarı sonucu olarak import edilemez; yeni candidate validation kuralı geçmiş ölçümü değiştirmez. V1 ön-hazırlık kanıtı eski test dosyası hash'ini taşır; yeni regression test eklenmesi o snapshot'ı tarihsel yapar, hashleri tekrar yazıp yeniymiş gibi göstermedik.

## Sıradaki adım ve durma noktası

Bu tek girişim tamamlandı; R21 producer contract riski observed, quality gate açık. Source bağlama iyileşmesi görüldü; gerçek modelin v2 contract'a uyacağı henüz kanıtlanmadı. Yeni tek-send onayı/route sınırı olmadan v2 gönderilmez; önceki onay tüketildi. Native/economic/broad corpus karşılaştırması, insan exact label review ve production stack kararı ayrı kapılar. Başarısızlık yeni genel araştırma veya sınırsız model tekrarına dönüştürülmez.

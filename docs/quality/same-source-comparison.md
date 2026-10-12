# Aynı dört kaynak mesaj üzerinde ilk ortak karşılaştırma

**2026-10-12 · T03p DONE · P0 geliştirme tanısı.** Kural tabanlı Spike-0 extractor, daha önce gerçek MEMBERSHIP-002 model testine verilen aynı iki request/dört mesaj üzerinde çalıştırıldı. Model yeniden çağrılmadı; ilk ham çıktısı kaynak/typed contract'tan geçirilerek kullanıldı. Rubric ancak iki prediction seti üretildikten sonra okundu; çıkarım oracle görmedi.

[Makine sonucu](same-source-comparison-results.json) · [karşılaştırma kodu](../../spikes/semantic-chain/compare_membership.py) · [önceki model ölçümü](membership-002-result.md).

| Yöntem | Aday sayısı | Shared span/kind TP / FP / FN | Önemli kapsam farkı |
|---|---:|---|---|
| Spike-0 lexical | 1 | 0 / 1 / 4 | Geç cevabı Decision olarak sınıflandırdı. AnswerRecord/Evidence türleri yok; human upload claim kuralı yok |
| Kayıtlı MEMBERSHIP-002 | 4 | 4 / 0 / 0 | Geç/belirsiz cevap, upload claim ve Evidence draft türleriyle eşleşti; aynı development örnekleri |

Ortak puan: project/message/kind/Unicode start/end; exact quote ayrıca kaynak üzerinde doğrulanır. Attributes yalnız model tarafında typed validation'dan geçer, karşılaştırma metriğine katılmaz. Beklentiler önceden authored_draft; human-gold veya blind holdout değildir. Baseline farklı/eksik candidate türleri nedeniyle bu görevde kapsam eksiği gösterir; genel semantik kalite veya bütün ürünler arasında ranking değildir. Kural extractor'a aynı context alanı verildi, fakat mevcut kod bu alanı kullanmaz; scope farkı gizlenmedi. Actor mapping mevcut baseline'da human_owner→user, diğerleri→assistant; production yetki karşılaştırması değil.

**Bulgu:** Basit kelime kalıpları ucuz aday sinyali için kullanılabilir, fakat bu haliyle soru sürümü/cevap ilişkisini veya kriter kanıtını taşımıyor. Bu, tüm metni her seferinde modele gönderme gerekçesi değildir. Deterministik source/type/quote/budget ve structured input yolları korunur; daha fazla etiketli örnek olmadan yeni sözlük kuralı veya routing eşiği seçmedik.

## Çalıştırma ve kontroller

```sh
python3 -B spikes/semantic-chain/compare_membership.py
python3 -B spikes/semantic-chain/compare_membership.py --out /tmp/same-source-comparison.json
python3 -B -m unittest discover -s spikes/semantic-chain -p test_compare_membership.py -v
```

Yeni dependency, model/API/egress veya canonical mutation yok. `--out` var olan dosyanın üzerine yazmaz. Beş yeni testle toplam91 semantik test passed: shared-field/project scope, eksik/duplicate/foreign rubric paydasını değiştirme retleri, abstention'ın incomplete kalması, değiştirilmiş caller output'unun original real run olarak sunulmaması ve yeni paket/schema/hash kontrolü.

İlk yerel harness denemesi `KeyError: project_id` verdi: source namespace'i ham türev adayında aramıştık. Normalizasyonu mevcut validate çıktısından aldık; namespace original request'ten ekleniyor. İlk denemede sonuç dosyası oluşmadı, model çağrısı yapılmadı. Ham çıktı/alanlar veya rubric değiştirilmedi; başarılı sonuç ve regresyon namespace sınırını kapsar.

## Ölçülmeyenler ve sonraki adım

Native tool karşılaştırması **not_run**. Yeni inference, eş koşullu latency, düzeltme süresi, gerçek token/para ve production authority/graph/target/AC bu skorun dışındadır. Modelin shared skorundan typed veya domain release başarısı çıkarılmaz. Dört mesaj/iki request bağımsız dört kullanıcı örneklemi değildir; aynı eski development mesajlarını tekrar kullanıyoruz.

[İki yeni development ailesi](../../examples/adversarial-smoke/README.md) sekiz sentetik mesajla hazırlandı; sent=0, gold/holdout değil. Eski/yeni soru sürümü, alıntı, gelecekteki yükleme planı, İngilizce seçim/claim/not_run kanıtı ve belirsiz kısa cevap ayrı adaylar olarak sınanacak. Yeni live çağrı onayı ayrı; önceki izin tüketildi. Sonuç kötü çıkarsa raw/rubric korunacak; doğrulayıcıyı veya paydayı geçmesi için daraltmayacağız.

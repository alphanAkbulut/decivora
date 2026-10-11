# Konuşma dili, proje içeriği ve yerelleştirme

**2026-10-11 — Kullanıcı ihtiyacı ve Q12-A ürün tercihi kabul edildi; teknik çözüm/faz ayrıntıları öneri, uygulanmadı.** Kullanıcı herkesin İngilizce konuşmadığını, konuşma dilinin tespit edilip not/proje içeriğinin o dilde hazırlanmasını istedi; maliyetli otomasyon P2'ye bırakılabilir. Bu, yalnız İngilizceye göre tasarım yapmama gereksinimidir. [Kapsam](full-scope.md), [token ekonomisi](../architecture/routing-token-economy.md), [lexical adaylar](../architecture/lexical-prefilter.md) ve [Q12](../delivery/decision-brief.md) ile birlikte geçerlidir.

## Üç farklı dil kavramı

| Kavram | Anlam / sınır |
|---|---|
| Kaynak dili | Mesaj/span'ın özgün dili veya dilleri; mixed/undetermined mümkün. Orijinal kaynak sessiz çevrilmez |
| İçerik üretim dili | Yeni görev başlığı, açıklama, gerekçe, hazır AC/DoD, review açıklaması ve devam paketinin dili |
| Arayüz dili | Menü, düğme, sistem durum etiketi ve yardım metni; kaynak veya bütün kayıtların aynı dilde olmasını zorlamaz |

Kullanıcının hedefi: izinli insan konuşmasının dilinde anlaşılır proje çıktıları. Assistant çıktısının İngilizce olması veya kod/stacktrace'in İngilizce kelimeler içermesi insanın dil tercihini kendiliğinden değiştirmez. Bir proje birden fazla session/insan/agent dili taşıyabilir. **Q12-A kabul edildi:** proje çıktı dili sabit kalır; sonraki session'ın farklı dili yalnız değişiklik önerisi doğurur. Kullanıcı kabul etmedikçe yeni notlar mevcut proje dilinde üretilir; eski notlar otomatik çevrilmez.

## Önerilen çözüm

1. Kaynak metin Unicode olarak korunur; source span, offset, ACL ve revision aynı kalır. Dil etiketleme için gereken veri mevcut izinli kaynaktan gelir; ek hesap taraması veya veri çıkışı yok.
2. Açık kullanıcı tercihi varsa onu uygula. Yoksa yeterli insan metninden hafif yerel tespit önerisi üret; dil modeli yalnız dil bulmak için varsayılan çağrılmaz. Kısa/karışık metinde undetermined/mixed veya belirsiz sonuç; yanlış kesinlik üretme. Detector/library/sürüm T03 sonrası seçilir, bir başarı oranı iddia edilmez.
3. Kabul edilmiş Q12-A kuralı: mevcut proje çıktı dili başka session'ın diliyle kendiliğinden değişmez. İlk güvenilir insan dili başlangıç önerisi olabilir; açık kullanıcı seçimi esas alınır. Farklı dil için öneri reddedilirse/yanıtsız kalırsa mevcut dil korunur; kabul edilirse yeni policy revision/effective_from ile sonraki üretime uygulanır. UI locale ayrıdır. Task'a özel açık dil override'ı teknik adaydır; proje policy'sini sessiz değiştirmez. Agent'ın dili veya içeriği insan dil değiştirme onayı yerine geçmez.
4. Yeni notları mevcut extraction/generation çağrısında doğrudan etkin dilde üret. Önce İngilizce yazıp ikinci çağrıda çevirme varsayılan yol değildir. Mekanik durum/şablon/UI işlemleri kodla; kapsamlı anlatı yine gereken izin/bütçe ve kalite kapısıyla.
5. Mevcut kayıt, event, karar, AC veya artifact üzerinde dil değişimi nedeniyle sessiz rewrite yapma. Yeni üretim dili ve tarihsel içerik ayrı; başka dilde görüntüleme ayrıca source revision'a bağlı türevdir.
6. Orijinal alıntı, dosya yolu, API/schema adı, kod, hata mesajı, commit/task ID ve teknik sembol korunur. İnsana açıklama etkin dilde olabilir; kanıt veya tanımlayıcı çevrilerek değiştirilmez.

İngilizce/Türkçe eş anlamlı açıklamaları iki ayrı task sanmama önemli kalite hedefidir. Cross-language eşleşme yalnız keyword benzerliğiyle auto-merge yapmaz; kaynaklı aday/uncertainty ve mevcut insan onayı korunur. Farklı dillerde ifade edilen çelişki veya ret gerekçesi retrieval'da kaybolmamalı.

## Mantıksal veri ve MCP sözleşmesi

Yeni DB/engine gerekmez. Aday metadata:
- Source/span: language tags veya mixed/undetermined, language_origin (user-specified/detected), detector_version ve uncertainty. Detector skoru kalibre edilmeden doğruluk olasılığı değildir.
- Project/output policy: seçili output_language, UI locale tercihi, scope/policy revision, effective_from ve seçimi yapan doğrulanmış insan; Q12-A uyarınca dil seçimi/değişimi kaydedilir; fiziksel alanlar teknik adaydır.
- RecordVersion/brief: content_language, kullanılan output policy revision; varsa translated_from source record/version, translator method/version ve review state.

Generated içerik ve çeviri kaynak ACL'sini genişletmez; cache anahtarı output locale/policy ile ilgili source/record/detector/template/extractor sürümlerini kapsar. Yeniden oynatma çeviri veya model çağrısı başlatmaz. Dil policy'si değişince ilgili brief/cached view güncelliği yeniden değerlendirilir; bütün proje geçmişi yeniden analyze edilmez.

MCP sorgusunda isteğe bağlı output language tercihi policy kapsamında çözülebilir; kaynak dili ve coverage korunur. Bu, bütün stored kayıtların o dilde zaten olduğu garantisi değildir. Fallback varsa neden/dil açık gösterilir; İngilizce cevabı “Türkçe tamamlandı” diye etiketleme. Nihai alan adı/transport/DDL henüz seçilmedi.

## Maliyet sınırı

Hafif yerel dil tespiti CPU/iş maliyeti taşır; kendiliğinden LLM token gerektirmez. Mevcut model çağrısının doğrudan istenen dilde üretimi ikinci çeviri çağrısını önlemeyi hedefler, fakat dillerin tokenizer/output uzunluğu ve model kalitesi farklı olabilir. Aynı kelime sayısının aynı token veya fiyata karşılık geldiği iddia edilmez.

Arşivdeki bütün notları çevirmek, çok dilli embedding/reranking veya çok dilde türev üretmek ayrı metered iştir. Varsayılan kapalı; ihtiyaç, veri izni, bütçe ve [yüksek tüketim onayı](token-risk-and-approval.md) kapsamında. Görünümde yalnız gereken kayıtları çevirme/cache adayı ile tüm proje toplu çevirisi ayrı seçeneklerdir. Bütçe dolarsa untranslated/pending durum görünür; kaynağı silme veya hatalı çeviriyle completed deme.

UI'nin sabit metinleri sürümlü locale kataloglarından gelir; her ekran açılışında modele menü çevirtme. Hazır AC/karar açıklamasının çevirisi teknik anlamı değiştirmişse yalnız görsel dil değişimi sayılmaz; normal diff/review gerekir. Çeviri edilmiş açıklama bağımsız test/approval kanıtı değildir; approval kapsamı ve source revision korunur.

## Faz yerleşimi

| Faz | Planlanan dil davranışı | Sınır |
|---|---|---|
| P1a/P1b temel | Unicode/source korunumu, language metadata/policy için genişletilebilir yapı, pilotta açık çıktı dili; kod/kanıt/ref değiştirmeme | Otomatik çok dil desteği veya tüm dillerde model kalite iddiası yok; ilk pilotun dilde üretimi ayrıca test edilir |
| P2 | Hafif otomatik tespit, mixed/short fallback, Q12-A: sabit proje dili ve insan onaylı değişim önerisi, seçili UI locale katalogları, çok dilli çıkarım/reconciliation/retrieval testleri | Destek matrisi dil ve model/host sürümü bazlı; ihtiyaç varsa kontrollü türev çeviri |
| P3 ve sonrası | Ölçümle model routing, yeni dil paketleri ve isteğe bağlı büyük çeviri işleri | Bütçe/onay/kalite kapıları; ekipte kişisel UI locale ortak canonical içeriği değiştirmez |

İlk fixture TR/EN adayıdır; bunun bütün dilleri kapsadığı söylenmez. Yeni diller kullanıcı ihtiyacı ve dil/kalite raporuyla eklenir; desteklenmeyen dil sessiz no-op veya otomatik yanlış İngilizce dönüşü olmaz. MVP'nin 14 AC'si ve 32 ana scope korunur; cross-cutting CAP/KNO/UX/CST/EVAL açılımıdır.

## Sentetik örnekler ve planlı kabul

Bunlar beklenen davranışlardır; detector/parser/model/UI çalıştırılmadı.

| ID | Örnek ve beklenen kabul |
|---|---|
| LANG-01 | İnsan Türkçe konuşur, assistant İngilizce kod verir: kaynaklar korunur; açık Türkçe çıktı tercihi değişmez, kod/ref aynen kalır |
| LANG-02 | “OK”, yalnız JSON veya mixed metin: zoraki dil değişimi yok; uncertainty/fallback görünür |
| LANG-03 | Türkçe çıktı dilli projede İngilizce insan session'ı başlar: yeni notlar Türkçe kalır; dil değişimi önerisi sunulabilir. Ret veya yanıt yoksa policy değişmez; assistant/kod dili onay değildir |
| LANG-04 | Yetkili insan çıktı dilini değiştirir: policy revision/effective_from kaydedilir; sonraki üretim yeni dilde, eski not/event/karar/AC aynı kalır. Stale/çakışan tercih normal revision kontrolüyle ele alınır; toplu çeviri tetiklenmez |
| LANG-05 | Locale katalog/UI refresh/graph için model çağrısı yok; toplu çeviri izinsiz/bütçesiz açılmaz |
| LANG-06 | Aynı iş TR/EN ifade edilir: kaynak/ret gerekçesi korunur; duplicate/conflict holdout ile ölçülür, keyword otomatik merge yapmaz |
| LANG-07 | Türev/cached çeviri source ACL/revision ve izin iptalini izler; özel metin diğer kullanıcıya/LLM'ye sızmaz |
| LANG-08 | Desteklenmeyen dil/model düşük kalitesi: fallback/not_run/coverage açık; yanlış completion, kayıp karar veya garanti tasarruf yok |

T01 corpus'una dil örnekleri eklenir. T05e/T24p temel dilimleri ile P2 T25a/T26c otomasyon/kalite dilimleri [backlog'da](../delivery/backlog.md) yer alır. Ölçüm: language tespit hatası/unknown, kayıt/ilişki/ret recall, yanlış çeviri veya yanlış karar, duplicate ve kullanıcı düzeltme sayısı, toplam çağrı/token/latency/review yükü. Detector belirlemek için görev içi bütün konuşmaları yeni modele gönderen pahalı analiz kurulmaz. Gerçek sonuçlar not_run.

## Q12 — Karma projede çıktı dili değişimi

**A — Seçildi (2026-10-11):** Proje dili konuşmanın ilk güvenilir dilinden önerilsin, kullanıcı düzeltebilsin; sonraki başka dil sinyali proje dilini değiştirme önerisi olsun. Ortak kayıtlar tutarlı kalır, eski notlar kendiliğinden çevrilmez.

**B — Korunan alternatif; varsayılan seçilmedi:** Her session'ın konuşma dilinde yeni not üret; aynı projede farklı dilli kayıtlar bulunabilir. Kaynaklar birleşir, başka session'da retrieval/çeviri ihtiyacı görünür.

Kullanıcı seçili A açıklamasına “a ile devam et” yanıtını verdi. Q12-A kabul edildi; session bazlı otomatik dil değişimi (B) varsayılan seçilmedi. Gerekçe: ortak görev/karar/AC dili tutarlı kalır, farklı sohbetler kontrolsüz dil değişimi yaratmaz; eski geçmişin çeviri maliyeti ve anlam değişimi önlenir. Bedel: sonraki sohbetin diliyle proje çıktısı farklı olabilir; değişim önerisi kullanıcının seçimini gerektirir. Bu gerekçe önerinin değerlendirmesidir; kullanıcının belirtmediği kişisel motivasyon olarak sunulmaz.

Seçim ürün davranışını karara bağlar; detector/library, desteklenen diller, ücret/egress, sayısal eşik veya genel dil desteği onayı değildir. Teknik tasarım ve P1/P2 ayrımı öneri/plan olarak kalır; LANG senaryoları not_run. Yeni output policy onayı geçmişi çevirme, kaynak metni değiştirme veya yeni modele veri aktarma izni vermez. Uygulama T05e/T24p/T25a/T26c üzerinden doğrulanır.

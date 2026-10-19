# İlk kayıtlı gerçek konuşma → model → inceleme çalışması

**19 Ekim 2026 · T09/T17/T19/T21. Durum: sınırlı gerçek API çalışması tamamlandı; semantik kabul açık.**

## Yetki ve kapsam

Kullanıcı bu oturumda açıkça onayladı: daha önce yerel TEST alanına kaydedilmiş6maskelenmiş mesaj, ilgili sınırlı proje/karar/görev bağlamı, OpenAI GPT-6 Luna; en fazla6generation+6token-count, istek başına10000input/2000output, bu deneme≤$0.25 ve önceki toplam≤$3. Yeni sohbet/host okuması, retry, model yükseltme, otomatik canonical apply ve sürekli aktarım yok. Önceki synthetic-only onayı bu veri paylaşımının gerekçesi olarak kullanılmadı; ayrı onay referansı private packet ve source grant'lerine kaydedildi.

Gerçek mesajlar ve ham yanıtlar repo dışında private pilot kopyasında tutuldu. TEST uygulamasının model kapalı sınırı değiştirilmedi. Kimlikler, metinler, anahtar, bütçe ledger'ı ve private approval packet GitHub'a eklenmedi. Credential taraması tekrar çalıştırıldı; bu tarama bütün PII/sır türlerini tanıyan eksiksiz bir sınıflandırıcı değildir.

## Çalışan kod

- [Kaynak başına factory](../../packages/capture/granted_extractors.py): exact source/hash/grant/context/provider sınırları; farklı mesajlar için ayrı extractor.
- [Yerel UI sunucusu](../../apps/local_ui/server.py): trusted factory queue, tek kaynak analizi ve server constructor'a bağlı; varsayılan kapalı, TEST bağlantısı reddedilir.
- [Çalıştırıcı](../../scripts/run_saved_conversation_pilot.py): offline SQLite snapshot, exact6kaynak, payload/hash/bağlam sabitleme, mevcut ortak bütçe ledger'ı, ayrı insan paylaşım izni, tek geçiş; otomatik apply yok.
- Sonlu6payload whitelist ve mevcut duplicate-dispatch engeli yeni çağrı/hash eklenmesini önler. Kabul edilmiş tarifede bütün input cache-write + tam output ile muhafazakâr rezervasyon6×2250=13500microusd, yani$0.0135; $0.25deneme sınırının altında. Mevcut$3root ve geçmiş kullanım değiştirilmedi. Bu limit account genelinde banka faturası garantisi değildir.

## Bulunan ve giderilen gerçek hata

İlk offline hazırlık `stale_source` ile durdu; API çağrısı0. Dialogue preparation Codex rol/provenance alanlarını eklerken Responses payload doğrulayıcısı yalnız id/hash/text bekliyordu. Böylece gerçek native kaynak yanlışlıkla değişmiş sayılıyordu; önceki manual-source sentetik kontroller bu kopukluğu göstermedi.

Ortak `source_envelope` artık preparation ve dispatch doğrulamasında aynı tam kaynağı üretir. Metin, rol/provenance, source kind veya notice değişirse eşleşme reddedilir; doğrulama gevşetilmedi. Başarısız offline kopya private alanda korundu, yeni hazırlık yapıldı. Bu, başarısız ücretli isteğin tekrarı değildir. Native alanları içeren pozitif ve tamper negatif regresyonları eklendi.

**Ders:** Adapter'ın gerçek envelope biçimi, ortak extractor'a kadar uçtan uca taşınmalı. Manual kaynak testi native entegrasyon kanıtı değildir. Her adapter için actor/provenance alanları olan contract örneği hazırlanmalı; source hash kontrolü geçsin diye metadata atılmamalı.

## Ölçülen sonuç

| Ölçü | Sonuç |
|---|---:|
| İşlenen gerçek kayıt | 6 |
| Generation / token-count HTTP | 6 / 6 |
| Ready for review | 6 |
| Kaynak/çıktı sözleşmesinden geçen | 6 |
| Yeni Task önerisi / Decision önerisi | 6 / 1 |
| Mevcut görev durum / soru yanıt / ilişki önerisi | 0 / 0 / 0 |
| Coverage | 6partial |
| Input / output token toplamı | 11018 / 3167 |
| Deneme maliyet tahmini | $0.002963 |
| Önceki pilotlar dahil toplam | 26generation / 52HTTP / $0.052555 |
| Ortak$3tavandan tahmini kalan | $2.947445 |
| Canonical records / otomatik apply | 0 / 0 |
| Orijinal TEST logical dump eşitliği | Değişmedi |

Bunlar6mesajdan7**öneri**dir; duplicate veya yanlış yorum içerebilir. Bağımsız insan etiketlemesi yapılmadı; precision/recall, gerçek tamamlanma ve kullanıcı değerini kanıtlamaz. Mevcut pilotta canonical görev olmadığı için mevcut görev status eşleme kabulü bu çalışmadan çıkarılamaz. Gerçek captured kaynakların bounded/partial geçmişi tüm konuşmanın yakalandığı anlamına gelmez. API reasoning seviyesi ayrıca gönderilmedi; ana geliştirme sohbetinin Medium ayarı API'ye taşınmadı.

## Doğrulama ve kalan teslim

Yeni hedefli kontroller: çok kaynaklı UI command/queue, yeni izinsiz import, stale context, revoked authority, expiry, native metadata tamper, ayrı clone/TEST dokunulmazlığı, root prior-spend korunması ve tekrar gönderilmeme. Tüm çağrılar fixture testlerinde sahtedir; yalnız yukarıdaki ayrı6çağrı gerçek API kullanır. Nihai test kaydı [işleme raporunda](conversation-processing-runtime.md#kaynak-başına-model-aktivasyonu--19-ekim-2026).

Sıradaki ürün bağlantısı mevcut T09/T17/T19 kapsamında: önerileri insanın kaynaklarıyla inceleyip ayrı uygulaması; izin kapsamı ve bütçeyi açıklayan aktivasyon/onboarding; canlı capture pause/revoke/gap ve sürekli worker. Tek deneme onayı tüketildi; yeni gerçek kaynak paylaşımı veya sürekli aktarım için kapsam yeniden belirlenmeli. Ana task/MVP Done yapılmadı, yeni takip görevi üretilmedi.

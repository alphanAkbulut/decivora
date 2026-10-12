# RECEIVER-002: ilk gerçek wire-2 çıktı

**2026-10-13 · Tek native Luna/Low turn tamamlandı; sonuç `invalid_contract`, skorlar hesaplanmadı.** [Değişmez ham metin](model-runs/receiver-002-response.txt) · [Ölçüm ve proje tanıları](receiver-002-results.json) · [Tüketilmiş izin](../../examples/receiver-next-smoke/authorization.json).

## Ne denedik?

Q03-R6 sorusuna kullanıcı “Bu tek yeni denemeyi onaylıyorum” yanıtını verdi. Bu yanıt açık soru ID'sine ve ayrı request/prompt hash'ine bağlandı; eski izin kullanılmadı. Onay dispatch öncesinde `70941bf8ffe6cb93f5f1816ac532f48db2e6b52f` commit'inde yayımlandı ve tekrar okundu.

Yeni projectless Codex sohbetine yalnız frozen **8089 UTF-8 byte** prompt, iki sentetik proje, sekiz mesaj, altı önceden çıkarılmış record ve prompt içindeki machine schema gönderildi. Configured model `gpt-6-luna`, reasoning `low`. Oracle, parent geçmişi ve repo gönderilmedi. Bir initial turn, ilk full final output; follow-up/retry/model tool/subagent/paid API **0**. Native host delegation wrapper enjekte etti; görünmeyen host/global context'in olmadığını veya backend model kimliğini doğrulayamadık.

Bu deney **mevcut typed/source-bound bilgiyi yeni oturumun okuyabilmesi** hakkındadır. Serbest metinden yeni kayıt keşfi, holdout veya ürün tamamlanma testi değildir. Frozen hazırlık manifestindeki `not_run` tarihi değiştirilmez; bu ayrı rapor actual run otoritesidir.

## Nerede başarısız oldu?

| Katman | Gözlenen sonuç | Kabul etkisi |
|---|---|---|
| Native gönderim / tam final capture | Tek çıktı; JSON syntax geçerli | Çıktı alındı; kalite başarısı değil |
| Proje 1 / storage | Zorunlu `next_actions` alanı yok | Machine schema reddetti; eksik alan boş listeyle tamamlanmadı |
| Proje 2 / UI | Belirsiz `N02-m04` için `question_id:"Q_UI"` önerildi | Kaynak record soru belirtmiyor; source guard tahmini bağlamayı reddetti |
| Bütün deney kalite kapısı | `schema oneOf at $.responses[0]` | `invalid_contract`; readback/action skorları null |
| Wire-2 bağımsız review | İki proje de `invalid_project_output` | Taslak review yok; başarılı alt parça score'u üretilmedi |
| Karar / hedef / test uygulaması | Hiçbiri çalıştırılmadı | Canonical mutation ve paid API 0 |

**Skor dışı tanı:** Q_STORE revision2 ile Q_UI revision1 bu kez korunmuş; eski/current cevap durumları, numeric AC revision2, `not_run`, `reported_only` ve false approval/verification literal'ları görünür doğru. İlk run'ın invalid abstention/string revision hatası bu çıktıda gözlenmedi. Bunlar bütün çıktı kabulünü veya genel anlam doğruluğunu kanıtlamaz; iki request farklı ve aynı örnekler geliştirme sırasında görülmüş olduğundan adil holdout ilerleme oranı çıkarılmaz.

Ham çıktı **1488 byte/karakter**, SHA-256 `3e72906a5f34c00863e64245b954f443fd200f4502352b051788df1e605c101a`. Karakter ve byte sayısı token değildir. Host turn süresi5802ms; provider latency ölçümü değildir. Full `read_thread final_answer` otoritedir; `wait_threads` compact summary yine false/null literal'larını kaybetti ve JSON geçersizdi. Summary onarılmadı veya model syntax hatası sayılmadı.

## Kullanım ve sınırlar

Input/output/reasoning/cache/total token ve ücret **unknown/null**. Soft1536 çıktı token hedefi; kesin token/context cap doğrulanmadı. Tek deneme öncesi/sonrası paylaşılmış10080dakikalık kota **%85 → %85 kullanılmış** göründü. Yuvarlanmış ortak hesap metriğinden deneyin sıfır tükettiği veya token sayısı çıkarılmaz; parent/diğer işler de kotayı kullanır. Hesap kimliği ve ham host metadata repoya aktarılmadı.

Üç yeni saved-output regresyonu ham hash'i, tam literal'ları, eksik alanı, iki proje ret gerekçesini, consumed exact permission'ı ve unknown usage'ı korur. **209 semantik /15 karar /40 repo testi** geçti; bu testler başarısız model örneğini doğru reddettiğimizi kanıtlar. Model çıktısını başarılı yapmaz.

## Çıkarım ve sıradaki iş

Prompt'a machine schema yazmak bu native host yolunda zorunlu alan ve bağlam ilişkisine uyumu garanti etmedi. Daha pahalı model veya daha uzun prompt gerektiği sonucuna varamayız. Önceki span dersine benzer şekilde, modelden deterministik olarak bilinen state'i ve altı tipli record'un işleme kuralını tekrar üretmesini istemek ek hata yüzeyi oluşturuyor.

**Önerilen en küçük yerel devam:** mevcut typed/source-bound record'lardan readback ve güvenli işlem taslağını kodla üret; belirsiz record'a soru tahmin etme. LLM yalnız serbest metinden semantik aday çıkarmada veya gerçekten belirsiz anlamda kullanılsın. Bu yeni yolda first raw düzeltilmez; sonuç ayrı köken/sürümle etiketlenir ve bağımsız oracle/negatif senaryolarla sınanır. Böylece aynı bilinen bilgiyi yeniden okuyacak üçüncü model çağrısı yapılmadan bu hata yüzeyi azaltılabilir. Bu rapor generator'ın uygulanmış olduğu iddiasını taşımaz.

Provider tarafından zorlanan schema ile API yolu ayrı test hipotezidir; required-field hatasını azaltma ihtimali semantic yanlış Q_UI bağını tek başına çözmez. Gerçek provider/schema/cost deneyi yapılmadı; API erişimi/ücret izni yok. Yeni harcama veya başka model turn başlatılmadı.

Q03-R6 tamamlandı ve izin tüketildi; artık açık soru değildir. Model/native/gold/ROI/production yatırım T03c kapıları açık, T04 başlamadı. T03 deneme kaydı güncellendi; sayacı azaltmak için yeni bir DONE ana görev üretilmedi. Ana proje konuşmasına parent sohbette devam edilir; trial sohbetine ek prompt gönderilmez.

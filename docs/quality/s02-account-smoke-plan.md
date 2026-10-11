# S02 — Mevcut hesapla sınırlı model smoke deneyi

**2026-10-11 · Q03-R2 A seçildi; paket hazır; gerçek model çalıştırması not_run.** Kullanıcı “burada da önerin ile devam edelim” yanıtıyla hazır S02 sentetik isteğini mevcut LLM hesabında çalıştırma yöntemini seçti. Bu önceki no-model sıra kararını iptal etmez; zorunlu gerçek extraction doğrulamasının sonraki küçük adımıdır. Sağlayıcı/hesap/model henüz seçilmedi. Yeni API harcaması, credit satın alma veya abonelik dışı kullanım yetkisi yoktur.

## Hazır paket ve sınırlar

| Alan | İlk deneye uygulanan sınır | Gerçekte ne denetlenebilir? |
|---|---|---|
| Veri | S02, 11 sentetik mesaj; yalnız hazır source/context/contract | [Kaynak isteği](../../examples/model-smoke/s02-request.json), sabit request/hash; gerçek konuşmalar ve repository yüklenmez |
| İstek | Bir yeni, boş oturumda tek gönderim; bir çıktı | İş akışında kullanıcı denetimi; sağlayıcının iç inference sayısına erişim yok |
| Tekrar | Otomatik/manual retry, regenerate ve “devam et” sıfır | İlk hatalı/eksik çıktı saklanır, başarısız/incomplete olarak ölçülür; ikinci çağrı ayrı sınırlı plan gerektirir |
| Araçlar | Browse, repository, tool/agent, proje memory ve ek dosya yok | Prompt talimatı; host tools gerçekten kapatılamıyorsa coverage/izolasyon sınırı kaydedilir |
| Çıktı | 1536 token uzunluk hedefi; geçerli compact JSON | Prompt hedefi; seçilen hesap arayüzü enforce etmiyorsa hard token cap değildir. Kesilmiş JSON onarılıp başarı ilan edilmez |
| Import | En fazla 128 KiB response; sözleşmenin 64 aday sınırı | Yerel validator tarafından uygulanır; önceden harcanan tokenları geri almaz |
| Para/kota | Dahil mevcut kullanım; ek API spend, credit satın alma veya ücretli aşım izni yok | Hesabın aktif billing/credit modu önceden kontrol edilir. Yalnız dahil kota içinde kalındığı teyit edilemiyorsa gönderim bekler |
| Sonuç | Tek output için smoke; n=1, development family | Release/üstünlük/tasarruf veya human-gold benchmark sonucu değildir |

[Gönderime hazır metin](../../examples/model-smoke/s02-prompt.txt) · [Makine tarafından okunur policy](../../examples/model-smoke/s02-policy.json).

## “LLM hesabında tavan yok” neden yanlış?

Üç ayrı sınır bulunur: bizim deney kapsamımız, provider’ın hesap kotası ve ücret/credit koşulları. Abonelik üzerinden çalışmak sınırsız veya ücretsiz kullanım anlamına gelmez. Mevcut kotadan tüketim olur; plana/arayüze göre ayrıntılı token/usage veya iş başına parasal tavan bulunmayabilir. Veri/byte tavanı, cevap uzunluğu talimatı ve süreyi durdurmak da harcama garantisi değildir. Görünmeyen usage/cost **null/unknown** kalır; sıfır yazılmaz.

OpenAI için [resmî authentication belgesi](https://learn.chatgpt.com/docs/auth) ChatGPT abonelik erişimi ve API key ile usage-based erişimi ayırır. [Resmî pricing belgesi](https://learn.chatgpt.com/docs/pricing) token, plan limiti ve ek credit kullanımını açıklar. Bunlar 2026-10-11'de okundu; seçilmemiş Claude hesabı, kullanıcının mevcut planı veya bu deneye ait tam bedel hakkında kanıt sayılmaz. [Plan usage preview limitleri](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations) örneğinde `max_output_tokens` desteklenmez; aynı kısıt bütün host/arayüzlere genellenmez. “1536 kesin uygulanır” varsayımı bu nedenle yapılmaz.

Gelecekteki otomatik API yolunda kendi call/retry/parent-child rezervasyon ve toplam bütçe admission sınırlarımız gerekir. Provider token/para/usage desteği ayrıca doğrulanır; API kullanmak tek başına hard parasal tavan sağlamaz. Bu deneyde o yol açılmadı.

## Çalıştırma ve ölçüm

1. Owner hesabı/arayüzü seçer; aktif model ve dahil kullanım/credit modu kayıt altına alınır. Mevcut bu sohbet extraction için yeniden kullanılmaz; asistan daha önce oracle/taslak gördü. Yeni bağımsız mesaj geçmişi gerekir; modelden modelin adını tahmin etmesi istenmez.
2. Yalnız hazır metni boş oturuma bir kez gönder. Proje dosyaları ve beklenen cevaplar ekleme; araç/bağlantı açma. İlk ham output’u düzenlemeden, model/arayüz/zaman ve varsa usage ile kaydet. Yeni hesap/bağlantı oluşturma gerekirse ayrıca değerlendirilir.
3. `python3 -B spikes/semantic-chain/experiment.py evaluate --responses /tmp/s02-account-response.json --out /tmp/s02-account-evaluation.json` ile bağımsız scorer çalışır. Output parse/contract hatası varsa failure/incomplete raporu saklanır; fixture/assistant taslağı ile yer değiştirilmez. Henüz bütün corpus değil, tek S02 olduğundan genel sonuç incomplete kalır.
4. Geçerli aday için `python3 -B spikes/semantic-chain/run.py --response /tmp/s02-account-response.json` kontrollü policy/impact/AC zincirini çalıştırır. Trusted receipt ve target hâlâ fixture’dır; gerçek insan onayı/target uygulaması iddiası yoktur. Parse hatasında bu adım yapılmaz.
5. Ham output hash’i, kaynak/prompt hash’i, provider/model provenance ve ölçüm sonucu ayrı kanıtla kaydedilir. Usage görünmüyorsa null; insan gold/holdout/native karşılaştırma kapıları kapanmaz. İlk çıktı sonrası yeni deney kapsamı sonuçtan hareketle hazırlanır.

**Kalan tek başlangıç sorusu:** Mevcut Claude hesabı mı, mevcut ChatGPT/Codex hesabı mı? Bu kayıt yöntemi seçildi diye sağlayıcı, model, yeni thread veya sınırsız veri/credit izni varsaymaz.

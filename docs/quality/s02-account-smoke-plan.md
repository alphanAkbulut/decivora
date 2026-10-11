# S02 — Mevcut hesapla sınırlı model smoke deneyi

**2026-10-11 · Q03-R5 ile ikinci ayrı denemeden gerçek output alındı; strict validator kaynak konumu hatasında reddetti.** [Güncel deney sonucu](s02-second-attempt-result.md). İlk Q03-R4 denemesi `cloudflare_challenge` ile çıktısız kaldı; [tarihsel rapor](s02-account-smoke-result.md). Kullanıcı “burada da önerin ile devam edelim” yanıtıyla hazır S02 sentetik isteğini mevcut LLM hesabında çalıştırma yöntemini seçti. Bu önceki no-model sıra kararını iptal etmez; zorunlu gerçek extraction doğrulamasının sonraki küçük adımıdır. **Q03-R3 A kabul edildi: mevcut ChatGPT/Codex hesabı (OpenAI) seçildi.** Tam arayüz/model ve enforce edilmiş token/context sınırları henüz doğrulanmadı. Yeni API harcaması, credit satın alma veya abonelik dışı kullanım yetkisi yoktur.

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

OpenAI için [resmî authentication belgesi](https://learn.chatgpt.com/docs/auth) ChatGPT abonelik erişimi ve API key ile usage-based erişimi ayırır. [Resmî pricing belgesi](https://learn.chatgpt.com/docs/pricing) token, plan limiti ve ek credit kullanımını açıklar. Bunlar 2026-10-11'de okundu; Claude hesabı veya bu deneye ait tam bedel hakkında kanıt sayılmaz. Mevcut Codex hesabının salt okunur kontrolünde normal kullanımın açık olduğu görüldü; bu gözlem iş başına token/para tavanı veya S02 usage kanıtı değildir. Hesap kimliği ve kişisel kota ayrıntıları repoya aktarılmaz. [Plan usage preview limitleri](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations) örneğinde `max_output_tokens` desteklenmez; aynı kısıt bütün host/arayüzlere genellenmez. “1536 kesin uygulanır” varsayımı bu nedenle yapılmaz.

Gelecekteki otomatik API yolunda kendi call/retry/parent-child rezervasyon ve toplam bütçe admission sınırlarımız gerekir. Provider token/para/usage desteği ayrıca doğrulanır; API kullanmak tek başına hard parasal tavan sağlamaz. Bu deneyde o yol açılmadı.

## Token/context güvenlik kaydı — gönderim öncesi tarihsel durum

Kullanıcının son isteği ayrı input, output ve toplam context sınırları; olağan dışı tüketimde durma/onay bekleme gereksinimidir. [Ürün sözleşmesi](../architecture/routing-token-economy.md) ve [risk davranışı](../product/token-risk-and-approval.md) güncellendi. Bu gereksinim ücret/credit veya daha büyük model izni değildir.

Bu smoke paketinde tam gönderilecek metin **5498 UTF-8 byte** olarak sabittir. Tokenizer/model ve arayüzün eklediği talimat/geçmiş bilinmediğinden bunu kesin input token sayısına çevirmiyoruz. Policy'de `max_input_tokens`, `max_context_tokens` ve `max_total_tokens` henüz **null**; “sınırsız izin” anlamına gelmez. 1536 output hedefi soft; enforce edilmiş output tavanı da null'dır. 128 KiB import kontrolü çağrıdan sonra çalışır, bütçeyi koruyan çağrı öncesi limit değildir.

**Gönderim öncesi zorunlu capability kontrolü:** seçilen model/arayüz, tam input sayımı, output ve context cap desteği, görünür/gizli ücretli token sınıfları, dahil kullanım/overage modu kaydedilir. Kontrol kısmen yapıldı: OpenAI seçildi, normal hesap kullanımı açık; kesin model/input/generation/context üst sınırları doğrulanmadı. Gönderim `pending_capability_review`, execution `not_run`. Hard cap gerekli olup arayüz sağlayamıyorsa otomatik veya manuel gönderim yapılmış sayılmaz; uygun kontrollü yöntem hazırlanır. Prompt'a “en çok şu kadar token” yazmak bu kapıyı kapatmaz. Daha zayıf sınırla manuel smoke ancak insanın açıkça kabul ettiği sınırlı risk istisnasıyla yapılabilir; bu son istek böyle bir istisna kabulü sayılmaz. Seçilmiş A yöntemi iptal edilmedi; kullanılabilirliği kontrol ediliyor. Ücretli API'ye kendiliğinden geçiş yoktur.

S02 için bir gönderim, sıfır retry/regenerate/continuation ve araç/alt agent olmaması korunur. Kesilen/eksik output yeni çağrıyla otomatik tamamlanmaz; failure/incomplete saklanır. Daha büyük context veya ikinci çağrı aynı deneye sessiz eklenmez. Ürün için önerilen sayısal deney profili bu henüz seçilmemiş hesapta uygulanmış tavan değildir.

## Çalıştırma ve ölçüm

Yerel first-use kontrolü artık kodlanmış ve fixture ile sınanmıştır: [token preflight](token-preflight.md). `python3 -B scripts/token_preflight.py --s02` paket hashlerini doğrular; henüz doğrulanmamış kesin model/limit/bütçe için blocked döner ve provider çağırmaz. Bu sonuç gerçek host limiter, parasal rezervasyon veya semantic inference başarısı değildir. Hesap capability incelemesi hâlâ pending.

1. Hesap ailesi seçildi: mevcut ChatGPT/Codex, OpenAI (Q03-R3 A). Kesin arayüz/model ve limit mekanizması engineering tarafından doğrulanır; kullanıcıya aynı sağlayıcı sorusu yeniden sorulmaz. Normal hesap kullanımı açık gözlemi ayrıca alındı; bu deneye özel dahil kullanım/credit koşulu kesin dispatch yönteminde kayıt altına alınır. Mevcut bu sohbet extraction için yeniden kullanılmaz; asistan daha önce oracle/taslak gördü. Yeni bağımsız mesaj geçmişi gerekir; modelden modelin adını tahmin etmesi istenmez.
2. Yalnız hazır metni boş oturuma bir kez gönder. Proje dosyaları ve beklenen cevaplar ekleme; araç/bağlantı açma. İlk ham output’u düzenlemeden, model/arayüz/zaman ve varsa usage ile kaydet. Yeni hesap/bağlantı oluşturma gerekirse ayrıca değerlendirilir.
3. `python3 -B spikes/semantic-chain/experiment.py evaluate --responses /tmp/s02-account-response.json --out /tmp/s02-account-evaluation.json` ile bağımsız scorer çalışır. Output parse/contract hatası varsa failure/incomplete raporu saklanır; fixture/assistant taslağı ile yer değiştirilmez. Henüz bütün corpus değil, tek S02 olduğundan genel sonuç incomplete kalır.
4. Geçerli aday için `python3 -B spikes/semantic-chain/run.py --response /tmp/s02-account-response.json` kontrollü policy/impact/AC zincirini çalıştırır. Trusted receipt ve target hâlâ fixture’dır; gerçek insan onayı/target uygulaması iddiası yoktur. Parse hatasında bu adım yapılmaz.
5. Ham output hash’i, kaynak/prompt hash’i, provider/model provenance ve ölçüm sonucu ayrı kanıtla kaydedilir. Usage görünmüyorsa null; insan gold/holdout/native karşılaştırma kapıları kapanmaz. İlk çıktı sonrası yeni deney kapsamı sonuçtan hareketle hazırlanır.

## Q03-R3 — Hesap seçimi ve kalan tek owner kararı

**2026-10-11 · Kullanıcı A dedi: mevcut ChatGPT/Codex hesabıyla ilerle.** Claude alternatifi bu ilk smoke için seçilmedi; sonraki kıyas kapsamından çıkarılmadı. Model testi zorunludur; bu seçim onu isteğe bağlı yapmaz.

Hard-cap koşulu korunuyor. İncelenen OpenAI SIWC plan kullanım preview yolu `max_output_tokens` desteklemiyor; CLI help de iş başına enforce edilmiş output/para tavanı kanıtı sağlamadı. Bunlar bütün OpenAI arayüzleri için yokluk kanıtı değildir. Bu nedenle mevcut S02 preflight blocked ve execution not_run kalır.

Somut istisna önerisi yalnız bu tek deney içindir: 5498 byte sabit sentetik prompt, bağımsız boş oturum, bir gönderim/ilk çıktı, sıfır retry/tools/subagent; 1536 token soft hedefi; ek ücretli kullanım/credit açılmadan mevcut kotadan tüketim. Kesin input/output/context/reasoning tavanı garanti edilemez. Kesme/timeout veya 128 KiB import kontrolü önceki tüketimi geri almaz. Kullanıcı bu sınırlı riski ayrıca kabul ederse ayrı receipt kaydedilir; ürünün hard-cap sözleşmesi gevşetilmez ve sonraki deneylere genellenmez. Bu öneri Q03-R3 sırasında henüz kabul edilmemişti. **Q03-R4 A ile sonraki insan yanıtı bu tek-deney istisnasını kabul etti**; bir gönderim denendi, host hatasında çıktı alınamadı. İzin tüketildi; ikinci gönderim otomatik değildir.

## İlk denemenin sonucu — Q03-R4 A

Önceki pending_capability_review anlatımı ilk gönderimden önceki strict/hard-cap kapısıdır. Q03-R4 açık insan istisnası yalnız manuel web smoke yolunu yetkilendirdi; hard-cap desteği doğrulanmış sayılmaz. Tek gönderimden sonra `cloudflare_challenge` gözlendi, response ve kullanım verisi alınmadı. Güncel durum policy'de attempted_no_model_output / attempted_retry_exhausted; parse/scorer/chain bu deneme için not_run_no_output. [Sonuç ve sonraki sınırlı plan](s02-account-smoke-result.md).

## Güncel sonuç — Q03-R5

Kullanıcı “tek yeni denemeyi onaylıyorum” dedi. Aynı kapsamla bir yeni gönderim normal Chrome, boş kişiselleştirilmemiş geçici ChatGPT oturumunda yapıldı; bir output alındı, retry 0. Alıntılar 11/11 exact fakat span 10/11 hatalı; evaluator validation aşamasında exit 1 ile durdu, skor/zincir çalışmadı. [Ayrı sonuç/provenance](s02-second-attempt-result.md). Token/cost unknown, strict otomatik preflight blocked ve ürün hard-cap gereksinimi değişmedi. İki ayrı yetkilendirilmiş gönderimin kayıtları korunur; Q03-R5 tüketildi, sonraki inference izni yok. Offline quote→source anchoring adapter deneyi sıradadır.

# S02-002 — Gerçek çıktı, kaynak konumu doğrulamasında ret

**2026-10-11 · Bir yeni gönderim, bir model çıktısı, sıfır tekrar.** Q03-R5 açık insan onayı tüketildi. Model çıktısı geldi; mevcut strict validator reddetti. Semantik skor ve karar zinciri sonucu üretilmedi. [Makine kaydı](s02-second-attempt-results.json) · [Değiştirilmemiş ham çıktı](model-runs/s02-002-response.txt) · [İlk denemenin ayrı kaydı](s02-account-smoke-results.json).

## Ne çalıştırıldı?

Aynı 5498 byte / 11 sentetik mesajlık [hazır prompt](../../examples/model-smoke/s02-prompt.txt), normal Chrome içindeki yeni, boş, kişiselleştirilmemiş geçici ChatGPT sohbetine bir kez gönderildi. UI bu modun bellek, eklenti ve özel talimatları yok saydığını belirtti. Oracle, repo, dosya veya gerçek konuşma aktarılmadı. Araç çağrısı gözlenmedi; provider backend izolasyonu bağımsız doğrulanmadı. Ekrandaki güç seçimi **Hızlı (1 of 3)**; kesin model kimliği unknown. API, yeni hesap, ücretli credit veya abonelik dışı kullanım açılmadı. Gerçek token/para telemetrisi yok: null/unknown, sıfır değil.

İlk deneme ayrı onayla bir gönderim yapmış, `cloudflare_challenge` ile çıktısız kalmıştı. Bu ikinci deneme yeni onayla yapıldı; toplam iki ayrı yetkilendirilmiş gönderim, her birinde sıfır retry. Chrome'da yanıt alınması önceki hatanın kök nedenini tek başına kanıtlamaz.

## Gerçek bulgu ve kapsamı

| Kontrol | Sonuç |
|---|---|
| JSON parse ve request ID | Parse edildi; hazır isteğin ID'si eşleşti |
| Aday sayısı | 11; bu sayı görev sayısı veya tamlık skoru değildir |
| Alıntının kaynak metniyle eşleşmesi | 11/11 alıntı ilgili mesajın tam metniyle aynı |
| Unicode codepoint kaynak konumu | 1/11 geçerli; 7 sınır dışı, 3 sınır içinde fakat alıntıyı kesiyor |
| Mevcut strict evaluator | Exit 1: `ValueError: candidate quote not in source` |
| Bağımsız semantik skor | Çalışmadı; validation bütün batch'i oracle okunmadan reddetti |
| Karar/etki/kanıt/AC zinciri | Çalışmadı; canonical mutation 0 |
| Retry veya ham çıktıyı başarı için değiştirme | Yapılmadı |

| Mesaj | Bildirilen `[start,end)` | Tam metnin codepoint uzunluğu | Sonuç |
|---|---|---|---|
| S02-m01 | [0,46) | 47 | Alıntıyı kesiyor |
| S02-m02 | [0,56) | 53 | Sınır dışı |
| S02-m03 | [0,62) | 59 | Sınır dışı |
| S02-m04 | [0,90) | 89 | Sınır dışı |
| S02-m05 | [0,9) | 9 | Geçerli |
| S02-m06 | [0,50) | 49 | Sınır dışı |
| S02-m07 | [0,79) | 72 | Sınır dışı |
| S02-m08 | [0,60) | 58 | Sınır dışı |
| S02-m09 | [0,83) | 84 | Alıntıyı kesiyor |
| S02-m10 | [0,65) | 61 | Sınır dışı |
| S02-m11 | [0,43) | 44 | Alıntıyı kesiyor |

Bu tablo oracle kullanmayan deterministik kaynak kontrolüdür; precision/recall/F1 veya doğru anlam çıkarımı skoru değildir. S02-m01'de `end=46`, gerçek uzunluk 47; son nokta kesildiği için validator ilk burada durdu. Sonraki kayıtlar ayrı tanısal incelemeyle kontrol edildi. Python slicing sınır dışı end değerini sessiz kısaltır: yalnız `text[start:end] == quote` kontrolü yetmez; `end <= len(text)` de zorunludur. Hataların UTF-8/UTF-16 farkından kaynaklandığı kanıtlanmadı.

Model Q_STORE/B/revision 1 için AnswerRecord önerdi; bu gözlem insan seçiminin doğrulanması veya doğru decision acceptance değildir. Yanlış offset bulunan bütün batch reddedildi. Tek geçerli span diğer adayların doğru anlam/ilişki taşıdığını kanıtlamaz.

## Tekrar üretim

Repo kökünde, ham response üzerinde:

```bash
python3 -B spikes/semantic-chain/experiment.py evaluate   --responses docs/quality/model-runs/s02-002-response.txt   --out /tmp/decivora-s02-002-evaluation.json
```

Beklenen gözlem mevcut kodda exit 1 ve yukarıdaki validation hatasıdır; değerlendirme JSON'u yazılmadı. Bu beklenen ret, test suite'in geçtiği veya model deneyinin başarılı olduğu anlamına gelmez. Ham response/hash, source/prompt hashleri ve mesaj bazlı diagnostic [makine kaydında](s02-second-attempt-results.json) saklandı. Screenshot yerelde tutuldu, GitHub'a hesap/session görseli eklenmedi.

## Öğrenme ve sıradaki iş

LLM'ye codepoint saydırmak güvenilir kaynak bağlama için zayıf bir sözleşme olabilir. Sıradaki insan bağımlılığı olmayan P0 işi: modelin mesaj kimliği + exact quote önerisini kodun kaynakta tekil exact match ile konumlandırdığı ayrı adapter deneyi hazırlamak. Eksik veya birden çok eşleşme varsa abstain/quarantine; fuzzy eşleşmeyle sessiz kabul yok. Orijinal response ve türetilmiş aday ayrı hash/revision/provenance taşır. Mevcut source-binding ve authority validator gevşetilmez. Bu öneri henüz uygulanmadı; düzeltilmiş türev sonuç orijinal modelin strict başarısı diye sunulamaz.

Ardından geçerli türetilmiş adaylar bağımsız scorer ve ayrı trusted-receipt zincirinde ölçülür. Development prompt/adapter seçimi ayrı kaydedilir; human-gold/holdout, native kıyas, production stack ve yetkili gerçek capture kapıları açık kalır. Bu rapor yeni model çağrısı izni değildir. Yeni inference ancak ayrı kapsam/bütçe/izin ile yapılır; offline source/adapter çalışması bunu beklemez.

# S02-002 — Gerçek çıktı, kaynak konumu doğrulamasında ret

**2026-10-11 · Bir yeni gönderim, bir model çıktısı, sıfır tekrar.** Q03-R5 açık insan onayı tüketildi. Model çıktısı geldi; mevcut strict validator reddetti. Semantik skor ve karar zinciri sonucu üretilmedi. [Makine kaydı](s02-second-attempt-results.json) · [Değiştirilmemiş ham çıktı](model-runs/s02-002-response.txt) · [İlk denemenin ayrı kaydı](s02-account-smoke-results.json).

## Ne çalıştırıldı?

Aynı 5498 byte / 11 sentetik mesajlık [hazır prompt](../../examples/model-smoke/s02-prompt.txt), normal Chrome içindeki yeni, boş, kişiselleştirilmemiş geçici ChatGPT sohbetine bir kez gönderildi. UI bu modun bellek, eklenti ve özel talimatları yok saydığını belirtti. Oracle, repo, dosya veya gerçek konuşma aktarılmadı. Araç çağrısı gözlenmedi; provider backend izolasyonu bağımsız doğrulanmadı. Ekrandaki güç seçimi **Hızlı (1 of 3)**; kesin model kimliği unknown. API, yeni hesap, ücretli credit veya abonelik dışı kullanım açılmadı. Gerçek token/para telemetrisi yok: null/unknown, sıfır değil.

İlk deneme ayrı onayla bir gönderim yapmış, `cloudflare_challenge` ile çıktısız kalmıştı. Bu ikinci deneme yeni onayla yapıldı; toplam iki ayrı yetkilendirilmiş gönderim, her birinde sıfır retry. Chrome'da yanıt alınması önceki hatanın kök nedenini tek başına kanıtlamaz.

## Gerçek bulgu ve kapsamı

> [!WARNING]
> **Gözlenen engel: R20 / High / Observed.** Model cevabı → kaynak konumu doğrulaması geçişinde durduk. Karar doğruluğu, görev etkisi veya AC doğrulamasına ulaşmadık. Test suite'in geçmesi bu engeli kapatmaz. Öncelik: T03 source anchoring; production build/kalite kapısı açık.


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

### Ne denedik; tam nerede durdu?

| Deneme | Amaç / yöntem | Durduğu yer | Sonuç ve etkisi |
|---|---|---|---|
| S02-001 | Sabit sentetik prompt, in-app ChatGPT, bir gönderim | Host erişimi; `cloudflare_challenge` | Output yok; backend/token/root cause unknown. [Tarihsel kayıt](s02-account-smoke-results.json) |
| S02-002 | Aynı prompt, normal Chrome, ayrı insan onayıyla bir gönderim | Output import'unda codepoint span kontrolü | Output var; 10/11 span yanlış. Ham çıktı değişmedi; scorer/chain çalışmadı |
| ANCHOR-PROBE-01 | Aynı çıktıda message ID + exact quote için kodla tekil eşleşme; yalnız yerel | Kaynak bağlama teknik fizibilitesi | 11/11 tekil eşleşme; yalnız bellekte türetilen adaylar mevcut validator'dan geçti. Yeni model çağrısı yok; semantik/chain ölçümü yok |

İlk hatanın bilinmeyen kök nedeni ile ikinci denemenin doğrulanmış offset hatası aynı olay değildir. “Tüm ürün ilk adımda çalışamaz” sonucu bu küçük örnekten çıkarılamaz; kullanılabilir model→kaynak bağlantısının henüz teslim edilmediği açık bir engeldir. Modelden hassas sayısal konum üretmesini isteyen sözleşme varsayımını fixture başarıları gerçek kullanımda doğrulamamıştı. Bu varsayım artık R20 olarak görünür; modelin iç nedenini bildiğimizi iddia etmiyoruz.

### Teknik olarak aşılabilir mi?

**Bu örnekte kaynak konumu engelini aşan deterministik yöntem yerelde doğrulandı.** [Probe kodu](../../spikes/semantic-chain/probe_source_anchors.py) yalnız kaynağı ve değiştirilmemiş cevabı okur; oracle/API/tool yok. Modelin önerdiği alıntıyı aynı mesajda exact arar; tek eşleşmede `[start,end)` hesaplar. Boş/eksik/çoklu/örtüşen eşleşme, farklı Unicode normalizasyonu sessizce kabul edilmez. Kodun hesapladığı konum anlam doğruluğu, insan onayı veya task completion kanıtı değildir.

```bash
python3 -B spikes/semantic-chain/probe_source_anchors.py
```

[Probe sonucu](source-anchor-feasibility.json): 11 tekil eşleşme ve mevcut validator'da 11 geçerli türev aday; 7 edge kontrolü (tekil alt metin, tekrar, örtüşen tekrar, eksik, boş, Unicode codepoint, normalizasyon farkı) geçti. Bunlar ayrı script kontrolleridir, root suite test sayısına eklenmez. Orijinal S02-002 hâlâ reddedilir. Türev yalnız bellekte oluştu; production import, karar uygulama veya human-gold benchmark yapılmadı. Kod/kaynak/ham response hashleri ve türev hash'i ayrı kayıttadır; mevcut model raporu değiştirilmedi.

### Riskin kapanması için gerekli işler

1. Probe'u bounded, revision/hash-bound adapter'a dönüştür; orijinal ve türev provenance'ı ayrı tut. Eksik/çoklu eşleşme için gözlenebilir rejection/quarantine; batch davranışı açık olsun.
2. Bozuk envelope, yanlış message/request/revision ve yetki iddiasını bu yolun da reddettiğini negatif testlerle doğrula; mevcut strict validator gevşemesin.
3. Geçerli türev adayları bağımsız scorer ve ayrı trusted receipt ile kontrollü zincirde ölç. Türev skorunu orijinal raw contract skoruyla karıştırma; AI oracle insan gold değildir.
4. Yeni veri üzerinde model/adapter kalite ve maliyetini değerlendir; hata/düzeltme yükü ölçülmeden R20 Closed veya MVP hazır deme. Yeni inference ayrıca izinli olsun.

**Şu an kullanıcı kararı bekleyen bir offline adım yok.** Kodla tekil kaynak eşleşmesi ve negatif testler ücret/veri paylaşımı gerektirmez. Yeni LLM çağrısı/sağlayıcı/ücret, gerçek private konuşma aktarımı, erişim genişletme veya production stack seçimi gerektiğinde somut sınırlarıyla ayrıca owner kararı alınır. Önceki tek gönderim izni tüketildi. Mevcut ürün hard-cap kuralına yeni istisna eklenmedi.


LLM'ye codepoint saydırmak güvenilir kaynak bağlama için zayıf bir sözleşme olabilir. Sıradaki insan bağımlılığı olmayan P0 işi: modelin mesaj kimliği + exact quote önerisini kodun kaynakta tekil exact match ile konumlandırdığı ayrı adapter deneyi hazırlamak. Eksik veya birden çok eşleşme varsa abstain/quarantine; fuzzy eşleşmeyle sessiz kabul yok. Orijinal response ve türetilmiş aday ayrı hash/revision/provenance taşır. Mevcut source-binding ve authority validator gevşetilmez. Bu öneri henüz uygulanmadı; düzeltilmiş türev sonuç orijinal modelin strict başarısı diye sunulamaz.

Ardından geçerli türetilmiş adaylar bağımsız scorer ve ayrı trusted-receipt zincirinde ölçülür. Development prompt/adapter seçimi ayrı kaydedilir; human-gold/holdout, native kıyas, production stack ve yetkili gerçek capture kapıları açık kalır. Bu rapor yeni model çağrısı izni değildir. Yeni inference ancak ayrı kapsam/bütçe/izin ile yapılır; offline source/adapter çalışması bunu beklemez.

## Ek teknik denetim — konum düzeltmesinden sonra kalan belirsizlik

Kullanıcının “her aşamada hata çıkarsa yatırım boşa gider mi?” sorusu için mevcut çıktıda, yeni provider çağrısı yapmadan ayrı bir diagnostic çalıştırıldı. [Ayrı kayıt ve kaynak hashleri](s02-derived-followup.json). Ham S02-002 başarısız sonucu ve önceki probe değişmedi.

- Kodla konumlandırılan geçici türev, `run.py --response` kontrollü zincirinin checkpoint scorer'ından geçti. Burada yalnız AnswerRecord önerisi modelden geliyor; graph, trusted approval, hedef içerik ve AC sonuçları scripted fixture. Otomatik ilişki çıkarımı, gerçek auth/target veya bütün ürün başarısı değildir.
- Aynı S02 türevi bağımsız `evaluate_corpus.score` ile yalnız S02 kaynak/taslak etiketleri üzerinde değerlendirildi: exact kind+span TP=0/FP=11/FN=11; message+kind TP=4/FP=7/FN=7. Model tam mesaj alıntılıyor; etiketler dar phrase span bekliyor. Etiketler AI draft ve insan review bekliyor. Bu sonuç “model hiçbir anlamı anlamıyor” veya insan-gold doğruluk oranı değildir.
- Candidate AnswerRecord ile canonical Decision gibi temsil farkları, türler ve span granularity aynı değerlendirme sözleşmesine bağlanmalı. Eşleme sessizce değiştirilip başarı skoru üretilmedi. Entity/attributes/relations/authority/impact/target/AC doğruluğu bu scorer'da ölçülmüyor.

**Sonuç:** Konum hatasının çözülebilirliği için kanıt var; tüm ürünün güvenilir/ekonomik üretilebilirliği için henüz yeterli kanıt yok. Sıradaki teknik öncelik yalnız adapter değil, candidate/output sözleşmesi ile bağımsız değerlendirme rubric'inin uyumunu sağlamak. Rutin tür/span sözleşmesini engineering hazırlar; insan anlam/karar doğruluğu review'u ayrı kalır. Daha fazla model çağrısı öncesinde bu uyum kontrol edilir. Unit/fixture başarıları production yatırım garantisi vermez.

**Owner'a öneri; henüz seçilmiş bütçe/takvim değil:** Açık uçlu belge ve araştırma yerine kısa çalışan teslimler ve süre/maliyet sınırı olan T03c devam/yeniden tasarım/durdurma kararı. İlk yerel teslim: source anchoring + negatifler + tutarlı scorer; sonraki ayrı izinli teslim: sınırlı yeni örnekte gerçek otomatik karar/görev/ilişki çıkarımı ve düzeltme yükü. Sınır dolduğunda bitmeyen analiz uzatılmaz; kanıt ve kalan riskle owner'a dönülür. Tam vizyon/MVP silinmez; production geliştirmesi bu deneyden başarı çıkmış gibi başlamaz.

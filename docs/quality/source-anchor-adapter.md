# Kaynak bağlama teslimi ve API değerlendirmesi

**2026-10-11 · P0 · Çalışan offline kod.** Kullanıcı 60 dakikalık odaklı geliştirme dilimini kabul etti. Kapsam kaynak bağlama, aday/değerlendirme sözleşmesi ve tekrar kullanılabilir derslerdir. Yeni inference/API harcaması onaylanmadı. Tam ürün vizyonu korunur; genel araştırma ve yeni özellik tasarımı bu teslimin dışında kaldı.

## Sonuç ve kanıt sınırı

| Alan | Bu teslimde ne var? | Ne kanıtlanmadı? |
|---|---|---|
| Kaynak konumu | `anchors.py`: ilgili mesajda tekil exact quote → kodla Unicode konumu; batch atomik, belirsizlikte ret | Her model cevabının doğru alıntı/tür üreteceği |
| Yeni çıktı yolu | Ayrı `decivora-quote-candidates-1`, prompt/contract hash; modelden karakter sayması istenmez | Gerçek model bu yeni contract ile çalıştırılmadı |
| Eski S02 | Açık `legacy=True` ile yalnız 10 offset değiştirilir; 11 aday mevcut strict validator’dan geçer | Ham S02 sonucu başarılı sayılmadı; semantic quality ölçülmedi |
| Değerlendirme | `candidate_eval.py`: message/kind/exact quote/attributes için one-to-one eşleşme | Entity identity, canonical state, authority, graph/impact, hedef ve DoD |
| Güvenlik davranışı | Geç cevap → ayrı onay bekleyen öneri; belirsiz A → eşleşmez; yükledim → claim | Gerçek model bu üç senaryoyu doğru çıkarır mı? |

[Tekrar üretilebilir makine kaydı](source-anchor-adapter-results.json) kaynak/kod hashlerini, raw/türev hashlerini, 10 değiştirilen offset ve üç scripted case sonucunu içerir. **48 semantik suite testi** geçti: mevcut 28 + yeni 20 test. Bunlar fixture/adapter testleridir, 48 gerçek model deneyi değildir. Yeni provider çağrısı 0; bu Codex çalışmasının kendi token/kota kullanımı ölçülmedi.

Orijinal `s02-002-response.txt`, iki gerçek deneme sonucu, önceki probe/follow-up ve corpus oracle’ları değiştirilmedi. Eski strict type/span **0/11** ve message-kind **4/11** draft sonuçları korunur; yeni rubric bu sayıların yerine konulamaz.

## Değerlendirme sözleşmesinin ayrılması

Mevcut corpus oracle’ı bazı mesajlarda **onay ve domain işlemlerinden sonraki** Decision/PendingDecision/Artifact durumlarını bekliyor. Model sözleşmesi ise **yetkisiz aday** çıkarıyor; AnswerRecord’ın Decision’a otomatik dönüştürülmesi yasak. Ayrıca eski scorer dar phrase span isterken model tam mesaj quote döndürdü. Bu granularity farkı strict skoru etkiler. Bu tespit modelin bütün anlam hatalarını açıklamaz.

Yeni candidate rubric ayrı sürümdür: `decivora-candidate-rubric-1`. Beklentiler modelden veya ürün algoritmasından üretilmez; source/request revision’a bağlanır. Dört alanın tamamı exact eşleşir; yanlış option/revision/attribute hem FP hem FN üretir. Tek beklenti birden çok çıktıyla tekrar sayılamaz. Empty output eksikleri gösterir; abstention incomplete kalır. Provisional entity key değerlendirme dışıdır; bu kimlik çözümlemesi için başarı iddiası vermez.

Üç [contract örneği](../../spikes/semantic-chain/fixtures/candidate-contract-cases.json) source, scripted response ve ayrı beklenti alanlarına sahip **authored_draft** mühendislik örnekleridir. Önceki vakalar ve beklentiler bu asistana görünürdü; blind/holdout/human-gold değildir. Bunları canlı kalite benchmark’ı olarak sunma. Eski domain oracle’ına `accepted`/`verified` gibi alanlar yazılabilir; aday rubric’inde bunlar yetki iddiası olduğundan reddedilir. Domain sonuçları ayrı trusted receipt, graph ve observer kontrollerinde ölçülür.

## Çalıştırma ve sınırlar

```bash
python3 -B -m unittest discover -s spikes/semantic-chain -v
python3 -B spikes/semantic-chain/run_anchor_checks.py
python3 -B spikes/semantic-chain/anchor_cli.py prepare \
  --request examples/model-smoke/s02-request.json
python3 -B spikes/semantic-chain/anchor_cli.py derive \
  --request examples/model-smoke/s02-request.json \
  --response docs/quality/model-runs/s02-002-response.txt --legacy
```

`prepare` yalnız packet hazırlar; göndermez. `derive` bir **audit wrapper** döndürür; `response` alanı strict candidate envelope’dur. Mevcut `run.py --response` doğrudan bu alanı içeren ayrı dosya ister; audit wrapper’ı model response diye vermek doğru değildir. `--out` mevcut dosyanın üzerine yazmaz. CLI, 128 KiB’den büyük input dosyasını okumayı durdurur; adapter 32 KiB source/64 message/64 record/128 KiB response sınırlarını ve mevcut 4 KiB attributes sınırını kullanır. Byte tavanı token veya para tavanı değildir.

Kaynakta olmayan, boş, tekrar eden, örtüşerek tekrar eden veya farklı Unicode normalization ile gelen quote reddedilir. Fuzzy eşleştirme yoktur. Aynı quote farklı message ID’lerdeyse her mesaj kendi içinde değerlendirilir. Model yetki/state alanları, duplicate, stale source/prompt/request/contract ve yanlış cevap revision tipi reddedilir. Sadece konum düzeltmek quote’un anlamını doğrulamaz.

## API neyi değiştirir?

Resmî belgeler 2026-10-11 tarihinde incelendi; hesapta API erişimi, kredi, fiyat veya quota sorgulanmadı.

| Gözlenen sorun | API yolunun beklenen katkısı | Kalan iş |
|---|---|---|
| Browser challenge / UI üzerinden kopyalama | Programatik istek browser ekran etkileşimini kullanmaz; bu bir mimari çıkarımdır, bizim bağlantımızda test edilmedi | API auth/ağ/rate/server hataları ayrı ölçülür; Cloudflare’ın bütün API yollarında yokluğu iddia edilmez |
| JSON/alan biçimi | Uyumlu modelde strict Structured Outputs ile desteklenen JSON Schema biçimi denetlenebilir | Bizim örnek `response_contract` henüz provider JSON Schema değildir; uygulama validator’ı korunur. [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) |
| Yanlış kaynak konumu / karar | Konumu kod hesaplar; API bunu kendiliğinden çözmez | Schema’ya uygun çıktı yanlış anlam içerebilir; ayrı candidate/domain rubric gerekir. [Hata sınırı](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses#handling-mistakes) |
| Kullanım ve çıktı tavanı | Usage ve `max_output_tokens` programatik kontrol sağlar | Reasoning ve görünür çıktı toplamına sınır; input/context ve toplam para bütçesi ayrıca. Limitte incomplete veya hiç görünür çıktı olmadan maliyet oluşabilir. [Reasoning/kullanım](https://developers.openai.com/api/docs/guides/reasoning) |
| Tekrarların bütçeyi tüketmesi | Retry sayısı uygulamada açık tutulabilir | İlk pilotta otomatik retry 0; timeout sonrası kullanım unknown ise rezervasyonu sessizce iade etme. Başarısız istekler de dakika limitine katkı yapar. [Rate limits](https://developers.openai.com/api/docs/guides/rate-limits) |

**Öneri:** Sonraki gerçek semantik deney için browser otomasyonu yerine sınırları belirlenmiş API yolu değerlendirmeye daha uygundur. Bu, satın alma/stack kararı veya çalıştırma izni değildir. Sağlayıcı/model, gönderilecek source-only örnekler, input/output/context/run bütçesi ve parasal tavan birlikte sabitlenmeden dispatch açılmaz. Refusal, incomplete, transport error ve unknown usage başarı veya ücretsiz çağrı sayılmaz. Provider’ın şema garantisi domain doğruluğu garantisi değildir.

## Bu teslimde görülen geliştirme hataları

- Yeni Unicode testinin ilk elle yazılan beklentisi 10 yerine 9 olmalıydı; karakterler manuel sayılarak test düzeltildi. Algoritmanın beklenen değeri üretmesine bağlanmadı.
- Yeni integration testinde seed çağrısı yanlış fixture rolüyle denendi; mevcut policy’nin yetkili `human` rolüyle doğru fixture kuruldu. Policy gevşetilmedi.
- Audit wrapper doğrudan eski chain runner’a verildiğinde envelope reddi görüldü; doğru `response` alanı ayrı dosyaya aktarılıp kontrollü zincir passed oldu. Runtime validator gevşetilmedi.

Bunlar geliştirme/komut sözleşmesi düzeltmeleridir; önceki n=1 gerçek model denemesi veya yeni semantic accuracy sonucu gibi sayılmaz. Son test koşusunda tüm 48 test geçti.

## Sıradaki yatırım kapısı

Bu local engel için yeniden genel araştırma gerekmiyor. Yeni quote-only contract üzerinde **yetkili, kullanım ölçülen gerçek inference**, insan incelemeli candidate/domain beklentileri ve yeni örneklerde anlam/yanlış karar testleri sıradadır. Graph ilişkileri ve etki analizi modelden henüz çıkarılmadı. Gerçek host/target, native karşılaştırma ve production stack kapıları açık. R20 yalnız bu adapter testiyle Closed olmaz. Sonuç yetersizse düzeltme kapsamı/bütçesi belirlenir veya native/extension/durdurma seçeneğine geçilir; süre otomatik uzatılmaz.

Tekrar kullanılabilir çalışma yaklaşımı: [kanıta dayalı geliştirme rehberi](../governance/evidence-first-development.md).

## Takip kanıtı ve regresyon kontrolleri

- 39 root testi geçti; tracker HTTP testleri localhost socket izniyle çalıştırıldı. İlk sandbox koşusundaki socket izin hataları uygulama arızası değildi.
- Tarihsel 91-test raporu README hash'ini de içeriyor. Semantik README güncellendiği için tracker bu eski snapshot'ı stale gösterir; bu yeni bir runtime test başarısızlığı değildir. Eski kanıtı güncelmiş gibi göstermek için hash/rapor değiştirilmedi. Test fixture'ı geçici kopyada güncel hashlerle hazırlanır; README değişikliğinin stale kalmasını sınayan ek test var.
- Yeni adapter için ayrı hashli sonuç mevcut. Doküman/link/anchor ve türetilmiş progress eşleşmesi geçti. Ana task ve risk kapıları açık kalır.

# RECEIVER-002 için bağımsız proje incelemesi

**2026-10-13 · T03z / P0, yerel kod teslimi.** Kabul edilmiş Q14-A davranışı yeni receiver wire-2 isteğine bağlandı. Bu çalışmanın amacı hazırlanmış yeni çıktıyı eski wire-1 kimliğiyle onarmadan inceleyebilmektir. Çalışan ürün UI/IAM veya yeni model sonucu değildir.

## Ne tamamlandı?

[`project_review_next.py`](../../spikes/semantic-chain/project_review_next.py) mevcut v2 request doğrulayıcısını kullanır. Caller'ın güncel source/state/access binding fixture'ı, bütün proje kimlikleri ve package digest'leri herhangi bir taslak gösterilmeden denetlenir. Teknik çıktı hatası yalnız kimliği doğrulanmış proje içinde ayrı tutulabilir.

| Durum | Bağımsız proje | Sorunlu proje | Sonuç |
|---|---|---|---|
| Revision string veya kaynak dışı action | Geçerli taslak korunur | Teknik hata; ham alan değiştirilmez | `partial_review` |
| Bilinen soru ve ayrı belirsiz cevap | Geçerli taslak korunur | Bilinen Q_UI + ayrı açıklama kaydı | `needs_clarification` |
| Temiz abstain / eksik output | Geçerli taslak korunur | `awaiting_context` / `missing_output` | Başarı sayılmaz |
| Aynı atomic group içinde bekleyen üye | Taslak gösterilmez | Taslak gösterilmez; açıklama kaydı korunur | `blocked_atomic_group` |
| Envelope, kimlik, yetki veya snapshot bozuk | Hiçbir taslak gösterilmez | Hiçbir taslak gösterilmez | Global ret |

Raw hash orijinal metne bağlıdır. Satır doğrulama zarfında aynı wire-2 formatı, request ID ve satır alanları korunur. V1 raw bu yola verilirse reddedilir; v1 ID/format yeniden yazılmaz. Eski [`project_review.py`](../../spikes/semantic-chain/project_review.py), ilk model çıktısı ve bütün tarihsel scorer/kanıtlar değişmedi.

## Doğrulama ve kullanım

14 yeni test: mixed type/source/false approval/false verification/duplicate answer, missing/abstain, global envelope/foreign identity/stale package, access-before-parse, stale/incomplete caller snapshot, overlapping atomic group, immutable raw, deterministic output ve eski gerçek v1 raw reddi. Bütün semantik suite **206 test** geçti; karar zincirinin **15**, repo/takip testlerinin **40** testi geçti. Testlerde bağımsız authored beklenti yalnız kontrollü valid input olarak kullanılır; model anlam doğruluğu ölçümü değildir.

```sh
python3 -B -m unittest discover -s spikes/semantic-chain -p test_project_review_next.py -v
python3 -B spikes/semantic-chain/project_review_next.py --request examples/receiver-next-smoke/request.json --response <saved-wire-2-response.json> --context examples/receiver-next-smoke/review-context.fixture.json
```

[`review-context.fixture.json`](../../examples/receiver-next-smoke/review-context.fixture.json) yalnız sentetik caller snapshot'ıdır. Model cevabından erişim/onay üretmez; gerçek auth servisi değildir. Açıklama descriptor'ı mevcut source-bound üreticiyle paylaşılır; wire-2 için geç cevap uygulama/kalıcı Inbox veya host teslim mekanizması bu teslimde eklenmedi.

**Review uygunluğu ≠ kalite skoru.** Katman `quality_scored:false`, `canonical_mutations:0`, `model_dispatches:0` döndürür. Tam deney kalite scorer'ı [`receiver_next.py`](../../spikes/semantic-chain/receiver_next.py) bütün çıktı için strict kalır; bir satır başarısızsa geçerli alt parçayı genel başarılı model run diye sunmaz. Eksik next-action recall'ı review kabulüyle ölçülmüş olmaz.

Yeni model/API/target erişimi yok. RECEIVER-002'nin prompt/request/schema/oracle/manifest hazırlık snapshot'ları aynı; yeni context yan dosyası inference prompt'una eklenmez. Sonraki [RECEIVER-002 actual run](receiver-002-result.md) iki satırda da ret verdi; Q03-R6 kabul edildi/tüketildi, artık yanıt beklemiyor. Human gold/native/ROI/production stack T03c kapıları kapanmadı; T04 başlamadı.

## Ana işleri bitirmek için kalanlar

| Ana iş | Tamamlanan bağımsız bölüm | Kapanışa kalan bağımlılık |
|---|---|---|
| T01 | Source/span/split ve dört sınırlı insan davranış incelemesi | Exact etiket incelemesi, adjudication, ayrılmış holdout |
| T02 | Capture fixture düzeneği | İzinli gerçek coding yüzeyinde capability/version/coverage kontrolü |
| T03 | Typed çıkarım, controlled chain, source-bound resume ve wire-2 review kodu | Yeni gerçek receiver ölçümü; native/ROI karşılaştırması; owner yatırım/stack kararı |
| T04–T24 | Uygulanabilir MVP görev ve AC planı | T03 kararından sonra üretim iskeletinden başlayacak sırayla uygulama |
| T25–T30 | Tam vizyondaki sonraki faz planı | MVP kabulü; erken bitmiş gibi sayılmaz |

Bu teslim 27 ana To Do'yu yapay olarak azaltmaz. T03z küçük kod işi DONE; T03 ana kabul koşulları hâlâ açık. Genel “devam” yeni model run izni veya production stack seçimi diye yorumlanmaz.

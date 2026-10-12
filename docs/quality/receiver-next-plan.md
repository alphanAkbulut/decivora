# RECEIVER-002: makine şemalı yeni istek

**2026-10-13 · T03y / P0 hazırlık DONE; gerçek model deneyi not_run.** [Önceki başarısız ilk çıktı](receiver-001-result.md) korunur; yeni request kimliği, wire formatı ve scorer ayrı. [İncelenebilir paket](../../examples/receiver-next-smoke/README.md) · [Yerel hazırlık kanıtı](receiver-next-preparation-results.json).

## Neyi değiştirdik?

| Alan | RECEIVER-001 | RECEIVER-002 hazırlığı |
|---|---|---|
| Model çıktısı sözleşmesi | Alan açıklamalı örnek descriptor | Type/required/additionalProperties/oneOf/const/enum/minimum taşıyan makine schema |
| Wire / request | `decivora-receiver-review-1`, önceki identity | `decivora-receiver-review-2`, ayrı identity |
| Talimat | Ambiguity, abstain ve record/action sınırları yeterince anlaşılmadı | Bilinen soru korunur; ayrı ambiguous record status ok içinde clarification bekleyebilir; whole-project abstain yalnız null/[] |
| Quote ve source | Aynı metin source/candidate/record içinde tekrarlandı | Sekiz exact source mesajı birer kez, record/candidate bilgisi message ID ile birleştirildi; model karakter saymaz |
| Prompt bytes | 7950 | **8089**; +139 byte, token tasarrufu iddiası değil |
| Boyut tavanı | Offline8192byte, hardtoken/context unknown | Aynı8192byte;103byte pay, truncation yok; hardtoken/context unknown |
| Model sonucu | Invalid contract, scoresunscored | **not_run**, örnek/scorer hazırlığı tamamlandı |

Yeni schema iki `ok`/`abstain` dalını projeler arasında paylaşır. Proje ve package değerleri enum, eşleşmeleri source guard'da ayrıca kontrol edilir. Bu yüzden schema şekli geçse bile yanlış proje/package çiftine izin verilmez. Boolean verification/real approval false, upload observed_verified yasak; Evidence not_run başarılı teste dönüştürülemez. Source ve enum sınırları, duplicate answer/test/action, stale selection ve future-plan action retleri çalışır.

## Source-only sınırı ve hermetik hazırlık

Hazırlayıcı yalnız şu üç dosyayı okur: frozen önceki source request ve N01/N02 readable view. Önceki request SHA-256 sabittir; okunmuş source view byte hash ve içerikleri request'e karşı kontrol edilir. Yeni projection, source snapshot ve schema template hash'leri request identity'ye bağlanır; yeni schema const request ID bunun ardından yazılır. Self-hash tek başına yetmez: saved request, güncel seçilmiş source ile yeniden hazırlanıp karşılaştırılır.

**Tespit:** Önceki `receiver_smoke.prepare` exporter'ın `compare_compact_resume.compare` fonksiyonuna gidiyordu; bu fonksiyon encoder'dan sonra bağımsız resume checklist'ini okuyup score üretiyordu. Checklist yeni model prompt'una konmuş değildir; bundan etiket sızıntısı/ilk run sonucu değişimi çıkarılmadı. Yeni hazırlayıcı bu değerlendirme bağımlılığını kullanmaz.20 testten biri tüm file read'lerini yukarıdaki üç kaynakla sınırlar; yeni/önceki oracle veya exporter scorer okuması testte reddedilir. Eski kod ve rapor sonradan onarılmadı.

Sekiz source message'ın text/actor/revision'ı, tüm fixture state, soru sunumları,6 preserved record kind/attributes/answer_status ve coverage korunur. Quote eşitliği bu iki fixture'da tüm message metnidir; subquote desteklenmiyorsa açık ret, sessiz kaynak kaybı yok. Model input'u projections + schema +rules'tur; full binding/source sidecar yerel request dosyasında. Expected.json, rapor, manifest, erişim credential veya parent sohbet prompt'a eklenmez. Status etiketleri önceki source-bound resume'nin mevcut gerçekleridir; bu yeni extraction discovery testi değildir.

## Çalışan yerel scorer ve ölçülmeyenler

`receiver_next.py evaluate` önce source/prompt/schema/type doğrular, sonra ayrı `authored_draft` oracle'yı okur. Readback checkpoint ile altı next-action skorunu ayrı üretir; eksik proje/clean abstain incomplete, eksik işlem failed_draft. Schema/source hata durumunda raw onarılmaz, model sonucu invalid contract olarak raporlanır. Hazırlık raporunda oracle'dan kopyalanmış scripted positive yalnız scorer wiring kontrolüdür; actualmodelruns0/goldfalse. Beklenen sonuçları model algoritması üretmedi; source kimlikleri dışında ayrı elle yazılmış taslak.

**192 semantik /15 karar /40 takip testi geçti;20 semantik test yeni.** Saved hash/no-overwrite, foreign/duplicate/schema/source, type/abstention, current question vs ambiguity, stale/future/false verification, budget/no truncation ve oracle/file read sınırları. Prompt/expected/readback schema pinned; tokenizer kurulu değil, token/para/ROI null. Schema interpreter yalnız mevcut dar keyword kümesi; genel standard conformance ve provider schema acceptance not_run.

Bu evaluator **bütün deney çıktısı için strict kalite kapısıdır**, ürün Q14-A review politikası değildir. Önceki T03x wrapper v1 input'uyla aynı kalır; v2 wire'ı onun içine ID/format değiştirerek sokmayız. Yeni gerçek run'da row diagnostics ve gerekiyorsa v2 review bağlama ayrı sürümlü iş olarak hazırlanır; primary trial skorunu başarılı alt parça seçerek değiştirmeyiz. Product UI/durable Inbox/IAM/host resume/atomic graph üretimi henüz yok.

```sh
python3 -B spikes/semantic-chain/receiver_next.py prepare
python3 -B spikes/semantic-chain/check_receiver_next.py
python3 -B -m unittest discover -s spikes/semantic-chain -p 'test_receiver_next.py' -v
```

Bu komutlar model/network/target erişimi yapmaz. Prepare response/expected parametresi kabul etmez; CLI mevcut output dosyasını overwrite etmez. Prompt-only schema modelin uyması istenen sözleşmedir, provider-enforced JSON output değildir.

## Hazır tek-run önerisi — yetki verilmedi

| Alan | Öneri / mevcut durum |
|---|---|
| Yeni deney | RECEIVER-002-PROPOSED; actualsubmissions0/outputs0 |
| Yöntem | Ayrı yeni native projectless Codex sohbeti; configured GPT-6 Luna / Low, önceki host/model önerisiyle tutarlı |
| Gönderilecek veri | Yalnız exact8089-byte prompt;2 synthetic proje/8 mesaj/schema. Oracle/parent repo/history yok |
| Sınır | Tek başlangıç turn/ilk full final output; retry0/follow-up0/tools0/subagents0/paidAPI0 |
| Çıktı hedefi | Soft1536token; kesin output/context/token/para cap doğrulanmadı |
| Hesap kullanımı | Mevcut üyelik kotasını tüketebilir; shared quota snapshot exact trial token/cost değildir |
| Backend / context | Configured model actual backend kanıtı değil; host/global talimatlar enjekte edilebilir. Tamamen steril context garanti edilmez |
| İzin | **Bekliyor.** Önceki tek-run izinleri tüketildi; “projeye devam” yerel hazırlık yetkisidir, yeni sınırsız model run izni değildir |

Manifest/request hazırlık snapshot'ı aynı kalır; izin ve actual run ayrı request/hash bağlı kayıtta tutulur. İzin gelirse exact prompt hash kaydedilip tek send yapılır. Full final message ham otoritedir; compact wait summary değildir. Tool kullanımı/extra context, refusal/incomplete, modelconfig/usageunknown ve ilk failure görünür raporlanır. Failed output onarılmaz veya otomatik bir sonraki denemeyle değiştirilmez. Değiştirdiğimiz request/schema yeni hipotezdir; başarı garantisi veya tüm ürün build/ROI kapısının kapanışı değildir.

# Yerel receiver sözleşmesi örnekleri

**P0, sentetik development verisi.** Yeni model çağrısı yok. [Amaç, kurallar ve sınırlar](../../docs/quality/receiver-contract.md).

- `response.schema.json`: mevcut frozen request/project/package kimliklerine bağlı makine shape sözleşmesi. Genel standard/provider conformance not_run; sınırlı yerel interpreter ve ayrı kaynak guard'ı çalışır.
- `valid-review.json`: elle yazılmış geçerli review; source-only hazır fixture'a bağlı, oracle/model output'tan kopyalanmadı. İnsan gold veya model başarı kanıtı değil.
- `invalid-reviews.json`: altı ayrı yanlış yapı/bağ örneği ve beklenen ret türü; testlerde okunur.

Kaynak request [önceki hazırlık klasöründe](../receiver-smoke/request.json) kalır; hash/id değişmedi. Yeni schema eski model prompt'una sonradan eklenmiş sayılmaz. Yeni guard semantik sürümü `receiver-source-guard-1`, eski evaluator ayrı tutulur. Başarı yalnız yerel sözleşme kontrolü; `response_coverage_complete` ürün tamamlanması değildir. Örneklerin önerdiği işlemler çalıştırılmaz.

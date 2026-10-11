# Quote-only API deney paketi

**2026-10-12 · P0 / T03 · Offline teslim.** `provider_packet.py` ve sekiz yeni test; semantik suite toplam **56 test geçti**. API gönderimi, model doğruluğu veya production ürün teslimi değildir. [Hazır paket](../../examples/model-smoke/s02-quote-api-draft.json) source-only S02 verisinden üretilir; eski request/prompt/policy ve gerçek deneme sonuçları değişmez.

## Ne kodlandı?

1. Responses API biçiminde strict JSON Schema taslağı: sabit request/contract kimliği, izinli kaynak mesajları/türler, quote ve provisional entity. Karakter konumunu model saymaz.
2. Kaynağı değerlendirme beklentilerinden ayıran paket hazırlayıcı. Model input'una yalnız request/contract/source/allowed kinds girer; rubric/oracle veya geçmiş izin policy'si girmez. Açıkça seçilmiş source context kaybolmaz.
3. Saved API response importer: completed tek assistant output text işlenir. Refusal ayrı; incomplete/failed, tool call, çoklu metin ve malformed veri başarı sayılmaz. Geçerli adayların domain state'i değiştirmesine izin verilmez.
4. Açık unresolved manifest: model, token/context/para tavanları, capability, veri/onay referansı null/pending; retry 0, tools/subagents kapalı. **Manifest onay/rezervasyon/rate limiter değildir; bu kod gönderim yapamaz.**

[Paket/kod hashleri](quote-api-package-results.json) sonucu tekrar üretmek içindir. Önceki 48 semantik test korunur; sekiz yeni test source binding, schema alanları, raw preservation, nested yetki retleri, inner JSON, stale contract, eksik/ret/çoklu çıktı, unknown usage ve CLI overwrite korumasını sınar. Beklenen model çıktıları test fixture'ıdır; gerçek model kalitesi ölçülmedi.

## Wire ile domain sözleşmesi ayrımı

Yeni `decivora-quote-wire-1`, existing quote adapter'ı değiştirmeden `attributes_json` string taşır. Strict object şemasının key'leri sabittir; eski aday attributes serbest JSON object olabilir. Bu **P0 transport tasarımıdır**, kabul edilmiş production API değildir. Inner JSON ayrıca 4 KiB, duplicate/nonfinite/type ve nested authority kurallarından geçer. Arbitrary JSON'u string'e koymak iç anlamı schema garantisinin dışına bırakır; token/escaping yükü getirir. Bu yük henüz ölçülmedi. Typed attributes tasarımı sonraki runtime kararıdır; ürün kabiliyetini bu geçici taşıma biçimine daraltma.

Decode yalnız attributes string → aynı JSON object ve exact quote → span dönüştürür. Tür/seçenek/gerekçe anlamı düzeltilmez. `wire_raw_sha256` orijinal metni, adapter `raw_sha256` decoded envelope'u işaretler; hashler aynı şey değildir. Candidate contract eski adapter source/prompt kimliğine; ayrıca package/payload/transport hashleri yeni provider talimatına bağlıdır. Saved response import kimlik kontrolü sağlayıcıdan gerçek çalıştırıldığı kanıtı değildir. Gerçek run kaydı approved package digest, model, dispatch/request ID, usage ve tarih bağını ayrıca taşımalıdır.

## Çalıştırma

Repo kökünde, model çağrısı olmadan:

```sh
python3 -B spikes/semantic-chain/provider_packet.py prepare --request examples/model-smoke/s02-request.json
python3 -B -m unittest discover -s spikes/semantic-chain -v
```

Saved provider response için:

```sh
python3 -B spikes/semantic-chain/provider_packet.py import --request examples/model-smoke/s02-request.json --response /tmp/saved-response.json --out /tmp/import-audit.json
```

Örnekteki saved response mevcut dosya olmalıdır; komut onu üretmez veya provider'a bağlanmaz. Audit çıktısının `derived.response` alanı candidate envelope'dur; bağımsız rubric `candidate_eval.py` ile ayrıca değerlendirilir. `candidate_validated` semantik başarı, insan onayı, domain tamamlanması veya güvenilir provider provenance demek değildir. CLI parse hatasında nonzero çıkar; bazı response retleri audit status olarak yazılır, CLI exit 0 bunlarda extraction başarısı değildir.

## Bütçe ve kalite kapıları

Model/`max_output_tokens` null olduğundan payload **gönderilebilir istek değildir**. `store:false` API request önerisidir; bütün provider retention politikasını sıfırladığı iddia edilmez. Token sayımı tam instructions + source + schema + framing'i kapsamalı; byte sayısını token tavanı sayma. Mevcut [token preflight](token-preflight.md) ayrıca bounded trusted snapshots ister; bu paket onun sayısal input'unu henüz üretmez. Usage saved response'dan raw/unverified korunur, absent null; sıfır kabul edilmez, harcama rezervasyonu çözülmez.

Gerçek test için sırasıyla: model/capability ve fiyat doğrulama → independent candidate/domain expectation insan review → seçili veri ve tam package digest → input/output/context/run/para tavanı → somut dispatch onayı → tek çağrı/retry 0 → kaynak/anlam/yetki/graph/hedef/AC ayrı ölçüm. Otomatik anlam çıkarımı test edilecek; seçenek bunun yapılması değil yöntemi ve sınırlarıdır. Aynı S02 development örneği n=1 kalite kanıtı veya sealed holdout değildir.

## Kaynak ve bu turdaki düzeltme

Resmî [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) 2026-10-12 tarihinde kontrol edildi: Responses `text.format`, `strict`, required object keys ve `additionalProperties:false` örüntüsü kullanıldı. Gerçek model/provider şema kabulü test edilmedi; şema doğruluğu anlam doğruluğunu sağlamaz.

İlk yerel editte mevcut `experiment.py` adının kullanılması import regresyonu yarattı. Yeni kod `provider_packet.py` olarak ayrıldı; eski dosya immutable GitHub blob'undan byte-for-byte geri getirildi (`09f7ee453a8d4edce37fcc0cc7000575c6ab0223`). Sonraki 56-test suite geçti. Eski işlev veya kalite kontrolü gevşetilmedi. Ders: yeni modül yazmadan mevcut dosya/isim çakışmasını kontrol et.

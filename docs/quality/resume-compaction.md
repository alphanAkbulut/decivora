# Devam paketi tekrarı azaltımı — RESUME-COMPACTION-001

**2026-10-12 · T03t scoped DONE / P0.** Deterministik, kayıpsız tablo codec'i ve kodla çözülen okunabilir görünüm. Yeni model çağrısı/paid API yok. [Makine ölçümü](resume-compaction-results.json) · [Altı örnek](../../examples/resume-compact-smoke/README.md) · [Önceki tam dosya kıyası](resume-file-comparison.md).

## Sorun, uygulanan çözüm ve seçim sınırı

Tam pakette aynı source quote, candidate nesnesi ve project/request/source namespace birkaç kez yer alıyordu. **Anlamsal özetleme veya kaynak silme yapmadık:** exact redundant metadata ortak scope'a taşındı, quote source-message + Unicode span'dan, answer candidate ise record_index'ten çözülür. Provisional entity_key/attrs/kayıt sırası/duplicate ayrımı/soru revision/state/coverage/boundaries aynı kalır. Proposal binding'in ortak alanları namespace/state'ten geri oluşturulur, eski proposal digest'i doğrulanır.

Yeni `resume_compact.py` mevcut v1 builder ve collector'ı kullanır; `resume_package.py`, frozen önceki exports, source/raw/rubric ve eski kanıtlar değişmedi. Bu ayrı P0 encoding sözleşmesi `decivora-resume-compact-fixture-1`; production API schema/ADR veya ürün release'i seçimi değildir. Git geçmişi yerine doküman v2/v3 kopyası oluşturulmadı; iki deney örneği ayrı kanıt kapsamıdır.

## Boyut ve bilgi koruma sonucu

| Grup | Önceki tam resume | Kayıpsız compact resume | Byte azalması | Okunabilir görünüm |
|---|---:|---:|---:|---:|
| N01 | 5.385 | 3.673 | %31,79 | 3.265 |
| N02 | 5.750 | 3.726 | %35,20 | 3.110 |

UTF-8 byte ölçümü son newline dahil. Aynı bilgiyle simple-file core da N01 4.731→3.005, N02 5.101→3.063 byte oldu. Basit dosya aynı codec/guardları kullanabilir; bu ürün üstünlüğü kanıtı değildir.

Compact paket ve compact simple-file **frozen önceki tam core'u birebir yeniden oluşturdu**; tüm record/attrs/source/messages/state/coverage/boundaries alanları eşleşti. Kendi encode/decode roundtrip'ine ek olarak bağımsız önceki export dosyaları karşılaştırıldı ve source/state binding'i yeniden doğrulandı. Değişmemiş authored `resume-checkpoints.json` output'lar üretildikten sonra okundu; compact paket, simple-file ve okunabilir görünüm üçünde de checklist geçti. Eski/current/ambiguous, question pending, verified false, upload claim/not_run korundu.

**Token, para, receiving-model accuracy ve kullanıcı düzeltme süresi ölçülmedi.** Byte azalması token tasarrufu oranı değildir; JSON anahtarları, tokenizer, reader formatı ve tekrar-getirme maliyeti ayrıca ölçülmeli. Native/fresh-session model deneyi not_run; yeni model/selection/paid API/canonical mutations 0.

## Ortaya çıkan gri nokta ve uygulanan önlem

Kayıpsız codec doğru çalışsa bile genel alıcı LLM'in `record_index` veya karakter konumunu doğru çözmesi garanti değildir. Daha önceki offset hatasının başka katmanda tekrarlanmasını istemiyoruz. **Karakter sayma ve tablo çözme işi koddadır.** `render_readable` actual source'tan literal quote'ları üretir; view'a start/end veya quoted metin için çözülmesi gereken tablo konumu verilmez. Cevap status'u ve kaynak mesaj ID'si açık kalır. Geliştirmede ilk readable taslak cevap için record_index kullanıyordu; bu da alıcıdan ilişki çözmesini isteyebilirdi. Yayımlamadan önce message_id + literal quote + attributes + status inline olacak şekilde düzeltildi, negatif test eklendi. Compact kayıpsız paket/actual checklist değişmedi; yalnız readable export ve yeni code hashleri güncellendi.

Makine codec'ini ve model-visible context'i aynı saymayız. Okunabilir görünüm seçili tüm mesajları, context/question presentations, current fixture state/AC/evidence, source-bound records, answer status, coverage ve safety boundaries taşır. Provisional IDs, span ve proposal ayrıntıları kayıpsız sidecar'dadır; view tam archive değildir. Checklist geçmesi alıcı modelin gerçek bir göreve doğru devam ettiğini kanıtlamaz. Gerçek model testi bu **okunabilir view** ile hazırlanacak; LLM'e karakter saydıran yol kullanılmayacak.

## Kontroller ve açık sınırlar

- **Tüm kaynak inline:** Tekil message ID ve request/source/context hash bağı korunur. Eksik/değişmiş kaynak, bozuk Unicode span, foreign namespace, duplicate source veya missing/repeated/boolean/out-of-range record reference reddedilir. Dış kaynağı fetch etmez veya erişilebilir varsaymaz.
- **Sessiz kayıp yok:** Canonical candidate kimliği ve zero-mutation kontrol edilir; bütün AnswerRecord'ların tablo referansı bulunmalı. Bilinmeyen schema/foreign metadata veya lossless mismatch ret olur. Quote onarılarak source hatası gizlenmez.
- **Copy/export freshness:** Digest'e tek başına güvenilmez; aynı current request/response/access/state'ten compact paket yeniden üretilir. Değişen state/access revision, revocation ve rehashed verified tamper ret. `render_readable` authorization değildir; caller önce `validate_before_export` çağırmalıdır.
- **Yetki ayrımı:** Source/actor/model status ≠ authenticated approval. Collector/codec/view karar, impact veya verification uygulamaz. Fixture state gerçek user project state'i değildir; production ACL ve çok-kullanıcılı atomic export gate açık.
- **Byte sınırı:** 32 KiB offline ceiling ve caller'ın küçük sınırı newline dahil kontrol edilir; compact veya readable sığmazsa context_incomplete, metin/paket yok. Kaynak sessiz kesilmez. Bu pilot önceki full builder'ın global preparation ceiling'ini bypass etmez; huge-source chunking ayrı iş.
- **Decode ≠ trust:** Standalone decoder yalnız yapısal/source-table doğruluğunu sağlar; decoded status'u canonical receipt/approval diye kullanma. Güncel authorized snapshot ile reconstruction kapısı hâlâ zorunludur. Private export'un başka araca yapıştırıldıktan sonra geri alınabildiği iddia edilmez.
- **Karşılaştırma scope'u:** İki synthetic current-question fixture, aynı archived MEMBERSHIP-003 çıktı ve aynı development checklist. İnsan gold/blind holdout veya tam hafıza/çoğul soru engine başarısı değil.

## Test ve yeniden üretim

**121 semantik test / 11 yeni test geçti.** Unicode exact quote/full reconstruction; missing inline source/context; invalid table/span/foreign reference/override; unknown schema/duplicate source; stale source/state/access/response; rehashed verification tamper; exact byte/no-truncation; frozen artifact + unchanged semantic checklist + byte reduction; CLI no-overwrite/no-partial; readable literal quotes/safety/byte ceiling; candidate identity corruption kapsamı.

```sh
python3 -B spikes/semantic-chain/compare_compact_resume.py
python3 -B spikes/semantic-chain/compare_compact_resume.py --out /tmp/decivora-compact-new.json --export-dir /tmp/decivora-compact-new
python3 -B -m unittest discover -s spikes/semantic-chain -p test_resume_compact.py -v
```

Altı yeni export text'i JSON'dan yeniden okunarak kontrol edilir; eski full dosyalar yeni generator'la overwrite edilmez. Kod/input/frozen-artifact/checklist hashleri sonuçta; temp SQLite fixture'ları temizlenir. Önceki Mermaid source'ları değişmedi; yeni diagram/render testi yapılmadı.

## Sonraki iş

Gerekli **gerçek fresh-session davranış testi** için iki okunabilir view'dan bounded source-only provider request, ayrı readback/next-action beklentileri ve saved-output evaluator hazırlanmalı. Beklentiler prompt'a oracle olarak konmamalı; source facts ile model başarı kriteri ayrılmalı. Bu hazırlık ücret/model çağrısı gerektirmez. Exact prompt/veri/byte/tek-send/retry/unknown hard-cap sınırı hazır olduğunda kullanıcıdan yeni somut test onayı alınır; önceki tek-send yetkileri tüketildi. Native/user burden/genel token ekonomi ve production yatırım T03c açık kalır.

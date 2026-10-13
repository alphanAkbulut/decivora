# Geç cevabın kalıcı bekleyen kayda bağlanması

**2026-10-13 · T03ac / P0, küçük kod teslimi DONE.** [`reply_store.py`](../../spikes/semantic-chain/reply_store.py) T03ab inceleme snapshot'ındaki pending clarification'a explicit kaynaklı cevap önerisi kaydeder. Cevap ve association program/veritabanı yeniden açılışından sonra bulunur. [Örnek cevap](../../examples/durable-reply-smoke/reply.fixture.json) · [Tekrar üretilebilir kanıt](reply-store-results.json).

## Çalışan akış

`kalıcı current snapshot → clarification ID + explicit soru/revision/option + source mesaj/hash → güncel scope kontrolü → append-only cevap önerisi → yeniden açılış → güvenilir onay bekleyen association`

Modelin metinden soru tahmin etmesi kullanılmaz. Gelen metnin semantiği burada yeniden çıkarılmaz: explicit question/option/revision alanları kontrollü **transport fixture** girdisidir. Kaynak hash'i metnin değişmediğini kontrol eder; verilen alanların doğal dille anlam olarak doğru olduğunu veya gerçek insan kimliğini kanıtlamaz. Gerçek UI/host receipt doğrulaması ve gerektiğinde insan review'u production katmanında ayrıca gerekir.

| Durum | Kalıcı sonuç |
|---|---|
| Hiç cevap yok | `awaiting_reply` |
| Güncel Q_UI/revision1/B explicit cevabı | `pending_trusted_selection`; sorunun gerçek approval/resolution'ı yok |
| Q_RELEASE sunumu biliniyor, current question yok | `needs_question_context` |
| Aynı source message/revision tekrar teslim | Tek receipt; idempotent duplicate |
| Aynı source kimliği farklı seçim veya snapshot'a yeniden bağlanmış | Ret; eski kayıt üzerine yazılmaz |
| Farklı source mesajları aynı seçimi tekrar ediyor | İki source korunur; yeni canonical karar üretilmez |
| Farklı source mesajları A/B çelişkisi taşıyor | `conflicting_reply_proposals`; son gelen kazanmaz |
| Yanlış proje/CID/soru/revision/option, bozuk hash veya agent actor fixture'ı | Ret; cevap satırı eklenmez |
| Access/snapshot değişmiş | Eski persisted association güncel diye okunmaz |

Clarification, current question ve kaynak presentation snapshot'ı birlikte korunur. Cevabın gelmiş olması eski clarification'ın otomatik `resolved` olması değildir. Atomic group cevap geldikten sonra da güvenilir onay/diğer blocker'lar tamamlanmadan ilerlemez. Hiçbir job/agent/test/target işlemi tetiklenmez.

## Saklama ve mevcut kodla uyum

T03ab `review_store.py` değiştirilmedi. `ReplyStore`, yalnız doğrulanmış P0 review DB'sine **ayrı sürümlü additive extension** olarak `reply_meta` ve `reply_proposals` tablosu/trigger'ları ekler. Constructor bu extension'ı transaction içinde başlatır; production migration protokolü değildir. Eski review reader snapshot'ları okuyabilir, yeni cevap lifecycle'ını okuyamaz; tam Inbox reader diye kullanılmaz.

Source receipt key proje + source message ID + source revision'a bağlıdır. Payload, reply'nin exact metin/hash/actor fixture'ını, record/CID ve request/context/source binding'ini saklar. Unique key + `BEGIN IMMEDIATE` retry/two-writer tekrarını önler; foreign key snapshot bağlantısını, update/delete trigger'ları normal append-only davranışı korur. Payload/hash/binding yeniden kontrol edilir. Önceki snapshot ve receiver raw'ları değiştirilmez.

Gerçek provider/session source namespace, authenticated identity, expiry/task-cancel policy ve tüm geçmiş için harici audit bu P0 profile'ın dışında. Bir DB yöneticisinin bütün kayıtları silmediğinin kriptografik kanıtı yok. Payload plaintext sentetik veridir; encryption/retention/purge/backup/power-loss garantisi yok. Snapshot-store kontrollü dosya/race sınırları aynen geçerli.

## Doğrulama ve kullanım

14 yeni test; **248 semantik /15 karar /40 repo testi** geçti. Explicit late reply/restart, duplicate/idempotency, conflicting/repeated choices, unknown question context, stale/foreign/CID/actor/hash/types/byte limit, revoked/current binding, atomic no-resume, rollback/retry/append-only, physical tamper, immutable source snapshot ve iki writer tek receipt test edildi. Tam production soru yönetimi, human gold veya model kalitesi ölçümü değildir.

```sh
python3 -B spikes/semantic-chain/check_reply_store.py
python3 -B -m unittest discover -s spikes/semantic-chain -p test_reply_store.py -v
# Önce review_store.py ile seçilmiş fixture snapshot'ını kaydet; record_id'yi kullan.
python3 -B spikes/semantic-chain/reply_store.py receive --db /tmp/decivora-review-example.sqlite --request examples/receiver-next-smoke/request.json --context examples/receiver-next-smoke/review-context.fixture.json --record-id <stored-record-id> --reply examples/durable-reply-smoke/reply.fixture.json
python3 -B spikes/semantic-chain/reply_store.py pending --db /tmp/decivora-review-example.sqlite --request examples/receiver-next-smoke/request.json --context examples/receiver-next-smoke/review-context.fixture.json --record-id <stored-record-id>
```

CLI mevcut review DB ister; revoked context için extension açılmaz. İlk `ReplyStore` açılışı extension schema'sını ekleyebilir; `pending` method'u bundan sonra read-only'dir. Test/kanıt örnekleri geçici DB'de çalıştı; örnek `/tmp` yolu önceden kurulu bir canlı kullanıcı deposu değildir. DB dosyası Git'e eklenmez.

## Kabul ve kalanlar

Gecikmiş **explicit fixture cevabı** kalıcı kayda bağlanır; yanlış context/authority fixture'ı reddedilir. `approved_real_decision:false`, `clarification_resolved:false`, `canonical_mutations:0`, model/API0. Cevap önerisi DB'ye gerçekten yazılır; canonical mutation0 bütün dosya işlemlerinin sıfır olduğu anlamına gelmez.

Gerçek insan onay kanalı ve decision apply, natural-language reply disambiguation, cancelled/expired task bağları, host delivery/resume, reminder, kullanıcı UI/IAM ve production Inbox henüz uygulanmadı. T13e/T18e/T19/T24f ile tam vision korunur; bu P0 bileşeni bunları complete yapmaz. İlk iki receiver denemesi failed/unscored olarak kalır. Yeni model çağrısı veya üçüncü deneme izni yok.

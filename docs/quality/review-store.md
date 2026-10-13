# İnceleme taslaklarının kalıcı yerel kaydı

**2026-10-13 · T03ab / P0, küçük kod teslimi DONE.** [`review_store.py`](../../spikes/semantic-chain/review_store.py) hazır source-bound typed review taslağını SQLite'da saklar. Programı kapatıp yeniden açınca aynı bekleyen inceleme ve açıklama descriptor'ı geri okunur. [Tekrar üretilebilir kanıt](review-store-results.json).

**Sonraki ayrı katman:** [T03ac explicit geç cevap deposu](reply-store.md) pending descriptor'a kalıcı fixture cevap önerisi ekler; actual insan approval/resolution değildir. T03ab kaynak kodu ve önceki kanıt snapshot'ı değişmedi.

## Çalışan kapsam

`request + güncel caller context → typed review guard → atomik SQLite append → kapanış → yeniden açılış → güncel access/source/context guard → kayıt bütünlüğü → mevcut taslak`

Bu, ayrı bir **inceleme snapshot deposudur**; canonical karar/event veritabanı veya çalışan ürün Inbox'ı değildir. P0 Python stdlib/SQLite yöntemi korunur; production teknoloji kararı yapılmadı. Mevcut iki sentetik proje/sabit request profili desteklenir. Production hesaplar, gerçek sohbet taraması, arbitrary task/project CRUD veya gerçek insan approval receipt'i eklenmedi.

| Durum | Kodun davranışı |
|---|---|
| Aynı request/context/çıktı yeniden kaydedilir | Aynı record ID; duplicate receipt, yeni satır yok |
| Program kapanıp yeniden açılır | Aynı source binding, current question ve pending clarification geri gelir |
| Güncel caller access iptal edilmiş | Saklanmış taslak olsa da okuma/yazma ret |
| Source/state/package binding değişmiş | Eski taslak güncel diye geri dönmez |
| Geçerli atomic-group context değişmiş | Yeni snapshot kimliği; kaydedilmediyse `current_snapshot_not_stored`, eski kayıt korunur |
| Atomik insert sırasında hata | Transaction rollback; retry tek kayıt oluşturabilir |
| İki bağımsız SQLite bağlantısı aynı taslağı yazar | Transaction + unique record ID ile tek satır |
| Normal SQL update/delete | Trigger ret; geçmiş snapshot değiştirilmez |
| DB yöneticisi payload'ı fiziksel değiştirmiş | Seçilmiş güncel payload/hash/kimlik karşılaştırması ret |

`record_id` sürüm + request ID + context digest + tam generated payload hash'ine bağlıdır. Özgün input/output kökeni `deterministic_selected_typed_records` kalır; model-reported kaynakların semantik doğruluğu artırılmış sayılmaz. Soruya tahminen bağlama, actual approval, hedef okuma, test/agent çalıştırma veya model dispatch yok. `canonical_mutations:0` domain karar değişimi olmadığını anlatır; SQLite inceleme satırı gerçekten yazılır.

## Kullanım ve doğrulama

```sh
python3 -B spikes/semantic-chain/review_store.py store --db /tmp/decivora-review-example.sqlite --request examples/receiver-next-smoke/request.json --context examples/receiver-next-smoke/review-context.fixture.json
python3 -B spikes/semantic-chain/review_store.py current --db /tmp/decivora-review-example.sqlite --request examples/receiver-next-smoke/request.json --context examples/receiver-next-smoke/review-context.fixture.json
python3 -B spikes/semantic-chain/check_review_store.py
python3 -B -m unittest discover -s spikes/semantic-chain -p test_review_store.py -v
```

İlk komut yeni fixture DB oluşturur veya yalnız kendi sürümü doğrulanan DB'ye append yapar. `current` CLI mevcut DB ister; stale/unauthorized input için DB oluşturmaz. Yalnız seçtiğin sandbox hedefini kullan. Örnek yolu çalıştırdığımız gerçek bir kullanıcı deposu değildir; testler geçici dizinlerde yapıldı. DB/runtime dosyaları Git'e eklenmez.

12 yeni test; **234 semantik /15 karar /40 repo testi** geçti. Restart ve exact pending descriptor, retry/append-only, revoked/foreign/stale scope, changed atomic context, insert rollback, payload tamper, ilgisiz DB/version ret,0600 yeni dosya izinleri, bilinen symlink ret, iki writer ve no-execution invariant'ları test edildi. Sentetik store örneği authored human gold/model doğruluğu veya geniş production concurrency ölçümü değildir.

## Sınırlar ve devam

- Kalıcı snapshot ve pending descriptor saklanıyor. **Gecikmiş cevabın kalıcı receipt'i, clarification çözme/reopen durumları ve host'a teslim henüz yok.** Önceki `project_review.py` explicit late-reply association fixture'ı ayrı; bu depoya entegre edildi diye gösterilmez.
- Caller access flag hâlâ controlled fixture; gerçek IAM değil. İki projelik profile grant'i herkesin bütün projelerini okuma izni değildir.
- Payload/hash kontrolü DB yöneticisine karşı harici audit veya bütün geçmişin silinmediği kanıtı değildir. Power-loss/crash recovery, signed audit, retention/purge, encryption, backup/restore ve migration bu store için ayrıca uygulanacak. Restart testi elektrik kesintisi testi değildir.
- SQLite path kontrolleri kontrollü sandbox içindir; hostile filesystem race/TOCTOU ve production provisioning garantisi değildir. Yeni DB0600; mevcut dosyanın izinleri sessizce değiştirilmez.
- Depo kendiliğinden tarama/polling/reminder/model/runner başlatmaz. Bekleyen kaydın yeniden bulunması, kararın verilmesi veya task'ın tamamlanması değildir.

Tam vizyonun kalıcı soru/cevap gereksinimi ve T07/T13/T19 işleri korunur. Bu küçük P0 teslimi production görevlerini kapatmaz. İlk/ikinci receiver raw, prompt, oracle ve önceki proof'lar aynı kalır. Model/API çağrısı0; bu geliştirme sohbetinin toplam token tüketimi unknown.

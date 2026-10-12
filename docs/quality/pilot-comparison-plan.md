# İlk değer karşılaştırması: ortak çalışma düzeni

**P0 · ortak protokol; dar same-source lexical/kayıtlı-model ölçümü var, native/ekonomi kıyası henüz yok.** Otomatik semantik extraction zorunlu iş; yalnız yöntemi, veri ve bütçesi açık. Karşılaştırma bütçe veya provider izni değildir.

| Kol | Aynı senaryoda uygulanacak yöntem | Bugünkü kanıt |
|---|---|---|
| Kural tabanlı baseline | Source-only Spike-0 lexical extraction; bağımsız draft scorer | [Çalıştırıldı, zayıf sonuç](lexical-baseline-results.json) |
| Decivora zincir deney düzeneği | Structured karar/gerekçe/target/AC command’ları | [Typed fixture geçti](decision-chain-results.json); metin çıkarımı karşılaştırması değil |
| Zorunlu semantik extractor | Kaynak chunk + ilgili pending question/karar; typed prediction ve abstention | [MEMBERSHIP-002](membership-002-result.md): dört draft aday ve source/type geçti; [aynı dört mesaj kıyası](same-source-comparison.md) yerelde çalıştı. Human gold/genel kalite açık |
| Devam paketi | Onaylı kararlar + kaynak pointer’ları + unknown uygulama/AC + bekleyen soru | [Offline serialization/freshness kontrolü](resume-file-comparison.md) çalıştı; gerçek fresh-session model davranışı not_run |
| Basit dosya yöntemi | Aynı bilgilerle insanın güncel tuttuğu küçük karar/task/kanıt dosyası | [Eşit core dosya serialization](resume-file-comparison.md) çalıştı; bağımsız manuel bakım/receiving-model/user burden not_run |
| Native araçlar | Kullanıcının erişebildiği belirli Projects/host build’i ve izinli proje bilgisi | not_run; erişilemeyen yetenek unknown/unsupported olarak kaydedilecek |

## Aynı koşulları koru

Her run: immutable corpus/oracle/scorer hash’i, source session/project/revision, sırayla açılan bilgi checkpoint’leri, yöntem/build/config, context penceresi, yetkiler, target ref/path/hash ve AC revision setini içerir. Gold açık kaynak input’una konmaz. Beklenen durumları extractor veya impact algoritması üretmez. Native platforma gönderilecek veri için ayrıca paylaşım sınırı gerekir.

S01→S02: eski Markdown → Q_STORE → başka chat’ten gecikmiş B → SQLite → AND/OR/unknown etki → ayrı apply → eski içerik → güncel içerik → yalnız rollback → bütün gerekli AC. S03: iki açık soru varken yalnız A → ambiguous, **onay yok**. Pending soru/resume, project isolation, permission denied ve conflicting evidence negatifleri ayrı case family olarak korunur.

**Geliştirme/holdout:** draft etiketler insan/adjudication’dan geçmeden gold denmez. Bu baseline reserved örnekleri de açtı; mühürlü kör holdout iddiası yok. Yeni sealed family oluşturulmadan final kalite genellemesi yapılmaz. Aynı oturumun farklı mesajlarını bağımsız kullanıcı örneklemi sayma.

## Skor ve veri alanları

- Exact/coarse extraction ayrı; entity/relation/authority/state/impact/target/AC ayrı skorlanır. Duplicate bire bir eşlemede iki TP yaratmaz. Eksik critical score/evaluator error `incomplete` olur; false approval/false verified ayrı zorunlu negatif kapıdır.
- Kullanıcı yükü: düzeltme sayısı, açık soru bulma/cevaplama süresi, yanlış öneri yükü, yeni oturumda doğru next-action seçimi; her görev için start/end ve gözlem kaydı.
- Latency: source occurred/received → captured → extraction → reconciled → reviewed → applied → observed → verified; provider kuyruğu/aktif süre ayrı. Clock farklılığı ve unavailable timestamp işaretlenir.
- Ekonomi: input/output/cache token, model/version, provider request ID’nin redakte referansı, retry/child dahil toplam bütçe ve wall-time. Ölçülmeyen host maliyeti null; fiyat snapshot’ı olmadan para tahmini karşılaştırma sonucu olmaz.
- Kapsam/adillik: yöntemlerin ulaşabildiği aynı bilgi ve target izinleri; manuel hazırlık yükü dahil. Bir native yöntem otomatik source capture yapamıyorsa manuel import biçimi ve kapsam farkı raporlanır.

Şimdiki scorer yalnız exact source span ve coarse tür tanısıdır; yukarıdaki tüm kriterler uygulanmış değildir. [Ölçüm protokolü](evaluation-protocol.md) release/quality kurallarının otoritesidir. Sonuçlar ve owner yatırım kararı T03c’de; otomatik build veya scope daraltma yok.

## İlk aynı-source tanısı — 2026-10-12

[T03p](same-source-comparison.md): aynı iki request/dört mesaj, eski kayıtlı ilk model output ve source-only lexical. Shared span/kind score model4TP/0FP/0FN, lexical0TP/1FP/4FN. AnswerRecord/Evidence eksik baseline capability açıkça kaydedilir; attributes/domain/native/metrik superiority yok. Cost/latency unknown; model yeniden çağrılmadı. Bu kaydın varlığı bütün protokolün çalıştırılmış olduğu anlamına gelmez.

[T01h yeni development paketi](../../examples/adversarial-smoke/README.md): sekiz yeni sentetik mesaj,6 drafted candidate ve2 scope-no-candidate vaka; eski/current question revisions,quoted/planned veEN örnekler. Hazırlıktan sonra [MEMBERSHIP-003](membership-003-result.md) bir kez çalıştı;6 draft aday/2scope-no-candidate eşleşti. H4 partial review tamamlandı, tek-send izin tüketildi; sealed holdout/gold değil.


## Resume/file yerel serialization tanısı — 2026-10-12

[T03s](resume-file-comparison.md) aynı MEMBERSHIP-003 kaynak/aday/current fixture bilgisini resume envelope ve simple-state JSON içinde eşit core ile taşıdı; bağımsız authored checklist iki kolda da geçti. Source-only ayrı capability koludur. Simple-file daha küçük; token/maliyet/LLM next-action veya kullanıcı yönetim yükü ölçülmedi. Snapshot wrapper freshness kontrolü basit dosya aracına da eklenebilir; ürün farklılaşması/üstünlüğü bu kıyasla kanıtlanmaz. RES-08 fresh-session/native ana kapısı açık.


## Kayıpsız paket küçültme — 2026-10-12

[T03t](resume-compaction.md): N01/N02 byte boyutu%31,79/%35,20 azaldı; compact paketten ve simple-file'dan frozen önceki core exact restored. Receiver-facing view quote'ları kodla çözer; değişmemiş authored checklist üç kolda geçti. Token/para veya gerçek alıcı/model/native sonucu değil. Sonraki model deneyi decoded readable view ile hazırlanır; LLM'e offset/record tablosu çözdürmek default yol sayılmaz. Yeni live izin yok.

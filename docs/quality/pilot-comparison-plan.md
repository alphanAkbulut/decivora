# İlk değer karşılaştırması: ortak çalışma düzeni

**P0 · uygulanacak protokol; native/semantik kıyas sonuçları henüz yok.** Otomatik semantik extraction zorunlu iş; yalnız yöntemi, veri ve bütçesi açık. Karşılaştırma bütçe veya provider izni değildir.

| Kol | Aynı senaryoda uygulanacak yöntem | Bugünkü kanıt |
|---|---|---|
| Kural tabanlı baseline | Source-only Spike-0 lexical extraction; bağımsız draft scorer | [Çalıştırıldı, zayıf sonuç](lexical-baseline-results.json) |
| Decivora zincir deney düzeneği | Structured karar/gerekçe/target/AC command’ları | [Typed fixture geçti](decision-chain-results.json); metin çıkarımı karşılaştırması değil |
| Zorunlu semantik extractor | Kaynak chunk + ilgili pending question/karar; typed prediction ve abstention | not_run; yöntem/veri/bütçe kaydı bekliyor |
| Devam paketi | Onaylı kararlar + kaynak pointer’ları + unknown uygulama/AC + bekleyen soru | not_run; yeni oturumda doğru sonraki adım ölçülecek |
| Basit dosya yöntemi | Aynı bilgilerle insanın güncel tuttuğu küçük karar/task/kanıt dosyası | not_run; dosya hazırlama/güncelleme yükü dahil |
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

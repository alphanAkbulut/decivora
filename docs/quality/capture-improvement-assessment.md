# Yakalama ve otomatik proje hafızası — iyileştirme önerileri

**19 Ekim 2026 — kullanıcı geliştirme sırasını onayladı.** Aşağıdaki ilk inceleme bulguları tarihsel dayanak olarak korunur. İlk teslimin sayfa checkpoint/dedup/pending kodu uygulandı; diğer öneriler henüz uygulanmış sayılmaz. Ayrıntı: [uygulama ve sınırlar](codex-exec-capture-runtime.md#page-atomic-continuation--19-october). Yeni gerçek sohbet okuması ve model çağrısı yapılmadı. Önceki bir defalık kaynak izni tüketilmiş durumdadır.

## Kararın dayanağı

| Gözlem | Kanıt | Yorum / sonuç |
|---|---|---|
|6mesaj kaydedildi; iki turda unread item kaldı | [Gerçek sonuç](codex-real-capture-001-results.json) | Kaynak bağlantısı bu hostta çalışıyor; kapsamın tamamlandığı kanıtlanmadı |
| Her çağrıda cursor yeniden `None` oluyor; nextCursor kalıcı makbuza taşınmıyor | [Reader](../../packages/capture/codex/read_client.py), [writer](../../packages/capture/codex/app_server.py) | Polling aynı başlangıç sayfalarına dönebilir; dedup tek başına ilerleme değildir |
| Aynı origin item yeni capture binding'inde farklı source oluyor | [Source identity](../../packages/capture/conversations.py); sentetik repro:1origin→2source ID | Yeni grant/bağlantı sırasında gereksiz yeniden analiz ve mükerrer öneri riski |
| Sonraki sayfa timeout'unda ilk okunmuş sayfa henüz kaydedilmemiş | Sentetik repro: bir başarılı sayfa, ikinci sayfa timeout, source import0 | Önceki kabul edilmiş veri silinmiyor; bu grupta henüz kabul edilmemiş sayfalar tekrar okunmak zorunda |
| Proje32import, capture32fingerprint sınırında duruyor | ConversationService._ingest / CodexAppServerCapture.collect | Sürekli kullanımın önünde gerçek preview kapasite sınırı; sabiti büyütmek tek başına yeterli değil |
| Önceki context en fazla6mesaj/6000UTF-8byte ve geliş sırasına dayanıyor | [Dialogue review](../../packages/capture/dialogue_review.py) | Kısa/geç cevapta gerekli soru eksik kalabilir; geliş sırası konuşma sırası değildir |
| CLI kaynak alımı doğrudan domain katmanına yazıyor; Operations command sınırı tam native pipeline trace'i değil | [CLI](../../scripts/capture_codex_thread.py), [Operations](../../packages/operations/local.py), [UI state](../../apps/local_ui/server.py) | Capture progress ve kullanıcıya gösterilen çalışma durumu tek görünümde henüz birleşmiyor |

Sentetik repro'lar geçici ayrı SQLite dosyalarında çalıştırıldı; gerçek TEST/normal DB'ye yeni kayıt yazılmadı. Bu analizde yeni ürün/performans/semantik kalite deneyi çalıştırılmadı.

## Önerilen geliştirmeler ve kabul sınırları

### 1. Kalıcı ilerleme ve sayfa başına güvenli kayıt — ilk öncelik

Her izinli source/turn için provider cursor, son kalıcı item kimliği, kapsam epoch'u ve policy revision saklansın. Maskelenmiş kaynaklar, atlanan item'ın yalnız güvenli tür/kimlik makbuzu ve ilerleme işaretçisi **aynı transaction'da** yazılsın. LLM ve host çağrıları transaction dışında kalsın.

Başarı ölçütü: sayfa bütçesi sonunda dur→yeniden başlat→sonraki sayfaya devam; arada crash/rollback olursa kayıpsız ve idempotent yeniden işleme. Yalnız hariç tutulan item'lar içeren bir sayfa da tarama ilerlemesi üretmeli. Unknown tür atlandı diye tam kapsam sayılmamalı. Büyük tek item veya geçersiz cursor'da görünür gap oluşturulmalı.

Önemli istisna: aktif turda ertelenmiş assistant item'ının ötesine cursor ilerletilirse final yanıt kaçabilir. Pending item/turn listesi tutulmalı; terminal değişiminde ilgili item tekrar değerlendirilmeli. Sadece `last_item_id` eklemek yeterli değildir.

### 2. Bağlantıdan bağımsız kaynak kimliği ve revision

Kaynak origin anahtarı workspace/project, source surface/profile, thread, turn, item ve source revision üzerinden tanımlansın. Bağlantı/grant kimliği ayrı provenance/authorization kaydı olsun. Aynı projedeki yeni izin aynı kaynağı tekrar içerik olarak çoğaltmasın; farklı proje ve audience bilgileri birbirine karışmasın. Değişen mesaj yeni revision/history üretsin, eski içerik sessizce değişmesin.

Başarı ölçütü: aynı origin→yeni bağlantı/restart→tek içerik kimliği, korunmuş iki provenance/izin makbuzu. Revoked kaynağa erişim dedup/cache üzerinden geri gelmesin. Edit/compaction ve eski onaylar stale/review gerektirsin. Ayrı grant'in eski private içeriği ortak görünür yapmadığı doğrulansın.

### 3. Kaynak deposu, kapasite ve kuyruk

Mevcut import metinleri audit'ten okunuyor; `_source` ve context hazırlığı geçmişi tarıyor, fingerprint map'i makbuzlarda tekrarlanıyor.32sınırını yalnız büyütmek sorgu/ekran/history maliyetini artırabilir. Mevcut SQLite içinde indeksli kaynak/işleme durumları, unique origin constraint ve sayfalı sorgu öneriyorum. Audit değişiklik tarihçesi olarak korunmalı; source payload/index ve audit'nin retention/purge ilişkisi ayrıca tasarlanmalı.

Durumları ayrı tut: hostta görüldü → kalıcı kaydedildi → analiz sırasına alındı → analiz edildi → inceleme bekliyor → uygulandı → doğrulandı. Source+queue outbox/checkpoint atomik olmalı. Worker crash/unknown provider usage, yeniden okuma veya yeni grant model çağrısını sessizce tekrarlatmamalı. Eski veriler için backup/restore ve açık migration gerekir; şu an uygulanmış sayılmaz.

Başarı ölçütü:32üzeri sentetik mesajı izinli kapsamda kademeli alabilmek; ekranları tüm geçmişi yüklemeden sayfalamak; kabul edilmiş işin kapasite/disk hatasında korunması.1000mesaj gibi kontrollü fixture'da query/işleme süresi ve DB büyümesi ölçülsün; henüz kapasite/SLA veya hız kazanımı iddia edilmiyor.

### 4. Eksik kapsamı ve duraklamayı gösteren kullanıcı deneyimi

Conversations/Operations içinde bir bağlantı kartı: seçilmiş kaynak, izin kapsamı, son kalıcı item, alınan public mesaj, analiz bekleyen kaynak, onay bekleyen öneri, unread/gap, son başarılı okuma, durma sebebi ve sonraki işlem. Bilinmeyen toplam için yüzde gösterilmesin. Örnek metin: “6 mesaj kaydedildi · 2 turda okunmamış öğe var · 6 kaynak model bekliyor”.

“Devam et”, “Duraklat”, “İzni kaldır” farklı işlemler olsun. Arayüz mevcut yetkiyi aşan eski tarih aralığını veya yeni thread'i sessizce eklemesin. Bu kart görev workflow stage'i değildir: task Blocked ile capture Paused/Partial birbirine karıştırılmamalı. Operations trace'i capture→persist→queue→model→review adımlarını içerik/secret taşımadan ilişkilendirsin.

### 5. Yeni mesajlar ve eski eksikleri ayrı ilerletme

İzinli izleme kapsamında live frontier ve backfill frontier ayrı tutulsun. Başlangıçta seçilmiş eski tur kümesi sabitlensin; yeni turlar gelince bitmemiş eski turlar son10penceresinden düşüp unutulmasın. Adil çalışma sırası, yeni soruları yakalarken geçmiş boşlukların da ilerlemesini sağlasın. Her tur aynı item sayısına sahip olmadığından sayfa bütçesi boşta kalan turlar arasında paylaşılabilir.

Scope, saklama ve zaman sınırı önce belirlenmeli. Bir defalık10tur izni sürekli live izleme izni değildir. Opaque cursor ömrü/kararlılığı varsayılmasın; cursor geçersizleşirse son doğrulanmış item anchor ile bounded overlap/reconciliation veya görünür gap önerilsin. Eksik kaynakta başlangıca kör reset yapılmasın.

### 6. Konuşma bağlamını ve geç cevapları güçlendirme

Mesajlar geliş sırasından ayrı host turn/item ilişkisini korusun. Hazırlanan context, yalnız son6mesaj yerine ilgili açık soru, seçenek revision'ı, karar ve hedef task ile kaynaklı yakın konuşmayı seçsin. Birden fazla olası soru varsa “evet/B” eşlemesi yapılmasın; clarification proposal oluşsun. Alıntı bugünkü source'a; yorum için kullanılan geçmiş ayrı referanslara bağlansın.

Başarı ölçütü: gecikmiş cevap ve yanlış geliş sırası fixture'larında doğru soruya öneri; belirsiz durumda seçimden kaçınma; assistant'ın insan adına yazdığı özetin insan onayı sayılmaması. Model anlam doğruluğu bağımsız örneklerde ayrıca ölçülmeli.

### 7. Model kullanımı ve token ekonomisi

Yeni/değişmiş ve henüz işlenmemiş uygun metinler semantic gruplara alınsın. Her araç item'ı, aynı fingerprint veya polling turu LLM çağrısı üretmesin. Girişe yalnız ilgili kaynak/context gönderilsin. İşlem anahtarı source revision + extraction version + context snapshot + grant/budget üzerinden tutulsun; geçerli sonuç yeniden kullanılabilir, stale sonuç otomatik kabul edilmez.

Deterministik kurallar candidate seçiminde yardımcı olabilir; kelime yakalamak karar seçildi/uygulandı/Done kanıtı değildir. Mevcut token/money reservation ve unknown usage kapıları korunmalı. Model işi gecikse bile yerel capture, kendi storage limiti ve yetkisi içinde ilerleyebilmeli. Capture RPC, model tokenı, review süresi ve gerçek göreve dönüşme ayrı ölçülsün; token tasarrufu yüzdesi henüz ölçülmedi.

Mevcut USD3 onayı sentetik veri içindir. Altı gerçek TEST mesajının API'ye gönderilmesi bu analiz veya önceki tek yerel okuma izniyle yetkilendirilmez.

### 8. Performansı ölçerek uyarlama — çekirdekten sonra

Şimdilik tek item/page1MiB güvenlik sınırını koru. Ölçümde RPC adedi, byte, p50/p95 yerel gecikme ve yeniden okunan item oranını kaydet. Provider destekliyorsa ve sınırlar korunabiliyorsa küçük kontrollü page-size artışı/debounce önerilebilir; büyük item, timeout ve bilinmeyen sonucu tekrar güvenli boyuta indirme ayrı tasarım ister. Mevcut tek gerçek çalışma bir performans benchmark'ı değildir.

MVP için mevcut modüler yerel servis/SQLite yaklaşımıyla ilerlemek uygun adaydır. Bu inceleme yeni mikroservis, Kafka, vector DB veya genel altyapı değişikliğini gerektiren kanıt üretmedi.

## Uygulama sırası önerisi

| Teslim | Gözlenebilir ürün çıktısı | Mevcut sahiplik / bağımlılık |
|---|---|---|
|1. Kaldığı yerden devam eden çekirdek | Sayfa kaydı/checkpoint + reconnect dedup + pending aktif item korunumu | T17; source/storage değişimi T07/T23 korumalarıyla, schema kararı/migration ayrıca incelemeye tabi |
|2. Günlük kullanıma uygun kaynak ve ilerleme görünümü | İndeksli/paged kaynak deposu, kuyruk/outbox, gap/progress/izin kartı, live/backfill adaleti | T17,T19,T20,T23; aynı iş için yeni parent açma |
|3. Onaylı otomatik çıkarım zinciri | İzinli yeni mesaj→bounded model→Task/Decision/status önerisi→review→kanıt/impact akışı | T09,T10,T13,T14,T21,T22; gerçek veri/model paylaşımı ayrıca onaylanır |

Birinci teslimin kabulü bütün gelecekteki UI/entegrasyonlara bağlanıp gereksiz açık tutulmamalı; kalan entegrasyonlar kendi mevcut sahibi ve first-use kapısıyla izlenmeli. Buna karşılık source cursor/dedup veya izin kontrolü kullanılmadan ilgili first-use kapısı geçilmiş sayılmamalı.

## Dayanaklar ve açık kararlar

- Kaynak: mevcut local kod ve [readback001](codex-real-capture-001.md). Yeni sentetik teşhisler uygulama testi/gold model değerlendirmesi değildir.
- Resmî [App Server referansı](https://developers.openai.com/codex/app-server),19Ekim2026kontrolü: selected-turn item pagination, opaque cursor ve turn-bound item anchors belgelenmiştir; her host/store desteği ayrıca doğrulanır. Cursor TTL veya tam geçmiş garantisi belgelenmiş kabul edilmedi.
- İncelenecek uygulama kararları: checkpoint/source storage migration sınırı; live/backfill öncelik policy'si; izin kartındaki veri/retention kapsamı; gerçek metin model grant'i. Teknik varsayımlar ADR kabulü veya yeni kullanıcı onayı gibi kaydedilmedi.

İlk analizde kod/yayın yapılmamıştı. Kullanıcının “önerilerinle devam et” onayı sonrası ilk teslim uygulandı; kapsamı ve doğrulaması yukarıdaki uygulama kaydındadır. İkinci ve üçüncü teslim, gerçek kaynak/model yetkisini kendiliğinden açmaz.

İkinci teslim ilerlemesi: [source outbox, izinli worker, ilerleme kartı ve native tanı](conversation-processing-runtime.md) kodlandı. İndeksli kapasite/paging ve live/backfill henüz bu dilime dahil değil. Worker üçüncü teslimin mevcut proposal-review ucuna bağlanır; sürekli otomatik izin/model akışı ve gerçek kalite kabulü açık.

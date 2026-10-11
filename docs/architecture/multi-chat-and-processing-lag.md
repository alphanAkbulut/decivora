# Bir proje, birden çok chat ve işleme gecikmesi

**2026-10-11 — Kullanıcı ihtiyacının teknik taslağı; uygulanmadı, hız/kalite ölçülmedi.** Bir proje farklı chat pencerelerinde ilerleyebilir. Hedef, yetkili kaynakları ortak proje hafızasında birleştirirken her chat'in bağlamını ve kanıtını korumaktır. İkinci ihtiyaç, gelen konuşma hızına yetişilemediğinde kaybı veya gecikmeyi gizlememektir. [Bağlantı](connection-and-context.md), [reconciliation](reconciliation-impact.md) ve [runtime](runtime-contracts.md) kuralları geçerlidir.

## 1. Chat ile proje aynı kimlik değildir

| Kayıt | İşlevi ve sınırı |
|---|---|
| Project/workspace ID | Ortak görev/karar hafızasının sabit kimliği; ad benzerliği proje eşlemesi değildir |
| Source session kimliği | Provider + hesap/installation + session/thread ID + epoch; sekme başlığı veya pencere sırası kimlik değildir |
| Session binding | İzinli kaynak kapsamını hedef projeye bağlayan sürümlü kayıt; kullanıcı veya önceden açıkça yetkilendirilmiş binding kuralı gerekir |
| Source span/revision | Mesaj/parça, role, reply/parent ilişkisi varsa referansı; orijinal ve düzenlenmiş sürümler ayırt edilir |
| Topic segment | Chat içindeki konu/amaç/task adaylarına bağlı mesaj aralığı; model çıkarımıysa öneri ve belirsizlik taşır |
| Context snapshot | Kullanılan proje/karar/task revision'ları, kaynak coverage, session işleme frontier'ları ve erişim kapsamı |

Bir proje birçok session'a bağlanabilir. Aynı session birden fazla projeyi karıştırıyorsa bütün konuşma hepsine kopyalanmaz: açıkça atanmış ve yetkili span kapsamı kullanılır; belirsiz aralık review/quarantine'a gider. Konu değişmesi otomatik proje değiştirme değildir. Binding düzeltmesi eski provenance'ı silmez; etkilenmiş adaylar yeniden değerlendirilir, yanlış projede görünürlük/cache erişimi geri çekilir ve düzeltme audit'i korunur.

Yeni chat kendiliğinden izne dahil sayılmaz. Önceden kabul edilmiş kaynak kuralı yeni session'ları açıkça kapsıyorsa o sınır içinde bağlanabilir; aksi halde Q10-A uyarınca yalnız ayrı listeleme izniyle önerilir, seçim ve gerekli izinler olmadan içerik okunmaz. Adapter tüm chat pencerelerini okuyabiliyor varsayımı yoktur. Destek yoksa kullanıcı tarafından seçilmiş export/import veya araç üzerinden açık kayıt kullanılır; coverage eksikliği görünür.

## 2. Konudan görev/karara giden yol

1. İzinli mesajı session/span/revision ve receipt ile kaydet. Mesajın konuşmacısı ve alıntı/tool sonucu ayrılır; alıntılanan “bunu yap” ifadesi kullanıcı yetkisi sayılmaz.
2. Açık project/task/decision kimliklerini deterministik çöz. Serbest konuşmada amaç, soru, fikir, karar önerisi, iş isteği, completion iddiası ve ilgili konu segmenti için kaynaklı adaylar üret. Her cümle task olmaz; açıklama, örnek, olumsuz ifade ve varsayımsal seçenekler ayrı değerlendirilir.
3. Yalnız ilgili yerel konuşma bağlamını ve erişilebilir ortak proje kayıtlarını getir. “Bunu iptal edelim” gibi belirsiz referansta önceki mesaj/reply ve task seçimini kullan; yeterli kanıt yoksa hedefi tahmin ederek kapatma, review iste.
4. Aynı projenin mevcut kayıtlarıyla `new / duplicate / refinement / conflict / supersession_candidate / uncertain` karşılaştırması yap. Aynı task ID güçlü işarettir; benzer başlık/embedding tek başına aynı iş kanıtı değildir. Aynı metnin iki chat'te geçmesi de iki bağımsız kanıt sayılmaz; kopya/fork lineage biliniyorsa saklanır.
5. Yeni adayda başlık, amaç, önerilen AC, bağımlılık/gerekçe, belirsizlik ve kaynak bağlantılarını hazırla. Aynı işse yeni provenance ekleme önerisi; değişmiş kapsam varsa mevcut kayda revision/diff önerisi; çelişkide alternatifler ve iki kaynak görünür.
6. Capture/aday üretimi ile canonical task/karar değişimini ayır. Mevcut approval policy uygulanır; AI önerisi veya başka chat'teki agent “done” mesajı insan onayı/verification olmaz.

Önerilen ilişki kaydı: session/span → topic segment → candidate/evaluation → canonical task/decision → approval/evidence. Bir task birden fazla chat'ten kaynak alabilir; bir mesaj birden fazla aday çıkarabilir. N:M ilişki provenance'ı kaybetmeden saklanır. Confidence ölçülmemişse kesin yüzde gösterilmez; ilişki review'su ve coverage kullanılır.

### Sentetik örnek

| Kaynak | Konuşma | Ortak projede önerilen sonuç |
|---|---|---|
| Chat A / mesaj 12 | “Markdown senkronizasyonunu yapalım” | T-1 taslağı; karar gerekçesi ve kaynak A:12 |
| Chat B / mesaj 8 | “Ana veri kaynağı SQLite olsun” | Yeni karar önerisi; T-1 için etki incelemesi. Onaysız otomatik iptal yok |
| Chat C / mesaj 20 | “Senkronizasyon işini bitirdim” | T-1'e completion claim; kanıt ve güncel uygulanabilirlik incelenir, otomatik verified değil |

Chat B'deki karar onaylanmış olsa bile A'dan sonradan gelen eski mesaj onu geri almaz. Provider zamanı, ingestion zamanı ve proje event sequence farklıdır. Chat'ler arasında tek güvenilir konuşma sırası varsayılmaz; açık revision/causation ve onay durumu esas alınır. Geç gelen veya düzenlenmiş mesaj etkili assessment'ları stale yapabilir; yeni değerlendirme ve gereken review üretilir.

## 3. Yeni chat bağlamı nasıl alır?

İzinli host/agent isteğinde küçük bir context paketi hazırlanır: proje amacı, seçili iş, ilgili güncel onaylı karar/AC, blocker ve pending impact, ilgili eski karar gerekçeleri, değişiklik delta'sı, kaynak pointer'ları ve coverage. Her chat'e bütün geçmiş gönderilmez. Cursor context'i geçersizse bounded resync yapılır; [token politikası](routing-token-economy.md) uygulanır.

Diğer session'lardaki özel içerik aynı projede diye paylaşılmaz. Özet, kaynak başlığı, sayım ve ilişki yolu da ACL kontrolüne tabidir. Eksik erişim için güvenli “bağlam kapsamı sınırlı” göstergesi kullanılır; gizli chat'in varlığı/açıklaması sızdırılmaz.

Bir chat'te karar değişince diğer açık model oturumunun bunu otomatik okuduğu veya belleğini güncellediği varsayılmaz. Decivora ilgili görünümü/brief'i stale işaretler; desteklenen abonelik bildirimi veya sonraki yetkili tool çağrısında delta sunar. Host bildirim/delta tüketmiyorsa eski context ile devam edebilir; canonical değişiklik uygulanırken revision ve approval kontrolleri son savunmadır. Kullanıcının ekranda bir chat açması tek başına context aktarımı değildir.

## 4. Hız: kaydetmek, analiz etmek ve onaylamak ayrı

| Aşama | İş ve kapasiteyi belirleyenler | Gösterilecek durum |
|---|---|---|
| Capture | Adapter erişimi, payload byte, disk, DB/queue admission | Son kalıcı receipt; alınamayan/eksik aralık |
| Extraction/reconciliation | İçerik uzunluğu, bağlam/retry, worker kapasitesi, model hızı/kotası, risk onayı | Son başarıyla işlenen frontier, pending/retry/deferred |
| Review/approval | Yetkili insan yanıtı ve güncel snapshot | Analiz edildi, karar bekliyor |
| Apply/verification | Revision/izin ve gerekli kanıt | Uygulandı; doğrulama ayrıca gösterilir |

Kısa trafik sıçraması sonlu kuyrukla karşılanabilir; **sürekli gelen iş hızı işleme kapasitesini aşarsa kuyruk büyür**. Bu yüzden “her hızda gerçek zamanlı” vaadi yoktur. Mesaj/saniye tek ölçü değildir: kısa mesaj ile uzun transcript aynı iş değildir. Byte, tahmini token, job servis süresi ve izinli provider kapasitesi birlikte ölçülür.

Yaklaşık bekleme tahmini ancak karşılaştırılabilir işler ve kararlı throughput varsa gösterilir; insan onayı/provider kesintisi/bütçe bekleyen iş için kesin ETA uydurulmaz. Projenin genel `current` durumu yalnız en son işlenen mesaj tarihinden çıkarılmaz: session başına alınan/işlenen aralık ve gap kümesi gerekir. Tek session'ın ilerlemesi diğerinin açığını kapatmaz.

### Yetişilemediğinde davranış

1. Capture ve semantik analiz ayrı kuyruk/iş aşamalarıdır; model yavaş diye alım hook'u uzun süre açık tutulmaz. Kalıcı receipt yalnız başarılı alımdan sonra verilir.
2. Kısa mesaj/stream parçaları sonlu idle + maximum-wait penceresi ve byte/token sınırıyla gruplanır. Sürekli konuşma flush'ı sonsuza kadar ertelemez. Ara özetler birleştirilebilir, **benzersiz kaynak mesajları düşürülemez**. Yalnız gerçekten alınmış parçalar için receipt/coverage tutulur.
3. Exact dedup/cache/delta ve deterministik yollar önce kullanılır. Aynı session sürekliliği ve bağımlı aralıklar korunur; bağımsız session extraction'ları sınırlı paralel çalışabilir. Proje canonical apply revision kontrolüyle seri tutarlı kalır; global transcript birleştirme gerekmez.
4. Aktif iş, bilinen blocker ve onaylı karar etkisi öne alınır; geçmiş import ve diğer projeler aç bırakılmaz. Henüz okunmamış mesajların kritik olduğu biliniyor varsayılmaz; yaş bazlı adil sıra ve max-wait gerekir. Model concurrency artırımı kota/bütçe/risk onayını aşamaz.
5. Semantik kapasite veya bütçe dolduysa kalıcı alınan iş pending/deferred olur. Dashboard “kaydedildi, henüz analiz edilmedi” ve nedenini gösterir. Bilinen ilgili gap, pending impact veya stale context ile next-ready/verification kesinmiş gibi ilerlemez; eksiklik tüm projeyi gereksiz kilitlemeden ilgili iş kapsamına bağlanır, bağımlılık kapsamı bilinmiyorsa belirsizlik korunur.
6. Queue/storage dolduysa yeni alım durur veya geri basınç döner; sahte receipt yoktur. Bounded adapter spool yalnız gerçekten destekleniyorsa kullanılır. Host replay/export sağlamıyorsa o aralık kaybolabilir; **kayıpsızlık garanti edilmez**, gap açık kaydedilir ve yeniden import yolu sunulur. Önceden kalıcı alınan iş hız uğruna silinmez.
7. Restart/catch-up idempotent ve bounded çalışır; receipt cursor ile processing frontier ayrıdır. Daha sonra işleme, eski kaynağı yeni karar gibi uygulamaz. Onaylar stale ise yeniden değerlendirme gerekir; replay modele/dış sisteme otomatik iş göndermez.

Batch, debounce, polling ve retry için [mevcut deney aralıkları](execution-and-integrations.md) korunur; üretim garantisi değildir. Rate, queue, disk, concurrency ve model sınırları [limit sözleşmesine](resource-limits-and-abuse.md), pahalı catch-up/import ise [ek risk onayına](../product/token-risk-and-approval.md) tabidir. Yüksek tüketim riski konuşma gecikti diye kendiliğinden onaylanmaz.

## 5. Kullanıcı ne görecek, neyi ölçeceğiz?

Proje kaynak görünümünde yetkili chat'ler, açık binding, ilgili konu/task bağlantıları ve her session için son receipt/son analiz, gap, bekleyen review bulunur. Task kartında “bu iş hangi chat/mesajlardan çıktı, hangi karar değiştirdi?” kaynakları görünür. Aynı anda açık chat'ler farklı snapshot'taysa bu fark belirtilir; host'taki görünümün gerçekten güncellendiği kanıtlanmadan “senkron” denmez.

P1 için ölçümler: capture gecikmesi, receipt→analysis p50/p95, uçtan uca review süresi ayrı, en eski queued iş, pending byte/tahmini token, gap/duplicate sayısı, proje başına adalet, maliyet ve kaynak→task ilişki doğruluğu. Test profilleri: kısa yoğun burst, sürekli yüksek yük, birkaç uzun chat, geç gelen/düzenlenen mesaj, provider yavaşlığı, onay bekleme, disk/queue dolması ve restart. Yük matrisi donanım, adapter/build, model, policy ve veri boyutlarıyla raporlanır.

Bugün “kaç chat/mesaj işleyebiliriz?” için ölçülmüş sayı yok. OPEN-12/16 kapsamında ilk pilot öncesi sonlu kapasite ve gecikme hedefleri seçilir. Kuyruğun test sonunda boşalması tek başına doğruluk değildir: mesaj/span korunumu, çift task üretmeme, karar sırası, ACL ve token tüketimi birlikte doğrulanır. Bu plan API'lerin tüm chat'lere erişebildiğini veya sınırsız capture sağladığını iddia etmez.

## 6. Planlı kabul senaryoları

| ID | Gözlenebilir kabul |
|---|---|
| CHAT-01 | İki chat aynı project ID'ye bağlanır; benzer adlı başka proje/kaynak izinsiz birleşmez; yeni session Q10-A/kapsam sınırına uyar |
| CHAT-02 | Aynı işin iki ifadesi kaynaklarını korur; otomatik çift canonical task yerine gerekçeli duplicate/refinement veya uncertain review oluşur |
| CHAT-03 | Farklı chat'lerde çelişen karar ve geç gelen eski mesaj onaylı kararı timestamp ile ezmez; yeni review/stale assessment gerekir |
| CHAT-04 | Konu/proje değişimi, belirsiz “bunu”, alıntı ve completion claim yanlış görev ataması veya insan onayı üretmez |
| CHAT-05 | Private chat özeti, başlık/sayım ve reason path diğer kullanıcı/agent context'ine sızmaz; yanlış binding düzeltmesi audit ve erişim invalidation taşır |
| CHAT-06 | Yeni brief yalnız yetkili ilgili bağlam/delta taşır; eski snapshot ile apply reddedilir; host'un okumadığı delta uygulanmış gösterilmez |
| LAG-01 | Sürekli mesaj akışında max-wait/byte sınırı flush üretir; session gap üzerinden processing watermark atlamaz |
| LAG-02 | Burst ve uzun yükte ölçülen throughput/lag raporlanır; yetişilemiyorsa pending görünür, sahte güncellik yok |
| LAG-03 | Queue/disk dolması ve replay'siz adapter senaryosunda receipt/gap doğru; önceden alınan işler korunur |
| LAG-04 | İki worker/restart/duplicate/fork kaynakları task/event etkisini çoğaltmaz; izinli provenance ayrı korunur |
| LAG-05 | Blocker önceliğinde diğer proje/geçmiş aç kalmaz; risk onayı/bütçe beklemek sessiz ücretli catch-up başlatmaz |
| LAG-06 | Gecikmiş/eksik ilgili bağlam final impact/ready/completion olarak sunulmaz; başka bağımsız iş gerekçesiz bloke edilmez |

T05d/T10b bağlama ve reconciliation, T18g context/source görünürlüğü, T06g/T24l yük ve coverage planını uygular. T02 capability deneyi gerçek erişim/geri oynatma sınırlarını önce belirler. Senaryolar **not_run**; bugünkü teslim dokümantasyondur, yeni engine veya otomatik host kontrolü değildir.

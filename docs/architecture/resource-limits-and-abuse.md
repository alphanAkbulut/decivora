# İşlem limitleri ve kötüye kullanım kontrolü

**14Ekim2026 — Sınırlı yerel kontroller kodlandı; tam kötüye kullanım/kapasite sözleşmesi öneridir.** Yerel HTTP32KiB JSON body/30yazma-dakika; stdioMCP32KiB giriş/16KiB tool-content/60çağrı-dakika-süreç; sınırlı graph/query/import/file/backup işlemleri ve managed parent-run rezervasyonları uygulanmıştır. Bunlar hardcoded yerel development tavanlarıdır; owner tarafından onaylanmış üretim SLO/dağıtık kota/provider harcama politikası değildir. Negatif regresyonlar ve [kısa karışık yük ölçümü](../quality/mixed-load.md) vardır; kapsamlı adversarial güvenlik testi, HTTP read/connection/deadline savunması ve gerçek provider bütçe enforcement tamamlanmadı. İlk load koşusundaki503açık güvenilirlik bulgusudur; doğrulanmış güvenlik açığı veya çözülmüş hata değildir. [Güncel kontrol matrisi](../quality/security-current-status.md). Kullanıcı işlem limitleri ve kötü niyetli kullanıma karşı önlem istedi. Aşağıdaki mekanizmalar teknik öneridir; sayısal eşikler, provider bütçesi veya otomatik hesap kapatma kararı kabul edilmiş sayılmaz. Tek kişilik pilotta da hatalı agent döngüsü aynı kaynak sorununu yaratabilir.

## 1. Neyi sınırlıyoruz?

| Kontrol | Kapsam ve birim | Koruduğu sınır |
|---|---|---|
| İstek hızı / burst | İşlem sınıfı başına istek/süre ve kısa sıçrama kapasitesi | Çok sık read/write/tool çağrısı |
| Eşzamanlılık | Aktif bağlantı, stream, job, runner ve model çağrısı sayısı | Uzun süren işlerin kaynakları tutması |
| İşlem büyüklüğü | Header/body byte, açılmış içerik byte, kayıt/batch sayısı, parse derinliği, cevap boyutu | Tek isteğin aşırı CPU/bellek tüketmesi |
| Hesaplama | Graph node/edge tarama, sorgu süresi, export sayfası, runner CPU/bellek/zamanı | Az sayıda pahalı istek |
| Kalıcı kapasite | Workspace/proje source, event, artifact, queue byte/sayı ve disk rezervi | Disk dolması ve sınırsız iş birikmesi |
| Harcama | Run/proje/workspace dönem bütçesi; token ve retry dahil çağrı sayısı | Agent fan-out ve üçüncü taraf maliyeti |
| DB transaction | Yazılan kayıt/byte, lock bekleme, yürütme süresi, açık snapshot yaşı | Uzun kilit ve yarım iş algısı |

İstek hızı, DB transaction ve harcama bütçesi aynı sayaç değildir. Bir istek çok sayıda alt işlem yaratabilir; admission batch büyüklüğünü ve maliyet sınıfını da hesaplar. Sayfa başına kayıt sınırı toplam sorgu/graph işini tek başına sınırlamaz. Admin olmak sınırsız kapasite anlamına gelmez.

## 2. Ortak sınırlar ve adil kullanım

- Kimlik doğrulamadan önce ucuz servis/bağlantı sınırı; gerekirse kaba IP sınırı uygulanır. IP tek kimlik değildir: aynı ağdaki insanlar ve localhost agent'ları bir IP paylaşabilir. Proxy header'ı yalnız tanımlı güvenilir proxy zincirinden kabul edilir.
- Kimlik doğrulandıktan sonra **principal + proje + workspace + kurulum** sınırlarının tümü geçerlidir. Token yenilemek veya yeni subagent açmak toplam bütçeyi sıfırlamaz. Alt run'lar parent run/sponsor toplamına da yazılır; bağımsız yeni run'lar dönem bütçesine tabidir.
- Read, import, impact, export, model ve runner ayrı maliyet sınıfıdır. Ucuz read hakkı pahalı iş başlatma hakkına dönüşmez. Yetki kontrolü ayrıca gerekir.
- Dış provider/account için projeler arasında ortak çıkış limiti bulunur. Provider'ın 429 vermesi kullanıcının kötü niyetli olduğunun kanıtı değildir. Retry, deadline ve `Retry-After` için [zamanlama sözleşmesi](execution-and-integrations.md) geçerlidir.
- Kuyrukta proje/workspace adaleti ve yaşlanan işlerin ilerlemesi gözetilir. Blocker önceliği başka tenant'ı aç bırakmaz, kapasite/izin tavanını aşmaz. Sağlık, yetki iptali ve iş durdurma için **ayrı ama yine sınırlı** kapasite ayrılır; bu yollar pahalı iş başlatamaz.

## 3. Kabulden çalıştırmaya kontrol sırası

1. Bağlantı, header, süre ve streaming body sınırını pahalı parse/DB/LLM işinden önce uygula. Desteklenmeyen sıkıştırmayı reddet; desteklenende açılmış byte ve işlem süresini de sınırla.
2. Kimliği ve erişim kapsamını doğrula; sınırlı parse/schema kontrolüyle hedef projeyi doğrula. Yetkisiz isteğe başka projenin varlığı, kotası veya idempotency sonucu açıklanmaz.
3. Principal/işlem hız sınırını uygula; yetkili scope içinde idempotency sonucunu kontrol et. Tekrarlanan istek request kapasitesi tüketir, **ikinci domain etkisi veya ikinci maliyet rezervasyonu yaratmaz**. Aynı key/farklı digest conflict'tir.
4. Yeni iş için byte/iş sayısı, queue/storage ve gereken maliyet kapasitesini atomik ayır. Admission reddi task durumunu değiştirmez; reddedilen payload/job başarılı alım gibi yazılmaz. Sınırlı güvenlik sayacı/audit ayrı olabilir.
5. Source/job için kalıcı commit sonrası receipt ver. Queue doluysa yeni receipt/offset ilerletme yok; adapter bounded spool, backpressure ve coverage açığını gösterir. Önceden kabul edilmiş iş limit düşmesiyle silinmez: aynı job kimliğiyle bekler veya `deferred` olur.
6. Worker dispatch ve domain commit aşamasında ilgili güncel izin/policy, fencing ve kapasite koşullarını yeniden denetle. Model öncesi atomik harcama rezervasyonu gerekir; timeout'ta bilinmeyen maliyet sıfır sayılmaz. Replay model/runner/dış teslim başlatmaz.

Request kabulü, job kabulü ve tamamlanma ayrıdır. Kayıp cevapta istemci aynı key/command ile sonucu sorgular; yeni işlem oluşturmaz. Durum sorguları da sınırlıdır. İptal isteği daha önce gönderilmiş provider çağrısının maliyetini geri almış sayılmaz.

## 4. DB transaction sınırı

LLM, dış API ve insan cevabı transaction içinde beklenmez. Büyük graph değerlendirmesi kısa snapshot/okuma üzerinden transaction dışında hazırlanır; apply sırasında revision ve onay digest'i yeniden denetlenir. Yazma işi kısa tutulur; yerel SQLite tek yazıcı planı korunur.

Lock bekleme, sorgu yürütme ve toplam transaction süresi ayrı parametrelerdir. Seçilen DB/driver'ın cancellation ve rollback davranışı T03/T08'de ölçülür; HTTP timeout DB işleminin durduğunu kanıtlamaz. Commit sonucu belirsizse `unknown`/durum sorgusu gerekir; kesin geri alınmış gibi rate-limit hatası verilmez.

Atomik onaylı change set sınırı aşıyorsa **sessizce bölünmez**: uygulanmadan açıklama döner, yeniden planlanmış proposal yeni digest/review gerektirir. Tarihsel source import'u mevcut süreklilik ve receipt/checkpoint kurallarıyla sınırlı parçalara ayrılabilir. Uzun read snapshot/cursor için ömür sınırı ve açık yeniden sorgulama davranışı gerekir.

SQL parametreli, sorgu biçimleri izinli olmalıdır; LLM metni SQL olarak çalıştırılmaz. SQLite engine limitleri kullanıcı/proje hız kotası yerine geçmez. Fiziksel DB'ye tam erişen OS/DB yöneticisini API limiter ile kısıtladığımız iddia edilmez.

## 5. Kötüye kullanım ve hatalı otomasyon

| Durum | Önlem ve istisna |
|---|---|
| İstek seli / pahalı batch | Ucuz erken admission, ağırlıklı işlem bütçesi, concurrency ve queue sınırı; batch içi iş sayısı da hesaplanır |
| Agent döngüsü / fan-out | Run/cause zinciri hop ve çocuk sayısı, ortak bütçe, toplam retry/deadline; yeni attempt bütçeyi sıfırlamaz |
| Büyük/derin/sıkıştırılmış içerik | Streaming byte, açılmış byte, derinlik, süre/bellek ve format allowlist; parse sonrası kontrol tek savunma değildir |
| Webhook tekrarı / sahte kaynak | Adapter'ın desteklediği imza/kimlik doğrulama, replay/dedup, bounded intake; geçerli imza sınırsız hak vermez |
| Prompt/SQL/path/URL manipülasyonu | Kaynak policy/komut olamaz; parametreli sorgu, source/path allowlist. URL alan adapter'da redirect/DNS/hedef doğrulaması; keyfi fetch açılmaz |
| Login/davet/reset kötüye kullanımı | Ekip yüzeyinde route + kimlik + kaba ağ kontrolü ve artan bekleme; başka kişiyi saldırıyla kalıcı kilitleyen otomatik hesap kapatma yok |
| Sayaç/log üzerinden bellek tüketimi | Sınırlı anahtar sayısı/TTL; key tahliyesi fail-open yaratmaz, aggregate üst sınır devrede kalır. Denial flood için bounded aggregate/drop sayacı; sınırsız audit satırı yok |
| Meşru yüksek kullanım / ortak ağ | Kademeli throttle/bekleme, güvenli neden ve yetkili inceleme yolu; trafik artışı tek başına kötü niyet etiketi değildir |

Tekrarlı ihlalde dar kapsamlı cooldown veya bağlantı pause önerilebilir; kalıcı hesap silme/cezalandırma otomatik değildir. Müdahale yetki, revision ve audit taşır. Ham prompt, credential, token veya başka tenant ayrıntısı loga girmez; [log sözleşmesi](logging-audit.md) geçerlidir.

İnternete açık gelecekteki kurulumda ağ/edge koruması ayrıca seçilir. Uygulama limiter'ı bant genişliğini tüketen DDoS'a karşı tek başına garanti vermez. Yerel auth/origin/CSRF kontrolleri de limiter ile ikame edilmez.

## 6. Tek servis ve büyüyen kurulum

P1'de tek yetkili admission noktası ve atomik güncellenen sınırlı token-bucket/concurrency sayaçları yeterli adaydır; Redis/Kafka zorunlu bağımlılık değildir. Restart yeni tam burst ödülü vermemeli: boş/kısıtlı başlangıç ve kontrollü dolum önerilir. Kalıcı job, idempotency, harcama ve storage muhasebesi yalnız bellekte tutulmaz; başlangıçta yeniden uzlaştırılır.

P4'te birden fazla replica öncesinde ortak atomik limit/rezervasyon otoritesi veya kanıtlanmış eşdeğer paylaşım gerekir. Her replica'ya tam kota vermek global limiti katlar. Sayaç arızasında pahalı işlem, mutation ve ücretli egress açılmaz; güvenli read-only mod ancak güncel yetki doğrulanabiliyorsa ve yerel sınırlı kapasiteyle çalışır. Backend seçimi C06 ölçümüyle yapılır; bugün ek servis kurulmaz.

## 7. Kullanıcı ve admin ne görecek?

| Önerilen sonuç | Davranış |
|---|---|
| `RATE_LIMITED` | HTTP yüzeyinde 429; biliniyorsa `Retry-After`. MCP stdio için structured tool sonucu ve `retry_after`; sahte HTTP cevabı değil |
| `PAYLOAD_TOO_LARGE` | İzinli büyüklük ve küçültme yolu; aynı payload'a kör retry yok |
| `QUEUE_FULL / SERVICE_BUSY` | Kapasite nedeniyle kabul edilememe; HTTP 503 adayı. Receipt yok, sınırlı backoff; her kapasite sorunu 429 değildir |
| `BUDGET_EXCEEDED / STORAGE_QUOTA_EXCEEDED` | Yetkili kapsam için neden ve çözüm; dönem/kapasite/policy değişmeden sonsuz retry yok |
| Kabul edilmiş job'da `retry_wait / deferred` | Aynı job, neden, varsa retry zamanı ve yeniden başlama koşulu; task otomatik failed/completed olmaz |

Kesin HTTP/MCP eşlemesi T04'te doğrulanır. Güvenli hata zarfı `code, request_ref, retryable, retry_after?, policy_revision` içerir; bilinmeyen süre uydurulmaz. İstemci `Retry-After`, backoff, jitter ve retry bütçesine uyar. Şiddetli aşırı yükte her bağlantıya ayrıntılı cevap garanti edilemez; belirsiz sonuç aynı kimlikle uzlaştırılır.

Admin; seçilmiş/etkin limit, kapsam, miras/tavan, kullanım + rezervasyon, kabul/ret sayacı, en eski iş ve limiter sağlığını görür. Normal kullanıcı yalnız kendi yetkili kapsamını görür. Limit artırımı kaynak/egress/runner iznini artırmaz. Parametre değişikliği önizleme + revision + audit taşır; limit düşüşü mevcut iş/maliyet kaydını silmez. [Parametre sicili](../product/administration-and-operations.md) aynı yönetim yüzeyidir; ayrı bir backoffice ürünü değildir.

## 8. Eşik seçimi, faz ve doğrulama

İlk dış girdi alan P1 runtime'da request/body/queue/concurrency kontrolü bulunur. İlk model dispatch'inden önce bütçe guard bulunur. P4 yalnız dağıtık sayaç, ekip login ve hosted edge ayrıntısını tamamlar; temel koruma ertelenmez.

Her parametre için kapsam, birim, sonlu aralık, aşım davranışı, sahibi, effective revision ve restart davranışı yazılır. Eşikler **OPEN-12/16 kapsamında seçilmedi**. Mevcut token/zamanlama deney adayları korunur; ölçülmüş güvenli varsayılan değildir. T04/T06 sentetik baseline ile ilk sonlu değerleri belirler; gerçek pilot bunların yük ve limit-aşımı kanıtı olmadan açılmaz. Provider harcaması ayrıca Q03/OPEN-10'a bağlıdır.

Ölçüm: meşru burst/import kabul ve ret oranı, queue yaşı/adalet, p95 gecikme, CPU/bellek/disk, DB lock/rollback süresi, limiter maliyeti, yanlış throttle, bounded log kaybı ve harcama. Ortam, hacim, concurrency ve policy revision raporlanır. Bugün kapasite/saldırı dayanımı sayısı yoktur.

| ID | Planlanan kabul senaryosu |
|---|---|
| LIM-01 | Paralel isteklerde atomik rate/concurrency tavanı aşılmaz; slot hata/cancel sonrası kontrollü bırakılır |
| LIM-02 | Token rotasyonu, child agent ve yeni run ortak dönem limitini aşamaz; başka tenant'ın kullanımını okuyamaz |
| LIM-03 | Pahalı batch/graph/export işlem/byte/traversal bütçesine uyar; incomplete sonuç tam analiz sayılmaz |
| LIM-04 | Büyük/derin/sıkıştırılmış sentetik input erken durur; ret LLM/runner başlatmaz |
| LIM-05 | Queue/disk doluyken sahte receipt/offset ilerlemesi yok; kayıp cevap + aynı key ikinci domain etkisi üretmez |
| LIM-06 | Lock/query/commit hata enjeksiyonunda rollback ile belirsiz commit ayrılır; change set kısmi uygulanmaz |
| LIM-07 | Paralel bütçe rezervasyonu ve provider timeout/retry toplam tavanı korur; unknown usage serbest bütçe değildir |
| LIM-08 | Restart, sayaç anahtarı taşması ve limiter arızası bypass yaratmaz; dağıtık kısmı P4'e açık not_run |
| LIM-09 | Meşru burst/ortak IP ve gürültülü tenant altında bounded revoke/cancel çalışır; diğer projeler aç kalmaz |
| LIM-10 | Denial flood log/belleği sınırsız büyütmez; provider 429 ban'a dönüşmez; UI neden/limit/retry koşulunu gösterir |

Bu tablo test sonucu değildir. Sentetik testler uygulama dilimiyle yazılır; dış servise saldırı veya izinsiz yük testi yapılmaz. [Backlog](../delivery/backlog.md) T04d/T06f/T08c/T24j; P4 C06 dağıtık doğrulama kapısıdır.

## Kaynak, tercih ve alternatif

- [OWASP API4:2023](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/) süre, payload/batch, kaynak ve provider maliyetini de sınırlamayı önerir. **Uyarlamamız:** ortak insan/agent bütçesi, receipt kaybetmeyen admission ve bounded işler. IP-only veya yalnız token kotası bu yüzden yeterli görülmedi.
- [RFC 6585 §4 ve §7.2](https://www.rfc-editor.org/rfc/rfc6585.html#section-4) 429 ve isteğe bağlı Retry-After'ı tanımlar; aşırı yükte cevap üretmenin de maliyeti olduğunu belirtir. **Tercihimiz:** rate, kapasite ve bütçe hatalarını ayırmak, client retry'ını sınırlamak.
- [SQLite limits](https://www.sqlite.org/limits.html) engine limitlerini açıklar. **Çıkarımımız:** DB sınırlarını uygulama admission/tenant bütçesiyle tamamlamak; distributed limiter servisini P1'e zorunlu eklemek için henüz ölçüm kanıtı yoktur.

Kaynaklar 2026-10-10'da kontrol edildi. Bunlar Decivora güvenliğinin sertifikası veya çalıştırılmış benchmark değildir.

# Düzenli yakalama — kod teslimi ve takip kapıları

**20 Ekim 2026 · Sprint1 · T17/T19/T22/T23.** İstenen: seçilmiş Codex sohbetlerinin kullanıcı her defasında Read düğmesine basmadan açık bir süre/aralık/read sınırı içinde yerel kaydedilmesi. [Mimari ve sequence](../architecture/codex-source-onboarding.md#düzenli-seçili-sohbet-yakalama--uygulanan-yerel-kod).

## Kodlandı

- Mevcut capture consent'e bağlı immutable plan; create okumaz, ayrı human Start gerekir.
- Kalıcı tick/read claim ve toplam sayaç; limit, expiry, authority değişimi, disconnect, crash ve hata yeni okumayı durdurur.
- Worker stop/shutdown event'i sonraki checkpoint'te kontrol edilir; önceki kabul edilmiş sayfalar silinmez. Harici host çağrısının anında iptal edildiği iddia edilmez.
- Sources ekranında plan/start/stop, durum ve refresh; operasyon izinde content-free capture_tick.
- Restart sayaçları korur ama thread'i başlatmaz. Bir capture worker ve bir model worker aynı yerel süreç içindedir; mikroservis dağıtımı eklenmedi.
- Yeni kaynaklar model izni kazanmaz, Task/status otomatik uygulanmaz. Yeni model çağrısı/gerçek chat read bu geliştirmede0.

## Bulgular ve düzeltmeler

1. Tek-read iznini her tick'te yeniden kullanmak yerine aynı kalıcı read sayacı kullanıldı; yeni schedule eski kullanımı sıfırlamaz. Parallel worker/manual read claim kontrolü korunur.
2. Yalnız bekleme event'ini kesmek in-flight checkpoint'i durdurmaya yetmiyordu. İç guard hem plan stop/expiry'sini hem worker cancellation'ını commit öncesi kontrol eder. Stop sırasında host beklemesi için iki ayrı negatif test vardır.
3. Yanlış schedule digest'iyle stop reddedildiğinde worker cancellation yapılmamalı. Cancel yalnız başarılı owner/digest stop kaydından sonra çalışır; negatif test eklendi.
4. Son izinli tick sonrası worker gereksiz interval beklememeli. Son başarılı tick ile Limit reached'e geçip çıkar.
5. İlk full-runtime denemesinin HTTP testleri sandbox port yasağıyla çalışamadı; test kapsamı daraltılmadı, aynı suite yerel port izniyle tekrar çalıştırıldı.
6. İlk tarayıcı harness'i worker bitişini erken kabul etti; kayıtlı tick sayısı ve worker active=false birlikte, sınırlı read-only polling ile kontrol edildi. Backend sayacı değiştirilmedi. Son tarayıcı kabulünde iki ayrı sentetik mesaj iki interval okumasıyla kaydedildi.

## Kanıt ve sınır

Yeni runtime senaryoları: create≠read, exact consent/digest, remaining read/expiry/interval, idempotent plan/no reset, aynı connection'da duplicate schedule, dedup, restart-no-autostart, failed/unfinished no-retry, authority değişimi, disconnect, in-flight stop/cancel, ikinci worker/manual read yarışı ve content-free log. Gerçek tarayıcıda config→ayrı start→iki otomatik tick→iki source→limit→stop→reload ve390px taşma/page-error0 kontrol edildi. Fake native host kullanıldı; gerçek Codex periyodik oturum kabulü değildir.

EN/TR yeni metinler vardır; ES/PT-BR/AR bu yeni kontrollere İngilizce fallback kullanır. Native çeviri kalitesi doğrulanmadı. Kullanıcıya otomatik polling/UI canlı güncelleme vaat edilmedi; Refresh processing state mevcut durumu okur.

## Sonraki somut kapılar

- Yeni exact gerçek sohbet için periyodik yerel read izni; süre, interval ve toplam read sayısı owner tarafından açıkça belirlenmeli. Önceki tek-read izinleri yenilenmedi.
- Seçili kaynaklarda yeni mesajların hangi kapsamda modele paylaşılabileceği; exact source grants otomatik genişletilmedi. Capture ile ücretli extraction ayrı kalır.
- Büyük/yoğun canlı sohbetlerde checkpoint continuity/backfill ve günlük kabul; mevcut bounded kaynak dışındaki history okunmuş sayılmaz.
- Pending/failed okumalar için güvenilir recovery UX; bu teslim crash sonrası kör devam yerine review ile durur.

Ana T17 kapanışı bu sentetik döngüyle ilan edilmedi. Mevcut capture/onboarding kodu yeniden açık eksik diye sayılmamalı; kalanlar gerçek periyodik native kabul ve birleşik günlük akıştır.


**Son doğrulama:**692runtime (12yeni scheduled-capture testi) ve49repo testi geçti. Sentetik iki-tick browser akışı, önceki native tek-read regresyonu ve5locale/RTL/draft kontrolleri geçti. Son Refresh kontrolünde yeni plan formunun taslağı/açık bölümü de korundu.63Mermaid/34belge offline render edildi; yeni sequence tam görüntüsü incelendi. LOCAL53610veTEST53611yedeklenip idle durumda yeniden başlatıldı; tüm uygulama tablolarının fingerprint'leri aynı, capture schedule0 ve her iki worker kapalı. API root54dispatch/108HTTP/$0.067895 olarak değişmedi. Gerçek periyodik native okuma yapılmadı.

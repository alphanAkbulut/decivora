# Konuşma kaynağından analiz kuyruğuna ve incelemeye

**19 Ekim 2026 — T09/T17/T19/T21/T22/T23 çalışan bağlantı dilimi.** Kullanıcı ana otomatik zincirin tamamlanmasını istedi. Source→kalıcı outbox→izinli bounded worker→mevcut proposal review bağlantısı ve Conversations/Operations ilerleme görünümü kodlandı. Tam MVP, sürekli native izleme veya gerçek konuşmaların API'ye gönderilmesi açılmadı.

## Kullanıcının göreceği davranış

Conversations üstündeki **Conversation processing** kartı kaydedilen kaynakları, analiz bekleyenleri, incelemeye hazır olanları, başarısız/belirsiz analizleri ve en az bir adayı uygulanmış kaynak sayısını gösterir. Operations aynı içeriksiz özeti sunar. Applied source sayısı bütün önerilerin veya görev kabulünün tamamlandığı anlamına gelmez; incelemeye hazır ve uygulanmış sayaçları birbirini dışlamaz. Bilinmeyen toplam için yüzde yoktur.

**Process authorized queue** bir bounded geçiştir; her tıklamada en fazla1kaynak dener. Model yapılandırılmamışsa düğme kapalıdır. Modelin yapılandırılmış olması kaynak paylaşım izni değildir: kaynak+hash, provider/model, context snapshot, authz revision, bütçe ve süre kontrolü mevcut `ConversationService.analyze` içinde korunur. HTTP command tam `action/limit` alanlarını kabul eder; limit1–10. Kaynağa uygun grant yoksa provider kurulmaz/çağrılmaz. Kullanıcı metni grant veya çalışma komutu üretemez.

## Kalıcı kayıt ve işleme

- Yeni maskelenmiş source receipt ile `conversation_enqueued` aynı transaction içinde yazılır. Outbox yalnız source ID/hash/zaman/state referansı taşır, metni çoğaltmaz. Outbox yazımı başarısızsa kaynak da rollback olur; native sayfa checkpoint'i aynı transaction kapsamında kalır.
- Önceki sources kaybolmaz: outbox öncesi kaynaklar salt okunur görünümden bulunur, `durable_outbox=false` ile ayrılır. Geçmiş audit veya gerçek DB yeniden yazılmaz. SQL schema ve runtime bağımlılığı değişmedi.
- `ConversationQueue.process` mevcut kaynakları sırayla, seçili proje ve güncel insan yetkisiyle değerlendirir. Trusted factory yalnız zaten geçerli grant için çağrılır. Yerel UI mevcut configured extractor'ının exact grant kimliğini eşleştirir; otomatik grant yaratmaz veya başka kaynağa uyarlamaz.
- Gerçek host/model çağrıları SQLite transaction dışında kalır. `conversation_analysis_started` kalıcı olduktan sonra sonuç gelmemişse **Analysis unknown** gösterilir ve worker yeniden dispatch etmez. Failed output, unknown usage veya overrun aynı pass içinde sonraki dispatch'i durdurur; mevcut ortak bütçe kuralları geçerlidir.
- Geçerli sonuç mevcut `conversation_analysis_finished` ve review yollarına gider. Capture/worker canonical Task oluşturmaz. Aday seçimi ve ayrı insan kabulü Task'ı oluşturur; task completion/AC/DoD başka kapıdır. Tamamlanan analiz tekrar çağrılmaz.

## Native capture tanısı

Seçilmiş Codex CLI okuma pass'i aynı DB yanındaki private `.operations.sqlite` dosyasına `native_capture` run + capture/execute_command span yazar. Başarı, süre, operation-ID, workspace/actor/authz revision ve allowlist hata kodu kalıcıdır. `capture_limit`, `codex_read_timeout`, `invalid_codex_cursor`, `capture_checkpoint_stale`, `capture_item_changed` gibi kodlar `application_error` altında kaybolmaz. Kaynak/şifre/tool/reasoning/provider hata metni tanıya yazılmaz.

Bu trace, bounded collect sınırıdır; her RPC/sayfa/model aşamasının ayrı span'ı değildir. App Server başlatma öncesi hatalar hâlâ CLI güvenli hata çıktısındadır. Sidecar yazım arızası canonical kabulü veya yetkiyi değiştirmez. `native_capture=false` ana uygulamanın native arka plan worker'ı çalıştırmadığını belirtir; ayrı CLI'nin geçmiş trace'lerini reddetmez. Normal workspace yedeği sidecar'ı kapsamaz.

## Doğrulama ve sınırlar

Sentetik kontroller: source/outbox atomic rollback ve dedup; read-only privacy; model/grant yokken sıfır çağrı; worker→source-bound proposal→ayrı human accept ile Task; unknown dispatch tekrarının önlenmesi; batch/unknown usage durması; backup/restore; proje/limit guard; UI command/Operations; gerçek stdio fixture'ında native success/failure trace ve içerik sızmaması. Browser dialogue fixture kaynaklı görev/durum akışını, yeni queue kartını, disabled default dispatch ve Operations görünümünü çalıştırır. Bunlar provider anlam doğruluğu veya yeni gerçek source izni değildir.

İlk doğrulamada Operations DTO şemasının yeni alanı eksikti; şema güncellendi. Yeni browser assertion'da yerel değişken adı çakıştı; kontrol betiği düzeltildi. Assertion kaldırılmadı, model/yetki sınırı gevşetilmedi. Son sonuçlar aşağıda kaydedilir.

**Açık kalan gerçek iş:**32source kapasitesi ve audit taramasının indeksli/paged depoya geçişi; source-specific grant/aktivasyon onboarding; per-source configured transport ve devamlı yetkili worker; live/backfill adaleti; capture pause/revoke/gap kartı ve daha ayrıntılı trace. Gerçek source model paylaşımı için ayrı izin, gerçek host yeniden okuması için yeni dar kapsam gerekir. Bu teslim bunları yapılmış göstermez; T17/T09/T19 ve MVP kapıları açık kalır.

Son doğrulama:524runtime ve48tracker/araç testi geçti.12browser senaryosunun11'i ilk koşuda geçti; yeni diyalog assertion betiğindeki ad çakışması düzeltildikten sonra diyalog senaryosu da geçti. Model dispatch0; yeni queue/Operations kartları ve mobil taşmama kontrol edildi.50diagram render edildi. Yerel normal/TEST uygulama verileri bu testlerde kullanılmadı veya yeniden yazılmadı; çalışan eski süreçler otomatik olarak hot-reload olmuş sayılmaz.

Yerel TEST deployment readback: `ce81f52938fd1e36b016fd0b92f61edceb230174` kodu53611üzerinde özel SQLite yedeği alınarak yeniden başlatıldı.6mevcut source/0task korundu; yeni queue görünümü6Waiting for model gösterdi, model kapalı. Önce/sonra canonical DB mantıksal dump hash'i eşleşti. Normal53610süreci değiştirilmedi. TEST tarayıcısı yeni ephemeral oturumla açıldı; hiçbir gerçek kaynak yeniden okunmadı veya API'ye gönderilmedi.

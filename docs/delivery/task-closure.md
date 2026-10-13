# Çekirdek teslim, entegrasyon ve ürün kabulü

**Q16-A kabul edildi ve uygulanıyor.** Owner “önerini de uygulayalım” dedi. [Manifest](task-closure.json), [otomatik kontrol](../../scripts/check_task_closure.py), [6 negatif/pozitif test](../../tests/test_task_closure.py). Yeni feature/task ID üretilmedi; mevcut30 ana/129 backlog+team-data alt kaydı kullanılır.129, eski backlog-only117 envantere12 mevcut team-data tanımının eklenmesidir;12 yeni iş değildir.

## Kapanış kuralı

Ana görev, manifestte kendi çekirdek kabulü ve zorunlu task-local işlerinin kanıtıyla kapanır. Başka modüle bağlı integration/release işinin sahibi ve first-use kapısı açık kaydedilir; ilgili sahip görevin kapanışında kontrol edilir. PROPOSED iş onaylı zorunlu kapsam değildir. First-use izin/ACL/limit/audit/veri koruması geçmeden ilgili kabiliyet açılmaz; modülün Done olması activation izni vermez.14MVP AC korunur.

| Mevcut alt iş | Kapanış sahibi / kapı | Korunan gerçek eksik |
|---|---|---|
| T04a genel command/query contract | T08 | T04 bounded source/startup kabulü geniş sözleşmeyi bitirmez |
| T04b network ingress güvenliği | T06, network ilk kullanımı | Disabled transport sessizce açılamaz |
| T04c fiziksel ER/event ilişki kontratı | T07 | Kalıcı event/relation DB öncesi test gerekir |
| T04d admission/transport limitleri | T06 | İlk ingress admission geçmeden receipt yok |
| T05d cross-source/record ilişki entegrasyonu | T10, T08b policy sonrası | T06 source/session pinlemesi ayrıca kendi kabulüdür; ACL atlanmaz |
| T07b command+security audit atomikliği | T08 | Domain apply audit ile birlikte geçmeli; log core bitişi tek başına yetmez |
| T18g resume envanter UI entegrasyonu | T20 | MCP retrieval ACL/limitleri önceden kendi göreviyle geçmeli |

Diğer mevcut alt işler task-local veya kayıtlı PROPOSED sınıfında tutulur. Sahiplik gereksinimden bağımsız yeni öncelik/özellik yaratmaz. `parent` kaynak aileyi, `owner` tamamlanmayı değerlendiren görevi, `first_use_gate` kullanım öncesi sorumluluğu gösterir. Slash'tan sonraki exact parent containment olabilir; gerçek teknik bağımlılık diye self-cycle üretilmez. Entegrasyon sahibine verilen alt iş, sahibi Done olurken hâlâ açıksa validator reddeder.

## Mevcut kapanışlar

T04 startup/source-contract kapsamı Done; mevcut12test kabul raporu korunur. T04a/b/c/d tamamlanmış sayılmadı; açık durumları ve sorumluları manifestte görülür. T05f/g/h Done, T05 parent In Progress: T05a/b/c core kalanları hâlâ açık; bu politika T05'i otomatik kapatmaz. T05e PROPOSED kendi statüsünü korur. T05d downstream entegrasyonu parent kapanışını döngüye sokmaz. T01 gold/T02 actual capture/T03 semantic-native-ROI açık kanıt kapılarıdır, Q15 core build başlangıcını tekrar bekletmez.

## Kontrolün kapsamı ve sınırı

Validator canonical acceptance/status/dependency değişimini, eksik cross-file alt işi, sınıflandırma/owner/gate kaybını, Done için eksik evidence/unfinished required child ve kapanış graph cycle'ını reddeder. Evidence dosyasının varlığı ve scoped_verified kaydı runtime doğruluğu değildir; runtime test/gerçek hedef/ürün AC ayrı değerlendirilir. İlk kullanımın çalışırken authorization enforcement'ı bu planning script tarafından yapılmaz. Actual product closure motoru değildir; development CI korumasıdır.

Yeni eksik eklemeden mevcut kayıt/kanıt/kararı kontrol et. Kalan işi aynı ID'de kanıt ve doğru sahibiyle güncelle; scope değişimi gerçekten yeni gerekliyse somut gerekçeyle ayrı öner. Manifest status kayıtları kanıt yerine geçmez; source row değiştiğinde manifest aynı review'da eşleşmeli. Kaynak metinleri/historical proof'ları yeniden yazıp başarı üretme. Bu kontrol görev/scope/kanıt değişiminde veya kapanışta çalışır, her sohbet mesajında bütün repo taraması istemez.

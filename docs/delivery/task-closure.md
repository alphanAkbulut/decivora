# Çekirdek teslim, entegrasyon ve ürün kabulü

**Q16-A kabul edildi ve uygulanıyor.** Owner “önerini de uygulayalım” dedi. [Manifest](task-closure.json), [otomatik kontrol](../../scripts/check_task_closure.py), [kapanış regresyon kontrolleri](../../tests/test_task_closure.py). Yeni feature/task ID üretilmedi; mevcut30 ana/129 backlog+team-data alt kaydı kullanılır.129, eski backlog-only117 envantere12 mevcut team-data tanımının eklenmesidir;12 yeni iş değildir.

## Kapanış kuralı

Ana görev, manifestte kendi çekirdek kabulü ve zorunlu task-local işlerinin kanıtıyla kapanır. Başka modüle bağlı integration/release işinin sahibi ve first-use kapısı açık kaydedilir; ilgili sahip görevin kapanışında kontrol edilir. PROPOSED iş onaylı zorunlu kapsam değildir. First-use izin/ACL/limit/audit/veri koruması geçmeden ilgili kabiliyet açılmaz; modülün Done olması activation izni vermez.14MVP AC korunur.

| Mevcut alt iş | Kapanış sahibi / kapı | Korunan gerçek eksik |
|---|---|---|
| T04a genel command/query contract | T08 | T04 bounded source/startup kabulü geniş sözleşmeyi bitirmez |
| T04b network/native ingress güvenliği | T16, ilk native/network activation | Disabled transport sessizce açılamaz |
| T04c fiziksel ER/event ilişki kontratı | T07 | Kalıcı event/relation DB öncesi test gerekir |
| T04d admission/transport limitleri | T06 | İlk ingress admission geçmeden receipt yok |
| T05d cross-source/record ilişki entegrasyonu | T10, T08b policy sonrası | T06 source/session pinlemesi ayrıca kendi kabulüdür; ACL atlanmaz |
| T07b command+security audit atomikliği | T08 | Domain apply audit ile birlikte geçmeli; log core bitişi tek başına yetmez |
| T18g resume envanter UI entegrasyonu | T20 | MCP retrieval ACL/limitleri önceden kendi göreviyle geçmeli |

Diğer mevcut alt işler task-local veya kayıtlı PROPOSED sınıfında tutulur. Sahiplik gereksinimden bağımsız yeni öncelik/özellik yaratmaz. `parent` kaynak aileyi, `owner` tamamlanmayı değerlendiren görevi, `first_use_gate` kullanım öncesi sorumluluğu gösterir. Slash'tan sonraki exact parent containment olabilir; gerçek teknik bağımlılık diye self-cycle üretilmez. Entegrasyon sahibine verilen alt iş, sahibi Done olurken hâlâ açıksa validator reddeder.

## Mevcut kapanışlar

T04 startup/source-contract kapsamı Done; mevcut12test kabul raporu korunur. Güncel olarak T04a/c/d kendi alt kabulüyle Done, T04b native first-use kapsamı In Progress; sahipleri ve kanıtları manifestte görülür. T05f/g/h/c ve T05a/b scoped core kanıtları toplu teslimle tamamlandı; T05 parent kendi normalized identity/binding/quarantine/query kabulüyle Done oldu. T06/T07/T08/T11 çekirdekleri de [toplu test](../quality/integrated-core.md) kanıtıyla kapandı; policy otomatik state üretemez. T05e PROPOSED kendi statüsünü korur. T05d downstream entegrasyonu parent kapanışını döngüye sokmaz. T01 gold/T02 actual capture/T03 semantic-native-ROI açık kanıt kapılarıdır, Q15 core build başlangıcını tekrar bekletmez.

## Kontrolün kapsamı ve sınırı

Validator canonical acceptance/status/dependency değişimini, eksik cross-file alt işi, sınıflandırma/owner/gate kaybını, Done için eksik evidence/unfinished required child ve kapanış graph cycle'ını reddeder. Evidence dosyasının varlığı ve scoped_verified kaydı runtime doğruluğu değildir; runtime test/gerçek hedef/ürün AC ayrı değerlendirilir. İlk kullanımın çalışırken authorization enforcement'ı bu planning script tarafından yapılmaz. Actual product closure motoru değildir; development CI korumasıdır.

Yeni eksik eklemeden mevcut kayıt/kanıt/kararı kontrol et. Kalan işi aynı ID'de kanıt ve doğru sahibiyle güncelle; scope değişimi gerçekten yeni gerekliyse somut gerekçeyle ayrı öner. Manifest status kayıtları kanıt yerine geçmez; source row değiştiğinde manifest aynı review'da eşleşmeli. Kaynak metinleri/historical proof'ları yeniden yazıp başarı üretme. Bu kontrol görev/scope/kanıt değişiminde veya kapanışta çalışır, her sohbet mesajında bütün repo taraması istemez.

Toplu manual/synthetic profile network ingress açmadığı için T04b owner/first-use T16 olarak netleştirildi; gereksinim ve açık durum korunur. T09/T10 kalite işleri bitmeden typed/manual graph kernel test edilebilir; plan sırası gerçek çalışma engeli değildir, full14MVP AC karşılanmış sayılmaz.

19Ekim [satır bazlı durum teyidi](../quality/task-status-audit.md)30ana/129alt kaydı kapsar. Checker artık canonical UNSPECIFIED durumunu, eksik/tekrarlı audit satırını, durum-audit uyumsuzluğunu ve eksik evidence yolunu reddeder. Kanıt yolunun varlığı semantik doğruluk veya ürün kabulünün yerine geçmez; açık kalan kabul audit'te ayrı yazılır.

## Kapanışlar final güne yığılmayacak

[20 Ekim retrospektifi](../quality/delivery-flow-retrospective.md), geniş paket/küçük teslim ayrımını ve yanlış raporlama etkisini inceler. Alt dilim kabulü tamamlandığında ilgili mevcut kayıt kapanır; parent kendi core/required setiyle aynı teslimde değerlendirilir. Eksik varsa exact ID ve neden görünür kalır. Başka release veya gelecek-faz işini kapatma bahanesiyle kanıtlı alt teslim açık tutulmaz.

Bir ortak entegrasyon birkaç parent'ın son eksiğini aynı anda giderirse ayrı kriter/evidence kontrolleriyle birkaç kapanış olabilir. Bu, toplu otomatik Done değildir. Sonraki modüle bağlı gereksinim atlanmaz; owner/first-use gate zaten manifestte açık tutulur. Bu açıklama kabul, sahiplik, statü veya 14 MVP kriterini değiştirmez.

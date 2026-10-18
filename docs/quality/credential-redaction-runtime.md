# Konuşma sırları, DB ve log sınırı

**19 Ekim2026 — uygulanmış dar koruma; tam DLP, secret vault veya şifreli DB değildir.** Kullanıcı konuşmadaki key/password değerlerinin maskelenmesini ve DB/log önlemlerini istedi. T06/T09/T18/T22/T23/T24 altında mevcut mahremiyet şartının uygulamasıdır; yeni ücret, collector, veri erişimi veya policy istisnası getirmez.

## Gözlenen yol ve düzeltme

Önce `ConversationService.ingest`, izinli konuşma metnini aynen `conversation_imported` audit kaydında saklıyordu. Private DB ve erişim kontrolü vardı; credential redaction yoktu. Hazırlanan model isteği bu kaynağı alıyor, raw provider/import output'u da analiz geçmişine yazılabiliyordu. Operational log zaten prompt/body/exception yerine allowlisted action/code tutuyordu. Bu bir repo kapsamlı güvenlik taraması değildir; kullanıcının belirttiği credential veri akışı incelendi.

| Sınır | Yeni davranış | Sınır / doğrulanmayan |
|---|---|---|
| Manuel konuşma girişi | Bilinen credential span'leri `[REDACTED]` yapılır, **sonra** kaynak ID/hash/dedup hesaplanır | Orijinal metin veya orijinal secret hash'i saklanmaz. Kaynak artık sanitized representation'dır; orijinal dosyanın fingerprint'i değildir |
| Kaynak kanıtı | Quote/span/hash maskelenmiş metne aittir. `redaction.policy/counts/original_retained` içeriksiz metadata taşır | Aynı bağlamda yalnız password farklıysa aynı sanitized kaynak olabilir; bu fark bilerek tutulmaz. Aynı maskeli quote tekrar ediyorsa unique-quote guard hâlâ reddeder |
| Model çıktısı / dış JSON import | Tanınan sır içeren structured output reddedilir. Failed provider output'un secret raw metni/hash'i saklanmaz | Parse/schema/source validity ayrı; sessizce temizleyip orijinal model kanıtıymış gibi gösterme yok |
| Model isteği / eski context | Kaynak ve context çıkışta tekrar kontrol edilir; tanınan sır varsa hazırlama/dispatch durur | Eski canonical geçmiş otomatik yeniden yazılmaz. Kaynak/model/bütçe izni yine ayrı |
| Native SourceEvent scaffold | Credential içeren event text kalıcı receipt öncesi reddedilir; session/project/event ID metadata'sı değiştirilmez | Bu synthetic scaffold'dur, gerçek native capture kabulü değildir; bu yola sanitize/revision adapter'ı ayrıca bağlanmalı |
| Yeni canonical task/body, soru ve LocalApp komutları | Tanınan sır içeren içerik reddedilir; kullanıcı önce redact eder | Bu vault değildir. Tüm doğrudan internal SQL yazımlarına evrensel DB-level içerik sınıflandırıcısı eklenmedi |
| MCP | Tool input ve görünür record/model context'i kontrol edilir; tanınan sır geçmez | Secret içeren eski kayıt düzeltmeden başka agent'a açılmaz; source-audience mahremiyet filtresi ayrıca korunur |
| HTTP JSON / UI | Display-only savunma maskelemesi; sanitized source uyarısı, gizli bilgi içeren import taslağının maskelenmiş karşılıkla değiştirilmesi | Display dönüşümü canonical veri veya onay payload'ının yeni sürümü değildir; browser/clipboard/OS geçmişinin temizlendiği iddia edilmez |
| Operations | İçeriksiz allowlist log devam eder; `sensitive_content` güvenli hata kodudur | Gövde/secret/ham exception kaydı eklenmedi. Operational sidecar canonical security audit değildir |
| DB dosyaları | POSIX'te canonical/diagnostics ve mevcut `-wal/-shm/-journal` dosyaları en fazla600iznine daraltılır (mevcut owner-read-only korunur); symlink sidecar açılmaz | ACL, admin/root, OS yedekleri veya disk imajına karşı koruma değildir. Windows ACL uygulaması yok; DB SQLCipher ile şifrelenmedi |

Kod: [detector/maskeleme](../../packages/privacy/secrets.py), [DB dosya izni](../../packages/storage/private_files.py), [kaynak yolu](../../packages/capture/conversations.py), [testler](../../tests/runtime/test_secret_privacy.py).

## Neleri tanıyor, neleri tanımıyor?

Policy `decivora-credential-redaction-1`: açık password/passwd/pwd/parola/şifre, API/client/private/secret key, access/refresh/session token ve credential atamaları; bilinen provider key prefix'leri; Bearer/JWT; URL userinfo parolası; PEM private key bloğu; Authorization/Cookie/Set-Cookie header'ı. JSON-escaped Unicode değerler parse sonrası kontrol edilir; tek/çift/backtick alıntı ve multiline password örnekleri testlidir. Tamamlanmamış private key başlangıcı metnin kalanını ihtiyatla maskeler.

`TASK-123`, `Q_STORE`, source/event/project ID ve hash'ler sır olarak otomatik silinmez. Client ID tek başına client secret değildir. Bir ID gerçekten oturum credential'ıysa etiketli session/token kuralı uygulanır. Her uzun rastgele sayı/string'i credential saymıyoruz. Tüm müşteri/işlem/kişisel kimlikleri için PII sınıflandırma politikası bu teslim değildir.

Regex deterministiktir ve local çalışır; model/token çağrısı gerektirmez. Bilinmeyen provider biçimi, etiketsiz parola, base64/özel encoding, görsel veya çok mesajda parçalanmış sır kaçabilir; false positive de mümkündür. Maskeleme UI uyarısı ve kod policy revision'ı bu yüzden görünürdür. Kullanıcı yine de gerçek sır göndermemelidir; tespit edilmiş olması credential'ın dışarıda sızmadığını veya geçerli olmadığını kanıtlamaz.

## Geçmiş DB, WAL ve yedekler

**Geçmiş veriler ve yedekler temizlenmiş sayılmaz.** Bu geliştirme gerçek konuşmaları otomatik taramadı, orijinal event/audit geçmişini silmedi veya WAL/vacuum/purge çalıştırmadı. Eski içerik display'de maskelenebilir ve model/MCP çıkışında durabilir; fiziksel dosyada bulunmaya devam edebilir. Mevcut private backup bütün workspace'i içerir ve şifresizdir; geçmiş sır varsa kopyası yedekte de olabilir. Yeni sanitized-source testi yalnız yeni sentetik DB/backup için sekret bulunmadığını doğrular, gerçek eski yedeklere genellenmez.

Geçmiş sır şüphesinde sonraki somut iş: owner kapsamıyla salt okunur envanter (**yalnız sayım/kategori, değer yok**) → affected source/ref ve yedek kapsamı → credential'ın ilgili sağlayıcıda rotation/revocation planı → append-only/privacy yönetişimine uygun kontrollü migration/purge/restore testi. Gerçek credential iptali, orijinal geçmişi silme veya yedekleri yok etme ayrıca açık kapsam/izin gerektirir. Varsayılan runtime yeni bir scan/rotation/üçüncü taraf upload başlatmaz.

Şifreleme-at-rest, anahtar yaşam döngüsü/OS keychain, backup encryption, TTL/purge/restore ve takım/tenant yetkileri mevcut ayrı kapılardır.600dosya izni, şifreleme veya eksiksiz tenant izolasyonu yerine geçmez.

## İnceleme ve doğrulama sınırı

Bağımsız read-only investigator başlatma girişimi model kapasitesi nedeniyle çalışmadı. Yönergenin izin verdiği alternatif olarak source→sink ve ayrı bypass/regression geçişleri ana agent tarafından yapıldı; bağımsız insan/agent review yapılmış sayılmaz. Sibling yollarında native text, structured provider output, prepared context, MCP exact get_record ve HTTP display ayrıca incelendi. Testler yalnız sentetik sırlar kullanır; gerçek anahtarlar rapora veya loga taşınmaz. [Repo çalışma kuralları](../../AGENTS.md) ile repo kuralları aynı kaynak/kanıt ve yetki sınırlarını korur.

## İlk doğrulama ve fixture düzeltmesi

423runtime testi (13yeni privacy testi) ve48repo kontrolü geçti. Yeni sentetik DB/backup dosyaları, sanitized hash/span, escaped JSON, raw output discard, eski kaynak için egress reddi, cookie/header/URL/private-key, ID korunması ve POSIX sidecar izinleri sınandı. İlk browser koşusunda Operations fixture'ındaki sahte sk-key artık doğru biçimde reddedildi ve eski test task kartını bekleyerek timeout oldu. Fixture önce bu reddi ve sıfır task oluşumunu doğrulayacak, sonra credentialsız private metinle eski log testini sürdürecek biçimde düzeltildi; guard gevşetilmedi.50Mermaid render başarılı. Test fixture sırları gerçek credential değildir.

Ayrı bypass kontrolünde eski record'un MCP exact get_record/brief/query yolları için doğrudan negatif test eklendi. Canonical plan operasyonları digest/approval kaydı öncesi, kaynak ise rezervasyon/started receipt öncesi de kontrol edilir; tanınan secret yerel preflight'ta durur. Son browser tekrarında11akış geçti; saf draft/source/request maskelemesi ve credential içeren manuel task reddi doğrulandı.

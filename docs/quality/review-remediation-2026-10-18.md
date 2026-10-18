# 18 Ekim 2026 — repository incelemesi ve düzeltmeler

**Kaynak:** kullanıcı ZIP'i 558 dosya; SHA-256 `17acedbc59f918c32cb2d828493f29b9f40b0729964f74e14c781332a4802689`. GitHub main başlangıcı `dfb942f24fedadc668225714b8e26b49fb762200`. ZIP ve bu ref'in ürün kaynakları eşleşti; eski yerel aynadaki `upstream-component-inventory.csv` farkı korunup teslim dışında bırakıldı. Kullanıcı bütün diyagramların render'ını, bulguların teyidini, gerekli düzeltmeleri ve GitHub'a aktarımı istedi. Ücretli API/gerçek host/veri izni verilmiş sayılmadı.

## Bulgu → düzeltme → kanıt

| Bulgu | Önceki kanıt | Yapılan işlem / kalan sınır |
|---|---|---|
| R01: bağımlı Done zinciri | B blocker/file nedeniyle Awaiting Verification, A Done; C de tamamlanabiliyordu | Etkili önkoşul durumu aynı snapshot'ta yeniden değerlendirilir. Unknown/unavailable/cycle/limit Done koruyamaz.64 depth/256 evaluation sınırı; historical Done silinmez. Blocker çözülüp ayrı scope review ile B→A→C tekrar tamamlanır |
| R02: overrun |10 rezervasyon/100 tavan; actual 1000 reddedildi ama 90 yeni rezervasyon açıldı | Gerçek actual ve overrun commit edilir, sonra hata döner. Yeni kök run dahil workspace rezervasyonu durur. Retry kaydı çoğaltmaz, actual yeniden yazılamaz. Otomatik unfreeze veya limit yükseltme yok; operasyonel insan reconciliation UX'i açık |
| R03: analyze bütçeden bağımsız | Fixture analizinde rezervasyon sayısı değişmedi | Kaynak/hash/actor/current authority/provider/model/output ceiling/root run/expiry bağlı trusted human grant zorunlu. Rezervasyon + started receipt atomik; model transaction dışında. Actual settle; unknown tutulu; overrun kalıcı ve görünür. Sadece authorized=True yetmez |
| R04: partial kapsam gizli | Backend coverage saklıyor; UI göstermiyordu | Complete/partial/unknown etiketi ve partial/unknown uyarısı var; reload'da korunur. Overrun uyarısı usage ve analiz kartında görünür |
| R05: CI UI eksik | Workflow yalnız Python/doküman/spike çalıştırıyordu | Pinned Node22/Playwright1.62.1 ile workflow/partial coverage/impact/projects smoke job; screenshot/log artifact. Mermaid11.17.2 ile tüm kaynak render'ı da CI'da. Lokal tam 8 akış koşusu ayrı |
| R06: belge drift | README_LOCAL üstte tek proje/MCP/file yok diyor; altta güncel dilimler var | Tek güncel yetenek tablosu eklendi. Mevcut proje seçimi≠proje yaratma; stdio≠native host kabulü; SHA≠test/deploy; token rezervasyonu≠parasal garanti ayrıldı |

Yeni regresyonlar [test_review_remediation.py](../../tests/runtime/test_review_remediation.py); [kaynak/model/bütçe grant şeması](../../manifests/conversation-dispatch-grant.schema.json). Fiziksel SQL schema1 ve TaskStage v2 değişmedi. Yeni grant audit payload'ı yayımlandı; eski izin veya receipt geriye dönük uydurulmadı. Model transport nesnesinin output cap değişikliği de grant'i geçersiz kılar. Kaynak onayı yalnız seçilen metin hash'ine aittir.

## Tekrar teyit ve doğrulama

- 330 runtime testi geçti. Yeni testler kaynak/model/outputcap/expiry/authz değişimi, rezervasyonsuz dispatch, started-audit rollback, known/unknown/overrun usage, eski usage'ın timeout'ta yeniden kullanılmaması ve çok katmanlı completion bozulmasını kapsar.
- Başlangıçtaki ilk tam koşuda üç eski MCP fixture'ı yeni grant şartında durdu; fixture'lara açık sentetik authorization hazırlığı eklendi. Ürün guard'ı gevşetilmedi. Yanlış çalışma dizininde başlayan yardımcı test çağrıları test yürütmedi; sonuç sayılmadı.
- Dört CI smoke akışı yerel çalıştırıldı; geniş sekiz-akış koşusu localization, backup, routing/graph ve file/MCP'yi de içerir. Model/target/agent/root verileri yalnız açık sentetik fixture; gerçek kullanıcı kaynaklarına erişim yok.
- 44 Mermaid / 23 belge yeniden render edildi: syntax/render failure0; accTitle/accDescr, pozitif viewBox, SVG XML ve kaynak/SVG hashleri kontrol edildi. Dört contact sheet ve değişen tam boy görseller incelendi. Büyük ER/sequence görsellerinde metin için SVG zoom gerekir; küçük contact sheet okunabilirlik kanıtı değildir.
- İki diyagram güncellendi: [yerel runtime](../architecture/local-preview.md) kaynaklı izin→rezervasyon→provider→settlement ve overrun sınırını; [workflow](workflow-ui-runtime.md) önkoşul kanıtı değişimini gösterir. Diğer 42 kaynak değişmedi fakat bu tur gerçekten render edildi. Kayıt [diagram-render-results.json](diagram-render-results.json). Önceki render kayıtları tarihsel olarak korundu.
- Tüm SVG/PNG çıktıları GitHub Actions `synthetic-ui-smoke` artifact'ında `diagram-render-results` dizininde yeniden üretilebilir. Değişen iki SVG repository'de güncellendi; diğerlerinin güncel kaynak/hash kaydı raporda. Kaynak paketinin yanında yerel tam görsel ZIP ayrıca hazırlanır.

[Makine kanıtı ve kaynak hashleri](review-remediation-results.json).

Komutlar: `python3.12 -B -m unittest discover -s tests/runtime -v`; `python3.12 -B scripts/check_ui_smoke.py --all --output /tmp/decivora-smoke`; `node scripts/render_diagrams.cjs /tmp/decivora-diagrams` (Playwright/bundle/browser ortam ayarları gerekir). Ağ erişimi render sırasında yalnız fixture loopback sunucusuna açıktır; remote asset engellenir. CI dependency kurulumu ise npm'den dev bağımlılık indirir.

## Kapatılmayan kapsam

Gerçek model taşıyıcısı/anahtar etkinleştirilmedi ve paid çağrı yapılmadı. Bu teslim doğrulanmış tokenizer/context/price/para/dönem tavanını veya production bütçe reconciliation arayüzünü tamamlamaz. Gerçek API kullanımı öncesinde bunlar ve açık provider/veri/bütçe kararı gözden geçirilmelidir. Default launcher modelsizdir; grant hazırlama trusted Python configuration entry'sidir, transcript/HTTP/MCP komutu değildir. Yanlış anlam çıkarımı/holdout kalitesi, iki gerçek coding adapter, gerçek hedef pilotu, kapsamlı impact→approval→apply, privacy/retention/cloud/release kapıları açık kalır.

Yerel test bağımlılıkları uygulamanın runtime bağımlılığı değildir: Playwright1.62.1 (declared Apache-2.0), Mermaid11.17.2 (declared MIT); seçilmiş sürümler kullanılan yerel renderer/harness ile eşleşir. Transitif dağıtım uygunluğu veya Decivora'nın nihai lisansı karara bağlanmış sayılmaz. İlk CI kurulumu ve Linux browser koşusu GitHub sonucuyla ayrıca doğrulanır. Normal ürün kullanımı bu paketleri istemez.

Ana görevler 7 Done / 14 In Progress / 9 To Do; bu hedefli düzeltmeler parent MVP kabulünü veya gelecek fazları kendiliğinden kapatmaz. T14/T15/T19/T21/T22/T24 sahiplikleri korunur; yeni ana görev yaratılmadı.

## Gerçek yerel servis başlatma ve doğrulama

18 Ekim2026: Kullanıcı yeni backend'in gerçekten çalıştırılmasını istedi. Ön kontrol53610portunda connection refused verdi; eski tarayıcı görüntüsü çalışan eski backend kanıtı değildi. Mevcut DB için SQLite API ile private600mode tutarlı yedek alındı; bütünlük geçti. Güncel `db0003df40a339fc9771951e3fb0c14ddc71d62d` kaynakları aynı veri dosyası ve aynı loopback portuyla başlatıldı.

Yeni backend'e özgü `usage.dispatch_blocked` alanı gerçek HTTP yanıtında doğrulandı. Dört eşzamanlı okuyucu/sekiz state isteği200; bu boş çalışma alanında4.93–10.78ms gözlendi (performans SLO'su değil). Invalid Origin403reddedildi; health'teki origin_denied olayı bu bilinçli negatif kontroldür. Başlatma ve kontroller sonrası bütün tablo içeriklerinin digest'i yedekle aynı, integrity ok ve journal WAL. Çalışma alanı önce/sonra boş; test task/conversation eklenmedi. Kaydedilmemiş giriş bulunmayan gerçek browser sekmesi yeni oturumla açıldı; konuşmalar, görev panosu ve kullanım/sağlık görünümleri kontrol edildi.

Model, capture ve file root aktive edilmedi; kullanıcı veritabanında semantik çıkarım veya dosya testi çalıştırıldığı iddia edilmez. Düzeltmelerin davranış testleri önceki330runtime ve8sentetik browser akışıdır; bu kayıt onların yanında gerçek yerel startup/auth/read/UI kanıtıdır. Özel yedek, oturum anahtarı ve yerel veri yolları GitHub'a eklenmedi. Güvenli özet [makine kaydındadır](review-remediation-results.json).

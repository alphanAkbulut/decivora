# Decivora — İlk yerel uygulama

**Karar etkisinden görev güncelleme:** Questions and decisions → Preview decision impact → etkilenen görevi seç ve önerilen kapsamı düzenle → Prepare task changes → değişiklik grubunu seç → Select task changes → Approve selected changes → Apply approved task changes. Son adıma kadar görev değişmez. Bu dilim görev kapsamını günceller; kararı emekli etmez ve görevi iptal etmez.

**İptal ve yeniden açma (19 Ekim):** Task Overview → Task rationale decision → Approve rationale link ile mevcut karara gerekçe bağlantısı eklenebilir. Questions and decisions ekranında retirement/restoration varsayımını seç; yalnız tek gerekçesi bu karar olan bağlı task'ları Confirm task rationale altında açıkça doğrula ve Preview çalıştır. Uygun adayda Prepare cancellation/reopening review → grup seçimi → ayrı onay → Apply yolu vardır. Başka aktif gereksinim/parent/downstream engeli varsa apply reddedilir. Cancelled Closed work filtresinde, olaylar History'de korunur; yeniden açma To Do'ya yeni event ile döner. Bu, canonical kararı emekli etmez veya semantik gerekçeyi otomatik çıkarmaz.


## Konuşmadan görev ve durum önerisi — 18 Ekim

Konuşmayı **Conversations** ekranına aktar. Model bağlantısı kapalıysa kaynak kartındaki **Use a response from your existing LLM** bölümünü aç; **Prepare LLM request** ile seçili metin, proje görevleri, canonical karar/kayıtlar, sorular ve kayıtlı ilişkileri içeren isteği incele. Bunu hangi LLM'ye göndereceğini sen seçersin; uygulama kendiliğinden dışarı göndermez. LLM'nin JSON yanıtını **Validate and import response** ile aktar.

Yeni görev adaylarını seçip kaydet. Mevcut göreve ilişkin durum önerisi için önce/sonra, kaynak alıntısı ve inceleme gerekçesini kontrol et; kabul et, reddet veya ertele. “Done” beyanı kanıt yerine geçmez; mevcut workflow/AC/DoD kuralları uygulanır. Context değişmişse yeni istek/yanıt hazırlanır; eski kayıt korunur. Otomatik session capture ve gerçek model kalite kabulü henüz tamamlanmadı. Dış LLM kullanımının token/para tüketimi bu import yolunda bilinmiyor; Decivora tarafından sınırlandırılamaz.


Mac'te **Decivora.command** dosyasına çift tıkla. Terminal açılır ve yerel uygulama tarayıcıda başlar. Terminal uygulama açıkken çalışır; UI'daki “Uygulamayı kapat” düğmesiyle durdurabilirsin. Python3.12 gerekir; bu Mac'teki Codex runtime'ı launcher tarafından bulunur. Başka bir Mac'te kurulu Codex runtime veya `python3.12` gerekir. Signed installer / tam MVP değildir.

**İki ayrı ekran var:** Bu program kendi görevlerini eklediğin ürün önizlemesidir; ilk açılışta “Benim projem” boş gelir ve sütunlar0 gösterir. Decivora’nın geliştirme backlog/teslim kayıtları ayrı [geliştirme takip ekranındadır](https://github.com/alphanAkbulut/decivora/blob/main/docs/delivery/progress-guide.md); geliştirme görevleri kişisel veritabanına otomatik kopyalanmaz.

Ana ekran **Konuşmalar ve öneriler**dir: seçtiğin konuşma parçasını aktar. Kaynak yerel olarak korunur. Model bağlantısı henüz varsayılan olarak kapalıdır; **Model bağlantısı bekleniyor** görünür, otomatik anlam çıkarımı çalıştırılmaz. API key/bakiye/izin verilmiş varsayılmaz. Provider yapılandırıldıktan sonra kaynaklı adaylar, mevcut kayıt karşılaştırması ve seçili önerileri kaydetme bu ekranda çalışacaktır. Bugünkü browser testi kontrollü model kullanır; gerçek semantic kalite kanıtı değildir.

Elle görev/soru ekleme yardımcı alanlardadır; ana ürün amacı konuşmalardan otomatik öneri üretmektir. Sidebar/metrikler yalnız kişisel workspace kayıtlarını gösterir.

1. Yardımcı görev bölümünü aç, görev ekle ve kartı aç.
2. Göreve göre düzenlenebilir AC/DoD şablonlarını incele; **Kriterleri onayla**.
3. **Çalışmaya başla**: kart In Progress'e geçer.
4. Sekmeyi veya programı yeniden açınca SQLite kayıtları korunur. Kriter değiştirirken gerekçe ve diff onayı gerekir; önceki sürümler silinmez.

Veri uygulama kaynak klasörünün yanında `decivora-local-data/workspace.sqlite` içinde tutulur; ZIP/veri GitHub'a otomatik yüklenmez. Program yeniden başladığında yeni browser session gerekir; launcher doğru oturumu açar. Eski adresi tek başına başka tarayıcıya yapıştırmak oturum açmaz. Tek yerel kullanıcı önizlemesidir. Kullanıcının yetkili olduğu mevcut projeler arasında seçim vardır; proje veya grant yaratma, ekip hesabı ve davet arayüzü yoktur.

**Güncel yetenekler (18 Ekim 2026):**

| Alan | Çalışan yerel alt küme | Açık sınır |
|---|---|---|
| Görev/karar | Board/List/Graph/Timeline, soru/cevap, ayrı karar onayı, sürümlü AC/DoD ve insan kanıtı | Otomatik chat capture ve gerçek semantik kalite doğrulanmadı |
| Projeler | Yetkili mevcut projeler arasında seçim | Proje/grant oluşturma ve ekip daveti UI yok |
| MCP | Bounded stdio araçları, ayrı agent önerisi ve insan onayı | Gerçek native host aktivasyonu ve private paylaşım pilotu açık |
| Doğrulama | İnsan incelemesi; açıkça seçilmiş root/recipe ile exact file SHA | Arbitrary test/deploy runner yok; dosya eşleşmesi uygulama testi değildir |
| Model/bütçe | Kaynak/provider/model/run/expiry bağlı izin, atomik rezervasyon, unknown/overrun muhasebesi ve görünür coverage | Varsayılan launcher model açmaz; gerçek erişim/veri/bütçe seçimi ve transport etkinleştirmesi ayrı |

In Progress çalışma beyanıdır; Done güncel kriterler ve bağlı önkoşulların etkili doğrulamasıyla değerlendirilir. Geçerliliğini kaybeden Done geçmişte korunur; güncel görünüm yeniden doğrulama ister. Bu paket tam AI-native otomatik hafıza MVP'si veya imzalı installer değildir.

Bekleyen karar soruları bölümünde soru ve 2–8 seçeneği kaydet; seçenek düğmesine bastığında soru ID/sürümüyle seçim tutulur. Başka konuya geçmek veya programı kapatmak soruyu silmez. Seçimden sonra gerekçe girip **Karar önerisi hazırla → Karar önerisini onayla → Onaylı kararı uygula** adımlarını ayrı tamamlayabilirsin. Decision yerel hafızaya kaydedilir; görevler otomatik değiştirilmez. Bu seçim kaydı görev iptali, kod çalıştırma veya dış erişim onayı değildir. Soru yönetimi ve geçmiş bölümünde gerekçeyle ertele/devam/iptal yapabilir veya yeni soru sürümü kaydedebilirsin. Eski cevaplar yeni seçeneklere taşınmaz; uygulanmış karar geçmişte kalır. Bağlamı sonradan gelen cevabı “Bağlamıyla yeniden değerlendir” düğmesiyle kontrol edebilirsin. Serbest sohbetten otomatik soru yakalama/eşleme henüz yok.

CLI alternatif: `python3.12 -B -m apps.local_ui.server`. `--data-dir` ile kendi private veri dizinini seçebilirsin; desteklenmeyen eski DB profile'ı sessiz migrate edilmez.


**Arayüz dili:** Header'daki Language seçicisinden English (varsayılan), Türkçe, Español, Português (Brasil) veya العربية seç. Seçim bu tarayıcıda hatırlanır; Arapça sağdan sola yerleşir. Menüler yerel katalogdan gelir ve model/token harcamaz. Görev, konuşma, gerekçe ve AC/DoD içerikleri çevrilmez; ilk proje şablonları Türkçe kalır. Pano statüleri İngilizcedir. ES/PT/AR çevirileri taslaktır; native inceleme yapılmadı. [Dil kararı ve test sınırları](https://github.com/alphanAkbulut/decivora/blob/main/docs/product/language-and-localization.md).


**Blockers:** Panonun üst listesi ve karttaki kırmızı Blocked işareti engellenen işleri gösterir. Kartı açıp “Blocker management and history” bölümünde gerekçe ve çözüm adımıyla işaretle/çöz. Görev kendi ilerleme sütununda kalır; aktif blocker yeni işe başlama işlemini durdurur. Geçmiş silinmez. Bu dilim açık insan beyanıdır; konuşma/dependency kaynaklı otomatik blocker bağlama henüz tamamlanmadı. Dört sütun nihai workflow sınırı değildir.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

Yeni görünüm: sidebar Conversations/Review inbox/Task board/Questions and decisions/Sources; Board/List/search/filter; task seç→yan panel Overview/AC-DoD/Sources/History, Escape/Close ile geri dön. Human-review kriterini açık reference/note ile passed/failed/pending/not_run/unknown kaydet; bütün gerekli current maddeler geçtiğinde Awaiting Verification’dan Done için ayrı scope review gerekir. Bu uzaktaki dosyayı kendi tarayan verifier değildir; automatic_test/file_check yapılandırılmadıkça endpoint reddeder. Blocker start/finish/both kapısını açık seçer; dependency finish gate ve linked pending soru görünür. Done/Closed/Blocked farklıdır; yeni UI task geçmişini değiştirmez.

## 14 October 2026 — private backup UI

[Current bounded backup download](docs/quality/private-backup-runtime.md): Sources view, explicit private-data acknowledgment, ZIP + manifest and temporary offline restore validation. Unencrypted source-preserving backup; not a shareable redacted export. Active restore/purge/migration/encryption remain open; no model call or new SQL schema.

## Current local delivery — 14 October 2026

[API-independent implementation and follow-up gates](docs/delivery/api-independent-development.md): bounded stdioMCP/create-only human review, optional explicit-root file SHA verification, recorded graph/audit timeline, routing/null usage and session-only health. Historical implementation limits above refer to their original deliveries; current limits and M01–M14 checks are in the linked report. No native capture, full brief/delta, sandbox test/deploy verifier, exact host token savings or global language quality is claimed.

## Current concurrent storage and manual impact UI —14October2026

[Working delivery and limitations](docs/quality/concurrency-impact-delivery.md): startupWAL, read-snapshot-only audit grouping,318runtime/48tracker/7browser, identical mixed-fixture improvement and controlled503mechanism regression. Questions/decisions now offers human-selected durable decision-impact hypothesis; no task cancellation/decision mutation, missing rationale review. Full model/host/source-aware approval/application and release checks remain open.

## Operations ve ayrı test ortamı

Sol menü **Operations**: işlem kimliğiyle ara, sonucu filtrele, komutun authorization/execute aşamalarını aç; süre ve güvenli hata kodunu gör. **Refresh diagnostics** yalnız okur. Kayıtlar restart sonrası korunur; kapsama/saklama sınırı ve kaydedilemeyen yazım uyarıları ekranda görünür. Ham konuşma ve API anahtarı bu logda tutulmaz. Bu ekran tam engine zinciri veya güvenlik audit konsolu değildir.

**Decivora Test.command** dosyasını çalıştır: ayrı53611portu, ayrı test veri klasörü ve belirgin TEST etiketi kullanır. Normal yerel kayıtlar kopyalanmaz; model/file-target bağlantıları kapalıdır. İki ortam aynı tarayıcıda farklı oturum çerezleriyle çalışır. Test işlerini burada elle sentetik veriyle deneyebilirsin. Veri sıfırlama düğmesi veya ücretli model aktivasyonu yoktur. [Ayrıntı](https://github.com/alphanAkbulut/decivora/blob/main/docs/quality/operations-runtime.md).

# Decivora — İlk yerel uygulama

Mac'te **Decivora.command** dosyasına çift tıkla. Terminal açılır ve yerel uygulama tarayıcıda başlar. Terminal uygulama açıkken çalışır; UI'daki “Uygulamayı kapat” düğmesiyle durdurabilirsin. Python3.12 gerekir; bu Mac'teki Codex runtime'ı launcher tarafından bulunur. Başka bir Mac'te kurulu Codex runtime veya `python3.12` gerekir. Signed installer / tam MVP değildir.

**İki ayrı ekran var:** Bu program kendi görevlerini eklediğin ürün önizlemesidir; ilk açılışta “Benim projem” boş gelir ve sütunlar0 gösterir. Decivora’nın geliştirme backlog/teslim kayıtları ayrı [geliştirme takip ekranındadır](https://github.com/alphanAkbulut/decivora/blob/main/docs/delivery/progress-guide.md); geliştirme görevleri kişisel veritabanına otomatik kopyalanmaz.

Ana ekran **Konuşmalar ve öneriler**dir: seçtiğin konuşma parçasını aktar. Kaynak yerel olarak korunur. Model bağlantısı henüz varsayılan olarak kapalıdır; **Model bağlantısı bekleniyor** görünür, otomatik anlam çıkarımı çalıştırılmaz. API key/bakiye/izin verilmiş varsayılmaz. Provider yapılandırıldıktan sonra kaynaklı adaylar, mevcut kayıt karşılaştırması ve seçili önerileri kaydetme bu ekranda çalışacaktır. Bugünkü browser testi kontrollü model kullanır; gerçek semantic kalite kanıtı değildir.

Elle görev/soru ekleme yardımcı alanlardadır; ana ürün amacı konuşmalardan otomatik öneri üretmektir. Sidebar/metrikler yalnız kişisel workspace kayıtlarını gösterir.

1. Yardımcı görev bölümünü aç, görev ekle ve kartı aç.
2. Göreve göre düzenlenebilir AC/DoD şablonlarını incele; **Kriterleri onayla**.
3. **Çalışmaya başla**: kart In Progress'e geçer.
4. Sekmeyi veya programı yeniden açınca SQLite kayıtları korunur. Kriter değiştirirken gerekçe ve diff onayı gerekir; önceki sürümler silinmez.

Veri uygulama kaynak klasörünün yanında `decivora-local-data/workspace.sqlite` içinde tutulur; ZIP/veri GitHub'a otomatik yüklenmez. Program yeniden başladığında yeni browser session gerekir; launcher doğru oturumu açar. Eski adresi tek başına başka tarayıcıya yapıştırmak oturum açmaz. Tek yerel kullanıcı / tek proje önizlemesidir; farklı projeler/ekip hesabı/invite UI yoktur.

**Çalışan:** kalıcı manuel soru/seçenek/cevap listesi, kalıcı manuel görev board'u, kriter/DoD onayı ve sürüm geçmişi, iş başlangıç kaydı, reload/restart, local session/CSRF/Origin/Host/body ve rate sınırları. **Güncel ekler:** Board/List, arama/filtre, yan görev paneli, altı çalışma aşaması, kayıtlı bağımlılık ve bekleyen soru kapıları; gerekli güncel AC/DoD insan incelemesi ve ayrı kapsam kontrolü sonrası Done. **Hazır olmayan:** otomatik chat capture, gerçek LLM çıkarımı, MCP, tam graph/timeline, otomatik dosya/test doğrulayıcısı. In Progress yalnız çalışma beyanıdır; insan incelemesi bağımsız hedef taraması değildir. Bu programa henüz “tam AI-native otomatik hafıza MVP” denmez. Para/ücretli API çağrısı yok.

Bekleyen karar soruları bölümünde soru ve 2–8 seçeneği kaydet; seçenek düğmesine bastığında soru ID/sürümüyle seçim tutulur. Başka konuya geçmek veya programı kapatmak soruyu silmez. Seçimden sonra gerekçe girip **Karar önerisi hazırla → Karar önerisini onayla → Onaylı kararı uygula** adımlarını ayrı tamamlayabilirsin. Decision yerel hafızaya kaydedilir; görevler otomatik değiştirilmez. Bu seçim kaydı görev iptali, kod çalıştırma veya dış erişim onayı değildir. Soru yönetimi ve geçmiş bölümünde gerekçeyle ertele/devam/iptal yapabilir veya yeni soru sürümü kaydedebilirsin. Eski cevaplar yeni seçeneklere taşınmaz; uygulanmış karar geçmişte kalır. Bağlamı sonradan gelen cevabı “Bağlamıyla yeniden değerlendir” düğmesiyle kontrol edebilirsin. Serbest sohbetten otomatik soru yakalama/eşleme henüz yok.

CLI alternatif: `python3.12 -B -m apps.local_ui.server`. `--data-dir` ile kendi private veri dizinini seçebilirsin; desteklenmeyen eski DB profile'ı sessiz migrate edilmez.


**Arayüz dili:** Header'daki Language seçicisinden English (varsayılan), Türkçe, Español, Português (Brasil) veya العربية seç. Seçim bu tarayıcıda hatırlanır; Arapça sağdan sola yerleşir. Menüler yerel katalogdan gelir ve model/token harcamaz. Görev, konuşma, gerekçe ve AC/DoD içerikleri çevrilmez; ilk proje şablonları Türkçe kalır. Pano statüleri İngilizcedir. ES/PT/AR çevirileri taslaktır; native inceleme yapılmadı. [Dil kararı ve test sınırları](https://github.com/alphanAkbulut/decivora/blob/main/docs/product/language-and-localization.md).


**Blockers:** Panonun üst listesi ve karttaki kırmızı Blocked işareti engellenen işleri gösterir. Kartı açıp “Blocker management and history” bölümünde gerekçe ve çözüm adımıyla işaretle/çöz. Görev kendi ilerleme sütununda kalır; aktif blocker yeni işe başlama işlemini durdurur. Geçmiş silinmez. Bu dilim açık insan beyanıdır; konuşma/dependency kaynaklı otomatik blocker bağlama henüz tamamlanmadı. Dört sütun nihai workflow sınırı değildir.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

Yeni görünüm: sidebar Conversations/Review inbox/Task board/Questions and decisions/Sources; Board/List/search/filter; task seç→yan panel Overview/AC-DoD/Sources/History, Escape/Close ile geri dön. Human-review kriterini açık reference/note ile passed/failed/pending/not_run/unknown kaydet; bütün gerekli current maddeler geçtiğinde Awaiting Verification’dan Done için ayrı scope review gerekir. Bu uzaktaki dosyayı kendi tarayan verifier değildir; automatic_test/file_check yapılandırılmadıkça endpoint reddeder. Blocker start/finish/both kapısını açık seçer; dependency finish gate ve linked pending soru görünür. Done/Closed/Blocked farklıdır; yeni UI task geçmişini değiştirmez.

## 14 October 2026 — private backup UI

[Current bounded backup download](docs/quality/private-backup-runtime.md): Sources view, explicit private-data acknowledgment, ZIP + manifest and temporary offline restore validation. Unencrypted source-preserving backup; not a shareable redacted export. Active restore/purge/migration/encryption remain open; no model call or new SQL schema.

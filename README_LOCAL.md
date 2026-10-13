# Decivora — İlk yerel uygulama

Mac'te **Decivora.command** dosyasına çift tıkla. Terminal açılır ve yerel uygulama tarayıcıda başlar. Terminal uygulama açıkken çalışır; UI'daki “Uygulamayı kapat” düğmesiyle durdurabilirsin. Python3.12 gerekir; bu Mac'teki Codex runtime'ı launcher tarafından bulunur. Başka bir Mac'te kurulu Codex runtime veya `python3.12` gerekir. Signed installer / tam MVP değildir.

1. Görev ekle ve kartı aç.
2. Göreve göre düzenlenebilir AC/DoD şablonlarını incele; **Kriterleri onayla**.
3. **Çalışmaya başla**: kart In Progress'e geçer.
4. Sekmeyi veya programı yeniden açınca SQLite kayıtları korunur. Kriter değiştirirken gerekçe ve diff onayı gerekir; önceki sürümler silinmez.

Veri uygulama kaynak klasörünün yanında `decivora-local-data/workspace.sqlite` içinde tutulur; ZIP/veri GitHub'a otomatik yüklenmez. Program yeniden başladığında yeni browser session gerekir; launcher doğru oturumu açar. Eski adresi tek başına başka tarayıcıya yapıştırmak oturum açmaz. Tek yerel kullanıcı / tek proje önizlemesidir; farklı projeler/ekip hesabı/invite UI yoktur.

**Çalışan:** kalıcı manuel soru/seçenek/cevap listesi, kalıcı manuel görev board'u, kriter/DoD onayı ve sürüm geçmişi, iş başlangıç kaydı, reload/restart, local session/CSRF/Origin/Host/body ve rate sınırları. **Hazır olmayan:** otomatik chat capture, LLM çıkarımı, MCP, graph/timeline/review inbox, kanıtla Done. Done boş ve disabled kalır; In Progress yalnız çalışma beyanıdır. Bu programa henüz “tam AI-native otomatik hafıza MVP” denmez. Para/ücretli API çağrısı yok.

Bekleyen karar soruları bölümünde soru ve 2–8 seçeneği kaydet; seçenek düğmesine bastığında soru ID/sürümüyle seçim tutulur. Başka konuya geçmek veya programı kapatmak soruyu silmez. Bu seçim kaydı görev iptali, kod çalıştırma veya dış erişim onayı değildir. Serbest sohbetten otomatik soru yakalama/eşleme henüz yok.

CLI alternatif: `python3.12 -B -m apps.local_ui.server`. `--data-dir` ile kendi private veri dizinini seçebilirsin; desteklenmeyen eski DB profile'ı sessiz migrate edilmez.

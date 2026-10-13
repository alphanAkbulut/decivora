# T13c + tıklanarak başlayan yerel uygulama

**Çalışan kod teslimi.** [Kullanım](../../README_LOCAL.md), [launcher](../../Decivora.command), [UI/server](../../apps/local_ui/server.py), [AC/DoD](../../packages/domain/acceptance.py), [runtime testleri](../../tests/runtime/test_acceptance.py), [HTTP testleri](../../tests/runtime/test_local_app.py), [sonuç/hash](local-preview-results.json), [şema/akış](../architecture/local-preview.md).

T13c core Done: versioned criteria/DoD preparation+human approval+explicit applicability reason; criteria weakening/change acknowledgment; stale contract/work-start guard. T13e pending-question resolution hâlâ açık, ana T13 In Progress. T19 ve T20 gerçekten kodlandı/start oldu: manuel AC kartı ve board var; full inbox/selector/graph/timeline tamamlanmadı. Ana sayı **7 Done / 8 In Progress / 15 To Do**. Sayımın düşmesi iki UI işinin başlamasıdır; ikisini Done göstermek için acceptance gevşetilmedi.

## Çalıştırılabilir paket

`scripts/package_local_preview.py` DB/token/transcript/test çıktısı içermeyen standalone source ZIP oluşturur. ZIP temiz temporary klasöre gerçek `unzip` ile açıldı, executable `.command` doğrudan çalıştırıldı, ayrı `--no-browser` server HTML200 verdi. Normal launch browser'ı session fragment ile açar. Signed .app/native installer ve Python-free executable değildir; bu Mac'in kurulu Codex Python3.12'si kullanılabilir. Programı kapat/açınca data SQLite'da kalır.

## Gerçek test kanıtı

- **185 runtime test geçti:** önceki168 +9acceptance +8localHTTP. Criteria/DoD empty/type/NA reason, required change acknowledgment, current task/contract version, role, audit rollback, start-before-criteria, restart/replay/backuprestore; Host/Origin/session/CSRF, cookie flags, unknown route/shell/foreign fields, private DB mode ve write-rate limit.
- **Gerçek tarayıcı akışı:** cached Playwright+ayrı headless Chrome, dış network abort. Task oluştur→kart aç→kriter yokken start reddi→template approval→In Progress→reload kalıcılık. Done cards0; UI gerçek DB/state okur. Masaüstü1440 ve mobil390 screenshot'ları görsel incelendi. Tam klavye/accessibility/product-pilot kabulü iddia edilmez.
- Yeni diagram aynı mevcut renderer ile incremental render/provenance kontrolünden geçer; ürün UI acceptance ile Mermaid çizimi ayrı tutulur. Şema artifact'i runtime typed alanlarla eşleştirilir; generic JSON Schema certification değildir.
- Root tracker/doküman/closure ve GitHub CI teslim sırasında ayrıca doğrulanır. Local app rate numbers development guard'dır, üretim SLO veya kullanıcı API bütçesi değildir.

## Neye yarar / henüz ne yapmaz?

Kullanıcı şimdi yerel Task hafızasını, onaylı kriterlerini ve iş başlangıçlarını ekran üzerinden kaydedebilir. Genel otomatik AI-native memory/decision graph ürünü hâlâ bitmedi: source adapters/semantic extraction/MCP/evidence/Done/full reviewgraph UI açık. UI ilk şablonları deterministik text draft'tır; model anlam çıkarımı diye sunulmaz. Kriteri onaylamak testi passed yapmaz. Work-start gerçek code runner başlatmaz; kişinin In Progress beyanını kalıcı kaydeder. Para/ücretli API/model call0; bu coding sohbetinin kullanımı unknown.

## Sıradaki teslim yolu

T13e ile bekleyen sorular/geç cevapları kapat → ana T13 acceptance → T14 kanıt+false-done → bu yerel arayüze gerçek review/Done bağlama → native capture/MCP → tam MVP pilot/package acceptance. Full vizyon/fazlar korunur. Kullanıcının yeni önceliği çalışır yazılım; ek genel benchmark/analiz bu teslim yolunu geciktirmeyecek.

# Görsel dokümantasyon sözlüğü

**2026-10-11 · Doküman tasarımı; ürün UI veya çalışan özellik değildir.** Amaç bütün Mermaid'lerde anlamlı renk, okunur etiket ve açık niyet/öneri ayrımıdır. [İçerik ve render kaydı](diagram-review.md) kanıt sınırını gösterir.

## Renk ve anlam

Renk tek anlam taşıyıcısı değildir; başlık, state/ilişki etiketi ve metin gerekir. “Yeşil kutu gördüm, test geçti” yorumu yanlıştır.

| Sınıf | Dolgu / sınır | Anlam |
|---|---|---|
| Kaynak | `#eff6ff` / `#1d4ed8` | İnsan, host, source veya hedef; içerik güvenilir talimat değil |
| İşleme | `#dbeafe` / `#1d4ed8` | Capture, reconciliation ve ürün niyeti; implemented rozeti değil |
| Yetki/inceleme | `#fef3c7` / `#92400e` | İnsan onayı, policy/grant/revision veya yatırım kapısı |
| Kalıcı bilgi | `#ccfbf1` / `#0f766e` | Event/store/projection/arşiv; sonsuz saklama değil |
| Kanıt alanı | `#dcfce7` / `#166534` | Observer/evidence/verification; ER evidence tablosu trusted/pass demek değil |
| Belirsizlik | `#ffedd5` / `#9a3412` | Unknown/partial/stale/deferred veya eksik kapsam |
| Ret/hata | `#ffe4e6` / `#9f1239` | Denied/failed/incident; cancelled ile aynı değil |
| Tarihçe | `#f1f5f9` / `#475569`, kesikli sınır | Önceki revision/obsolete/cancelled; silme değil |
| Gelecek/öneri | `#ede9fe` / `#6d28d9`, kesikli sınır | Seçilmemiş stack/ADR veya koşullu sonraki faz |

Node metni `#0f172a`; sabit beyaz canvas ve pastel dolgu üzerinde kontrast ayrıca hesaplanır. Sequence'lerde açık mavi işlem bandı, sarı not, mesaj numarası ve alt/opt başlığı kullanılır. Bandın tamamı DB transaction değildir; TX etiketi atomiklik sınırını gösterir.

## Oklar ve etiketler

- Ok girdi/çıktı, kontrol veya açıklanan ilişkiyi gösterir; yetki devri değildir. Model/provider ve target ayrı izin/budget/capability kapısıyla okunur.
- `required_by`, `depends_on`, `part_of`, `supersedes` farklıdır. Kesikli çizgi tek başına domain anlamı taşımaz; tarihçe, öneri veya budget kontrolü etiket/metinle ayrılır.
- Decision map okları niyet evrimi veya değerlendirilecek önerileri gösterir; task dependency veya teknoloji seçimi değildir. DEC-01–20 tablosu canonical kayıttır.
- Sequence numarası yerel anlatım sırasıdır; global kaynak zamanı veya event sequence yerine geçmez. Callback ack kalıcı receipt'ten sonra adapter üzerinden döner.
- ER cardinality, bütün fiziksel DDL/FK/ACL alanlarının tamamı değildir; [DB ilişkileri](../architecture/data-relationships.md), [domain](../architecture/domain-model.md) ve [IC](../architecture/implementation-contracts.md) birlikte okunur.
- Upload gözlemi ile AC/DoD kabulü ayrı; erişim hatası missing değildir. Boş AC otomatik pass olamaz.
- İptal metin etiketiyle korunur; edge silinmez. Ended/invalidated ayrı event'tir. [Graph sözlüğü](../product/graph-experience.md) UI davranışını açıklar.

## Yerleşim ve erişilebilirlik

README/engine/faz akışı dikey okunur. Karar haritası kabul edilen niyet ile teknik öneri olarak iki çizime ayrılır. Her kaynak `accTitle`/`accDescr` taşır; SVG metadata'sı yardımcıdır, UI erişilebilirlik sertifikası değildir. State anlamı renk olmadan metinle de anlaşılır.

Yoğun ER/sequence atlası SVG zoom ile okunabilir; mobilde bütün etiketlerin aynı anda okunacağı garanti edilmez. README SVG fallback aynı Mermaid'den üretilir, ikinci elle düzenlenen truth değildir. Kaynak değişince hash raporu ve fallback yenilenir.

Markdown NOTE statü, IMPORTANT kritik ayrım, TIP gezinme, WARNING sınır/risktir. Henüz gerçek olmayan “tests passing”, release/install/download veya performans badge'leri eklenmez. Marka logoları ve dış badge görselleri kopyalanmadı.

## Hedefli repository sunum benchmark'ı

İnceleme: root README ve non-truncated pinned tree'deki klasör/entrypoint yapısı. Yeni code/runtime veya bütün içerik audit'i değildir.

| Sabit kaynak | Gözlenen yapı | Uyarlama / sınır |
|---|---|---|
| [Graphiti](https://github.com/getzep/graphiti/blob/964bb11d1e7020e3cc67fab244268b0736b6c219/README.md) | Problem/karşılaştırma, quickstart/MCP/service ayrımı; graphiti_core/examples/mcp_server/server/tests | Sorudan ilgili belgeye kısa giriş. Bizde runtime/quickstart yok; uygulama klasörleri boş olarak kopyalanmadı |
| [Langfuse](https://github.com/langfuse/langfuse/blob/cb2cebae9f8e7d53e8e514780fce8493d680ecfb/README.md) | Features/deploy/integrations/license/security ayrımı; specs/fern/web/worker/packages | Durum tablosu, üç rol giriş yolu ve açılır tam belge indeksi. Deploy/cloud metinleri, logo/asset ve uygulama yapısı kopyalanmadı |

Mevcut product/discovery/architecture/delivery/quality/governance/portfolio ayrımı bu aşamaya uygun; dosya taşıma/yeniden adlandırma gerekmedi. Runtime src/apps/packages düzeni stack ve paket sınırı seçildikten sonra T04'te hazırlanır. Esinlenme kod alımı veya lisans seçimi değildir.

Resmî teknik kaynaklar 2026-10-11'de okundu: [theming](https://mermaid.js.org/config/theming.html), [ER styling](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), [accessibility](https://mermaid.js.org/config/accessibility.html), [sequence](https://mermaid.js.org/syntax/sequenceDiagram.html). Local renderer raporda pinlidir; resmî site veya GitHub'ın aynı sürüm olduğu varsayılmaz.

## Bakım ve doğrulama

[JSON render raporu](diagram-render-results.json) her kaynak için path/block/hash, metadata, outcome ve renderer ortamını tutar. Docs lint link/fence/inventory sayar; parser/render veya ürün testinin yerine geçmez. Hash güncel değilse eski render sonucu yeni kaynağın kanıtı değildir.

GitHub dosya read-back ve local render ayrı doğrulamadır; GitHub Preview'da ayrıca denenenler inceleme kaydında adlarıyla belirtilir. Yeni diagram eklenince inventory, source hash, varsa SVG fallback ve semantic contract birlikte incelenir. Accepted niyet ile proposed implementation birleştirilmez.

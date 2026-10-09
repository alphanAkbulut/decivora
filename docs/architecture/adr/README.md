# ADR dizini

ADR'ler henüz uygulanan teknoloji kararları değildir. Kabul edilmiş kullanıcı ilkesi ile önerilen teknik çözüm her dosyada ayrılır. Karar değiştiğinde eski ADR silinmez; yeni ADR supersedes bağlantısı taşır.

- [ADR-0001 — Yerel canonical store](0001-local-canonical-store.md)
- [ADR-0002 — Append-only log ve current projection](0002-event-log-projections.md)
- [ADR-0003 — Yüzeye özel capture + MCP](0003-capture-adapters.md)
- [ADR-0004 — Tipli gerekçe grafiği](0004-decision-aware-impact.md)
- [ADR-0005 — Hazır onay ve evidence-bound state](0005-review-verification.md)
- [ADR-0006 — Deterministik iş ve hedefli bağlam](0006-cost-aware-routing.md)
- [ADR-0007 — Kalıcı işleme ve etkisiz replay](0007-durable-processing.md)
- [ADR-0008 — Snapshot'a bağlı onay ve ayrı çalıştırma yetkisi](0008-approval-snapshot-authority.md)

0007, 0002/0003'ü; 0008, 0004/0005'i tamamlar. Hiçbiri önceki ürün ilkelerini geçersiz kılmaz. 2026-10-09 [mimari inceleme tablosu](../../quality/completeness-review.md) bütün ADR'lerin yeniden değerlendirmesini ve gereken kanıtı kaydeder.

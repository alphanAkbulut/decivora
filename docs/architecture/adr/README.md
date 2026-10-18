# ADR dizini

ADR-0012, Q15-A ile ilk runtime/koşullu build için kabul edildi; diğer ADR'lerin kapsam/statüleri kendi dosyalarında korunur. Kabul edilmiş seçim uygulanmış özellik demek değildir. Kabul edilmiş kullanıcı ilkesi ile önerilen teknik çözüm her dosyada ayrılır. Karar değiştiğinde eski ADR silinmez; yeni ADR supersedes bağlantısı taşır.

- [ADR-0001 — Yerel canonical store](0001-local-canonical-store.md)
- [ADR-0002 — Append-only log ve current projection](0002-event-log-projections.md)
- [ADR-0003 — Yüzeye özel capture + MCP](0003-capture-adapters.md)
- [ADR-0004 — Tipli gerekçe grafiği](0004-decision-aware-impact.md)
- [ADR-0005 — Hazır onay ve evidence-bound state](0005-review-verification.md)
- [ADR-0006 — Deterministik iş ve hedefli bağlam](0006-cost-aware-routing.md)
- [ADR-0007 — Kalıcı işleme ve etkisiz replay](0007-durable-processing.md)
- [ADR-0008 — Snapshot'a bağlı onay ve ayrı çalıştırma yetkisi](0008-approval-snapshot-authority.md)

0007, 0002/0003'ü; 0008, 0004/0005'i tamamlar. Hiçbiri önceki ürün ilkelerini geçersiz kılmaz. 2026-10-09 [mimari inceleme tablosu](../../quality/completeness-review.md) bütün ADR'lerin yeniden değerlendirmesini ve gereken kanıtı kaydeder.

- [ADR-0009 — Kapsamlı insan/agent principal ve grant](0009-scoped-principals.md)
- [ADR-0010 — Depolama katmanları ve veri yaşam döngüsü](0010-storage-lifecycle.md)

0009, 0005/0008'i; 0010, 0001/0002/0007'yi tamamlar. Rol matrisi, ekip DB geçişi, retention sayıları ve capacity hedefleri öneridir; onaylanmış/uygulanmış kabul edilmez.

- [ADR-0011 — Hedef uygulama gözlemi ve ayrı kabul kanıtı](0011-target-application-evidence.md)

0011, 0005/0008/0010'u tamamlar; mevcut event/kimlik/impact ilkelerini iptal etmez. [Güncel tasarım revizyonu](../../product/current-direction.md) ilk yatırım odağını belirtir; Q15-A/ADR-0012 koşullu ilk build/runtime kabulüdür; diğer mimari ayrıntıların statüleri ve native/ROI kapıları korunur. Genel mimariyi komple tekrar sürüm kopyasına dönüştürmeyin.

- [ADR-0012 — Koşullu yerel MVP çekirdeği ve Python runtime](0012-conditional-python-runtime.md): accepted Q15-A; T01/T02/T03 kalite/ROI kapıları açık.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

[ADR-0013](0013-task-workflow-and-familiar-ui.md): accepted task workflow ve tanıdık UI; physical schema1 korunur, local human verifier ile native/automatic doğrulama sınırı ayrıdır.

## Current local delivery — 14 October 2026

[API-independent implementation and follow-up gates](../../delivery/api-independent-development.md): bounded stdioMCP/create-only human review, optional explicit-root file SHA verification, recorded graph/audit timeline, routing/null usage and session-only health. Historical implementation limits above refer to their original deliveries; current limits and M01–M14 checks are in the linked report. No native capture, full brief/delta, sandbox test/deploy verifier, exact host token savings or global language quality is claimed.

- [ADR-0014 — Local Operations and separate TEST environment](0014-local-operations-and-test-environment.md): accepted local implementation direction,19October2026; bounded diagnostics, not full end-to-end tracing/platform administration.

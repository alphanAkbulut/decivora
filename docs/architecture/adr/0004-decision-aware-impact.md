# ADR-0004 — Tipli gerekçe grafiği

**Durum:** Ürün yönü kabul edilmiş; ifade/saklama tasarımı öneri.

## Bağlam

Eski kararı kaldırmak, ona bağlı bütün işleri gereksiz yapmaz.

## Önerilen karar

required_by ile depends_on ayrılır; AND/OR/unknown gerekçe ifadeleri; bounded traversal + gerekirse AI; semantic iptal insan onaylı.

## Alternatifler

Düz task listesi; bütün task'ları her mesajda LLM'e gönderme; graph database zorunluluğu.

## Sonuçlar ve risk

Az bağlamla explainable impact; yanlış/eksik edge false negative yaratabilir.

## Doğrulama / yeniden açma koşulu

Çoklu gerekçe, eksik link, cycle, done artifact ve stale approval testleri; periyodik orphan audit.

Kaynak: [Karar haritası](../../product/decision-map.md), [evrim kaydı](../../discovery/evolution.md). Onaylayan/tarih henüz atanmadı; kullanıcı niyeti teknik uygulama onayıyla eşitlenmez.


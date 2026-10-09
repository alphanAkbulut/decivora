# ADR-0003 — Yüzeye özel capture + MCP

**Durum:** Öneri; her adapter teknik kanıt bekliyor.

## Bağlam

MCP çağrısını agent unutabilir; platformlar aynı konuşma erişimini sağlamaz.

## Önerilen karar

Hooks/session events pasif sinyal, MCP aktif kayıt, reconciliation missed capture kontrolü; izinli import fallback.

## Alternatifler

Yalnız skill; yalnız manuel import; genel tarayıcı scraping.

## Sonuçlar ve risk

Capability ve coverage açık olur; daha fazla adapter bakımı gerekir.

## Doğrulama / yeniden açma koşulu

İki coding yüzeyinde sürüm sabitli deney. Normal chat erişimini ayrıca ölç; desteklenmeyeni otomatik diye gösterme.

Kaynak: [Karar haritası](../../product/decision-map.md), [evrim kaydı](../../discovery/evolution.md). Onaylayan/tarih henüz atanmadı; kullanıcı niyeti teknik uygulama onayıyla eşitlenmez.


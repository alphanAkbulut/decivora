# ADR-0001 — Yerel canonical store

**Durum:** Öneri; P0 build/extend deneyi sonrası kesinleşir.

## Bağlam

Araştırma ve kodlama çıktıları aynı projede; repo zorunlu değil. Üç task motorunu eşzamanlamak gereksiz authority çatışması yaratır.

## Önerilen karar

Tek local service ve SQLite canonical domain store; kaynak payload, domain log ve projection mantıksal olarak ayrılır. Markdown export/plan olabilir; runtime authority değildir.

## Alternatifler

Beads üstüne genişleme; Cortex/mai-mcp uyarlama; PostgreSQL; Markdown canonical state.

## Sonuçlar ve risk

Küçük kurulum ve transaction avantajı; migration, backup ve tek-yazar yönetimi sorumluluğu bize geçer.

## Doğrulama / yeniden açma koşulu

P0 corpus'u en yakın alternatiflerle karşılaştır. SQLite atomic/replay/crash prototipini ölç. Çok cihaz/ekip ihtiyacı veya store uyumsuzluğu kararı yeniden açar.

Kaynak: [Karar haritası](../../product/decision-map.md), [evrim kaydı](../../discovery/evolution.md). Onaylayan/tarih henüz atanmadı; kullanıcı niyeti teknik uygulama onayıyla eşitlenmez.


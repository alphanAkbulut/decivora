# ADR-0006 — Deterministik iş ve hedefli bağlam

**Durum:** Ürün yönü kabul edilmiş; routing eşikleri öneri.

## Bağlam

Her işlem için model çağırmak ve tüm projeyi tekrar okutmak maliyet yaratır.

## Önerilen karar

İş sınıfı/yürütücü ayrımı; deterministic-first; budgeted retrieval/model escalation; usage nullable.

## Alternatifler

Her işi güçlü modele verme; yalnız insan yönetimi; ölçümsüz ucuz model.

## Sonuçlar ve risk

Maliyet görünürlüğü; düşük bütçe recall'u düşürebilir, bu yüzden quality gate gerekir.

## Doğrulama / yeniden açma koşulu

Eş corpus/kalite ile baseline karşılaştır; schema overhead, retries ve unknown usage dahil.

Kaynak: [Karar haritası](../../product/decision-map.md), [evrim kaydı](../../discovery/evolution.md). Onaylayan/tarih henüz atanmadı; kullanıcı niyeti teknik uygulama onayıyla eşitlenmez.


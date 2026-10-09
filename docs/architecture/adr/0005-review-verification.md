# ADR-0005 — Hazır onay ve evidence-bound state

**Durum:** Ürün ilkeleri kabul edilmiş; policy ayrıntısı öneri.

## Bağlam

Kullanıcı onay vermeye razı; kart ve DoD yazmak istemiyor. Agent iddiası test değil.

## Önerilen karar

Generated changeset, digest/revision-bound approval; implementation ve verification ayrı; kanıt AC/artifact revision'a bağlı.

## Alternatifler

Her şeyi auto-apply; her metadata için modal; serbest metin zorunluluğu.

## Sonuçlar ve risk

İnsan kontrolü ve düşük giriş yükü; review kuyruğu/eskime yönetilmeli.

## Doğrulama / yeniden açma koşulu

No-text review flow, yanlış done, test failure, partial approval ve iki-agent race senaryosu.

Kaynak: [Karar haritası](../../product/decision-map.md), [evrim kaydı](../../discovery/evolution.md). Onaylayan/tarih henüz atanmadı; kullanıcı niyeti teknik uygulama onayıyla eşitlenmez.


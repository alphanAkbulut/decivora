# ADR-0002 — Append-only log ve current projection

**Durum:** Ürün ilkesi kabul edilmiş; teknik biçim öneri.

## Bağlam

Hatalı tamamlanma ve değişen karar düzeltilmeli fakat önceki iddia kaybolmamalı.

## Önerilen karar

Domain olayları append-only; records/edges projection. Düzeltme compensating event; onay ve projection aynı transaction.

## Alternatifler

Mutable row + audit side table; tam event-sourcing framework.

## Sonuçlar ve risk

Replay ve gerekçe izlenebilirliği; şema evrimi ve privacy erase istisnası karmaşıklığı.

## Doğrulama / yeniden açma koşulu

Deterministik replay, crash atomicity, migration ve restore drill. Admin tamper-proof iddiası yok.

Kaynak: [Karar haritası](../../product/decision-map.md), [evrim kaydı](../../discovery/evolution.md). Onaylayan/tarih henüz atanmadı; kullanıcı niyeti teknik uygulama onayıyla eşitlenmez.


# ADR-0007 — Kalıcı işleme ve etkisiz replay

**Durum: öneri; 2026-10-09 mimari incelemesinde eklendi.** Önceki ADR'leri iptal etmez; ADR-0002/0003'ün işletim sözleşmesini tamamlar. Onaylayan ve uygulama kanıtı henüz yoktur.

## Problem

Source alındıktan sonra model başarısız olabilir; session-end gelmeyebilir. Restore sırasında replay'in tekrar dış mesaj/iş üretmesi duplicate etki yaratabilir. Tek cursor ve “retry et” ifadesi bu durumları yeterince tanımlamaz.

## Önerilen karar

Kalıcı source+job kaydı sonrası receipt; ayrı ingest ve processing cursors; bounded queue, lease/fencing, idempotent completion ve görünür quarantine. Replay yalnız kayıtlı domain olaylarından projection üretir; LLM/verifier/outbox teslimi yapmaz. Restore sonrası uzak yazılar reconciliation yapılana kadar durur. [Runtime sözleşmesi](../runtime-contracts.md) ayrıntıları tanımlar.

## Alternatifler ve sonuç

Hook içinde eşzamanlı model çağrısı: basit ama hook gecikmesi ve veri kaybı riski. Memory queue: kolay ama crash'te ack edilmiş veri kaybı. Harici broker: gelecek ölçek için seçenek, yerel MVP'ye işletim yükü. Öneri başlangıçta aynı yerel store'da dayanıklı job tablosudur; ayrı broker zorunlu değildir.

Ek durum ve recovery kodu gerekir. At-least-once teslim açıkça kabul edilir; exactly-once provider vaadi verilmez. Maliyet limiti işleri kaybettirmez, deferred yapar.

## Kabul ve yeniden açma

T06/T07/T08: V19–V21; T15: V27; T23: restore testi. Disk dolması, commit sonrası response kaybı, lease devri ve replay yan etkisizliği kanıtlanmalıdır. Çok cihazlı queue/ölçek ihtiyacı veya yerel storage sınırı bu ADR'yi yeniden açar.

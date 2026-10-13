# ADR-0008 — Snapshot'a bağlı onay ve ayrı çalıştırma yetkisi

**Durum: öneri; 2026-10-09 mimari incelemesinde eklendi.** ADR-0004/0005'i tamamlar; kullanıcı ilkeleri ile teknik kontrol tasarımı ayrı tutulur. Local T08/T12/T13a snapshot/onay diliminin [uygulama kanıtı](../../quality/review-kernel.md) artık vardır; tam ADR/policy, gerçek login/runner ve T13b/c/e–T14 kabulü açıktır.

## Problem

Onay preview'sundan sonra task'a yeni gerekçe edge'i eklenebilir. Task revision'ı değişmese bile obsolete önerisi yanlış olur. Ayrıca modelin çıkardığı bir test komutunu çalıştırmak, sadece task'ı izleme izninden türetilemez.

## Önerilen karar

MVP impact preview'su project knowledge revision taşır. Decision/requirement/edge/justification değişimi revision'ı artırır; apply tüm base revision, graph/AC snapshot, policy ve digest'i aynı transaction'da denetler. Eski onay stale döner. İnsan approval oturumu, agent proposal kimliği ve verifier runner capability ayrıdır. Transcript runner komutu veya insan onay yetkisi vermez.

Karar tek başına kabul edilirse etkilenen işlerde impact review beklemesi görünür olur. Toplu işlemde bağımlı operations atomik kalır. Ayrıntılar [runtime sözleşmesinde](../runtime-contracts.md).

## Alternatifler ve sonuç

Yalnız record version: yeni edge yarışını kaçırabilir. Uzun DB transaction içinde model: writer kilidi ve timeout sorunu. İnce read-set/predicate kontrolü: daha az yanlış stale ama daha karmaşık. MVP için project knowledge revision muhafazakâr ve anlaşılırdır; yoğun projede fazla stale üretebilir.

Verifier için her rapora güvenmek yanlış done riski; her test için modal istemek kullanıcı yükü yaratır. Öneri önceden izinli, sınırlandırılmış runner ve revision-bound evidence; desteklenmeyen kontrol unknown/manual review kalır.

## Kabul ve yeniden açma

T08/T12/T13: yeni OR edge yarışı, policy değişimi, partial approval ve agent impersonation. T14: untrusted command ile script çalışmaması ve stale artifact kanıtı. V22–V24/V28 bu kapılardır. T24'te yanlış stale oranı ölçülür; darboğaz kanıtı varsa P2'de daha ince concurrency modeli önerilir.

# ADR-0009 — İnsan ve agent için kapsamlı yetki

**Durum: önerilen; uygulama/onay kanıtı yok.** 2026-10-09. ADR-0005/0008'i tamamlar. Ürün ihtiyacı kullanıcı tarafından istendi; aşağıdaki ayrıntılı rol/policy teknik öneridir.

## Problem

Projeye üye olmak tüm özel kaynaklara erişmek değildir. İnsan adına çalışan agent, insanın bütün yetkilerini alamaz. Bir üyelik iptali, queue'da bekleyen iş veya eski approval üzerinden aşılmamalı. Tek kişilik MVP'nin veri modeli ileride tenant ayrımını pahalı bir migration'a bırakmamalı.

## Öneri

Workspace tenant, project membership ve ayrı human/agent/system principal. Rol preset'leri nesne permission'larına çevrilir. Agent çalışması süreli grant ve task/run kapsamıyla kısıtlanır; insan adına çalışma etkin izinlerin kesişimidir. İnsan approval yetkisi devredilemez. Değişiklikler knowledge/policy revision yanında authz revision'a da bağlanır. Türetilmiş hafıza kaynak görünürlüğünü korur; paylaşım ayrı bilinçli işlemdir.

## Alternatifler ve bedeller

| Alternatif | Değerlendirme |
|---|---|
| Tek owner token'ını bütün agent'larla paylaş | Basit fakat atıf/revocation/en az yetki bozulur; reddedilen yön |
| Yalnız workspace rolü | Private proje/kaynak ve dar task iznini ifade edemez |
| İlk gün tam OpenFGA servisi/custom role editor | Esnek, fakat yerel P1 işletim yükü gereksiz; boundary korunur, ihtiyaçta tekrar değerlendirilir |
| DB RLS ile bütün authorization | Local SQLite'a uymaz; model context ve dış egress kararlarını tek başına çözmez |

Bedel: her sensitive dispatch/commit için güncel izin; invalidation ve onay staleness artabilir. Permission cache yalnız revision güvenliği ile kullanılabilir. Ekipte bağımsız insan review bekleme yaratabilir; korunan işlem kapsamı gerçek kullanımda ölçülmeli.

## Kabul kapısı

P1: T05b/T08b/T18b kapsamındaki tek owner + dar agent sözleşmeleri ve MU01–MU06/MU10 erişilebilir yolları. Ekip açılmadan: davet/offboarding, bağımsız reviewer, tenant DB/ACL, shared summaries, connector ve support access testleri. Ayrıntı [rol ve lifecycle modeli](../identity-access.md), [fazlı plan](../../delivery/team-data-plan.md), [benchmark](../../discovery/collaboration-storage-benchmark.md).

Bu ADR kabul edilene kadar ürün kodunda teknoloji veya custom role bağımlılığı seçilmiş sayılmaz. Aynı OS hesabına tam dosya/shell erişimi olan agent'a karşı servis API'si fiziksel güvenlik sınırı değildir.

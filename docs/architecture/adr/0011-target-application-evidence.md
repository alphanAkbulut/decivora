# ADR-0011 — Hedef uygulama gözlemi ile kabul kanıtını ayırma

**Durum: teknik öneri; 2026-10-11. Uygulanmadı.** Kullanıcı dosya üretimi sonrası yükleme ve gerçek yaklaşım seçiminin bilinmemesini problem olarak bildirdi. ADR-0005/0008/0010'u tamamlar; yeni servis veya kesin DB stack kararı değildir.

## Bağlam ve öneri

Generated artifact hedefte uygulanmış iş değildir. Sessizlik insan seçimi değildir. Güvenilir karar kaydı, expected artifact etkisi, exact hedef ve revision'a bağlı uygulama gözlemi ayrı tutulur. ApplicationAssessment mevcut ENG-08 üzerinden policy/event yoluna girer; acceptance VerificationAssessment ile aynı completion kapısı değildir. İnsan attestation'ın dayanağı açık, otomatik read-back'ten farklıdır.

[Domain modeli](../domain-model.md) ve [ER-03](../data-relationships.md#er-03--artifact-hedef-uygulama-ve-kabul-ayrımı) ApplicationExpectation/Target/Observation/Assessment ve çoklu artifact bağlarını önerir. [GAP-01–10](../../product/intent-to-reality-gap.md) oracle'ıdır.

## Alternatifler ve bedeller

| Alternatif | Neden yeterli değil / bedel |
|---|---|
| Yalnız konuşma özeti | Yükleme önerisini gerçekleşmiş olaya dönüştürebilir; dış gözlem yok |
| Her “yükledim” ifadesini otomatik verified saymak | Authority, hedef, sürüm ve AC/test kapsamı kaybolur |
| Her mesajda bütün dosyaları kontrol etmek | İzin, API/token, gizlilik ve kullanıcı gecikmesi yükü |
| Her defasında kullanıcıya tekrar sormak | Yönetim yükünü artırır; mevcut güvenilir karar/kanıt tekrar kullanılabilir |

Önerilen read-back talep veya ilgili değişimle bounded; cache sadece hedef snapshot ve freshness policy'siyle. Ağ/DB transaction birlikte tutulmaz. Unknown veya erişim reddi missing değildir; partial mismatches toplu başarı sayılmaz. Artifact bulundu diye test/deploy gerçekleşmiş sayılmaz.

## Kabul / yeniden açma

T01/T02/T03 karşılaştırma, T14d/T18i/T20i/T24n ve GAP-01–10. Geç karar/AC/target değişimi eski assessment'ı stale yapar. İzin iptalinde yeni read yok; sırf eski receipt var diye current yetki verilmez. Native Projects/extension yeterliyse bağımsız uygulama ihtiyacı yeniden değerlendirilir. Gerçek model/host kullanım kanıtı yokken context aktarımı başarı ilan edilmez.

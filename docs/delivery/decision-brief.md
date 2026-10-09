# Owner soruları ve teknik karar hazırlığı

**2026-10-09.** Amaç kullanıcıya bütün teknik tasarımı seçtirmek değil; yalnız ihtiyaç, erişim, veri ve maliyet tercihlerini almak. Cevap alınmaması karar veya izin sayılmaz. Bu kayıt geçici karar kuyruğudur; AGENTS.md içine taşınmaz.

## Şimdi sorulan üç konu

| ID | Soru | Durum / cevap | Etkisi |
|---|---|---|---|
| Q01 | İlk pilot kimin işiyle doğrulansın? | **Kabul edildi:** önce owner'ın bireysel kullanımı, sonra benzer kullanıcılar. Kullanıcının bu oturumdaki açık cevabı | İlk UX ve araştırma örneklemi; tam kapsam ve P4 ekip vizyonu korunur |
| Q02 | Günlük kullanılan coding/chat yüzeyleri, pilotun zorunlu ilk ikisi ve hedef OS? | Soruldu, cevap bekleniyor | T02 capability deneyi sırası, kurulum/host matrisi. Tam MVP'nin iki coding adapter hedefi kendiliğinden düşmez |
| Q03 | Ayıklanmış sohbet parçaları harici API'ye gönderilebilir mi; aylık bütçe tavanı? | Soruldu, cevap bekleniyor | OPEN-08/10; gerçek veri ve ücretli model deneyi. Yanıt yokken yalnız doküman ve sentetik, ücret yaratmayan hazırlık |

Q01 müşteri talebi veya pazar segmenti doğrulaması değildir. Q02'de mevcut bilgisayarın gözlenmesi desteklenecek tek OS seçimi sayılmaz. Q03'te genel API istekliliği tüm özel konuşmaların aktarım izni yerine geçmez; kaynak ve redaction sınırı pilotta somutlaştırılır.

## Şimdi cevap gerektirmeyen ama unutulmayacak kararlar

| Konu | Kimin hazırlayacağı / öneri | Owner'a ne zaman sunulacak? |
|---|---|---|
| Build veya extend | Engineering: Cortex/mai-mcp/Tracker/Beads aynı fixture; lisans/bakım/veri modeli farkı | T03'te sonuç ve somut alternatif; kanıt olmadan soyut seçim sorulmaz |
| Runtime, storage ve UI paketleri | Engineering: local service + SQLite + TypeScript aday; küçük transaction/adapter spike | T03 sonrası ADR seçenek/fayda/risk/kanıt |
| Batch, lease, timeout, context limiti | Engineering: baseline'a dayalı sınırlı config | Kullanıcı deneyimi veya maliyet trade-off'u varsa; rutin sayısal ayarı owner'a devretme |
| Hangi değişiklikler otomatik? | Kabul edilmiş ilke: capture/öneri otomatik, kabul edilmiş karar/scope değişimi insan onaylı; ayrıntılar taslak | Hazır review örneğiyle T13/T19; cevap beklerken daha geniş otomasyon varsayma |
| Retention, encryption, backup | Engineering: gerçek veri yaşam döngüsü ve restore önerisi | Gerçek veri pilotu öncesi OPEN-08/12 |
| “Başarılı pilot” eşiği | Engineering: golden corpus ve manuel baseline; false closure sıfır invariant | T01/T24'te ölçülebilir örnekle. Mevcut yüzde hedefleri henüz owner taahhüdü değil |
| Lisans, marka ve commercial boundary | Lisans/metin/isim incelemesiyle alternatifler | Public release öncesi; bu özel repo turunda zorunlu seçim değil |

## Cevap geldikten sonra güncelleme sırası

1. Yanıtı kapsamıyla bu tabloda kaydet; açık karar ve varsayımla ayır.
2. Yalnız etkilenen status/pilot planı/adapter deney sırasını güncelle. Tam vizyonu daraltma.
3. Veri/maliyet izni gerekiyorsa deneyin somut veri kümesi, provider ve tavanına uygula; sınırsız onay çıkarma.
4. Bağımsız hazırlığı sürdür. T01/T02/T03 tamamlanmadan uygulama veya benchmark sonucu varmış gibi iş kapatma.

Bağlantılar: [açık kararlar](../governance/open-decisions.md), [kullanıcı araştırması](../discovery/user-research.md), [benchmark bulguları](../discovery/benchmark-findings.md), [proje yönetim planı](project-management.md).

## UI ve token tercihi — takip soruları

2026-10-09 kullanıcının talebi üzerine iki somut seçenek soruldu ve yanıt alındı. Kabul edilen ürün tercihi ile hâlâ açık dosya/harcama kararı aşağıda ayrılır.

| ID | Soru / seçenekler | Durum | Etkisi |
|---|---|---|---|
| Q04 | Graph ilk açılış ve olgunlaşma görünümü | **Kabul edildi:** güncel işler + seçili işin bağlamı; fikirlerin evrimi, önemli değişimlerin gerekçesi ve task AC/DoD/test görünürlüğü isteniyor | Default graph + context/acceptance sekmesi; tarihçe korunur |
| Q05 | Proje/görev analiz sıklığı | **Kabul edildi:** kullanıcı proje başlangıcında seçebilmeli, task bazında değiştirebilmeli ve ileride yeni yaklaşım seçebilmeli | Tek global profil dayatılmaz; tavan/egress onayı değişmez |
| Q06 | Ana iş milestone'larında context özeti + otomatik sürümlü Markdown mı; yoksa yalnız istek üzerine export mu? | Soruldu; cevap bekleniyor | Uygulama içi context her iki seçenekte var; otomatik Git push yok |

Q02 ilk coding/chat yüzeyleri/OS ve Q03 dış model/veri/aylık bütçe soruları hâlâ açık. Tekrar sorularak yeni yanıt varmış gibi yazılmadı. Q05 tercihi Q03'ün yerine geçmez; ücretli arka plan modeli Q03 kararı olmadan açılmaz. Sayısal token/batch sınırlarını kullanıcıya seçtirmek yerine engineering deneyleriyle kalibre edeceğiz.

Öneri paketleri: [connection/context](../architecture/connection-and-context.md), [token ekonomisi](../architecture/routing-token-economy.md), [graph deneyimi](../product/graph-experience.md). Q04/Q05 yanıtları graph, task context ve token profil sözleşmesine işlendi. Q06 yanıtı geldiğinde yalnız export üretim tercihi ve bu kayıt güncellenecek.

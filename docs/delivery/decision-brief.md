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

## Geçmiş aktarımı ve görev boyutu — Q07–Q09

**2026-10-09, Q07 / kullanıcıya gösterilen soru 1:** Kullanıcı “önerin ne ise onla devam edelim … 1C'yi şu sebeple seçtik” diyerek öneriyi kabul etti. Ürün kararı **1C: açıkça izin verilmiş ve erişilebilen geçmişin tamamını, aktif işlere öncelik vererek aşamalı işlemek**. DEC-15 kabul edilen niyeti; bağlantı/retention belgeleri önerilen uygulama sözleşmesini taşır.

| Alternatif | Kazanç / maliyet | Karar ve gerekçe |
|---|---|---|
| 1A — Yalnız seçilen konuşma veya tarih aralığı | İlk işleme daha küçük; seçimin dışında eski gerekçeler kalabilir | Varsayılan seçilmedi. Kullanıcı kaynak iznini sınırlamak isterse geçerli bir kapsam seçeneği olarak korunur |
| 1B — Yalnız bağlantı sonrasındaki konuşmalar | En az geçmiş hazırlığı; önceki kararların evrimi bulunmaz | Varsayılan seçilmedi; mevcut bağlamı koruma hedefini tek başına karşılamaz. Geçmiş erişilemiyorsa açık coverage uyarısıyla kullanılabilir |
| **1C — İzinli ve erişilebilir geçmiş, aşamalı işleme** | İlk indeksleme/çıkarım ve depolama yükü daha büyük; gerekçe ve alternatifleri sonradan bulma imkânı sağlar | **Seçildi.** Kaynağı koruma ile her çağrıda dar bağlam kullanmayı ayırır; aktif işler önce, kalan geçmiş görünür kuyrukta |

1C, bütün geçmişi her çağrıda modele göndermek veya geçmişteki her öneriyi aktif görev yapmak değildir. Sürüm bağlı kaynak, sonuç cache'i, delta işleme ve gerektiğinde orijinal parçaya dönüş kullanılır. En düşük maliyet veya kusursuz hatırlama kanıtlanmış değildir; kaynak bulunabilirliği ve karar/ilişki recall'u token maliyetiyle birlikte ölçülecek. Kabul, şu anda hesaplardan veri toplama, harici modele gönderme veya ücretli çağrı izni vermez; Q02/Q03 ve OPEN-08 geçerlidir.

| ID / kullanıcı soru no | Seçenekler | Durum |
|---|---|---|
| Q08 / 2 — Task boyutu | 2A: anlamlı ana/alt görev + küçük adımlarda checklist; 2B: her küçük adım ayrı task; 2C: yalnız büyük işler | **Öneri: 2A.** Kullanıcı ayrıca “bu taskı alt görevlere böl ve takibi öyle gerçekleştir” seçeneğini değerlendirmemizi istedi. İsteğe bağlı önizlemeli bölme tasarlandı; varsayılan otomatik bölme kararı alınmadı |
| Q09 / 3 — Dikkat ve iş önceliği | Önceki alternatifler: 3A engelleyici/önemli konular hemen, kalanlar inbox; 3B hepsi inbox; 3C her anlamlı değişimde bildirim | **Öncelik ilkesi kabul edildi:** blocker'lar ve diğer işleri geciktiren bağımlılıklar önce; tüm projede Product Owner ve çevik ürün yaklaşımı. Bu yanıt 3A'nın anlık kanal/zamanlama ayrıntılarını bütünüyle seçmiş sayılmaz; bunlar açık, servis/otomasyon yok |

Q08 önerisinin kazanımları ve sınırları [task bağlamı belgesinde](../product/task-context-and-acceptance.md#isteğe-bağlı-alt-görevlere-böl-ve-takip-et) yer alır. Q06 otomatik Markdown tercihi hâlâ açıktır. Bu kayıt seçeneklerin neden elendiğini korur; henüz cevaplanmayan tercihleri kabul edilmiş göstermez.

Q09 yanıtı ayrıca Scrum Alliance yaklaşımından yararlanma yönlendirmesi içerir. [Öncelik/akış sözleşmesi](../product/priority-and-flow.md) ve [Scrum kaynaklı çalışma planı](project-management.md) hazırlandı. Takım rolleri, sabit Sprint takvimi ve dış bildirim kanalı atanmış değildir. Q08 otomatik/parçalı task tercihi bu yanıtla cevaplanmış sayılmaz. Kısa öğrenme/teslim döngüleri şimdiki çalışma yaklaşımıdır; tam Scrum uygulaması veya sertifikasyon iddiası yoktur.

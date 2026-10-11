# Owner soruları ve teknik karar hazırlığı

**2026-10-09.** Amaç kullanıcıya bütün teknik tasarımı seçtirmek değil; yalnız ihtiyaç, erişim, veri ve maliyet tercihlerini almak. Cevap alınmaması karar veya izin sayılmaz. Bu kayıt geçici karar kuyruğudur; AGENTS.md içine taşınmaz.

## Şimdi sorulan üç konu

| ID | Soru | Durum / cevap | Etkisi |
|---|---|---|---|
| Q01 | İlk pilot kimin işiyle doğrulansın? | **Kabul edildi:** önce owner'ın bireysel kullanımı, sonra benzer kullanıcılar. Kullanıcının bu oturumdaki açık cevabı | İlk UX ve araştırma örneklemi; tam kapsam ve P4 ekip vizyonu korunur |
| Q02 | Günlük kullanılan coding/chat yüzeyleri, pilotun zorunlu ilk ikisi ve hedef OS? | Kısmen cevaplandı: Q02-R1 A ilk pilot, B sonraki hedef; OS/host ve somut kaynak/hedef açık | T02 capability deneyi sırası, kurulum/host matrisi. Tam MVP'nin iki coding adapter hedefi kendiliğinden düşmez |
| Q03 | Ayıklanmış sohbet parçaları harici API'ye gönderilebilir mi; aylık bütçe tavanı? | Kısmen cevaplandı: Q03-R1 A; ilk deney ek ücretli model API'si olmadan. Sonraki gerçek veri/provider/bütçe açık | OPEN-08/10; ilk dilim etiketli fixture/kod kontrolleri. Otomatik anlam çıkarımını uygulama/test etme gereksinimi sabit; model/veri/bütçe ve deney zamanı ayrıca somutlaştırılır |

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

## Çok-agent ve ekip kurulumu — kapsam netleştirmesi

2026-10-09 kullanıcı tek insanın birden fazla agent'ın işlerini izlemesini ve ürünü kendi ekibine kurabilmesini sordu; agent girdileri/gözlenebilir davranışların kapsanmasını istedi. Mevcut INT-02/TEAM-01 ihtiyacı [işletim sözleşmesiyle](../architecture/agent-and-team-operation.md) açıldı. İlk bireysel pilot korunur; T02c/T18d/T24e çok-agent gözlem dilimleri, C01–C04 ekip kurulum/davet/giriş akışı olarak ayrıdır.

Bu istek belirli bir host/SDK, hidden reasoning erişimi, harici veri aktarımı, yeni provider ücreti veya hosted ürün satın alımı kararı değildir. Q02/Q03 ve OPEN-14–16 kapıları geçerlidir. Gözlenebilir olayların davranış örüntüsü analizi önerildi; modelin iç düşünce yapısını bildiğimiz iddia edilmez. Owner'ın mevcut hesabını ekibe/agent'lara dağıtma yaklaşımı önerilmez.

## Q10 — Yeni kaynakların keşfi ve bağlanması

**2026-10-10 / cevaplandı: A kabul edildi.** Kullanıcının seçili öneriye verdiği “1a ile devam” yanıtı Q10-A'ya aittir; geçmiş işleme kapsamındaki Q07/1C kararını değiştirmez. Kullanıcı proje erişim alanları ve izni veren kişilerin görünürlüğünü istedi. [Erişim sözleşmesi](../architecture/connection-and-context.md#proje-erişim-sözleşmesi-ve-izin-ekranı) kurulumda hedef/kaynak, işlemler, geçmiş, görünürlük, egress ve süre sorularını tanımlar. Bunlar ürünün onboarding sorularıdır; bugünkü dokümantasyon çalışmasına yeni gerçek bağlantı izni vermez.

Ürün tercihi sorusu: İzinli hesabında yeni repo/proje bulunduğunda sistem ne yapsın?

- **A — Seçildi:** Kullanıcı ayrıca metadata keşfine izin vermişse yeni kaynağı bağlama önerisi göster; içerik okuma veya capture yalnız kaynak seçimi ve gerekli onaydan sonra başlasın. Manuel bağlantı da mümkün kalsın.
- **B — Alternatif olarak korundu, varsayılan seçilmedi:** Yalnız kullanıcının elle seçtiği/verdiği kaynaklarla çalış; hesap genelinde metadata keşfi ve yeni kaynak önerisi yapma.

İkisi de otomatik tüm-proje yetkisi içermez. A önerisi aktif keşif zorunluluğu değildir; provider listeleme kapsamı gerçekten ayrıştırılabiliyorsa sunulur. Bu ayrım uygulama öncesi capability deneyi ister. Seçim gerekçesi: yeni kaynakları fark etme kolaylığı sağlarken içerik erişimini kullanıcı seçimine bağlı tutar. Bu ürün tercihi, bugün herhangi bir hesabı listeleme izni değildir; her bağlantıda ayrıca açık metadata/list izni gerekir. Bu izin yoksa keşif kapalıdır ve manuel bağlantı kullanılır. Q03 dış veri/bütçe, Q07/1C izinli geçmiş ve OPEN-14 ekip yetki kapısı korunur. Bağlantı için read/capture/proposal başlangıç paketi teknik öneridir; dış yazma, execution veya scope onayı kabul edilmiş sayılmaz.

## Q11 — İlk devam düğmesi

**2026-10-11 / cevap bekleniyor.** Yapıştırılan metindeki önceki assistant cevabı A'yı öneriyor; kullanıcı tercihi sayılmaz. [Somut paket ve izin tasarımı](../product/resume-package-and-memory.md), [Spike-1 v1 görev planı](spike-1-v1.md) hazırlandı.

- **A — Önerilen:** İlk deneyde önizle/kopyala; kullanıcı istediği araçta yapıştırır. Paket kalitesi/fresh-session testi ve düşük kurulum eforu öne çıkar.
- **B:** İlk deneyde host'a teslim/başlat seçeneğinin fizibilitesini de araştır. Gerçek uygulama ayrıca host capability, somut hedef/path, izin ve maliyet doğrulaması ister; bu tercih tek başına agent başlatma yetkisi değildir.

MVP'yi “unutulanlar radarı” olarak yeniden tanımlama onayı yok; bu ifade pilot konumlandırma adayıdır. Çalışan Spike-0 kaydı bu repoda bulunmadı. Gerçek 3–5 oturum ve iki haftalık pilot için kaynak/model/bütçe ve takvim ayrıca somutlaştırılır. Q03 kararı yerine öneriden izin çıkarılmaz.

## 2026-10-11 — Son evrimi belgelere yansıtma

Kullanıcı tüm diagram/şema/giriş/analiz belgelerinin güncel yönle tutarlı olmasını, eski ve güncel planın karşılaştırılmasını ve sürüm kopyalarının kafa karıştırmamasını istedi. **Doküman güncelleme yetkisi vardır**; independent build, iptal veya ücret/hesap/runner izni çıkarılmaz.

Uygulanan belge düzeni: tek canonical set, tasarım revizyonu 03; [önce/sonra ve yatırım kapısı](../product/current-direction.md), [sürüm anlamı](../governance/versioning.md). DEC-18 gerçek seçim/uygulama problem ihtiyacını kaydeder; DEC-19 bounded prototip + native kıyas önerisidir. Q02/Q03/Q06/Q08/Q11 ve OPEN yatırım/stack/sayısal policy kararları açık kalır. Sonraki uygulama talebinde T01→T02d→T03a hazırlığı, yetkili T03b deneyinden sonra T03c owner kararı; prototip bu tur başlamadı.

## Q12 — Aynı projede konuşma dili değişirse

**2026-10-11 / cevaplandı: A kabul edildi.** Kullanıcı konuşma dilinin tespit edilip not/proje çıktılarının o dilde üretilmesini istedi; maliyetli otomasyonun P2'de olabileceğini belirtti. [İhtiyaç, teknik öneri ve faz planı](../product/language-and-localization.md) kaydedildi. İlk pilot yalnız İngilizce varsayımıyla tasarlanmayacak; somut detector/model/language desteği henüz test edilmedi.

- **A — Seçildi:** İlk insan konuşmasının dili proje dili olarak önerilir, kullanıcı düzeltebilir. Sonradan başka dil konuşulursa proje çıktı dilini değiştirme önerisi gösterilir; eski kayıtlar otomatik çevrilmez.
- **B — Korunan alternatif; varsayılan seçilmedi:** Her sohbetin dilinde yeni not üret; aynı projede farklı dilli kayıtlar bulunabilir. Ortak retrieval/cross-language kalite ayrıca gerekir.

Kullanıcının seçili A önerisine “a ile devam et” yanıtı Q12-A'yı kabul eder. Proje çıktı dili kullanıcı değiştirmedikçe sabittir; farklı sohbet dili yalnız öneri doğurur, ret/yanıt yoksa mevcut dil korunur. Değişim kabul edilince sonraki üretim yeni policy revision'ına bağlanır; eski notlar otomatik çevrilmez. Seçimin gerekçesi öneri değerlendirmesidir: ortak proje içeriği tutarlı, tercih kontrollü, gereksiz toplu çeviri maliyeti ve anlam değişimi önlenir. B alternatifi korunur; bedel sonraki sohbet diliyle çıktı dilinin farklı olabilmesidir. Detector/stack/otomasyon faz ayrıntıları hâlâ teknik öneri; uygulama/test yapılmadı. Kaynak dili, yeni üretim dili ve UI locale ayrıdır. Genel dil ihtiyacı toplu geçmiş çevirisi, yeni modele veri aktarımı/ücret veya eski karar/AC rewrite onayı değildir. Q03 ve mevcut izin/kanıt kapıları korunur.

## Q13 — Kaynak kodu/teknoloji yaklaşımı için hazır seçenekler

**2026-10-11 · Açık; seçenekler hazır, owner seçimi yok.** Kullanıcı bütün upstream kod alanlarından Decivora'da nerede/nasıl yararlanılabileceğinin somutlaştırılmasını istedi. [Kod/teknoloji değerlendirmesi](../discovery/code-reuse-assessment.md), 39 manifest alanı, yapısal kod envanteri, R01–24 adayları, paket kapanışı, hedef/kabul/uyarlama ve alım yöntemlerini sunar. Bu kayıt varsayılan stack kabulü değildir.

**Soru:** Sıradaki araştırma yolunda A, B veya C'yi tercih ediyor musun?

- **A — Önerilen:** Küçük deterministik modüller + governance contract uyum deneyi; native/extension kontrol baseline'ı korunur.
- **B:** Önce WrongStack native/extension aynı GAP/RES/WS oracle'ında yeterli mi incele; eksikse küçük reuse/core önerisine dön.
- **C:** Upstream kaynak taşımadan özgün küçük implementation; aynı algoritma/sözleşmeleri referansla karşılaştır.

Yanıtsızsa açık kalır; kod alımı/production stack seçilmiş sayılmaz. T01/T02/T03a sırası, somut scope ve Q03 gerçek veri/ücret kapısı korunur. Bu seçenekler gelecekteki araştırma önceliğidir; bütün platformu fork etme, provider hesabı veya sınırsız kodlama yetkisi çıkarılmaz. Ayrıntılı artı/eksi ve WS-R çıkışları kaynak raporunda.

## Teknik gap incelemesi — soruların adım adım sırası

[İnceleme ve soru kuyruğu](../quality/technical-gap-analysis.md) Q02→Q03→gerçek veri policy→Q11/Q06→Q08→kanıtlı Q13/pilot değerlendirmesi sırasını önerir. Cevabı verilmiş ürün tercihleri tekrar açılmaz; rutin serializer/offset/constraint seçimlerini engineering test eder. Sorular bu tur düz metin A/B/C ile gösterilir; UI widget yanıtı kaybolduğu için kalıcı kayıt da korunur.

**Q02-R1 · İlk kaynak yolu · 2026-10-11: A kabul edildi; B sonraki hedef.** Q02'nin alt netleştirmesidir; OS/host ve somut kaynak/hedef sorularını kapatmaz.

- **A — İlk pilot için seçildi:** Claude/ChatGPT sohbetinden kullanıcı tarafından açıkça aktarılan parça + seçilmiş tek uygulama hedefinde read-only gözlem. Önce “dosya verildi, gerçekten uygulandı mı?” zincirini capture entegrasyonu olmadan sınar.
- **B — Sonrasında görülmesi istendi:** Codex coding oturumu + tek repo. MCP ile hedefli bağlam/öneri alışverişi; otomatik capture için ayrıca seçili host/build'de kaynak erişimi ve coverage deneyi. İlk pilot için seçilmedi.
- **C — Korunan, seçilmemiş alternatif:** Claude Code oturumu + tek repo; otomatik capture fizibilitesini önce sınama seçeneği.

**Kaynak ve gerekçe:** Kullanıcı “ilk etapta maliyet odaklı düşünürsek A. ama sonra B yi de görmek isterim” dedi. A, başlangıçtaki adapter/kurulum bağımlılığını azaltıp asıl değer zincirini daha erken sınamak için seçildi; B bağlantılı kullanımın sonraki doğrulamasıdır. A'nın toplam token/maliyet bakımından daha ucuz olduğu henüz ölçülmedi. Açık metinden karar çıkarımı ile deterministik hedef kontrolü ayrı maliyet kalemleridir; aktarımın manuel olması model maliyetini kendiliğinden sıfırlamaz.

MCP bağlantısı tools-only olabilir; bütün oturum veya alt agent mesajlarının yakalandığı anlamına gelmez. B'nin deneyi aynı kaynaklı karar/artifact/AC kayıtlarını kullanır; yeniden geçmişi her çağrıya yüklemez. [Bağlantı planı](../architecture/connection-and-context.md#kabul-edilmiş-pilot-sırası--q02-r1) ve [Spike-1](spike-1-v1.md) aşama/kanıt ayrımını tutar.

Bu seçim pilot araştırma yönüdür; gerçek transcript/hesap/target okuma, config/runner, dış veri veya ücret izni sağlamaz. Somut grant ve Q03'ün sonraki gerçek veri/provider/bütçe kısmı ayrıca kapanır. Q03-R1 A kabul edildi: ilk deney ek ücretli model API'si olmadan sentetik/elle etiketli fixture ve deterministik kontrollerle ilerler. Serbest metin çıkarım kalitesi ve gerçek Codex bağlantısı bu hazırlıkla doğrulanmış sayılmaz.


## Q03-R1 — İlk deneyde ek ücretli model API'si

**2026-10-11 · A kabul edildi; sonraki açıklamayla kapsamı netleştirildi.** Önceki Q02-R1 ilk kaynak yolu sorusundan ayrıdır. A yalnız ilk deneyin model/maliyet sırasını seçer. Kullanıcı sonraki mesajında otomatik anlam çıkarımının uygulanıp test edilmesinin isteğe bağlı seçenek değil, gerekli ürün işi olduğunu belirtti; bu açıklama güncel yorumun otoritesidir.

- **A — Seçilen sıra:** Önce örnek/elle etiketlenmiş kayıtlar ve kod kontrolleri; bu ilk dilimde ek ücretli model API'si kullanılmaz. Ardından otomatik serbest metin anlam çıkarımının uygulaması ve gerçek extractor çıktısıyla testi zorunlu doğrulama işidir.
- **B — Yalnız zamanlama alternatifi:** Anlam çıkarımı deneyini ilk dilimde de yapmak. Bu erken başlama sırası seçilmedi; özelliğin kendisi reddedilmedi. Model/provider, aktarılacak veri ve bütçe sınırını belirlemek, ilgili deneyin her iki sırada da önkoşuludur.

**Neden / trade-off:** Maliyet önceliği ve domain zincirindeki hataları model doğruluğundan ayrı inceleyebilme. Bedeli, ilk sonucun doğal dil extraction, native karşılaştırma veya alıcı modelin bağlamı doğru kullandığını doğrulamamasıdır. Bu tercih bütün ürünün LLM kullanmayacağı, ücretli araştırmanın kalıcı olarak yasaklandığı veya mevcut host/geliştirme tokenlarının sıfır olduğu anlamına gelmez.

**Etki / kabul:** [Spike-1](spike-1-v1.md) ilk dilimi `no_model` fixture/code kontrolleriyle sınırlar; model dispatch/judge/retry ve fresh-session model deneyleri bu dilimde çalıştırılmaz. T01 oracle/corpus sıradaki hazırlıktır. Sonuç raporu code/fixture ile model `not_run` durumunu ayırır. Sonraki gerçek veri/provider/aylık bütçe, somut hedef read ve retention izinleri açık; bu cevap bunları onaylamaz. Bunlar otomatik anlam çıkarımını yapıp yapmama kararı değil, zorunlu deneyi hangi yöntem/veri/sınırla yürüteceğimizin açık ayrıntılarıdır. T01/T03f hazırlığı → T09 extractor uygulaması → T24/T24q ölçümü mevcut görevlerdir. Yalnız fixture/code sonucu otomatik ürünün doğrulama kapısını kapatamaz; izin/erişim eksikse ilgili sonuç `blocked`/`not_run` olur, passed sayılmaz. Uygulama veya deney bu kayıtla başlamış/tamamlanmış sayılmaz.

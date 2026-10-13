# Owner soruları ve teknik karar hazırlığı

## Güncel odak — Q14-A kabul edildi / 2026-10-13

Kullanıcı gri alanların sessiz varsayımlarla şekillenmemesini istedi. Teknik ayrıntı, deney sınırı ve kullanıcıya görünen davranış farklı kayıtlar olmalı. [P0 receiver guard](../quality/receiver-contract.md) genel production kararı değildir: bir mesajda çoklu preserved record şu anda unsupported, kayıt başına bir next-action mevcut deney sınırı, küçük keyword schema interpreter genel validator değildir. Bu sınırlara kullanıcı ürünü olarak onay verilmiş sayılmaz. Gerçek token/cost, IAM/adapter, nihai stack/lisans ve yatırım sonucu açık; eski geçici seçimleri accepted ADR diye ilerletme.

**Q14 — Birden fazla bağımsız projenin review çıktısında bir proje hatalıysa diğerinin geçerli taslakları nasıl gösterilsin? Durum: A kabul edildi. Kullanıcının yanıtı: “A. AMA PROJE 2 NE OLACZAK BU senaryodA?”; ek soru Proje 2 yaşam döngüsünü açıklamayı ister, A seçimini geri almaz.**

- **A — Seçildi:** Her proje ayrı değerlendirilir; kendi source/shape/yetki kontrollerinden geçen bağımsız projenin taslakları incelemeye sunulur. Hatalı/belirsiz bölüm görünür biçimde bekler; aynı projenin bağımsız işleri de ilerleyebilir. Toplam değerlendirme partial/failed kalır; geçerli taslak otomatik karar/apply değildir.
- **B — Seçilmedi:** İki proje de inceleme için bütün çıktı düzelene kadar bekler; kaynağın alındığı ve hangi projenin hatalı olduğu gösterilir.

Örnek: depolama projesinin cevabı geçerli, UI projesinde yanlış revision var. A depolama taslağını review'da gösterir, UI düzeltme bekler. B ikisini review'a açmaz. Hiçbiri yanlış cevabı düzeltip başarılı saymaz, yeni model çağrısı veya gerçek iş onayı vermez.

**Sınır:** A yalnız kimliği ve kaynak yetkisi doğrulanmış ortak envelope içindeki bağımsız proje birimleri için kabul edilmiş review ilkesidir. Envelope/request/project kimliği ya da access belirsizse kısmi kabul yok. Aynı atomik ChangeSet veya birbirine bağlı karar/görev etkileri bölünemez. Ham çıktı korunur; eski RECEIVER-001 ve scorer sonucu değişmez. Güncel P0 validator bütün output'u fail-closed kontrol eder; Q14-A'nın ayrı fixture wrapper'ı [T03x](../quality/project-review.md) ile uygulandı; whole-output guard/scorer tarihsel yol olarak korunur. Gerçek UI/IAM/durable Inbox henüz yok. Yanıt gecikirse Q14 kimliğine bağla; yeni soru veya onay sanma.

### Proje 2'nin devamı — kabul edilen ayrımın yaşam döngüsü

1. Belirsiz kaynak mesajı/cevap, proje ve erişilebilir soru bağlamı korunur. Proje iptal veya completed yapılmaz; otomatik seçenek tahmini yok.
2. Review Inbox'ta `Needs clarification` gösterilir: belirsiz cevap, olası sorular, gereken yetkili yanıt ve bu yanıta bağlı bekleyen işler. Tek odaklı soru aynı kalıcı question ID/presentation revision'a bağlıdır; bütün sohbet yeniden okutulmaz.
3. Yalnız bu karara/yanıta gerçekten bağımlı işler bekler. Proje 1 ve Proje 2 içindeki bağımsız yetkili işler ilerleyebilir; aynı atomic ChangeSet ve ortak bağımlılıklar ayrı tutulmaz.
4. Kullanıcı başka chatte/gecikerek cevap verebilir; source binding, yetki ve soru/seçenek revision kontrol edilerek aynı kayda bağlanır. Eski/değişmiş seçeneklere yanıt yeni seçenekmiş gibi uygulanmaz. Yanıt association, karar onayı, hedef uygulama ve AC ayrı kalır.
5. Cevap gelmezse bekleyen kayıt Inbox/devam paketinde kalır; sessizlik onay veya otomatik iptal sayılmaz. Bildirim kanalı/sıklığı mevcut açık policy kapsamındadır; A seçimi yeni otomatik mesaj izni değildir.
6. Sorun anlam belirsizliği değil `criterion_revision` string gibi teknik çıktı hatasıysa kullanıcıdan ürün kararı istenmez: teknik hata/onarım işi olarak gösterilir, output bozuk haliyle korunur. Yerel düzeltme yapılabilir; yeni model çağrısı ancak mevcut kapsam/bütçe/yetki içinde, sınırsız retry yok.

[Kalıcı soru/geç yanıt](../product/pending-questions-and-late-answers.md) ve [Review Inbox](../product/approval-ux.md) sözleşmelerini tamamlar. Bu kayıt çalışan UI, otomatik takip veya yeniden başlama capability kanıtı değildir. Proje bazında fixture guard uygulaması T03x scoped DONE;20 yeni test ve [kod raporu](../quality/project-review.md). Durable Inbox henüz uygulanmadı; production T13/T19/T24 kapıları açık.

Bu MVP review/error UX davranışıdır; OPEN-07 ile ilişkilidir. Yeni request'in bağımsız yerel hazırlığını durdurmaz. Uygulama, format sürümü, kaynak izolasyonu ve valid/invalid/mixed/atomic negatif testleri somut tasarımda hazırlanır. Nihai stack, lisans, gerçek veri saklama ve model/bütçe sonraki etki kapılarında ayrıca ele alınır; hepsini bugün seçtirmeye gerek yok.

**2026-10-09.** Amaç kullanıcıya bütün teknik tasarımı seçtirmek değil; yalnız ihtiyaç, erişim, veri ve maliyet tercihlerini almak. Cevap alınmaması karar veya izin sayılmaz. Bu kayıt geçici karar kuyruğudur; AGENTS.md içine taşınmaz.

## Şimdi sorulan üç konu

| ID | Soru | Durum / cevap | Etkisi |
|---|---|---|---|
| Q01 | İlk pilot kimin işiyle doğrulansın? | **Kabul edildi:** önce owner'ın bireysel kullanımı, sonra benzer kullanıcılar. Kullanıcının bu oturumdaki açık cevabı | İlk UX ve araştırma örneklemi; tam kapsam ve P4 ekip vizyonu korunur |
| Q02 | Günlük kullanılan coding/chat yüzeyleri, pilotun zorunlu ilk ikisi ve hedef OS? | Kısmen cevaplandı: Q02-R1 A ilk pilot, B sonra; Q02-R2 A tek GitHub dokümanı manuel kontrol edildi. Coding OS/host ve gerçek sohbet kaynağı açık | T02 capability deneyi sırası, kurulum/host matrisi. Tam MVP'nin iki coding adapter hedefi kendiliğinden düşmez |
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


<a id="q03-r1--ilk-deneyde-ek-ücretli-model-apisi"></a>

## Q03-R1 — İlk deneyde ek ücretli model API'si

**2026-10-11 · A kabul edildi; sonraki açıklamayla kapsamı netleştirildi.** Önceki Q02-R1 ilk kaynak yolu sorusundan ayrıdır. A yalnız ilk deneyin model/maliyet sırasını seçer. Kullanıcı sonraki mesajında otomatik anlam çıkarımının uygulanıp test edilmesinin isteğe bağlı seçenek değil, gerekli ürün işi olduğunu belirtti; bu açıklama güncel yorumun otoritesidir.

- **A — Seçilen sıra:** Önce örnek/elle etiketlenmiş kayıtlar ve kod kontrolleri; bu ilk dilimde ek ücretli model API'si kullanılmaz. Ardından otomatik serbest metin anlam çıkarımının uygulaması ve gerçek extractor çıktısıyla testi zorunlu doğrulama işidir.
- **B — Yalnız zamanlama alternatifi:** Anlam çıkarımı deneyini ilk dilimde de yapmak. Bu erken başlama sırası seçilmedi; özelliğin kendisi reddedilmedi. Model/provider, aktarılacak veri ve bütçe sınırını belirlemek, ilgili deneyin her iki sırada da önkoşuludur.

**Neden / trade-off:** Maliyet önceliği ve domain zincirindeki hataları model doğruluğundan ayrı inceleyebilme. Bedeli, ilk sonucun doğal dil extraction, native karşılaştırma veya alıcı modelin bağlamı doğru kullandığını doğrulamamasıdır. Bu tercih bütün ürünün LLM kullanmayacağı, ücretli araştırmanın kalıcı olarak yasaklandığı veya mevcut host/geliştirme tokenlarının sıfır olduğu anlamına gelmez.

**Etki / kabul:** [Spike-1](spike-1-v1.md) ilk dilimi `no_model` fixture/code kontrolleriyle sınırlar; model dispatch/judge/retry ve fresh-session model deneyleri bu dilimde çalıştırılmaz. T01 oracle/corpus sıradaki hazırlıktır. Sonuç raporu code/fixture ile model `not_run` durumunu ayırır. Sonraki gerçek veri/provider/aylık bütçe, somut hedef read ve retention izinleri açık; bu cevap bunları onaylamaz. Bunlar otomatik anlam çıkarımını yapıp yapmama kararı değil, zorunlu deneyi hangi yöntem/veri/sınırla yürüteceğimizin açık ayrıntılarıdır. T01/T03f hazırlığı → T09 extractor uygulaması → T24/T24q ölçümü mevcut görevlerdir. Yalnız fixture/code sonucu otomatik ürünün doğrulama kapısını kapatamaz; izin/erişim eksikse ilgili sonuç `blocked`/`not_run` olur, passed sayılmaz. Uygulama veya deney bu kayıtla başlamış/tamamlanmış sayılmaz.


<a id="q02-r2--ilk-gerçek-read-back-hedefi"></a>

## Q02-R2 — İlk gerçek read-back hedefi

**2026-10-11 · A kabul edildi.** Kullanıcının doğrudan “A” yanıtı bu bekleyen hedef sorusuna bağlandı; Q02-R1 kaynak yolu ve Q03-R1 no-model sıra kararıyla karıştırılmadı.

- **A — Seçilen ilk hedef/sıra:** Mevcut private Decivora GitHub reposunda seçilmiş tek doküman; exact path/ref ve içerik karşılaştırmasıyla read-only kontrol.
- **B — Korunan sonraki senaryo:** Kullanıcının belirttiği tek yerel dosya; yalnız o path/artifact için scoped read. İlk hedef olarak seçilmedi; ürün kapsamından çıkarılmadı.

**Gerekçe ve uygulama tercihi:** Mevcut dokümanı/izinli bağlantıyı kullanmak, ilk somut read-back için yeni host kurulumuna ihtiyaç bırakmaz. Bunun daha düşük toplam token maliyeti sağladığı ölçülmedi. Asistan, onaylanan sınıf içinde önceki corpus rehberini `examples/corpus/README.md` olarak seçti; kullanıcı exact path'i ayrıca belirtmedi.

**Sonuç:** [READBACK-01](../quality/first-target-readback.md) önceki artifact yayım commit'ini ve gözlem anındaki main ref'ini `6de536e44b22d6f839aa7c94e3ca2444addb5115` olarak sabitledi. Yerel içerik ile GitHub UTF-8 içeriği/SHA-256/blob kimliği birebir eşleşti: tek doküman/ref için **observed_match**. Rehber bu kontrolde değiştirilmedi. Bu, manuel mevcut GitHub connector'ıyla yapılan kontrol; Decivora adapter/harness, semantik extraction veya tüm task DoD testi değildir.

**Sınır / devam:** Tek hedef dokümanın read kapsamı somutlaştı. Bütün kaynak hesapları, ücretli model, gerçek sohbet import'u ve target execution yetkisi çıkarılmaz. Repo belge bakımının önceki commit/push yetkisi ayrı kalır. T01 insan review'u ve remaining coverage, T02 coding capability ve zorunlu T09/T24q extraction testi açık; gelecekteki model/veri/bütçe ayrıntıları ayrıca karara bağlanır. Sadece hedef/sıra seçildi; gerekli doğrulama işleri seçenek hâline getirilmedi.


## Q03-R2 — İlk gerçek model output'u mevcut hesapla

**2026-10-11 · A kabul edildi.** Kullanıcı seçili A/B önerisine “burada da önerin ile devam edelim” yanıtını verdi. A: hazır S02 sentetik isteği mevcut LLM hesabında tek yeni oturumda çalıştır; sonucu import/ölç. B: otomatik API provider + bounded bütçe alternatifi korunur, bu ilk smoke için seçilmedi. Gerçek semantik çıkarım zorunlu iş olmaya devam eder.

Gerekçe: mevcut hesabı kullanmak, ilk output smoke'una ek API bağlantısı/harcama bağımlılığı eklemez. Dahil hesap kotası tüketilebilir; abonelik veya prompt token hedefi iş başına hard parasal tavan değildir. Kullanıcı da tavan ihtiyacını sordu. İlk engineering sınırı: tek S02/11 sentetik mesaj, bir gönderim/çıktı, retry/regenerate/tools/subagent yok, 1536 çıktı token hedefi (enforce edilmediyse soft), 128 KiB import/64 aday hard validator sınırı; ek API spend/credit satın alma veya ücretli aşım izni yok.

[Hazır paket, plan ve kaynaklar](../quality/s02-account-smoke-plan.md). Hesap/arayüz ve model seçimi açık; bu nedenle model execution not_run, usage null. Q03-R1 A önceki no-model dilimin sırası olarak tarihsel kayıtta korunur. S02 ilk output, n=1 development smoke; human gold, sealed holdout, native kıyas veya production build kapısını kapatmaz. Bu sohbet oracle/taslak gördüğü için bağımsız inference diye tekrar kullanılmaz. Yeni dış hesap/thread otomatik açılmadı.

## Q03-R2 güvenlik eki — Token ve bağlam sınırları

**2026-10-11 · İhtiyaç kabul edildi; hesap capability ve sayısal policy açık.** Kullanıcı olağan dışı tüketimin para/kotayı tüketmeden durmasını veya insan onayı beklemesini istedi. Input, output, toplam context ve parent/dönem tüketimi ayrı sınırlar olacak. Risk eşiğinde sınırları belli onay; hard cap aşıldığında veya gerekli üst sınır bilinmediğinde blocked. Kaynak/geçmiş korunur, retry/child bütçeyi sıfırlamaz.

Gerekçe: tek gönderim veya kısa cevap talimatı, gizli context/reasoning ve ücretli kullanım için kesin güvence sağlamaz. Korunan alternatif mevcut hesapla manuel smoke'dur; hard sınırları desteklemiyorsa capability kapısı veya açık sınırlı risk istisnası gerekir. İlk çağrıdan sonra iptal/timeout harcamayı geri almaz. Ücretli API alternatifi kendi dispatch sınırlarını uygulama adayıdır; otomatik seçilmedi ve harcama izni yoktur.

[Token/context hesaplama sözleşmesi](../architecture/routing-token-economy.md), [durma/onay UX'i](../product/token-risk-and-approval.md), [S02 kayıt ve kapısı](../quality/s02-account-smoke-plan.md) güncellendi. Model/arayüz seçimi açık; token/cost null alanları unlimited sayılmaz. Ürün kontrolü P1 uygulama/doğrulama gereksinimi; dokümantasyon güncellemesi runtime enforcement kanıtı değildir.

## Q03-R3 — İlk model smoke için sağlayıcı

**2026-10-11 · Kabul edildi: A, mevcut ChatGPT/Codex hesabı (OpenAI).** Kaynak: kullanıcının A/B hesap sorusuna verdiği “a” yanıtı. Claude bu ilk smoke için seçilmedi. Q03-R2 tek S02/bir output/sıfır retry, sentetik-only ve ek ücret yasağı korunur. Hesap seçimi kapandı; kesin model/arayüz, enforce edilebilir limitler ve gerekirse yalnız bu deney için sınırlı risk istisnası açık.

Salt okunur hesap kontrolünde normal kullanım açık görüldü; özel hesap/kota ayrıntıları repoya taşınmadı. [Capability bulgusu ve somut istisna kapsamı](../quality/s02-account-smoke-plan.md#q03-r3--hesap-seçimi-ve-kalan-tek-owner-kararı): incelenen SIWC preview yolunda output token cap parametresi desteklenmiyor; bütün hostlar için genelleme yok. Token tavanını prompt hedefiyle eşitlememek için dispatch bekliyor. Bu yanıt ücretli API veya risk istisnası sayılmadı; gerçek inference not_run.

## Q03-R4 — Tek S02 için sınırlı token riski istisnası

**2026-10-11 · Kabul edildi: A.** Kullanıcı, önceki mesajdaki “Yalnız bu deney için istisnayı kabul et” seçeneğine “a” dedi. Scope: 11 sentetik mesaj/5498 byte sabit prompt, bir gönderim/ilk output, sıfır tekrar/araç/alt agent; ek ücretli kullanım açılmaz, kesin token/context tavanı garanti edilmez. Ürün hard-cap gereksinimi değişmedi; genel/gelecek deney izni değildir.

[Deney raporu](../quality/s02-account-smoke-result.md): kişiselleştirilmemiş geçici ChatGPT web oturumunda tek gönderim denendi; cloudflare_challenge, sıfır model output, usage unknown. İlk onay denetimi reddinden sonra önceki seçenek ve güncel insan cevabı sohbet kaydında doğrulandı; aynı UI eylemi yeniden değerlendirildi, dolaylı gönderim yapılmadı. İzin tüketildi; ikinci model gönderimi/retry yapılmadı.

## Q03-R5 — Bir yeni S02 gönderimi

**2026-10-11 · Kabul edildi ve tüketildi.** İnsan yanıtı: “tek yeni denemeyi onaylıyorum”. Aynı 5498 byte/11 sentetik mesaj, bir yeni boş kişiselleştirilmemiş ChatGPT oturumu, tek gönderim/ilk output, sıfır retry/tools/subagent ve ek ücret yasağı korunur. Q03-R4'ün yalnız bu sınırlı smoke için kabul edilmiş token/context riski dışında ürün hard-cap kuralı değişmez.

Normal Chrome'da bir gerçek output alındı. [S02-002 raporu](../quality/s02-second-attempt-result.md): JSON parse edildi, 11 exact alıntının 10'unda kaynak konumu hatalı; strict evaluator validation aşamasında reddetti, skor/zincir uygulanmadı. UI “Hızlı” model sürümü değildir; token/cost unknown. İlk cloudflare sonucu ayrı korunur; yeni çıktı eski hatanın kök nedenini kanıtlamaz. Yeni gönderim izni yok; insan bağımlılığı olmayan offline source anchoring işi sıradadır.

## Q03-R6 — RECEIVER-002 tek yeni native run önerisi

**2026-10-13 · Kabul edildi, tek native turn tamamlandı ve izin tüketildi.** [RECEIVER-002 gerçek sonuç](../quality/receiver-002-result.md): missing required next_actions ve ambiguous-question bağlaması nedeniyle invalid_contract, skorlar null; yeni retry yetkisi yok. [Ayrı onay kaydı](../../examples/receiver-next-smoke/authorization.json), Q03-R6 ve exact prompt hashine bağlıdır. Frozen hazırlık manifesti değişmez. T03y [paketi](../quality/receiver-next-plan.md) hazırlandı: ayrı yeni projectless Codex sohbetinde configured GPT-6 Luna/Low, yalnız exact8089-byte synthetic prompt; tek başlangıç turn/ilkfullfinaloutput, retry/follow-up/tools/subagents/paidAPI0. Source2project/8message, machine schema prompt içinde; oracle/parent history/repo aktarılmaz. RequestID `f60e6a29a6b475a3cfc9b97162a6caf0ebdd3bfd91e6e8045fee7b4eb1a9c42f`, promptSHA `14f68a36d7ee013eb07fbbef4c214e264a7108d00bc73529f30c9044878efb48`. Soft1536outputtoken hedefi, kesin token/context/para cap unknown; mevcut üyelik kotası tüketilebilir.

Somut soru: Bu exactpaketi ayrı yeni GPT-6 Luna/Low sohbetinde tek gönderim/0retry ile çalıştırmayı onaylıyor musun? Genel devam veya önceki run'ın geç teyidi bu yeni source-scope/modelturn izni sayılmaz. Cevap gecikirse Q03-R6/id/hash'e bağlanır; Manifest actualsend0/authorizationnot_granted frozen hazırlık snapshot'ıdır; gerçek izin ve run ayrı request/hash bağlı kayıtta tutulur. Yeni API key/bakiye/yeni ücret veya sınırsız inference yetkisi yok. İlk başarısızlık aynen raporlanacak; failure'ı düzeltmek için ikinci prompt otomatik gönderilmeyecek.

## Q15 — Koşullu MVP çekirdeğine geçiş ve runtime seçimi

**2026-10-13 · Q15-A kabul edildi.** Kullanıcı “onay bekleyen iş varsa senin. önerin ne ise o öneri ile ilerleyelım…” yanıtını verdi; [exact onay kaydı](../quality/reviews/q15-build-approval.json), [ADR-0012](../architecture/adr/0012-conditional-python-runtime.md). Kullanıcı ana To Do işlerinin neden sabit kaldığını sorup ilerleme istedi. [Somut öneri](build-transition-proposal.md): A Python3.12/stdlib SQLite yerel MVP çekirdeği build'i; T04 başlangıcını koşullu owner kararı + runtime ADR kabulüne bağla, T01/T02/T03 ölçüm ve tüm MVP release kapıları açık kalsın. B mevcut T03 kapanışını bekleme düzenini koru. Genel önceki “devam” yeni stack/dependency kabulü diye kaydedilmedi.

Mevcut durum→tespit→değişiklik→fayda/risk→etkilenen hedefler→doğrulama öneride hazır. Python bundled3.12.14/SQLite3.53.1 version gözlemi ve248 semantik test bu runtime'da passed; T04 clean-start/test/scaffold henüz yok. Model/API/gerçek data/connector/deploy izni istenmiyor. Bu yeni explicit cevapla T03c koşullu yatırım kararı kayıtlandı ve T04 başladı; T01/T02/T03 evidence ve release kapıları kapanmış sayılmaz. Yeni model/API izni yok.

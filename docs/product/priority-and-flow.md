# Ürün değeri, engeller ve iş akışı

**2026-10-09 — kabul edilen ürün ilkesi, önerilen uygulama sözleşmesi.** Q09/DEC-17: engeller ve diğer işleri geciktiren bağımlılıklar öncelikli; proje Product Owner bakışıyla, çevik öğrenme ve değer teslimiyle ilerler. Çalışan scheduler veya bildirim servisi yok. Bu belge GRF-01, APR-02, UX-02 ve ROU-01 kapsamını detaylandırır; Scrum sertifikası veya yeni bir proje yönetimi ürünü iddiası değildir.

## Hangi iş önce?

**Yöntemden bağımsız anlamlar:** Bağımlılık bir işin başka bir koşula bağlı olmasıdır; bu koşul gelecekte gerektiğinde normal şekilde sağlanıyorsa bugün blocker olmak zorunda değildir. Blocker, ilgili adımın ilerlemesini fiilen engelleyen durumdur; bir görev, erişim, karar veya dış teslim olabilir. Risk olası gelecekteki sorunla, gerçekleşmiş engel mevcut durumla ilgilidir. Bu ayrımlar Scrum'a veya PMI'a özel değildir; [yöntem ve kaynak açıklaması](../delivery/project-management.md) Scrum kullanım örneği ile genel ürün yeteneğini ayırır. Bir node'un çok işi etkilemesi tek başına kritik yol hesabı değildir; bu belgede süre/takvim temelli kritik yol motoru tasarlanmış sayılmaz.

Bir task'ın önemli olması, hemen çalışılabilir olması ve bildirim gerektirmesi ayrı alanlardır. Engellenmiş işi sürekli çalıştırmayı denemek yerine engeli kaldıran **uygulanabilir adım** belirlenir. Bu adım kod, test, erişim, dış teslim veya insan kararı olabilir. İzin bekleyen işin önceliği artabilir; öncelik izin sağlamaz.

| Durum | Önerilen davranış |
|---|---|
| Mevcut hedefi veya aktif işleri durduran doğrulanmış engel | Engeli çözme adımını ve karar/sorumlu ihtiyacını önce göster |
| Başkalarının başlamasını veya bitirmesini geciktiren açık bağımlılık | Doğrudan ve dolaylı etki yollarını açıkla; açılacak değer ve gecikme riskine göre öncelik öner |
| Engel dış ekip/izin nedeniyle şu anda çözülemiyor | Bekleyen karar/teslimi takipte tut; yetkili, hazır ve hedefe katkılı bağımsız işi öner |
| İlişki yalnız varsayım, eski veya eksik | Unknown/review göster; kanıtsız blocker veya kesin ready üretme |
| Çok sayıda düşük değerli işi açıyor, az sayıda kritik işi açan başka aday var | Yalnız bağlantı sayısıyla sıralama yapma; hedef/değer/risk trade-off'unu Product Owner'a göster |

Önerilen değerlendirme sırası: mevcut hedef ve kabul edilmiş ürün sırası → gerçek engel ve etkisi → zaman hassasiyeti/risk → açılacak değer → çözümün yapılabilirliği/eforu → bekleme yaşı. Kritik veri kaybı gibi acil risk mevcut kalite kapılarından gelir; sırf çok bağlantısı olan iş bunları bastırmaz. Ağırlıklı tek puan veya tahmini parasal gecikme maliyeti ölçülmeden uydurulmaz. Eşit adaylarda mevcut onaylı sıra korunur; kısa iş olması tek başına öne geçirme nedeni değildir.

Sürekli yeni blocker gelen projede uzun süredir bekleyen değerli işler review'a çıkar; starvation görünürdür. Scope'u terk edilmiş veya iptal edilmiş işler aktif etki sayısını şişiremez. Bir blocker'ı gidermek için gereksiz bağımlılığı azaltma, daha küçük bağımsız teslim veya alternatif yol da önerilebilir; kabul edilmiş scope/karar değişimi ayrı onaylıdır.

## Bağımlılık hesabı ve kayıtlar

`depends_on` gerçek ilerleme koşuludur; `required_by` varoluş gerekçesi, `part_of` hiyerarşidir. Son ikisi tek başına blocker üretmez. Bu repo backlog'undaki planlama sırası da doğrulanmış teknik bağımlılık gibi otomatik graph'a alınmaz. Başlama ve bitirme koşulları ayrı belirtilir; B'nin tamamlanması A'yı bekliyor diye B'nin bütün hazırlığı yapılamaz sayılmaz.

Önerilen `BlockerAssessment`: project/task, blocker kaynağı ve revision, başlangıç/bitiş kapısı, etkilenen hedef, blocked_since, kanıt, çözüm adımı, sorumlu/karar mercii veya unassigned, açık/çözüldü/unknown, son değerlendirme. `PriorityRecommendation`: graph/goal/policy/authz revisions, aday iş, reason paths, doğrudan/dolaylı etkiler, belirsizlik, değer/efor varsayımları, mevcut→önerilen sıra ve insan override gerekçesi. Bunlar yeni servis gerektirmez; mevcut graph, approval ve context modüllerinin sözleşmesidir.

Deterministik traversal güncel onaylı execution ilişkilerinde çalışır. Aynı downstream task birden fazla yoldan yalnız bir kez sayılır. “Etkileniyor” ile “bu çözülünce hazır olacak” ayrıdır: başka ön koşul, onay, kanıt veya izin eksikse iş hâlâ ready değildir. Döngü review'a gider; kısmi traversal/ACL/unknown ilişkide kapsam sınırlaması taşınır. Yetkisiz başlık, kişi, sayım veya gizli öncelik bilgisi sızdırılmaz. Gösterilen öneri yalnız yetkili görünüm için hesaplanır; eksik kapsamı projenin tamamı gibi sunmaz.

Öneri üretmek kabul edilmiş backlog sırasını değiştirmez. İnsan sıra değişimini onaylarsa gerekçe ve revision yeni event olur; stale önizleme yeniden değerlendirilir. Onaylı hedef/scope/policy içinde teknik sonraki adımı seçmek uygulayıcının olağan yetkisidir; her küçük plan değişimi yeni ürün onayı gerektirmez. Sprint Goal'u veya scope'u etkileyen değişim görünür müzakere ister. ENG-05 ilişki etkisini, ENG-06 review'u, ENG-09 yürütücü uygunluğunu, ENG-10 açıklamalı next-action görünümünü sağlar.

## UI ve bildirim

Inbox'ın üstünde `İlerlemeyi engelleyenler`, iş kartında `Engelleniyor` / `Başka işleri engelliyor` ayrı rozetleri bulunur. Seçili işte neden zinciri, bekleme başlangıcı, çözüm adımı ve hangi çıktıların açılacağı görünür; sayı yoksa uydurulmaz. Board ve graph aynı snapshot'ı kullanır. Renk yanında metin/ikon ve liste alternatifi vardır.

Sentetik örnek: **API sözleşmesini netleştir → import ve doğrulama entegrasyonları ilerleyebilir.** UI önce sözleşme kararını gösterir. Import ayrıca erişim bekliyorsa “iki iş hemen açılır” demez; “iki iş etkilenir, biri bu engel kalkınca hazır olabilir” der.

Q09 ile blocker'ların dikkat sırası kabul edildi. Anlık push/e-posta kanalı, sessiz saatler ve diğer olayların bildirim sıklığı henüz seçilmedi. İlk tasarım uygulama içi öncelikli inbox'tır; dış mesaj/otomasyon açılmaz. Aynı blocker için tek kayıt ve aynı revision'da tekrar uyarı yok; maddi etki değişiminde aynı kayda güncelleme önerilir. Onay bekleyen işi tekrar tekrar soruyla bölmek yerine çözüm seçeneği hazır tutulur. Bildirimi kapatmak blocker kaydını veya etkisini silmez.

## Planlı kabul senaryoları

| ID | Beklenen gözlenebilir davranış |
|---|---|
| FLOW-01 | A→B→C zincirinde erişilebilir ve çözülmemiş A için çözüm adımı öne çıkar; C'yi boşuna çalıştırma önerilmez |
| FLOW-02 | Elmas graph'ta ortak downstream bir kez sayılır; başka gate'i olan iş hemen ready gösterilmez |
| FLOW-03 | Yalnız part_of/required_by/plan sırası blocker üretmez; başlangıç ve bitirme gate'leri ayrıdır |
| FLOW-04 | Cancelled/obsolete, unknown, cycle, eksik ACL ve kesilmiş traversal yanlış tamlık/sayım/ready üretmez |
| FLOW-05 | Graph/goal/izin değişmişken eski sıra onayı uygulanmaz; insan override gerekçesi ve geçmiş sıra korunur |
| FLOW-06 | Dış engel beklerken bağımsız hazır iş önerilir; öncelik grant veya bütçe genişletmez; tekrar bildirim çoğalmaz |
| FLOW-07 | Çok düşük değerli ilişki az kritik ilişkiyi yalnız sayıyla bastırmaz; bekleyen işler ve Sprint Goal etkisi review'da görünür |
| FLOW-08 | Aynı snapshot'ta graph/inbox/board gerekçesi tutarlı; graph gezme ve sıralama yeni LLM çağrısı gerektirmez |

T11c/T20e uygulama, T24d sentetik oracle ve pilot ölçümü için planlandı; hiçbiri çalıştırılmadı. Yanlış ready güvenlik kapısı ve kullanıcı yönetim yükü birlikte değerlendirilir. Scrum dayanağı ve proje çalışma ritmi [kısa yönetim planında](../delivery/project-management.md); bu belgedeki algoritma ve UI tercihleri Decivora tasarımıdır, Scrum'ın zorunlu formülü değildir.

## 40+ bekleyen task için açıklanabilir ranking

**2026-10-10 — kullanıcı talebinin dokümantasyon kaydı.** DEC-17'nin 2026-10-09 tarihli kabulü korunur. Kullanıcı biriken fakat ilerlemeyen işler için sistem önerisi ve insan/izinli üst agent kontrolünde board istedi. “40+” kullanım senaryosudur; ölçülmüş müşteri verisi veya mevcut repo task sayısı değildir. Bu bölüm önerilen uygulama sözleşmesidir; feature geliştirme, scoring formülü kabulü veya otonom plan değişimi yetkisi vermez.

### Birbirinden ayrı üç sıra

- **Canonical priority:** Product Owner'ın kabul ettiği ürün önceliği/sırası; hedef, scope ve business/product value kararlarının kaydıdır.
- **Recommended rank:** belirli graph, goal, context, policy ve authz snapshot'ından hesaplanan geçici öneri. Yeniden hesaplama canonical priority'yi değiştirmez; puan, işin ready olduğunu veya çalıştırma iznini göstermez.
- **Execution order:** onaylı hedef/scope içinde uygulanabilir teknik adımların sırası. Admin/owner yalnız etkin proje yetkisiyle düzenler; “üst agent” unvanı yeterli değildir. Üst agent ancak önceden verilmiş, proje/task/action/süre bakımından geçerli grant'in izin verdiği plan düzenlemesini yapabilir. Ürün sırası, değer, scope, AC ve karar hakları insan Product Owner'da kalır.

Board öneri ve canonical priority'yi yan yana gösterir; execution order değişiminin ürün kararına etkisi ayrıca önizlenir. Öneriyi görmek/seçmek veya kartı sürüklemek sessiz kayıt değildir: değişiklik özeti, neden ve yetki kontrolüyle ayrı apply command gerekir. Yetki içi teknik düzenleme için her seferinde yeni insan onayı istenmez; korunan ürün kararı değişiyorsa güvenilir insan onayına gider. Read-only kullanıcı sıralamayı inceleyebilir, kaydedemez. Kurulum admin'i olmak proje verisine veya Product Owner kararına sınırsız yetki vermez.

### Faktörler ve açıklama sözleşmesi

| Faktör | Girdi ve açıklanacak etki | Eksik veri / sınır |
|---|---|---|
| Blocker/dependency ağırlığı | Doğrulanmış aktif başlangıç/bitiş gate'i, benzersiz doğrudan/dolaylı downstream, mevcut hedefin durması | Yalnız ilişki sayısı değer değildir; başka gate varsa ready olmaz |
| Business/product value | İnsan PO'nun kaynaklı hedef/değer değerlendirmesi ve açılacak kullanıcı sonucu | LLM değer kararı vermez; boş alan sıfır değer sayılmaz |
| Critical path | Süre, takvim, ilişki ve kapasite varsayımları yeterliyse hedef teslim yoluna etkisi | Çok bağlantı kritik yol değildir; veri yoksa yalnız bağımlılık yolu gösterilir, gün cinsinden gecikme uydurulmaz |
| Stale task / aging | Oluşturulma yaşı, blocked_since ve son anlamlı ilerleme ayrı; review ihtiyacı | Yorum/heartbeat yaş sayacını sıfırlamaz; eski iş otomatik iptal/obsolete olmaz |
| Effort | Çözüm adımının tahmini efor aralığı ve tahmin kaynağı | Küçük iş otomatik kazanmaz; bilinmeyen efor sıfır değildir |
| Uncertainty | Bilinmeyen ilişki, düşük coverage, tahmin güveni ve gerekli araştırma | Belirsizliği gizleyen kesin tek puan yerine review/spike önerisi |
| Context readiness | Güncel AC/karar/input/evidence, pending impact ve gerekli erişimin varlığı | Eksik/stale context'te önce bağlamı tamamlama adımı; skor bu gate'i aşamaz |
| Risk | Gecikmenin ürün/teslim riski ve işi yapmanın güvenlik/değişiklik riski ayrı | Yüksek uygulama riski otomatik çalıştırma nedeni değil; mitigation/insan kararı gerekebilir |

MVP'de yukarıdaki mevcut değerlendirme sırası deterministik ve açıklamalı kullanılır; faktörler kanıt/unknown olarak gösterilir, ağırlıklı toplam icat edilmez. Önce yetki ve hazır olma kapıları değerlendirilir; engellenmiş önemli task ile onun uygulanabilir çözüm adımı ayrı tutulur. Eşitlikte canonical sıra, sonra sabit task ID kullanılır. Aging yalnız kaynak zamanı ve kayıtlı değerlendirme zamanı üzerinden hesaplanır; eşik/policy sürümlüdür ve henüz seçilmemiştir.

Faz 2 scoring adayı her faktörün ham girdisini, kaynağını, normalization/weight sürümünü, katkısını, eksiklerini ve hassasiyetini açıklar. İlişki sayısı/değer/critical path aynı faydayı tekrar puanlamamalıdır. Ağırlıklar, eşikler ve score ölçeği feasibility/pilot sonrası insan PO review'una gider; sabit formül veya doğruluk iddiası yoktur. LLM yalnız izinli context'te anlamsal açıklama/aday çıkarımı yapabilir; deterministik graph hesabının ve insan kararının yerine geçmez.

Her öneri en az şunları taşır: aday task ve **next actionable**, neden şimdi, mevcut→önerilen sıra, canonical priority, ilerlememe nedenleri, çözüm sahibi/karar mercii, reason paths ve kaynak revision'ları, etkilenen işler, açılabilecek işler, belirsizlik/coverage, değerlendirme zamanı ve geçerlilik. İlerlememe nedeni dependency, insan kararı, erişim, dış teslim, context eksikliği, kapasite/WIP, failed verification, pending impact veya unknown olabilir; birden çok neden birlikte görünür. Hiç uygun iş yoksa zorla task seçilmez; “uygulanabilir iş yok” ve gereken karar/izin gösterilir.

**Sentetik impact explanation:** “API sözleşmesini şimdi netleştirmezsek B import entegrasyonu ve B üzerinden C doğrulama işi beklemeye devam eder: A→B→C. B ayrıca erişim bekliyor; A çözülünce B ve C hemen ready olmayacak. Teslim tarihi/süre verisi yok; kaç gün gecikeceği bilinmiyor. Şimdiki adım: sözleşme seçeneklerini PO review'una hazırlamak; bu karar beklerken yetkili ve hazır D fixture işine geçilebilir.” Gizli başlık/sayım/yol açıklamada veya LLM context'inde sızmaz.

### Board, seçenekler ve fazlama

Board'da canonical sıra / önerilen sıra / execution order, ready-blocked-review durumu, aging, neden, owner ve next actionable birlikte bulunur. Filtreleme ve klavye ile sıra düzenleme alternatifi 40+ kartta kullanılabilir olmalıdır. Öneriyi kabul/ertele/reddet ve manuel override gerekçeleri geçmişte korunur; refresh kullanıcının kaydedilmiş sırasını ezmez. Board/graph/inbox aynı snapshot'ı gösterir.

| Seçenek | Fayda / bedel | Önerilen yer |
|---|---|---|
| Yalnız manuel board | Basit ve kontrollü; birikimde dependency etkisini insan keşfeder | Fallback; otomatik öneri ihtiyacını tek başına karşılamaz |
| Deterministik blocker/dependency önerisi + yetkili board | İzlenebilir neden, düşük model maliyeti; semantik değer/efor tahmini sınırlı | MVP: T11c çekirdek, T20e board, T24d kabul |
| Context-aware çok faktörlü scoring, what-if simülasyon ve gelişmiş UX | Değer/risk/efor trade-off'unu karşılaştırır; veri kalitesi, kalibrasyon ve yanlış kesinlik maliyeti | Faz 2 / P2 adayı: T26b; feasibility kapılı |

Bu faz ayrımı ön taslaktır. Fazı belirleyen kanıt; veri bulunabilirliği/kalitesi, deterministik oracle doğruluğu, 40+ görevde gecikme ve anlaşılabilirlik, context/izin desteği, model maliyeti ve uygulama eforudur. Sırf “AI özelliği” olduğu için Faz 2'ye atılmaz. MVP'ye sığmayan parça gerekçe ve fallback ile raporlanır; güvenlik kapıları ertelenmez. Faz değişikliği feasibility kanıtıyla önerilir, scope değişimini PO kabul eder. What-if sonucu varsayımsaldır; plan/priority/dependency'yi değiştirmez. Kesin süreli kritik yol veya Gantt motoru taahhüdü yoktur.

### Ek kabul kriterleri ve test senaryoları

Aşağıdaki senaryolar **planlı / not_run**; FLOW-01–08'in yerine geçmez.

| ID | Senaryo → gözlenebilir kabul kriteri | Kapı |
|---|---|---|
| FLOW-09 | 40+ sentetik task, aynı snapshot ve assessment zamanı → deterministik öneri ve eşitlik sırası aynı; rank refresh canonical priority/execution order değiştirmez | MVP |
| FLOW-10 | Yüksek rank fakat erişim/context/karar eksik → nedenler ve çözüm sahibi görünür; yetkili next actionable veya hazır bağımsız iş; hiçbiri yoksa açık none | MVP |
| FLOW-11 | A→B→C ve ek gate → “yapılmazsa etki” gerçek yol/kaynakla açıklanır; etkilenen/hazır olacak ayrılır; süre yoksa tarih uydurulmaz | MVP |
| FLOW-12 | Owner/admin, read-only, geçerli/revoked/expired/scope dışı üst agent → yalnız yetkili teknik sıra apply edilir; PO value/scope/kararı agent'a devredilmez | MVP |
| FLOW-13 | Board reorder sırasında graph/goal/context/authz/plan revision değişir veya iki kişi yazar → stale/conflict; overwrite yok, yeni preview; retry tek event | MVP |
| FLOW-14 | Aging eşiği aşımı, heartbeat ve stale kanıt → son anlamlı ilerleme korunur; review önerisi oluşur; otomatik iptal/completion/priority değişimi yok | MVP |
| FLOW-15 | 40+ kartta filtre, klavye reorder, öneri ertele/reddet/override ve refresh → neden/üç sıra açık, kayıt korunur; FLOW-08 snapshot tutarlılığı ve ACL negatifleri geçer | MVP gerçek UI pilotu |
| FLOW-16 | Eksik value/effort, değişen weight ve belirsiz context → katkı/unknown/sensitivity görünür; yeniden üretilebilir score; manuel/deterministik baseline ile PO review kıyası | P2 feasibility |
| FLOW-17 | Süre/takvim yeterli ve yetersiz iki what-if fixture → ilkinde varsayımlar/yol/etki aralığı görünür, ikincide yalnız nitel etki; canonical state ve dış execution değişmez | P2 feasibility |

### Rollout ve geri dönüş

1. T01'e sentetik 40+ görev, zincir/elmas, bağımsız işler, cycle, eksik ACL/context ve aging oracle'ı ekleme planı; T11c graph kuralları önce. Gerçek kullanıcı verisi kendiliğinden alınmaz.
2. T20e/T24d'de öneriler önce shadow/read-only karşılaştırılır; ardından yetkili board apply akışı pilotlanır. Zorunlu sette yanlış ready ve yetkisiz mutation sıfır; açıklama anlaşılabilirliği, next-action seçme süresi, override nedenleri, starvation ve öneri değişim sıklığı ölçülür. Hız hedefleri baseline sonrasında belirlenir.
3. T26b feasibility raporu veri/kalite/maliyet/UX kanıtı ve go/no-go sunar. Önce açıklamalı çok faktörlü öneri, sonra varsayımsal simülasyon değerlendirilir; dış runner veya connector açılmaz.
4. Hatalı rank, ACL sızıntısı, yetkisiz plan değişimi veya açıklanamayan dalgalanmada öneri özelliği kapatılır; canonical sıra ve manuel board korunur. Önceden uygulanmış sıra geri dönüşü yeni yetkili revision/event'tir; tarihçe silinmez. Replay LLM, bildirim veya agent dispatch tetiklemez.

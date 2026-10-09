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

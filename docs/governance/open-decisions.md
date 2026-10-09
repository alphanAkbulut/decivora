# Açık kararlar ve varsayımlar

| ID | Soru | Önerilen yön | Ne zaman / kanıt |
|---|---|---|---|
| OPEN-01 | Build mi extend mi? | Özgün domain/impact; lisanslı adapter reuse | P0 karşılaştırmalı deney sonrası |
| OPEN-02 | Kesin runtime/DB/UI paketleri? | TypeScript, yerel servis, SQLite, React aday | P1a başlamadan version/license spike |
| OPEN-03 | İlk coding adapter sırası? | İki yüzeyi test et; daha erişilebilir olanla P1a | P0 gerçek capability sonuçları |
| OPEN-04 | Chat otomasyon seviyesi? | P1b provenance koruyan açık aktarım | Hesap/host izin testi; P2 otomasyon |
| OPEN-05 | Lisans? | AGPLv3 ilk aday; Apache-2.0 alternatif | Public release öncesi owner |
| OPEN-06 | Nihai marka? | Decivora geçici | Marka/alan adı/paket taraması ve owner |
| OPEN-07 | Hangi değişiklikler auto-apply? | Capture/metadata/izinli verification; scope insan | Policy UX pilotu |
| OPEN-08 | Retention/erase/şifreleme? | Minimize payload, ayrı yönetici akışı | Gerçek veri pilotundan önce |
| OPEN-09 | Ölçüm eşikleri? | Ölçüm belgesindeki pilot hedefleri | Golden corpus baseline sonrası |
| OPEN-10 | Ücretli model ve bütçe? | Provider bağımsız usage, explicit limit | API-backed deneme öncesi |
| OPEN-11 | Public/core/commercial sınırı? | Yerel çekirdek açık aday, servisler ayrı aday | Talep ve lisans incelemesi sonrası |
| OPEN-12 | Queue/lease/timeout/traversal ve recovery limitleri? | Sınırlı versioned config; ayrı cursors; snapshot backup; RPO/RTO ölçülsün | T04/T06 fixture ve T23 gerçek veri öncesi; ADR-0007 |
| OPEN-13 | Approval graph snapshot ve verifier yetkisi? | P1 project knowledge revision; insan/agent/runner capability ayrı | T08/T12/T14; ADR-0008; T24 false-stale ölçümü |

## Cevaplanan ihtiyaç ve bekleyen sorular

2026-10-09 owner yanıtı: ilk pilot kendi bireysel kullanımıyla, ardından benzer kullanıcılarla yapılacak. Bu artık varsayım değil, pilot kapsamı kararıdır; tam ürünün ekip vizyonunu kaldırmaz. Günlük coding/chat yüzeyleri ve ilk hedef OS ile harici model/veri/bütçe sınırı soruldu, yanıt bekleniyor. [Karar hazırlığı ve soru kaydı](../delivery/decision-brief.md).

Varsayımlar: local-first kabul edilebilir; ilk dil Türkçe dokümantasyon ve İngilizce teknik ID'ler; otomatik capture için bir defalık izin/binding kurulabilir. Bunlar kanıt veya alınmış ticari karar değildir. Teknik ayrıntılar önce deneyle hazırlanır; bütün açık maddeler için hemen kullanıcıya soyut seçim sorulmaz.

Bu açık sorular dokümantasyonun GitHub'a kaydedilmesini engellemez. Etkili oldukları uygulama görevinden önce karara bağlanırlar; AGENTS.md içine güncel iş listesi olarak gömülmezler.

## Ekip ve veri altyapısı karar kapıları

2026-10-10: OPEN-12/16, [rate/burst, concurrency, kapasite ve DB transaction limitlerini](../architecture/resource-limits-and-abuse.md) de kapsar. T04/T06 ilk dış girdi öncesi sonlu değerleri sentetik ölçümle hazırlar; gerçek pilot için limit-aşımı kanıtı gerekir. İlk model dispatch'i ayrıca bütçe guard ister. Kesin eşikler ve P4 dağıtık sayaç backend'i açık; kullanıcıya ölçümsüz dakika/istek sayısı seçtirilmez. Bu belge Q03 harcama/egress iznini vermez.

2026-10-10: OPEN-12 için [olay/profil ve sayısal zamanlama deney adayları](../architecture/execution-and-integrations.md#3-aralıklar-ve-takvim) hazırlandı. Kesin debounce/max-wait, polling, lease/deadline ve bakım değerleri fake-clock/yük/gerçek capability ölçümüyle seçilecek; bunlar yeni kullanıcı onayı veya aktif takvim değildir. OPEN-02/T03 ardından fiziksel [ER/FK/transaction şeması](../architecture/data-relationships.md) migration'a dönüşür. Dış provider destekleri bilinmeden kesin endpoint/timeout uydurulmaz.

| ID | Karar | Önerilen yön | Ne zaman / kanıt |
|---|---|---|---|
| OPEN-14 | Ekip deployment, identity ve veri sahipliği? | Kişisel workspace ile başla; ekipte merkezi servis ve ayrı human/agent kimliği; private kaynak otomatik paylaşılmaz | T30/C01; gerçek ekip profili ve işletim sorumlusu |
| OPEN-15 | Korunan işlemler için kaç bağımsız reviewer? | Tek owner pilot; ekipte korumalı karar/scope için bağımsız insan review | C04 öncesi policy/UX deneyi; grant/role preset onayı |
| OPEN-16 | Kapasite/SLO, audit kapsamı ve işletim bütçesi? | Sentetik 100k/1m event ve concurrent client profili; RPO/RTO ölçülsün | T23d ve C06; ortamlı rapor ve maliyet |

OPEN-08 için [retention tablosunda](../architecture/storage-memory-capacity.md) somut süre önerileri, OPEN-02 için DB/blob/secret sınırları hazırlandı; bu hazırlık owner onayı veya çalışan silme politikası değildir. [Uygulama planı](../delivery/team-data-plan.md) bağımlılıkları korur. Mevcut yanıt bekleyen sorular tekrar sorulmadı.

## UI görünümü ve analiz sıklığı

2026-10-10 yönetim ayrıntıları [admin/operasyon belgesinde](../product/administration-and-operations.md): OPEN-14 kurulum işletim sorumlusu ve rol preset'lerini; OPEN-16 alert kanalı, hizmet eşiği ve operasyon bütçesini kapsar. OPEN-05/11 kaynak lisansı/ticari modeldir; kurulum ve veri erişiminden ayrıdır. Yerel owner görünümü önerildi, çok-kullanıcı backoffice P4'te. Sayısal kullanıcı level'ı veya L1 destek ekibi seçilmiş sayılmaz; bugün bu ayrım dokümantasyonu bloke etmez.

**Q09/DEC-17 güncellemesi:** Blocker ve downstream gecikmesi önceliği, Product Owner bakışı ve çevik çalışma yönü kabul edildi. Önceki Q09 açık kaydı artık yalnız bildirim kanalı/sıklığı ayrıntılarını kapsar. Yanıt Sprint süresi/rol ataması veya dış mesaj izni değildir. [Öncelik sözleşmesi](../product/priority-and-flow.md) ve [yönetim planı](../delivery/project-management.md) hazır; uygulama yok. Q08 ayrı açık kalır.

Q07/1C kabul edildi: izinli ve erişilebilir geçmiş, aktif işler önce olacak şekilde aşamalı işlenecek. Bu karar OPEN-08'i kapatmaz: 1C kaynak arşivine önceki genel 30 günlük geçici payload önerisi otomatik uygulanmaz; kesin arşiv süresi, kapasite ve silme politikası gerçek veri öncesi kararlaştırılacak. Kaynak korunumu ile modelin eksiksiz hatırlaması farklı hedeflerdir. Q08 isteğe bağlı alt göreve bölme/varsayılan boyut önerisi ve Q09 bildirim kanalı/sıklığı ayrıntıları [soru kaydında](../delivery/decision-brief.md) açıktır. Q03 dış model/bütçe yanıtı yerine yeni izin çıkarılamaz.

Q04 güncel işler/seçili iş bağlamı; Q05 proje/görev bazlı değiştirilebilir analiz profili olarak cevaplandı. Q06 context dosyasının otomatik milestone export tercihi [karar kaydında](../delivery/decision-brief.md) bekliyor. Bu sorular OPEN-07/09/10 ile ilişkilidir; yeni ücret/egress yetkisi vermez. İptal ve ended edge geçmişinin korunması mevcut append-only ilkesinin sonucudur; grafikte çarpı/renk tercihi bu domain kuralını değiştirmez.

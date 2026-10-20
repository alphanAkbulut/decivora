# Teslim akışı retrospektifi: ilerleme neden kapanışa dönüşmedi?

**20 Ekim 2026 · İnceleme tabanı: `876e363973b96e13f65821c28340dc2907d98784`.** Kullanıcının sorusu: “Tasklar bir anda mı kapanacak; yanlış ilerlediysek bunu düzeltmeli miyiz?” Bu rapor geliştirme ve takip yöntemini değerlendirir; yeni ürün özelliği, scope azaltma veya ücretli işlem izni değildir.

## Sonuç ve sorumluluk

**Yalnız sayacı açıklamak yeterli değil; teslim biçimini de düzeltmeliyiz.** Kapanış sayısının sabit kalmasında hem geniş ana paketler ve takip hataları hem de tamamlanmamış gerçek entegrasyonlar etkili. Bunları sadece “epic sayıyoruz” diyerek açıklamak eksik olur. Uygulayıcının planlama, önceliklendirme ve raporlama yaklaşımı kullanıcıya sık görünen, çalışan ve kapanabilir sonuçlar sunamamıştır.

Bütün işler bir final gününde topluca kapanmak üzere bekletilmeyecek. Mevcut küçük teslim, kendi kabulü geçince kapanır; ana paket de kendi çekirdek kabulü ve kendisine atanmış zorunlu açık işleri bittiği anda kapanır. Bir ortak entegrasyon aynı anda birkaç kabulü gerçekten sağlarsa birkaç kayıt aynı teslimde kapanabilir. Her biri için ayrı kriter/kanıt kontrolü yapılır; tek testin geçmesi bütün parent'ları kapatmaz. MVP release onayı T24'te ayrıca kalır.

## Kanıtlanan gözlemler

| Gözlem | Kaynak | Ne gösterir / neyi göstermez? |
|---|---|---|
| 30 ana kayıt: 8 Done, 20 In Progress, 2 To Do; alt kayıtlar 56 Done/42 In Progress/26 To Do/5 Proposed | [Backlog](../delivery/backlog.md), [manifest](../delivery/task-closure.json), [satır incelemesi](task-status-audit.json) | Küçük teslimler gerçekleşmiş; ana paketlerin kapanışı geride. Efor/tamamlanma yüzdesi değildir |
| “Bir küçük PR” olarak boyutlanmış bazı ana satırlar, geniş sistem işleri ve çok sayıda alt kabul taşıyor | [Backlog](../delivery/backlog.md), özellikle T03/T18/T20/T24 | Paket boyutu ile raporlama birimi uyuşmuyor; hepsi eşit büyüklükte task değildir |
| İki-chat gerçek UI/model yolu dar kapsamda çalıştı; düzenli native okuma 3 tick geçti, fakat okumalar arasında yeni mesaj gelmedi | [UI yolculuğu](native-ui-journey-001.md), [düzenli yakalama](scheduled-native-001.md) | Bazı entegrasyonlar var; yeni mesaj→izinli analiz→review günlük zinciri henüz tam kabul edilmiş değil |
| J04 soru kaçırma ve desteklenmeyen soru çıktısı nedeniyle yarım kaldı | [J04](dialogue-batch-001-j04.md) | Gerçek model kalitesi açık; bunu yalnız takip hatasını düzelterek kapatamayız |
| Ana backlog üst özeti ve bazı sonraki-adım metinleri eskiydi; T30 genel bölümden yanlış kabul metni alıyordu | [22 iş incelemesi](task-status-audit.md#20-ekim--neden-hâlâ-22-açık-ana-iş-var), parser ve regresyon testi | Somut veri/gösterim hataları. Bunların düzelmesi ürün özelliklerinin tamamlandığını göstermez |
| Kullanıcı daha önce Codex günlük akışını önceliklendirdi; Claude doğrulamasına erken yönelme düzeltilmişti | [Sprint planı](../delivery/sprint-plan.md), [Codex uçtan uca kaydı](codex-e2e-001.md) | Öncelik dağılmasını önlemek gerekir; ikinci adapter gereksinimini silmek gerekmez |

Çalışma süresi ve efor ölçümleri yeterli olmadığı için “şu kadar gün/token boşa harcandı” veya her gecikmenin tek nedeni hakkında sayı üretilmedi.

## Neden zinciri ve güven düzeyi

1. **Kesin: takip birimi karıştı.** Ana paket, küçük kod/deney teslimi ve ürün kabul kapısı aynı “task” ifadesiyle sunuldu. Bu yüzden biten alt teslimler artarken ana To Do/Done sayımı aynı kaldı. Faz 2–4 kayıtları ve kısmi ana paketler de In Progress toplamına girdi. Bu sayı aktif WIP olarak kullanılmamalı.
2. **Kesin: güncel durumun tek görünümü yeterince korunmadı.** Eski özetler ve parser sınır hatası, son kanıtın bütün görünümlere doğru taşınmadığını gösteriyor. Düzeltilmiş metin ile tarihsel raporun ayrımı kullanıcı için yeterince açık değildi.
3. **Kanıtlarla desteklenen süreç yorumu: modül ve deney teslimleri, tek kullanıcı yolculuğunun tamamlanmasından daha görünür hale geldi.** Kod ve yerel kontroller yararlıydı; fakat ana otomatik akış açık kalırken test/doküman sayısını öne çıkarmak kullanıcının beklediği çalışan ürün sonucunu anlatmadı. Sorun test yapmak değil, test/araç teslimini ürün bağlantısının yerine koymak ve çok sayıda pakette kısmi ilerlemektir.
4. **Kesin: gerçek iş de kaldı.** [22 satırlık inceleme](task-status-audit.json) 10 ürün kodu sahibi, 2 host kabulü, 4 kalite/entegrasyon/release kapısı ve 6 gelecek-faz işini ayırır. Split, genel çatışma, verifier, continuation ve recovery/privacy eksikleri bir etiket sorunu değildir.
5. **Tek kök neden diye kabul edilmedi: API bakiyesi/izin.** Önceki API eksikliği bazı gerçek çıkarım deneylerini sınırladı; artık genel kod geliştirme engeli değildir. Yeni gerçek kaynak okuması/paylaşımı ve ücretli test için dar izin gerekir, fakat bağımsız kodun veya bütün projenin durmasının gerekçesi olamaz. Bazı failure'lar model/schema/timeout katmanındadır; ayrı raporları korunur.

## Düzeltmeler ve durumları

| Aksiyon | Durum | Sahip / mevcut kayıt | Kanıt veya sonraki kontrol |
|---|---|---|---|
| Eski ana özet/sonraki adımları düzelt; parser'ı her peer başlıkta durdur; özgün T30 kabulünü geri eşle | **Uygulandı** | Tracker/raporlama | Önceki commit `876e363`; 50 repo/takip testi, closure/docs/anchor ve çalışan 8765 readback |
| 22 açık ana iş için gerçek eksik, gate ve gelecek-faz gerekçesini kaydet | **Uygulandı** | Mevcut audit | [Satır bazlı JSON](task-status-audit.json); kanıtsız Done ve kabul değişimi yok |
| Aktif teslimi tek çalışan kullanıcı sonucuna bağla; parent toplamını WIP sayma | **Çalışma talimatı ve sprint planında netleştirildi; uygulama sonucu henüz bekleniyor** | [Sprint 1](../delivery/sprint-plan.md); mevcut WIP=1 yaklaşımı | Yeni mesaj→izinli analiz→aynı Task önerisi→insan review; her oturum çalışan sonuç ve kalan kabul raporu |
| Mevcut alt dilimin kapsam/kanıt/durumunu teslimle birlikte güncelle; parent kapanışını bütün release'e bağlama | **Kural mevcut; uygulama disiplini netleştirildi** | [Kapanış sözleşmesi](../delivery/task-closure.md) | Alt kabul geçerse alt kayıt kapanır. Parent kendi required seti ve core kabulü geçince hemen kontrol edilir |
| Genel kalite ve gerçek günlük kabulü yerel testten ayrı ölç | **Plan hazır; kalan koşular açık** | T01/T03/T15/T24, [test planı](mvp-test-plan.md) | Dörder semantik case; J04 failure korunur. Yeni host/model izinleri gerektiğinde exact kapsam sunulur |
| Görsel olarak aktif dilim/parent/gelecek faz ve son kapanan dilimleri daha net ayır | **UI değişikliği bu raporda uygulanmadı** | Mevcut tracker görünüm işi | Ekranı değiştiren ayrı somut öneri gerekir; mevcut kanonik durumları kozmetik olarak değiştirerek çözülmez |

Bu rapor çalışma yönünü netleştirir; tamamlanmamış kodu uygulanmış göstermez. Yeni ana görev, yeni statü, otomatik zamanlayıcı, yeni ücret veya ürün kapsamı eklemez.

## Bir iş bundan sonra nasıl kapanacak?

| Seviye | Kapanış anı | Açık kalma sebebi |
|---|---|---|
| Küçük kod/entegrasyon dilimi | Kendi gözlenebilir kabulü + ilgili negatif/regresyon + güncel kanıt/durum kaydı tamamlandığında | Sadece dosyanın yazılması veya bir bağımlılığın bitmesi yeterli değil |
| T01–T30 ana paket | Değişmeyen core kabul + manifestte kendisine ait zorunlu alt/entegrasyon işleri tamamlandığında | İlgisiz sonraki faz işi değil, kendi eksik kabulü açık tutar |
| T15 teknik zincir | Aynı uygulama revisionında kaynak→etki→onay→state→kanıt→düzeltme/recovery kanıtlandığında | Ayrı modül testlerinin toplamı tek zincir kabulü değildir |
| T24 MVP kabulü | Mevcut 14 AC, iki adapter, semantik/günlük kullanıcı ve kurulum kapıları kanıtlandığında | Çekirdek Done sayısı veya paket ZIP'i ürün kabulü yerine geçmez |

**Somut örnek:** T13d split teslimi cycle/ACL/stale/retry/atomiklik kabulüyle biterse T13d kapanır. T13e'nin genel soru/cevap kabulü hâlâ eksikse T13 parent açık kalır; rapor “T13d tamamlandı, T13e şu nedenle açık” der. T13e ve T13'ün diğer zorunlu kabulü bittiğinde parent kapanır; T24 veya bütün Phase 2 beklenmez. Bu bir gelecek testinin geçtiği iddiası değil, mevcut manifestin uygulanma örneğidir.

**Ortak teslim örneği:** Yeni-message yolculuğu T09/T19/T21/T22'ye dokunabilir. Aynı versioned kanıt uygun kriterlerle bu satırlara bağlanır; dört ayrı sahte teslim üretilmez. Her parent'ın kalan required seti ayrı kontrol edilir. Bu nedenle bir teslimde birden çok kapanış mümkündür, fakat “ana akış çalıştı, hepsini Done yap” uygulanmaz.

## Sonraki teslim ve takip ölçüsü

Bir sonraki aktif sonuç [Sprint 1 mikro planındaki](../delivery/sprint-plan.md) izinli yeni mesaj→analiz kuyruğu/worker→review bağlantısıdır. Genel benchmark veya gelecek-faz genişletmesi bunun önüne geçmez; kritik güvenlik/veri kaybı bulgusu varsa ilgili akış önce güvenceye alınır.

Her teslim raporu şu beş soruyu yanıtlar: **Kullanıcı artık ne yapabiliyor? Hangi mevcut alt kabul bitti? Hangi parent neden açık? Gerçek host/model/target testinin durumu ne? Sıradaki tek uygulanabilir adım ne?** Araç/test/doküman çıktıları kendi türüyle belirtilir.

İyileşme; çalışan uçtan uca teslimin gözlenmesi, kabulü tamamlanan alt dilimlerin aynı teslimde kapatılması, parent'ı açık tutan exact kalan ID'lerin azalması ve stale metnin tekrar etmemesiyle takip edilir. Yeni iş girişleri ve kalan kabul ayrı yazılır; sırf sayacı düşürmek veya güvenilir olmayan yüzde üretmek hedef değildir. “Artık sorun çözüldü” denmesi için bu çalışma biçiminin sonraki gerçek teslimde uygulandığı görülmelidir.

## Bu raporun doğrulama sınırı

Güncel kod/manifest, audit, sprint, yönetim ve kapanış belgeleri karşılaştırıldı. Bu tur doküman/link/anchor/closure/progress tutarlılığı kontrol edilir; yeni ürün kodu, runtime suite, model/API veya gerçek sohbet okuması yapıldığı anlamına gelmez. Önceki parser düzeltmesinin 50-test kanıtı önceki teslimindir. Mermaid kaynakları değiştirilmedi.

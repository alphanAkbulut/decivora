# Görev durumları — satır bazlı teyit

**20 Ekim delta:** [T17 core gerçek kabulü](scheduled-native-001.md) sonrası ana8Done/20InProgress/2ToDo. Yalnız T17 evidence/status gözden geçirildi; aşağıdaki19Ekim tam audit tarihsel kalır. Alt kayıt sayıları56Done/42InProgress/26ToDo/5Proposed değişmedi.

**19 Ekim2026.** Kullanıcının talebiyle30ana görev ve129alt kaydın tamamı gözden geçirildi. Bu bir geliştirme takip düzeltmesidir; yeni ürün özelliği, ücretli çağrı, gerçek kaynak okuması veya MVP kabulü değildir. [Makine tarafından okunabilir159kayıt](task-status-audit.json), önceki durum, yeni durum, gerekçe, evidence seviyesi ve kalan kabulü içerir. Canonical durum backlog/team-data; audit ikinci bağımsız görev listesi değildir.

| Durum | Önce | Sonra |
|---|---:|---:|
| Ana Done / InProgress / ToDo |7 /15 /8|7 /15 /8|
| Alt Done |56|56|
| Alt InProgress |16|39|
| Alt ToDo |10|29|
| Alt Proposed |5|5|
| Alt Unspecified |42|0|

## Ne düzeltildi?

- 42durumsuz satırın19'unda kapsamla ilişkili uygulanmış alt küme bulundu: InProgress.23satırda kendi teslim/pilot başlangıcına yeterli kayıt yok: ToDo. Eksik durum, tamamlandı veya yeni bir iş olarak yorumlanmadı.
- 4eskiToDo, gerçek kısmi teslim nedeniyle InProgress oldu: T01e(TR/EN development örnekleri),T18e(host metadata/late-answer),T22b(kalıcı kaynak checkpoint),T24f(soru/geç cevap negatif fixture). Bunların gold/delivery/arşiv/pilot kabulü tamamlanmadı.
- 56Done dar teslim kaydı korundu. Başarısız bir model denemesinin **çalıştırılması ve raporlanması** tamamlanmış olabilir; modelin ürün kabulünü geçtiği anlamına gelmez. Tamamlanan test sayısı ürün tamamlanma yüzdesi değildir.
- 7ana çekirdek kapanışı ve23açık ana iş korundu. Gelecek fazlardaki5Proposed alt dilim sessizce zorunlu geliştirme veya Done yapılmadı. Kabul, parent/owner/first-use kapısı ve bağımlılıklar değiştirilmedi.

## Eski “kalan işler” açıklamaları

Current-state, backlog, build-delivery-plan ve implementation-readiness içindeki güncel özetler son capture/queue, source-bound relation/answer/replacement, AND/OR ve lifecycle koduyla eşleştirildi. Tarihli eski raporlar ve deney sonuçları silinmedi; tarihsel “yok/açık” ifadesi bugünün eksik özelliği sayılmasın diye güncel girişler/linkler eklendi. Team-data'daki durum içermeyen tekrarlar otorite satırıyla eşleştirildi. İlerleme görünümü canonical kaynaklardan yeniden üretilir.

## Teyidin sınırı

Kod ve test/teslim kayıtları statik olarak karşılaştırıldı; bağlı geçmiş raporların dar kapsamı korundu. Bu inceleme tüm159kayıt için yeni runtime veya kullanıcı kabul testi yapıldığı iddiası değildir. Özellikle T24 pilotları, ikinci gerçek adapter, source/model onboarding, indexed kapasite ve genel semantik kalite açık. Örtüşen bir test, alt görevin bütün kabulüymüş gibi kullanılmadı. Güvenilir efor kalibrasyonu olmadığı için toplamdan ürün yüzdesi üretilmedi.

## Tekrarını önleme

`check_task_closure.py` canonical satırların açık durumunu ve exact audit envanterini denetler. Durum değişince aynı incelemede audit/manifest güncellenir; tarihi kanıt yeniden yazılmaz. Parser tanımsız fixture'ı hâlâ Unspecified gösterebilir; canonical CI bunu kabul etmez. Böylece sessizce kaybolan iş veya kanıtsız Done yerine açık, kaynaklı takip kalır.

Doğrulama:49tracker/araç testi geçti; closure/dependency kontrolü30ana/129alt kaydı ve sıfır cycle doğruladı. Önce/sonra129alt kabul ve bağımlılık alanı bire bir eşleşti. Doküman/link/anchor kontrolleri geçti; Mermaid kaynakları değişmedi.15InProgress ana görevin güncel ilerleme/risk/sonraki adım alanları da yenilendi. Yerel8765panosu yeni sayımları ve15ilerleme kaydını salt okunur readback ile sundu; ürün53611görev verileri değiştirilmedi.

## 19Ekim — kullanıcı talebiyle8TODO geliştirme güncellemesi

[Somut kod ve kalan kabul](todo-development-review.md) sonrasında6ana TODO IN_PROGRESS oldu; T25/T30TODO kaldı. Güncel ana7Done/21InProgress/2ToDo; alt56Done/42InProgress/26ToDo/5Proposed. Yukarıdaki ilk tarama sayımları tarihsel başlangıçtır; current JSON/canonical backlog bu dar güncellemeyi içerir. Hiçbir ana kabul azaltılmadı ve yeni Done iddiası yok.


## 20 Ekim — neden hâlâ 22 açık ana iş var?

Kullanıcı açık işlerin gerekliliğini sorguladı. 22 ana tanımın tamamı, manifestteki zorunlu açık alt dilimler ve mevcut kod/test/rapor yollarıyla karşılaştırıldı. [Makine kaydı](task-status-audit.json) her satırın gerekçesini ve zorunlu açık alt ID'lerini içerir. Bu statik takip incelemesi yeni runtime/host/model kabulü değildir.

**Sonuç:** 22 sayısı “22 yeni kod paketi” değildir. 6 gelecek faz, 4 kalite/entegrasyon/release kapısı, 2 gerçek host kabulü ve 10 ürün kodu sahibi vardır. Önceki 11 kod sahibi grubu T16 adapter'ını da içeriyordu; bu incelemede onun kalan gerçek-host kapısı ayrı gösterildi. Toplam ve scope değişmedi. MVP yolunda 16 açık iş bulunması 16 eşit büyüklükte yeni geliştirme anlamına gelmez.

**Takip hataları:**

1. Backlog'un üst özeti 7/15/8 ile kalmıştı; mevcut 8/20/2 ile eşleştirildi. Güncel alanlardaki eski “model yok/onboarding yok” açıklamaları gerçek 20 Ekim teslimleriyle düzeltildi. Tarihsel deney raporları değiştirilmedi.
2. Tracker son task'ı yalnız sonraki task başlığında bitiriyordu. T30'dan sonraki genel araştırma bölümünün Kabul alanı T30'u eziyordu; kapanış manifesti de bu yanlış metni taşımıştı. Parser artık her aynı düzey başlıkta durur. T30'un zaten yazılı özgün kabulü geri eşlendi; gereksinim veya statü değiştirilmedi. Olumsuz regresyon testi genel bölümün task kabulünü/statüsünü değiştirmediğini denetler.
3. 20 In Progress bir aktif sprint WIP göstergesi değildir: kısmi teslimi bulunan geniş ana paketleri sayar. Bunlardan dördü gelecek fazdadır. Bu sayıyı aktif çalışma diye sunmak yanıltıcıdır. Aktif teslim Sprint 1'in yeni mesaj→izinli analiz→review bağlantısıdır; diğer partial kayıtlar bu yüzden Done veya yeniden To Do yapılmadı.
4. P0 karşılaştırma, T15 entegrasyon ve T24 release kanıtları aynı yolculuktan farklı soruları ölçer; ayrı ayrı yeni özellik geliştirme emri değildir. Aynı versioned kanıt gerektiği yerde yeniden kullanılır. Mevcut build/stack ve Q06/Q08 kararları yeniden owner kararı bekliyormuş gibi gösterilmez.

| İş | Sınıf | Neden açık / yapılacak gerçek işlem |
|---|---|---|
| T01 | quality_gate | Veri ve scorer var; bağımsız etiket/adjudication ve geliştirmede kullanılmamış holdout kabulü yok. |
| T02 | host_acceptance | Codex kanıtı var; ikinci coding yüzeyinin gerçek host/version/coverage deneyi tamam değil. T16 ile ilişkili kabul; ayrı iki yeni kod paketi değil. |
| T03 | quality_gate | Build/stack kararı verilmiş; bunu yeniden beklemiyoruz. Açık olan semantik/gerçek zincir ve adil native/management-overhead kıyası. |
| T09 | product_code | Gerçek provider ve iki-chat öneri kanıtı var; genel bağlam/çıkarım, risk assessment ve yeni mesajın izinli sürekli analiz bağlantısı tamam değil. |
| T10 | product_code | Exact eşleme ve olası refinement var; semantik eşdeğerlik/çatışma ve karşı kanıt çözümü genel olarak tamam değil. |
| T13 | product_code | Güvenilir review ve seçenekli kaynak soru var; onaylı split/part_of/AC eşleme ve genel soru-belirsizlik çözümü açık. |
| T14 | product_code | Done guard ve file/human evidence var; genel izinli verifier, hedef/AC revision bağları ve tam parent kriter zinciri açık. |
| T15 | integration_gate | Modül crash/restore kanıtı var; tek uygulama revisionında tam karar-etki-onay-kanıt-düzeltme zinciri raporu eksik. Yeni bağımsız özellik değil. |
| T16 | host_acceptance | Hook adapter kodu ve fixture negatifleri var; kurulu gerçek Claude session/hook kabulü yok. Codex ana yolundan önceye alınmayacak. |
| T18 | product_code | Sınırlı MCP/iki-agent fixture var; gerçek client onboarding ve kaynak ACL koruyan kapsamlı continuation teslimi eksik. |
| T19 | product_code | Kaynak/paylaşım/ilk scope UI artık kodlu ve dar native kabulü var. Gerçek kalan: T19b risk kartı ve genel çatışma/yeni mesaj policy UI. |
| T20 | product_code | Board/Graph/Timeline ve blocker timer var; Q08-A split/child ilerlemesi, Q06-A milestone context ve tam görünüm entegrasyonları eksik. |
| T21 | product_code | Rezervasyon, unknown ve source aktivasyon var; parametre sicili/config revision ve trusted settlement tam değil. API bakiyesi veya yeni bütçe seçimi beklenmiyor. |
| T22 | product_code | Import/native lineage/cursor var; Q07/1C geçmiş manifest/coverage ve prompt-execution-artifact zincirinin tamamı eksik. |
| T23 | product_code | Loopback/redaction/private backup/offline restore var; aktif recovery/migration ve purge/retention/export tamam değil. |
| T24 | release_gate | 14 AC, iki adapter, bağımsız semantik kabul ve günlük kullanıcı pilotu birleşik kanıtı yok. Her modülün testini yeniden yazma işi değil. |
| T25 | future | Ek chat yüzeyleri faz 2; MVP bekleyen işi diye sunulmamalı. Başlanmamış scope korunur. |
| T26 | future | Orphan audit alt kümesi var; gelişmiş reconciliation/holdout iyileşme faz 2. In Progress kısmi geçmiş teslim, aktif sprint değil. |
| T27 | future | Read-only GitHub observer alt kümesi var; gerçek hedef ve host panel kabulü faz 2. PR varlığı AC kanıtı değildir. |
| T28 | future | Paired-cost alt kümesi var; dış connector sync/kalite eşitliğinde kıyas faz 3. Güncel MCP/Codex akışını bekletmez. |
| T29 | future | Release hazırlık alt kümesi var; public ürün release onayı/temiz kurulum/lisans envanteri tam kabulü faz 3. Repo public olması ürün release değildir. |
| T30 | future | Ekip/cloud keşfi faz 4. Tracker genel araştırma kabulünü T30 sanıyordu; özgün multi-tenant kapsam/izin/lisans kabulü geri eşlendi. |

### Kapanış ve öncelik sonucu

Bu incelemede **kanıtı tamamlanmışken gereksiz açık tutulduğu teyit edilen ek ana görev yok**. Bu, bütün eski ilerleme metinlerinin doğru olduğu anlamına gelmez; yukarıdaki somut takip hataları düzeltildi. Kabul edilmemiş kapsamı silerek veya yalnız kod dosyası bulunduğu için Done vererek sayı düşürülmedi. Daha önce T17 bu yöntemle kendi kapsamının gerçek kanıtıyla kapatılmıştır.

Yeni araştırma turu veya yeni ana görev açılmayacak. Önce Sprint 1 birleşik akış teslim edilir; aynı teslimin kanıtı T09/T19/T21/T22'nin ilgili dilimlerine bir kez bağlanır. Ardından T13/T20 split/context, T14 verifier ve T23 recovery/privacy açıkları mevcut sahiplerinde geliştirilir. T02/T16 ikinci host doğrulaması Codex günlük yolculuğundan önceye alınmaz. T01/T03/T15/T24 kabul işleri hazırlanmış ürün dilimlerinin kanıtını kullanır; bağımsız kodu bloke eden sonsuz analiz olarak çalıştırılmaz. Alt dilim ve parent kabulü ayrı kapatılır.

Doğrulama: peer-heading parser regresyonu, repo/tracker suite, closure, doküman/anchor ve generated progress eşleşmesi bu düzeltmenin kontrol kapsamıdır. Ürün runtime ve gerçek model testleri bu inceleme adına yeniden çalıştırılmış sayılmaz. Yeni chat okuması, veri paylaşımı veya ücretli dispatch yapılmadı.

Kontrol sonucu: **50 repo/takip testi geçti**; closure 30 ana/129 alt kayıt ve sıfır cycle, doküman/anchor/progress kontrolleri geçti. Salt okunur 8765 takip süreci güncel parser ile yeniden başlatıldı; API readback özgün T30 kabulünü ve değişmeyen 8/20/2 sayımını doğruladı. Ürün süreçleri/veritabanları değiştirilmedi. Mermaid kaynakları değişmedi; yeniden render iddiası yok.

## Süreç nedenleri ve düzeltme yaklaşımı

Kullanıcının kapanışların bir anda olup olmayacağı sorusu üzerine [teslim akışı retrospektifi](delivery-flow-retrospective.md) hazırlandı. Geniş parent sayımını açıklamak tek başına çözüm değildir: modül/deney çıktıları ile çalışan günlük kullanıcı sonucu ayrılır, küçük kabul kapanışı final release’e ertelenmez, parent kendi kalan required setiyle kontrol edilir. Uygulanmış tracker düzeltmeleri ile henüz tamamlanmamış ürün entegrasyonları ayrı gösterilir.

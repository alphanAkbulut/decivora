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

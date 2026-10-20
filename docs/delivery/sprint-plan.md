# MVP teslim planı ve aktif sprint

**Durum: 20 Ekim 2026.** Bu plan mevcut backlog'un yürütme görünümüdür; yeni backlog, kapsam daraltma veya tarih garantisi değildir. Kaynaklar: [ana işler](backlog.md), [kapanış kanıtları](task-closure.json), [denetim](../quality/task-status-audit.json). Testlerin yürütülmesi: [MVP test planı](../quality/mvp-test-plan.md).

[22 açık işin gereklilik ve takip hatası incelemesi](../quality/task-status-audit.md#20-ekim--neden-hâlâ-22-açık-ana-iş-var): sayılar değişmedi; her açık satırın kalan kabulü sorgulandı.

## Güncel sayılar

| Seviye | Done | In Progress | To Do | Proposed | Toplam |
|---|---:|---:|---:|---:|---:|
| Ana işler | 8 | 20 | 2 | 0 | 30 |
| Alt kayıtlar | 56 | 42 | 26 | 5 | 129 |

Ana ve alt kayıtlar birbirine eklenmez. Açık 22 ana işin **16'sı MVP yolunda, 6'sı sonraki fazlardadır**. MVP yolundaki 16 iş: 11 ürün kodu sahibi (T09/T10/T13/T14/T16/T18/T19/T20/T21/T22/T23), 3 P0 kalite/karar işi (T01–T03), 2 entegrasyon ve kabul kapısı (T15/T24). Bu ayrım görev kapsamını veya kabul kriterlerini değiştirmez. In Progress kayıtları aynı anda çalışan 20 agent değildir; kısmi teslimi olan açık ana işlerdir. Sayılar tamamlanma yüzdesi veya süre tahmini değildir.

Done: **T04** runtime/sözleşmeler, **T05** proje binding, **T06** ingress/checkpoint, **T07** olay logu/projector, **T08** atomik change set/policy, **T11** gerekçe graph, **T12** impact preview/apply planı, **T17** desteklenen Codex adapter çekirdeği. Her kapanış kendi kapsamına aittir; bütün MVP bitmiş değildir.

Tamamlanan 56 alt kaydın birincil çıktı sınıflaması: **42 kod/araç/sözleşme, 13 test/deney/değerlendirme hazırlığı, 1 analiz/karar**. Bu, toplam harcanan eforun veya bütün dokümanların sayımı değildir; kodla gelen test/doküman ikinci görev sayılmaz. Sınıflama [work breakdown](work-breakdown.json) içindedir.

## Ürün hedefi ve mevcut kanıt

İzinli Codex konuşması → kaynaklı görev/karar/soru önerisi → mevcut görevle eşleme → insan incelemesi → durum/karar etkisi → güncel kabul kanıtı → sonraki sohbetin proje bağlamı.

- [İki gerçek Codex sohbetinin dar UI yolculuğu](../quality/native-ui-journey-001.md): 6 kaynak ve 2 Luna isteği; A tek görev önerdi, B aynı Task ID için başlangıç önerdi. Owner kapsamı ve güncel insan geçişini onayladı: tek Task In Progress, bağlı soru Resolved; AC/DoD not_run. Eski stale model önerisi tarihçede kaldı.
- [Düzenli native capture](../quality/scheduled-native-001.md): 10 saniye arayla 3 okuma; kaynak 6→6, duplicate 0; Stop/Disconnect/reload geçti, API harcaması ve task değişimi olmadı. Okumalar arasında yeni mesaj yazılmadı. Bu nedenle yeni mesajların sürekli anlamlandırılması henüz kabul edilmiş değildir.
- Kaynak kurulumu, exact paylaşım önizlemesi, ayrı aktivasyon, ilk review'da AC/DoD veya bağlı netleştirme ve sınırlı capture/model worker kodu var. Günlük birleşik otomasyon, genel semantik kalite ve doğrulanmış Done zinciri açık.

## Büyük plan

Sprintler teslim sırasıdır; sabit takvim veya Scrum sertifikasyon iddiası değildir. Ürün önceliği kullanıcı/PO'da, teknik uygulama planı mevcut bağımlılıklara göre ilerler. Süre tahmini, ilk birleşik teslimin gerçek kapasitesiyle yapılır.

| Sprint | Çalışan sonuç | Mevcut sahipler | Çıkış kapısı |
|---|---|---|---|
| 1 · Konuşmayı düzenli işle | Yeni mesajı kayıpsız al; izinli bağlamla analiz et; Inbox'a tek öneri getir; aynı görevi ilerlet | T09/T13/T19/T21/T22; T17 tamamlanmış temel | İlerleyen gerçek sohbet; iki sohbet aynı proje; stop/revoke/expiry; duplicate ve izinsiz egress yok |
| 2 · Diyaloğu ve değişimi takip et | Konu dönüşü, açık soru/geç cevap, benzer görev, Blocked/Cancelled ve karar değişimi | T09/T10/T13/T20/T22; T01/T03 kalite kararı | Dörder case; bağımsız beklentiyle pass/fail/unknown/not_run; yanlış eşleme veya false Done çözülmeden grup kapanmaz |
| 3 · Sonucu ve etkiyi kanıtla | Done beyanı → güncel kriter → izinli hedef kanıtı → ayrı kabul; AND/OR ve karar değişimi | T13/T14/T20/T23; T11/T12 mevcut temel; T15 kapısı | Eski kanıt/onay reddi; yanlış obsolete yok; rollback/replay/restore aynı doğru state |
| 4 · Günlük kullanım ve MVP kabul | MCP devam bağlamı, ikinci coding adapter, temiz kurulum, recovery ve günlük pilot | T16/T18/T19/T21/T22/T23/T24; T02 iki yüzey kanıtı | Mevcut 14 MVP AC'nin kanıt matrisi; iki adapter raporu; kullanıcı lokal kurulumdan gerçek işi tamamlar |

Claude kapsamdan çıkarılmadı; **Codex günlük akışı önce** tamamlanır. Tek adapter kabulü sınırlı pilot olarak adlandırılır. Ekip/cloud, ek chat yüzeyleri, gelişmiş reconciliation ve public release T25–T30 kapsamındadır; MVP'ye sessizce taşınmaz.

## Teslimi nasıl görünür kapatacağız?

[Retrospektif](../quality/delivery-flow-retrospective.md) uyarınca tek aktif sonuç Sprint 1'in ilerleyen mesaj yolculuğudur. Mevcut küçük dilim kendi kabulünde kapanır; parent aynı teslimde core/required-set kontrolünden geçer. Parent açık kaldıysa kalan exact alt ID ve kanıt eksiği raporlanır. Tek entegrasyon farklı kriterleri sağlarsa birkaç kayıt birlikte kapanabilir; final güne erteleme veya otomatik toplu Done yok. 20 In Progress ana paket aktif WIP sayısı değildir. Bu plan yeni task veya scope üretmez.

## Sıradaki mikro plan — Sprint 1

Bunlar yeni ana görev değildir; mevcut işlerin uygulanacak dilimleridir.

| Sıra | Kod/entegrasyon teslimi | Kabul / kanıt | Bağımlılık |
|---|---|---|---|
| 1 | Yeni yakalanan mesaj için model paylaşım kapsamı ve aktivasyonun uçtan uca bağlantısı | Yeni mesaj ya izin kapsamındadır ya bekleyen exact paylaşım önizlemesidir; eski grant yeni metne otomatik yetki vermez; kullanıcı seçilmiş kaynak/model/süre/bütçeyi görür | Mevcut capture ve paylaşım temelini kullanır; daha geniş sürekli paylaşım politikası gerekiyorsa somut owner kararı |
| 2 | Capture receipt → analiz kuyruğu → bounded worker → review bağlantısı | Her uygun kaynak bir kez işlenir; gap/unknown görünür; stop/revoke yeni dispatch'i durdurur; restart kendiliğinden başlamaz | 1'in yetki sözleşmesi; yerel kod/fixture geliştirmesi API izni beklemez |
| 3 | İlerleyen konuşma ve ikinci sohbet bağlamı | Yeni görevden sonra başlama/blocked bilgisi aynı ID'ye önerilir; ayrı proje karışmaz; insan uygulaması ayrı kalır | 2; kayıtlı proje bağlamı ve schema |
| 4 | Gerçek UI kabulü ve sprint review | Yeni mesaj aktif okuma sırasında eklenir; capture, öneri ve insan uygulaması ayrı kanıtlanır; kullanıcı günlük akışı görür | Yerel kontroller geçer; yalnız gerekli exact kaynak ve ücretli paylaşım izinleri alınır |

Kalan checklist/timeline UX, verifier ve backup işleri uygun bağımsız dilimlerde ilerleyebilir; bütün işler tek sıra beklemek zorunda değildir. Buna karşılık source yetkisi → dispatch, güncel kapsam → durum uygulaması ve güncel kanıt → Done bağımlılıkları atlanmaz.

## Daily ve takip

**Yapılan:** T17 core gerçek native kanıtla kapandı; ilk scope ve iki sohbet dar yolculuğu doğrulandı. **Şu anki eksik:** yeni mesajın düzenli yakalanmasından izinli model işlemesine ve aynı göreve öneriye kadar birleşik günlük akış. **İlk teknik iş:** yukarıdaki 1–2 dilimi. **Karar bekleme:** şu anda bu plan için cevapsız yeni soru yok; yeni gerçek okuma/egress testi için kapsam test öncesi sunulur. Önceki deneme izinleri tüketilmiştir; genel API tavanı kaynak paylaşım izni değildir.

Her teslimde ilgili test ve log kanıtı, kalan gerçek eksik ve sonraki kod adımı yazılır. Ana görev yalnız kendi kabulü sağlandığında kapanır; sayıyı azaltmak için kriter düşürülmez. Eski kanıtlar raporlarda/Git geçmişinde korunur; bu plan güncel tek yürütme görünümüdür.

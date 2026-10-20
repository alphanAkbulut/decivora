# Belge, diyagram ve GitHub güncellik denetimi — 20 Ekim 2026

**Tür:** mevcut durumu yeniden uzlaştırma; yeni ürün kapsamı veya release kabulü değil. Denetim sürerken kullanıcı J04sınırlı çalışmasını ayrıca onayladı; aşağıdaki güncel sonuç onu içerir. İncelenen GitHub main: `80f8098a82e9e42c576bc081d1913e7b2292c1ef`. Karşılaştırma706remote blob'u kapsadı; eksik yerel dosya yoktu. Bu tur değiştirilen giriş belgeleri dışında yalnız önceden mevcut, ilgisiz `upstream-component-inventory.csv` farkı görüldü; bu değişiklik teslimata alınmadı. Remote'da olmayan bütün yerel dosyaların yayınlanması amaçlanmadı.

## Bulgular → yapılan düzeltme → açık kalan

| ID | Bulgu / kanıt | Düzeltme | Sonuç ve sınır |
|---|---|---|---|
| DOC-01 | README yalnız eski6mesaj pilotunu anlatıyor; native ve çok turlu raporlar daha yeni | Giriş tablosuna8native kaynak ve J01–J04 sonucu, audit bağlantısı eklendi | Capture, semantik öneri ve canonical apply ayrı; genel başarı iddiası yok |
| DOC-02 | current-state/handoff içinde7/15/8ve39/29alt sayımlar güncel gibi okunuyor | Güncel ana7/21/2vealt56/42/26/5özeti; tarihsel notlar ayrıldı | Task kapanışı değiştirilmedi; sayı azaltmak için AC daraltılmadı |
| DOC-03 | Güncel yön tablosu “runtime hâlâ yok”, roadmap sadeceP0 diyordu | YerelP1geliştirme + açıkP0kalite/MVPkapıları olarak düzeltildi | Çalışan modül ile tamamlanmış otomatik ürün ayrımı korundu |
| DOC-04 | Karar haritası DEC-22'de bitiyor, son seçimlerin gerekçeleri dağınık | DEC-23–27, alternatif/neden/bedel/kanıt/yeniden değerlendirme tablosu | Ürün owner kabulü, mühendislik ayarı ve bekleyen risk kararı ayrı |
| DOC-05 | Evrim hikâyesi kaynak sonrası11Ekim'de kalmış |13–20Ekim plan→runtime→native→çok turlu→clarification/unknown öğrenmesi eklendi | E01–14orijinal kaynak kimlikleri değiştirilmedi; eksik turn ID uydurulmadı |
| DOC-06 | Overview ve karar evrimi yeni clarification/dört-case/aging kararını göstermiyor | Mevcut dört Mermaid bloğu güncellendi (README1, karar haritası2, güncel yön1); güncel tüm kaynaklar offline render kontrolüne alındı | Diyagram rengi veya render başarısı runtime/model kabulü değildir |
| DOC-07 | Engine girişi yerel runtime yerine yalnızP0fixture izlenimi veriyor | Yerel kod ve sınırlı native/model kanıtı ayrı tarif edildi | Engine ayrı mikroservis veya tamamlanmış production ürünü değil |
| DOC-08 | GitHub mevcut görünürlük `private:false`; ilk private niyeti mevcut ayar sanılabilir | DEC-10tarihsel niyet olarak korundu; güncel public gözlemi not edildi | Bu tur erişim ayarı değişmedi; kim/ne zaman değiştirdiği bilinmiyor; lisans/release kabulü değil |

## Gerçek deney sonucu

| Case | Tam model yanıtı | Beklenen dar kontrol / gözlenen sonuç | Durum |
|---|---:|---|---|
| J01 |6/6| Aynı Task, doğru ilerleme; kanıtsız Done kabul edilmedi | Dar taslak kontrolleri geçti; görev bitmiş veya genel kalite geçer değil |
| J02 |5/6| Kapsam netleştirmesi ayrı Task önerildi; m4generation unknown; sonraki doğru task ilerlemesi yanlış öneriyi silmez | Eksik; ürün kuralı DEC-25ile netleşti |
| J03 |5/6| İki görev ayrıldı, belirsiz cevapta kaçınıldı; m6generation timeout | Eksik; eski unknown tekrar edilmedi |
| J04 |2/6provider yanıtı| m1soru kaçırıldı; m2paraphrase unsupported_question ile reddedildi | Eksik; m3–m6gönderilmedi. [Son rapor](dialogue-batch-001-j04.md) |

**Toplam:**20dispatch kabulü,18tam provider yanıtı,17valid çıktı/1validation hatası/2unknown;4/4grup başarısı yok. Bilinen yanıtlarda28903input+5515output=34418reported token. Unknown generation tokenları sıfır değil, bilinmiyor. Root tüm önceki deneyleri de içerir:50dispatch/100HTTP bütçe payı, bilinen$0.059952+korunan$0.006750=$0.066702yerel tahmin; nihai fatura değil. Kaynak: [ilk rapor](dialogue-batch-001.md), [devam raporu](dialogue-batch-001-continuation.md) ve makine çıktıları. Bu tablo ayrı deney otoritesi değildir.

## Projeyi şekillendiren son kararların nedeni

- **DEC-23:**48senaryoyu tek bulk yerine dört-case gruplarla çalıştırmak: tek mesaj başarısını bütün proje bağlamına genellememek, bulgu sonrası küçük düzeltme ve owner incelemesi yapmak.
- **DEC-24:** Bilinen başlangıçtan >7gün blocker uyarısı: unutulan beklemeyi görünür kılmak. Uyarı otomatik task ilerletmez; başlangıç unknown ise yaşı unknown kalır. Harici bildirim kurulmadı.
- **DEC-25:** “Önce kapsamı netleştirelim” ayrı teslim istemiyorsa Task'la bağlı clarification: bilgi korunur, gereksiz To Do üremez. İnsan review/resolve ve audit var; yeni model uyumu henüz yeniden ölçülmedi.
- **DEC-26:** Unknown için ayrı owner review ve rezervi tutma: potansiyel harcamayı sıfırlamadan, aynı isteği tekrarlamadan yalnız izinli yeni işlere devam. J03unknown için de bu tur ayrı owner kabulü alındı; J04soru validation hatasında durdu. Eski kabul yeniunknown'a genellenmez.
- **DEC-27:** Son timeout'un45saniye socket beklemesinde oluştuğu doğrulandığı için yeni işlemlerde120saniye ayarı: istemci beklemesine alan açar; sağlayıcı kök nedeni veya çözüm garantisi değildir. Token/para/no-retry kuralları değişmedi.

Tam alternatifler ve yeniden değerlendirme koşulları [karar haritasında](../product/decision-map.md), olgunlaşma [evrim hikâyesinde](../discovery/evolution.md). Kaynak sözleşmeleri ve tarihsel ham model sonuçları yeniden yazılmadı.

## Mevcut kod ve kalan kabul

Yerel clarification source→exactTask→humanreview→Open→humanresolution→Resolved akışı ve restart/backuprestore kontrolleri önceki teslimde doğrulandı. Yeni schema/talimat eklenmeden önce alınan baseline sonuçları yeni prompt başarısı gibi sunulamaz. Seçeneksiz bağımsız proje sorularının tam yakalanması ve serbest cevapla otomatik clarification kapanışı açık kalır.

Native pilot2human/6assistant kaydı ve8→8dedup gösterir; authored synthetic dialogue batch'i native capture testi değildir. Native task In Review ve ACnot_run. Ana ürün capture→context→reconcile→impact→review/apply→verification→devam zincirinin günlük kullanım kabulü tamamlanmadı. Ana23açık işin17'si MVP yolunda,6'sı gelecek fazdadır; parent kabulünü tek alt özellik teslimi kapatmaz.

## Doğrulama ve yayın kanıtı

- Denetim başlangıcı main commit'i GitHub'dan yeniden okundu. [Önceki GitHub kontrolü](https://github.com/alphanAkbulut/decivora/actions/runs/39338494618) `completed/success`; bunun model doğruluğuyla eşdeğer olmadığı korunur.
- Belge denetimi kendi başına yeni kaynak/ücret izni vermedi. Kullanıcının sonradan verdiği ayrı J04onayıyla yalnız2model+2sayım çağrısı ve izole J04DBoluştu; mevcut bütçe/tavan/expiry, task closure ve public/private ayarı değişmedi. Sonuçtaki source-literal soru talimatı ve salt okunur J04report seçimi kodda düzeltildi; yeni sohbet okunmadı.
- Güncel Mermaid render ve source/hash kanıtı: [render makbuzu](diagram-render-results.json); insan görsel inceleme kapsamı: [diyagram denetimi](diagram-review.md).
- Belge/anchor/closure/progress kontrolleri ve49repo/tracker testi yayın öncesinde doğrulanır; sonuç makbuzları aşağıdadır. Soru talimatı/report seçimi değiştiği için runtime regresyonları bu tur yeniden çalıştırıldı; sonuç aşağıdadır.
- Yayın sadece bu denetim dosyaları ve karşılık gelen SVG/render makbuzuyla sınırlandırılır. Secret, gerçek transcript, pilot DB, ledger ve ilgisiz CSV yayınlanmaz. Yeni commit sonrası remote tree/hash readback ayrı yapılır; henüz çalışmamış yeniCI başarılı sayılmaz.

## Sonraki açık adım

J03unknown rezervli devamı için kullanıcı ayrı onay verdi; J04planı iki turda durdu. Son rapor [J04bulgularını](dialogue-batch-001-j04.md) ve neden görünür Codex sohbeti açılmadığını açıklıyor. Sonraki küçük trial exact veri/talimat sürümü ve geçerli izinle sınırlandırılmalı; eski expiry uzatılmaz. Eski baseline yeniden yazılmaz; J05veya yeni trial bu tur başlatılmadı.

## Son doğrulama sonucu

57/57Mermaid render; dört değişen şemanın tam görsel incelemesi;647runtime ve49repo/tracker testi geçti. Doküman/anchor/closure/progress kontrolleri geçti. Runtime testinde ilk adlandırılmış modül çağrısı sibling fixture import'u nedeniyle çalışmadı; standart discover komutuyla647test başarıyla koşuldu. Gerçek model J04iki turunun başarısızlığı testlerin geçmesiyle örtülmedi. Remote commit ve blob readback yayın sonunda ayrıca kontrol edilir; sonraki CIsonucu bağımsızdır.

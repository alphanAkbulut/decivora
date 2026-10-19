# İlk dört diyalog senaryosu — gerçek model bulguları

**İlk duruş raporu —20 Ekim2026. Güncel onaylı devam ve geliştirme [ayrı kayıtta](dialogue-batch-001-continuation.md); aşağıdaki ilk sonuçlar tarihsel olarak korunur.** Kullanıcı dört senaryo halinde ilerlemeyi, bulguları raporlayıp sonraki adıma onayla geçmeyi istedi. Yalnız J01–J04 hazırlandı; J05–J48 için model çağrısı yapılmadı. [Makine sonuçları](dialogue-batch-001-results.json).

## Sonuç

| Senaryo | İlerleme | Sonuç | Gözlenen durum |
|---|---:|---|---|
| J01 — plan, başlangıç, test edilmemiş bitirme |6/6mesaj | **Hedef görev/durum kontrolleri geçti** | Aynı Task; To Do→In Progress önerisi; Done beyanı alındı, kanıtsız Done reddedildi. Canonical In Progress |
| J02 — konu değiştirme ve geri dönüş |4/6istek kabulü;3model yanıtı | **Eksik / inceleme gerekli** |2.mesaj ayrı kapsam-netleştirme Task'ı önerdi, uygulanmadı.4.mesajda generation sonucu unknown; kalan2mesaj çalışmadı. Canonical Task To Do |
| J03 — iki benzer görev ve belirsiz zamir |0/6 | **Çalıştırılmadı** | Yeni belirsiz kullanım nedeniyle grup durdu |
| J04 — iki soru ve geç cevap |0/6 | **Çalıştırılmadı** | Yeni belirsiz kullanım nedeniyle grup durdu |

Bu tablo tüm ürünün başarı oranı değildir. Beklentiler AI-authored taslak; bağımsız insan-gold/holdout yok. J01'in dar kontrolünden genel karar çıkarım kalitesi veya bütün diyaloğun anlaşılması sonucu çıkarılmaz. J02 eksik olması yanında semantik gri bulgu da içerir; “tamamlanmadı” etiketi bunu gizlemez.

## Deney nasıl yürüdü?

`scripts/run_dialogue_batch.py --prepare` yalnız ilk4case'i özel klasöre dondurur. `--run` aynı grubun turunu sırasıyla işler: yalnız o anki mesajı kaydet→mevcut canonical proje + önceki sınırlı mesajları hazırla→exact payload için model/bütçe grant'i ver→sayım→Luna çıkarımı→literal/source/schema kontrolü→önceden ilan edilmiş dar kontrol→ayrı **scripted test operatörü** aksiyonu→sonraki mesaj. Gelecek mesajlar ve oracle modele gönderilmedi. Tek seferde bütün senaryoyu verip geçmişi bildiğini varsayan bir ölçüm değildir.

- Talep edilen model `gpt-6-luna`; ayrı reasoning effort alanı gönderilmedi. API çağrısı Low/Medium diye etiketlenmez. Provider kimliği/sürümü ve fatura ayrıca doğrulanmış değildir.
- En fazla24generation+24count planı; gerçekte10dispatch/20HTTP bütçe payı,9tam yanıt ve1unknown. Tekrar/model yükseltme/sonraki batch yok.
- Her senaryo ayrı SQLite Workspace. `synthetic_dialogue` açık kaynak türü; yerel Codex native capture yapılmış gibi provenance üretilmedi. Roller fixture metadata'sı, onay yetkisi değildir.
- Kontrollü operatör yalnız ilk açık Task adaylarını ve ayrı sentetik AC/DoD sözleşmesini kaydeder; doğru mevcut Task başlangıcını ayrıca review eder. Keyfi yeni adaylar uygulanmaz. Done negative probe kanıt sağlamaz. Bunlar gerçek insan UX/kabulü veya kullanıcı otomatik onayı değildir.
- Başarısız/unknown durumda grup durur. Tamamlanmış raporu tekrar okumak API çağırmaz. Kısmi crash klasörü sessizce yeniden başlatılmaz. Mevcut runner ilk4case'e sabittir; otomatik sonraki grup yok.
- `scripts/report_dialogue_batch.py` sadece receipt okur, key veya ağ kullanmaz. Public JSON receipt türevlerini ve ayrı AI analyst yorumlarını içerir; raw model output, exact private request, DB ve key repoda yoktur.

## Bulgu B001-F1 — netleştirme ayrı görev mi?

**Kanıt:** J02_m2 kaynağı “Önce kontrolün kapsamını netleştirelim.” Model `Task / proposed / Kontrolün kapsamını netleştirme` verdi. Yeni aday kaynaklıdır; canonical Task'a uygulanmadı.

**Yorum:** Dar oracle sonraki turlarda yeni Task beklemediği için `unexpected_new_task_candidate` ile başarısız saydı. Fakat bu, gerçekten yeni bir teslim mi yoksa mevcut işin açık kapsam sorusu mu konusunda ürün kuralı gerektirir. Otomatik olarak “model yanlış” veya “test yanlış” demiyoruz. Beklenti değiştirilerek eski sonuç geçirilmedi.

**Öneri — owner kararı bekler:** Ayrı teslim/alt görev açıkça istenmedikçe bu ifade mevcut Task'a bağlı netleştirme ihtiyacı olsun. Kayıp olmamalı, fakat yeni bağımsız To Do üretmemeli. Bunun için seçenek zorunlu olmayan açıklama sorusu / linked clarification sözleşmesi gerekir. Mevcut soru taslağı API'si en az2literal seçenek ister; yalnız prompt'a “yeni Task üretme” demek soruyu kaybettirebilir. Şema/domain/UI ve kabul testleri ayrı, küçük bir teslimle ele alınmalı. Henüz yeni ürün kuralı veya prompt değişikliği uygulanmadı.

## Bulgu B001-F2 — generation sonucu unknown

**Kanıt:** J02_m4 için input count1682başarılı. Ledger diagnostic phase=`generation`, code=`provider_connection_unknown`; usage=null. Yeni2250microusd rezerv korunuyor, root frozen. Aynı payload tekrar gönderilmedi.

**Kök neden sınırı:** Count ve generation farklı HTTP işlemleridir. Model yanıtının connection, timeout, TLS veya JSON çözümlemesi sırasında mı kaybolduğu tarihsel genel koddan kesinleşmiyor. Sayım başarısı generation başarısı değildir; unknown sonuç modelin diyaloğu yanlış anladığına dair kanıt değildir. Mevcut istemci45saniye bekler; bu tek olay için “kesin timeout” demiyoruz.

**Uygulanan düşük riskli düzeltme:** Gelecek çağrılarda timeout/TLS/JSON decode ayrı allowlist kodlarıyla yazılır (`provider_timeout_unknown`, `provider_tls_unknown`, `provider_json_invalid`). Secret/raw hata text'i kaydedilmez. Eski genel hata kaydı geriye dönük yeniden adlandırılmadı; timeout/istek limiti değiştirilmedi, ağ denemesi yapılmadı. Offline mocked HTTP regresyonu üç hata sınıfını ve gövde maskelemesini kontrol eder.

**Devam önerisi — ayrı onay bekler:** Yeni2250microusd de harcanmış gibi tutulabilir; actual=null ve eski exact payload tekrar reddi korunarak yalnız kalan14mesaj (J02_m5–m6, J03'ün6mesajı, J04'ün6mesajı) ayrı sonlu continuation planına alınabilir. En fazla14generation+14count, aynı10kinput/2koutput, Luna, aynı3USD root ve mevcut expiry. Bu J02_m4'ü tekrar etmek veya J02'yi eksiksiz başarılı saymak değildir. Yeni continuation kodu/planı kullanıcı kararı sonrası hazırlanacak; mevcut report üzerine yazılmayacak. Root henüz açılmadı ve yeni çağrı yapılmadı.

## Bulgu B001-F3 — değerlendirme kapsamı eksik

J02_m3'te “giriş sayfasının rengi mavi olsun mu?” açık sorusuna model hiçbir structured aday vermedi. Dar oracle yalnız restore Task kimliği/yanlış start'ı kontrol ettiği için bu turu geçirdi. Bu bir **ölçüm kapsamı boşluğu**: task/status kontrolü bütün açık soruların yakalanmasını ölçmez. Teklif edilen linked clarification kuralıyla birlikte, seçenekleri literal verilmemiş soruların nasıl kalıcı izleneceği netleşmeli ve ayrı beklenen sonuç eklenmeli. Bu kayıt gizlenmedi veya bütün tur anlamı doğru diye sunulmadı.

## Bulgu B001-F4 — J01 pass kapsamını aşmayalım

J01_m3 “Kapsamı böyle tutalım” ayrıca bir Decision adayı üretti. Uygulanmadı. Task progression kontrolü bunu hata saymıyordu. Bunun uygun bir kapsam-onayı kaydı mı, gereksiz yeni mimari karar mı olduğu ayrı granularity review gerektirir. Başarılı J01 sonucu yalnız Task kapsamı, aynı-ID ilerleme, qualifier korunması ve false-Done guard'ı içindir.

## Maliyet ve çağrı hesabı

-9tam yanıt:14080input+2743output=16823reported token.10.çağrının generation tokenları unknown. Bu toplam bütün hesap kullanımı değildir.
- Bu grup yeni bilinen yerel fiyat tahmini3136microusd (**$0.003136**) +yeni unknown rezerv2250microusd (**$0.002250**) =yerel bütçe taahhüdü artışı5386microusd (**$0.005386**).
- Ortak root önce55940→sonra61326microusd (**$0.061326**); bunun56826'sı bilinen tahmin,4500'ü iki unknown rezervidir. İlk unknown daha önce ayrı onayla rezerv korunarak kabul edilmişti; bu yeni unknown o onaya dayanarak açılmadı.
- Root40dispatch/80HTTP bütçe payı;3USD tavan değişmedi. Bunlar benimsenmiş fiyat snapshot hesaplarıdır, doğrulanmış fatura değildir. Belirsiz generation'ın provider'a ulaşıp ulaşmadığı veya gerçek faturası bilinmiyor.

## Sonraki onay kapısı

1. Netleştirme ve seçeneksiz açık soru için önerilen linked kayıt kuralını karara bağla; gerekiyorsa küçük şema/domain/UI geliştirmesini yap.
2. Yeni unknown rezervini koruyarak yalnız kalan14mesaja devam için risk/kapsam onayı al; aynı mesajı tekrar veya yeni grubu otomatik çalıştırma.
3. İlk4grup raporuna ayrı continuation sonuçlarını ekle. Sonra J05–J08 için tekrar bulgu ve owner onayı; kalan44case henüz başarı/başarısızlık sonucu değildir.

Genel ürün, ekip ve native arka plan kabulü bu deneyle kapanmaz. Ana task sayıları deney sayısıyla azaltılmaz.


**Yerel doğrulama:**640runtime testi geçti; üç batch-runner kontrolü fake HTTP ile24mesajın sıralı context'ini, aynı raporu tekrar okumada sıfır çağrıyı, expiry reddini ve ilk unknown'da sonraki case'leri durdurmayı sınar. Ayrı HTTP diagnostic kontrolü timeout/TLS/JSON kodlarını maskeli tutar. Bu fake testler gerçek model başarı sayılarına katılmadı. UI/57Mermaid kaynağı değişmedi; bu teslimde yeniden browser/render kontrolü yapılmış diye sayılmadı.

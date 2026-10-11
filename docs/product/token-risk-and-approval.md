# Yüksek token tüketimi riski ve ek onay

**2026-10-11 — Kullanıcı ihtiyacı kabul edildi; teknik tasarım önerisi, uygulanmadı.** Kullanıcı aşırı token tüketebilecek işlerin önceden tespitini ve ayrıca onaylanmasını istedi. Bu belge [token ekonomisi](../architecture/routing-token-economy.md) ve [işlem limitlerine](../architecture/resource-limits-and-abuse.md) ek bir kontrol tanımlar. Risk onayı bütçe, veri erişimi, dış modele aktarım veya runner izni yerine geçmez.

## Amaç ve sınır

Bütçesi henüz dolmamış bir iş de gereksiz derecede pahalı olabilir. Amaç, büyük veya belirsiz tüketimi kullanıcıya **başlamadan** göstermek; gerekirse daha dar bir yol seçtirmektir. Token/maliyet tahmini kesin fatura değildir. Kaynak receipt'i alınmışsa iş onay beklerken kalıcı kaydı korunur; task otomatik başarısız veya tamamlandı olmaz.

P1 önerisi deterministik preflight kontrolüdür. Riski anlamak için bütün geçmişi başka bir pahalı modele göndermeyiz. Mevcut manifest, boyut/token tahmini, planlanan model/araç adımları, izinli metadata ve kullanım kayıtları kullanılır. Kaynak okuma izni yoksa tahmin uğruna içerik alınmaz. Semantik yardımcı değerlendirme ileride gerekirse kendisi de bütçeli/onaylı iş sayılır.

## Olağan dışı durumda durma ve devam etme

**2026-10-11 — Kullanıcı token ve context sınırları ile onay bekleme ihtiyacını ayrıca doğruladı.** [Token/context sözleşmesi](../architecture/routing-token-economy.md) zorunlu preflight'ın parçasıdır. Bu gereksinim mevcut hesaba otomatik hard cap uygulandığı anlamına gelmez.

- Normal eşik içinde ve geçerli grant/rezervasyonla iş ilerler.
- Risk inceleme eşiği aşılmış fakat kesin tavanlar içinde sonlu plan kurulabiliyorsa `requires_risk_approval`: yeni model/araç dispatch'i durur, insan sınırları ve planı görür. Sessizlik, eski genel onay veya agent cevabı onay değildir.
- Kesin token/context/para/attempt sınırı aşılacaksa veya zorunlu üst sınır bilinmiyorsa `blocked`: ek risk onayı bunu aşamaz. Kapsam küçültülür veya yetkili ayrı policy değişimi hazırlanır.
- Çalışma sırasında döngü, büyüyen context, beklenmedik child/retry ya da unknown usage saptanırsa yeni dispatch'ler durur. Çağrı öncesi output sınırı gerekir; streaming'i sonradan kesmek veya timeout, oluşmuş tüketimi geri almaz.
- Bekleme kaydı checkpoint, kalan kapsam, sebep, kullanılan/rezerve edilen/bilinmeyen tüketim ve uygulanabilir devam yollarını gösterir. Task `done` olmaz; kaynak ve geçmiş korunur. Yeniden başlatma aynı parent muhasebesiyle güncel izin/tavanları tekrar kontrol eder.

TRA-04 güvenli üst sınırı olmayan context/output capability'yi; TRA-06 unknown tüketim ve eşzamanlı rezervasyonu; TRA-07 in-flight ile yeni dispatch ayrımını; TRA-09 dış hesabın sınırlanamayan tüketimini de içerecek. Bunlar planlı senaryolardır, bu belge değişikliği test başarısı değildir.

## Hangi sinyaller risk yaratır?

| Sinyal | Açıklanacak gerekçe / daha az tüketen aday yol |
|---|---|
| Büyük geçmiş import'u veya tam yeniden analiz | Kaynak/chunk sayısı, tahmini toplam input/output; aktif işler önce, sınırlı batch ve checkpoint |
| Aynı context'in tekrar gönderilmesi / cache geçersizliği | Tekrarlanan byte/token, değişen revision; delta, hedefli retrieval veya geçerli evaluation'ı yeniden kullanma |
| Çok child agent, görev veya paralel çağrı | Parent planın toplamı; child başına düşük tüketim toplam riski gizlemez; fan-out ve concurrency sınırı |
| Retry/escalation zinciri veya ilerlemeyen döngü | Deneme sayısı, önceki unknown usage, gözlenen ilerleme; durdur/incele veya deterministik çözüm |
| Daha büyük context/output ya da model değişimi | Mevcut → önerilen planın tahmini token ve parasal etkisi; model pahalı olduğu için otomatik seçilmez |
| Toplu embedding, reranking veya özet yenileme | Ayrı metered operation toplamı; yalnız değişen/ilgili kayıtları işleme |
| Dönem bütçesinin yüksek payı / olağandışı tüketim hızı | Kendi yetkili kapsamındaki kalan bütçe ve rezervasyon; işleri sıraya alma veya erteleme |
| Tahmin/capability/fiyat bilgisinin eksikliği | Unknown alanlar ve nedenleri; sınırlı örnek planı veya insan incelemesi. Bilinmeyen tüketim düşük risk sayılmaz |

Tek bir sabit “uzun prompt” eşiği yeterli değildir. Task/run/parent plan toplamı ve proje/workspace dönemi birlikte değerlendirilir. Yeni token, child veya run bütçeyi ve risk kontrolünü sıfırlamaz. Meşru büyük import kötü niyet etiketi almaz.

## Tahmin ve karar

Önerilen `TokenRiskAssessment`: job/task/parent plan kimliği, plan digest'i, kaynak manifest/revision, model/provider/config, estimator ve fiyat revision'ı, tahmini input/output ve diğer faturalama sınıfları, beklenen aralık, uygulanabilir üst sınır, retry/fan-out dahil toplam, actual + outstanding reservations, reason codes, confidence/unknown alanları, policy/authz revision ve assessed_at. Secret veya ham transcript içermez; assessment da kaynak ACL'sine tabidir.

Beklenen tüketim ile güvenli rezervasyon üst sınırı ayrı gösterilir. Cache indirimi kesin değilse üst sınırda varsayılmaz. Aynı token sınıfı iki kez sayılmaz; token sayısı ile para karıştırılmaz. Tahmin aralığı yalnız dayanak varsa üretilir; veri yoksa sayı uydurulmaz. Dış fiyat bilgisi yokken mevcut parasal hard-cap sessizce token-only moda çevrilmez.

| Sonuç | İşin ilerlemesi |
|---|---|
| `within_policy` | Mevcut izin/profil ve atomik bütçe rezervasyonu uygunsa olağan akış; yeni modal gerekmez |
| `requires_risk_approval` | Yüksek tahmini tüketim veya önemli belirsizlik var, fakat uygulanabilir sonlu sınır kurulabiliyor; yeni model dispatch'i onay bekler |
| `blocked` | İzin/bütçe yok, hard-cap aşılacak veya mevcut policy için güvenli üst sınır kurulamıyor; “yine de onayla” ile geçilemez. Planı sınırla ya da ilgili policy/izin değişimini ayrı yetkili akışta yap |

Eşikler sürümlü kurulum/workspace/proje policy'sidir: mutlak tahmini token/maliyet, kalan bütçenin payı, fan-out/retry, tahmin belirsizliği ve tüketim hızı. Task ayarı üst sınırları gevşetemez. Sayısal eşikler OPEN-12/16 ve pilot baseline ile seçilecek; bugün optimum değer seçilmiş değildir. İlk model dispatch'inden önce sonlu risk policy'si bulunur; eksik policy otomatik güvenli kabul edilmez.

## Kullanıcıya gösterilecek onay kartı

Kart; yapılacak işi, kaynak kapsamını, **neden riskli bulunduğunu**, beklenen tüketim/aralık veya unknown'u, onayla izin verilecek üst sınırı, retry/child dahil toplamı, mevcut harcama/rezervasyonu ve kalan bütçeyi gösterir. Tahminin hangi kısmının host/provider kontrolü dışında olduğu açıktır. Veriyi kimin göreceği ve bekleyen işler ayrıca görünür.

Seçenekler: **Bu planı belirtilen sınırla onayla / Kapsamı küçült / Aşamalı plan hazırla / Deterministik veya insan yolunu seç / Ertele / Reddet**. Bölmenin her zaman tasarruf sağlamadığı belirtilir; yeni planın context tekrarları dahil toplamı yeniden hesaplanır. Kapsam küçültme eksik coverage'ı gizlemez; daha ucuz model kalite kapısını atlayamaz. Task'ın amaç/AC değişikliği ayrıca ürün onayı gerektirir.

Sentetik örnek: “Tüm arşivi yeniden değerlendirmek, değişen kayıtları işlemekten daha fazla context gerektiriyor. Cache'in bir bölümü geçersiz. Önce aktif işlere bağlı kayıtları işleme seçeneği var; arşivin kalanı bekleyecek.” Gerçek ölçüm olmadan bu örneğe tasarruf yüzdesi veya fiyat eklenmez.

Tek owner pilotunda yetkili insan kullanıcı; ekipte ilgili proje/workspace için maliyet onayı yetkili insan karar verir. Agent/parent agent plan ve öneri sunabilir, bu ek insan onayını kendisine veremez. Genel task onayı, önceden seçilmiş hızlı profil, eski risk onayı veya sohbetten çıkarılmış “devam” metni yeni planın güvenilir onayı sayılmaz. Doğrulanmış UI/transport ve açık plan kapsamı gerekir.

## Onayın kapsamı, yeniden kontrol ve koşu sırasında risk

`TokenRiskApproval`: assessment/plan digest, task/parent job, kaynak ve model/config sınırları, izin verilen toplam token/maliyet/attempt/fan-out, geçerlilik süresi, approver identity, policy/authz revision, karar/gerekçe ve audit ref. Onay kartını açmak, cevap gelmemesi veya süre dolması onay değildir. Reddetme/erteleme kalıcı source/task kaydını silmez; yalnız önerilen pahalı yürütme bekler veya iptal edilir.

Onay sırasında uzun DB transaction tutulmaz. Dispatch öncesi güncel yetki, assessment/approval tazeliği ve üst sınırlar kontrol edilir; approval kapsamının kalan payı ile bütçe rezervasyonu atomik korunur. Aynı onayı iki worker veya duplicate command ikinci kez tam harcama hakkı gibi kullanamaz. Onaylanmış aynı batch'teki adımlar kapsam içinde kaldıkça tekrar sorulmaz; **onay tüketimi sınırlı bir planı kapsar, kalıcı sınırsız izin değildir**.

Kaynak/plan kapsamı, model, retry/fan-out sınırı veya onaylanan üst sınır değişirse yeniden assessment ve gerekli yeni onay hazırlanır. Aynı planın sadece actual usage güncellemesi kart yağmuru yaratmaz; kalan pay yeniden hesaplanır. Başka işler bütçeyi tüketmişse geçerli risk onayı olsa da dispatch bekler. İzin iptali/expiry/policy değişimi eski onayı bypass etmez; tam uygunluk tekrar doğrulanır.

Koşu sırasında her yeni çağrıdan önce actual + unknown rezervasyon + planlanan kalan tüketim değerlendirilir. Sapma, tekrar döngüsü veya ek kapsam yeni risk doğurursa **yeni dispatch durur**, checkpoint ve sonuçlar korunur; yeniden plan/review gerekir. Devam eden provider çağrısının anında durduğu veya ücretinin geri alındığı varsayılmaz. Timeout usage'ı `unknown` tutar; yeni onay önceki belirsiz tüketimi silmez. Durum `deferred` + `token_risk_approval_required` nedeni olabilir; completion/verification'dan ayrıdır.

Aynı plan/risk için yetkili kapsamda tek onay kartı ve sınırlı bildirim kullanılır. Reddedilmiş aynı plan tekrar tekrar önerilmez; anlamlı plan/policy değişimi veya kullanıcının yeniden istemesi yeni review açar. Audit geçmişi korunur; replay onay üretmez veya çağrı başlatmaz.

## Kontrol edemediğimiz tüketim

Bu kapı Decivora'nın başlattığı/yönettiği model ve diğer metered işleri durdurabilir. Harici coding host'un bağımsız reasoning, context, başka araç ve abonelik tüketimini kesin sınırlayamaz. MCP sonuç boyutu ve erişimi daraltılır; gözlemlenemeyen usage `unknown` kalır. Host durdurma desteği doğrulanmamışsa yalnız uyarı/öneri ve Decivora tarafındaki yeni işleri durdurma sözü verilir; tüm agent durmuş sayılmaz.

## Küçük teslimler ve kabul

T09d: P1 deterministik assessment + dispatch gate; T19b: güvenilir risk kartı ve sınırlı plan onayı; T24k: sentetik corpus ve izinli pilot. T08c/T21b bütçe rezervasyonunu, T21c parametre sicilini sağlar. Review UI hazır değilken yüksek riskli çağrı otomatik açılmaz. Yeni engine/servis gerektirmez; ENG-06/09 ve mevcut job/audit modüllerini tamamlar.

| ID | Planlanan gözlenebilir kabul |
|---|---|
| TRA-01 | Normal yetkili iş modal olmadan ilerler; yüksek riskli plan güvenilir onay olmadan sıfır model dispatch üretir |
| TRA-02 | Tespit için deterministik metadata/manifest yolu model çağırmaz; okuma izni olmayan kaynağı tahmin için almaz |
| TRA-03 | Child/run/token rotasyonu ve çok küçük parçaya bölme parent/dönem toplamını veya risk kapısını aşamaz |
| TRA-04 | Tahmin bilinmiyor veya hard-cap/izin eksik: unknown/blocked doğru gösterilir; onay tek başına bypass sağlamaz |
| TRA-05 | Plan/model/kapsam değişimi, expiry/revocation ve sahte agent approval eski onayla dispatch üretemez |
| TRA-06 | İki worker, double click ve retry onay hakkını çoğaltmaz; rezervasyon atomik; provider timeout tüketimi unknown kalır |
| TRA-07 | Koşu sırasında sapma/döngü yeni çağrıyı durdurur; checkpoint/source korunur, in-flight çağrı iptal edilmiş varsayılmaz |
| TRA-08 | Ertele/reddet/küçült/böl akışları task'ı completed yapmaz; coverage ve yeni toplam görünür; aynı plan bildirimi çoğalmaz |
| TRA-09 | Host toplamı gözlenemiyorsa unknown; garanti tasarruf/host stop iddiası yok; replay sıfır model çağrısı |
| TRA-10 | Kart neden, sınır, alternatif ve karar yetkilisini anlaşılır gösterir; başka tenant kaynak/usage sızmaz |

Senaryolar **planlı / not_run**. Ölçüm: tahmin sapması ve üst sınır ihlali, risk yakalama/yanlış uyarı, onay yükü, bekleme süresi, tekrar çağrı ve aynı kalite/coverage koşulunda actual tüketim. Tasarruf henüz ölçülmedi. Kabul edilen ihtiyaç kullanıcının bu tarihli talebidir; sınıflandırma, alanlar ve eşikler teknik öneridir. Mevcut Q03 gerçek veri/provider/bütçe kararı açık kalır.

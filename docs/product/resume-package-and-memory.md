# Bekleyen işi bulma, devam paketi ve hafıza yeterliliği

**2026-10-11 — Yapıştırılan konuşmadan derlenen öneri; uygulama ve pilot sonucu yok.** Kullanıcının metni farklı chat'lerde bağlam sürekliliği, hızlı işleme ve LLM hafıza sorununu soruyor; içindeki önceki assistant cevabı “unutulanlar + devam paketi”, Spike-1 ve iki düğme alternatifi öneriyor. Bu assistant önerileri kullanıcı tarafından kabul edilmiş yeni MVP/otomasyon kararı sayılmaz. Bu belge mevcut vizyonu ayrıntılandırır; [Spike-1 v1](../delivery/spike-1-v1.md) incelenebilir deney planıdır.

## 1. Hafıza ihtiyacını nasıl çözeceğiz?

Kalıcı kaynak kaydı tek başına modelin doğru devam edeceğini kanıtlamaz. Decivora, model dışındaki proje hafızasına doğru, güncel ve yetkili bilgiyi kaydedip gerektiğinde sınırlı context olarak vermeyi hedefler. Modelin kendi oturum/context sınırları devam eder; dış hafıza da capture açığı, hatalı çıkarım, eksik retrieval veya bayat karar nedeniyle başarısız olabilir.

| Problem | Önerilen kontrol | Kanıtlanması gereken |
|---|---|---|
| Oturumlar arasında bağlam eksikliği | Kalıcı source/event/record ve chat→task ilişkisi | İzinli kaynak/span geri getirilebiliyor mu? |
| Context'e bütün geçmişin sığmaması | İlgili task, karar, AC/DoD, delta ve kaynak pointer'ları | Kritik gerekçe eksik mi; paket boyutu sınır içinde mi? |
| Eski veya çelişen bilgi | Karar revision'ı, supersession, gerekçe grafiği ve pending impact | Yeni oturum eski planı yeniden uyguluyor mu? |
| Fikir/iş çıkarımında hata | Candidate, coverage, kaynaklı reconciliation ve insan review | Önemli işler kaçıyor mu, açıklama yanlış task oluyor mu? |
| Zehirli veya yetkisiz kaynak | Kaynak ≠ talimat; ACL, approval ve bounded araçlar | Transcript instruction'ı gerçek izin/onay gibi okunuyor mu? |
| Kaynak kaybı/retention/recovery | Receipt, gap, archive/purge ve tutarlı backup | Kaydın neresi erişilebilir; restore sonrası ne eksik? |

“Veritabanı unutmaz” garantisi kullanmayız. Kalıcı saklama ile erişilebilirlik, doğru seçme ve modelin bilgiyi kullanması ayrı ölçümlerdir. [Çoklu chat/lag](../architecture/multi-chat-and-processing-lag.md), [hafıza ömrü](../architecture/storage-memory-capacity.md) ve [token ekonomisi](../architecture/routing-token-economy.md) aynı çözümün parçalarıdır.

## 2. Unutulduğunu iddia etmeden adayları göstermek

İlk önerilen rozet: **“Son anlamlı ilerlemeden beri X süre geçti; güncel tamamlanma kanıtı yok.”** X kaynağa ve assessment zamanına bağlıdır. Heartbeat veya tekrarlı yorum anlamlı ilerleme sayılmaz; kayıt gelmemesi işin yapılmadığını kanıtlamaz. Coverage eksikse “bu kaynak kapsamındaki kayıtlarda kanıt bulunamadı” denir.

Liste aktif/yarım işler, açık instruction adayları ve çözümlenmemiş kararları ayrı gösterir. Ertelenmiş, iptal edilmiş, obsolete veya verified kayıtlar otomatik unutulan iş adayı olmaz. Owner'ı olmayan, erişim/karar bekleyen veya dışarıda devam eden işlerin nedeni görünür. Uyarı eşiği sürümlü policy ve pilotla seçilir; yaş tek başına öncelik veya gereksizlik değildir. [Öncelik sözleşmesi](priority-and-flow.md) blocker ve değer kapılarını korur.

Kart eylemleri: **Devam paketi hazırla / Ertele / Durumu incele / Gereksiz olduğunu öner**. Sonuncusu gerekçe/alternatif kullanım/AND-OR ilişkileri ve gerekli insan onayını ister. Bir düğme geçmiş bağlantıları silmez veya görevi kanıtsız kapatmaz. “Tamamlandı” iddiası için mevcut AC/DoD/evidence akışı kullanılır.

## 3. Devam paketinin içeriği

Önerilen `ResumePackage`: project/task kimliği, paket sürümü/digest ve oluşturma zamanı, izinli session/source span referansları, record/decision/AC/evidence revision'ları, coverage/gap/unknown, hedef araç için format ve token/byte tahmini. Paket gövdesi şu sıradadır:

1. Proje amacı ve seçili işin beklenen sonucu.
2. Kullanıcının izinli özgün isteği veya kaynaklı kısa özeti; alıntı açıkça untrusted kaynak metnidir.
3. Ne yapıldığı: kanıtlı sonuç, agent claim ve bilinmeyen durum ayrı. Mevcut artifact revision'ı ile eski kanıt karıştırılmaz.
4. Ne kaldığı: AC/DoD, blocker, bekleyen insan kararları ve izinler.
5. İlgili güncel onaylı kararlar; bunlara ters düşen eski yaklaşımın neden sona erdiği.
6. Yetki içinde önerilen next actionable ve yapmadan önce doğrulanacak dosya/kanıt/snapshot bilgileri.
7. Gerektiğinde hedefli açılacak kaynaklar; pakette olmayan bağlamın coverage sınırı.

Paket bağımsız anlaşılabilir bir çekirdek taşır. Kaynak pointer'ı alıcı araçtan erişilemiyorsa “erişilebilir” varsayılmaz; kritik bilgi eklenir veya `context_incomplete` denir. İlgisiz chat geçmişi ve sibling işler kopyalanmaz. Kritik karar/AC token limitine sığmıyorsa sessiz kesme yok: kapsam küçültme, review veya ek context gerektiği açıklanır. Test komutu ve transcript'teki shell talimatı otomatik execution yetkisi olmaz.

Önce deterministik şablon ve mevcut kaynaklı kayıtlar kullanılır. Yeni anlamsal özet/model çağrısı gerektiren seçenek açıkça belirtilir; bütçe/egress ve [token risk onayı](token-risk-and-approval.md) geçerlidir. Listeyi açmak veya paketi kopyalamak Decivora tarafında yeni LLM çağrısı gerektirmez. Hedef araca yapıştırınca oluşacak model tüketimini garanti sınırlayamayız.

## 4. Düğme seçenekleri ve izin

| Seçenek | İşlem ve doğrulama | Statü |
|---|---|---|
| A — Önizle ve kopyala | Paket önizlemesi; açık clipboard/export eylemi; pano yazımı başarısızsa seçilebilir metin/dosya fallback. Kullanıcı istediği araçta yapıştırır | İlk deney için önerilen; henüz kullanıcı varsayılan kararı değil |
| B — Host'a teslim et veya başlat | Ayrı host capability, hedef kimliği, proje/path, execution/egress ve maliyet kapsamı; teslim/başlangıç acknowledgment'ı | Gelecek seçenek; provider/CLI desteği ve izinler doğrulanmadan yok |

Bir “Başlat” tıklaması her komuta/repoya/model ücretine sınırsız izin vermez. Gösterilen somut kapsamın yetkili onayı ve güncel izin gerekir; ayrı execution kapıları korunur. Paket oluşturuldu, kopyalandı, hedefe teslim edildi, run başladı ve task verified oldu farklı durumlar olarak tutulur. Kopyalanması çalışmanın başladığı kanıtı değildir.

Kopyalama anında kaynak ACL, onaylı karar/AC snapshot'ı, pending impact ve paket tazeliği tekrar denetlenir. Değişmişse yeniden paket/önizleme gerekir. Kopyalandıktan sonra revocation'ın clipboard veya başka araca yapıştırılmış metni fiziksel olarak geri aldığı iddia edilmez. Paket export kapsamı ve asgari veriyi gösterir; secret veya yetkisiz kaynak içermez. Clipboard'a otomatik arka plan yazımı yoktur.

Blocked iş için paket engeli çözecek adımı önerebilir; hazır uygulama işi diye sunulmaz. Obsolete veya pending impact işte önce karar/uygulanabilirlik incelemesi hazırlanır. Kullanıcı eski planı tarihsel görmek istiyorsa açık historical etiketiyle sunulur; current paketle karışmaz.

## 5. Hafıza yeterliliği deneyi

Amaç: aynı görevin **temiz bir model oturumunda** güncel doğru noktadan devam edebilmesi. Deney planı [Spike-1 v1](../delivery/spike-1-v1.md) içindedir. Gerçek model çağrısı, hesap/chat açma, özel kaynak aktarımı veya dosya çalıştırma bu dokümanla yetkilendirilmez.

Golden corpus'ta en az şu türler planlanır: iki chat'te devam eden iş, yeni kararla eski planın değişmesi, done claim fakat kanıt yok, erteleme/blocker, eksik retrieval/erişilemeyen kaynak ve transcript injection. Yetkili insan önce beklenen next step/karar/AC ve yanlış devam örneklerini oracle olarak yazar. Yeni oturum eski history/hidden context almamalıdır; aksi halde koşul kirlenmiş olarak raporlanır.

Kontroller: aynı hedef/model/config ve koşullarda (a) yalnız özgün prompt, (b) paket, (c) izinli ve yeterli tam kaynak baseline'ı. C seçeneği context'e sığmıyorsa eşdeğer tam-kapsam koşulu olduğu iddia edilmez; uygulanamayan baseline ve gerekçesi yazılır. Model değişkenliği için tekrar sayısı/bütçesi pilot protokolünde belirlenir; tek güzel çıktı başarı kanıtı sayılmaz.

Ölçümler: gerekli karar/AC hatırlama, doğru next-action, eski kararın yeniden canlandırılması, kanıtsız done, yetki aşımı, eksik bağlamın fark edilmesi, kullanıcı düzeltme sayısı/süresi ve token/unknown usage. Paket kalitesi, çıkarım kalitesi ve alıcı modelin uyumu ayrı hata nedenleri olarak etiketlenir.

“Unutulan iş” precision/recall'u yalnız owner tarafından etiketlenmiş gözlenebilir örneklemde hesaplanabilir. Recall için listede hiç görünmeyen gerçek işlerin de oracle'da bulunması gerekir; yalnız gösterilen kartları puanlamak recall ölçmez. Ertelenmiş veya başka araçta bitmiş işi yanlış alarm olarak ayır. Önerilen 3–5 gerçek oturum yalnız küçük nitel pilot adayıdır; gerçek veri izni veya pazar genellemesi değildir. İki haftalık pilot da takvim/onay alınmış otomasyon değildir.

## 6. Planlı kabul senaryoları

| ID | Gözlenebilir kabul |
|---|---|
| RES-01 | Yaş/kanıt/coverage rozeti bilinen kayıtlara dayanır; expired/erteleme/iptal ile unutuldu etiketi karışmaz |
| RES-02 | İki chat'in kaynakları ve güncel task/AC/karar tek sınırlı pakette bulunur; gerekli eski ret/supersession gerekçesi korunur |
| RES-03 | Paket revision/ACL değişince copy öncesi stale/review olur; private özet veya kaynak başlığı sızmaz |
| RES-04 | Kopyala eylemi yeni LLM, shell, host run veya dış yazma başlatmaz; clipboard başarısızlığı açık fallback verir |
| RES-05 | Blocked/pending impact/unknown context'te uygulama başlamış/ready/verified iddiası yok; geçerli next-action veya soru görünür |
| RES-06 | Boyut sınırında kritik kaynak sessiz kesilmez; token/coverage ve alıcı erişim eksikliği açıklanır |
| RES-07 | Kaynak injection ve done claim testinde izin/kanıt ayrımı korunur; paket metni execution onayı üretmez |
| RES-08 | Kontrollü temiz oturum baseline kıyasında doğru next-step ve stale karar hatası ölçülür; örneklem/config/usage ve not_run dürüst raporlanır |

Senaryolar **planlı / not_run**. Mevcut F04/F08/F11/F13, KNO-01/02, APR-02, UX-02, CST-01/02 ve GOV kapsamını tamamlar; yeni engine veya tam vizyonun küçültülmesi değildir.

## Kaynak güvenilirliği ve açık seçim

Yapıştırılan metindeki Projects/Claude/Cortex/mai-mcp davranışları, rekabetin iki haftada ne yapacağı ve Spike-0 sonuçları bu görevde birincil kaynak/çalıştırılmış artifact ile doğrulanmadı; yeni benchmark sonucu olarak kaydedilmez. Bu repo main'inde 2026-10-11 kontrolünde Spike-0/Wedge-0 uygulaması bulunmadı. Ayrı bir deney varsa repo/artifact/revision ve raporuyla ayrıca tanıtılmalıdır.

İlk deney adı için “bekleyen iş + devam paketi” önerisi korunur. Mevcut MVP'yi “unutulanlar radarı” olarak yeniden tanımlamak ve B otomatik başlatmayı seçmek owner kararı ister. A önerisi düşük efor ve araç bağımsızlığı sağlar; devam kalitesi için kabul testi gerekir. [Q11 seçim kaydı](../delivery/decision-brief.md) öneriyi kabul edilmiş karar gibi göstermeden saklar.

## Konuşulan planı gerçekleşmiş saymama

[Konuşma→gerçekleşme sözleşmesi](intent-to-reality-gap.md), paketin karar, üretilen artifact, hedefe uygulama ve AC kanıtını ayrı taşımasını zorunlu kılar. “Dosyaları yükle” talimatı veya generated dosya uploaded sayılmaz; sessizlik kabul değildir. User reported, exact hedefte observed, test verified ve unknown ayrıdır. GAP-01–10, RES-01–08'i tamamlayan planlı senaryolardır. Daha çok reasoning gözlenmeyen dış işlemi kanıtlayamaz.

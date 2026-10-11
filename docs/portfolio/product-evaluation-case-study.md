# Decivora — ürün değerlendirme ve karar verme vaka çalışması

**2026-10-11 · Ürün keşfi ve teknik tasarım · Çalışma adı.** Decivora, AI ile yürütülen projelerde konuşulan fikirleri, insanın seçtiği kararları, yapılan işleri ve bunların kanıtını birbirine bağlamayı hedefliyor. İlk kullanıcı ürün sahibinin kendisi. Henüz çalışan ürün, kullanıcı pilotu veya ölçülmüş ticari sonuç yok. Marka uygunluğu doğrulanmadı.

Bu belge portföy ve ürün değerlendirme görüşmesi için ayrı bir giriş sağlar; README veya teknik gereksinimlerin yerine geçmez. Private repository bağlantısı erişimi olmayan okuyucuya açılmaz. Bu metnin yayımlanması ve repository görünürlüğünün değiştirilmesi ayrıca kararlaştırılmalı; burada yayın yapılmadı.

## İki dakikada proje

| Başlık | Açıklama |
|---|---|
| Problem | AI bir dosya veya iş öneriyor; insan konuşmaya devam ediyor. Sonraki oturum, önerinin seçilip seçilmediğini veya hedefe uygulanıp uygulanmadığını bilmiyor. Yeni kararlar eski işleri gereksiz bırakabiliyor; gecikmiş cevaplar açık sorulardan kopabiliyor |
| Hedef kullanıcı | İlk olarak birden fazla AI oturumuyla proje yürüten bireysel kullanıcı; sonra benzer kullanıcılar. Çok-agent ve ekip kullanımı tam vizyonda; pilot segmenti doğrulanmış pazar değildir |
| Kullanıcının yapmak istediği iş | Projeye döndüğünde “neye karar verdim, ne gerçekten yapıldı, ne bekliyor, neden ve sırada ne var?” sorularını tekrar bütün sohbetleri okumadan cevaplamak |
| Ürün hipotezi | Kaynaklı, karar farkındalıklı hafıza; hedef uygulama kanıtı ve açıklanabilir değişiklik etkisiyle yönetim yükünü azaltabilir |
| İlk doğrulama | Aynı senaryoda manuel takip, mevcut araçların uygun native ayarları ve izinli sınırlı Decivora prototipi; GAP/RES oracle, yanlış seçim/uygulama/verified, bağlama dönüş doğruluğu ve toplam yönetim süresi |
| Bugünkü çıktı | Kapsam, ayrı MVP, karar haritası, ADR önerileri, benchmark kaynakları, risk/ölçüm planı ve küçük uygulanabilir backlog |
| Bugünkü sınır | Ürün doğruluğu, token tasarrufu, kurulum kolaylığı, kullanım talebi ve rakibe üstünlük henüz ölçülmedi |

Kanıt: [güncel yön](../product/current-direction.md), [gerçekleşme boşluğu](../product/intent-to-reality-gap.md), [geç cevap örneği](../product/pending-questions-and-late-answers.md), [ölçüm planı](../quality/measurement.md).

## Ürün sahibinin rolü ve AI katkısı

Ürün sahibi problemi kendi kullanımından getirdi; kapsamın daraltılmamasını, MVP'nin ayrıca tutulmasını, geçmişin korunmasını, insan/agent yetkilerini, token maliyetini, kararların nedenlerini ve uygulanma kanıtını sorguladı. Pilot sırası, geçmiş işleme yaklaşımı, graph görünümü, kullanıcıya analiz profili seçimi ve çıktı dili gibi açık tercihleri yaptı. Ayrıntılı [soru/cevap kaydı](../delivery/decision-brief.md) bu kararları teknik önerilerden ayırır.

AI; araştırma, kaynak karşılaştırma, doküman düzenleme, teknik çözüm önerileri ve tutarlılık kontrolüne yardımcı oldu. Kaynak okumaları ve belgeleme kullanıcı kararı veya ürün testi yerine geçmez. Kullanıcının bu vakadaki katkısı **problem tanımlama, ürün değerlendirme ve karar sahipliğidir**; bütün teknik kodu kendisinin yazdığı veya çalışan ürünü teslim ettiği iddia edilmez.

## Problemin evrimi: özellik listesinden doğrulanabilir ürün tezine

| Öğrenme / tetikleyici | Ürün değerlendirmesi | Tasarımdaki karşılık | Kalan doğrulama |
|---|---|---|---|
| Oturumlar arasında AI önerileri kayboluyor | Sadece elle güncellenen Markdown kullanıcıya yeni iş çıkarıyor | İzinli kaynak capture, kalıcı kaynak referansı ve kısa devam paketi | Host erişimi ve gerçek kurulum T02; doğruluk T03b |
| Mimari değişince eski görev açık kalıyor | Task'ın varlığı kadar neden gerekli olduğu bilinmeli | Decision-aware gerekçe graph'ı; AND/OR/unknown, impact önerisi | Yanlış obsolete ve eksik/gizli edge oracle |
| Geniş vizyon erken daraltılıyor | İlk teslim ile nihai ürün farklı planlanmalı | Tam kapsam korunur; P1a/P1b, P2/P3/P4 ayrılır | Küçük ilk deney değer üretiyor mu? |
| AI “done” diyebiliyor; dosya henüz yüklenmemiş | Konuşulmuş/seçilmiş/istenmiş/uygulanmış/doğrulanmış ayrı eksenler | Artifact revision, exact target/ref/path, observation ve AC | GAP-01–10 ve fresh-session doğruluğu |
| Kullanıcı Q12-A cevabını sonra veriyor | Açık soru run/chat süresine bağlı olmamalı | Kalıcı Question/Answer; option snapshot, bağlama eşleme ve ambiguity review | LATE-01–08; host metadata kabiliyeti |
| Claude Projects ve WrongStack örtüşmesi görülüyor | Genel memory, graph, task ve verification tek başına özgün değil | Aynı fixture'da native/extension/build karşılaştırması; gerekirse yatırım yapmama seçeneği | T03b sonuçları; henüz üstünlük yok |

Bu sıra konuşmada gözlenen ürün gelişimini özetler; sonradan yapılmış yorum geçmişte alınmış karar gibi gösterilmez. [Evrim kaydı](../discovery/evolution.md) ve [karar haritası](../product/decision-map.md) ayrıntıları korur.

## Kritik tercihler, alternatifler ve bedeller

| Karar / statü | Alternatif | Tercihin nedeni | Bedel / yeniden değerlendirme koşulu |
|---|---|---|---|
| DEC-07 kabul: tam vizyon + ayrı MVP | Yalnız dar task tracker'a dönüşmek | Bilginin kaybolmasını önler; ilk teslim yine sınırlıdır | Belge/kapsam yükü; MVP gereksiz genişlerse faz sınırları gözden geçirilir |
| DEC-15 / Q07-1C kabul: izinli geçmişi aşamalı işle | Yalnız seçilmiş tarih aralığı; yalnız yeni konuşmalar | Eski gerekçeler bulunabilir; aktif iş önce gelir | İlk işleme/retention maliyeti; eksik kaynak coverage açık gösterilir |
| DEC-17 kabul: blocker ve ürün değeri önceliği | Yalnız FIFO veya task sayısı | Başka işleri açan uygulanabilir işi görünür kılar | Eksik graph yanlış ranking üretebilir; owner override ve açıklama gerekir |
| Q04 kabul: güncel işler + seçili bağlam ve tarihçe | Her tarihsel ilişkiyi ilk ekranda göstermek | İlk bakış sade; neden/olgunlaşma erişilebilir kalır | Tarihçenin keşfedilebilirliği ve erişilebilirlik test edilmeli |
| DEC-20 / Q12-A kabul: sabit proje çıktı dili | Her session diliyle otomatik değiştirmek | Karma konuşmalar ortak kayıt dilini sürekli değiştirmez | Dil değişimi ek insan seçimi; eski notlar otomatik çevrilmez |
| DEC-11/13 öneri: yerel servis, SQLite, TypeScript/React | Native araç, extension veya başka stack | İlk solo kullanım için aday; kaynak reuse seçenekleri var | Kabul edilmiş teknoloji değil. T03 kanıtı ve owner kararıyla değişebilir |

Kaynak yaklaşımları, bizim yorumumuz ve insan kabulü [karar gerekçe standardında](../product/decision-map.md) ayrılır. Blocker/dependency takibi yöntemden bağımsızdır; [yönetim planı](../delivery/project-management.md) Scrum Guide/Scrum Alliance kaynaklarını bizim tercihimize eşler. PMI veya Scrum uygunluk sertifikasyonu iddiası yoktur.

## Mevcut çalışmanın güçlü tarafları ve gerçek eksikleri

| Değerlendirme alanı | Mevcut kanıt / güçlü taraf | Eksik | Öncelikli kapatma yolu |
|---|---|---|---|
| Problem keşfi | Ürün sahibinin somut upload ve geç cevap örnekleri; kaynaklı şikâyet araştırması | Başka kullanıcıda sıklık, şiddet ve mevcut çözüm maliyeti bilinmiyor | İlk solo baseline; sonra benzer kullanıcı görüşmeleri ve karşı örnekler |
| Kapsam ve öncelik | 32 kapsam, 17 özellik, ayrı MVP ve 30 ana görev; dependency/AC planı | Belge kapsamı uygulanabilirlik kanıtı değil | T01→T02→T03; gerçek blocker'a göre küçük teslim |
| Rekabet | Birincil kaynak/issue incelemesi ve karşı kanıt | Aynı koşulda native kullanım ve runtime benchmark yok | Kurulum/ayar/maintenance dahil kontrollü karşılaştırma |
| Teknik düşünce | Claim/authority/evidence, replay/ACL/bütçe/retention sınırları | Adapter, DB, UI ve engine çalışmıyor | Bir source + exact target + taze oturum akışı; negatif oracle |
| UX | Review, graph, timeline, AC/test/unknown tasarımları | Tıklanabilir akış ve kullanıcı anlayışı ölçülmedi | Sentetik kısa UX örneği; yanlış yorum, adım ve review süresi |
| Ekonomi | Deterministik-first, dar context ve parent bütçe tasarımı | Token/host toplamı, işlem maliyeti ve ödeme isteği yok | Gözlenebilir toplam ek yük; kurulum+review+tekrar sorular dahil |
| Portföy anlatısı | Bu ayrı vaka çalışması ve kaynak bağlantıları | Bağımsız okuyucunun anlayıp anlayamadığı bilinmiyor | Okuyucuya problem/karar/kanıt/sıradaki iş soruları; sonuç kaydı |

Buradaki eksikler dokümantasyonla kapanmış sayılmaz. [Benchmark bulguları](../discovery/benchmark-findings.md), [kullanıcı araştırması](../discovery/user-research.md) ve [tamlık incelemesi](../quality/completeness-review.md) kanıt sınırını gösterir.

## Ölçüm ve yatırım kararı

Önerilen ilk deneyde aynı anlamlı iş için manuel takip ve uygun native araç ayarlarıyla baseline alınır. Kaynak/target/AC revision gold etiketi sistem sonucundan önce hazırlanır. Setup, izin/import, review/düzeltme, target kontrolü ve context aktarma süreleri birlikte ölçülür. Yanlış accepted/applied/verified ataması zorunlu sette sıfır hedefidir; evrensel garanti değildir. Görülemeyen host tüketimi veya uygulanamayan karşılaştırma null/not_run olarak kalır.

T03c'deki yatırım seçenekleri: native yeterli; küçük extension yeterli; küçük modül reuse ile özgün domain gerekir; ek deney gerekir; yatırım durdurulmalı. Sonuç olumlu çıkmak zorunda değildir. Daha çok belge veya feature üretmek kullanıcı değeri kanıtı olmaz. Eşikler, paydalar ve hata sınıfları [ölçüm planında](../quality/measurement.md); ana/alt görevler [backlog](../delivery/backlog.md) ve [faz görünümünde](../delivery/phase-tracker.md).

## Görüşmede gösterilecek dosyalar ve dürüst iddialar

1. Problem ve ilk ürün tezi: bu belge + [güncel yön](../product/current-direction.md).
2. Neden o kararlar: [karar haritası](../product/decision-map.md) + Q07/Q12 seçenekleri.
3. Teknik değerlendirme: [ADR dizini](../architecture/adr/README.md) + [kod/teknoloji değerlendirmesi](../discovery/code-reuse-assessment.md).
4. Teslim planı ve kalite: [fazlar](../delivery/phase-tracker.md) + [ölçüm](../quality/measurement.md).

CV için kullanılabilecek kapsam: **“AI-native proje hafızası için ürün keşfi ve teknik tasarım; problemden karar haritası, kaynaklı benchmark, MVP/backlog ve doğrulama planı oluşturma. AI destekli çalışma; geliştirme ve kullanıcı doğrulaması henüz başlamadı.”** Kullanıcı sayısı, teslim edilen ürün, gelir, token tasarrufu veya rakibe üstünlük yazılmamalı; bu sonuçlar mevcut değil.

Bir okuyucu bu repodan amacı, kullanıcının kararlarını, ürün sınırlarını ve sıradaki işi anlayabilmeli. Aynı okuyucu çalışan bir uygulama veya doğrulanmış iş modeli bulmayı beklememeli. Bu ayrım vaka çalışmasının değerlendirme gücünü artırır.

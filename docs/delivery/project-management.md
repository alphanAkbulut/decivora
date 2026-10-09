# Kısa proje yönetim planı

**Aşama: P0 — Discovery / Product Definition.** Ürün çalışmıyor. Amaç: AI konuşmalarını yaşayan, karar farkındalıklı hafızaya dönüştürmek; eskimiş işleri açıklanabilir biçimde yeniden değerlendirmek ve manuel yönetim yükünü azaltmak. Tam kapsam korunur; ilk kullanılabilir teslim P1b MVP'dir.

**Pilot kararı (2026-10-09):** önce owner'ın bireysel kullanımı; sonra benzer kullanıcılar. [Sorular/cevaplar](decision-brief.md) pilot erişimi ve bütçe sınırını izler. [Şikâyet araştırması](../discovery/user-research.md) görüşme akışını ve ürünü terk ettirebilecek riskleri; [benchmark bulguları](../discovery/benchmark-findings.md) ölçülmüş sonuç ile kaynak araştırmasını ayırır.

## Başarı ve teslim sınırı

İlk değer: bir mimari değişiklikte tek gerekçeli eski işi obsolete adayı yapmak, alternatif gerekçeli işi korumak, historical done'ı silmemek ve kullanıcıya hazır toplu onay sunmak. İlerleme belge/kod miktarıyla değil [MVP kabul kriterleri](../product/mvp.md) ve [ölçüm kapılarıyla](../quality/measurement.md) değerlendirilir.

| Rol | Sorumluluk / karar yetkisi |
|---|---|
| Product owner: kullanıcı | Ürün yönü, scope/öncelik, maliyet, public/lisans ve mimari trade-off kararları |
| Uygulayıcı: yetkilendirilmiş geliştirici/agent | Sıradaki küçük işi hazırlama/uygulama, seçenek ve kanıt sunma; kendine scope onayı veremez |
| Reviewer/verifier | AC ve invariant kontrolü; bir agent'ın kendi iddiasını bağımsız kanıt saymaz |

Bunlar görev rolleridir; kurulmuş ayrı bir ekip veya atanmış çalışan iddiası değildir.

## Faz ve karar kapıları

| Faz | Somut teslim | Devam etmek için gerekli kanıt |
|---|---|---|
| P0 | Corpus, gerçek adapter capability ve alternatif karşılaştırması | T01–T03; build/extend ve stack kararı |
| P1a | Import→impact→approval→event→verification teknik dilimi | T15; atomicity, isolation, false-done, graph race ve replay |
| P1b | İki coding adapter, minimal MCP, review/board/graph/timeline, temel ekonomi | T24; 14 AC, holdout ve kullanıcı pilotu |
| P2 | Chat sürekliliği, daha iyi semantik, GitHub read, panel | Platform/kalite kanıtı; fallback açık |
| P3 | Cost report, yetkili dış yazma, release hazırlığı | İzin, lisans, isim, kurulum/demo kanıtı |
| P4 | Takım/cloud/ticari sınırlar | Talep, isolation/sync tasarımı ve owner kararı |

Tarih ve bütçe henüz taahhüt edilmedi. Bağımlılık kapısını geçemeyen özellik full scope'ta kalır; sınırlı pilot diye adlandırılır. Güncel durumun otoritesi [status](status.md), uygulanabilir işin otoritesi [backlog](backlog.md).

## Çalışma ritmi

**Kabul edilen yön:** Product Owner bakışı, blocker/bağımlılık önceliği ve çevik değer teslimi. Kullanıcı ihtiyacı→beklenen sonuç→en küçük doğrulanabilir teslim→geri bildirim→uyarlama bağlantısı her anlamlı işte görünür olacak. Ayrıntılı [öncelik sözleşmesi](../product/priority-and-flow.md) yalnız sayı sırasına bağlı çalışmayı önler.

1. Her çalışma oturumunda hedef, status, aktif engel ve sıradaki hazır görevi oku. Önce ilerlemeyi açan uygulanabilir çözüm adımını değerlendir; dış engel beklerken hazır bağımsız işi ilerlet. Varsayılan WIP bir iş; büyük T02/T03 gibi satırları yüzey/deney bazında küçük alt dilimlere ayır.
2. Başlamaya hazır olma: bağlı görevler tamam, ilgili ADR kararı açık, input/fixture hazır, AC gözlenebilir, izin ve maliyet sınırı belli. Eksik karar varsa somut seçenek hazırla; alakasız iş başlatma.
3. Uygula: küçük değişiklik, ilgili sözleşme ve test. Aynı bulguyu yeni task olarak tekrar üretme. Fark edilen kapsam dışı işi öneri olarak kaydet.
4. Bitiş: AC kanıtı, ilgili regresyon, doküman/status güncellemesi, revision/sonuç kaydı ve gerekli remote doğrulama. `not_run` veya `unknown` başarı değildir.
5. Oturum sonunda kısa devir: ne değişti, hangi kanıt var, hangi risk/karar bekliyor, sonraki tek küçük adım. Faz sonunda go/no-go review; takvim hatırlatıcısı kendiliğinden kurulmaz.

## Scrum dayanağı ve bu projeye uygulama sınırı

### Kavram düzeltmesi: bağımlılıklar Scrum'a özgü değildir

**2026-10-10 açıklaması:** Önceki “Scrum Alliance bağımlılık yaklaşımı” ifadesi, bu genel yeteneğin Scrum'a ait olduğu anlamına gelmemeli. Görev bağımlılığı ve engel yönetimi farklı çalışma biçimlerinde kullanılabilir. Scrum Alliance makalesi, bunların Scrum ortamında nasıl ele alınabileceğine ilişkin dayanaklarımızdan biridir; kavramların tek kaynağı veya ürünümüzün zorunlu yöntemi değildir.

**Scrum** bir çalışma çerçevesidir. **PMI (Project Management Institute)** mesleki kuruluştur; tek bir rakip yöntem adı değildir ([PMI hakkında](https://www.pmi.org/about)). PMI'ın [A Spectrum of Approaches](https://www.pmi.org/learning/thought-leadership/series/achieving-greater-agility/spectrum-of-approaches) yayını öngörücü, yinelemeli, artımlı, çevik ve hibrit yaklaşımları birlikte ele alır. Dolayısıyla “Scrum mu PMI mı?” zorunlu bir ikili seçim değildir. Bu kaynak karşılaştırması genel yaklaşımı açıklamak içindir; belirli PMBOK sürümünün tüm maddelerine uyum analizi yapılmadı.

| Katman | Bu projede karşılığı | İddia sınırı |
|---|---|---|
| Yöntemden bağımsız ürün çekirdeği | Görev, karar/gerekçe, bağımlılık, engel, kaynak, değişiklik etkisi, onay ve kanıt | Bunları yalnız Scrum kullanıcısına bağlamıyoruz |
| Bizim geliştirme çalışma biçimimiz | Kullanıcının kabul ettiği ürün değeri odağı, küçük teslim, geri bildirim; Scrum kaynaklarından yararlanma | Formal Scrum ekibi/Sprint uygulanmış sayılmaz |
| Müşterinin çalışma yöntemi | Scrum veya öngörücü/hibrit süreçte aynı çekirdeği kullanma hedefi | Kullanım senaryolarında test edilmeden tam uyum/destek iddiası yok |

**Konumlandırma önerisi:** “Decivora, insan ve agent çalışmalarını kararlar, bağımlılıklar ve kanıtlarla ilişkilendiren; farklı proje yönetimi yaklaşımlarına uyarlanması hedeflenen AI-native proje hafızasıdır.” Bu öneri “Scrum ve PMI sertifikalı/uyumlu ürün” ifadesinin yerine geçer. Pazarlama metni veya yeni bir workflow motoru kararı olarak kabul edilmiş sayılmaz. Sprint, rol ya da süreç preset'lerini ürünün her kullanıcısına zorunlu kılmıyoruz; müşterinin karar yetkilisi kendi proje policy'siyle belirlenir. Bizim projede Product Owner kullanıcının rolüdür.

Bu açıklama DEC-17 blocker önceliğini veya mevcut yetki kurallarını değiştirmez; gerekçenin atfını düzeltir. PMBOK uyumu, kritik yol/Gantt hesaplama, kaynak dengeleme veya yeni Scrum/PMI modları bu turda kapsamımıza eklenmedi. Gelecekte belirli bir yönteme destek iddiası gerekiyorsa hedef süreç, somut senaryo ve kabul kanıtı ayrıca tanımlanır.

### Scrum'dan yararlandığımız çalışma yaklaşımı

[Scrum Guide 2020](https://scrumguides.org/scrum-guide.html) çerçevenin dayanağıdır: Product Owner ürün değerinden ve Product Backlog sırasından; Developers Sprint planından; Scrum Master çerçevenin etkin uygulanmasından sorumludur. Product Goal yönü, Sprint Goal dönem amacını, Definition of Done tamamlanma standardını tanımlar. Planning planı kurar, Daily Scrum ilerlemeyi uyarlar, Review sonucu inceler, Retrospective çalışma yöntemini iyileştirir. Sprint en çok bir aydır; değişiklik hedefi tehlikeye atmamalı ve kaliteyi düşürmemelidir. Hazır olma checklist'imiz Scrum'ın zorunlu ayrı bir artefaktı değildir.

[Scrum Alliance bağımlılık rehberi](https://resources.scrumalliance.org/Article/managing-dependencies-scrum) teknik bağımlılıkların Product Owner'a görünür kılınmasını, ürün backlog sırasının buna göre değerlendirilmesini ve sprint içi task koordinasyonunun uygulayıcılarda olmasını anlatır. Bağımlılıkları azaltma seçeneğini de ele alır. [Product Owner sorumlulukları](https://resources.scrumalliance.org/Article/im-new-product-owner-responsibilities) kullanıcının ihtiyacı, ürün vizyonu ve değer odağını destekler. Bu makaleler uygulama rehberidir; sertifika/uygunluk denetimi değildir. Kaynaklar 2026-10-09'da incelendi.

**Decivora için çalışma uyarlaması:** Şimdilik bireysel pilot ve yetkili agent desteği var; ayrı Scrum Team/Scrum Master veya başlamış Sprint yok. Bu yüzden mevcut düzen Scrum'dan yararlanan çevik çalışma olarak adlandırılır. Formal Scrum'a geçerken sorumlular, sabit dönem ve etkinlik düzeni birlikte belirlenir; takvim veya toplantı bu dokümanla yaratılmaz.

| Çalışma öğesi | Şimdi uygulanacak karşılık |
|---|---|
| Ürün hedefi | İlk owner pilotunda karar değişiminin gereksiz işi açıklaması, hâlâ gerekli işi koruması ve yönetim yükünün ölçülebilmesi |
| Yakın dönem öğrenme amacı | T01–T03 kanıtlarıyla uygulanabilir capture ve build/extend kararını hazırlamak; P0 belgesi çalışan ürün Increment'i sayılmaz |
| İş seçimi | Hedefe katkı, kullanıcı sonucu, blocker etkisi, risk, kanıt ve uygulanabilirlik. Önce engeli çöz; bağımlılık yoksa küçük değerli dilimi seç |
| Oturum kontrolü | Hedefe ilerleme, yeni engel, değişen varsayım ve sıradaki uygulanabilir adım. İnsanlara durum toplantısı dayatılmaz |
| Teslim incelemesi | Çalışan çıktı varsa demo + AC/DoD/kanıt; discovery'de sonuç ve sınırı. Owner geri bildirimi backlog/karar geçmişine bağlanır |
| Süreç iyileştirme | Tamamlanan anlamlı dilim sonunda bir somut iyileştirme adayı ve takip ölçüsü; daha çok doküman/kart üretmek başarı ölçüsü değil |

Mevcut T01–T30 sırası başlangıç teslim planıdır. Refinement sırasında gerçek teknik gate, politika/izin gate'i ve yalnız planlama sırası ayırt edilir. Kanıt olmadan sırayı kaldırma veya bütün gelecekteki işleri bugünkü blocker sayma. Yeni öneri hedefi/scope'u değiştiriyorsa owner kararı gerekir; onaylı kapsam içindeki rutin teknik planlama uygulayıcılarda kalır. Gereksiz bağımlılığı azaltmak da çözüm adayıdır. Product Owner sorumluluğu AI'ya devredilmiş sayılmaz.

## DEC-17 — Kaynak yaklaşımı → tercih → gerekçe

**Karar sahibi:** kullanıcı/Product Owner. **Tarih:** 2026-10-09. **Tetikleyici:** kullanıcının Q09 yanıtında blocker ve başka işleri geciktiren bağımlılıkların önceliğini, ürün bakışını ve Scrum Alliance yaklaşımından yararlanmayı istemesi. **Statü:** bu yön kabul edildi; öncelik hesabı/UX teknik öneri, çalışma düzeni bireysel pilot uyarlamasıdır.

Bu ayrıntılı kaynak–gerekçe eşlemesi 2026-10-10'da kullanıcının açıklık talebiyle eklendi; önceki karar tarihi değiştirilmedi.

Kararın başlangıcı kullanıcı ihtiyacıdır. Ardından Scrum kaynaklarıyla sorumluluk ve çalışma yaklaşımı kontrol edilmiştir; kaynak incelemesinin kullanıcı kararından önce yapıldığı veya kaynağın algoritmamızı zorunlu kıldığı iddia edilmez.

| Baz alınan yaklaşım / doğrudan kaynak | Bizim tercihimiz | Neden / sınır | Doğrulama veya yeniden değerlendirme |
|---|---|---|---|
| Scrum Alliance [Managing Dependencies in Scrum — Intra-team dependencies](https://resources.scrumalliance.org/Article/managing-dependencies-scrum): teknik bağımlılıkları görünür kılma, backlog sırasını değerlendirme | Engellenmiş işi tekrar denemek yerine ilerlemeyi açan işi/kararı öner; gerekçe yolunu göster | Kullanıcının diğer işlerin gecikmesini azaltma ihtiyacını karşılar. Salt downstream sayısı bizim için yeterli değer ölçüsü değildir | FLOW-01–04/07; yanlış ready, bekleme ve owner override gerekçeleri |
| Aynı [Scrum Alliance rehberi](https://resources.scrumalliance.org/Article/managing-dependencies-scrum): sprint içi task koordinasyonunu uygulayıcıların yapması | Ürün sırası/scope kullanıcıda; izinli teknik sonraki adımlar uygulayıcıda | Her küçük teknik adım için owner'ı bekletmeden kontrolü korumak. Agent grant'i insan onayına dönüşmez | FLOW-05/06; eski onay, scope ve izin sınırları |
| Scrum Alliance [Product Owner Responsibilities — Defining the Vision / Prioritizing Needs](https://resources.scrumalliance.org/Article/im-new-product-owner-responsibilities): vizyon ve değer odağı | İş seçiminde kullanıcı sonucu, mevcut hedef ve risk açıklaması | Kart/puan sayısını başarı saymak ürünün manuel yönetim yükünü azaltma amacını kaçırabilir | Yönetim yükü, doğrulanmış kullanıcı çıktısı ve pilot geri bildirimi |
| [Scrum Guide — Inspection / Adaptation](https://scrumguides.org/scrum-guide.html#inspection): gözlemle inceleme ve uyarlama | Küçük doğrulanabilir teslim, sonuç incelemesi ve somut süreç iyileştirmesi | Yanlış varsayımı erken görmek; P0 araştırma çıktısını çalışan ürün diye göstermemek | T01–T03 kanıt kapıları; teslim sonu AC/DoD ve sonraki karar kaydı |

**Bedeller:** ilişki/kanıt güncel tutulmalı; eksik coverage doğru sıralamayı sınırlayabilir; sürekli yeni acil iş odak kaybı yaratabilir. Bu yüzden unknown, bekleme yaşı ve öncelik değişiminin gerekçesi görünürdür. Hazırlanmış öneri kabul edilmiş planı sessiz değiştirmez.

**Bu turdaki karşılaştırma:** yalnız geliş sırasıyla ilerlemek bağımlılık etkisini kaçırabilir; yalnız bağlantı sayısıyla ilerlemek düşük değerli işleri öne çıkarabilir; her değişimde planı otomatik değiştirmek odağı bozabilir. Bunlar mevcut kararın açıklayıcı değerlendirmesidir; geçmişte kullanıcıya ayrı seçenek olarak sunulduğu iddia edilmez. Seçilen yön, blocker etkisini ürün hedefi/değeriyle birlikte değerlendirmektir; kesin puanlama formülü seçilmedi.

**Uyarlama sınırı:** WIP=1, bireysel oturum kontrolü, agent yetkileri, FLOW algoritması ve onay UX'i Decivora tercihidir; Scrum Alliance'ın zorunlu reçetesi değildir. Formal Sprint takvimi/roller henüz yoktur. Ekip pilotunda sorumlular ve ritim; bireysel pilotta yanlış öncelik, bekleme ve yönetim yükü sonuçları bu kararı yeniden değerlendirme girdileridir. Kaynaklara referans vermek tam Scrum uyumu/sertifikasyonu kanıtlamaz.

## Değişiklik kaydı ve riskler

Yeni fikir → mevcut scope/kararla karşılaştır → delta ve etki → gerekiyorsa owner onayı → ADR/scope/backlog birlikte güncelle. Eski karar ve görevi silerek geçmişi yeniden yazma. Öncelikli riskler: kaynak erişimi, yanlış obsolete/verified, capture kaybı, onay yorgunluğu, token maliyeti ve lisans. Ayrıntılar [risk kaydında](../governance/risks.md); bekleyen seçimler [açık kararlarda](../governance/open-decisions.md).

**Sıradaki üç iş:** T01 sentetik corpus ve oracle; T02 Claude Code/Codex yüzeylerini izole fixture'da gözlemleme; T03 Cortex/Tracker/mai-mcp/Beads alternatiflerini aynı senaryoda karşılaştırıp build/extend kararı hazırlama. Doküman denetiminin tamamlanması bu üç işi yapılmış saydırmaz.

## Ekip/veri hattının yönetimi

[Team/data plan](team-data-plan.md) P1 temellerini ve P4 ekip dilimlerini ana backlog'a bağlar. Owner ürün policy/retention/hosting kararını; uygulayıcı izin/log/migration kanıtını hazırlar. “Belgelendi”, “uygulandı” ve “MU senaryosu geçti” ayrı durumlar olarak raporlanır. İlk pilotun bireysel kullanım kararı korunur; ücretli servis veya yeni dış bağlantı belge yazımıyla onaylanmış sayılmaz.

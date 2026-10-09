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

## Değişiklik ve risk uygulaması

Yeni fikir → mevcut scope/kararla karşılaştır → delta ve etki → gerekiyorsa owner onayı → ADR/scope/backlog birlikte güncelle. Eski karar ve görevi silerek geçmişi yeniden yazma. Öncelikli riskler: kaynak erişimi, yanlış obsolete/verified, capture kaybı, onay yorgunluğu, token maliyeti ve lisans. Ayrıntılar [risk kaydında](../governance/risks.md); bekleyen seçimler [açık kararlarda](../governance/open-decisions.md).

**Sıradaki üç iş:** T01 sentetik corpus ve oracle; T02 Claude Code/Codex yüzeylerini izole fixture'da gözlemleme; T03 Cortex/Tracker/mai-mcp/Beads alternatiflerini aynı senaryoda karşılaştırıp build/extend kararı hazırlama. Doküman denetiminin tamamlanması bu üç işi yapılmış saydırmaz.

## Ekip/veri hattının yönetimi

[Team/data plan](team-data-plan.md) P1 temellerini ve P4 ekip dilimlerini ana backlog'a bağlar. Owner ürün policy/retention/hosting kararını; uygulayıcı izin/log/migration kanıtını hazırlar. “Belgelendi”, “uygulandı” ve “MU senaryosu geçti” ayrı durumlar olarak raporlanır. İlk pilotun bireysel kullanım kararı korunur; ücretli servis veya yeni dış bağlantı belge yazımıyla onaylanmış sayılmaz.

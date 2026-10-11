# Ölçüm ve pilot kapıları

**Tüm sayısal hedefler önerilen pilot eşikleridir, gerçekleşmiş sonuç değildir.** Eşikler P0 baseline sonrası owner ile güncellenebilir; sonuç bilindikten sonra başarısızlığı saklamak için değiştirilmez.

| Metrik | Tanım / payda | İlk pilot hedefi |
|---|---|---|
| Capture recall | Doğru bulunan anlamlı gold kayıt / tüm gold anlamlı kayıt | ≥ %90 toplam; tür bazında ayrıca rapor |
| Capture precision | Doğru anlamlı capture / tüm oluşturulan capture | ≥ %90 |
| False capture rate | Yanlış veya anlamsız capture / tüm capture | ≤ %10; duplicate ayrı kırılım |
| State accuracy | Doğru state ekseni/revision değerlendirmesi / tüm etiketli state | ≥ %95; unknown'u gizlemeden |
| False verified | Kanıtsız veya kriteri karşılamayan verified / tüm verified | Zorunlu sentetik güvenlik setinde 0 |
| Obsolete precision | Gold'a göre doğru obsolete adayı / tüm obsolete adayları | ≥ %95; confidence interval ve n |
| Harmful auto-closure | Yetkisiz veya geçerli gerekçeli işi otomatik kapatma | Tüm zorunlu suite'te 0 |
| Impact recall | Doğru bulunan etkilenen kayıt / tüm gold etkilenen kayıt | ≥ %90; eksik-edge fixture ayrı |
| Traceability coverage | Kaynak/gerekçe/karar zinciri olan kabul edilmiş task / tüm kabul edilmiş task | ≥ %95; eksikler inbox'a |
| Management overhead | Yönetim dakikası / çalışma saati; tıklama ve manuel metin ayrı | Manual baseline'a göre ≥ %50 azalma hipotezi |
| Token overhead | Capture/eval/tool schema/brief/retry toplamı / anlamlı event | Önce baseline; kalite eşitliğinde iyileşme |
| Capture latency | Durable ingest→review-ready süresi p50/p95 | İlk hedef p95 ≤ 60 sn; offline ayrı |
| Reliability | Tekrar/çökme sonrası kayıp ve duplicate domain effect | Fault suite'te 0 |
| False-stale approval | Yeniden hesaplanınca semantik sonucu değişmeyen stale proposal / tüm stale proposal | Önce baseline; kaba graph revision kontrolünün UX maliyeti ölçülür |
| Review backlog age | Açık PendingDecision/ChangeSet yaşının p50/p95'i; deferred ayrı | Önce baseline; bildirim sayısı ile birlikte yorumla |
| Ready precision | Gold'a göre gerçekten hazır önerilen task / tüm ready önerileri | Zorunlu pending-impact/unknown fixture'da yanlış ready 0 |
| Processing health | Oldest queued age, gap sayısı, quarantine ve retry / kaynak türü | Limit ve alarm eşikleri T06/T24 baseline sonrası; healthy tek puana indirgenmez |
| No-op doğruluğu | Gold'a göre yeni task gerektirmeyen input'ta task üretmeyen sonuç / tüm no-op input | Başlangıç baseline; meaningful capture recall ile birlikte raporla |
| İlk değere ulaşma | İzinli temiz kurulum başlangıcı → doğru kaynaklı ilk yararlı review | Önce baseline; başarısız kurulumlar ve recovery zamanı dahil |
| Yeniden bağlam kurma | Projeye dönüş görevi süresi + aktif karar/next action doğruluğu | Manuel yöntemle eş görev; hız uğruna yanlış karar gösterme kabul edilmez |

Farklılaşma hipotezlerinin deney karşılığı [H1–H6 tablosunda](../product/differentiation.md). Etiketleyiciler false-stale/ready gold sonucunu sistem çıktısından bağımsız belirler. Bu ek metrikler için sayısal ürün SLA'sı henüz yoktur.

Takip araştırmasındaki [UR-01–07](../discovery/user-research.md), no-op, onboarding ve yeniden bağlam kurma ölçümlerini gerekçelendirir. Bunlar yeni ürün kapsamı değil, mevcut CAP/KNO/UX/CST davranışlarının kullanıcı maliyetini görme yoludur. Mevcut araçların güncel profile/fix seçenekleri baseline'a dahil edilir.

## Deney tasarımı

En az 6 sentetik oturum ve 30 anlamlı kayıtla başla; no-op mesaj, belirsiz fikir, ret, partial work, false done, AND/OR, aynı adlı proje ve geri dönen prompt içersin. Gold etiketleri model tahmininden önce hazırlanır. Train/tune ile holdout source oturumu bazında ayrılır; aynı konuşma iki sete sızmaz. İkinci insan etiketleyici yoksa tek etiketleyici sınırlaması raporlanır.

Başlangıç küçük örneklemi pazar veya genellenmiş doğruluk kanıtı sayma. Sonraki pilotta açık izinli gerçek oturumlar anonimleştirilir; iki değerlendirici anlaşmazlığı kaydeder ve ortak gold üretir. Gerçek kullanıcı projesini izinsiz pilotlaştırma.

Manual tracking, full-context LLM ve Decivora hedefli context aynı anlamlı görevle karşılaştırılır. İzin veriliyorsa araç sırası değiştirilir; öğrenme etkisi ve kurulum süresi ayrı kaydedilir. Model/provider/prompt/engine sürümü, fiyat tarihi, donanım, sample size, latency ve retry dahil edilir. UI onay süresi maliyet hesabının parçasıdır.

Precision paydası sıfırsa metrik N/A olur, %100 yapılmaz. Unknown kaynak kapsamı recall'da “yakalandı” sayılmaz; erişilebilir gold ve tüm beklenen kaynak coverage ayrı raporlanır. Tasarruf iddiası eş kalite altında karşılaştırmalı ölçüm olmadan yayınlanmaz.

## Ürün değeri ve blocker akışı

[Öncelik sözleşmesi](../product/priority-and-flow.md) için T24d raporu: blocker kaydı→çözüm süresi; gerçek blocked süre/aktif iş süresi; çözüm sonrası gerçekten hazır olan işler; hedefe katkılı doğrulanmış çıktı; yanlış blocker/ready; owner sıra override gerekçeleri; tekrar bildirim; uzun bekleyen işlerin yaşı. Çözülememiş kayıtlar atılmaz, mevcut yaşlarıyla ayrıca raporlanır. Başlangıç/bitiş gate'i ve dış bekleme ayrıdır; bunlar kişi performans puanı değildir.

FLOW-01–08 oracle'ı zincir, elmas, ek gate, gizli/eksik graph, eski onay ve dış engel içerir. Zorunlu sette kanıtsız ready sıfır olmalı; hız veya tasarruf baseline olmadan vaat edilmez. Tamamlanan task/puan sayısı kullanıcı değerinin yerine geçmez. Bireysel pilot ekip verimliliği kanıtı sayılmaz. Kontroller planlıdır.

## Gate değerlendirmesi

P1a: invariants ve sentetik güvenlik suite'i. P1b: AC-01..14, iki adapter raporu, holdout ve UX pilotu. Her kritik yanlış kapanış, çapraz proje sızıntısı veya log veri kaybı release blocker'dır. Eşikler tutmazsa hata sınıfı ve sonraki küçük iş açılır. Tekil kullanıcı pilotu ödeme isteğini kanıtlamaz; P3/P4 için ayrı talep görüşmeleri gerekir.

## Ekip ve depolama ölçümleri

[Storage kapasite planındaki](../architecture/storage-memory-capacity.md) workload/ortam protokolüne göre DB read/commit p50/p95, writer wait, queue büyümesi, WAL/disk alanı ve backup/restore süresi ölçülür. Sayısal başlangıç eşikleri kalibrasyon hedefidir; baseline yok. Yetki revocation sonrası yanlış servis edilen kayıt/egress sayısı sıfır olmalı; negatif oracle MU01–MU07 ile değerlendirilir. Cache invalidation ve stale approval kaynaklı kullanıcı yükü de ölçülür.

Retention UI'sında kullanıcı hangi içeriğin kalacağını/kimle paylaşılacağını doğru anlıyor mu, expired raw kaynak kaç review'u engelliyor, dedup yeniden öneri oranı artıyor mu soruları T24b pilot çıktısıdır. Ekipte grant yönetimi/onay bekleme süresi, offboarding tamamlanma ve tenant başına iş bütçesi C06'ya eklenir. Bunların hiçbiri bugün ölçülmüş sonuç değildir.

## Token ve graph deney paketi

[TOK kabul planı](../architecture/routing-token-economy.md) aynı corpus ve kaliteyle full-context baseline karşılaştırmasını; host toplamının bilinmediği durumda yalnız gözlenebilen ek yükün raporlanmasını tanımlar. Cache write/read ve reasoning sınıfları provider'a göre eşlenir. Graph yükleme/filtre/zoom model çağrı sayısı sıfır olmalı.

[GUX senaryolarında](../product/graph-experience.md) kullanıcıya sentetik iptal/obsolete/verified ve ended/invalidated ilişki örnekleri verilir; “ne oldu, neden oldu, ne hâlâ gerekli?” cevapları, yanlış yorum sayısı ve açıklamaya ulaşma adımları ölçülür. Q04 tercihine göre başlangıç görünümü değişebilir; tarihçe ve erişilebilirlik kabulü korunur. Sonuç yoktur.

## Güncel ilk değer kapısı — GAP/RES ve native kıyas

[Tasarım revizyonu 03](../product/current-direction.md), geniş MVP metriklerini kaldırmaz. İlk deney [GAP-01–10](../product/intent-to-reality-gap.md) ve [RES](../product/resume-package-and-memory.md) üzerinde şunları birlikte raporlar:

- Yanlış accepted/uygulandı ataması: gold'a aykırı atamalar / tüm adoption/application değerlendirmeleri; false-positive ve kaçan belirsizlik ayrı.
- Hedef doğruluğu: exact repo/ref/path/artifact revision, partial bundle, unknown/stale; application observation acceptance başarıyla karıştırılmamalı.
- Yeni oturumda current karar/uygulama bilinmeyeni/next-action doğruluğu; typed input veya paket kısa olması gerçek extraction/host kullanım başarısı değildir.
- Yönetim süresi: setup + izin/import + durum kontrolü + review/düzeltme + context aktarma; yalnız düğme tıklama süresi alınmaz.
- Tekrar soru, model tokenı, adapter/API istekleri ve maintenance/setup yükü; bilinmeyen değer null/not_run.

Aynı senaryo native Projects ve izinli Decivora prototipte uygun desteklenen ayarlarla karşılaştırılır; bağlı target ile manuel/providerlar arası koşul ayrı raporlanır. Model ve dataset kontrolü, paket/full-source contamination ve reviewer oracle bağımsızlığı korunur. Zorunlu sette yanlış seçildi/uygulandı/verified ataması 0 kabul hedefidir; genellenmiş garanti değildir.

T03c yatırım kararı olumlu sonuç çıkarmak zorunda değildir. Native yeterli veya maintenance faydayı aşıyorsa integration/native/durdur önerisi kanıtlı sonuçtur; account/izin yoksa not_run, rekabet üstünlüğü unknown. Henüz hiçbir sonuç ölçülmedi.

## Uygulanabilir teknik ölçüm protokolü

[Karar→etki→gerçekleşme protokolü](evaluation-protocol.md) yukarıdaki eşikleri değiştirmeden frozen oracle, entity/span matching, stage/checkpoint scoring, exact target read-back, run manifest, evaluation_error/incomplete ve fair baseline'ı ayrıntılandırır. [Tek zincir örneği](../../examples/decision-impact-evaluation-case.json) yedi checkpoint ve dört izole negatif varyant içerir; illustrative/not_run, corpus veya çalışan harness değildir. T01f/T03f/T24p uygulanacak küçük işlerdir. Doküman/veri kontrolü ürün ölçüm sonucu sayılmaz.

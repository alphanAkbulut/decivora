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

## Deney tasarımı

En az 6 sentetik oturum ve 30 anlamlı kayıtla başla; no-op mesaj, belirsiz fikir, ret, partial work, false done, AND/OR, aynı adlı proje ve geri dönen prompt içersin. Gold etiketleri model tahmininden önce hazırlanır. Train/tune ile holdout source oturumu bazında ayrılır; aynı konuşma iki sete sızmaz. İkinci insan etiketleyici yoksa tek etiketleyici sınırlaması raporlanır.

Başlangıç küçük örneklemi pazar veya genellenmiş doğruluk kanıtı sayma. Sonraki pilotta açık izinli gerçek oturumlar anonimleştirilir; iki değerlendirici anlaşmazlığı kaydeder ve ortak gold üretir. Gerçek kullanıcı projesini izinsiz pilotlaştırma.

Manual tracking, full-context LLM ve Decivora hedefli context aynı anlamlı görevle karşılaştırılır. İzin veriliyorsa araç sırası değiştirilir; öğrenme etkisi ve kurulum süresi ayrı kaydedilir. Model/provider/prompt/engine sürümü, fiyat tarihi, donanım, sample size, latency ve retry dahil edilir. UI onay süresi maliyet hesabının parçasıdır.

Precision paydası sıfırsa metrik N/A olur, %100 yapılmaz. Unknown kaynak kapsamı recall'da “yakalandı” sayılmaz; erişilebilir gold ve tüm beklenen kaynak coverage ayrı raporlanır. Tasarruf iddiası eş kalite altında karşılaştırmalı ölçüm olmadan yayınlanmaz.

## Gate kararı

P1a: invariants ve sentetik güvenlik suite'i. P1b: AC-01..14, iki adapter raporu, holdout ve UX pilotu. Her kritik yanlış kapanış, çapraz proje sızıntısı veya log veri kaybı release blocker'dır. Eşikler tutmazsa hata sınıfı ve sonraki küçük iş açılır. Tekil kullanıcı pilotu ödeme isteğini kanıtlamaz; P3/P4 için ayrı talep görüşmeleri gerekir.

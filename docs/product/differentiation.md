# Farklılaşma tezi ve karşılaştırma deneyi

**Tez:** Decivora, AI çıktılarının yalnız hatırlanmasını değil, onları doğuran karar değiştiğinde hangilerinin hâlâ geçerli olduğunu açıklamayı hedefler. Ürün sözleşmesi: **yakala → uzlaştır → gerekçeye göre etki çıkar → hazır onay → kanıtla doğrula**. Tek bir özelliğin icadı veya kanıtlanmış pazar üstünlüğü iddiası değildir.

En güçlü demo “bir task oluşturduk” olmayacak: mimari değişirken gereksiz işi bulmak, alternatif gerekçesi kalan işi korumak, eski başarıyı silmemek ve bütün bunları kullanıcıya kart yazdırmadan yaptırmak olacak.

## Referanslarla somut fark hedefi

Aşağıdaki karşılaştırma doküman incelemesine dayanır. **Rakipte bulunmadığı gösterilmemiş hiçbir yeteneğe yok demiyoruz.** Tam kaynak/kanıt statüsü [benchmark matrisinde](../discovery/benchmark.md). Yakın dört kaynağın ana sayfaları 2026-10-09 yeniden incelendi; runtime testi yapılmadı.

| Referans | Öğrendiğimiz / örtüşen alan | Decivora'da sınayacağımız ilave sözleşme |
|---|---|---|
| [Beads](https://github.com/gastownhall/beads) | Görev hafızası ve dependency graph | Yürütme bağımlılığına ek olarak Decision/Requirement gerekçeleri, AND/OR/unknown ve açıklanmış obsolete önerisi |
| [Task Master](https://github.com/eyaltoledano/claude-task-master) | Gereksinimden uygulanabilir küçük işler üretmek | Yeni sohbet/karar geldikçe mevcut planı yeniden değerlendirmek; gereksiz task sayısını ve manuel düzeltmeyi ölçmek |
| [Linear](https://linear.app/docs/mcp) | Proje/issue erişimi ve olgun çalışma yüzeyi | Kaynak konuşmadan hazır change set ve etki review; insanın başlık/AC yazma süresini azaltmak |
| [Claude Task Tracker](https://github.com/ProblemFactory/claude-task-tracker) | Hook tabanlı pasif görev çıkarımı | Task dışı prompt/decision/document instruction lineage, çoklu gerekçe ve kanıta bağlı geçerlilik |
| [Cortex](https://github.com/gsl0001/Cortex) | Kalıcı yerel hafıza, typed provenance, bütçeli context, kontrol merkezi ve evidence içeren kayıtlar | Bu alanları farklılık diye saymamak; değişen karar→task etkisini aynı corpus ve onay/race koşullarında karşılaştırmak |
| [mai-mcp](https://github.com/maikai-group/mai-mcp) | Search-before-write, extends/supersedes, review ve bounded retrieval | Knowledge evolution yakınlığı nedeniyle öncelikli alternatif; AND/OR gerekçe, geçmiş completion ve approval freshness deneyinin sonucuna göre extend seçeneğini değerlendirmek |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) | Proposed change/current spec ayrımı | Spec deltasını task, prompt, execution ve evidence'a bağlayan otomatik impact ve source capture |
| [BeadSpec](https://github.com/boardthatpowder/BeadSpec) | Spec/task ilişkileri ve insan kuyruğu | Karar review'sunu passive capture ve kaynak/evidence zinciriyle birleştirmek |
| [Beads Dashboard](https://github.com/alexgorbatchev/beads-dashboard), [Scotty](https://beadmeupscotty.com), [beads-web](https://github.com/AvivK5498/beads-web) | Board/graph/çok proje görsel katmanı | Görsel karttan karar gerekçesine, etki diff'ine ve doğrulama kaynağına kesintisiz gezinmek |
| [BeadBoard ve Lista Beads](https://github.com/gastownhall/beads/blob/main/docs/community-tools.md) | Koordinasyon ve editörde görünürlük referansları | Host'a özel yetkileri dürüst sunmak; shared memory ile agent orchestration'ı ayırmak |

Jira/Rovo, ClickUp, GitHub Projects/Copilot ve konuşmadaki diğer araçlar benchmark havuzunda korunur. Kimliği net olmayan Agent Memory Hub/Memorix için özellik karşılaştırması uydurulmaz. Bu görevin çıktısı onların kodlarının birleştirilmesi değildir.

## Altı yanlışlanabilir ürün iddiası

| Hipotez | Aynı deneyde aranan sonuç | Başarısız sayılacağı durum |
|---|---|---|
| H1 Karar değişimi açık iş listesini doğru günceller | Tek gerekçeli iş obsolete adayı; OR gerekçeli iş korunur; unknown review | Yanlış kapanış, gizlenen eksik graph veya atlanan etki |
| H2 Hafıza yeni oturuma anlam taşır | Aktif karar, eski ret gerekçesi ve pending approval doğru sürümle gelir | Tüm geçmişi tekrar okuma zorunluluğu veya eski kararın active görünmesi |
| H3 Manuel yönetim azalır | Hazır başlık/AC ve atomik onay; süre ve düzeltme sayısı baseline'dan düşük | İnsan kartları yeniden yazıyorsa veya review kuyruğu büyüyorsa |
| H4 Tamamlanma güvenilirdir | Claim/partial/verified/stale ayrımı, başarısız kanıtta yeni düzeltme olayı | “Done” ifadesinden doğrulama veya eski testle yeni AC kapatma |
| H5 Otomasyon ekonomik olur | Eşdeğer kaliteyle bounded context ve deterministic bypass farkı ölçülür | Token azalışı karşılığında recall/precision gerilerse |
| H6 Bilgi ürünler arasında kaybolmaz | Source→prompt revision→execution→artifact→evidence izlenir | Import otomatik diye etiketlenirse veya erişim kesintisi gizlenirse |

T01 corpus, T02 platform testi, T03 alternatif karşılaştırması, T24 pilot bu hipotezleri sınar. Sonuçlar **native/configuration/custom extension/unavailable/unknown**, sürüm, süre, tıklama, manuel metin, kalite ve token alanlarıyla kaydedilir. Decivora henüz uygulanmadığından bugün karşılaştırmalı skor veya üstünlük sonucu yoktur.

## Özgün katkı için karar kuralı

Mevcut araç veya makul bir extension aynı sözleşmeyi daha az bakım yüküyle sağlıyorsa entegrasyon geçerli sonuçtur. Bağımsız ürün ancak karar gerekçesi, güvenilir impact ve düşük yönetim yükü kombinasyonu ölçülebilir değer üretiyorsa anlamlıdır. Lisans, bakım ve veri göçü maliyeti de değerlendirilir. “Hepsinin özelliklerini toplayalım” yeterli bir farklılaşma tezi değildir.

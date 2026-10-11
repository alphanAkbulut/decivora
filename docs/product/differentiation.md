# Farklılaşma tezi ve karşılaştırma deneyi

**Tez:** Decivora, AI çıktılarının yalnız hatırlanmasını değil, onları doğuran karar değiştiğinde hangilerinin hâlâ geçerli olduğunu açıklamayı hedefler. Ürün sözleşmesi: **yakala → uzlaştır → gerekçeye göre etki çıkar → hazır onay → kanıtla doğrula**. Tek bir özelliğin icadı veya kanıtlanmış pazar üstünlüğü iddiası değildir.

En güçlü demo “bir task oluşturduk” olmayacak: mimari değişirken gereksiz işi bulmak, alternatif gerekçesi kalan işi korumak, eski başarıyı silmemek ve bütün bunları kullanıcıya kart yazdırmadan yaptırmak olacak.

## Referanslarla somut fark hedefi

Aşağıdaki karşılaştırma doküman incelemesine dayanır. **Rakipte bulunmadığı gösterilmemiş hiçbir yeteneğe yok demiyoruz.** Tam kaynak/kanıt statüsü [benchmark matrisinde](../discovery/benchmark.md). Yakın dört kaynağın ana sayfaları 2026-10-09 yeniden incelendi; runtime testi yapılmadı.

| Referans | Öğrendiğimiz / örtüşen alan | Decivora'da sınayacağımız ilave sözleşme |
|---|---|---|
| [Beads](https://github.com/gastownhall/beads) | Görev hafızası ve dependency graph | Yürütme bağımlılığına ek olarak Decision/Requirement gerekçeleri, AND/OR/unknown ve açıklanmış obsolete önerisi |
| [Task Master](https://github.com/eyaltoledano/claude-task-master) | Gereksinimden uygulanabilir küçük işler üretmek | Yeni sohbet/karar geldikçe mevcut planı yeniden değerlendirmek; gereksiz task sayısını ve manuel düzeltmeyi ölçmek |
| [Linear](https://linear.app/docs/mcp) | Proje/issue erişimi; [agent-assisted updates](https://linear.app/docs/initiative-and-project-updates) ve [Intercom'dan AI issue üretimi](https://linear.app/docs/intercom) | Genel AI taslağını özgünlük saymamak; coding/chat kaynaklarını karar gerekçesi, downstream impact ve revision-bound kanıtla birleştirmeyi sınamak |
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

## Şikâyetlerden çıkan öncelik

[Kullanıcı araştırması](../discovery/user-research.md) context yükü, gereksiz task üretimi, veri kurtarma güveni, görünürlük, kurulum yükü ve bilgi tutarlılığı sinyallerini ayrı kanıt seviyeleriyle kaydeder. Ters düşünme sonucu: bizim ürünümüz bunları çözmeye çalışırken daha kalabalık inbox, daha pahalı context ve daha zor kurulum yaratırsa başarısız olur. İlk pilotta H1/H3/H4 birlikte ölçülmeli; yalnız üretilen task sayısı başarı metriği olmamalı.

Task Master ve Beads için okunan tarihsel şikâyetlerde bakımcı düzeltmeleri de var. Güncel sürümü ve desteklenen yapılandırmayı karşılaştırmadan üstünlük iddia etmeyiz. [Güncellenen bulgular ve deney şablonu](../discovery/benchmark-findings.md).

## Yeni Claude Projects ve somut gerçekleşme boşluğu

2026-10-11 [güncel inceleme](../discovery/claude-projects-overlap.md): paylaşılan memory, karar bağlamı, paralel threads ve iş takibi ciddi örtüşmedir. “Claude yalnız dosya klasörü” veya “karar hatırlama yalnız bizde” tezi kullanılmaz. Bağlı çalışma ortamında native takip güçlü olabilir; manuel veya providerlar arası geçiş için aynı oracle gerekir.

Kullanıcının “dosyalar üretildi ama yüklenip yüklenmediği ve hangi yaklaşımın seçildiği bilinmiyor” örneği H2/H4/H6'yı [GAP-01–10](intent-to-reality-gap.md) ile somutlaştırır. Öneri, gerçek insan seçimi, artifact üretimi, exact hedefe uygulama ve acceptance evidence ayrı tutulur. Bu hipotezi yalnız memory boyutuyla veya token bütçesiyle çözülmüş saymayız. Native Projects bunu yeterli yönetim yüküyle sağlıyorsa integration/extension T03 için geçerli sonuçtur.

## Güncel yatırım sırası

[Tasarım revizyonu 03](current-direction.md) H2/H4/H6'yı GAP ve RES ile ilk sınırlı deneyde sınamayı önerir; H1 karar-aware impact tam vizyonda ve aynı fixture'ın stale/OR kısmında korunur. Tek hedef kanıtı ve tekrar başlayan oturum davranışı gösterilmeden geniş orchestration/admin/ekip yatırımı önerilmez. Ürün iptali veya independent build kararı verilmedi; native/extend/build kapısı sonuçlara bağlıdır.

## WrongStack ile örtüşme ve reuse sınırı

2026-10-11 [sabit ref kaynak incelemesi](../discovery/wrongstack-review.md): SAGE conditional validity/anchors, completion gate, evidence schema, requirement coverage ve proposal-only MCP ciddi örtüşmedir. DoD paneli ve subagent budget/orchestration belgeleri de tekil özellikleri fark diye saymamamız gerektiğini gösterir. Exact insan seçimi/target uygulama/AC freshness, AND/OR/unknown impact ve providerlar arası kaynak sürekliliği aynı WS/GAP/RES fixture'ında sınanmalı; incelenmeyen yeteneğe yok denmez.

WrongStack'in küçük deterministik modülleri reuse adayıdır; bütün platformu fork etmek veya onu gereksiz ilan etmek bugünkü kanıtla gerekçeli değildir. T03d kaynak/uyum deneyi T03b karşılaştırmasını besler; T03c sonucu bağımsız build, native kullanım veya extension olabilir. Bugün kod alımı, çalışan interoperability veya üstünlük sonucu yok.

**Repo geneli takip (2026-10-11):** [R04–09 kaynak bulguları](../discovery/code-reuse-assessment.md) governance event/receipt/revision/grant/verification ve typed contract graph örtüşmesini güçlendirir. Decision/options/rationale kayıtları da upstream core'da var. Bu temel bileşenler özgünlük iddiası olamaz; H1/H4/H6'da insan seçimi, exact target observation, causal supersession ve providerlar arası devam birlikte ölçülmeli. Uygun native/extension konfigürasyonu kontrol baseline'ı olarak korunur.

## Ekosistem karşı kanıtı — 2026-10-11

[10 repo taraması](../discovery/ecosystem-research.md): Graphiti zamansal bilgi ilişkisi, LangGraph kalıcı interrupt/resume, LiteLLM rezervasyon ve rate limit mekanizmaları içeriyor. “Bilgi yaşar”, “soru kaybolmaz”, “bütçe rezervasyonu var” tek başına benzersizlik iddiası değil. Kaynak okuması bütün domain sözleşmesinin çalıştığını veya eksik olduğunu kanıtlamaz.

Ölçülecek hedef H1/H3/H4/H6 birleşimi: kullanıcı seçiminin doğru bağlanması, gerekçeye bağlı değişiklik etkisi, hedef revision'da uygulama kanıtı ve az yönetim yüküyle providerlar arası devam. Hazır bileşen/native kullanım bu zinciri daha ekonomik sağlıyorsa reuse/extension başarıdır. T03e kapsamı araştırma; ürün yönü, model/stack ve Q13 adoption kararı değişmedi.

# Fikrin olgunlaşma hikâyesi ve kaynak kapsamı

Kaynak: **AI Proje Takibi**, conversation ID `6ac90f90-848c-83eb-9fbb-f655c0d63413`; [orijinal sohbet](https://chatgpt.com/c/6ac90f90-848c-83eb-9fbb-f655c0d63413). İnceleme tarihi 2026-10-09. İki sayfada 14 kullanıcı turu alındı; bir assistant mesajı 20.000 karakterde kesildiği için son kısmı ayrıca orijinal sohbet ekranından okundu. Kaynağın önerileri yürürlükte talimat veya doğrulanmış ürün kabiliyeti sayılmadı.

Bu belge birebir transcript değildir: ürün fikirlerini, değişen yönleri ve gerekçeleri koruyan düzenlenmiş kaynak haritasıdır. Özel başka proje isimleri, örnek repo adları ve ilgisiz detaylar yeni ürüne taşınmadı. Rakip yıldız sayıları, fiyatlar ve doğrulanmamış genel pazar hükümleri ürün gerçeği olarak kopyalanmadı.

| Evre | Kaynak kullanıcı turn ID | Yeni ihtiyaç / olgunlaşma | Kalıcı karşılık |
|---|---|---|---|
| E01 | cb914886-519c-4747-a7f4-407512db004e | Prompt'tan sonra dallanan işlerde ilk tespitler unutuluyor | [Vizyon](../product/vision.md), CAP-01 |
| E02 | 41edb356-f622-4fcd-b53c-c3d5f9c3abb7 | Ne bitti, yarım kaldı, gereksizleşti? Çalışma ekranında görmek | UX-01/03, VER-01 |
| E03 | 27263725-087e-4133-a130-553d733069e6 | Sürekli Markdown okuma token israfı; MCP ve grafik arayışları | [Routing/maliyet](../architecture/routing-token-economy.md) |
| E04 | 51e553b6-8795-47a4-8db9-29b0c29f4220 | Yeni fikir, verilen prompt ve dosya kaydetme talimatı da kaybolmasın | Tipli çıktı ve execution lineage |
| E05 | 91080775-1e16-4349-bc66-7ac23a3e192a | Mevcut AI PM araçlarıyla karşılaştırma | [Benchmark](benchmark.md), geniş referans havuzu |
| E06 | 9744118b-062a-4530-8a86-f0b239b12e36 | Kim değerlendirir, nasıl bağlanır, çok proje ve normal chat ne olacak? | PRJ-01, binding, capture coverage, repo olmadan araştırma |
| E07 | 38b3d735-48fd-46d2-b79a-c7eb981a9d47 | Eski/yanlış fikirler aktif görünmesin; yenisi nasıl değerlendirilecek? | Active/history, canonical decision, reconciliation |
| E08 | 580df353-a060-4bc1-a74b-6a6423ae45f8 | Mevcut araçların maliyeti, lisansı ve gerçek kullanım yüzeyi | Lisans riski, build/extend ve görsel UX benchmark |
| E09 | 7097dc8e-3b23-4779-a728-c9089ea3f88a | Beads UI ekosistemi, token/yönetim yükü ve güvenilirlik şikâyetleri | Minimal araç seti, atomic batch, audit, ürün farklılaşması |
| E10 | 5c9ef097-5449-4bbb-8790-bc13a03b85f1 | Manuel planlama sıfıra yaklaşsın; log olsun; unutulan onay; Chat→Code bağlantısı | Event log, PendingDecision, adapter, source/state ayrımı |
| E11 | 8f8aefda-71ad-46a7-9d37-1fe54958657d | Onay sorun değil; elle başlık/DoD yazmak istemiyorum | Hazırlanmış toplu çoktan seçmeli onay |
| E12 | 4d8da776-2aa2-40ab-998f-6fe2e63b6e67 | Yeni mimari eski işleri gereksiz bırakırsa nasıl anlayacağız? | Decision-aware graph, impact triggers, çoklu gerekçe |
| E13 | 4780d162-cf0e-4bf3-b9f8-3fa2b7e26942 | Kapsamı koru; MVP ayrı; basit insan işleri etiketi; OpenSpec ve lisans | [Tam kapsam](../product/full-scope.md), routing, licensing |
| E14 | c968d496-e95f-4510-95b0-28121cbdc9ae | Karar/evrim/roadmap ve Codex-ready GitHub devir paketi | Bu repo, [backlog](../delivery/backlog.md), AGENTS |

## Evreler arasındaki kritik dönüşüm

Başlangıç çözümü gereksinim dosyaları ve GitHub task disiplinidir. Token ve manuel yük itirazı, yapılandırılmış store ve context-on-demand yaklaşımına götürür. “Task” tanımı yetersiz kalınca tüm AI çıktılarının yaşam döngüsü gündeme gelir. Birikmiş ama eskimiş fikirler problemi, aktif bilgi ile tarihçeyi ayırmayı gerektirir. Pasif capture adaylarının bulunmasıyla rakiplerin kapsamı genişler; benzersizlik iddiası geri çekilir. Son olarak mimari değişikliklerin eski planı nasıl etkilediği sorusu ürünün merkezini oluşturur.

## Korunan yan fikirler

Araştırma→prompt→agent execution→kod/belge→verification zinciri; daha önce reddedilmiş fikrin yeni kanıtla yeniden ele alınması; source mesajına geri dönme; birden çok gerekçeyi birlikte karşılayan işler; epoch/cursor ile incremental analysis; ayrı audit; kanıtla otomatik ilerleme; oturum sonunda tek review; kısa kurulum kuralı; editör yanında görünürlük; next-ready task; mevcut araçla kısa vadeli pilot; kendi geliştirme sürecinde dogfooding; açık kaynak reputasyonu; open core/managed service ihtimali kapsamda korunmuştur.

Ürünün kendi hafızasını kullanması gelecekte hedeflenir; bugün çalışmayan ürünün kendisine bağımlı geliştirme süreci kurulmaz. Git dokümantasyonu bootstrap hafızadır.

## Kaynak konuşma sonrası evrim — 2026-10-11

Bu takip E01–E14 orijinal evrelerini değiştirmez. Yeni Claude Projects'in memory/koordinasyon örtüşmesi [rekabet incelemesinde](claude-projects-overlap.md) kaydedildi. Kullanıcı, dosya üretimi/yükleme talimatı ile gerçek uygulama ve gerçek yaklaşım seçiminin konuşmada karışmasını problem olarak verdi. [GAP sözleşmesi](../product/intent-to-reality-gap.md), yeni domain/ER/event karşılıkları ve [güncel yön](../product/current-direction.md) bu somut ihtiyaca bağlandı.

Sonraki assistant önerisi geniş geliştirmeden önce sınırlı prototip/karşılaştırmadır; kullanıcı tüm belgelere son evrimi yansıtmayı istedi. Bu istek belge revizyonunu yetkilendirir; bağımsız ürün geliştirme, iptal, stack veya model/hesap erişimi kararı çıkarılmaz. Tam vizyon, impact ve ekip geleceği korunur; tasarım revizyonu 03 tek güncel set içinde tutulur.

## Kaynak sonrası uygulama ve öğrenme — 13–20 Ekim 2026

Bu kayıt E01–E14 kaynak haritasını değiştirmez; tarihler build/rapor ve bu geliştirme sohbetinin takip kayıtlarına dayanır. Tarihsel11Ekim belge odağı bugün runtime yok anlamına gelmez.

| Dönüşüm | Önceki varsayım / karşılaşılan kanıt | Alınan yön ve neden | Mevcut sınır |
|---|---|---|---|
| Plandan yerel ürüne | Yalnız belgeyle teknik yapılabilirlik kanıtlanamaz | Q15-A/DEC-21 ile Python3.12/SQLite çekirdek; event, onay, review, arayüz ve güvenli kaynak akışı kodlandı | Yerel alt modül başarısı MVP değildir |
| Tek çıktıdan gerçek bağlama | Regex/schema ve tek mesaj doğru task/durum evrimini göstermez | Geç cevap, aynı task, ayrı işler, belirsizlik ve false-Done için48çok turlu case; dört-case ölçüm | İlk grup eksik; AI-authored oracle insan gold değildir |
| Gönderilen mesajdan gözlenen kaynağa | Araçla iletilen prompt normal human mesajı olarak görünmedi | Seçilmiş child chatte gerçek insan girişiyle2human/6assistant ve8→8dedup ayrı doğrulandı | Başka sohbetler veya sürekli tam coverage sonucu değil |
| Test geçmesinden ürün politikasına | J02 kapsam sorusunu model ayrı Task yaptı | Kullanıcı görevle bağlı clarification seçti; domain/schema/review/UI/resolve eklendi | Eski başarısız çıktı korunur; yeni talimat gerçek modelle yeniden sınanmadı |
| API başarısızlığından güvenli devam yoluna | Generation unknown, sonra45saniye timeout görüldü | Kör retry yok; reserve-retained owner review ve güvenli phase tanısı; geleceğe120saniye socket | Sağlayıcı kök nedeni bilinmiyor; son unknown için ayrı kabul sonrası J04soru yakalama/kaynak validation bulgusu verdi |
| Dağınık teslim notlarından güncel girişe | README/devir/roadmap eski durumları güncelmiş gibi taşıdı | [20Ekim güncellik denetimi](../quality/documentation-currency-audit.md): güncel özet, karar gerekçesi, tarihsel kanıt ayrımı | Belge/render başarısı semantik ürün kabulü değildir |

Ürün kimliği değişmedi: yaşayan karar farkındalıklı hafıza. Öğrenilen ayrım **kaynağı görebilmek → anlamı çıkarmak → doğru işe bağlamak → yetkili kabul → gerçek kanıt** halkalarının her birinin ayrı doğrulanmasıdır. [DEC-23–27](../product/decision-map.md) gerekçeleri ve sonraki değerlendirme koşullarını saklar.

20Ekim ek öğrenme: Kullanıcı Codex'te yeni chat göremediğini sorunca test yüzeyi ayrımı açıklığa kavuşturuldu. Çok turlu API replay, normal host arayüzü capture deneyi değildir. Onaylı J04iki turda soru kaçırma ve paraphrase reddi gösterdi; literal-question talimatı düzeltildi, eski başarısız sonuçlar korundu. [Sonuç ve yöntem](../quality/dialogue-batch-001-j04.md).

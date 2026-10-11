# Yeni Codex oturumu için başlangıç

Önce [AGENTS.md](../../AGENTS.md), [güncel yön](../product/current-direction.md), [status](status.md) ve sıradaki [backlog](backlog.md) görevini oku. İlk P0 deneyi ile tam [P1b MVP](../product/mvp.md) ayrı; [sürüm düzeni](../governance/versioning.md) tek güncel seti gösterir. İlgili ADR ve mimari belgesini hedefli aç; tüm repo ve kaynak sohbeti her turda tekrar okutma.

Fazına göre görev bulmak için [proje ağacı ve MVP/P2/P3 takip görünümünü](phase-tracker.md) aç. Görev durumunun otoritesi backlog/status'tur; faz görünümü bağımsız kopya değildir.

Projeyi ilk kez gören model için [LLM devir haritası](llm-handoff.md) 25 anlama kontrolü içerir. Çalışma düzeni [kısa proje yönetim planında](project-management.md); engine adlarının karşılığı [engine kataloğundadır](../architecture/engines.md). Uygulamadan önce ilgili [runtime sözleşmesini](../architecture/runtime-contracts.md) ve [izlenebilirlik satırını](../quality/traceability.md) oku.

Kullanıcının uygulama geliştirme talebi geldiğinde kullanılabilecek talimat:

> Decivora'nın mevcut durumunu ve AGENTS.md'yi oku. Backlog'daki sıradaki bağımlılıkları karşılanmış tek görevi seç. Görevin kabul kriterlerini ve etkilenecek dosyaları kısaca belirt; yetkilendirilmiş kapsamda uygula. Taslak ADR'yi kesin karar sayma. İlgili doğrulamayı çalıştır, sonucu ve açık belirsizliği kaydet. Tam kapsamdan fikir silme, başka projeye dokunma, test edilmemiş özelliği çalışıyor diye sunma. Görev bittiğinde sonraki küçük işi belirt.

T01/T02 önce kanıt üretir. Kurulum gerekiyorsa yalnız izole fixture workspace kullan; mevcut gerçek projelerin agent config'ini değiştirme. Ücret, dış erişim veya scope kararı gerektiren adımları somut hazırlık sonrası owner'a sun.

Portföy/ürün değerlendirmesi için ayrı [vaka çalışması](../portfolio/product-evaluation-case-study.md) problemi, owner katkısını, karar alternatiflerini ve kanıt eksiklerini özetler. Kod/teknoloji alımı için [kaynak değerlendirmesi](../discovery/code-reuse-assessment.md) R01–24, paket haritası ve henüz seçilmemiş A/B/C önerilerini gösterir. README'nin veya canonical backlog/ADR'nin yerine geçmezler.

Ek kaynak ararken [T03e araştırma kartı](../discovery/ecosystem-research.md) ve [pinned aday listesi](../discovery/ecosystem-candidates.json) ile başla. İlk 10 repo tarandı; Graphiti/LangGraph/LiteLLM öncelikli derin inceleme adayı, henüz seçilmiş dependency değil. Araştırmanın stop kuralı, küçük işleri ve not_run deneyleri kartta; T01 ana sıra korunur.

Sonraki engineering çalışmasında [teknik boşluk analizini](../quality/technical-gap-analysis.md) ve ilgili [IC sözleşme ayrıntısını](../architecture/implementation-contracts.md) oku. TG kayıtları neden neyin incelendiğini, kanıt sınırını, kapanış testini ve pending owner sorusunu gösterir; ürünün çalıştığına dair kanıt değildir. İki farklı iş için T24p kullanımı düzeltildi: dil T24p, ölçüm T24q.

## Görsel rehber ve bugünkü aşama

> [!TIP]
> İlk okuma: [README aşama tablosu](../../README.md) → [görsel sözlük](../quality/visual-documentation.md) → ilgili atlas/sequence/ER → [teknik gap](../quality/technical-gap-analysis.md). 35 renkli Mermaid çizimi tasarımı anlatır; çalıştırılmış ürün veya geçilmiş acceptance sonucu değildir.

Ürün keşif/tanım/teknik tasarımda; T01 IN_PROGRESS. [İlk corpus](../../examples/corpus/README.md) ve [baseline hazırlığı](../quality/baseline.md) mevcut; insan review'u, gerçek kaynak/target capability ve izinli sınırlı T03b deneyi henüz bitmedi. [Q02-R1](decision-brief.md) cevaplandı: maliyet odağıyla A açık aktarım + tek hedef ilk pilot; B Codex + tek repo sonraki bağlantı hedefi. MCP tools-only ile otomatik capture'ı ayır. Q03-R1 A da kabul edildi: ilk deney ek ücretli model API'si olmadan etiketli fixture/kod kontrolleriyle ilerler; otomatik anlam çıkarımını uygulayıp kalitesini ölçmek zorunlu sonraki doğrulama adımıdır; isteğe bağlı özellik değildir. Q02-R2 A ile ilk gerçek hedef private repo rehberidir; [READBACK-01](../quality/first-target-readback.md) manuel exact içerik eşleşmesini gösterir. Ürün target adapter/coding host ve sonraki gerçek sohbet/provider/bütçe açık; bu tek kontrol bunları çözmez. Stack/build/extend ve production yatırım kararı verilmedi. Görevleri doküman ve render başarılarına bakarak complete yapma.

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

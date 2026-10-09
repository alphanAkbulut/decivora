# Yeni Codex oturumu için başlangıç

Önce [AGENTS.md](../../AGENTS.md), [status](status.md), [MVP](../product/mvp.md) ve sıradaki [backlog](backlog.md) görevini oku. İlgili ADR ve mimari belgesini hedefli aç; tüm repo ve kaynak sohbeti her turda tekrar okutma.

Projeyi ilk kez gören model için [LLM devir haritası](llm-handoff.md) sekiz anlama kontrolü içerir. Çalışma düzeni [kısa proje yönetim planında](project-management.md); engine adlarının karşılığı [engine kataloğundadır](../architecture/engines.md). Uygulamadan önce ilgili [runtime sözleşmesini](../architecture/runtime-contracts.md) ve [izlenebilirlik satırını](../quality/traceability.md) oku.

Kullanıcının uygulama geliştirme talebi geldiğinde kullanılabilecek talimat:

> Decivora'nın mevcut durumunu ve AGENTS.md'yi oku. Backlog'daki sıradaki bağımlılıkları karşılanmış tek görevi seç. Görevin kabul kriterlerini ve etkilenecek dosyaları kısaca belirt; yetkilendirilmiş kapsamda uygula. Taslak ADR'yi kesin karar sayma. İlgili doğrulamayı çalıştır, sonucu ve açık belirsizliği kaydet. Tam kapsamdan fikir silme, başka projeye dokunma, test edilmemiş özelliği çalışıyor diye sunma. Görev bittiğinde sonraki küçük işi belirt.

T01/T02 önce kanıt üretir. Kurulum gerekiyorsa yalnız izole fixture workspace kullan; mevcut gerçek projelerin agent config'ini değiştirme. Ücret, dış erişim veya scope kararı gerektiren adımları somut hazırlık sonrası owner'a sun.

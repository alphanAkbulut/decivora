# Mevcut durum

2026-10-09 — **Discovery / Product Definition**.

| Alan | Durum |
|---|---|
| Kaynak konuşma derlemesi, vizyon/MVP/karar haritası | Bu dokümantasyon paketinde hazırlanmış |
| Mimari, ADR, görev ve kabul planları | Öneri; uygulama kanıtı yok |
| Benchmark | Birincil belge incelemesi; runtime karşılaştırma bekliyor |
| Uygulama / adapter / dashboard | Başlanmadı |
| Model doğruluğu / tasarruf / kullanıcı talebi | Ölçülmedi |
| Lisans ve nihai marka | Karar bekliyor |

**Sıradaki iş: T01** — golden corpus ve kanıt şablonunu hazırlamak; ardından T02 adapter fizibilitesi. İlk üretim kodu T03'te build/extend ve stack kapısından sonra gelir. Bu paketin GitHub'da bulunması ürün MVP'sinin tamamlandığını göstermez.

## İlerleme kaydetme düzeni

### 2026-10-09 — İkinci kapsam ve mimari incelemesi

- Kaynak konuşmanın 14 evresi ve engine adları tekrar eşleştirildi; 32 scope satırı için kaynak→özellik→engine→görev→kontrol matrisi eklendi.
- 17 kullanıcı özelliği, 10 engine/alias sözlüğü, sekiz mimari diyagram, genişletilmiş roadmap, farklılaşma hipotezleri, LLM handoff ve kısa proje yönetim planı hazırlandı.
- ADR-0007/0008 önerileri; graph snapshot yarışı, durable processing, verifier yetkisi ve etkisiz replay sözleşmeleri eklendi. 30 ana göreve küçük alt dilimler bağlandı; zorunlu test planı V01–V28 oldu.
- Yerel doküman kontrolü geçti: 46 Markdown, 32 scope, 30 ana görev, 14 MVP AC, 17 feature, 10 engine ve 14 kaynak evresi referansları tutarlı. Mermaid render ve remote içerik doğrulaması teslimin ayrı kontrolüdür.
- Uygulama geliştirilmedi; engine/adapter/test suite çalıştırılmadı. Bağımsız LLM anlama deneyi yapılmadı. T01 hâlâ sıradaki görev.

İnceleme: [bulgular ve açık kalanlar](../quality/completeness-review.md). Teknik önerilerin eklenmesi onları owner tarafından kabul edilmiş mimari karar yapmaz.

Her görev sonunda görev ID, değişen dosyalar, AC karşılığı, çalıştırılan kontrol ve sonuç, açık engel ve bir sonraki görev buraya veya tarihli delivery kaydına eklenir. ADR statüsü gerçek karar olmadan accepted yapılmaz. Tamamlanma yalnız somut kanıtla kaydedilir. Geçici ilerleme ve branch isimleri AGENTS.md içine yazılmaz.

## Korunacak alanlar

Başka kullanıcı projeleri bu repo için pilot olarak kendiliğinden bağlanmaz/değiştirilmez. Kaynak transcript ve credentials repoya konmaz. Doküman düzenlemesi ürünü çalıştırma, ücretli API kullanma veya public release yetkisi değildir.

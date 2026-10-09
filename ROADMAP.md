# Roadmap

Takvim değil, kanıt kapılarıyla ilerleyen yol haritası. Tüm ürün yetenekleri [tam kapsamda](docs/product/full-scope.md) korunur. Mevcut aşama **P0 Discovery / Product Definition**; uygulama geliştirilmedi.

```mermaid
flowchart LR
    P0[P0 Kaynak ve fizibilite] --> P1A[P1a Teknik kanıt]
    P1A --> P1B[P1b Yerel MVP]
    P1B --> P2[P2 Chat ve agent sürekliliği]
    P2 --> P3[P3 Maliyet ve entegrasyon]
    P3 --> P4[P4 Ekip ve ürünleşme]
```

| Faz | Teslim | Çıkış kapısı |
|---|---|---|
| P0 | Kaynak haritası, benchmark, platform testleri, build/extend ve stack kararı | Gerçek capability/karşılaştırma raporu; sonraki ADR'ler onaylı |
| P1a | Import→reconcile→impact→approval→event→projection teknik dilimi | Synthetic oracle, atomic retry, AND/OR/unknown, replay ve false-done senaryoları geçer |
| P1b | Çok projeli local MVP; iki coding adapter; MCP; Inbox/Board/Graph/Timeline; temel verifier/routing/telemetry | AC-01..14 ve pilot kalite kapıları; destek matrisi dürüst |
| P2 | Aynı sağlayıcı ve cross-provider chat sürekliliği; gelişmiş reconciliation, verification, read-only GitHub evidence; izinli panel/import iyileştirmeleri | Kaynak→prompt→execution trace ve coverage; gerçek yüzeylerde test |
| P3 | Maliyet raporları, model routing, kontrollü GitHub/Linear/Jira yazma, kurulum ve açık kaynak release hazırlığı | Cost/quality kıyası, outbox conflict testleri, lisans/isim kararı |
| P4 | Takımlar, organization, RBAC, cloud sync, enterprise audit, managed service ve open core değerlendirmesi | Talep kanıtı, güvenlik/uyumluluk ve ticari model onayı |

Kritik sıra: [T01 → T02 → T03](docs/delivery/backlog.md) → çekirdek veri/olay → reconciliation/impact → approval/verification → görsel MVP. Tek adapter'lı P1a bütün MVP diye adlandırılmaz. Sonraki fazlara geçmek için bütün vizyonu gerçekleştirmiş olmak gerekmez.

```mermaid
flowchart TB
    S[Kaynak konuşma ve tam vizyon] --> C[T01 Corpus ve oracle]
    C --> A[T02 Gerçek adapter capability]
    A --> D{T03 Build veya extend kararı}
    D -->|Karar ve izinler hazır| CORE[T04-T08 Kimlik, kalıcı source, log, policy]
    D -->|Kanıt yetersiz| EXP[Küçük ek deney ve açık karar]
    EXP --> D
    CORE --> INT[T09-T14 Extraction, reconciliation, impact, approval, verification]
    INT --> G{T15 Teknik kanıt kapısı}
    G -->|Geçti| MVP[T16-T23 İki adapter, MCP, UX, ekonomi, restore]
    G -->|Başarısız| FIX[Kanıta bağlı küçük düzeltme]
    FIX --> G
    MVP --> PILOT{T24 MVP ve kullanıcı pilotu}
    PILOT -->|AC ve kalite kanıtlı| NEXT[T25-T30 Chat, entegrasyon, release, ekip]
    PILOT -->|Eksik capability| LIMITED[Sınırlı pilot ve açık gap]
```

Güvenlik/kalıcı işleme/graph race sözleşmeleri ilk çekirdek dilimlerinde doğrulanır; son release'e bırakılmaz. Çalışma ritmi ve roller [kısa proje yönetim planında](docs/delivery/project-management.md).

Başarısız kapıda: neden ve kanıt kaydedilir, küçük düzeltme işi açılır, faz geçişi bekler. Bir yetenek platformca engellenirse full scope kaydında kalır; sınırlı sürüm adı ve fallback açıkça belirtilir.

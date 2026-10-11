# Roadmap

> [!NOTE]
> **Şema anahtarı:** mavi kaynak/işleme · sarı yetki/onay · turkuaz kalıcı bilgi · yeşil kanıt alanı · turuncu belirsizlik · gri tarihçe · mor öneri/gelecek. Renkler implementasyon veya test başarısı değildir. [Görsel sözlük](docs/quality/visual-documentation.md).

Takvim değil, kanıt kapılarıyla ilerleyen yol haritası. Tüm ürün yetenekleri [tam kapsamda](docs/product/full-scope.md) korunur. Mevcut aşama **P0 keşif + kontrollü çalışan deneyler**; ürün MVP’si geliştirilmedi. [Audit sonrası sonuç/kalan işler](docs/quality/audit-remediation.md).

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Arial, sans-serif","fontSize":"14px","primaryColor":"#eff6ff","primaryTextColor":"#0f172a","primaryBorderColor":"#1d4ed8","lineColor":"#64748b","secondaryColor":"#ccfbf1","tertiaryColor":"#f1f5f9","background":"#ffffff","mainBkg":"#eff6ff","textColor":"#0f172a","clusterBkg":"#f8fafc","clusterBorder":"#94a3b8","edgeLabelBackground":"#ffffff","actorBkg":"#eff6ff","actorTextColor":"#0f172a","actorBorder":"#1d4ed8","signalColor":"#64748b","signalTextColor":"#0f172a","noteBkgColor":"#fef3c7","noteTextColor":"#0f172a","noteBorderColor":"#92400e"},"flowchart":{"htmlLabels":false,"curve":"linear"},"sequence":{"wrap":true},"themeCSS":"background-color:#ffffff;"}}%%
flowchart TB
    accTitle: Fazlar ve yatırım alternatifleri
    accDescr: Önerilen tasarım veya açıkça belirtilen sentetik örnek. Renkler alan ve kontrol türünü gösterir; implemented veya passed kanıtı değildir. Yetki, revision ve coverage sınırları korunur.
    P0[P0 Oracle ve kaynak hedef fizibilitesi] --> E[P0 Sınırlı gerçekleşme devam deneyi]
    E --> G{Native extend veya build kararı}
    G -->|Build kanıtlı ve owner seçti| P1A[P1a Teknik kanıt]
    G -->|Native yeterli| N[Mevcut çözüm veya entegrasyon]
    G -->|Dar açık| X[Extension deneyi]
    G -->|Kanıt yetersiz| W[Ek deney veya bekleme]
    G -->|Owner durdurma kararı| S[Gerekçeli kapanış]
    P1A --> P1B[P1b Yerel MVP ve owner sağlık görünümü]
    P1B --> P2[P2 Chat ve agent sürekliliği]
    P2 --> P3[P3 Maliyet ve entegrasyon]
    P3 --> P4[P4 Ekip, yönetim ve ürünleşme]
    classDef process fill:#dbeafe,stroke:#1d4ed8,color:#0f172a
    classDef gate fill:#fef3c7,stroke:#92400e,color:#0f172a,stroke-width:2px
    classDef future fill:#ede9fe,stroke:#6d28d9,color:#0f172a,stroke-dasharray:5 3
    classDef warning fill:#ffedd5,stroke:#9a3412,color:#0f172a
    classDef history fill:#f1f5f9,stroke:#475569,color:#0f172a,stroke-dasharray:5 3
    class P0,E process
    class G gate
    class P1A,P1B,P2,P3,P4,N,X future
    class W warning
    class S history
```

| Faz | Teslim | Çıkış kapısı |
|---|---|---|
| P0 | T01 oracle, T02 kaynak + tek hedef capability, T03a yöntem, T03b sınırlı prototip/native kıyas, T03c yatırım kararı | GAP/RES kanıtı ve native/extend/build/durdur değerlendirmesi; erişim yoksa not_run, otomatik P1 geçişi yok |
| P1a | Import→reconcile→impact→approval→event→projection teknik dilimi | Synthetic oracle, atomic retry, AND/OR/unknown, replay ve false-done senaryoları geçer |
| P1b | Çok projeli local MVP; iki coding adapter; MCP; Inbox/Board/Graph/Timeline; temel verifier/routing/telemetry | AC-01..14 ve pilot kalite kapıları; destek matrisi dürüst |
| P2 | Aynı sağlayıcı ve cross-provider chat sürekliliği; gelişmiş reconciliation, verification, read-only GitHub evidence; izinli panel/import iyileştirmeleri | Kaynak→prompt→execution trace ve coverage; gerçek yüzeylerde test |
| P3 | Maliyet raporları, model routing, kontrollü GitHub/Linear/Jira yazma, kurulum ve açık kaynak release hazırlığı | Cost/quality kıyası, outbox conflict testleri, lisans/isim kararı |
| P4 | Takımlar, organization, RBAC, cloud sync, enterprise audit, managed service ve open core değerlendirmesi | Talep kanıtı, güvenlik/uyumluluk ve ticari model onayı |

Güncel yön ve önceki plan karşılaştırması [tasarım revizyonu 03](docs/product/current-direction.md) içindedir. Bu P0 deney önerisidir; tam vizyon ve aşağıdaki P1b çıkış kapısı korunur. Native/extension seçilirse T04–T30 bağımsız uygulama yolu otomatik çalıştırılmaz, ilgili yeni teslim planı owner kararıyla hazırlanır.

MVP, P2 ve P3 ana görevleri ayrı tablolarla [faz bazlı proje ağacı ve takip görünümünde](docs/delivery/phase-tracker.md) bulunur. Görev durumları backlog ile eşleştirilir; ayrı sürüm listesi veya ilerleme veritabanı yoktur.

Dil ihtiyacı: P1'de source/Unicode/metadata ve açık pilot dili korunur; P2'de otomatik dil tespiti, mixed fallback, locale katalogları ve çok dilli kalite önerilir. [Dil sözleşmesi](docs/product/language-and-localization.md); Q12-A kabul edildi: proje çıktı dili sabit, dil değişimi yalnız öneri, toplu çeviri varsayılan değil.

Kritik sıra: [T01 → T02 → T03](docs/delivery/backlog.md) → çekirdek veri/olay → reconciliation/impact → approval/verification → görsel MVP. Tek adapter'lı P1a bütün MVP diye adlandırılmaz. Sonraki fazlara geçmek için bütün vizyonu gerçekleştirmiş olmak gerekmez.

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Arial, sans-serif","fontSize":"14px","primaryColor":"#eff6ff","primaryTextColor":"#0f172a","primaryBorderColor":"#1d4ed8","lineColor":"#64748b","secondaryColor":"#ccfbf1","tertiaryColor":"#f1f5f9","background":"#ffffff","mainBkg":"#eff6ff","textColor":"#0f172a","clusterBkg":"#f8fafc","clusterBorder":"#94a3b8","edgeLabelBackground":"#ffffff","actorBkg":"#eff6ff","actorTextColor":"#0f172a","actorBorder":"#1d4ed8","signalColor":"#64748b","signalTextColor":"#0f172a","noteBkgColor":"#fef3c7","noteTextColor":"#0f172a","noteBorderColor":"#92400e"},"flowchart":{"htmlLabels":false,"curve":"linear"},"sequence":{"wrap":true},"themeCSS":"background-color:#ffffff;"}}%%
flowchart TB
    accTitle: Küçük teslimler ve kanıt kapıları
    accDescr: Önerilen tasarım veya açıkça belirtilen sentetik örnek. Renkler alan ve kontrol türünü gösterir; implemented veya passed kanıtı değildir. Yetki, revision ve coverage sınırları korunur.
    S[Kaynak konuşma ve tam vizyon] --> C[T01 Corpus ve oracle]
    C --> A[T02 Gerçek adapter capability]
    A --> PLAN[T03a Geçici deney yöntemi]
    PLAN --> PROTO[T03b İzinli sınırlı prototip ve native baseline]
    PROTO --> D{T03c Yatırım kararı}
    D -->|Build seçildi ve izinler hazır| CORE[T04-T08 Kimlik, kalıcı source, log, policy]
    D -->|Native veya extend| ALT[İlgili entegrasyon veya extension yolu]
    D -->|Owner durdurma kararı| STOP[Gerekçe ve kanıtla kapanış]
    D -->|Kanıt yetersiz| EXP[Küçük ek deney ve açık karar]
    EXP --> D
    CORE --> INT[T09-T14 Extraction, reconciliation, impact, approval, verification]
    INT --> G{T15 Teknik kanıt kapısı}
    G -->|Geçti| MVP[T16-T23 Adapter, MCP, UX, ekonomi, yerel yönetim, restore]
    G -->|Başarısız| FIX[Kanıta bağlı küçük düzeltme]
    FIX --> G
    MVP --> PILOT{T24 MVP ve kullanıcı pilotu}
    PILOT -->|AC ve kalite kanıtlı| NEXT[T25-T30 Chat, entegrasyon, release, ekip]
    PILOT -->|Eksik capability| LIMITED[Sınırlı pilot ve açık gap]
    classDef source fill:#eff6ff,stroke:#1d4ed8,color:#0f172a
    classDef process fill:#dbeafe,stroke:#1d4ed8,color:#0f172a
    classDef gate fill:#fef3c7,stroke:#92400e,color:#0f172a,stroke-width:2px
    classDef future fill:#ede9fe,stroke:#6d28d9,color:#0f172a,stroke-dasharray:5 3
    classDef warning fill:#ffedd5,stroke:#9a3412,color:#0f172a
    classDef history fill:#f1f5f9,stroke:#475569,color:#0f172a,stroke-dasharray:5 3
    class S source
    class C,A,PLAN,PROTO process
    class D,G,PILOT gate
    class CORE,INT,MVP,NEXT,ALT future
    class EXP,FIX,LIMITED warning
    class STOP history
```

Güvenlik/kalıcı işleme/graph race sözleşmeleri ilk çekirdek dilimlerinde doğrulanır; son release'e bırakılmaz. Çalışma ritmi ve roller [kısa proje yönetim planında](docs/delivery/project-management.md).

Başarısız kapıda: neden ve kanıt kaydedilir, küçük düzeltme işi açılır, faz geçişi bekler. Bir yetenek platformca engellenirse full scope kaydında kalır; sınırlı sürüm adı ve fallback açıkça belirtilir.

## Ekip ve veri altyapısı hattı

[Yönetim merkezi](docs/product/administration-and-operations.md) P1b'de yerel owner için sağlık/hata/etkin limitler; P4'te ekip admin ve platform operasyon konsolu olarak ayrılır. T20f/T21c/T23e/T24g mevcut görevlerin küçük dilimleridir. Kaynak lisansı, private veri erişimi, self-host/managed kurulum ve olası paketler ayrı kararlardır; bugün hosted servis veya lisans seçilmedi.

P1'de tenant/agent kimliği, dar izin, kalıcı audit ve retention/recovery temeli kurulur; P4'te davet, rol yönetimi, ortak hafıza, bağımsız review ve merkezi ekip işletimi gelir. [Ekip/veri planı](docs/delivery/team-data-plan.md) küçük P1 alt görevlerini ve C01–C06 kapılarını açıklar. [Kapasite planındaki](docs/architecture/storage-memory-capacity.md) S0–S3 topolojileri bir kullanıcı sayısı garantisi veya takvim değildir; ölçülmüş darboğaz ve operasyon ihtiyacıyla seçilir.


**Restore sırası açıklaması:** P1a T07c çekirdek DB+payload restore’u üretir, T15/T15a sınar; şemadaki P1b restore etiketi T23’ün kapsamlı migration/privacy/export ve operasyon devamıdır. Teknik kalite kapısı P1b’yi beklemez. Mevcut Mermaid/SVG kaynağı değişmedi.

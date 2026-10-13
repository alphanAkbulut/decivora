# Yerel review çekirdeği: mevcut kod ve kalan işler

**Uygulanmış dilim: T13a + ana T13 In Progress.** `ReviewService` local/manual operation group önerisini kalıcı saklar; compare → selection → ayrı human approval → atomik apply sağlar. İnsan rolü LocalAuthorityStore'un trusted local issuer'ıdır; gerçek login/UI değildir. [Kod](../../packages/domain/review.py), [input şeması](../../manifests/review-groups.schema.json), [test/teslim](../quality/review-kernel.md). SQL core FORMAT/schema1 değişmedi; aşağıdaki payload varlıkları fiziksel yeni tablo değil, append-only `audit.ref` JSON kayıtlarıdır.

## Uygulanan sıra ve güvenlik kapıları

```mermaid
sequenceDiagram
    accTitle: Uygulanan yerel review ve ayrı onay akışı
    accDescr: Önizleme kalıcıdır. İnsan seçim ve onayı ayrı yapar. Kaynak graph yetki ve policy değiştiyse uygulama durur. Görev iptali ayrıca lifecycle korumasından geçer, verification henüz yoktur.
    participant P as Manual proposal
    participant H as Local human owner
    participant R as ReviewService
    participant S as SQLite workspace
    rect rgb(235, 243, 255)
    P->>R: ImpactRun + typed operation groups
    R->>S: Current ACL ve impact snapshot kontrolü
    R->>S: review_created audit kaydı
    H->>R: Compare ve grup seçimi
    R->>R: Declared ve temp-ID dependencies kontrolü
    R->>S: Yeni selection digest ve review_selected
    end
    rect rgb(240, 235, 255)
    H->>R: Ayrı approve çağrısı
    R->>S: Human authority + policy + snapshot
    R->>S: Bound approval + review_approved
    end
    rect rgb(235, 250, 239)
    H->>R: Apply selection + approval
    R->>S: BEGIN IMMEDIATE
    R->>S: Source frontier + knowledge + authz + policy recheck
    R->>R: Lifecycle varsa gerekçe ve downstream koruması
    alt Stale veya eksik kapsam
        R->>S: ROLLBACK
        R-->>H: Yeni preview veya seçim gerekiyor
    else Güncel ve yetkili
        R->>S: Domain events + projection + command + review_applied
        R->>S: COMMIT
        R-->>H: Applied receipt
    end
    end
    Note over H,S: Reject/defer yeni audit olayıdır. Defer eski seçimi geçersiz kılar.
    Note over R,S: Retry aynı sonucu okur. Replay model veya dış işlem çalıştırmaz.
```

## Mevcut fiziksel saklama ve mantıksal bağlar

```mermaid
flowchart TB
    accTitle: Review payload bağları ve fiziksel storage
    accDescr: Impact review seçim onay ve uygulama mantıksal JSON kayıtlarıdır. Audit ve domain events ayrı kalır. Arayüz soru cevabı ve acceptance evidence ileri işlerdir.
    I["impact_preview audit payload<br/>run + source/graph/authz digest"] --> P["review_created payload<br/>gruplar + policy"]
    P --> C["review_selected payload<br/>subset + dependencies + plan digest"]
    C --> A["review_approved payload<br/>selection digest + approval ID"]
    A --> X["review_applied payload<br/>command sonucu"]
    DB[("Mevcut audit tablosu<br/>append-only JSON ref")]
    I -. saklanır .-> DB
    P -. saklanır .-> DB
    C -. saklanır .-> DB
    A -. saklanır .-> DB
    X -. aynı transaction .-> DB
    A --> T[("Mevcut approvals tablosu<br/>digest + base + authz + key")]
    X --> E[("Mevcut events / records / edges<br/>command idempotency")]
    P --> D["Reject / Defer<br/>review_decision payload"]
    D -. eski seçimi geçersiz kılar .-> C
    F["Açık T13c/e ve T14<br/>AC/DoD, geç cevap, evidence"]
    X -. tamamlandı anlamına gelmez .-> F
    classDef persisted fill:#e8f1ff,stroke:#315c9b,color:#132b50;
    classDef approved fill:#eee7ff,stroke:#7853a7,color:#33204b;
    classDef applied fill:#e6f5ea,stroke:#347c49,color:#163c23;
    classDef pending fill:#fff4d6,stroke:#a87b18,color:#4b360a;
    class I,P,C,DB persisted;
    class A,T approved;
    class X,E applied;
    class D,F pending;
```

Ana mimari ve README şemaları ürün vizyonunu anlatır; bu iki çizim uygulanan local dilimi açıkça ayırır. Yeni tablo/migration/HTTP endpoint veya otomatik görev iptali çizilmez. [T13b lifecycle](task-lifecycle.md) uygulandı; T13c versioned AC/DoD, T13e pending question + late answer ve T14 completion/evidence hâlâ açık; bu yüzden ana T13 Done değildir.

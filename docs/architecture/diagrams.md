# Mimari ve yaşam döngüsü atlası

**Tüm diyagramlar önerilen tasarımı gösterir; çalışan sistem görüntüsü değildir.** Mermaid kaynakları GitHub'da görüntülenebilir. Oklar yetki aktarımı anlamına gelmez; yazma otoritesi command/policy katmanıdır. Metinsel sözleşmeler [engine haritası](engines.md), [domain](domain-model.md) ve [runtime](runtime-contracts.md) belgelerindedir.

## 1. Sistem bağlamı ve güven sınırları

```mermaid
flowchart TB
    USER["Kullanıcı: incele ve karar ver"]
    subgraph SOURCES["Harici kaynaklar: içerik güvenilir talimat değildir"]
        CC[Claude Code]
        CX[Codex desteklenen yüzey]
        CHAT[İzinli Chat importu]
        ART[Artifact ve test raporu]
    end
    subgraph LOCAL["Yerel Decivora sınırı"]
        AD[Adapter ve kalıcı ingress]
        EN[Extraction ve değerlendirme]
        UI[Review ve kontrol merkezi]
        POLICY[Kimlik ve command policy]
        STORE[Event log ve current projection]
        MCP[Yetkili ve bütçeli MCP]
    end
    MODEL["Opsiyonel model provider: izinli veri ve bütçe"]
    EXT["P3 dış sistem yazımı: ayrı izin"]
    CC --> AD
    CX --> AD
    CHAT --> AD
    ART --> AD
    AD --> EN
    EN -->|Öneri| UI
    USER -->|Güvenilir oturum| UI
    UI --> POLICY
    MCP -->|Proposal veya query| POLICY
    POLICY --> STORE
    STORE -->|Revision ile read| UI
    EN <-->|Hedefli bağlam| MODEL
    STORE -->|Yetkili outbox| EXT
```

Yerel depolama dış model kullanımında veri çıkmayacağı anlamına gelmez. Agent'ın MCP kimliği UI insan kimliğine yükseltilemez. P1'de model olmadan deterministik fixture akışı mümkündür.

## 2. Engine zinciri ve karar otoritesi

```mermaid
flowchart LR
    E1[ENG-01 Capture] --> E2[ENG-02 Classification]
    E2 --> E3[ENG-03 Reconciliation]
    E3 --> E4[ENG-04 Idea Evaluation]
    E3 --> E5[ENG-05 Graph ve Impact]
    E4 --> E5
    E5 --> E6[ENG-06 Review ve Policy]
    E6 --> E7[ENG-07 Log ve Projection]
    E7 --> E10[ENG-10 Context ve Health]
    E10 -->|İlgili current ve history| E3
    E7 --> E8[ENG-08 Verification]
    E8 -->|Assessment command| E6
    E9[ENG-09 Routing ve Budget] -.-> E2
    E9 -.-> E4
    E9 -.-> E8
```

E4 her aday için zorunlu model çağrısı değildir. Verification okunan kanıtı değerlendirir; bu ok kendiliğinden test komutu veya agent başlatma yetkisi vermez. Knowledge Evolution bu zincirin ortak davranışıdır.

## 3. Mantıksal veri modeli

```mermaid
erDiagram
    PROJECT ||--o{ BINDING : scopes
    PROJECT ||--o{ SOURCE_EVENT : contains
    PROJECT ||--o{ RECORD : owns
    SOURCE_EVENT ||--o{ JOB : schedules
    JOB ||--o{ EVALUATION : produces
    EVALUATION ||--o{ CHANGESET : proposes
    CHANGESET ||--o{ APPROVAL : reviewed_by
    CHANGESET ||--o{ DOMAIN_EVENT : applies_as
    RECORD ||--|{ RECORD_VERSION : versions
    RECORD_VERSION ||--o{ EDGE : source
    RECORD_VERSION ||--o{ EDGE : target
    RECORD_VERSION ||--o{ EVIDENCE_LINK : supported_by
    EVIDENCE ||--o{ EVIDENCE_LINK : backs
    SOURCE_EVENT ||--o{ PROVENANCE_LINK : cited_by
    RECORD_VERSION ||--o{ PROVENANCE_LINK : cites
    DOMAIN_EVENT ||--o{ OUTBOX_ITEM : schedules
    PROJECT {
        string project_id PK
        int knowledge_revision
        int policy_revision
    }
    SOURCE_EVENT {
        string source_id PK
        string project_id FK
        string payload_ref
        string source_epoch
    }
    RECORD_VERSION {
        string record_id FK
        int revision
        string type
    }
    EDGE {
        string edge_id PK
        string project_id FK
        string relation_type
        string justification_expression_ref
    }
    CHANGESET {
        string changeset_id PK
        string operation_digest
        int knowledge_revision
        string base_revisions
    }
    DOMAIN_EVENT {
        string event_id PK
        int append_sequence
        string project_id FK
        int schema_version
    }
```

Şema mantıksaldır; fiziksel DDL değildir. RecordVersion'ın anahtarı `(project_id, record_id, revision)`; edge iki endpoint revision'ına başvurur. Diagram okunabilirliği için tüm foreign key'ler ve Evaluation'ın çoklu input provenance bağlantıları çizilmedi. Source kimliği quarantine'da henüz project'e bağlı olmayabilir. Imported/manual ChangeSet ayrıca evaluation olmadan oluşabilir; normal inferred akış yukarıda gösterilir. Detailed constraints runtime belgesinde korunur.

## 4. Capture: receipt ile değerlendirme farklıdır

```mermaid
sequenceDiagram
    participant A as Adapter
    participant I as Ingress
    participant D as Durable Store
    participant W as Worker
    participant M as Optional Model
    A->>I: Envelope + source key + binding
    I->>I: Yetki, şema, redaction
    I->>D: TX source + job + dedup
    alt Commit başarılı
        D-->>I: Durable receipt
        I-->>A: Alındı, henüz evaluated değil
        A->>A: Ingest offset ilerlet
    else Storage hatası
        I-->>A: Hata, başarı ack yok
    end
    W->>D: Lease + fencing token al
    W->>M: Gerekirse bounded input
    M-->>W: Structured result veya hata
    alt Geçerli sonuç ve güncel lease
        W->>D: TX result + mapping + processing interval
    else Timeout veya bozuk sonuç
        W->>D: Retry/deferred/quarantine + reason
        Note over W,D: Başarısız aralık üzerinden watermark atlamaz
    end
```

## 5. Onay öncesi yeni ilişki yarışı

```mermaid
sequenceDiagram
    participant U as Kullanıcı
    participant P as Preview
    participant C as Command Policy
    participant S as Store
    P->>S: Snapshot knowledge revision 12
    S-->>P: Karar, task ve justification graph
    P-->>U: Task obsolete adayı + digest A
    Note over S: Başka yetkili değişiklik OR gerekçesi ekler
    S->>S: Knowledge revision 13
    U->>C: Approve digest A, revision 12
    C->>S: TX current revisions kontrolü
    S-->>C: STALE_IMPACT
    C-->>U: Etki değişti, yeni diff gerekli
    P->>S: Snapshot revision 13
    P-->>U: Task korunsun, yeni digest B
    U->>C: Approve digest B, revision 13
    C->>S: TX events + projection + outbox
    S-->>U: APPLIED + sequence
```

Eski onay yeni öneriye otomatik taşınmaz. Agent/source metnindeki “onayladım” cümlesi bu güvenilir approval akışının yerine geçmez.

## 6. Çoklu gerekçe ve tarihsel başarı

```mermaid
flowchart TB
    OLD["Eski Markdown kararı: superseded"] -->|false| ONLY["Sync: tek gerekçe"]
    OLD -->|false| OR["Watcher: ANY"]
    IMPORT["Belge importu: active"] -->|true| OR
    OLD -->|false| AND["Özel export: ALL"]
    OTHER["İkinci koşul: active"] -->|true| AND
    MISS["Eksik ilişki: unknown"] --> REVIEW["Review ve graph düzeltme"]
    ONLY --> OBS["Obsolete önerisi: insan onayı"]
    OR --> KEEP["Keep: başka gerekçe var"]
    AND --> CHANGE["Update veya obsolete adayı"]
    DONE["Önceki revision'da verified iş"] --> HISTORY["Tarihsel completion korunur"]
    DONE --> APPLIC["Bugünkü applicability ayrıca değerlendirilir"]
```

Boolean false gerekçenin sağlanmadığını söyler; tek başına task'ı cancelled/done yapmaz. Semantik alternatif ve kullanıcı tercihi için review gerekir.

## 7. ChangeSet durumları

```mermaid
stateDiagram-v2
    [*] --> proposed
    proposed --> deferred: ertele
    deferred --> proposed: yeniden incele
    proposed --> rejected: reddet
    proposed --> approved: güvenilir onay
    proposed --> stale: bağlam değişti
    approved --> stale: apply öncesi revision değişti
    approved --> applied: policy ve atomic commit
    approved --> failed: storage veya validation hatası
    failed --> approved: aynı onay hâlâ geçerli ve retry
    failed --> stale: onay artık geçersiz
    stale --> proposed: yeni sürüm ve yeni digest
    applied --> [*]
    rejected --> [*]
```

Stale→proposed yeni proposal revision oluşturur; eski onay/history silinmez. Undo ayrı compensating ChangeSet'tir. Bu state machine task execution veya knowledge validity state machine'i değildir; onların değerleri [domain modelinde](domain-model.md) ayrı eksenlerdir.

## 8. Geri yükleme ve yan etkisiz replay

```mermaid
flowchart TD
    B[DB ve payload backup snapshot] --> V[Şema ve bütünlük denetimi]
    V -->|Uyumlu| R[Staging projection replay]
    V -->|Uyumsuz| STOP[Diagnostic read-only veya upgrade]
    R --> D[Sequence ve digest karşılaştır]
    D -->|Geçti| SW[Projection atomik geçiş]
    D -->|Fark var| STOP
    SW --> J[Lease ve pending job recovery]
    SW --> O[Outbox duraklatılmış]
    O --> REC[Uzak durum ve receipt reconciliation]
    REC -->|Yetkili devam| SEND[Idempotent delivery]
    R -.-> NO[LLM, verifier veya dış yazma tetiklenmez]
```

Yedekten dönmek uzak GitHub/Linear durumunu geriye almaz. Dış etkiler local replay'den ayrı denetlenir.

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
        AG[Agent run ve soru gözlemleri]
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
    AG --> AD
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
    E5 --> E6[ENG-06 Review, soru yönlendirme ve Policy]
    E6 --> E7[ENG-07 Log ve Projection]
    E7 --> E10[ENG-10 Context, Health ve sonraki adım]
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
    WORKSPACE ||--o{ PROJECT : contains
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
        string workspace_id FK
        int knowledge_revision
        int policy_revision
        int authz_revision
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

Şema mantıksaldır; fiziksel DDL değildir. RecordVersion'ın anahtarı `(workspace_id, project_id, record_id, revision)`; tüm proje kayıt/FK/unique sınırları tenant kapsamını korur. Edge iki endpoint revision'ına başvurur. Diagram okunabilirliği için her tabloda tenant/FK alanları, üyelik/ACL ve Evaluation'ın çoklu input provenance bağlantıları tekrarlanmadı; [yetki sözleşmesi](identity-access.md) normatiftir. Source kimliği quarantine'da henüz project'e bağlı olmayabilir; izolasyon kalkmaz. Imported/manual ChangeSet ayrıca evaluation olmadan oluşabilir. Run ve soru ilişkileri aşağıdaki ayrı diyagramlarda; bunlar task hiyerarşisi değildir.

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
    W->>W: Güncel yetki, veri izni, dedup ve bütçe kontrolü
    alt Model gerekli ve izinli
        W->>D: Atomik bütçe rezervasyonu
        W->>M: Rezervasyon başarılıysa bounded input
        M-->>W: Structured result veya hata
    else Deterministik veya bekleyen iş
        W->>W: Deterministik sonuç veya deferred nedeni
    end
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

## 9. Task, agent ve run farklı kimliklerdir

```mermaid
flowchart LR
    H[İnsan veya servis sponsoru] --> G[Süreli dar grant]
    A[Agent principal] --> R1[Run A]
    G --> R1
    R1 -->|Gözlenmiş parent ilişkisi| R2[Run B]
    G2[Alt küme child grant] --> R2
    R1 -->|Çalışma bağlantısı| T[Ana task]
    R2 -->|Çalışma bağlantısı| T
    T -.->|Yalnız ayrı onaylı split| ST[Alt task]
    R2 --> END[Run sona erdi]
    END --> E[Artifact ve kanıt iddiası]
    E --> V[Güncel AC ve DoD doğrulaması]
    V -->|Geçerli kanıt| DONE[Task completion command]
    V -->|Eksik veya stale| WAIT[Verification bekliyor]
```

Parent kimliği bulunamıyorsa unknown kalır; gizli muhakeme çıkarılmaz. Run soy ağacı otomatik alt görev yaratmaz. Tüm child'ların geçmesi parent AC/DoD doğrulamasını kaldırmaz. [Agent işletimi](agent-and-team-operation.md), [split ve acceptance](../product/task-context-and-acceptance.md).

## 10. Soru, cevap, onay ve teslim ayrımı

```mermaid
flowchart TB
    Q[Kalıcı QuestionRequest ve bağımlı iş] --> TYPE{Soru türü ve gerekli yetki}
    TYPE -->|Bilgi veya görüş| RET[İzinli kaynak veya yetkili uzman agent]
    TYPE -->|Yetki içi teknik seçim| POL[Mevcut policy ve geçerli karar]
    TYPE -->|Korunan karar veya yetki eksik| HUMAN[Yetkili insan Inbox]
    RET --> ANS[Kaynaklı AnswerRecord]
    POL --> ANS
    HUMAN --> APP[Digest ve revision bağlı approval]
    APP --> CHECK[Güncel yetki ve bağlam kontrolü]
    ANS --> CHECK
    CHECK -->|Stale veya çelişkili| REVIEW[Yeni değerlendirme; bağlı iş bekler]
    CHECK -->|Geçerli| CAP{Host delivery capability}
    CAP -->|Destekli ve yetkili| DEL[Teslim ve receipt takibi]
    CAP -->|Yok veya bilinmiyor| MAN[Manuel aktarım veya delivery pending]
    DEL --> ACK{Host devamı doğruladı mı}
    ACK -->|Evet| RUN[Bağımlı çalışma devam edebilir]
    ACK -->|Hayır| MAN
    Q -->|Timeout veya döngü limiti| WAIT[Escalation veya bekleme; otomatik onay yok]
```

Bilgi cevabı approval değildir; protected karara dönüşürse insan koluna gider. Uzman/parent agent insanın yerini alamaz. Yetkili ve değişmemiş önceki karar tekrar sorulmadan kullanılabilir. Yalnız bağlı iş bekler; harici agent'ın durduğu veya yeniden başladığı capability/receipt olmadan iddia edilmez. [ASK sözleşmesi](agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider).

## 11. Blocker çözüm sırası ve görev önceliği

```mermaid
flowchart TB
    GRAPH[Güncel ve yetkili dependency graph] --> VALID{Coverage ve ilişkiler yeterli mi}
    VALID -->|Hayır| GAP[Unknown veya cycle inceleme]
    VALID -->|Evet| BLOCK[Engellenen işler ve ortak kök neden]
    BLOCK --> READY[Engeli çözen uygulanabilir iş veya karar]
    GOAL[Ürün hedefi, değer, risk ve owner tercihi] --> RANK[Gerekçeli öncelik önerisi]
    READY --> RANK
    RANK --> REVIEW[Yetkili değerlendirme ve sırayı düzenleme]
    REVIEW --> ACT[İzin sınırları içinde çalışma]
    ACT --> VERIFY[Kanıt ve graph yeniden değerlendirmesi]
    VERIFY --> GRAPH
```

Blocked task ile engeli çözen ready iş farklıdır. Etki sayısı tek başına öncelik değildir; gizli kayıtları açıklamaz. Dependency ve blocker yöntemden bağımsızdır; Scrum/PMBOK uygunluğu veya kritik yol hesabı iddiası yok. [Öncelik sözleşmesi](../product/priority-and-flow.md).

## 12. Yönetim yüzeyleri ve veri sınırları

```mermaid
flowchart TB
    USER[Günlük kullanıcı] --> APP[Inbox Board Graph Timeline]
    OWNER[Workspace veya proje yöneticisi] --> SETTINGS[Üye, grant, policy ve limit ayarları]
    OP[Kurulum veya platform operatörü] --> OPS[Operasyon merkezi]
    APP --> AUTH[Ortak kimlik, kapsam ve kaynak yetkisi]
    SETTINGS --> AUTH
    OPS --> AUTH
    AUTH -->|Yetkili proje query veya command| DOMAIN[Domain store ve projection]
    AUTH -->|Yetkili admin command| CONFIG[Sürümlü config ve audit]
    AUTH -->|Operasyon okuma| HEALTH[Redakte sağlık ve incident görünümü]
    DOMAIN -->|İçeriksiz sinyaller| HEALTH
    CONFIG --> POLICY[Etkin policy ve dispatch sınırları]
    SUPPORT[Süreli ve açık onaylı destek grant] -.-> AUTH
```

Operatör kimliği domain içeriğine otomatik izin değildir. Aynı servis önerilir; ayrı backoffice DB veya mikroservis zorunlu değil. P1b yerel owner sağlık/ayar görünümü, P4 ekip ve hosted operasyon konsolu. [Yönetim sözleşmesi](../product/administration-and-operations.md).

## 13. Hata müdahalesi ve config değişimi

```mermaid
flowchart TB
    ERR[Operasyon hatası] --> SAFE[Yazmadan önce redaction]
    SAFE --> INC[Kapsamlı incident ve güvenli fingerprint]
    INC --> TRIAGE[Etki, sorumlu ve inceleme]
    TRIAGE --> PLAN[Retry, pause veya ayar önizlemesi]
    PLAN --> GUARD[Yetki, revision, bütçe ve idempotency]
    GUARD -->|Geçti| APPLY[İşlem kaydı ve zorunlu audit]
    GUARD -->|Ret veya stale| HOLD[İşlem yapılmaz; neden görünür]
    APPLY --> HEALTH[Sağlık kontrolü ve çözüm kanıtı]
    HEALTH -->|Geçti| RES[Incident resolved]
    HEALTH -->|Başarısız| TRIAGE
    RES -->|Tekrarlandı| INC
    RES -.-> SEPARATE[Job ve task doğrulaması ayrı kalır]
    APPLY -->|Dış sonuç belirsiz| UNKNOWN[Önce reconciliation; kör retry yok]
```

Config apply beklenen revision ile atomiktir; rollback yeni revision olur. Dış istek yerel transaction'a alınamaz. Telemetry veya DB arızası kayıtsız başarı iddiası üretmez. [ADM kabul senaryoları](../product/administration-and-operations.md#planlı-kabul-senaryoları).

# Kalıcı model aktivasyonu — çalışan backend

**19 Ekim 2026 · T09/T17/T19/T21. Uygulanan yerel alt kapsam.** [Kod](../../packages/capture/model_activation.py), [test](../../tests/runtime/test_model_activation.py). Yeni kaynak okuma, API harcama veya sürekli izleme izni vermez. Kullanıcıya dönük kurulum ekranı ve zamanlayıcı henüz bağlı değildir; varsayılan LOCAL/TEST uygulaması model kapalı kalır.

## İş kuralı ve durumlar

Yalnız zaten verilmiş exact source/context/model/run grant'leri bir aktivasyonda toplanabilir. Oluşturma **Paused** durumundadır; ayrı insan komutu Active yapar. Kapsam10grant, history512event ile bounded; bunlar yerel uygulama tavanlarıdır, ölçülmüş kapasite/ürün SLA'sı değildir. Profil mevcut grant'lerden uzun yaşayamaz; yeni grant, root bütçe, token veya credential oluşturmaz. Aynı grant'in bir aktivasyona bağlandığı kalıcı olarak görüldükten sonra eski kontrolsüz extractor yolu da dispatch yapamaz.

```mermaid
flowchart LR
  accTitle: Kalıcı model aktivasyonunun durumları
  accDescr: Yeni konfigürasyon duraklatılmış başlar. Ayrı insan komutu geçerli kaynak ve yetkiyle etkinleştirir. Duraklatma tekrar açılabilir; iptal terminaldir. Süre ve yetki değişimi yeni çağrıları durdurur, kendiliğinden yenilenmez.
  G["Mevcut exact grantler<br/>Kaynak + context + model + bütçe"] --> P["Paused<br/>Yeni gönderim yok"]
  P -->|"İnsan: revision + config digest"| A["Active<br/>Yalnız izinli bounded queue pass"]
  A -->|"Pause"| P
  A -->|"Revoke"| R["Revoked<br/>Terminal; geçmiş korunur"]
  P -->|"Revoke"| R
  A -.-> E["Expired / Permission changed<br/>Etkin durum türetilir; otomatik yenileme yok"]
  P -.-> E
  classDef paused fill:#fef3c7,stroke:#92400e,color:#451a03
  classDef active fill:#dcfce7,stroke:#166534,color:#052e16
  classDef stopped fill:#fee2e2,stroke:#991b1b,color:#450a0a
  classDef source fill:#dbeafe,stroke:#1e40af,color:#172554
  class P paused
  class A active
  class R,E stopped
  class G source
```

Renkler tek başına anlam taşımaz; state labelleri metin olarak bulunur. Revoked profil eski kimliğiyle yeniden açılamaz. Yeni profil oluşturmak ayrı, açık insan işlemi ve mevcut geçerli source grant'leri gerektirir; eski iptal kaydı silinmez. Expired/Permission changed event geçmişinin değiştirilmesi değil, salt okunur etkin durumdur. Paused/Revoked komutu, yeni çağrıları kesmek için izin/expiry değişmiş olsa bile profil sahibince uygulanabilir.

## İşleme anı ve yarışlar

```mermaid
sequenceDiagram
  accTitle: Aktivasyon kontrolü ve model çağrısının transaction sınırı
  accDescr: Factory ön kontrolü yeterli değildir. Analiz transactionı güncel activation revision, kaynak grant, context ve bütçeyi kontrol eder. Kabul makbuzu commit edildikten sonra model dışarıda çağrılır. Sonradan duraklatma kabul edilmiş çağrıyı geri alamaz fakat sonraki çağrıyı keser.
  actor H as Yerel insan
  participant API as Command API
  participant DB as Workspace SQLite
  participant Q as Kuyruk / managed factory
  participant M as Yetkili transport
  H->>API: Active / Paused / Revoked + revision + config digest
  API->>DB: Human/project check + append-only activation event
  Q->>DB: Active + geçerli exact source grant ön kontrolü
  Q->>API: Kaynağı analiz et
  API->>DB: BEGIN IMMEDIATE ve aktivasyon revision yeniden kontrolü
  alt Durum, yetki veya context değişmiş
    DB-->>API: Yeni çağrı reddedilir, token rezervasyonu yok
  else Güncel ve izinli
    API->>DB: Bütçe rezervasyonu + analysis_started ve COMMIT
    API->>M: Transaction dışında tek model çağrısı
    Note over H,M: Bu noktadan sonra pause, dışarıdaki isteği geri çağıramaz
    M-->>API: Sonuç / hata / unknown usage
    API->>DB: Sonuç ve kullanım korunur, otomatik task apply yok
  end
```

Factory'nin seçtiği extractor aktivasyon ID/revision taşır; `ConversationService.analyze` bunu rezervasyonla **aynı transaction** içinde tekrar kontrol eder. Pause→resume sonrasında eski extractor da stale kalır. Duraklatma önce commit olduysa gönderim başlamaz. `analysis_started` önce commit olduysa in-flight sonuç/maliyet makbuzu korunur; sonraki kaynak bekler. HTTP200, Active durumu veya hazır öneri Task Done değildir.

## Backend API ve depolama

Mevcut session/Host/Origin/CSRF ve proje yetkili `POST /api/command` zarfı kullanılır; yeni anonim endpoint yok.

| action | Alanlar (`action` dışında) | Etki |
|---|---|---|
| `create_model_activation` | `activation_id`, `grant_ids`, `expires_at`, `reason` | Exact configuration/hash ile Paused kayıt |
| `change_model_activation` | `activation_id`, `base_revision`, `configuration_sha256`, `state`, `reason` | İnsan/proje/current revision kontrolüyle yeni event |

Kaynak grant'leri bu uçlardan oluşturulamaz. Görünüm `/api/state.model_activations` içinde selected-project metadata olarak okunur; grant_count, actor/authz revision, config digest, expiry, state/effective_state taşır; metin/anahtar taşımaz. `model_ready` yalnız transport yapılandırmasını anlatır, Active izni veya çalışmakta olan worker demek değildir.

Aynı Workspace DB `audit` tablosunda `conversation_model_activation` event'leri kullanılır; yeni tablo, migration veya event schema version artışı yok. Profil history ve exact grant referanslarının digest'leri kalıcıdır; credential/ham mesaj kopyalanmaz. Proje query/command yetkisi, backup/restore ve append-only rollback kuralları korunur. Audit512event kapasitesinde yeni değişim reddedilir; aktif görünse bile yeni dispatch dondurulur ve effective_state History capacity reached gösterilir. Böylece pause kaydı eklenemiyor diye model gönderimi açık kalmaz. Önceki kabul edilmiş kayıt silinmez; bakım kendi onaylı kapsamıyla ele alınmalıdır.

## Log ve geliştirme sınırları

Operations iki komutu extraction bileşeninde normal command span olarak izler. Safe reason code örnekleri: `activation_inactive`, `activation_required`, `stale_activation`, `activation_denied`, `activation_transition_denied`; raw reason/transcript/key loga yazılmaz. Queue kaynağı model/provider başlamadan bekletirse bu hata değil beklemedir. Activation görünümü nedenini gösterir; bütün pipeline için ayrı span varmış gibi sunulmaz.

13hedefli test: pause/active/resume/revoke, factory→admission yarışının engellenmesi, eski extractor, expiry/yetki değişimi, grant/expiry genişletme reddi, insan/agent/proje sınırı, idempotent create, restart+restore, audit rollback, eksik profil, in-flight yanıtın korunması ve legacy bypass engeli. Bütün provider çıktıları sentetik; gerçek API0. Arayüz butonları, background timer, sürekli izinli source/model onboarding ve günlük kullanıcı kabulü mevcut T09/T17/T19/T21 işlerinde açık kalır.

Nihai doğrulama:556runtime ve49kök/tracker testi geçti.13yeni hedefli test bunlara dahildir.52Mermaid blok offline render edildi; yeni iki diyagram görsel olarak incelendi. İlk sequence renderındaki metin ayraç hatası düzeltildi; başarısız koşular başarı diye kaydedilmedi. Bu tur gerçek provider çağrısı0, kaynak okuması0.

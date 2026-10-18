# Log, audit ve gözlemlenebilirlik

> [!NOTE]
> **Şema anahtarı:** mavi kaynak/işleme · sarı yetki/onay · turkuaz kalıcı bilgi · yeşil kanıt alanı · turuncu belirsizlik · gri tarihçe · mor öneri/gelecek. Renkler implementasyon veya test başarısı değildir. [Görsel sözlük](../quality/visual-documentation.md).

**14Ekim2026 — Yerel domain/audit ve sınırlı operasyon görünümü kodlandı; tam operasyon sözleşmesi öneridir.** Canonical değişikliklerle atomik, uygulama düzeyinde append-only audit; onay/grant/işlem makbuzları ve replay koruması vardır. UI son25güvenli hata kodunu yalnız süreç belleğinde gösterir; restart sonrası sıfırlanır. Ham istek/credential/prompt operational loga yazılmaz. Kalıcı redakte incident deposu, genel denied-access olay kapsamı, merkezi log/OTel, alert ve retention henüz tamamlanmadı. DB/OS yöneticisine karşı kriptografik değiştirilemezlik iddiası yok. [Güncel durum ve kanıt](../quality/security-current-status.md). Saklama sürelerinin tek referansı [veri yaşam döngüsü](storage-memory-capacity.md); erişim kuralları [kimlik/yetki modelidir](identity-access.md).

## 19 Ekim — güncel yerel uygulama

[Operations ekranı ve TEST ortamı](../quality/operations-runtime.md) kodlandı.200bounded command run/100safe HTTP error-group tutan ayrı private SQLite sidecar, request operation ID, authorization/dispatch span süreleri, persisted hata grupları ve degraded/lost/eviction görünümü var. Önceki paragraftaki25hata view'u eski session-only özettir; yeni ekran restart sonrası kayıtları korur. Tam receipt→job→model→review→evidence trace, merkezi OTel/alert/retention yönetimi ve security audit konsolu hâlâ açık. Operational row eviction canonical history'yi silmez.

## Dört kayıt sınıfı

| Sınıf | Amaç / örnek | Kalıcılık ve erişim |
|---|---|---|
| Source capture | Konuşma, import, tool gözlemi | Korumalı payload; gözlem onay/gerçek değildir. Kaynak ACL |
| Domain event log | Karar değişti, task yeniden açıldı, onay/verification | Canonical tarihçe; proje sequence ve revision; normal API append-only |
| Security audit | Davet, rol/grant değişimi, denied erişim, export, runner izni, veri çıkışı, purge | Ayrı güvenlik görünümü; sınırlı audit izni; domain içeriği/raw sohbet içermez |
| Operational telemetry | Hata, latency, queue lag, retry, adapter sağlığı, kullanım ölçümü | Redakte yapılandırılmış log/metric/trace; kısa retention; ürün doğruluğunun kaynağı değildir |

DB'nin WAL dosyası crash recovery içindir; insanın “kim, hangi yetkiyle ne yaptı?” sorusuna audit yanıtı değildir. Model prompt/completion kayıtları otomatik debug log olmaz. Gerekliyse ayrı kaynak deposu ve açık veri policy'si kullanılır.

## Yapılandırılmış alanlar

Her güvenlik kaydı: `audit_id`, schema, occurred/observed timestamp, server sequence, workspace/project, actor_type/id, on_behalf_of, grant/run/connection ID, action, resource_type/id, outcome (`attempted/succeeded/denied/failed/unknown`), güvenli reason_code, policy/authz revisions, request/correlation/trace ID. Kaynak/proposal digest referansı taşınabilir; serbest metin ve kişisel içerik taşınmaz. Wall-clock sırası domain append sequence'in yerine geçmez.

Operational log severity, component/version, trace/span, safe error code, duration ve retry count taşır. OpenTelemetry alan uyumu adaydır; collector/sağlayıcı seçilmiş değildir. [OTel veri modeli](https://opentelemetry.io/docs/specs/otel/logs/data-model/) telemetry'nin ortak biçimine referanstır; kendi başına audit deposu veya bütünlük garantisi değildir.

Credential, API key, authorization header, cookie, ham prompt, belge gövdesi ve hassas URL/query loglanmaz. Redaction export öncesine bırakılmaz; ilk yazımdan önce uygulanır. Kullanıcı girdisi escape/normalize edilir; log injection engellenir. Actor ID pseudonymous olabilir, anonim olduğu iddia edilmez. Metrics label'larına user/task ID koymak yerine düşük cardinality kategoriler kullanılır; trace'e erişim ayrıca sınırlandırılır.

## Transaction ve arıza davranışı

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Arial, sans-serif","fontSize":"14px","primaryColor":"#eff6ff","primaryTextColor":"#0f172a","primaryBorderColor":"#1d4ed8","lineColor":"#64748b","secondaryColor":"#ccfbf1","tertiaryColor":"#f1f5f9","background":"#ffffff","mainBkg":"#eff6ff","textColor":"#0f172a","clusterBkg":"#f8fafc","clusterBorder":"#94a3b8","edgeLabelBackground":"#ffffff","actorBkg":"#eff6ff","actorTextColor":"#0f172a","actorBorder":"#1d4ed8","signalColor":"#64748b","signalTextColor":"#0f172a","noteBkgColor":"#fef3c7","noteTextColor":"#0f172a","noteBorderColor":"#92400e"},"flowchart":{"htmlLabels":false,"curve":"linear"},"sequence":{"wrap":true},"themeCSS":"background-color:#ffffff;"}}%%
sequenceDiagram
    accTitle: Atomik audit ve ayrı dış teslim
    accDescr: Önerilen tasarım veya açıkça belirtilen sentetik örnek. Renkler alan ve kontrol türünü gösterir; implemented veya passed kanıtı değildir. Yetki, revision ve coverage sınırları korunur.
    autonumber
    participant C as İstemci
    participant P as Policy ve command
    participant D as Kalıcı DB
    participant W as Outbox worker
    participant X as Dış hedef
    Note over C,D: Source, domain, audit ve dış delivery ayrı kayıtlardır
    rect rgb(239, 246, 255)
    C->>P: Kimlikli ve revision bağlı istek
    P->>P: Güncel yetki ve input kontrolü
    alt İzin yok
        P->>D: Sınırlı denied audit
        P-->>C: Güvenli ret
    else İzin var
        P->>D: Atomik domain event + projection + audit + outbox
        D-->>P: Commit sonucu
        P-->>C: Commit başarılıysa yerel sonuç
        W->>D: Due item ve lease
        W->>W: Dispatch anında yetkiyi tekrar kontrol et
        W->>X: İzinli outbox teslimi
        X-->>W: Sonuç veya belirsiz cevap
        W->>D: Ayrı delivery sonucu ve audit
    end
    end
```

Yüksek etkili başarılı permission/approval/export/purge işlemlerinin audit kaydı aynı yerel transaction'da kalıcı olmalıdır; yazılamıyorsa işlem de commit olmaz. Export/veri çıkışı için dispatch intent önce kalıcıdır; dış servis yerel transaction'a alınamaz. Sonuç kaydı başarısızsa intent reconciliation ile `unknown` olarak izlenir; teslim edildiği varsayılmaz. Domain olayları ile audit farklı tablolar olsa da aynı correlation üzerinden bulunur.

Denied istek zaten durum değiştirmez. Audit diski dolsa bile erişim açılmaz. Tekrarlanan saldırı istekleri rate-limit ve sınırlı aggregate kayıtla tutulur; aggregate sayacı/dropped-count görünür, eksiksiz olay tutma iddiası yapılmaz. Operational telemetry arızasında bounded buffer ve drop counter kullanılabilir; domain/audit gerektiren başarı sessizce düşürülemez. Audit exporter kesintisi yerel kalıcı audit'i kaybetmez; outbox tekrar dener, disk high-watermark yeni pahalı işler için backpressure üretir.

## Bütünlük ve inceleme

[Operasyon sözleşmesi](../product/administration-and-operations.md) incident alanlarını, open/mitigated/resolved/reopened ayrımını, güvenli retry/pause ve config audit'ini tanımlar. Incident kapanması domain task'ını veya failed job'ı tamamlamaz. Ortak fingerprint farklı tenant içeriğini birleştiremez. DB arızasında kalıcı hata yazılamayacağı durum ayrı degraded health ve kayıt boşluğuyla görünür olur; logger çalışıyor varsayılmaz. ADM-05–09 doğrulaması planlıdır.

Normal insan/agent API'si event/audit satırı UPDATE/DELETE etmez. Authorized privacy purge ayrı rol, gerekçe, policy ve silinen veri sınıflarının minimal tombstone kaydını gerektirir. Hash zinciri ve bağımsız saklanan imzalı/checkpoint kopyaları değişiklik tespitine yardımcıdır; DB, anahtar ve checkpoint'leri yöneten kişinin tüm müdahalelerini engellediği iddia edilmez. Harici immutable storage ve anahtar ayrımı ekip/hosted aşamasında maliyet ve tehdit modeline göre değerlendirilecek.

Proje timeline'ı tüm security audit'i göstermez. Project reviewer yalnız izinli karar zincirini; ayrı workspace auditor yetkisi üyelik/erişim hareketlerini görür. Audit izni ham özel sohbeti okuma hakkı vermez. Download/export işlemi de audit'lenir. Platform operasyon ekibi tenant içeriğini sıradan hata logundan görememeli.

İlk operasyon paneli için gereken sinyaller: capture coverage ve son receipt; pending/failed/quarantine iş sayısı/yaşı; writer wait ve transaction latency; stale approval oranı; rejected auth; model token/usage unknown oranı; WAL/disk/backup yaşı; audit export lag. Uyarı bütçesi ve eşikleri pilot baseline sonrası belirlenir. Health endpoint hata detayı/tenant adını halka açmaz. Doğrulama: MU08, MU09, MU15 ve mevcut V17/V19/V26/V27.

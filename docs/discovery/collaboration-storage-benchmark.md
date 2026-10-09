# Ekip, agent yetkileri ve hafıza benchmark'ı

İnceleme: **2026-10-09**. Yöntem: aşağıdaki birincil belgelerin okunması; ürünler kurulup yetki/yük testi yapılmadı. `D` belgelenen davranış; `Ö` Decivora için öneri. Ürünlerin pazarlama iddiası runtime doğrulaması değildir. Kod, şema veya prompt kopyalanmadı; dış bağımlılık eklenmedi.

| Kaynak ve doğrudan kanıt | D: belgede görülen örüntü | Ö: Decivora'da uygulanacak tasarım | Sınır / karar |
|---|---|---|---|
| [Linear roller](https://linear.app/docs/members-roles) | Workspace/team rolleri ve davetli takımlarla sınırlı guest erişimi | Workspace yönetimini proje içeriği erişiminden ayır; guest'e açık proje listesi göster | Plan/fiyat kıyası yapılmadı; Decivora rolleri birebir kopya değil |
| [Linear private teams](https://linear.app/docs/private-teams) | Üyelik ve entegrasyonlar private içeriğin erişim sınırını etkiler | Connector ve paylaşım önizlemesi; workspace admin'e sessiz private okuma verme | UI görünürlüğü tek başına connector sızıntısını engellemez |
| [Linear audit](https://linear.app/docs/audit-log) | Aktör/işlem/zaman bilgisiyle yönetim olaylarını inceleme ve export | Ayrı security audit görünümü, export'un kendisini de kaydet | Enterprise özelliği olduğu için yerel üründe aynı kapsam var sayılmaz |
| [GitHub user access tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app) | User adına erişim uygulama ile kullanıcının yetkilerinin kesişimiyle sınırlı | Agent'ın kendi grant'i ve insanın güncel yetkisi birlikte gerekli | Dış token kapsamı iç ürün onayı yerine geçmez |
| [GitHub installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app) | İzin/repository kapsamı daraltılabilir | Connector ve agent için resource allowlist; tüm hesap yetkisini devretme | Token yalnız vault/ref ile tutulacak |
| [OpenFGA roles](https://openfga.dev/docs/modeling/roles-and-permissions) | Roller üzerinden nesne permission'ları modellenir | Uygulama role string yerine `can_approve(resource)` kontrol eder | OpenFGA servis bağımlılığı bugün seçilmedi |
| [OpenFGA agents](https://openfga.dev/docs/modeling/agents/agents-as-principals) | Agent ayrı principal olabilir; task kapsamı ayrıca daraltır | İnsan ve agent ayrı ID; run ve delegation zinciri | Bizde insan karar onayı agent'a verilemez; referans örneğinin her rol mirası alınmaz |
| [OpenFGA RAG](https://openfga.dev/docs/modeling/agents/rag-authorization) | İzinli belgeler LLM context'ine girmeden filtrelenir | Source ACL, summary/index/cache ve export'a kadar taşınır | Yalnız sonuç ekranındaki filtre yeterli değil |
| [Cortex](https://github.com/gsl0001/Cortex) | Yerel SQLite ve watch/plan/assist/auto gibi autonomy düzeyleri; protected repo sınırları | Otonomi policy'si, ayrı runner izni ve proje koruması | Otonomi düzeyi insan üyeliği/RBAC kanıtı değildir |
| [mai-mcp](https://github.com/maikai-group/mai-mcp) | MCP bağlantısında tek proje; bounded reads; advisory agent claims; opt-in paylaşım | Project-bound session, context bütçesi, claim/yetki ayrımı | Claim dosya izolasyonu sağlamaz; worktree/sandbox ayrıca gerekir |
| [Letta stateful agents — V1/legacy](https://docs.letta.com/v1-sdk/concepts/stateful-agents) | In-context memory blokları ile kalıcı mesaj geçmişi farklı; bloklar paylaşılabilir | Geçici context ile kalıcı hafıza farklı tabloda/policy'de | Legacy kavramsal referans; güncel SDK entegrasyonu önerisi değil; ortak hafıza ACL'si ayrıca tasarlanır |
| [SQLite kullanım](https://www.sqlite.org/whentouse.html) · [WAL](https://www.sqlite.org/wal.html) | Yerel depolama; aynı DB'de tek writer; WAL aynı host koşulları | P1 local DB, kısa transaction, DB dosyasını ağdan paylaşmama | Kullanıcı sayısından performans sonucu çıkarılmadı |
| [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | Satır policy'leri; owner/superuser bypass sınırları | Ekipte API kontrolü + nonowner uygulama DB rolü + tenant izolasyonu | RLS açmak tek başına tenant güvenliği sağlamaz |
| [SQLite backup](https://www.sqlite.org/backup.html) · [Postgres PITR](https://www.postgresql.org/docs/current/continuous-archiving.html) | Tutarlı snapshot; server DB'de base backup/WAL ile recovery | DB+blob manifest, restore drill, purge ve grant reconciliation | Bu repoda yedek sistemi kurulmadı |
| [OpenTelemetry log modeli](https://opentelemetry.io/docs/specs/otel/logs/data-model/) | Timestamp, trace/span ve severity gibi ortak alanlar | Yapılandırılmış operational log; audit ayrı doğruluk/retention sınırı | Telemetry standardı güvenlik audit'i veya saklama servisi değildir |

## Karara dönüşen sonuçlar

1. **Adopt:** Tekil principal, nesne/işlem kontrolü, dar grant, project-bound session ve model öncesi yetki filtresi → [identity-access](../architecture/identity-access.md).
2. **Adapt:** Rol preset'leri ve autonomy seviyeleri karar farkındalıklı onay sözleşmesiyle birleşir. İnsan onayı, kanıt kaydı, runner çalıştırma ve dış sistem yazma ayrı izinlerdir → [ADR-0009](../architecture/adr/0009-scoped-principals.md).
3. **Adopt:** Kalıcı event/provenance ile yeniden üretilebilir context/index ayrımı; küçük yerel DB ve ölçümle ölçek geçişi → [hafıza/kapasite](../architecture/storage-memory-capacity.md).
4. **Defer:** Custom role builder, merkezi authorization servisi, çok bölgeli veri, gerçek zamanlı offline multiwriter sync, dedicated vector DB → talep/ölçüm kapısından önce bağımlılık değil.

Bu, “rakiplerden daha güvenli/hızlı” sonucu değildir. Hedeflenen birleşim; kimin hangi kararı onaylayabildiğini, değişimin hangi işleri etkilediğini ve sonucu hangi kaynağa dayanarak gördüğünü aynı izlenebilir zincirde yönetmektir. [MU senaryoları](../quality/collaboration-validation.md) bu hipotezin uygulanabilir kabul ölçütleridir.

Önceki Beads, Task Master, OpenSpec, Claude Task Tracker ve Beads UI karşılaştırmaları [ana benchmark'ta](benchmark.md) korunur. Bunların görev/bağımlılık veya UI yetenekleri multi-tenant IAM desteğinin kanıtı olarak kullanılmadı. Bu hedefli tarama erişim, veri yaşam döngüsü ve operasyon kararlarına odaklanır; kapsamlı IAM ürün sıralaması değildir.

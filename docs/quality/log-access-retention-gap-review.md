# Log erişimi, kimlik ve saklama — repo/kod boşluk incelemesi

**19 Ekim2026 — salt okunur ürün/uygulama analizi.** Kullanıcı “bu bilgiler repoda var mı, eksik var mı?” diye sordu. Mevcut dokümanlar, operational SQL, HTTP yetki sınırı ve ilgili test kaynakları karşılaştırıldı. Bu kayıt yeni erişim/retention kararı, security policy istisnası veya yeni runtime teslimi değildir. Güvenlik taraması/pentest veya gerçek çok kullanıcılı test yapılmadı.

**Sonuç:** bilgiler büyük ölçüde var, fakat kimlik/rol, yönetim, saklama ve mevcut log rehberleri arasında dağılmış. Çalışan local tek-kullanıcı görünümü ile önerilen ekip görünümü ayrılmalıdır. Çok-kullanıcılı log yetkilendirmesi tamamlanmış değildir; sırf login ekranı eklemek bu eksikleri çözmez. Aşağıdaki LG kimlikleri bulgu referanslarıdır, yeni backlog/task otoritesi değildir.

## Kullanıcının soruları mevcut repoda nerede?

| Soru | Mevcut kaynak | Kod/uygulama sonucu |
|---|---|---|
| Loga nasıl girilir, ayrı kullanıcı adı mı? | [Operations kullanım/kapsamı](operations-runtime.md), [kimlik](../architecture/identity-access.md), [ekip işletimi](../architecture/agent-and-team-operation.md) | Yerel başlatıcı/bootstrap session ve Operations menüsü var; HTTP principal `local_owner`. Ayrı insan login hesapları, IdP/davet/recovery tamamlanmadı. Log için ikinci hesap sistemi seçilmiş değil |
| Ben başkasının logunu görebilir miyim, o benimkini görebilir mi? | [Rol/özel kaynak matrisi](../architecture/identity-access.md#varsayılan-rol-matrisi), [yönetim kapsamı](../product/administration-and-operations.md) | Genel least-privilege ve private kaynak ilkeleri var. Operational trace için own/shared/project/installation/support görünürlük matrisi tam ve kabul edilmiş uygulama sözleşmesine dönüşmedi |
| Kurucu bütün kurulumları görebilir mi? | [Yönetim merkezi](../product/administration-and-operations.md) | Başkasının self-host kurulumuna gizli merkezi admin/telemetry tasarlanmıyor. Yerel log store için remote collector yok. Managed support kapsamı ileriki faz; normal kullanıcıya kurucunun private kurulumuna hak verilmez |
| Hangi DB? | [Fiziksel ER ve şema rehberi](../architecture/logging-diagrams-and-schema.md#3-gerçek-fiziksel-diagnostics-veri-modeli), [logging](../architecture/logging-audit.md) | Canonical `workspace.sqlite`, ayrı `workspace.operations.sqlite`. LOCAL/TEST ayrı dosya/dizin. Operational rows canonical audit değildir |
| Ne kadar saklanır? | [Çalışan sınırlar](operations-runtime.md#coverage-and-limits), [onaylanmamış süre önerileri](../architecture/storage-memory-capacity.md) |200run/100error-group sayısal sınır; görünüm50project run/25installation group. Gün/TTL temizliği ve production retention yönetimi yok.30gün operasyon/7gün debug/90gün audit satırları onaylanmamış pilot önerileridir |
| Session ID var mı? | [Fiziksel/API şema rehberi](../architecture/logging-diagrams-and-schema.md), [kimlik tasarımı](../architecture/identity-access.md) | Per-command operation ID + internal logger instance session var. Browser session cookie ayrı; raw secret loglanmaz. User login session/agent run/pipeline correlation mevcut trace'e bağlanmış değil |
| Alanlar/kapsam nedir? | [DTO alan sözlüğü](../architecture/logging-diagrams-and-schema.md#4-api-şeması-alanlar-nasıl-yorumlanır), [JSON şeması](../../manifests/local-operations.schema.json) | Action/component, iki command sınırı, zaman/süre/outcome/safe code, HTTP group count, coverage/loss/eviction var. Actor/tenant/grant/engine version/causation köprüsü eksik |

## Doğrudan kod kanıtı ve çıkarım sınırı

- [LocalApp.operations_view](../../apps/local_ui/server.py) principal'ı `core.authority.issue_scope('local_owner')` ile çözer; güncel human project scope ve active kontrol eder. HTTP session/Host/Origin sınırı da uygulanır. Bu, herkese açık log endpoint'i değildir; fakat bağımsız multiuser session principal çözümlemesi veya loga özel role permission değildir.
- [LocalOperations](../../packages/operations/local.py) run'ları `project` ile filtreler. `op_runs` alanları: id, logger session, project, action, component, started/finished/duration, outcome/code. Actor/user/agent/on_behalf_of/grant/workspace alanları yoktur. Dolayısıyla bu tablo üzerinden “yalnız kendi kullanıcı izleri” filtresi uygulanmış sayılmaz.
- Error grupları kurulum genelinde `(endpoint,code)` ile birleştirilir; mevcut tek kişilik kullanım için içeriksiz bir özettir. Ayrı tenant/agent/user veya trace join'i yoktur. Bu tasarım paylaşılan ekip/hosted konsoluna aynı haliyle taşınamaz.
- [Operations testleri](../../tests/runtime/test_operations.py) proje izolasyonu/revocation, oturum gereksinimi, redaksiyon, restart, eviction ve LOCAL/TEST cookie ayrımını içerir. Bunlar bağımsız iki insanın kendi/başkasının logu, security auditor rolü veya süreli support grant doğrulaması değildir.
- [Schema guide ER](../architecture/logging-diagrams-and-schema.md) bugünkü fiziksel yapıyı doğru anlatır; olmayan actor kolonlarını veya cross-database FK'leri göstermediği için bu bir çizim hatası değildir. Yeni alan/permission tasarımı kabul edilip kodlandığında SQL/DTO/test/diagram birlikte güncellenmelidir.

## Eksikler ve ne zaman engel oldukları

| Bulgu | Gerçek eksik | Öncelik / kapı | Mevcut sahiplik ve doğrulama |
|---|---|---|---|
| LG-01 | İnsan login principal'ı ve agent kimliğini log okuma/yazımına bağlama | **Ekipte ilk kullanım öncesi zorunlu.** Tek-owner yerel geliştirmeyi durdurmaz | T05b/T08b + C01/C03. İki bağımsız insan oturumu ve agent; aktör metni istemciden taklit edilemez; revocation yeni okuma/dispatch'i durdurur |
| LG-02 | Operational loga özel own/project/installation/audit/support görünürlük politikası ve server-side enforcement | **Ortak log ekranını açmadan zorunlu.** Normal proje okuma ile her log görünümü eşitlenmemeli | T20f/T08b + C03/C05. Kendi/başkasının shared/private izi, admin olmayan kullanıcı, security auditor ve expired support için pozitif/negatif API testleri |
| LG-03 | Güvenilir actor_type/id, workspace kapsamı, on_behalf_of, grant/authz revision ve gerekirse kaynak erişim bağları | **Çok-agent attribution veya ortak servis öncesi zorunlu.** Canonical audit'te actor olması operation trace'teki eksikliği otomatik kapatmaz | T07b/T08b/T20f + C02/C04/C05. Kimlik/grant trusted context'ten gelir; farklı kiracı/proje aynı ID ile karışmaz; private-derived log/diagnostics yetki genişletmez |
| LG-04 | Operation/logger session ile login-session referansı, agent run, root correlation/causation ve command/event/evidence bağları | **İlgili native/model zinciri işletilmeden gerekli.** Loga ham cookie/token eklenmez | T20f/T21c/T16/T17. Çok command'lı zincir bulunur; root/child ayrı kalır; unknown/retry yeni başarı veya çift yan etki üretmez |
| LG-05 | Gün bazlı onaylı retention, pin/expiry policy revision, cleanup açıklaması ve audit/operational ayrımı | **Production veya gerçek ekip saklama taahhüdünden önce zorunlu.** Mevcut200/100bounded preview policy bunun yerine geçmez | OPEN-08/T23c/T21c. Süreler kullanıcıca seçilir; expiry/eviction görünür; canonical audit ve unresolved source/task geçmişi sessiz budanmaz |
| LG-06 | Diagnostics backup/restore/purge ve access-revocation sürekliliği | **Recovery/retention işletimi öncesi gerekli.** Mevcut workspace ZIP diagnostics sidecar'ını kapsamıyor | T23c/T23d/T23e + C05. Restore edilmiş loglar eski üyeye erişim açmaz; sidecar eksikliği açıklanır; log/backup türevlerinde purge sınırı korunur |
| LG-07 | Tenant/proje kapsamlı hata agregasyonu, saklama kotası/fairness ve log okuma kaydının kendi denetimi | **Çok-kullanıcılı/hosted ortam öncesi gerekli.** Şimdiki global200run başka projelerin eski izlerini de düşürebilir; bu local dev sınırı açıktır | T20f/T23c + C05/C06. Bir tenant diğerinin tanı geçmişini silemez/göremez; private iş yükü çıkarımı sınırlandırılır; log/audit export ayrı kontrol edilir |
| LG-08 | Ekip log kabul matrisi ve operatör pilotu | **İlgili ekip/çok-agent kapısında zorunlu.**382runtime geçmesi bu henüz olmayan senaryoların geçtiği anlamına gelmez | T24g + C03/C05/C06. Aşağıdaki visibility senaryoları, grant sona ermesi ve agent sponsor değişimi bağımsız olarak doğrulanır |

Bu eksikler gerçek gereksinimdir; bugünkü tek kişilik ürünün var olan loglarını “bozuk” diye yeniden sınıflandırmaz. Aynı şekilde bunları yalnız future başlığına koyup ekip/native entegrasyonda kontrol etmeden açmak doğru değildir. Her biri ilk kullanım kapısına bağlı kalır; parent görevler bu raporla Done olmaz.

## Görünürlükte karara bağlanmamış ayrıntılar

Aşağıdaki alanlar mevcut ilkelere uyacak şekilde **netleştirilecek**; yeni role izin vermek bu analizin kapsamı değildir:

1. Normal proje üyesi varsayılan olarak yalnız kendi command izini mi, içeriksiz ortak proje tanısını da mı görecek? Task history/domain provenance erişimiyle operational log erişimi ayrı tanımlanmalı.
2. Project admin veya workspace admin'in başka kişinin operational izine erişimi hangi iş gerekçesi ve görünür audit ile verilecek? Private kaynak yetkisi otomatik genişlememeli.
3. Log okuma, filtreleme, toplu export ve support geçici erişimi için farklı yetkiler gerekli mi? “Auditor” tek etiketle bütün kaynakları açmamalı.
4. Kullanıcı ayrıldığında actor ID/provenance ne kadar tutulacak; isim/personel alanlarının silinmesi ile olay kimliğinin korunması nasıl ayrılacak?
5. Operasyon/debug/audit için gün ve kapasite sınırı, pin ve yedek süreleri hangi pilot profilinde kabul edilecek? Eski30/7/90önerisini kullanıcı seçimi diye kaydetme.

Bugün owner-only log geliştirmesini durduran yeni bir karar gerekmiyor. Bu tercihlerin yanıtı, ilgili ekip/prod/native kullanım kapısı açılmadan alınmalı; ücret/connector/ham veri izni bu rapordan çıkarılmaz. [Açık kararlar](../governance/open-decisions.md), OPEN-08 ve [C01–C06 ekip kapıları](../delivery/team-data-plan.md) mevcut otoritelerdir; duplicate soru/task oluşturulmadı.

## Test kapsamına eklenecek kabul senaryoları

Bunlar **planlı**, çalıştırılmış sonuç değildir:

- Aynı projede iki insan: kendine ait/ortak/private operational kayıtları politika kadar görünür; alan maskelemesi ile yalnız menü gizlemek ayrıdır.
- Bir projedeki admin başka proje/tenant logunu veya private source ref'ini otomatik göremez. İzinli proje metadata'sı ham özel conversation grant'i değildir.
- Platform/support operatörü kuruluma/tenant'a göre sınırlanır; zamanlı grant bittiğinde query/cursor/export tekrar reddedilir. Self-host kurucuya varsayılan remote erişim açmaz.
- Agent logunda agent, sponsor/on_behalf_of ve kullanılan grant ayrıdır; insan onayı taklit edilemez. Agent'ın bütün workspace loglarını okuması varsayılan değildir.
- Login session kapansa/revoke olsa da eski logger instance/operation ID yeniden giriş veya veri yetkisi sağlamaz.
- Retention/restore sonrası güvenlik ve domain provenance korunur; istenen dönemin eksikliği visible coverage olur. Bir tenant'ın yoğunluğu diğerinin zorunlu audit'ini budamaz.

## Belge düzenindeki eksikler

- Kullanıcı sorularına cevap veren tek bir log-access overview yoktu; bu inceleme kaynakları ve uygulama boşluklarını bir araya getirir. Genel rollerin mevcut tasarım olması, son konuşmadaki daha ayrıntılı own/shared matrisi kabul edilmiş demek değildir.
- [Backlog yönetim alt dilimleri](../delivery/backlog.md#yönetim-merkezi-ve-hata-takibi-alt-dilimleri) başındaki eski “tümü TODO/çalışan panel değildir” metni artık T20f IN_PROGRESS ve çalışan Operations ile güncel değildir. Düzeltme ihtiyacı kaydedildi; runtime iş sayısı bu metinden hesaplanmamalı.
- Saklama tablosunun başlığı süreleri zaten açıkça onaylanmamış olarak işaretliyor. Bu bir gizli TTL uygulanması veya kesin contradiction değil; çalışan200/100sınırı ile aynı yerde çapraz referans faydalı.
- ER/DTO bugünkü alanları doğru yansıtıyor. Henüz olmayan actor/tenant/role/TTL alanları mevcut şemaya sessizce eklenmedi. Tasarım kabulü, veri migration'ı, erişim guard'ı ve negatif test kendi uygulama işidir.

## İnceleme sınırı

Mevcut repo kaynakları ve test kodu okundu; yeni multiuser runtime, provider/model deneyi, security scan veya canlı kullanıcı verisi sorgusu yapılmadı. Runtime kodu, log erişimi, retention parametreleri, SQL/JSON şeması ve Mermaid kaynakları değiştirilmedi. Belge/link/anchor ve mevcut plan tutarlılığı hedefli doğrulanır; geçmiş test/render sayıları yeni sonuç diye sunulmaz.

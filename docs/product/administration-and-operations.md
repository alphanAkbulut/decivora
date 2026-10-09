# Yönetim merkezi ve sistem işletimi

**2026-10-10 — Önerilen tasarım; ekranlar, yetkiler ve hata servisi uygulanmadı.** Kullanıcı ihtiyacı: ürün sahibinin sistemi yönetebilmesi, günlük kullanıcıların uygun yetkiyle çalışması, hata ve parametrelerin görünür olması. Mevcut TEAM-01/GOV-01/AUD-01/CST kapsamının ayrıntısıdır. Yönetici olmak bütün konuşmaları okuyabilmek veya ürün kararlarını atlayabilmek değildir.

## Üç görünüm, ortak yetki katmanı

| Görünüm | Kim kullanır? | İçerik |
|---|---|---|
| Çalışma alanı | Günlük kullanıcı; projedeki rolüyle | Inbox, görevler, karar grafiği, kaynak/kanıt, kendi bağlantıları, izinli kullanım bilgisi ve anlaşılır hata |
| Workspace / proje ayarları | Kapsamına göre owner/admin | Üyeler, agent grant'leri, connector kapsamı, bütçe, analiz profili, review ve retention policy'si |
| Kurulum / operasyon merkezi | Yerel kurulum sahibi; ileride bizim işlettiğimiz servisin yetkili operatörü | Servis sağlığı, olay/incident takibi, kuyruklar, disk/yedek, sürümler, sistem tavanları, audit teslimi |

Öneri aynı web uygulamasında yetkiye göre açılan bölümlerdir; ortak yetkili API kullanılır. Menü gizlemek erişim kontrolü değildir: her endpoint, export, arama ve stream kontrol edilir. Backoffice ikinci bir proje veritabanı veya başlangıçta ayrı mikroservis olmaz. Codex/Claude Code entegrasyonu yönetim konsolunun yerine geçmez. Operasyon görünümü ham kullanıcı bağlamını dışarı çıkarmaz.

Tek kişilik kurulumda aynı kişi owner ve kurulum yöneticisi olabilir; arayüz hangi kapsamda işlem yaptığını gösterir. Ekipte bu sorumluluklar ayrılabilir. Kurucu olarak yalnız bizim işlettiğimiz kurulumlarda verilmiş operasyon yetkimiz olur. Başkasının self-host kurulumuna gizli merkezi admin, zorunlu telemetri veya uzaktan kapatma erişimi tasarlanmıyor.

## Kullanıcı seviyesi yerine kapsamlı roller

| Kimlik / rol | Önerilen yetki | Sınır |
|---|---|---|
| Installation administrator | Kendi kurulumunda güncelleme, yedek/restore, servis ve kapasite ayarı | Uygulama üzerinden tenant içeriği için ayrıca kaynak yetkisi gerekir; OS/DB sahibi fiziksel olarak daha güçlüdür |
| Platform operator — gelecek managed servis | Sağlık, redakte hata, kapasite, tenant kota tavanları | Varsayılan ham konuşma/kanıt okuma veya kullanıcı taklidi yok |
| Workspace Owner / Admin | Owner sahiplik ve policy; Admin delegasyonla üyelik/operasyon | Private proje/kaynakları otomatik okuyamaz; son owner ve yükseltme kuralları korunur |
| Proje Owner / Maintainer / Contributor / Reviewer / Viewer | [Mevcut rol matrisindeki](../architecture/identity-access.md) görev ve karar işlemleri | Proje rolü kurulum yönetimi yetkisi değildir |
| Agent / system principal | Adlandırılmış, süreli, proje/task/run kapsamlı grant | İnsan approval'ı, rol yönetimi ve purge devredilmez |

“1. level user” günlük kullanıcı anlamındaysa normal proje rolüdür; düşük bir insan seviyesi değildir. Destek ekibi **L1** anlamındaysa ayrı bir gelecek preset önerilir: redakte hata kodu/servis durumu görür, ticket sınıflar; içerik, secret, restore, replay ve yetki değiştirme hakkı yoktur. L2/L3 kıdemi otomatik daha fazla veri izni sağlamaz; gereken işlem ayrıca grant ister. Bu presetler MVP gereksinimi değildir.

Free/Pro/Enterprise gibi olası paketler rol değildir. Ücretli kullanıcı başka projenin verisini okuyamaz; admin olmak harcama limitini kaldırmaz. Paket/koltuk fiyatlandırması seçilmedi.

## Yönetici ne görecek?

1. **Sağlık:** capture coverage ve boşlukları, son receipt, adapter/build desteği, worker durumu, kuyruk yaşı, failed/quarantine sayısı. Servisin ayakta olması bütün kaynakların alındığı anlamına gelmez.
2. **Maliyet ve sınırlar:** bilinen tüketim, tahmin, unknown usage, ayrılmış fakat sonuçlanmamış bütçe, defer nedeni, storage/queue tavanları. Host model tüketimi ile Decivora arka plan analizi ayrı.
3. **Hatalar ve kurtarma:** incident listesi, güvenli hata kodu, etkilenen bileşen/sürüm, başlangıç/son görülme, tekrar sayısı, redakte correlation, atanan operatör ve doğrulama kanıtı.
4. **Erişim ve değişiklikler:** yetki reddi, grant iptali, policy sürümleri, admin işlemleri ve audit export gecikmesi; içerik erişimi ayrıca denetlenir.
5. **Veri güvenilirliği:** disk/WAL baskısı, son yedek ve başarılı restore tatbikatı, migration/schema sürümü, purge manifest durumu. Yedek alınması restore'un test edildiği anlamına gelmez.

Günlük kullanıcı bunun yalnız kendi izinli işlerini etkileyen bölümünü görür: “analiz bütçe nedeniyle bekliyor”, “bağlantı yeniden yetki istiyor”, “sonuç henüz bilinmiyor” ve destek referansı. Başka workspace adı, kaynak başlığı veya stack trace gösterilmez. Global metriklerde düşük cardinality ve içeriksiz toplamlar; workspace detayı ayrıca scope kontrolü gerektirir.

## Hata takibi ve incident yaşam döngüsü

Operational telemetry, security audit ve domain event farklı kayıtlardır; [log sözleşmesi](../architecture/logging-audit.md) geçerlidir. Logger/OTel uyumu adaydır; Sentry veya başka ücretli servis seçilmedi. İlk sürüm yerel yapılandırılmış log ve basit sağlık/hata görünümüyle başlayabilir.

Önerilen `Incident`: ID, scope, güvenli fingerprint (component + error_code + version), severity, first/last_seen, count, owner, status, safe trace refs, affected capability, mitigation, resolution evidence. Tenant'a özgü kayıtlar tenant kapsamında gruplanır; global aynı hata kategorisi içeriksiz aggregate olabilir. Redaction **ilk yazımdan önce** yapılır; prompt, token, credential ve kişisel veri loga giremez. Incident ayrıntı retention'ı operational sınıfa bağlıdır; incident açmak kaynak arşivini veya logu süresiz tutmaz.

Akış: `open → acknowledged → investigating → mitigated → resolved`; kalıcı çözüm doğrudan investigating'den resolved'a da geçebilir. Tekrar görülürse yeni occurrence ile `reopened`. Mitigated etkisi azaltıldı, resolved ise tanımlı sağlık kontrolü/kanıt geçildi demektir. **Incident kapanınca failed job, blocked task veya verification otomatik completed olmaz.** Severity hizmet etkisidir; task önceliğine etki önerisi olabilir fakat DEC-17 kararının yerine geçmez. Uyarı eşikleri baseline sonrası; bugün SLA/on-call süre garantisi yok.

| Müdahale | Güvenli davranış |
|---|---|
| Pause / resume | Capture, analiz veya dış delivery kapsamı ayrı seçilir. Duraklatılan aşama görünür; bounded spool dolunca yeni receipt verilmez. Gerçek host stop desteği yoksa harici agent durdu denmez |
| Retry | İzin, sürüm, idempotency, retry bütçesi yeniden denetlenir. Belirsiz dış sonuç önce reconcile edilir; kör yeniden gönderim yok |
| Quarantine incele | Hata nedeni ve görünür kanıt incelenir; proposal düzeltmesi yeni sürüm olur. Admin SQL editörü yok |
| Replay / restore | Restore taslağı, tutarlı snapshot, purge manifest ve yetki doğrulaması; dış delivery kapalı. Replay LLM/verifier/dış yazma tetiklemez |
| Destek paketi | Kullanıcı önizlemesi ve ayrı export yetkisi; redakte, süreli erişimli. Otomatik üçüncü taraf upload yok |

Audit gerektiren admin mutasyonu audit yazılamıyorsa commit olmaz. Telemetry kaybı bounded buffer/drop sayacıyla görünür. DB/disk arızasında aynı DB'ye incident yazılamayabilir: yerel güvenli health sinyali ve sınırlı emergency buffer kullanılır; kalıcı kayıt başarısı iddia edilmez. İyileşince kayıp aralığı açıklanır. Hosted alert kanalı/provider ve on-call sorumluluğu C05/C06 kararıdır.

## Parametre sicili ve değişiklik yönetimi

Her parametre: `key, type, unit, allowed_range, default_source, scope, effective_value, inherited_from, locked_reason, policy_revision, effective_at, restart_required`. Secret'ın kendisi değil `credential_ref` tutulur. Geçersiz veya desteklenmeyen değer reddedilir; sıfır, boş ve unlimited aynı yorumlanmaz. UI hem seçilen hem fiilen uygulanan değeri gösterir.

| Parametre ailesi | Örnekler | Kim / sınır |
|---|---|---|
| İşleme ve maliyet | Profil, context limiti, günlük/run bütçesi, model allowlist, eşzamanlılık | Workspace/project; task override yalnız üst policy içinde. Harcama/egress izni ayrıca gerekir |
| Dayanıklılık | Payload/queue/storage tavanı, retry sayısı/deadline, lease, batch sınırı | Kurulum tavanı; workspace daha daraltabilir. Keyfi limitsiz değer yok |
| Veri yaşamı | Geçici payload, 1C arşivi, cache, telemetry, audit, backup/purge | Yetkili veri yöneticisi; OPEN-08. Kaynak sınıfları birbirine dönüştürülmez |
| Erişim ve review | Üyelik, grant süresi, izinli connector/kaynak, korunan işlem policy'si | Workspace/project sahibi kendi kapsamı içinde; agent insan approval'ı veremez |
| İşletim | Uyarı eşikleri, bakım, backup schedule, export hedefi | Kurulum yöneticisi; dış hedef/secret kurulumu ayrı açık işlem |

Öncelik: değişmez ürün kuralları → kurulumun güvenlik/kapasite tavanları → workspace → proje → task. Sayısal üst sınırlar en dar izinli değerde, izin kümeleri kesişimle uygulanır. Basit profil tercihi izinli kapsamda override edilebilir. **Retention için genel “en küçük süre kazanır” uygulanmaz:** minimum/maksimum saklama ve erase kuralları veri sınıfıyla çözülür; çatışma intake/deletion öncesi açık karar ister. 1C işlenmemiş arşiv geçici payload TTL'sine sokulmaz.

Değişiklik: etkileneni önizle → ilgili yetki ve gerekirse güvenilir insan onayı → beklenen policy/authz revision ile atomik yeni sürüm + audit → effective policy'yi tekrar oku. Yarışta stale, kısmi uygulanmış gibi başarı yok. Geri alma eski audit'i silmez, yeni revision üretir. Limit düşerken in-flight rezervasyonlar hesaplanır; aşılmış tutar silinmez ve geçmiş maliyet geri alınmış sayılmaz. Yeni dispatch durabilir; zaten gönderilen dış istek geri çağrılmış varsayılmaz. Recovery sırasında eski yedekteki daha geniş yetkiler sessizce açılmaz.

Kurulum ilk owner'ı doğrulanabilir bootstrap ile oluşturur; ortak default admin parolası yok. Yüksek etkili işlemler güncel oturum/yeniden doğrulama gerektirir. Ekip support erişimi gerekiyorsa hedef kaynak sahibi/yetkilisinin açık onayı, amaç, süre ve audit ile sınırlı grant; gizli impersonation yok. Credential ve key recovery kurulum sorumluluğudur; OS/DB root erişimi uygulama rolüyle engellenmiş sayılmaz.

## Neden bu tasarım?

**İhtiyaç:** tüm sistemi yönetmek; kullanıcıların hatayı ve yetkisini anlayabilmesi. **Alternatifler (bu incelemede değerlendirildi):** tek sınırsız admin; sayısal level merdiveni; scope'lu roller ve ayrı operasyon görünümü. **Öneri:** üçüncü yol, çünkü ekip kaynağı, kişisel bağlam, agent grant'i ve hizmet işletimi farklı haklardır. Bedeli daha fazla policy/negatif test ve açık yetki UX'idir. [Mevcut benchmark](../discovery/collaboration-storage-benchmark.md) ve ADR-0009/0010 ile tutarlı tasarım çıkarımıdır; yeni rakip runtime testi değildir. Sayısal parametre varsayımları kanıtla kalibre edilecek.

**P1b:** owner için yerel sağlık/hata özeti, etkin limitler, güvenli pause/retry ve backup/restore durumu. P1a'da bunların policy/audit/budget temeli kurulur. **P4:** workspace admin ekranları, destek presetleri, managed platform konsolu, olay yönetimi ve tenant kotaları. Ayrı SaaS/backoffice geliştirmesi bugünkü MVP'ye eklenmez. [Alt görevler](../delivery/backlog.md#yönetim-merkezi-ve-hata-takibi-alt-dilimleri) ve [diyagram atlası](../architecture/diagrams.md) uygulama sırasını tamamlar.

## Planlı kabul senaryoları

**Çalıştırılmadı.** Fixture'lar sentetik; runtime ve UI tesliminde test edilecek.

| ID | Gözlenebilir kabul |
|---|---|
| ADM-01 | Viewer gizli menünün API'sini çağırınca mutation reddedilir; project owner kurulum policy'sini değiştiremez |
| ADM-02 | Platform operator/L1 tenant'ın ham kaynağına, citation/export'una erişemez; süreli support grant bitince tekrar reddedilir |
| ADM-03 | İki admin aynı revision'ı değiştirince biri stale olur; effective değer ve audit tutarlı; rollback yeni revision |
| ADM-04 | Task override üst bütçe/egress sınırını aşamaz; in-flight rezervasyonlu limit düşüşü yeni dispatch'i durdurur, usage korunur |
| ADM-05 | Secret/prompt içeren hata fixture'ı log/incident/export'ta sızmaz; aynı fingerprint farklı tenant içeriklerini birleştirmez |
| ADM-06 | Timeout sonrası belirsiz dış işlem kör retry edilmez; incident resolve job/task'ı tamamlamaz; tekrar hata reopen üretir |
| ADM-07 | Audit yazımı bozulunca admin mutasyonu commit olmaz; telemetry/DB kaybında sağlık degraded ve dropped/gap görünür |
| ADM-08 | Pause kapsamı UI'da doğru; queue/storage dolunca sahte receipt yok; 1C arşivi geçici TTL ile silinmez |
| ADM-09 | Restore/replay dış etki/model çağrısı üretmez; purge/izin manifest'i uygulanmadan servis açılmaz; unknown host stop açık |
| ADM-10 | Self-host kurulum ağda kurucuya/üçüncü tarafa varsayılan telemetri veya admin yolu açmaz; admin ekranında lisans/hosting/erişim/paket ayrımı anlaşılır |

Lisansı veya repo görünürlüğünü yönetici düğmesiyle değiştirme önerilmiyor. [Lisans ve dağıtım seçenekleri](../governance/licensing.md#kaynak-kodu-kurulum-erişim-ve-paket-ayrı-kararlar) ayrı owner kararlarıdır.

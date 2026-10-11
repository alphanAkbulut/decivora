# Kullanıcı davranışıyla özellik kataloğu

**Planlanan ürün davranışlarıdır; çalışan özellikler değildir.** Kapsamın otoritesi [32 maddelik tam kapsam](full-scope.md), ilk sürümün kabul sınırı [MVP](mvp.md). Bu katalog bu maddelerin kullanıcıya nasıl görüneceğini açıklar. F numaraları yeni ve ayrı scope talepleri değildir.

| Özellik | Kullanıcı durumu → ürün davranışı | Görülebilir çıktı / önemli istisna | Kapsam / faz / engine |
|---|---|---|---|
| F01 Proje kimliği ve başlangıç | Kod reposu olsun/olmasın proje açılır; bir defalık kaynak izni ve oturum bağlantısı kurulur | Ad/klasör benzerliğiyle sessiz eşleme yok; belirsiz kayıt quarantine'da | PRJ-01,GOV-01 / P1a / ENG-01,06 |
| F02 Pasif yakalama | Desteklenen coding oturumunda sohbet sürerken yeni mesaj/araç olayları kaydolur | Alındı/işlendi ayrımı, kaynak ve gap; bütün sohbetlere erişim iddiası yok | CAP-02,CAP-05 / P1a→P1b / ENG-01 |
| F03 Tüm AI çıktıları | Fikir, bulgu, risk, requirement, task, prompt, belge talimatı ve karar çıkarılır | Hazır açıklama/AC/ilişkiler; her fikir otomatik yapılacak iş olmaz | CAP-01 / P1a / ENG-02 |
| F04 Yaşayan bilgi | Aynı konu tekrarlandığında eski karar/ret gerekçesiyle karşılaştırılır | Duplicate/refinement/conflict/new; aktif bilgi ve history ayrı | KNO-01,KNO-02 / P1a→P2 / ENG-03,07 |
| F05 Fikir değerlendirme | “Bu daha iyi mi?” sorusuna alternatif, destek/karşı kanıt ve belirsizlik hazırlanır | Öneri ve kullanıcı kararı ayrı; yeni olmak doğru olmak değildir | KNO-03 / P1b→P2 / ENG-04 |
| F06 Karar farkındalıklı etki | Mimari/requirement değişimi eski task/prompt/artifact gerekçelerini tarar | Keep/update/replace/obsolete/review ve neden zinciri; OR gerekçe korunur | GRF-01,GRF-02,IMP-01,IMP-02 / P1a→P2 / ENG-05 |
| F07 Hazırlanmış review | Kullanıcı başlık/DoD yazmadan öneriyi onaylar, reddeder, erteler veya karşılaştırır | Bağımlı işlemler atomik grup; stale onay yenilenir; cevap vermemek onay değildir | APR-01,APR-02 / P1a→P1b / ENG-06 |
| F08 Chat→Code ve çıktı yaşam döngüsü | Araştırma fikri prompt'a; prompt farklı coding oturumunda uygulamaya dönüşür | Source→prompt revision→execution→artifact→evidence; manuel aktarım açık etiketli | CAP-03,CAP-04,INT-02 / P1b→P2 / ENG-01,02,07 |
| F09 Kanıta bağlı ilerleme | Agent tamamlandığını bildirir; uygun kanıt değerlendirilir | Kriter bazında partial/pending/passed/failed/stale; historical done kaybolmaz | VER-01,VER-02 / P1a→P2 / ENG-08 |
| F10 Ortak görsel hafıza | Inbox/Board/Graph/Timeline arasında aynı kayda gidilir | Kaynak, karar gerekçesi, geçmiş diff ve current revision; history varsayılan işi kirletmez | UX-01 / P1b / ENG-07,10 |
| F11 Bekleyenler ve sonraki iş | Unutulan karar, blocked task, orphan ve stale evidence görünür | Hazır seçenekli PendingDecision; ready iş gerekçesi; kaçırılan kaynak aralığı görünür | APR-02,UX-02 / P1b→P2 / ENG-06,10 |
| F12 İnsan veya ucuz yürütücü | Basit iş için script/API veya kullanıcı uygunluğu önerilir | `human_suitable` etiketi; insan tercih edebilir; işin stratejik karar olması ayrı alan | ROU-01,ROU-02 / P1b→P3 / ENG-09 |
| F13 Hedefli bağlam ve ekonomi | Agent yalnız bu işe gereken onaylı bilgi ve ilgili geçmişi ister | Bütçeli brief/delta, kesilen bağlam, tahmini/gerçek usage; null sıfır değildir | CST-01,CST-02 / P1a→P3 / ENG-09,10 |
| F14 Güvenli hafıza işletimi | Hata düzeltilir, servis yeniden başlar veya backup geri yüklenir | Yeni düzeltme olayı, tekrar üretilebilir current state, privacy purge ayrı audit | AUD-01,GOV-01,GOV-02 / P1a→P2 / ENG-01,06,07 |
| F15 Günlük çalışma yüzeyleri | Kullanıcı IDE yanında bilgi ister; GitHub/Linear/Jira ile bağlantı kurar | Destekli panel/fallback; önce read, sonra ayrı yetkili write/outbox; sync çatışması görünür | UX-03,INT-01 / P2→P3 / ENG-01,06,08,10 |
| F16 Paylaşım ve ürünleşme | İleride ekip, organizasyon, cloud, enterprise audit, OSS/managed service değerlendirilir | Tenant/rol/sync tasarımı ayrı kapı; bugünün yerel MVP'sinde varmış gibi sunulmaz | TEAM-01,OSS-01 / P3→P4 / yeni ADR |
| F17 Ürünün kendini sınaması | Aynı corpus ile alternatifler ve Decivora karşılaştırılır | Hata örnekleri, manuel yönetim süresi, kalite/maliyet ve sürüm; dogfooding gerçek çalışınca | EVAL-01 / P0 ve tüm fazlar / bütün engine'ler |

## Ana kullanım hikâyesi

**F11/F12 — Blocker ve ürün önceliği:** Q09 ile diğer işleri geciktiren engellerin önceliği ve Product Owner bakışı kabul edildi. Kullanıcı engellenen işi, engeli kaldıracak adımı, açılacak değeri, hazır olma sınırını ve sıra gerekçesini görür. Çok bağlantı tek başına yüksek değer değildir; mevcut hedef/risk gözetilir. [Akış sözleşmesi](priority-and-flow.md) grant/bütçe sınırını korur; dış bildirim veya agent yürütme başlatılmaz. Bu mevcut kapsamın uygulama tasarımıdır; çalışan özellik değildir.

Bir araştırma sohbetinde üç bulgu, bir prompt ve henüz kabul edilmemiş teknoloji önerisi çıkar. F02/F03 bunları kaynaklarıyla aday olarak kaydeder. F04 eski fikirleri getirir; F05 farklılığın gerekçesini hazırlar. Kullanıcı onaylamadığı için teknik öneri mevcut kararın yerine geçmez.

Kullanıcı yeni depolama kararını seçince F06 etki önizlemesi çıkarır. Eski sync işi yalnız eski karara bağlıdır; watcher hem eski karar hem import gereksinimiyle OR bağlıdır. F07 birincisini obsolete adayı olarak gösterir, ikincisini korur. Onay eskiyse hiçbir yarım güncelleme oluşmaz.

F08 prompt'un hangi sürümünün hangi agent tarafından uygulandığını bağlar. F09 “bitti” ifadesini claim olarak gösterir; yeni AC sürümüne uygun test olmadan verified yapmaz. F10/F11 neden açık iş kaldığını ve hangi insan kararının gerekli olduğunu gösterir. F12/F13 sıradaki basit doğrulamayı modele göndermeden çözmeyi hedefler.

## Sıfıra yaklaştırılan ve kalan insan işi

Hedef: kart başlığı, açıklama, ilişki, AC ve durum takibi için rutin elle yazmayı azaltmak. Kaynak erişimine ilk izin, belirsiz projeyi bağlama, gerçek scope/karar onayı ve gerektiğinde kanıtı değerlendirme insan işidir. Kullanıcı metin yazarak öneriyi düzeltebilir; metin yazmak standart akışta zorunlu değildir.

Kullanıcı bekleyen kararı ertelediğinde yeni oturum aynı kararı tekrar yoktan üretmez; aynı PendingDecision'a bağlanır. Bildirim sıklığı policy ile sınırlanır; agent kendi oluşturduğu bildirimleri tekrar capture edip sonsuz task döngüsü oluşturamaz. Ölçüm, yalnız tıklama sayısını değil review yorgunluğunu ve yanlış öneri yükünü de içermelidir.

## Kapsam korunumu

**F08/F13 — Q07 kabulü:** 1C, izinli ve erişilebilir geçmişi aktif işlere öncelik vererek aşamalı işler. Arşiv ve model context'i ayrı tutulur; eski öneriler otomatik aktif görev olmaz. Alternatifler, seçim gerekçesi ve maliyet sınırı [karar kaydındadır](../delivery/decision-brief.md).

**F07/F09/F10 — Q08 önerisi:** Kullanıcı bir task için `Alt görevlere bölerek takip et` seçebilir; hazır child/AC/bağımlılık önizlemesini değerlendirir. Anlamlı teslimler child, küçük adımlar checklist olabilir. Parent'ın kendi kabulü korunur; ayrı doğrulanan çocuklar parent'ı kendiliğinden complete yapmaz. [Ayrıntılı tasarım](task-context-and-acceptance.md) öneridir; otomatik bölme veya agent başlatma kararı alınmadı.

Aynı sağlayıcı Chat→Code sürekliliği önce, sağlayıcılar arası otomasyon sonra gelir. P1b import fallback kapsamı görünür tutar ama otomasyon hedefini teslim etmiş sayılmaz. Gelecekteki code graph/IDE/cloud fikirleri silinmez. Bu repo bir agent çalıştırma platformunu, tüm sağlayıcılara sınırsız erişimi veya insan kararı olmadan proje yön değiştirmeyi taahhüt etmez.

## F16 — Ekip kullanımının açılımı

**Tek insan + çok agent da ayrı kullanım hikâyesidir:** araştırma, uygulama ve doğrulama run'ları aynı task/karar görünümüne kaynaklı katkı verir. Kullanıcı agent/run, sponsor, görev, blocker, çıktı/kanıt, son sinyal ve coverage sınırını görür. Run bitişi task'ın tamamlanması değildir; modelin gizli muhakemesini okuduğumuz iddia edilmez. F08/F13/F16 için [gözlem ve ekip kurulum sözleşmesi](../architecture/agent-and-team-operation.md) merkezi hesap/rol akışını ve bireysel çok-agent pilotunu ayrı tanımlar.

Bir projede insanlar farklı rollerle çalışır; agent'lar ayrı kimlik, süre ve görev kapsamıyla görünür. Kullanıcı kimin neyi görebildiğini, kimin adına çalışan agent'ın hangi işlemleri yapabildiğini ve erişimi nasıl durduracağını görür. Kişisel sohbetten ortak bilgiye geçiş açık paylaşım önizlemesi taşır. Karar onayı, iş üstlenme, test çalıştırma ve dış sisteme yazma ayrı izinlerdir.

[Yönetim/rol tasarımı](../architecture/identity-access.md), [kayıt ve audit](../architecture/logging-audit.md), [hafıza/retention](../architecture/storage-memory-capacity.md) ve [C01–C06 ekip dilimleri](../delivery/team-data-plan.md) bu kullanıcı davranışlarının önerilen çözümüdür. İlk pilot tek kullanıcıdır; henüz ekip ekranı yoktur.

## F07/F09/F10 — Olgunlaşma ve iş başına kabul görünümü

Kullanıcı isteğiyle [task context ve kabul dosyası](task-context-and-acceptance.md) ayrıntılandırıldı: ilk fikir→alternatif→değişim gerekçesi→onaylı yaklaşım→uygulama/test kanıtı aynı task üzerinden görünür. AC ve uygulanabilir DoD işe başlamadan versiyonlu hazırlanır; iş sonrasında test/evidence matrisi bunlara karşı gösterilir. Ana işin önemli değişimi veya kapanışı context milestone'ı üretir; dosya otomasyonu Q06 tercihidir. Bu mevcut kapsamın açılımıdır, çalışan özellik değildir.

## Bekleyen işten yeni oturuma dönüş

F11'in yaş/kanıt göstergesi ve F08/F13'ün context aktarımı [devam paketi](resume-package-and-memory.md) ile birleşir: seçili işin izinli kaynakları, ne yapıldığı/ne kaldığı ve güncel kararlar önizlenir. İlk deney için önerilen kopyala eylemi run başlatmaz veya görevi completed yapmaz. F04 stale/çelişki kontrolü ve F09 verification korunur. Q11 tercihi açık; [Spike-1 v1](../delivery/spike-1-v1.md) bir uygulama/test sonucu değildir.

## F07/F08/F09/F10 — İlk gerçekleşme sürekliliği deneyi

[Güncel yön](current-direction.md) F07'de gerçek insan seçimini, F08'de generated artifact ve target expectation'ı, F09'da reported/observed/partial/unknown ile acceptance ayrımını, F10'da bunların kaynaklı görünümünü birlikte sınar. Minimal deney ekranı tam Inbox/Board/Graph/Timeline teslimi değildir. [GAP oracle](../../examples/intent-reality-scenario.json) sentetik ve not_run; native Projects ile ek değer kanıtlanmadı. Mevcut 17 feature ve tam scope korunur.

## F03/F04/F07/F08/F10/F13 — İngilizce dışındaki kullanım

Kullanıcı Türkçe konuşuyorsa proje çıktılarının anlaşılır Türkçe üretilmesi; başka dillerde de aynı ihtiyacın desteklenmesi hedeflenir. [Dil ve yerelleştirme](language-and-localization.md) kaynak metnini, üretim dilini ve UI locale'i ayırır. Kod/ref/kanıt çevrilmez; eski kayıt sessiz yeniden yazılmaz. P1 temel metadata/açık pilot dili; P2 otomatik tespit, mixed/fallback, locale katalogları ve dil/model bazlı kalite raporları önerilir. Q12-A kabul edildi: proje çıktı dili sabit kalır, başka sohbet dili değişim önerisi olur; kabul sonrası yeni çıktılar değişir, eski notlar çevrilmez. Yeni feature numarası/engine veya uygulanmış çok dil desteği iddiası yok.

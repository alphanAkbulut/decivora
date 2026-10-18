# İşin olgunlaşma hikâyesi ve tamamlanma dosyası

**Durum: Q06-A/Q08-A ürün tercihleri 18 Ekim kabul edildi; aşağıdaki snapshot/split otomasyonları henüz uygulanmadı.** Kullanıcı güncel/seçili iş görünümünü seçti; fikirlerin neden değiştiğinin, işin hangi yoldan ilerlediğinin ve yapılan testlerin görülebilmesini istedi. Kalıcı olay geçmişine dayalı bağlam özeti öneriyoruz. Q06-A ile önemli karar değişimi/ana görev kapanışında otomatik yerel Markdown snapshot seçildi; uygulama hafızası esas kalır.

## İş bağlamı özeti

Bu çıktı task'ın yeniden yazılmış tarihçesi değil; kayıtlı kaynak, evaluation, karar, ilişki ve kanıtların **revision bağlı türetilmiş görünümüdür**. Yanlış veya eski özet canonical kararı değiştiremez. Gerekçe kaynakta yoksa “gerekçe kayıtlı değil” yazar; model geçmişe makul görünen nedenler ekleyemez.

Bir ana işin ayrıntısında `Bağlam ve evrim` sekmesi şu bölümleri gösterir:

1. Amaç ve bağlı gereksinim/kararlar: bu iş neden var?
2. İlk düşünülen yaklaşım ve alternatifler; kaynağın tarihi/ID'si.
3. Değişim çizelgesi: önce → yeni öneri → gerekçe/karşı kanıt → karar veren/onay → etkiler.
4. İptal, ret, obsolete veya supersession: hangisi oldu, hangi eski yol kaldı, hangisi sona erdi?
5. Güncel uygulama yaklaşımı ve korunmuş alternatif gerekçeler.
6. Kabul kriterleri, uygulanabilir DoD maddeleri ve mevcut kanıt durumları.
7. Açık sorular, denenmeyen senaryolar, remaining work ve bilginin erişim/tazelik sınırı.

UI aynı kaydın Graph/Timeline görünümlerine gider. Başlangıçta küçük kaynaklı şablon yeterlidir; isteğe bağlı anlatı güzelleştirmesi ayrı bütçeli model işi olabilir. Her task sonrası bütün projeyi yeniden özetleyen LLM zinciri yoktur.

## Ne zaman yeni sürüm üretilir?

| Olay | Davranış |
|---|---|
| Ana task kabul edilir veya ilk plan onaylanır | Başlangıç context snapshot'ı; kabul edilmemiş öneriler ayrı |
| Onaylı yaklaşım/scope/AC/DoD veya önemli gerekçe değişir | Önce/sonra ve karar gerekçesiyle yeni milestone sürümü |
| İş gerçekten doğrulanarak tamamlanır | Tamamlanma snapshot'ı; hangi evidence hangi revision'a ait açık |
| Task cancelled/obsolete/superseded olur | Kapanış türü ve etkileriyle yeni sürüm; başarı olarak anlatılmaz |
| Yeni kanıt başarısız/stale yapar veya iş yeniden açılır | Önceki tamamlanma snapshot'ı korunur; güncel status değişimi yeni sürüm |
| Alt task veya tek test sonucu gelir | Canlı checklist/timeline güncellenir; her küçük olay için yeni Markdown/model özeti zorunlu değil |

`Ana task` başlıktaki bir sözcükten çıkarılmaz; task hierarchy/milestone işaretiyle belirlenir. Her task kendi AC/DoD/kanıt ekranına sahiptir; milestone dosyası üretim eşiği ana task veya kullanıcının işaretlediği task içindir. Child tamamlanması parent'ı otomatik complete yapmaz; parent'ın kendi ölçütleri ve gerekli child ilişkileri değerlendirilir.

`ContextSnapshot`: workspace/project/task, task/knowledge/AC/DoD revision, trigger event/sequence, kaynak ve evidence refs, authz/viewer kapsamı, template version, content digest, generated_at, stale/coverage. Aynı trigger + template + yetkili kaynak seti retry'ı ikinci milestone üretmez. Job domain transaction'ıyla kaydedilir, dosya/özet üretimi commit sonrasında çalışır. Export başarısızsa task'ın doğrulanma olayı geri alınmaz; context export `pending/failed` görünür. Yalnız açık project DoD dosya teslimini zorunlu yapmışsa o teslim eksikliği completion'ı bloke eder; varsayılan teknik export hatası işi gizlice başarısız yapmaz. Dosyanın kendisi DoD teslimi olarak zorunlu seçilirse üretim yalnız completed sonrasına bağlanamaz: implementation/review aşamasında aday teslim snapshot'ı hazırlanır, teslim kanıtı değerlendirilir, completion sonrasında nihai snapshot oluşur. Böylece completion→export→completion döngüsü kurulmaz.

## Dosya biçimi ve sınırları

Q06-A kabul edildi; önerilen fiziksel çıktı düzeni: kullanıcı tarafından seçilmiş data/export dizininde `context/<project_id>/<task_id>/v0003.md`. Dosya yeni sürüm olarak yazılır; önceki sürüm üzerine yazılmaz. Manifest en güncel yetkili snapshot'ı gösterir. Runtime data/export varsayılan olarak uygulama kaynak reposunun dışında ve private kalır; otomatik Git commit/push, paylaşım veya tüm ekip için erişim açma yoktur.

Kaynak metin, secret ve private konuşma gövdesi dosyaya varsayılan gömülmez; izinli kısa bilgi ve kontrollü referans kullanılır. Birden fazla kaynağın ACL'si türevin erişimini daraltır. Özel sürüm projeye ortak dosya diye kopyalanmaz. Yetki/purge değişikliği türevi stale/restricted yapar; yönetilen export manifest temizliği [retention planına](../architecture/storage-memory-capacity.md) tabidir. Kullanıcının dışarı kopyaladığı dosyaları geri çağırabildiğimiz söylenmez. Eski snapshot güncel karar gibi servis edilmez.

## Kabul kriteri ve Definition of Done

**AC**, o işin hangi gözlenebilir sonucu sağlaması gerektiğidir. **DoD**, proje/iş türünde “tamamlandı” demeden önce uygulanabilir ortak kalite/teslim koşullarıdır. Örnek kod değişikliğinde ilgili regresyon kanıtı; belge işinde kaynak ve bağlantı kontrolü olabilir. Her işe aynı gereksiz test listesi zorlanmaz.

AC ve DoD iş başlamadan önerilir, kaynak gerekçesiyle görünür ve gerekli insan onayıyla version'lanır. Kullanıcı bunları baştan yazmak zorunda değildir. İş bittikten sonra başarıya uyacak şekilde gizlice kriter uydurulmaz veya düşürülmez. Yeni gereksinim geldiğinde diff/onay ve etkilenen evidence'ın stale değerlendirmesi gerekir.

Önerilen alanlar: `AcceptanceCriterion(id, task_revision, statement, method, required, source_ref, version)`; `DoDTemplate(project, task_type, version, applicable_rules)`; task'a bağlanmış `DoDAssessment(template_version, applicability, criterion_refs, evidence_refs)`. Duplicate AC/DoD kontrolü aynı evidence'a referans verebilir; gereksiz iki test koşusu zorunlu olmaz.

| Ekran alanı | Kullanıcının göreceği bilgi |
|---|---|
| Beklenen | Onaylı AC/DoD metni; gerekli mi, koşullu mu? |
| Doğrulama yolu | Otomatik test, dosya/commit denetimi, insan incelemesi veya başka izinli verifier |
| Sonuç | `Başarılı`, `Başarısız`, `Çalıştırılmadı`, `Bekliyor`, `Kanıt eskidi`, `Bilinmiyor`, `Uygulanamaz` |
| Kanıt | Test/inceleme adı, güvenli komut özeti, ortam, zaman, commit/artifact hash, sonuç/log referansı |
| Açık kalan | Eksik kriter, başarısız senaryo, uygulanamaz gerekçesi ve gerekli yetkili değerlendirme |

`Çalıştırılmadı` evidence report sonucudur; domain verification'da neden bilgisiyle `unknown` veya `pending` olabilir, `failed`/`passed` değildir. Test aracının çalışamaması ürün testinin başarısız olduğuyla aynı değildir. `Uygulanamaz` ancak kriterin koşulu gerçekten sağlanmıyorsa ve ilgili policy/onay gerekçesiyle seçilir; failed kriteri saklama yolu değildir.

**Current completed:** gerekli AC'ler ve uygulanabilir gerekli DoD maddeleri güncel task/AC/DoD/artifact revisions için geçerli kanıtla passed, gerekli review tamam, bloke eden pending impact/scope yok. Agent'ın “bitti” ifadesi yalnız implementation claim'dir. Başarısız zorunlu kontrol, test edilmemiş zorunlu madde veya stale kanıt completed'ı engeller. Önceden gerçekten doğrulanmış tarihsel başarı, daha sonraki scope değişimiyle tarihten silinmez.

## Sentetik bağlam dosyası içeriği örneği

> **Örnek; gerçek task/test sonucu değildir.** TASK-004 / snapshot v3.
>
> İlk yaklaşım: Markdown dosyalarını izlemek ve senkronize etmek.
>
> Değişim: DEC-002 ile canonical depolama SQLite olarak önerildi ve bu örnekte onaylandı. Markdown senkronizasyonu için gerekçe sona erdi; belge importu gereksinimi watcher'ı hâlâ gerekli kılıyor. Bu yüzden watcher daraltılarak korundu, sync işi obsolete olarak ayrı kapatıldı.
>
> AC-1: Aynı dosya olayı tekrar geldiğinde tek kayıt oluşmalı — **Çalıştırılmadı**.
>
> AC-2: İşlenmeyen kaynak aralığı kaybolmamalı — **Çalıştırılmadı**.
>
> DoD: İlgili hata/tekrar senaryolarının kanıtı bulunmalı — **Bekliyor**.
>
> Sonuç: Yaklaşım açıklanmış, uygulama ve test doğrulanmamış. Completed değil.

<a id="isteğe-bağlı-alt-görevlere-böl-ve-takip-et"></a>

## İsteğe bağlı: Alt görevlere böl ve takip et

**Q08-A / DEC-16 kabul edildi (18 Ekim).** Task menüsünde `Alt görevlere bölerek takip et` eylemi öneriyoruz. Ayrı teslimi, kabul kriteri, sorumlusu veya bağımlılığı olan anlamlı parçalar task; küçük uygulama adımları checklist olur. Her işi otomatik mikro görevlere bölmek önerilmez.

Örnek (sentetik): **“Geçmiş konuşmaları güvenle aktar”** ana işi altında **kaynak/izin önizlemesi**, **tekrarları ayıklayan devam edilebilir import**, **tarihsel kararların uzlaştırılması** ayrı test edilebilir alt çıktılardır. “Dosyayı aç / alanı oku / başlığı göster” gibi adımlar bağımsız çıktı değilse checklist'te kalır. Ana işin ayrıca uçtan uca kabul koşulu bulunur.

| Kazanç | Nasıl sağlanır / sınır |
|---|---|
| Nerede takıldığını anlama | Her child kendi blocked nedeni, AC ve kanıtını taşır; belirsiz bir ana task yüzdesine güvenilmez |
| Daha dar agent bağlamı | İlgili child + ana amaç + gerekli kararlar getirilir; ek planlama maliyeti yüzünden tasarruf garanti değildir |
| Değişikliğin etkisini sınırlama | Karar yalnız etkilenen child ve ilişkilerinde review üretir; diğer doğrulanmış kanıtlar revision uyumluysa korunabilir |
| İşi paylaşma ve yeniden başlama | Farklı insan/agent adayları ve sıralama görülebilir; atama, yetki verme ve execution başlatma ayrı işlemlerdir |
| Daha anlamlı tamamlanma | Eksik bir teslim veya test gizlenmez; child'lar bitse de ana işin kendi AC/DoD/entegrasyon kanıtı aranır |

### Önizleme ve kayıt sözleşmesi

1. Sistem mevcut task/AC/DoD/ilişkilerden hazır öneri çıkarır. Model gerekirse normal veri/bütçe politikasına tabidir; kullanıcı manuel de bölebilir. Önizlemede eski→yeni yapı, gerekçe, child çıktıları/AC, bağımlılıklar, checklist'te kalanlar, mevcut kanıtın eşlemesi ve karşılanmamış ana AC'ler görünür.
2. İnsan düzenleyip onaylar. Parent ID, amaç, geçmiş kararlar ve önceki kanıtlar korunur; task yerine kimliği ilgisiz yeni bir task yaratılmaz. Mevcut child'lar kontrol edilir, duplicate plan oluşturulmaz. Alt görev eklemek parent'ın kapsamını sessiz genişletmez veya düşürmez.
3. Child kayıtları, `part_of` bağlantıları, completion gereklilikleri ve kriter eşlemesi aynı onaylı ChangeSet içinde atomik uygulanır. Kaynak task/knowledge/authz revision değişmişse önizleme stale olur. Retry aynı işlemi tekrarlamaz; yarım hierarchy bırakılmaz. Çalışan işin sonucuyla yarış halinde yeni revision için yeniden değerlendirme gerekir.
4. Ana AC→child AC eşlemesi kapsam boşluğunu gösterir; eski evidence child'a körlemesine `passed` kopyalanmaz. Aynı kanıt yalnız kapsam/artifact/revision gerçekten uygunsa referanslanabilir. Yeni child verification başlangıcı kanıt yoksa unknown'dur.
5. Kullanıcı sonradan yapıyı değiştirebilir. Eski bağlantı ended/invalidated olaylarıyla izlenir; geçmiş silinmez. İptal edilen child grafikte iptal etiketi ve seçili işin tarihçesiyle kalır. Zorunlu child iptal edilirse ana iş otomatik ilerlemiş sayılmaz; replacement veya açık scope/completion review gerekir.

### Takip ve tamamlama

Ana işte örneğin **“Gerekli alt işlerin 3/5'i güncel kanıtla doğrulandı; ana işin uçtan uca kontrolü bekliyor”** yazılır. Bu süre/eforun %60'ı bitti demek değildir. Opsiyonel, iptal, blocked, unknown ve stale ayrı sayılır; paydanın değişmesi onaylı scope geçmişine bağlanır. Parent ve child aynı toplam iş sayısında iki kez sayılmaz; gösterimin düzeyi açık olur.

Child tamamlanması: kendi güncel AC/DoD/kanıt kapıları. Parent tamamlanması: kendi kapıları **ve** onaylı gerekli child koşulları; yalnız child sayacı yeterli değildir. Child eklemek/silmek execution grant veya bütçe tavanını değiştirmez. Her küçük adım için bildirim/dosya/model üretmek zorunlu değildir; Q06 milestone export ve Q09 bildirim tercihi ayrı kalır.

**Planlı doğrulama:** self-parent/cycle/cross-project reddi; eski onay ve eşzamanlı sonuç; retry ile tek bölme; mevcut child/evidence korunumu; zorunlu child iptali; child passed ama parent entegrasyon kanıtı eksik; sonradan eklenen child ve değişen payda; parent/child toplam bütçe. Uygulama dilimleri T13d ve T20d, Q08 tercih kapısı cevaplandı. Teknik otomasyon geliştirmesi açık; bu kabul ile uygulanmış/test edilmiş sayılmaz.

## Mevcut bağlam ve kabul senaryoları

| ID | Gözlenebilir kriter | Görev |
|---|---|---|
| CTX-01 | Onaylı büyük değişim/kapanış trigger'ı idempotent context sürümü üretir; minor event dosya fırtınası yaratmaz | T20c |
| CTX-02 | Önceki yaklaşım, karar gerekçesi ve kaynak refs görünür; kayıtsız gerekçe uydurulmaz | T20c/T24c |
| CTX-03 | Gerekli AC/DoD başlamadan görünür; değişim version/onay ve evidence staleness doğurur | T13c/T14b |
| CTX-04 | Failed/not_run/unknown/stale/NA ayrılır; eksik zorunlu koşul completed'ı engeller | T14b |
| CTX-05 | Context/Markdown kaynak ACL'yi genişletemez; purge/export manifest ilişkisi testlidir | T18b/T23c |
| CTX-06 | Dosya üretimi başarısızlığı görünür; false test sonucu yok; yeniden açılmada geçmiş snapshot korunur | T20c |

Kontroller planlıdır; bağımsız test veya bağlam dosyası generator'ı yok. [Q04–Q06](../delivery/decision-brief.md), [Graph](graph-experience.md), [verification](../quality/verification.md) ve [token bütçesi](../architecture/routing-token-economy.md) ile birlikte uygulanır.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

[Current local completion](../quality/workflow-ui-runtime.md): versioned AC/DoD ve human_review criterion sonuçları kodda; gerekli current maddeler passed + explicit scope review + finish gates ile Done. Automatic test/file-check/remote artifact observer ve ana task context/export/parent automation hâlâ açık. Üstteki genel uygulanmadı ibaresi bu future kapsamı anlatır; AC/DoD manuel dilimi uygulanmıştır.

## Current local delivery — 14 October 2026

[API-independent implementation and follow-up gates](../delivery/api-independent-development.md): bounded stdioMCP/create-only human review, optional explicit-root file SHA verification, recorded graph/audit timeline, routing/null usage and session-only health. Historical implementation limits above refer to their original deliveries; current limits and M01–M14 checks are in the linked report. No native capture, full brief/delta, sandbox test/deploy verifier, exact host token savings or global language quality is claimed.

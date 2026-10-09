# İşin olgunlaşma hikâyesi ve tamamlanma dosyası

**Durum: kullanıcı ihtiyacına dayalı önerilen tasarım; uygulanmadı.** Kullanıcı güncel/seçili iş görünümünü seçti; fikirlerin neden değiştiğinin, işin hangi yoldan ilerlediğinin ve yapılan testlerin görülebilmesini istedi. Kalıcı olay geçmişine dayalı bağlam özeti öneriyoruz. Otomatik Markdown dosyası mı, isteğe bağlı export mu olacağı Q06'da soruldu; cevap bekliyor.

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

Q06 kabul edilirse önerilen local çıktı: kullanıcı tarafından seçilmiş data/export dizininde `context/<project_id>/<task_id>/v0003.md`. Dosya yeni sürüm olarak yazılır; önceki sürüm üzerine yazılmaz. Manifest en güncel yetkili snapshot'ı gösterir. Runtime data/export varsayılan olarak uygulama kaynak reposunun dışında ve private kalır; otomatik Git commit/push, paylaşım veya tüm ekip için erişim açma yoktur.

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

## Kabul planı

| ID | Gözlenebilir kriter | Görev |
|---|---|---|
| CTX-01 | Onaylı büyük değişim/kapanış trigger'ı idempotent context sürümü üretir; minor event dosya fırtınası yaratmaz | T20c |
| CTX-02 | Önceki yaklaşım, karar gerekçesi ve kaynak refs görünür; kayıtsız gerekçe uydurulmaz | T20c/T24c |
| CTX-03 | Gerekli AC/DoD başlamadan görünür; değişim version/onay ve evidence staleness doğurur | T13c/T14b |
| CTX-04 | Failed/not_run/unknown/stale/NA ayrılır; eksik zorunlu koşul completed'ı engeller | T14b |
| CTX-05 | Context/Markdown kaynak ACL'yi genişletemez; purge/export manifest ilişkisi testlidir | T18b/T23c |
| CTX-06 | Dosya üretimi başarısızlığı görünür; false test sonucu yok; yeniden açılmada geçmiş snapshot korunur | T20c |

Kontroller planlıdır; bağımsız test veya bağlam dosyası generator'ı yok. [Q04–Q06](../delivery/decision-brief.md), [Graph](graph-experience.md), [verification](../quality/verification.md) ve [token bütçesi](../architecture/routing-token-economy.md) ile birlikte uygulanır.

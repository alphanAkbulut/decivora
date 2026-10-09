# Kullanıcı şikâyetlerinden ürün gereksinimlerine

**İnceleme: 2026-10-09.** Bu nitel masa başı araştırmasıdır; temsilî pazar anketi veya yeniden üretilmiş hata raporu değildir. Yedi kamuya açık konuşma/issue kümesi incelendi. Üç GitHub issue'su, bir UI tartışması ve üç Reddit konuşması amaçlı örneklemdir; aynı başlıktaki cevaplar bağımsız kullanıcı araştırması sayılmaz. Ürün sahibinin kaynak sohbetteki ihtiyacı ayrıca birinci el pilot girdisidir.

## Kanıt kaydı: gözlem ile yorum ayrı

| ID / kaynak | Kaynakta gözlenen yakınma | Güncel kontrol ve sınır | Bizim çıkarımımız |
|---|---|---|---|
| UR-01 · [Task Master #1280](https://github.com/eyaltoledano/claude-task-master/issues/1280), 2025-10-06 | Kullanıcı MCP araç tanımlarının geliştirme bağlamını daralttığını bildiriyor; başka biri aracı kapatıp gerektiğinde açtığını söylüyor | Issue kapalı. [Bakımcı yanıtı](https://github.com/eyaltoledano/claude-task-master/issues/1280#issuecomment-3403117739), seçilebilir araçlar için PR #1181'in birleştirildiğini ve 0.30.0'a alınacağını bildiriyor. Sayısal token iddiasını yeniden ölçmedik | Context tasarrufu için minimum tool profile gerekli; bugün rakibin çözemediği bir alan diye pazarlanamaz |
| UR-02 · [Task Master #1728](https://github.com/eyaltoledano/claude-task-master/issues/1728), 2026-08-17 | Rapor sıfır alt görev önerdiği halde expansion'ın beş görev üretmesi bildiriliyor | Okunan sayfada açık. Rapor 0.43.1 ve diğer sürümlere atıf yapıyor; burada yeniden üretilmedi. Kaynakta null ile sıfırı karıştıran kontrol iddiası var | “Hiç yeni iş gerekmiyor” birinci sınıf sonuç olmalı. Her girdiyi task veya alt göreve çevirmek başarı değildir |
| UR-03 · [Beads #2363](https://github.com/gastownhall/beads/issues/2363), 2026-03-05 | Agent'ın bağlantı hatası sonrası aracın önerilerini izleyerek yeniden başlatma yoluyla veri kaybı oluşturduğu bildiriliyor | Issue kapalı. [Bakımcı yanıtı](https://github.com/gastownhall/beads/issues/2363#issuecomment-4007206076), hata metinlerinin değiştiğini ve non-interactive destructive reinit'in reddedildiğini bildiriyor; commit 58f5989b. Fix'i çalıştırarak doğrulamadık | Hata mesajı agent'a yetki vermez. Kurtarma, tanı ve veri silme yetkileri ayrılmalı; mevcut data için otomatik reset olmamalı |
| UR-04 · [Beads UI #276](https://github.com/gastownhall/beads/discussions/276), 2025-11-09 başlangıç | Görsel ilerleme, ekipte paylaşım, tekrar eden kurulum ve editör açık olmadan görünürlük ihtiyaçları tartışılıyor | Hem olumlu araç önerileri hem deneyim anlatıları var. Bir katılımcı IDE kaynak yükünden dolayı ayrı uygulama yaptığını söylüyor; bu tüm IDE'lerin ölçülmüş performans sonucu değil | Tek board herkesin iş akışına uymaz; hafif görünürlük ve onboarding maliyeti ölçülmeli. UI varlığı tek başına farklılaştırıcı değil |
| UR-05 · [Sistemler arasında bilgiyi tutarlı tutmak](https://www.reddit.com/r/projectmanagement/comments/1tz4pid/how_much_of_your_week_is_just_keeping_information/), 2026-06-07 | Toplantı, proje aracı ve diğer kanallardaki bilgiyi elle tutarlı tutma yükü anlatılıyor | Genel PM topluluğu, doğrudan coding-agent örneklemi değil. Yanıtlarda her bilgi için belirli bir otorite seçmek de öneriliyor | Canonical record ve hangi sistemin hangi alanı yönettiği önemlidir; tüm araçlara çift yönlü yazmak sorunu büyütebilir |
| UR-06 · [Araç işin kendisinden karmaşık olmasın](https://www.reddit.com/r/aiToolForBusiness/comments/1srje0j/whats_the_best_ai_tool_for_managing_projects/), 2026-04-21 | Workflow/dashboard kurulumunun yeni iş yüküne dönüşmesi ve öğrenme eğrisi yakınması | Yazar çözüm önerisi istiyor; doğrulanmış kullanıcı kimliği/bağımsız motivasyon yok. Cevaplarda öğrenmenin tamamen ortadan kalkmayacağı itirazı da var | Hazır varsayılanlar ve ilk değere ulaşma süresi önemlidir; onboarding'i sıfır emek diye sunmamalıyız |
| UR-07 · [AI kod yazarken projeyi takip etmek](https://www.reddit.com/r/ClaudeAI/comments/1pdd0pc/how_do_you_keep_track_of_your_project_when_ai/), 2025-12-03 | Hızlı üretilen kodda zihinsel bağlamı kaybetme ve projeye dönerken yeniden öğrenme anlatılıyor | Yanıtlar kod inceleme, küçük değişiklikler ve yüksek seviyeli dokümantasyon öneriyor. Bir hafıza ürününün tek başına kod anlama açığını çözeceği sonucu çıkmaz | Karar gerekçesi ve artifact/source lineage geri dönüşü kolaylaştırabilir; kod okuma ve mühendislik muhakemesinin yerine geçmez |

Sayfa durumu erişim anındaki gözlemdir; açık issue her sürümde hâlâ hata olduğunu, kapalı issue de her ortamda düzeldiğini kanıtlamaz. Kaynak metinler paraphrase edildi; kullanıcı adları, tam transcript ve hassas işlem bilgileri taşınmadı. Farklı başlıkları “kullanıcıların yüzde X'i” şeklinde sayısallaştırmıyoruz.

## Yakınmadan geriye doğru tasarım

Önce istenen kullanıcı sonucu, sonra onu engelleyen varsayım, en son teknik çözüm seçilir. Aşağıdaki nedenler **hipotezdir**, kaynaklarda kanıtlanmış evrensel kök neden değildir.

| Problem / dayanak | İstenen sonuç ve neden hipotezi | Decivora'nın çözmeye çalışacağı şey | Sınırı / ters etki | Mevcut kapsam ve deney |
|---|---|---|---|---|
| Bağlam sürekli tüketiliyor / UR-01 | Kod için alan kalsın; tüm araç ve geçmişin her tur yüklenmesi pahalı olabilir | Minimal tools, bounded brief, delta/cache, deterministic-first | Eksik bağlam recall'ı bozabilir; token düşüşü tek başına başarı değil | CST-01/02, ENG-09/10; T18/T21; eş kalite token ölçümü |
| Sistem gereksiz iş üretiyor / UR-02 | Kullanıcı gerçek işe odaklansın; sıfır çıktı yanlışlıkla hata/eksik sanılıyor olabilir | No-op, exact dedup, task yerine idea/finding, gerekçesiz expansion yapmama | Fazla filtre gerçek işi kaçırabilir | CAP-01,KNO-02; T09/T10; no-op ile meaningful recall birlikte |
| Agent bakım yaparken hafızayı bozuyor / UR-03 | Geçmiş kurtarılabilir kalsın; hata recovery önerisi yetki sanılıyor olabilir | Append-only command sınırı, teşhis ile destructive admin ayrımı, backup/restore | Yönetici disk erişimi varsa mutlak immutability yok | AUD-01,GOV-01; T07/T23; V10/V17/V27 |
| Görmek için ikinci iş akışı gerekiyor / UR-04/06 | İş yanında güncel ve hafif görünüm; kurulum ve UI değiştirme sürtünmesi olabilir | Project selector, hazır review, browser/panel fallback, ilk değer rehberi | Her host'a native panel sözü veremeyiz | UX-01/03; T19/T27; kurulum süresi ve context switch gözlemi |
| Araçlar farklı gerçek anlatıyor / UR-05 | Hangi bilginin güncel olduğu belli olsun; sahiplik ve revision belirsiz olabilir | Tek canonical kayıt, kaynak/revision, dış sync conflict görünürlüğü | Yeni merkez eski araçların yanına bir güncelleme yükü daha ekleyebilir | KNO-01,INT-01; T07/T28; tutarsızlık ve manuel tekrar girişi ölçümü |
| Yeni karar eski planı eskitti / ürün sahibinin E12 ihtiyacı | Artık gerekmeyen iş görünür olsun; rationale bağlantıları eksik olabilir | AND/OR/unknown graph, impact diff, geçmiş completion ile current applicability ayrımı | Eksik graph'ta kesin obsolete sonucu verilemez; pazar sıklığı henüz kanıtlı değil | GRF-01/02,IMP-01; T11/T12; V05/V06/V22 |
| Projeye dönüşte nedenleri yeniden aramak / UR-07 + E01/E07 | Yeni oturum doğru karar ve bekleyen işi getirsin; kod ile gerekçe kopmuş olabilir | Source→decision→prompt→execution→artifact→evidence | Teknik kavrayışı veya doğru ürün kararını garanti etmez | CAP-03,INT-02; T18/T22; geri dönüş görevi süresi/doğruluğu |
| “Bitti” bilgisine güvenememe / ürün sahibinin E10 ihtiyacı | Test edilmiş sonuç ayırt edilsin; claim kanıt yerine kullanılıyor olabilir | AC/artifact revision-bound verification | Her AC otomatik test edilemez; insan değerlendirmesi gerekebilir | VER-01/02; T14; V08/V24 |

Önemli ayrım: **karar değişimi sonrası stale task** ve **false done** bu çalışmada doğrudan owner problemiyle güçlü biçimde desteklenir; yedi kamu kaynağı bu iki sorunun yaygınlığını ayrıca kanıtlamaz. Bunun için hedef kullanıcı görüşmeleri gerekir.

## Ters düşünme: Decivora'yı neden terk ederler?

| Başarısızlık varsayımı | Erken uyarı | Tasarım karşılığı / durdurma kararı |
|---|---|---|
| “Yeni bir inbox daha yarattı” | Review yaşı ve düzeltme dakikası artıyor | Batch/dedup/no-op; aynı işi manuel yöntemden daha yorucu yapıyorsa yeni connector yerine kaliteyi düzelt |
| “Eksik yakaladığı halde her şey tamam diyor” | Kaynak boşlukları ile yeşil dashboard birlikte | Coverage/gap ve supported surface açık; belirsizliği gizleyen release durur |
| “Eski işi yanlış kapattı” | Geçerli alternatif gerekçeli iş obsolete | H1 gate; gerekçe/approval snapshot kontrolleri geçmeden otomatik scope değişimi yok |
| “Kurmak, hatırlamaktan zor” | İlk yararlı kayıt öncesi çok adım/hata | İzole kurulum, anlaşılır fallback, setup ve upgrade maliyetini raporla |
| “MCP maliyeti kazancını yedi” | Yönetim zamanı azalırken toplam maliyet büyüyor | Capture, tool schema, retry ve insan review maliyetini birlikte ölç |
| “Hassas konuşmam nereye gitti?” | Kullanıcı kaynağın/model çağrısının kapsamını açıklayamıyor | Project consent, redaction, egress görünürlüğü; veri sınırı belirsizken gerçek veri pilotu yok |
| “Mevcut aracım zaten bunu yapıyordu” | Aynı corpus'ta yapılandırılmış alternatif eşit/daha iyi | Build/extend kararını yeniden aç; yalnız güzel graph için yeni ürün yapma |

## Ne öğrenmeden büyümemeliyiz?

İlk pilot **ürün sahibinin bireysel kullanımı**, sonra benzer kullanıcılar olarak seçildi. Bir pilot pazar talebi değildir. Henüz kimseyle görüşme yapılmadı ve dış kişiye mesaj gönderilmedi.

İkinci aşamada önerilen 3–5 görüşme amaçlı keşif örneklemidir; istatistiksel temsil iddiası yok. Yönlendirmeyen görüşme akışı:

1. Son projeye dönüşünü anlat: hangi bilgiyi nerede aradın, ne kadar sürdü?
2. Son değiştirdiğin karar hangi açık işleri etkiledi? Bunu nasıl fark ettin?
3. Gerçekte bitmemiş bir işi bitmiş sandığın son örnek neydi; kanıt neydi?
4. Şu an kullandığın çözümün iyi çalışan tarafı ne? Yeni araç hangi yükü eklememeli?
5. Kaynak paylaşmadan benzer sentetik akışta bir iş yap; süre, geri dönüş, düzeltme ve tereddüt gözlensin.
6. Demo sonrası “beğendin mi?” yerine bir sonraki gerçek oturumda neyi kullanacağı ve hangi nedenle kullanmayacağı sorulsun.

Karşı kanıt aktif aranır: sorun seyrekse, mevcut araç yeterliyse, kullanıcı karar review'sunu istemiyorsa veya source erişimi kapalıysa bunu da raporla. Olumlu yorum ve star, kullanım/ödeme isteği yerine geçmez. Sonuçlar [benchmark bulgularına](benchmark-findings.md) ve [ölçüm planına](../quality/measurement.md) bağlanır.

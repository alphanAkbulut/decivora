# Spike-1 — Güncel gerçekleşme ve devam paketi deneyi

**2026-10-11 / PROPOSED / not_started.** Yapıştırılan konuşmadaki öneri incelenebilir bir görev planına dönüştürüldü. Bu belge “Spike-0 çalışıyor” varsayımına dayanmaz. Repo bugün dokümantasyon aşamasındadır; önceki prototip kanıtı yoktur. Üretim kodu, otomatik agent başlatma veya ücretli model çalıştırma taahhüdü değildir.

**Tek aktif deney belgesi:** Dosya adındaki v1 geçmiş kimliğidir; içerik tasarım revizyonu 03 için yerinde güncellendi. Yeni v2/v3 plan kopyası yok. [Güncel yön](../product/current-direction.md) ve [sürüm düzeni](../governance/versioning.md) otoriteyi açıklar.

## Deney sorusu

Kullanıcı hangi yaklaşımı seçtiğini ve hangi artifact'in gerçekten hedefe uygulandığını unknown/partial/kanıt ayrımıyla görebiliyor; sınırlı ve güncel paketle yeni oturumda doğru next-action'a dönebiliyor mu? [GAP-01–10](../product/intent-to-reality-gap.md) seçim→hedef uygulama oracle'ını ekler. Native Projects ile ek kullanıcı değeri henüz ölçülmedi. [Ürün sözleşmesi](../product/resume-package-and-memory.md) state, tazelik, izin ve RES-01–08 test oracle'ını tanımlar.

Önerilen dar deney: kaynaklı bekleyen kartlar + yaş/kanıt/coverage + önizle/kopyala devam paketi + ertele/incele. Obsolete tespiti önce mevcut güncel karar/impact kayıtlarına dayanır; bir regex'in bulduğu “yerine” ifadesi doğrulanmış supersession sayılmaz. Tam ürün vizyonu ve 14 MVP kriteri aynen kalır; bu bir öğrenme dilimidir.

## Seçilmiş ilk kaynak ve sonraki bağlantı

[Q02-R1](decision-brief.md) 2026-10-11'de cevaplandı: **A ilk pilot**, maliyet/kurulum bağımlılığını azaltmak için; **B Codex oturumu + tek repo sonra görülmek isteniyor**. C Claude Code-first alternatifi korunur, seçilmedi. Bu seçim deneyin tamamlandığı veya bağımsız ürün yatırımının onaylandığı anlamına gelmez.

A, kullanıcının açıkça aktardığı Claude/ChatGPT parçasını mevcut oracle'a bağlar; seçilmiş tek hedef/ref/path'te read-only gözlem yapar. Dosya varlığı tek başına AC/test başarısı değildir. Q03-R1 A uyarınca ilk deney sentetik/elle etiketli fixture ve deterministik kontrollerle, ek ücretli model API'si olmadan ilerler; gerçek kaynak/hedef izni ve sonraki gerçek veri/provider/bütçe açık kalır. A'nın model/token maliyeti otomatik olarak sıfır veya B'den düşük sayılmaz.

B takip deneyi aynı seçim/uygulama senaryosunu Codex ile tekrarlar: önce MCP brief/query/proposal bağlantısı, ayrıca gerçek host/build destekliyorsa otomatik capture coverage'ı. `tools_only` ile capture-connected ayrı raporlanır; elle import edilmiş olay otomatik capture başarısı sayılmaz. T02/T17/T18 ve [CON-01–08](../architecture/connection-and-context.md#bağlantı-kabul-senaryoları) mevcut görev/kontrol referanslarıdır; yeni tamamlanmış iş oluşturulmadı.

## Önkoşullar ve ilerleme kapısı

- T01 golden corpus/oracle ve T02 kaynak/host capability raporu hazırlanır. Önceki Spike-0 artifact'i varsa ayrı repo/path, revision, test ve izin kapsamıyla incelenir; doğrulanana kadar bağımlılık değildir.
- T03a sınırlı prototype yöntemi/stack önerisi hazırlanır; T03b yalnız yetkili kapsamda küçük deney, T03c sonuç sonrası native/extend/build yatırım ve production stack kararıdır. Prototype T03c sonucunu sınamak içindir; önce sonuç kararı isteme döngüsü yok. Production entegrasyonu için T05/T07/T08 kaynak/kimlik/event/audit, T10 reconciliation ve ilgili context/UI katmanları gerekir.
- **Q03-R1 A kabul edildi:** İlk deneyde deterministic template, örnek/elle etiketli kayıt ve mock job kullanılır; ek ücretli model API'si çağrılmaz. Otomatik anlam çıkarımı uygulaması ve kalitesinin testi zorunlu sonraki doğrulama adımıdır; native/fresh-session model karşılaştırması da ilk no-model sonuçla geçmiş sayılmaz. Gerçek transcript ve sonraki model testi somut veri/provider/bütçe izni gerektirir. Paket hazırlama, gerçek araçta resume veya execution ile karıştırılmaz.
- Q11-A ilk deney için öneridir. Owner tercihi gelmezse taslak/sentetik değerlendirme hazırlanabilir; B host/CLI başlatma uygulanmaz.

## Küçük ardışık görevler

| Adım | Çıktı ve bağımlılık | Gözlenebilir kabul |
|---|---|---|
| S1-01 Kaynak/oracle envanteri | T01/T02/T02d; GAP/RES, human selection ve source/target scope | Aynı projeye bağlı iki chat ve eksik erişim ayrı; beklenen next-step/AC/karar etiketi model çıktısından bağımsız yazılır |
| S1-02 Gerçekleşme/bekleyen iş görünümü | S1-01; karar, artifact, target assessment, yaş ve coverage | GAP-01–05/07/09/10 ve RES-01/05; reported/observed/unknown/partial ve acceptance ayrı; exact ref/path kontrolü fake ise etiketi açık |
| S1-03 Paket şablonu | S1-01; source→task/decision/AC/evidence snapshot ve bounded metin | RES-02/06/07; kritik eksik bağlam görünür, raw transcript talimat değil; LLM çağrı sayısı sıfır |
| S1-04 Önizle/kopyala | S1-02/03; clipboard veya seçilebilir metin fallback | RES-03/04/05; explicit copy, stale/ACL negatifleri, copy run başlatmaz; prototype temel tıklama gerçekten test edilir |
| S1-05 Native ve hafıza deney protokolü | S1-03; bağlı/manual hedef ayrımı, native Projects, fresh-session prompt/paket/full-source ve puanlama | RES-08; model/config/context contamination/usage alanları ve izin kapısı; çalıştırılmadıysa not_run |
| S1-06 Pilot ve karar raporu | S1-04/05; önce sentetik, sonra yalnız izinli gerçek örneklem | Yanlış alarm ve kaçırılan iş için ayrı oracle; stale karar, next-step ve düzeltme maliyeti raporlu; go/no-go ve kalan açıklar |

Adımlar tamamlanmış sayılmaz. Üretim entegrasyonu mevcut backlog'da T20h/T18h/T24m ile izlenir; sıradaki ana iş T01 olarak kalır. Gerçek prototip ile ürün runtime'ı ve doküman taslağı ayrı teslim durumlarıdır.

## İlk no-model dilimin kabul sınırı — Q03-R1 A

- Beklenen karar/görev/ilişki/durumlar elle etiketli veya sentetik oracle'dan gelir; parser'ın kendi ürettiği sonucu oracle yapma. Bu dilim kaynak kimliği, revision, replay/dedup, uygulanma/AC ayrımı ve kısa paket tutarlılığını test etmeye hazırlanır.
- Deney yapılandırması `no_model` olur; ek ücretli provider dispatch, LLM judge, model retry veya alt agent model deneyi bu dilime dahil edilmez. Gerçek runner/provider henüz yok; bu bir kabul kuralıdır, uygulanmış bütçe kontrolü değil.
- Rapor code/fixture sonucunu otomatik serbest metin extraction ve fresh-session model başarısından ayırır. Model koşulları `not_run` kalır. No-model tercihinden toplam geliştirme/host token tüketiminin sıfır olduğu çıkarılmaz; ölçülmeyen maliyet için uydurma sıfır yazılmaz.
- Bütçe/kalite trade-off'u: önce düşük maliyetle domain zincirini sınamak, ardından zorunlu otomatik anlam çıkarımı deneyini dar kapsam ve ölçülebilir yöntemle yürütmek; LLM kullanılırsa veri/provider/tavan ayrıca belirlenir. T01 ve S1 adımları bu karar kaydıyla tamamlanmış olmaz.

## Zorunlu sonraki adım — otomatik anlam çıkarımı

Q03-R1 A yalnız sırayı değiştirir. Konuşmadan karar/görev/soru ve ilişkilerini otomatik çıkarma ürünün temel gereksinimidir; önceden etiketlenmiş kaydı okumak bu yeteneğin uygulanması/testi değildir. Ek ücretli API kullanımı bir yöntem/maliyet kararıdır; ürün gereksinimini isteğe bağlı yapmaz.

| Adım / mevcut görev | Gerekli çıktı ve kabul | Durum |
|---|---|---|
| Hazırlık / T01,T01f,T03f | Kaynak span ve beklenen tip/ilişki/durumlar bağımsız etiketlenir; geliştirme ve holdout ayrılır. Fixture/code kontrolü yalnız domain katmanını doğrular | TODO |
| Uygulama / T09 ve ilgili routing/decoder alt işleri | Gerçek serbest metinden çalışan extractor aday üretir; yöntem/sürüm kaydedilir. LLM kullanılırsa model/veri/bütçe ve ilk dispatch guard'ları önceden hazırdır. Mock çıktı gerçek extraction sayılmaz | TODO |
| Zorunlu ölçüm / T03f,T24,T24q | Gerçek extractor'a expected etiket verilmeden holdout çalıştırılır; tip/karar/soru/ilişki ve source-span doğruluğu, TP/FP/FN, duplicate/yanlış onay/tamamlanma, coverage, maliyet/gecikme ve insan düzeltme yükü raporlanır | not_run |

Ret/negation, “yapıldı” iddiası ile uygulama kanıtı, gecikmiş/bağlamı belirsiz cevap ve değişmiş karar negatifleri mevcut oracle'larla sınanır. [Ölçüm protokolü](../quality/evaluation-protocol.md) scorer, payda ve hata sınırlarını belirler; LLM judge ek değerlendirme seçeneği olarak kalır, zorunlu extractor testinin yerine geçmez.

Semantik test çalıştırılmadıysa fixture prototipi başarılı olabilir; otomatik anlam çıkarımı doğrulandı veya P1b MVP tamamlandı denemez. İzin/erişim/bütçe eksikliği açık blocker'dır; zorunlu işi backlog'dan düşürmez. Yerel/model/provider seçimi bu belgede yapılmadı ve ölçülmemiş başarı eşiği icat edilmedi.

## Hafıza değerlendirme formu

Her testte kaydedilecek alanlar:

| Alan | Kayıt |
|---|---|
| Kaynak kapsamı | Sentetik/izinli gerçek; proje/session/spans, snapshot ve gap |
| Oracle | Güncel karar/AC, beklenen next-action, yasak/eski adım ve gerekli soru |
| Koşul | Prompt-only / paket / full-source; fresh-session yöntemi; erişilebilir araç/context |
| Çalıştırma | Run ID, tarih, model/config, paket digest, tekrar, token/estimated/unknown, bütçe |
| Sonuç | Karar/AC doğru mu; next-step uygun mu; eski planı canlandırdı mı; false-done/izin aşımı var mı |
| Hata nedeni | Capture / extraction / retrieval / stale paket / alıcı model / unknown |
| İnsan değerlendirmesi | Düzeltme ihtiyacı, süre, anlaşılabilirlik, gerekçe ve reviewer |

Bir modelin “anladım” demesi başarı değildir. Plan/cevap güncel oracle ile puanlanır; gerçek kod execution ölçülecekse ayrı workspace/runner izni ve artifact doğrulaması gerekir. İlk memory testi yalnız sonraki adım önerisini puanlayabilir; bu, görevin bitirildiği veya dış hafızanın tüm sorunları çözdüğü anlamına gelmez.

## Çıkış kriterleri ve DoD

- RES-01–07 için deterministik/prototype test kanıtı veya açık not_run nedeni; temel UI gerçekten çalıştırıldıysa test artifact'i ve revision kaydı.
- RES-08 protokol ve rapor: örneklem, karşılaştırılabilir koşullar, tazelik/ACL, unknown tüketim ve izinli çalışma. Gerçek model deneyi yapılmadıysa sonuç yerine hazır protokol sunulur.
- Zorunlu fixture setinde yetkisiz veri/dispatch, kanıtsız tamamlanma ve eski kararı current gibi sunma kabul edilmez. Diğer başarı eşikleri baseline sonrası owner review'una gider; ölçümsüz yüzde veya optimum token hedefi yok.
- Negatif sonuçlar, kaçırılan işler ve yanlış uyarılar rapordan çıkarılmaz. Paket daha kısa fakat gerekli karar eksikse tasarruf başarısı sayılmaz.
- Go/no-go: GAP/RES doğru ve kullanıcı düzeltme yükü kabul edilebilirse native/extension/bağımsız build seçeneklerini aynı maliyet/kalite verisiyle sun. Native yeterliyse ayrı ürün gerekliliği yok; erişim/deney yoksa sonuç unknown ve ek deney/bekleme. Hatalı kabul/uygulama ataması önce çözülür; yatırım owner kararıdır. B başlatma seçeneği için ayrı capability ve izin kapısı devam eder.

Önerilen 3–5 gerçek oturum ve iki haftalık süre yalnız pilot adaylarıdır; takvim, veri erişimi, ücret veya başarı garantisi değildir. Hiçbir gerçek oturum/deney bu doküman hazırlanırken çalıştırılmadı.

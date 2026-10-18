# Ana ürün akışı denetimi — 18 Ekim 2026

**Sonuç: ana otomatik ürün akışı tamamlanmış değil.** Yerel çekirdek, source review, task workflow ve verification parçaları çalışıyor; sürekli konuşma yakalama → gerçek çıkarım → kaynaklı ilişki/karar değişimi → onaylı görev etkisi → sonraki agent'a izinli devam bağlamı zincirinde kritik bağlantılar açık. Test sayısı ve tamamlanan alt parçalar bu zincirin kabulü değildir.

## Amaç ve değerlendirme sınırı

Ürün amacı: kullanıcı/agent diyaloglarından fikir, karar, gerekçe ve işleri yakalamak; farklı oturumlardaki kayıtları aynı proje bağlamında uzlaştırmak; karar değiştiğinde etkilenen görevleri açıklamak; insan yetkisi ve kanıtla güncel durumu tutmak; yeni oturuma doğru devam bağlamını sağlamak. Elle task girilen genel Kanban ürünün esas hedefi değildir.

İnceleme yerel `outputs/decivora` kaynakları içindir; bu dizin Git checkout değildir. GitHub main salt okunur kontrolünde `48f4783f1d1007695649cbbee1c60c0c015c58ac` bulundu. Son diyalog geliştirmeleri ve bu denetim yerelde; bu commit'te yayımlanmış sayılmaz. Önceki P0 model denemeleri korunur; güncel native uçtan uca ürün akışının gerçek modelle geçtiği iddia edilmez. Ücretli API, kullanıcı transcript'i veya gerçek repo/root izni eklenmedi.

**Kanıt türleri:** kod okuması; mevcut runtime/browser regresyonları; yeni context testleri; tekrarlanabilir sentetik seam probe. Statik tespit runtime başarısı diye, fixture yanıtı da gerçek anlam çıkarımı diye gösterilmez.

## Adım adım mevcut durum ve bağlantılar

| Ana adım | Kod / mevcut davranış | Denetim sonucu / gerçek eksik | Mevcut sahibi |
|---|---|---|---|
| Proje/oturum bağlama | `Workspace.bind/receive`, scope ve quarantine çekirdeği; UI mevcut projeler arasında seçim yapar | Gerçek host oturum binding'i ve native adapter kabulü açık. Mevcut proje seçimi proje kurulum/keşif wizard'ı değildir | T05,T06,T16,T17,T19 |
| Diyalog yakalama | `ConversationService.ingest` manual_paste, hash/dedup/receipt; ayrı SourceEvent scaffold yalnız synthetic kabul eder | Sürekli gerçek Codex/Claude oturumu capture yolu bağlı değil. Paste alanı adapter değildir; synthetic flag'i kaldırarak çözülmez | T02,T06,T16,T17,T22 |
| Gerçek anlam çıkarımı | `ResponsesExtractor` strict payload/parser + injected send callback; `DialogueReviewService` dış JSON import'u | Varsayılan launcher extractor=None. Gerçek HTTP/credential/activation ve güncel bağımsız semantic kalite kabulü açık. Bu tek başına bakiye eksikliği değildir | T03,T09,T21 |
| Önceki bilgiyle bağlam kurma | Önce task özetleri vardı | **Bu tur düzeltildi:** task + canonical non-task kayıtları + soru seçimleri/revision + kayıtlı ilişki state/revision aynı hash bağlı context'te. Açıklamalar etiketli excerpt; raw başka konuşmalar ve tüm geçmiş dahil değil. Otomatik önem sıralı tam retrieval değil | T09,T10,T18,T22 |
| Kayıt tipleri / yeni görev | UI/model schema Task/Decision/PendingDecision; core ayrıca Idea/Finding/Risk/Requirement/Prompt/DocumentInstruction/Artifact bilir | Tüm core tipleri model öneri formatında yok. Yeni task review ile To Do olur. Canonical karar kabulü task'a gerekçe ilişkisi otomatik eklemiyor | T09,T10,T22 |
| Uzlaştırma | `reconcile`: exact same title+description duplicate/source attach; aynı title farklı description refinement review | Semantik refines/conflict/supersedes önerisi ve bu ilişkinin kullanıcı çözüm/apply akışı bağlı değil. Disabled refinement adayı çözülmüş sayılmaz | T10,T13,T19 |
| Soru / geç cevap | `QuestionService`, question revision/option/state, exact-ID association; `QuestionDecisionService` ayrı approve/apply | Konuşmadan PendingDecision create, QuestionRequest üretmiyor. Serbest geç cevap→doğru soru önerisi main extractor çıktısına bağlı değil; manuel exact-ID yolu var. Soru seçeneklerini/insan kararını uydurmayacağız | T09,T10,T13,T22 |
| Gerekçe grafiği | typed link/end_link, AND/OR/unknown kernel; UI manual depends_on | Dialogue output'ta kaynaklı required_by/refines/supersedes veya AND/OR proposal formatı yok. Gerçek karar–task grafiği kendiliğinden oluşmuyor | T09,T10,T11,T12 |
| Karar değişimi / etki tetikleme | `DecisionImpactService.preview`: seçili eski karar için geçersizlik hipotezi, task required_when=None | Canonical yeni karardan otomatik tetik yok. UI gerekçeyi vermediğinden mevcut test senaryosu review/after=null üretir. Kernel AND/OR başarılarını bu UI için obsolete otomasyonu diye gösteremeyiz | T10,T12,T13,T19 |
| Etkiyi onaylayıp uygulama | `ReviewService` create/compare/select/approve/apply/ret/defer ve lifecycle guard gerçek SQLite testleri var | 18 Ekim devam tesliminde görev kapsamı edit→select→ayrı approve→apply UI/HTTP bağlantısı kodlandı. 19 Ekim insanın doğruladığı tek karar gerekçesiyle iptal/yeniden açma UI bağlantısı da kodlandı; otomatik semantik değişiklik planı ve genel AND/OR gerekçe yazarı açık. İptal için ayrı geçerli gerekçe ve bağımlılık incelemesi zorunlu | T13,T19,T20 |
| Task durum değişimi | Son dilimde source/context bağlı status proposal, accept/reject/defer, ortak workflow; UI ve fixture-provider yolu testli | Kanıtlı yerel davranış var. Cancelled/Blocked stage'e zorlanmaz; lifecycle/impediment ayrı. Gerçek modelin doğru task/niyet seçtiği henüz ölçülmedi | T09,T13,T14,T19 |
| Verification / gerçek hedef | current AC/DoD, human review, izinli root varsa file SHA, false Done invalidation | Dosya SHA gözlemi test/deploy değildir. Genel otomatik runner ve gerçek hedef pilotu açık. Done claim kabul kriteri kanıtı değildir | T14,T15,T23,T24 |
| Sonraki chat / agent hafızası | sınırlı stdio MCP, current records, get_record current execution state | `_visible` private source'dan türeyen kayıtları/ilişkili component'i gizler; kaynak audience grant UI yok. Proje okuma izni, özel konuşma bağlamını otomatik paylaşmaz. get_project_brief tam task/decision/question/history paketi değildir | T05,T18,T22 |
| Kullanım / operasyon | token reservation, actual/unknown/overrun, freeze, private backup ve restore çekirdeği | Doğrulanmış tokenizer/context/price/para/dönem preflight, güvenilir bütçe uzlaştırması ve clean-machine pilot açık. Dış üyelikte manuel model kullanımına parasal tavan uygulanamaz | T21,T23,T24 |

## Kodla yeniden üretilen kopukluklar

[Probe sonucu](primary-flow-probes.json), [çalıştırılabilir kaynak](../../scripts/probe_primary_flow.py). Komut: `python3.12 -B scripts/probe_primary_flow.py --output /tmp/decivora-primary-flow-probes.json`. Yalnız geçici synthetic fixture DB kullanır; model/ağ/kullanıcı kaydı yok.

1. Task/Decision/PendingDecision kabulü → **3 canonical record, 0 otomatik ilişki**. Ürün için karar–task gerekçe köprüsü açık.
2. PendingDecision kabulü → **1 PendingDecision, 0 soru inbox kaydı**. İki model birbirinin yerine geçmiyor.
3. Probe'un ayrı açıkça kurduğu required_by edge üzerinde UI impact adapter → **review, after=null, canonical mutation yok**. Eksik gerekçede muhafazakâr davranış doğru; otomatik etki/apply ürün zinciri tamamlanmış değil.
4. Kaynaklı 3 canonical record'dan agent brief → **0 record**. Privacy filter doğru çalışıyor; izinli paylaşım/devam UX'i eksik. Filtreyi kaldırmak çözüm değildir.

## Bu tur düzeltilenler

- `DialogueReviewService._context`: görevler dışındaki karar/gereksinim vb. canonical kayıtlar, gerçek soru ID/revision/status/selection ve kayıtlı aktif/eski ilişki state'leri scoped snapshot'a eklendi. Description truncation/recorded-only coverage açık. 100record/64soru/500edge tavanında eksik snapshot sessiz tam gösterilmez. Stored context büyükse yerel artifact sınırı reddeder.
- Aynı kaynak/input ile hazırlanan context, soru cevabı geldikten sonra stale olur; eski yanıt yeni soruya/karara uygulanamaz. Context egress mevcut exact context hash grant'ine bağlı; source-only izin genişletilmedi.
- `ConversationService.analyze` cached readback'i ilk tarihsel analiz yerine en yeni append-only analizi döndürür; görünümle çelişki giderildi. Geçmiş raw yanıt silinmedi.
- Gerçek browser fixture'ında önceki Decision ve açık QuestionRequest artık hazırlanan request içinde doğrulanır; task/status akışı regresyonu korunur.

## Öncelik: hangi kod zinciri kapanmalı?

Yeni task otoritesi veya yeni faz üretmiyoruz. Mevcut backlog kapsamında:

1. **T09/T10:** mevcut kaynaklı response'tan relation/decision-change ve soru/cevap proposal köprüleri; açık quote/revision/uncertainty. Önce dar source→karar→gerekçe→etki→ayrı review senaryosu çalışmalı. Büyük yeni benchmark/kozmetik UI bu yolu ertelememeli.
2. **T13/T19:** mevcut impact review kernel'inin typed command/UI bağlantısı; AND/OR gerekçe incelemesi, seçili grup, ayrı approval/apply; stale/race/iptal/bağımlılık guard'ları korunur. Bu geliştirme API bakiyesi beklemez.
3. **T03/T09/T21:** gerçek HTTP/credential etkinleştirme ve kullanım sınırlarını tamamla; ardından somut model/veri/bütçe onayıyla aynı kullanıcı senaryosunu gerçek modelde çalıştır. “API hazır olunca her şey çalışır” kabulü yok.
4. **T18/T22:** kaynak bazında açık audience paylaşımı ve current continuation pack; sonraki agent doğru kararı, pending soruyu ve task state'ini izinli okuyabilmeli. Yeni erişim politikası/gerçek grant uygulanmadan somut kapsam kullanıcıya gösterilir.
5. **T16/T17/T24:** gerçek host capture, kesinti/yeniden başlama/coverage ve iki adapter kabulü. Manuel input ile çalışan döngü, native capture tamamlandı sayılmaz.

Bağımsız kod hazırlıkları birlikte ilerleyebilir; entegrasyon kabulü ilgili bağımlılık kanıtlarını bekler. Hiçbir mevcut güvenlik/mahremiyet/14MVP kriteri kaldırılmadı. Otomatik modelin doğru anlam çıkarması hâlâ ölçüm gerektirir; yeni genel “built edilebilir” garantisi verilmez.

## İlerleme raporlamasındaki düzeltme

Ana işler hâlâ açık olduğu halde alt modül/test teslimleri konuşmada kullanılır ürün yolculuğuna yaklaşmışız izlenimi verdi. Bundan sonraki her teslim bu tablodaki hangi bağlantıyı kapattığını, fixture/gerçek kullanıcı-model kanıtını ve açık uçtan uca kapıyı belirtmeli. Ana akış dışında gerekli güvenlik işi yapılabilir; fakat ana ürün tesliminin yerine sayılmaz. Bu denetim ürünün tamamlandığı raporu değildir.


## Doğrulama sonucu

**351runtime testi,48kök/takip testi ve dokuz tarayıcı akışı geçti;44Mermaid render failure0.** Dört yeni regresyon önceki karar/soru/ilişki içeriği, cevap sonrası context invalidation, etiketli excerpt ve en yeni analiz readback'ini doğrular. Browser testi önceki canonical Decision ve gerçek QuestionRequest'in request'e taşındığını doğrular. Bu testler main product gaps'i kapalı saymaz. [Makine kaydı ve kaynak hash envanteri](primary-flow-results.json), [yeniden üretilen seam sonuçları](primary-flow-probes.json). Kullanıcı DB'sinde veya gerçek modelde bu fixture'lar çalıştırılmadı.


### Devam teslimi — görev kapsamı değişikliğini uygulama

T13/T19 kapsamında artık impact kartından revize task description hazırlanır, grup seçilir, ayrı onaylanır ve uygulanır; ret/erteleme kalıcıdır. Bu, yukarıdaki UI-apply kopukluğunun task-update alt bölümünü kapatır; automatic relation/decision-change açık kalır. 19 Ekim lifecycle-cancel/reopen UI, insanın doğruladığı tek karar gerekçesi ve mevcut guard'larla ayrıca bağlandı. [Kod teslim kaydı](workflow-ui-runtime.md#18-ekim--etki-kartından-görev-değişikliğini-uygulama).

### 19 Ekim devamı — geç cevap önerisi köprüsü

Soru/geç cevap satırındaki manuel-only sınırının bir bölümü kapandı: güncel context soru kimlik/sürüm/seçeneklerine kaynak alıntılı model önerisi bağlanır; insan ayrı doğrular ve cevap ile review makbuzu atomik kaydedilir. Eski veya cevaplanmış soru değiştirilemez. Gerçek semantik eşleştirme kalitesi, konuşmadan yeni QuestionRequest, relation/decision-change planı ve native capture hâlâ açık. [Güncel kod sözleşmesi](dialogue-status-runtime.md#19-ekim--kaynaklı-geç-cevap-önerisi).

### 19 Ekim devamı — mevcut kayıtlar için relation→impact köprüsü

Dialogue/model JSON artık source quote ile mevcut Task→Decision required_by ve Task→Task depends_on önerisini taşır. İnsan review sonrası gerçek graph event ve kaynaklı makbuz atomik uygulanır. Uygulanan rationale kartı açık insan retirement hipoteziyle mevcut impact önizlemesine götürür. Genel AND/OR gerekçe, yeni candidate endpoint, supersession/decision change ve gerçek model kalitesi henüz kapanmadı. [Güncel uygulama](dialogue-status-runtime.md#19-ekim--kaynaklı-ilişki-önerisinden-etki-incelemesine).

### 19 Ekim devamı — kaynaklı karar replacement

Dar Decision→Decision supersedes önerisi human review ile canonical edge ve kaynaklı makbuza bağlandı. Karttan onay öncesi/sonrası etki önizlemesi var. Eski kayıt/gerekçe/Done geçmişi korunur; yeni graph bağlamı current verification'ı geçersiz kılabilir. Global validity/AND-OR karar planı ve gerçek anlam doğruluğu açık. [Güncel sınır](dialogue-status-runtime.md#19-ekim--konuşmadan-kararın-yerini-alan-seçim).

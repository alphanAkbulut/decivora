# Başka bir LLM bu repodan ne anlamalı?

**20 Ekim — gerçek düzenli Codex capture geçti; T17 çekirdeği Done:** Native B,10sarayla3kez seçili scope içinde okundu; kaynak6→6, duplicate0, task/kapsam ve API bütçesi değişmedi. Stop+Disconnect+reload doğrulandı. T17mevcut çekirdek kabulü evidence ile kapandı; ana8Done/20InProgress/2ToDo, MVP yolunda16iş açık. Yeni mesaj eklenmesi/semantik kalite bu3read'de ölçülmedi; günlük/release T24 ve yeni mesaj model paylaşımı açık. [Sonuç ve kapanış gerekçesi](../quality/scheduled-native-001.md).

**20 Ekim — düzenli yakalama kodlandı:** Mevcut seçili-sohbet iznine bağlı kalıcı plan/tick, sınırlı worker, ayrı start/stop ve Sources kontrolleri eklendi. Süre/read/interval, in-flight stop ve restart-no-autostart korunur. Yeni kayıt modele otomatik paylaşılmaz. Gerçek periyodik sohbet okuması başlatılmadı; önceki izinler tüketilmiş kalır. [Kod, bulgular ve kalan kapılar](../quality/scheduled-capture-runtime.md).

**Son owner onayı — kapsam ve başlangıç:** İlk turdaki bağlı soru tercihi korundu; kullanıcı açıklamadan sonra önerilen AC/DoD ve güncel başlangıç işlemini onayladı. Aynı tek Task artık **In Progress**, contract v1; kapsam sorusu **Resolved**, AC1/DOD1 **not_run**. Eski model önerisi stale/Deferred geçmişte tutuldu; yeni API veya chat read0, bütçe değişmedi. [Karar ve uygulama kanıtı](../quality/native-ui-journey-001.md#son-owner-kararı--kapsam-onayı-ve-güncel-başlangıç).

**20 Ekim — gerçek LOCAL kullanıcı yolculuğu:** İki seçili sentetik Codex sohbeti arayüzden birer kez yakalandı (6kaynak); iki Luna isteği A'da tek Task, B'de aynı Task ID'sine In Progress önerisi üretti. Owner AC/DoD yerine bağlı kapsam sorusunu seçti: Task To Do, soru Opened; durum uygulanmadı, kanıt/Done yok. İki istek4236token, tahmin$0.000609; root54dispatch/108HTTP/$0.067895 (önceki3unknown rezervi dahil). Kaynak/model dar izinleri tüketildi. [Sonuç, karar gerekçesi ve UI-J01 düzeltmesi](../quality/native-ui-journey-001.md).

**20 Ekim — onaylı API süre yenilemesi:** Kullanıcı aynı toplam sınırlarla 24 saat yenilemeyi onayladı. Dönem 20 Ekim 13:35:38–21 Ekim 13:35:38 Türkiye saati (UTC+3). $3 toplam tavan, 100 model/200 HTTP, istek başına 10.000 giriş/2.000 çıkış korunur; geçmiş 52 dispatch/104 HTTP bütçe payı ve $0.067286 taahhüt taşındı. Üç unknown actual=null ve toplam $0.006750 rezerviyle korunur. Kalan 48 model/96 HTTP ve $2.932714 yerel paydır; hesap bakiyesi/fatura değildir. LOCAL profil Available, worker kapalı; yeni sohbet okuma/model çağrısı yok. Kaynak paylaşımı ve aktivasyon ayrıca gerekir. [Taşıma ve doğrulama](../quality/openai-development-budget.md#20-ekim--aynı-toplam-sınırlarla-onaylı-süre-yenilemesi).

**20 Ekim Sprint1 — paylaşım ve ilk scope:** Yeni kaynağın exact source/context model-sharing preview+approval akışı ve ilk Task review'ında human AC/DoD veya bağlı clarification kodlandı. Approval dispatch değildir; kriterler not_run. [Uygulama, sınırlar ve NM-02](../architecture/source-sharing-and-first-review.md). Gerçek provider UI kabulü yeni source scope ve geçerli policy dönemi gerektirir; ücretli çağrı0.


**20 Ekim sonraki Sprint1 teslimi:** Sources ekranına exact Codex chat ID/link ile bounded yerel capture izni, ayrı tek-okuma ve disconnect bağlandı. Yapılandırma host/sohbet okumaz; model egress grant oluşturmaz. [Uygulama, hata/yarış sınırları ve sequence](../architecture/codex-source-onboarding.md). Native kabul yeni gerçek kaynak izniyle ayrıca yapılacak; NM-02ve sürekli otomasyon halen açık.


**20 Ekim Sprint1 kod teslimi:** Sources ekranında mevcut izin seçimi→Paused aktivasyon→activate/pause/revoke ve sınırlı worker planı/start/stop bağlandı. Yerel sentetik tarayıcı kabulü; gerçek kaynak/API çağrısı0. Yeni sohbet izin/transport onboarding halen açık. [Sprint/mikro plan](sprint-plan.md) · [Kod ve sınırlar](../architecture/model-activation-runtime.md#20-ekim--sources-ekranında-aktivasyon-ve-worker-kontrolleri). Ana7Done/21InProgress/2ToDo korunur.


**20 Ekim — Native A/B model zinciri:** A'dan tek Task önerisi, kullanıcı onayıyla To Do kaydı; B'den yeni Task açmadan aynı ID için In Progress önerisi alındı. İlk uygulama AC guard'ında durdu. Ayrı kapsam onayından sonra eski öneri stale korunarak güncel insan işlemiyle In Progress uygulandı. Tek Task, AC/DoD not_run; iki model + iki sayım isteği, 4.104 token, tahmin $0,000584. [Sonuç ve sınırlar](../quality/native-two-model-001.md). Deney izni tüketildi; varsayılan uygulama otomatik etkinleştirilmedi.

**20Ekim gerçek Native A/B sonucu:** normal input üzerinden2human+4assistant kaynak yakalandı; iki geçişte6→6, yeni duplicate0; reopen readback6. Kaynak izni tüketilip bindingler kapatıldı. Model çağrısı0; aynıTask/ilerleme semantik kabulü henüz yok. [Makbuz ve sınırlar](../quality/native-two-chat-001.md). Aşağıdaki önceki “hazır/izin bekliyor” notları tarihsel hazırlıktır.

**20Ekim native iki-chat hazırlığı:** Yeni kaynak izni kabul edildi; Native A/B oluşturuldu. Private plan `outputs/decivora-local-data/native-two-chat-001/capture-plan.json`, ayrıpilot.sqlite; workspace native_two_chat_001/project atlas_native/local_owner. İki chat kimliği yalnız bu manifest'ten seçilir; başka kaynak okunmaz. Max10tur/thread, iki geçiş,2saniye; provider_dispatch_allowed=false. Kaynak/geçiş0, normalhumaninput bekleniyor. Henüz gerçek capture yapıldı deme; önce kullanıcı ilgili chatlere örnekleri yazmalı. Sonraki test yalnız bu plan kapsamında başlar; mevcut gerçekTEST/LOCALDB değiştirilmez. Bu hazırlık notu henüz yeniGitHubcommit'i olarak doğrulanmadı.

**20Ekim — iki Codex sohbeti:** aynı native sohbeti yeniden bağlamada yakın geçmiş kaybı düzeltildi;1–4explicit seçilmiş thread için ortak sınırlı pipeline ve read-only CLI eklendi. Shared proje Task/soru context'i ile thread-local raw history ayrı tutulur. [Kök neden ve gerçek iki-pencere test planı](../quality/native-two-chat-review.md). Yerel11kontrol geçti; gerçek iki-pencere kabulü henüz yapılmadı. Yeni ücretli çağrı yok.

## 20 Ekim 2026 — güncel kanıt özeti

Bu özet önceki tarihli teslim notlarının yerine geçen güncel okuma noktasıdır; tarihsel raporlar değiştirilmedi. Ana görevler **7 Done / 21 In Progress / 2 To Do**; alt kayıtlar **56 Done / 42 In Progress / 26 To Do / 5 Proposed**. Bunlar farklı seviyelerdir, toplanmaz.

- Seçilmiş sentetik Codex sohbetinde **2 human + 6 assistant kaynak**, tekrar okumada **8→8**: bu dar native capture doğrulandı. Canonical görev In Review, kabul kriterleri not_run; tam günlük otomasyon değil.
- İlk dört-case grubunda **J01 6/6 dar kontrol pass; J02/J03 5/6 eksik; J04 iki yanıt aldı, biri valid/biri unsupported_question**.20dispatch/18tam provider yanıtı/2unknown; J04kalan4tur gönderilmedi. [Son rapor](../quality/dialogue-batch-001-j04.md).
- Task'a bağlı netleştirme review/resolve ve >7 günlük bilinen blocker başlangıcı uyarısı yerel kodda var. Yeni clarification talimatı gerçek modelle yeniden ölçülmedi; bilinmeyen blocker başlangıcına yaş uydurulmaz.
- Son J03unknown rezervi için kullanıcı ayrı onay verdi. Yalnız J04planı iki çağrıdan sonra response-validation hatasında durdu; yeniunknown yok, root frozen=false. Bu, sonraki gruba veya yeni trial'a otomatik izin değildir.
- Birikimli root kaydı50dispatch/100HTTP bütçe payı; bilinen tahmin$0.059952 + korunan unknown rezerv$0.006750 = $0.066702. Fatura veya hesap toplamı doğrulanmış değildir. Aynı$3/expiry sözleşmesi korunur; süresi geçmiş izin yenilenmiş sayılmaz.

Kararlar ve gerekçeler [DEC-23–27](../product/decision-map.md), bulgu/aksiyon/kanıt ayrımı [güncellik denetiminde](../quality/documentation-currency-audit.md). Varsayılan uygulama modeli kapalıdır; native pilot, sentetik model batch'i ve ürün kabulü ayrı kanıtlardır.


## Önceki teslim notları — tarihsel okuma

Aşağıdaki tarihlere bağlı notlar ilk teslim anını anlatır; en üstteki20Ekim özeti ve bağlı son rapor geçerlidir. Eski sayaç/izin/kapasite notunu güncel yetki veya blocker sanma.

Görev durumları19Ekim'de129alt/30ana satır üzerinden [teyit edildi](../quality/task-status-audit.md). Tanımsız statü0; kod/test/plan ve tam kabul ayrımı korunur. Eski tarihli “açık/uygulanmadı” metnini tek başına yeni blocker yapma; current-state ve audit reason/evidence/remaining kabulünü kullan.

Güncel T17: [kalıcı sayfa checkpoint](../quality/codex-exec-capture-runtime.md#page-atomic-continuation--19-october) source/cursor/restart/pending assistant ve yerel profile dedup kodunu anlatır. Önceki gerçek source izni tüketildi; yeni kod yalnız sentetik doğrulandı. Indexed1000kaynak/25sayfa ve queue metadata teslim edildi. Kaynak başına trusted model factory UI command/queue yoluna bağlandı; [aktivasyon sınırları](../quality/conversation-processing-runtime.md#kaynak-başına-model-aktivasyonu--19-ekim-2026). [İlk6gerçek kayıtlı kaynak pilotu](../quality/saved-source-pilot-001.md) tamamlandı:6Ready for review/7öneri/$0.002963; kaynak envelope hatası düzeltildi. Orijinal TEST değişmedi, canonical apply0. Kalıcı [aktivasyon backend lifecycle](../architecture/model-activation-runtime.md) kodlandı; kalıcı sınırlı processing worker API/claim/start/stop bağlantısı da kodlandı. Onboarding ekranı, yeni mesaj kaynak izni ve semantik insan kabulü açık; tek deneme izni tüketildi. Plan: [iyileştirme değerlendirmesi](../quality/capture-improvement-assessment.md). Parent T17 açık.

Log ekip erişimi: [kod/doküman boşluk incelemesi](../quality/log-access-retention-gap-review.md). HTTP hâlâ local_owner; own-user filtre, actor/on_behalf_of, loga özel roller ve zaman bazlı retention uygulanmış sayılmaz. Tasarım rol matrisiyle çalışan local görünümü karıştırma.


Operations açıklaması: [diagram ve şema okuma rehberi](../architecture/logging-diagrams-and-schema.md). ER gerçek sidecar tablolarını, DTO şeması read çıktısını anlatır. Error group/run correlation veya her engine'in izlenmesi varmış gibi çıkarım yapma.


Runtime teşhisi: [log çalışma rehberi](../architecture/logging-audit.md#teşhis-ve-geliştirme-çalışma-rehberi) ve [insan kontrol ayrımı](../architecture/logging-audit.md#manuel-kontrol-ne-zaman-gerçekten-gerekli). Operations local command sınırlarını izler; başarısız testte önce izinli tanı+canonical sonuç+TEST reproducer'ı incele. Kullanıcıdan yalnız gerçekten insan katkısı gereken kararı iste; otomatik incident/alert/correlation uygulanmış deme.


Güncel 19 Ekim ek teslim: [Operations ve TEST ortamı](../quality/operations-runtime.md). Komut sınırları izlenir; bütün pipeline izleniyor deme.

Son durum özeti: [current-state.md](current-state.md). Kanonik ana durum7Done/21InProgress/2ToDo; MVPye giden17ana iş,6gelecek faz. Q06/Q08 kabul edilmiş; work-breakdown deferred_choices listesinden çıkarıldı.

19 Ekim: [gerekçeli lifecycle UI](../quality/workflow-ui-runtime.md#19-ekim--gerekçeli-iptal-ve-yeniden-açma-arayüzü) iptal/yeniden açma ve history kullanıcı bağlantısı tamamlandı; tek karara bağlı gerekçe insan tarafından açıkça doğrulanır. Genel AND/OR yazarı, semantic relation ve resolution editor açık.

Önceki kod teslimi: [impact task scope review/apply](../quality/workflow-ui-runtime.md#18-ekim--etki-kartından-görev-değişikliğini-uygulama). Preview artık explicit task edits→select→separate approve→apply UI/HTTP sunuyor. Önceki “UI yalnız preview” tespiti bu alt kapsamda giderildi; automatic source relation/decision proposal ayrı açık; cancellation/reopen UI 19 Ekim diliminde bağlandı. Manual conversation receipts eski impact approval'ı invalid eder.

Öncelikli güncel devir: [ana ürün akışı denetimi](../quality/primary-flow-audit.md). Asıl kullanıcı değeri zinciri tamamlanmadı; native/model/relation/question/impact-apply/private-resume kopukluklarını oku. Son context düzeltmesini full automatic memory diye sunma.

18 Ekim ek teslim: [diyalogdan görev/durum](../quality/dialogue-status-runtime.md). Yeni import UI + provider context schema ortak doğrulaması; varsayılan model kapalı. Gerçek semantik kalite/native capture ve güvenli ücretli aktivasyon kapıları açık.

Bu repo kaynak sohbet açılmadan ürünün amacı, evrimi, kapsamı, proposed mimarisi ve sıradaki işi anlaşılabilecek şekilde hazırlanmıştır. **Doküman tamlığı, uygulama doğruluğu veya modelin mutlaka doğru anlayacağı garantisi değildir.** Q15-A ile ilk uygulama iskeleti [T04](../../apps/hub/README.md) kendi12test/clean-start kabulüyle tamamlandı; T05f in-memory project/binding çekirdeği ve CLI demo da [uygulandı](../quality/project-binding-core.md); [T05g project store](../quality/project-store.md) restart/idempotency/rollback ile uygulandı; [T05h local authority](../quality/local-authority.md) persisted revision/deny sağlıyor; login/token ve gerçek ingress/production backup hazır sayılmaz. Yerel/manual ACL, queue, backup/restore [integrated core](../quality/integrated-core.md) ile uygulandı; [kritik inceleme](../quality/core-critical-review.md) CR01–06 düzeltmelerini ve109runtime test sınırını tutar. Model/capture/native/ROI/gerçek kullanıcı UI kabulü açık.

[T12/T12a](../quality/impact-preview.md) local manual preview tamamlandı:130runtime test, immutable persisted proposals, source/graph/authz snapshot ve stale guard. `impact-demo` altı oracle case'ini gerçekten çalıştırır; task state değişmez. Sıradaki mevcut iş T13 ayrı review/onay; T14 gerçek evidence/completion.

[T13a](../quality/review-kernel.md) seçim/ayrı approval/atomic apply çekirdeği uygulandı;148runtime test, yeni [schema/sequence](../architecture/review-runtime.md). Ana T13 In Progress; T13b/c/e açık, sıradaki cancellation lifecycle.

[T13b lifecycle](../quality/task-lifecycle.md) uygulandı;168runtime test. cancel/edge ending/compensating reopen ayrı; current schema/diyagram [burada](../architecture/task-lifecycle.md). Sırada T13c versioned AC/DoD, sonra T13e pending question. Ana T13 hâlâ açık.

[Yerel program](../quality/local-preview.md) artık launcher ile açılır. T13c Done, T19/T20 ilk UI dilimi IP;185runtime test ve gerçek browser flow. Sırada T13e ve T14, sonra programa full review/evidence/capture bağlama. Manuel UI otomatik AI-native MVP değildir.

## Kısa giriş

Decivora geçici çalışma adıdır. Problem AI sohbetlerinde fikir/karar/prompt/yarım işlerin kaybolması ve yeni karar sonrası gereksiz işlerin açık kalmasıdır. Kullanıcı kart/DoD yazmak istemez, hazırlanmış onay vermeye razıdır. Ürün bütün çıktıları yakalamayı, eski bilgiyle uzlaştırmayı, gerekçe grafiğinde etkisini çıkarmayı ve revision'a bağlı kanıtla ilerlemeyi göstermeyi hedefler. Çok proje ve repo olmayan araştırma projeleri kapsamdadır. İlk tasarım local-first; Q15-A/ADR-0012 koşullu ilk çekirdek build'i ve Python3.12/SQLite runtime'ını kabul eder; frontend/ekip/cloud ve native/ROI sonuçları açık.

## Soru → yetkili belge

| LLM'in cevaplayabilmesi gereken soru | Okunacak yer |
|---|---|
| Ürünün problemi ve değişmez kullanıcı tercihleri ne? | [Vizyon](../product/vision.md), [AGENTS](../../AGENTS.md) |
| Fikir neden basit task tracker'dan farklılaştı? | [Evrim](../discovery/evolution.md), [karar haritası](../product/decision-map.md) |
| Hangi özellikler olacak, kullanıcı nasıl kullanacak? | [Tam kapsam](../product/full-scope.md), [özellik kataloğu](../product/feature-catalog.md) |
| MVP ne; hangi fikirler daha sonra? | [MVP](../product/mvp.md), [roadmap](../../ROADMAP.md) |
| Konuşulan engine'ler nerede? | [Engine ve alias haritası](../architecture/engines.md) |
| Sistem nasıl çalışacak ve yanlış nerede olabilir? | [Diyagram atlası](../architecture/diagrams.md), [runtime sözleşmeleri](../architecture/runtime-contracts.md) |
| Karar neden seçildi; kesinleşti mi? | [ADR dizini](../architecture/adr/README.md), [açık kararlar](../governance/open-decisions.md) |
| Veri, status ve ilişkiler ne demek? | [Domain](../architecture/domain-model.md), [event log](../architecture/event-log.md) |
| Neyi rakiplerden farklı hedefliyoruz? | [Farklılaşma](../product/differentiation.md), [kanıt seviyeli benchmark](../discovery/benchmark.md) |
| Şimdi ne yapılacak, nasıl bitecek? | [Status](status.md), [backlog](backlog.md), [kısa yönetim planı](project-management.md) |
| Receiver/yenichat ne durumda; hangi kod çalıştı? | [İlk gerçek failed run](../quality/receiver-001-result.md), [yerel schema/source guard ve akış](../quality/receiver-contract.md), [yeni RECEIVER-002 hazırlığı](../quality/receiver-next-plan.md), [wire-2 proje incelemesi](../quality/project-review-next.md); [RECEIVER-002 actual tek run](../quality/receiver-002-result.md) invalid_contract; Q03-R6 tüketildi, yeni inference izni yok |
| Tipli veriler için receiver hatası nasıl azaltıldı? | [T03aa kod/kanıt](../quality/typed-review.md): source-only deterministic taslak, model0; önceki failed actual raw ayrı, free-text extraction başarı iddiası yok |
| İnceleme kaydı program kapanınca saklanıyor mu? | [T03ab](../quality/review-store.md): iki sentetik profile SQLite snapshot/pending descriptor restart; source/access yeniden kontrolü. [T03ac](../quality/reply-store.md) explicit fixture late reply persistence ekler; actual insan approval/resolution/UI/IAM henüz yok |
| Hangi sonuç kanıt sayılır? | [Doğrulama](../quality/verification.md), [ölçüm](../quality/measurement.md) |
| Hangi eksikler bulundu ve hangileri hâlâ açık? | [Kapsam/mimari incelemesi](../quality/completeness-review.md) |
| İnsanların hangi şikâyetleri bu yönü destekliyor; karşı kanıt ne? | [Kullanıcı araştırması ve ters düşünme](../discovery/user-research.md) |
| Benchmark gerçekten çalıştırıldı mı? | [Bulgular ve test edilmemiş alanlar](../discovery/benchmark-findings.md) |
| Bekleyen işe yeni chat'te nasıl devam edilir; hafıza yeterli mi? | [Ürün önerisi](../product/resume-package-and-memory.md), [Spike-1 v1](spike-1-v1.md); production proposed/not_run. P0 [resume kodu](../quality/resume-compaction.md) ve [receiver sonucu](../quality/receiver-001-result.md) ayrı scoped kanıt |
| Pilot için owner neyi seçti, hangi yanıtlar bekliyor? | [Sorular ve cevaplar](decision-brief.md) |

## Belge otoritesi ve çelişki çözümü

Güncel yetkili kullanıcı talimatı ve uygulanabilir AGENTS kuralları izlenir. Ürün kapsamı full-scope, sürüm kabulü MVP, teknik gerekçe statülü ADR, güncel ilerleme status, görev AC'si backlog içindedir. Özellik kataloğu ve diagramlar bu kaynakların açıklamasıdır; yeni karar otoritesi değildir. Runtime sözleşmesi teknik öneriyi detaylandırır; ADR kabul edilmiş gibi yorumlanmaz. Kaynak sohbet tarihsel veri, rakip README'si documented iddia, test raporu yalnız belirtilen revision için kanıttır.

Çelişkide sessizce daha yeni dosyayı doğru sayma: farkı ve etkiyi kaydet, mevcut kabul edilmiş invariant'ı koru; uygulama yönünü etkiliyorsa somut karar iste. Bütün dokümanları her tur yeniden okutma; bu indeksle hedefli retrieval yap.

## Sözlük ve karıştırılmaması gerekenler

- **Source:** gözlenen mesaj/olay; talimat, doğru bilgi veya onay değildir.
- **Candidate:** çıkarılmış öneri; accepted task değildir.
- **Evaluation:** neyin hangi bağlamla değerlendirildiği; insan kararı değildir.
- **Canonical:** onay/policy sürecinden geçen güncel proje kaydı; evrensel doğru iddiası değildir.
- **ChangeSet:** atomik uygulanacak ilişkili operasyon önerisi; geçmişi düzenlemez.
- **ImpactRun:** belirli graph snapshot'ında reason path ve kapsamla yapılan etki değerlendirmesi.
- **Evidence:** belirli AC ve artifact revision'ı için kanıt; generic “done” metni değildir.
- **PendingDecision:** konusu/seçenekleri/blokladığı işler belli karar ihtiyacı; her belirsiz cümle kesin taahhüt değildir.
- **Obsolete / cancelled / superseded / completed:** sırasıyla gerekçe kalmaması / yetkili durdurma / yeni sürümle yer değiştirme / gereken kanıtın sağlanması. Aynı sütuna indirgenmez.
- **Engine:** modül sorumluluğu; ayrı servis veya ayrı agent şartı yoktur.

## Anlama kontrolü: beklenen cevaplar

1. Yeni mimari geldiğinde eski bütün işleri kapatır mıyız? **Hayır.** Tipli gerekçe, AND/OR/unknown, alternatif kullanım, current applicability ve insan onayı gerekir.
2. “Task done” mesajı gelirse? **Implementation claim.** Gerekli AC ve artifact revision kanıtı yoksa verified değil.
3. Yeni OR edge preview sonrası eklendiyse? **Stale impact.** Yeni snapshot/diff; eski onay taşınmaz.
4. Model kapalı veya budget doluysa? **Kaynak korunur.** Deterministik işler yapılabilir; semantik iş deferred/unknown görünür.
5. ChatGPT Chat içeriğine otomatik erişim garanti mi? **Hayır.** Yüzey/izin/build bazlı capability testi; açık import fallback.
6. Çalışan çekirdek veya onaylı stack var mı? **Sınırlı evet:** Q15-A/ADR0012 Python3.12/SQLite; T04 CLI ve T05/T06/T07/T08/T11 yerel normalized core code/test. Tam ürün MVP, login/adapter/UI/model kalite kabulü yok; T01–T03 evidence açık.
7. Knowledge Evolution Engine eksik bir ayrı servis mi? **Hayır.** ENG-03/04/05/06/07 birleşik davranışının kaynak konuşmadaki adı.
8. Üstünlük ve tasarruf kanıtlandı mı? **Hayır.** Hipotez/ölçüm planı var; benchmark runtime sonucu yok.

Sonraki LLM'den bu cevapları ve aşağıdaki ek kontrolü ilgili belgeyle destekleyebilmesini bekleriz. Bu bir **handoff kontrol protokolüdür**; bağımsız LLM deneyi yapılmış değildir.

## Ekip ve veri için ek anlama kontrolü

9. Owner'ın agent'ı owner gibi onay verebilir mi? **Hayır.** İnsan izni, dar grant, run, kaynak ACL ve policy kesişir; insan approval yetkisi devredilmez.
10. Private sohbetten türetilen özet ekibe otomatik açılır mı? **Hayır.** Kaynak erişimleri korunur; paylaşım ayrı redakte kayıt ve onaydır.
11. Context dolunca proje hafızası silinir mi? **Hayır.** Context geçicidir; canonical geçmiş ve dedup kimliği ayrı dayanıklılık taşır.
12. SQLite WAL denetim logu mu? **Hayır.** Domain log, security audit, source ve operational telemetry ayrı kayıt sınıflarıdır.
13. DB ekip büyümesine hazır mı? **Henüz uygulama yok.** Local SQLite ve merkezi PostgreSQL geçişi için ölçüm, migration ve recovery planı var; kapasite kanıtlanmadı.

Kaynaklar: [identity/access](../architecture/identity-access.md), [logging](../architecture/logging-audit.md), [storage/memory](../architecture/storage-memory-capacity.md), [benchmark](../discovery/collaboration-storage-benchmark.md), [fazlı işler](team-data-plan.md). Handoff protokolü artık 13 soruyu içerir; bağımsız model deneyi yapılmadı.

## Bağlantı, token ve graph için ek sorular

14. MCP kurmak tüm geçmişi yakalar mı? **Hayır.** [Capture, tool ve UI yolları](../architecture/connection-and-context.md) ayrı; tools-only coverage mümkündür.
15. MCP/token cache toplam tüketimi garanti düşürür mü? **Hayır.** [Host/arka plan ayrımı ve bütçe sözleşmesi](../architecture/routing-token-economy.md) yalnız kontrol edilebilen alanı sınırlar; kullanım/kalite ölçülmeli.
16. Task iptal edilince okları siler miyiz? **Hayır.** Task cancelled, edge ended/invalidated ve privacy purge ayrı işlemdir; [graph geçmişi](../product/graph-experience.md) korunur.

Handoff kontrolü toplam 16 sorudur; bağımsız LLM testi yapılmadı. Q04 güncel/seçili bağlamı, Q05 kullanıcıya proje/görev bazlı profil seçimini kabul eder. Otomatik context dosyası Q06 ve gerçek veri/bütçe Q03 ayrı sorulardır.

## Ürün önceliği için ek kontrol

17. Blocked task'ı sürekli tekrar çalıştırır mıyız? **Hayır.** Engeli kaldıran uygulanabilir adım/karar öne çıkar; dış beklemede hedefe katkılı hazır iş seçilir. Çok bağlantı tek başına yüksek değer veya ready kanıtı değildir.
18. Scrum yaklaşımı AI'nın Product Owner olması veya başlamış Sprint anlamına gelir mi? **Hayır.** Ürün değeri, engel etkisi ve küçük doğrulanabilir teslim ilkeleri kabul edildi. Ürün sorumluluğu kullanıcıda; uygulayıcı teknik planı yetkisi içinde yapar. Formal roller/takvim ve dış bildirim seçilmedi.

[Öncelik sözleşmesi](../product/priority-and-flow.md), [çalışma planı](project-management.md) ve [Q09](decision-brief.md) referanslardır. Kontrol toplam 18 sorudur; bağımsız LLM testi yapılmadı.

## Çok-agent ve ekip kurulum kontrolü

19. Tek insanın birçok agent'ını takip etmek için takım SaaS'ı veya özel düşünce erişimi gerekir mi? **Hayır.** İzinli task/run/tool/artifact kayıtları ve dar ortak hafıza yeterli temel; provider'ın sunmadığı input/parent bilinmiyor kalır. Agent'ı başlatmak ayrı yetkidir.
20. Ürünü ekibe vermek owner hesabını/DB dosyasını paylaşmak mıdır? **Hayır.** Merkezi servis, ayrı üyelik/oturum ve agent grant'leri gerekir; kişisel kaynakların paylaşılması ayrı onaylıdır. Bugün ekip kurulum paketi veya SaaS yoktur.

[Agent ve ekip işletim belgesi](../architecture/agent-and-team-operation.md) iki senaryoyu, test kapılarını ve platform kaynaklarını açıklar. Toplam 20 kontrol sorusu; bağımsız LLM deneyi yapılmadı.

## Subagent soru yönlendirme kontrolü

21. Parent agent subagent'ın her sorusuna kullanıcı yerine karar verebilir mi? **Hayır.** Bilgi/görüş sağlayabilir ve kendi yetkisi içindeki teknik seçimi yapabilir. Scope/AC/izin gibi korunan karar güvenilir insan approval'ı ister; agent'ın “owner kabul etti” mesajı yeterli değildir.
22. Soru cevaplanınca bütün görevler otomatik devam edip tamamlanır mı? **Hayır.** Revision/izin ve diğer blocker'lar kontrol edilir. Yalnız bağlı işler bekler; bağımsız işler ilerleyebilir. Host delivery/resume desteği yoksa destek varmış gibi gösterilmez; görev completion yine kanıta bağlıdır.

[Soru/karar sözleşmesi](../architecture/agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider) timeout, parent kaybı, döngü, çelişki ve geç yanıt istisnalarını tanımlar. Toplam 22 kontrol sorusu; bağımsız LLM testi yapılmadı.

## Güncel yatırım ve gerçekleşme anlama kontrolü

23. Şimdi ürün v3 veya bitmiş yeni MVP var mı? **Hayır.** [Tasarım revizyonu 03](../product/current-direction.md), aynı tam vizyonun ilk kanıt odağını günceller. Tek güncel set main'de; geçmiş Git'te, [sürüm düzeni](../governance/versioning.md) product/schema/task sürümlerini ayırır.
24. Dosya üretimi, yeni soruya geçiş veya agent “kullanıcı seçti” özeti yeterli mi? **Hayır.** Güvenilir insan selection'ı, generated artifact, exact target application ve AC verification ayrı. [Domain](../architecture/domain-model.md#artifact-ve-hedef-uygulama-gözlemi), [ER-03](../architecture/data-relationships.md#er-03--artifact-hedef-uygulama-ve-kabul-ayrımı), [GAP oracle](../../examples/intent-reality-scenario.json).
25. İlk prototipten sonra mutlaka bağımsız ürün mü? **Hayır.** T03a yöntem → T03b yetkili deney → T03c native/extend/build/ek deney/durdur. Native Projects kıyası yoksa üstünlük unknown; test edilmiş typed fixture actual capture/fresh-session başarısı değildir.

Güncel kontrol toplamı **25**; önceki toplamlar tarihsel ekleme kayıtlarıdır. Bağımsız LLM anlama testi henüz yapılmadı. İlk okuma güncel yön→status→T01; geniş roadmap koşullu yatırım yoludur.

## Ürün değerlendirmesi ve kaynak alımı için ek okuma

[Portföy vaka çalışması](../portfolio/product-evaluation-case-study.md), owner rolünü ve AI destekli katkıyı gerçek kanıt sınırıyla gösterir. [Kod/teknoloji raporu](../discovery/code-reuse-assessment.md) tüm manifest alanlarının yapısal taraması ile R01–24 seçili davranış okumalarını ayırır. 9.657 dosya indeksi semantic audit veya test sonucu değildir. Governance ve contract graph örtüşmesi önceki hedefli benchmark'ı genişletir; EvidenceValidator bulgusunu bütün upstream verification yüzeyine genelleme. Upstream reuse A/B/C seçimi ve runtime kod alımı henüz yok; ilk kendi çekirdeğimiz için Python3.12/SQLite Q15-A ile seçildi, frontend/lisans açık. T03d öneri ve T01 sırası korunur.

## Ekosistem araştırması devir notu

[T03e](../discovery/ecosystem-research.md) 10 ek repo için immutable ref/root lisans ve beş seçili source okumasını toplar; [JSON](../discovery/ecosystem-candidates.json) gerçekten okunan yolları listeler. ER-R1 masa başı çıktısı mevcut; ER-R2–4 TODO, ER-T1–5 not_run. D/S kanıtını V runtime sonucu sayma. Graphiti temporal invalidation, LangGraph wait/resume ve LiteLLM reservation özgünlük karşı kanıtıdır; semantik uyum/closure/unknown-cost/premium gate'ler henüz tam deneyle doğrulanmadı.

Öncelikli derin inceleme Graphiti/LangGraph/LiteLLM; ekip authorization OpenFGA/Cedar koşullu, Temporal dağıtık ihtiyaçta. Bunlar teknoloji/ücretli hizmet/kod alımı seçimi değil. Native/config/extension/own seçenekleri, Q13 ve T01 sırası korunur. Repo sayısını artırmayı ilerleme ölçütü sayma; açık contract sorusu için 1–2 aday yeterliyse dur.

## Ölçüm sorusu ve somut teknik boşluklar

“Nasıl ölçeriz, yöntem net mi?” sorusunda [teknik protokolü](../quality/evaluation-protocol.md) oku. Metrik/eşik ve oracle yaklaşımı mevcut; çalışan scorer/harness/adapter/telemetry ve gerçek karşılaştırma yok. [CHAIN-01](../../examples/decision-impact-evaluation-case.json) yedi checkpoint/dört negatif varyant illustrative taslaktır, T01 corpus/holdout veya V pass değil. T01f/T03f/T24q TODO. Domain authority/target/state code oracle ile; serbest açıklama human rubric, optional judge yalnız ek izin/bütçeyle.

Graphiti graph-building eval ve Langfuse Python SDK source/test hedefli okundu; iki repo değerlendirme örüntüsü için faydalı, bizim domain doğruluğumuzun hazır oracle'ı değil. Missing score/evaluator error critical gate'i incomplete yapar. Yeni framework, paid telemetry veya kod alımı yok; T01/Q03/Q13 korunur.

## Teknik boşluklar ve inceleme hafızası

[2026-10-11 TG-01–24](../quality/technical-gap-analysis.md) inceleme ref'i/yöntemi, iki somut doc conflict, önerilen ayrıntılar, implementation/capability/owner/measurement ayrımı ve sonraki soruları tutar. “Boşluk var mı?” sorusunda her şeyi yeniden yok sayma; ilgili TG→[IC-01–08](../architecture/implementation-contracts.md)→canonical task→closure evidence zincirini aç. Yeni component/release/accepted ADR yok. IC testleri not_run; son task ID düzeltmesinde dil T24p korunup ölçüm T24q oldu. Source/generated/accepted/observed/verified ve doc pass/runtime pass ayrımını açıklayamayan model uygulamadan önce ilgili bölümü yeniden okumalı.


## İlk pilot yolu — Q02-R1 kabul kaydı

2026-10-11: kullanıcı maliyet odağıyla **A açık aktarım + tek read-only hedef** yolunu ilk pilot için seçti; **B Codex coding oturumu + tek repo** sonrasında görülmek isteniyor. C Claude Code-first seçilmedi, alternatif korunur. İlk yol sorusunu tekrar sorma; [kaynak, alternatifler ve gerekçe](decision-brief.md) kayıtlıdır. B'de MCP hedefli bağlam/öneri araçları ile ayrıca host/build capability deneyi isteyen otomatik capture ayrıdır. Somut kaynak/hedef/host ve sonraki gerçek veri/provider/bütçe açık; ücret veya gerçek veri okuma izni çıkarma. T01 IN_PROGRESS: [ilk corpus/baseline hazırlığı](../quality/baseline.md) mevcut, insan review'u pending; diğer 29 ana görev TODO, pilot not_started. Q03-R1 A 2026-10-11'de kabul edildi: ilk deney ek ücretli model API'si olmadan sentetik/elle etiketli fixture + deterministik kontrollerle ilerler. Bu soruyu tekrar sorma; otomatik anlam çıkarımını uygulamak ve gerçek extractor/holdout ile test etmek zorunlu sonraki adımdır; T09/T24q kapsamında `not_run`. Native/fresh-session model kalitesi de fixture sonucuyla doğrulanmaz. Q03-R1 B yalnız erken başlama alternatifidir; özelliği reddetme seçeneği değildir. Gelecek paid provider/veri/bütçe kararı kapanmadı. Görsel tur sonrası toplam 35 Mermaid/15 belge; güncel inventory/render kaydı ürün runtime kanıtı değildir.

## İlk somut hedef — Q02-R2 A

2026-10-11: kullanıcı private Decivora reposunda tek dokümanı ilk read-back hedefi seçti. Asistanın exact path tercihi `examples/corpus/README.md`; [READBACK-01](../quality/first-target-readback.md) önceki yayım ref'inde manuel içerik/SHA-256/blob eşleşmesi kaydeder. Q02-R2'yi tekrar sorma. Yukarıdaki `pilot not_started` end-to-end ürün deneyi içindir; artık tek manuel target gözlemi vardır. Otomatik source/answer/approval eşleme, adapter/harness/extractor/native/UI testleri çalışmadı. T01 IN_PROGRESS; T02/T03b kapanmadı. Gerçek sohbet/host erişimi ve sonraki provider/veri/bütçe ayrıntıları açık; target seçimi geniş hesap veya ücret yetkisi vermez.


## Audit sonrası çalışan P0 kanıtı — 2026-10-11

[Audit düzeltme kaydı](../quality/audit-remediation.md) güncel sonuçları gösterir. T01/T02/T03 IN_PROGRESS; ürün MVP’si ve production stack seçilmedi. Spike-0 fixture capture/regresyon kodu, typed karar–etki–kanıt zinciri ve bağımsız lexical scorer çalıştırıldı. Üstteki geçmiş “scorer/prototype yok” cümleleri bu ekten önceki duruma aittir. İnsan etiket incelemesi, zorunlu gerçek semantik çıkarım, iki gerçek coding-host capability testi, devam paketi/simple/native kıyası hâlâ kapanış işleri. Deney kodunu ürün auth/permission/DoD garantisi sayma; exact komutlar AGENTS ve spike README’lerindedir.


**Güncel P0 kod devamı:** [Implementation readiness](implementation-readiness.md) ve [semantik bağlantı](../../spikes/semantic-chain/README.md) source-only prepare/output import/validation/selection bridge/checkpoint testlerini gösterir. İnsan incelemesi bu hazırlığı bekletmez. Ayrı model provider dispatch, production auth, gerçek target ve native kıyas not_run; T01/T02/T03 ana kapıları açık.

## Kapanış sınırı

[CL01–08/Q16](../quality/task-closure-audit.md) parent/integration gate çelişkilerini kaydeder; first-use güvenlik kontrolünü kaldırma veya future işleri bugünkü parent kapanışına yükleme. Q16-A kabul edildi; [manifest ve validator](task-closure.md) uygulanır. T05 otomatik Done yapılmaz; T05/T06/T07/T08/T11 [yerel sentetik/manual core kabulüyle](../quality/integrated-core.md) tamamlandı; T09/T10 In Progress, actual adapter/login/model/UI/release açık.

## Current local delivery — 14 October 2026

[API-independent implementation and follow-up gates](api-independent-development.md): bounded stdioMCP/create-only human review, optional explicit-root file SHA verification, recorded graph/audit timeline, routing/null usage and session-only health. Historical implementation limits above refer to their original deliveries; current limits and M01–M14 checks are in the linked report. No native capture, full brief/delta, sandbox test/deploy verifier, exact host token savings or global language quality is claimed.

## Task Master targeted review — 14 October 2026

[Review](../discovery/task-master-review.md) and snapshot metadata record17read files/pinned commit. Recommendations only: existing next-action explanationT20e, bounded tool profilesT18/T21, original restricted CLI extractor feasibilityT09/T03f, optional splitT13d/T20d afterQ08, atomic exportT23. Paid API is not the only conceivable selected local pilot transport; CLI subscription integration and service eligibility are unverified, no call/config grant. MIT+Commons Clause prevents assuming unrestricted code/prompt reuse; none copied. Legacy findings do not generalize to modern paths. No main/subtask status change or runtime redesign from this research.

## Local response timings —14October2026

[Measured report](../quality/local-performance.md): live tracker API5.203ms median, empty product1.236ms;100synthetic returnedTasks43.494ms and4452SQLite queries/state;150stored truncates100. Real reload browser product133.47ms/tracker34.34ms median. No user mutation/model call/runtime optimization. Small fixture/tail/Chrome-vsIAB/100record coverage limits stated; future dense-source/file/concurrency/model tests open, existingT23d/T24l ownership. Do not infer production capacity or call rejected hash-navigation2.57ms a reload result.

## Mixed-load early measurement —14October2026

[Source/graph/history/concurrency report](../quality/mixed-load.md) and JSON: three temporary fixtures, no model/user mutation. Dense100tasks10decisions32sources394edges1409events2327audits: single438.581msmedian/four-readers1097.918ms; full measured run all200, nofalseDone, sources retained, oversized/overflow rejected. Prior overlapHTTP503remains unresolved/notfixed; later diagnostic run noexception.100record preview truncates; ASCII payload volume, nosemantic/Unicode/capture/cost proof. T20/T23d profiling and T15/T23d503reproducer now; T24l longload/release and T09/T21 actualmodel timing later. No runtime/config/status change or source authorization. Do not postpone all testing until finalrelease.

## Current concurrent storage and manual impact UI —14October2026

[Working delivery and limitations](../quality/concurrency-impact-delivery.md): startupWAL, read-snapshot-only audit grouping,318runtime/48tracker/7browser, identical mixed-fixture improvement and controlled503mechanism regression. Questions/decisions now offers human-selected durable decision-impact hypothesis; no task cancellation/decision mutation, missing rationale review. Full model/host/source-aware approval/application and release checks remain open.

## 18 October2026 review remediation

Read [current fixed findings and remaining gates](../quality/review-remediation-2026-10-18.md) before paid activation: source-bound dispatch grants/reservation/settlement are implemented, but verified tokenizer/context/money limits and trusted overrun reconciliation are still activation work. Do not reactivate from an old authorized=True transport. Prerequisite effective Done now propagates through current file/blocker state. All44diagrams rerendered; two sources changed.

## 19 October2026 — actual OpenAI pilot001 completed

Read [actual pilot and findings](../quality/openai-pilot-001.md) and its JSON before any further model call. Private key is configured, never read or echo it into chat. Owner-approved synthetic-only20HTTP allowance is fully consumed:10count+10generation,0retry. Source/schema10/10passed; canonical seed records unchanged; not native capture or MVP acceptance.13275tokens, cache-aware model-token estimate$0.024165, not invoice. Luna omitted the unverified Done claim; Sol proposed it for review. Decision source also matched an open question; association needs human review.

Cache-write pricing gap was found and fixed after preserving original receipts/ledger. New `openai-standard-cache-aware-2026-10-19` reserves worst-case input tariff and freezes missing/overlapping categories or unpriced tier. Original manifest is historical and must not be silently renewed; read-only report script reproduces the correction without new API calls. LOCAL/TEST UI still has no default extractor. Continue native adapter/UI activation and claim handling locally; a new paid batch needs a new exact grant. No new parent tasks or relaxed MVP criteria.

## 19 October2026 — explicit shared USD3 development approval

Owner explicitly approved `$3 bütçe ve bu sınırlarla devam et`. Read [root budget and results](../quality/openai-development-budget.md) before paid work: synthetic-only Luna/Sol, standard tier, input10000/output2000percall, generation100/HTTP200/USD3**including pilot001**. This supersedes the earlier financial wait within the same scope; do not ask generic spend approval again for each bounded synthetic batch. Real transcripts/native source sharing and scope/limit expansion remain separate.

`run_openai_development.py` owns fixed private root policy/ledger; new payload lists register as batches against the same limits. Prior corrected cost24165microusd/10generations/20HTTP carried once. Current snapshot20generations/40HTTP/49592microusd, remaining2950408microusd/80generations/160HTTP. Root expires technically after24hours; never renew by creating a zero-spend root. No scheduled or automatic background run authorized.

Completion prompt now explicitly captures unverified reported Done, preserves qualifiers, and rejects future/negated claims. Four new TR/ENcases×2models and original source/context×2models passed source/schema and expected narrow behavior; no canonical apply. Same original Luna case now emits the claim. AI-authored sample, not human-gold or broad accuracy proof. Continue native adapter/UI product connection instead of spending the allowance on repeated successful examples.

## 19 October2026 — selected Codex exec capture implementation

[Capture implementation and limits](../quality/codex-exec-capture-runtime.md): `packages/capture/codex/exec_stream.py` and explicit-file CLI bridge selected completed assistant events to existing ConversationService/dialogue review. Durable cursor/source transaction, retry/restart/prefix checks and credential redaction are implemented. No native host process, real transcript, model dispatch or default UI activation was performed. T17 In Progress, core_verified=false;7Done/15InProgress/8ToDo. Existing T16 release dependency remains; independent coding was possible. Continue the user-message/desktop-supported surface and explicit activation path, not a claim that CLI output observes all desktop sessions. Current synthetic USD3 budget and20generation/40HTTP/$0.049592 usage unchanged.

## 19 October — App Server capture implementation

Read the [new user-message and polling section](../quality/codex-exec-capture-runtime.md#19-october--app-server-user-message-capture-and-bounded-polling). Selected-thread read-only stdio transport, both text roles, bounded recent-turn polling and same-capture nearby context are coded. Real installed offline schema probe succeeded at0.162.0-alpha.17.2; synthetic child wire tests are not actual user-thread readback. No paid calls or transcript sharing. Do not restart normal UI or activate capture automatically. Next gate needs a concrete selected source and local-read consent, with model egress separate. T17 stays In Progress, core_verified=false; no new parent tasks.

## 19 October — first actual selected-thread readback and consumed source consent

Read [real capture001](../quality/codex-real-capture-001.md). Owner granted only a one-time local TEST import from this exact chat, at most10turns;2were selected. First full-turn response exceeded1MiB with0imports, disconnected. Corrected metadata+one-item paging completed the same one-time transfer:6public user/assistant sources,34localRPCs including initialization,2incomplete item turns,older history omitted,provider0,canonical0. This is partial native host proof, not complete capture or semantic extraction.

Real consent is **consumed**; both bindings are disconnected. Do not invoke another real host read, enable polling or share these sources with a model from this consent. Source approval is not part of the existing synthetic USD3 API grant. Private TEST guards/DB/backups must not be published or reset. Existing persisted TEST sources may be checked locally within scope. Normal DB hash unchanged. Current read client retains1MiB per response and32one-item pages; CLI has --turn-limit. Durable item cursors/checkpoint and gap UI are explicitly still T17 work; new polling can repeat head pages. T17 core_verified remainsfalse;7Done/15InProgress/8ToDo. No new parent tasks.

19 Ekim ana akış kodu: [source→outbox→izinli queue worker→review ve ilerleme kartı](../quality/conversation-processing-runtime.md) bağlandı. Native CLI collect success/failure Operations trace'i kalıcı. Otomatik grant/background activation yok;32source/indexed kapasite, kaynak onboarding ve gerçek model/native kabulü açık. Yeni parent veya erken Done yaratılmadı.

19 Ekim source kapasite dilimi: [1000source ve25lik sayfalama](../quality/source-capacity-pagination.md) kodlandı. Eski32source/capture fingerprint açık kaydını bugünkü engel sayma: source kapasitesi1000, incremental native yakın fingerprint32+kalıcı origin lookup. Kalan model/kaynak aktivasyonu ve sürekli otomatik zincir açık.

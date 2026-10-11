# Domain modeli ve durum makineleri

**Önerilen sözleşme.** Bütün proje kapsamlı tablolar/işlemler `(workspace_id, project_id)` ile sınırlandırılır. Workspace tenant sınırıdır; ilk pilot tek kişisel workspace içerir. Ad, klasör adı veya repository URL'si kimliğin yerine geçmez. Cross-project ilişki ancak ayrı yetkilendirilmiş paylaşım tasarımıyla gelir.

## Kayıtlar

`Project`: değişmeyen ID, ad, lifecycle (research/active/waiting/maintenance/archived), policy revision.

`ProjectBinding`: provider, account scope, workspace/repo/session/conversation referansı, project_id, bound_by, valid_from/to. Aynı repo çok projeyi içeriyorsa açık seçim gerekir. Repo olmayan projede conversation binding yeterlidir.

Binding değişince yeni epoch yalnız yeni kaynak olaylarına uygulanır. Önceki kaynak/record proje geçmişi sessizce taşınmaz. Yanlış bağlanmış geçmiş veri için ayrı yetkili transfer/correction önerisi, provenance ve etki review gerekir. Quarantine'dan ilk bağlama da kaydedilir; eski session adını yeniden kullanmak eski veriye yetki vermez.

`KnowledgeRecord`: ID, type, title, description, version, source_refs, rationale, tags, created_by, timestamps. Tipler: Idea, Finding, Risk, Requirement, Task, Prompt, DocumentInstruction, Decision, PendingDecision, Artifact. Execution ve Evidence ayrı nesnelerdir. Aday birleşmesi kimlik ve provenance kaybettirmez.

`Evaluation`: input source spans, retrieved record revisions, extractor/prompt/model versions, recommendation, rationale, counter_evidence, uncertainty, cost reference. Model confidence ölçülmemişse olasılık gibi sunulmaz.

`ImpactRun`: project, trigger/source revisions, knowledge snapshot revision, engine version, visited/remainder frontier, reason paths, coverage, candidate operations ve status. Aynı input snapshot tekrarında önceki sonuç referanslanabilir; yeni engine sürümü eski değerlendirmeyi silmez. Evidence sonucu ve impact sonucu ayrı nesnedir.

`ChangeSet`: operations, local temp IDs, ilişkiler, base revisions, source IDs, evaluation, idempotency key, digest, proposed/approved/applied/rejected/deferred/stale/failed durumu. Operasyonlar create/update/link/supersede/mark_obsolete/progress/verify/invalidate. Modelin arbitrary SQL üretmesi yasak.

Karar/edge/justification değişimlerinde artan `Project.knowledge_revision`, impact proposal'a bağlanır; apply öncesi kontrol yeni eklenen gerekçeyi de yakalar. Detay [ADR-0008](adr/0008-approval-snapshot-authority.md). Kayıtların yalnız bugünkü aktif sürümü değil, kullanıldıkları revision ilişkileri korunur.

## Ayrı durum eksenleri

| Eksen | Değerler | Kural |
|---|---|---|
| Extraction processing | pending / processing / processed / failed / ignored_with_reason | UI'da görülmek processed kanıtı değildir |
| Review | unreviewed / evaluated / decision_pending / accepted / rejected / deferred | Evaluated, kullanıcı onayı değildir |
| Knowledge validity | proposed / active / superseded / obsolete / disputed / archived | Active, her koşulda bilimsel doğru demek değildir |
| Execution | todo / in_progress / blocked / implemented / cancelled | Implemented bir uygulama iddiasını ifade edebilir |
| Verification | unknown / pending / passed / failed / stale / not_applicable | `completed` görünümü gerekli AC'lerin passed olmasını gerektirir |

`Rejected`: öneri plana alınmadı. `Cancelled`: yetkili kişi işi durdurdu. `Obsolete`: var olma gerekçesi kalmadı. `Superseded`: belirli bir yeni sürüm/yaklaşım yerini aldı. Bunlar “done” altında birleştirilmez.

Gelecekte verified bir çıktının kullanımdan kalkması, historical completion'ı iptal etmez. Current applicability ayrıca değişir. Yeni kanıt geçmiş doğrulamayı çürütürse verification.invalidate ve yeniden çalışma olayı eklenir.

## İlişki semantiği

| İlişki | Yön / anlam |
|---|---|
| depends_on / blocks | Task→prerequisite; ilerleme sırası, varoluş gerekçesi değildir |
| part_of | Child Task→Parent Task; Q08 önerisi: hiyerarşi, execution sırası veya gerekçe değildir |
| required_by | Task→Decision/Requirement; iş neden var? |
| implements | Task/Artifact→Requirement |
| discovered_from | Finding/Idea→SourceRecord/Execution |
| refines | Yeni aday→önceki kayıt; otomatik supersession değildir |
| supersedes | Yeni onaylı sürüm→eski sürüm |
| conflicts_with | İki kayıt arasında çelişki iddiası; evaluation bağlı |
| verified_by | Task/Requirement revision→Evidence |
| generated_from / executed_as / produces | Prompt→Requirement, Prompt→Execution, Execution→Artifact |
| related_to | Keşif bağlantısı; impact için tek başına zorunluluk yaratmaz |

Her edge için revision, kaynak, onay durumu ve gerekçe tutulur. Yürütme bağımlılıklarında cycle reddedilir veya bloke inceleme durumuna alınır; bilgi grafiğinin tümü DAG olmak zorunda değildir. Supersedes zincirinde cycle yasaktır.

## Gerekçe ifadeleri

Bir task'ın zorunluluk koşulu `any` / `all` ifadesiyle belirtilir. Yapraklar onaylı Decision/Requirement revision referanslarıdır. Eksik/çelişkili yaprak `unknown` olur.

- `any(false,true)=true`: alternatif gerekçe bulunduğundan koru.
- `all(false,true)=false`: birleşik koşul bozulmuştur; obsolete/update **adayı** üret, otomatik iptal etme.
- `any(false,unknown)=unknown`: review gerekir.
- `all(true,unknown)=unknown`: review gerekir.
- Boş gerekçe listesi `unknown`; “gerekmiyor” sonucu değildir.

İlişki grafiğinin eksiksiz olduğunu varsaymayız. “Gerekçe kalmadı” yalnız kaydedilmiş kapsama göre öneridir. Periodic audit ilişkisiz task'ları gösterir; insan onayı kapanış hatasına karşı son kapıdır.

## Kimlik, erişim ve veri yaşam döngüsü uzantısı

[İlişki ve bütünlük şemaları](data-relationships.md) Membership, ConnectionAuthorization, grantor join, run/task join, kriter/kanıt join ve assessment revision'larını ER ile gösterir. Source/Evaluation ve task/evidence bağlantıları çoktan çoğa olabilir; atlasın sade işlem okları fiziksel FK kardinalitesi yerine kullanılmaz. Task, KnowledgeRecord türü olarak kalır; ikinci task deposu eklenmez.

Workspace, Membership, Principal, AgentRun, DelegationGrant, ResourceACL ve ServiceConnection [kimlik modelinde](identity-access.md) tanımlanır. Project policy/knowledge revision yanında authz revision'a bağlıdır. ChangeSet/Approval kapsamı workspace, kaynak ACL revision'ları ve authz revision taşır; server güncel durumu commit'te kontrol eder. Kaynağın `personal` görünürlüğü proje binding'i yapılınca kendiliğinden `shared` olmaz.

Kaynak/blob referansında retention_policy_version, expires_at, pin_reason/pin_until, availability ve deletion/tombstone durumu bulunur. Canonical kayıtlar ve türev context aynı ömre sahip değildir; [yaşam döngüsü tablosu](storage-memory-capacity.md) authoritative tasarım önerisidir. Credential gövdeleri hiçbir domain entity'de tutulmaz.

## İlişki yaşam döngüsü ve graph görünümü

Edge kaydı proposal/onay durumundan bağımsız `asserted / ended / invalidated` yaşam döngüsü ve revision taşır. `valid_from_sequence`, `valid_to_sequence`, değişim gerekçesi, actor/approval ve önceki revision bağlantısı önerilen alanlardır. Ended önceki ilişkinin sona erdiğini, invalidated geçmiş iddianın yanlış bulunduğunu söyler; fiziksel DELETE değildir. Değişiklik knowledge_revision'ı artırır; eski impact/onay stale olur.

Current traversal yalnız güncel geçerli ilişkileri kullanır; historical traversal seçilmiş sequence'i gösterir ve bugünkü ACL'yi uygular. Gerekçenin kaldırılması otomatik obsolete kararı değildir; kalan AND/OR/unknown ve coverage yeniden değerlendirilir. Task cancelled olduğunda ilişkiler kendiliğinden ended olmaz; açık gereksinim/bağımlı işler review veya blocked kalabilir. Görsel karşılığı [graph deneyimindedir](../product/graph-experience.md).

## Task context ve DoD assessment

Q08 için önerilen hierarchy: ilk tasarımda child'ın aynı workspace/project içinde en fazla bir güncel parent'ı vardır; self-parent/cycle reddedilir. Birden fazla işin kullandığı ortak task kopyalanmaz; diğer bağlantılar gerçek anlamına göre depends_on/related_to olabilir. `part_of` tek başına completion zorunluluğu, gerekçe veya yetki/grant mirası oluşturmaz. Parent completion planı hangi child'ın gerekli olduğunu ve ana AC→child AC eşlemesini version'lı tutar. Çoklu parent modeli gerekirse ayrı mimari review ister. Split yalnız onaylı atomik ChangeSet'tir; parent kimliği, geçmiş ve evidence korunur. [Bölme önizlemesi ve kabul kuralları](../product/task-context-and-acceptance.md) uygulanır; öneri Q08 kararından önce runtime'a alınmaz.

`ContextSnapshot` kaynak/karar/evidence revision'larından türetilen milestone görünümüdür; canonical truth değildir. `DoDTemplate` proje/iş türü bazlı version'lanır, task assessment hangi maddelerin neden uygulanabilir olduğunu kaydeder. Completion gerekli AC'lerle birlikte uygulanabilir gerekli DoD kanıtı ve review/impact kapılarını kontrol eder. Parent task sırf child'lar bitti diye complete olmaz. [Context ve acceptance sözleşmesi](../product/task-context-and-acceptance.md) alanları, üretim tetiklerini, export hatasını ve eski kanıt davranışını tanımlar.

## Artifact ve hedef uygulama gözlemi

**ADR-0011 teknik önerisi; fiziksel şema yok.** [GAP sözleşmesindeki](../product/intent-to-reality-gap.md) insan seçimi, generated artifact, hedef uygulama ve acceptance eksenleri tek task status enum'una eklenmez. Mevcut review/validity/execution/verification eksenleri korunur.

| Mantıksal kayıt | Alan / anlam |
|---|---|
| Artifact revision | KnowledgeRecord'ın Artifact tipi; hash/availability/source refs, generated claim veya güvenilir artifact gözlemi dayanağı |
| ApplicationTarget | Scope içinde değişmeyen kimlik ve versioned locator: local makine+kapsamlı path veya provider/account/repo/ref/environment; credential gövdesi yok |
| ApplicationExpectation | Task/proposal, seçilmiş karar revision'ları, target revision, beklenen etki/validation rule, authz/policy ve source refs; proposed/accepted kapsamı açık |
| ExpectedArtifactLink | Expectation↔Artifact revision N:M; gerekli dosya/path/ref ve expected content/hash; üç dosyayı tek “var” bitine indirgeme |
| ApplicationObservation | Observer/reporter principal, authority class, target snapshot/ref, artifact gözlemi veya human report, occurred/observed_at ve availability/coverage; yüklendi claim'i otomatik read-back değil |
| ApplicationAssessment | Expectation revision, kullanılan observation/evidence refs, assessment yöntemi/sürümü, input decision/target/artifact snapshot, result/reason ve freshness |
| AssessmentObservationLink | Bir assessment birçok observation, bir observation birçok assessment'ta kaynak olabilir; provenance kaybolmaz |

Application result: not_observed / reported / pending / observed / partial / mismatch / failed / unknown. Freshness current / stale / unknown ayrı boyuttur; bunlar acceptance VerificationAssessment passed değildir. not_observed “olmuyor” demek değildir; missing ancak exact hedefin yetkili, yeterli kapsamlı gözlemiyle raporlanabilir. Permission denied unknown/unavailable'dır. observed yalnız belirtilen expected effect ve snapshot'ta; test/deploy/whole task completion kapsamaz.

Trusted insan selection'ı policy/kimlik/kapsamla Decision'a bağlanır; bu ek tablo ikinci karar deposu değildir. Expectation hâlâ proposal'a ait olabilir; capture onu accepted backlog yapmaz. Hedef, artifact veya ilgili karar/AC değişimi current assessment'ı stale/review yapar; tarihsel observation silinmez. Evidence önceki snapshot'a bağlı kalır. Başka hedefe uygulama aynı expectation başarı sonucu değildir.

Kayıtlar aynı workspace/project composite sınırına tabidir. Yeni query'de güncel kaynak/target ACL gerekir; assessment türevi ACL genişletemez. [ER-03 ve DB bütünlüğü](data-relationships.md#er-03--artifact-hedef-uygulama-ve-kabul-ayrımı), [tetikler](execution-and-integrations.md#10-hedef-uygulama-gözlemi-tetikleri) ve [ADR-0011](adr/0011-target-application-evidence.md) ayrıntıları tamamlar.

## Dil ve locale metadata önerisi

[Konuşma dili sözleşmesi](../product/language-and-localization.md) source/span language tags (mixed/undetermined dahil), detector provenance; proje output policy revision; record content_language ve varsa version-bound translated_from alanlarını önerir. UI locale üretim dilinden ayrıdır. Bu mantıksal tasarım fiziksel DDL/migration değildir. Orijinal source span/offset/ACL, decision/AC/evidence kimliği korunur; çeviri ayrı türevdir. Dil değişimi event/karar/kanıtı rewrite etmez; cache/brief ilgili language policy/source revision ile bağlanır. Q12-A kabul edildi: sabit proje output_language, insan kabulüyle yeni policy revision/effective_from; session dili kendiliğinden geçiş veya geçmiş çevirisi üretmez. Fiziksel DDL ve detector seçimi hâlâ öneri.

## Soru ve gecikmiş cevap ilişkisi

[Kalıcı soru/cevap sözleşmesi](../product/pending-questions-and-late-answers.md) QuestionRequest ↔ QuestionPresentation/option snapshot ↔ AnswerRecord ↔ Decision/Approval bağını önerir. Soru ID'si değişmez; aynı soru yeniden gösterildiğinde presentation ref eklenir, seçenek değişiminde revision korunur. Cevap source kimliği/responder/selected source/answer association state ve source-created/received/resolved zamanları ayrı tutulur. PendingDecision karar kuyruğudur; her bilgi sorusu bu tip olmaz. Belirsiz veya soru öncesi gelen cevap association bekler, canonical karar üretmez. Exact hedef bile güncel authority/revision/expiry kontrolünü atlamaz. Bu mantıksal metadata/state açılımıdır; fiziksel tablo/migration veya yeni state enum kabulü değildir.

## Uygulama ayrıntıları için tamamlayıcı inceleme

[IC-01–08](implementation-contracts.md) kaynak koordinatı/strict schema, canonical digest, bütçe sayısal temsili, target snapshot, boş AC ve projection freshness ayrıntılarını önerir. Bunlar yeni accepted domain enum veya fiziksel DDL değildir. [TG incelemesi](../quality/technical-gap-analysis.md) mevcut kuralla gerçek eksik/test borcunu ayırır; type/state/authority kararları bu belge ve ilgili ADR ile birlikte uygulanır.

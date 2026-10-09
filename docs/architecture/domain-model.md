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

Workspace, Membership, Principal, AgentRun, DelegationGrant, ResourceACL ve ServiceConnection [kimlik modelinde](identity-access.md) tanımlanır. Project policy/knowledge revision yanında authz revision'a bağlıdır. ChangeSet/Approval kapsamı workspace, kaynak ACL revision'ları ve authz revision taşır; server güncel durumu commit'te kontrol eder. Kaynağın `personal` görünürlüğü proje binding'i yapılınca kendiliğinden `shared` olmaz.

Kaynak/blob referansında retention_policy_version, expires_at, pin_reason/pin_until, availability ve deletion/tombstone durumu bulunur. Canonical kayıtlar ve türev context aynı ömre sahip değildir; [yaşam döngüsü tablosu](storage-memory-capacity.md) authoritative tasarım önerisidir. Credential gövdeleri hiçbir domain entity'de tutulmaz.

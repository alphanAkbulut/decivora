# Proje ilerleme görünümü

> Otomatik üretilir. Ana kaynak backlog’dur; bu dosyayı elle düzenleme.

**Açık çalışma fazı: P0, P1a, P1b, P2, P3**

[Canlı yerel ekranı açma ve güncelleme rehberi](progress-guide.md). GitHub bu Markdown görünümünü gösterir; canlı ekran yerel dosyaları izler.

`IN_PROGRESS` açık çalışma kaydıdır; bir agent’ın şu anda çalıştığını göstermez. Plan ön koşulları otomatik teknik blocker değildir. Test sayısı ürün tamamlanma yüzdesi değildir.

| Ana görev durumu | Sayı |
|---|---|
| DONE | 8 |
| IN_PROGRESS | 20 |
| TODO | 2 |

## İş türü ve bekleyen insan kapıları

Ana görev ve alt teslim sayıları toplanmaz. Tür, tamamlanan alt teslimin birincil çıktısıdır; efor veya ürün yüzdesi değildir.

| Alt teslim durumu | Sayı |
|---|---|
| DONE | 56 |
| IN_PROGRESS | 42 |
| PROPOSED | 5 |
| TODO | 26 |

| Tamamlanan alt teslimin türü | Sayı |
|---|---|
| Test / deney / değerlendirme hazırlığı | 13 |
| Kod geliştirme / araç / sözleşme | 42 |
| Analiz / teknik karar | 1 |

Kod kategorisi prototipleri, araçları ve executable sözleşmeleri de kapsar; hepsi son ürün özelliği değildir. Bağımsız doküman sayısı ve test fonksiyonu sayısı görev sayısına eklenmez.

| İnsan katkısı/izni gereken kapı | Gereken | Ne zaman |
|---|---|---|
| Gerçek model deneyi | API erişimi ve$3sentetik kapsam mevcut; gerçek sohbet/veri paylaşımı, exact kaynak/context ve uygulama aktivasyonu ayrı izin ister | İlk ücretli dispatch öncesi |
| Gerçek coding/MCP kaynağı | Yeni gerçek okuma/izleme veya başka istemci için seçilmiş host/oturum ve dar izin; önceki Codex tek TEST izni tüketildi | Gerçek host bağlantısı öncesi |
| Gerçek dosya hedefi | Seçilen kök, dosya, beklenen içerik ve kriter kapsamı | Kullanıcı dosyasını okumadan önce |
| İnsan doğruluk incelemesi | Hazırlanmış exact etiket/holdout incelemesi; önceki H1–H4 yeniden sorulmaz | Kalite/ürün kabulü öncesi |

Bunlar dört gruplanmış insan kapısıdır; dört açık onay penceresi değildir. Bağımsız kod işleri beklemez. Daha sonra netleştirilecek ürün tercihleri: Q09 Bildirim kanalı ve sıklığı; blocker önceliği zaten kabul edildi.


## Tamamlanmış küçük teslimler

Alt teslim kapanışı ana görev veya MVP kapanışı değildir. Kabul kapsamı ve kanıt backlog’da kayıtlıdır.

| Alt görev | Ana görev | Durum | Teslim |
|---|---|---|---|
| T01g | T01 | DONE | DONE / P0: H1/H2/H3 ilk davranış incelemesi |
| T01h | T01 | DONE | DONE / P0: iki yeni development family ve ayrı kaynak/rubric paket |
| T01i | T01 | DONE | DONE / P0: H4 quoted/planned partial insan review |
| T03g | T03 | DONE | DONE / P0: bounded quote adapter ve ayrı candidate rubric |
| T03h | T03 | DONE | DONE / P0: gönderimsiz API paket ve saved response import |
| T03i | T03 | DONE | DONE / P0: tek selected local file observer |
| T03j | T03 | DONE | DONE / P0: tek komutluk integrated zincir |
| T03k | T03 | DONE | DONE / P0: mevcut üyelik source-only paket ve batch import/score |
| T03l | T03 | DONE | DONE / P0: onaylı MEMBERSHIP-001 tek gönderim ve değişmez ölçüm kaydı |
| T03m | T03 | DONE | DONE / P0: separate typed v2 field/type contract ve offline paket |
| T03n | T03 | DONE | DONE / P0: onaylı MEMBERSHIP-002 gerçek typed çıktı ve ölçüm |
| T03o | T03 | DONE | DONE / P0: gerçek kayıtlı candidate → controlled karar/impact/hedef/AC/restore replay |
| T03p | T03 | DONE | DONE / P0: aynı source'ta lexical ve saved-model dar ölçüm |
| T03q | T03 | DONE | DONE / P0: yeni8-message MEMBERSHIP-003 gerçek typed output ve ölçüm |
| T03r | T03 | DONE | DONE / P0: birden fazla source-bound cevap için read-only öneri koleksiyonu |
| T03s | T03 | DONE | DONE / P0: deterministic kaynak bağlı resume ve eşit bilgiyle dosya serialization kıyası |
| T03t | T03 | DONE | DONE / P0: kayıpsız inline source/record table ve çözülmüş readable model view |
| T03u | T03 | DONE | DONE / P0: bounded fresh-session receiver request ve bağımsız saved-output evaluator hazırlığı |
| T03v | T03 | DONE | DONE / P0: tek configured Luna/Low native run ve first-output kanıtı |
| T03w | T03 | DONE | DONE / P0: offline strict shape schema ve kaynak bağlı receiver guard |
| T03x | T03 | DONE | DONE / P0: Q14-A bağımsız proje review ve açıklama cevabı descriptor |
| T03y | T03 | DONE | DONE / P0: yeni source-only receiver isteği ve ortak makine schema/scorer |
| T03z | T03 | DONE | DONE / P0: wire-2 için Q14-A bağımsız proje incelemesi |
| T03aa | T03 | DONE | DONE / P0: selected typed record'dan readback ve safe action taslağı |
| T03ab | T03 | DONE | DONE / P0: SQLite inceleme snapshot deposu |
| T03ac | T03 | DONE | DONE / P0: persisted clarification'a explicit source-bound reply proposal |
| T03c | T03 | DONE | DONE: kabul edilmiş koşullu çekirdek build seçimi; Python3.12/SQLite, ADR-0012 |
| T04a | T04 | DONE | DONE / P1a: Versioned envelope/command/query şemaları ve error taxonomy |
| T04c | T04 | DONE | DONE / P1a: Source, command, trigger ve async result şemaları; ER composite key/N:M ilişki kontratı |
| T04d | T04 | DONE | DONE / P1a: Sonlu request/body/burst/concurrency config, erken admission, güvenli hata/transport eşlemesi |
| T05h | T05 | DONE | DONE / P1a: kalıcı local principal/grant revision ve transaction guard |
| T05g | T05 | DONE | DONE / P1a: kalıcı project/binding snapshot store |
| T05f | T05 | DONE | DONE / P1a: scope kontrollü in-memory proje/binding çekirdeği ve çalışan CLI demo |
| T05a | T05 | DONE | DONE / P1a: Immutable project binding epoch ve quarantine |
| T05c | T05 | DONE | DONE / P1a: kaynak/hedef binding ve versioned izin makbuzu schema/rule fixture |
| T05b | T05 | DONE | DONE / P1a: Kişisel workspace, human/agent ID, compound tenant FK, session binding şeması |
| T06a | T06 | DONE | DONE / P1a: Source+job atomic receipt ve ingest cursor |
| T06b | T06 | DONE | DONE / P1a: Worker lease/fencing ve job transitions |
| T06c | T06 | DONE | DONE / P1a: Processing intervals, idle flush, bounded retry/quarantine |
| T06e | T06 | DONE | DONE / P1a: Kalıcı due jobs, kaçan wake-up taraması, max-wait/fairness ve replay suppression |
| T06f | T06 | DONE | DONE / P1a: Bounded queue/storage admission, scope adaleti, restart sayaç ve receipt/backpressure |
| T06g | T06 | DONE | DONE / P1a: Session frontier, max-wait flush, bounded catch-up ve gap/lag ölçümü |
| T06d | T06 | DONE | DONE / P1a: Receipt/dedup ömrünü raw payload'dan ayır; bounded spool/backpressure |
| T07a | T07 | DONE | DONE / P1a: Replay mode ve projector version gate |
| T07c | T07 | DONE | DONE / P1a: ** Minimal çekirdek DB+payload backup/restore |
| T07b | T07 | DONE | DONE / P1a: Domain command + güvenlik audit atomikliği; güvenli structured logger |
| T08a | T08 | DONE | DONE / P1a: Command identity, key/digest ve policy capability |
| T08c | T08 | DONE | DONE / P1a: Principal/proje/workspace toplamı, parent-run bütçesi, DB transaction sınırı ve limiter arıza davranışı |
| T08b | T08 | DONE | DONE / P1a: `authorize(action,resource,context)` sınırı, dar grant, authz revision/commit kontrolü |
| T11c | T11 | DONE | DONE / P1a: başlangıç-bitiş gate'i, blocker assessment, revision bağlı traversal, benzersiz downstream |
| T11b | T11 | DONE | DONE / P1a: Edge revision, ended/invalidated ve sequence geçerliliği |
| T12a | T12 | DONE | DONE — ImpactRun snapshot, visited/frontier ve knowledge revision |
| T13a | T13 | DONE | DONE — Onay token'ı snapshot/policy/digest ile bağla |
| T13b | T13 | DONE | DONE — Task cancel ve edge ending için farklı impact preview/compensating olay |
| T13c | T13 | DONE | DONE — İş öncesi versioned AC/DoD hazırlama/onay; applicability gerekçesi |
| T18a | T18 | DONE | DONE / P1b: Scope/snapshot-bound query cursor ve context limits |

## Açık fazda neler değişti?

Ana görev kapanışı ile hazırlık/kod/ölçüm ilerlemesi ayrıdır. Aşağıdaki kayıtlar backlog'dan gelir; canlı agent etkinliği değildir.

### T01 · Golden corpus ve karşılaştırma protokolü

19 Ekim2026 — TR/EN development örnekleri, H1–H4 kısmi insan review ve scorer/corpus mevcut; [durum teyidi](../quality/task-status-audit.md).

**Aktif teknik risk:** Development örneği insan gold/holdout değildir; genel doğruluk hâlâ açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Exact etiket/adjudication ve family holdout kabulünü T01e/f kapsamında tamamla.

### T02 · İki coding yüzeyinde capability spike

19 Ekim2026 — [Codex readback](../quality/codex-real-capture-001.md)6gerçek TEST source; offline şema ve bounded App Server client mevcut.

**Aktif teknik risk:** Tek kısmi readback iki gerçek host veya sürekli capture garantisi değildir.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Claude ve MCP/hook yüzey raporunu dar izinle tamamla; Codex yeni checkpoint sürümünü sonraki izinli okumada doğrula.

### T03 · Native/extend/build ve teknoloji kararı

19 Ekim2026 — RECEIVER-001/002 invalid_contract geçmişi korunur; sonra20generation/40HTTP sentetik API deneyi ve$3root guard çalıştı. [Güncel sonuç](../quality/openai-development-budget.md).

**Aktif teknik risk:** Dar schema/source başarıları genel semantik kalite, native üstünlük veya ROI kanıtı değildir.

**Denemeler / sonuç:** S02 erişim/span failure, MEMBERSHIP-001 incomplete, MEMBERSHIP-002/003 dar typed/source draft eşleşmeleri. RECEIVER-001 invalid_contract/unscored; RECEIVER-002 actual tek run invalid_contract/unscored; missing next_actions ve ambiguous soru bağlama ret. R22 multi-answer fixture düzeltmesi T03r DONE; eski run hataları korunur, güncel teknik engel diye tekrar sunulmaz.

**Etkilenen iş:** T03 semantik receiver kalite ve gerçek capture/native-ROI kıyası açık; T03c/Q15-A conditional yatırım/runtime kararı kabul edildi. T03y istek/scorer ve T03x bağımsız review fixture kodu DONE; insan gold/gerçek hedef/production IAM/UI kabulü değildir.

Sıradaki adım: Aynı bağımsız beklentilerde tam ürün zincirini ve adil native kıyası değerlendir; yeni genel keşif turuyla uzatma.

### T09 · Extraction ve bounded retrieval

19 Ekim2026 — [Exact-source aktivasyon + kalıcı bounded processing worker](../architecture/model-activation-runtime.md) API/thread/queue yoluna bağlandı. Pass/source caps restartta korunur; stop, unfinished claim ve unknown usage yeni dispatch keser. Kaynak/context ve root bütçe guard korunur.

**Aktif teknik risk:** Varsayılan model kapalı; genel retrieval/chunking/çıkarım kalitesi ve otomatik aktivasyon kabulü açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Kaynak/model onboarding ekranını hazır backend komutlarına bağla; yeni mesaj paylaşım kapsamını mevcut tek-deneme izinlerinden ayrı al. Bağımsız semantic ölçüm kendi kapısında açık.

### T10 · Temel reconciliation

19 Ekim2026 — Exact duplicate/source attach, kaynaklı relation ve Decision replacement review kodlandı. [Sözleşme](../quality/dialogue-status-runtime.md).

**Aktif teknik risk:** Semantik conflict/refinement/equivalence ve genel Idea Evaluation tamamlanmadı.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T10a/b kapsamındaki açıklanabilir karşı kanıt ve belirsizlik çözümünü tamamla; similarity ile otomatik merge yapma.

### T13 · Review işlemi ve güvenilir onay

19 Ekim2026 — [Kaynaklı seçenekli soru backend bağlantısı](../quality/dialogue-status-runtime.md#19-ekim--konuşmadaki-seçenekli-sorudan-kalıcı-soru-kaydına): model taslağı→ayrı insan review→atomik kalıcı soru→geç cevap. Duplicate/ret/erteleme ve provenance korunur; Kaynaklı taslak inceleme kartı da bağlandı; genel soru türleri ve ekip routing açık.

**Aktif teknik risk:** Konuşmadan QuestionRequest üretimi, genel clarification ve split planı atomik kabulü açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T13d split, T13e genel/serbest metin soru ve çatışma çözümü; T19 genel çatışma çözümü ve kaynak/model onboarding. Seçenekli soru backend ve inceleme kartı aşağıda teslim edildi.

### T14 · Evidence ve false-done düzeltmesi

19 Ekim2026 — Human/file-SHA AC/DoD, false-Done/current basis ve önkoşul invalidation kodlandı. [Kanıt sınırı](../quality/workflow-ui-runtime.md).

**Aktif teknik risk:** Gerçek artifact/target/runner yetkisi ve parent-child completion tam kapsamı açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T14a–d kapsamında exact hedef/recipe ve parent completion bağlantısını doğrula; transcript komutu çalıştırma.

### T15 · Teknik kanıt kapısı

19 Ekim2026 — Core crash/restore/replay, source checkpoint ve queue backup/restore fixture mevcut. [Son worker dilimi](../quality/conversation-processing-runtime.md).

**Aktif teknik risk:** Modül/regresyon başarıları bütün native/model/target zincirinin kabulü değildir.

**Denemeler / sonuç:** Aynı394ilişki/1409event/2327audit yükünde WAL + snapshot audit reuse:133ms/260msmedyan; kaynak korunumu/falseDone0,100record preview truncated. [318runtime/7browser ve teslim](../quality/concurrency-impact-delivery.md).

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Aynı kaynak/revision üzerinden tam zinciri ve recovery proof raporunu birleştir.

### T16 · Claude Code adapter

Son ilerleme kaydı yok.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Ayrıntılı backlog'u kontrol et.

### T18 · Minimal MCP ve cross-agent read

19 Ekim2026 — Beş-tool bounded stdio MCP, signed query cursor, private-derived visibility guard ve iki-agent fixture var. [Kod/kapsam](api-independent-development.md).

**Aktif teknik risk:** Brief/delta/continuation, paylaşım proposalı ve gerçek host onboarding/delivery kabulü açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T18b–i kalan kabulü: source ACL korunarak deterministic devam bağlamı ve gerçek client kurulumu.

### T19 · Proje seçimi ve Review Inbox UI

19 Ekim2026 — Mevcut proposal/status/answer/relation review yanında [finite worker yönetim backend API](../architecture/model-activation-runtime.md) create/start/run/stop ve state metadata tamamlandı. Kurulum/aktivasyon UI bağlantısı açık.

**Aktif teknik risk:** Proje/kaynak kurulum izin wizardı ve risk plan kartı yok; bütün öneri türleri tamamlanmadı.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T19b risk kartı ve source/model onboarding; mevcut source/proposal review uçlarını yeniden yazma.

### T20 · Board, Graph ve Timeline

19 Ekim2026 — Board/List/Graph/Timeline, blockers/lifecycle, AND/OR yazarı ve Operations/queue görünümü kodlu. [Güncel UI](../quality/workflow-ui-runtime.md).

**Aktif teknik risk:** Parent-child/split, milestone context export ve tam pending-age/bağlantı envanteri açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T20c/d/g/h/i kapsamını mevcut UIya bağla; parent kriterlerini child sayısıyla tamamlandı sayma.

### T21 · Routing etiketleri ve usage kaydı

19 Ekim2026 — Shared root token/money reservation, count+actual/unknown/overrun ve routing etiketleri mevcut. [API bütçe kaydı](../quality/openai-development-budget.md).

**Aktif teknik risk:** Dönem/config ve source/model onboarding UI açık; source activation/finite-loop backend kodlu, tahmin nihai fatura değildir.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T21b/c kalan dönem/parametre görünümü ve trusted reconciliation; root bütçeyi yeni batch ile sıfırlama.

### T22 · Chat import ve prompt lineage

19 Ekim2026 — Manual/native source provenance, redaction, turn/item/role ve source+outbox checkpoint kodlu. [Kaynak akışı](../quality/conversation-processing-runtime.md).

**Aktif teknik risk:** Genel1C arşiv/fairness/retention ve iki-host lineage bağları açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T22b kapasite/manifest ve izinli geçmiş işleme; eski gerçek kaynaklar için izin kendiliğinden yenilenmez.

### T23 · Backup, export ve yerel güvenlik

19 Ekim2026 — Private SQLite backup/offline restore, loopback security, credential redaction ve safe Operations sidecar mevcut. [Son TEST readback](../quality/conversation-processing-runtime.md).

**Aktif teknik risk:** Aktif migration/recovery, purge/retention/encryption ve ölçülmüş RPO/RTO açık.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: T23a–e kalan recovery/privacy ve kapasite kabulünü tamamla; accepted kaynakları limitte silme.

### T24 · MVP kabul ve kullanıcı pilotu

Son ilerleme kaydı yok.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Ayrıntılı backlog'u kontrol et.

### T26 · Gelişmiş reconciliation ve orphan audit

Son ilerleme kaydı yok.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Ayrıntılı backlog'u kontrol et.

### T27 · GitHub evidence ve görünür panel deneyi

Son ilerleme kaydı yok.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Ayrıntılı backlog'u kontrol et.

### T28 · Maliyet raporu ve kontrollü entegrasyonlar

Son ilerleme kaydı yok.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Ayrıntılı backlog'u kontrol et.

### T29 · Public release hazırlığı

Son ilerleme kaydı yok.

**Aktif teknik risk:** Bu görev için ayrı risk kaydı yok; risksiz olduğu anlamına gelmez.

**Denemeler / sonuç:** Ayrıntılı kaynak kayıtlarını kontrol et.

**Etkilenen iş:** Backlog kabul ve bağımlılıkları geçerli.

Sıradaki adım: Ayrıntılı backlog'u kontrol et.


## Mevcut teslim parçaları

Bunlar P0 hazırlığı ve kontrollü deney kodudur; tamamlanmış production engine/MVP değildir.

- **T09/T10/T22 konuşma→öneri→pano** — Manual conversation receipts, Responses request/parser, source quote binding, reconciliation/review; main UX konuşma alanı; [237runtime + browser fixture](../quality/conversation-review-runtime.md); ilk rapor bu alanları doğrulamadı; sonradan transport/grant/MCP/partial Codex ve queue kodlandı, gerçek genel kalite/aktivasyon kabulü açık
- **T13e soru→karar dilimi** — Kalıcı manual soru/cevap→gerekçeli proposal→ayrı human approve/apply→Decision; stale ve tek resolution guards; [208runtime + gerçek browser](../quality/question-decision-runtime.md); [cancel/defer/revise/orphan](../quality/question-lifecycle-runtime.md)221runtime testli; fullT13e agent-routing/source kabulü açık
- **Yerel program/T13c** — Kalıcı Task board, AC/DoD sürümü/onayı, work-start; executable launcher/package; [185runtime + real browser flow](../quality/local-preview.md); T19/T20 IP, semantic/Done/native/MCP açık
- **T13b lifecycle** — Complete rationale + downstream guard, explicit cancel/reopen event, preserved edges/history; [20yeni/168runtime test/lifecycle-demo](../quality/task-lifecycle.md); lifecycle UI sonradan bağlandı; gerçek completion ve otomatik plan kabulü açık
- **T13a review kernel** — Persisted selection/dependent groups/separate approval, source+policy recheck/atomic apply; [18yeni/148runtime test/review-demo](../quality/review-kernel.md); T13b/c ve temel UI sonradan bağlandı; tam T13e/otomatik ürün kabulü açık
- **T12/T12a impact preview** — Bounded deterministic proposal, visited/frontier, source/knowledge/authz snapshot + persisted stale guard; [21yeni/130runtime test ve impact-demo](../quality/impact-preview.md); manual input, apply/verification T13/T14
- **Beş ana yerel çekirdek teslimi** — T05/T06/T07/T08/T11: normalized tenant binding, durable receipts/jobs, event/replay/restore, atomic approval/audit/budget, typed graph; [44 yeni/95 runtime test ve core-demo](../quality/integrated-core.md); gerçek source/login/model/UI yok
- **T09/T10 çalışan hazırlık** — Structured source-span validator/lexical context/exact duplicate relationship review; [Kod ve açık kalite sınırı](../quality/integrated-core.md); semantic inference/FTS/gold ölçümü açık, ana görevler In Progress
- **T05c connection izin schema/rule** — Bounded immutable receipt, scope/current-context/action/expiry review gate; activation daima false; [9 test ve CLI demo](../quality/connection-authorization.md); gerçek provider/approval/audit/receipt persistence yok
- **T05h yerel izin iptali** — Persisted authority revision + transaction scoped guard; actor claim yetki değil; [8 yeni test](../quality/local-authority.md); login/token/ACL/production IAM yok
- **T05g kalıcı proje/binding** — SQLite snapshot/command store; memory state restart sonrası korunur, T05 açık; [11 yeni test ve restart demo](../quality/project-store.md); backup/power-loss/gerçek IAM/ingress yok
- **T05f proje/binding çekirdeği** — Scope kontrollü memory-only servis ve CLI sentetik demo; T05 ana görev In Progress; [11 yeni runtime testi](../quality/project-binding-core.md); kalıcılık/gerçek IAM/ingress yok
- **Capture ölçüm düzeneği** — Spike-0 kaynak/session kimliği, kapanışsız delta ve kısa cevap gözlemi; production adapter değil; 40 fixture/regresyon testi; gerçek host capability açık
- **Kaynak-only model input’u** — 6 session istek hazırlayıcı; 58 mesaj; source metadata auth ve oracle dışarıda; exact hash/version/proje kimliği; Protocol input/leak/cache/namespace testleri
- **Semantik çıktı sözleşmesi** — JSON envelope, 14 aday türü, Unicode source span, tip/byte/record limiti, duplicate ve abstention; Hatalı/stale/yetki iddialı çıktı reddediliyor
- **Geç cevap bağlantısı** — Model AnswerRecord → pending proposal; ayrı trusted receipt ile karar; task impact apply ayrı; Actor/receipt/project/source/question/base/retry negatifleri
- **Ölçüm ve başarısızlık** — Import edilmiş response → bağımsız span scorer; eksik output/abstention incomplete; yedi state checkpoint için exact scorer; Eksik/yanlış expectation başarı sayılmıyor
- **Zincir proof’u** — Gerçek sentetik source dosyası → scripted contract response → selection → AND/OR/unknown → old target → partial/full AC → restore; [Sonuç](../quality/semantic-readiness-results.json); gerçek inference/target değil
- **Otomasyon ve devir** — Test/CI komutları, mevcut status/backlog ve bu tek hazırlık kaydı; Docs/corpus/anchor + runtime regresyonları
- **Seçili gerçek hedef okuması** — Tek GitHub dokümanı iki immutable ref'te; aynı içerikte eski ref stale, seçili ref observed_match; Repo/path/ref/hash denetimi; task_verified false; ürün adapter veya SQLite uygulama kanıtı değil
- **Geliştirme takip ekranı** — Mevcut parçalar, açık işler, fazlar, AC/alt görevler ve engine görev bağlantıları; açık fazın son ilerleme/kalan adımı kartlarda görünür; 14 tracker testi; tarayıcıda T03 aktif risk/deneme bölümü ve önceki detay/P0 filtre kontrolleri; ürün UI veya canlı agent telemetry değil
- **S02 gönderim ve güvenlik hazırlığı** — İki ayrı onaylı tek gönderim: S02-001 cloudflare_challenge/çıktı yok; S02-002 gerçek output, 10/11 span hatalı, strict ret; her denemede retry 0; [Güncel rapor/ham çıktı](../quality/s02-second-attempt-result.md); kaynak hashleri sabit. JSON parse geçti, scorer/zincir çalışmadı; hard-cap/production limiter doğrulanmadı
- **Kaynak adapter ve candidate rubric** — Bounded exact quote + source/revision contract; explicit legacy türev; candidate/domain beklentileri ayrı; CLI offline; [48 suite testi ve üç scripted case](../quality/source-anchor-adapter.md); gerçek inference/semantic accuracy değil
- **Quote-only API deney paketi** — Strict schema taslağı, source-only payload, pending bütçe/onay manifesti ve saved response importer; [56 semantik test / 8 yeni](../quality/quote-api-package.md); gerçek provider dispatch/schema/kalite not_run
- **Seçilmiş yerel hedef observer** — Tek dosya real filesystem read, bounded no-follow/hash/change kontrolü; source metninden komut çalıştırılmaz; [65 semantik test ve ayrı gerçek yerel gözlem](../quality/local-observer.md); remote upload/task acceptance veya production IAM değil
- **Tek komutluk integrated zincir / T03j DONE** — Quote-only adapter ve bounded observer mevcut decision/impact/AC/restore akışına bağlandı; [66 semantik test ve yedi checkpoint](../quality/integrated-chain.md); T03g/h/i de scoped DONE, ana T03 ve gerçek model kalite kapısı açık
- **Mevcut üyelik smoke paket/harness / T03k DONE** — 3330-byte source-only prompt, dört mesaj/iki project, ayrı candidate expectations, batch import/score; [72 semantik test / 6 yeni](../quality/membership-smoke-plan.md); hazırlık tarihsel; MEMBERSHIP-001 run tamamlandı, genel kalite/hard cap/usage açık
- **Gerçek üyelik run kaydı ve typed v2 / T03l,T03m DONE** — Bir gerçek output: source doğrulaması passed, candidate gate incomplete; alias/tür sorunu ayrı açık v2 contract ile sınırlandı; [78 semantik test ve run kanıtı](../quality/membership-001-result.md); typed v2 hazırlığı tarihsel; sonraki MEMBERSHIP-002 run kaydedildi, primary skor/gold/production gate korunur
- **Gerçek typed v2 ölçümü / T03n DONE** — Tek yeni model output; dört draft aday eşleşti, source/type pass; isolated guards mutation 0; [80 semantik test ve ilk çıktı](../quality/membership-002-result.md); yeni send izni tüketildi, insan gold/production kalite değil
- **Kayıtlı gerçek aday zincir replay / T03o DONE** — V2 raw/source→ayrı receipt→AND/OR impact→eski/güncel içerik→partial/full AC→restore; [13 kontrollü checkpoint,86 semantik/6 yeni test](../quality/membership-chain-replay.md); yeni model/egress0; üretim IAM/criterion revision/lineage değil
- **Yeni development aileleri / T01h DONE** — Sekiz synthetic mesaj/iki source-only request, ayrı draft rubric/manifest/5321-byte prompt; [Hazır paket](../../examples/adversarial-smoke/README.md); source/hash/schema testleri; hazırlık tarihsel; H4 partial review ve MEMBERSHIP-003 gerçekleşti, sealed holdout/gold değil
- **Same-source kıyas / T03p DONE** — Aynı dört mesajda lexical ve saved-model shared span/kind skorları; capability farkı açık; [91 semantik test/5 yeni harness testi](../quality/same-source-comparison.md); yeni model0, native/domain/ekonomi kıyası değil
- **Yeni aile gerçek ölçümü ve H4 review / T03q,T01i DONE** — Onaylı tek çıktı6 draft aday/2 scope-no-candidate; source/type ve partial behavior review hash bağlı; [93 test/guard sonuçları](../quality/membership-003-result.md); run sırasında whole-batch çok-aday blok gözlendi; sonraki T03r fixture düzeltmesi DONE, production reconciliation açık, izin tüketildi
- **Çoklu cevap koleksiyonu / T03r DONE** — Her cevabın message/question revision'ı ayrı; tam response validation, source kimliği ve read-only proposal; [102 test/9 yeni ve stored raw replay](../quality/proposal-collection.md); stale/conflict/ambiguity korunur, production çok-soru/IAM değil
- **Resume/export ve eşit bilgi dosya kıyası / T03s DONE** — Bounded deterministic core, source/state/access freshness, inspectable altı synthetic dosya; [110 test/8 yeni ve byte ölçümü](../quality/resume-file-comparison.md); iki temsil checklist geçti, receiver/native/token/user burden not_run
- **Kayıpsız resume table + okunabilir view / T03t DONE** — Tek inline source, source-span/record references; code-decoded literal quotes ve current-snapshot export guard; [121 test/11 yeni, exact frozen core ve byte ölçümü](../quality/resume-compaction.md); üç checklist geçti, receiving-model/token/production IAM değil
- **Receiver bounded request/evaluator / T03u DONE** — İki readable view, ayrı readback/next-action oracle,7950-byte frozen prompt; source/schema/critical guards; [134 test/13 yeni ve hazırlık planı](../quality/receiver-smoke-plan.md); hazırlık snapshot send0; sonraki RECEIVER-001 failed run ayrı kayıtta, scripted positive model kanıtı değil
- **İlk native receiver run kaydı / T03v DONE** — Tek configured Luna/Low turn ve actual firstoutput; source/contract gate ve model-token/context kaydı; [136 test/2 yeni guard](../quality/receiver-001-result.md); syntaxvalid/schemainvalid, usageunknown, actualquality gate açık
- **Receiver shape/source guard / T03w DONE** — Request bağlı makine schema; current question ve ambiguous record ayrı, strict integer/abstention/record-action/evidence kontrolü; [152 test/16 yeni](../quality/receiver-contract.md); ilk gerçek çıktı failed kalır, provider conformance/model kalite yeniden sınanmadı
- **Q14-A bağımsız proje review / T03x DONE** — Global envelope/current binding preflight, per-project shape/source sonucu, atomic group ve stable clarification reply association; [172 test/20 yeni](../quality/project-review.md); fixture context, durable Inbox/gerçek IAM/UI/host resume ve model kalitesi açık
- **Yeni machine-schema receiver isteği / T03y DONE** — 8source/6record,8089byte yeni kimlikli prompt ve ayrı oracle/scorer; hermetik3file source-only hazırlık; [192 test/20 yeni](../quality/receiver-next-plan.md); hazırlık snapshot send0 korunur; sonraki [RECEIVER-002 tek run](../quality/receiver-002-result.md) invalid_contract, provider-enforced schema not_run
- **Wire-2 bağımsız proje incelemesi / T03z DONE** — Exact yeni request/source binding, global preflight ve yerel teknik hata ayrımı; atomic grup bölünmez; [206 semantik test/14 yeni](../quality/project-review-next.md); raw/format onarımı yok, strict whole-trial scorer ayrı, gerçek model/IAM/UI not_run
- **Tipli record'dan deterministic review / T03aa DONE** — Source-bound6record, bilinen state ve candidate status'tan yeni kökenli6action; oracle/model raw input değil; [222 test/13 yeni ve authored kıyas](../quality/typed-review.md); model çağrısı0, geçmiş actual failures aynı, extraction/IAM/ekonomi gate açık
- **Kalıcı review snapshot / T03ab DONE** — Typed review store için SQLite append/transaction ve restart sonrası pending clarification geri okuma; [234 test/12 yeni](../quality/review-store.md); dedup/current scope/access/tamper/rollback/two-writer, gerçek insan reply çözümü/UI/IAM değil
- **Kalıcı explicit cevap önerisi / T03ac DONE** — Stored snapshot'a CID/source/question revision ile late reply; ayrı append-only SQLite extension; [248 test/14 yeni](../quality/reply-store.md); restart/retry/conflict/current access/atomic no-resume. Actor fixture; actual approval/resolved/UI/IAM değil
- **T04 uygulama runtime iskeleti DONE** — Apps/hub CLI, ayrı domain contract, sürüm/lisans manifest/schema ve sentetik bounded input validation; [12runtime test ve clean-start](../quality/runtime-scaffold.md); model/runner/server/auth/storage/UI disabled, ilk ana görev kabulü. P0 replay/model başarısı değil
- **Yerel token/bağlam preflight kodu** — Manifestteki bütün çağrıların input/generation/context/run/parent bütçe hesaplaması; unknown/risk/hard cap ayrımı; [17 fixture testi ve S02 no-dispatch sonucu](../quality/token-preflight.md); gerçek para/atomik rezervasyon/provider limiter değil

## Açık karar ve doğrulama kapıları

| Konu | Etkisi | Sonraki adım |
|---|---|---|
| Receiver model kalitesi ve genelleme | RECEIVER-002 düzeltmeli tek run da invalid_contract; missing required field ve ambiguous-question binding kaynak retleri gözlendi. Dar MEMBERSHIP-002/003 source/type draft eşleşmesi genel kalite değildir | [İlk failure](../quality/receiver-001-result.md), [ikinci gerçek failure](../quality/receiver-002-result.md); ham çıktılar değişmedi. R22 multi-answer fixture toplama T03r DONE; production reconciliation, gold/native/ROI açık |
| Gold etiket/adjudication | Kodun çalışmasını değil, kalite skorlarının insan doğruluğu ve release genellemesini sınırlar | T01g/H1-H3 ve T01i/H4 partial davranış review DONE; [review kuyruğu](../quality/human-review-queue.md), exact etiket/adjudication/holdout açık |
| Gerçek Codex/Claude capture | Otomatik capture/capability iddiası; MCP tool erişimi full capture değildir | Codex selected-thread6source readback doğrulandı; checkpoint/queue ve native trace kodlandı. Claude ve sürekli capture/onboarding/kapsam kabulü açık; native receiver sohbeti tek başına transcript adapter kanıtı değildir |
| Native/dosya/resume kıyas | Üstünlük ve yatırım yeniden değerlendirmesi; Q15-A core start değil | [Kıyas protokolü](../quality/pilot-comparison-plan.md): offline serialization/byte kıyası tamamlandı; gerçek alıcı/native/user-burden/ROI kıyası not_run |

## Fazlara göre tüm ana işler

| ID | Faz | Durum | İş | Plan ön koşulu | Alt dilim |
|---|---|---|---|---|---|
| T01 | P0 | IN_PROGRESS | Golden corpus ve karşılaştırma protokolü |  | 5 |
| T02 | P0 | IN_PROGRESS | İki coding yüzeyinde capability spike | T01 | 3 |
| T03 | P0 | IN_PROGRESS | Native/extend/build ve teknoloji kararı | T01, T02 | 27 |
| T04 | P1a | DONE | Runtime iskeleti ve sözleşme doğrulayıcıları | T03c | 4 |
| T05 | P1a | DONE | Proje kimliği ve binding | T04 | 8 |
| T06 | P1a | DONE | Source ingress ve checkpoint | T05 | 7 |
| T07 | P1a | DONE | Domain log ve projector | T06 | 3 |
| T08 | P1a | DONE | Atomic change set ve policy | T07 | 3 |
| T09 | P1a | IN_PROGRESS | Extraction ve bounded retrieval | T08 | 4 |
| T10 | P1a | IN_PROGRESS | Temel reconciliation | T09 | 2 |
| T11 | P1a | DONE | Tipli gerekçe graph | T10 | 2 |
| T12 | P1a | DONE | Impact preview ve apply planı | T11 | 1 |
| T13 | P1a | IN_PROGRESS | Review işlemi ve güvenilir onay | T12 | 5 |
| T14 | P1a | IN_PROGRESS | Evidence ve false-done düzeltmesi | T13 | 4 |
| T15 | P1a | IN_PROGRESS | Teknik kanıt kapısı | T14, T07c | 1 |
| T16 | P1b | IN_PROGRESS | Claude Code adapter | T15 | 1 |
| T17 | P1b | DONE | Codex adapter | T16 | 0 |
| T18 | P1b | IN_PROGRESS | Minimal MCP ve cross-agent read | T17 | 9 |
| T19 | P1b | IN_PROGRESS | Proje seçimi ve Review Inbox UI | T18 | 1 |
| T20 | P1b | IN_PROGRESS | Board, Graph ve Timeline | T19 | 9 |
| T21 | P1b | IN_PROGRESS | Routing etiketleri ve usage kaydı | T20 | 2 |
| T22 | P1b | IN_PROGRESS | Chat import ve prompt lineage | T21 | 1 |
| T23 | P1b | IN_PROGRESS | Backup, export ve yerel güvenlik | T22 | 5 |
| T24 | P1b | IN_PROGRESS | MVP kabul ve kullanıcı pilotu | T23 | 17 |
| T25 | P2 | TODO | Chat yüzeyleri ve cross-provider adapter araştırması | T24 | 1 |
| T26 | P2 | IN_PROGRESS | Gelişmiş reconciliation ve orphan audit | T25 | 2 |
| T27 | P2 | IN_PROGRESS | GitHub evidence ve görünür panel deneyi | T26 | 0 |
| T28 | P3 | IN_PROGRESS | Maliyet raporu ve kontrollü entegrasyonlar | T27 | 2 |
| T29 | P3 | IN_PROGRESS | Public release hazırlığı | T28 | 0 |
| T30 | P4 | TODO | Ekip/cloud/open-core keşfi | T29 | 0 |

## Kanıt kapsamı

Kayıt durumu: **stale**; rapor tarihi: 2026-10-11; kayıtlı test sayısı: 91. Kaynak raporun tarihsel model kaydı: not_run; insan gold: pending; native kıyas: not_run. Production runtime: False.

Güncel model denemesi T03 son ilerleme kaydındadır. Bu alan kaynak raporun tarihsel checkpoint’idir. Kod hash kontrolü yalnız raporun listelediği dosyaları kapsar; bütün repo veya güncel CI sonucu değildir. [Kaynak rapor](../quality/semantic-readiness-results.json).

Görev kabul kriterleri, doğrulama ve alt görevler [kanonik backlog](backlog.md) içinde; 10 production engine [engine sözleşmesinde](../architecture/engines.md) planlıdır.

Kaynak fingerprint: `00f9e5a143fa74b30ce94ea198b1cc014fe7cd057edc1d19faa260fbf8c09fc2`

# Mevcut durum

**19 Ekim — ilk gerçek Codex kaynak aktarımı:** kullanıcı onaylı tek yerel TEST okuması, seçilmiş2turdan6user/assistant mesajı kaydetti; TEST API readback doğrulandı. İlk full-response byte sınırı hatası korundu; metadata+one-item pagination düzeltildi. İki turda da okunmamış item var; kalıcı cursor/backfill açık, T17 kapanmadı.6kaynak Waiting for model; yeni Task0 ve ücretli çağrı0; kaynak izni kullanılıp bağlantı kapatıldı. [Bulgu, düzeltme ve kanıt](../quality/codex-real-capture-001.md). Ana7/15/8 korunur.

**19 Ekim — kullanıcı mesajı capture bağlantısı kodlandı:** App Server üzerinden seçilmiş tek thread'in bounded user/assistant metin okuması ve açık sınırlı polling komutu eklendi. Önceki mesajlardan bounded bağlam, actor/item/turn kimliği, tekrar/değişiklik/privacy ve revoke/commit kontrolleri var. Kurulu CLI offline şeması doğrulandı; gerçek sohbet okuma/normal UI etkinleştirme yapılmadı. [Kod, sürüm ve sınırlar](../quality/codex-exec-capture-runtime.md#19-october--app-server-user-message-capture-and-bounded-polling). T17 In Progress; ana7/15/8 aynı, yeni ücretli çağrı0.

**19 Ekim — T17 Codex capture kodu başladı:** seçilmiş `codex exec --json` akışındaki tamamlanmış assistant mesajları kalıcı, kaynak kimlikli conversation kaydına ve mevcut review zincirine bağlandı. Cursor/retry/restart, partial coverage, privacy ve atomik rollback var. Gerçek desktop sohbet yakalama/otomatik model dispatch yok; T17 tamamlanmadı. [Kod ve sınırlar](../quality/codex-exec-capture-runtime.md). Ana7Done/15InProgress/8ToDo; ücretli yeni çağrı0.

**19 Ekim — $3 geliştirme kapsamı kabul edildi ve kodlandı:** ilk pilot dahil100generation/200HTTP/$3ortak root; prior usage taşınır, yeni batch/restart sıfırlamaz.10yeni gerçek generation: Türkçe/İngilizce completion claim, future/negation ve özgün eski claim yeni talimatla denendi;10source/schema pass ve bu dar örneklerde beklenen öneriler alındı. Otomatik apply yok. Toplam20generation/40HTTP, tahmin$0.049592; kalan$2.950408. [Kod, onay ve sonuç](../quality/openai-development-budget.md). Yeni kaynak izni veya native/MVP kabulü değildir; mevcut scope içinde yeniden genel ücret onayı beklenmez.

**19 Ekim — ilk gerçek API pilotu tamamlandı:** kullanıcı private anahtarı kurdu; onaylı sentetik Luna/Sol batch'inde10generation+10count, retry0,10/10source/schema pass. Toplam13275token; cache-write dahil tahmin$0.024165, nihai fatura değil. Luna completion claim'i atladı; Sol bunu yalnız Pending Done önerisi yaptı; canonical apply yok. Cache-write fiyatlama eksikliği kodda düzeltildi; eski ledger korunarak ayrı düzeltme raporu eklendi. [Sonuç ve sınırlar](../quality/openai-pilot-001.md).20HTTP izin tüketildi; yeni çağrı yok. Normal/TEST UI model kapalı, native capture/MVP kabulü açık. Ana7/14/9 korunur.

[Güncel ürün resmi ve kalan kod işleri — 19 Ekim](current-state.md):12geliştirme ana işi,2entegrasyon/release kapısı,3P0 kabul/kalite işi açık;6gelecek-faz işi ayrı. Ana/alt görevler toplanmaz.

2026-10-14 — **P1a çekirdek geliştirme + açık P0 kanıt işleri**.

| Alan | Durum |
|---|---|
| Kaynak konuşma derlemesi, vizyon/MVP/karar haritası | Bu dokümantasyon paketinde hazırlanmış |
| Mimari, ADR, görev ve kabul planları | Production önerisi; P0 fixture zinciri test edildi |
| Benchmark | Birincil belge incelemesi; runtime karşılaştırma bekliyor |
| Ürün MVP / adapter / dashboard | Yerel sentetik/manual runtime: T04/T05/T06/T07/T08/T11/T12 DONE; local workflow/human verification dahil güncel runtime testi; local app+AC contract, diğer core demos. T09/T10 kalite ve ürün/adapter/UI işleri açık. P0 kodu ve tracker ayrı; gerçek host/ürün dashboard kabulü yok |
| Semantik model / tasarruf / kullanıcı talebi | [MEMBERSHIP-002](../quality/membership-002-result.md): tek v2 output, dört draft aday/source/type geçti; production doğruluk/tasarruf/talep ölçülmedi; lexical baseline ayrı |
| İlk gerçek hedef gözlemi | [READBACK-01](../quality/first-target-readback.md): tek GitHub rehberi exact içerik eşleşti; manuel kontrol, ürün adapter testi değil |
| T01 corpus hazırlığı | IN_PROGRESS; 6 sentetik oturum/58 mesaj/46 farklı bilgi kaydı; insan incelemesi pending |
| Lisans ve nihai marka | Karar bekliyor |

**Güncel işler: 7 Done / 15 In Progress / 8 To Do. T15/T18/T21 kod dilimleri başladı; native/model/target/release kabulü açık.** Q15-A koşullu build seçimi kabul edildi; T04 artık T03 parent kapanışını beklemiyor. [Hazırlık matrisi](implementation-readiness.md): source→typed model candidate→guard bağlantısı kaydedilmiş gerçek output ile sınandı. MEMBERSHIP-002 dört authored_draft beklentiyle eşleşti; ayrı fixture guard karar veya verification uygulamadı. 26 küçük P0 teslim + T03c koşullu yatırım kararı DONE; ilk ana runtime görevi T04 DONE. T01/T02/T03 kalite kapıları ve tüm ürün MVP kabulü açık. Kayıtlı gerçek v2 aday zincir replay13 kontrollü checkpoint geçti; same-source kıyas da çalıştı; yeni8-message MEMBERSHIP-003 ve H4 partial review tamamlandı; çok-aday P0 read-only collector tamamlandı; resume/eşit bilgi dosya kıyası ve kayıpsız küçültme/readable view tamamlandı; receiver tek Luna/Low native run kaydedildi fakat contract geçmedi; yerel schema/source guard ve Q14-A bağımsız proje review katmanı tamamlandı; yeni model ve native karşılaştırma açık. Q15-A/T03c ilk yatırım ve runtime seçimi kabul edildi; T04 tamamlandı. Diğer mimari/release kararları açık. Test/aday sayıları ürün yüzde tamamlanması değildir.

## İlerleme kaydetme düzeni

### 2026-10-14 — API-bağımsız geliştirme

- [Kod, bulgular ve M01–M14 takip kapıları](api-independent-development.md): stdioMCP/durable agent review, file observer/current proof, graph/timeline/routing/unknown usage/sanitized health ve teknik restore zinciri. Kaynaklar private/source-linked ise MCP varsayılanı deny. Gerçek host ve paid model aktive edilmedi.


### 2026-10-14 — Özel yedek indirme

- [T23a teslimi](../quality/private-backup-runtime.md): UI private backup, bounded authenticated download, temporary offline restore verification. T23 In Progress; ana7Done/11InProgress/12ToDo. Public/redacted export/purge/migration/active restore açık.


### 2026-10-14 — Onaylı workflow ve familiar UI

- [Teslim](../quality/workflow-ui-runtime.md):6stage + Closed filter, current lifecycle projection, dependency/question/manual start-finish assessment, human criterion evidence + guarded Done; Board/List/search/filter/end panel. Kullanıcı14Ekim2026 onayı DEC-22/ADR-0013. Ana7Done/10InProgress/13ToDo; T14 başladı, parent kapanmadı. Paid API0; automatic/target/native/semantic kabul açık.


### 2026-10-13 — Görünür Blocked / çözüm akışı

- Task'ın ilerleme sütunundan ayrı kırmızı Blocked işareti + üst Blockers listesi, gerekçe/next action, explicit human çözümü, revision ve append-only audit uygulandı. [Kanıt](../quality/task-blocker-results.json):4yeni/244runtime test, browser mark→reload→resolve ve5locale regresyonu geçti. Aktif blocker yeni start'ı durdurur; çözüm otomatik start/Done üretmez. [Sınırlar](../architecture/local-preview.md): otomatik graph/capture blocker UI bağlama açık; T20e/T24d mevcut kapsam, yeni ana görev yok.

### 2026-10-13 — EN-default beş UI dili

- [Yerel UI dilimi](../product/language-and-localization.md): İngilizce varsayılan/fallback; TR/ES/PT-BR/AR katalogları ve Arabic RTL. Yerel dil değişimi model/command çağırmaz, kaynak ve düzenlenen taslak/checkbox seçimini korur. Çok dilli model kalitesi/otomatik çıktı dili P2'de açık; ana görev kapanışı yok.
- [Doğrulama kaydı](../quality/localization-results.json):240runtime/46tracker test ve gerçek browser fixture; beş dil, persistence/storage fallback, RTL desktop/mobile, içerik korunumu ve mevcut manuel karar akışı geçti; gerçek API0. ES/PT/AR native inceleme bekliyor, kataloglar taslak.

### 2026-10-13 — Konuşma aktarımı birinci öncelik; UX düzenlemesi

- [Konuşma→öneri→pano](../quality/conversation-review-runtime.md): gerçek manuel kaynak ayrı tutulur, provider payload/parser, exact quote kodla span, candidate review/comparison/explicit accept.16yeni/237runtime test; browser kontrollü model3aday→Taskpanoya→reload. Gerçek semantic kalite/network dispatch yok; model/veri/bütçe etkinleştirmesi açık, API yarına ertelendi.
- Ana7Done/9InProgress/14ToDo; T22 gerçek kodla başladı, tamamlandı değil. Konuşma/öneri ana UI, sidebar ve scoped metrikler, elle kayıt yardımcı araç; desktop/mobile kontrolü. Kullanıcı yeni UX önceliği verdi; gelecekteki tam kapsam/14AC korunur.

### 2026-10-13 — Soru lifecycle ve kaybolmayan geç cevap

- [Soru lifecycle](../quality/question-lifecycle-runtime.md): cancel/defer/resume, gerekçeli yeni revision/superseded history, original cevap silinmeden explicit orphan reassociation, presentation retry;13yeni/221runtime test. Tarayıcıda ertele→devam→iptal→reload ve eski Decision korunumu geçti.
- T13/T13e ana kapanışı değil; ASK/LATE agent-routing/source/policy eşlemesi ayrıca açık. Ana7Done/8InProgress/15ToDo; yeni task/model/API/ücret yok.

### 2026-10-13 — T13e cevaptan ayrı onaylı canonical karar

- [Karar runtime](../quality/question-decision-runtime.md):11 yeni/208runtime test; actual UI prepare→approve→apply→reload; same-question/current-revision, authority/base, generic bypass ve iki bağlantı tek effect. Görevleri değiştirmez; otomatik capture/model/Done hâlâ açık.
- Ana7Done/8InProgress/15ToDo aynı; T13e soru lifecycle/orphan/source normalize kalanları mevcut kapsamda izlenir. Yeni task/model/API/ücret yok.

### 2026-10-13 — Altı kod teslim planı ve manuel pending soru dilimi

- [Altı paket](build-delivery-plan.md): mevcut kodu geliştiren uygulama sırası;15To Do=9MVP+6future, yeni görev yok.
- [Question runtime](../quality/pending-question-runtime.md): kalıcı soru/seçenek snapshot, exact ID/revision cevap, stale/unmatched/conflict/retry ve UI pending listesi.12yeni/197runtime test; T13e In Progress, canonical karar/apply bağı hâlâ açık. Ana7Done/8InProgress/15ToDo; packet1 tamamlanmadı, ücretli model/API0.

### 2026-10-13 — T13c + çift tıklamayla başlayan yerel yazılım

- [Local preview](../quality/local-preview.md): versioned AC/DoD/check/approval/history, manual Task board+prepared AC card, actual localhost session/CSRF/Origin/rate limit; launcher+standalone ZIP.185runtime test; gerçek browser create→approve→start→reload flow geçti. T13c Done; T19/T20 gerçek koduyla In Progress.
- Ana7DONE/8IN_PROGRESS/15TODO; T13e ve T14 Done/semantic/native/MCP/full UI acceptance açık. User priority runnable local product; manual UI slice ahead of full connector path, no scope/14AC removed. PaidAPI/model0, user data ZIP/GitHub'a dahil değil.

### 2026-10-13 — T13b Task iptali ve compensating geri dönüş

- [Task lifecycle](../quality/task-lifecycle.md): separate impact+human review token, reason/downstream/parent guards, cancel≠edge ending, metadata update state korunumu ve compensating event.20yeni/168runtime test; lifecycle-demo cancel→reopen/history/replay geçer. SQLschema1 aynı; yeni event/operation artifact ve3diagram render (1new/2changed),41source/20belge.
- Ana7DONE/6IN_PROGRESS/17TODO aynı; T13a/b Done, T13c/e ve T14 hâlâ açık. Ücretli API/model/gerçek kaynak yok; önceki rapor/hashler tarihsel olarak korunur.

### 2026-10-13 — T13a kalıcı review/onay çekirdeği

- [Review kernel](../quality/review-kernel.md): compare/select/reject/defer, dependent partial groups, ayrı human approval, policy/source/graph/authz snapshot, atomic apply/audit ve çift bağlantı tek effect.18yeni/148runtime test +review-demo; SQLschema1 aynı. Yeni JSONschema ve2Mermaid gerçek render/görsel kontrol;40kaynak/19belge.
- Ana7DONE/6IN_PROGRESS/17TODO; T13 başladı, T13a Done. T13b cancellation, T13c AC/DoD, T13e pending question ve14MVP AC açık; ana T13 kapanmadı. Ücretli API/model/gerçek kaynak yok; tarihsel kanıtlar korunur.

### 2026-10-13 — T12/T12a çalışan impact preview

- [Impact preview](../quality/impact-preview.md): typed trigger/version, bounded visited/frontier, reason/counter-evidence, AND/OR/unknown, keep/update/review/obsolete_candidate, geçmiş korunumu. SQLite immutable preview+digest, source/knowledge/authz snapshot, stale OR edge/gap/quarantine ve restart/restore bağlandı.21yeni/130runtime test ve impact-demo geçti; preview canonical mutation0/model0.
- Ana7DONE/5IN_PROGRESS/18TODO. T13 ayrı insan review/onay ve T14 verification sırada; T09/T10 semantic/gold ve14MVP AC açık. Yeni görev/API/gerçek kaynak/ücret yok. Tarihsel proof/hash raporları korunur.

### 2026-10-13 — Hızlandırılmış teslim sonrası kritik düzeltmeler

- [CR01–06](../quality/core-critical-review.md): archive/reopen, quarantine ACL, authority-bound worker, tek backup/read snapshot, strict replay ve restore/event eşitliği + hata cleanup düzeltildi. Önceki modülde ilk10regression gerçekten fail; güncel14yeni/109runtime +46tracker test geçti. Çalışan core-demo korunur.
- Yeni görev/ana kapanış yok:6DONE/5IN_PROGRESS/19TODO.14MVP AC ve T09 gerçek extraction kapısı açık. Ücretli API/model/gerçek kaynak çağrısı yok; production güvenlik/restore garantisi yok. Tarihsel integrated-core hash raporu yeniden yazılmadı.

### 2026-10-13 — Beş ana çekirdek teslimi birlikte

- [Integrated core](../quality/integrated-core.md): T05/T06/T07/T08/T11 scoped çekirdek Done;44 yeni/95 runtime test. Gerçek SQLite receipt/job/event/approval/audit, graph, backup/restore ve ayrı process abort; core-demo pass.
- Ana sayım6DONE/5IN_PROGRESS/19TODO; T09/T10 kodu In Progress, gerçek extraction/FTS/semantic/gold ölçümü açık. T04b native/network activation owner/first-use T16, disabled profile gerçek gate'i kapatmaz. Yeni görev/model/API/gerçek kaynak/ücret yok;14MVP AC korunur.


### 2026-10-13 — T05c izin makbuzu sözleşmesi

- [T05c](../quality/connection-authorization.md) mevcut schema/rule alt görevi DONE; typed immutable makbuz, exported schema, scope-digest/current-context/action intersection/expiry gate ve çalışan connection-demo.9 yeni/51 runtime test; actual activation/read/model0.
- Ana1DONE/4IN_PROGRESS/25TODO aynı. T05a/b tenant-FK ve güvenilir binding core kabulü açık; actual source/audit/login entegrasyonları kendi kapılarında kalır. Yeni task ID yok.


### 2026-10-13 — Q16-A kabulü ve uygulaması

- [Kapanış manifesti](task-closure.md):30 ana/129 mevcut cross-file alt kayıt;7 downstream entegrasyonun sahip/first-use gate'i ayrı, core/PROPOSED korunur.6 planning testi ve closure cycle/missing owner/evidence/AC drift kontrolleri uygulandı. Ana1DONE/4IN_PROGRESS/25TODO ve14AC aynı.
- Ortak çalışma rehberi ve proje AGENTS kısa kapanış/dedup/stale kontrol kuralıyla güncellendi. T04 startup kabulü korunur; T05a/b/c core kalanları kanıtla tamamlanacak, future team/login işleri T05'e yüklenmez. Yeni runtime/model/ücret yok.


### 2026-10-13 — Görev kapanış denetimi

- [CL01–08](../quality/task-closure-audit.md):30 ana/117 backlog alt satır; gerçek release eksikleri, future/integration ve stale karar/sayım ayrıldı. Parent-all-child gate yorumunda T05→T08→T06→T05 döngüsü, T04 Done/child belirsizliği var.
- Güncel stale Q03-R6/T03c/OPEN02/snapshot/handoff metinleri düzeltildi. Tarihsel run/hashler, ana1DONE/4IN_PROGRESS/25TODO ve14AC korunur. Q16 closure önerisi henüz uygulanmadı; yeni runtime/model yok.

### 2026-10-13 — T05 yerel izin iptali

- [T05h](../quality/local-authority.md): DB authority revision, issued scope/current grant guard, owner-only management ve restart/rollback.8 yeni/42 toplam runtime test; authority-demo gerçekten çalıştı.
- Ana sayım1 DONE/4 IN_PROGRESS/25TODO korunur. T05 bağlantı/session izin makbuzu ve ingress kapsamı açık; gerçek authentication, role UI veya production IAM yok.


### 2026-10-13 — T05 kalıcı kayıt dilimi

- [T05g project store](../quality/project-store.md): SQLite restart, command retry/dedup, rollback, stale writer ve scope query testleri geçti;11 yeni/34 toplam runtime test. Gerçek temp DB ile `project-store-demo` çalıştı.
- Ana sayım1 DONE/4 IN_PROGRESS/25 TODO; T05 grant/authz lifecycle ve ingress kabulü açık. Yeni model/API/gerçek kaynak yok.


### 2026-10-13 — T05 gerçek kod geliştirmesi başladı

- [T05f binding çekirdeği](../quality/project-binding-core.md): aynı adlı projelerde ayrı kimlik, scope kontrollü CRUD/archive, versioned session binding ve quarantine sonucu; çalışan `binding-demo` CLI.11 yeni test; runtime toplam23.
- T05 IN_PROGRESS; kalıcı store/restart/authz/ingress henüz bitmedi.1 DONE/4 IN_PROGRESS/25 TODO. Demo memory-only, fixture scope; login/insan onayı veya gerçek source receipt değil.


### 2026-10-13 — İlk ana MVP işi T04 Done

- [T04 kabulü](../quality/runtime-scaffold.md): çalışan CLI entrypoint ve immutable domain source contract, manifest/schema,12 runtime test ve clean copied-package startup. `apps/hub`/`packages/domain` gerçek kod; spike import yok, diğer capabilities disabled.
- Ana sayım1 DONE/3 IN_PROGRESS/26TODO; T03c yalnız koşullu owner seçim kapanışı, P0 kalite/capture/native/ROI sonuçları açık. Sonraki ana iş T05. Yeni model/API/connector/gerçek source/ücret yok.

### 2026-10-13 — Q15-A kabul edildi, T04 uygulaması başladı

- [İnsan onayı](../quality/reviews/q15-build-approval.json), [ADR-0012](../architecture/adr/0012-conditional-python-runtime.md): Python3.12/SQLite ilk çekirdek ve T04 başlangıç bağımlılığı T03c. Diğer P0 evidence ve release kapıları açık; model/ücret/gerçek data izni yok.
- Yeni apps/hub ve packages/domain kodu açılıyor; önceki spike/raw/kanıtlar korunur. T04 In Progress; startup/source-contract testleri gerçek runtime kabulüne bağlanacak.

### 2026-10-13 — Ana To Do geçişindeki plan engeli görünür

- T04 parent T03 kapanışına, T03 da henüz kapanmayan corpus/capture/native/ROI koşullarına bağlı;26 küçük P0 DONE ana MVP işlerini açmadı. Daha fazla küçük alt görev bu bağımlılığı çözmez.
- [Q15 kontrollü build önerisi](build-transition-proposal.md) hazır: yerel Python3.12/SQLite çekirdeğine başlayıp bağımsız kalite/release kapılarını açık tutma. Yeni stack/dependency kararı kullanıcı yanıtı bekliyor; henüz T04/phase/ADR değişmedi, bu yeni DONE kod işi değil. Bundled3.12.14/SQLite3.53.1 okundu,248 semantik test aynı runtime'da geçti; model/ücret/API yok.

### 2026-10-13 — Kalıcı explicit geç cevap önerisi tamamlandı

- T03ac scoped DONE: [reply store](../quality/reply-store.md), stored current snapshot/CID/soru-revision/source binding, SQLite reply append ve restart; duplicate kaynak tek receipt, çelişki last-writer seçilmez.14 yeni/248 semantik,15 karar,40 repo test geçti.
- Actual approval/clarification resolution/execution yok; actor/access transport fixture. Model/API0, eski snapshot/receiver failures aynı.26 küçük DONE; production UI/IAM/gold/capture/T03c kapıları açık, T04 başlamadı.

### 2026-10-13 — İnceleme snapshot kalıcı kaydı tamamlandı

- T03ab scoped DONE: [yerel review store](../quality/review-store.md), SQLite append/unique ID/transaction, restart sonrası aynı pending descriptor; current access/source/context tekrar kontrolü.12 yeni/234 semantik,15 karar,40 repo test geçti; gerçek geç cevap çözümü/Inbox UI/IAM yok.
-25 küçük DONE; ana T01/T02/T03 ve27TODO açık. Yeni model/API yok, actual receiver failures korunur. Gerçek capture inventory: PATH içinde Codex CLI bulundu, --version 0.162.0-alpha.17.2; alias oluşturma girişimi sandbox tarafından reddedildi, version çıktı. Claude komutu PATH'te bulunamadı; başka yerde kurulu olmadığı iddiası değil. Host hook/session/coverage veya model inference yapılmadı.

### 2026-10-13 — Tipli veriden model çağrısız taslak kodlandı

- T03aa scoped DONE: [typed review dönüşümü](../quality/typed-review.md), caller binding/access fixture sonrası mevcut6record'dan readback/action üretir; ambiguous soru null, claim/AC false verification ve atomic bekleme korunur.13 yeni/222 semantik,15 karar,40 repo test geçti.
- Ayrı authored draft kıyasında6action eşleşti; model inference/serbest metin extraction/production kabulü değil. İlk/ikinci raw aynı failed, yeni generated köken ayrı; model/API/mutation0.24 küçük DONE; T01/T02/T03 ve27 anaTODO/T03c açık.

### 2026-10-13 — RECEIVER-002 tek run tamamlandı; kalite geçmedi

- [İlk tam wire-2 çıktı](../quality/receiver-002-result.md) kaydedildi:1488byte/JSONvalid, storage next_actions missing, UI ambiguous Q_UI bind source ret; trial invalid_contract/unscored. İki proje review yok; raw onarılmadı, canonical mutation0.
- Q03-R6 cevaplandı/tüketildi; artık pending izin kapısı değil. Tek Luna/Low turn, follow-up/retry/tools/subagents/paidAPI0; usage/backend unknown, shared kota85→85 sıfır tüketim demek değil.209 semantik/15 karar/40 repo test passed; ana T01/T02/T03 açık, T04 başlamadı. Sırada aynı tipli gerçeklerin modelce tekrar üretilmesini azaltan yerel deterministic taslak; yeni model çağrısı yok.

### 2026-10-13 — Q03-R6 tek yeni deneme onayı

- Kullanıcı “Bu tek yeni denemeyi onaylıyorum” yanıtını açık RECEIVER-002 sorusuna verdi. Source-bound [authorization](../../examples/receiver-next-smoke/authorization.json) kaydedildi; yalnız exact8089-byte sentetik isteğin tek yeni projectless Luna/Low turn'ü, retry/tools/subagents/paidAPI0.
- Dispatch öncesi kayıt: gönderim/çıktı0. Kesin token/context cap unknown; parent/oracle/repo modele aktarılmaz. İlk başarısızlık korunacak; yeni retry otomatik yetkili değil. T03 ana gate kapanmadı.

### 2026-10-13 — Wire-2 bağımsız proje incelemesi tamamlandı

- T03z scoped DONE: [yeni receiver inceleme yolu](../quality/project-review-next.md), eski raw/ID/format onarılmadan v2 source guard ve Q14-A proje ayrımı.14 yeni/206 semantik,15 karar,40 takip testi geçti; eski deneyler ve38 Mermaid kaynakları aynı.
- Valid bağımsız proje taslağı korunur; ortak atomik grup bekler; whole-trial kalite scorer ayrı ve strict. Model/API/mutation0, Q03-R6 tek-run izni açık.23 küçük DONE;3 ana IN_PROGRESS/27 TODO değişmedi. Production T04 açılmadı; ana kapanış bağımlılıkları raporda görünür.

### 2026-10-13 — Takip kayıtlarının güncellik incelemesi

- [Denetim](../quality/tracker-status-audit.md):3 IN_PROGRESS/27 TODO ve22 küçük DONE doğru; açık kapılar tablosu ve T01 sonraki adımı eski kalmıştı. Q03-R6 tek-run onayı görünür, R22 fixture düzeltmesi ve T03y hazırlığı tekrar açık iş gösterilmez.
- Ana status/engine/production kabulü değiştirilmedi.6 aktif karar/doğrulama kapısı; bütün unanswered question envanteri değil. Açık tarayıcı sekmesi eski HTML tuttuğu için güncel Board/İngilizce status için reload; eski91test/stale checkpoint raporu yeni247test veya CI diye onarılmaz. Yeni model/API çağrısı yok.

### 2026-10-13 — Yeni source-only receiver isteği hazır

- T03y scoped DONE: [RECEIVER-002](../quality/receiver-next-plan.md), farklı request/wire sürümü, typed ortak machine schema ve açık per-record kurallar;8source mesajı tam,8089byte/8192tavan. No-oracle3file prepare, bağımsız authored scorer, no-overwrite ve20 yeni test;192 semantik/15 karar/40 takip geçti.
- Actual model send/output0, yeni izin yok; prompt-only schema provider enforced değil. İlk run/raw/prompt/expected ve38Mermaid kaynakları aynı. Shared kota/token/cost unknown; yeni tek-run önerisi somut pakette, production/gold/native/ROI/T03c kapıları açık.

### 2026-10-13 — Q14-A proje ayrımı ve açıklama cevabı kodu

- T03x scoped DONE: [ayrı per-project review katmanı](../quality/project-review.md). Bağımsız valid proje taslağı korunur; teknik hata/abstain/missing/ambiguity görünür, atomic group bölünmez, global kimlik/access hatasında ret. Sabit clarification ID ve explicit geç cevap association; gerçek approval/resolved yapılmaz.
- 20 yeni/172 semantik,15 karar,40 takip testi geçti. Yeni model/API/target/mutation0; ilk failed raw/scorer aynı. Descriptor/report var; durable Inbox, gerçek IAM/host resume/UI henüz yok. Sıra yeni ayrı source-only receiver isteği; T03c/main quality gate açık.

### 2026-10-12 — Receiver yerel sözleşme düzeltmesi

- T03w scoped DONE: [makine schema ve source guard](../quality/receiver-contract.md); bilinen soru korunur, belirsiz kayıt ayrı kalır; abstention/integer/record-action/kanıt sınırları test edildi.16 yeni/152 semantik,15 karar,40 takip testi geçti.
- Yeni model/API0; ilk gerçek sonuç failed olarak aynı kaldı. T03 kartındaki deney öncesi kayıt düzeltildi; yeni schema bağlı isteğin yerel hazırlığı sırada. Ana gate/stack/insan gold/native karşılaştırma açık.

### 2026-10-12 — RECEIVER-001 native ilk çıktı ve context/usage kaydı

- T03v scoped DONE yalnız [ilk configured Luna/Low native run kayıt/ölçümü](../quality/receiver-001-result.md). Tekturn/ilkoutput/retry0/paidAPI0; rawsyntaxvalid/schema invalidabstention, readback/action scoresunscored. UI model-label screenshot erişimi güvenlik kısıtıyla yok; backendunknown.
- 136 semantik test/2 yeni saved-output guard; frozen prompt/expected/manifest değişmedi. Full-messagecapture ile waitsummary farkı R23; receiver type/scope/abstention R24. Token/cost/aşımunknown; immediate sharedquota74→74 tüketim0 değildir. Ana context bu sohbet/devir dosyasında, yeni model izni tüketildi; sıra offline strict-schema örnekleri.

### 2026-10-12 — Receiver çalıştırma öncesi model/kullanım/context kaydı

- Kullanıcı yeni Luna/Low chat deneyini ve önce kayıt alınmasını istedi. [Execution notu](../quality/receiver-execution-notes.md), source-bound one-turn authorization dispatch'ten önce yazıldı. Model/tool/token/host sınırları ve ana sohbetin korunması açık.
- T03v IN_PROGRESS; henüz gerçek output yok. Native projectless yöntem önceki Chrome hazırlık önerisinden ayrı. Frozen prompt/expected/manifest/önceki model run'ları değişmedi; tokenizer/actual token usage unknown, paylaşılmış kota yüzdesi per-trial tüketim değildir.

### 2026-10-12 — Receiver isteği ve bağımsız evaluator

- T03u scoped DONE: [7950-byte frozen source-only istek ve ayrı authored oracle/evaluator](../quality/receiver-smoke-plan.md). İki readable view, readback ile safe next-action ayrı, metadata/type/source/critical false-state guardları.
- 134 semantik test/13 yeni; scripted positive yalnız evaluator harness. Actual model sends0/outputs0/paidAPI0, tek yeni run onayı bekliyor; source/gold/native/production ve ana gate'ler kapanmadı.

### 2026-10-12 — Kayıpsız paket küçültme ve readable view

- T03t scoped DONE: [inline kaynak/record table, decoder ve readable view](../quality/resume-compaction.md). Frozen önceki core exact; üç temsil aynı bağımsız authored checklist, alıntılar kodla çözülür, alıcı modele karakter saydırılmaz.
- 121 semantik test/11 yeni, byte azalması N01%31,79/N02%35,20. Missing source/ref, stale/source/access, no-truncation/no-authority testleri geçti; model/API/selection0. Gerçek receiver/native/token/gold kapıları açık; sırada bounded receiver test contract/evaluator hazırlığı.

### 2026-10-12 — Devam paketi ve dosya serialization kıyası

- T03s scoped DONE: [çalışan resume/export preflight](../quality/resume-file-comparison.md), source/response/state/access revision binding; eski/current/ambiguous/claim/not_run aynı core ile iki temsil içinde korundu.110 semantik test/8 yeni; model/selection/paidAPI0.
- İki proje için altı sentetik inspectable export, bağımsız authored checklist ve byte ölçümü. Simple-file daha küçük; token/para/receiver-model/native/user yükü ölçülmedi. Production RES/stack/yatırım kapıları ve ana task statusları korunur; sırada duplicate context azaltımı.

### 2026-10-12 — Çoklu cevap koleksiyonu

- T03r scoped DONE: [çalışan collector ve rapor](../quality/proposal-collection.md). MEMBERSHIP-003 tam response'ları source binding korunarak işlendi; old/current/ambiguous ayrı, upload claim/not_run evidence kaydı korunur. Projection unchanged/selection0/model0/paidAPI0.
- 102 semantik test/9 yeni: conflict, duplicate, wrong source/project, agent authority, abstention, separate receipt, retry/stale base. R22 gözlenen P0 bloklama yeni collector yolunda giderildi; single-answer API/tarihsel kanıt korundu. Single-current-question fixture production reconciliation değildir; ana görevler/kalite/stack gate açık.

### 2026-10-12 — H4 ve MEMBERSHIP-003 tek yeni run

- Kullanıcı1-EVET ile H4 partial quoted/planned review,2-EVET ile yeni8-message tek-send testini ayrı onayladı. [Review](../quality/reviews/h4-behavior.json) ve [tüketilmiş izin](../../examples/adversarial-smoke/authorization.json). T01i scoped DONE.
- [MEMBERSHIP-003](../quality/membership-003-result.md):6 candidate/source/type ve2scope-no-candidate beklentisi eşleşti; eski/current revision veENnot_run doğru, softcap/usage unknown; retry/paidAPI0. T03q scoped DONE,93 semantik test. Whole-batch çok-adayları bloklar; ayrı source-bound tanı no-mutation, R22/T10/T13 production reconcile açık.


### 2026-10-12 — Ortak kaynak kıyası ve iki yeni aile hazırlığı

- T03p scoped DONE: [aynı dört mesajda ölçüm](../quality/same-source-comparison.md), lexical/model shared-field skorları ve unsupported tür farkı açık. Yeni model çağrısı0; native/ekonomi veya genel quality değil.
- T01h scoped DONE: [sekiz yeni sentetik mesaj](../../examples/adversarial-smoke/README.md),6 draft candidate ve2 scope-no-candidate vaka;5321-byte frozen prompt, source/quote/hash consistency. H4 quoted/planned review pending; MEMBERSHIP-003-PROPOSED için tek-send onayı yok, sent0.91 semantik test passed; eski raw/corpus/rubric ve onaylı36 Mermaid değişmedi.


### 2026-10-12 — Gerçek kayıtlı adaydan tam kontrollü zincir

- T03o scoped DONE: [replay](../quality/membership-chain-replay.md), 13 authored checkpoint; source/karar kimliği değiştirilmedi. Ayrı fixture selection/impact, üç bounded gerçek temp dosya okuması, partial/full verifier fixture ve SQLite backup/reopen birlikte çalıştı.
- 86 semantik/15 decision/40 root test passed. Yetkisiz selection/impact, stale graph, değiştirilmiş raw/rebinding ve eksik expectations retleri; yeni model/paid API/egress0. Production IAM/criterion revision/full lineage ve geniş kalite açık; ana task statusları değişmedi.


### 2026-10-12 — Deney şeması doğrulandı

- Kullanıcının talebiyle MEMBERSHIP-002 kaynak/aday/guard akışı Mermaid olarak geri eklendi. Private GitHub inceleme ref'inde native SVG/metadata/bütün etiketler ve geniş görünüm kontrol edildi; önceki file:// erişim engeli değiştirilmedi.
- [Güncel şema](../quality/membership-002-result.md) ve [provenance](../quality/diagram-review.md): 36 kaynak /16 belge; önceki35 çizim hash'leri korundu. Bu doküman teslimi yeni model veya runtime testi değildir; ana görevler/sıradaki offline chain replay değişmedi.


### 2026-10-12 — MEMBERSHIP-002 gerçek typed çıktı ölçümü

- Kullanıcı yeni tek-send v2 isteğini onayladı; [izin](../../examples/membership-smoke-v2/authorization.json) tüketildi. Aynı dört sentetik mesaj, boş geçici/kişiselleştirilmemiş normal Chrome sohbeti, Instant UI etiketi; retry/paid API 0.
- [Sonuç](../quality/membership-002-result.md): dört exact quote/typed aday authored_draft beklentileriyle eşleşti; TP4/FP0/FN0. Alanlar değiştirilmedi, önceki raw/rubric korundu. Ayrı request guard'larında proposal pending_trusted_selection/unmatched_or_stale, projection unchanged; upload veya task verified olmadı.
- T03n scoped DONE; 80 semantik test. Genel accuracy/holdout/human gold/production IAM/domain target kapıları açık. Sıradaki offline replay beklemiyor; yeni model send yetkisi yok.


### 2026-10-12 — MEMBERSHIP-001 gerçek çıktı ve offline typed düzeltme

- Kullanıcı kesin token/context cap unknown riskini not ederek tek denemeyi onayladı. [Onay](../../examples/membership-smoke/authorization.json) tüketildi: tek normal Chrome geçici/nonpersonalized ChatGPT gönderimi, Instant UI etiketi; gerçek sürüm/usage unknown, paid API yok, retry 0.
- [Sonuç](../quality/membership-001-result.md): üç source quote geçti; farklı association/criterion attribute adları ve Execution upload türü, S03 abstain. Exact gate incomplete; controlled guard canonical mutation 0. Raw/primary rubric korunur; n=1 authored draft genel accuracy değildir.
- T03l run kayıt/ölçüm teslimi DONE; T03m ayrı typed v2/negatif test/paket DONE. 78 semantik suite testi passed; v2 gönderilmedi. R21 observed ve ana T03 kalite/native kapıları açık.


### 2026-10-12 — Mevcut üyelik gerçek test paketi hazır

- T03k scoped DONE: [MEMBERSHIP-001 planı](../quality/membership-smoke-plan.md), 3330-byte source-only prompt, dört synthetic mesaj/iki scoped request ve ayrı authored expectations. No-dispatch batch preparation/import/scorer, 72 semantik suite testi (6 yeni).
- Öneri bir UI submission/sıfır retry; soft 2048 output token hedefi, kesin token/context cap unknown. Önceki izinler tüketildi; yeni manual-risk onayı gelmeden gerçek send yok. Paid API yok, gerçek accuracy not_run; product hard-cap gereksinimi korunur.


### 2026-10-12 — H3 onayı ve ilk üç behavior incelemesi tamamlandı

- Kullanıcı H3 için “uygun” dedi: belirsiz A saklanır, hangi soruya ait olduğu tahmin edilmez, açıklama istenir. [Review](../quality/reviews/h3-behavior.json) kaynak/oracle hash ve scope taşır. T01g ilk üç davranış incelemesi scoped DONE; tam corpus/exact etiket gold veya production runtime tamamlanmış değildir.
- T01/T02/T03 IN_PROGRESS; dört kod teslimi ve T01g kapanışı korunur. Sırada gerçek quote-only anlam testi hazırlığı ve exact etiket ölçümü; ücret/ek model dispatch izni yok.


### 2026-10-12 — H2 açıklama sonrası insan incelemesi

- Kullanıcı kısmi kriterin nedenini sorguladı; geçici durum/hata senaryosu ve kalan doğrulamayı sürdürme açıklandı, ardından “evet” ile kabul edildi. [Review kaydı](../quality/reviews/h2-behavior.json) soru/itiraz/açıklama/yanıt ve source/oracle hashlerini korur. Bir passed criterion bütün görevi kapatmaz; eksikler ve next verification takip edilir.
- H1/H2 behavior reviewed, H3 ve exact etiket/corpus gold pending. Source/oracle değişmedi; yeni model/ücret izni yok, T01 IN_PROGRESS ve dört scoped Done teslimi korunur.


### 2026-10-12 — H1 insan davranış incelemesi

- Kullanıcı doğrulanmış geç cevapla karar seçimi ve görev etkisinin ayrı onayı davranışını kabul etti. [Sürümlü review](../quality/reviews/h1-behavior.json) exact soru/yanıt ve source/oracle hash içerir. Yalnız sorulan davranış reviewed; task impact/extraction etiketleri veya bütün corpus gold yapılmadı, oracle değiştirilmedi.
- H2 kısmi kabul kriteri soruldu; H3 ve tam etiket/karşılaştırma kapıları açık. T01 IN_PROGRESS; yeni model/harcama izni yok. Dört küçük Done teslimi korunur.


### 2026-10-12 — Dört küçük teslimin kapanışı ve tek komutluk zincir

- T03g/T03h/T03i/T03j scoped DONE olarak kaydedildi; her teslimin kabulü ve kanıtı backlog'da. Geniş ana T03 ve T03f kalite/native kapıları korunur. [Tek komutluk çalışan zincir](../quality/integrated-chain.md) quote-only adapter ile bounded observer'ı karar/impact/AC/restore'a bağlar.
- 66 semantik test ve yedi checkpoint geçti; model_dispatches=0, semantic_inference=not_run, production_runtime=false. İnsan H1 yanıtı pending; paid API yok.


### 2026-10-12 — Ek API ödemesi olmadan yerel hedef kodu

- Kullanıcı API kredisi $0.00 bildirdi ve bakiye yüklemeden devam istedi; bu model call/harcama onayı değil. [Local observer](../quality/local-observer.md) kodlandı: tek seçili dosya, gerçek hash okuması; eksik/izin/boyut/yarış ayrı, task_verified=false. 65 semantik suite testi (9 yeni) geçti.
- Önceki API paket teslimi korunur. T01/T02/T03 IN_PROGRESS; insan H1 review soruldu fakat yanıt gelmeden gold sayılmaz. Mevcut hesap için yeni tek-send planı ve anlam kalite ölçümü açık; ödemeyi bütün kod çalışmasının blocker'ı sayma.


### 2026-10-12 — Quote-only API paket ve import kodu

- [Teslim](../quality/quote-api-package.md): source-only schema/payload hazırlığı, pending token/context/para manifesti, saved response import; refusal/incomplete/authority retleri. 56 semantik suite testi geçti (8 yeni); yeni provider inference 0.
- Paket gönderilebilir değildir; model ve tavanlar null. T03 IN_PROGRESS, gerçek anlam/graph/hedef/native/production kapıları açık. Sırada somut bounded dispatch kararı ve insan review var.


### 2026-10-11 — Onaylı sınırlı kaynak adapter teslimi

- Kullanıcı 60 dakikalık kaynak/değerlendirme kod dilimini kabul etti; genel araştırma ve yeni özellik tasarımı genişletilmedi. API yalnız resmî belgelerle değerlendirildi; yeni paid/inference çağrısı yapılmadı.
- [Teslim](../quality/source-anchor-adapter.md): bounded exact-quote adapter + ayrı quote-only contract/CLI + candidate rubric; 48 semantik suite testi. [Hashli kanıt](../quality/source-anchor-adapter-results.json): 10 offset ayrı türevde düzeltildi, 11 candidate geçti; üç scripted case state değiştirmedi.
- Candidate ve canonical/domain değerlendirmesi ayrıldı; eski gerçek sonuçlar/oracle değişmedi. Gerçek model kalite, ilişki/impact extraction, gerçek host, native karşılaştırma ve production stack kapıları açık. T03 IN_PROGRESS kalır.
- [Projeler arası rehber](../governance/evidence-first-development.md) proje AGENTS dosyasına bağlandı. Global config ve başka repo değiştirilmedi; diğer projelerde referansla kullanılabilir.


### 2026-10-11 — Built edilebilirlik sınırının ek denetimi

- [S02 türev follow-up](../quality/s02-derived-followup.json): kontrollü AnswerRecord + fixture graph/onay/target/AC zinciri passed; bağımsız S02 draft değerlendirmesinde tür eşleşmesi 4/11, exact type/span 0/11. Bu oranlar insan-gold doğruluk değildir; candidate/canonical tür ve span granularity uyumu da incelenmelidir. Ham model sonucu değiştirilmedi.
- Yeni provider çağrısı veya ücretli API yok; bu Codex çalışmasının kendi hesap kotası/token maliyeti ayrıca geçerlidir ve ölçülmedi. Teknik blokların fixture/test edilebilirliği tüm ürünün ekonomik, güvenilir veya pazarda faydalı olduğunu kanıtlamaz.
- T03 sonraki iş scorer/output uyumu + bounded source adapter; kısa teslimli süre/maliyet sınırlı T03c kapısı owner'a öneridir, bütçe/takvim kabulü değil. Tam kapsam korunur; yeni research/production/modeller otomatik başlatılmaz.


### 2026-10-11 — R20 görünürlüğü ve ücretsiz kaynak konumu fizibilitesi

- README, risk register ve T03 kartına gözlenen engel/denemeler/etkilenen iş eklendi. Model cevabı geldi ama source span import'unda durduğumuz; semantik kalite/karar zincirinin henüz ölçülmediği ayrı gösterilir. R20 High bir etki değerlendirmesi; n=1 ölçülmüş genel hata olasılığı değildir.
- [ANCHOR-PROBE-01](../quality/source-anchor-feasibility.json) ve salt okunur probe kodu: aynı raw output'ta 11 tekil exact quote, kodla konumlandırılan bellekteki türev mevcut validator'dan geçti; 7 edge kontrolü geçti. Oracle, yeni inference, ücret ve canonical mutation yok; orijinal response ve ilk iki makine sonuç kaydı değişmedi. Production adapter veya semantik başarı teslimi değildir.
- Doğrulama: 38 root testi, 28 semantik bağlantı testi ve 7 ayrı probe kontrolü geçti; docs/anchor/progress kontrolü geçti. Tarayıcıda aktif risk/deneme bölümü görünür, kaynak bağlantıları ve R20 açık durumu okundu. Bu sonuçlar model anlam kalitesini veya production düzeltmesini kanıtlamaz.
- Offline bounded adapter/negatif test/ölçüm sıradadır; kullanıcı kararı bekleyen offline adım yok. Yeni model çağrısı/gerçek veri/erişim/ücret ve production stack ayrı somut kararları korur. T03 IN_PROGRESS, R20 açık; unit test sayısı veya probe geçişi risk kapatmaz.


### 2026-10-11 — Q03-R5: gerçek output ve strict kaynak konumu reddi

- Kullanıcının bir yeni deneme onayıyla aynı sentetik S02 normal Chrome, boş kişiselleştirilmemiş geçici ChatGPT oturumunda tek kez gönderildi; bir gerçek output alındı, retry 0. İlk cloudflare kaydı ayrı korunur; kök neden kanıtlanmadı.
- [Ham çıktı ve güncel rapor](../quality/s02-second-attempt-result.md): JSON parse/ID eşleşmesi geçti, 11/11 quote exact, 10/11 source span hatalı (7 sınır dışı, 3 kesilmiş). Strict evaluator exit 1 ile skor/zincir öncesinde reddetti; canonical mutation 0. Semantik kalite başarısı ilan edilmedi.
- Rapor checkpoint’inin eski model `not_run` alanı UI ve generated görünümde tarihsel olarak etiketlendi; güncel model sonucu T03 kaydında gösterilir, tarihsel kanıt JSON’u değiştirilmedi. 37 mevcut kök test, docs/anchor/progress kontrolleri geçti; model validator ret durumu ayrıca yeniden üretildi.
- Q03-R5 tüketildi; yeni inference/ücret izni yok. Model kimliği ve gerçek token/cost unknown. Offline message-ID + exact-quote anchoring deneyi sıradadır; orijinal output değiştirilmez, türev ayrı ölçülür. Human gold/native/capture/production kapıları ve T01/T02/T03 IN_PROGRESS korunur.

### 2026-10-11 — Q03-R4 A ve ilk gerçek web gönderimi

- Kullanıcı yalnız bir S02 için hard token/context cap olmadan sınırlı risk istisnasını kabul etti. Ürün hard-cap kuralı, sıfır retry/tools ve ek ücret yasağı korunur.
- Boş, kişiselleştirilmemiş geçici ChatGPT web oturumunda sabit sentetik prompt bir kez gönderildi. `cloudflare_challenge` görüldü; model output 0, usage/token unknown. Retry veya ikinci yöntem çağrısı yapılmadı; kalite/scorer/chain bu deneme için çalışmadı.
- [Rapor](../quality/s02-account-smoke-result.md) ve [makine kaydı](../quality/s02-account-smoke-results.json), policy ve T03 ilerlemesi güncellendi. İlk otomatik onay reddi, mevcut insan cevabının sohbet kaydında doğrulanmasından sonra aynı eylemin yeniden değerlendirilmesiyle çözüldü; dolaylı dispatch yok.
- T01/T02/T03 IN_PROGRESS ve 11 mevcut parça korunur; başarısız transport denemesi ana görev kapanışı veya semantik başarısızlık değildir. Sonraki gönderim yeni sınırlı izin gerektirir.

### 2026-10-11 — Q03-R3 A: OpenAI hesabı seçildi

- Kullanıcı mevcut ChatGPT/Codex hesabını seçti; policy, deney planı ve owner karar kaydı güncellendi. Normal hesap kullanımının açık olduğu salt okunur kontrol edildi; kişisel hesap/kota detayları yayınlanmadı.
- İncelenen SIWC preview yolunda output cap parametresi desteklenmiyor; kesin per-run token/context tavanı doğrulanmadı. [S02 planı](../quality/s02-account-smoke-plan.md) tek-deney risk istisnasını somutlaştırıyor; henüz kabul edilmedi, dispatch pending_capability_review ve inference not_run.
- Board'un kaynak T03 ilerleme/kalan adımı güncellendi. 11 hazırlık parçası ve T01/T02/T03 IN_PROGRESS korunur; hesap seçimi semantik başarı veya ana görev kapanışı sayılmaz.

### 2026-10-11 — İngilizce status ve P0 preflight kodu

- Kullanıcı tercihine göre Board/filter/task status etiketleri To Do/In Progress/Blocked/Done oldu; kanonik task state veya faz değişmedi. Jira'nın özel workflow desteğiyle uyumlu etiketleme; Blocked her Jira'nın varsayılanı diye sunulmaz.
- T03f/T03b altında [yerel token/context preflight](../quality/token-preflight.md) kodlandı: tam input/generation/context ve tüm çağrı/parent bütçe üst sınırları; unknown, review ve hard cap ayrımı. 17 fixture testi; S02 package hashleri sabit, current assessment blocked, gerçek inference not_run. Model/hesap/para veya global host config değişmedi.
- T03 Son ilerleme ve hazırlık matrisi güncellendi; mevcut parça sayısı 11. İlk gerçek S02 output'u için hesap/model ve uygulanabilir limit/dahil kullanım teyidi açık. Production atomik rezervasyon/para/provider enforcement TODO; test sonucu yalnız offline kontratı kapsar. [Sonuç kaydı](../quality/token-preflight-results.json).

### 2026-10-11 — P0 ilerlemesini ekrana yansıtma

- Son token/context güncellemesi yalnız status/deney belgelerine işlenmişti; ekranın dört kaynak dosyasındaki hazırlık tablosu ve task özetleri güncel olmadığı için görünüm değişmemişti. Eksik bağlantı giderildi.
- T01/T02/T03 kanonik backlog'una Son ilerleme ve Sıradaki adım eklendi; açık faz özeti, Board kartları ve detay bunları aynı kaynaklardan okur. S02 hazırlığı mevcut parçalara eklendi (10); capability kapısı güncellendi. Üç ana görev IN_PROGRESS, 27 TODO; kapanış veya gerçek model başarısı üretilmedi.
- 12 tracker testi geçti; tarayıcıda T03 ayrıntısı ve P0=3 filtre sonucu görüldü. [Doğrulama kaydı](../quality/p0-progress-visibility-results.json). Rehber, sonraki teslimlerde durumun yanında task ilerleme/kalan alanlarının da güncellenmesini ister; canlı agent telemetry iddiası yok.

### 2026-10-11 — Token ve context durdurma sözleşmesi

- Kullanıcının aşırı tüketimde durma/onay bekleme ihtiyacı [risk belgesine](../product/token-risk-and-approval.md) ve [token ekonomisine](../architecture/routing-token-economy.md) işlendi: tam input + generation rezervi + margin, uygulama/model pencerelerinin küçüğü; risk eşiği ile hard cap ayrılır.
- [S02 plan/policy](../quality/s02-account-smoke-plan.md) hard token/context desteği henüz unknown olduğundan `pending_capability_review`; gerçek inference not_run. 5498 byte sabit prompt, 1536 soft output hedefi, bir gönderim/sıfır retry korunur. Ek ücret, dış hesap kullanım kontrolü veya sayısal optimum iddiası yok.
- Gereksinim kaydı tamamlandı; production limiter/atomik rezervasyon uygulanmadı. Ana task durumları değişmedi; model/arayüz seçimi ve first-dispatch capability/limit doğrulaması açık.

### 2026-10-11 — Basit Board ve Q03-R2 mevcut hesap smoke'u

- Kullanıcının görsel takip talebi üzerine aynı veriden Board eklendi: Planlandı/Çalışılıyor/Engelli/Tamamlandı, kart→AC/alt görev, faz/arama/durum filtreleri; Liste görünümü korunur. Salt okunur; ana task statüsü veya production UI kapsamı değişmedi.
- Tarayıcıda 30 kart (27 TODO/3 IN_PROGRESS), MVP=21, T01 ayrıntısı ve Board/Liste geçişi görüldü; mevcut 10 tracker testi geçti. Model çalıştırma veya completion mutation yok. [Teslim doğrulaması](../quality/board-and-account-preparation-results.json).
- **Q03-R2 A kabul edildi:** [S02 mevcut hesap planı](../quality/s02-account-smoke-plan.md) ve üç kaynak-only/prompt/policy dosyası hazır. Tek S02/11 sentetik mesaj, bir gönderim, retry/tools/subagent yok; ek API/credit ücretine izin yok. 1536 token hedefi enforce edilmiş tavan diye gösterilmez; 128 KiB import sınırı provider maliyetini sınırlamaz.
- Sağlayıcı/hesap/model seçimi ve dahil kullanım teyidi açık; gerçek inference not_run, usage null. Bu sohbet oracle gördüğü için bağımsız extraction output'u diye yeniden kullanılmadı. Human gold/native/production kapıları korunur. Statik ilerleme görünümü yenilendi; repo private tutulur.

### 2026-10-11 — Dinamik geliştirme görünümü

- [İlerleme görünümü](progress.md) ve [yerel takip ekranı rehberi](progress-guide.md) eklendi. Aynı backlog/hazırlık/engine/kanıt kaynaklarını okur: 30 ana görev, 9 mevcut hazırlık/deney/araç parçası, 5 açık kapı, görev AC/alt dilimleri ve 10 production engine planı.
- Kaynak dosyaları API isteğinde yeniden okunur; görünür tarayıcı 15 saniyede bir sorgular. GitHub Markdown görünümü aynı kaynaklardan üretilir; CI bayat görünümü reddeder. GitHub’dan yerel kopyaya otomatik sync veya canlı agent telemetry yoktur.
- [Doğrulama kaydı](../quality/development-tracker-results.json): 10 yeni tracker testi geçti; tarayıcıda MVP=21/açık=3 filtreleri, T01 kabul/alt görev, boş arama ve yenileme görüldü. Önceki 91 P0/evaluation test kaydı ayrı kanıt kapsamıdır; tracker ürün kalitesini kanıtlamaz. Docs/anchor/source görünüm kontrolü geçti. Responsive override ve polling latency ölçümü yapılmadı.
- Salt okunur loopback; model çağrısı/ücret/public hosting yok. Ana görev durumları T01–T03 IN_PROGRESS ve diğer 27 TODO olarak korunur. Production stack, semantik gerçek model, insan gold ve native kıyas kapıları açık kalır. Engine belgesindeki “hiç uygulanmadı” ifadesi production teslimi ile P0 parçalarını ayıracak şekilde düzeltildi.

### 2026-10-11 — Öneri, gerçek kullanıcı seçimi ve hedef uygulama ayrımı

- Kullanıcının dosya üretimi/yükleme bilinmeyeni [ürün sözleşmesine](../product/intent-to-reality-gap.md) dönüştürüldü: karar, artifact, exact hedefe uygulama ve acceptance evidence ayrı; reported/observed/unknown, partial ve stale davranışları tanımlandı.
- İki tamamlayıcı Mermaid akışı, GAP-01–10 ve T14d/T18i/T20i/T24n planlandı; T01 oracle ve T03 native/extension karşılaştırmasına bağlandı. Yeni engine/scope veya otomatik bağlantı/upload yetkisi yok.
- [Claude Projects incelemesi](../discovery/claude-projects-overlap.md), ciddi memory/koordinasyon örtüşmesini ve 17 Eylül tanıtımı ile bildirilen 9 Ekim erişim yayılımını ayırır. Orijinal X kaynağı 403; rollout tarihi ikincil teyit düzeyinde, bütün hesaplar/genel erişim iddiası yok.
- Uygulama, target adapter, gerçek kullanıcı/LLM deneyi ve GAP testleri not_run. Doküman kontrolü geçti: 73 Markdown, 552 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. GAP-01–10, dört alt dilim ve iki Mermaid kaynak bloğu kontrol edildi; görsel render yapılmadı. Sıradaki T01 ve açık owner tercihleri korunur.

### 2026-10-11 — Devam paketi ve hafıza yeterliliği taslağı

- Yapıştırılan konuşmadan [devam paketi](../product/resume-package-and-memory.md) ve [Spike-1 v1](spike-1-v1.md) hazırlandı: yaş/kanıt/coverage, güncel karar/AC, source provenance, copy/launch ayrımı ve clean-session baseline kıyası.
- T20h/T18h/T24m, S1-01–06 ve RES-01–08 planlandı. Q11 ilk düğme tercihi açık; A kopyala öneri, B capability araştırması. Wedge/MVP yeniden tanımı yapılmadı; bu repo main'inde Spike-0 runtime/prototipi bulunmadı.
- Yalnız tasarım ve deney protokolü; gerçek oturum, model, clipboard veya UI testi yapılmadı. Tam vizyon, ana görev/MVP kriterleri ve sıradaki T01 korunur.
- Doküman kontrolü geçti: 71 Markdown, 532 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. RES-01–08 ve S1-01–06 kimlikleri kontrol edildi; senaryolar not_run.

### 2026-10-11 — Token riski onayı, çoklu chat ve işleme gecikmesi

- [Ek token risk onayı](../product/token-risk-and-approval.md): deterministik risk tespiti, sınırlı plan onayı, unknown/hard-cap ayrımı ve koşu sırasında yeni çağrıyı durdurma. T09d/T19b/T24k ve TRA-01–10 planlandı.
- [Çoklu chat/lag](../architecture/multi-chat-and-processing-lag.md): session/span binding, kaynak→konu→task/karar ilişkisi, çelişki/geç mesaj, ACL-aware context, frontier/queue/gap ve yük ölçümü. T05d/T10b/T06g/T18g/T24l; CHAT-01–06/LAG-01–06 planlandı.
- Teknik tasarım ve test planıdır; model/host erişimi, runtime, hız, tasarruf ve UI testi yapılmadı. Ana 32 scope/30 görev/14 MVP kriteri korunur; T01 sıradaki iş. Q03 ve sayısal kapasite/risk eşikleri açık kalır.
- Doküman kontrolü geçti: 69 Markdown, 507 yerel bağlantı; TRA/CHAT/LAG için 22 planlı senaryo kimliği doğrulandı. Bunlar runtime test sonucu değildir; mevcut diyagramlar değiştirilmedi.

### 2026-10-10 — Q10-A kaynak keşfi tercihi kabul edildi

- Kullanıcı seçili öneriye “1a ile devam” dedi: ayrı metadata/listeleme izni varsa yeni kaynak için bağlama önerisi; seçilmeden ve gerekli onaylar tamamlanmadan içerik okuma veya takip yok. Manuel bağlantı alternatifi korunur.
- Karar/gerekçe, bağlantı, tetikleme, backlog ve ACC-02 güncellendi. Önceki ilerleme kayıtlarındaki Q10 bekleme durumu bu yeni kayıtla kapanır; Q07/1C ve diğer açık izin/bütçe kararları değişmez.
- Ürün tercihi belgelendi; gerçek hesap keşfi, yeni bağlantı, runtime veya provider testi yapılmadı. T01 sıradaki iş olarak kalır.

### 2026-10-10 — İşlem limitleri ve kötüye kullanım tasarımı

- [Limit sözleşmesi](../architecture/resource-limits-and-abuse.md): rate/burst, concurrency, byte/iş kotası, token/harcama ve DB transaction sınırları ayrıldı. Ortak insan/subagent bütçesi, receipt koruyan admission, limiter arızası, bounded log ve admin açıklamaları tanımlandı.
- T04d/T06f/T08c/T24j ve LIM-01–10 planlandı; OWASP API4, RFC 6585 ve SQLite birincil belgeleri incelendi. Mekanizmalar öneri, eşikler OPEN-12/16 ölçüm kapısında; Q03 harcama/egress izni açık kalır.
- Mevcut 30 Mermaid diyagramının topolojisi değiştirilmedi; ek sözleşme yeni servis/engine gerektirmez. Runtime, yük/saldırı testi veya çalışan limiter yok; T01 sıradaki hazırlık olarak kalıyor.
- Doküman kontrolü geçti: 67 Markdown, 483 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. LIM-01–10 kimlikleri kontrol edildi; senaryolar not_run. Eşzamanlı ranking güncellemesi korunarak birleştirildi.

### 2026-10-10 — Biriken işler için açıklanabilir ranking tasarımı

- [Ranking sözleşmesi](../product/priority-and-flow.md): 40+ task senaryosu, sekiz faktör, ilerlememe nedenleri, next actionable ve downstream etki açıklaması; canonical priority / önerilen rank / teknik execution order ayrıldı.
- Admin/owner etkin proje yetkisiyle; üst agent yalnız önceden verilmiş grant içinde teknik planı düzenleyebilir. Scope/value ve korunan karar hakları insan Product Owner'da; öneri otomatik plan değişikliği değildir.
- MVP deterministik blocker/dependency + basit board; P2 context-aware scoring/simülasyon/UX feasibility adayı. T11c/T20e/T24d ayrıntılandırıldı, T26b PROPOSED eklendi; FLOW-09–17 planlandı, FLOW-01–08 ve ana görev bağımlılıkları korundu. DEC-17'nin kabul tarihi 2026-10-09 olarak kaldı; teknik ağırlık/eşik/faz kesinleşmedi.
- Yalnız doküman değişikliği; feature, runtime, UI veya scoring deneyi yapılmadı. T01 sıradaki iş; açık kararlar ve 14 MVP kriteri korunuyor. Doküman kontrolü geçti: 66 Markdown, 471 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Sekiz hedef belge dışında değişiklik olmadığı ve FLOW-01–08/ana görev bağımlılıklarının korunduğu ayrıca kontrol edildi; planlı FLOW senaryoları not_run.

### 2026-10-10 — Sequence, DB ilişkileri ve tetikleme/zamanlama sözleşmesi

- [İletişim belgesi](../architecture/execution-and-integrations.md): 12 tetikleyici, sistem/API matrisi, olay odaklı işleme ve profil/polling/retry deney aralıkları; task doğrulama, koşullu LLM ve dış teslim için üç sequence.
- [DB ilişkileri](../architecture/data-relationships.md): bağlantı/izin ve task/run/kanıt için iki ER; N:M input/kanıt, composite key, revision, transaction ve indeks adayları. Toplam 30 Mermaid şeması; kesin DDL veya çalışan API yok.
- T04c/T06e/T09c/T14c/T18f/T24i/T28c ve SEQ-01–08/DBR-01–06 planlandı. Sayısal süreler ölçülmemiş adaydır; Q02/Q03/Q06/Q08/Q10 açık kalır. T01 sıradaki hazırlık; runtime/DB/provider testleri yapılmadı.

### 2026-10-10 — Proje erişimi, izin makbuzu ve bağlantı soruları

- Kaynak hesabı/OS yetkisi, hedef projeye bağlantı ekleme yetkisi ve agent grant'i ayrı tanımlandı. Sürümlü ConnectionAuthorization, requested/granted/effective scope, kurulumda altı soru ve proje bazlı “Bağlantılar ve izinler” görünümü belgelendi.
- Yeni kaynak, scope/egress artışı, kaynak transferi, path kaçışı, karışık transcript, revocation ve kayıtların sonraki kullanımı açıklandı. T05c/T16b/T20g/T24h ile ACC-01–08 planlandı; metadata keşfi için Q10 seçenekleri hazır, cevap bekliyor.
- Mevcut 25 Mermaid şeması değiştirilmedi; bağlantı/policy sınırlarının metinsel sözleşmesi ayrıntılandırıldı. Runtime, provider izin deneyi veya yeni görsel render testi yapılmadı. Hesap bağlantısı, yetki genişletme, gerçek veri aktarımı ve ücret yok; T01 sıradaki iş olarak kalıyor.

### 2026-10-10 — Diyagram incelemesi ve yönetim/operasyon tasarımı

- 11 belgedeki 20 Mermaid şeması son kararlarla karşılaştırıldı; 1C arşiv/TTL, eksik DEC-15–17, MCP routing ve tenant ER kapsamı düzeltildi. Run, soru, blocker, admin ve incident için beş şema eklendi: toplam 25. Ayrıntı [inceleme kaydında](../quality/diagram-review.md).
- [Yönetim sözleşmesi](../product/administration-and-operations.md) yerel/kurulum admin'i, workspace/proje rolleri, platform operatörü, günlük kullanıcı, agent ve olası L1 desteği ayırır. Incident, güvenli müdahale, versioned parametre ve miras/tavan kuralları; T20f/T21c/T23e/T24g ve ADM-01–10 planlandı.
- Lisans, hosting, veri erişimi ve ticari paket ayrı kararlardır. OSI/AGPL/Apache kaynakları tekrar okundu. Repo private kalır; lisans, ücretli provider, kullanıcı hesabı veya hosted servis oluşturulmadı. P1b minimal yerel yönetim, P4 ekip/platform konsolu önerisi; runtime/test sonucu değil.
- Doküman kontrolü ve diagram inventory çalıştırıldı; son kontrol kapsamı inceleme kaydında. T01 hâlâ sıradaki uygulamalı hazırlık; açık lisans/retention/host/bütçe kararları bu tasarımla kapanmadı.

### 2026-10-10 — Scrum, PMI ve genel bağımlılık yönetimi ayrımı

- Scrum çerçevesi, PMI mesleki kuruluşu ve yöntemden bağımsız bağımlılık/engel kavramları ayrıldı. Önceki Scrum Alliance atfı tek sahiplik/kaynak gibi yorumlanmayacak şekilde açıklandı; DEC-17'nin kabul edilmiş ilkesi korunuyor.
- Ürün çekirdeği, kendi geliştirme ritmimiz ve müşterinin yöntemi ayrı katmanlarda açıklandı. Farklı süreçlere uyarlanabilirlik konumlandırması önerildi; tam Scrum/PMBOK uyumu, kritik yol veya yeni yöntem modları taahhüt edilmedi.
- PMI birincil kaynakları okundu; Scrum kaynakları tekrar kontrol edildi. Ürün kodu/öncelik algoritması değişmedi, runtime veya yöntem uyum testi yapılmadı. T01 sıradaki uygulamalı hazırlık olarak kalıyor.
- Doküman kontrolü geçti: 62 Markdown, 374 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Beş belgede kavram ve kaynak atfı netleştirildi.

### 2026-10-10 — Subagent soru ve karar mekanizması

- Bilgi/görüş isteği, yetki içi teknik seçim ve korunan insan kararı ayrıldı. Parent/uzman agent danışması onay yetkisine dönüşmez; önceki geçerli karar tekrar sorulmadan kaynaklı kullanılabilir.
- Soru/cevap/approval/delivery/resume/task verification ayrı; timeout, parent kaybı, stale/conflict, ACL, döngü/bütçe ve gözlem-only host istisnaları yazıldı. Yalnız cevaba bağımlı iş bekler; dış process'in durduğu teyitsiz söylenmez.
- T13e/T18e/T24f ve ASK-01–08 planlandı; insan review ilkesi değiştirilmedi. Host kurulumu, messaging, agent execution veya runtime testi yapılmadı. T01 sıradaki hazırlık; önceki açık tercihler korunuyor.
- Doküman kontrolü geçti: 62 Markdown, 371 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Sekiz ASK senaryosu planlı kabul tanımıdır, çalışmış test sonucu değildir.

### 2026-10-10 — Karar gerekçelerinin kaynakla eşlenmesi

- Proje yönetim planında DEC-17 için kullanıcı ihtiyacı, karar sahibi/tarihi, kaynak yaklaşımı, Decivora uyarlaması, seçim gerekçesi, bedel ve doğrulama aynı kayıtta eşlendi. Kaynak kontrolünün kullanıcı yönlendirmesinden sonra yapıldığı ve formal Scrum uyumu iddiası olmadığı açık.
- Karar haritasına gerekçe belgeleri indeksi ve kayıt standardı eklendi. Kayıtsız geçmiş gerekçeler uydurulmadı; sonradan yapılan karşılaştırma tarihsel seçenek sunumu gibi gösterilmedi. Ürün kapsamı/karar statüsü değişmedi.
- Doküman kontrolü geçti: 62 Markdown, 366 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Runtime veya bağımsız LLM anlama testi yapılmadı.

### 2026-10-09 — Tek insanın çok agent'ı ve ekip kurulumu

- İnsan sayısı, agent sayısı ve execution yetkisi ayrı eksenler olarak belgelendi. Mevcut INT-02/TEAM-01 kapsamında tek owner + iki agent için T02c/T18d/T24e; ekip kurulum/hesap/davet için C01–C04 ayrıntıları eklendi.
- Resmî Codex SDK, OpenAI reasoning ve Claude Code hook belgeleri okundu. Girdi/parent/tool/artifact/usage coverage, gözlemci/aktör kimliği, private muhakeme sınırı, run başarı/task doğrulama ayrımı, duplicate/revoke/race ve usage toplamı tasarlandı. Agent veya provider kurulmadı.
- Self-host/managed seçenekleri, merkezi servis/ayrı hesaplar, private kaynak paylaşımı, bootstrap/recovery/offboarding ve kişisel→ekip geçişi belgelendi. Hosting/SSO/ticari lisans seçilmedi; bireysel pilot ve T01 sıradaki hazırlık olarak kaldı.
- AGT-01–08 planlıdır; uygulama, gerçek çok-agent çalışması veya ekip giriş testi yapılmadı. Q02/Q03 ve OPEN-14–16 mevcut karar kapılarıdır.
- Doküman kontrolü geçti: 62 Markdown, 362 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Yeni sekiz AGT senaryosu uygulama kabul planıdır, test sonucu değildir.

### 2026-10-09 — Product Owner yaklaşımı ve blocker önceliği

- Q09/DEC-17 kabul edildi: ilerlemeyi engelleyen işler/kararlar ve downstream gecikmesi önce; değer/hedef/risk odaklı çevik çalışma. Bildirim kanalı/sıklığı ve formal Sprint takvimi seçilmedi; Q08 ayrı açık.
- Scrum Guide ve Scrum Alliance kaynakları incelendi; çerçeve, uygulama rehberi ve bireysel pilot uyarlaması ayrıldı. AGENTS ve kısa yönetim planı güncellendi; sertifika/uygunluk iddiası yok.
- Öncelik/akış belgesi, blocker ile ready ayrımı, benzersiz etki hesabı, ACL/unknown/stale, karar yetkisi, inbox ve öğrenme ölçümleri yazıldı. T11c/T20e/T24d ve sekiz FLOW kabul senaryosu planlandı; runtime veya bildirim servisi yok.
- T01 sıradaki uygulamalı hazırlık olarak kaldı; dokümantasyon corpus/adapter testlerinin tamamlandığı anlamına gelmez.
- Doküman kontrolü geçti: 61 Markdown, 348 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri korundu. Sekiz FLOW tanımı ve değişen belgelerin bölüm yapısı ayrıca kontrol edildi. Bunlar runtime, Scrum uygunluğu veya bildirim testi değildir.

### 2026-10-09 — 1C kararı ve alt görev önerisi

- Kullanıcı Q07/1C'yi kabul etti: izinli/erişilebilir geçmişi aktif işlere öncelik vererek aşamalı işleme. 1A/1B seçenekleri ve seçilmeme nedenleri korundu; DEC-15, import, token ve retention belgelerine işlendi. Geçici ham payload için eski 30 gün önerisi 1C kaynak arşivinden ayrıldı; OPEN-08 kesin süre/kapasite kararı açık.
- Q08 için isteğe bağlı alt göreve bölme önizlemesi, parent/child kimliği, AC/kanıt eşlemesi, part_of, atomik onay, iptal ve tamamlama kuralları önerildi. Anlamlı child + küçük adımlarda checklist önerisi henüz varsayılan kullanıcı kararı değil. DEC-16 ve T13d/T20d öneri olarak kaldı; T22b kabul edilen geçmiş davranışının uygulama dilimi.
- Doküman kontrolü geçti: 60 Markdown, 331 yerel bağlantı; mevcut 32 scope, 30 ana görev ve 14 MVP kriteri korundu. Yeni sözleşme senaryoları planlıdır; runtime veya yeni Mermaid render testi yapılmadı.
- Q02/Q03/Q06 ve yeni Q08/Q09 açık; gerçek kaynak aktarımı, ücretli model, çalışan task bölme veya yeni runtime testi yok. T01 sıradaki uygulamalı hazırlık olarak korunuyor.

### 2026-10-09 — Bağlantı, token ve iş bağlamı

- MCP/capture/insan UI ayrımı, bir defalık kurulum, tools-only health, delta brief/resync, disconnect ve sağlayıcı build kapıları ayrıntılandırıldı. OpenAI/Claude resmî kaynakları belge düzeyinde kontrol edildi; gerçek kurulum yapılmadı.
- Host model tüketimi ile kendi arka plan analizimiz ayrıldı. No-op/duplicate bypass, sınırlı context, sürümlü cache, retry/escalation ve atomik bütçe rezervasyonu; bilinmeyen usage ve deferred UI davranışı yazıldı. Fiyat/tasarruf iddiası veya ücretli çağrı yok.
- Kullanıcı Q04 ile güncel işler + seçili iş bağlamını; Q05 ile proje/görev bazlı, sonradan değiştirilebilir analiz profilini seçti. Olgunlaşma hikâyesi, AC/DoD ve test matrisi istendi; task context/acceptance sözleşmesi eklendi. Q06 otomatik Markdown üretimi, Q02 yüzey/OS ve Q03 gerçek veri/bütçe ayrı açık sorular.
- Görev iptali, obsolete ve relationship ended/invalidated ayrıldı; geçmiş bağlantıları silmeyen graph sözlüğü ve üç yeni Mermaid şeması eklendi. AC/DoD başlamadan versiyonlu; completion güncel kanıta bağlı.
- CON/TOK/GUX/CTX kapsamında 30 planlı senaryo ve küçük görev dilimleri eklendi. Doküman kontrolü geçti: 60 Markdown, 319 yerel bağlantı; mevcut 32 scope, 30 ana görev, 14 MVP AC korundu. Runtime, maliyet veya tıklanabilir UI testi yapılmadı. T01 sıradaki uygulamalı hazırlık olarak kaldı.
- İçerik commit'i `451c85bd382114d236245f4d17b89d2333ba5121`: 22 değişen dosya GitHub'dan geri okunup yerel içerikle birebir eşleşti. Üç yeni Mermaid diyagramı GitHub'da render edildi; iptal/karar ilişkileri diyagramı görsel olarak da incelendi. Bu kontrol gerçek graph UI veya model maliyet testi değildir.



### 2026-10-09 — Çok kullanıcı, log ve hafıza planı

- Linear/GitHub/OpenFGA, Cortex/mai-mcp, Letta legacy kavramları ve SQLite/PostgreSQL/OTel birincil belgeleri üzerinden hedefli benchmark hazırlandı; ürünler kurularak IAM veya yük kıyası yapılmadı.
- Workspace/project üyeliği, insan/agent principal, süreli grant, authz revision, private/shared türev bilgi, davet/offboarding ve reviewer policy tasarımı eklendi. İlk bireysel pilot korundu.
- Source/domain/security audit/operational telemetry ayrımı; SQLite başlangıcı, merkezi ekip PostgreSQL adayı, blob/secret sınırı, retention/backup/purge ve sentetik kapasite profilleri belgelendi.
- ADR-0009/0010 önerileri, P1 alt görevleri, P4 C01–C06 ekip dilimleri ve 18 MU kabul senaryosu eklendi. README, AGENTS, scope, roadmap, handoff ve izlenebilirlik bağlandı.
- Doküman kontrolü geçti: 57 Markdown, 264 yerel bağlantı, 32 scope, 30 ana görev, 14 MVP AC; 28 V + 18 MU planlı senaryo. Bunlar runtime test sonucu değildir.
- Ana içerik commit'i `6c659c1367e9618a76efc537fb409a6c2d66796e`: 33 değişen dosya GitHub'dan geri okunup yerel içerikle birebir eşleşti. Repository private olarak tekrar doğrulandı. Dört yeni Mermaid diyagramı GitHub'da render edildi; audit akışı görsel olarak da incelendi. Son incelemede gizli gerekçelerin impact analizinde yanlış obsolete üretmemesi netleştirildi.
- Sayısal retention/SLO/RPO/RTO önerileri ve ekip deployment/reviewer seçenekleri açık karar olarak kaldı. Uygulama ve gerçek veri/ücretli API deneyi yapılmadı. T01 hâlâ sıradaki uygulamalı hazırlık.



### 2026-10-09 — Kullanıcı araştırması ve pilot soruları

- Owner ilk pilotu kendi bireysel kullanımıyla, sonra benzer kullanıcılarla ilerletmeyi seçti. Coding/chat yüzeyleri + hedef OS ve harici API/veri/bütçe sınırı soruldu; henüz cevap gelmedi. Karar durumu [soru kaydında](decision-brief.md).
- Yedi kamuya açık issue/tartışma kaynağı ve iki Linear resmî belgesi incelendi. İki kapalı issue'nun bakımcı düzeltme açıklamaları okundu; tarihsel yakınmalar güncel rakip kusuru olarak sunulmadı.
- [Kullanıcı araştırması](../discovery/user-research.md), şikâyet→hipotez→ürün davranışı→ölçüm zincirini ve ürünü terk ettirebilecek durumları kaydeder. [Benchmark bulguları](../discovery/benchmark-findings.md) belge incelemesi ile runtime deneyi arasındaki sınırı ve doldurulmamış sonuç şablonunu gösterir.
- Linear'ın otomatik taslak kabiliyetleri karşılaştırmaya eklendi; farklılaşma genel AI task üretimi yerine gerekçeli karar etkisi ve yönetim yükü üzerinde netleştirildi. No-op, onboarding ve projeye dönüş ölçümleri mevcut scope'a bağlandı.
- Dokümantasyon kontrolü geçti; runtime benchmark, kullanıcı görüşmesi ve ücretli/gerçek veri deneyi yapılmadı. T01 corpus henüz tamamlanmadı; sıradaki uygulamalı hazırlık olarak kalıyor.

### 2026-10-09 — İkinci kapsam ve mimari incelemesi

- Kaynak konuşmanın 14 evresi ve engine adları tekrar eşleştirildi; 32 scope satırı için kaynak→özellik→engine→görev→kontrol matrisi eklendi.
- 17 kullanıcı özelliği, 10 engine/alias sözlüğü, sekiz mimari diyagram, genişletilmiş roadmap, farklılaşma hipotezleri, LLM handoff ve kısa proje yönetim planı hazırlandı.
- ADR-0007/0008 önerileri; graph snapshot yarışı, durable processing, verifier yetkisi ve etkisiz replay sözleşmeleri eklendi. 30 ana göreve küçük alt dilimler bağlandı; zorunlu test planı V01–V28 oldu.
- Yerel doküman kontrolü geçti: 46 Markdown, 150 yerel bağlantı, 32 scope, 30 ana görev, 14 MVP AC, 17 feature, 10 engine ve 14 kaynak evresi referansları tutarlı.
- Ana içerik commit'i `4b29c19fcb5a9cfef5a25b2de3d790a49a65468f`: değişen 29 dosya GitHub'dan geri okunup yerel içerikle birebir karşılaştırıldı; tamamı eşleşti. Repository private olarak doğrulandı.
- GitHub üzerinde atlasın sekiz ve roadmap'in iki Mermaid diyagramı render edildi; render hata mesajı görülmedi. Sistem bağlamı ve onay yarışı diyagramları görsel olarak da incelendi. Bu kontrol uygulama davranışını doğrulamaz.
- Uygulama geliştirilmedi; engine/adapter/test suite çalıştırılmadı. Bağımsız LLM anlama deneyi yapılmadı. T01 hâlâ sıradaki görev.

İnceleme: [bulgular ve açık kalanlar](../quality/completeness-review.md). Teknik önerilerin eklenmesi onları owner tarafından kabul edilmiş mimari karar yapmaz.

Her görev sonunda görev ID, değişen dosyalar, AC karşılığı, çalıştırılan kontrol ve sonuç, açık engel ve bir sonraki görev buraya veya tarihli delivery kaydına eklenir. ADR statüsü gerçek karar olmadan accepted yapılmaz. Tamamlanma yalnız somut kanıtla kaydedilir. Geçici ilerleme ve branch isimleri AGENTS.md içine yazılmaz.

## Korunacak alanlar

Başka kullanıcı projeleri bu repo için pilot olarak kendiliğinden bağlanmaz/değiştirilmez. Kaynak transcript ve credentials repoya konmaz. Doküman düzenlemesi ürünü çalıştırma, ücretli API kullanma veya public release yetkisi değildir.

## Tasarım revizyonu 03 — güncel durum özeti

**2026-10-11:** [Güncel yön](../product/current-direction.md) ilk karşılaştırma odağını gerçek seçim/artifact/hedef uygulama/devam bağlamı olarak toplar. Tam vizyon ve P1b MVP korunur; projenin iptal edilmesi veya bağımsız build'e geçiş kabul edilmiş değil. Bu tur belgeleme/tutarlılık güncellemesidir, prototip/runtime başlamadı.

76 başlangıç dosyası remote/local eşleşmesiyle tarandı; diagram/şema/ADR/giriş/analiz/delivery etkileri çapraz incelendi. ApplicationTarget/Expectation/Observation/Assessment ve ER-03/ADR-0011, T02d/T03a–c yatırım sırası, GAP JSON oracle ve tek canonical set sürüm düzeni eklendi. Tasarım revizyonu 03 product v3 değildir; v2/v3 kopyaları oluşturulmadı.

Sıradaki **T01**; ardından source/tek target capability ve sınırlı yöntem önerisi. T03b prototype/native deney ancak yetkili kapsamda; T03c sonuç sonrası yatırım kararı. Q02/Q03/Q06/Q08/Q11 ve sayısal/stack/lisans kararları açık. Prototip, native benchmark, gerçek LLM/adapter/DB/UI/migration/test sonucu not_run.

Bu teslimin içerik commit'i `aaf9cbef1c5a387848a6d75975482b9d09ae9e4a`: 42 değişen/yeni dosya aynı ref'ten GitHub üzerinden geri okundu ve local içerikle birebir eşleşti. Doküman kontrolü geçti: 76 Markdown, 658 yerel bağlantı; 32 scope, 30 ana görev, 14 MVP kriteri, 17 feature ve 10 engine korundu. JSON/ID/diyagram inventory kontrolü geçti. Hatalı fixture implemented işareti, yanlış inventory sayısı ve tanımsız GAP ID'si geçici kopyalarda reddedildi.

15 belgedeki 34 Mermaid çıktısının tamamı GitHub Preview üzerinden render edilmiş SVG/etiket düzeyinde kontrol edildi; syntax/render hatası görülmedi. Güncel roadmap ayrıca ekran görüntüsüyle incelendi. Bu kontrol ürünün DB, API, agent, model veya tıklanabilir UI davranışını doğrulamaz. Kontrol kaydı değişiklikleri ayrıca küçük bir doküman commit'inde tutulur; ürün release'i oluşturulmadı.

## 2026-10-11 — Token önlemleri ve sözlük/pattern önerisi

Yedi token önlemi mevcut routing/connection/risk belgelerinde kontrol edildi: batch/delta, structured bypass, revision bağlı cache, kaynaklı özet, parent/dönem bütçesi ve yüksek tüketim onayı mevcut tasarımda var. Uygulama veya tasarruf kanıtı yok.

[Lexical prefilter](../architecture/lexical-prefilter.md) önerisi eklendi: 20 elle hazırlanmış sentetik TR/EN örnek, versiyonlu küçük rule config adayı, guard/actor/target/provenance, structured-first/shadow/unmatched yolu ve üç ekonomik karşılaştırma. T01e/T09e/T24o ve LEX-01–08 planlı; gerçek transcript/model sıklık analizi yapılmadı. Keyword completion, insan approval, shell/write veya doğrulanmış hedef gözlemi üretemez. 10 engine ve 30 ana görev korunur; yeni DB veya kabul edilmiş stack yok.

Bu teslim yalnız dokümantasyon değişikliğidir; mevcut 34 Mermaid kaynak bloğu değiştirilmedi. Sıradaki T01, Q03 gerçek veri/ücretli model kapısı ve mevcut açık owner kararları korunur. Doküman kontrolü geçti: 77 Markdown, 672 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri ve 34 Mermaid inventory korundu. LEX-01–08 tekil/sıralı ve T01e/T09e/T24o referansları ayrıca kontrol edildi. Commit sonrası içerik read-back teslimde ayrıca doğrulanır; LEX senaryoları runtime'da not_run kalır.

## 2026-10-11 — Faz bazlı proje ağacı ve takip

Kullanıcı güncel planın MVP, P2 ve P3 olarak ayrı takip edilip edilmediğini sordu. [Tek faz takip görünümü](phase-tracker.md) eklendi: P0 hazırlık kapısı, MVP için P1a 12 + P1b 9 ana görev, P2 üç ana görev, P3 iki ana görev ve korunan P4 ekip hattı. Her fazın teslim/çıkış kanıtı ve küçük alt iş örnekleri kaynak backlog'a bağlıdır. T03 ana indeks başlığı mevcut native/extend/build detay başlığıyla eşleştirildi; ön koşullar/kapsam değiştirilmedi.

Ana görev ID/faz/durum/başlık/ön koşulları doküman betiğiyle backlog'a eşleştirilir; ikinci bağımsız backlog veya v2/v3 kopyası yaratılmadı. README/roadmap/start-here/backlog bu görünümü işaret eder. Bütün runtime ana görevleri TODO, aday alt dilimler PROPOSED; uygulama, model veya yeni UI testi yok. Mevcut 34 Mermaid kaynak bloğu değiştirilmedi. Sıradaki T01 ve owner karar kapıları korunur.

Teslim kontrolü geçti: 78 Markdown, 693 yerel bağlantı; 30 ana görev satırı faz/durum/başlık/ön koşul düzeyinde backlog ile eşleşti. Geçici kopyada yanlış DONE durumu kontrol tarafından reddedildi; gerçek dosyalarda böyle bir değişiklik yapılmadı. 32 scope/14 MVP kriteri/10 engine ve 34 Mermaid inventory korundu. Bu statik denetim çalışan proje takip uygulaması veya ürün test sonucu değildir.

## 2026-10-11 — Konuşma dili ve İngilizce dışındaki kullanıcılar

Kullanıcı konuşma dilini tespit edip not/proje çıktısını o dilde üretme ihtiyacını ekledi; maliyetli otomasyonun P2'de olabileceğini belirtti. [Dil sözleşmesi](../product/language-and-localization.md), P1 source/Unicode/metadata/açık pilot dili, P2 otomatik tespit/mixed fallback/locale katalogları/cross-language kalite planını önerir. Source/üretim/UI dili ayrıdır; kod/kanıt/ref korunur, eski kayıtlar sessiz çevrilmez. Q12 proje dili değişim önerisi (A) veya session bazlı dil (B) açık; A teknik öneridir, kullanıcı seçimi değil.

T05e/T24p/T25a/T26c ve LANG-01–08 mevcut parent kapsamına bağlandı. Detector/model/library veya yeni DB/engine seçilmedi; gerçek veri/model/translation görevi çalıştırılmadı. Bütün dil desteği veya token tasarrufu ölçülmedi. 30 ana görev/P1b 14 AC korunur; faz takip görünümü P2 dil satırıyla tamamlandı. Mevcut 34 Mermaid kaynak bloğu değiştirilmedi; sıradaki T01 ve Q03 erişim/bütçe kapısı korunur.

Doküman kontrolü geçti: 79 Markdown, 711 yerel bağlantı; 30 ana görev faz/durum/ön koşul görünümüyle eşleşti, 32 scope/14 AC/17 feature/10 engine ve 34 Mermaid inventory korundu. LANG-01–08 tanım/referansları, dört alt görev ve tek Q12 açık soru kaydı kontrol edildi. Detector/model/çeviri/UI deneyi yapılmadı; planlı dil kabulü not_run.

## 2026-10-11 — WrongStack kaynak ve yeniden kullanım incelemesi

Kullanıcı WrongStack'in yararlı açık kaynak parçalarını araştırmayı istedi. [Immutable inceleme](../discovery/wrongstack-review.md), commit `5234c15b05fe18857d0119eabd3b8a8f910ecc66` gerçek MIT LICENSE/manifest, seçili kaynak/test tanımları, memory/verification/MCP/pattern/budget/IPC ve bir DoD UI bileşeni üzerinden hazırlandı. EvidenceValidator, requirement coverage, validity schema ilk küçük reuse adayları; native/extension seçeneği ve semantik uyum farkları kaydedildi. Repo geneli audit, CI veya çalışma testi yapılmadı.

Benchmark/bulgu/farklılaşma/lisans/kaynak/lexical/README ve T03d planı güncellendi; 30 ana görev, 10 engine, MVP ve sıradaki T01 korundu. Kod/prompt/asset/runtime dependency alınmadı, yeni orchestration kararı verilmedi. WS-01–08 not_run; performans/token tasarrufu ve çalışan entegrasyon iddiası yok. Q03 ve stack/lisans karar kapıları açık. Doküman kontrolü geçti: 80 Markdown, 727 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri/17 feature/10 engine ve 34 Mermaid inventory korundu. WS-01–08 sırası ve pinned kaynak yolları ayrıca kontrol edildi. Mermaid kaynakları değiştirilmedi; yeni render/runtime testi yapılmadı. Remote teslim read-back sonucu kullanıcı raporunda ayrıca belirtilecek.

## 2026-10-11 — Q12-A çıktı dili tercihi kabul edildi

Kullanıcı seçili A önerisine “a ile devam et” yanıtını verdi. DEC-20/Q12-A kaydedildi: sabit proje çıktı dili, farklı sohbet dili için öneri, ret/yanıtsız durumda mevcut dili koruma, yetkili insan kabulünde yeni policy revision ve sonraki üretim; eski notları otomatik çevirmeme. B alternatifi/gerekçe/bedel dil ve soru kaydında korundu. Önceki dil keşfi kaydı o zamanki açık durumu anlatır; bu kayıt tercihi kapatır.

Dil sözleşmesi, scope/catalog/domain/roadmap/phase/backlog/verification/traceability ve açık kararlar eşleştirildi; karar haritasının mevcut Mermaid bloğuna DEC-20 eklendi. 30 ana görev/10 engine/MVP/P1-P2 ayrımı ve sıradaki T01 korunur. Detector/LLM/çeviri/UI çalıştırılmadı; LANG senaryoları not_run. Q03/stack/lisans ve diğer owner tercihleri bu yanıtla kapanmaz.
Doküman kontrolü geçti: 80 Markdown, 730 yerel bağlantı; 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 34 Mermaid inventory korundu. Güncel Q12 kayıtları kabul edilmiş A ile eşleşti; eski açık durum yalnız tarihsel keşif kaydında bırakıldı. Mermaid render ve runtime/dil model testleri yapılmadı.

## 2026-10-11 — Q12 örneği, cevapsız sorular ve geç yanıt bağlamı

Kullanıcı Q12-A seçimini gecikmeli vermesini ürünün canlı problemi olarak gösterdi. [Kalıcı soru/geç cevap sözleşmesi](../product/pending-questions-and-late-answers.md), explicit ID/selected source/option snapshot bağını, iki A/B sorusundaki ambiguity'yi, answered/associated/approved/applied ayrımını, timeout/stale/expiry, soru öncesi ingest ve ACL/replay/coverage istisnalarını somutlaştırdı. Q12-A/DEC-20 gerçek seçimi korunur; bu sohbetin işlenmesi Decivora otomatik adapter/test kanıtı değildir.

Approval UX, soru/domain/çoklu chat, verification/traceability ve README bağlandı. Önceki belgelerde referanslanan fakat backlog teslim satırı bulunmayan T13e/T18e/T24f eksikliği giderildi. LATE-01–08 planlı; yeni engine/ana görev, reminder servisi, ücret veya erişim kararı yok. Hatırlatma kanalı/sıklığı açık; uygulama içi pending/brief önerisi ve bağımsız iş ilerlemesi korunur. Sıradaki T01; runtime/parser/LLM/host/UI sonuçları not_run.

Doküman kontrolü geçti: 81 Markdown, 746 yerel bağlantı; 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 34 Mermaid inventory korundu. Sekiz LATE kabul ID'si ve üç soru alt dilimi ayrıca kontrol edildi. Mevcut Mermaid kaynakları değişmedi; runtime veya render testi yapılmadı.

## 2026-10-11 — Ürün değerlendirme vakası ve repo geneli kod adayları

Kullanıcı README'ye yazmadan ürün değerlendirme/mindset anlatısı ve bütün upstream kod alanlarında somut kullanım önerisi istedi. Ayrı [portföy vaka çalışması](../portfolio/product-evaluation-case-study.md), owner/AI katkısı, problem evrimi, gerçek karar/alternatif/bedel, güçlü taraflar ve eksik kanıtları toplar. Çalışan ürün/üstünlük/gelir/token tasarrufu iddiası yok; private repo ve yayın izni değişmedi. README değiştirilmedi.

[Kod/teknoloji değerlendirmesi](../discovery/code-reuse-assessment.md) sabit upstream ref'te 39 manifest ve 9.657 kod dosyasının yapısal envanterini; R01–24 kaynak/hedef/uyarlama/kabul adaylarını ve paket kapanışını sunar. 2.203.270 satır test/fixture/declaration/yorum dahil; bütün satırların semantik denetimi değildir. Yeni governance append-only event/receipt/verifier/grant ve Kanban contract graph/core decision/rationale bulguları önceki hedefli benchmark'ı genişletti; eski ref-only/soft-gate bulguları bütün platforma genellenmedi. Tam source, upstream script/install veya runtime dependency alınmadı.

Benchmark/farklılaşma/lisans/kaynak/handoff ve öneri T03d WS-R2/3 kapsamı güncellendi. Q13 A/B/C somut araştırma seçenekleri açık; owner seçimi yok. T01 sırası, 30 ana görev TODO, 10 engine, tam vizyon ve MVP korunur; nihai stack/alıma geçiş/gerçek veri/ücret kararı verilmedi.

Doküman kontrolü geçti: 83 Markdown, 791 yerel bağlantı; 32 scope/30 ana görev/14 MVP AC ve 34 mevcut Mermaid inventory korundu. Envanter betiği yalnız kaynak okuyup metadata üretti; upstream kod/test/model/agent çalıştırılmadı. Yeni Mermaid bloğu yok; render/runtime/native benchmark sonucu not_run. Envanter tekrarında CSV/JSON birebir aynı çıktı; 39 manifest alanı, 35 paket ve R01–24 eşleşti. İndekslenen 9.657 kod dosyası immutable Git tree blob hashleriyle birebir eşleşti. Kaynak kimliği/yapısal kontrol davranış testi değildir; remote commit/read-back teslimde doğrulanır.

## 2026-10-11 — Ekosistem araştırma görevi ve ilk tarama

Kullanıcı WrongStack dışında projelerden de yararlanmak istedi. [T03e araştırma kartı](../discovery/ecosystem-research.md), 10 immutable aday/root lisans, beş seçili source incelemesi ve [makine okunur kayıt](../discovery/ecosystem-candidates.json) hazırlandı. ER-R1 masa başı belge çıktısı mevcut; ER-R2–4 derin closure/deney/owner önerisi TODO. Graphiti, LangGraph, LiteLLM ilk derin inceleme adayları; OpenFGA/Cedar ekip modeli, Temporal distributed ihtiyaç kapısında.

Benchmark/farklılaşma/lisans ve devir belgeleri karşı kanıtla genişletildi. Source D/S, runtime V değil; ER-T1–5, accuracy/token/latency sonuçları not_run/null. Yeni dependency, kaynak kod kopyası, install, paid bağlantı veya mimari kabulü yok. Q13, 30 ana görev, T01 sonraki iş ve README korunur. Doküman kontrolü geçti: 84 Markdown, 817 yerel bağlantı; 32 scope/30 ana görev/14 MVP kriteri/17 feature/10 engine ve 34 Mermaid kaynak bloğu korundu. Pinned kaynak kayıtları ayrıca kontrol edildi; runtime veya diyagram render testi yapılmadı. Commit sonrası hedeften içerik doğrulaması ayrı teslim kontrolüdür.

## 2026-10-11 — Teknik ölçüm protokolü ve hedefli evaluator incelemesi

Kullanıcı karar→etki→gerçekleşme farkının teknik olarak nasıl ölçüleceğini sordu. [Protokol](../quality/evaluation-protocol.md), bağımsız frozen oracle, one-to-one entity/span matching, checkpoint/action/path scoring, exact target binding, stage telemetry, quality/cost/coverage ve incomplete gate'i ayrıntılandırdı. [CHAIN-01 taslağı](../../examples/decision-impact-evaluation-case.json) yedi checkpoint/dört negatif varyant; illustrative/not_run, T01 corpus/holdout veya uygulama değil. T01f/T03f/T24p TODO; T01 ana sıra ve Q03/Q13 korunur.

Graphiti evaluator/judge ve ayrı Langfuse Python SDK experiment/test/license hedefli okundu. Source örneğinin kendi gold/verdict/error bağını denetleme ihtiyacı kaydedildi; bütün source audit'i, upstream test başarısızlığı veya runtime üstünlük iddiası yok. Yeni dependency, model çağrısı, paid telemetry, mimari karar ve kod kopyası yok. Doküman kontrolü geçti: 85 Markdown/833 yerel bağlantı; 32 scope, 30 ana görev, 14 MVP kriteri, 17 feature, 10 engine ve 34 Mermaid kaynak bloğu korundu. CHAIN-01 ID/ref, not_run/null ve mock sınırları veri kontrolünde doğrulandı; scorer/ürün runtime testi veya Mermaid render yapılmadı. Ölçüm harness'i uygulanmadı.

## 2026-10-11 — Teknik boşluk analizi, sözleşme ayrıntıları ve görev kimliği düzeltmesi

Kullanıcı bütün akıştaki boşlukları ve neden neyi incelediğimizi kalıcı belgelememizi istedi. [TG-01–24 analiz kaydı](../quality/technical-gap-analysis.md) başlangıç ref/yöntem/kanıt sınırı, iki somut doc conflict, teknik ayrıntı önerileri, implementasyon/capability/owner/ölçüm açıkları, first-use G0–G6 kapıları ve adım adım soru kuyruğunu tutar. [IC-01–08](../architecture/implementation-contracts.md) strict wire/source span, canonical digest, exact budget/period, target consistency, empty AC/projection freshness ve transport/recovery/test raporu ayrıntılarını önerir. Accepted ADR, code/DB/API veya yeni dependency değildir.

**Düzeltme geçmişi:** önceki ölçüm güncellemesinde T24p zaten dil görevi için tanımlıyken ikinci kez ölçüme verilmişti; ölçüm **T24q**, dil **T24p** olarak ayrıldı. Önceki status kaydı o anki teslimi anlatır ve korunur. Güncel ölçüm referansları düzeltildi; checker canonical subtask definition tekrarını da reddeder. Event/runtime source key scope/epoch tarifi DB ilişkileriyle hizalandı; runtime dedup uygulanmadı.

Q02-R1 ilk pilot kaynak yolu A/B/C cevap bekler; öneri A kullanıcı seçimi değildir. Q03/Q06/Q08/Q11/Q13 ve OPEN policy/stack/permission kapıları korunur. İlk T01 ve 30 ana görev TODO; 32 scope/17 feature/10 engine/14 MVP AC ve 34 mevcut Mermaid bloğu değişmedi. README ve başka projeler değiştirilmedi. Runtime, model, gerçek adapter/target, load/restore/UI veya security testleri not_run. Doküman teslimi ve checker negatif testi ayrıca doğrulanır.

Teslim kontrolü: doküman betiği geçti; 87 Markdown/893 yerel bağlantı, 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 34 Mermaid/15 belge inventory korundu. Ayrı geçici repo kopyasına T24p duplicate definition enjekte edildi; checker beklenen hata ile reddetti, asıl repo değiştirilmedi. 24 tekil TG kaydı/8 IC bölümü ve dil T24p→T25a bağı ayrıca kontrol edildi. Bunlar doc/checker kanıtı; ürün conformance sonuçları not_run. Remote commit/read-back ayrıca teslimde doğrulanır.

## 2026-10-11 — Bütün Mermaid'lerin görsel ve içerik incelemesi

Kullanıcı çalışma aşamasını ve README dahil tüm Mermaid'lerin güncel/eksiksiz incelenmesini, anlamlı renk/label ve daha iyi belge sunumunu istedi. **Aşama hâlâ keşif, ürün tanımı ve teknik tasarım**; uygulama/pilot/build/stack seçimi yapılmadı. 24 TG bulgusu dokümantasyon/implementation/deney/owner ayrımıyla geçerli; render bunları runtime düzeyinde kapatmaz.

34 önceki şemanın tamamı semantik karşılaştırma ve görsel güncellemeye alındı. Karar haritasında eksik DEC-10–14 görselleştirildi; kabul edilmiş niyet ve teknik öneriler iki görünüm oldu. Yeni toplam **35 Mermaid / 15 belge**; 23 flowchart, 4 ER, 7 sequence, 1 state. Ortak renkler, metin etiketi, accTitle/accDescr, numaralı sequence/açıklama bandı eklendi. Atlas budget kontrolü/late answer association/source key, callback receipt ve outbox worker çizimi netleştirildi.

README aşama tablosu/kısa rol girişleri/açılır tam indeks ve üretilmiş SVG fallback kazandı; dosyalar taşınmadı. [Görsel sözlük](../quality/visual-documentation.md) iki pinned upstream README/tree incelemesinden alınan sunum örüntülerini ve sınırını tutar. Asset/logo/kod kopyası, runtime dependency veya public/license kararı yok.

Ağ kapalı yerel Mermaid 11.17.2/Chrome render: **35/35 başarı, 0 son parser hatası**; bütün SVG'lerde accessible title/description. 35 görüntü contact sheet'te, dört temsilci ayrıca tam görüntüde incelendi. İlk başarısız ayırıcı denemeleri [inceleme kaydında](../quality/diagram-review.md) korunur; [JSON raporu](../quality/diagram-render-results.json) source ve SVG hashlerini taşır. Checker live render yapmaz; kayıt/current source uyumunu kontrol eder. GitHub dark/mobil/renderer uyumu ve gerçek ürün UI/erişilebilirlik/runtime testleri bu local kontrolle kanıtlanmış değildir. Q02-R1 ilk soru pending; Q03 ve diğer açık owner kararları korunur. Remote teslim ayrıca read-back ile doğrulanır.

Teslim kontrolü geçti: 88 Markdown/931 yerel bağlantı, 32 scope/30 ana görev/14 MVP AC/17 feature/10 engine ve 35 Mermaid/15 belge inventory. Geçici kopyada Mermaid kaynağı değiştirilince stale render hash, SVG değiştirilince stale fallback hash kontrolü beklenen şekilde reddetti; asıl dosyalar değiştirilmedi. Local yayın metinleri 22 hedef dosyayla birebir karşılaştırıldı. Bunlar doküman/render kanıtıdır; uygulama testleri not_run kalır.


## 2026-10-11 — Q02-R1: maliyet odağıyla A önce, Codex B sonra

Kullanıcı ilk pilot için **A açık aktarım + tek read-only hedef** yolunu seçti; **B Codex coding oturumu + tek repo** sonrasında görülmek isteniyor. C Claude Code-first alternatifi korunur, seçilmedi. Gerekçe başlangıçtaki otomatik capture/kurulum bağımlılığını azaltıp seçim→gerçek uygulama değerini önce sınamak. Maliyet üstünlüğü ölçülmedi; manuel aktarım serbest metin çıkarımını ücretsiz yapmaz. [Seçenekler, kaynak ve gerekçe](decision-brief.md) kabul kaydıdır.

README, başlangıç/devir, teknik gap soru kuyruğu, bağlantı sözleşmesi ve Spike-1 bu sıraya hizalandı. B için MCP hedefli bağlam/öneri araçları ile ayrıca host/build deneyi gerektiren otomatik capture ayrıldı; `tools_only` tam transcript/subagent coverage sayılmaz. Q02'nin somut kaynak/hedef/host/OS ayrıntıları ve Q03 veri/provider/bütçe açık. Sonraki öneri ek ücretli model API'si olmadan sentetik/elle etiketli fixture + deterministik kontrol; henüz Q03 owner yanıtı değil.

Pilot, runtime, gerçek hedef taraması, host/MCP kurulumu veya model deneyi yapılmadı. T01 ve ana backlog TODO; yatırım/stack kararı açık. Bu tur hiçbir Mermaid kaynak bloğu veya SVG değişmedi; önceki render kanıtını yeni render yapılmış gibi sunma. Teslim doğrulaması doküman tutarlılığı, değişmeyen diagram source/fallback hashleri ve remote içerik read-back'i ile yapılır.


## 2026-10-11 — Q03-R1 A: ilk deney ek ücretli model API'si olmadan

Kullanıcı, “İlk deneyde ek ücretli model API'si kullanalım mı?” sorusuna **A** yanıtını verdi. İlk dilim örnek/elle etiketli kayıtlar ve deterministik kod kontrolleriyle ilerler; otomatik serbest metin extraction ve native/fresh-session model değerlendirmesi sonraki ayrı deneydir. B alternatifi korunur, seçilmedi. [Karar/gerekçe](decision-brief.md#q03-r1--ilk-deneyde-ek-ücretli-model-apisi) Q03'ün ilk-deney kısmını kapatır; sonraki gerçek veri/provider/bütçe açık kalır.

README, karar brief'i, başlangıç, LLM devir, teknik gap kuyruğu ve Spike-1 aynı kabul durumuna hizalandı. Spike-1 no-model dilimin kabul sınırı, model sonuçlarının `not_run` kalması ve ölçülmeyen maliyetin sıfır diye gösterilmemesini açıklar. Bu seçim kalıcı LLM yasağı veya gerçek kaynak/target erişim izni değildir. T01/ana backlog TODO; runtime, corpus deneyi, gerçek model/API/capture/target/UI testi bu tur yapılmadı. İlk kaynak A → sonraki Codex B sırası korunur.

Mermaid/SVG kaynakları değişmedi; mevcut render hash kayıtları korunur. Teslim kontrolü doküman/link/inventory ve remote metin read-back ile yapılır; yeni runtime/render testi iddiası yok.


## 2026-10-11 — Düzeltme: otomatik anlam çıkarımı isteğe bağlı değildir

Kullanıcı Q03-R1 B ifadesinin otomatik anlam çıkarımını uygulanmayabilecek seçenek gibi göstermesine itiraz etti. **Güncel açıklama:** A yalnız ilk fixture/code kontrolünü ek ücretli model API'si olmadan başlatma sırasıdır. Otomatik serbest metin anlam çıkarımını uygulamak ve gerçek extractor çıktısını bağımsız holdout ile test etmek gerekli ürün işidir. B yalnız bu deneyi ilk dilimde de başlatma alternatifiydi; özelliğin kendisi reddedilmedi. Önceki soru sunumu bu ayrımı yeterince açık kurmadı; geçmiş status kayıtları korunur, bu kayıt yorumunu düzeltir.

Karar brief'i, Spike-1, MVP, T09/T24 backlog kabulü, README ve başlangıç/devir/gap kuyruğu hizalandı. T01/T01f/T03f hazırlığı → T09 uygulama → T24/T24q semantik ölçüm zinciri mevcut görevlerle açıklandı; yeni ana task/engine/AC, stack veya ücret seçimi yok. Model/veri/bütçe ve gerçek hedef izinleri ilgili deneyin yürütme önkoşuludur, özelliği yapıp yapmama oylaması değildir. LLM judge opsiyonel değerlendirme desteği olarak kalır.

Yalnız typed fixture/code pass otomatik extraction veya P1b MVP doğrulaması değildir; çalıştırılmayan gerçek semantik test `not_run` ve ilgili blocker ile görünür kalır. T01 ve ana işler TODO; gerçek extractor/model/API/host/corpus deneyi bu tur yapılmadı. Mermaid/SVG kaynakları değişmedi; doküman/link/inventory ve remote read-back teslim kontrolü uygulanır.


## 2026-10-11 — T01 ilk somut corpus hazırlığı

Kullanıcı etiketli örnekleri hazırlamamızı ve zorunlu işleri yapılmayabilecek seçenek gibi sunmamamızı istedi. Kalıcı çalışma kuralı AGENTS.md'de yöntem/sıra tercihi ile gerekli iş ayrımına işlendi; MVP ve tam kapsam/fazlar korundu. Q03-R1 A ilk no-model dilimi, otomatik extraction uygulama/testi zorunlu sonraki adımdır.

[Corpus](../../examples/corpus/README.md): 2 sentetik proje/6 oturum, 58 mesaj, 66 kayıt annotation'ı ve 46 farklı KnowledgeRecord kimliği. 51 anlamlı mesaj ve 7 no-new-record örneği. Storage evolution/new-chat late answer, aynı adlı proje/ambiguous A/ret, multi-agent authority/bütçe ve release option/target/AC/stale aileleri. Belirsiz A cevabı AnswerRecord olarak tutuldu, yeni PendingDecision oluşturulmaz; farklı KnowledgeRecord sayısı son semantik düzeltmede 47'den 46'ya indi. 4 oturum geliştirme, 2 aynı aileli oturum ayrılan değerlendirme; source/oracle ayrı. Etiketler bu AI çalışmasında hazırlandı; insan gold incelemesi pending. Seti yazan model ayrılan seti gördü; sealed/blind holdout iddiası yok.

[Baseline hazırlığı](../quality/baseline.md) kritik checkpoint, MVP/P2/P3/P4 temsil/kalan kanıt, T01 alt teslim ve insan review listesini tutar. İlk semantik incelemede staging hedefi→canary stratejisi için kaynaksız supersedes edge çıkarıldı; veri kontrolünde dört boş expected assertion tamamlandı. Bunlar corpus düzeltmesidir; çalışan üründe hata/başarı sonucu değil.

`check_corpus.py --self-test` veri/hash/exact Unicode span/split/referans/minimum kayıt kontrolünü geçti; 11 mutant beklenen şekilde reddedildi. [JSON kontrol raporu](../quality/corpus-preparation-results.json) validator/manifest hashlerini ve product_result=not_run sınırını taşır. Validator extractor/scorer/harness değildir; gerçek precision/recall, token tasarrufu, replay, target read ve UI testi yapılmadı. Ek ücretli model/provider çağrısı başlatılmadı.

T01 IN_PROGRESS ve diğer 29 ana görev TODO; canonical backlog/phase tracker eşleştirildi. İnsan incelemesi, T01e/T01f ve daha geniş FLOW/authority/crash/protokol hazırlığı kapanmadan T01 complete sayılmaz. Görsel Mermaid/SVG kaynakları değişmedi; yeni ürün diagram/render testi iddiası yok. Remote commit/read-back teslimde ayrıca doğrulanır.

## 2026-10-11 — Q02-R2 A ve tek gerçek hedef gözlemi

Kullanıcı mevcut private repo dokümanını ilk read-back hedefi seçti. Asistan önceki corpus rehberini seçip değiştirmeden `6de536e44b22d6f839aa7c94e3ca2444addb5115` ref'inde okudu; yerel artifact ile GitHub içeriği/SHA-256/Git blob kimliği eşleşti. [READBACK-01 raporu](../quality/first-target-readback.md) ve [JSON gözlem](../quality/first-target-readback.json) scope, revision ve not_run ayrımlarını tutar.

Bu manuel happy-path, yüklenmiş tek dosyanın somut kanıtıdır; Decivora target adapter'ı, semantik kalite, coding capture, bütün corpus bundle'ı veya task DoD kanıtı değildir. T02d kısmi manuel kanıt aldı; ana durumlar **T01 IN_PROGRESS, diğer 29 TODO**. İnsan etiket review'u ve kalan T01 protokolü sıradadır; otomatik extraction uygulaması/testi zorunlu kalır. Ek ücretli model/provider deneyi yok; host token kullanımının ölçümü yok. GitHub hedef sorusu tekrar sorulmaz; B yerel hedef senaryosu ve sonraki Codex bağlantı testi korunur.


## 2026-10-11 — Audit önerileri ve çalışan P0 düzeltmeleri

Kullanıcı raporların private GitHub’a alınmasını, Spike-0 önerilerini ve dört devam maddesini uygulamayı istedi. [Güncel bulgu/düzeltme matrisi](../quality/audit-remediation.md) tarihsel audit ve source review’u ayırır. Kullanıcı ZIP’inden capture ölçüm kodu alındı; 8 regression eklendi. Source kimliği, tam içerik ölçümü, kısa claim/answer, cap görünürlüğü, fuzzy conflict, durable receipt ve bounded catch-up uygulandı. Gerçek projeye kurulum/host/model çağrısı yok.

63 test (40 Spike-0 + 15 typed chain + 8 scorer/anchor) geçti; kaynak/scorer-only lexical corpus koşusu zayıf çıktı ve başarısızlıklar saklandı. Typed karar→impact→target→AC→backup/replay zinciri geçti; bu IAM, gerçek semantik extraction veya production backup değildir. T07c erken restore teslimi, T15 kapanış bağımlılığı; T23a kapsamlı operasyon restore olarak ayrıldı. CI tanımı ve explicit Türkçe anchors eklendi.

T01/T02/T03 **IN_PROGRESS**, diğer 27 ana görev TODO; hiçbir ana görev tamamlanmadı. [Üç insan review örneği](../quality/human-review-queue.md), zorunlu semantik model koşulları ve [native/dosya/devam paketi kıyası](../quality/pilot-comparison-plan.md) sıradadır. Eski tarihsel “kod/scorer/CI yok” kayıtları kendi snapshot’ına aittir. Mevcut 35 Mermaid source/SVG hashleri korunur; yeni render/UI testi iddiası yok. Yayın/remote read-back kanıtı teslim sırasında ayrıca doğrulanır.


## 2026-10-11 — İnsan incelemesini beklemeyen semantik bağlantı kodu

Kullanıcı bağımsız işleri tamamlamamızı istedi. Source-only request hazırlığı (6 session/58 mesaj), hash/version/proje bağlama, strict output schema/Unicode span/limit/duplicate/abstention, ayrı selection makbuzu ve mevcut chain’e AnswerRecord bridge, imported response evaluator ve yedi kritik checkpoint scorer uygulandı. [Kod ve komutlar](../../spikes/semantic-chain/README.md); [hazırlık matrisi](implementation-readiness.md).

28 yeni test, scripted reply ve bu asistanın 12 adaylı S02 yorum taslağını import eden kontrollü zincir sınanır. Beklenti dosyası current projector’dan üretilmez; human gold pending. Taslak prior oracle exposed/non-blind, API/model dispatcher yok; semantik kalite veya genel doğruluk kanıtı değildir. Eksik 5 session output’u incomplete; canonical mutations model/parse aşamasında 0. Gerçek target/auth/host/API hâlâ not_run; model/provider/usage null. Mevcut fixture yöntem ve sınırlar somutlaştırıldı; P0 kod hazırlığı human review veya future faz kararlarını beklemez.

Ana durumlar T01/T02/T03 IN_PROGRESS, diğer 27 TODO. [Sonuç kaydı](../quality/semantic-readiness-results.json) güncel test kapsamını önceki 63-test audit paketinden ayırır. Production stack/T03c, gerçek provider/veri/bütçe, insan gold ve native kıyas kapıları açık; zorunlu extraction görevi korunur. Var olan Mermaid/SVG kaynakları değiştirilmedi.


Ek aynı-tur gözlem: [seçili corpus README için gerçek GitHub readback](../quality/semantic-target-readback.json), iki immutable ref, aynı blob; eski ref stale/seçili ref observed_match. Scope/hash kontrol kodu ve dört negatif/pozitif test eklendi. Task verification veya production target adapter iddiası yok.

## Current concurrent storage and manual impact UI —14October2026

[Working delivery and limitations](../quality/concurrency-impact-delivery.md): startupWAL, read-snapshot-only audit grouping,318runtime/48tracker/7browser, identical mixed-fixture improvement and controlled503mechanism regression. Questions/decisions now offers human-selected durable decision-impact hypothesis; no task cancellation/decision mutation, missing rationale review. Full model/host/source-aware approval/application and release checks remain open.

## 2026-10-14 — WAL recovery and populated impact load

319 runtime regressions passed, including uncheckpointed WAL backup→offline restore/event/projection preservation. The mixed-load harness now accepts bounded `--impact-previews` fixtures and checks latest-five history, stale-after-write, unchanged projection and no false Done. [Current findings and checks](../quality/concurrency-impact-delivery.md#follow-up-wal-recovery-and-populated-impact-history). No new model/root/host permissions; previous 7 browser/48 tracker results remain historical. Main task closure unchanged.

## 18 Ekim 2026 — teyit edilen repo bulguları giderildi

[Altı bulgu ve aksiyon](../quality/review-remediation-2026-10-18.md): effective prerequisite completion, kalıcı overrun/workspace freeze, source/model/output-cap bağlı dispatch grant+budget settlement, partial coverage UX, CI browser/render job ve güncel README_LOCAL.330runtime test;44Mermaid yeniden render. Gerçek model/para/context/policy/host/release kapıları açık; ana task sayımı değişmedi.

## 18 Ekim 2026 — diyalogdan mevcut görev durumuna çalışan dilim

[Dialogue status runtime](../quality/dialogue-status-runtime.md): kullanıcı mevcut LLM'den yapılandırılmış yanıt aktarabilir; aynı schema configured Responses adapter'da da desteklenir. Yeni görev + mevcut task status claim ayrı öneridir; insan kabul/ret/ertelemesi kalıcıdır. Apply kaynak/task/workflow/ilişkili context güncelliğini ve ortak AC/blocker/verification kurallarını kontrol eder. Modeller ve capture varsayılan kapalı; gerçek anlam doğruluğu veya MVP kabulü tamamlanmadı. Ana görev sayımı değiştirilmedi.

## 18 Ekim 2026 — ana ürün yolculuğu yeniden denetlendi

[Ana akış denetimi](../quality/primary-flow-audit.md): source/schema/fixture başarıları otomatik ürün kabulü değildir. Native capture, gerçek çıkarım, kaynaklı semantik ilişki/karar etki köprüleri, impact UI apply ve izinli next-agent context kritik açık bağlantılar. Tekrarlanabilir probe3canonical kayıt→0ilişki,1PendingDecision→0QuestionRequest,UIimpact→review/unknown,MCPprivate→0record üretti. Bu tur model context'ine karar/soru/ilişki snapshot'ı eklendi; cached analyze readback en yeni sürüme düzeltildi. Ana task durumu değiştirilmedi.

## 18 Ekim — Q08-A ve Q06-A açık kullanıcı cevabıyla kabul edildi

Exact cevap “1A / 2A”: anlamlı ana/alt görev planı + checklist + tek inceleme/onay; önemli karar değişimi/ana görev kapanışında kaynaklı yerel Markdown snapshot. T13d/T20d PROPOSED→TODO; T20c snapshot geliştirmesi açık. DB/event log esas, dosya türev; uygulama/ücret/egress/GitHub push yetkisi değildir. Ana işler7/14/9 aynı; iki eski karar beklemesi kaldırıldı.

## 18 Ekim — impact→task scope update kullanıcı akışı kodlandı

T13/T19: etki kartında görev description düzenle, review hazırla, grup seç, ayrı onayla ve uygula; ret/erteleme kalıcı. Prepare/select/approve görevi değiştirmez; Apply atomic yeni version oluşturur. Manual source receipt değişimi eski impact approval'ını invalid eder. [Teslim kaydı](../quality/workflow-ui-runtime.md#18-ekim--etki-kartından-görev-değişikliğini-uygulama). Otomatik semantic proposal/AND-OR authoring/cancel/native açık; ana task Done yapılmadı.

### 19 Ekim — API-bağımsız lifecycle UI

T13/T19/T20: task→Decision gerekçe ilişkisinin açık onayı, tek karar gerekçeli retirement/restoration impact girdisi, ayrı lifecycle select→approve→apply ve iptal/yeniden açma geçmişi kullanıcı arayüzüne bağlandı. Ana görevler kendi tam kabulüyle açık kalır; gerçek model/host/target kapıları kapanmadı. [Kod, sınırlar ve doğrulama](../quality/workflow-ui-runtime.md#19-ekim--gerekçeli-iptal-ve-yeniden-açma-arayüzü).

### 19 Ekim — T20/T21/T23/T24 Operations alt teslimi

Operations okuma ekranı, ayrı kalıcı safe diagnostic sidecar, command boundary spans/operation-ID, test ortamı başlatıcısı ve normal/test cookie ayrımı kodlandı. Canonical audit, üretim retention, incident yönetimi ve end-to-end trace kabulü ayrı; parent görevler kapatılmadı. [Kod kapsamı ve doğrulama](../quality/operations-runtime.md).

### 19 Ekim — log kimliği ve ekip kapısı

Yeni LocalApp izleri trusted preflight actor/workspace/authority revision taşır; eski izler null kimlikte korunur. Operations görünümü, SQL/JSON ve ER/sequence açıklaması birlikte güncellendi.387runtime/48root/11browser geçti;50diagram render edildi. LOCAL/TEST yeniden açıldı ve eski veriler korundu. Ekip login, loga özel yetki ve tenant izolasyonu tamamlanmadan ortak erişim açılmaz. Parent sayıları değişmez. [Kapsam ve kanıt](../quality/operations-runtime.md#yerel-actor-attribution--19-ekim2026).

### 19 Ekim — T09/T10/T13/T19/T22 geç cevap köprüsü

Konuşma/model response → kaynaklı exact soru/sürüm/seçenek önerisi → insan kabul/ret/erteleme → atomik soru cevap kaydı kodlandı. Karar ve task uygulaması ayrı kalır. Eski status-only çıktılar korunur. [Uygulama ve sınırlar](../quality/dialogue-status-runtime.md#19-ekim--kaynaklı-geç-cevap-önerisi). Parent durumları ve model/native kalite kapıları açık; yeni ana görev oluşturulmadı.

### 19 Ekim — T09/T10/T11/T13/T19 ilişki önerisi köprüsü

Konuşma çıktısında mevcut kayıtlara source-bound required_by/depends_on önerisi, ayrı human review, atomik graph apply ve karar emekliliği için açık impact hypothesis bağlantısı kodlandı. [Sözleşme ve sınırlar](../quality/dialogue-status-runtime.md#19-ekim--kaynaklı-ilişki-önerisinden-etki-incelemesine). AND/OR, otomatik decision supersession ve gerçek semantic/native kapıları açık; mevcut parent statüleri korunur, yeni ana iş yok.

### 19 Ekim — T06/T09/T18/T22/T23 credential koruması

Yeni manuel konuşmada pre-storage redaction, sanitized-source hash/quote, provider/import/context/MCP guard, HTTP display maskesi ve POSIX DB/sidecar izinleri kodlandı. Log gövdesi tutulmaz. Geçmiş DB/yedek purge veya encryption yapılmadı; mevcut lifecycle/release kapıları açık. [Kapsam ve sınırlar](../quality/credential-redaction-runtime.md). Parent durumları değişmez.

### 19 Ekim — T09/T10/T11/T13/T19 karar replacement

Source-bound Decision NEW supersedes OLD önerisi, onay öncesi/sonrası impact önizlemesi, ayrı insan onayıyla atomik lineage kaydı kodlandı. Conflicting replacement/stale endpoint/cycle guard'ları ve tarihsel Done korunarak current verification invalidation doğrulanır. [Kapsam](../quality/dialogue-status-runtime.md#19-ekim--konuşmadan-kararın-yerini-alan-seçim). Genel validity/AND-OR, semantic/native kabulü ve parent görevler açık; yeni ana task yok.

### 19 Ekim — T11/T12/T13/T19/T20 kalıcı AND/OR

Human-confirmed versioned rationale/facts, eksiksiz known-edge kapsamı, task editor, prepared context ve impact bağlantısı kodlandı. Unknown/conflicting/stale facts otomatik false sayılmaz; eski tek-karar override'ı stale ifadeyi geçemez. [Kapsam](../quality/dialogue-status-runtime.md#19-ekim--kalıcı-andor-gerekçesi-ve-etki-bağlantısı). Parent/semantic/native release kapıları açık; ücretli çağrı yok.

# Decivora workflow benchmark ve değişiklik önerisi

**14 Ekim 2026 — Kullanıcı workflow + UI/UX yönünü açıkça onayladı.** Jira, Linear, ClickUp ve Asana: dört ürünün resmî belgeleri incelendi. Çalışan ürün, canonical analiz dokümanları, kod, veritabanı, ZIP veya GitHub bu araştırma kapsamında değiştirilmedi. Bu dosya kabulün gerekçesini ve araştırma kapsamını korur. Aşağıdaki uygulama sınırı öneri ile çalışan dilimi ayırır. İlk araştırma sırasında ürün/GitHub değiştirilmemişti; onaydan sonra ilgili dilimler uygulandı.

## 1. Araştırma kapsamı ve kanıt sınırı

Kriterler: ilerleme aşaması, aday/aktif görev ayrımı, blocked/blocks, insan onayı, uygulandı/doğrulandı ayrımı, iptal/duplicate/obsolete, yeniden açma, geçmiş ve admin konfigürasyonu. Çalışan Decivora kodu ile doküman planı ayrı kontrol edildi. Rakip hesaplarına giriş, ücretli plan veya runtime testi yapılmadı. Özelleştirilebilir ürünlerde bütün müşteri konfigürasyonlarını listeleyen tek bir “tüm statüler” listesi yoktur; resmî varsayılanlar, kategoriler, belgelenmiş örnekler ve ilişkiler incelendi. Statü, kategori, board sütunu, priority, resolution ve approval sonucu birbirine eşit değildir.

Aşağıdaki belgeler hedefli okundu: product/mvp, full-scope, priority-and-flow, approval-ux, pending-questions-and-late-answers, task-context-and-acceptance; architecture/task-lifecycle, local-preview, reconciliation-impact, multi-chat-and-processing-lag, data-relationships; quality/verification; delivery/backlog ve discovery/benchmark/benchmark-findings. Kod: local_ui/server, acceptance, task_blockers, task_lifecycle, impact/graph, storage/workspace. Tüm repo için yeni güvenlik/performans audit'i yapılmadı.

## 2. Dört ürünün statü envanteri

### Jira

Ürüne/template'e bağlı resmî etiketler:

- Genel: Open, In Progress, Done, To Do, In Review, Under review, Approved, Cancelled, Rejected, Draft, Published, Second Review.
- Diğer iş türleri: Interviewing, Interview Debrief, Screening, Offer Discussions, Accepted, Applications, Lost, Won, Contacted, Opportunity, In Negotiation, Purchased, Requested.
- Yazılım: Reopened, Resolved, Closed, Building, Build broken, Backlog, Selected for Development.
- Service Management: Declined, Waiting for support, Waiting for customer, Pending, Canceled, Escalated, Waiting for approval, Awaiting CAB approval, Planning, Awaiting implementation, Implementing, Peer review / change manager approval, Work in progress, Completed, Under investigation.

Bunlar aynı projeye zorunlu bir akış değildir. Üç üst kategori: To do/In progress/Done. Resolution ayrı alan; örneğin Duplicate. Flagged/Impediment engel işaretidir. Bizde bütün Jira etiketleri gerekli değil; yaşam döngüsü/çözüm ayrımı yararlı. Kaynaklar: [statü envanteri](https://support.atlassian.com/jira-cloud-administration/docs/what-are-issue-statuses-priorities-and-resolutions/), [kategoriler](https://support.atlassian.com/jira-cloud-administration/docs/what-is-a-workflow-status/), [flag](https://support.atlassian.com/jira-software-cloud/docs/flag-an-issue/).

### Linear

Varsayılan: Backlog → Todo → In Progress → Done → Canceled. Duplicate sistem durumu; Triage ek intake kategorisi. Belgelenmiş ekip örneği ayrıca Icebox, In Review, Ready to Merge, Could not reproduce ve Won’t Fix kullanır. Bloklayan/bloklanan ilişkiler statüden ayrıdır. Bizde basit varsayılan, ayrı aday inbox'ı ve ilişki rozetleri en iyi eşleşmedir. Kaynak: [issue properties / status / relations](https://linear.app/docs/issue-property). Eski configuring-workflows adresi aramada erişilebilir fakat direct open hata verdi; içerik güncel issue-property sayfasında doğrulandı.

### ClickUp

Üst gruplar Active, Done, Closed; Not Started ayrı etkinleştirilebilir. To do ve Complete başlangıç/bitiş için verilir; özel statüler konum hiyerarşisinde tanımlanabilir. Blocks/Blocked by/Waiting on ilişkileri ayrıdır. Done grubuna geçiş dependency gerekliliklerini kaldırabilir. Bizde bu otomatiği kopyalamamalıyız: prerequisite'i karşılayan güncel kanıt ve gate politikası belirleyicidir. Kaynak: [task statuses](https://help.clickup.com/hc/en-us/articles/6309452618647-Manage-task-statuses), [dependencies](https://help.clickup.com/hc/en-us/articles/6309155073303-Intro-to-Dependency-Relationships). Customizable features belgesi örnek Waiting on/Planned adlarını da verir; bunlar evrensel default değildir.

### Asana

Özel task type kendi statülerini ve hangilerinin complete sayılacağını tanımlayabilir; örnek Submitted, In review, Sent for translation, Published. Approval görevleri Pending → Approved/Changes requested/Rejected sonuçlarını ayırır. Dependencies yönlü Blocked by/Blocking olarak görünür. Bu kombinasyon bizim karar/onay kuyruğu ve bilgi türlerine iyi eşleşir. Approval feature plan ve yetki sınırları vardır; bu inceleme hesapta test değildir. Bizde rejected approval ürün görevinin başarıyla tamamlandığı anlamına gelmez. Kaynak: [custom task types](https://help.asana.com/s/article/custom-task-types?language=en_US), [approvals](https://help.asana.com/s/article/approvals), [dependencies](https://help.asana.com/s/article/use-dependencies-to-kick-work-off-at-the-right-time).

## 3. Senaryo → ürün eşleşmesi → Decivora açığı

| Mevcut senaryo / referans | En uygun örüntü | Kod ve dokümandaki gerçek durum | Önerilen değişiklik |
|---|---|---|---|
| Sohbette fikir/öneri var, insan seçmedi; APR-01/CAP | Linear Triage + Backlog | Aday inceleme ayrı; accept yeni Task'ı To Do yapıyor, seçilmemiş aday Task değil | Inbox/Proposal ayrı; kabul edilmiş fakat planlanmamış iş için Backlog |
| İş seçildi ama başlamadı; versioned AC | Jira/Linear başlangıç aşaması | To Do ve AC gate var | To Do teknik hazır garantisi olmayacak; readiness ayrı |
| Agent “bitti” diyor; AC-04/CTX-04 | Linear In Review + Jira Resolved/verification ayrımı | Başlangıç audit'i var; handoff/current review stage yok; Done kapalı | In Review ve Awaiting Verification; Done yalnız gerçek completion predicate |
| Q12 geç yanıt, Proje2 belirsiz B; AC-12/LATE/Q14 | Asana approval, ayrı pending queue | Manual soru lifecycle var; semantic/capture/agent routing kısmi | Awaiting Decision/Needs Clarification task rozetleri, soru kendi durumuyla; bütün proje bloke olmaz |
| API bakiye, veri/ücret izni; TRA/TOK | Jira approval bekleme örüntüsü | Policy/bütçe planı ile model bağlantısı ayrı; task UI typed bekleme kapsamı yok | Awaiting Approval, Budget/Permission gibi nedenler bağlı kararda; öncelik harcama izni değildir |
| A görevi B'yi engelliyor; FLOW-01–04 | Linear/ClickUp/Asana yönlü dependency | Core graph var; local UI yalnız manual blocker | Blocked by/Blocks, kaynak/revision/gate, otomatik assessment→UI; manual ayrı tutulur |
| B'nin bitmesi A'ya bağlı ama hazırlığı mümkün; FLOW-03 | Bağımlılık + gate ayrımı; bize özel netleştirme | Graph.assessment tüm dependency'yi genel blockers'a toplar; manual blocker bütün yeni start'ı durdurur | Start/finish/specific-action gate; bütün task'ı gereksiz kilitleme yok |
| SQLite kararı Markdown işini gereksiz yapıyor; AC-05/IMP | Jira resolution + Linear cancellation reason | Impact/cancel core var; enum todo/cancelled, UI sonucu gerekçeden ayrıştırmıyor | Obsolete önerisi ayrı review; onay sonrası Cancelled + Obsolete resolution; otomatik başarı yok |
| Aynı iş iki chat'te var; reconciliation | Linear canonical duplicate ilişkisi | Exact kaynak attachment var; duplicate outcome/semantik merge sınırlı | Auto duplicate sadece güvenli provenance; belirsiz birleşme review; canonical link/history |
| İptal edilen iş yeniden gerekli; lifecycle | Jira Reopened + event geçmişi | Core compensating event var; UI eski start kaydını hâlâ kullanır | Reopened geçmiş olayı; güncel stage son geçerli lifecycle/transition'dan hesaplanır |
| Rollback passed ama diğer AC bilinmiyor; CTX-04 | Bizim completion gate; genel tracker etiketinden güçlü | acceptance sonuçları not_run/completed=false, verifier henüz yok | Per-criterion passed/failed/pending/not_run/stale/unknown; tek passing test Done yapmaz |
| Restore/replay/ACL; AC-09/10 | Bizim event/approval modelimiz | Core snapshot/replay var, UI state ayrı okumalarla birleşiyor | Aynı yetki + knowledge snapshot, enum/schema version, no dispatch replay |
| Kullanıcı bilinçli bekletiyor | Linear Backlog örüntüsü + ayrı pause nedeni | Soru Deferred var; Task On Hold yok | On Hold bağımsız insan pause bilgisi; Blocked ile karıştırma; P2 configurable UX |
| İş deploy/yükleme bekliyor; GAP | Jira Published örneği, bize özel hedef kanıtı | Görülen dosya/test/deploy ayrımı dokümanda; target adapter açık | Publication/target evidence ayrı; gerekli DoD değilse global yeni sütun yaratma |

## 4. Gerçek açıklar ve önemleri

**G1 — yüksek:** Task için canonical güncel workflow statüsü yok; UI audit tarihinde task_work_started varsa In Progress türetiyor. Core cancellation→todo doğru olsa da eski start claim, UI'da yeniden açılmış işi yanlış In Progress gösterebilir. Statik kod çıkarımı; bu turda yeniden üretim/test yapılmadı. Düzeltme son geçerli event+revision projection, eski olay korunur.

**G2 — yüksek:** In Review/Awaiting Verification + gerçek kanıta bağlı completion UI/transition yok. Sütun eklemek T14 verifier'ı sağlamaz. Yeni stage'ler aynı API, guard ve testle uygulanmalı; Done gate korunmalı.

**G3 — yüksek:** Manual blocker, dependency blocker, insan kararı, erişim/bütçe ve işlem hatası aynı beklenti değil. Manual kayıtta gate, typed source, linked blocker node/owner ve blocked_since interval henüz yok. recorded_at, next_action metni var; otomatik owner ataması yok. Mutable label yerine typed assessment önerilir.

**G4 — yüksek:** Graph snapshot node'ları eligibility=false/verification=unknown kuruyor; graph kalite/ready entegrasyonu incomplete. Graph çekirdeği hazır diye otomatik doğru ready/blocked/öncelik iddia edilemez. Unknown → kesin Blocked değil, Needs Review olabilir. Snapshot/API/UI ve kriter verisi birlikte bağlanmalı.

**G5 — orta/yüksek:** Status, terminal outcome ve resolution gerekçesi ayrık sözleşme/metric UI'da eksik. Cancelled/Rejected/Duplicate/Obsolete başarı sayılmamalı; ended edge veya obsolete candidate task kapanışı değildir.

**G6 — orta:** Eski ve yeni dokümanların bazı genel “uygulanmadı” ibareleri güncel manual runtime eklerine rağmen geniş. approval-ux ASK/LATE “UI yok” ifadesi native/agent kısmı ile manual dilimi ayırmıyor. task-context-and-acceptance genel uygulanmadı; current AC sözleşmesi artık var. Güncel/plan/tarihsel kapsam netleştirilmeli, eski proof yeniden başarı diye yazılmamalı.

**G7 — orta:** Board dört lane'i frontend hardcode, task progress metrikleri review/verification/closed ayrımını taşımıyor; aynı task çeşitli listelerde iki kez toplam sayılmamalı. Bir kolon bir statü demek zorunda değil.

**G8 — sonraki faz:** Workflow preset/schema/configuration revision, dış status ID mapping, admin yayın/onay/migration, rollback, özelleştirilmiş durumlar ve takım kuralları henüz yok. MVP için tam Jira workflow editor şart değil.

## 5. Önerilen ürün modeli

Altı ana ilerleme aşaması: **Backlog → To Do → In Progress → In Review → Awaiting Verification → Done**. Bu default preset; her task sırf bu sıralamaya uymak için yapay iş üretmez. Review/verification gereksinimi task'ın onaylı policy/AC/DoD'sine bağlı; uygulanamaz madde explicit gerekçeli kalır. Done yine geçerli kanıt ister.

Cancelled ayrı terminal durum/kapalı işler görünümüdür; UI filtreyle görünür, silinmez. Böylece altı ana sütun + kapalı işler görünümü öneriyoruz; dört mevcut statünün sadece adını değiştirme değil. Kullanıcı isterse later preset'ler farklı column grouping sunar. Reopened bir transition/history olaydır; sonsuz yeni ana sütun gerekmez.

Ayrı eksenler:

1. **workflow stage:** iş bugün hangi aşamada?
2. **impediment/readiness:** Ready / Blocked / Needs Review; insan/dependency assessment'ları kaynak/gate ile. On Hold insanın bilinçli pause'u; engel kanıtı yerine geçmez.
3. **bekleme:** Awaiting Decision / Approval / External Input / Permission / Budget / Retry; yalnız ilgili işlem/task'ın gate'i etkilenir. Queue/job retry task'ın Failed olduğu anlamına gelmez.
4. **verification:** criterion ve aggregate current assessment; reported/observed/verified ayrı, unknown/stale/not_run başarısız gibi gösterilmez.
5. **resolution:** terminal nedeni Completed / Cancelled / Obsolete / Superseded / Duplicate; rejected proposal Task cancel değildir. Duplicate canonical link, obsolete karar ve review bağını korur.

Approval kendi lifecycle/digest'ini korur; Approved Decision applied veya task Done değildir. Agent run ended, job succeeded, verified Task ve kullanıcı kararı farklı varlıklardır. Metrikler bu türleri ayrı sayar. Bu önerilen alanlar fiziksel DB tablosu tasarımı olarak onaylandı sayılmaz; mevcut event/audit çekirdeğine önce versioned contract ve projector uygulanır. UI label değişimiyle mevcut stored execution alanı körlemesine değiştirilmez.

Almayacağımız varsayılanlar: boş Done ile prerequisite karşılama; eskiye otomatik auto-close; bütün rejected approval'ları iş başarısı sayma; Done'dan global sınırsız drag transition; yalnız başlık benzerliğiyle duplicate merge. Genel marketing/recruitment statüleri ürünümüze zorla taşınmaz.

## 6. Küçük uygulanabilir teslim sırası

- **D1:** benchmark + status sözlüğü + transition/source authority + stage/resolution/verification mapping ve migration planı; G1 regression testi; status projection. Yeni paid API gerekmez.
- **D2:** mevcut T13/T20 kapsamında guard'lı Backlog/To Do/IP/review handoff; bütün UI/list/status metrikleri tek snapshot; migration mevcut kayıtları tahmin ederek review/Done'a taşımaz. Completion callback hazır değilken Done işlemi disabled kalır.
- **D3:** mevcut T11c/T20e/T19/T21 kapsamında gate-aware linked blockers/bekleme kartları, review/clarification kaydı, owner/age/next-action ve canonical priority'den ayrı recommendation. Kaynak olmadan otomatik ilişki uydurma yok.
- **D4:** T14a/b/c ve T24 altında izinli verifier→criterion assessment→completion predicate; current passed ile Done, failure/stale sonrası yeni assessment/reopen; parent scope ayrıca. Task onayı shell/provider izni değildir. Ücretli model gerektiren semantic capture ve pending T09 ölçümü kendi API/bütçe kapısında kalır; bu workflow düzeni onu tamamlamış sayılmaz.
- **P2:** role-bound workflow presets/configurator, dış Jira/Linear mapping, gelişmiş On Hold/aging/reporting. MVP'yi genel workflow editor'a çevirmiyoruz; tam scope korunur.

Yeni main task eklemek veya Done sayısını yapay artırmak yok. Var olan T13/T14/T19/T20/T21/T24 alt dilimlerinde kayıtlı kapsamla ilişkilendirilecek. Bu sıranın süre/teslim garantisi yok.

## 7. Onay sonrası etkilenecek hedefler

| Hedef | Değişim |
|---|---|
| docs/discovery/benchmark.md + benchmark-findings.md | Bu dört kaynak, neden seçildiği, statü/ilişki/approval örüntüsü ve ölçülmemiş sınırlar |
| Yeni docs/discovery/workflow-status-benchmark.md | Bu araştırmanın repo içi canonical kısa raporu; duplicate analiz versiyonları yok |
| docs/product/priority-and-flow.md + approval-ux.md + task-context-and-acceptance.md + pending-questions-and-late-answers.md | Tek sözlük, blocker/waiting/review/verification ayrımı; manual ve future native durum netliği |
| docs/product/full-scope.md + mvp.md + current-direction.md | İlgili kapsam referansları;32scope ve14AC korunur; yeni vizyon icat edilmez |
| docs/architecture/runtime-contracts.md + data-relationships.md + task-lifecycle.md + local-preview.md + reconciliation-impact.md | Transition/event/projector/digest/resolution/DDL değişirse versiyon/migration; fiziksel öneri ile çalışan kod ayrımı |
| İlgili ADR + decision-map/decision-brief | Benchmark alternatifleri ve kullanıcının gerçek onayı/gerekçesi; bugünden onay verilmiş gibi kayıt yok |
| README.md + ROADMAP.md + README_LOCAL.md | Güncel preset, çalışan/planlı sınır ve board kullanımı |
| delivery/backlog.md + status.md + implementation-readiness.md + task-closure.json + generated progress.md | Mevcut işe mapping, gerçek kanıt ve sayımlar; tracker ürün panosunun statülerini kör kopyalamaz |
| packages/domain/*, storage projection/schema gerektiğinde, apps/local_ui/*, manifests/* | D1–D4 ilgili kod/sözleşme; mevcut çalışır path korunur, yeni frontend dependency yok |
| tests/runtime + browser + docs/quality/verification ve sonuç kayıtları | Aşağıdaki ilgili yeni acceptance/regression; native/semantic test uydurulmaz |
| İlgili Mermaid kaynakları + SVG + render inventory | Task lifecycle, review, verification, DB ilişki ve local UI akışları değişirse birlikte hash/render; aynı kalan diagramın tarihi gereksiz yazılmaz |
| Yerel ZIP + private GitHub + devam paketi | Yalnız onaylı/test edilen değişiklikler; kullanıcı DB/key/transcript pakete eklenmez |

AGENTS.md'ye geçici benchmark/aktif task dökümü ekleme gerekmez; mevcut authority/verification kuralları zaten yeterli. İlgisiz CSV korunur. “Her yerde” aynı paragrafı tüm dosyalara yaymak değil, etkilenen sözleşme ve görünüm referanslarını tutarlı güncellemektir.

## 8. Doğrulama ve risk

Ölçülebilir kabul: agent completion claim→review, tek passed kriter≠Done, stale/failed/not_run→completion ret, reject proposal≠cancelTask, Done/cancelled history korunumu, start/finish gate ayrımı, bir blocked task'ın bağımsız projeyi durdurmaması, permission/budget wait≠failed, multiple manual/dependency blockers'tan yalnız birinin çözümü≠ready, resolve≠auto-start. İnceleme/Done kriterleri zorunlu değilse policy gereksiz review yaratmaz. Stale/unauthorized/agent human-spoof, iki eşzamanlı transition, retry idempotency, graph cycle/incomplete/ACL unknown, old-start→cancel→reopen, snapshot coherence, backup/replay/schema migration ve rollback testleri. Bir task çeşitli görünümlerde görünebilir; toplam paydası unique Task ID olur. Beş locale ve RTL klavye/mobile; statü isimleri mevcut kullanıcı tercihine göre İngilizce.

**Fayda:** doğru bekleme/ilerleme görünümü, gerçekten kapanan iş sayısı, yanlış Done ve gereksiz blocker azalması; hangi işin hangi engeli açtığı görünür.

**Risk:** projection/migration hatası, label ile yetki/gerçeklik karışması, workflow karmaşıklığı, stale snapshot ve parent scope karışması. Önlem: önce contract/regression, yeni stage event'leri versioned, kayıpsız eski→yeni mapping ve yedek/restore, fail-closed authorization/completion, mevcut records'u otomatik yeniden sınıflandırmama. Eski doğrulama sayıları yeni davranış için başarı kanıtı değildir.

Onay beklenen somut kapsam: bu beş eksenli model ve altı ana aşamalı preset; mevcut işlerde D1–D4 kod/doküman/diagram/test entegrasyonu ve doğrulanmış çıktının private GitHub/yerel pakete kaydı. Yeni ücret, hesap bağlantısı, production veri geçişi, dış araçlara yazma veya key kullanımı bu onayın kapsamına girmez. Mevcut yerel veri migration'ı gerekiyorsa uygulanabilir yedek/mapping hazırlandıktan sonra risk ve exact hedef ayrıca gösterilir.


## 9. UI/UX benchmark ve görsel öneri — 14 Ekim 2026

**Kullanıcı tarafından kabul edilen kapsam:** Kullanıcı aynı dört ürünün arayüzlerini görsellerden incelemeyi ve ilk etapta alışılmış bir düzenle benzerleştirmeyi istedi. Image search yapıldı; incelenebilir ürün ekranları tarayıcıda gerçekten açılıp görsel kontrol edildi. Teknik davranışlar resmî güncel dokümana dayandırıldı. Screenshot'ların hepsi güncel release ekranı değildir; eski örnekleri güncel ürün sürümü diye göstermiyoruz. Hesap oluşturma, giriş, paid plan, kaynak kod tersine mühendisliği veya ürün davranışı üzerinde gerçek görev deneyi yapılmadı.

### Kaynak ve görsel gözlem

| Ürün | Görsel / kanıt ve sınır | Decivora'ya uyarlanacak örüntü |
|---|---|---|
| Jira | [Resmî Server9.8 backlog örneği](https://confluence.atlassian.com/jirasoftwareserver0908/creating-your-backlog-1235856793.html): sol gezinme, sütunlar, hızlı filtre, sağ görev paneli; tarihsel örnek, güncel Cloud screenshot değil. [Güncel kolon sözleşmesi](https://support.atlassian.com/jira-software-cloud/docs/configure-columns/) ayrıca okundu | Pano açısını kaybetmeden görev detayına erişim; kolon başlığı + sayım; görünüm/status mapping ayrı |
| Linear | [Filters resmi ekranı](https://linear.app/docs/filters) görselde gruplanmış liste gösteriyor; image search buna board demişti, gözlenen görüntüyle düzelttik. [Board layout](https://linear.app/docs/board-layout) resmi hero örneği görsel/placeholder; gerçek task içeriği gibi değerlendirilmedi. [Display options](https://linear.app/docs/display-options) güncel davranış kaynağı | Kompakt başlık/ID/az metadata; List/Board geçişi, filter chip, sayım ve gösterilecek alan ayrımı; bütün açıklamayı karta basma |
| ClickUp | [Resmî Boards sayfasındaki sade görsel](https://clickup.com/features/kanban-board) tarayıcıda görüldü: sidebar, List/Board sekmesi, açık kolonlar, kompakt kartlar, collapse edilmiş review kolonu; pazarlama örneği. Help screenshot attachment erişilemedi; başarı diye yazılmadı. [List/Board davranışı](https://help.clickup.com/hc/en-us/articles/6310314670359-List-view-vs-Board-view) | Bir veri seti üzerinde view değiştirme, kolon gruplama/alt gruplama; bütün ClickUp menü kalabalığını taşımama |
| Asana | [Resmî forumdaki connected-work görseli](https://forum.asana.com/t/coming-soon-connected-work-links/160908): gruplanmış görev listesi ve sağ detay/activity paneli;2021tarihsel örnek, board screenshot diye sınıflandırılmadı. [Güncel Board rehberi](https://help.asana.com/s/article/board-view?language=en_US) ayrıca kontrol edildi | Görev detayı, description/dependency ve activity ayrımı; ana görünümü kaybetmeden geçmişe erişim |

Screenshot ile etkileşim, latency, erişilebilirlik veya kullanıcı başarısı kanıtlanmaz. Aşağıdaki UX değerlendirmesi örüntü analizi ve mevcut kaynak koda dayalı çıkarımdır; kullanılabilirlik testi sonucu değildir. Rakip screenshot, logo, CSS, özel ikon veya fontlar uygulamaya kopyalanmayacak; genel yerleşim/etkileşim örüntüleri kendi kodumuzla uygulanır.

### Mevcut yerel UI'da tasarımla ilgili açıklar

- Sol bağlantılar aynı uzun sayfadaki anchor'lara gider; conversation→manual task→manual question→blockers→board→detail dikey akışı görev takibini zorlaştırabilir.
- Kart seçimi detayları panonun aşağısına açıyor; seçili task görünümü ile board bağlamı aynı anda yeterince görünmüyor.
- Search, gerçek status/blocker/pending filtreleri, görünüm seçenekleri ve ayrı yoğun List görünümü yok.
- Kartta tam description yer alıyor; uzun metinde kart yüksekliği/task tarama yükü artabilir. Toolbar ve kart metadata hiyerarşisi daha belirgin olmalı.
- Model etkin değilken uzun açıklamalar var; kısa connection chip + isteğe bağlı ayrıntı, hatayı gizlemeden daha az yer kaplayabilir.
- Blocker listesi görevleri ikinci kez sunuyor; attention summary→filtered view geçişi, unique task sayımını koruyarak tekrar/kalabalığı azaltabilir.
- Altı lane'e geçildiğinde mevcut eşit fr grid her kartı aşırı daraltabilir. Desktop'ta kontrollü board yatay scroll; mobile'da lane seçici/List alternatifi; sayfanın tümü yatay taşmamalı.

### Önerilen tanıdık düzen

**Ana referans Linear'ın bilgi yoğunluğu + Jira/Asana'nın yanında açılan görev detayı.** ClickUp'tan view tab/kolon collapse örüntüsü; büyük platformun tüm seçeneklerini eklemiyoruz.

1. Sabit sol gezinme: proje seçimi, Conversations, Review inbox, Board, Decisions, Sources. Overview yalnız somut fayda sağlayan metriklerle. Mevcut tek proje preview'da project switcher çok proje varmış gibi çalışmaz; destek yoksa current project gösterir. Yeni schema/team feature gerektiren kontroller disabled ve açıklamalı, dekoratif tıklanabilir değil.
2. Üst project başlığı + görünüm sekmeleri + search/filter/display. Board mevcut işler; Review inbox ayrı aday/onay. Ana capture amacı header'daki Import conversation ve Conversations görünümünden erişilir; manual Task oluşturma ikincil. Açılış onboarding'i veya task-focused varsayılan görünüm, son kullanıcı seçimine göre; sırf board-first diye öneriler/kararlar kaybolmaz.
3. Kompakt kart: stable görünür Task ID, başlık, workflow statüsü, Blocked/Blocks veya pending rozet, gerekirse owner/kanıt özeti. Tarih/öncelik yalnız mevcut veri varsa; uydurma avatar/agent/owner ataması yok. Full description detail'da.
4. Kart seçilince mantıksal end-side panel: başlık/status/reason; Overview, AC/DoD, Sources, History. English LTR'da sağda, Arabic RTL'da yön uyumlu. Yer darsa tam sayfa detail + açık Back. Panel açma/kapama board filter, scroll ve seçili task bağlamını korur. Side panel sayfa bölgesiyse gereksiz modal focus trap yok; narrow-screen modal kullanılırsa doğru dialog/focus yönetimi.
5. Attention bar: Blocked, Awaiting Decision, Awaiting Verification sayıları + gerçek filtreye geçiş. Bir task birden fazla rozet taşıyabilir; rozet toplamı unique task sayısı diye sunulmaz. Parent/child ve kapalı işler ayrı filtrelenir.
6. Tasarım tokenları: açık yüzey, ince border, nötr tipografi, tek ana vurgu; blue active, purple review, amber waiting, green verified, red blocked. Metin/ikon rengi destekler; tek başına renk anlam taşımaz. Mevcut palette korunup düzenlenir; sistem fontu, yeni dış font/CDN gerekmiyor.
7. Statü değiştirme hem dropdown/klavye ile; drag-and-drop ikinci yol ve aynı server guard. Done/cancel/merge gate'leri gesture ile bypass edilemez. İlk dilimde güvenilir dropdown yeterli, DnD ertelenebilir.
8. View değişimi ve panel açma LLM çağırmaz; token bütçesine etkisi normal UI okumasıyla sınırlı. Task/decision/source içerikleri UI locale ile çevrilmez. English task status tercihimiz korunur;5locale veRTL regresyonu devam eder.

**Farklılaştırıcı içerik yerleşimi:** Kaynak→insan kararı→etkilenen işler→uygulama kanıtı zinciri task detail'da gösterilir. Kullanıcıya yeni bir navigasyon dili öğretmek yerine bildiği board içinde bu ek bilgi sunulur. Graph ilk açılışta zorunlu ana ekran değil; gerektiğinde detaydan açılır. Bunun tamamı bugünkü runtime'da varmış gibi gösterilmez.

### İncelenebilir görsel taslak

[Repo dışı SVG wireframe](../../assets/mockups/workflow-ui-proposal.svg). Kendi çizimimiz, synthetic5Task; hiçbir gerçek kullanıcı verisi/model sonucu yok. Statik düzen taslağı: navigation/search/button tıklamaları uygulanmış ürün sayılmaz. Desktop yerleşim tarayıcıda görsel incelendi; SVG XML parse edildi. Bu mobile/RTL/erişilebilirlik veya etkileşim kabul testi değildir. Ürünün mevcut arayüzü değiştirilmedi.

Uygulamada preview'daki dar kolonları aynen kopyalamıyoruz: kart okunabilirliği için minimum genişlik ve board-local horizontal scroll; detail açıkken alternatif List görünümü. Aynı state/source ile filtreleme ve row/card görünümü; mock cardinality'den completion yüzdesi üretilmez. Wireframe'daki tab/alanlar, uygulama sırasında gerçek handlers/scope ile bağlanacak veya unavailable açıklaması taşıyacak.

### Onay sonrası hedefler / doğrulama

Önceki D1–D4'e UX eklenir: D1 state/IA/design token ve component sözlüğü; D2 view routing + toolbar + side panel + board/list; D3 blockers/waiting filters; D4 current evidence/review detayları. Yeni genel design framework, Web Awesome/React bağımlılığı veya kapsamlı rewrite bu önerinin şartı değil. Component/library pilotu ayrı mevcut proposal; bugün installed diye gösterilmez.

Etkilenecek ek belgeler: approval-ux, graph-experience, language-and-localization, local-preview, UX verification, README_LOCAL ve benchmark; gerçek kod apps/local_ui/index.html/app.js/i18n katalogları, gerektiğinde scoped state API. ADR/diagram/README/backlog referansları gerçek değişiklikte güncellenir. Başka dosyaları sırf kapsamlı görünmek için düzenleme yok.

Kabul: bir kart seç→detay→kaynak/AC→kapat akışında board konumu/filtre korunur; search/filter ile doğru task ve doğru filtered/total sayım; blocker card'dan neden/owner/next action; pending clarification kaybolmaz; manual task ikincil ama erişilebilir; ready/unknown/verified karışmaz; form drafts korunur;401/403/storage/model-off/empty/error/loading ayrı; keyboard/Escape/focus visible/screenreader;390pxmobile ve ArabicRTL;40+sentetik task ile gezinme ve local list limit/truncation açık; hiçbir görünüm eylemi model/approval tetiklemez. Süre veya UX iyileşme yüzdesi baseline ölçülmeden uydurulmaz.

Onay isteği: önceki workflow sözleşmesi ve D1–D4 ile bu tanıdık sidebar/toolbar/board-list/end-panel düzenini birlikte uygulamak; çalışan product UI/kod/doküman/diagram/test/ZIP ve privateGitHub kaydı. Kullanıcının önceki “yapmadan önce onay al” sınırı geçerlidir; bu mesaj yalnız research/draft hazırlığına yetki olarak kullanıldı. Ücretli model, yeni hesap, dış uygulama bağlantısı, public yayın veya kullanıcı verisi taşınması için izin çıkarılmadı.


## 10. Onay sonrası gerçek uygulama sınırı

14 Ekim 2026 kullanıcı “onaylıyorum; tüm doküman, diagram, şema ve GitHub'dakileri kontrol et, gerekiyorsa güncelle” dedi. [ADR-0013](../architecture/adr/0013-task-workflow-and-familiar-ui.md) seçimi/gerekçeyi tanımlar. D1 güncel stage projection + schema/regression, D2 altı-stage/Board-List/filter/end-panel, D3 kayıtlı dependency + linked manual question + gate-aware manual impediment, D4 **yerel human-review verifier yolu** kodda vardır. Automatic test/file verifier, host artifact revision gözlemi, semantic blocker extraction, native agent delivery ve tam parent completion/policy kabulü açık; bunları tamamlandı saymıyoruz. P2 workflow editor/sync/cloud/On Hold config aynı fazda kalır. Yeni otomatik capture/model çağrısı yok; T09 kalitesi bu UI değişikliğiyle çözülmedi.

Legacy DB için yeni tablo veya kayıtlara yazan migration yok. Eski task_work_started kaydı lifecycle yoksa legacy başlangıçtır; cancellation→todo sonrasında eski start stage'i taşımaz. TaskStage ve criterion_evidence append-only audit'te versioned payload; task/AC/graph-linked evidence değişimi güncel Done'ı Awaiting Verification gösterir, eski başarı/audit silinmez. Cancelled ve pending clarification ayrı kalır. Gereksiz yeni main task eklenmedi; T14 In Progress, parent Done değil.

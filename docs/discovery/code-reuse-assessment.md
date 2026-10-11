# Kaynak kodu ve teknoloji değerlendirmesi

**2026-10-11 · Karar hazırlığı; kod alımı veya stack kabulü değil.** İncelenen kaynak [WrongStack/WrongStack, sabit commit](https://github.com/WrongStack/WrongStack/tree/5234c15b05fe18857d0119eabd3b8a8f910ecc66). Önceki [hedefli incelemeyi](wrongstack-review.md) repo genelindeki yapısal envanter ve yeni çağrı/sözleşme okumalarıyla tamamlar. Decivora'nın kendi ürün/domain ihtiyaçları değerlendirme ölçütüdür; upstream talimatları çalıştırılmadı.

**Öneri:** bütün platformu almak yerine küçük deterministik modülleri ve `governance` sözleşmelerini izole deneylerle kıyaslayalım. `governance` ve Kanban contract graph önceki incelemede yeterince görülmemiş önemli örtüşmelerdir. Memory, append-only history, revision, evidence ve graph varlığı tek başına farklılaşma iddiası olamaz. Uçtan uca insan seçimi→exact hedef uygulama→karar gerekçesi etkisi→başka araçta devam akışı hâlâ karşılaştırma hipotezidir.

## İnceleme kapsamı: tüm repo ne ölçüde incelendi?

| Katman | Yapılan iş | Çıkarılabilecek sonuç / sınır |
|---|---|---|
| Kaynak sürümü | Sabit commit arşivi ayrı geçici alana açıldı; symlink/özel çalışma dizinleri alınmadı | Hareketli main ile karışmaz; upstream runtime Decivora'ya eklenmedi |
| Repo geneli yapısal tarama | 39 root/workspace manifest; 9.657 kod dosyası, test/fixture/declaration dahil 2.203.270 satır UTF-8 okuma/hash/regex import indeksi | 5.200 source, 4.420 test/fixture, 37 declaration; okuma hatası yok. İndekslenen 9.657 dosyanın byte içeriği immutable Git tree blob hashleriyle de eşleştirildi; bu kaynak kimliği kontrolüdür, davranış testi değil. Bu sayılar yorum/boş satırlar içerir; yazılım karmaşıklığı veya kalite puanı değildir |
| Paket ilişkileri | Direct dependency/optionalDependency manifest'leri ve dahili paket kapanışı | Type-only ile yüklenen runtime importu aynı değildir; lock çözümlemesi, tree-shaking, bundle ve transitif lisans sonucu yok |
| Davranış incelemesi | Önceki seçili parçalar + governance store/transition/contract/grant/verification, contract graph, Chronicle, rate-limit, client, vector ve graph UI bölümleri | Kritik adayların semantik farkları saptandı. 2,2 milyon satırın tek tek anlam denetimi yapılmış değildir |
| Çalıştırma | Upstream install/build/test/script/agent/provider çağrısı yapılmadı | CI, güvenlik, performans, entegrasyon ve tasarruf `not_run` |

**İstisnalar:** `.wrongstack`, `.project`, `.git`, `node_modules` dışlandı; özel çalışma günlükleri/prompt çıktıları incelenip taşınmadı. Markdown, JSON/YAML/config, lockfile, binary/asset gibi kod dışı dosyalar tümüyle semantik incelemeye alınmadı; root LICENSE ve ilgili manifest/config belgeleri hedefli okundu. Tarama, sıfırdan hazırlanmış [envanter betiğiyle](../../scripts/inventory_upstream.py) tekrarlanabilir. [CSV](upstream-component-inventory.csv) bütün 39 manifest alanını; [JSON](upstream-inventory-summary.json) yöntem, kapsam, hata ve path/hash digest'ini tutar. Büyük per-file import/hash indeksi geçici inceleme alanında kaldı; upstream source metni repository'ye kopyalanmadı.

Bu, **bütün paketleri kapsayan yeniden kullanım değerlendirmesidir**; bütün kodun doğruluğunu veya tüm olası yeniden kullanım fırsatlarını tüketen audit değildir. “Tüm kaynak doğrulandı” veya “hiç eksik kalmadı” sonucu çıkarılmaz.

## Değerlendirme ölçütleri

1. Mevcut ihtiyacı karşılıyor mu: provenance, human authority, revision, unknown ve decision-aware impact?
2. Küçük bir sınırdan ayrılabiliyor mu; paket kapanışı ne getiriyor?
3. Domain/permission/retention semantiği değişmeden taşınabiliyor mu?
4. Kaynak/test/notice ve doğrudan bağımlılıklar izlenebilir mi?
5. Native/extension aynı kullanıcı sonucunu daha az bakım ve yönetim işiyle verebilir mi?
6. Kullanıcı yararı ve toplam maliyet aynı fixture ile ölçülebilir mi?

Yüksek/orta/düşük uyarlama sınıfları masa başı yorumudur; saat/gün tahmini veya ölçülmüş efor değildir. Aday test kaynağının varlığı çalışmış test sonucu sayılmaz.

## Bütün paketlerin Decivora açısından kullanım haritası

**K:** küçük kaynak adaptasyonu adayı. **Ö:** mimari/UX örüntüsü. **E:** native/extension deneyinde değerlendir. **S:** sonraki fazda gerekirse. **D:** ilk deneyde dışarıda. Hepsi öneri; paketler alınmadı. Satırların tamamı manifest/yapısal tarama kapsamındadır; her paketin her davranışı elle okunmadı.

| Upstream alanı | Değerlendirme ve Decivora karşılığı | Yol |
|---|---|---|
| `governance` | Event/receipt, task contract, plan revision, verifier/grant; T07/T13/T14. Ayrıntılı yeni aday | K/Ö/E |
| `persistence` | SQLite runtime, atomik dosya/export, IPC secret; T04/T07/T23 | K/Ö |
| `primitives` | Token compare, zaman/regex guard, redaction; T05/T09/T18 | K, yalnız gerekli helper |
| `kanban` | Evidence, managed lifecycle, dependency ve contract graph; T11/T14/T20 | K/Ö/E |
| `sdd` | Requirement/spec/plan coverage; T11/T15 | K/Ö |
| `requirement-intake` | Model önerisi ile lifecycle ayrımı; T09/T13 | Ö/K |
| `sage` | Kaynaklı/koşullu memory, anchors, search, revision; T09/T10/T14/T18 | K/Ö/E; komple paket kararı değil |
| `vector-memory` | SAGE mirror, semantic/lexical fusion, cache temizliği; T26 | S; ilk deneyde gerekçe yok |
| `core` | Chronicle, compaction, skill pattern, subagent budget/knowledge graph; T06/T09/T18/T21 | Seçili K/Ö; tüm agent loop D |
| `runtime` | Port/container ve governance bootstrap; extension kabiliyeti | E; bağımsız ürüne komple import D |
| `mcp` | Stdio/HTTP, cancellation, schema, elicitation/policy; T18 | Ö/E; küçük contract adaptasyonu |
| `sage-mcp` | Memory read/proposal policy; T18 | Ö/E |
| `kanban-mcp` | Task MCP host; T18 | E; Decivora command modeli ayrı |
| `mailbox-mcp` | Actor-bound agent iletişimi; T18d/P4 | E/S |
| `requirement-intake-mcp` | Intake MCP yüzeyi; T18 | E/S |
| `codebase-index-mcp` | Kod indeks erişimi; evidence adapter'a komşu alan | S; index sonucu uygulama kanıtı değil |
| `client` | WebSocket client/error ayrımı | Ö/S; özel protocol ve core kapanışı |
| `webui-protocol` | Typed wire/read model; T19 | Ö; Decivora API olarak kopyalama D |
| `webui-server` | Host/API/session/connection assembly | E; tek domain paneline tüm server D |
| `webui` | Memory/contract/dependency/verification graph ve i18n | Ö; seçili view logic K adayı |
| `webui-hq` | Çok-agent kontrol ve ekip görünümleri | Ö/S; ilk solo deneyde D |
| `simpleui` | Daha dar web deneyimi | Ö/E; tüm chat UI gerekli değil |
| `tui` | Terminal task/memory sunumu | E/S; ilk insan UI seçimi açık |
| `providers` | Çok-provider model binding/usage | S; mevcut host hesabına erişim vermez |
| `tools` | Tool search, filesystem/Git/code index/browser/shell araçları | Seçili Ö/K; geniş runner D |
| `acp` | Agent Client Protocol bağlantısı | E/S; MCP/capture yerine varsayılmaz |
| `plugin-sdk` | Upstream extension sınırı | E; bağımsız core zorunluluğu değil |
| `plugins` | Guard/brain/routing/review eklentileri | E; tüm katalog D |
| `plug-lsp` | LSP/symbol desteği | S; sembol doğrulama ihtiyacı çıkarsa |
| `bench` | Harness fingerprint, rapor karşılaştırması, oracle ayrımı | K/Ö; coding grader ürüne aynen uymaz |
| `security-scanner` | Scan/batch/manifest/report pattern | Ö/S; yeni güvenlik ürünü kapsamı D |
| `techstack` | Teknoloji katalog/store/öneri modeli | Ö/S; pilotun ana problemi değil |
| `telegram` | Harici bildirim/chat delivery | S; kanal/izin açık, ilk deney D |
| `wrongtrace` | İzleme/gate client ve tool hook entegrasyonu | Ö/S; dış servis gereksinimi ayrıca araştırılır |
| `cli` | Yukarıdaki alanların kurulum/host/fleet assembly'si | Native E; bağımsız uygulamada komple D |
| `apps/desktop` | Desktop packaging ve bridge | S; web-first adayı test edilmeden Electron alma |
| `apps/wrongstack` | Upstream ürün entry point | Native E; Decivora entry point olarak alma D |
| `website` | Tanıtım/demo sitesi | D; ürün çekirdeğine katkısı yok |
| Root manifest ve diğer alanlar | Build/config/scripts/e2e/deploy/styles/root src envanteri | Test/build örüntüsü Ö; script, asset ve deploy kopyası D |

Tablo 35 `packages/*` + 2 `apps/*` + website + root = 39 manifest alanını kapsar. CSV'de fixture altındaki örnek manifest'ler ayrı workspace ürünü olarak sayılmaz; fixture kodu ilgili alanın test sayısındadır.

## Somut kod adayları: nerede, nasıl, hangi farkla?

Aşağıdaki yollar sabit upstream ref'e aittir. Kaynak metinleri alınmadı. Önerilen hedefler mevcut runtime dosyaları değil; ilgili backlog görevinde oluşturulabilecek modül sınırlarıdır.

| ID / gerçek kaynak yolu | İncelenen davranış / bağımlılık | Decivora hedefi ve alım yöntemi | Uyarlama ve kabul sınırı |
|---|---|---|---|
| R01 `packages/kanban/src/verification/evidence-validator.ts` | Ref sayısı/türü + belirsiz İngilizce summary kontrolü; domain tipleri | T14 Evidence input validator; küçük adaptasyon | Fake ref varlığını doğrulamaz; observation/issuer/revision ayrı. Locale ve negatif örnekler; WS-01 |
| R02 `packages/sdd/src/requirement-coverage.ts` | Missing/unknown mapping, spec mismatch ve execution DAG integrity; core tipleri | T11/T15 CoverageValidator; saf algoritma adaptasyonu | N:M requirement; active spec revision; history/justification graph'a DAG yasağı yok; WS-04 |
| R03 `packages/sage/src/shared/memory-validity.ts` | Bounded conditional validity ve literal path/check normalizasyonu | T09/T10 ConditionInput; küçük schema adaptasyonu | Literal eşleşme koşulun mantıksal ispatı değildir; AND/OR/unknown ayrı; WS-02/03 |
| R04 `packages/governance/src/event-store.ts` + `event-store-contract.ts` | BEGIN IMMEDIATE içinde command/receipt; idempotent replay; event/receipt/observation UPDATE/DELETE trigger; persistence paketi | T07/T15 EventStore deneyi; önce dar port ile kaynak adaptasyonu | Task aggregate'a bağlı; Decivora source receipt/job/outbox/multi-entity changeset/graph fence/purge hazır değil. Crash/retry/replay testleri |
| R05 `packages/governance/src/task-contract.ts` + `plan-version.ts` | Requirement/AC/check/scope/autonomy; plan parent revision ve canonical fingerprint | T13/T14 TaskContract/ChangeSet contract; validator örüntüsü | Plan hash insan onayı değil; decision/AC/graph/authz/target revision digest'e bağlanmalı. N:M ilişkiler ve mevcut domain korunur |
| R06 `packages/governance/src/transition-engine.ts` | Stale revision, grant/snapshot/evidence guard; model self-admit yasak | T13/T14 TransitionPolicy; saf policy adaptasyonu | Policy'nin otomatik admit yolu var; protected insan kararını devretme. Terminal completed'dan düzeltme/yeniden açma bizim event kurallarımıza uyarlanır |
| R07 `packages/governance/src/verification-run-contract.ts` + `verification-check-binding.ts` | Contract/plan/workspace/check/handler bağlı run; bağımsız verifier ve süre sınırlı registry binding | T14 VerificationContract; ilk schema/negatif oracle deneyi | Exact target/ref/artifact/AC + authz/runner scope gerekli. `trusted_deterministic` etiketi gerçek sandbox kanıtı değil |
| R08 `packages/governance/src/capability-grant.ts` + `authenticated-project-service.ts` | Opaque credential, project/client binding, TTL/revoke/rotate; server-owned capability | T05/T18 scoped principal gateway; önce örüntü | Local registry ekip IAM/SSO değil; kaynak ACL intersection, türev egress, restart/revocation ve stale receipt kontrolü ayrıca |
| R09 `packages/kanban/src/types-contract-graph.ts` + `contract-graph.ts` | Objective/guardrail/risk/artifact/check; typed edge/rationale; readiness/conflict evaluation; off/advisory/strict | T11/T12/T20 GraphReadModel ve review açıklaması | Execution DAG'dan zaten ayrı. Decision supersession AND/OR/unknown, ended/invalidated edge ve causal history ayrıca; graph olduğu için aynen alma |
| R10 `packages/sage/src/anchors/verify.ts` + `sqlite-store-verify.ts` | Hash/file/symbol/git/command availability ve fenced verify update | T14 TargetObserver; selected adapter örüntüsü | Local disk ≠ GitHub'daki exact ref; offline/denied unknown; symbol text match/test availability verified değildir |
| R11 `packages/sage/src/retrieval/format.ts` | Revision/date/conditions/IDs, escaped data; ilk memory limit aşabilir | T18 ContextEnvelope; formatter adaptasyonu | Hard cap + cursor/ref/coverage; permission check önce; oversized atomik kayıt görünür; WS-05 |
| R12 `packages/sage-mcp/src/policy.ts` | Read/proposal-only tool schema + runtime action guard | T18 MCPCommandPolicy; dar wrapper örüntüsü | Tool visibility/annotation insan authority değildir. Server-side per-call authz; WS-06 |
| R13 `packages/mcp/src/server-dispatch.ts` + `elicitation-form.ts` | Transport dışı host interface; cancel/schema; form ID/option mapping ve bounded retry | T18 host bridge; elicitation UX örüntüsü | MCP cevabı durable PendingQuestion yerine geçmez; late/orphan/cross-chat association ve option revision; LATE suite |
| R14 `packages/tools/src/tool-search.ts` | Limit/filter; ilk beş full schema, kalan kısa | T18/T21 ToolCatalog; gerekirse küçük adaptasyon | MVP küçükse ek tool/round-trip gereksiz; toplam maliyet ve discovery başarısı ölçülür |
| R15 `packages/core/src/coordination/agents/project-agent-skill-routing.ts` + `project-agent-capture.ts` | Explicit skill tag, vocabulary, LEARNED blok çıkarımı | T09e LexicalCandidateFilter; fikir/algoritma | Task/human choice/action completion'a çevrilmez; TR/EN/quote/negation/unmatched guard; LEX suite |
| R16 `packages/core/src/execution/compaction-elision.ts` | Eski tool I/O digest; paired IDs, error/read context | T18 ResumeContextPacking; örüntü | Yalnız kendi paketimiz; host geçmişini değiştirme, raw source silme. Full-context kalite baseline |
| R17 `packages/core/src/chronicle/decision-adapter.ts` + `file-observer.ts` | Decision option ID ve hash/correlation; debounce/rescan/file fingerprint | T06 Capture metadata, T14 selected local target observation | Brain kararı insan kararı değildir. Chronicle ham gerekçeyi tutmuyor; domain source arşivi ayrı. Council unknown usage burada `??0`; biz null koruruz |
| R18 `packages/core/src/coordination/mailbox-project-server-protocol.ts` | Project owner IPC ve actor request | T18d MultiAgent adapter; protokol dersleri | Mailbox retention domain audit değil. Child vote/answer insan scope onayı değil; actor provenance |
| R19 `packages/core/src/coordination/subagent-budget.ts` + `spawn-budget.ts` | Child budget negotiation/stop + depth ceiling | T21 UsagePolicy; örüntü | Parent/period atomik rezervasyon ve belirsiz usage ledger ayrıca. Extension/child yeni tavan açamaz; WS-07 |
| R20 `packages/core/src/coordination/mailbox-http-rate-limit.ts` | Key başına in-memory sliding window | T06/T18 admission limiter; küçük algoritma adayı | Process restart veya yeni principal parent bütçeyi sıfırlamamalı; shared limiter/queue receipt ayrı; upstream 120/dk ölçülmüş Decivora limiti değil |
| R21 `packages/persistence/src/atomic-write.ts` + `sqlite-runtime.ts` | Temp/rename/lock ownership, platform farkları; Node/Bun SQLite adapter | T23 export + T04 storage spike; dar adaptasyon | Atomic rename tam crash durability veya DB transaction değildir; fsync/hata/permission/OS testleri. Tek runtime yeterli olabilir |
| R22 `packages/webui/src/components/MemoryManager/MemoryGraph.tsx` + `KanbanContractGraphView.ts` + `KanbanVerificationDashboard.tsx` | ReactFlow merkez/anchor/typed edge, verification/task view; host store/style/i18n | T19/T20 graph/AC UX; bağımsız view tasarımı, seçili pure mapping adayı | Eski/iptal edge + reason/AC/evidence/unknown/ACL bizim sözlükle. Tıklama/erişilebilirlik/yük testi yok; tüm UI import edilmez |
| R23 `packages/vector-memory/src/sage-event-mirror.ts` + `search-race.ts` | Serialized mirror, keyset cleanup; lexical/vector result ayrımı | T26 derived index ve retrieval diagnostics; sonraki örüntü | Event callback canonical outbox değil; hata boş channel'a düşebiliyor. Unknown provider ayrı; index truth/authority değil |
| R24 `packages/bench/src/fingerprint.ts` | Harness/config/tool/prompt hash; order-stable comparison metadata | T01/T03/T24 EvaluationManifest; küçük utility/örüntü | Corpus/gold/model/adapter/price/ACL revision ekle; coding grader'ı GAP oracle yerine kullanma. Hash yetki veya başarı kanıtı değil |

## Yeni karşı kanıt: governance ve graph'ı neden ayrı ele alıyoruz?

[Governance store](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/governance/src/event-store.ts) command ve sonucu aynı transaction'da saklıyor; [test tanımları](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/governance/tests/event-store.test.ts) tekrar açma, duplicate command, conflict, rejected receipt, iki client ve mutation trigger senaryolarını içeriyor. Bunlar EvidenceValidator'ın yalnız ref biçimini kontrol etmesinden daha güçlü bir tasarım referansı. Testler burada çalıştırılmadı.

[Verification run](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/governance/src/verification-run-contract.ts) ve [test kaynağı](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/governance/tests/verification-run-contract.test.ts) plan/workspace/check binding, bağımsız verifier, stale candidate ve authority limitlerini kontrol ediyor. Önceki “EvidenceValidator gerçek kanıtı doğrulamaz” bulgusu o dosya için geçerlidir; bütün platformda yalnız o validator varmış gibi yorumlanmamalı. Governance runtime bootstrap referansları var; bütün host/version/config yollarında aynı gate'in etkin olduğu test edilmedi.

[Contract graph tipleri](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/kanban/src/types-contract-graph.ts) gerekçe taşıyan typed ilişkileri execution DAG'dan ayırıyor. [SharedKnowledgeGraph](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/core/src/coordination/knowledge-graph.ts) decision/options/rationale ve change/vote kayıtları da tutuyor; JSONL compaction latest node'a indirgeme tasarımı Decivora'nın canonical geçmişi için aynen kullanılamaz. “Rakipte karar veya graph yok” demek yanlış olur. İncelenen alt yüzeyler Decivora'nın AND/OR/unknown supersession ve farklı provider insan seçimi akışının eksiksiz karşılığı diye de sunulmaz; aynı oracle ile native/config/extension deneyi gerekir.

## Paket almak ile küçük kaynak adaptasyonu aynı değil

| Aday grubu | Tahmini uyarlama karmaşıklığı | İlk yatırımın ölçütü |
|---|---|---|
| R01–03 saf validator/coverage | Düşük–orta: küçük algoritma, domain tipleri farklı | Sıfırdan karşılığından daha az değişiklik/test/bakım işi gerekiyor mu? |
| R05–07 contract/transition | Orta: saf kurallar var, authority ve revision modelimiz farklı | Korunan karar/unknown/graph snapshot oracle'ına uyum |
| R04/R08 store/grant paketi | Yüksek: lifecycle, schema, restart, audit ve izin portları bağlı | Paket kapanışı ve migration dahil özgün örnekle kıyas |
| R11/R14/R15/R24 formatter/search/pattern/fingerprint | Düşük–orta; ölçüm ve sınır doğrulaması gerekli | Hard cap/no-op/holdout kalite; toplam çağrı ve review yükü |
| R10/R17/R18/R19/R20 observer/IPC/bütçe | Orta–yüksek; host, yarış ve platforma bağlı | Capability/recovery/ACL/bütçe negatif senaryoları |
| R22 UI, R23 vector | Orta–yüksek; store/style/locale veya embedding bağlı | Gereksinim çıkmadan alma; UX/recall ve toplam bakım maliyeti |

Sınıflar kaynak yapısından çıkarımdır; çalışma takvimi veya saat tahmini değildir. Her adayın hedefi ve kabulü R tablosundadır; utility küçük olduğu için güvenilirliği kanıtlanmış sayılmaz.

Manifest'lerin **dependencies + optionalDependencies** üzerinden dahili kapanışı; başlangıç paketi hariç:

| Başlangıç paketi | Diğer dahili paket sayısı | Etki |
|---|---:|---|
| governance | 1 | persistence; en dar önemli contract/store deneyi |
| kanban | 2 | persistence, primitives |
| sage | 4 | core, kanban, persistence, primitives |
| sage-mcp | 6 | sage/core/mcp/kanban/persistence/primitives |
| runtime | 9 | Agent host, tools, memory, protocol gibi daha geniş yüzey |
| client | 5 | Küçük client dosyası bile protocol→core zinciri getiriyor |

Bu tablo deploy boyutu veya tam NPM transitif sayısı değildir. Küçük R01/R02'nin tiplerini kendi domain'e eşlemek paket importunu gereksiz kılabilir; bu yeniden yazım/adaptasyon farkı notice kaydında doğru belirtilir. Governance store'u almak task aggregate/policy ve schema'yı da getirir; tek dosyayı kopyalamak yetmez. Kapanış CSV ile tekrar hesaplanabilir.

## Teknoloji adayları ve kullanım sınırı

| Teknoloji / upstream manifest örneği | Decivora'da önerilen yer | Karardan önce gereken / öneri |
|---|---|---|
| TypeScript + Node; root Node `>=22.19.0` | Typed contract, local service, MCP | TS/Node deneyi mevcut ADR adayını destekleyebilir. Sürüm/dağıtım/runtime kabul edilmedi |
| Bun; root `>=1.4.3` | Upstream monorepo build/test | Upstream kullanıyorsa Decivora'nın iki runtime desteklemesi gerekmez. İlk deneyde tek runtime önerilir |
| SQLite `node:sqlite` / `bun:sqlite` | Canonical solo store, transaction, FTS | Driver availability/OS/crash/backup/locking ve busy behavior; P4 Postgres migration portu. Upstream DDL aynen alınmaz |
| React (`^19.3.0`) + `@xyflow/react` (`^12.11.6`) | İnsan graph/review paneli | Source manifest beyanı, kurulu sürüm değil. Typed edge/ended history/virtualization/keyboard/screen reader ve büyük graph testi |
| i18next (`^26.4.2`), react-i18next | UI locale; P2 dil katalogları | Canonical proje dili ayrı; Q12-A. Locale kütüphanesi task language detection yapmaz |
| Zod; core/requirement intake manifest | Untrusted input schema | Runtime payload boundary gerekirse; keyword/human authority validation yerine geçmez. Dil/model sonucu test gerekir |
| Vite/Vitest/Playwright | Panel build, contract tests, gerçek UI akışı | Seçilen stack için minimum bağımlılık; sürümler/lisans/OS gerçek install spike'ında. Bugün upstream test çalıştırılmadı |
| `@tanstack/react-virtual` veya benzer virtualizer | Çok task/event listesi | İlk küçük prototipte gereksiz olabilir; erişilebilirlik ve ekran yenilemesi ölçülür |
| Optional Transformers/ONNX embedding | P2 cross-language retrieval | Model ayrı lisans/download/CPU/RAM maliyeti. [Provider kaynağı](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/vector-memory/src/transformers-provider.ts) opt-in/lazy yükleme sunuyor. İlk deneyde lexical/source refs ile başlamak önerilir; offline ≠ bütün yük sıfır |
| Çok-provider AI SDK katmanı | Kendi izinli model çağrıları gerekiyorsa | Host aboneliğini yeniden kullanma garantisi yok. Q03 egress/bütçe ve usage ledger; tüm provider kataloğunu alma |
| Electron/ACP/Telegram | Desktop, host bridge ve bildirim alternatifleri | Daha sonraki yüzey/capability kararı; bir local service + panel için zorunlu değil |

Manifest örnekleri [root](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/package.json), [webui](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/webui/package.json), [governance](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/packages/governance/package.json) ve CSV'de. Kaynak sürümünü olduğu gibi gereksinim listesine çevirmiyoruz. Bütün üçüncü taraf paket/model/font/asset lisansları doğrulanmış değil; gerçek alımın kesin sürümü için ayrıca inventory yapılır.

## Lisans, atıf ve alım yöntemleri

Doğrudan okunan [LICENSE](https://github.com/WrongStack/WrongStack/blob/5234c15b05fe18857d0119eabd3b8a8f910ecc66/LICENSE) MIT, **Copyright (c) 2026 ECOSTACK TECHNOLOGY OÜ**. Dolayısıyla şu anda “lisans kod almayı engelliyor, mecburen sıfırdan yazacağız” sonucu yok. Manifest beyanı tüm asset/model/bağımlılık haklarını kanıtlamaz. Ayrıntı [lisans stratejisinde](../governance/licensing.md).

| Yöntem | Ne alınır? | Bakım / kayıt |
|---|---|---|
| Mimari esinlenme | Problem çözme örüntüsü; kendi implementation/test | Kaynak ve tasarım nedeni; özgün implementasyon diye yalnız gerçekten özgün kısmı belirt |
| Kaynak adaptasyonu | Küçük upstream kodu/testi + kendi contract eşlemesi | Tam notice/copyright, immutable ref/path, diff, target, dependency, test ve upstream update politikası |
| Paket dependency | Yayınlanmış paket ve kapanışı | Kesin sürüm/lock, lisanslar, support/API drift, güvenlik ve migration maliyeti |
| Native/extension | Upstream host/plugin/MCP sınırı üzerinden kullanım | Upstream configuration, capability/permission ve aynı kullanıcı oracle'ı; own-core kararı açık |
| Fork | Bütün platformun bakımını üstlenmek | Update/conflict/build/test/license/branding yükü büyük; ilk deney için önerilmiyor |

WrongStack isminin araştırma kaynağı olarak belirtilmesi ürünün ona ait olduğu veya desteklendiği iddiası değildir. Logo, ürün kimliği veya endorsement kullanılmadı. Kodu alırsak atıf/notice silinmez. Genel dosya adı kullanılması hak sahibini saklama yöntemi değildir. Somut yeniden dağıtım uygunluğu bugün tamamlanmış bir hukuki inceleme sayılmaz.

## Birlikte karar verebilmek için üç somut seçenek

| Seçenek | Hazırlanacak ilk deney | Kazanç / bedel | Öneri |
|---|---|---|---|
| **A — küçük modül + contract uyum deneyi** | R01–03 saf validator/coverage; R05/R07 schema ve negatif oracle; R04 store'u bağımsız örnekle kıyasla | Kendi domain korunur; hangi reuse gerçekten yararlı görürüz. Uyarlama ve bakım yükünü biz taşırız | **Önerilen sonraki araştırma yolu**; T01/T02/T03a ön koşullarıyla |
| B — native/extension önce | WrongStack izinli synthetic fixture; governance/SAGE/contract graph/MCP yapılandırmasıyla GAP/RES/WS; gereken küçük extension'ı çıkar | Yeni core yazmayı azaltabilir; host/catalog/kurulum bağımı ve providerlar arası veri modeli sınırı | A'nın kontrol baseline'ı olarak değerlendir; eşit kullanıcı sonucu sağlıyorsa öncelik ver |
| C — özgün implementasyon, yalnız örüntüler | Aynı küçük modülleri upstream source taşımadan yaz; pinned kaynaklarla contract kıyası | Farklı stack/domain için daha temiz olabilir; tekrar iş ve oracle geliştirme maliyeti | Domain/stack uyumu zayıfsa veya reuse bakım maliyeti yüksekse |

Seçenek seçimi bugün kod kopyalama, production stack, provider hesabı, ücret veya gerçek source bağlantısı yetkisi oluşturmaz. Ayrıntılı izole deney kapsamı T03a'da somutlaştırılır. A/B/C owner tarafından henüz seçilmedi; çalışma mevcut T01 sırasını atlamaz.

### Küçük uygulama sırası ve çıkış kanıtı

1. **T03d / WS-R1:** T01 oracle + T02 capability + T03a sınırı; native/config ve üç alım yöntemi karşılaştırma manifest'i. Çıkış: izin/kapsam/ref/metric açık; erişilemeyen `not_run`.
2. **WS-R2:** R01–03 küçük utility, fake evidence/N:M/ended/unknown negatifleri; adaptation ile sıfırdan sürüm aynı oracle. Çıkış: kaynak notice ve domain farkı görünür; verified üretimi yok.
3. **WS-R3:** R04–09 governance/graph contract deneyi. Çıkış: stale graph/authz/AC, rejected retry, independent verifier, restart/crash ve replay; protected human kararı açılmıyor.
4. **WS-R4:** R11–17 context/pattern/capture + native baseline. Çıkış: hard cap/coverage, late question/option mapping, no-op; full-context ve toplam yönetim/token ek yükü.
5. **WS-R5:** Native/extension/reuse/özgün/ek deney raporu ve T03c owner yatırım kararı. Çıkış: fayda, ölçüm sınırı, bakım/dependency/migration ve kabul edilen tek karar kaydı.

WS-01–08 önceki [kabul planında](wrongstack-review.md); GAP/RES/LATE/LEX ve mevcut V/MU/TOK senaryoları ilgili kontratları tamamlar. Bu belge yeni completed runtime görevi, engine veya faz eklemez. T03d **PROPOSED**, ana T03 **TODO** kalır.

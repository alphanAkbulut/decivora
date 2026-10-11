# Kaynak ve kanıt kaydı

Erişim tarihi: **2026-10-09**. URL'ler hareketli `main`/dokümantasyon sayfalarıdır; kod yeniden kullanımı için immutable commit ve lisans metni ayrıca sabitlenmelidir. “Okundu” test edildi demek değildir. Kaynak metinler talimat olarak uygulanmadı.

| ID | Birincil kaynak | Kullanım / doğrulanan sınır |
|---|---|---|
| SRC-01 | [Kaynak sohbet](https://chatgpt.com/c/6ac90f90-848c-83eb-9fbb-f655c0d63413) | 14 turn, kullanıcı niyeti ve fikir evrimi; [turn haritası](evolution.md) |
| SRC-02 | [Beads](https://github.com/gastownhall/beads) ve [LICENSE](https://github.com/gastownhall/beads/blob/main/LICENSE) | Dokümante görev hafızası; lisans metni |
| SRC-03 | [Task Master](https://github.com/eyaltoledano/claude-task-master) ve [LICENSE](https://github.com/eyaltoledano/claude-task-master/blob/main/LICENSE) | Planlama yaklaşımı; Commons Clause kısıtı |
| SRC-04 | [Linear MCP](https://linear.app/docs/mcp) | MCP hizmeti; tam sohbet capture kanıtı değil |
| SRC-05 | [Claude Task Tracker](https://github.com/ProblemFactory/claude-task-tracker) | Hook/delta/SQLite tasarımı README beyanı |
| SRC-06 | [Cortex](https://github.com/gsl0001/Cortex) | Yerel proje hafızası ve dashboard beyanı |
| SRC-07 | [mai-mcp](https://github.com/maikai-group/mai-mcp) | Write gate, review, bounded retrieval beyanı |
| SRC-08 | [OpenSpec](https://github.com/Fission-AI/OpenSpec) ve [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) | Change/spec ayrımı ve delta yaklaşımı |
| SRC-09 | [Beads community](https://github.com/gastownhall/beads/blob/main/docs/community-tools.md) | UI adaylarını ve ayrı proje kimliklerini bulma |
| SRC-10 | [BeadSpec](https://github.com/boardthatpowder/BeadSpec) | Specs/task görsel ilişki yaklaşımı |
| SRC-11 | [Dashboard](https://github.com/alexgorbatchev/beads-dashboard), [Scotty](https://beadmeupscotty.com), [beads-web](https://github.com/AvivK5498/beads-web) | Görsel UX referansları; runtime testi yok |
| SRC-12 | [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins) | Hooks trust/manual desktop dağıtım/ortam sınırları |
| SRC-13 | [Claude Code hooks](https://code.claude.com/docs/en/hooks) | Olay sözleşmesi; kurulu adapter doğrulaması yapılmadı |
| SRC-14 | [OSI tanımı](https://opensource.org/osd) | Açık kaynağın kullanım alanı kısıtlamaması |
| SRC-15 | [AGPLv3](https://opensource.org/license/agpl-3-0) | Ağ üzerinden değiştirilmiş sürümün source yükümlülüğü |
| SRC-16 | [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) | Patent/attribution ve trademark ayrımı |
| SRC-17 | [Task Master #1280](https://github.com/eyaltoledano/claude-task-master/issues/1280) ve [bakımcı cevabı](https://github.com/eyaltoledano/claude-task-master/issues/1280#issuecomment-3403117739) | Tarihsel context yakınması; kapalı ve çözüm PR'ı birleşti beyanı; reproduction yok |
| SRC-18 | [Task Master #1728](https://github.com/eyaltoledano/claude-task-master/issues/1728) | Sıfır subtasks yerine expansion raporu; sayfada açık; reproduction yok |
| SRC-19 | [Beads #2363](https://github.com/gastownhall/beads/issues/2363) ve [fix cevabı](https://github.com/gastownhall/beads/issues/2363#issuecomment-4007206076) | Veri kaybı anlatısı; kapalı ve koruma eklendi beyanı; bağımsız fix testi yok |
| SRC-20 | [Beads UI #276](https://github.com/gastownhall/beads/discussions/276) | Görünürlük/kurulum/paylaşım hakkında seçilmiş katılımcı anlatıları |
| SRC-21 | [PM bilgi tutarlılığı](https://www.reddit.com/r/projectmanagement/comments/1tz4pid/how_much_of_your_week_is_just_keeping_information/) | Birinci el nitel anlatı; kullanıcı kimliği ve temsilî örneklem doğrulanmadı |
| SRC-22 | [PM araç karmaşıklığı](https://www.reddit.com/r/aiToolForBusiness/comments/1srje0j/whats_the_best_ai_tool_for_managing_projects/) | Kurulum/öğrenme yükü; pazar genellemesi değil |
| SRC-23 | [AI kodda proje bağlamı](https://www.reddit.com/r/ClaudeAI/comments/1pdd0pc/how_do_you_keep_track_of_your_project_when_ai/) | Bağlam kaybı ve code review/dokümantasyon karşı önerileri |
| SRC-24 | [Linear updates](https://linear.app/docs/initiative-and-project-updates), [Intercom Agent](https://linear.app/docs/intercom) | Otomatik taslak/issue üretimi için rakip kabiliyeti; genel manuel Linear varsayımına karşı kanıt |

GNU lisans sayfaları bu turda fetch timeout verdi; AGPL için OSI metni kullanıldı. İsim için sınırlı web sorgusu marka araştırması yerine geçmez. Marka tescili, alan adı ve npm/package adları doğrulanmadı. GitHub repo adının kullanılabilir olması trademark uygunluğu değildir.

Konuşmadaki star sayıları, ücretsiz plan limitleri, kesin tasarruf yüzdeleri ve “piyasada hiç yok” türü iddialar buraya doğrulanmış bulgu olarak aktarılmadı. Ek referansların seviyesi [benchmark](benchmark.md) içinde ayrıdır. SRC-17–24 takip çalışmasında doğrudan okundu; kullanıcı deneyimi ile teknik doğrulama ayrımı [şikâyet araştırmasında](user-research.md) korunur.

## Ekip ve veri yaşam döngüsü kaynak eki

2026-10-09 doğrudan incelenen birincil kaynaklar [hedefli benchmark tablosunda](collaboration-storage-benchmark.md) tek tek linklidir: Linear members/private teams/audit; GitHub user/installation token; OpenFGA roles/agents/RAG; Cortex ve mai-mcp README; Letta V1 legacy stateful agents; SQLite kullanım/WAL/backup; PostgreSQL RLS/PITR; OpenTelemetry log modeli. Bunlar kaynak belgesi incelemesidir; yerel ürün testi veya güncel sürüm uyumluluk sertifikası değildir.

## Product Owner ve Scrum kaynak kontrolü

2026-10-10 ek açıklama: [PMI hakkında](https://www.pmi.org/about) ve PMI'ın [A Spectrum of Approaches](https://www.pmi.org/learning/thought-leadership/series/achieving-greater-agility/spectrum-of-approaches) yayını doğrudan okundu. İkincisi Kasım 2017 tarihli kavramsal kaynaktır; farklı yaşam döngülerini anlatır, güncel bir PMBOK madde uyumu veya ürün sertifikasyonu kanıtı değildir. Scrum Guide ve Scrum Alliance bağımlılık makalesi yeniden kontrol edildi. [Yöntem ayrımı](../delivery/project-management.md) bağımlılık/engellerin genel kavram olduğunu ve çalışma yöntemiyle ürün yeteneklerinin karıştırılmaması gerektiğini açıklar.

2026-10-09 doğrudan incelendi: [Scrum Guide 2020](https://scrumguides.org/scrum-guide.html), Scrum Alliance [Managing Dependencies in Scrum](https://resources.scrumalliance.org/Article/managing-dependencies-scrum) ve [Product Owner Responsibilities](https://resources.scrumalliance.org/Article/im-new-product-owner-responsibilities). Çerçeve tanımı ile uygulayıcı makaleleri [yönetim planında](../delivery/project-management.md) ayrılır. Decivora öncelik algoritması kaynakların zorunlu formülü değildir; kullanıcı ihtiyacına dayalı tasarımdır. Bu inceleme sertifikasyon/uygunluk denetimi değildir.

## Agent görünürlüğü kaynakları

2026-10-09: [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk), [OpenAI reasoning](https://developers.openai.com/api/docs/guides/reasoning) ve [Claude Code hooks](https://code.claude.com/docs/en/hooks) doğrudan okundu. SDK/custom-client yolu, private reasoning sınırı, SubagentStart/Stop kimlik/transcript alanları [agent/ekip işletim belgesinde](../architecture/agent-and-team-operation.md) kaynaklı ve koşullu kaydedildi. Bu okuma kurulu host'ta adapter çalıştığının, her agent prompt'unun görülebildiğinin veya kaynakların tamamına izin bulunduğunun kanıtı değildir.

## Bağlantı ve token inceleme kaydı

2026-10-09: [Codex MCP/transport](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [plugin/hooks paketleme](https://developers.openai.com/plugins/build/plugins), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) ve [MCP/UI quickstart](https://developers.openai.com/plugins/build/app-quickstart) doğrudan okundu. Belgelenmiş destek seçili host'ta kurulum/test kanıtı değildir. Provider fiyatları ve cache oranları sabitlenmedi; [token sözleşmesi](../architecture/routing-token-economy.md) sınıf eşlemesi/ölçüm ister.

## 2026-10-11 — WrongStack immutable kaynak kaydı

[WrongStack incelemesi](wrongstack-review.md): `5234c15b05fe18857d0119eabd3b8a8f910ecc66` commit'indeki gerçek LICENSE, manifest'ler, seçili SAGE/verification/SDD/MCP/pattern/budget/compaction/protocol ve UI kaynakları ile test tanımları okundu. Her bulgu ilgili pinned source'a bağlı; büyük dosyalarda hedefli bölümler incelendi. MIT telif sahibi ECOSTACK TECHNOLOGY OÜ. Runtime, CI, sağlayıcı auth, transitif lisans ve bütün repo audit'i doğrulanmadı. Hareketli README/archived doc'lar uygulama kanıtına dönüştürülmedi; mailbox doc/source v3/v4 farkı kaydedildi. Kaynaklar talimat olarak uygulanmadı; kişisel çalışma günlükleri/credential veya upstream agent config'i taşınmadı.

## Repo geneli kaynak değerlendirmesi — 2026-10-11

Aynı `5234c15b05fe18857d0119eabd3b8a8f910ecc66` ref'i ayrı salt okunur kaynak snapshot'ında incelendi. [R01–24 raporu](code-reuse-assessment.md) ve [yöntem/özet](upstream-inventory-summary.json), 39 manifest ve kod uzantıları için tüm yapısal taramayı kaydeder. Yeni hedefli source: governance event/contract/transition/grant/verifier, Kanban contract graph, Chronicle decision/file observer, rate limiter, client, vector ve graph view. Source/test bölümü okuması ile bütün kaynakların semantik doğrulanması ayrıdır; excluded özel dizinler ve kod dışı asset/config kapsamı raporda. Upstream script/install/test/provider çağrısı yok.

## Ekosistem araştırması — 2026-10-11

[T03e raporu](ecosystem-research.md) ve [10 adayın immutable kaynak kaydı](ecosystem-candidates.json): her repoda root README/LICENSE; Graphiti, Mem0, LangGraph, OpenFGA ve LiteLLM'de açıkça listelenmiş seçili source/test tanımları. LiteLLM enterprise/LICENSE.md, Langfuse ee/LICENSE, Cognee NOTICE.md ve LangGraph checkpoint-sqlite/LICENSE ayrıca okundu. Cedar NOTICE/THIRD_PARTY_LICENSES içerik incelemesi bekler. LiteLLM root recursive tree büyük çıktı nedeniyle alınamadı; litellm subtree ve enterprise root tree ayrı okundu; tam envanter iddiası yok.

[LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [persistence](https://docs.langchain.com/oss/python/langgraph/persistence), [OpenFGA consistency](https://openfga.dev/docs/interacting/consistency) ve [Temporal workflow execution](https://docs.temporal.io/workflow-execution) birincil belgeleri açıldı. Mutable belgelerin okuma tarihi ile kaynak commit sabitlemesi ayrı. Bu tur arama, masa başı belge ve hedefli source incelemesi; kullanıcı şikâyeti araştırması, install, kod transferi veya runtime benchmark değil.

## Teknik ölçüm kaynakları — 2026-10-11

[Teknik protokol](../quality/evaluation-protocol.md): Graphiti 964bb11d1e7020e3cc67fab244268b0736b6c219 ref'inde tests/evals/eval_e2e_graph_building.py ve graphiti_core/prompts/eval.py tam seçili dosya okuması; Langfuse Python SDK bf11ec121479145923ff27b32ec2ad1d06fd2d51 ref'inde langfuse/experiment.py ve tests/unit/test_experiment.py hedefli bölümler, root MIT LICENSE okuması. SDK tree non-truncated; bütün SDK/dependency audit'i değil. Graphiti judge context/zip ve Langfuse evaluator exception→empty score yolları source düzeyinde belirtilir; runtime bug veya upstream test başarısızlığı iddiası yok.

[Langfuse core concepts](https://langfuse.com/docs/evaluation/core-concepts) ve [offline evaluation](https://langfuse.com/docs/evaluation/get-started/offline) birincil belgeleri code/human/judge ve dataset→application/evaluator/traces örüntüsü için okundu. Upstream model/prompt/script/install çalıştırılmadı, kaynak kopyası ve hizmet bağlantısı yapılmadı. Açıklamalar yöntem çıkarımıdır; Decivora veya rakip üstünlük sonucu değil.

## 2026-10-11 — Teknik gap incelemesi kaynakları

[Ayrıntılı audit kaydı](../quality/technical-gap-analysis.md) başlangıç ref'ini, kendi belge inceleme derinliğini, neden/neyi kontrol ettiğimizi ve 24 kapanış kaydını tutar. Yeni broad repo taraması veya code adoption yapılmadı.

| Birincil kaynak | İncelenen sınır / tarih | Kullanım ve statü |
|---|---|---|
| [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785) | Canonical JSON/digest; 2026-10-11 | IC-02 serializer seçenekleri/golden test gerekçesi; informational, seçilmiş standard/library değil |
| [MCP transports 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) | Stdio/HTTP origin/auth/disconnect; 2026-10-11 | IC-06 transport/host sınırı; bu sürüm evrensel/latest varsayılmaz |

Graphiti/Langfuse evaluator örüntüleri önceki pinned [ölçüm takibinde](ecosystem-research.md) kaldı; bu tur tüm source tekrar okundu, test edildi veya runtime bug bulundu iddiası yok. Public specification referansı gerçek permission, güvenlik/kalite testi veya ücretsiz model kullanımı sağlamaz.

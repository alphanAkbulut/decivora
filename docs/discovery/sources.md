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

2026-10-09 doğrudan incelendi: [Scrum Guide 2020](https://scrumguides.org/scrum-guide.html), Scrum Alliance [Managing Dependencies in Scrum](https://resources.scrumalliance.org/Article/managing-dependencies-scrum) ve [Product Owner Responsibilities](https://resources.scrumalliance.org/Article/im-new-product-owner-responsibilities). Çerçeve tanımı ile uygulayıcı makaleleri [yönetim planında](../delivery/project-management.md) ayrılır. Decivora öncelik algoritması kaynakların zorunlu formülü değildir; kullanıcı ihtiyacına dayalı tasarımdır. Bu inceleme sertifikasyon/uygunluk denetimi değildir.

## Bağlantı ve token incelemesi

2026-10-09: [Codex MCP/transport](https://learn.chatgpt.com/docs/extend/mcp?surface=cli), [plugin/hooks paketleme](https://developers.openai.com/plugins/build/plugins), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) ve [MCP/UI quickstart](https://developers.openai.com/plugins/build/app-quickstart) doğrudan okundu. Belgelenmiş destek seçili host'ta kurulum/test kanıtı değildir. Provider fiyatları ve cache oranları sabitlenmedi; [token sözleşmesi](../architecture/routing-token-economy.md) sınıf eşlemesi/ölçüm ister.

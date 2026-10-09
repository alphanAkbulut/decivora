# Benchmark matrisi

İnceleme: 2026-10-09. **D = Documented Capability** (birincil belgede okundu), **V = Verified Capability** (sürümü sabitlenmiş testte çalıştırıldı), **U = Unverified**, **O = Observed Limitation** (tekrarlanabilir gözlem). Bu turda V veya O sonucu üretilmedi. Belgede bir özelliğin bulunmaması, üründe olmadığına kanıt değildir. Star sayısı, README iddiası ve tek issue pazar talebini/kaliteyi kanıtlamaz.

| Araç / kaynak | D: incelenen yaklaşım | Decivora'ya ders | U: sıradaki test | Lisans/reuse durumu |
|---|---|---|---|---|
| [Beads](https://github.com/gastownhall/beads) | Agent görev hafızası ve bağımlılıklar | Tipli ilişki, hazır iş seçimi | Karar gerekçesi AND/OR ve repo olmadan araştırma | [MIT metni](https://github.com/gastownhall/beads/blob/main/LICENSE) görüldü; alımda commit sabitle |
| [Task Master](https://github.com/eyaltoledano/claude-task-master) | PRD'den görev ayrıştırma, MCP araçları | Hazır AC, task decomposition ve minimal tool profile | Gereksiz alt görev, context maliyeti | [MIT + Commons Clause](https://github.com/eyaltoledano/claude-task-master/blob/main/LICENSE); kod/prompt kopyalama yok |
| [Linear](https://linear.app/docs/mcp) | MCP ile proje/issue erişimi | Hızlı review ve görsel tutarlılık | Sohbetten task'a yönetim süresi; kapsam yetkileri | Hizmet koşulları; API/UX araştırması, kod alımı yok |
| [Claude Task Tracker](https://github.com/ProblemFactory/claude-task-tracker) | Claude Code hook/transcript tabanlı pasif task inference, SQLite ve dashboard | Delta capture/checkpoint | Partial completion, ret, yanlış proje, Codex uyumluluğu | README MIT diyor; alım öncesi tam lisans/commit |
| [Cortex](https://github.com/gsl0001/Cortex) | Yerel SQLite hafıza, proje operasyonu, graph, autonomy ve bounded context | Entegre kontrol merkezi ve bilgi bütçesi | Onaylı karar değişince eski task gerekçeleri ne oluyor? | Repo MIT gösteriyor; bileşen incelemesi gerekli |
| [mai-mcp](https://github.com/maikai-group/mai-mcp) | Search-before-write, novel/extends/supersedes, review queue, bounded reads | Reconciliation kapısı ve evidence lineage | Aynı fixture'da çelişki ve obsolete precision | Repo MIT gösteriyor; bağımlılık koşulları ayrı |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) | Current specs ile proposed change/delta ayrımı | Proposal→approval→canonical akışı | Task/prompt downstream etkisi nasıl korunuyor? | Repo MIT gösteriyor; bu çalışmada kod alınmadı |
| [BeadSpec](https://github.com/boardthatpowder/BeadSpec) | OpenSpec/Beads görsel ilişkisi, graph ve insan karar kuyruğu | Spec/task birlikte review | Çoklu gerekçe ve pasif sohbet capture | Kod alım lisans incelemesi bekliyor |
| [Beads Dashboard](https://github.com/alexgorbatchev/beads-dashboard) | Yerel görsel task/board yaklaşımı | Hafif dashboard, çok proje gezinme | Gerçek kurulum, refresh ve veri uyumu | Hedef commit lisansı kontrol edilecek |
| [Bead Me Up, Scotty](https://beadmeupscotty.com) | Board, list, epic, dependency graph | Çoklu proje ve insan/agent attribution | Sabit panel ihtiyacı ve review maliyeti | Demo görülmesi kod kullanım hakkı değildir |
| [BeadBoard](https://github.com/gastownhall/beads/blob/main/docs/community-tools.md) | Katalogda agent koordinasyonu ve dependency graph | Handoff ve çalışma çakışması görünürlüğü | Ortak hafıza ile orchestration ayrımı | Katalog beyanı; tam repo/lisans testi yok |
| [Lista Beads](https://github.com/gastownhall/beads/blob/main/docs/community-tools.md) | Katalogda VS Code paneli ve stale issue yönetimi | Çalışma ekranında sabit görünürlük | Codex desktop paneliyle aynı kabiliyet değil | Hedef extension lisansı incelenecek |
| [beads-web](https://github.com/AvivK5498/beads-web) | Kanban ve çoklu proje görsel katmanı | Sadece yeni bir board üretmenin yeterli olmaması | Fork/ürün kimliği ve sürüm farkı | Katalogdaki diğer forkla karıştırma |

mai-mcp'nin bounded read ve supersession beyanı özellikle yakın bir rakip davranışıdır; “karar farkındalığı yalnız bizde” sonucu çıkarılamaz. Claude Task Tracker, ProblemFactory projesidir; Anthropic'in resmî ürünü olarak sunulmaz. Bugünkü Beads storage yaklaşımı eski konuşmadaki sürüm varsayımlarıyla eşitlenmez.

## Konuşmada geçen ek referansları kaybetmeme havuzu

| Referans | Neden saklandı | Bu turdaki kanıt seviyesi |
|---|---|---|
| [Jira + Rovo](https://www.atlassian.com/software/jira/ai) | Kurumsal capture ve bilgi akışları | U; ayrıntılı ürün testi yapılmadı |
| [ClickUp Brain](https://clickup.com) | Doküman/görev/sohbet ortak alanı | U |
| [GitHub Projects](https://github.com/features/issues) + Copilot | Issue/PR tabanlı ilerleme | U |
| [Vibe Kanban](https://github.com/BloopAI/vibe-kanban) | Coding agent orchestration | U; konuşmadaki sonlandırılma iddiası yeniden doğrulanmadan kullanılmaz |
| [Claude Kanban](https://github.com/CjS77/claude-kanban) | Claude ile görsel task akışı | U |
| Agent Memory Hub | Oturum hafızası fikri | U; kaynak konuşmada benzersiz repo linki yok, kimlik araştırması bekliyor |
| Memorix | Çoklu agent hafızası fikri | U; aynı isimli projeler karıştırılmadan kimlik araştırılacak |
| [Codex for Claude Code](https://github.com/openai/codex-plugin-cc) | Agent handoff referansı | U; bu turda entegrasyon testi yok |

## Konuşmadaki kullanıcı şikâyetleri: araştırma ipuçları

[Task Master #1280](https://github.com/eyaltoledano/claude-task-master/issues/1280) context yükü, [#1728](https://github.com/eyaltoledano/claude-task-master/issues/1728) görev bölme, [Beads #2363](https://github.com/gastownhall/beads/issues/2363) veri kaybı anlatısı ve [UI tartışması](https://github.com/gastownhall/beads/discussions/276) kaynak konuşmada anıldı. Bu turda yeniden üretilmedi; güncel hata, sayı veya çözülme durumu iddia edilmez. Reddit PM/Linear tartışmaları da nitel kullanıcı araştırması ipucudur, temsili örneklem değildir. Dersler: context ölç, gereksiz task üretimini cezalandır, agent silme yetkisini sınırla, toplu ilişkili işlem sun.

## Karşılaştırmalı deney protokolü

P0'da aynı sentetik corpus'u Cortex, Claude Task Tracker, mai-mcp ve mümkünse Beads+UI ile çalıştır. Version/commit, OS, kurulum süresi, izinler, model ve fiyat tarihi kaydedilsin. Kod kurmadan önce lisans ve yürütme etkileri incelensin; gerçek kullanıcı projelerine bağlanılmasın.

Fixture görevleri: yeni fikir, duplicate, geri çekilen öneri, forgotten approval, false done, çoklu gerekçe, karar değişimi, crash/retry, iki proje ve prompt→execution. Her araç için **native / configuration / custom extension / unavailable / unknown** sonucu yaz. Onay tıklaması, manuel metin, token, elapsed time ve doğru state aynı kriterlerle ölçülsün. Custom geliştirme süresi ayrıca raporlansın.

Önerilen seçim sırası: önce Cortex/mai-mcp ile yakın domain kapsamını, Tracker ile pasif capture'ı kanıtla; sonra store/adapter reuse kararını ver. Şimdilik bağımsız domain çekirdeği önerilir; karşılaştırma sonuçları bunu değiştirebilir. Mevcut araç hedefi yeterince karşılıyorsa entegrasyon yolu geçerli başarıdır.

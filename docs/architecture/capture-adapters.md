# Capture adapters ve platform sınırları

Kontrol tarihi: 2026-10-09. **Documented**, üretici belgesinde bulundu demektir; bu repository için çalışan entegrasyon demek değildir.

| Yüzey | Belgelenmiş dayanak | Decivora planı | Bilinmeyen / test kapısı |
|---|---|---|---|
| Claude Code | [Resmî hooks referansı](https://code.claude.com/docs/en/hooks) olay ve transcript alanlarını tanımlar | Hook ingress + incremental transcript + MCP | Kurulu sürüm, alt agent, compaction, final output ve izin kapsamı |
| Codex | [Plugin paketleme](https://developers.openai.com/plugins/build/plugins) manuel desktop plugin hooks, trust ve script ortamı koşullarını açıklar | Desteklenen hook/session yüzeyi + MCP | CLI/IDE/desktop/Work aynı kabul edilmez; ayrı capability probe |
| ChatGPT Chat | Ortak plugin mimarisi tüm sohbet geçmişini verdiğini kanıtlamaz | İzinli connector kaydı veya açık import | Plan/hesap/host yazma yetkileri ve okunabilir mesaj kapsamı test edilmedi |
| Claude Chat | Bu çalışmada tam pasif geçmiş erişimi doğrulanmadı | Desteklenen connector veya açık import | Chat ile Code aynı transcript deposu kabul edilmez |
| GitHub | Daha sonraki kanıt/senkronizasyon adapter'ı | Önce read-only commit/PR evidence | Webhook yetkileri, imza ve retry sözleşmesi ayrı görev |

OpenAI belgeleri plugin hooks için güven incelemesi gerektiğini, web kurulumunun script'i yürütme ortamına taşımadığını ve hook içeren plugin'lerin public directory uygunluğunda sınır bulunduğunu söylüyor. Dağıtım tasarımını buna göre doğrula; kaynak kodunda event adı görmek dağıtılan her sürümde erişim kanıtı değildir. Bu oturumdaki `read_thread` aracı Decivora'nın dağıtılabilir genel API yeteneği olarak varsayılamaz.

## Adapter sözleşmesi

Çok-agent gözleminde her capability ayrı raporlanır: agent identity, parent run, task input, tool events, artifacts, usage, stop ve backfill. [Agent/ekip işletim belgesi](agent-and-team-operation.md) documented Codex SDK ve Claude Code subagent hook yollarını, görünmeyen prompt/özel muhakeme sınırını ve AGT-01–06 testlerini tanımlar. Agent'ın bildirimi verified sonuç değildir; observer kimliği ile observed actor karıştırılmaz. SDK üzerinden kontrol edilen run'ların görünürlüğü bütün mevcut desktop oturumlarına erişim garantisi sayılmaz.

`capabilities()` → source_surface, provider_version, supported_events, transcript_access, historical_backfill, coverage_limitations, consent_state.

`collect(cursor)` → normalize edilmiş source events, next_candidate_cursor, gap markers; cursor storage commit'ten sonra kesinleşir. `health()` → last_seen, last_durable, backlog, dropped/failed count, unsupported reason. `disconnect()` → yeni capture'ı durdurur; storage retention politikasını değiştirmez.

Mesaj role, source ID, session, thread parent, timestamp, edit revision, tool/execution ilişkisi, redaction durumu ve content reference korunur. Partial stream bir tamamlanmış mesaj sayılmaz. Turn-end/idle/debounce tetiklemesiyle batch yapılır; session-end gelmeyebilir, bu nedenle yalnız kapanış hook'una güvenilmez. Boyut limiti aşılırsa chunk zinciri ve işlenmemiş kalan bölüm görünür tutulur.

## Bir defalık kurulum; kalıcı garanti değil

Kullanıcı adapter'a açık proje binding'i ve izin verir. Kısa agent kuralı “actionable bilgiyi kaydet, kanıt ekle, scope için onay al” der. MCP agent'ın aktif yazma yolu, hooks pasif sinyal, reconciliation kaçanların kontrolüdür. Skill tek başına eksiksiz yakalama garantisi vermez.

Proje belirsizse global quarantine inbox kullanılır; kayıtlar kullanıcı seçiminden önce başka projeyle anlamsal aramaya sokulmaz. Workspace taşıma/branch/worktree değişikliği binding'i yeniden doğrular. Sistemin kendi capture/özet olayları origin marker ile feedback loop'tan çıkarılır.

## Faz ve fallback

P0 iki coding yüzeyinin teknik keşfi. P1b coding capture ve aynı sağlayıcı Chat→Code aktarımında provenance zinciri; desteklenmeyen normal chat için import. P2 sağlayıcılar arası sohbet sürekliliği ve izinli pasif yöntemler. Manuel import otomatik capture gibi pazarlanmaz. Tarayıcı DOM scraping kalıcı ürün mimarisi olarak benimsenmiş değildir.

Her adapter için: yeni mesaj, assistant final, tool failure, stop olmadan kapanma, offline, retry, edit, transcript rotation, compaction, truncation, subagent, başka proje ve redacted payload test edilir. Her test gerçek sürüm/build, hesap yetkisi, fixture ve sonucu kaydeder.

## Kurulum ve context protokolü

[Bağlantı sözleşmesi](connection-and-context.md) kullanıcı kurulumunu, MCP/capture/UI ayrımını, tools-only durumunu, stdio/HTTP adaylarını, health/disconnect ve delta context akışını somutlaştırır. Bağlı MCP, pasif capture kanıtı değildir. Kaynak iki yoldan gelirse model çağrısı/öneri duplicate olmamalı; CON-01–CON-08 ile doğrulanır. Paket/komut ve kurulu host testleri henüz yoktur.

## İlk deney için kaynak ile hedef erişimi ayrımı

[Güncel yön](../product/current-direction.md) T02'de iki coding yüzeyinin kaynak capability'sini korur; sınırlı deney için ayrıca **tek seçilmiş hedef** read-back fizibilitesi ister. Local read/GitHub erişimi ile source transcript erişimi ayrı izin ve coverage'dır. Generated artifact sinyali (ID/revision/hash/availability), güvenilir insan selection kaynağı ve upload observation/report alanları platform tarafından sunulmuyorsa unknown/manual fallback kalır.

Typed sentetik input ile state testi extraction/capture doğruluğunu kanıtlamaz. Import edilen assistant “user accepted” özeti insan principal yaratmaz. Hedef diff/refetch desteklenmedikçe durumun sürekli güncel kaldığı iddiası yok. GAP-01–10 ve T02d bu contract raporunu tamamlar.

## 19 Ekim — mevcut ilk Codex CLI kodu

[Seçilmiş exec JSONL adapter ve kullanım](../quality/codex-exec-capture-runtime.md) public assistant mesajlarını mevcut kaynak/review yoluna yazar. Explicit consent/project/thread/version, append-only prefix kontrolü ve source+cursor transaction uygulanmıştır. Bu bölüm yukarıdaki genel tasarımın dar uygulanmış alt kümesidir; `collect` caller-supplied snapshot alır, kendi başına dosya taramaz veya arka planda tail etmez. Masaüstü, user prompt capture, tam health UI ve gerçek host version probe açık.

19 Ekim ek uygulama: [App Server selected-thread read](../quality/codex-exec-capture-runtime.md#19-october--app-server-user-message-capture-and-bounded-polling) user/assistant metinleri ve bounded polling sağlar; kurulu0.162.0-alpha.17.2şema probe yapıldı, gerçek user thread readback yapılmadı. CLI exec ve App Server binding yüzeyleri karıştırılamaz. Normal UI source/model kurulumu hâlâ kapalı.

**19 Ekim gerçek selected-thread proof:** [readback001](../quality/codex-real-capture-001.md)6publicmesajı yalnız TEST'e kaydetti. Full-turn yanıtı1MiB'yi aştığından mevcut client turn metadata→one-item pagination kullanır; byte sınırı büyütülmedi.32sayfa/eksik item göstergesi var, kalıcı item cursor açık. Tek seferlik izin tüketildi; canlı polling/model paylaşımı açılmadı.

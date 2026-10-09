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

`capabilities()` → source_surface, provider_version, supported_events, transcript_access, historical_backfill, coverage_limitations, consent_state.

`collect(cursor)` → normalize edilmiş source events, next_candidate_cursor, gap markers; cursor storage commit'ten sonra kesinleşir. `health()` → last_seen, last_durable, backlog, dropped/failed count, unsupported reason. `disconnect()` → yeni capture'ı durdurur; storage retention politikasını değiştirmez.

Mesaj role, source ID, session, thread parent, timestamp, edit revision, tool/execution ilişkisi, redaction durumu ve content reference korunur. Partial stream bir tamamlanmış mesaj sayılmaz. Turn-end/idle/debounce tetiklemesiyle batch yapılır; session-end gelmeyebilir, bu nedenle yalnız kapanış hook'una güvenilmez. Boyut limiti aşılırsa chunk zinciri ve işlenmemiş kalan bölüm görünür tutulur.

## Bir defalık kurulum; kalıcı garanti değil

Kullanıcı adapter'a açık proje binding'i ve izin verir. Kısa agent kuralı “actionable bilgiyi kaydet, kanıt ekle, scope için onay al” der. MCP agent'ın aktif yazma yolu, hooks pasif sinyal, reconciliation kaçanların kontrolüdür. Skill tek başına eksiksiz yakalama garantisi vermez.

Proje belirsizse global quarantine inbox kullanılır; kayıtlar kullanıcı seçiminden önce başka projeyle anlamsal aramaya sokulmaz. Workspace taşıma/branch/worktree değişikliği binding'i yeniden doğrular. Sistemin kendi capture/özet olayları origin marker ile feedback loop'tan çıkarılır.

## Faz ve fallback

P0 iki coding yüzeyinin teknik keşfi. P1b coding capture ve aynı sağlayıcı Chat→Code aktarımında provenance zinciri; desteklenmeyen normal chat için import. P2 sağlayıcılar arası sohbet sürekliliği ve izinli pasif yöntemler. Manuel import otomatik capture gibi pazarlanmaz. Tarayıcı DOM scraping kalıcı ürün mimarisi olarak benimsenmiş değildir.

Her adapter için: yeni mesaj, assistant final, tool failure, stop olmadan kapanma, offline, retry, edit, transcript rotation, compaction, truncation, subagent, başka proje ve redacted payload test edilir. Her test gerçek sürüm/build, hesap yetkisi, fixture ve sonucu kaydeder.

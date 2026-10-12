# RECEIVER-001 — ilk native Luna/Low cevabı

**2026-10-12 · T03v scoped DONE yalnız deney/kayıt teslimi; model kabul kapısı geçmedi.** Kullanıcı ayrı chat'i açıp deneyi yapmamızı ve önce token/model/reasoning/context notlarını kaydetmemizi istedi. [Dispatch öncesi kaydı](receiver-execution-notes.md) main commit `0e9164b5c9f45b27963e89a1b57606e0f86f998d` üzerinden yayımlayıp geri okuduk; sonra tek yeni local projectless Codex chat oluşturduk.

[İlk tam final mesajı](model-runs/receiver-001-response.txt) · [Sonuç/usage/provenance](receiver-001-results.json) · [Tüketilmiş izin](../../examples/receiver-smoke/authorization.json) · [Frozen prompt](../../examples/receiver-smoke/prompt.txt) · [Ayrı authored oracle](../../examples/receiver-smoke/expected.json).

## Ne denedik, hangi modelle?

Configured `gpt-6-luna` + reasoning `low`, `create_thread` ile yeni projectless **Decivora RECEIVER-001 Luna Low** sohbeti. Parent history/fork/repo/oracle aktarılmadı; yalnız exact7950-byte prompt. Host `<codex_delegation>` wrapper ve source-thread metadata enjekte etti; system/developer/global host context'in sıfır olduğu garanti edilmez. Native çalışma önceki Chrome/Instant planıyla aynı koşul değildir.

Model/effort tool request'inde açık seçildi ve chat creation kabul edildi. **Actual provider backend identity/usage dönmedi.** Native UI'yi ayrıca görüntüleme aracı `com.openai.codex` erişimini güvenlik nedeniyle reddetti; ekran/screenshot doğrulaması yapılmadı veya kısıt aşılmadı. Tool config kabulünü provider telemetry doğrulaması diye sunmayız.

Bir initial turn, ilk final output, follow-up/retry/model-switch/paidAPI0. Full turn kaydında receiver tarafından tool call görünmedi; `create_thread` functionCallOutput host injection marker'ıdır, receiver'ın çağırdığı araç değildir. Hidden provider internal sampling/retry count unknown. Turn started **22:17:15**, completed **22:17:21 Europe/Istanbul**; host duration6660ms. Bu yalnız host turn süresi, API latency/ekonomi kıyası değil.

## Sonuç: geçerli JSON, geçersiz cevap sözleşmesi

Ham tam-message capture **1739 UTF-8 byte/1739 karakter**, SHA-256 `f17e134b68bec39cf7d5539cc812db7a87bd970a851aa30ecf2b43aaeaac4b03`. Newline eklenmedi; null/false değerleri değiştirilmedi. Kaynak provider transport byte'ları değil, app `read_thread` full final_answer text'idir.

`receiver_smoke.evaluate` **invalid_contract / invalid receiver abstention** ile durdu. İkinci proje `status: abstain` dediği halde readback nesnesi ve nonempty next_actions döndürdü. Kontrat abstain için readback:null/actions:[] gerektiriyordu. **Readback/action skorları null/unscored**, overall pass veya başarılı subset puanı üretilmedi. Parse JSON syntax geçti; schema/abstention kapısı geçmedi.

| Gözlenen çıktı | Yorum ve sınır |
|---|---|
| N01 eskiQ_STORE1/B stale, current2/A pending | Bu kısım doğru görünen source-backed tanı; whole-run başarı puanı değil |
| N01-m04 için request_target_verification | Bu mesaj future upload planı; preserved record listesinde yok. Prompt'un one-action-per-preserved-record scope'unu aşan ek öneri |
| N02 explicitQ_UI fixture mevcutken question_id/revision:null/state:unknown | BindlessB belirsizliği current sorunun bilinmesini ortadan kaldırmamalıydı; grup seviyesinde aşırı abstention |
| N02 abstain + readback/actions | Gözlenen ilk strict ret nedeni; raw onarılmadı |
| AC_SMOKE criterion_revision:"2" | String; sözleşme positive integer ister. Ayrı typed kusur, string→int coercion yapılmadı |
| AC_SMOKE not_run için preserve_history | Draft oracle test execution permission önerisi bekliyordu; semantic next-step uyumsuzluğu. Kontrat ret olduğundan metinsel tanı, scored model sonucu değil |
| task_verified/approved_real_decision:false ve upload reported_only | Görünen raw'da false-done/false real approval yok. Bütün schema/domain kapıları geçti demek değil |

Bu gözlemler root cause'un sadece model kapasitesi olduğunu kanıtlamaz: source-only genel descriptor sözleşmesi, native host/global talimatlar, reasoning/konfigürasyon ve belirsizlik granülaritesi ayrı adaylardır. Bir run'dan “Luna çalışmaz”, “High şart” veya “ürün yapılamaz” sonucu çıkarmayız.

## Aktarım katmanında ayrı bulgu

`wait_threads` compact latestAssistantMessage snapshot'ı full-message text ile eşleşmedi; null/false literal'ları kaybettirmiş görünen snapshot geçerli JSON da değildi. Bu **modelin JSON syntax hatası diye kaydedilmedi**. `read_thread` full, untruncated final_answer mesajı null/false değerlerini korudu ve geçerli JSON çıktı. Sonuç için yalnız bu full-message kaynak kullanıldı; yanlış summary'ye missing values eklenmedi.

İlk read_thread denemesinde maxOutputCharsPerItem32768 tool sınırına takıldı; desteklenen20000 ile salt okunur tekrar yapıldı. Bu model retry veya ikinci inference değil. Task completed state/tek initial turn/final mesaj ve input preview'ın exact7950-byte prompt ile eşleşmesi doğrulandı. Private thread/message/account IDs ve tam host wrapper yerel capture'da repo dışında; repo ham hesap kaydı içermez. Source summary ve raw output'un rollerini karıştırmama yaklaşımı sonraki adapter'lara taşınmalı.

## Kullanım ve beklenenden fazla tüketim

| Ölçüm | Değer |
|---|---|
| User input bytes | 7950; token sayısı değil |
| Visible final bytes / characters | 1739 /1739; token sayısı değil |
| Input/output/reasoning/cache/total tokens | **unknown/null**; host endpoint sunmadı |
| Local tokenizer | Kurulu değil; yeni dependency eklenmedi |
| Output hedefi | Soft1536token; gerçek adherence/hardcap doğrulanamadı |
| Trial token aşımı | **not_evaluable**; within_limit veya0 denmedi |
| Account shared quota | Immediate before74%, after74% used;10080min pencere |
| Kota farkı yorumu | Yuvarlanmış shared account snapshot. Aynı değer tüketim0 kanıtı değildir; parent/başka görevleri içerir |
| API/cost | PaidAPI0; üyelik quota tüketildiği exact miktar bilinmiyor, para karşılığı null |

Reasoning output total'ın alt bileşeni olabilir; ölçüldüğünde iki kez toplamayız. API fiyatını native üyelik yüzdesine çevirmedik. Başlangıçtan önceki daha erken hesap snapshot'ı73% iken root dokümantasyon/hazırlık sırasında74% oldu; immediate trial74→74 alınmıştır. Tüm bu farkları receiver'a yüklemiyoruz. Account/provider IDs kayda taşınmadı.

## Doğrulama ve devam yeri

**136 semantik test /2 yeni recorded-output regresyonu geçti.** Bunlar gerçek output'un schema retini, raw hash/literal null-false korunmasını, consumed permission/unknown usage/quality gate ayrımını doğrular; failed model cevabını başarılı yapmaz. Oracle, request/prompt/manifest/önceki proof'lar değişmedi. Canonical mutation0, onay/apply/target/verify yok.

Ana proje geliştirmesine **orijinal sohbette** devam ediyoruz. Deney chat'i tek-run kanıtıdır; ikinci prompt/soru/model-call gönderilmedi, silinmedi/archive edilmedi. Bu sohbetin yerel devir kaydı repo dışındaki `outputs/decivora-next-chat-handoff.md`; mevcut status/backlog/kalite kayıtları güncel otoritedir. Yeni gerçek model çağrısı yetkisi kalmadı.

Sonraki bağımsız iş: mevcut wire contract'ın strict JSON Schema/synthetic valid-invalid örneklerini hazırlayıp per-record scope/abstention/type kurallarını kodla sınamak; native prompt-only çıktı ile provider-enforced schema arasındaki farkı açık tutmak. Frozen RECEIVER-001 raw/prompt/oracle onarılmaz. Yeni prompt/model/backend/paidAPI denemesi ayrıca somut scope/onay ister. R23/R24, mainT03 ve production yatırım/stack/gold/native/user-burden kapıları açık; result recording DONE ürün acceptance DONE değildir.

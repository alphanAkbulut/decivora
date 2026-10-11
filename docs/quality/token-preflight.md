# P0 — Gönderim öncesi token/bağlam kontrolü

**2026-10-11 · Yerel deterministik kod ve fixture testleri uygulandı. Gerçek model gönderimi, parasal limiter ve production admission uygulanmadı.** T03f/T03b deney hazırlığını ilerletir; T09d/T21b/T21c veya ana P0 görevlerini kapatmaz.

## Çalışan parça

[Kontrol kodu](../../scripts/token_preflight.py), açık çağrı manifesti, sonlu policy, gerekli parent/proje bütçe snapshot'ları ve adapter capability kaydını alır. Her çağrıda tam input üst sınırı + generation rezervi + margin hesaplanır; uygulama ve model penceresinin küçüğü uygulanır. Child/retry çağrılarının input/output toplamı aynı run ve bütün gerekli bütçelere eklenir. Spent + outstanding reservation + yeni üst sınır tavanı aşamaz; unknown in-flight tüketimi reservation'a dahil olmalıdır. Bu kod reservation yaratmaz veya lease serbest bırakmaz.

Sonuçlar: **within_policy / requires_risk_approval / blocked**. Risk eşiği hard cap'i aşma hakkı vermez. Eksik/negatif/boolean/non-finite sayı, model veya policy uyuşmazlığı, bilinmeyen reasoning/output sınırı, eksik parent bütçesi ve duplicate çağrı kimliği blocked kalır. Byte sınırından kesin token sayısı türetilmez.

Her sonuçta dispatch_authorized, dispatch_performed, reservation_created ve monetary_cap_enforced **false**. Bir JSON kaydında verified=true yazması gerçek yetki/provider kanıtı değildir: üretimde bu alanları trusted adapter/policy katmanı sağlamalıdır. Bu modül onay kabul etmez; assessment digest'i yalnız snapshot izlenebilirliği sağlar. Gerçek onay, authz/revision recheck ve atomik rezervasyon/dispatch T08/T09d/T21 kapsamındadır. Offline snapshot iki eşzamanlı worker'ın aynı bütçeyi harcamasını tek başına engelleyemez.

## S02 üzerinde sonuç

`python3 -B scripts/token_preflight.py --s02` seçilmiş paket hashlerini doğrular, oracle veya hesap credential'ı okumaz; provider'a istek göndermez. [Kayıt](token-preflight-results.json): paket değişmemiş, token/model/capability ve bütçe üst sınırları henüz unknown olduğu için **blocked**. Bu, ürün task'ının başarısızlığı veya otomatik BLOCKED ana task mutasyonu değildir; ilk gönderimin kapısıdır.

`python3 -B -m unittest discover -s tests -p test_token_preflight.py -v`: 17 fixture testi. Sonlu normal örnek, risk/hard ayrımı, küçük model penceresi, reasoning/output desteği, input sayımı, child/retry toplamı, eski model/policy, eksik/duplicate parent, unknown usage ve S02 no-dispatch kontrolü. Fixture rakamları kullanıcı bütçesi veya ölçülmüş optimum değildir. TRA/LIM bütün senaryolarının gerçek dispatcher üzerinde geçtiği iddia edilmez.

## Mevcut hesap yolu: ne doğrulandı?

OpenAI Docs üzerinden [resmî config referansı](https://learn.chatgpt.com/docs/config-file/config-reference) okundu. model_context_window model kapasitesini, tool_output_token_limit tek tool sonucunun geçmişte tutulma bütçesini anlatır; bunlar toplam harcama veya cevap için doğrulanmış sert tavan kanıtı değildir. Bu sayfada açık max_output ayarı bulunmadı; yokluğu tüm host/provider'larda unsupported olduğunun kanıtı sayılmaz.

Yalnız yerel sürüm/help okuması yapıldı: codex-cli 0.162.0-alpha.17.2. exec yardımında açık per-run output/token/para tavanı gösterilmedi; genel config override vardır, ancak belirli bir limitin server tarafından uygulanacağı test edilmedi. Global config, auth, host kurulumu değişmedi; yeni oturum/agent veya inference başlatılmadı. CLI mevcudiyeti seçilmiş model/hesap veya dahil kullanım teyidi değildir.

[Resmî context belgesi](https://developers.openai.com/api/docs/guides/conversation-state) input/output/reasoning'in pencereye etkisini açıklar. Bu API açıklaması, mevcut sohbet arayüzünün iş başına hard cap desteğinin kanıtı değildir. Claude hesabı/modeli seçilmedi ve bu incelemede sınanmadı.

**Devam sırası:** hesap/arayüz seçimi → model ve tam request sayımı/limit mekanizması/dahil kullanım teyidi → sonlu policy → bir S02 output → bağımsız scorer ve kontrollü karar/kanıt zinciri. Desteklenmeyen mekanizmayı prompt talimatıyla eşdeğer sayma; ücretli API veya zayıf sınır istisnasına sessiz geçme. Para/veri izinleri ayrı kalır.

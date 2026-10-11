# Benchmark: mevcut bulgular ve ölçülmemiş alanlar

**2026-10-09 — araştırma sonucu, runtime yarışma sonucu değil.** [Benchmark matrisi](benchmark.md) araç kaynaklarını; [farklılaşma](../product/differentiation.md) ürün hipotezlerini; [şikâyet araştırması](user-research.md) problem kanıtını içerir.

## Gerçekte ne yapıldı?

| Katman | Durum | Ne söyleyebiliriz? |
|---|---|---|
| Birincil ürün belgeleri ve repository README'leri | İncelendi | Dokümante kabiliyet/örtüşme ve araştırma adayları |
| Seçilmiş issue ve kullanıcı konuşmaları | Yedi kamu kaynağı incelendi; iki kapanan issue'nun bakımcı yanıtları okundu | Kaynak sahibinin deneyimi ve bildirilen düzeltme; yaygınlık veya bağımsız reproduction değil |
| Sabit sürüm kaynak kodu incelemesi | Araçların tamamı için yapılmadı; 2026-10-11 WrongStack seçili kaynak/test bölümleri [sabit ref'te incelendi](wrongstack-review.md) | Statik davranış/uyum adayları; çalışmış benchmark veya tüm source/CI doğrulaması değildir |
| Aynı fixture ile kurulum ve kullanım | Henüz yapılmadı | Native/config/custom/unavailable sonuçları henüz yok |
| Token, latency, doğruluk, manuel yönetim süresi | Ölçülmedi | Skor, yüzde üstünlük veya tasarruf sonucu yok |
| Decivora karşılaştırması | Ürün henüz uygulanmadı | Ürün sözleşmesi ve test planı var |

## Karşı kanıtla güncellenen çıkarımlar

**Genel task capture ve hafıza, tek başına boş pazar değildir.** Tracker, Cortex, mai-mcp, Beads ve OpenSpec'in belgelenen davranışları başlangıç fikrinin önemli bölümleriyle örtüşüyor. Sıfırdan her şeyi yazmak için yeterli gerekçe henüz yok. T03'te extend seçeneğini gerçekten sınamak gerekir. Ayrıntılı kaynaklar [matriste](benchmark.md).

**Task Master context şikâyeti tarihsel ders olarak kalır.** UR-01'de bakımcı araç seçimi çözümünün birleştirildiğini bildirmiş. Modern profili ölçmeden “biz az token kullanacağız, onlar kullanamıyor” diyemeyiz. Güncel yapılandırma ile karşılaştırmak gerekir. [Bakımcı açıklaması](https://github.com/eyaltoledano/claude-task-master/issues/1280#issuecomment-3403117739).

**Beads veri kaybı vakasını kalıcı rakip kusuru saymıyoruz.** UR-03'te hata yönlendirmesi ve non-interactive reset koruması için düzeltme bildiriliyor. Decivora için çıkarım recovery yetkisini sınırlamak; üstünlük iddiası değil. [Düzeltme açıklaması](https://github.com/gastownhall/beads/issues/2363#issuecomment-4007206076).

**Linear sadece elle kart doldurulan bir ürün olarak temsil edilemez.** Resmî belgede agent yardımıyla proje güncellemesi taslağı ve Intercom konuşmasından başlık/açıklama üretme anlatılıyor. Bu, tüm coding/chat yüzeylerinin pasif capture'ı veya AND/OR impact ile aynı şey değildir; fakat “otomatik başlık ve özet” tek başına farklılaşma oluşturmaz. [Project updates](https://linear.app/docs/initiative-and-project-updates), [Intercom Agent](https://linear.app/docs/intercom).

**UI ihtiyacı güçlü bir tasarım girdisi, tek başına ürün tezi değil.** Beads topluluğunda farklı UI biçimleri zaten var. Bizim deneyimiz kullanıcıyı board'dan karar gerekçesine ve kanıta daha az emekle götürüp götüremediğimiz olmalı. [UI tartışması](https://github.com/gastownhall/beads/discussions/276).

## Odak önerisi

İlk pilotta aynı kaynak oturumundan şu üç sonucu birlikte göstermek: **unutulan bilgiyi kaynakla geri getirme; değişen kararın eski plan üzerindeki etkisini doğru ayırma; bunu kullanıcıya yeniden kart yazdırmadan inceletme.** Verification ve maliyet bu sonucu güvenilir kılan koşullardır. Tam kapsam korunur; deneyin ölçüm odağı belirlenir.

Potansiyel fark bir engine adı değil; altı hipotezin birlikte sağlandığı ölçülebilir sözleşmedir. Özellikle H1 (karar etkisi) + H3 (yönetim yükü) + H4 (kanıta bağlı durum) önceliklidir. İddia: hedef. Sonuç: henüz ölçülmedi.

## Uygulanacak adil karşılaştırma

1. **T01:** Altı sentetik oturum/30 anlamlı kayıt ve no-op örnekleri; iki proje; source span/expected record/state/edge oracle. Holdout oturumları ayrı tutulur. Bu belge corpus'un yerine geçmez.
2. **T02:** Owner'ın gerçek host/yüzey seçiminden sonra izole adapter deneyleri; sürüm ve erişim sınırı. Gerçek özel projeyi kendiliğinden bağlama.
3. **T03:** Önce Cortex ve mai-mcp (yakın domain), Tracker (pasif capture), Beads+bir UI (task/dependency); OpenSpec change modeli ayrıca. Task Master decomposition ve minimal profile; Linear izinli erişim mümkünse UX/intake referansı. Account yokluğu unsupported diye yazılmaz, `not_run` olur.
4. Her araçta güncel desteklenen yapılandırma kullanılmalı. Uygun mevcut profil/ayar göz ardı edilerek kötü baseline seçilmemeli. Baseline, Decivora ve extension maliyeti ayrı kaydedilmeli.
5. Her sonucu özellik bazında `native`, `configuration`, `custom_extension`, `unavailable`, `unknown` ve çalışma statüsü `pass/fail/not_run` ile kaydet. Dokümanda görülmeyen özelliği unavailable sayma.
6. Senaryolar: capture/dedup/no-op; rejected revival; pending approval; karar değişimi/AND/OR/unknown; false done; prompt lineage; crash/retry; wrong project; stale approval; context budget. Her senaryo tüm araca doğal uymayabilir; uyumsuzluğu raporla, ortak çekirdeği ayrıca karşılaştır.
7. Ürün doğruluğu için test/holdout; UX için kullanıcı görevi; maliyet için bütün çağrı/retry/tool context ve review süresi. Unsupported yüzeyleri başarı paydasından sessiz çıkarma.

## Sonuç kaydı şablonu

```yaml
run_id: null
status: not_run
tool_and_version: null
source_commit: null
license_checked_at: null
host_and_configuration: null
dataset_revision: null
scenario_id: null
capability_mode: unknown
expected: null
observed: null
evidence_refs: []
setup_minutes: null
manual_input_minutes: null
review_correction_minutes: null
tokens_actual: null
tokens_estimated: null
provider_price_snapshot: null
limitations: []
```

Bu doldurulmamış şablon sonuç değildir. Ölçülen sıfır `0`, ölçülmeyen `null/not_run` olur. Üstünlük için aynı senaryo ve karşılaştırılabilir kalite gerekir. Mevcut çözüm düşük bakım yüküyle yeterliyse entegrasyon önerilir; bağımsız ürün kararı otomatik varsayılmaz.

## 2026-10-11 — Yeni Claude Projects karşı kanıtı

[Yeni Projects incelemesi](claude-projects-overlap.md) ve [kullanıcının gerçekleşme örneği](../product/intent-to-reality-gap.md) önceki bulguları tamamlar. Paylaşılan hafıza, karar gerekçelerini taşıma, koordinasyon ve iş takibi Anthropic tarafından belgeleniyor; genel memory eksikliği iddiası yeterli değil. T03 karşılaştırmasına GAP-01–10 ve aynı kaynak/karar/target revision oracle'ı eklenir. Belge incelemesi, kullanıcının deneyim bildirimi ve ölçülmemiş Decivora hipotezi ayrı tutulur. Runtime üstünlük sonucu yok.

## 2026-10-11 — WrongStack kaynak karşı kanıtı

[Hedefli inceleme](wrongstack-review.md) koşullu memory, anchor stale/unknown, completion evidence, DoD UI, MCP proposal-only ve deterministik requirement coverage için seçili uygulama kaynaklarını içerir. Hafıza/gate/dependency tek başına özgünlük iddiası değildir. Küçük validator/coverage/schema reuse, native kullanım ve extension T03'te ayrı seçeneklerdir. WS-01–08 sonuçları not_run; runtime/CI/maliyet testi yok. Doğrudan kod alınmadı; uyumsuz soft completion, hard cap ve unknown semantics açık yazıldı.

## Repo geneli kaynak taramasından yeni karşı kanıt — 2026-10-11

[Kod/teknoloji değerlendirmesi](code-reuse-assessment.md) 39 manifest alanı, 9.657 kod dosyası ve dahili paket ilişkilerini yapısal olarak kapsar; kritik adaylarda seçili davranış okumaları ekler. Governance append-only event/receipt, revision/plan contract, bağımsız verifier/grant; Kanban contract graph ve core karar/gerekçe graph'ı ilk incelemeyi genişletir. EvidenceValidator ref-only veya legacy soft completion bulguları bütün platforma genellenmez. Native/config/extension aynı GAP/RES/WS oracle'ında en uygun desteklenen yapılandırmayla denenmeli. Kod kopyası, install, CI, runtime/performans/lisans-audit sonucu yok; inceleme V değildir. A/B/C reuse seçenekleri henüz owner kararı değildir.

## 2026-10-11 — On ek repo: karşı kanıt ve araştırma önceliği

[Ekosistem taraması](ecosystem-research.md) kaynakla destekli üç yeni örtüşmeyi kaydeder: Graphiti fact validity/supersession; LangGraph persistent wait/resume; LiteLLM çağrı öncesi rezervasyon/uzlaştırma. Kalıcı hafıza, soru bekleme veya bütçe rezervasyonu tek başına farklılaşma değildir. Domain karar yetkisi, exact uygulama kanıtı ve downstream etki birlikte aynı fixture'da sınanmalı.

Mem0 managed benchmark'ının OSS'den ayrılması, LiteLLM enterprise yolu/premium priority feature ve Langfuse ticari klasörleri adil karşılaştırma/alım için önemlidir. Root lisans okuması tüm dependency/model/feature uygunluğu değildir. 10 root belge/lisans, beş seçili kaynak okuması; bütün repo audit'i ve runtime yok. T03e ilk masa başı çıktısı hazır; derin closure, deney ve owner adoption kararı bekler. Native/config/extension/own seçenekleri korunur.

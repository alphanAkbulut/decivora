# Intelligent work routing ve token ekonomisi

## İki ayrı etiket ekseni

`work_class`: DETERMINISTIC, LOW_COMPLEXITY, REASONING, HUMAN_DECISION.

`executor`: SYSTEM, SCRIPT, API, AGENT, HUMAN. İnsan basit bir işi üstlenebilir; HUMAN_DECISION yalnız stratejik/yetki kararı içindir. `human_suitable` ve `automation_available` yardımcı etiketleri insan seçeneğini görünür tutar. Bunlar rol/yetki yerine geçmez.

| İş | Nitelik | Tercih edilen yürütme |
|---|---|---|
| Dosya varlığı, JSON şeması, graph traversal | DETERMINISTIC | SYSTEM/SCRIPT |
| GitHub durumunu okuma | DETERMINISTIC | API |
| Standart alanları belgeden aktarma | LOW_COMPLEXITY | Önce parser; gerekirse küçük model |
| Çelişen mimari gerekçeleri yorumlama | REASONING | Bütçeli model evaluation |
| Eski kabul edilmiş kararı değiştirme | HUMAN_DECISION | İnsan onayı; AI analizi yardımcı |
| Basit manuel kontrol / erişilemeyen UI adımı | DETERMINISTIC veya LOW_COMPLEXITY | Kullanıcı tercih ederse HUMAN |

Routing sırası: yetki → risk → gerekli yetenek → deterministik çözüm → ölçülmüş model kalitesi → bütçe → kullanıcı tercihi. Ucuz model uygun kaliteye erişmiyorsa görev zorlanmaz; escalation veya review olur. Routing gelecekte executor başlatabilir; MVP etiketleme ve kayıt temellidir, izinsiz agent orchestration değildir.

## Context on demand

MVP MCP araç adayları: `get_project_brief(project_id, budget)`, `query_records(project_id, filters, cursor, limit)`, `get_record(project_id,id,revision)`, `submit_changeset(project_id,operations,base_revisions,key)`, `submit_evidence(project_id,evidence,key)`. Ayrıntılı graph ve admin araçları ihtiyaçta açılır. İnsan onayı ayrı güvenilir UI kimliği taşır; agent bir alanı `approved=true` göndererek onay veremez.

Brief yalnız current approved decisions, aktif iş, unresolved blockers ve değişiklik delta'sı içerir. Arşiv bağlamı, duplicate/rejected revival için hedefli getirilir. Tool schema boyutu, sonuç boyutu ve conversation context birbirinden ayrı ölçülür. MCP taşıma protokolüdür; kendi başına token tasarrufu garantilemez.

## Maliyet kontrolü

- Turn/idle batch, kalıcı cursor, content/revision cache ve hedefli retrieval.
- Cache anahtarı project + record revisions + policy + extractor/prompt/model sürümü; yanlış proje cache paylaşımı yok.
- Her iş için max_input_tokens, max_output_tokens, max_retries, max_cost ve deadline; limitte defer/review, sessiz drop yok.
- Kesilen retrieval ve çıkarılmamış kaynak bölümü kullanıcıya görünür kalır. Bütçe için recall kaybı saklanmaz.
- Aynı kaynak seti ve engine sürümü tekrar değerlendirilirken önce kayıtlı sonuç kullanılır; zorunlu yeniden analiz ayrı run ID alır.

Usage kaydı: provider/model, operation, actual_input/output/cached tokens veya null, estimate ve estimator version, currency, price snapshot date, latency, retry count, deterministic bypass. Abonelik/quota kullanımı sıfır maliyet sayılmaz. Fiyat ve plan değerleri burada sabitlenmez.

Tahmini model maliyeti = uncached input × input rate + cached input × cached rate + output × output rate; birim dönüşümü ve provider'ın token sınıfları belirtilir. Araç/API bedelleri ayrı eklenir. “Tasarruf” aynı golden corpus ve benzer kaliteye sahip full-context baseline ile karşılaştırılır; varsayımsal fark gerçekleşmiş fatura tasarrufu değildir.

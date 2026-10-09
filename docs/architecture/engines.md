# Engine haritası ve yürütme sınırları

**Durum: önerilen tasarım; hiçbir engine henüz uygulanmadı.** Konuşmada geçen farklı adlar aşağıda tek sözlüğe bağlanır. Engine bir sorumluluk sınırıdır; ayrı servis, ayrı LLM veya otonom agent demek değildir. Başlangıçta aynı yerel süreçte test edilebilir modüller öneriyoruz.

## Konuşmadaki isimler nereye gitti?

| Kaynak terim | Kanonik karşılık | Ayrım |
|---|---|---|
| Universal Capture Engine / Capture Engine / Capture Agent | ENG-01 + ENG-02 | Adapter erişimi ile metinden anlam çıkarma ayrı |
| Agent Adapters / Event Collector | ENG-01 | Gözlemi kaydeder; doğruluk kararı vermez |
| Classification Engine | ENG-02 | Tipli aday üretir; aktif scope'a kabul etmez |
| Idea Evaluation Engine | ENG-04 | Gerekçe, karşı kanıt, belirsizlik; mutlak doğruluk puanı yok |
| Change Detection Pipeline | ENG-03 → ENG-04 → ENG-05 | Ucuz eşleştirme, gerekirse yorum, sonra etki |
| Reconciliation Engine | ENG-03 | Yeni bilgiyi mevcut kayıtlarla uzlaştırma önerisi |
| Knowledge Evolution Engine | ENG-03/04/05/06/07 birlikte | Yeni bir ikinci truth store veya ayrı karar otoritesi değil |
| Change Impact Engine / Impact Trigger | ENG-05 | Karar/requirement değişiminin gerekçeli downstream etkisi |
| Verification Engine | ENG-08 | İddia ile revision'a bağlı kanıtı ayırır |
| Intelligent Work Routing | ENG-09 | İş sınıfı, uygun yürütücü ve bütçe |
| Knowledge Store / Canonical Decision Record | ENG-07 ve Decision record | Depo ve sürümlü kayıt; AI engine değil |
| Knowledge Change Request | ChangeSet + ENG-06 | Hazırlanan, incelenen ve atomik uygulanan öneri |
| Living Knowledge Graph | ENG-05/07 read model | İlişki görünümü; kendi başına doğruluk oracle'ı değil |
| Visual Control Center / Knowledge Review | UI + ENG-06/10 | İnsan review, board, graph, timeline ve coverage |
| AI Output Lifecycle | Feature F08 | Source→prompt→execution→artifact→evidence zinciri |

Kaynak: [E06–E13 evrim kayıtları](../discovery/evolution.md). Konuşmada örnek başka proje içinde geçen **AI Benchmark Engine** ve **Attribution engine** bu ürünün engine'i değildir; örnek içerikle ürün gereksinimini karıştırmıyoruz.

## Modül sözleşmeleri

| ID / modül | Girdi → çıktı | İşleme / yetki | Hata veya belirsizlik | Görev / ilk faz |
|---|---|---|---|---|
| ENG-01 Capture & Ingestion | Provider event + binding → SourceEnvelope, kalıcı job, receipt | Deterministik; yalnız source ingest | Disk/izin hatasında ack yok; belirsiz proje quarantine; coverage gap | T05,T06,T16,T17 / P1a |
| ENG-02 Extraction & Classification | Source spans + bounded context → typed candidates, suggested title/AC/links | Parser önce, gerektiğinde şema denetimli model; proposal yetkisi | Invalid span/output failed; hiçbir bilgi yoksa gerekçeli no-op; model kapalıysa deferred | T09,T22 / P1a |
| ENG-03 Reconciliation | Aday + ilgili current/history revisions → new/duplicate/refines/conflict/supersession önerisi | Exact-match deterministik; semantik model opsiyonel | Belirsiz eşleştirme uncertain; benzerlik otomatik merge/onay değil | T10,T26 / P1a |
| ENG-04 Idea Evaluation | Alternatifler, karar gerekçeleri, destek/karşı kanıt → Evaluation | Bütçeli reasoning veya insan değerlendirmesi; karar yetkisi yok | Kaynak yetersizse eksik kanıtı belirt; yeni fikri doğru ilan etme | T10,T26 / P1b temel, P2 gelişmiş |
| ENG-05 Decision Graph & Impact | Proposed/accepted trigger + graph snapshot → ImpactRun, reason paths, keep/update/review/obsolete adayları | Traversal ve AND/OR/unknown deterministik; semantik yorum sınırlı | Eksik frontier/gerekçe review; timeout tamamlandı sayılmaz | T11,T12,T26 / P1a |
| ENG-06 Review & Policy | ChangeSet + actor + approval token → reject/defer/stale veya yetkili domain command | Deterministik yetki, digest, revision, policy ve grup denetimi | Agent insan kimliğine dönüşemez; stale için yeniden diff/onay | T08,T13,T19 / P1a |
| ENG-07 Event & Projection | Yetkili command → event sequence + current state + outbox | Tek transaction; replay deterministik, LLM yok | Commit yoksa etki yok; response kaybında idempotent sonuç | T07,T08,T23 / P1a |
| ENG-08 Verification | AC revision + artifact revision + verifier result → verification assessment | Önceden izinli kontrollere dayalı; yorum veya manuel kanıtın otoritesi açık | Başarısız/stale/unknown farklı; test koşulamaması failed ile karıştırılmaz | T14,T27 / P1a |
| ENG-09 Work Routing & Budget | İş, risk, izin, capability, preference, budget → route + usage/defer | Önce kurallar; model seçimi ancak ölçümle; yürütme izni ayrı | Limitte source korunur; pahalı fallback izinsiz başlamaz | T21,T28 / P1b |
| ENG-10 Context & Health | Yetkili query + snapshot + budget → brief, ready work, coverage, health | Deterministik retrieval/ranking baseline; bounded sonuç | Truncation/cursor, stale projection ve bilinmeyen coverage görünür | T18,T20,T26 / P1b |

ENG-10 adı ve bu onlu ayrım, bu repo incelemesinde eklenen **uygulama tasarımıdır**; konuşmada alınmış on ayrı servis kararı değildir. Token hesaplama ENG-09'un; context paketleme ENG-10'un sorumluluğudur. Aynı metin tekrar tekrar farklı engine'lerde ücretsizmiş gibi analiz edilmez.

## Ortak çalışma bağlamı

[TRG-01–12 tetikleme kaydı](execution-and-integrations.md#1-tetikleme-kaydı) her engine'in hangi olayda çalıştığını, API hedeflerini ve kod/LLM/insan ayrımını tanımlar. Scheduler ve event dispatcher ENG-01/06/07/09/10 uygulamasının parçalarıdır; on birinci engine veya zorunlu ayrı servis değildir. Her task/run sonu LLM çağrısı gerektirmez.

Her değerlendirme `project_id`, `run_id`, `input_refs`, `input_revisions`, `policy_revision`, `engine_version`, `correlation_id`, `budget` taşır. Sonuç `status`, `output_refs`, `reason`, `coverage`, `usage_ref` içerir. Model/prompt sürümü yalnız model kullanıldıysa eklenir. Log satırları raw transcript ve secret içermez.

`received`, `extracted`, `evaluated`, `approved`, `applied`, `verified` farklı kilometre taşlarıdır. Kaynakta değerlendirilmeye değer içerik bulunmaması gerekçeli no-op olabilir; provider/model hatası no-op değildir. Yalnız ENG-06'nın yetkilendirdiği command ENG-07 üzerinden canonical durumu değiştirebilir. ENG-08 de doğrudan store'a yazmaz.

## Hazır iş ve project health kuralları

Next-ready adayı: accepted/active task, execution todo, çözülmüş zorunlu prerequisite'ler, açık scope kararı veya stale impact engeli yok, proje policy'si yürütmeye izin veriyor. “Ready” izinli executor'ın otomatik çalıştırılması değildir. Unknown bağımlılık ready sayılmaz. Öncelik/sıralama gerekçesi ve snapshot revision döner.

Health en az ayrı göstergeler sunar: capture coverage, oldest unprocessed age, pending decisions, stale impact, stale evidence, orphan records, review backlog ve budget. Tek yeşil sağlık puanı eksik yakalamayı gizleyemez. İnaktivite abandonment kanıtı değildir; kullanıcı lifecycle seçimi korunur.

## Engine bazlı doğrulama

ENG-01 duplicate/crash/gap; ENG-02 tür ve span recall; ENG-03 duplicate/conflict precision; ENG-04 gerekçe/karşı kanıt insan değerlendirmesi; ENG-05 false-obsolete ve missed-impact; ENG-06 yetki/stale/partial approval; ENG-07 atomic/replay; ENG-08 false-done/freshness; ENG-09 kalite eşitliğinde maliyet; ENG-10 cross-project retrieval ve missed-ready ölçülür. Hedefler [ölçüm planında](../quality/measurement.md); sonuçlar henüz yoktur.

Detaylar: [runtime sözleşmeleri](runtime-contracts.md), [diyagramlar](diagrams.md), [routing](routing-token-economy.md).

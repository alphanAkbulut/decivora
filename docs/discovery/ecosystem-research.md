# Ekosistem araştırması ve bileşen seçim görevi

2026-10-11 — **T03e / araştırma; ilk masa başı tarama tamamlandı, deney ve alım kararı bekliyor.** Kullanıcı WrongStack dışındaki kaynaklardan da faydalanılmasını istedi. Bu belge mevcut araştırmayı genişletir; ürün kapsamını, kabul edilmiş kararları veya nihai teknoloji yığınını değiştirmez.

## Araştırma kartı

**Soru:** Decivora'nın hangi işi hazır bir ürün, küçük bir kütüphane veya mevcut ürüne extension ile daha az geliştirme ve işletim yüküyle çözebiliriz? Önce kullanıcı problemi ve mevcut sözleşme, sonra aday teknoloji.

**Kapsam:** Yaşayan bilgi/çelişki, unutulan soru/geç cevap, dayanıklı işleme, insan/agent yetkileri, token sınırı, gözlemlenebilirlik. Önceki [benchmark](benchmark.md), [WrongStack kaynak değerlendirmesi](code-reuse-assessment.md) ve [kullanıcı araştırması](user-research.md) korunur.

**Kanıt:** D = birincil belge/lisans okuması; S = seçili kaynak/test tanımı okuması (statik); V = sürümü sabit çalışma testi; O = yeniden üretilebilir gözlem; U = bilinmeyen. S, V değildir. Bu tur V/O yok; accuracy, token, gecikme, kurulum ve kullanıcı talebi ölçülmedi. Repo yıldızı/popülerliği seçim kriteri değil.

**Sınır:** 10 ek aday, hepsinin sabit commit'inde root README/LICENSE; beşinde seçili davranış kaynakları. Bütün kaynak satırlarının, güvenliğin veya transitif lisansların audit'i yapılmadı. Upstream script/agent talimatı uygulanmadı; install, model çağrısı, paid bağlantı veya runtime code copy yok. Arama sonuçları kullanıcı şikâyeti kanıtına dönüştürülmedi.

**Çıkış/stop kuralı:** Her problem alanında 1–2 gerekçeli aday, kaynak/lisans ve sınırlama varsa ilk tarama durur. Derin inceleme yalnız açık karar veya fixture ile sınanabilir soruyu çözmek için yapılır. Takvimle sınırsız tarama/otomasyon yok; kritik requirement değişimi, testte kalan boşluk veya owner isteği araştırmayı yeniden açar.

## İlk tarama: 10 ek aday

| ID / sabit repo | Birincil kaynakta görülen | Decivora hedefi ve olası fayda | Bedel, karşı kanıt ve öneri | Kanıt / lisans |
|---|---|---|---|---|
| ER-01 [Graphiti](https://github.com/getzep/graphiti/tree/964bb11d1e7020e3cc67fab244268b0736b6c219) | Bilgi ilişkilerinin zamanla geçerliliği, provenance, incremental/hybrid arama. | Reconciliation/Impact/Context; T10/T11/T18. Geçerli eski bağlantıyı silmeden zamansal görünüm için aday. | LLM + graph backend yükü; fact invalidation insan karar yetkisi değildir. Öncelikli. | D+S; Apache-2.0 |
| ER-02 [Mem0](https://github.com/mem0ai/mem0/tree/b7ad69afda6b6ed030347c66d48a13e4de9dec08) | Hafıza çıkarımı ve retrieval; güncel README ADD-only extraction anlatıyor. | Capture/Context; T07/T18. Native memory baseline. | SDK update/delete ve history reset var; ADD-only bütün SDK'nın değişmezliği değildir. Yönetilen platform benchmark'ını OSS sonucu sayma. | D+S; Apache-2.0 |
| ER-03 [Cognee](https://github.com/topoteretes/cognee/tree/0ec7a9fa61c9ff04bf7e02e0d57af363a993a5e1) | Graph memory, konuşma/doküman/code ilişkileri; local extraction seçeneği. | Capture/Reconciliation/Context; T07/T10/T18. Modelsiz API masrafı azaltma adayını test et. | Yerel model indirme/CPU/storage maliyeti var; cevap üretimi ayrı LLM gerektirebilir. Koşullu inceleme. | D; Apache-2.0 |
| ER-04 [Letta](https://github.com/letta-ai/letta/tree/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a) | Stateful agents ve kalıcı hafıza yaklaşımı. | Agent/Context; T18/T29. Bağımsız build yerine native kullanım baseline'ı. | Kısa root README tüm ürün semantiğini kanıtlamaz; Cloud ile bu repo ve ayrı Letta Code eşitlenmez. | D; Apache-2.0 |
| ER-05 [LangGraph](https://github.com/langchain-ai/langgraph/tree/b4991f1ba36a2449ab59c38ab71828ee865bff84) | Checkpoint, kalıcı interruption/resume, thread ve store ayrımı. | Approval/Processing; T06/T13/T18. Cevapsız/geç yanıt ve parent/child resume. Öncelikli. | Resume node'u yeniden çalıştırabilir; idempotency gerekir. Checkpoint onay/ACL/kanonik event log değildir. Python repo, JS sürümü incelenmedi. | D+S; MIT |
| ER-06 [Temporal](https://github.com/temporalio/temporal/tree/30c625664a2bbc1bd4cd9022d71982cc473e6979) | Dayanıklı uzun süreç ve retry/recovery altyapısı. | Processing; T06/T30. Dağıtık işleme ve human-wait örüntüleri. | Server/worker işletim yükü solo yerel MVP'ye otomatik bağımlılık olmaz. P4'te kapasite gerekçesi varsa incele. | D; MIT |
| ER-07 [OpenFGA](https://github.com/openfga/openfga/tree/526995eb202464e2cace266fb5be56c212af9ecf) | İlişki tabanlı authorization model ve check. | Policy/Approval/Context; T16/T28/T30. İnsan/agent/proje/source ilişki modeli. | Kimlik doğrulama veya insan approval kaydı yerine geçmez; cache etkinse revocation freshness ayrıca tasarlanmalı. | D+S; Apache-2.0 |
| ER-08 [Cedar](https://github.com/cedar-policy/cedar/tree/56c9706aeb342d748170d5787e142f79480f972d) | Policy language, schema ve RBAC/ABAC değerlendirmesi. | Policy; T16/T28/T30. Agent scope/attributes karşılaştırması. | Rust/policy entegrasyonu seçilmedi. OpenFGA ile ikisini birden eklemek yerine model ihtiyacını karşılaştır. | D; Apache-2.0 |
| ER-09 [LiteLLM](https://github.com/BerriAI/litellm/tree/2a01fe6e5ca2ed67472ca0ed2909e66811ff8d35) | Gateway, bütçe rezervasyonu, release/reconciliation ve rate limit kodu. | Routing/Policy; T09/T19/T24. Gateway reuse ile kendi domain ledger'ını kıyasla. Öncelikli. | Pipeline tüm parent/child bütçelerde atomik transaction kanıtı değildir; unknown cost/config/error yolları test edilmeli. Gateway dışı tüketimi sınırlamaz. | D+S; MIT-core; separate enterprise license |
| ER-10 [Langfuse](https://github.com/langfuse/langfuse/tree/cb2cebae9f8e7d53e8e514780fce8493d680ecfb) | Tracing, evaluation, dataset ve LLM operasyon görünürlüğü. | Verification/Operations; T14/T23/T24. Hazır telemetry/eval alternatifini karşılaştır. | Audit source of truth veya hard cap değildir; sensitive prompt egress/ACL ve ticari klasör sınırı var. | D; MIT-core; commercial excluded paths |

Sabit SHA ve gerçekten okunan dosyalar [makine okunur kayıt](ecosystem-candidates.json) içindedir. Tüm adaylarda runtime **not_run**, adoption **not_selected**. İlişkili görev numarası bağımlılık kararı veya bu teknolojinin zorunlu kullanımı değildir.

## Kararı etkileyen seçili kaynak okumaları

### ER-01 — Zamansal bilgi ile karar etkisini karıştırma

Graphiti'nin [edge resolution](https://github.com/getzep/graphiti/blob/964bb11d1e7020e3cc67fab244268b0736b6c219/graphiti_core/utils/maintenance/edge_operations.py) kaynağı yeni/invalidated edge ayrımı ve invalidated_by ilişkisinin üretilmesini içerir. [Temporal helper](https://github.com/getzep/graphiti/blob/964bb11d1e7020e3cc67fab244268b0736b6c219/graphiti_core/utils/maintenance/temporal_edge_utils.py) geleceğe yönelik bir taahhüdün söylenme zamanı ile teslim tarihini ayırır: deadline otomatik fact invalidation değildir. [Test tanımı](https://github.com/getzep/graphiti/blob/964bb11d1e7020e3cc67fab244268b0736b6c219/tests/utils/maintenance/test_temporal_edge_utils.py) bu sınırın örneklerini içerir; çalıştırılmadı.

**Uyarlama adayı:** Zaman alanları/ilişki provenance ve supersession aday üretimi. **Korumamız gereken:** öneri, insan seçimi, uygulanmış değişiklik ayrı; edge contradiction otomatik task cancellation/approval olamaz. Graphiti modeli projection/retrieval katmanı adayı olabilir; kanonik append-only olay kaydı yerine konulmuş değildir. LLM extraction ve graph altyapısı token/işletim baseline'ına dahil edilmeli.

### ER-05 — Geç yanıt ve subagent beklemesi için hazır örüntü

[LangGraph types](https://github.com/langchain-ai/langgraph/blob/b4991f1ba36a2449ab59c38ab71828ee865bff84/libs/langgraph/langgraph/types.py) interrupt kimliği, Command resume ve node yeniden yürütüm davranışını; [test tanımları](https://github.com/langchain-ai/langgraph/blob/b4991f1ba36a2449ab59c38ab71828ee865bff84/libs/langgraph/tests/test_interrupt_state.py) interruption state örneklerini içerir. Kalıcı checkpointer ile soru bekleme/resume örüntüsü adaydır; soruyu yanıtlayanın yetkisi ve karar revision'ı Decivora tarafından ayrıca kontrol edilir.

[Resmî interrupts belgesi](https://docs.langchain.com/oss/python/langgraph/interrupts) resume öncesi yan etkilerin yeniden çalışabileceğini ve typed response ile ham JSON Schema validation farkını açıklar. [Persistence belgesi](https://docs.langchain.com/oss/python/langgraph/persistence) thread checkpoint ile cross-thread store'u ayırır; RAM saver restart sonrası kalmaz. Bu nedenle checkpoint'i kanonik hafızayla eşitlemeyiz.

**Uyarlama adayı:** question_id/interrupt_id eşlemesi, persistent wait, bağımsız iş ilerlemesi, idempotent resume. **Ek contract:** answer received → associated → approved → applied ayrımı; stale approval, late ambiguity, parent kaybı, ACL ve duplicate resume. Python source'u başka dilde doğrudan alınabilir sayma; ayrı JS repo bu tur incelenmedi.

### ER-09 — Bütçe rezervasyonu tek başına özgünlük değil

[Budget reservation](https://github.com/BerriAI/litellm/blob/2a01fe6e5ca2ed67472ca0ed2909e66811ff8d35/litellm/proxy/spend_tracking/budget_reservation.py) çağrı öncesi maliyet tahmini, çoklu spend counter, lease renewal, finalize/release ve fail_closed_budget_enforcement dalları içerir. [Release middleware](https://github.com/BerriAI/litellm/blob/2a01fe6e5ca2ed67472ca0ed2909e66811ff8d35/litellm/proxy/middleware/budget_reservation_release_middleware.py) callback'in sahiplenmediği rezervasyon temizliğini; [rate limiter](https://github.com/BerriAI/litellm/blob/2a01fe6e5ca2ed67472ca0ed2909e66811ff8d35/litellm/proxy/hooks/dynamic_rate_limiter_v3.py) limit örüntülerini gösterir.

Önemli sınır: seçili source'ta fiyat bilinmiyorsa reservation yerine read-time enforcement'a dönüş var; fail-closed konfigürasyonu ve cleanup yolları davranışı etkiler. INCRBYFLOAT pipeline görünmesi bütün owner/parent/child sayaçlarında tek atomik all-or-nothing transaction garantisi değildir; çağrılan backend ve hata senaryosu bu tur bütünüyle incelenmedi. In-flight cancellation input-cost uzlaştırması provider gerçeğiyle ayrıca doğrulanmalı.

**Uyarlama adayı:** gateway/native özellikleri kullanıp Decivora task/run/approval bütçe ledger'ıyla bağlamak. **Sınanacak fark:** scope bağlı risk onayı, tüm alt agent/retry bütçesi, unknown kullanımın muhafazası, reservation recovery ve callback tekrarları. Gateway dışındaki bağımsız host harcaması kontrol ediliyor diye sunulmaz. Maliyet tasarrufu veya hard-cap başarısı ölçülmedi.

### ER-07 — İzin önbelleği ürün davranışını etkiler

[Check command](https://github.com/openfga/openfga/blob/526995eb202464e2cace266fb5be56c212af9ecf/pkg/server/commands/check_command.go) model kimliği, request consistency ve tuple/context validation içerir; [check kaynağı](https://github.com/openfga/openfga/blob/526995eb202464e2cace266fb5be56c212af9ecf/pkg/server/commands/check.go) ayrı incelendi. [Resmî consistency belgesi](https://openfga.dev/docs/interacting/consistency) cache etkinse minimize-latency sonucunun hemen yapılan ilişki değişimini yansıtmayabileceğini, higher-consistency'nin DB'ye gittiğini belirtir. Cache varsayılan kapalı; her kurulum stale değildir.

**Uyarlama adayı:** user/agent → workspace/project/source yetki ilişkileri. **Ek contract:** revocation sonrası queued job/read/egress/approval yeniden yetkilendirme ve domain işlemindeki yarış. Higher-consistency tek başına farklı servisler arasında atomik revocation/execution sağlamaz. Cedar ile RBAC/ABAC/ReBAC ihtiyaç matrisi yapılmadan iki motor birden eklenmez.

### ER-02 — ADD-only extractor ile değişmez arşiv farklıdır

[Mem0 README](https://github.com/mem0ai/mem0/blob/b7ad69afda6b6ed030347c66d48a13e4de9dec08/README.md) ADD-only extraction ve yönetilen platform benchmark'ları ile OSS farkını açıklar. [Memory API](https://github.com/mem0ai/mem0/blob/b7ad69afda6b6ed030347c66d48a13e4de9dec08/mem0/memory/main.py) update/delete yolları; [storage](https://github.com/mem0ai/mem0/blob/b7ad69afda6b6ed030347c66d48a13e4de9dec08/mem0/memory/storage.py) history kayıtları ve reset/message retention davranışları içerir. ADD-only, kaynak ve history'nin bütün API'lerde sonsuza kadar korunması garantisi değildir.

**Uyarlama adayı:** extraction/retrieval native baseline; oracle, provenance, retention ve canonical history Decivora contract'ına göre ayrı kontrol edilir. Yönetilen sürümün accuracy/token rakamı OSS veya Decivora sonucu olarak kullanılmaz.

## Kod alımı ve lisans kapısı

Root lisanslar okundu; Apache/MIT etiketinden dosya bazında tüm uygunluk sonucu çıkarılmadı. Her alım için immutable path, copyright/NOTICE, yapılan değişiklik, transitif dependency, prompt/model/asset hakları ve dağıtım uyumluluğu gerekir. [Lisans stratejisi](../governance/licensing.md) geçerlidir.

- LiteLLM [root LICENSE](https://github.com/BerriAI/litellm/blob/2a01fe6e5ca2ed67472ca0ed2909e66811ff8d35/LICENSE) enterprise/ alanını ayırır; gerçek [enterprise/LICENSE.md](https://github.com/BerriAI/litellm/blob/2a01fe6e5ca2ed67472ca0ed2909e66811ff8d35/enterprise/LICENSE.md) ayrıca okunmuştur. Root metindeki enterprise/LICENSE yolu ile ağaçtaki gerçek LICENSE.md adı farklı; hakları root etiketten tahmin etme. Üretim kullanımı için ayrı ticari şartlar var; bu alandan source alınmaz. Ayrıca incelenen dynamic rate limiter, priority için TPM/RPM rezervasyonunu premium feature/license kontrolüne bağlıyor. Core dizininde bir dosyanın bulunması tüm özelliklerin lisanssız etkin olduğu anlamına gelmez; bu gate'i kaldırarak reuse önerilmez.
- Langfuse [root LICENSE](https://github.com/langfuse/langfuse/blob/cb2cebae9f8e7d53e8e514780fce8493d680ecfb/LICENSE) ee/, web/src/ee/, worker/src/ee/ alanlarını dışarıda bırakır; [ee/LICENSE](https://github.com/langfuse/langfuse/blob/cb2cebae9f8e7d53e8e514780fce8493d680ecfb/ee/LICENSE) ayrıca okundu. Core ve ticari UI/özellik aynı reuse hakkı sayılmaz.
- Cognee [NOTICE](https://github.com/topoteretes/cognee/blob/0ec7a9fa61c9ff04bf7e02e0d57af363a993a5e1/NOTICE.md) okundu. Yerel model indirme opsiyonunun model ağırlığı lisansı/transitif hakları bu tur doğrulanmadı.
- Cedar root Apache lisansı okundu; root tree'de NOTICE/THIRD_PARTY_LICENSES.txt görüldü, içerik/transitif uygunluk incelemesi alım öncesi bekler. Root lisans taraması hukuki onay/uyumluluk sertifikası değildir.

Bugünkü öneri **kaynak/contract araştırması**dır. Seçenekler her aday için native ürün, mevcut ürüne extension, küçük port/paket veya kendi uygulamamız. Bütün platformu fork etmek varsayılan değildir. Yan yana on dependency eklemek token ve bakım ekonomisine ters düşebilir.

## Ardışık küçük araştırma işleri

| İş | Durum | Çıktı / kabul kriteri |
|---|---|---|
| ER-R1 — bounded keşif | DOC_COMPLETE | 10 aday, pinned SHA, gerçek root lisans, kaynak seviyesi, hedef task, karşı kanıt; bu belge ve JSON mevcut. Runtime tamamlandı anlamına gelmez. |
| ER-R2 — üç odaklı code/contract incelemesi | TODO | Graphiti supersession/temporal, LangGraph durable wait/resume, LiteLLM reservation/unknown yolları; export/dependency/test closure ve source-path→Decivora contract matrisi. İncelenmemiş bölüm açık işaretlenir. |
| ER-R3 — uygunluk ve aynı oracle ile deney önerisi | TODO | Native/config/extension/port/own için kurulum, izin, lisans, bounded harcama ve bakım planı; çalıştırma yetkisi ve T01/T02/T03a tamamlanmadan runtime yok. |
| ER-R4 — karar önerisi | TODO | Ölçüm varsa eşit kalite/maliyet; yoksa null/not_run. Native yeterliyse native öner. Alım/mimari kararı owner'a alternatif/bedel ile sun; gerekçeli eleme de geçerli çıktı. |

**Önerilen sıra:** ER-01/05/09 derinleşsin; ER-02/03/04 yakın memory/native baseline havuzunda tutulsun. ER-07/08 ekip policy modeline ilişkin ihtiyaç netleştiğinde; ER-10 telemetry ihtiyacı, ER-06 dağıtık kapasite gerekçesi oluştuğunda. T01 ana geliştirme sırası ve T03d/Q13 mevcut reuse tercihleri açık kalır. Bu belge Q13-A seçimi değildir.

## Deney planı ve ölçüm

Yeni planlanan araştırma senaryoları:
- **ER-T1:** yeni karar → eski gerekçenin geçerliliği → AND/OR etkisi; Graphiti baseline. [GAP](../product/intent-to-reality-gap.md) ile öneri/applied ayrımı birlikte.
- **ER-T2:** iki pending soru, geç cevap, process restart, duplicate resume, parent kaybı ve stale permission; LangGraph ve kendi [LATE](../product/pending-questions-and-late-answers.md) sözleşmesi.
- **ER-T3:** parallel parent/child, retry, unknown fiyat/kullanım, disconnect, callback duplicate, backend failure; LiteLLM/config ve kendi [token risk](../product/token-risk-and-approval.md)/limit oracle'ı.
- **ER-T4:** ilişki iptali → queue/context/approval erişimi; OpenFGA/Cedar ile [erişim sözleşmesi](../architecture/identity-access.md).
- **ER-T5:** aynı bounded [devam paketi](../product/resume-package-and-memory.md) görevi, source coverage ve review süresi; native memory/extension ve bağımsız çekirdek.

Beşi de **not_run**. Desteklenmeyen feature ile çalıştırılmayan feature ayrılır. Dataset revision, commit/config, cost-price snapshot, bütün extraction/retrieval/retry çağrıları, tool response token'ları ve manuel review süresi kaydedilir. Ölçülmeyen sıfır yazılmaz. Framework'ü tam kullanıcı ürünüyle bütün özelliklerde yarıştırma; bileşen senaryosu ile uçtan uca ürün baseline'ı ayrı raporlanır.

**Yatırım ölçütü:** Aynı doğruluk/izin/kanıt şartlarında daha düşük toplam kullanıcı yönetim süresi, token, geliştirme ve işletim yükü. Sonucu önceden Decivora lehine tanımlama. Yeni repository ismi veya engine adı kendiliğinden değer kanıtı değildir.

## Ölçüm yöntemi için hedefli takip — 2026-10-11

Kullanıcının teknik ölçülebilirlik sorusu üzerine [evaluation protocol](../quality/evaluation-protocol.md) hazırlandı. Graphiti'nin aynı pinned ref'inde graph-building eval/judge prompt; ayrı Langfuse Python SDK bf11ec121479145923ff27b32ec2ad1d06fd2d51 ref'inde experiment.py/unit test/LICENSE okundu. SDK önceki Langfuse server source kapsamından farklı repodur; önceki 10 aday JSON'u bütün SDK incelendi diye değiştirilmedi. Source okumaları statik; testler, exporter/platform/CI ve model çağrısı not_run.

ER-R2 üç runtime adayının tüm export/dependency closure incelemesi tamamlanmadı. Bu takip yalnız oracle/scoring/run/error örüntüsünü çözer. Yeni T01f/T03f/T24q küçük işleri; bağımsız typed oracle, exact evidence ve incomplete gate protokolde. Bounded araştırma bittiğinde corpus/harness deneyine geçilir; yeni broad scan veya dependency adoption kararı yok.

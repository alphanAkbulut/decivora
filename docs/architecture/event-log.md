# Event log, projection ve audit

## İki farklı olay türü

**Source events:** Kullanıcı/assistant mesajı, tool result, dosya olayı, import fragment. Bunlar gözlemdir; doğruluk veya onay yetkisi taşımaz.

**Domain events:** `record.captured`, `changeset.proposed`, `changeset.approved`, `decision.superseded`, `task.implementation_claimed`, `verification.passed`, `verification.failed`, `verification.invalidated`, `task.reopened`, `approval.deferred`, `binding.changed` gibi policy kontrolünden geçmiş durum olaylarıdır.

Ham metin ayrı, korumalı bir payload deposunda tutulabilir; event güvenli referans ve hash taşır. Retention/erase istisnası [gizlilik belgesinde](../governance/risks.md).

## Önerilen zarf

```json
{
  "schema_version": 1,
  "event_id": "evt_example_005",
  "workspace_id": "ws_demo",
  "project_id": "prj_demo",
  "stream_id": "task_demo_01",
  "stream_version": 5,
  "event_type": "task.reopened",
  "occurred_at": "2026-10-09T12:35:00Z",
  "ingested_at": "2026-10-09T12:35:01Z",
  "actor": {"type": "system", "id": "verifier"},
  "source_refs": ["source_demo_04"],
  "correlation_id": "cs_demo_01",
  "causation_id": "evt_example_004",
  "idempotency_key": "prj_demo:verification_demo:reopen",
  "payload": {"reason": "acceptance test failed", "verification_id": "verification_demo"}
}
```

Bu örnek sentetiktir, runtime şema uygulaması değildir. Zaman damgası sıralama otoritesi değildir; append sequence/stream_version belirleyicidir. Late event ayrı gözlem olarak eklenir; eski zamana sahip diye bugünkü durumu körlemesine geri sarmaz.

## Atomik uygulama ve concurrency

1. Capture endpoint doğrulanmış kaynak zarfını ve job'ı dayanıklı storage'a yazar; bundan sonra receipt verir. Adapter ingest cursor'ı bu receipt sonrası ilerler.
2. Worker yeni aralığı işler, extraction sonucu ve source→record mapping'i aynı commit'te saklar. Ayrı processing cursor yalnız başarıyla kalıcı yazılan kesintisiz aralığa ilerler. Model hatasında başarısız aralık atlanmaz; lease/fencing eski worker'ın yazmasını engeller.
3. Change set uygulanırken project/actor policy, digest, tüm base revisions, graph knowledge revision, edge referansları ve AC sürümleri kontrol edilir. Preview sonrası eklenen gerekçe edge'i eski onayı stale yapar.
4. Tek transaction içinde domain events, projection değişiklikleri ve outbox kayıtları yazılır. Kısmi create/link olmaz.
5. Aynı idempotency key ve aynı digest önceki sonucu döndürür; farklı digest conflict verir. Aynı record'a eşzamanlı yazan agent'lardan biri version conflict alır.
6. Dış API transaction'ın parçası değildir. Outbox consumer ayrı retry/idempotency ile çalışır; local success dış sistem success diye gösterilmez.

Bağlı kaynak dedup anahtarı workspace/project/provider/account/session/source_epoch/source_event_id/source_revision bileşimidir; [runtime sözleşmesi](runtime-contracts.md) ve [DB ilişkileri](data-relationships.md) aynı kapsamı kullanır. Henüz bağlanmamış kaynak quarantine sahibinin erişim kapsamında tutulur; sahte project_id verilmez. Content hash değişiklik saptamak içindir; aynı cümleyi farklı oturumda söylemek yeni olay olabilir. Kaynak ID yoksa kararlı import manifest + source_epoch + offset + content hash birlikte kullanılır; yeniden import aynı manifest'i korur. Quarantine→project binding provenance ve receipt eşlemesi T05/T06'da doğrulanır; bu işlem yeni capture veya içerik paylaşma izni oluşturmaz.

## Hatalı tamamlanma ve geri alma

| Olay | Anlam |
|---|---|
| EVENT-001 | Task ve AC oluşturuldu |
| EVENT-002 | Çalışma başladı |
| EVENT-003 | Agent implement edildiğini iddia etti |
| EVENT-004 | İlgili AC testi başarısız oldu |
| EVENT-005 | Task yeniden çalışma gerektiriyor; verification failed |

EVENT-003 silinmez. Eski sistemden gelen “done” kaydı ayrıca legacy/unverified etiketlenebilir. Undo, yeni compensating change set'tir; mevcut revision ve downstream etkiler tekrar kontrol edilir. Geçmiş satırları düzenleyen Undo yoktur.

## Projection ve bütünlük

Projection tabloları: records, record_versions, relationships, approvals, evidence_links, processing_state, project_bindings. Replay yalnız saklı domain olaylarına dayanır; LLM, verifier veya dış delivery çağırmaz. Outbox kaydının yeniden projekte edilmesi teslim edilmiş işlemin yeniden gönderilmesi değildir. Projector version ve schema migration kaydedilir. Snapshot replay'i hızlandırır fakat source of truth olmaz. Recovery ve iki cursor ayrıntısı [runtime sözleşmelerindedir](runtime-contracts.md).

Normal agent API'sinde UPDATE/DELETE event ve arbitrary SQL yoktur. Ayrı process/file izinleri, hash chain ve dış checkpoint/backup izinsiz değişikliği tespit etmeye yardım eder. Aynı yöneticinin DB ve tüm hash'leri değiştirmesine karşı mutlak garanti yoktur. Restore drill sırasında event sayısı, son sequence ve projection digest karşılaştırılır.

## Kayıt sınıfları ve ekip uzantısı

Bu belgedeki source/domain ayrımına ek olarak [security audit ve operational telemetry](logging-audit.md) ayrı amaç, erişim ve retention taşır. DB WAL audit kaydı değildir. Event actor bilgisi güvenilir transport'tan üretilir; gerektiğinde on_behalf_of, grant/run ve authz revision kaydedilir. Permission değişimi ve high-impact command başarı audit'i aynı yerel transaction'da kalıcıdır.

Zarftaki tenant/proje kapsamı source dedup, stream unique key ve idempotency anahtarlarına da dahil edilir; sadece aynı ID'ye sahip farklı tenant verileri birleşmez. Ham payload silinmesi kompakt dedup kimliğini silmez. [Depolama planı](storage-memory-capacity.md) minimal event payload, privacy purge ve restore sonrası tombstone uygulamasını tamamlar.

## İptal ve ilişki değişimi olayları

`task.cancelled`, `relationship.ended` ve `relationship.invalidated` farklı önerilen domain olaylarıdır. İlki yürütme kararını; diğerleri ilişki geçerliliğini değiştirir. Eski event/edge revision silinmez. Geri alma yeni yetkili revision ve etki değerlendirmesi gerektirir. Projection aktif edge'leri günceller, tarihçe eski görünümü korur; knowledge revision değişimi eski approval'ı geçersiz kılar. [Graph UX](../product/graph-experience.md) normal iptalin privacy purge veya yalnız görünüm filtresi olmadığını açıklar.

## Artifact uygulama geçmişi ve güncel karar

[ADR-0011](adr/0011-target-application-evidence.md) için örnek domain türleri: `artifact.generation_claimed`, `artifact.generated_observed`, `application.expectation_proposed`, `application.reported`, `application.observation_recorded`, `application.assessed`, `application.assessment_stale`. Bunlar **önerilen event kataloğudur**, uygulanmış runtime enum/schema değildir. Kaynak observation'ın domain event'e dönüşmesi kimlik/policy ve şema doğrulaması ister; source metni kendi başına karar yetkisi taşımaz.

Projection, expectation ve assessment geçmişini target/ref/artifact/decision revision'larıyla tutar; current pointer ilgili freshness'e göre türetilir. İnsan “yükledim” beyanı reporter/authority ile reported kalabilir; acceptance human_attestation policy'si ayrı ve açık. `application.assessed: observed` kendiliğinden `verification.passed` veya task completion olayı üretmez.

Yeni onaylı karar önceki uygulamayı tarihsel olmaktan çıkarmaz; current uygunluk ve stale assessment ayrı olayla değerlendirilir. Restore/replay bu gözlemleri yeniden gösterir, dosya read/upload/LLM/check başlatmaz. Kaynak kaybı ve privacy purge observation availability'yi etkileyebilir; geçmişten current erişim/onay üretilemez.

# RECEIVER-002 hazırlığı — model çalıştırılmadı


**Güncel actual durum:** [RECEIVER-002 tek native run](../../docs/quality/receiver-002-result.md) tamamlandı, invalid_contract; [ayrı onay](authorization.json) tüketildi. Aşağıdaki request/manifest/scorer örneği frozen hazırlık snapshot'ıdır; actual başarı veya yeni dispatch izni değildir.
[Plan ve sınırlar](../../docs/quality/receiver-next-plan.md) · [Yerel hazırlık raporu](../../docs/quality/receiver-next-preparation-results.json).

- `request.json`: yeni identity, pinned source sidecar, projection/schema ve gönderimsiz metadata.
- `prompt.txt`: **8089 UTF-8 byte**, newline dahil; yalnız bu metin olası alıcıya gider.
- `response.schema.json`: prompt içinde de taşınan ortak typed machine schema; provider enforced değil.
- `expected.json`: ayrı authored_draft oracle, insan gold/model cevabı değil; alıcıya gönderilmez.
- `manifest.json`: exact file/schema/source hash'leri, önerilen one-turn sınırı ve authorization **not_granted**.

Request ID `f60e6a29a6b475a3cfc9b97162a6caf0ebdd3bfd91e6e8045fee7b4eb1a9c42f`, prompt SHA `14f68a36d7ee013eb07fbbef4c214e264a7108d00bc73529f30c9044878efb48`. Yeni wire `decivora-receiver-review-2`; önceki klasör/ham run/manifest/code proof'ları değiştirilmedi. Bu bir hazırlık teslimidir; henüz yeni model cevabı, yetki veya API bütçesi yok.

Manifest/request hazırlık snapshot'ları frozen kalır; ileride owner izni veya actual run geldiğinde ayrı request/hash bağlı authorization/run kaydı eklenir. Hazırlığın actual0/not_granted alanları geçmişi yeniden yazmak için değiştirilmez.

# T13b — İptal, edge ending ve compensating dönüş

**Tamamlandı: local/manual T13b çekirdeği. Ana T13 In Progress.** [Guard kodu](../../packages/domain/task_lifecycle.py), [19 yeni regression](../../tests/runtime/test_task_lifecycle.py), [sonuç/hash](task-lifecycle-results.json), [şema/diyagram](../architecture/task-lifecycle.md). T13c versioned AC/DoD ve T13e question/late-answer çözümü açık; yeni görev ID'si yok. Gerçek UI/host/semantic inference/verification kabulü değildir.

```sh
python3.12 -B -m apps.hub lifecycle-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Demo real isolated SQLite'de ayrı impact/seçim/onay ile todo→cancelled→todo işlemlerini uygular. İki lifecycle event'i, artan record version'ları ve asserted ilişki korunur; replay digest'i aynı. İptal Task silmez, verified completion üretmez. Geri dönüş metadata overwrite değil yeni onaylı event'tir.

## Kabul sonuçları

| Kabul / risk | Kodla doğrulanan davranış |
|---|---|
| Task cancel ≠ edge ending | Review end_link edge'i bitirir; Task todo ve lifecycle history boş kalır. End_link sonrası eski cancel onayı stale olur |
| Geçmiş / ilişkiler korunur | İptalde record sayısı aynı, edge asserted, Task history cancelled; reopening history cancelled→todo |
| Aktif ihtiyaç sessiz kapanmaz | Live OR, ifade dışındaki required_by/implements gerekçesi, depends_on downstream ve part_of parent (aynı changeset'te eklenecek ilişkiler dahil) guard'ları cancellation ret/review üretir |
| Batch açık onaylıdır | İki independently obsolete Task birlikte explicit seçilirse ikisi aynı transaction'da iptal edilebilir; implicit cascade yok |
| Bilgi boşluğu ≠ obsolete | Cancellation yalnız complete false-rationale obsolete_candidate üzerinden; missing/AND update/unknown/partial kapsam onay yolu iptal üretmez |
| Completion korunur | Historical completion taşıyan proposal cancellation'a çevrilmez; T14 gerçek evidence ayrı açık |
| Normal metadata state değiştiremez | Update açıklama/başlığı değiştirir, mevcut cancelled state'i korur; lifecycle Task type değiştirerek guard aşılamaz |
| Authorization ve current snapshot | Bare generic human approval lifecycle için yetmez; ReviewService source/knowledge/authz/policy/decision snapshot'ı ve impact ID/record revision bağını kontrol eder |
| Rollback / replay / restore | Audit failure lifecycle version/event/projection değişimini geri alır; retry tek effect, restart/replay/backuprestore state ve history'yi korur |
| Aktif sıra / scope | Cancelled Task ready olmaz ve aktif rank'ten çıkar; task_history project ACL'si taşır. Cancelled dependency passed sayılmaz |

19yeni/167 toplam runtime test geçti. T13a stale/source/policy/role/concurrent approval testleri de bu suite'te korunur. Root takip kontrolleri teslimde ayrıca yürütülür. Ücretli model/API veya gerçek kaynak çağrısı0; geliştirme sohbetinin kullanım miktarı unknown.

## Depolama ve sürüm sınırı

SQL FORMAT/schema1 aynı; implicit migration/newtable yok. Yeni domain event kind `task_lifecycle` mevcut Task stream'inde version artırır; Task read body'de execution optional alanı oluşur. Önceki üç alanlı Task default todo; input create/update body üç alanlı kalır ve execution yazamaz. State history reason + impact ref ile event log'dadır. [Operation schema](../../manifests/task-lifecycle-event.schema.json) review-groups schema'ya referansla eklendi. Generic JSON Schema engine çalıştırıldığı iddia edilmez; custom runtime validator test edildi ve JSON/alan/limit artifact'i kontrol edildi.

Eski runtime yeni kind'ı replay edemeyip fail-closed durur; lifecycle event'i yazılan DB güncel runtime ile açılmalı. T13b restore/replay güncel kodla doğrulandı; production migration/key recovery/retention T23'tedir. Replay bugünkü impact sonucundan eski kararı yeniden üretmez; saklı event'in type/stream/version/transition'ını kontrol eder, dış işlem/model tetiklemez.

## Diyagram / doküman güncelliği

Bir yeni lifecycle flowchart ve iki değişen review diagramı cachedMermaid11.17.2 ile dış ağ kapalı render edildi; XML/title/description/source+SVG hash kontrolü geçti. Yeni lifecycle ve updated storage görselleri masaüstünde incelendi; sequence lifecycle guard etiketi render/source üzerinde kontrol edildi. Toplam41source/20belge; eski38 kaynak değiştirilmedi ve yeniden render edilmiş sayılmaz. Önceki iki review render kaydı superseded history'de saklandı. SVG export'ta HTML br tag'ları self-closing XML biçiminde normalize edildi; model/product UI doğruluğu render'dan çıkarılmaz.

## Kalanlar

Ana sayım **7 Done / 6 In Progress / 17 To Do**; T13a/b Done. Sırada T13c: işe başlamadan versioned AC/DoD ve applicability kararı. T13e pending QuestionRequest/AnswerRecord çözümü ve T14 evidence/completion açık. Aktif gereksinime rağmen force-cancel/override bu çekirdekte desteklenmez; gerekli kapsam/risk kararı review'ya gider. Manual facts/rationale doğru semantik bilgi kanıtı değildir. Bu sınırlar ana ürün vizyonunu silmez ve extra API harcama izni oluşturmaz.

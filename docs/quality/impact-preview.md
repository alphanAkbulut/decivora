# T12 — Çalışan karar etkisi önizlemesi

**Uygulandı: local/manual deterministic çekirdek.** [Engine](../../packages/impact/preview.py), [workspace bağlantısı](../../packages/storage/workspace.py), [21 yeni test](../../tests/runtime/test_impact_preview.py), [sonuç/hash kaydı](impact-preview-results.json). T12/T12a çekirdek kabulü tamamlandı; görev durumlarını uygulayan güvenilir review/onay T13, gerçek evidence/completion T14 ve otomatik anlam çıkarımı T09/T10 ayrı kalır. Bu teslim gerçek model kalitesi veya MVP AC-05'in bütün ürün pilotu kanıtı değildir.

```sh
python3.12 -B -m apps.hub impact-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Demo yeni temporary SQLite workspace'e sentetik Decision/Requirement/Task kayıtlarını ayrı manual approval ile kurar. Sonra varsayımsal storage değişikliğini değerlendirir; **preview kaynaklı canonical değişiklik0**, model çağrısı0. Yedek/restore sonrası aynı ImpactRun okunur. Fixture'daki completion işareti açık manuel örnek metadata'sıdır; demo gerçek verification üretmez. Eski [impact-scenario](../../examples/impact-scenario.json) oracle dosyası değiştirilmedi; `implemented:false` eski fixture provenance'ıdır, güncel kod durumunun otoritesi bu rapordur.

| Önceden tanımlı örnek | Gerçek demo önerisi | Neden |
|---|---|---|
| T1: geçmiş tamamlanmış iş | review | Geçmiş korunur, güncel uygunluk ayrı |
| T2: eski depoyu değiştirme | update | Açıkça kaydedilmiş replacement, scope incelemesi gerekir |
| T3: sadece eski mimari için sync | obsolete_candidate | Önceden geçerli bütün OR alternatifleri false |
| T4: eski mimari OR import | keep | Import gerekçesi true; counter-evidence gösterilir |
| T5: eski mimari AND export | update | Zorunlu koşul bozuldu; otomatik iptal yok |
| T6: gerekçesi eksik iş | review | Bilgi yokluğu gereksizlik kanıtı değildir |

## Uygulanan sözleşme

- Exact trigger kind/record/version; record metadata/fact revision projenin aynı SQLite snapshot'ına bağlanır. Facts ve rationale **açık manual hypothetical input**'tur; sistem bunları metinden çıkardığını veya doğruladığını iddia etmez. Public/trusted login API yok.
- `required_by`, `implements`, `depends_on`, `part_of`, `refines`, `conflicts_with` yönlü ters traversal ve explicit justification referansları visited set ile izlenir. Bağımlılık yalnız etki incelemesi için yol olabilir; kendi başına obsolete yaymaz. Her kaydın tüm rationale ifadesi AND/OR/unknown ile yeniden değerlendirilir.
- Geçerli kalan gerekçe keep; bütün kayıtlı OR alternatifleri true→false ise obsolete **adayı**; bozulmuş AND veya explicit replacement update; unknown/missing review. Historical completion her öneride ayrı korunur. Reason path, karşı kanıt, önce/sonra truth ve record version görünür.
- Trigger kind'ı anlam çıkarımı değildir: teknoloji adından ilgili işi tahmin eden semantic yol henüz yoktur. Güncel enum mevcut trigger kataloğunun deterministic dilimini temsil eder; periodic/verification trigger'ları sonraki mevcut görevlerdedir.
- Traversal varsayılan100 node/500 edge; çağıran en fazla1000/5000'e çıkabilir. Partial traversal'ın frontier'ı ve visited listesi saklanır; coverage incomplete olunca bütün öneriler review'a düşer. Eksik gerekçeli kayıtlardan bounded orphan review da üretilir. Tam geçmişin keşfedildiği iddia edilmez.
- Manual input32KiB, result64KiB, snapshot1000 kayıt, proje başına128 immutable preview geliştirme tavanı. Tavan aşımında partial canonical iş yok; explicit ret gelir. Bunlar production capacity/SLO veya ücret bütçesi değildir. Büyük graph/storage-retention politikası sonraki aşamalardadır.
- `Workspace.impact_preview` current writer+active project yetkisi ister; **audit'te kalıcı preview** ekler, record/edge/event/task state değiştirmez. Aynı run ID+actor+input retry aynı sonucu verir; changed input conflict, knowledge/authz/source frontier değişimi stale olur. Kaynak receipt/job/gap/quarantine snapshot'ı da bağlanır; knowledge revision değişmeden yeni mesaj gelse eski sonuç güncel sayılmaz.
- Kaynak namespace/frontier okunurken current ACL uygulanır. Bilinen receipt gap veya quarantine varsa coverage incomplete olur; başarıyla işlenen tek position2 position1 eksikliğini gizlemez. Kaynakta henüz hiç gözlenmemiş mesajların varlığı ispatlanamaz; actual adapter coverage T16'dadır.
- `Workspace.impact_run` güncel read ACL ile immutable tarihsel sonucu ve stale bayrağını döndürür. Restart/replay/backup/restore sonucu korur. Audit insert hatası yarım run bırakmaz. Archive ve authority değişimi eski preview'yu uygulanabilir göstermez.
- Digest trigger, bütün öneriler, kaynak/knowledge/authz snapshot, run/input kimliği dahil çıktı üzerine hesaplanır. Bu **onay token'ı değildir**; T13 bu digest'e ayrı insan seçimi/policy/operation group bağlayacak. Incomplete/stale preview görev iptali için kullanılmayacak.

## Kabul ve doğrulama

21 yeni runtime test; toplam130 başarılı. Mevcut altı-case oracle, missing-link, AND/OR/unknown, traversal limit/frontier, cycle termination, trigger/fact/record revision, dependency-only no-obsolete, input immutability, duplicate/restart, yeni OR edge yarışı, receipt/coverage değişimi, gap/quarantine, actor/ACL/archive, audit rollback, backuprestore ve executable CLI sınandı. Oracle converter yalnız eski fixture referanslarını opaque runtime ID'lerine çevirir; beklenen action vektörü hesaplayıcıdan üretilmez.

T12a tamamlandı; yeni task ID açılmadı. Ana sayım **7 Done / 5 In Progress / 18 To Do**. Tam MVP14AC, semantic extraction, gerçek completion, kullanıcı UI ve source adapter kapıları açık. [Önceki kritik düzeltmeler](core-critical-review.md) ve tarihsel kanıtlar yeniden yazılmadı. Mevcut mimari diagramları preview→ayrı onay akışını zaten gösterir; bu tur diagram/schema topology değişmedi, yeni render iddiası yok.

## Sonraki mevcut iş

T13: önerilerin accept/reject/defer/compare seçimi, partial selection dependent group doğrulaması, digest/snapshot/policy-bound ayrı onay ve stale/double approval. T12 preview'nun ürettiği adaylar kullanıcı kararı, gerçek task cancellation veya verified completion yerine geçmez. T09 API finansman checkpoint'i zorunlu gerçek semantic çalışmaya gelindiğinde hatırlatılacak; bu teslimde ücretli çağrı gerekmedi.

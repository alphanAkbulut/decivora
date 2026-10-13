# Reconciliation ve karar farkındalıklı etki analizi

## Capture → canonical knowledge

1. Kaynak olayları proje ve session ile böl; redaction ve erişim kontrolü uygula.
2. Açık araç kayıtlarını deterministik çıkar. Serbest konuşmada kaynak span'lı adaylar üret; model başarısızsa işi retry veya review'ya bırak.
3. Önce ID, ilişki, kelime/FTS ve revision filtreleriyle ilgili kayıtları getir. Embedding sonraki optimizasyon; benzerlik doğruluk kanıtı değildir.
4. Her aday için `new`, `duplicate`, `refinement`, `conflict`, `supersession_candidate`, `previously_rejected`, `uncertain` önerisi üret.
5. Önerilen change set başlık, açıklama, AC, gerekçe, karşı kanıt, etkilenen kayıtlar, kaynaklar ve base revision içerir.
6. Policy izin verdiği düşük riskli capture/provenance güncellemelerini uygular; onaylı bilgi, task scope ve karar değişimi kullanıcıya gider.

Sadece yeni mesajları okumak eski bağlamı unutturabilir: extraction sırasında atıf yapılan eski kayıtlar ve reddetme gerekçeleri de getirilir. Kaynak mesaj→aday→evaluation→onay→domain event zinciri “ne değerlendirildi?” sorusunun cevabıdır. Görüldü veya özetlendi işareti insan onayı değildir.

## Impact trigger kataloğu

| Trigger | Aday küme / sonuç |
|---|---|
| Decision approved/superseded | Eski karara gerekçeyle bağlı task, requirement, prompt ve artifact |
| Requirement revised | Implements ilişkileri ve AC/evidence geçerliliği |
| Feature cancelled | Alt işler, gerekçe koşulları, yeniden kullanılabilir çıktılar |
| Technology changed | Teknolojiye özgü karar/gereksinim alt grafiği |
| New idea/conflict | Reconciliation; hemen scope değişimi değil |
| Task implemented/test result | Verification ve downstream ready durumu |
| Periodic consistency audit | Orphan task, eksik gerekçe, stale evidence, kaçan kaynak aralığı |

Preview, önerilen yeni kararın **varsayımsal** etkisini gösterebilir. Apply yalnız onaylı change set digest'i ve güncel revisions üzerinde çalışır. Karar onayı ile ona bağlı task değişiklikleri aynı change set'te atomik uygulanabilir; alternatif olarak karar uygulanır ve impact incelemesi pending kalır. Hangi yol seçildiyse UI açık gösterir.

Pending impact, etkilenen işin uygulanabilirliği belirsiz demektir; next-ready/auto verification bunu geçmez. Preview `knowledge_revision` taşır; sonradan eklenen veya değişen gerekçe/edge varsa eski onay reddedilir. [ADR-0008](adr/0008-approval-snapshot-authority.md) bu yarışın korumasını, [diyagram 5](diagrams.md) örneğini açıklar. Bilinen etki kümesinin dışındaki eksik bağlar için coverage ve periodic audit gerekliliği sürer.

## Çalışan yerel dilim ve önerilen ileri entegrasyonlar

[T12/T12a](../quality/impact-preview.md) deterministic/manual trigger + bounded traversal + rationale proposals ve SQLite snapshot/persistence olarak uygulandı. `impact_preview` canonical kayıt değiştirmez; T13 ayrı selection/approval, T14 verification ve T09/T10 semantik trigger üretimi açıktır. Aşağıdaki algoritmanın semantic evaluation/onay/apply adımları bu teslimde uygulanmış sayılmaz.

## Önerilen algoritma

```text
on meaningful change:
  resolve authorized project + trigger revision
  collect typed reachable edges using visited set and traversal budget
  for each affected record:
    evaluate all recorded justification expressions in three-valued logic
    check remaining active requirements and artifact reuse
    if done historically: preserve completion; evaluate applicability separately
    if missing links / unknown / truncated traversal: propose review
    otherwise propose keep / update / replace / obsolete_candidate
  use bounded semantic evaluation only where rules do not settle meaning
  store reason paths, uncertainty and base revisions in change set
  request required approval; revalidate versions; append domain events
```

`depends_on` yürütme sırasıdır; yalnız bu edge üzerinden obsolete yayılmaz. `required_by` ve AND/OR grupları zorunluluğu tanımlar. Traversal bütçesi dolduğunda “analiz tamamlandı” denmez, kalan frontier saklanır. Aynı trigger/version için tekrar çalıştırma idempotenttir.

## Kanonik örnek

| Kayıt | Önce | Yeni karar sonrası öneri |
|---|---|---|
| T1 gereksinim dosyası | Gerçekten verified | Completion korunur; kullanım durumu ayrı incelenir |
| T2 Markdown karar deposu | Açık; yalnız eski mimari için | Replace/cancel önerisi; kullanıcı kararı |
| T3 Markdown sync | Açık; yalnız eski mimari için | Obsolete adayı |
| T4 file watcher | Açık; eski mimari OR belge importu için | Keep; import gerekçesi geçerli |
| T5 iki koşullu export | Açık; eski mimari AND özel export koşulu | Update/review; koşul bozuldu, otomatik iptal yok |
| T6 ilişkisiz iş | Gerekçe bilinmiyor | Review; güvenli biçimde obsolete çıkarılamaz |

Geliştirilen çıktı yeni karar altında yanlış olabilir; geçmiş olay ile güncel uygunluk ayrılır. Reddedilmiş öneri yeni kanıtla geri gelebilir fakat eski reddetme gerekçesi gizlenmez. [Sentetik fixture](../../examples/impact-scenario.json) gelecekteki test oracle'ını gösterir.

## Uygulama gözlemi gelmeden planı gerçekleşmiş saymama

[GAP sözleşmesinde](../product/intent-to-reality-gap.md) yeni upload report veya artifact observation ENG-03'te doğru task/proposal/target/revision ile eşleştirilir. Metinsel benzerlik human adoption veya exact target eşleşmesi sağlamaz. Yeni karar kabulünde ApplicationExpectation/ApplicationAssessment current uygunluğu da IMP-02/VER-02 kapsamında değerlendirilir; eski artifact uygulanmış olsa bile yeni planın uygulanması sayılmaz.

Karar current, uygulama unknown veya impact pending olduğunda context bunları ayrı taşır. Bilinen gerekli ön koşul unknown ise ilgili iş ready olmaz; bu belirsizlik bağımsız işleri kapatmaz. Source/event tarihçesi, AND/OR ve historical completion korunur; hedef değişimi bütün task'ları otomatik obsolete yapmaz.

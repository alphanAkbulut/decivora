# T13a — Kalıcı seçim ve ayrı onay çekirdeği

**Uygulandı: T13a. Ana T13 In Progress.** [ReviewService](../../packages/domain/review.py), [workspace atomic helpers](../../packages/storage/workspace.py), [18 yeni regression](../../tests/runtime/test_review_service.py), [sonuç/hash](review-kernel-results.json). T13b iptal/compensating lifecycle, T13c versioned AC/DoD ve T13e kalıcı soru/geç cevap çözümü açık olduğundan ana görev kapanmadı. Bu teslim terminal/API çağrısı üzerinden no-text review çekirdeğidir; kullanıcı UI kabulü değildir.

```sh
python3.12 -B -m apps.hub review-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Demo yeni temporary workspace'te gerçek manual impact preview oluşturur. Compare → seçili operation group → ayrı approve → explicit apply akışında yalnız onay sonrası apply record açıklamasını değiştirir; tekrar gönderim aynı receipt'i döndürür, replay digest'i eşleşir. **Task metadata update**, görev iptali veya verified completion değildir. Gerçek login/model/provider/dış araç çağrısı yok.

## Çalışan kurallar

- Caller yetkili proje writer'ı olarak typed operation gruplarını önerir. Gruplar impact proposal record ID'lerine bağlanır; create/update/link/end_link dışında komut çalıştırma alanı yoktur. Exact alan/type/body/relation, cycle ve bounded payload kontrolü uygulanır. Input32KiB, groups32, groupoperations64, dependency32; uygulanacak toplam operasyon ayrıca mevcut Workspace64 limitine tabidir. Sayılar development ceiling'dir.
- Compare salt okunurdur; stale flag ve hazırlanmış değişiklikleri gösterir. Accept/select group ID listesidir; serbest metin gerekmez. Reject/defer yetkili local human owner kararıdır; canonical kayıtları değiştirmez, audit'te korunur. Reddedilmiş proposal yeni ID/öneri olmadan canlandırılmaz. Uygulanmış işi reject geçmişini silmek yerine ayrı compensating değişiklik ister.
- Kısmi seçim yalnız seçilmiş grupları yeni plan/digest'e alır. Explicit dependencies ve seçilmiş link'in gerektirdiği temporary create ID'si dışarıda bırakılamaz. Omitted operations onay kapsamına girmez; birlikte seçilen create/link aynı transaction'da uygulanır.
- **Seçim ≠ onay ≠ uygulama.** Selection digest + actor + policy + ImpactRun digest + base knowledge + source frontier + authority snapshot bağlanır. `approve` current local human owner ister. Genel `Workspace.apply` review-bound token ile source/policy guard'ını atlayamaz; token yalnız ReviewService'in yeniden denetlenen yolundan kullanılabilir.
- Apply BEGIN IMMEDIATE içinde current ACL/active project, impact completeness/knowledge/source/authz, policy ve seçimden sonraki review kararlarını yeniden denetler. Yeni OR edge, yeni source receipt/gap, değişmiş policy veya defer eski seçimi durdurur. Defer sonrasında explicit yeni selection ile devam edilir; timeout/sessizlik otomatik onay değildir.
- Domain event/projection/command + review_applied audit tek commit'tir. Audit failure bütün domain değişimini geri alır. İki gerçek eşzamanlı SQLite connection aynı selection/token için yalnız bir effect üretir; duplicate aynı sonucu okur. Apply sonrası tekrar, yeniden işlem değil geçmiş receipt okumasıdır.
- Restart/backup/restore seçimi, approval ve uygulanmış sonucu korur. Replay kayıtlı domain event'leri kurar; yeni model/notification/runner/dış write veya review approval üretmez.
- Policy şu an kodun fixed `local-human-review-1` revision'ıdır; backoffice policy editor yoktur. Version değişimi eski seçimi reddeder. Agent compare/propose yapabilir; owner selection/approval/reject/defer/apply yetkisini taşımaz. Trusted local issuer gerçek hesap doğrulama değildir.

## Şema ve diyagramlar

[Input JSON Schema artifact](../../manifests/review-groups.schema.json), [renkli sequence ve storage şeması](../architecture/review-runtime.md), [sequence SVG](../../assets/diagrams/review-runtime-1.svg), [storage SVG](../../assets/diagrams/review-runtime-2.svg). SQL core FORMAT/schema1 korunur: yeni tablolar veya sessiz migration yok. review_created/selected/decision/approved/applied mevcut append-only audit.ref JSON payload'larıdır; bound approval mevcut approvals tablosunda kalır.

Custom Python validator runtime'da pozitif/negatif testlerle sınandı; JSON artifact parse ve alan/limit sözleşmesiyle eşleştirildi. Generic Draft202012 conformance sertifikası veya JSON Schema engine çalıştırma iddiası yok; bu ortamda jsonschema paketi bulunmadı, ek bağımlılık yüklenmedi. Actual HTTP/MCP endpoint de açılmadı.

İki yeni Mermaid cached11.17.2, ağ dış erişimi kapalı, ayrı headless Chrome'da render edildi; title/description/SVG kaynak hash'i kontrol edildi ve masaüstü görselleri incelendi. Storage yerleşimi okunabilir dikey düzene alındı. Önceki38 kaynak değişmedi; yeni toplam40 kaynak/19belge. Tüm eski çizimler yeniden render edilmiş veya ürün UI test edilmiş sayılmaz.

## Sonuç ve kalanlar

18 yeni/148 runtime test geçti. No mutation before apply, partial selection dependency, generic-token bypass, source/graph/policy stale, reject/defer, agent restrictions, audit rollback, restart/restore, simultaneous double-submit ve executable demo sınandı. Mevcut MVP14AC ve T13b/c/e gereksinimleri korunur; yeni task ID yok. Ana sayım **7 Done / 6 In Progress / 17 To Do**. T13a Done, ana T13 In Progress.

Sırada T13b: görev iptalini edge ending'den ayıran lifecycle ve compensating plan; sonra versioned AC/DoD ve pending question çözümü. Sadece Task açıklamasını değiştirerek cancellation/acceptance tamamlandı diye gösterilmez. Ücretli API/model/capture çalıştırılmadı; T09 gerçek semantic çalışma finansman checkpoint'i açık.

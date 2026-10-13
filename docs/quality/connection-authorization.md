# T05c — Sürümlü kaynak bağlantısı izin sözleşmesi

**T05c schema/rule fixture kapsamı tamamlandı; T05 ana görevi In Progress.** [Domain kodu](../../packages/domain/connection_authorization.py), [machine schema](../../manifests/connection-authorization.schema.json), [sentetik kayıt](../../examples/runtime/connection-authorization.json), [9 test](../../tests/runtime/test_connection_authorization.py), [sonuç/hash](connection-authorization-results.json).

```sh
python3.12 -B -m apps.hub connection-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Makbuz değişmeyen authorization/binding/resource ID, workspace/project, provider/account/source epoch; makbuz/binding/authz/policy revision; grantor/source evidence/approval refs; visibility/retention/egress policy refs; requested/externally-granted/application-allowed actions; include/exclude resource refs; source zaman aralığı, approved/expiry ve requested/granted/revoked statüsünü tutar. Credential/token veya transcript body yok. Kaynak/target/reference alanları opaque ID'dir; path/glob tarayıcısı, gizlilik politikası motoru veya provider grant kanıtı değildir.

Validation bounded exact alan/tip/revision/list/action/range kontrolüdür; payload'daki `granted`, `grantor_id`, approval ref veya dış izin listesi doğrulanmış onay sayılmaz. Schema yapısal alanları açıklar; cross-field kaynak seçimi, aralık ve üç action listesinin kesişimi Python kurallarında denetlenir. Genel JSON Schema engine/sertifikası değildir.

İnceleme ayrı typed ReviewContext ile karşılaştırır: workspace/project/binding/account/epoch/resource/grantor/revision/approval/source evidence eşleşmesi; scope digest; source access, target write, human approval, audit ve coverage'ın ayrı verified değerleri; expiry; action kesişimi. Eksik/unknown veya yanlış tipli doğrulama değeri denied olur. Source izni olmayan project owner veya target izni olmayan source owner, fixture kuralında review_ready olamaz. `capture_events` yalnız `read_source` makbuzundan türemez; write/execute action bu source sözleşmesinde yok.

| Kabul senaryosu | Kanıt |
|---|---|
| ACC01 source/target izni ayrı | Her iki yönün eksik/unknown/spoofed boolean context'inde denied |
| ACC03 proje/kaynak kimliği | Cross-project/workspace/account/binding/epoch mismatch ve stale revision ret |
| ACC07 makbuz ve scope | Digest değişimi/expired/requested/revoked, missing human/audit/source coverage ret; receipt payload ekstra approval/execution alanları ret |
| Çalışan demo | Sentetik own fixture: valid review_ready; missing source/stale context review_denied; capture/read/model0 |

9 yeni test ve toplam51 runtime test geçti. **review_ready bağlantı activation yetkisi değildir**; sonuç her durumda connection_activated false/source_read_performed false taşır. ReviewContext'in verified alanları fixture'da elle kurulmuştur: bu modül insan login, gerçek source ACL, imzalı approval, audit logger veya actual provider credential doğrulamaz. Anonymous tool/API source JSON'u ReviewContext'e dönüştürmemelidir; ileride authenticated policy/adapter/audit kanalından ayrı sağlanmalıdır. Dict context'i typed trusted context sayılmaz, ancak aynı Python process'teki arbitrary code güven sınırı değildir.

Makbuz persistence/version history/authority-signed approval henüz canonical runtime'a bağlı değil; schema/rule scope'u tek başına gerçek connection oluşturmaz. T05b normalized tenant/FK ve T05a alımda güvenilir epoch pinlemesi core kalanıdır; T06 durable receipt/quarantine source entegrasyonunu, T08b/T07b actual activation policy/audit'i tamamlar. Plan sırası/schema dependency gerçek source açılmadan doğrulanacak; standalone typed fixture hazırlanması bunların bitmiş olduğunu göstermez. T05d cross-source lineage sahibi T10, full login/team sonraki kapsam; T05'i büyütme veya otomatik kapatma yok.

Yeni task ID veya yeni ürün kapsamı eklenmedi; mevcut T05c satırı evidence ile güncellendi. Önceki başarısız model çıktıları ve tarihsel hash proof'ları korunur; yeni API/model/gerçek kaynak/dış yazım/ücret yok. Mermaid blokları değişmedi.

# T05h — Kalıcı yerel izin sürümü ve iptal

**Uygulandı; T05 ana görevi IN_PROGRESS.** [Kod](../../packages/storage/local_authority.py), [project transaction guard](../../packages/storage/project_store.py), [8 test](../../tests/runtime/test_local_authority.py), [CLI demo](../../apps/hub/authority_demo.py), [hash/sonuç](local-authority-results.json).

```sh
python3.12 -B -m apps.hub authority-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Yeni local authority profili açık bir owner ID ile ayrı boş DB'de kurulur. Mevcut legacy project DB'si sessizce yükseltilmez; owner/workspace değiştirilmez. Human/agent principal türü, active durumu ve read/write project setleri append-only authority_versions içinde korunur. Grant değişimi global authz revision artırır; izin genişletme de dahil önceki scope'lar stale olur. Owner inactive/agent yapılamaz. Agent ve normal kullanıcı grant yönetemez. Bunlar mevcut tasarımın yerel alt kümesidir; rol tablosunun tamamı uygulanmadı.

Scope trusted local adapter tarafından issue edilir; source JSON'dan veya actor metninden kabul edilmez. Python nesnesi açık store instance'ına bağlıdır; aynı alanlarla yeniden oluşturulmuş veya başka instance'tan taşınmış scope reddedilir. Grant yönetimi yalnız güncel human owner scope + base revision ile yapılır. Issue edilmiş bağlam sayısı development profilde1024, authority snapshot64KiB tavanındadır; yeni kabul sınırda durur, geçmiş silinmez.

**İşlem akışı:** Local authority command → ProjectStore BEGIN IMMEDIATE → issue kaydı/current authority revision kontrolü → current project/base kontrolü → snapshot/command commit. Query de aynı yetki/state snapshot'ını writer lock altında değerlendirir, sonra commit eder. Böylece revocation ve işlem SQLite'da sıralanır; iptal sonrası başlayan veya iptalden önce hazırlanıp sonra kullanılan eski scope geçmez. İptalden önce tamamlanmış okumanın kullanıcıdaki kopyasını geri alamaz. Cache retry de guard'dan geçer. Daha önce başarılı command'ın idempotency sonucu izinsiz geri verilemez.

| Senaryo | Gerçek test |
|---|---|
| Agent erişimi iptal | Eski read/write/cache retry ret; project revision değişmez |
| Scope taklidi | Aynı alanlarla constructed scope ve başka instance scope ret |
| Yönetici sınırı | Agent grant yönetemez; owner disable/agent dönüşümü ret |
| İki bağlantı/restart | Başka connection'ın eski bağlamı ret; persisted revoked principal yeniden issue edilemez |
| Read-only değişimi | Eski scope stale; yeni scope query yapar, write forbidden |
| Hatalı grant commit | Forced insert abort rollback; eski revision ve izin geçerliliği korunur |
| Legacy DB/owner değişimi | Ret; mevcut DB byte içeriği korunur |
| Çalışan CLI | Gerçek temporary SQLite grant/read/revoke/denied read/write/reopen; model0 |

8 yeni test, toplam runtime42 passed. [T05g](project-store.md) ve T05f tarihsel hashleri değiştirilmedi; guard/CLI güncel kodu bu yeni proof'tadır. T05'in ana kapanışı, bağlantı izin makbuzu/session-source metadata ve ilk ingress sınırları tamamlanmadan ilan edilmez. T08b genel action/resource policy ve T07b atomik security audit gelecekteki işler olarak kalır.

**Desteklenmeyenler:** Login/OAuth, cryptographic session/token, user-facing endpoint, expiring delegation, task/run grants, personal-source ACL, external model dispatch, audit export, role UI ve production team IAM. `issue_scope(principal_id)` kimlik doğrulaması yapan trusted local adapter içindir; anonim network tool/API'ye açılmamalıdır. Owner bootstrap gerçek kişinin hesabının doğrulandığı anlamına gelmez. Python'da trusted process içindeki arbitrary code/raw DB erişimi bu sınırı aşabilir; legacy ProjectStore trusted internal API olarak kalır, source-facing endpoint diye expose edilmez. Bu nedenle `human_authentication` capability false kalır.

Grant deny/rollback testleri process kill/power loss/production throughput kanıtı değildir. Authority revision global olduğundan ilgisiz grant değişimleri de context yenilemeyi gerektirir; ilk güvenli basit davranıştır, ölçülmüş UX/performans sonucu değil. SQLite çağrıları eşzamanlı aynı Python instance'ından thread kullanımına açılmadı. İptal, önceki authorized history'yi silmez; yeni event/snapshot üretir. Yeni harcama, gerçek kaynak veya model çağrısı yok.

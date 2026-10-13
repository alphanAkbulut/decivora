# Çekirdekte kritik boşluk incelemesi

**2026-10-13 / uygulanmış düzeltmeler / yerel sentetik-manuel profil.** Kullanıcı hızlanırken atlanan major/fatal eksikleri tamamlamamızı istedi. İnceleme T05–T08'in mevcut veri, yetki, arşiv, worker ve recovery sınırlarına odaklandı; genel refactor veya yeni entegrasyon değil. [Önceki teslim](integrated-core.md) ve hash raporu tarihsel olarak korunur. Bu kontrol bütün ürünün güvenlik sertifikası veya production kabulü değildir.

## Bulgular ve yapılan düzeltmeler

| ID / önem / mevcut sahibi | Önceki açık | Uygulanan davranış ve kanıt |
|---|---|---|
| CR01 / Major / T05,T08 | Arşiv yalnız binding/capture'da denetleniyordu; önceden onaylanan değişiklik ve worker çalışması devam edebiliyordu. | Yeni plan/onay/apply/lease/finish/budget/reservation arşivde reddedilir. Arşiv açma-kapama knowledge snapshot'ını ilerletir, lifecycle audit ekler, aktif lease'i fence ederek kuyruğa döndürür. Eski onay/worker yeniden açılınca da geçersizdir. Receipt ve geçmiş silinmez; tamamlanmış command retry yalnız eski sonucunu okuyabilir. Geçmiş okuma/replay/backup ve önceki kullanımı settle etme mümkündür. |
| CR02 / Major / T05 | Quarantine'da canonical project=NULL olduğu için local owner proje iznini kaybettikten sonra kaynak ve session frontier okuyabiliyordu. | Kaynağın admission'da yetkilendirilmiş claimed project'i ve varsa pinned binding projesinin güncel read ACL'si birlikte aranır. Frontier ve bütün DB yedeği aynı sınırı uygular. Owner rolü proje ACL'sini aşmaz. Henüz kayıtlı olmayan proje iddiası içeren karantina da yedeğe izinsiz girmez. |
| CR03 / Major / T06,T08 | Yetki değişiminden sonra aynı principal yeni context alarak eski lease'i tamamlayabiliyordu. | Lease grant'i append-only audit'te actor/source/fence/authz revision ile saklanır; completion güncel authority ile aynı grant'i ister. Eski veya önceki sürümden damgasız lease bekletilir, expiry sonrası yeni lease alınabilir. Lease actor/fence/expiry ve retry limitleri korunur. |
| CR04 / Major / T05,T07 | Backup yetki kontrolü ile SQLite kopyası farklı snapshot'lardan gelebiliyordu; arada yeni proje eklenebiliyordu. | Authorization, source ACL ve kopya tek read transaction'a bağlıdır. İki gerçek bağlantı/WAL yarışında daha sonra eklenen p3 yedeğe girmez. Snapshot alındıktan sonraki değişiklik sonraki işlemde değerlendirilir; yeni veri bu eski yedeğe katılmaz. Project/frontier/plan/projection digest okumaları da tek authorization/data snapshot'ı kullanır. |
| CR05 / Major / T07 | Replay bilinen op adına bakıyor, stream/version/base ve update hedefi eksiklerini atlayabiliyordu; var olmayan kayıt güncellemesi sessiz kabul ediliyordu. | Exact event alanları, record body, stream kimliği, ardışık version/base ve edge lifecycle yeniden uygulanırken doğrulanır; graph invariant'ları commit öncesi kontrol edilir. Hata transaction'ı geri alır, önceki projection kalır. Model veya dış servis çağrılmaz. |
| CR06 / Major / T07 | Restore manifest ile projection eşleşse bile canonical event'lerden farklı projection kabul ediliyordu; beklenmeyen hata bağlantıyı açık bırakabiliyordu. | Restore ayrıca canonical events → projection eşitliğini kontrol eder. Hata connection'ı kapatır, yalnız bu çağrının oluşturduğu hedef ve SQLite sidecar'larını temizler; backup ve mevcut kullanıcı hedefi korunur. Read-only proje içeren yedek offline doğrulanabilir; restore yazma izni vermez. Backup connection açılış hatasında yarım dosya kaldırılır; pending write transaction içinden backup, kilitlenmek yerine `backup_busy` ile reddedilir. |

**Fatal gerçekleşmiş veri kaybı veya production ihlali gözlenmedi:** Henüz gerçek kullanıcı/network/provider profili aktif değil. Major sınıflaması bu bug'ların o sınırları yanlış uygulaması içindir; zarar yaşandı iddiası değildir. Raw DB INSERT/corruption testleri normal agent'ın DB yönetici erişimi olduğunu varsaymaz.

## Tekrar üretim ve doğrulama

[14 regression](../../tests/runtime/test_core_regressions.py), [düzeltilen kod](../../packages/storage/workspace.py), [sonuç/hash kaydı](core-critical-review-results.json).

- İlk 10 regression, değişmeden alınan GitHub `595a4060ce0851cd6d0d5560b999defde4e4be5d` workspace modülü ile izole temporary DB'lerde çalıştırıldı: **10 test / 10 beklenen failure / 0 error**. Gerçek repo eski sürüme döndürülmedi. Restore failure testi açık bağlantıyı; race testi izinsiz yeni p3'ün kopyaya girmesini doğruladı.
- Nihai runtime suite: **109 test geçti**; önceki 95 korunur, 14 regression eklenir. İlk 10 regresyonun tamamı düzeltilen sürümde geçti. Son 4 test backup quarantine ACL, write-TX hang önleme, backup cleanup ve read-only restore sınırını genişletir; bu dört test için eski sürüm sonucu iddia edilmiyor.
- Integrated core-demo: receipt/dedup/frontier, atomic record/event, replay ve restore eşleşti; real semantic extraction/provider capture/human login false, model dispatch0.
- Root tracker/closure kontrolleri teslim doğrulamasında ayrıca çalıştırılır. Sayımlar değişmez: 6 Done / 5 In Progress / 19 To Do; yeni task ID yok. Bu düzeltmeler mevcut çekirdek sahiplerinin kabul sınırına aittir; ayrıca yeni backlog şişirilmez.

```sh
python3.12 -B -m unittest discover -s tests/runtime -v
python3.12 -B -m apps.hub core-demo
```

## Uyumluluk ve açık sınırlar

SQL schema/FORMAT değişmedi; sessiz migration yok. Yeni audit action'ları `project_lifecycle` ve `lease_granted`. Eski ongoing lease'in yetki damgası yoksa finish reddedilir; kayıt silinmez, expiry sonrası güncel worker claim eder. İlk profilden arşivli kalan DB'de arşiv guard'ı hemen uygulanır; yeniden açılması knowledge revision'ı ilerlettiğinden eski onay geri canlanmaz. Yeni dependency veya ücretli model/API deneyi yok.

Tam login/transport/gerçek source adapter, event schema migration, privacy purge + eski backup authority/consent'i dış servisler açılmadan güncel politika ile yeniden uzlaştırma, hostile filesystem/disk fault/load/RPO-RTO ve gerçek semantic kalite önceki T16/T23/T09 kapılarında açık kalır. Restore eski snapshot authority'sini taşır; dış bağlantı açıldığı veya güncel dış yetkiler doğrulandığı anlamına gelmez. Mevcut local issuer gerçek kimlik doğrulama değildir. Bu incelemeden “başka major hata asla yoktur” sonucu çıkarılmaz.

## Tekrarını azaltan çalışma kuralı

Bir modülün happy-path'inin geçmesi, yaşam döngüsü sınırlarını kanıtlamaz. İlgili teslimde **izin iptali → yeni context; archive → reopen; queue → worker; event → replay; backup → restore** geçişlerini de negatif örnekle kontrol et. Snapshot yalnız domain revision değil, yetki ve yaşam döngüsü için de tutarlı olmalı. Geçmiş başarılı raporu yeniden yazmak yerine yeni bulguyu mevcut task sahibine ve yeni kanıta bağla; her mesajda tüm repo taraması yapma.

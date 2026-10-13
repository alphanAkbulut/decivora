# T05g — Kalıcı proje ve binding kaydı

**Uygulandı; T05 ana görevi IN_PROGRESS.** [Storage kodu](../../packages/storage/project_store.py) · [11 test](../../tests/runtime/test_project_store.py) · [Çalışan demo](../../apps/hub/project_store_demo.py) · [Sonuç/hash kaydı](project-store-results.json).

```sh
python3.12 -B -m apps.hub project-store-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Demo ayrı temporary SQLite dosyasında gerçekten dört command commit eder, bağlantıyı kapatır/açar, iki projeyi ve iki binding revision'ını tekrar okur. Aynı command_id/actor/içerik retry'si yeni snapshot oluşturmaz. Demo bittikten sonra yalnız kendi temporary dosyaları temizlenir; kullanıcı DB'sine veya transcript'ine erişmez. Python API caller'ın seçtiği regular private DB dosyasını açar; kendi state'i kalıcıdır. Bir CLI demo sonucu production persistence/recovery SLA'sı değildir.

| Kontrol | Doğrulanan davranış |
|---|---|
| Restart | Aynı ad/farklı kimlik ve binding history korunur; eski revision eski projeye çözülür |
| Atomik yazma | BEGIN IMMEDIATE → güncel snapshot yükle → scope/base kontrolü → command sonucu + yeni snapshot → COMMIT |
| Retry | Aynı workspace DB, command_id, principal ve digest aynı sonucu döndürür; farklı içerik conflict |
| Güncel erişim | Cache hit dahil her command scope kontrol eder; binding retry eski projelerin izinlerini de denetler |
| Yarış | İki bağlantıda eski base_revision yazması stale olur; önceki başarılı değişiklik kaybolmaz |
| Hata | Insert abort fixture rollback olur; eski proje revision'ı kalır, aynı kimlikle retry başarılı olabilir |
| Geçmiş | Snapshot UPDATE/DELETE SQL trigger ile reddedilir; binding tarihi yeni snapshot'ta korunur |
| Yanlış DB | Bilinmeyen format/workspace ve unrelated DB üzerine migration/DDL uygulanmaz; byte eşitliği test edildi |
| Dosya | Yeni DB0600; önceden mevcut symlink/directory reddi. Raw kaynak/credential depolanmaz |
| Bütünlük | Canonical state/hash ve yapısal kontrol; fiziksel state değiştirilince yeniden açılış ret |

11 yeni test; toplam runtime34. T04/T05f geçmiş proof'ları yeniden yazılmadı; değişen runtime dosyaları bu yeni rapora bağlıdır. Yeni model, ücretli API, gerçek kaynak veya connector çağrısı yok. Source receipt, domain decision/event log, approval ve task completion bu tabloda tutulmaz; T06/T07 kapsamı ayrı kalır.

**Sınırlar:** Bu ilk store her command için tam proje/binding snapshot'ı tutar; küçük local çekirdek içindir, kapasite/performans üstünlüğü iddiası yok. 1MiB state admission sınırında yeni yazma reddedilir; önceki kayıt silinmez. DB toplam disk kotası, transaction limiter, normalleştirilmiş storage/migration, encryption, retention, backup/restore ve power-loss/kill-process testleri tamamlanmadı. SQLite FULL sync ve rollback testi power-loss doğrulaması yerine geçmez. Trigger/hash fiziksel DB adminine karşı değişmezlik garantisi değildir; hash'ler kriptografik imza veya harici audit ledger değil. Hostile filesystem yarışları desteklenen güvenlik sınırı değildir. Unknown DB read girişimi format kontrolü dışında yetki sağlamaz.

**Sıradaki T05 kapsamı:** Güvenilir principal/grant ve güncel authz revision kaynağını persist edilen membership ile ilişkilendirmek; eski scope/revocation kontrolü. Ardından ingress binding revision'ını alımda pinlemeli ve karantinayı durably kaydetmeli (T06). Bugünkü AccessScope nesnesi trusted caller tarafından sağlanır; source payload veya metin onu üretemez. Production login/team permission sistemini bu fixture ile tamamlandı sayma. T05 ana görevi bu nedenle açık tutulur.

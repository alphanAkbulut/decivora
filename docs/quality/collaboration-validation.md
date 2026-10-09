# Ekip, erişim ve veri yaşam döngüsü doğrulaması

**Tamamı planlanan senaryodur; runtime test sonucu yok.** Mevcut [V01–V28 planını](verification.md) tamamlar. Fixture sentetik: Workspace A/B; private proje P1/P2; owner Ayşe, contributor Bora, reviewer Cem, viewer Deniz; agent A1/A2; private kaynak S1 ve ortak kayıt K1. Bunlar gerçek kullanıcı/veri değildir.

| ID | Tetik / kurulum | Gözlenebilir kabul kriteri | İlk kapı |
|---|---|---|---|
| MU01 | A oturumuyla B resource ID/cursor/blob isteği | İçerik/başlık/count dönmez; güvenli ret; query/command aynı sınırı uygular | P1 T05b |
| MU02 | Contributor agent'ı owner/approve alanı gönderir | Güvenilir principal değişmez; approval reddedilir; audit aktörü doğru | P1 T08b |
| MU03 | Parent grant iptal; queued child run dispatch edilir | Child token geçerli görünse bile çalışmaz; scope-wide authz revision kontrolü | P1 T08b; child desteği geldiğinde tekrar |
| MU04 | Model çağrısı sürerken üyelik/grant iptal edilir | Yeni egress yok; gelen sonuç canonical uygulanmaz; quarantine/audit; geçmiş dış gönderim gizlenmez | P1 T08b |
| MU05 | Viewer retrieval, graph, export veya citation üzerinden private S1 ister | S1 ve türev özeti modele/yanıta giremez; erişim daralınca cache stale; görünmeyen gerekçe yanlış obsolete sonucu üretmez | P1 T18b; shared UI'da tekrar |
| MU06 | İki agent aynı revision'ı değiştirir; eski worker geç yanıtlar | Tek canonical effect; stale/conflict ve fencing sonucu; claim izne dönüşmez | P1 T06b/T08b |
| MU07 | Aynı canonical human ID'ye bağlı iki hesap/token veya o insanın iki agent'ı korumalı proposal'ı onaylar | Aynı doğrulanmış insan/sorumlu zincir bağımsız review sayılmaz; başka reviewer gerekir | Ekip C04 |
| MU08 | Başarılı permission/approval transaction'ında audit yazımı bozulur | Canonical mutation commit olmaz; attempted/failed gerçek sonuca uygun | P1 T07b |
| MU09 | Debug'a secret/newline içeren sentetik payload; telemetry sink kesilir | Secret/raw gövde yok; log injection yok; bounded buffer/drop counter; audit gerektiren başarı kaybolmaz | P1 T07b |
| MU10 | Personal kaynak ortak projeye bilinçli redakte paylaşılır | Önizleme ve insan onayı; ayrı ACL'li kayıt; raw source okuyucu listesi genişlemez | P1 T18b / ekip C04 |
| MU11 | Context/cache/raw TTL dolar; eski source tekrar import edilir | Karar geçmişi korunur; raw unavailable; dedup yeniden effect üretmez; pending öneri accepted olmaz | P1 T06d/T23c |
| MU12 | Source purge edilir; eski backup restore edilir | Servis açılmadan tombstone uygulanır; index/cache/blob temiz; eski izinler otomatik canlanmaz | P1 T23c; ekip C05 |
| MU13 | SQLite snapshot → Postgres fixture migration | Tenant/FK/ID/sequence ve projection digest eşit; yetki oracle aynı; yeni yazı sonrası unsafe rollback reddi | Ekip C02 |
| MU14 | Pool bağlantısı A'dan B'ye geçer; worker yanlış tenant yazar | Context transaction-local; DB/application sınırları reddeder; nonowner RLS ve admin bypass kapsamı kayıtlı | Ekip C02 |
| MU15 | Disk dolu, WAL büyüyor, blob eksik, backup key yok | Dayanıklı receipt olmayan veri accepted görünmez; backpressure/uyarı; restore başarı iddiası verilmez | P1 T23d |
| MU16 | 100k/1m event, 1/5/20 client; ısıtılmış ve soğuk cache | p50/p95/hata/queue/disk raporu, ortam tanımı; sağlanmayan hedef açık; tekrar aynı fixture | P1 T23d/T24b |
| MU17 | Davet yanlış kişi/süresi dolmuş; son owner ayrılır | Davet reddi; son owner korunur; transfer kabulü atomik; offboard açık işler görünür | Ekip C03 |
| MU18 | Outbox dispatch öncesi connector scope daralır; dış cevap kaybolur | Yeni dispatch durur; belirsiz dış sonuç unknown; uzlaştırma/idempotency olmadan retry yok | T28b / ekip C05 |

Her çalıştırma kanıtı: senaryo ID, sürüm/commit, fixture seed/hash, ortam, beklenen/gerçek sonuç, redakte log/trace referansı, pass/fail/not_run, kalan risk. Başarısız kontrol için runtime davranışı düzeltilir; test listeden çıkarılmaz. P1'de henüz olmayan team UI/DB yolları `not_run: P4` kalır; mevcut agent ve proje izolasyonu kontrolleri bu gerekçeyle ertelenmez.

Benchmark ölçümü ile policy oracle ayrı raporlanır. Erişim testinin geçmesi karşılaştırılan rakipten daha güvenli olduğumuzu kanıtlamaz. Veri silme testinin geçmesi tüm üçüncü taraf kopyaların silindiği veya hukuki uyum anlamına gelmez.

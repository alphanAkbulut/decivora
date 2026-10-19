# Kaynak kapasitesi, indeksler ve sayfalı inceleme

**19 Ekim2026 — çalışan T09/T17/T19/T22/T23 alt teslimi.** Kullanıcı API beklemeden kod geliştirmeye devam edilmesini istedi.32kaynak preview sınırı bu teslimde1000kaynak/proje sınırına taşındı; yalnız sabit değiştirilmedi. Yeni audit indeksleri, bounded exact-ID/origin/context sorguları, source snapshot sayfalaması, queue metadata projeksiyonu ve gerçek HTTP/UI sayfa geçişleri bağlandı. Varsayılan model hâlâ kapalı; gerçek kaynak okuması veya model paylaşımı izni genişlemedi.

## Çalışan davranış

| Alan | Mevcut uygulama |
|---|---|
| Kalıcı kapasite | Proje başına1000source; her source en fazla12000UTF-8byte. İmplementasyon sınırıdır, ölçülmüş production kapasitesi veya retention politikası değildir |
| Source listesi | Varsayılan25source, iç API limit1–50; HTTP/UI25. Sadece seçilen sayfanın source body ve ilişkili analysis kayıtları hazırlanır |
| Cursor | Seçili workspace/project + son source seq + snapshot ceiling. Yeni source mevcut sayfaları kaydırmaz; yenileme/ilk sayfa yeni snapshot alır |
| Cursor yetkisi | Base64JSON read position'dır, signed grant değildir. Güncel proje ACL kontrolü önce; iki seq anchor aynı projenin immutable source satırı olmalı. Foreign/malformed/oversize cursor ret |
| Exact inceleme | İlk sayfanın dışındaki source için accept kendi exact source görünümünü yükler.100kayıt comparison sınırı hâlâ açık; sayfalama onu aşma izni vermez |
| Native capture |32item/RPC pass bütçesi korunur. İncremental writer yalnız son32fingerprint'i tutar; eski item değişimi kalıcı indexed origin lookup ile yakalanır.50public item fixture'ı geçti |
| Queue | Bütün kayıtlı source durumlarının toplamı; ekranda en fazla25içeriksiz metadata. İşleyici ilk sayfada yetkisiz kaynaklar olsa da ilerideki izinli kaynağı bulur; unknown/finished çağrı tekrarlanmaz |
| Bağlam | Aynı capture/thread için en fazla7önceki source SQL'de seçilir;6mesaj/6000byte context sınırı korunur. Diğer raw source geçmişi Python'a yüklenmez |

## SQLite ve mevcut veriyi koruma

Yeni `source_pages.py` ilk **yetkili source write transaction'ında** additive indeksler kurar: workspace/project/action/seq, source ID, yerel profile/thread/turn/item origin ve source-key analysis/outbox/grant sorguları. İndeksler mevcut append-only audit üzerinde hızlandırıcıdır; ayrı source payload kopyası veya yeni tablo yoktur. SQL FORMAT/schema_version değişmedi. Source ID, eski provenance, event/audit ve gerçek altı TEST kaynağı yeniden yazılmaz. Legacy DB yalnız okunurken indeks kurulmaz; ilk izinli source write ile kurulur. CREATE INDEX source/outbox/checkpoint ile aynı transaction'dadır; hata halinde yeni kayıt/ilerleme kabul edilmez.

Bu, genel migration/purge/retention sistemi değildir. Normal backup/restore indeksi ve payloadları beraber taşır; integrity ve kaynak kimlikleri test edildi. Uzun vadede payload retention ve büyüyen audit için ayrıştırılmış storage gerekiyorsa ayrı kabul/operasyon işi kalır. Yeni schema/session/key global config veya dış DB servisi kurulmadı.

## HTTP ve arayüz

Yeni `GET /api/conversations` yalnız mevcut local session, Host/Origin ve seçili proje read scope ile çalışır. Query: `project_id` ve **ya** `cursor` **ya** `source_id`. Duplicate query, ek alan, foreign cursor ve mixed cursor/source ret. HTTP body/config/SQL kabul etmez; okuma model/worker çalıştırmaz. Sonuç `imports`, `knowledge_revision`, `automatic_capture=false`, `total`, `next_cursor`, `has_more` taşır. `total` güncel bütün source sayısıdır; pinned cursor'ın tarihi snapshot'ına yeni source kendiliğinden eklenmez.

Conversations ilk/önceki/sonraki sayfa düğmeleri sunar. Gönderilmemiş metin taslağı sayfa geçişinde korunur. Proje değişince eski cursor/focus sıfırlanır.25üzeri source varken yeni import edilen source exact görünümde gösterilir; kullanıcı kaydın kaybolduğunu sanmaz. İlk sayfa düğmesi listeye döndürür. Header imported-count toplamı gösterir; proposal sayısı sayfa bazlıysa açıkça **Proposals on this page** yazar. EN/TR yeni mesajlar eklendi; diğer taslak kataloglarda bu yeni metinler İngilizce kalır. RTL ve genel dil davranışı değişmedi.

## Doğrulama

-1000source kapısı,40sayfada kayıpsız/duplicatesiz traversal; cap'te mevcut dedup kabul,1001.yeni source ret; SQL query plan exact-ID indeksini kullanıyor.
- Snapshot sırasında yeni source; foreign/malformed/fabricated-anchor cursor; read-only DB; yalnız seçili source body hazırlığı; backup/restore source ID+index korunumu.
- İlk25kaynağın dışında grantli source→worker→proposal→ayrı human accept→Task. Genel source grant/activation wizard'ı henüz yok.
-50public native item'dan sonra fingerprint map32kalır; yeniden bağlantıda ilk eski mesajın değiştirilmesi yine reddedilir.32binding sayısı ve page/RPC byte tavanları değişmedi.
- Gerçek HTTP session/query sınırları ve35source browser fixture'ında25/10sayfa, taslak koruma, proje reset, TR/EN ve mobil taşmama. Sonradan36.source importu exact görünümde kalır.

Önceki capacity-failure regresyonu test içinde32limiti enjekte ederek aynı atomik hata yolunu korur; gerçek1000sınırı ayrı testte çalıştırılır. İlk HTTP fixture hatasında testin server/app erişimi düzeltildi; assertion veya kapsam gevşetilmedi.

## Ölçüm ve açık kapılar

[1000source ölçümü](source-pages-load-results.json), [yeniden üretim script'i](../../scripts/benchmark_source_pages.py): geçici SQLite Workspace, yaklaşık4KiB/source,20okuma örneği, p50/p95, DB boyutu ve integrity. Bu bir concurrency/HTTP/browser/provider SLA veya eski sürüme göre hız kazancı değildir. Gerçek token/model çağrısı0, gerçek kaynak0. Son kaynak dosyalarının SHA256'ları raporda tutulur.

Açık kalanlar: source/model onboarding ve sürekli izinli worker; live/backfill adaleti; GUI capture pause/revoke/gap; edit revision/account değişim semantiği; retention/purge ve kapasite yönetimi; genel semantic/model/native MVP kabulü. Bu teslim yalnız kendi capacity/read/review bağlantısını kapatır; ana işleri veya14MVP kriterini otomatik kapatmaz.

Son doğrulama:532runtime,49tracker/araç kontrolü ve13browser senaryosu geçti; yeni source odaklama davranışı son browser koşusunda ayrıca doğrulandı.50Mermaid render edildi. SQLite JSON fonksiyonları yeni source sorguları/indeksleri için gereklidir; yerel bundled runtime üzerinde çalıştırıldı. Yeni üçüncü taraf Python/JS paketi eklenmedi. Gerçek source/model çağrısı0.

TEST deployment readback:53611yeni kodla özel SQLite yedeği sonrası yeniden başlatıldı. Mevcut6source/0task,model kapalı,kapasite1000ve yeni GETsayfa endpoint'i doğrulandı. Canonical DB önce/sonra mantıksal hash'i aynı kaldı; legacy read indeks kurmadı. Normal53610süreci/verisi değiştirilmedi. Yerel oturum anahtarını araç çıktısına koyan ilk readback adımı otomatik onay denetimince reddedildi; yalnız aggregate/bütünlük çıktısı veren güvenli kontrol geçti. Tarayıcı normal local başlangıç akışıyla, credential yazdırılmadan açılmak üzere başlatıldı; bu local kontrol gerçek host/model izni değildir.

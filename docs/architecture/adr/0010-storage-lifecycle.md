# ADR-0010 — Katmanlı kalıcı veri ve sınırlı çalışma hafızası

**Durum: önerilen; uygulanmadı.** 2026-10-09. ADR-0001/0002/0007'yi tamamlar; SQLite başlangıç önerisini geçersiz kılmaz.

## Problem ve öneri

Tüm transcript'i süresiz tutmak maliyet/gizlilik yükü doğurur. Model context'ini kalıcı hafıza sanmak bilgi kaybettirir. DB WAL'ı audit sanmak yetki izini kaybettirir. Tek bir TTL bütün veri sınıflarına uygulanamaz.

Canonical karar/olay ve gerekli provenance dayanıklı kalır; kaynak payload, evidence blob, operational log ve backup ayrı retention policy taşır. Context/cache/index türevdir; yeniden oluşturulabilir ve ACL'ye tabidir. Dedup kimlikleri ham payload TTL'inden bağımsız tutulur. High-impact command audit'i domain transaction'ına eşlik eder. Privacy purge kaynak+türev+restore yollarını kapsar; normal agent geçmişi değiştiremez.

P1: yerel tek servis, SQLite WAL ve ayrı korumalı blob deposu. Ekip: merkezi API/PostgreSQL adayı, nonowner DB rolü ve tenant izolasyonu; object storage/worker ölçeği ölçümle eklenir. DB migration tenant/ACL/sequence/projection eşitliği ve tutarlı blob manifest ile yapılır. Aktif DB dosyasını cloud klasörüyle sync etmek ortak çalışma protokolü değildir.

## Alternatifler

- Her şeyi ephemeral tutmak: kalıcı proje hafızası hedefini karşılamaz.
- Her şeyi sonsuz saklamak: gizlilik, maliyet ve eski bilginin yeniden kullanılması sorunlarını büyütür.
- İlk günden PostgreSQL + vector DB + dış queue: geleceğe esneklik sağlar, fakat kişisel pilot kurulumunu ağırlaştırır; kanıt kapısına ertelenir.
- Her şeyi Markdown/Git üzerinde sürümlemek: okunabilir export için yararlı; atomik concurrency, scoped erişim ve değişen kaynak saklama politikasını ana store olarak zorlaştırır.

## Sonuçlar / doğrulama

Retention durumu UI'da görünmeli; eksik kaynak sessizce verified sayılmaz. Backup/PITR veri kaybını azaltabilir ama key/ACL/purge manifest olmadan güvenilir restore değildir. Kapasite ve RPO/RTO yalnız [ölçülecek hedeflerdir](../storage-memory-capacity.md), garanti değil.

T06d/T07b/T23c/T23d; MU08/MU09/MU11–MU16 ve mevcut V17/V19/V26/V27 acceptance kapılarıdır. Sayısal retention önerileri OPEN-08; exact DB/crypto sürümü OPEN-02; ekip mimarisi OPEN-14 kapsamında kalır. [Log sözleşmesi](../logging-audit.md) ve [yaşam döngüsü](../storage-memory-capacity.md) normative öneri ayrıntılarıdır.

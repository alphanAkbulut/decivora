# Açık kararlar ve varsayımlar

| ID | Soru | Önerilen yön | Ne zaman / kanıt |
|---|---|---|---|
| OPEN-01 | Build mi extend mi? | Özgün domain/impact; lisanslı adapter reuse | P0 karşılaştırmalı deney sonrası |
| OPEN-02 | Kesin runtime/DB/UI paketleri? | TypeScript, yerel servis, SQLite, React aday | P1a başlamadan version/license spike |
| OPEN-03 | İlk coding adapter sırası? | İki yüzeyi test et; daha erişilebilir olanla P1a | P0 gerçek capability sonuçları |
| OPEN-04 | Chat otomasyon seviyesi? | P1b provenance koruyan açık aktarım | Hesap/host izin testi; P2 otomasyon |
| OPEN-05 | Lisans? | AGPLv3 ilk aday; Apache-2.0 alternatif | Public release öncesi owner |
| OPEN-06 | Nihai marka? | Decivora geçici | Marka/alan adı/paket taraması ve owner |
| OPEN-07 | Hangi değişiklikler auto-apply? | Capture/metadata/izinli verification; scope insan | Policy UX pilotu |
| OPEN-08 | Retention/erase/şifreleme? | Minimize payload, ayrı yönetici akışı | Gerçek veri pilotundan önce |
| OPEN-09 | Ölçüm eşikleri? | Ölçüm belgesindeki pilot hedefleri | Golden corpus baseline sonrası |
| OPEN-10 | Ücretli model ve bütçe? | Provider bağımsız usage, explicit limit | API-backed deneme öncesi |
| OPEN-11 | Public/core/commercial sınırı? | Yerel çekirdek açık aday, servisler ayrı aday | Talep ve lisans incelemesi sonrası |
| OPEN-12 | Queue/lease/timeout/traversal ve recovery limitleri? | Sınırlı versioned config; ayrı cursors; snapshot backup; RPO/RTO ölçülsün | T04/T06 fixture ve T23 gerçek veri öncesi; ADR-0007 |
| OPEN-13 | Approval graph snapshot ve verifier yetkisi? | P1 project knowledge revision; insan/agent/runner capability ayrı | T08/T12/T14; ADR-0008; T24 false-stale ölçümü |

## Cevaplanan ihtiyaç ve bekleyen sorular

2026-10-09 owner yanıtı: ilk pilot kendi bireysel kullanımıyla, ardından benzer kullanıcılarla yapılacak. Bu artık varsayım değil, pilot kapsamı kararıdır; tam ürünün ekip vizyonunu kaldırmaz. Günlük coding/chat yüzeyleri ve ilk hedef OS ile harici model/veri/bütçe sınırı soruldu, yanıt bekleniyor. [Karar hazırlığı ve soru kaydı](../delivery/decision-brief.md).

Varsayımlar: local-first kabul edilebilir; ilk dil Türkçe dokümantasyon ve İngilizce teknik ID'ler; otomatik capture için bir defalık izin/binding kurulabilir. Bunlar kanıt veya alınmış ticari karar değildir. Teknik ayrıntılar önce deneyle hazırlanır; bütün açık maddeler için hemen kullanıcıya soyut seçim sorulmaz.

Bu açık sorular dokümantasyonun GitHub'a kaydedilmesini engellemez. Etkili oldukları uygulama görevinden önce karara bağlanırlar; AGENTS.md içine güncel iş listesi olarak gömülmezler.

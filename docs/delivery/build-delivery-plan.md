# Altı kod teslim paketi

2026-10-13 — **uygulama sırası**, yeni görev listesi veya altı ayrı program değildir. Mevcut Python 3.12/SQLite çekirdeği ve yerel web arayüzü büyütülecek. Tam vizyon korunur; paketler MVP teslimini yönetir. [Backlog](backlog.md) görev otoritesidir; paket adı yeni task sayılmaz.

Bugün 7 ana iş Done, 8 In Progress, 15 To Do. To Do'nun **9'u MVP (T14–T18, T21–T24), 6'sı sonraki fazlar (T25–T30)**. In Progress işlerin de MVP kabulünde kalanları var. Bu sayılar tamamlanma yüzdesi değildir. Çift tıklamayla başlayan manuel uygulama zaten mevcut; otomatik hafıza MVP'si tamamlanmış değil.

| Paket | Kod işi / mevcut görevler | Mevcut kodu güncelleme ve yeni modül | Kullanıcının göreceği teslim | Paket kabulü |
|---|---|---|---|---|
| 1. Karar–kanıt döngüsü | T13e, T14, T15 | storage/review/acceptance/local UI güncellenir; question ve verifier modülleri eklenir | Kalıcı sorular, geç cevap, ayrı uygulama onayı, kriter bazında kanıt ve gerçek Done | Stale/çelişkili cevap yanlış karar yaratmaz; not_run/unknown/failed Done olmaz; restart/retry/restore uçtan uca geçer |
| 2. Konuşmadan proje bilgisi | T09, T10; T22 manual import dilimi; T01–T03 kalite kapıları | capture/extraction ve reconciliation güncellenir; bounded provider/import bağlantısı eklenir | İzinli metni içeri aktar → kaynaklı görev/karar önerilerini incele | Gerçek semantik çıkarım ve bağımsız beklenti ölçülür; alıntı/plan başarı iddiası yapılmaz; yanlış otomatik karar yok |
| 3. Kod agent bağlantıları | T16, T17 | Mevcut ingress/jobs kullanılır; Claude Code ve Codex adapter modülleri eklenir | Desteklenen oturumdan otomatik veri alımı, bağlantı izinleri ve eksik yakalama uyarısı | Gerçek host/version fixture, revoke/retry/gap; olmayan hook veya desktop yeteneği varmış gibi sunulmaz |
| 4. MCP proje hafızası | T18 | Yeni dar MCP transport/tool katmanı; mevcut scope/query/proposal kullanılır | Agent gerekli proje bağlamını kısa ve sayfalı ister; insan onayı atlanmaz | Proje izolasyonu, output limit/cursor, revoke, duplicate; write doğrudan canonical apply değildir |
| 5. Günlük kullanım arayüzü | T19, T20, T21; T22 kalan lineage | Mevcut local UI genişler; graph/timeline/usage bileşenleri eklenir | Proje seçimi, Review Inbox, karar–görev grafiği, geçmiş/iptaller, kullanım ve yönlendirme | Gerçek tıklama akışları, hata/boş/loading; iptal geçmişi korunur; usage unknown dürüst gösterilir |
| 6. Kurulabilir MVP ve pilot | T23, T24 | Mevcut backup/restore ve launcher güncellenir; export/privacy/kurulum kontrolü eklenir | Lokal açılır, veri korunur, export/restore yapılır; ilk bireysel pilot | 14 MVP kriteri, iki adapter ve zorunlu gerçek çıkarım/holdout kapıları; eksik varsa sınırlı preview etiketi |

Arayüzü paket 5'e kadar bekletmeyiz: her paketin davranışı mevcut programa eklenir. Paket 5 kalan bütünleşik UX kabulünü tamamlar. Paket 2'de T22'nin izinli manuel input dilimini erken kullanmak, T22'nin bütün lineage/privacy kabulünü kapatmaz. Backlog bağımlılıkları tam görev kapanışına aittir; bağımsız hazırlık/erken UI dilimi bütün downstream kapılarını atlamaz.

## Şimdi yapılacak kod sırası

1. T13e: kalıcı soru/seçenek snapshot'ı ve exact soru/sürüm cevap kaydı; uygulama Inbox'ına bağla.
2. Cevap kaydını kaynaklı karar önerisi ve ayrı review/apply ile birleştir; iptal/superseded/orphan durumlarını tamamla. Ancak sonra T13e/T13 kapanış kontrolü.
3. T14: gerçek kanıtı görev/AC/hedef revision'ına bağla; criterion sonuçları ve current completion predicate. Agent iddiasını evidence yerine kullanma; transcript'ten komut çalıştırma.
4. T15: aynı uygulamada cevap → karar → etki → ayrı onay → hedef kanıtı → kriter → düzeltme ve restore zinciri.
5. Paket 2'ye geç; gerçek model çağrısı hazır olduğunda sağlayıcı/veri/bütçe yetkisini somut run kapsamıyla netleştir.

## İlerleme ve dış bağımlılıklar

Her teslimde kod, ilgili davranış testleri, güncel status/backlog, gerekiyorsa gerçek render edilmiş diagram/şema ve çalıştırılabilir yerel paket güncellenir. Ana görevi sadece kendi kabulü geçince Done yaparız; yeni paket isimleriyle To Do şişmez. Test sayısı veya belge teslimi otomatik ürün kabulü değildir.

Paket 1'in yerel deterministik geliştirmesi API bakiyesine bağlı değil. Paket 2'nin gerçek semantik doğrulaması için yeni model çalıştırma yetkisi gerekecek; bugün ücretli API yetkisi/bakiye varsayılmaz. Paket 3 gerçek host erişimi/izinine, paket 4 ilgili istemcinin MCP desteğine bağlı. Bu dış bağımlılıklar güvenli yerel kod hazırlığını durdurmaz; fixture testi gerçek entegrasyon kabulü sayılmaz.

T25–T30 ekip/cloud, ileri bağlam, gelişmiş adapter/dil ve sonraki büyüme işleridir; ilk kullanılabilir MVP'ye hepsini yüklemeyiz. Kabul kapıları ve tam vizyon silinmez. Takvim, doğruluk ve maliyet garantisi verilmez; her paketin sonucu çalışan davranış ve kalan engelle raporlanır.

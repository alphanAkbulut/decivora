# Altı kod teslim paketi

2026-10-13 — **uygulama sırası**, yeni görev listesi veya altı ayrı program değildir. Mevcut Python 3.12/SQLite çekirdeği ve yerel web arayüzü büyütülecek. Tam vizyon korunur; paketler MVP teslimini yönetir. [Backlog](backlog.md) görev otoritesidir; paket adı yeni task sayılmaz.

Bugün 7 ana iş Done, 14 In Progress, 9 To Do. To Do'nun **3'ü MVP (T16,T17,T24), 6'sı sonraki fazlar (T25–T30)**. T14 yerel insan incelemesiyle başladı; otomatik doğrulama ve tam kabulü açık. In Progress işlerin de MVP kabulünde kalanları var. Bu sayılar tamamlanma yüzdesi değildir. Çift tıklamayla başlayan manuel uygulama zaten mevcut; otomatik hafıza MVP'si tamamlanmış değil.

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

2026-10-13: kullanıcı asıl değer olan otomatik konuşma çıkarımını öne aldı; API hazırlığını yarına bıraktı ve önce UX istedi. Paket numaraları korunur, paket2'nin konuşma/çıkarım dilimi paket1 tam kapanmadan öne alındı. Tam vizyon/14AC/gerçek çıkarım kalite kapısı kaldırılmadı.

1. Konuşma aktarımı ve kaynaklı aday incelemesini uygulamaya bağla; manuel görev/soru girişi yardımcı alan olur. [Kod teslimi](../quality/conversation-review-runtime.md).
2. Konuşma/öneri odaklı masaüstü/mobil UX; model bekleme, hata, kaynak ve onay durumlarını dürüst göster.
3. API erişimi hazır olunca model, exact data/target ve somut çağrı/para/token tavanı onayını netleştir; bounded gerçek provider transport ve zorunlu semantic kalite ölçümünü yap. Payload/parser fixture başarıları gerçek model doğruluğu değildir.
4. T13e agent/source acceptance eşlemesini, T14 revision-bound Evidence/Done ve T15 bütün zinciri tamamla. Bugüne kadar yapılan core/history/approval kodu bu akışta kullanılır.
5. T16/T17 capture ve T18 MCP kapılarına ilerle; tek paste alanı sürekli otomatik capture diye sunulmaz.

## İlerleme ve dış bağımlılıklar

Her teslimde kod, ilgili davranış testleri, güncel status/backlog, gerekiyorsa gerçek render edilmiş diagram/şema ve çalıştırılabilir yerel paket güncellenir. Ana görevi sadece kendi kabulü geçince Done yaparız; yeni paket isimleriyle To Do şişmez. Test sayısı veya belge teslimi otomatik ürün kabulü değildir.

Paket 1'in yerel deterministik geliştirmesi API bakiyesine bağlı değil. Paket 2'nin gerçek semantik doğrulaması için yeni model çalıştırma yetkisi gerekecek; bugün ücretli API yetkisi/bakiye varsayılmaz. Paket 3 gerçek host erişimi/izinine, paket 4 ilgili istemcinin MCP desteğine bağlı. Bu dış bağımlılıklar güvenli yerel kod hazırlığını durdurmaz; fixture testi gerçek entegrasyon kabulü sayılmaz.

T25–T30 ekip/cloud, ileri bağlam, gelişmiş adapter/dil ve sonraki büyüme işleridir; ilk kullanılabilir MVP'ye hepsini yüklemeyiz. Kabul kapıları ve tam vizyon silinmez. Takvim, doğruluk ve maliyet garantisi verilmez; her paketin sonucu çalışan davranış ve kalan engelle raporlanır.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

14Ekim2026 kullanıcı workflow/UX önceliğini onayladı: [yerel teslim](../quality/workflow-ui-runtime.md) mevcut T13/T14/T19/T20 kapsamında. Otomatik capture/real semantic model ve hedef verifier kapıları ayrı; altı paket planı silinmedi.

## 14 October 2026 — private backup UI

[Current bounded backup download](../quality/private-backup-runtime.md): Sources view, explicit private-data acknowledgment, ZIP + manifest and temporary offline restore validation. Unencrypted source-preserving backup; not a shareable redacted export. Active restore/purge/migration/encryption remain open; no model call or new SQL schema.

## Current local delivery — 14 October 2026

[API-independent implementation and follow-up gates](api-independent-development.md): bounded stdioMCP/create-only human review, optional explicit-root file SHA verification, recorded graph/audit timeline, routing/null usage and session-only health. Historical implementation limits above refer to their original deliveries; current limits and M01–M14 checks are in the linked report. No native capture, full brief/delta, sandbox test/deploy verifier, exact host token savings or global language quality is claimed.

# Altı kod teslim paketi

**20 Ekim yürütme güncellemesi:** Aşağıdaki paket yapısı korunur; güncel sıra, sayılar ve kullanıcı onaylı sprint/mikro plan [Sprint planında](sprint-plan.md). Eski tarihli sayılar tarihsel teslim anlarıdır.


2026-10-13 — **uygulama sırası**, yeni görev listesi veya altı ayrı program değildir. Mevcut Python 3.12/SQLite çekirdeği ve yerel web arayüzü büyütülecek. Tam vizyon korunur; paketler MVP teslimini yönetir. [Backlog](backlog.md) görev otoritesidir; paket adı yeni task sayılmaz.

19Ekim teyidi:7ana iş Done,15InProgress,8ToDo. ToDo'nun **2'si MVP (T16,T24),6'sı sonraki fazlar (T25–T30)**; T17 artık InProgress. [129alt kayıt teyidi](../quality/task-status-audit.md). T14 yerel insan incelemesiyle başladı; otomatik doğrulama ve tam kabulü açık. In Progress işlerin de MVP kabulünde kalanları var. Bu sayılar tamamlanma yüzdesi değildir. Çift tıklamayla başlayan manuel uygulama zaten mevcut; otomatik hafıza MVP'si tamamlanmış değil.

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

**18 Ekim 2026 — güncel devam planı.** 13 Ekim'deki aktarım/inceleme hazırlığı artık sıfırdan yapılacak iş değildir. Mevcut yerel uygulama, manuel konuşma import'u, kaynaklı aday incelemesi, kalıcı soru/geç cevap, ayrı insan onayı, kriter bazlı verification, Board/List/Graph/Timeline, sınırlı stdio MCP ve özel yedek dilimleri kullanılacak. Bu tablo mevcut görevlerin teslim sırasıdır; yeni görev otoritesi veya kabul edilmiş yeni mimari değildir.

**Başlangıç kanıtı:** [18 Ekim inceleme ve çalışan yerel servis raporu](../quality/review-remediation-2026-10-18.md). 330 runtime testi, sekiz yerel browser akışı ve 44 Mermaid render kaydı mevcut; bunlar gerçek semantik kalite veya tamamlanmış MVP kanıtı değildir. Kaynak bağlantılı model izni ve token rezervasyonu kodlandı; default launcher hâlâ modelsizdir.

| Sıra / teslim | Mevcut sahipler | Yapılacak kalan kod / kullanıcı çıktısı | Bağımlılık ve kabul |
|---|---|---|---|
| 1. Güvenli model bağlantısını kullanıma hazırla | T03, T09, T21 | Kaynak/model/run izninin anlaşılır yapılandırılması; doğrulanmış input/context/output hesabı; fiyat/para/dönem preflight'ı; fazla veya belirsiz kullanım için güvenilir insan uzlaştırması | Hazırlık API bakiyesi istemez. Sentetik transport ile timeout, eksik usage, tekrar, iptal, limit aşımı ve restart sınanır. Actual kayıt silinmez; otomatik limit artırılmaz. Sayısal tavanlar onaylanmış varsayılmaz |
| 2. Karar → görev etkisi → kanıt döngüsünü bütünleştir | T10, T13, T14, T15, T19, T20, T22 | Mevcut kernel/UI üzerinden geç cevap, AND/OR gerekçesi, etki önizleme, kabul/ret/erteleme, ayrı uygulama onayı ve kriter bazlı kapanışı aynı kullanıcı akışında tamamla | API'siz yapılabilir. Eski onay revision değişince uygulanamaz; iptal edilmiş ilişki/geçmiş silinmez; hedef içerik veya önkoşul değişince eski başarı güncel Done sayılmaz. Sahte çıkarım gerçek model sonucu diye etiketlenmez |
| 3. Gerçek otomatik çıkarımı ölç ve düzelt | T01–T03, T09, T10, T24 | İzinli metinden kaynaklı karar/görev/soru adayları; aynı programda inceleme. Bağımsız beklentilerle yanlış karar, false done/obsolete, geç/belirsiz cevap ve kapsam kaçırma ölçümü | 1'in gerçek çağrı güvenlik kapıları ve somut veri/model/bütçe onayı gerekir. Şema uygunluğu, kaynak doğruluğu, anlam doğruluğu, düzeltme süresi ve kullanım ayrı raporlanır. Başarısız sonuç gizlenmez; fixture başarısıyla kapatılmaz |
| 4. Gerçek coding agent ve MCP bağlantılarını doğrula | T16, T17, T18 | Önceden seçilmiş kaynak/host üzerinden gerçek capture; yeniden bağlanma, eksik veri, revoke; kısa/sayfalı MCP bağlamı ve insan incelemesine düşen öneriler | Hazırlık 1–2 ile ilerleyebilir; gerçek host/version ve erişim kapsamı ayrıca belirlenir. Backlog kapanış sırası T15→T16→T17→T18 korunur. Kullanıcının Codex'i görme isteği hazırlık/smoke önceliğidir; Claude Code kabulünü iptal etmez. MCP tek başına otomatik transcript capture değildir |
| 5. Kurulabilir pilot ve MVP kabulü | T15, T19–T24 | Temiz kurulum, seçilmiş gerçek hedef kanıtı, restore/recovery, mahremiyet/export ve yoğun geçmişte sayfalama; günlük kullanım testi | Teknik hazırlık erkenden yapılır; tam MVP kapanışı 3–4 ve 14 kabul kriterinin kanıtını bekler. Tek adapter geçen teslim sınırlı pilot diye adlandırılır; iki adapter şartı kaldırılmaz |

### 18 Ekim uygulama ilerlemesi

Kullanıcı diyalogdan gerçek görev ve durum üretimini öne aldı. [Diyalog inceleme kod dilimi](../quality/dialogue-status-runtime.md) ile 2. sıranın kaynaklı status önerisi ve ortak workflow bağlantısı uygulandı; 1. sıradaki tam maliyet/aktivasyon ekranı ve 3. sıradaki gerçek anlam doğruluğu bekliyor. Mevcut LLM yanıtı içeri aktarımı API beklemeden bu yolu kullanmayı sağlar; sürekli otomatik yakalama değildir. Tam etki analizi, gerçek hedef ve ana task kapanışları ayrıca kanıt ister.

### İlk sonraki kod teslimi

**Güncel kod sırası:** native source kapasitesi/index/paging → kaynak/model onboarding ve izinli queue aktivasyonu → gerçek semantik kalite/reconciliation → bütünleşik impact/review/verification/continuation kabulü. Source-bound answer/relation/replacement, AND/OR gerekçe yazarı, scope/lifecycle apply, gerçek kısmi Codex readback, kalıcı checkpoint ve bounded source queue worker kodlandı. Bunları yeniden yapılacak özellik diye sayma. [Güncel durum](current-state.md) ve [teyit](../quality/task-status-audit.md) çalışan alt küme ile kalan kabulü ayırır. Claude adapter, kaynak izin UI, full backfill ve gerçek günlük kullanım kabulü açık.

### Neler birlikte ilerleyebilir?

1 ve 2'nin bağımsız dosya/akışları; adapter fixture hazırlığı; temiz kurulum/restore ve mevcut performans darboğazlarının hedefli düzeltmeleri birlikte hazırlanabilir. Bu, alt agent çalıştırma talimatı değildir. Gerçek model çağrısı 1'i; canonical uygulama güncel insan onayını; tam MVP kabulü gerçek çıkarım ve iki adapter kanıtını bekler. Ana görevin kapanışı ile bağımsız alt dilimin başlaması aynı şey değildir.

### Kullanıcıdan ne zaman ne gerekecek?

Şimdi planlama veya API'siz geliştirme için bakiye yüklemek gerekmiyor. Gerçek çağrıdan önce tek somut onay kaydıyla **sağlayıcı/model, gönderilecek exact metin/kapsam, çağrı ve retry sayısı, input/output/context/run token sınırları, parasal tavan ve geçerlilik süresi** netleşmeli; API anahtarı sohbete yazılmamalı. Bunlar genel “devam et” izninden türetilmez. Gerçek adapter/hedef için seçili host/session/repo/root ve okuma/yazma yetkileri ayrıca sınırlandırılır. Fiyat veya politika tercihi gerektiren gri alan varsa çalışan taslak üzerinden odaklı soru sorulur.

### Her teslimin görünür kapanışı

Kodun ilgili davranışı test edilir; çalışan programa bağlanan dilim gösterilir. [Backlog](backlog.md), [kapanış kaydı](task-closure.json) ve türetilmiş [ilerleme görünümü](progress.md) kanıta göre güncellenir. İlgili ana kabul geçmeden Done artırılmaz. Değişen sözleşmenin diyagram/şeması güncellenip render edilir; değişmeyen 44 diyagram her küçük teslimde tekrar düzenlenmez. Gerçek model ölçümü yetersizse yeni genel araştırma turu yerine belirli hata, düzeltme ve yeniden değerlendirme kararı yazılır.

P2/P3 ekip/cloud, ileri entegrasyon ve dil kalitesi kapsamı [tam vizyonda](../product/full-scope.md) kalır; ilk pilotun tümünü bekletmez. Takvim ve yüzde tahmini yerine her teslimde çalışan çıktı, kalan kabul ve dış bağımlılık raporlanır.

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


18 Ekim kod devamı: T13/T19 impact UI→ReviewService task scope update→separate approve/apply bağlantısı teslim edildi. [Kapsam ve sınırlar](../quality/workflow-ui-runtime.md#18-ekim--etki-kartından-görev-değişikliğini-uygulama). Sıradaki ana bağlantı kaynaklı relation/decision/question önerisi; cancellation ve AND/OR authoring ayrıca açık.

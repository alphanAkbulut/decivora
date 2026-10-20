# Onaylı geliştirme bütçesi ve completion-claim dilimi

**19 Ekim 2026 · T03/T09/T15/T21.** Kullanıcı “$3 bütçe ve bu sınırlarla devam et” diyerek önerilen sınırları açıkça onayladı. Bu yeni kapsam ilk pilotu da içerir; her alt grup için yeniden$3açılmaz. Ana task/MVP kapanışı değildir.

**Sonraki ayrı veri izni:** kullanıcı6kayıtlı maskelenmiş gerçek mesajın Luna ile≤6generation/6count/$0.25denemesini ayrıca onayladı; aynı$3root altında çalışıldı. [Sonuç](saved-source-pilot-001.md): bu ek iş$0.002963; genel26generation/52HTTP/$0.052555. Aşağıdaki synthetic-only tablosu ilk onayın kapsamıdır; bütün gerçek sohbetlerin paylaşılmasına veya sürekli aktarımına dönüşmez.

## Ortak sınırlar

| Alan | Kabul edilen sınır |
|---|---|
| Toplam model-token maliyet tahmini | ≤$3; pilot001dahil |
| Model generation | ≤100; pilot001dahil |
| HTTP attempt | ≤200; count dahil, pilot001dahil |
| Her generation | ≤10000input +≤2000toplam output token |
| Modeller | OpenAI GPT-6 Luna ve GPT-6.1 Sol; standard tier |
| Kaynak | Yalnız kontrollü sentetik örnekler; gerçek sohbet paylaşımı yok |
| Çalışma biçimi | Küçük gruplar; unknown/error/overrun'da dur, otomatik retry0 |

Anahtar veya raw transcript repo/loga girmez. Onaylı modeller dışına geçiş, gerçek kaynak paylaşımı, bu sınırların artması veya farklı ücretli araç bu izin kapsamında değildir. Fiyatlama ve provider riskleri nedeniyle bu model-token admission sınırı banka ekstresine/account'taki başka programlara kesin tavan iddiası değildir.

## Kodlanan ortak muhasebe

[PilotTransport](../../packages/capture/openai_transport.py) eski20HTTP/$1manifestlerini genişletmez. Yeni `budget_scope=decivora-development-2026-10-19-usd3` biçimi; sabit root policy, kaynaklı prior usage ve küçük exact-payload batch grant'leri kullanır. Root SQLite policy ilk kurulumda `BEGIN IMMEDIATE` ile bağlanır; başka batch/restart onay, limit, fiyat, expiry veya prior kullanımını sıfırlayamaz. Batch hashleri ayrıca kaydedilir.100generation admission,200HTTP ve$3aynı transaction içinde denetlenir. Unknown bir batch bütün root'u dondurur.

[Çalıştırıcı](../../scripts/run_openai_development.py), pilot001private receipt'lerini [salt okunur raporlayıcıyla](../../scripts/report_openai_pilot.py) yeniden okuyarak10generation/20HTTP ve cache-aware24165microusd geçmişini root'a **bir kez** taşır. Eski kayıtlar düzenlenmez. Yeni örnekler ayrı Workspace'lerde; hepsi tek `openai-development-001/shared-budget.sqlite` altında sayılır. Her istekte mevcut domain source/context grant'i ve token rezervasyonu da korunur.24saatlik teknik manifest geçerliliği, bütçeyi yenilemez veya işi arka planda sürdürme izni vermez.

`--prepare`offline'dır; `--run`belirli mevcut grubu çalıştırır. `claims` ve `original-claim` ayrı bilinçli deneylerdir. Receipt'i olan işi yeniden göndermez. Ham model çıktısı değişmez; validator kalitesi geçsin diye gevşetilmez. LOCAL/TEST UI provider'ı kendiliğinden etkinleştirilmedi.

## Kaybolan completion claim için kod değişikliği

[DialogueReviewService](../../packages/capture/dialogue_review.py) talimatı netleştirildi: mevcut task için açık “bitirdim ama testler çalışmadı” raporu, qualifications içeren literal quote ve `status_changes.stage=Done` **iddiası** olarak yakalanmalı. Bu alan canonical Done veya AC/DoD kanıtı değildir. Negation, future conditional, example veya hypothetical completion'da öneri üretmemeli. Türkçe ayrımı açıkça eklendi.

UI, onay, workflow ve verification kapıları değiştirilmedi. Model çıktısı sonradan kural/regex ile başarılı görünecek biçimde düzeltilmedi. Talimat değiştiği için yeni exact payload hashleriyle yeni batch hazırlandı; eski model yanıtı veya pilot001manifesti üzerine yazılmadı.

API payloadında ayrı reasoning seviyesi gönderilmedi; çağrılar Low/Medium diye etiketlenmedi ve provider varsayılanının hangi düzey olduğu doğrulanmadı. Geliştirme sohbetindeki model/düşünme ayarı APIye taşınmaz. Dönen reasoning tokenları output alt kategorisinde saklanır; maliyet ve2000output sınırında ikinci kez eklenmez.

## Gerçek sonuç

[Makine raporu](openai-development-001-results.json) ve [salt okunur üreticisi](../../scripts/report_openai_development.py).

| Grup / kaynak | Model sayısı | Gözlenen sonuç |
|---|---:|---|
| İngilizce “bitirdim, testler çalışmadı” |2 | İki modelde de kaynaklı Done **iddiası** |
| Türkçe “bitirdim, testleri çalıştırmadım” |2 | İki modelde de kaynaklı Done **iddiası** |
| İngilizce “iş bitince ... henüz başlamadım” |2 | Durum önerisi yok |
| Türkçe “bitirmedim, henüz başlamadım” |2 | Durum önerisi yok |
| Pilot001'deki özgün claim cümlesi, yeni talimat |2 | Luna ve Sol'da kaynaklı Done **iddiası** |

Son karşılaştırmada eski/yeni source ID ve context hashleri aynı, payload hashleri farklıdır. İlk Luna yanıtı claim'i atlamıştı; yeni talimatla **aynı tek örnekte** yakalandı. Bu tek karşılaştırma nedensel veya genellenebilir model doğruluğu oranı değildir. Yeni5kaynağın beklentileri AI-authored; bağımsız human-gold/holdout değildir.10yeni source/schema kontrolü geçti; otomatik canonical apply0, başlangıç task/versionları korundu. Gerçek Codex native capture denenmedi.

**Bütçe durumu:** yeni10generation/20HTTP, ilk pilotla birlikte toplam**20generation/40HTTP**. Cache-aware model-token maliyet tahmini toplam**$0.049592**; kalan tahmini pay**$2.950408**,80generation ve160HTTP. Nihai fatura doğrulanmadı. Tavanı tüketmek amaç değildir; bu bulgu için ek çağrı yapılmadı.

## Doğrulama ve kalan sınırlar

[Ortak bütçe testleri](../../tests/runtime/test_development_budget.py) geçmiş para/çağrı/generation taşımasını, başka batch/restart ile sıfırlamayı reddetmeyi, shared freeze ve eski manifestin sessizce genişlememesini sınar. [Runner testi](../../tests/runtime/test_openai_pilot.py) ilk pilot→8iş→2iş zincirini ve salt okunur raporun API çağırmadığını kontrol eder. Sahte HTTP çıktıları semantik kalite kanıtı sayılmaz.

Tam anlam kalitesi, role/source ayrımı, onaylı gerçek Codex adapter'ı ve ana UI aktivasyonu mevcut görevlerde açık. Bu kapsam bütçe hazırlığını yeniden insan blocker'ı yapmaz; mevcut root sınırları içindeki sentetik işlerde tekrar genel harcama onayı gerekmez. Gerçek kaynak veya kapsam değişikliği ayrı izin ister.

**Yerel doğrulama:**475runtime ve48repo testi geçti;50Mermaid kaynağı offline render edildi. UI kodu değiştirilmedi; browser testleri bu tur yeniden koşulmuş sayılmaz. Test ve rapor üretimi ek API çağrısı yapmadı. İlk ücretli grupla birlikte bütün private receipt kayıtları korunur; raw içerik veya API key GitHub'a gönderilmez.

## 19Ekim — native sentetik Codex sohbet deneyi

[Codex E2E raporu](codex-e2e-001.md): mevcut geçerli3USD ortak root altında4model dispatch kabulü/8HTTP bütçe payı daha sayıldı;3settled/1unknown. Belirsiz işte gerçek HTTP/generation sayısı kesinleşmedi. Root30dispatch/60HTTP bütçe sayımı, known tahmin$0.053690 +held unknown$0.002250. Dördüncü request sonrası root frozen; yeni retry/çağrı veya policy reset yok. Bu kullanım yeni açılmış sentetik sohbetten assistant kaynaklarıdır, gerçek kullanıcı geçmişi paylaşımı değildir. Kesin fatura ve unknown kullanım uzlaştırması açık.


**19Ekim takip kararı:** Kullanıcı rezerv koruyarak devamı açıkça onayladı. `unknown_reviews` kaydı root freeze'i kaldırdı; orijinalunknown, actual=null,2250microusd rezerv,30dispatch/60HTTP bütçe sayımı ve aynı payload tekrar reddi korundu. Toplam55940microusd yerel taahhüt; tavan3USD ve önceki expiry değişmedi. Yeni çağrı0. Pending/overrun bu işlemle açılamaz; kalan limitler ve exact source izinleri yeni istekte tekrar uygulanır. [Uygulama/risk sözleşmesi](codex-e2e-001.md#belirsiz-kullanımda-devam-sözleşmesi). Bu karar gerçek fatura uzlaştırması değildir.


## İlk4case diyalog batch

[Bulgu raporu](dialogue-batch-001.md):10yeni dispatch/20HTTP bütçe payı,9usage yanıtı,1generation unknown. Yeni bilinen3136microusd+rezerv2250=5386yerel taahhüt. Root40dispatch/80HTTP,known56826+held4500=61326microusd.3USD/expiry değişmedi. Eski unknown onayı yeni unknown için kullanılmadı; root frozen ve yeni continuation onayı bekliyor. Fatura doğrulanmadı.


**Onaylı devam:** Önceki J02_m4unknown rezervi user onayıyla korundu;8yeni dispatch/16HTTP payı,7usage ve1yeni timeout unknown. Root48dispatch/96HTTP;known59332+held6750=66082microusd. Yeni unknown nedeniyle frozen; diğer iki unknown onayı bunu kapsamaz. Kalan6mesaj çağrılmadı. [Detay ve yeni owner kapısı](dialogue-batch-001-continuation.md).


## 20 Ekim — aynı toplam sınırlarla onaylı süre yenilemesi

**Karar ve gerekçe:** Kullanıcı `call_2c463c6c33ae4cfaa8d5aa94bd09955a` cevabında aynı toplam sınırlarla 24 saat yenilemeyi onayladı. Başlangıç onayın alındığı 20 Ekim 2026 10:35:38 UTC; bitiş 21 Ekim 2026 10:35:38 UTC / **13:35:38 Türkiye**. Amaç süresi dolmuş izin dönemini yenilemektir; harcama tavanını veya kaynak erişimini genişletmek değildir.

| Sınır / kullanım | Yenileme sonrası |
|---|---:|
| Birikimli para tavanı | $3 |
| Birikimli model / HTTP sınırı | 100 / 200 |
| İstek başına giriş / çıkış | 10.000 / 2.000 token |
| Taşınan dispatch / HTTP bütçe payı | 52 / 104 |
| Bilinen maliyet tahmini | $0.060536 |
| Unknown sayısı / korunan rezerv | 3 / $0.006750 |
| Birikimli yerel taahhüt | $0.067286 |
| Kalan model / HTTP payı | 48 / 96 |
| Kalan ihtiyatlı yerel harcama payı | $2.932714 |
| Bu yenilemede yeni dispatch / HTTP | 0 / 0 |

HTTP bütçe payı kesin wire/generation sayısı değildir; unknown actual kullanım halen bilinmiyor. Yerel pay provider hesap bakiyesi veya fatura değildir. Önceden benimsenmiş fiyat revision'ı değişmedi; bu işlem güncel fiyat araştırması değildir.

**Uygulama:** Eski policy ve ledger değiştirilmedi. Tutarlı private SQLite predecessor yedeği, policy/ledger hashleri, unknown rezervleri ve önceki continuation onaylarını bağlayan taşıma makbuzu korundu. Successor immutable policy aynı budget_scope ve tam birikimli `prior_usage` ile oluşturuldu. Dispatch satırlarını ayrıca kopyalamamak çifte sayımı önler; prior_usage'ı sıfırlamamak yeni $3 bütçe açılmasını önler. Eski dönem expired kaldığı için önceki launcher yeni çağrı için geçerli izin kazanmaz. Private dosyalar, anahtar, DB ve ham sohbet GitHub'a konmadı.

**Doğrulama:** Constructor/snapshot yerel ve ağsız çalıştırıldı; olmayan credential yolu ve çağrılırsa hata veren transport kullanıldı. Sayaçlar 52/104/67286microusd ve yeni dispatch0 doğrulandı; eski unknown satırları actual=null, rezerv6750microusd ve devam onaylarıyla değişmeden kaldı. LOCAL yedeği alınıp idle kontrolüyle yalnız LOCAL yeniden başlatıldı; tüm uygulama tablolarının fingerprint'leri eşit, seçili native bağlantı0, worker kapalı, profil Available. TEST yeniden başlatılmadı. Yeni gerçek sohbet okuma, anahtar okuma veya provider çağrısı yok.

**Açık sınır:** Yeni profile digest eski source consent'i geçerli kılmaz. Sonraki gerçek kabul için exact kaynak/context paylaşımı ve ayrı aktivasyon gerekir. Bu yenileme bunları veya otomatik retry/model yükseltmesini onaylamaz. Önceki 680runtime/49repo ve 62Mermaid render sonucu kod teslimine aittir; bu config değişikliği için tümü yeniden koşulmuş sayılmaz. Diyagramların onay→ayrı aktivasyon→dispatch sınırları değişmedi; Mermaid içeriği değiştirilmedi. Bu yenilemede 7 birikimli bütçe regresyon testi, docs/anchor ve progress kontrolleri geçti.

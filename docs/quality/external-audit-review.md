# Decivora — Dış teknik audit karşı değerlendirmesi

> **Tarihsel inceleme:** Aşağıdaki değerlendirme `28e9d6d` öncesi uygulama durumunu anlatır. Sonraki kod/CI/restore/scorer düzeltmelerinin güncel kaydı [audit remediation](audit-remediation.md) içindedir. “Yok / yapılmadı” satırlarını bugünkü main durumu sayma.

> **Sonraki kanıt güncellemesi — 2026-10-11:** Kullanıcının gönderdiği Spike-0 paketi artık incelendi; sağlanan 32 test burada geçti ve ek sentetik denemeler yapıldı. [Spike-0 kaynak/test karşı değerlendirmesi](spike0-audit.md), aşağıdaki ilk incelemenin S-01–S-10 erişim sınırlamasını günceller. Gerçek bulut oturumu burada yeniden çalıştırılmadı; paket GitHub main'e dahil edilmedi. Aşağıdaki ilk inceleme kendi ref/kapsamıyla tarihsel kayıt olarak korunur.

**İnceleme tarihi:** 2026-10-11  
**Kaynak rapor:** `decivora_teknik_durum_ve_audit_v2.md`, Claude; beyan edilen yerel ref `fb0d983`.  
**Kaynak rapor SHA-256:** `e8c4f9d7e4122143a1c1206428a2cae4c5c83cb6f5eca0f943551175681602bb`  
**Bu incelemenin güncel GitHub ref'i:** `28e9d6d29fa2010ff6febc220d7e4b123abe04de`.  
**Tür:** Salt okunur teknik/ürün karşı değerlendirmesi; düzeltme, kabul edilmiş ADR, runtime audit veya tamamlanmış ürün testi değildir.

## 1. Değerlendirme

Rapor faydalı bir risk listesi. Güncel repo için bütünüyle doğru bir durum raporu olarak kullanılamaz: eski snapshot'a dayanıyor; bazı boşluklar sonradan kısmen kapandı; Spike-0 kanıtları bu incelemede erişilebilir değil. Raporun kendi güncellik uyarısı yerindedir. Eski durumda doğru olan sayıları bugün yanlış ölçülmüş gibi değerlendirmemek gerekir.

Ana tespit geçerli: **ürün runtime'ı yok; ürün değeri, otomatik capture, extraction kalitesi, maliyet ve native üstünlük doğrulanmış değil.** Bunun yanında doküman ve veri doğrulama kodu gerçekten mevcut. Bunları çalışan ürün diye sunmak da “hiç çalışan kod/fixture yok” demek de hatalıdır.

Önerim: tam vizyonu koru; ilk kanıtı küçük bir karar → görev etkisi → hedef uygulama zincirinden üret. Backlog'un teknik bağımlılıklarını düzelt, güvenilir oracle/scorer ve küçük çalışma deneyine geç. Sadece yeni belge/araştırma üretmekten kaçın. “Wedge-0'a daraltıldı”, “Projects yüzünden bırakıldı”, “owner işleri park etti” sonuçlarını bu dış rapordan kullanıcı kararı olarak aktarma.

## 2. Yöntem ve gerçekten doğrulananlar

- GitHub main ref'i, commit/tree ve dosya envanteri alındı; tree truncated değildi.
- Yerel mirror dosyaları Git blob SHA ile immutable tree'ye karşılaştırıldı. Bu incelemede kullanılan Markdown/JSON/script dosyaları eşleşti. Bir araştırma CSV'sinin yerel blob kimliği farklı çıktı: `docs/discovery/upstream-component-inventory.csv`. CSV bu karşı değerlendirmenin kanıtı olarak kullanılmadı; farkın nedeni araştırılmadı ve dosya değiştirilmedi.
- `scripts/check_docs.py` tekrar çalıştırıldı: **91 Markdown / 990 yerel bağlantı**, 32 scope, 30 görev, 14 MVP kriteri; faz görünümü backlog ile eşleşti. 35 Mermaid/15 belge inventory ve kayıtlı render kaynak hashleri uyumlu.
- `scripts/check_corpus.py --self-test` tekrar çalıştırıldı: **6 oturum / 2 proje / 58 mesaj / 66 annotation / 46 farklı KnowledgeRecord**, 11 negatif veri gate'i beklenen şekilde reddedildi. İnsan review'u pending; ürün sonucu not_run.
- Geçici repo kopyasında var olan belgeye var olmayan bir `#anchor` bağlantısı eklendi. Checker **exit 0 / PASS** verdi. Asıl repo değiştirilmedi; geçici kopya temizlendi. A-03 güncel ve yeniden üretildi.
- Wilson örneklem hesabı Python standart kütüphanesiyle yeniden hesaplandı; yöntem NIST kaynağıyla kontrol edildi.
- Anthropic Consumer/Commercial Terms resmî sayfaları okundu. Bu, sözleşme maddesi kontrolüdür; Decivora'nın hukuki sınıflandırmasının sonucu değildir.
- Spike-0 kaynakları, 32 test ve real-run-001 verisi bu incelemede görülmedi/çalıştırılmadı. Raporun v1 eki de sunulmadı.
- Ürün, model, gerçek coding capture, native Projects, UI ve yeni Mermaid render deneyi çalıştırılmadı. Önceki render kaydı kontrol edildi; canlı tekrar render yapılmadı.

[İncelenen GitHub snapshot](https://github.com/alphanAkbulut/decivora/tree/28e9d6d29fa2010ff6febc220d7e4b123abe04de).

## 3. Güncel envanter: raporla fark

| Alan | Dış raporda | Güncel kanıt / sınır |
|---|---|---|
| Doküman/link | 70 / 487 | Bu tur 91 / 990; eski sayım kendi snapshot'ına ait olabilir |
| Mermaid | 30 | 35 / 15 belge; kayıtlı 35 render sonucu ve kaynak/SVG hash tutarlılığı mevcut |
| Ürün runtime | Yok | Hâlâ yok |
| Veri/fixture | Yok; tek impact örneği | Ayrı corpus source/oracle dosyaları, manifest, GAP/CHAIN örnekleri ve corpus validator var; executable production şema/scorer yok |
| Gerçek hedef gözlemi | Yok/Spike-0 varsayımı | READBACK-01: tek doküman/ref için manuel GitHub eşleşmesi; tüm bundle/task/adapter başarısı değil |
| CI | Yok | Hâlâ workflow yok |
| LICENSE / SECURITY / CODEOWNERS | Yok | Hâlâ yok; lisans seçenek belgesi var, lisans verilmiş değil |
| İnsan/gold review | Yok | Corpus etiket taslağı var; insan review'u pending |
| Native/model deneyleri | Yok | Hâlâ not_run |

## 4. A-01–A-17: bulgu bazında hüküm

Aşağıdaki ID'ler raporun **3. bölümündeki ayrıntılı tabloya** aittir. Yönetici özetindeki A-03/A-04/A-05 başka konular için kullanılmış; ID çakışması raporun izlenebilirlik kusurudur. Eski F-01–17 eşlemesi v1 olmadan doğrulanamaz.

| ID | Hüküm | Kanıt / ne yapılmalı |
|---|---|---|
| A-01 Doğrusal backlog | **Kısmen doğru; önemli** | Ana tabloda T01–T30 büyük ölçüde zincir. Fakat T03 birden fazla önkoşula sahip, alt işler farklı bağımlı ve giriş metni teslim sırasını hard blocker'dan ayırıyor. “Hiç erken kesme noktası yok” güncel T03a/b/c yatırım kapılarını atlıyor. Gerçek teknik/policy bağımlılıklarını ayırıp hazır işleri göstermek gerekir; scope'u sessizce daraltmak çözüm değil. |
| A-02 T15/restore | **Geçerli plan belirsizliği** | T15 işi restore/replay, T15a crash/restore proof istiyor; tam DB+payload backup/migration/restore T23a'da ve T23 T15 sonrasında. Erken çekirdek restore'un üretileceği açık teslim yok. “Mantıken kesin imkânsız” yerine mevcut planın kendi kapanış kanıtını açık üretmediği söylenmeli. Öneri: minimal çekirdek backup/restore dilimini T07/storage ile erken tanımla, T15'te sınayıp T23'te export/privacy/migration/operasyon kapsamını tamamla. Restore kalite kapısını silme. |
| A-03 Anchor kontrolü | **Doğru; yeniden üretildi** | Script `#` sonrasını kırpıyor, aynı sayfa anchor'larını da atlıyor. Geçici negatif örnek PASS aldı. GitHub başlık slug/Unicode/duplicate heading ve explicit ID'leri kapsayan testli kontrol gerekli. Her özel anchor otomatik bozuk sayılamaz. |
| A-04 Sabit sayılar | **Doğru; hüküm düzeltilmeli** | 30 görev ve AC-01–14 sabit; başka expected ID kümeleri de sabit. Yeni task'ta sessiz başarısızlık değil açık error üretir. Kapsamın korunması için kasıtlı regression guard faydalıdır. Görüntülenen sayıları veriden üret; beklenen kapsam manifest'ini kontrollü değiştir. Guard'ları tamamen kaldırma. |
| A-05 ADR kabulü | **Olgu doğru; tek başına blocker değil** | ADR'ler proposed; kullanıcı ürün ilkelerinin kabulü teknoloji kabulü değildir. P0 build/extend seçilmeden production stack'i kilitlememek doğru. Küçük deney öncesi geçici stack/yöntem/erişim sınırı açık seçilmeli; gerekli invariant'lar uygulama görevi başladığında kabul/statü kaydıyla bağlanmalı. “ADR hiç yok” doğru değil. |
| A-06 CI/lisans/policy | **Doğru; önemleri farklı** | Workflow ve üç kök dosya yok. CI mevcut docs/corpus kontrollerini otomatikleştirebilir. LICENSE owner yayın/reuse stratejisi kararı; private keşif için lisans verilmiş gibi davranılmaz. SECURITY gerçek ingress/release'de kapsam/kontakt ister. CODEOWNERS ekip review yönetişimidir; tek kişilik keşfin ilk zorunlu blocker'ı değil. |
| A-07 Şema/fixture yok | **Güncel durumda yanlış; kısmi boşluk var** | Corpus source/oracle/manifest ve validator mevcut. Production JSON Schema ve executable domain harness yok. “AC koda dökülemez” fazla güçlü: mevcut test edilebilir kurallar executable sözleşmeye çevrilebilir. Kritik karar/onay/target durumları ilk adım. |
| A-08 Sayı drift'i | **Kısmen / A-10 ile duplicate** | Eski tarihsel sayımlar kendiliğinden drift değil. Güncel statü ile tarihsel kontrol net ayrılmalı; tek current inventory kaynağı ve eski sonuçların ref'i korunmalı. |
| A-09 İstatistik | **Matematik koşullu doğru; güncel protokol eksik sunulmuş** | n=30 ve hatasız sonuç için iki taraflı %95 Wilson alt sınırı ≈0.8865; 0.95 alt sınırı için 73 bağımsız, hatasız gözlem gerekir. Yöntem/tek-çift taraf ve sampling değişince sayı değişir. Güncel protokol n=30'u hata bulma örneklemi diye açık sınırlar; genel %95 kalite kanıtı saymaz. Hedef reliability, confidence ve corpus sayısını ayrı tut; cluster'ları bağımsız trial sayma. |
| A-10 Belgeler arası sayılar | **Kısmen giderilmiş** | start-here artık 25 anlama kontrolü; güncel 35 diagram inventory mevcut. Status tarihsel kayıtları eski sayımlar tutuyor; bunlar aynı anda current iddia değil. Current summary otomatik üretilebilir, tarihsel kanıt silinmemeli. |
| A-11 Katmanlı diagram notları | **Tarihsel yapı; okunabilirlik riski sürer** | Sayfanın başında 35/15 güncel inventory ve eski kayıtların tarihsel olduğuna dair açıklama var. Tek güncel bölüm + tarihsel bölüm düzeni korunmalı; sırf eski sayılar var diye hepsini yeniden yazmak delil kaybettirir. |
| A-12 Mermaid render | **Güncel kanıt açısından eskimiş; CI açığı gerçek** | Mermaid 11.17.2 ile kayıtlı 35/35 yerel render; source/SVG hash eşleşmesi var. Checker canlı parse/render yapmıyor; CI yok. Sürümü sabit, ağ/asset sınırı belli render kontrolü eklenebilir. Önceki sonuç gelecekteki renderer uyum garantisi değil. |
| A-13 Makine okunur senaryo | **Kısmen doğru** | GAP JSON, CHAIN örneği ve 6 corpus oracle mevcut. Bütün V/MU/CON ve kritik crash/authority yolları executable suite'e dönüşmüş değil. Önce required case/checkpoint/state/authority/prediction/matching/result formatını kur; tüm Markdown'ı YAML'a çevirmek tek başına runtime doğrulama değildir. |
| A-14 Kendi kendini puanlama | **Risk doğru; mevcut ayrım atlanmış** | evaluation-protocol bağımsız oracle/human reviewer ve adjudication ister; ikinci reviewer yoksa sınırlamayı bildirir. Corpus AI taslağıdır, gold değildir. Çalışan scorer ve insan review henüz yok. Beklenen sonucu sistemin kendi extractor/traversal'ı üretmemeli; model judge tek release otoritesi olmamalı. |
| A-15 Kapsam şişkinliği | **Makul ürün riski; otomatik scope kararı değil** | Full scope geniş, uygulama ve kullanıcı ölçümü geride. 10 engine ayrı servis şartı değil; modül sorumlulukları. Kullanıcı full vizyonu korumayı istedi. MVP/öğrenme dilimini küçültmek ve P2–4 işlerini sıraya koymak mümkündür; vision/roadmap'ten silme veya multi-tenant'i şimdi kurma yok. |
| A-16 Anthropic şartları | **Gerçek inceleme konusu; hukuki sonuç unknown** | Resmî şartlarda rekabetçi kullanım, reverse engineering ve bazı otomatik erişim sınırları var. Ürün/hesap/region/uygulanabilir şart ayrılmalı. Halka açık davranış dokümanı analizi ile hizmet kullanımı ve OSS lisansı farklı; “doküman okumak kesin hukuken güvenli” ya da “Decivora kesin yasak” çıkarılmaz. |
| A-17 Reuse sadece README | **Bütün araştırma için yanlış; bazı adaylar için geçerli** | WrongStack pinned kaynak/modül/manifest çalışması, R01–24 ve Graphiti/LangGraph/LiteLLM/OpenFGA seçili source okumaları var. Cortex/mai-mcp vb. aynı derinlikte olmayabilir. Bütün rakipler klon düzeyinde audit edildi veya çalıştırıldı denemez. Yeni tarama yalnız açık contract/adoption sorusunu çözecek adaya yapılmalı. |

## 5. Spike-0: S-01–S-10

**Ortak durum: bu raporda bildirilen dış artifact bulguları; bağımsız doğrulanmadı.** Güncel main tree'de `spikes/spike-0` yok. İncelenen çalışma alanında real-run-001/kaynak bulunmadı. Claude'un yerel untracked kodu başka workspace'te olabilir; yok olmuş veya hiç yapılmamış demiyoruz.

| ID | Bildirilen iddia nasıl yorumlanmalı? | Doğrulama / sonraki iş |
|---|---|---|
| S-01 Stop'ta transcript eksik | n=1 doğruysa önemli freshness bulgusu; bütün hook'ların güvenilmezliği veya genel tasarımın çürümesi değildir. Güncel capture sözleşmesi zaten partial/idle/deadline ve session-end gelmeme durumunu içerir. | Kurulu host/build, trigger ve dosya revision/zamanı, bounded retry/rescan ve contiguous checkpoint; normal bitiş/crash/parallel/compaction örnekleri. |
| S-02 Araç gürültüsü | 538 satır /313 mesaj /33 text farklı paydalardır. Rol ve block-type tanımları olmadan genel sinyal oranı olmaz. Tool çıktısı task başarısı/evidence için yine önemli olabilir. | Raw içerik yerine redakte sayım/metadata; insan/assistant/tool/evidence ve quote ayrımı. Sadece text extraction, tool evidence kaybını maskelememeli. |
| S-03 Assistant decision adayı | **Aday üretmek tek başına invariant ihlali değil.** Sorun, agent claim'in accepted insan kararı olarak uygulanması. Tip/source/authority/state ayrımı kaynak okunmadan değerlendirilemez. | Proposal/reported/accepted ve human binding fixture'ları; decision terimi canonical kabul için kullanılıyorsa düzeltme. |
| S-04 Regex recall | Ölçülmedi bilgisi doğru sınırdır; regex'in düşük recall'u burada kanıtlı değil. | Etiketli input, bağımsız gold, prediction ve per-class precision/recall; kritik false-approval/false-done seti. Otomatik anlam çıkarımı zorunlu işi parser alternatifiyle iptal etme. |
| S-05 Jaccard 0.8 | Eşiğin kalibrasyonu yoksa keyfi aday heuristic olabilir. Türkçe morfoloji önemli; embedding'e geçmek otomatik çözüm değil. | Negation/quote/conditional/different project/aynı metin farklı niyet; calibration ve yanlış merge maliyeti. Fuzzy similarity canonical onay üretemez. |
| S-06 Tek kullanıcı/makine | Pilot sınırı makul; sentetik paralel test gerçek concurrency kanıtı değil. | Aynı/different project, parent/child, crash/retry ve gerçek parallel fixture session raporu. |
| S-07 Installer yedeği | Backup/marker iyi örüntü olabilir; güvenli kurulum kanıtı sayılmaz. | İzinli izole workspace'te install/uninstall idempotency, var olan ayar korunumu, parse/path/race negatifleri. |
| S-08 exit 0/stdout boş | Host'u bloklamamak için mümkün tercih; hook hatalarını sürekli sağlıklı göstermek doğru değil. | Başarı receipt'i ve operational failure ayrı; handler güvenli hata/timeout; ilgili hook sözleşmesine göre çıktı. |
| S-09 Redaction | Pattern-only eksik olabilir; .gitignore erişim/gizlilik sınırı veya secret taraması değildir. | Veri minimizasyonu, yerel read scope, secret fixture'ları, payload/log/export ayrımı; gerçek transcript'i analize/publish'a taşımadan redakte review. |
| S-10 Untracked spike | Kaybolma/traceability riski makul; “hemen commit” kör uygulanmaz. | Önce code/test/result/real data/config lisans ve gizlilik ayrımı; yalnız incelenmiş temiz code/fixture ve reproducible komut. Gerçek transcript/credential/config repoya commit edilmez. |

## 6. Gri alanlar: G-00–G-14

| ID | Güncel durum / kapanış |
|---|---|
| G-00 Upstream | Bu tur GitHub main/tree erişildi; güncel inceleme ref'i sabitlendi. Eski kısa ref Git Data endpoint'inden çözülemedi; eski klonun birebir envanteri yeniden kanıtlanmadı. |
| G-01 Hooks | Hâlâ gerçek capability bilinmiyor. 3–5 oturum arıza keşfi başlangıcı; güvenilirlik yüzdesi kanıtı değil. Spike artifact erişimi ilk önkoşul. |
| G-02 Fresh memory | Protokol mevcut, deney yok. Paket/full-source/prompt-only aynı güncel oracle ve contamination/sıra kontrolüyle sınanmalı. |
| G-03 Ledger-first | Faydalı basit kontrol adayı. Native/extend/build baselines mevcut; ledger-first adıyla ayrı pinned kol ve hangi manuel update maliyetinin sayılacağı netleştirilmeli. Henüz koşul seçilmiş veya denenmiş değil. |
| G-04 Projects örtüşmesi | Gerçek native kullanım/kıyas hâlâ yok. Dokümanda görünmemesi özellik yokluğunun kanıtı değil; erişim/build/config ve unknown korunmalı. |
| G-05 Kullanıcı ihtiyacı | Owner problemi birinci el; kamu issue/konuşma masa başı araştırması var. Doğrudan görüşme ve pazar doğrulaması yok. Önce owner pilotu, sonra benzer kullanıcı tercihi geçerli; 5–8 bir keşif önerisi, zorunlu istatistik eşiği değil. |
| G-06 Build/extend | Source-level araştırma bazı adaylarda mevcut; gerçek kıyas/adoption kararı yok. T03a/b/c uygun; sadece README bilgisi bütün araştırmaya genellenmez. |
| G-07 API/bütçe | Q03-R1 A ilk no-extra-paid deney sırası kabul; sonraki veri/provider/bütçe açık. “Şimdilik ücretli deneyi ertele” bütün ürünün LLM'siz olacağı veya owner'ın konuyu süresiz park ettiği anlamına gelmez. |
| G-08 İkinci yüzey/Windows | B Codex + tek repo sonraki bağlantı olarak istendi; host/build/OS matrisi açık. Windows tek başına MVP requirement seçilmiş değil. |
| G-09 Hizmet şartları | Madde kontrolü var; uygulanabilir region/plan ve Decivora'nın rekabetçi kullanım yorumu açık. OSS source lisansı bu sözleşmeyi çözmez. |
| G-10 Çok yüzey capture | **Tam kapsamdan çıkarılmadı.** Coding adapter'lar P1, geniş chat/provider araştırması P2; ilk manuel A otomatik capture başarısı değildir. MCP araç bağlantısı bütün chat/capture izni değildir. |
| G-11 Kapasite | Workload/limit/latency hedefleri taslak; uygulama ölçümü yok. İlk uygun fazda finite limits ve replay/crash; distributed kapasiteyi bugünkü blocker yapma. |
| G-12 Consent | Q10-A kayıtlı; listeleme ve seçilmiş içerik scope'u ayrı; runtime rıza/ACL testleri yok. |
| G-13 Görünürlük/lisans | **Private başlangıç kararı mevcut ve repo private.** Public yayın ve lisans kararı açık; ikisini “ikisi de kararsız” sayma. |
| G-14 Go/no-go | T03c ve Spike-1'de nitel kapılar var; önceden sabit nicel kullanıcı yükü/fayda eşiği yok. “Hiç kriter yazılmadı” fazla güçlü. Erken pilot bazeline sonrası eşik önerisi hazırlayıp gerçek karşılaştırmadan önce owner'a bağla. |

Rapor ağacındaki “PARK (owner bekle dedi)” etiketleri bu kullanıcı konuşmasının karar kaydı yerine geçmez. Q09 product mindset/blocker önceliği kabul edilmiş; kanal/sıklık farklı sorudur. Q06/Q08 açık, Q02/Q03 kısmen çözülmüş; bunları topluca park etmek yeni karar olur.

## 7. Örneklem planı düzeltmesi

NIST'in Wilson/binom confidence interval yöntemini temel alarak yapılan **bizim hesabımız**, n bağımsız Bernoulli trial ve hepsi başarıysa:

- İki taraflı %95 Wilson alt sınırı: `n / (n + z²)`, `z ≈ 1.96`.
- n=30: alt sınır ≈0.8865.
- Alt sınır ≥0.90 için en az 35; ≥0.95 için en az 73 **hatasız bağımsız** trial.
- %95 exact binomial tek taraflı yöntem aynı 0.95 alt hedefi için 59; çift taraflı için 72 hatasız trial gerektirir.

Bu rakamlar farklı yöntemlerin sonuçlarıdır; interchangeably kullanılmaz. “95% confidence” ve “95% true success lower bound” farklı parametrelerdir. Tek konuşmadan 73 mesaj, 73 bağımsız task/decision veya kullanıcı değildir. Aynı case'in model tekrarları da bağımsız pazar örneklemi değildir. Precision, recall ve kritik hata riski ayrı denominator/örneklem ister. Mevcut 6 oturum/46 record **regresyon/arıza keşfi** içindir; genellenebilir reliability kanıtı değildir. Sıfır gözlenen kritik hata riskin sıfır olduğunu kanıtlamaz.

Kaynak: [NIST — Confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). Sayılar burada Python ile hesaplandı; ürün ölçüm sonucu değildir.

## 8. Hizmet şartları ve lisans ayrımı

İncelenen Consumer sayfası October 8, 2025 effective tarihli ve EEA/Switzerland kapsamı söylüyor; bunu kullanıcı için uygulanabilir Türkiye şartı diye varsaymıyoruz. Rekabetçi hizmet geliştirme, reverse engineering ve izin verilmemiş otomatik erişim maddeleri görülüyor. Commercial sayfası June 17, 2025 effective tarihli; hizmete rekabetçi ürün geliştirmek amacıyla erişimi sınırlıyor, ayrıca bazı ürün/hizmetleri API üzerinden güçlendirmeyi izin/policy koşullarıyla düzenliyor. Hangi kullanımın hangi sınıfa girdiği bu teknik incelemede karara bağlanmadı.

Kaynaklar: [Anthropic Consumer Terms](https://www.anthropic.com/legal/consumer-terms), [Anthropic Commercial Terms](https://www.anthropic.com/legal/commercial-terms).

Hizmet kullanım sözleşmesi, public belge benchmark'ı ve açık kaynak kod lisansı ayrı inceleme alanlarıdır. Kendi codebase'imizi yazmak, kullandığımız hizmetin sözleşmesini otomatik olarak geçersiz kılmaz. Önce somut adapter/native deneyinde plan, erişim yöntemi, amaç ve uygulanabilir şart sürümü belirlenmeli. Bu inceleme yeni hesap/ücret, scrape veya hukuki uygunluk garantisi vermez.

## 9. Somut öneriler: mevcut durum → değişiklik → doğrulama

Bu bölüm **öneri**, uygulanmış task veya yeni scope kararı değildir.

| Öncelik | Mevcut durum → öneri | Fayda / risk | Hedefler / kabul kanıtı |
|---|---|---|---|
| 1 | Erken restore teslimi belirsiz → T07/storage altında minimal snapshot/restore+replay'i tanımla; T15 ona bağlı; T23 geniş operasyon | Kapı kapanabilir olur; yanlışlıkla T23 güvenlik kapsamını azaltma riski | backlog, phase-tracker, gate metni; fixture restore digest/crash/unknown schema kanıtı, teknik dependency cycle kontrolü |
| 1 | Teslim sırası teknik blocker gibi okunuyor → gerçek bağımlılık/kanıt kapısı/plan sırasını ayır | Erken kullanılabilir öğrenme; entegrasyon güvenlik kapıları atlanmamalı | canonical backlog/faz/roadmap; her prerequisite'in gerekçesi, hazır dilim ve ilk kesme noktası |
| 1 | AI oracle taslağı mevcut → insan review + anlaşmazlık kaydı + frozen scorer/checkpoint contract | Gerçek kalite ölçümüne zemin; aynı AI oracle ve ürünün ortak kör noktası | T01/T01f/T03f; source exact span, rejected/unmatched, authority, AND/OR/unknown, target revision testleri |
| 2 | Checker anchor false-pass + CI yok → testli anchor validator ve mevcut doc/corpus kontrolleriyle minimal CI | Belge/fixture drift'i erken yakalar; false alarm/renderer paket maliyeti | scripts/.github; geçerli/bozuk/TR/duplicate anchor mutantları, scope guard ve source-hash kontrolleri |
| 2 | Runtime/harness yok → T03a sınırlı yöntemi seç; T03b küçük no-model decision/impact/target deneyi | En erken gerçek state zinciri kanıtı; mock sonucu otomatik semantics diye sunulmamalı | izole fixture workspace; manual input→typed candidate→approval→state→immutable observer→AC; geç/yanlış/izin eksik negatifleri |
| 2 | Otomatik semantics hâlâ zorunlu/not_run → ayrı gerçek extractor prediction testi | Ürünün asıl automation gereksinimi sınanır; egress/bütçe/maliyet | T09/T24q; source-only input, bağımsız oracle, heldout family, per-class score/error/usage; actual provider gerekiyorsa önce somut permission |
| 3 | Fresh-session/native/ledger kıyas yapılmadı → karşılaştırılabilir kolları pin ve quality/review/cost ölç | Build/extend kararını besler; learning/contamination ve farklı izinler yanıltabilir | T03b/T03c/RES-08; eşit source/target erişimi, zorunlu unknown'lar, order ve bütün manual upkeep maliyeti |
| Koşullu | Spike-0 dış artifact → kaynak/result/kapsam incelemesi, sonra temiz artifact paylaşımı | Eski emeği tekrar kullanma; gerçek transcript/secret/config yayımlama riski | exact path/ref/test komutu ve redakte receipt; n=1 yeniden üretim, normal/crash/parallel coverage |
| Release öncesi | LICENSE/policy ve owner fayda eşiği açık → somut dağıtım/hesap planına göre karar | İddia ve yetki sınırı; üretim sistemi varmış gibi policy oluşturma riski | OPEN kararları; owner seçimi, dependency notices ve privacy/release checklist |

### İlk incelebilir küçük çalışma dilimi

Mevcut dataset'ten tek bir karar değişimi + gecikmiş exact cevap + AND/OR etki + eski/yeni target ref + tek AC/tüm DoD ayrımını çalıştırılabilir harness'te sınamak en değerli başlangıçtır. Önce elle/fixture girdisi; ardından aynı oracle üzerinde gerçek otomatik extractor çıktısı. No-model hazırlık otomatik çıkarımı iptal etmez. Tam P1b MVP ve P2–4 kapsamları bu öğrenme dilimiyle değiştirilmez.

Mevcut kaynaklar: [backlog](https://github.com/alphanAkbulut/decivora/blob/28e9d6d29fa2010ff6febc220d7e4b123abe04de/docs/delivery/backlog.md), [evaluation protocol](https://github.com/alphanAkbulut/decivora/blob/28e9d6d29fa2010ff6febc220d7e4b123abe04de/docs/quality/evaluation-protocol.md), [baseline](https://github.com/alphanAkbulut/decivora/blob/28e9d6d29fa2010ff6febc220d7e4b123abe04de/docs/quality/baseline.md), [Spike-1 planı](https://github.com/alphanAkbulut/decivora/blob/28e9d6d29fa2010ff6febc220d7e4b123abe04de/docs/delivery/spike-1-v1.md), [target gözlemi](https://github.com/alphanAkbulut/decivora/blob/28e9d6d29fa2010ff6febc220d7e4b123abe04de/docs/quality/first-target-readback.md).

## 10. Yapılmayanlar ve eksik kanıt

Bu tur yalnız karşı değerlendirme ve bu yerel rapor üretildi; repository dosyaları, kullanıcı projeleri, agent ayarları ve GitHub branch'i değiştirilmedi. Model API, ücretli hizmet veya dış kişiye mesaj yok. Kararları/ADR'leri sessizce kabul etme, scope daraltma veya çalıştırılmamış spike'ı commit etme yapılmadı.

Spike-0'ın exact kod/sonuç yolu veya redakte artifact paketi gerekiyor. Gerçek transcript gerekli değil: ilkin source code, synthetic fixture/test, kurulu host/build ve redakte observation/result yeterli. Dosyalar geldikten sonra S-01–10 kaynak düzeyinde kontrol edilebilir; öncesinde “32 test geçti” yalnız dış raporun iddiasıdır.

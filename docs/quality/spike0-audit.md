# Spike-0 paket incelemesi — kaynak ve yeniden üretim

> **Düzeltme öncesi kaynak incelemesi:** Bulgular aşağıdaki arşiv hash’ine aittir. Kullanıcı sonrasında uygulamayı yetkilendirdi. [Güncel düzeltmeler/testler](audit-remediation.md) ayrı kayıttır; bu rapordaki “uygulanmadı / main’de yok” ifadeleri tarihsel durumdur.

**Tarih:** 2026-10-11  
**Paket:** `decivora_spike0_v1.zip`, 30 dosya, 91.193 açılmış byte.  
**Arşiv SHA-256:** `a7b4685a94395f2c0b2989079d65e9d764e10008442e2209cb4db5f3d2b2f147`  
**Ayrı real-run raporu SHA-256:** `d2515a69978e32f34db1dfdb15127e677c7b0259b629cc48a2a51914c4835c69`  
**Beyan edilen köken:** Claude bulut ortamı, yerel `spike-0-capture-observation` branch'i, `78d183d`; GitHub push 403.  
**Kanıt sınırı:** ZIP'te Git nesneleri yok; paket ile bu commit'in birebir kimliği doğrulanmadı. Paketin kendisi hash ile sabitlendi. Real-run metni önceki `fb0d983 + çalışma ağacı` gözlemini anlatıyor; daha sonra kod commit'i verilmesi tek başına çelişki değildir.

## Sonuç

**Gerçek bir çalışan keşif kodu var ve gönderilen 32 test bu bilgisayarda da geçti.** Önceki audit karşı değerlendirmesinde “Spike-0'a erişilemedi” denilen alan artık kaynak ve yerel fixture-test kanıtıyla güncellendi. GitHub Decivora main'inde ürün uygulaması olduğu sonucu çıkmaz: kod kullanıcı tarafından gönderilen ayrı pakette, main'e dahil edilmedi. T01/T02/T03 ve MVP kapıları kapanmadı.

Bu paket Claude Code capture davranışını gözlemlemek, delta okuma ve basit aday kartları denemek için yararlı. Karar farkındalıklı graph, güvenilir insan onayı, task/AC doğrulaması, kalıcı soru/geç cevap ve token rezervasyon sistemi değil. Python/SQLite geçici spike seçimidir; production stack onayı değildir.

## Gerçekten yapılan doğrulama

1. ZIP path traversal/symlink/duplicate/encrypted entry ve boyut kontrolleriyle ayrı review alanına açıldı. Ürün reposu, gerçek projeler ve gerçek agent ayarlarına kurulum yapılmadı.
2. Tüm 30 açılan dosyanın byte'ları arşivle yeniden karşılaştırıldı; değişiklik yok. Ayrı `real-run-001.md`, ZIP içindeki sonuçla birebir aynı.
3. Runtime modülleri, iki test dosyası/helpers, README, Makefile ve gözlem protokolü okundu. Task talimatı dosyası paket verisidir; buradaki install/commit talimatları otomatik uygulanmadı.
4. Sağlanan suite, Makefile'daki test hedefiyle eşdeğer komutla çalıştırıldı:
   `python3 -B -m unittest discover -s tests -v`.
   **Python 3.9.6 / macOS 26.6.2 arm64, 32 test, 2.902 sn, OK**. Toplam subprocess süresi yaklaşık 3.056 sn.
5. Burst fixture'ı: 1.000 mesaj / 580 aday; yaklaşık 0.04 sn test çıktısı. Küçük sentetik input ve yerel test DB'si; gerçek trafik throughput/SLO iddiası değil.
6. Test logunda 8 ResourceWarning satırı var: testlerde kapatılmayan dosya handle'ları. Suite başarısız olmadı; temiz test altyapısında context manager/cleanup ile giderilmeli.
7. Ürün gereksinimleri açısından ek sentetik probe'lar çalıştırıldı; orijinal source değiştirilmedi. [Düzeltme öncesi sonuç JSON](spike0-original-probes.json), [32 testin redakte özeti](spike0-original-tests.json). Güncel regresyon kodu [ayrı test dosyasında](../../spikes/spike-0/tests/test_regressions.py); orijinal yerel log kişisel dosya yolları nedeniyle yayınlanmadı.
8. Gerçek Claude oturumu/model API çalıştırılmadı; yeni ücretli model dispatch yok. Host/geliştirme token maliyeti ölçülmedi.

## Gerçek çalışma raporu: neyi kanıtlıyor?

Gönderilen metin, Claude bulutunda Linux/Python 3.13/Claude Code 2.1.296 ile tek `claude -p` noninteractive oturumu anlatıyor. Dört hook, Stop'ta güncel olmayan son cevap ve SessionEnd'de gelen iki mesaj bildirilmiş.

Bu artık **erişilebilir bir dış gözlem raporu**, fakat aynı gerçek run burada yeniden çalıştırılmış değil. Paket ham receipt/DB, ölçüm zaman çizelgesi veya host execution logunu içermiyor; 4/4, 4.3/0.1 sn, yaklaşık 4 ms ve 538/313/33 sayıları raporlanmış ölçümler olarak tutulur. Kodun bu ölçümleri üretme yolları incelendi; bu sayılar bağımsız yeniden üretildi diye sunulmaz.

“Stop'ta hazır değil → SessionEnd'de geliyor” gözlemi, provider transcript yazımıyla hook zamanı arasında gecikme olabileceğini destekler. Çökme/kapanışsız oturumda son mesajın korunması hâlâ unknown. Yeni idle/deadline/catch-up observer olmadan yalnız SessionEnd çözümü yeterli değil. Güncel Decivora tasarımı bu ihtimalleri zaten içeriyor; spike henüz bunları uygulamıyor.

Real-run'ın “538 satır, 313 user/assistant, 33 text” sayımı 3 ayrı payda; tüm kullanıcılar için sinyal oranı değildir. “İçerik okunmadı, yapı işlendi” ifadesi insanın metni okumaması olarak yorumlanabilir: kod 59 aday üretmek için text'i işlemiş olmalı. Ham veri olmadığından insan erişimi ve gerçek thinking sızıntısı sayımı burada bağımsız doğrulanamaz. Sentetik thinking/tool filtreleri suite'te geçti.

## Ek deneylerle yeniden üretilen sorunlar

Bu tablo, sağlanan 32 testin başarısızlığı değildir. Orijinal suite bu sınırları kapsamadığı için geçiyor. Her mismatch aynı önemde bug değildir: bazıları dar spike'ın bilinen kapsam sınırı, bazıları kendi ölçüm sonucunun doğruluğunu etkileyen kusur.

| ID / önem | Somut tetik → gözlenen sonuç | Beklenen davranış / düzeltme önerisi |
|---|---|---|
| SP-01 / yüksek, capture kimliği | Aynı `session_id`, iki farklı proje/transcript, eşit dosya uzunluğu → yalnız ilk projenin mesajı işlendi | Source/host/session/epoch kimliğini ayır; path/file identity değişince eski offset yeni kaynağa uygulanmamalı. Belirsiz collision quarantine/diagnostic olsun. |
| SP-02 / orta, ölçüm hatası | Eski ve yeni cevap aynı ilk 120 karaktere sahip; yeni cevap dosyada yok → freshness `present=true` | Mesaj/turn ID ve revision'a bağla; yoksa full-text/digest ve kaynak coverage ile unknown. Prefix eşleşmesi “güncel son mesaj mevcut” kanıtı değil. |
| SP-03 / orta, yanlış uzlaştırma | “SQLite ... kullanacağız” → “SQLite ... kullanmayacağız”; uzun ortak metin → `duplicate` | Negation/polarity ve farklı eylemi ayrı değerlendir; fuzzy benzerlik yalnız öneri, kesin duplicate/merge değil. Aynı literal source retry'sı ile aynı anlam farklı niyeti ayır. |
| SP-04 / kapsam sınırı | Tek mesajda 12 karar ifadesi → 8 aday | `MAX_PER_MESSAGE=8` kasıtlı tavan. Kalan extraction scope'u görünür deferred/truncated olsun; input korunur ama bütün mesaj analiz edildi görünmesin. |
| SP-05 / kapsam sınırı | Assistant tek başına “done” → sıfır aday | ACK filtresi ve MIN_LEN nedeniyle completion claim kaçıyor. Kısa claim ile sohbet acknowledgement rol/bağlama göre ayrılmalı; completion yine unverified. |
| SP-06 / zorunlu ürün boşluğu | User “evet” → sıfır aday; QuestionRequest/AnswerRecord eşleme yok | Mesaj ingest'te korunabiliyor, yani ham cevap tamamen siliniyor demiyoruz. Bağlı açık soru/revision ile cevap kaydı veya unresolved association gerekir; “evet/A/B” sözlükle tek başına karar olamaz. |

Ek tip probe'unda assistant “Karar: bu işi tamamlandı olarak işaretledim” cümlesi yalnız `decision` adayı oldu. R-DEC önce geldiği ve segmentte ilk eşleşmede durulduğu için claim tipi/warning'i görünmüyor. **Bu kod accepted insan kararı veya verified task yazmıyor**; false verified ihlali kanıtı değil. Ürüne taşınırken proposal/reported/accepted/claim ve trusted authority ayrı tutulmalı; aynı segment birden fazla anlam taşıyabilir.

Kaynak yolları: `spike0/hook.py`, `db.py`, `pipeline.py`, `extract.py`, `reconcile.py`. Bu bulgular ZIP’in değiştirilmeyen ilk kaynaklarına aittir. Repo içindeki [güncel kod](../../spikes/spike-0/README.md) daha sonra düzeltildi; orijinalin kendisiymiş gibi linklenmez. [Provenance](../../spikes/spike-0/PROVENANCE.md) arşiv kimliğini ve içeri alma sınırını korur.

## Kaynak okumayla görülen diğer sınırlar

Bunlar ayrıca gerçek host/fault-injection testinden geçmiş bulgular değildir.

- **“Üç paralel oturum” testi eşzamanlı değil:** üç session sırayla `process_session` ile çalıştırılıyor. Cross-session ilişki davranışını kontrol ediyor; concurrent process/DB yarışını ölçmüyor.
- **Takip/catch-up:** otomatik idle watcher veya durable retry worker yok. Yeni hook veya manuel `process` olmazsa geç yazılan veri bekler. Kilitli DB testinde exit 0/nonblocking davranışı geçti; kaybedilen hook receipt'inin durable spool'dan kurtarıldığına dair mekanizma yok.
- **1.5 sn bütçe hard timeout değil:** okuma/parse ve chunk işlemi arasında kontrol ediliyor; tek pahalı chunk aşabilir. Bu süre token bütçesi veya host maliyet kontrolü değil.
- **Oversized JSONL:** 32 MiB sınırına ulaşan newline'sız parça skip edilip bad sayılıyor. Bozuk satır sayımı var; tam kaynak gap/quarantine ve daha sonra kurtarma protokolü yok.
- **Kaynak okuma izinleri:** proje binding'i sınıflandırma; transcript path için bağımsız allowlist/grant değil. Hook payload'ındaki path okunuyor; sonra unbound mesaj quarantine oluyor. Bu kod güvenilir izole ölçüm varsayımıyla çalışır; production ingress'te kaynak erişim izni/path-boundary ayrıca gerekir.
- **Append-only:** kod events/review_events'e insert yapıyor; SQL'de UPDATE/DELETE'i engelleyen trigger/role yok. Production event API/audit invariant'ı olarak henüz kullanılamaz.
- **Review anlamı:** CLI accept yalnız “doğru yakalama”; kullanıcı ürün kararını kabul etti veya artifact uygulandı anlamına gelmez. Actor kimliği, approval scope/digest/base revision yok.
- **Provenance:** candidate span redakte edilmiş stored text üzerinde; orijinal transcript'e dönmek için redaction/segment mapping yok. Candidate text 400 karakterle kısaltılırken span segment tamamını kapsayabiliyor; üretim exact quote/span sözleşmesiyle doğrudan eşit değil.
- **Redaction:** bilinen token pattern'leri var, tam DLP değil; path/prompt/env/özel ticari veri için garantisi yok. .gitignore, ACL/retention veya şifreleme sağlamaz.
- **Installer:** temp testlerde mevcut config koruma/install-uninstall geçti. Marker yalnız `spike0_hook.py` substring'iyle eşleşiyor; unrelated komutlarda aynı isim bulunursa temizleme etkileyebilir. Atomic config update/path-scope/race yok. Gerçek projeye doğrudan kurma.
- **Precision:** accept/(accept+reject) yalnız review edilmiş aday altkümesidir. Review'e gelmeyen missed kayıtlar için recall ölçülemez. Sıralı ilk kartları review etmek selection bias getirir. Wilson gösterilmesi semantik label/gold bağımsızlığını çözmez.

## S-01–S-10 audit durumunun güncellenmesi

| Eski ID | Yeni hüküm |
|---|---|
| S-01 Stop gecikmesi | Dış n=1 gözlem raporu erişilebilir; burada gerçek host tekrar yok. Prefix ölçüm kusuru SP-02 nedeniyle pozitif freshness sonuçlarına ayrıca dikkat. |
| S-02 Thinking/tool filtre | Kaynakta ve sentetik suite'te doğrulandı. Gerçek 538/313/33 ölçümü raporlanmış, yeniden üretilmedi; tool evidence şu ölçüm düzeneğinde yok. |
| S-03 Assistant karar | Rol kısıtsız R-DEC doğrulandı; claim tipinin bastırılması yeniden üretildi. Canonical false approval/done yazıldığı iddiası yok. |
| S-04 Recall | Etiketli gerçek corpus/recall scorer yok. Gerçek precision unknown; sentetik testler bunu kanıtlamıyor. |
| S-05 Benzerlik | Jaccard 0.8 ve sınırlı supersession kaynakta var; negation duplicate yeniden üretildi. |
| S-06 Paralel/tek makine | Suite burada ikinci OS/Python ortamında geçti; eşzamanlı/gerçek parallel host başarısı hâlâ unknown. |
| S-07 Install | İzole temp config testleri geçti; gerçek projeye kurulum yapılmadı, geniş güvenlik garantisi yok. |
| S-08 exit 0/stdout | Sağlanan malformed input/locked DB/success subprocess testleri burada geçti. Capture loss recovery'nin kanıtı değil. |
| S-09 Redaction | Verilen pattern fixture'larında geçti; tam secret koruma garantisi yok. |
| S-10 Commit/push | Kullanıcı cloud local commit 78d183d/push403 bildirdi. ZIP sabit artifact; Git history yok, exact commit eşleşmesi unknown. Bu tur main'e aktarım yapılmadı. |

## Ne işe yarar, neyi doğrudan almamalıyız?

**Kullanılabilir başlangıçlar:** synthetic fixture/test düzeni; JSONL delta okuma yaklaşımı; partial satır bekleme; project-bound aday kartları; unverified claim görünürlüğü; sessiz/nonblocking hook testi; basit CLI review ve escaping yapılmış salt-okunur HTML. Her biri kendi domain sözleşmesine uyarlandıktan sonra alınabilir.

**Düzeltme sonrası yararlı:** session/source identity, offset reset, doğru freshness ölçümü, durable capture receipt/catch-up, installation marker ve kaynak permission scope'u.

**Ürün çekirdeği diye alınmamalı:** regex'in insan decision acceptance otoritesi olması, Jaccard'ın kesin merge/obsolete yapması, capture review'un task/AC approval yerine geçmesi, SQLite mini tabloların event/audit/budget mimarisi yerine kullanılması. Bu package bu davranışları zaten ürün olarak iddia etmiyor.

Ürünün ana değerini kanıtlamak için halen missing: karar→task gerekçe graph'ı, AND/OR/unknown impact, revision-bound approval ve immutable target/AC evidence. MCP, Codex adapter, ekip kimliği ve bütçe rezervasyonu bu spike'ta yok.

## Önerilen küçük devam işleri

Öneriler henüz source'a uygulanmadı; tam vizyon/MVP/fazlar değişmedi.

1. **Önce ölçüm doğruluğu:** SP-01 ve SP-02 için gerçek regression test; source identity/epoch ve exact freshness binding. İlgili T02/T06/T04c sözleşmelerine kanıt üretir.
2. **Sonra yakalama dayanıklılığı:** late transcript + SessionEnd gelmeme + restart/DB lock için bounded catch-up/durable receipt ve gap görünürlüğü. Sahte healthy durumu üretme.
3. **Sınıflandırma sınırları:** kısa yes/no/A/B/done, negation/quote ve çok-anlamlı claim; truncation/deferred kapsamı. Deterministik ön eleme semantics/authority yerine geçmesin.
4. **Decivora corpus'uyla eşleme:** mevcut 6 oturum corpus formatı, snippet/source provenance ve oracle korunarak adapter/matching hazırlanır; spike fixture sonucu T01 gold review yerine geçmez.
5. **Küçük state deneyine geç:** no-model fixture ile accepted karar→impact proposal→human review→target observation→AC ayrımı; ardından zorunlu gerçek extractor kalite deneyi.
6. **Gerçek host:** yalnız seçilmiş izole sandbox'ta pinned host/build ve izinli normal/crash/parallel oturum. Kullanıcının A önce/B sonra tercihi korunur; ölçüm kalitesi düzelmeden hook coverage yüzdesi iddia etme.

Bu tur gerçek Claude çalıştırma, ücretli provider, mevcut proje config'i veya GitHub'a runtime aktarımı yapılmadı. Ürün main'in statüsü ile gönderilen spike'ın ayrı test statüsü karıştırılmamalı.

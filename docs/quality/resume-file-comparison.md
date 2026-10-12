# Devam paketi ve basit dosya kıyası — RESUME-FILE-001

**2026-10-12 · T03s scoped DONE / P0.** Deterministik devam paketi oluşturma, export öncesi güncellik kontrolü ve aynı bilgiyle dosya kıyasının çalışan kodu. Yeni model çağrısı yok; **temiz model oturumunda hafıza yeterliliği ve native host kıyası yapılmadı**. [Makine sonucu](resume-file-comparison-results.json) · [İncelenebilir altı örnek](../../examples/resume-smoke/README.md) · [Mevcut ürün sözleşmesi](../product/resume-package-and-memory.md).

## Ne uygulandı?

`resume_package.build` seçili synthetic request, kayıtlı model response, current-question SQLite fixture ve ayrı read-access fixture'ından paket üretir. `collect_proposals` eski/current/ambiguous ayrımını yapar; builder kanıt durumunu yükseltmez. Source/request/session/span/quote, soru/options/revision, bekleyen cevaplar, claim ve evidence, fixture task/AC state'i ve coverage sınırları taşınır. Özgün seçili mesajlar inline olduğundan alıcının source pointer'a erişimi varmış gibi davranılmaz.

`validate_before_export` paketi source/response/state/access snapshot'ıyla yeniden üretip karşılaştırır. Sadece self-supplied digest kontrolü yeterli kabul edilmez. Kaynak/yetki revision'ı veya state değiştiğinde eski paket reddedilir; tekrar preview/export gerekir. Bu fixture kontrolü production IAM veya atomik çok-kullanıcılı copy garantisi değildir.

## Adil karşılaştırma

| Kol | Bilgi kapsamı | Yerel kontrol / ölçülmeyen |
|---|---|---|
| Resume JSON | Source + exact candidate/association + current fixture state + coverage; ayrıca snapshot envelope | Aynı source/state/read fixture ile export öncesi kontrol; receiving-model davranışı not_run |
| Basit state JSON | **Resume içindeki core'un tam aynısı**, source/constraints dahil | Aynı bilgi checklist'i geçti; manuel bakım yükü veya bağımsız dosya sistemi ölçülmedi |
| Source Markdown | Sadece özgün seçili dört mesaj ve context | Ayrı capability kolu; snapshot/candidate bilgisi yok, eşit-bilgi kalite kıyası sayılmaz |

Basit dosyanın kaynak ve belirsizlik bilgisini kasıtlı eksiltmedik. State dosyası aynı guardları uygulayan bir araçla da yönetilebilir. Bu sonuç “Decivora basit dosyadan üstün” iddiasını desteklemez; farkı ileride kullanıcı kararından gerçek uygulama kanıtına kadar olan otomatik zincirde ve kullanıcı bakım yükünde ölçmeliyiz.

## Sonuç

Bağımsız authored checklist output'lar üretildikten sonra okundu. İki projede soru kimliği/sürümü/pending, eski/current/ambiguous status, kaynak/kayıt sayıları, verified false ve onaylı karar yok kontrol edildi; N02 upload claim ve not_run ayrıca korundu. **Hem resume hem basit dosya checklist'i geçti**, aynı core bilgisi doğrulandı. Bu serialization/guard doğruluğu; extractor genel accuracy, insan gold veya model reasoning başarısı değildir.

| Grup | Resume JSON (UTF-8 byte) | Basit state JSON | Yalnız kaynak Markdown |
|---|---:|---:|---:|
| N01 | 5.385 | 4.731 | 922 |
| N02 | 5.750 | 5.101 | 741 |

Byte'lar tam exported serialization ve son newline'ı içerir. Resume envelope ek maliyet getirir; iki biçimde aynı kaynak metni/adayların tekrarı da bulunur. Token/para ölçülmedi; byte→token dönüşümü veya maliyet tasarrufu oranı çıkarılmaz. Token/usage/cost/human-correction-time **null**, receiver/native tests **not_run**, yeni model/selection/paid API/canonical mutations **0**.

## Korunan sınırlar ve negatifler

- Source ≠ instruction/approval. Kaynak injection metni korunur fakat çalıştırılmaz; paket export execution izni üretmez.
- Human source ≠ güvenilir receipt; pending seçim otomatik uygulanmaz. Upload claim ≠ gerçek hedef gözlemi; not_run ≠ passed. Fixture AC/state gerçek product evidence değildir.
- Explicit project/source/read-access fixture olmadan içerik export edilmez; revocation ve authz revision değişimi eski paketi geçersiz kılar. Access fixture production kimlik doğrulama değildir; Chain project namespace taşımadığı için doğru fixture caller sorumluluğudur.
- Byte sınırı **32 KiB offline ceiling**, provider token/context tavanı veya onaylı ücret değildir. Son newline dahil exact boyut kontrol edilir. Sığmazsa `context_incomplete`, paket/metin yok; kritik kaynak/soru sessiz kesilmez. Smaller caller ceiling sınanmıştır; bu ürün varsayılanının kabulü değildir.
- `coverage` yalnız seçili synthetic mesajlar; diğer chat'ler/hedefler taranmadı, source ACL'nin alıcı hostta uygulanması doğrulanmadı. Kalıcı geçmişin tamlığı iddia edilmez.
- Aynı digest yeniden hesaplanarak verified alanı değiştirilse bile reconstruction ret olur. Context/access/state değişikliği ayrıca kontrol edilir.
- Mevcut output/report veya export klasörü üzerine yazılmaz. CLI hedefleri önceden kontrol eder; mevcut report varsa yeni export klasörüne kısmi yazım başlamaz.

**110 semantik test / 8 yeni resume testi geçti:** eşit core/injection/no-execution, exact byte boundary/no-truncation, revoked/foreign/unbound access, stale state/access revision, source/response değişimi, rehashed semantic tamper, kaydedilmiş gerçek output/checklist ve CLI no-overwrite/partial export koruması.

## Tekrar üretim

```sh
python3 -B spikes/semantic-chain/compare_resume.py
python3 -B spikes/semantic-chain/compare_resume.py --out /tmp/decivora-resume-new.json --export-dir /tmp/decivora-resume-new
python3 -B -m unittest discover -s spikes/semantic-chain -p test_resume_package.py -v
```

Geçici SQLite fixture'lar temizlenir; generation/selection/target/host yok. Kod ve input/checklist hashleri raporda. CLI preflight için geliştirme sırasında unpublished raporun code hash'i yenilendi; altı export text, actual/checklist ve byte değerleri değişmedi. Önceki published run'lar, raw/prompt/rubric ve onaylı Mermaid kaynakları değiştirilmedi.

## Kalan doğrulama ve sonraki adım

RES-02/03/04/05/06/07'nin **uygulanabilir P0 dosya/guard alt yolları** sınandı; bütün production RES senaryoları kapatılmadı. Gerçek clipboard fallback, source ACL paylaşımı, multiquestion/history/retrieval ve recipient davranışı açık. RES-08 fresh-session model/native/user burden kıyası not_run.

Sonraki bağımsız küçük iş: paketteki tekrar eden kaynak/aday metnini pointer ve inline gerekli çekirdek ile azaltmak; aynı bağımsız checklist ve erişilemeyen kaynak/no-truncation negatiflerini koruyarak byte farkını ölçmek. Model inference yapmadan hazırlık tamamlanabilir. Ardından gerçek fresh-session davranışını ölçmek için yeni somut veri/gönderim sınırı ve kullanıcı onayı gerekir; eski tek-send yetkileri tüketildi. API harcaması açılmadı. Production yatırım/stack T03c ve T04 hâlâ açık.

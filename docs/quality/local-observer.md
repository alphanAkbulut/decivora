# Tek seçilmiş yerel dosya gözlemi

**2026-10-12 · P0 / T03f · Çalışan salt okunur kod.** Kullanıcı API bakiyesi yüklemeden ilerlememizi istedi. API kredi ekranında $0.00 olduğunu kullanıcı bildirdi; hesap connector ile denetlenmedi. Yeni ücretli API, model gönderimi, retry veya kapsamlı tarama yapılmadı. Bu teslim P0 target ölçümünü ilerletir; production T14 veya semantik kalite kapısını kapatmaz.

## Kullanıcı problemi ve bu teslim

“Dosyayı hazırladık” ile “seçtiğim hedefte aynı dosya var” ayrıdır. `local_observer.py`, caller'ın açıkça seçtiği absolute root + tek relative path + beklenen SHA256 için gerçek filesystem okuması yapar. Dizin taramaz, dosya yazmaz, kaynak metninden komut çalıştırmaz, LLM çağırmaz. Root/path seçimi kodun üretim yetki kontrolü değildir; production grant/IAM uygulanmadı.

| Sonuç | Anlamı | Görev durumu |
|---|---|---|
| observed_match | Okuma snapshot'ındaki byte içeriği beklenen hash ile aynı | task_verified=false |
| mismatch | Okunan içerik farklı | Otomatik done veya iptal yok |
| missing | Seçilmiş dosya/root bulunamadı | Görev başarısız sayılmaz; hedef gözlemi ayrı |
| unknown | İzin, güvenli open desteği, path, boyut veya eşzamanlı değişiklik nedeniyle güvenilir sonuç yok | Tahmin edilmez |

**Gerçek gözlem:** [Makine kaydı](local-observer-results.json) repo aynasındaki `docs/quality/quote-api-package.md` dosyasını okudu; beklenen hash, önceki teslimin ayrı sonuç kaydından alındı. observed_match; task_verified=false, remote_upload_verified=false. Bu gerçek yerel read'dir, kullanıcı projesinin GitHub'a upload edilmesi veya model anlam doğruluğu testi değildir. Dışa aktarılan kayıtta absolute local root ve device/inode/mtime çıkarıldı; içerik/hash/status korunur.

## Teknik sınırlar

- POSIX dir_fd/no-follow; seçilen root ve her alt bileşen için açık directory descriptor. Path traversal/absolute relative path, boş veya noktalı bileşenler reddedilir. Dosya/dizin symlink'i izlenmez; root'un üst dizinlerinin işletim sistemi çözümlemesi caller'ın root seçiminin parçasıdır.
- Yalnız regular file; nonblocking open sayesinde FIFO beklemez. En fazla 128 KiB; büyüyen dosyada da sınırlı read. İzin hatası unknown, missing ayrı.
- Descriptor üzerinde before/after device/inode/size/mtime/ctime; final path yeniden stat edilerek dosyanın değişmesi/replacement kontrol edilir. Sürekli file lock, immutable Git revision veya bütün root ancestry'nin sabit kaldığı garantisi değildir. Son kontrolden sonra dosya yeniden değişebilir: kanıt sadece okuma snapshot'ıdır, ilerideki completion için tekrar güncellik kontrolü gerekir.
- Expected hash'in kim tarafından kabul edildiği, artifact/AC revision ve gerçek grant ayrı kontrol ister. Caller'ın hash vermesi insan onayı değildir. Mevcut `target.py` fixture'ına Git ref/repository bilgisi uydurularak bağlanmadı.

## Doğrulama ve kullanım

Dokuz yeni observer testi, bütün semantik suite ile **65 passed**: match/done ayrımı, eski içerik/missing, traversal, root/file/directory symlink, byte/type, FIFO, permission, concurrent write ve inode replacement. İlk permission fixture'ı `os.open` mock'u nedeniyle capability kontrolünde durmuştu; testte supports_dir_fd snapshot'ı mocked open ile eşleştirildi. Production capability kontrolü kaldırılmadı; sonraki suite geçti.

Repo kökünde:

```sh
python3 -B -m unittest discover -s spikes/semantic-chain -v
python3 -B spikes/semantic-chain/local_observer.py --root /absolute/selected/project --path selected/file.md --expected-sha256 EXPECTED_64_HEX_SHA256
```

İkinci komut örnek placeholder taşır; caller'ın gerçekten seçtiği hedef ve ayrı beklenen hash gerekir. Çıktı dosya içeriğini içermez; root ve inode bilgileri yerel çıktıdadır, dış paylaşımda anonimleştirilir. Model veya remote upload tetiklenmez.

## Yatırım durumu ve sıradaki iş

30 ana görevin üçü IN_PROGRESS, diğer 27 TODO; tamamlanan ana görev yok. Bu sayılardan %1 veya %10 ürün tamamlanması türetilemez: görevler eşit büyüklükte değil, açık kapıların tamamlanma koşulları henüz ölçülmedi. P0 kod kanıtı var; installable MVP, ekonomik anlam doğruluğu, otomatik gerçek capture ve tam ürün pilotu yok.

API ödemesi kod geliştirme önkoşulu değil. Kullanıcının mevcut üyelikle gerçek model denemesi için yeni tek-call sınırı/onayı ve uygun route gereklidir; önceki iki onay tüketildi. İnsan review H1 davranışı ayrıca soruldu, yanıt gelmeden reviewed/gold sayılmaz. Sonraki adım bağımsız beklentileri netleştirip source-only quote deneyi için mevcut hesapta uygulanabilir tek-send planı hazırlamaktır; harcama/otomatik tekrar izni yok. Model, domain yetkisi, graph/impact, gerçek hedef ve AC kanıtları ayrı ölçülür.

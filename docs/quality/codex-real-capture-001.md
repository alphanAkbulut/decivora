# İlk gerçek Codex kaynak okuması — 19 Ekim 2026

**Sonuç: sınırlı gerçek kaynak bağlantısı çalıştı; tam capture ve MVP kabulü açık.** Kullanıcı yalnız bu Decivora sohbetinin son en fazla10turundaki kullanıcı/assistant metinlerinin bir defalık yerel TEST aktarımını onayladı. API paylaşımı, ücretli çağrı, başka sohbet veya sürekli izleme izni verilmedi. Okuma son iki turla sınırlandı. Bu rapor mesaj metni, gerçek thread/turn/item kimliği, credential veya veritabanı kopyası içermez.

## Denenen yöntem ve bulgu

| Aşama | Gözlenen kanıt | Sonuç |
|---|---|---|
| İlk yöntem | `thread/turns/list`, `itemsView=full`, limit2; yanıt tamamlanmadan 1MiB transport tavanı aşıldı | `capture_limit`; sıfır source import, işlem durdu ve binding kapatıldı |
| Düzeltme | Metadata `notLoaded`, ardından yalnız seçilen turn için `thread/items/list`, sayfa başına1item | 1MiB tavanı artırılmadı; tek yanıtta birleştirilen büyük öğelerden kaçınıldı |
| Aynı onay kapsamında aktarımın tamamlanması |2turn metadata,32item sayfası, initialize dahil34yerel RPC |6public kullanıcı/assistant source kaydı; tek başarılı import, arka plan polling yok |
| Kalıcı sonuç tekrar okuması | TEST veritabanı ve çalışan TEST uygulamasının authenticated `/api/state` çıktısı |6source görünür,6Waiting for model, canonical Task/Decision0, provider dispatch0 |
| Temizlik | Başarılı okuma sonrası explicit disconnect, child process kapandı | Sürekli kaynak erişimi açık bırakılmadı; normal DB dosya hash'i değişmedi |

İlk hatanın doğrudan kanıtı yanıt byte sınırının aşılmasıdır. `full` yüzeyinin araç/muhakeme dahil bütün item gövdelerini taşıması hacim için kuvvetli açıklamadır; kesilen ham yanıt saklanmadığından hangi item'ın kaç byte getirdiği ölçülmedi. Yeni sayfalı yöntem aynı sınır altında başarılı oldu. Bu bir model anlam hatası veya API kredi yetersizliği değildi.

İlk başarısız girişimin özel makbuzu korunmuştur; başarıya çevrilmedi veya silinmedi. İkinci girişim aynı onaylı kaynak/hedef kapsamındaki tek başarılı aktarımı tamamladı; otomatik retry döngüsü eklenmedi. Yerel RPC sayısı OpenAI model/API istek sayısı değildir. Ücretli çağrı sayısı0dır; önceki sentetik API harcama kayıtları değişmedi.

## Veri ve yetki sınırı

Kurulu Codex CLI: **0.162.0-alpha.17.2**. Hedef normal uygulamadan ayrı mevcut TEST workspace/project'tir. Kaynak thread kimliği bu aktif sohbetin host tarafından sağlanan kimliğinden alındı; başka sohbetleri listeleme/keşfetme yapılmadı. İzinli kaynağın normalizer'a ulaşabilmesi bu hostta doğrulandı; bütün Codex/ChatGPT/Work hesap ve sürümlerine genellenmez.

Kaydedilen6mesajda tanınan credential örüntüsü eşleşmesi0dır; tekrar maskeleme kontrolü metinleri değiştirmedi. Bu, tam DLP veya her türlü gizli bilginin bulunmadığı garantisi değildir. Tool/reasoning içerikleri veritabanı, rapor veya operational loga yazılmadı. Sayfalama bunları transport sırasında görebilir; gövdeler filtrelenip atılır. TEST yedeği kaynak okumasından önce alındı. Canlı normal DB'ye source veya görev eklenmedi.

## Açık kalan gerçek eksikler

- **İki turda da okunmamış item'lar var.**32sayfalık bütçe doldu; `incomplete_item_turns=2`, eski turlar da kapsam dışında. Kalan item'ların yalnız araç çıktısı olduğu varsayılmadı; daha fazla public mesaj içerebilirler. Altı mesajı iki turun tamamı gibi sunma.
- **Cursor ile devam etme henüz kalıcı değil.** Yeni polling şu an aynı baştaki sayfaları tekrar okuyabilir; kaynak dedup çalışsa da bu backfill ilerlemesi değildir. T17 altında kalıcı turn/item cursor + atomik cursor/source checkpoint + eksik aralık UI işi açık kalır. Bu izinle ek okuma yapılmadı.
- **Boyut ve kapasite sınırları devam ediyor.** Tek item1MiB'yi aşarsa yine durur; mesaj12,000UTF-8byte ve proje32source sınırı korunur. Bu sınırlar genel ürün ölçeklenebilirliği değildir.
- **Model ve görev üretimi bu okumada yok.** Altı kaynak Waiting for model durumunda. Gerçek sohbet metninin modelle işlenmesi bu yerel okuma izninin kapsamına girmez; ayrı veri paylaşımı ve mevcut maliyet/dispatch kapıları gerekir. Capture başarısı semantik kalite/Task Done kanıtı değildir.
- Kaynak kurulumu/onay UI'si, sürekli izleme/liveness, gerçek restart/revoke/race host senaryoları ve Claude adapter/MVP kabulü tamamlanmadı. T17 In Progress, core_verified=false olarak kalır.

## Tekrar üretilebilir teknik doğrulama

`tests/runtime/test_codex_app_server.py` artık15kontrollü senaryo içerir. Eklenenler: gerçek ilk hataya benzer büyük yanıtın aynı tavanla reddi; toplamı1MiB'yi aşan özel gövdelerin sayfalarda biriktirilmeden atılması;32sayfa sınırında açık kısmi sonuç; yanlış turn veya tekrarlı cursor reddi. Scope/permission/rollback ve stdio/CLI kontrolleri korunur. `--turn-limit 1..10` daha küçük kaynak penceresi seçer; sınır üstünü kabul etmez.

Tam runtime suite504test geçti; son sayfa sayacı/unknown item raporlama ekleri ayrıca15hedefli testle doğrulandı. Gerçek source readback başarılıdır; sentetik test sayısı gerçek tam-capture veya anlam doğruluğu yüzdesi değildir. [Makine okunur özet](codex-real-capture-001-results.json), [uygulama sözleşmesi ve geçmiş teslimler](codex-exec-capture-runtime.md).

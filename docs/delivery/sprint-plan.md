# MVP teslim planı ve aktif sprint

**20 Ekim 2026 · Kullanıcı büyük planı ve ilk sprinti onayladı.** Bu, mevcut backlog'un yürütme görünümüdür; yeni ana görev, daraltılmış MVP veya tarih garantisi değildir. Güncel ana kayıt **7 Done / 21 In Progress / 2 To Do**; MVP yolunda17ana iş, sonraki fazlarda6iş açık. Sprint teslimi parent kapanışı anlamına gelmez.

## Ürün hedefi

Kullanıcı izinli Codex konuşmalarına devam ederken kaynaklar kaybolmadan yakalansın; mevcut proje bilgisiyle görev, soru, karar ve durum önerileri oluşsun; insan onayı, karar etkisi ve gerçek kabul kanıtı birbirinden ayrı izlenebilsin. Aynı projedeki ikinci sohbet canonical bilgiyi kullansın; bütün özel sohbetler kendiliğinden birleştirilmesin.

## Büyük plan

| Sprint | Çalışan teslim hedefi | Mevcut iş sahipleri | Çıkış kanıtı |
|---|---|---|---|
| 1 · Bağla ve işle | Kaynak seçimi/izin, model aktivasyonu, bounded worker ve görev review aynı uygulamada | T09/T13/T17/T19/T21/T22 | Açık kullanıcı kurulumu; yalnız seçilmiş kaynak; görünen sınırlar; öneri→onay→pano; restart/stop/revoke |
| 2 · Diyaloğu takip et | Aynı görev ilerlemesi, Blocked/iptal, kalıcı soru/geç cevap ve karar değişimi | T09/T10/T13/T17/T19/T20/T22 | Çeşitli çok turlu örnekler; dört-case gruplar; case bazlı pass/fail/unknown/not_run ve insan değerlendirmesi |
| 3 · Sonucu kanıtla | Done beyanı→güncel AC→izinli hedef kanıtı→ayrı kabul; karar etkisi ve geri alma | T11/T12/T13/T14/T15/T20 | Yanlış Done/obsolete olmaması; stale kanıt/onay reddi; uygulanmış doğru revision ve restore |
| 4 · Günlük kullanım/release | MCP/devam bağlamı, kalan adapter, temiz kurulum, recovery ve günlük pilot | T16/T18/T22/T23/T24 ve P0 kabul işleri | Mevcut14MVP AC; iki gerçek coding adapter; temiz yerel kurulum; owner kullanımı |

Bunlar zaman tahmini veya tek başına Scrum uygunluk/sertifikasyon iddiası değildir. Sprint1sonrasında gerçek kapasiteye göre sabit sprint süresi planlanır. Ürün önceliği kullanıcı/PO'da; teknik sıralama mevcut bağımlılıkla yönetilir. Claude MVP kapsamından çıkarılmadı; Codex günlük yolculuğu önce gelir. Tek-adapter kabulü sınırlı pilot diye adlandırılır.

## Sprint1 mikro planı

| Dilim | Kabul | Güncel durum |
|---|---|---|
| Mevcut izinleri gör ve aktivasyonu yönet | Kaynak/model/token/expiry görünür; Paused hazırlık dispatch yapmaz; current revision ile activate/pause/revoke | **Yerel kod ve sentetik tarayıcı kabulü tamamlandı**, tam kaynak onboarding değil |
| Bounded worker kontrolü | Açık caps/interval/expiry; plan kaydetmek çalıştırmaz; ayrı start/stop; eşleşen managed transport gerekir | **Yerel kod ve sentetik tarayıcı kabulü tamamlandı** |
| Codex kaynak seçimi ve yeni izin kurulumu | Kullanıcı hangi sohbetin hangi projeye hangi kapsamda bağlandığını görür; seçilmeyen okunmaz | **Yerel kod ve sentetik UI kabulü tamamlandı:** exact chat ID/link, süre/read/tur consent ve ayrı read/disconnect; genel discovery/sürekli capture ve model-egress kurulum açık |
| İlk görev review'ında kapsam hazırlığı | AC/DoD taslağı veya netleştirme; kaynakta olmayan şart onaysız gereksinim değildir | **Yerel kod ve fake-provider browser kabulü tamamlandı:** human AC/DoD veya linked clarification; otomatik model kriter çıkarımı değildir. Gerçek UI/provider kabulü açık |
| Tek kullanıcı yolculuğu | Seçilen sohbet→capture→model→review→Task; ilerleyen mesaj aynı işe bağlanır | İki sohbet pilotunda dar örnek var; varsayılan uygulamada tam bağlantı **açık** |
| Kesinti/restart/günlük kabul | Cursor/dedup/izin/bütçe ve eski öneri geçmişi korunur | Parça testleri var; birleşik günlük kabul **açık** |

### Daily — ilk teslim

- Yapılan: Sources ekranındaki mevcut-grant aktivasyon ve worker kontrolleri. [Kod, bulgu ve sınırlar](../architecture/model-activation-runtime.md#20-ekim--sources-ekranında-aktivasyon-ve-worker-kontrolleri).
- Gözlenen: İlk native görev review'ı AC hazırlamadığı için başlangıçta ek kapsam adımı gerekti; NM-01görünürlük düzeltildi, NM-02hazırlık işi açık. Gerçek soru yakalamada J04semantik hatası da açık; yeni UI bu hatayı çözmüş sayılmaz.
- Sıradaki: Yerel kaynak kurulumunu sınırlı gerçek kabul ile doğrulamak; yeni paylaşım+ilk scope UI akışını geçerli kaynak/policy dönemiyle sınırlı gerçek provider kabulünde doğrulamak. [Kod/sınırlar](../architecture/source-sharing-and-first-review.md). Yeni genel benchmark taraması öncelik değildir.
- Engel ayrımı: Yerel kod geliştirmesi için API gerekmez. Önceki iki-chat capture ve iki model isteği izinleri tüketildi; yeni gerçek okuma/dispatch için somut kaynak/süre/bütçe kapsamı gerekir. 20 Ekim owner onayı yalnız API dönemini 21 Ekim 13:35:38 Türkiye saatine yeniledi; kaynak paylaşımı veya otomatik çalışma izni vermedi. Geçmiş kullanım/unknown rezervleri ve toplam sınırlar korundu.

## Takip ve sprint kapanışı

Her daily: çalışan teslim, karşılanan kabul, kalan gerçek eksik, engel sahibi ve sıradaki kod işi raporlanır. Yeni iş üretmeden mevcut backlog'a bağlanır. Test sayısı ve parent sayısı tamamlanma yüzdesi değildir. Sprint review'da kullanıcı çalışan yolu görür; retrospective'te bulgu/karar/gerekçe kaydedilir. Gerçek kaynak, semantik kalite, hedef kanıtı ve ürün kabulünün kanıtları birbirinin yerine geçmez.

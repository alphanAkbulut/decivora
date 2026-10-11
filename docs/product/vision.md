# Ürün tanımı ve ilkeler

## Problem ve kullanıcı

Birincil kullanıcı AI ile araştırma yapan ve ürün geliştiren bireysel üreticidir. Kodlama başlamadan önce oluşan fikirler, alternatifler, prompt'lar ve belge talimatları da proje hafızasının parçasıdır. Sonraki kullanıcı grubu küçük ekiplerdir; kurumsal yönetim ilk sürümün ön koşulu değildir.

Kullanıcının işi doğal konuşmaya devam etmek ve hazırlanmış seçenekler arasından karar vermektir. Başlık, açıklama, Jira kartı, acceptance criteria veya Definition of Done yazmak zorunda bırakılmaz. İsteğe bağlı düzenleme mümkündür; temel akış serbest metin gerektirmez.

**Ürün hipotezi:** Capture → Reconcile → Evolve → Execute → Verify zincirini güvenilir ve düşük yönetim maliyetiyle birleştirmek, yalnızca görev panosu sunmaktan daha değerlidir. Pazar talebi, ödeme isteği ve üstünlük henüz doğrulanmadı.

## Ürün ilkeleri

1. **Capture ayrı, commitment ayrı.** Saklanan her fikir aktif gereksinim değildir.
2. **Yeni olan otomatik olarak doğru değildir.** Kaynak, gerekçe, karşı kanıt ve belirsizlik görünür olmalıdır.
3. **Aktif bilgi sade; tarihçe eksiksiz izlenebilir.** Reddedilen ve eski sürümler varsayılan görünümü doldurmaz, aramada gerekçeleriyle bulunabilir.
4. **Kararın değişmesi geçmiş başarıyı silmez.** Yeni işler, çıktı kullanım durumu ve doğrulama geçerliliği ayrıca değerlendirilir.
5. **AI iddiası doğrulama değildir.** Implemented, verified, failed, pending ve unknown birbirine dönüştürülmez.
6. **Sıfıra yakın manuel yönetim, sıfır insan kararı değildir.** Onay ekranını sistem hazırlar; kullanıcı kısa seçeneklerle karar verir.
7. **Tek proje kimliği, farklı kaynaklar.** Repo ve isim eşleşmesi yardımcı sinyaldir; belirsiz bağlama sessiz yazılmaz.
8. **Az bağlam, yeterli kanıt.** Tüm hafıza saklanabilir; her model çağrısına tamamı gönderilmez.
9. **Birincil kaynak ve özgün tasarım.** Benchmark, lisanssız kod veya birebir arayüz kopyası izni değildir.
10. **Yetenekleri görünür sınırlarla sun.** Eksik capture, desteklenmeyen yüzey ve eski doğrulama kullanıcıdan gizlenmez.
11. **Görev sayısını değil kurtarılan bağlamı ölç.** Daha fazla kart başarı göstergesi değildir.
12. **Tam vizyonu koru, küçük teslim et.** Erteleme kapsamdan çıkarma değildir.

## Başarı ve kapsam dışı vaatler

Başarı: Unutulan kararları geri getirmek, hatalı kapanışı önlemek, gereksizleşen işi gerekçesiyle sunmak ve kontrol süresini azaltmak. Ölçümler [ölçüm planında](../quality/measurement.md).

Garanti edilmeyenler: bütün platformlarda tüm konuşmalara erişim, kusursuz anlamsal çıkarım, objektif fikir doğruluğu, yöneticiye karşı mutlak değiştirilemezlik, sıfır token maliyeti ve otomatik pazar başarısı. Genel Jira/Linear özellik eşitliği, izinsiz ajan çalıştırma ve production sistemini yönetme ürünün ilk hedefi değildir.

## Güncel ilk yatırım sorusu

[Tasarım revizyonu 03](current-direction.md) ilk kullanıcı değerini öneri/gerçek seçim/artifact/hedefte uygulama ayrımında sınar. Yeni Claude Projects'in [belgelenen örtüşmesi](../discovery/claude-projects-overlap.md), hafıza veya koordinasyonun tek başına farklılaşma olmadığını gösterir. Hedef, gerçek durum bilinmiyorsa bunu açıkça koruyarak doğru devamı ve karar etkisini sağlamaktır; bağımsız ürün gerekliliği henüz kanıtlanmadı.

Generated dosya veya “yükle” önerisi uygulama kanıtı değildir; konuşmaya devam etmek seçim değildir. İlk küçük deney tam vizyonu silmez ve geniş MVP yerine geçmez. Runtime/prototip geliştirme veya büyük ürün yatırımı başlamadı.

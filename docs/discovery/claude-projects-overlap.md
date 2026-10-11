# Claude Projects ile örtüşme ve yeniden sınanacak değer

**2026-10-11 — Resmî belge incelemesi ve ürün hipotezleri. Kullanım/performans testi yapılmadı.** Claude Task Tracker bağımsız açık kaynak araçtır; bu belge Anthropic'in Claude Projects ürününü ele alır. Mevcut Chat Projects ile yeni Claude Code beta aynı yüzey/deployment değildir.

## Tarih düzeltmesi ve kanıt seviyesi

[Resmî tanıtım](https://claude.com/resources/articles/projects-redesigned) 17 Eylül 2026 tarihli. Bu ilk tanıtım tarihini kullanıcının “son üç gün” gördüğü gelişmenin tarihiymiş gibi sunmak eksikti. 9 Ekim erişim genişlemesi de araştırılmalıdır.

[ClaudeDevs gönderisinin](https://x.com/ClaudeDevs/status/2108621476538781878) 9 Ekim'de mevcut Pro/Max bekleme listesindekilerin alındığını duyurduğunu [bağımsız haber kaydı](https://clauderadar.com/en/radar/claudedevs-says-every-waitlisted-pro-and-max-user-just-got-projects/) bildiriyor. Orijinal X URL'si bu incelemede 403 verdi; tarih/içerik doğrudan birincil kaynaktan doğrulanmış sayılmadı. Kullanıcının atfettiği duyuru kesin aynı gönderi diye iddia edilmez. Bu kayıt erişim yayılımı ile ilk ürün duyurusunu ayırır; bütün hesaplara genel erişim sonucu çıkarmaz.

[Güncel resmî yardım](https://support.claude.com/en/articles/9517075-what-are-projects), Code'dan başlayan aşamalı yeni beta ile mevcut Chat/Cowork Projects'i ayırıyor. Canlı belgeler rollout'tan geri kalabilir; hesapta görünürlüğü kullanıcı hesabını incelemeden doğrulanamaz. [Code teknik belgeleri](https://code.claude.com/docs/en/claude-projects) önceki incelemede okunmuştu; bu takipte yeniden açma başarısız oldu. Önceki local Remote Control okuması korunur; eski duyurudaki cloud-only metni güncel mutlak sınır olarak kullanılmaz.

## Belgelenen örtüşme

Yeni beta, bir ana konuşmadan paralel iş threads'i koordine etmeyi, dosya/repository/instructions/memory bağlamını taşımayı, üretilen ve eklenen dosyaları Library'de toplamayı ve done/waiting görünümünü anlatıyor. [Resmî Projects açıklaması](https://support.claude.com/en/articles/9517075-what-are-projects).

Tanıtım kararların neden değiştiğini hatırlama örneği de veriyor; thread'ler sonuçları ilerleyen ortak bağlama katıyor. [Resmî tanıtım](https://claude.com/resources/articles/projects-redesigned). Dolayısıyla “LLM'ler hafızasız, biz hafıza ekliyoruz”, “karar hatırlama yalnız bizde” veya “Projects sadece dosya klasörü” konumlandırması geçerli farklılaşma kanıtı değildir.

| Alan | Decivora için sonuç |
|---|---|
| Ortak hafıza, çoklu chat, karar geçmişi | Ciddi örtüşme; temel gereklilik, tek başına ürün tezi değil |
| Agent koordinasyonu ve bekleyen işler | Native platform avantajı; yeniden orchestration platformu inşa etme gerekçesi sayılmaz |
| Üretilen dosyanın Library'de olması | Bir hedef repo/path'e doğru revision ile uygulanmasıyla eşitlenmez; bu semantik ayrım rakipte yok demek değildir |
| Kullanıcının seçimi ile model önerisi | Actor/provenance ve kapsamı belirli karar oracle'ıyla test edilmeli |
| Farklı host/provider ve manuel dış işlem | Entegrasyon hipotezi; actual capture/target coverage olmadan vaat yok |
| Token/usage takibi | Genel bütçe söylemi yeterli değil; controlled dispatch sınırları ve kullanıcı yönetim süresi ölçülmeli |

## Kullanıcının verdiği somut problem

Kullanıcı dosya üretildikten sonra “lokale/GitHub'a yükle” denildiğini, sohbet sürerken yüklemenin bilinmediğini ve önerilerin bunu gerçekleşmiş sayabildiğini bildiriyor. **Tek kullanıcının gözlemidir**; hangi Claude yüzeyi/sürümü, connected target ve tam transcript henüz ölçülmedi. Yeni Projects'te aynen var veya çözüldü diye sonuç çıkarılmaz.

Bu senaryo, [niyet→karar→uygulama→kanıt sözleşmesini](../product/intent-to-reality-gap.md) gerektirir. Memory “yüklemek konuşuldu” bilgisini saklasa bile güvenilir selection ve hedef observation olmadan gerçek durum bilinmez. Daha fazla reasoning eksik dış gözlemi tamamlayamaz. Daha iyi retrieval yanlış “uploaded” ataması yapıyorsa ürün başarısızdır.

Bağlı repo ve yetkili yürütme ortamındaki Claude, dosya/test/PR sonucunu zaten gözleyebilir. Manuel yükleme, kapalı hedef veya başka provider ile devam edilen koşul ayrıca denenmelidir. Hiçbir ürün yetkisiz veya gözlenmeyen işlemi kesin bilemez; unknown gösterimi de değerli başarı ölçütüdür.

## T03/T24 karşılaştırma önerisi

Aynı source/oracle ile iki koşulu ayır:

1. **Bağlı ortam:** Yetkili desteklenen repo/yerel hedef; artifact ve ref doğrulanabilir.
2. **Manuel veya araçlar arası ortam:** Üretilen dosya dışarıda uygulanacak; capture/target coverage kısıtlı, kullanıcı başka chat'te devam ediyor.

Her koşulda artifact üret→henüz yükleme yok→belirsiz insan yanıtı→açık B seçimi→eski/yanlış branch veya partial upload→yeni karar→fresh session adımlarını dene. GAP-01–10 oracle'ı proposal/adoption/application/verification ayrımını değerlendirir. Model/sürüm/ayar/izin, kritik context ve veri eşdeğerliği kaydedilir; çalışan native özellik bilerek kapatılarak kötü baseline üretilmez.

Ölç: yanlış seçildi/uygulandı varsayımı, kaçan bilinmeyen, eski planı canlandırma, kullanıcı düzeltme süresi, tekrar soru, setup/maintenance, toplam token ve API isteği. Hesap/izin yoksa not_run. Dokümanda bulunmayan özellik unknown; unavailable ancak uygun capability testiyle. Decivora'nın runtime'ı yok, dolayısıyla bugün yüzde üstünlük/skor yok.

**Ürün kararı kapısı:** Claude Projects veya makul extension bu ihtiyacı daha az yönetim yüküyle karşılıyorsa integration/extension geçerli sonuçtur. Bağımsız ürün için providerlar arası güvenilir state ve gerekçeli impact'in ölçülebilir ek değeri gerekir. Tam vizyon korunur; bu belge yeni MVP/stack/otomasyon kararını kabul edilmiş saymaz.

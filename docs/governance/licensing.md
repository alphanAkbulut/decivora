# Lisans ve esinlenme stratejisi

**Karar bekliyor.** Bu private tasarım repository'sine açık kaynak lisansı uygulanmadı. AGPLv3 kaynak konuşmadaki ana aday olarak korunuyor; Apache-2.0 alternatifi mevcut. Aşağıdakiler seçenek değerlendirmesidir; somut yeniden kullanım veya dağıtım için lisans kapsamı ve uyumluluk incelemesi gerekir.

| Seçenek | Karar açısından fark | Öneri |
|---|---|---|
| MIT | Esnek yeniden kullanım; kapalı türevleri engellemez | En kolay yayılım öncelikse değerlendir |
| Apache-2.0 | Açık patent hükümleri ve attribution koşulları; trademark hakkı vermez | Benimsenme/patent açıklığı öncelikse güçlü alternatif |
| GPLv3 | Dağıtılan covered türevlerde copyleft; sırf ağ hizmeti senaryosu AGPL ile aynı değil | Dağıtım modeli netleşince değerlendir |
| AGPLv3 | Değiştirilmiş covered sürümle ağ üzerinden etkileşen kullanıcılara ilgili source sağlama şartı | Açık çekirdek için ilk aday; şirket benimseme etkisini ölç |
| BSL / source-available koşullar | Ek ticari kullanım sınırlamaları olabilir | Kullanım kısıtı taşıyan modeli “OSI açık kaynak” diye sunma |
| Open core / dual licensing | Ürün modeli; başlı başına lisans değildir | Hak sahipliği ve modül sınırları ayrı tasarlanmalı |

AGPL rakiplerin ticari kullanımını yasaklamaz; bütün şirket kodunun otomatik açılacağı anlamına da gelmez. Hangi çalışmanın covered/derivative olduğu somut entegrasyona bağlıdır. [AGPL metni](https://opensource.org/license/agpl-3-0), [Apache metni](https://www.apache.org/licenses/LICENSE-2.0) ve [OSI tanımı](https://opensource.org/osd) esas alınır.

## Task Master için özel sınır

[Mevcut lisans metni](https://github.com/eyaltoledano/claude-task-master/blob/main/LICENSE) MIT yanında Commons Clause içeriyor; “Sell” kavramını ücretli hosting ve değeri yazılımın işlevinden önemli ölçüde türeyen hizmetleri kapsayacak biçimde tanımlıyor. Bunu basitçe “her rakip fikir yasak” diye yorumlamak doğru değildir. Bu proje için pratik kural: lisans incelemesi olmadan kod, prompt, test veya asset taşınmaz; genel problem/iş akışı fikirlerinden özgün tasarım yapılır.

## Alım kapısı

Bir bileşen kullanılmadan önce repo/commit, dosya yolu, telif sahibi bildirimi, lisans ve ek koşullar, yapılan değişiklik, uyumluluk ve notice yükümlülüğü bir reuse kaydına yazılır. Bağımlılıkların transitif lisansları da kontrol edilir. MIT etiketini görmek tüm dosyaların tek lisanslı olduğu garantisi değildir. Marka/logo ve ekran görüntüsü izinleri kod lisansından ayrı değerlendirilir.

Bu başlangıçta üçüncü taraf runtime kodu, logo veya ürün asset'i kopyalanmadı. Özgün dokümantasyon ve sentetik örnek vardır. Uygulama geliştirilirken THIRD_PARTY_NOTICES ve dependency inventory gerekiyorsa eklenir; boş bir lisans bildirimiyle kullanım izlenimi yaratılmaz.

## Public release öncesi

Owner lisans seçer; katkı hakları (DCO/CLA ihtiyacı), olası dual licensing yetkisi, isim/marka araştırması ve tüm bağımlılık uyumluluğu incelenir. Private repo public yapılmadan ayrıca açık kullanıcı talimatı gerekir. Açık çekirdek: yerel hafıza/adapter/MCP/graph/dashboard; olası ticari alan: ekip, yönetilen bulut, kurumsal erişim/audit ve yönetilen otomasyon. Bu ayrım onaylı ticari karar değildir.

## Kaynak kodu, kurulum, erişim ve paket ayrı kararlar

2026-10-10 owner sorusu: “Kapalı mı, açık kaynak mı, seçilebilir mi?” Aşağıdaki ayrım önerilen ürün davranışıdır; lisans seçimi veya repo görünürlüğü değişikliği yapılmadı.

| Eksen | Seçenekler | Kim, ne zaman seçer? |
|---|---|---|
| Kaynak lisansı | AGPLv3 / Apache-2.0 / başka onaylı model; kapalı kaynak ayrı ticari yön | Hak sahibi, yayın öncesi. Son kullanıcı ekranındaki toggle değildir |
| Kurulum / işletim | Kendi bilgisayarında, ekibin sunucusunda self-host, ileride managed servis | Sunulan ve test edilmiş dağıtımlardan kurulum sahibi; şu an hiçbiri ürün olarak uygulanmadı |
| Veriye erişim | Personal, proje ortak, restricted workspace | Kaynak sahibi ve yetkili admin, ACL/policy içinde. Kodun açık olması proje verisini public yapmaz |
| Ticari paket | Olası ücretsiz/ücretli özellik veya hizmet kotaları | Ürün sahibinin ayrı ticari kararı; rol/izin yerine geçmez. Fiyat ve paket seçilmedi |

Önerimiz önce mevcut private repo ve kişisel pilotla ilerlemek; yayın öncesinde OPEN-05/11 kapısında lisans ve hizmet modelini seçmek. Açık çekirdek + ücretli barındırma/destek kaynak konuşmadaki aday yön olarak korunur; temel erişim güvenliği, gizlilik ve veri çıkarabilme ticari karardan bağımsız tasarlanır. Self-host kullanıcı kendi kurulumunu yönetir; kurucuya gizli erişim verilmez. Hosted müşteriye seçenek sunmak ileride kurulum/erişim/paket için mümkündür; bugün destek varmış gibi gösterilmez.

“Kaynağı göster ama ticari kullanım/kopyalama yasak” koşulu OSI açık kaynak tanımıyla aynı değildir; açık kaynak yeniden dağıtım, türevler ve ticari kullanıma izin vermelidir. [OSI tanımı §1–3, §6](https://opensource.org/osd). Lisans seçiminin bedeli açık yazılmalı: AGPL değişiklik paylaşımını belli koşullarda korur, Apache daha esnek yeniden kullanımı destekler; ikisi de kopyalanmayı tümden engelleme aracı değildir.

Yayınlanmış sürüm için geçerli lisans hakları repo düğmesiyle geri alınamaz: AGPL §2 ve Apache §2 koşullara bağlı geri alınamaz haklar tanımlar. Gelecek sürümün modeli, katkıların hak sahipliği ve bağımlılık uyumluluğuna bağlı ayrıca değerlendirilebilir; eski dağıtılmış kopyalar sessizce yeniden lisanslanmış sayılmaz. [AGPL metni](https://opensource.org/license/agpl-3-0), [Apache metni](https://www.apache.org/licenses/LICENSE-2.0). Kaynaklar 2026-10-10 tekrar kontrol edildi; somut dağıtımın uyum analizi henüz yapılmadı.

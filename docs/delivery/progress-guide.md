# Dinamik geliştirme takibi

**Uygulandı: salt okunur yerel geliştirme ekranı.** Bu araç Decivora’nın kendi geliştirmesini gösterir; planlanan ürün UI’si, ENG-10 runtime’ı, MCP bağlantısı veya canlı agent monitörü değildir. Yeni production stack/hosting kararı yoktur.

## Nereden bakacağım?

- GitHub’da [ilerleme görünümü](progress.md): mevcut parçalar, açık kapılar ve 30 ana görevin faz/durum/alt dilim sayıları.
- Etkileşimli yerel ekran (varsayılan Board; Liste görünümü korunur): repo kökünde `python3 -B scripts/project_progress.py --serve` çalıştır; tarayıcıda `http://127.0.0.1:8765` aç. Servis kapanırsa ekran güncelleme hatasını gösterir. Başka port için `--port 8766`; internet yayını yoktur.
- Başlatılmış ekranı Codex’in tarayıcı panelinde açık tutabilirsin. Kullanılan yerel repo kopyası güncellendikçe görünüm değişir. Yeni makinede private repoyu yetkili hesabınla indirip aynı komutu kullan.

## Ekranda ne göreceğim?

| Görünüm | Ne anlatır? | Otorite |
|---|---|---|
| Mevcut teslim parçaları | Kodlanmış P0 hazırlığı/deneyler ve doğrulama sınırı | [Hazırlık matrisi](implementation-readiness.md) |
| Açık çalışma / başlanacak | Ana görev durumları; MVP ve sonraki fazlar ayrı filtrelenir | [Backlog](backlog.md) |
| Görev ayrıntısı | Kabul, doğrulama, kalan kapanış, plan ön koşulu, alt dilim kabulü | Aynı backlog; yeni görev deposu oluşturulmaz |
| Açık kapılar | Kullanıcı kararı, insan etiket incelemesi, host/erişim ve kıyas | Hazırlık matrisinin açık konular tablosu |
| Engine haritası | 10 production sorumluluğu, ilişkili görevler ve sınırlar | [Engine sözleşmesi](../architecture/engines.md) |
| Kanıt | Kayıtlı suite sonucu/tarihi, raporda listeli kod hash kontrolü ve not_run/pending durumları | [Sonuç JSON’u](../quality/semantic-readiness-results.json) |

`IN_PROGRESS` görev kaydıdır: agent’ın bu saniye çalıştığına dair telemetry değildir. Plan ön koşulundan otomatik BLOCKED/ready hükmü çıkarılmaz. Bir deney dilimi uygulanmış olsa da ana görev ancak tüm AC ve kapanış kanıtıyla kapanır. 91 kayıtlı test ürün tamamlanma yüzdesi değildir. Eksik kanıt unknown; değişmiş kanıt kodu stale; tutarsız suite toplamı incomplete görünür. Hash denetimi yalnız raporun kapsamıdır.

## Nasıl güncellenir?

1. Her ilgili teslimde ana görev kapanmasa bile backlog'daki **Son ilerleme** ve **Sıradaki adım** alanlarını güncelle. Hazırlık/kod/gerçek ölçüm türünü ve remaining kapsamı belirt; sadece durum dosyasını değiştirmek ekranı güncellemez. Bunlar açık faz özetinde, Board kartında ve görev ayrıntısında görünür. Teslim parçası veya açık kapı değişiyorsa hazırlık matrisini de güncelle; yeni sonucu ilgili quality kaydına ekle. Ekran kendi başına done üretmez.
2. Açık yerel ekran görünürken **15 saniyede bir** bu kaynakları tekrar okur; “Şimdi yenile” anında okur. Kaynak fingerprint ve son okuma zamanı gösterilir. Okuma zamanı test çalıştırma veya commit zamanı değildir.
3. `python3 -B scripts/project_progress.py --write` GitHub Markdown görünümünü aynı kaynaklardan üretir; `--check` bayat türetilmiş görünümü reddeder. CI bu kontrolü çalıştırır. Commit/push sonrası GitHub görünümü değişir.

GitHub’daki değişiklikler yerel kopyaya **otomatik indirilmez**; güncel repoyu senkronize etmek gerekir. GitHub Markdown görünümü commit bazında güncellenir; interaktif HTML GitHub sayfasında doğrudan çalışmaz. Repo private kalır; GitHub Pages veya public servis açılmadı. Durum değişikliği bu takip ekranından yapılmaz; authenticated product command/UI ayrı MVP kapsamıdır.

## Güvenlik ve maliyet

Python standard library; yeni paket/provider/hesap yok. API yalnız durum okur, loopback’e bağlanır; iki sabit route dışında dosya sunmaz. Host/Origin sınırı, no-store, CSP ve yazma reddi vardır. Transkript, credential, key/env ve ham kullanıcı verisi endpoint’e alınmaz; repository’nin seçili ürün planı/kanıt metadatası sunulur. Durum sorgusu **0 model çağrısıdır**; bu ürünün gelecekteki extraction maliyeti hakkında ölçüm iddiası değildir. Ortak makinedeki yerel kullanıcılar için tam IAM sağlanmaz; ekip/web hosting’e açılmamalıdır.

Doğrulama: parser/otorite, değişen kaynağın yeniden okunması, eksik/stale/tutarsız kanıt, duplicate/invalid metadata, salt okunur API ve erişim sınırları için tracker testleri. Ürün deney testlerinden ayrı değerlendirilir. Tarayıcı filtre/seçim/alt görev/yenileme ve dar ekran kontrolleri teslim kaydında belirtilir.

[Bu teslimin doğrulama kaydı](../quality/development-tracker-results.json): tracker testleri ve gerçekten gözlenen tarayıcı etkileşimleri; gerçek ürün/agent telemetry testi değildir.

Board sütunları: **Planlandı / Çalışılıyor / Engelli / Tamamlandı**. Kartlar aynı ana görevleri gösterir; faz/durum/arama filtreleri ve AC/alt dilim detayı her iki görünümde de çalışır. Sürükleyerek durum değiştirme yoktur; yeni task otoritesi oluşturulmadı. Hazırlık/deney parçaları bitmiş ana görev gibi Tamamlandı sütununa alınmaz. Gerçek BLOCKED kaydı yoksa Engelli boş kalır; açık insan/ölçüm kapıları ayrı paneldedir.

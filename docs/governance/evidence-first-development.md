# Kanıta dayalı geliştirme: projeler arası çalışma rehberi

**Amaç:** Uzun analizden sonra en temel varsayımın yanlış çıkma riskini erken görmek; kullanıcı maliyetini sınırlamak. Bu rehber teslim garantisi vermez ve kullanıcı yetkisini genişletmez. Başka projede kullanılabilir; Decivora’ya özel ders/kanıt [teslim raporundadır](../quality/source-anchor-adapter.md).

## Her projede başlangıç

1. Mevcut davranış, kullanıcı hedefi ve erişilebilir kanıtı oku. “Yapılabilir” iddiasını kesin teslim/kalite/maliyet vaadine dönüştürme.
2. En riskli varsayımı yaz: **hangi gözlenebilir sonuç yanlış çıkarsa yatırım yönümüz değişir?** Önce bu varsayımı küçük çalışan kod/deneyle sına. Genel araştırmayı bu testi geciktirecek kadar büyütme.
3. Deney sözleşmesini çağrıdan önce sabitle: input, çıktı schema/türleri, bağımsız beklenti, başarı/başarısızlık/unknown/incomplete, source/revision ve ölçülmeyen alanlar. Aday ile canonical sonucu aynı etiket uzayına zorla sokma.
4. Deterministik işi koda ver: kimlik, hash, revision, exact quote konumu, schema, limit ve izin. Modeli anlamlı belirsizlik için kullan. Şema doğruluğu anlam doğruluğu değildir.
5. Kullanıcının onayladığı süre/çağrı/retry/token/context/para sınırını kaydet. Byte limit token değildir; bilinmeyen usage sıfır değildir. Alt agent veya retry toplam tavanı sıfırlamaz. Süre dolması yeni iş/harcama izni değildir.

## Çalışırken

- Ham input/output ve başarısız deneme değişmeden kalsın; hash ve sürüm kaydet. Türev düzeltme ayrı artefakt ve açık politika taşısın. Geçmiş hatayı sonradan başarılı çalışma gibi yazma.
- Beklentiyi ürüne veya modelin kendi çıktısına ürettirme. Test helper’ının kendini doğrulaması ayrı; bağımsız örnek/etiket doğrulaması ayrı. AI taslağı human-gold/holdout değildir.
- Hata katmanını ayır: erişim → çıktı aktarımı → parse/schema → kaynak bağlama → anlam → yetki/karar → ilişki/etki → gerçek hedef → AC. Bir katmandaki başarı diğerinin kanıtı değildir.
- Yanlış davranış, belirsizlik, duplicate, stale revision, yetkisiz actor, eksik cevap ve timeout örneklerini çalıştır. Geçmesi için validator/policy/kalite kapısını gevşetme.
- Engeli, denemeyi ve sonraki uygulanabilir adımı takip kaydında görünür tut. Fixture teslimi ana ürün görevini otomatik kapatmaz.

## Durma ve yatırım kararı

Timebox sonunda: **çalışan çıktı → kanıt → kalan risk → sonraki en küçük iş → gerekli karar**. Başarısızlık yeni bir haftalık araştırmaya otomatik dönüşmez. Devam, küçük extension/native çözüm, yeniden tasarım veya durdurma seçeneklerini kanıtla değerlendir. Yeni harcama/erişim/kapsam gerekiyorsa önce somut öneri hazırla.

| İddia | Gerekli kanıt |
|---|---|
| Yerel parça çalışıyor | Kod + tekrar üretilebilir pozitif/negatif test |
| Model doğru çıkarıyor | Bağımsız etiket, gerçek çıktı, açık örneklem ve hata ölçümü |
| Gerçek iş uygulandı | İzinli gerçek hedefte doğru revision/içerik gözlemi |
| Ürün kabulü sağlandı | İlgili AC/DoD ve ayrı yetki/onay |
| Ürün ekonomik/faydalı | Toplam usage, review/düzeltme süresi ve uygun baseline |

## Başka projede nasıl yeniden kullanılır?

Bu dosyayı projenin kendi `docs/governance/` alanına kopyalayıp proje `AGENTS.md` dosyasında şu sabit kuralı referansla: **“Yeni uygulama/entegrasyon yatırımlarında evidence-first-development.md rehberini oku; riski önce küçük çalışan dilimle sına, kanıt düzeylerini ayır ve onaylı bütçede dur.”** Kullanıcı isteği ve proje kuralları önceliklidir.

Decivora `AGENTS.md` bu rehbere bağlıdır. Başka projelere/global agent config’ine otomatik değişiklik yapılmadı; dosyanın burada bulunması her gelecekteki agent’ın kendiliğinden okuyacağı anlamına gelmez. Yeni projede referans/çağrı gerekir. Geçici görev, günlük sonuç veya token bütçesini kalıcı `AGENTS.md` içerisine taşıma.

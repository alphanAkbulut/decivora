# OpenAI pilot001 — ilk gerçek API sonucu

**19 Ekim 2026 · Gerçek inference; sınırlı sentetik örneklem.** Kullanıcı anahtarı yerel yardımcıyla kurduğunu bildirdi; private dosya anahtarı göstermeden doğrulandı. Kaynak/context/para/çağrı onayı önceki açık kullanıcı cevabına bağlıydı.10generation ve10token-count isteği tamamlandı; retry0. Kaynak hash, context hash, strict JSON ve literal quote kontrolleri10/10geçti. Gerçek kullanıcı sohbeti gönderilmedi. Otomatik canonical apply yapılmadı;10pilot veritabanında yalnız başlangıçtaki görev/version1 kaldı.

[Makine raporu](openai-pilot-001-results.json), [salt okunur rapor üreticisi](../../scripts/report_openai_pilot.py), [transport ve kapsam](openai-pilot-runtime.md). Raw yanıtlar/private DB'ler repo dışında korunur. Buradaki özet, ham kanıtın üzerine yazmaz.

## Gözlenen davranış

| Senaryo | GPT-6 Luna | GPT-6.1 Sol | Yorum / mevcut sınır |
|---|---|---|---|
| Yeni backup test isteği |1Task adayı |1Task adayı | Kaynaklı öneri; kullanıcı kabulü henüz yok |
| SQLite kararı |1Decision +1cevap önerisi |1Decision +1cevap önerisi | Açık Q_STORE ile semantik eşleme önerilmiş; exact soru adı kaynakta yok. İnsan review gerekir; otomatik cevap/Decision apply yok |
| Mevcut işe başlama |1In Progress önerisi |1In Progress önerisi | Mevcut exact Task ID'sine bağlandı; otomatik durum değişmedi |
| “Bitti ama test çalıştırmadım” |Öneri yok; coverage complete |1Done **iddiası** önerisi | Luna claim yakalama beklentisini kaçırdı; Sol sonucu doğrulanmış Done değildir. Coverage complete, semantik eksiksizlik kanıtı değildir |
| Q_STORE rev1 sqlite geç cevabı |1cevap önerisi |1cevap önerisi | Exact soru/sürüm/seçenek önerildi; gerçek insan seçimi ayrı review olmadan kaydedilmedi |

Bu5kısa İngilizce senaryo ve model başına tek örnektir. Beklentiler AI-authored taslaktır; bağımsız human-gold veya holdout değildir.10/10**yapısal sözleşme başarısı**,10/10anlam doğruluğu, production güvenilirliği veya iki model arasında kesin kalite sıralaması anlamına gelmez. Negation, çoklu chat, belirsiz Türkçe cevap, context drift, yeni kararın görev etkisi ve gerçek Codex capture bu batch'te sınanmadı.

## Kullanım ve maliyet düzeltmesi

- Input10680, output2595, toplam**13275token**. Reasoning output alt kategorisidir; iki kez ücret eklenmez.
- İlk ledger'ın uncached input/output hesabı**$0.021368** gösteriyordu.
- Provider ayrıca**10650cache_write_tokens** döndürdü. Doğru kategori fiyatlarıyla yukarı yuvarlanmış çağrı tutarları toplamı**$0.024165**; yaklaşık2.42UScent. Bu **fiyat tablosuna dayalı tahmin**, banka hareketi veya doğrulanmış nihai fatura değildir.
- Gerçek tahmin $1onayının altında. Ledger/receipt geçmişi değiştirilmedi; düzeltme ayrı bu rapor ve JSON'da kaydedildi. Yeni çağrı yapılmadı.

**Bulgu:** ilk transport cache-write kategorisini hem reservation hem settlement'ta eksik fiyatlıyordu. Böyle bir hesap başka parametrelerde yanlış admission'a neden olabilirdi. Bu batch'te gerçek tutar sınırı aşmadı;10sabit payload'ın cache-write dahil muhafazakâr azami generation token maliyeti de$0.23625'tir. Sorunu görünmez biçimde “ledger zaten doğruydu” diye düzeltmedik.

**Kod düzeltmesi:** [PilotTransport](../../packages/capture/openai_transport.py) artık bütün input'u en yüksek cache-write fiyatından rezerve eder. Settlement uncached/cache-read/cache-write/output kategorilerini ayrı hesaplar; input kategorileri toplamı tutmazsa, detay eksikse veya farklı service tier dönerse unknown/frozen kalır. Beş yeni regression bunu sınar. Fiyat revision `openai-standard-cache-aware-2026-10-19` oldu; eski onaylı manifest/ledger kendiliğinden yeniden fiyatlanıp yeni harcama iznine dönüşmez.

[Resmî caching açıklaması](https://developers.openai.com/api/docs/guides/prompt-caching): cache-write aynı token için ek uncached ücret değildir; input tokenı kategorisine göre bir tarifeden hesaplanır. [Resmî spending-controller örneği](https://developers.openai.com/cookbook/articles/per_run_spending_controller_responses_api) admission'da en yüksek input ücretini varsaymayı ve eksik muhasebeyi unknown tutmayı destekler. Model fiyatları [API fiyat tablosundan](https://developers.openai.com/api/docs/pricing)19Ekim2026doğrulandı.

## Ne kapandı, ne kapanmadı?

Kapandı: seçilmiş API hesabına bağlantı, gerçek Responses count/generation sözleşmesi,5sentetik kaynak için model→kaynaklı inceleme çıktısı, usage alma. Ücretli20HTTP izni tüketildi; otomatik retry/yeni batch yok. Anahtar repo/log/rapora alınmadı.

Açık: anlam kalitesi ve claim yakalama tutarlılığı, farklı sohbet/dil/rol ayrımı, Codex native adapter, ana UI'da kaynak+model aktivasyonu ve uçtan uca gerçek kullanıcı review/apply. Mevcut T03/T09/T10/T15/T17/T19/T21/T24 işleri kendi kalan kabulüyle açık; yeni parent veya mükerrer blocker eklenmedi. Tek pilot bütün MVP kabulünü kapatmaz.

Sıradaki bağımsız kod: completion claim'ini ayrı ve gözden kaçmayacak biçimde review'da izleme; dar Codex adapter/scope hazırlığı ve uygulama aktivasyonu. Yeni gerçek model ölçümü için yeni somut çağrı izni gerekir; bu gereklilik yerel geliştirmeyi durdurmaz.

## Düzeltme sonrası yerel doğrulama

Beş yeni cache-price regression dahil467runtime ve48repo testi geçti. Salt okunur raporun inference tekrarlamadığı ve saved receipt/DB hashlerini değiştirmediği test edildi.50Mermaid kaynağı yeniden render edildi. UI kodu değişmedi; önceki browser sonuçları bu tur yeniden koşulmuş sayılmaz. Bu yerel doğrulamalar için ek ücretli API çağrısı yapılmadı.

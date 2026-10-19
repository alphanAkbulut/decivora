# Gerçek OpenAI bağlantısı: sınırlı sentetik pilot

**19 Ekim 2026 · T09/T15/T21/T23 alt teslimi.** HTTP transport ve kontrollü CLI çalıştırıcı kodlandı. Bu kayıt gerçek modelin başarılı çalıştığı veya otomatik Codex capture'ın tamamlandığı anlamına gelmez. İlk doğrulama offline HTTP doubles ile yapılır; gerçek dispatch için yerel API anahtarı beklenir. Ana tasklar kendi geniş kabulüyle açık kalır.

## Kullanıcının verdiği izin

Kullanıcı API bakiyesini yüklediğini bildirdi ve bu sohbette kapsamı açıkça onayladı: yalnız sentetik örnekler; OpenAI `gpt-6-luna` ve `gpt-6.1-sol`; toplam en fazla20istek; retry0; istek başına giriş≤10000 ve toplam çıkış≤2000token; toplam≤$1. Gerçek konuşmalar veya kullanıcı veritabanı bu izin kapsamında gönderilmez. Anahtar henüz oluşturulmadı; kod anahtar keşfetmez, credential dosyalarını taramaz ve kullanıcı hesabında key oluşturmaz.

Token sayımını da20HTTP attempt tavanına dahil ettiğimiz için ilk parti **5senaryo×2model =10generation +10count** üst sınırındadır. Bu azami izin içindedir;20generation+20count gönderilmez. Timeout/crash durumunda ayrılan iki HTTP slotu iade edilmez; sayaç gerçek ağ trafiğinin kesin ölçümü değil, muhafazakâr attempt rezervasyonudur.

## Kod ve akış

- [Transport](../../packages/capture/openai_transport.py): yalnız sabit TLS host `api.openai.com`, iki endpoint; proxy discovery/redirect/retry yok. Bounded response; HTTP hata gövdesi ve Authorization header loglanmaz.
- [Mevcut Responses adapter](../../packages/capture/responses_extractor.py): `store:false`, tools kapalı, streaming kapalı, `service_tier:default`, strict JSON schema. Gerçek transport bu callback'e bağlanır; model çıktısı yine source/context/quote doğrulamasından geçer.
- [Çalıştırıcı](../../scripts/run_openai_pilot.py): offline `--prepare`, sonra açık `--run`. Kaynak+görev+soru bağlamı, exact payload hash listesi ve24saatlik manifest ayrı PILOT klasöründe hazırlanır. Her örneğin kendi Workspace'i vardır; bütün modellerin **tek ortak parasal/HTTP ledger'ı** vardır. Kaynak/context authority grant'i ve mevcut token rezervasyonu ayrıca uygulanır. Network DB transaction dışında çalışır. Uygulamanın LOCAL ve TEST DB'lerine yazılmaz.
- Count endpoint aynı model, instructions, input, schema ve tools'u sayar. Sayım eksikse generation yapılmaz; giriş sınırı aşılırsa generation reddedilir. Provider usage bilinmiyorsa veya beklenen count/output sınırını aşarsa sonraki dispatch durur. Modelin anlam hatası deterministic validator tarafından otomatik düzeltilmez.
- `ConversationService.analyze` gerçek sonuçtan inceleme adayları üretir. Runner hiçbir öneriyi kabul etmez, görev kapatmaz veya graph/karar uygulamaz. Hazırlanan örnekler task, decision, mevcut görev başlangıcı, kanıtsız done iddiası ve geç soru cevabını kapsar.

## Bütçe ve yeniden başlatma

Manifest onayı, expiry, fiyat sürümü ve exact payload hashleriyle bağlanır. SQLite `BEGIN IMMEDIATE` ortak ledger'da count+generation için iki slot ve maksimum input/output maliyetini ağdan **önce** ayırır. Yeni model, başka source veya script restart tavanı sıfırlamaz. Aynı exact payload tekrar gönderilmez. Farklı manifest mevcut ledger'ı devralamaz.

Standart kısa bağlam, uncached liste fiyatı `openai-standard-2026-10-19`:1Minput/output başına Luna $0.10/$0.50, Sol $2/$10. Caching indirimi hesaplanmaz. Token maliyeti USD millionths ile yukarı yuvarlanır; float tutar birikimi yapılmaz. Her generation'ın kullanılabilir maksimum token maliyeti önce ayrılır; usage mevcutsa observed input/output üzerinden ücret **tahmini** saklanır. Bilinmeyen usage rezervasyonu korur ve çalışmayı dondurur. Bilinen overrun actual kayıtla korunur.

Bu yalnız bu transport/ledger'dan geçen onaylı pilotu sınırlar; başka programların aynı API hesabını tüketmesini kontrol etmez. Fiyatlar tekrar doğrulanmalı; provider'ın sınıra uymaması, faturalandırma gecikmesi, vergi/kart kuru ve dış çağrılar için kesin banka ekstresi tavanı iddiası yoktur. Token count isteği generation değildir; ayrı arama/araç/storage/paid grader çalıştırılmaz. Count sözleşmesi veya fiyat/usage varsayımı gerçek erişimde tutmazsa durulur, kör fallback/retry yoktur.

## Anahtarın yerel kurulumu

[Kurulum yardımcısı](../../scripts/setup_openai_key.py) `getpass` kullanır; echo kapalıdır ve anahtar CLI argümanına girmez. Varsayılan dosya repo **dışındaki** `outputs/decivora-local-data/secrets/openai-api-key`; private klasör0700, dosya0600, symlink ve overwrite ret. `--status` yalnız dosyanın hazır olup olmadığını bildirir; ağ/bakiye doğrulaması yapmaz. Bu owner-only dosyadır, şifreli keychain veya ekip secret manager değildir. Anahtarı sohbet, issue, GitHub veya ekran görüntüsünde paylaşma. Kurulum kendiliğinden API çağırmaz.

Kullanıcı kendi Terminal'inde Python3.12 ile `scripts/setup_openai_key.py` çalıştırır. Kod çalışma dizininden bağımsızdır. İptal/missing credential yerel hata olarak durur; source analysis başlatılmaz. Paketleme kapsamı bu dosyayı veya pilot sonuç klasörünü içermez.

## Doğrulama ve kalan kapılar

[Transport testleri](../../tests/runtime/test_openai_transport.py) exact payload, money/HTTP admission, count ceiling, private credential, unknown/overrun freeze, concurrency ve restart kurallarını sınar. [Wiring testleri](../../tests/runtime/test_openai_pilot.py)10işin gerçek ConversationService grant→adapter→transport double→source/context validation→review zincirinden geçmesini ve canonical auto-apply olmamasını sınar. Bunlar gerçek inference veya semantik başarı ölçümü değildir.

Gerçek çalışmada private raw model output, usage ve sözleşme sonucu korunur. Hazır senaryo beklentileri **AI-authored** taslaktır; bağımsız insan gold/holdout sayılmaz. Kaynaklı iddiayı görev doğrulamasıyla karıştırmadan sonuçlar ayrıca incelenecek; ilk hata batch'i durduracak. Native Codex capture, sürekli otomatik processing, ana UI'da bağlantı ayarları ve tüm MVP kabulü açık kalır.

**Bu teslimde doğrulandı:**17yeni offline transport/wiring/credential testi dahil462runtime ve48repo testi geçti.50Mermaid kaynağı yerel bundle ile render edildi; değişen local-preview şeması görsel kontrol edildi.192Markdown,2206yerel link,103anchor ve30ana/129alt görev tutarlılık kontrolleri geçti. İzole pilot için10exact request hazırlandı; ağ çağrısı0. UI kodu değiştirilmedi; önceki12browser sonucu bu teslimde yeniden koşulmuş gibi sunulmaz. Bu sonuçlar gerçek model kalitesi, gerçek API hesabı/bakiye veya native host kanıtı değildir.

## Resmî kaynaklar

- [OpenAI Responses token counting](https://developers.openai.com/api/docs/guides/token-counting): exact request sayımı, `POST /v1/responses/input_tokens`.
- [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs): strict schema anlam doğruluğu veya yürütme kanıtı değildir.
- [API fiyatları](https://developers.openai.com/api/docs/pricing): model/fiyat/katman kaynağı;19Ekim2026 kontrol edildi.
- [Prepaid billing](https://help.openai.com/en/articles/8264644-setting-up-and-managing-prepaid-api-billing): bakiye anlık kesin harcama kesicisi değildir.

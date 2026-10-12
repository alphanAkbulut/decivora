# RECEIVER-001 — model, reasoning, kullanım ve oturum kaydı

**2026-10-12 · Deney başlamadan önce yazıldı.** [Dondurulmuş hazırlık](receiver-smoke-plan.md) ve [izin kaydı](../../examples/receiver-smoke/authorization.json). İlk sonuç henüz yok; bu not başarı raporu değildir.

## Model ve host seçimi

Kullanıcı model menüsünde GPT-6.1 Sol/GPT-6 Astra/GPT-6 Sol/GPT-6 Luna/5.6 seçeneklerini gösterdi ve ana sohbetin Sol6.1/High olduğunu bildirdi. Bu **kullanıcı gözlemi**; ana sohbet backend/model token kullanımını ayrıca doğrulamadık. Ana sohbeti otomatik değiştirmedik. Günlük geliştirme için Sol6.1/Medium, kritik mimari/hata incelemesinde geçiciHigh önerildi; uygulanmış hesap ayarı diye kaydedilmez.

Dar receiver testi için **GPT-6 Luna / Low** seçildi: mevcut durumları okuma ve altı güvenli next-action önerisi, tam proje geliştirmesinden ayrı iş. [OpenAI model seçim rehberi](https://developers.openai.com/api/docs/guides/model-selection) scoped/simple extraction için Luna/Low; complex technical work için Sol6.1/Medium yönlendirmesi sunar. [Model ayarları](https://learn.chatgpt.com/docs/models) model/effort kontrollerini açıklar. Bu rehberler başlangıç önerisidir; bizim fixture sonucumuz veya hesap erişim kanıtı değildir.

**Yöntem değişikliği açık:** hazırlık manifesti normal Chrome/temporary ChatGPT önerisi taşıyordu. Kullanıcı şimdi “diğer oturumu sen aç” diyerek Luna/Low deneyini ayrı chat'te yapmamızı istedi. Yeni run, `create_thread` ile local projectless Codex sohbeti, configured model `gpt-6-luna`, effort `low`, tek başlangıç prompt'u olacak. Tarayıcı Instant etiketini Luna API kimliği saymayız. Eski prompt/request/expected/manifest değişmedi; önceki host önerisi historical preparation kaydıdır. Yeni model/host scope'u ayrı authorization'a bağlıdır.

## Context sınırı ve devam yeri

Ana proje geliştirme ve kullanıcı kararları **bu mevcut sohbette** devam eder. Yerel devir dosyası repo dışındaki `outputs/decivora-next-chat-handoff.md` içindedir; repo status/backlog/proof kayıtları güncel otoritedir. Deney sohbeti proje konuşmasının devamı değildir.

Yeni sohbete yalnız exact prompt.txt; iki synthetic readable view/8 kaynak mesaj gönderilir. Parent conversation, repo, expected.json/oracle, rapor veya bu execution notu prompt'a eklenmez. Fork/thread-history kopyası kullanılmaz. Projectless target repository erişimini test için istemez. Global system/developer/agent talimatlarının yok olduğu veya tamamen steril context garanti edilmez; host extra input token/context hidden olabilir. Tool/subagent/write istenmez; transcript'ten araç/komut çalıştırılmaz. Tool kullanımı görülürse run contamination açıkça işaretlenecek.

Sonuç burada ilk-output saved evaluator ile ölçülür; aynı source/question/revision bağı ve authored oracle korunur. Deney chat'ine sonradan çalışma/fix prompt'u gönderilmez, ikinci inference yapılmaz. Bu chat'i silme/archive etme varsayılanı yok; kullanıcı sonucu inceleyebilir.

## Token, kota ve aşımın anlamı

- Exact user prompt:7.950UTF8byte; byte token değildir. Softoutput hedefi1536token; **provider hard output/context cap doğrulanmadı**. Bir task/başlangıç turn'ü, ilk final cevap,0retry/0regenerate/0follow-up/0paidAPI. Host internal inference/retry sayısı unknown.
- Yerel Python'da tokenizer bulunmadı; yeni dependency kurulmadı. Input/visible-output token sayısı ve bunların seçili model encoding'ine eşleşmesi **unknown**. Varsayımsal bytes/4 sayısı gerçek usage diye kullanılmaz.
- Input/output/reasoning/cache/provider total token alanları, host telemetry sunarsa source ile kaydedilecek; yoksa null kalacak. [Resmî token ölçümü](https://developers.openai.com/api/docs/guides/token-counting) görünür metin ile toplam output consumption'ın farklı olabileceğini açıklar. [Reasoning usage](https://developers.openai.com/api/docs/guides/reasoning) reasoning'in output usage içinde bildirilebildiğini açıklar; output+reasoning diye iki kez toplamayız.
- Account quota snapshot global/shared ve yuvarlanmış yüzde olabilir; parent sohbet/başka işler aynı pencerede tüketir. Önce/sonra yüzde farkı tek trial'ın token sayısı veya maliyeti değildir. Account/provider kimlikleri veya ham hesap snapshot'ı repo'ya konmaz.
- Expected-versus-actual token sapması **measured_usage_available** ise karşılaştırılır. Şu an baseline tahmini ve exact provider usage yok: aşım sonucu `not_evaluable`,0 veya limit_within değildir. Visible byte/character boyutu ayrı deterministic metrik; para/token değildir.
- API pricing'i üyelik quota tüketimine çevirmeyiz. Bu run için yeni API key, bakiye, üçüncü taraf paid bağlantısı veya satın alma yok. Ana sohbetin reasoning ayarını düşürmek deneyin configured model/effort'ünü kendiliğinden değiştirmez.

## Beklentiler ve başarısızlık

İki readback ve altı proposed next-action authored_draft; N01 eski1/B korunur/current2/A yalnız confirmation, N02 explicit UI/B confirmation/bindlessB clarification; upload yalnız reported, AC_SMOKE/rev2not_run. Fixture_initial gerçek human-approved karar değildir. True approval/verified/upload proof, not_run→passed, ambiguous mapping, stale selection kritik hata. Schema/source-binding bozuksa raw değiştirilmez; first failure/incomplete raporlanır. Gerçek sonuç test bitince ayrı run raporuna yazılacak; burada önceden tahmin başarı diye sunulmaz.

Bu n=1 development receiver deneyi source extraction accuracy, native/file baseline üstünlüğü, gerçek target/AC veya tokenROI/genel kalite kanıtı değildir. AnaT01/T02/T03 ve production T03c yatırım/stack açık kalır.


## İlk run sonrası ek — 2026-10-12

[RECEIVER-001](receiver-001-result.md) tek configured Luna/Low native turn'de completed; model contract invalid abstention nedeniyle geçmedi.136 semantik test actualraw guardlarını doğrular; model başarısı değildir. Read-thread full final text syntax valid; wait summary null/false kaybı ayrı taşıma bulgusudur. Usage/token aşımı unknown/not_evaluable; quota immediate74→74 shared/rounded, consumption0 diye sunulmaz. Native UI screenshot erişimi güvenlik kısıtıyla reddedildi; configured model ile backend doğrulaması ayrı. Ana geliştirme mevcut sohbette sürer; deney chat'inde yeni inference yapılmaz. Yukarıdaki notlar gerçek dispatch'ten önceki snapshot, bu bölüm actualrun kanıtıdır.

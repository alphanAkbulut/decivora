# Konuşmadan kaynaklı adaylara ve görev panosuna

2026-10-13 — T09/T10/T22 çalışan hazırlık ve UI dilimi; gerçek semantic model/transport/kalite kabulü açık. Kullanıcı otomatik diyalog yakalamanın asıl amaç olduğunu tekrar vurguladı; paket2 import/çıkarım akışı öne alındı, elle kayıt ana ürün akışı olmaktan çıkarıldı. API erişimini yarına bıraktı; harcama onayı değildir. T22 In Progress; yeni task ID yok.

## Kodda ne var?

[ConversationService](../../packages/capture/conversations.py) izinli manuel metni gerçek kaynak olarak kalıcı saklar: source ID/hash/revision, manual_paste provenance, owner ve received_at. Aynı proje/text dedup, restart/backup/restore;12000UTF-8byte ve32import geliştirme tavanı. Synthetic SourceEvent sözleşmesi değiştirilmedi; gerçek metne synthetic etiketi takılmadı.

[ResponsesExtractor](../../packages/capture/responses_extractor.py) provider-neutral send callback üzerinden OpenAI Responses request/response şemasını hazırlar/parse eder. `text.format` strict JSONschema, explicit model/max_output_tokens, store=false, tools=[]; refused/incomplete/invalid response ret. [Resmî Structured Outputs referansı](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) request şeklinin kaynağıdır; JSON shape anlam doğruluğu değildir. Yeni dependency yok. **18 Ekim güncel sınır:** source-bound grant ve token rezervasyonu/settlement bağlandı; gerçek HTTP send, credential kurulumu ve doğrulanmış token/context/para activation kapıları henüz tamamlanmadı. Default UI extractor=None; anahtar okumaz veya API çağırmaz. Trusted test injection authorization gerçek üretim grant sistemi diye sunulmaz.

Analiz yapılırsa whole-batch exact source ID/hash/type/intent/quote doğrulanır. Unique quote konumunu kod bulur; modelden karakter saymasını istemez. Model başlığı/türü/niyeti semantic kalite kabulü değildir. Rejected intent apply olmaz. Transcript komutu veya actor=human metni capability/onay yaratmaz. Bounded decoded raw output/hash özel DB'de korunur; unknown usage null. Büyük/başarısız output ile canonical state değişmez.

Model/transport DB transaction dışında çalışır; önce durable started receipt. Timeout/crash/tekrar veya iki bağlantı aynı kaynağı kör tekrar göndermez; Analysis failed/unknown görünür. Activation/data/cost sınırları ayrıca doğrulanmadan gerçek transport açılmayacak. Fixture invocation count ücretli gerçek model çağrısı değildir.

Kaynaklı adaylar mevcut100scoped record ile exact comparison'a girer; eksik comparison apply'i engeller. Yeni aday typed create; exact duplicate ikinci görev üretmez, source attachment audit'i ekler. Possible refinement ayrı relationship review ister, overwrite yok. Seçili önerileri kaydetmek explicit human write/current knowledge revision ve atomic approval/apply/audit gerektirir. Retry tek etki; audit failure event/record/receipt rollback. Reported done metni yalnız claim: Task To Do olur, AC/verification hâlâ gerekir. PendingDecision adayı henüz kaynak host'un QuestionRequest seçenek/authority mapping'i değildir.

## Kullanıcı arayüzü

Ana akış: konuşma aktarımı solda, kaynaklı öneri incelemesi sağda; sidebar, gerçek workspace metrikleri ve görev panosu. Manuel Task ve soru/karar araçları yardımcı collapsed bölümlerde kalır. Kullanıcıya source code, private engine jargon veya tamamlanmış olmayan MCP vaadi gösterilmez. Model bağlı değilse açık bekleme açıklaması; empty/review/recorded durumu ayrılır. Desktop→mobile stacked layout, odak halkaları ve native label/checkbox/buttons; tam accessibility certification iddiası yok.

## Kanıt ve kalanlar

16yeni/237runtime test;46tracker testi ayrıca kontrol edilir. Gerçek browser kontrollü extractor3aday→seçili Task→pano→reload geçti; manual AC/soru/lifecycle regresyonu korundu. Desktop1440 ve mobile390 incelendi, mobile yatay taşma yok. [Kaynak hashli sonuç](conversation-review-results.json). Fake output extraction değildir; semantic accuracy, gerçek provider dispatch ve native capture not_run.

İlk testte mevcut records query'nin iç transaction'ı outer read snapshot ile çakıştı; scoped SQL read aynı snapshot içinde kullanılarak düzeltildi. Yardımcı bölümlerin reload'da kapalı olması için browser testi bölümü açacak şekilde güncellendi; işlev kaldırılmadı. Eski failure/output raporları yeniden yazılmadı.

Sıradaki gerçek kapı: kullanıcı API erişimini hazırlar; sağlayıcı/model, exact source veri izni, token/context/çağrı/para tavanı ve gerçek transport onaylanır. O zamana kadar ücretli dispatch yok. Sonra bağımsız beklentilerle gerçek anlam çıkarımı; T22 message/prompt lineage/coverage ve T09/T10 kalite kabulü. T16/T17 continuous capture, T18 MCP, T14 Done kapıları açık. Paste alanı otomatik oturum takibi değildir; full MVP kabulü yok.


## 18 Ekim — konuşmadan mevcut görevin durumuna

[Çalışan diyalog inceleme dilimi](dialogue-status-runtime.md): izinli kaynak + güncel görev bağlamından hazırlanan istek; kaynak/context bağlı yapılandırılmış yanıt → yeni görevler ve mevcut görevlere durum önerileri → ayrı insan incelemesi → ortak workflow/AC/Done kontrolleri. Mevcut LLM yanıtını manuel aktarma UI'si ve configured Responses adapter'ın `dialogue_review=True` yolu aynı validator'ı kullanır. Context egress için source-only grant yeterli değildir. Gerçek model/capture etkinleştirilmedi; sentetik yanıtlar semantik kalite kanıtı değildir.


[Primary flow audit](primary-flow-audit.md) görev/karar/soru/ilişki zincirinin kalan kopukluklarını ve fixture probe sonuçlarını içerir. Model öncesi context v2 canonical non-task kayıtları ve gerçek soru/ilişki snapshot'larını da taşır; yalnız task listeleyen eski davranış güncellendi.

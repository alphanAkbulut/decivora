# Diyalogdan görev ve mevcut görev durumuna — 18 Ekim 2026

**Uygulandı: yerel inceleme ve workflow bağlantısı. Gerçek model anlam doğruluğu ve otomatik oturum yakalama uygulanmış/kabul edilmiş sayılmıyor.** Mevcut T09/T10/T13/T14/T19/T20/T22 dilimidir; yeni ana görev veya yeni MVP tanımı değildir.

## Kullanıcının göreceği akış

1. Konuşmayı aktar. Kaynak metin, hash ve proje kimliği korunur; task elle yazmak zorunlu değildir.
2. Model kapalıysa kaynak kartındaki **Use a response from your existing LLM → Prepare LLM request** seçilir. İstek seçilmiş konuşmayı ve o projenin mevcut task kimliklerini, kısa açıklamalarını, güncel stage/contract/workflow bağlamını içerir. Kullanıcı nereye göndereceğini seçer; hazırlama ve kopyalama dış veri paylaşım izni değildir.
3. Yapılandırılmış JSON yanıtı **Validate and import response** ile aktarılır. Kaynak alıntısı, source/context hash ve mevcut task kimliği doğrulanır. İlk import canonical task/stage değişikliği yapmaz.
4. Yeni Task/Decision/PendingDecision adayları eski kaynaklı aday incelemesini kullanır. Kabul edilen yeni task To Do'dur. Mevcut task için status önerisi önce/sonra + literal alıntıyla ayrı görünür; insan gerekçeyle kabul, ret veya erteleme yapar.
5. Kabul, ortak workflow kontrolünü çalıştırır. In Progress için onaylı güncel AC ve açık start gate gerekir. Done için izinli stage geçişi, bütün zorunlu güncel AC/DoD kanıtları, kapalı finish gate ve ayrı scope acknowledgment gerekir. “Yaptım/yükledim” metni evidence değildir.

## Kod ve sözleşme

- [DialogueReviewService](../../packages/capture/dialogue_review.py): scoped hazırlık, dış yanıt import'u, ortak kaynak/context validator ve status review/apply. [ConversationService](../../packages/capture/conversations.py) mevcut create/reconciliation ve source geçmişini korur; görünüm en yeni append-only analiz revision'ını gösterir.
- [ResponsesExtractor](../../packages/capture/responses_extractor.py) `dialogue_review=True` ile aynı response schema/context validator'ını kullanır. Her dispatch için kopya adapter hazırlanır; ortak extractor üzerinde source context yarışması yaratılmaz. Provider çağrısı DB transaction'ı dışındadır. Default launcher hiçbir provider açmaz.
- [Response şeması](../../manifests/dialogue-review-response.schema.json): source_id/source_sha256/context_sha256/coverage/candidates/status_changes. Her değişiklik task_id/stage/quote taşır; sürüm/digest trusted request snapshot'ından alınır, modele bırakılmaz.
- [Grant şeması](../../manifests/conversation-dispatch-grant.schema.json): dialogue-aware provider dispatch için exact `context_sha256` zorunludur. Eski source-only grant bu veriyi dışarı gönderemez. Mevcut token rezervasyonu/settlement aynen korunur; tam input/context/para preflight ve gerçek aktivasyon hâlâ açık.
- [TaskWorkflowService](../../packages/domain/task_workflow.py) public transition wrapper'ı aynı kontrolleri korur; iç `_transition` aynı transaction'da stage ve kaynaklı inceleme makbuzunu atomik kaydetmeye izin verir. İç metot insan/yetki/active/revision kontrollerini atlamaz. Ara kayıt başarısızsa stage de rollback olur.
- HTTP command'leri: prepare_dialogue_review, import_dialogue_response, review_dialogue_status; mevcut session/Origin/CSRF/project/write kontrollerinden geçer. Stage mutation read endpoint'inden veya LLM metninden tetiklenmez.

## Güncellik ve geçmiş

Import sırasında bütün hazırlanmış context güncel olmalıdır. Apply sırasında o task'ın version/workflow/ilişkili bağlamı yeniden kontrol edilir; bağımsız başka task'a yapılan status değişikliği ikinci öneriyi gereksiz yere geçersiz kılmaz. Aynı task'a tek yanıt içinde iki farklı iddia gelirse whole response reddedilir; son cümle sessizce seçilmez. Bu ilk dilimde çelişkili iddiaları otomatik kronolojik çözme yoktur.

Dış import yolundaki eski öneri stale olduğunda yeni current-context istek/yanıtı aynı source için append-only analiz olarak kaydedilebilir; önceki raw/hash ve review'lar korunur. Aynı context'e farklı raw yanıtla önceki analizi değiştirme yoktur. Source/model dispatch sonucu, unresolved started receipt veya timeout geçmişi import ile değiştirilemez. Kimliği eşit import/review retry tek etki üretir. Accepted stage kaydı source görünümüne ve audit timeline'a bağlanır; ret/erteleme task stage'ini değiştirmez.

## Doğrulama

17 yeni domain/entegrasyon testi: task create + ayrı status review, bağımsız iki task, restart/backup/restore, yanlış quote/target/context, duplicate JSON, stale workflow, revoke/agent/project sınırı, partial evidence/Done/scope, blocker, atomik rollback ve configured-provider payload/usage. Yeni tarayıcı testi gerçek HTTP/DB/UI üzerinden ilk konuşma→Task To Do, AC onayı, ikinci konuşma→In Progress, reload/source link, yanlış Done ret ve 390px taşma kontrolünü yapar. Yanıtlar açık sentetiktir; gerçek inference/token ekonomisi ölçümü değildir.

İlk geliştirme koşusunda nested transaction hatası bulundu; kontroller gevşetilmeden ortak workflow iç metodu ve atomik dış transaction ile düzeltildi. Browser testinin ilk denemelerinde buton adı ve çoklu Sources/alıntı seçicisi yanlış olduğundan harness düzeltildi. Optional context grant alanı için source-only ve context-bound payload beklentileri ayrı doğrulandı. Sandbox'taki ilk geniş runtime koşusu port açamadı; izinli loopback test ortamında tekrar çalıştırıldı. Başarısız denemeler başarılı test sayılmadı.

Son ölçüm ve dosya hashleri: [makine kaydı](dialogue-status-results.json). Diagram [yerel runtime](../architecture/local-preview.md) içinde güncellendi; render sonucu model kalitesi kanıtı değildir.

## Açık sınırlar / sıradaki geliştirme

Bu teslim sürekli otomatik capture değildir. LLM anlamı çıkarır; yerel kod yalnız sözleşme, kaynak, kimlik, güncellik ve yetkiyi doğrular. Ücretli gerçek HTTP transport/credential etkinleştirilmedi; gerçek semantic corpus/holdout ve kullanıcı pilotu açık. Dış LLM yanıtının model kimliği ve kullanım miktarı doğrulanamaz; model_calls=0 yalnız Decivora'nın yerel dispatch sayısı, dış harcamanın sıfır olduğu iddiası değildir. Request'in task açıklamaları 512 karakterlik etiketli excerpt; context en çok 100 proje record'u ile tam hazırlanır, fazlası sessiz truncate edilmez. Yanıt 16KiB, aday/değişiklik sayısı ayrı 32 sınırındadır.

Blocked/Cancelled/yeniden açma bu response formatında stage olarak uygulanmaz; mevcut impediment/lifecycle/impact incelemesi korunur. Aynı source içindeki çelişkili çoklu status iddiaları, otomatik AC çıkarımı, decision-aware ilişki/etki adaylarının tam entegrasyonu ve native capture sonraki dilimlerdir. İlk yeni geliştirme güvenli model aktivasyonu/input-context-money preflight ve ardından bounded gerçek çıkarım deneyi; bütün bu kapılar geçmeden ana görev/MVP Done olmaz.


Son doğrulama: **347 runtime + 48 kök test geçti; sekiz mevcut browser akışı ve düzeltilmiş yeni diyalog akışı geçti.44Mermaid render failure0.** Mevcut özel DB yedeklendi; güncel uygulama53610portunda başlatıldı, authenticated read-only browser/HTTP kontrolü yapıldı. DB logical digest değişmedi ve integrity ok. Kullanıcı DB'sine sentetik örnek eklenmedi; yeni görev/durum ekran görüntüleri ayrı geçici fixture ortamındandır.44dosyalık veri içermeyen kaynak ZIP üretildi; temiz başka makine kabulü değildir.


## Ana akış denetimi sonrası context düzeltmesi

[18 Ekim ana akış denetimi](primary-flow-audit.md) görev-only input'un karar/soru/ilişkileri taşımadığını saptadı. `decivora-dialogue-context-2` bunları aynı scoped/hash-bound snapshot'a ekler; kayıt açıklamaları en çok1024karakter excerpt, task açıklamaları512, soru64 ve relation500 tavanındadır. Eksik gövde/history açıkça belirtilir. Aynı kaynak için cache readback en yeni analizi döndürür.21diyalog testi içindeki4yeni regresyon bağlam içeriği, geç cevapta stale input, excerpt ve latest readback'i kontrol eder. Bu düzeltme otomatik relation/question proposal veya izinli MCP devam paketini tamamlamaz.

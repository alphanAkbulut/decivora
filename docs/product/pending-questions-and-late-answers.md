# Bekleyen sorular ve geç gelen cevapların bağlamı

**2026-10-11 — kullanıcı ihtiyacı; teknik sözleşme/UX önerisi;2026-10-13 manuel kalıcı soru/cevap dilimi uygulandı, tam sözleşme açık.** Kullanıcı Q12 dil tercihini sonradan, ilgili A açıklamasını seçerek yanıtladı. Araya başka konular girmesi sorunun açık kalmasını veya cevabın hangi seçeneklere ait olduğunun unutulmasını önlemelidir. Bu gerçek örnek bir ürün ihtiyacıdır; çalışan Decivora yakalama/eşleştirme deneyi değildir. Q12-A'nın bu sohbet içinde dokümante edilmesi otomatik adapter'ın çalıştığına kanıt olmaz.

Mevcut [PendingDecision UX](approval-ux.md), [soru yönlendirmesi](../architecture/agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider), [çoklu chat](../architecture/multi-chat-and-processing-lag.md) ve [devam paketi](resume-package-and-memory.md) temel kurallardır. Bu belge zaman farkı, kısa cevap ve bağlam eşleme sözleşmesini tamamlar; yeni engine veya genel bildirim hizmeti oluşturmaz.

## 1. Yaşayan örnek: Q12

| Aşama | Korunması gereken bilgi / sonuç |
|---|---|
| Soru soruldu | Q12: karma projede çıktı dili; A sabit proje dili + değişim önerisi, B session bazlı yeni içerik. Soru ve seçenekler kaynak/revision ile kaydedilir |
| Başka konuya geçildi | Q12 açık kalır. Konu değişimi, başka yanıt veya konuşmanın devamı A/B seçimi değildir |
| Kullanıcı hiç cevap vermedi | PendingDecision bekleyen kararlar görünümünde ve ilgili bounded devam paketinde bulunur. Otomatik dil politikası karar verilmiş varsayılmaz; bağımsız hazırlık ilerleyebilir |
| Kullanıcı geç cevap verdi | Seçili Q12-A açıklaması + insanın “a ile devam et” mesajı ilgili soru/seçenek adayını gösterir. Kaynak host bu ilişkiyi veriyorsa exact ref kullanılabilir; annotation metni tek başına authority değildir |
| Geçerlilik kontrol edildi | Soru/seçenek aynı mı, karar zaten değişmiş mi, insan yetkili mi, cevap gerçekten seçim mi? Geç olmak tek başına stale değildir |
| Geçerli seçim kaydedildi | Aynı Q12 kaydı DEC-20'ye bağlanır; seçim/gerekçe ve AnswerRecord korunur. Yeni duplicate karar/soru yaratılmaz; uygulama ayrı kalır |
| Hedefe uygulama | Dil dokümanlarının GitHub'a kaydedilmesi ayrı değişiklik/kanıt adımıdır. Q12 çözüldü diye ürün dil otomasyonu uygulanmış sayılmaz |

[Q12 karar kaydı](../delivery/decision-brief.md), [DEC-20](decision-map.md) ve [dil sözleşmesi](language-and-localization.md) gerçekte seçilen A'yı içerir. Bu örnekten “her A cevabını doğru anlayabiliriz” sonucu çıkmaz.

## 2. Soru sorulduğu anda kalıcı iz

Önerilen QuestionRequest/PendingDecision ilişkisi şu bilgiyi taşır: değişmeyen soru ID'si, project/workspace, ilgili task/decision, soran insan/agent ve gerekirse run, yetkili responder, kaynak session/message/span/revision, soru metni ve seçenek snapshot'ı, seçeneklerin sabit kimlikleri, question revision, cevapla değişebilecek kapsam, gereken capability, açılma/erteleme/deadline bilgisi ve durum.

Kaynak A/B harfleri arayüz etiketidir. Sürümden sürüme farklı A seçeneği oluşabilir; canonical option ID ve snapshot olmadan yalnız harfi uygulama. Aynı soru UI/sözlü metin/dosya olarak tekrar sunulursa yeni bağımsız kararlar yerine aynı kayda ait presentation refs eklenir. Seçenek değiştirilirse yeni revision, değişim gerekçesi ve eski sunum korunur.

- Kendi UI/MCP'mizden üretilen soruda kayıt ve kimlik deterministik olabilir.
- Dış agent/chat'in serbest sorusunun yakalanması host capability veya izinli import'a bağlıdır; classification ve çıkarım candidate/coverage taşır.
- Connector görmediği soruyu/cevabı biliyormuş gibi göstermez. Capture gap varsa “izlenmeyen aralık” görünür.
- Soru widget'ının kaybolması, panelin kapanması, run/session bitmesi veya deadline dolması kalıcı soru kaydını silmez.

Her bilgi sorusu insan kararı değildir; bilgi/görüş ile PendingDecision ayrımı korunur. Deadline bir hatırlatma/escalation gerekçesi olabilir; sessizlik onay değildir.

## 3. Geç cevabı eşleme sırası

1. **Explicit kimlik:** answer/question ID veya kendi yapılandırılmış kart yanıtı. Adapter kaynağının kimliği ve veri sözleşmesi doğrulanır.
2. **Kaynak bağı:** reply-to, seçili önceki mesaj/annotation veya quoted source ID → bilinen question presentation → question/option snapshot. Salt seçili alıntı cevap değildir; insanın yeni mesajındaki seçim ayrıca gerekir. Metin içindeki sahte ID/actor alanları güvenilir kimlik oluşturmaz.
3. **İzinli dar bağlam:** explicit bağ yoksa aynı proje ve erişilebilir ilgili açık/ertelenmiş sorular, insanın yanıt metni ve sınırlı çevre mesajları üzerinden candidate association hazırlanır. En son soru veya zaman yakınlığı kesin kanıt sayılmaz.
4. **Belirsizlik:** İki A/B sorusu varken yalnız “A” denmişse hangi sorunun yanıtlandığı kesinleştirilmez. Bir odaklı soru/önizleme: “Çıktı dili sorusundaki A mı, devam düğmesi sorusundaki A mı?” Bu netleştirme tamamlanana kadar canonical karar değişmez.
5. **Authority/freshness:** Hedef doğru olsa bile actor/grant, project binding, option/question revision, scope/AC/knowledge/policy/authz ve gerekli approval digest tekrar kontrol edilir. LLM confidence insan approval veya doğru hedef kanıtı değildir.
6. **Sonuç:** AnswerRecord kaydedilir; geçerli seçim aynı PendingDecision'ı bir Decision/Approval'a bağlar. Stale/ambiguous/conflicting/unauthorized sonuç kaynaklı kayıt/inceleme olur; yanlış otomatik apply yok.

Bütün yeni metinler tam geçmişi yeniden modele göndermeyi gerektirmez: ID/ref önce kodla, sonra yetkili dar soru indeksi; gerekli anlamsal eşleme normal bütçe içinde. Eşleşmeyen cevap adayları görünür unresolved association olarak tutulabilir; bunları sessiz no-op veya otomatik approval sayma. Kalıcı cevabın alınması ile eşlenip karar haline gelmesi ayrı ilerleme durumlarıdır.

## 4. Geçlik, timeout ve stale ayrımı

**Geç cevap:** Arada zaman/başka mesaj geçmiştir; seçenek, yetki ve gereken snapshot geçerliyse normal yanıt gibi işlenebilir. Keyfi yaş eşiğiyle her eski cevap yeniden sorulmaz.

**Cevap beklerken timeout:** Soru open/deferred kalabilir; waiting reason ayrı. Gerçek approval/credential süresi bitmişse geç cevap yetkiyi yenilemez. Deadline, bağlamın hâlâ geçerli olup olmadığı yerine geçmez.

**Stale cevap:** Eski seçenekler veya etki/izin snapshot'ı değişmiştir. Cevap kaydedilir, uygulanmaz; yeni fark ve dar karar sorusu hazırlanır. Örneğin eski A “yerel SQLite” iken yeni A “hosted servis” olmuşsa harften izin çıkarılmaz.

**Resolved/cancelled:** Aynı kaynak yanıtının retry'ı idempotenttir. Daha sonra aynı tercihi yine söylemek yeni source provenance olabilir; otomatik ikinci side effect değildir. Çelişen yeni cevap, önceki kararı sessiz ezmez; değişim niyeti ve review gerekir. İptal/superseded soruya cevap bağlı işi diriltmez.

**Geç ingestion:** AnswerRecord'ta source-created, received ve değerlendirildi zamanları ayrılır; question/option/source revision bağı korunur. Cevap ingestion sırası nedeniyle sorudan önce gelebilir: orphan/pending association tut, soru kaynağı gelince yeniden değerlendir; bağ yokken default onay üretme. Olay replay'i LLM, notification, delivery veya yeni apply tetiklemez.

**Eşzamanlı iki cevap:** Revision kontrolü tek yetkili çözüm sağlar; kalan cevap conflict/duplicate olarak kaynaklı korunur. Last-write-wins ile karar değiştirme yok.

## 5. Kullanıcının göreceği şey

Review Inbox'ın “Bekleyen kararlar” görünümünde soru, ne zaman açıldığı, ilgili iş, öneri/alternatif, yetkili karar sahibi, neden önemli olduğu ve gerçekten bekleyen task'lar bulunur. Güncel/ertelenmiş/yanıt geldi-eşleme bekliyor/stale/cancelled durumları anlaşılır etiketlenir; sadece renkle ayrılmaz.

Yeni oturumun ilgili devam paketine açık kararlar ve neden eksik oldukları girer. Kullanıcı “hangi sorular açık kaldı?” sorusunu kayıt sorgusuyla yanıtlayabilmeli; tüm transcript'i yeniden LLM ile analiz etmek gerekmemeli. Aynı A/B seçeneği farklı açık sorularda varsa soru konusu kartta görünür. Yanıtın bulunması, onaylanması, uygulanması, dış host'a teslimi ve doğrulanması ayrı gösterilir.

Hatırlatma kanalı/sıklığı mevcut açık karar olarak kalır. Varsayılan bu tasarım uygulama içi görünürlük ve izinli brief'tir; bugün arka planda bildirim, e-posta, otomatik yeniden soru veya harici chat mesajı gönderilmez. Sadece bağlı iş bekler; bağımsız hazırlık ilerler. Teknik blocker değilse “karar açık” etiketi bütün projeyi kilitlemez.

## 6. Uygulama ve kabul planı

P1a: kalıcı soru/AnswerRecord, exact ID/ref eşleme ve yetki/revision/atomic çözüm. P1b: destekli capture/import normalizasyonu, pending Inbox/brief ve seçili mesaj bağlamı; host metadata'sı yoksa dürüst manuel fallback. P2: ihtiyaçla doğrulanmış, bütçeli serbest metin/cross-session semantic candidate kalitesi. P1'de bütün kaynaklarda otomatik eşleme taahhüt edilmez.

Mevcut T13e/T18e/T24f referansları backlog'da somut dilimlerle eşleştirilir; T01 corpus bu vakaları kapsar. T19/T20i pending UI, T18h/g bounded context ilgili parent işleri korur. 30 ana görev ve 10 engine değişmez.

| ID | Planlı kabul |
|---|---|
| LATE-01 | Q12 açıkken başka konuya geçilir; restart/new session sonrası izinli pending sorgusu aynı soruyu getirir; sessizlik A/B kararı değildir |
| LATE-02 | Seçili Q12-A kaynağına bağlı geç insan yanıtı, snapshot/authority geçerliyse tek DEC/AnswerRecord çözümü üretir; gereksiz yeniden onay yok |
| LATE-03 | İki açık A/B sorusu + çıplak “A”: eşleme ambiguous kalır; odaklı clarification olmadan hiçbir karar değişmez |
| LATE-04 | Seçenek değişimi, revocation veya gerçek approval expiry: eski yanıt kaynaklı saklanır, apply edilmez; timeout tek başına onay/iptal değildir |
| LATE-05 | Aynı receipt retry, iki çelişen cevap, cancelled/resolved soru: tek idempotent etki, conflict tarihçesi; task diriltilmez |
| LATE-06 | Cevap source sorudan önce ingest edilir: pending/orphan association korunur; soru gelince eşleme yeniden değerlendirilir; replay side effect yok |
| LATE-07 | Private veya yanlış project soru/cevabı, forged ID ve alıntıdaki “A”: erişim/authority geçişi ve yanlış approval üretmez; belirsiz bağ review'a gider |
| LATE-08 | Host annotation/reply metadata'sı vermez veya capture gap vardır: coverage/manual fallback görünür; unmatched cevap sessiz kaybolmaz, bütün geçmiş tekrar analiz edilmez |

**Hepsi not_run.** Ölçüm: açık soruların coverage'ı, doğru hedef eşleme/yanlış karar, unknown/clarification sayısı, receipt→association→resolution gecikmesi, duplicate etkiler, insan düzeltme yükü, toplam çağrı/token. Yanlış korunan karar kabulü engelleyici regresyondur; sayısal kalite ve bildirim eşikleri ölçüm/owner kapısında seçilir. Gerçek bu sohbetin gecikmesi için süre veya başarı yüzdesi uydurulmaz.

## 6. Q14-A: bağımsız proje ilerlerken belirsiz bölüm kaybolmaz

**2026-10-13 — ürün davranışı kabul edildi, runtime uygulaması bekliyor.** Bir projenin bilinen/valid review taslağı gösterilirken diğer projenin “B” cevabı hangi soruya ait olduğu belirsiz kalabilir. İkinci proje iptal veya tamamlandı sayılmaz. Kaynak cevap ve izinli olası sorular tutulur; Inbox'ta `Needs clarification`, kalıcı soru ID'si, gereken yanıt, bağlı task'lar ve bekleme nedeni görünür. Yalnız karara bağlı iş bekler, aynı projenin bağımsız işleri de ilerleyebilir.

Geç cevap aynı soru/seçenek sürümüne bağlanır ve authority/freshness yeniden kontrol edilir; cevap önceki bağlamdan kopmuşsa tahmin edilmez. Cevap yoksa kayıt açık kalır; timeout otomatik karar/iptal değildir. Reminder policy ayrı; bu seçim mesaj gönderme veya yeni model bütçesi izni değildir. Teknik output tipi/schema hatası insanın belirsiz tercihi gibi sorulmaz, teknik düzeltme işine gider. [Q14 seçenekleri ve kayıt](../delivery/decision-brief.md). Yeni bağımsız proje ayrımı ve explicit geç reply association [T03x](../quality/project-review.md) içinde20 yeni fixture testle sınandı. Sabit descriptor/report var; durable Inbox/gerçek capture/authority henüz uygulanmadı. P0 whole-output validator ve ilk failed run aynı kalır.

## Güncel kod sınırı — 2026-10-13

[Manuel runtime](../quality/pending-question-runtime.md): izinli UI sorusu/seçenek snapshot ve exact revision yanıtı kalıcı audit history içinde tutulur. Open/Answered ve Selected/Stale/Unmatched/Conflict/Duplicate ayrı; kaynak manual_ui, assistant transcript veya host authority değildir. Canonical Decision/Approval binding, iptal/superseded, orphan yeniden eşleme, agent proposal/capture ve tam ASK/LATE kabulü henüz uygulanmadı. Ana T13 veya T13e bu kısmi dilimle Done değildir.

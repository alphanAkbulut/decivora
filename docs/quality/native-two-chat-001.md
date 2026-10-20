# Native A/B: gerçek Codex pencerelerinden sınırlı capture sonucu

**20 Ekim 2026 — yalnız capture katmanı doğrulandı.** Kullanıcı iki yeni sentetik Codex sohbetinin10'ar turunu iki geçişte yerelTEST'e almayı onayladı; ardından örnek cümleleri normal chat input'larına kendisi yazdığını bildirdi. Yalnız bu iki thread okundu. [Makine makbuzu](native-two-chat-001-results.json), [önceden hazırlanan plan/kök neden](native-two-chat-review.md).

## Gözlenen sonuç

| Kontrol | Native A | Native B |
|---|---:|---:|
| Kaydedilen normal kullanıcı mesajı |1|1|
| Kaydedilen assistant metni |2|2|
| İlk geçiş yeni kaynak |3|3|
| İkinci geçiş yeni kaynak |0|0|
| Bekleyen tur / assistant |0/0|0/0|
| Seçilen metadata penceresinde eski tur dışarıda |false|false|
| Desteklenmeyen item |0|0|
| Dışlanan private/tool item gövdesi |1|1|
| Diğer sohbetin ham metni yakın bağlamda |hayır|hayır|

Toplam **6public kaynak:2human +4assistant**. Her beklenen insan cümlesi kendi thread/turn/item kimliğiyle kaydedildi. İlk ve ikinci geçiş arasında2saniye beklendi; ikinci geçiş item/source tekrar üretmedi. Sonraki DBreopen readback yine6kaynak döndürdü. İşlem hatası yok; hem AhemBkendi capture kaydını korudu.

İlk byte-exact expected-string karşılaştırması başarısız oldu: iki kullanıcı mesajında da beklenen cümlenin yanında2boundarywhitespace karakteri bulunuyordu. Bu doğrulama bulgusu saklandı: byte_exact=false, trimmed expected_line_match=true. Kaynak metni veya hash'i trim edilerek değiştirilmedi. Mesaj içeriği eksik veya değişmiş diye raporlanmadı; kayıtlı metadata bu ayrımı gösterir.

## Neyi ispatladı?

- Araçla gönderilmiş prompt'u kullanıcı saymadan, gerçek normal `userMessage` iki seçilmiş sohbetten alınabildi.
- Aynı içerik/turn/item adları başka thread'e ait diye kaynaklar karışmadı; origin iki thread için ayrı kaldı.
- `DialogueReviewService.prepare` mevcut kaynaklardan yalnız kendi thread'inin yakın geçmişini hazırladı; diğer thread'in rawmetni eklenmedi.
- Kaynaklar kalıcıDB'de ve tekrar okumada korundu; checkpoint devamı mükerrer oluşturmadı.

Bu gerçek host deneyi, önceki authoredAPIreplay veya fakeprotocoltesti değildir. Fakat **kesintisiz streaming/closed-appizleme/tümgeçmiş garantisi değildir**: transport stored-item pagination kullandı, terminal metinleri aldı; genel coverage hâlâpartial. Bu küçük pencerede omitted/pending olmaması bütün host geçmişinin tamamlandığı anlamına gelmez. Çalışan sürüm/kurulum başka cihaz için otomatik kabul sayılmaz.

## Neyi henüz sınamadı?

Model çağrısı **0**, kaynak dışarı gönderimi0, yeni canonicalTask0, otomatik durum değişikliği0. Görev çıkarımı yapılmadığından Native B'nin “başladım” ifadesi gerçek modelle A'da oluşturulmuş aynıTask'a bağlandı denemez. Aynı projenin canonicalTask/soru paylaşımı yerel controlledtestte doğrulandı; bu native deney henüz semantik+review halkasını kapatmadı. [İki katmanın farkı](native-two-chat-review.md).

Sadece iki capture geçişi izinliydi; tamamlandı. Her iki binding ayrı disconnectaudit'iyle kapatıldı, restart sonrası yetki reddi kontrol edildi. Aynı kaynağa yeni polling, yeni mesaj okuma veya APIpaylaşımı bu tek izinle yapılamaz. Kalıcı kaynaklar izin verilen yerel incelemede durur; çalışan LOCAL/öncekiTESTDB değiştirilmedi.

## Güvenlik ve kanıt

İzole `native-two-chat-001` TESTalanı, scopedowner, owner-onlyDB/manifest kullanıldı. Kullanıcı/assistant text dışında reasoning, araç çıktısı veya başka sohbet okunup modele taşınmadı; private item gövdeleri capture katmanına döndürülmedi. Ham transcript,DB,privateplan/hostthreadIDlistesi/credential repoya eklenmedi. Publicmakbuz alias/sayı/hash ve sınırları içerir; privatecapture/planSHA256türev kanıtıdır, şifreleme değildir.

Bu tur capture kodu değişmedi; yeni runtime özelliği için test tekrarı yapılmadı. Doğrulama gerçek native iki geçiş + yerel kaynak/context/DBreopen + consumedbinding kontrolüdür. Belge/anchor/progress kontrolleri ve değişen mevcut şemanın offline render'ı ayrıca yapılır. Önceki658runtime/49repotesti tarihsel kod tesliminin kanıtıdır; bu tur yeniden koşuldu iddiası yok.

## Sıradaki kapı

Yalnız kaydedilmiş sentetik kaynakların exactallowlist'i için ayrı model paylaşım/bütçe izniyle A'nın görev önerisini çıkar; somut öneriyi ayrı insan review'uyla kaydet; sonra B'nin başlangıç beyanını yeni canonicalTaskcontext'iyle modelle değerlendir. Sonuç önce öneridir; ayrı review olmadan taskstatus değişmez. Kullanıcıya karar verdirmeden scriptedapply'ı insan kabulü gibi gösterme. Kaynak yakalama onayı bu model kapısını açmaz; süre/token/çağrı/bütçe sınırı sabitlenmeden paidcall yok.

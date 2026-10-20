# İlk grubun onaylı devamı ve netleştirme geliştirmesi

**Takip:** Bu rapor8yeni isteğin tarihsel makbuzudur. Sonradan onaylı J04iki turda soru/validation bulgusuyla durdu; [güncel takip](dialogue-batch-001-j04.md). Aşağıdaki0/6ve frozen sayıları bu rapor anına aittir, eski receipt değiştirilmedi.

**20 Ekim 2026.** Kullanıcı iki kararı açıkça onayladı: ayrı teslim/alt görev istenmedikçe netleştirme mevcut Task'a bağlı tutulacak; J02_m4'ün2250microusd rezervi korunarak aynı istek tekrarlanmadan ilk grubun kalan14mesajı işlenebilecek. [İlk rapor](dialogue-batch-001.md) ve private receipt'leri değiştirilmedi. [Devam makine raporu](dialogue-batch-001-continuation-results.json).

## Güncel dört-case görünümü

| Case | Alınan model yanıtı | Sonuç |
|---|---:|---|
| J01 |6/6 | Task/aynı-ID/status/false-Done dar kontrolleri geçti; canonical In Progress |
| J02 |5/6 | m5'te doğru Task In Progress oldu; m6 yanlış renk-task başlangıcı üretmedi. Eski m2 netleştirme Task önerisi ve m4 unknown korunuyor; case eksik |
| J03 |5/6 | İki farklı Task yakalandı; belirsiz “ona başladım”da seçim yapılmadı; açık geri yükleme cevabında doğru ID In Progress önerildi. m6 generation timeout; case eksik |
| J04 |0/6 | Yeni unknown duraklaması nedeniyle henüz çalışmadı |

Devamda en fazla14yerine **8dispatch/16HTTP bütçe payı** kullanıldı;7yanıt alındı,1unknown. İlk denemeyle toplam18dispatch,16yanıt ve2unknown vardır. Native Codex capture değil, authored synthetic dialogue kaynağıyla production extraction/review yoludur. Kontroller AI-authored taslak; human gold/holdout veya genel başarı yüzdesi değildir.

## Devam mekanizması

`scripts/run_dialogue_batch.run(...continuation_approval=..., continuation_base_sha256=...)` yalnız incelenmiş ilk raporun hash'ine ve J01=6/J02=4 snapshot'ına uyar. J01'i yeniden çalıştırmaz; J02'de m5'ten devam eder, aynı Task/AC/history korunur. İlk rapor üzerine yazılmaz; ayrı `continuation-report.json` kaydedilir. Kısmi crash klasörü sessiz tekrar başlatılmaz. Completed continuation raporunu tekrar okumak model çağırmaz.

Root `accept_reserved_unknown` yalnız onaylanan J02_m4 için uygulandı: actual=null,2250rezerv ve exact-payload retry reddi korundu. Bütçe/çağrı/expiry yenilenmedi. Sonradan oluşan J03_m6 unknown bu onayla otomatik kabul edilmedi.

**Ölçüm sürümü:** Devamdaki8exact request'in şeması/talimatı önceki baseline olarak kaldı; `clarification_proposals` alanı henüz bu isteklere dahil değildi. Geliştirilen netleştirme kodu bu eski çıktıları düzeltmiş veya yeniden başarılı saymış gibi sunulmaz. Payload hash'leri tur bazında makine raporunda; eski puanlama değiştirilmedi.

## B001-F2 devamı — bu kez timeout sınıfı doğrulandı

J03_m6 için input-count2002başarılı; diagnostic phase=`generation`, code=`provider_timeout_unknown`, usage=null. Bu, istemcinin45saniyelik socket beklemesinin aşıldığını gösterir. Sağlayıcı iş yükü, ağ veya model üretim süresi arasında kök neden ayrıştırılmış değildir. Generation'ın sağlayıcıya kesin ulaşmadığı veya sıfır harcadığı söylenmez.

**Düzeltme:** Yeni HTTP işlemlerinin socket beklemesi120saniye yapıldı. Bu gerçek provider deadline veya uçtan uca süre garantisi değildir; bounded socket ayarıdır. Model, token/para/HTTP tavanı ve no-retry değişmedi. Timeout yine unknown+rezerv+duraklama üretir. Eski çağrı yeniden gönderilmedi.120saniye ayarının gerçek çağrıda yeterliliği henüz ölçülmedi; offline HTTP kontrolü doğru değeri ve güvenli hata sınıflarını doğrular.

## B001-F1 ürün kararı uygulandı

[Kod ve UI sözleşmesi](dialogue-status-runtime.md#mevcut-göreve-bağlı-netleştirmeler): kaynaklı `clarification_proposals` yalnız context'te bulunan exact Task'a yönelir. İnsan review'u Open netleştirme açar; bu yeni Task, karar uygulaması veya otomatik blocker değildir. Task detayı ve soru kutusunda görünür; açık ihtiyaç metrikte sayılır. İnsan resolution'ı revision kontrolüyle kaydeder; kaynağı ve geçmişi korunur. Kaynak Task'ın Sources görünümüne bağlanır.

- Yeni model talimatı ayrı teslim/alt görev açıkça istenmedikçe scope clarification'ı Task olarak çoğaltmamayı söyler.
- Eski çıktılar import edilebilir; yeni published JSON schema runtime ile aynı tutuldu. Eski model çıktısı yeniden yazılmadı.
- Netleştirme kayıtları sonraki context'e durum/revision ile girer; seçenek uydurulmaz.
- Bu yeni kuralın **gerçek model uyumu henüz tekrar ölçülmedi**; ilk baseline dört-case tamamlandıktan ve owner review'dan sonra ayrı trial gerekir. Sırf prompt eklendi diye başarı iddiası yok.
- Seçeneksiz bağımsız proje sorusu ile bir Task'a bağlı scope clarification farklıdır. B001-F3'ün bütün açık soruları kapsayan ölçümü bu teslimle tamamlanmış değildir. Serbest metin cevaplarını otomatik netleştirmeye bağlayıp kapatma da yok; mevcut çözme yetkisi insandadır.

## Maliyet ve korunan rezervler

Devamın7bilinen yanıtının yerel model fiyat tahmini2506microusd ($0.002506); yeni J03_m6 rezervi2250microusd ($0.002250). Artış4756microusd ($0.004756). İlk grupla toplam bilinen16yanıt26013input+4764output=30777reported token; iki başarısız generation'ın tokenları unknown.

Ortak root48dispatch/96HTTP bütçe payı; known59332+held6750=66082microusd (**$0.066082**).3USD tavan ve önceki expiry aynı. Üç unknown kaydı vardır: ilk iki rezervli devam ayrı onaylandı; üçüncü yeni unknown nedeniyle root şimdi frozen. Fatura doğrulanmadı. Tek başına bakiye varlığı yeni risk onayı değildir.

## Sonraki somut kapı

Öneri: yeni J03_m6 için de2250rezerv tutulup actual=null bırakılırsa, yalnız **J04'ün6mesajı** sonlu planda çalıştırılabilir. Max6generation+6count; Luna,10kinput/2koutput, aynı3USD/expiry; yeni120saniye socket ayarı. J02_m4 veya J03_m6 tekrar edilmeyecek, J05 başlamayacak. Bu yeni unknown için owner kararı gerekir; henüz uygulanmadı. İlk grup tamamıyla başarılı sayılmayacak: iki teknik eksik ve seçilmiş yeni ürün kuralına göre eski clarification bulgusu korunur.

## Doğrulama sınırı

646runtime ve49repo/tracker testi geçti. Fake HTTP continuation testi incelenmiş base hash'ini,14üst sınırını, eski unknown turu atlamayı ve eski raporun değişmemesini kontrol eder. Netleştirme integration kontrolleri literal quote/Task, stale workflow, idempotent review, history/restart/resolve ve audit rollback'i sınar. Gerçek tarayıcı kontrollü JSON import ile yeni Task üretmeden Open→Resolved akışını ve yenilemede korunmasını doğruladı. Bunlar yeni prompt'un semantik model başarısı değildir.


**Hazır fakat çalıştırılmamış kapı:** İncelenmiş continuation report hash'ine bağlı `owner-approved-reserve-retained-J04only6` yolu yalnız J04 için6üst sınırı uygular; J02/J03 unknown turları ve önceki raporlar korunur. Fake HTTP testinde iki ayrı duruş sonrası10+8+6akışı ve toplam24üst sınırı geçti. Bu kapı için yeni root risk onayı henüz yoktur. Sonraki J04 çalışması güncel şema/talimat sürümüyle ayrı raporlanmalı; önceki baseline'la aynı prompt sürümü gibi gösterilmemeli.

# Gerçek LOCAL arayüzü — iki sohbet, tek görev ve açık kapsam sorusu

**20 Ekim 2026 · Sprint1 · T09/T13/T17/T19/T21/T22.** Bu, önceki CLI/service pilotundan ayrı olarak gerçek yerel ürün arayüzü üzerinden yürütülen dar kullanıcı yolculuğudur. Kaynaklar daha önce insan tarafından yazılmış iki sentetik Codex sohbetidir; bu tur yeni sohbet veya yeni mesaj üretilmedi. İki sohbet tekrar ve yalnız birer kez okundu. Manuel Task metni girişi, fixture/model yanıtı import'u veya doğrudan domain status uygulaması kullanılmadı.

## Aşamalar ve sonuç

| Aşama | Gerçek gözlem | Durum |
|---|---|---|
| Kaynak seçimi | LOCAL'de ayrı Atlas UI Pilot projesi; iki exact sohbet için birer read, son en fazla 10 tur; consent ve ayrı read düğmeleri | Dar kabul geçti |
| Capture | 2 human + 4 assistant = 6 kaynak; pending turn0, unsupported item0, older history omitted=false | Geçti; coverage yine partial |
| Model paylaşımı | A ve B için exact yerel preview, ayrı source-sharing onayı ve ayrı activation/Analyze | Gerçek provider ile geçti |
| A anlam çıkarımı | Tek Task önerisi; “henüz başlamadım” için start veya Done önerisi yok | Bu tek örnek geçti |
| İlk Task incelemesi | Owner AC/DoD onayı yerine bağlı netleştirmeyi seçti; tek Task To Do, tek Opened soru, contract yok | Seçim atomik kaydedildi |
| B anlam çıkarımı | Yeni Task yok; A'daki aynı Task ID'sine In Progress önerisi | Bu tek örnek geçti |
| Başlangıç uygulaması | Kapsam sorusu açık; AC/DoD onaylanmadı; kullanıcı durum uygulamasını onaylamadı | Uygulanmadı; To Do korundu |
| Doğrulanmış tamamlama | Hedef dosya/test kanıtı ve Done kabulü yok | not_run |

İstekler yalnız seçili human mesajını, kendi sohbetindeki tek kısa önceki assistant metnini ve ilgili pilot proje bağlamını içerdi. A'da canonical Task yoktu; B'de owner'ın kaydettiği tek Task ve bağlı kapsam sorusu vardı. Başka sohbetin ham geçmişi eklenmedi. Kaynak actor metadata'sı insan onay yetkisi yerine kullanılmadı. Ham transcript, private DB, key, bağlantı kimlikleri ve exact payload dosyaları public rapora taşınmadı.

## İzinler, karar ve gerekçe

- Kaynak izni `call_ca22e9a4d20a48a9b91f9c887095480d`: yalnız iki sentetik chat, birer read, son en fazla10tur, yerel kayıt. Okuma sonrası iki bağlantı disconnected; yeni okuma yapılmadı.
- Model izni `call_4ad07ebb5f7941bd820a79928d0610c9`: yalnız iki sentetik human kaynak/ilgili context, Luna, en fazla2model+2sayım, 10kinput/2koutput, bu kabulde$0.01 ve aynı birikimli$3. Retry/model yükseltme yok. İki istek kullanıldı; bu dar izin tüketildi.
- İlk Task kararı `call_48c7e954d9954405a58984edb9636344`: kullanıcı **“Kapsamı netleştirme sorusuyla kaydet”** seçti. Önerilen AC/DoD kabul edilmiş sayılmadı. Contract üretmek veya B'nin start iddiasını otomatik uygulamak bu seçimi ihlal ederdi; açık soru ve incelemedeki durum önerisi korundu.

Bu sonuç “sistem her sohbeti otomatik takip ediyor” veya MVP tamamlandı anlamına gelmez. Kaynak seçimi, capture, exact paylaşım, aktivasyon ve Task review insan adımlarıydı. Sürekli capture ve yeni mesajlara izinli otomatik paylaşım politikası/günlük kullanım kabulü hâlâ ayrı işlerdir. İki dar cümle genel semantik başarı oranı değildir; J04 soru yakalama bulgusu bu testle çözülmedi.

## Token ve maliyet

| İstek | Input | Output | Output içindeki reasoning | Toplam | Yerel tahmin |
|---|---:|---:|---:|---:|---:|
| A | 1738 | 265 | 70 | 2003 | $0.000350 |
| B | 1953 | 280 | 84 | 2233 | $0.000259 |
| Toplam | 3691 | 545 | 154 | 4236 | $0.000609 |

Reasoning output'un alt kategorisidir; toplam ve maliyete ikinci kez eklenmedi. Geliştirme sohbetinin reasoning ayarı API'ye aktarılmadı. Model-token/cache kategorilerine dayalı tahmin; nihai provider faturası değildir. İki generation ve iki sayım başarılı döndü, unknown0/retry0. Birikimli root54dispatch/108HTTP bütçe payı; bilinen tahmin$0.061145 + önceki3unknown için korunan$0.006750 = $0.067895. Kalan yerel ihtiyatlı pay$2.932105,46model/92HTTP; hesap bakiyesi değil. [Makine özeti](native-ui-journey-001-results.json).

## Bulgu UI-J01 — yeni önizlemeyi eski onay gizliyordu

İncelemede `renderSourceSharing` kaynak ID'sine ait herhangi bir eski onayı “saved” sayıyordu. Aynı kaynağın output sınırı değiştirilip yeni exact önizleme hazırlanırsa eski onay yeni onay formunu gizliyordu. Backend eski izni yeni payload için geçerli saymıyor; arayüzde yenileme yolu kapanıyordu.

Düzeltme: hazırlanmış bir önizleme varken saved makbuzu aynı **plan ID**'sine de bağlı olmalı. Önceki audit/grant korunur; yeni plan yeni, işaretlenmemiş onay kutusu ister. Kaynak, model, context veya politika kapısı gevşetilmedi. Mevcut source-sharing tarayıcı testi değişen output sınırıyla genişletildi: düzeltme öncesi yeni checkbox beklemesi başarısız oldu; düzeltme sonrası yeni grant ID ve ayrı onayla tüm Task/AC akışı geçti. Sahte provider1, gerçek dış çağrı0. Gerçek A/B yolculuğu ile sentetik UI regresyonu ayrı kanıtlardır.

## Açık kalan ve sonraki adım

Owner'ın seçtiği kapsam sorusu gerçek açık kayıttır; gereksiz tamamlanmadı etiketi değildir. Soru cevaplanıp AC/DoD ayrıca onaylanmadan başlangıç uygulamasını tamamlanmış saymayız. B'nin önerisi geçmişte korunur; kapsam değişirse eski öneriyi current saymak yerine güncel insan işlemi/yeniden değerlendirme gerekir. Bunun için otomatik yeni API izni veya tekrar verilmedi.

20 hedefli runtime testi (11sharing/9native UI connection) ve genişletilmiş gerçek tarayıcı regresyonu geçti. Diyagramlardaki ilk-scope clarification dalı ve ayrı capture→sharing→activation→dispatch sınırları bu gözlemle uyumludur; Mermaid kaynağı değişmedi, render yeniden yapılmış sayılmadı. Ana görev kapanış sayıları değiştirilmedi.


**Kapanış kontrolü:** İki model aktivasyonu ayrı Pause komutuyla duraklatıldı; worker kapalı, iki native bağlantı disconnected. Sayfa reload sonrası tek To Do Task, tek Opened kapsam sorusu ve aynı Task ID için tek start önerisi korundu;390px görünümde yatay taşma yok. Yeni pilot dışındaki 12 project-scoped tablonun satırları önceki yedekle aynı; owner yetkisine yalnız bu yeni pilot proje eklendi. Diğer proje içerikleri değiştirilmedi. Dört assistant kaynak capture edilmiş fakat bu iki-human model iznine dahil olmadığından analiz edilmedi; UI'daki kalan Waiting for model sayısı gizli hata veya yeni okuma izni değildir.

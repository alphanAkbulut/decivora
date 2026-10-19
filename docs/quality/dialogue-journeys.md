# Çok turlu diyalog: bağlam, görev kimliği ve ilerleme

**20 Ekim 2026 — çalışan iz backend'i ve yerel çok turlu kontroller; yeni semantik API ölçümü yapılmadı.** Tek mesajın capture edilmesi, konunun anlaşılması veya bütün projenin doğru izlenmesi değildir. Önceki [native pilot](codex-e2e-001.md) aynı task için üç gerçek model sonucu içeriyordu; yine de kısa, operatör yönlendirmeli bir örnekti. Genel diyalog başarısı diye sunulamaz. Eski altı oturumluk corpus da bütün ürün yolunun native/semantik kabulü değildir.

## Ayrı ölçülecek üç katman

| Katman | Soru | Kanıt |
|---|---|---|
| Capture | Kullanıcı/assistant metni, rolü ve kaynak kimliği kaybolmadan alındı mı? | Native receipt, checkpoint, tekrar/eksik sayfa, completion ve maskeleme kontrolü |
| Anlam / bağlam | Konu, kapsam, yeni iş veya mevcut task bağlantısı, karar ve doğru durum beyanı anlaşıldı mı? | Çok turlu gerçek model çıktısı; bağımsız etiketle karşılaştırma. Scripted output bunu ispatlamaz |
| Uygulama / doğrulama | Öneri doğru insan incelemesinden geçti mi, doğru task değişti mi; gerçek kabul kanıtı var mı? | Kaynak/context/workflow revision, review receipt, canonical durum ve AC/DoD sonuçları |

## Diyalog kaydı zaten nerede?

SQLite'daki mevcut `audit` kaynakları: `conversation_imported` maskelemeden geçmiş public metin, source hash, proje, capture/thread/turn/item/rol ve alım zamanı taşır. `dialogue_review_prepared` kaynak+context digest'ini; analysis kayıtları öneri/başarısızlığı; `conversation_candidates_applied` aday→oluşturulmuş/bağlanmış record'u; `conversation_status_reviewed` öneri→review→task ilişkisini korur. Workflow ve kriter kanıtı ayrıca canonical kayıttır. Modelin düşünce zinciri veya özel tool çıktısı tutulmaz.

Bu kaynak hafızası **operational log değildir**. Hata loguna konuşma metni, credential veya raw model yanıtı kopyalanmaz. Source hash kimlik/bütünlük işaretidir, şifreleme değildir. SQLite kullanımı tek başına disk şifrelemesi veya ekip izolasyonu sağlamaz; mevcut owner-only yerel sınır geçerlidir. Capture/DB/backup/egress gizlilik ve yetki kuralları aynen devam eder. Saklama/purge politikası [storage sözleşmesindedir](../architecture/storage-memory-capacity.md); bu teslim yeni bir retention süresi kabul etmez.

Yeni `DialogueTraceService.view(scope, project, source_ids=[...])`, mevcut kayıtları **salt okunur** birleştirir: kaynak kimlikleri/rol/256karakter masked excerpt, analysis state/context hash, adaylar, gerçek record bağlantıları, reported stage, review state/history, güncel canonical stage ve verification sonucu. Yeni transcript tablosu veya ikinci görev otoritesi oluşturmaz.1–25seçili source; proje yetkisi gerekir, bilinmeyen/izinsiz kaynak reddedilir. Anahtar, raw model output veya başka sohbetin gövdesi eklenmez. API/model çağırmaz, onay vermez, task durumunu değiştirmez.

**UI sınırı:** Bu teslim backend sorgusudur; yeni bir timeline ekranı eklenmedi. Conversations ekranındaki mevcut kaynak/review kartları korunur. Bu sorguyu ayrı yetkili diyalog inceleme ekranına bağlama işi T14/T17 kapsamındadır; varmış gibi sunulmaz.

## Context'in güncel sınırları

- Native capture için mevcut Task/Decision/PendingDecision, soru/seçenek/revision, ilişki ve gerekçeler hazırlanır; task IDs ve workflow revision'ları taşınır.
- Aynı proje/capture/thread/source surface/**kurulum profili** içinden en fazla6önceki kaynak metni, toplam6000UTF-8byte verilir. Byte/mesaj sınırında kesilen veya dışarıda kalan geçmiş açık belirtilir. Profil eşitliği bu teslimde sorguya eklendi.
- Bu komşuluk **alım sırasıdır**, kanıtlanmış tam konuşma kronolojisi değildir. Gecikmiş/eski mesaj otomatik son durum otoritesi olamaz; stale workflow uygulaması reddedilir.
- Onaylanıp kaydedilmiş görev kısa kaynak penceresinden çıktıktan sonra yapılandırılmış proje hafızasında kalır. Eski konuşmada kalmış, henüz kaydedilmemiş kapsamın pencereden düşmesi gerçek risktir. Konuya dayalı uzun geçmiş retrieval/özetleme bu kodla çözülmüş sayılmaz.
- Manual paste varsayılanında bu native komşuluk yoktur. Kullanıcı birden fazla mesajı açık role/kimliklerle aktarmazsa eksik bağlam tahmin edilmez.
- Bir görev oluşturma, kapsam/AC onayı, işe başlama, bitirme iddiası ve doğrulanmış Done ayrı adımlardır. “Testleri çalıştırmadım” kaybolmadan Done **beyanı** yakalanmalı; task otomatik Done olmamalı.

## Çeşitlendirilmiş senaryolar

[Kaynaklar](../../examples/dialogue-journeys/sources.json) ve [ayrı AI-authored beklenti taslakları](../../examples/dialogue-journeys/oracles.json):12case/78mesaj. Gerçek kullanıcı verisi yok. Oracle metni modele verilmez. Bunlar insan onaylı gold veya sealed holdout değildir; bütün semantik run'lar `not_run`.

| Case | Ne zorlanıyor? | Kritik yanlış sonuç |
|---|---|---|
| J01 | Kapsam→görev→başlama→test edilmemiş bitirme | Her mesajda yeni task açmak / false Done |
| J02 | Konu değiştirme ve işe geri dönme | Renk konusunu yedek işinin ilerlemesi saymak |
| J03 | Benzer iki görev ve belirsiz zamir | “Ona” ifadesiyle ID tahmin etmek |
| J04 | İki açık soru sonrası gecikmiş cevap | Yanlış soruyu/versiyonu cevaplamak |
| J05 | Karar değişimi ve eski gerekçeler | Görev/ilişki geçmişini silmek, iptal etmek |
| J06 | İki işin bağımsız ilerlemesi | Bir işin durumunu diğerine geçirmek |
| J07 | Alıntı, olumsuzluk ve gelecek koşulu | Gerçekleşmemiş Done/start üretmek |
| J08 | Bitirme beyanından sonra başarısız test | Önceki iddiayı doğrulanmış Done tutmak |
| J09 | Subagent teslimi ve ana görev kabulü | Agent run finished = ürün kabulü saymak |
| J10 |6mesajdan uzun ara ve eski işe dönüş | Kesilmiş geçmişi eksiksiz bağlam gibi sunmak |
| J11 | Geç ulaşan eski durum ve stale review | Son gelen mesaj kazanır diyerek geriye almak |
| J12 | Sırlar ve proje/kaynak sınırı | Ham sır saklamak veya başka projenin taskını eşlemek |

## Çalıştırılan yerel akış

`tests/runtime/test_dialogue_journeys.py` gerçek capture/context/import/review/workflow kodunu kontrollü protocol sayfaları ve **scripted model cevaplarıyla** çalıştırır:

1.6mesaj: kapsam→task oluşturma→ayrı test operatörü AC/DoD onayı→konu değiştirme→aynı task In Progress önerisi→ayrı review→test edilmemiş Done beyanı. Doğrudan Done reddedildi; aynı task In Progress kaldı.
2.Uzun arada önceki raw metin6mesaj sınırından çıktı; onaylanmış Task context'te kaldı; omission işareti doğru.
3.Unicode uzun metinde6000byte sınırı ve truncation doğrulandı.
4.Aynı capture/thread kimliğine sahip başka kurulum profilinin metni context'e karışmadı.
5.Trace maskeli, scope/bound kontrolü var ve hiçbir audit yazmıyor. Restart sonrası lineage eşit.

İlk test kurulumu acceptance sözleşmesi olmadan start denedi ve `acceptance_required` ile durdu. Guard gevşetilmedi; senaryoya ayrı operatör kapsam onayı eklendi. Bu, sohbetin görev üretmesiyle işe başlamaya hazır olmasının da ayrı olduğunu gösterir.

Mevcut native pilot DB üzerinde yeni trace sorgusu8kaynak/1record bağlantısı/2durum önerisi döndürdü; yeni kaynak okuması/API çağrısı0. Private trace receipt SHA256 `9c26f80824e4478ce9c34983994cd936323710bafc34be1bd1cbc4dd6eae86d8`. Raw trace/DB GitHub'a konmadı. Bu sorgu önceki model sonuçlarını gösterir; yeni gerçek diyalog semantik ölçümü değildir.

## Gerçek model değerlendirme planı

Önce J01/J02/J03/J07 ile küçük, sonlu bir batch; sonra geç cevap/karar etkisi/uzun geçmiş ve eşzamanlılık. Her turda yalnız o ana kadar izinli kaynaklar ve **o anki** canonical snapshot verilir. Gelecekteki mesajlar ve oracle modele sızmaz. Scripted test operatörü onayı kullanılırsa bu ayrı işaretlenir; modelin kendi cevabı doğruluk etiketi yapılmaz. Hiç onaylanmamış ve hiç başlamamış görevler de negatif örnektir.

Tur bazında source hash, context hash, payload/model/fiyat revision, truncated/omitted işaretleri, sonuç, eşlenen task ID, literal quote, review sonucu, canonical durum ve token/maliyet/latency kaydedilir. Diyalog bazında: doğru konu/kapsam korunumu, doğru mevcut task ID, yanlış yeni task sayısı, status-claim doğruluğu, belirsizlikte çekimserlik, false Done/yanlış iptal, düzeltme süresi ve toplam harcama karşılaştırılır. Eksik/unknown yanıtlar paydadan gizlenmez; insan düzeltmeleri ayrıca sayılır. Önceden bağımsız etiket ve değerlendirme kuralı olmadan başarı yüzdesi yayınlanmaz.

Mevcut3USD root, source/context izni, HTTP/token tavanları ve unknown rezervi korunur. Bu belge model çağrısı veya süresi dolan manifesti yenileme izni değildir. Semantic runner'ın bu12yolculuğu sıralı ve snapshot'lı yürütmesi ve bağımsız etiket review'u hâlâ açıktır. Yeni case sayısı tek başına MVP tamamlanması veya model doğruluk kanıtı değildir.


**Teslim kontrolü:**632runtime testi geçti.12input/oracle hash eşleşmesi ve78mesaj doğrulandı; doküman/link/anchor kontrolü geçti. Mevcut56Mermaid kaynağı değiştirilmedi; bu teslimde yeniden render edilmiş diye sayılmaz. UI kodu değişmedi; yeni bir timeline ekranı veya browser akışı test edildiği iddia edilmez.

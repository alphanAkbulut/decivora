# MVP test yürütme planı

**20 Ekim 2026 · Plan, tam ürünün başarı raporu değildir.** [Sprint planı](../delivery/sprint-plan.md) uygulanırken kullanılacak yürütme sırasıdır. Senaryo otoritesi [V01–V28](verification.md), ürün kabulü [AC-01–AC-14](../product/mvp.md), semantik örnekler [J01–J48](dialogue-journeys.md) olarak kalır. Bu belge yeni feature/task veya izin oluşturmaz.

## Başlangıç kanıtı ve açık kapı

| Katman | Kayıtlı sonuç | Kanıtın sınırı |
|---|---|---|
| Runtime | Son kayıtlı koşuda 692 test geçti | Otomatik kod testleri; bütün modeller/hostlar veya 14 ürün AC'si geçmiştir demek değil |
| Repo/tracker | Son kayıtlı koşuda 49 test geçti | Takip, kapanış ve değerlendirme araçları; ürün semantik kabulü değil |
| Diyagram | 34 belgede 63 Mermaid render; hata 0 | Görsel/sözdizim kanıtı; runtime davranışı değil |
| Native capture | 3 sınırlı okuma, duplicate 0, Stop/Disconnect/reload geçti | Aynı mevcut mesajlar; okumalar arasında yeni mesaj gelmedi |
| İki sohbet + gerçek model | A yeni Task, B aynı ID için başlangıç önerisi; owner güncel kapsam ve In Progress uyguladı | Dar iki sentetik kullanıcı mesajı; Done yok, kriterler not_run |
| Çok turlu model | J01 dar 6/6; J02/J03 kısmi; J04 soru kaçırma ve unsupported_question reddi | J04 düzeltmesi gerçek modelle yeniden doğrulanmadı; J05–J48 not_run; AI oracle taslakları insan-gold değildir |

Referanslar: [düzenli capture kodu](scheduled-capture-runtime.md), [native sonuç](scheduled-native-001.md), [UI/model sonucu](native-ui-journey-001.md), [J04](dialogue-batch-001-j04.md), [diyagram kayıtları](diagram-render-results.json). Yukarıdaki sayılar önceki koşuların kaydıdır; bu plan yazılırken bu suite'ler yeniden çalıştırılmış sayılmaz.

## Yürütme sırası

| Aşama / sahip | Test akışı | Beklenen ve ölçülecek sonuç | Bugünkü durum / izin |
|---|---|---|---|
| Sprint 1 / T09,T13,T19,T21,T22 | Yeni kaynak → exact paylaşım → aktivasyon → kuyruk → worker → Inbox → ayrı insan apply | Uygun kaynak bir kez; işlenmeyen/gap görünür; grant/hash/revision eşleşir; izin yoksa dispatch 0 | Parça kanıtları var; birleşik ilerleyen mesaj kabulü açık. Yerel fixture/API fake yanıtı yeni ücret gerektirmez |
| Sprint 1 / T17 temeli,T24 | Aktif capture sırasında gerçek A sohbetine yeni kullanıcı mesajı; ardından aynı proje B'de başlangıç; ayrı projede benzer isim | Gerçek yeni mesaj alınır; aynı görev ID'sine öneri; duplicate 0, proje sızıntısı 0; tamlık sınırı görünür | Yeni mesajlı native kabul not_run. Testten önce exact kaynak/süre/read ve egress kapsamı ayrı |
| Sprint 1 / T13,T21,T23 | Stop/disconnect/revoke/expiry; eşzamanlı manual read; crash/restart; pending/unknown | Yeni yetkisiz read/dispatch 0; toplam sayaç reset olmaz; önceki commit korunur; otomatik kör retry/restart yok | Yerel kontroller var; birleşik günlük koşuya alınacak. V01/02/11/13/19–21/23/27 |
| Sprint 2 / T09,T10,T13,T20 | Önce açık J04 hatası; ardından J05–J08, J09–J12 ve kalan gruplar dörder | Soru ID/sürüm eşleşmesi; belirsizde abstain; konu değişimi yeni görev şişirmemeli; durum ve lifecycle ayrı; Done beyanı doğrulama değil | Gerçek model grupları açık; her grubun rapor/owner incelemesi tamamlanmadan sonraki grup yok |
| Sprint 2 / T20 | Blocked süresi >7 gün, tam eşik, bilinmeyen başlangıç; unblock/reblock | Uyarı yalnız doğru yaşta; bilinmeyen yaş uydurulmaz; tekrar kontrolü duplicate uyarı oluşturmaz; geçmiş korunur | Yerel timer kodu var; günlük UI/iş akışı kabulüne bağlanacak |
| Sprint 3 / T11,T12,T13,T14,T20 | Karar değişimi; AND/OR/unknown; etki preview sonrası yeni edge/scope; Cancelled/obsolete | OR gerekçesi varken yanlış iptal 0; tarihçe silinmez; stale apply reddi; graph/board/timeline aynı revision | Çekirdek yerel kanıt var; birleşik kabul açık. V04–08/15/22/28; AC-05/06/09 |
| Sprint 3 / T14,T15 | “Yükledim/bitti” → izinli dosya hedefi → güncel içerik/hash/test → AC/DoD | Yalnız varlık kanıtı Done değildir; eksik/başarısız/eski kanıt görevi tamamlamaz; bütün zorunlu kriterler güncel doğrulanır | Genel hedef/verifier ve tam kabul açık. V08/24; AC-04/08. Gerçek hedef kapsamı ayrıca |
| Sprint 3–4 / T23,T15 | Backup→restore→replay; disk hatası; export/purge/retention; aktif iş recovery | Aynı canonical digest; LLM/komut tekrar çalışmaz; sırlar export/logda yok; silinen kaynak restore ile erişime geri dönmez | Alt küme testleri var, tam operasyon kabulü açık. V14/17/19/26/27 |
| Sprint 4 / T16,T18,T22 | Desteklenen gerçek Codex ve Claude kurulumu; gerçek MCP istemcisi; yeni chat context paketi | İki ayrı adapter raporu; rol/thread/item/cursor/coverage; izinli kısa ve kaynaklı bağlam; başka proje yok | Codex çekirdeği geçti; Claude/MCP gerçek host kapıları açık. AC-01/02/11/14 |
| Sprint 4 / T19,T20,T24 | Temiz yerel kurulumdan günlük kullanım; klavye/dar ekran/locale; Board/Graph/Timeline | Kullanıcı sohbeti bağlar, öneriyi inceler, aynı görevi ilerletir, gerekçe/test sonucunu görür; restart sonrası korunur | Yerel UI testleri var; tam pilot ve 14-AC matrisi açık |
| Değişen risk yüzeyi / T21,T23,T24 | Sentetik uzun konuşma + yoğun ilişki + olay geçmişi + eşzamanlılık; auth/privacy/budget saldırıları | p50/p95/p99, throughput, bellek, DB boyutu, kuyruk yaşı ve hata/gap kaydı; ACL/sır sızıntısı 0 | Mevcut performans raporları baseline; değişen birleşik akışta hedefli tekrar. LLM gecikmesi/token maliyeti ayrı ölçülür |

Sayısal performans SLO'su bu planla kendiliğinden kabul edilmiş sayılmaz. Aynı makine/veri/sürümle önceki baseline'a göre değişim raporlanır; ürün eşiği veya risk kabulü gerekiyorsa owner'a sunulur. Sonraki faz ekip/cloud testleri MVP tek-kullanıcı kabulüne tamamlandı diye yazılmaz.

## Her semantik grubun protokolü

1. Dört case'in input ve bağımsız beklenen sonucunu model çağrısından önce sabitle. Her tur için görev/soru/karar kimliği, öneri ile canonical state, status/lifecycle/blocker, beklenen abstain, kaynak quote ve sürüm ayrı olsun. Oracle extractor'a verilmez. İnsan tarafından incelenmeyen AI taslak etiketleri gold sayılmaz; önceki H1–H4 kararları yeniden sorulmaz.
2. Kaynak + prompt/schema + model/reasoning + code revision + context seçimini kaydet. Aynı vakada farklı model/prompt sonucu yeni koşudur; eski failure üzerine yazılmaz.
3. Her mesaj sonrası capture receipt, proposal, review ve uygulanan state'i ayrı karşılaştır. Kaynak quote/konumunu kodla doğrula. Modelin kendi gerekçesi tek başına doğruluk oracle'ı değildir.
4. Precision/recall için bağımsız etiketli item sayısı ve payda; aynı-task eşleme doğruluğu, geç cevap/soru sürümü doğruluğu, durum önerisi doğruluğu, abstain/yanlış karar, gecikme, düzeltme adımı/süresi ve token/maliyet kaydet. Küçük n için genellenmiş kalite yüzdesi verme.
5. Her tur pass/fail/unknown/not_run olarak raporlanır. Timeout/unknown maliyeti 0 sayılmaz ve blind retry yapılmaz. Yerel testlerden geçen talimat düzeltmesi gerçek modelde passed sayılmaz.
6. Grubu bulgu → kök neden kanıtı → kod/talimat düzeltmesi → hedefli regresyon → kalan risk ile kapat. Sonraki gerçek gruba owner incelemesi ve geçerli exact ücret/veri izniyle geç. Her başarısızlık sınırsız araştırmaya dönüşmez.

## Başlatma, durma ve release koşulları

- Yerel sentetik testler izole TEST veritabanında yapılır; gerçek çalışma alanının snapshot/backup'ı korunur. Test fixture'ı gerçek host/model/target kanıtı diye sunulmaz.
- Gerçek read/model/verifier öncesi seçilmiş kaynak/hedef, açık kapsam, izin süresi ve harcama rezervasyonu geçerli olmalı. Plan veya API bakiyesi izin yerine geçmez. Eski dar trial izinleri tüketildi; toplam usage/unknown rezervleri sıfırlanmaz.
- Sır sızıntısı, proje izolasyonu ihlali, yetkisiz dispatch/komut, false Done, yanlış obsolete veya stale onayın uygulanması o akış için durdurucu bulgudur. Gösterim hatası/partial kapsam ile veri kaybı ayrı sınıflanır. Kayıtlı kabul düşürülmez.
- Exit: ilgili sprintin çalışan yolculuğu ve negatifleri kanıtlanır; kritik açıklar çözülür. MVP release ancak mevcut AC-01–AC-14'ün her biri versioned evidence ile karşılandığında, T15/T24 kapıları ve iki coding adapter kabulü tamamlandığında yapılır. Çözülmemiş gerçek model/J04 hatası kapatılmadan ilgili yetenek verified ilan edilmez.

## Sonuç kaydı ve tekrar sıklığı

Her rapor: senaryo/tur/Task/AC ID, ortam, revision/hash, test verisi sınıfı, beklenen/gerçek, kaynak/öneri/uygulama/kanıt ayrımı, status, süre, çağrı/token/known-cost/unknown-reserve, hata katmanı, aksiyon ve kanıt yolu. Raw sohbet/anahtar/DB dump'ı yayınlanmaz; yetkili maskeli trace kullanılır.

Her kod diliminde ilgili pozitif/negatif ve etkilenen regresyonlar; entegre sprint tesliminde birleşik UI yolu; release adayında tam ilgili suite, yük/restore/temiz kurulum ve gerçek host kabulü çalışır. Değişmeyen bütün suite'leri her mesajda yeniden çalıştırmak gerekmez. Plan/test sayısı ürün teslimi değildir; rapor açık kalan kod ve kabul sahiplerini mevcut backlog'a bağlar.

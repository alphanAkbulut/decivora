# Onay ve görsel çalışma alanı

## Ana deneyim

Project selector yanında capture sağlığı ve son işlenen kaynak görünür. Ana ekran **Review Inbox** olur. Board yürütmeyi, Graph neden/ilişkiyi, Timeline tarihçeyi açıklar. Decision Pending kuyruğu normal yapılacak işlerden ayrı gösterilir. Knowledge Health; unreviewed, disputed, stale, blocked ve unknown sayılarını ayrı tutar.

Kullanıcı normal sohbet eder. Sistem session sonunda veya anlamlı değişiklikte hazırlanmış kart sunar; sürekli modal açmaz. Sonradan bakılacak kararlar erteleme nedeni/tarihi veya bağımlı olay ile saklanır. Bildirimler tekrar eden gürültü üretmez; uygulanacak politika kullanıcı tercihine bağlıdır.

## Örnek etki kartı — tasarım, canlı UI değil

**Karar:** Yerel depolamayı SQLite'a taşı.

**Mevcut → önerilen:** Markdown canonical storage → SQLite canonical storage.

**Neden:** Onay bekleyen yeni mimari öneri. **Etkiler:** Sync obsolete adayı; watcher import için korunacak. **Belirsizlik:** İlişkisiz export işinin gerekçesi eksik. **Kaynak:** Mesaj ve evaluation bağlantısı. **Kanıt:** İlgili requirements/ADR revisions. **Geri alma:** Yeni telafi olayı; sonraki etkiler tekrar değerlendirilir.

Seçenekler: **Onayla / Koru / Ayrı incele / Ertele / Reddet / Karşılaştır**. Hazır başlık, description ve test edilebilir AC okunabilir; metin girmek zorunlu değildir. Sistem ürettiği AC'nin öneri olduğunu ve gereksinimden nereden türetildiğini gösterir.

## Otonomi politikası

| İşlem | İlk sürüm varsayılanı |
|---|---|
| Kaynak capture, exact duplicate provenance, teknik checkpoint | Yetkili binding içinde otomatik |
| Yeni fikir/task taslağı, açıklama önerisi | Otomatik proposal; aktif scope olmaz |
| Düşük riskli metadata tamamlama | Politika sınırında; anlam/scope değişmez |
| Implementation claim | Otomatik gözlem, verified değil |
| Önceden yetkilendirilmiş AC verifier sonucu | Policy karşılanırsa otomatik verification |
| Kabul edilmiş karar/AC/scope değişimi; ambiguous merge; obsolete/cancel | Kullanıcı onayı |
| Publish, ücret, dış sisteme yazma, erişim değişikliği | Ayrı açık yetki; task onayı bu yetkiyi otomatik vermez |
| Geçmişi fiziksel silme | Normal agent erişiminde yok |

## Toplu onay güvenliği

Bağımsız işlemler seçilebilir. Birbirine referans veren operations aynı atomic group olarak gösterilir; kullanıcı birini kaldırırsa kalan set yeniden doğrulanır. “Approve All” otomatik yeni seçim veya timeout onayı değildir. Onay `actor + workspace/project + changeset digest + base revisions + knowledge revision + policy revision + authz revision` taşır. Stale onayda diff yeniden hazırlanır. Double click aynı sonucu döndürür. Reddetme nedeni hazır seçeneklerden seçilebilir; açıklama opsiyoneldir.

Klavye erişimi, focus sırası, ekran okuyucu etiketleri, yalnız renge dayanmayan durum, uzun başlıklar ve dar ekranda review akışı P1b testine dahildir. Graph'ın erişilebilir liste alternatifi bulunmalıdır. Board'da drag-and-drop tek işlem yolu olmamalıdır.

## Bekleyen kararın yaşamı

PendingDecision: açık soru, alternatifler, öneri/gerekçe, source, owner, blocker links ve durum (open/deferred/resolved/cancelled). Belirsiz “sonra bakarız” ifadesi source olarak saklanabilir; konu belirlenmeden committed decision olmaz. Resolved olduğunda gerçek Decision ID'sine bağlanır. Kullanıcının bir kartı açması “değerlendirildi/onaylandı” anlamına gelmez.

[Geç cevap sözleşmesi](pending-questions-and-late-answers.md): konu/chat/run değişse de açık soru kaybolmaz. Seçili soru/explicit ID varsa geç cevap aynı kayda bağlanır; yalnız “A” iki soruya uyuyorsa odaklı netleştirme gerekir. Yanıt alınması, ilişkilendirilmesi ve geçerli karar olması ayrı; eski seçenek veya iptal sonrası yanıt otomatik uygulanmaz. Pending Inbox ve bounded devam paketleri cevapsız soruları gösterir; hatırlatma kanalı/sıklığı açık kalır. LATE-01–08 planlıdır, uygulanmadı.

## Birden fazla reviewer ve agent

### Subagent soruları ve karar yönlendirmesi

Bilgi isteği, danışma, yetki içi teknik seçim ve insan onayı gerektiren karar [agent işletim sözleşmesinde](../architecture/agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider) ayrıdır. Her soru PendingDecision değildir; yalnız gerçek karar ihtiyacı bu kuyruğa bağlanır. Teknik soru önce güncel yetkili kayıttan/ilgili agent'tan çözülür. Parent agent kanıt/seçenek toparlayabilir; insan scope/AC/izin kararını veremez.

İnsan kartı şunları gösterir: soran agent/run ve task, eksik bilgi veya karar, öneri/alternatifler, kaynaklar/karşı görüş, bekleyen işler, bağımsız ilerleyebilecek işler, gereken karar yetkisi ve cevabın kapsamı. Ekipte yetkili reviewer'a, tek owner pilotunda kullanıcıya gider. Aynı konu aynı yetkili kapsamda tek soruya toplanır; özgün talepler kaybolmaz. Yanıtı kimin verdiği ve hangi revision'a uygulandığı tarihçede kalır.

`Yanıt geldi`, `insan onayladı`, `host'a teslim edildi`, `iş yeniden başladı` ve `task doğrulandı` farklı göstergelerdir. Cevap yokken veya süre dolunca onay varsayılmaz. Önceden geçerli bir karar varsa kullanıcı tekrar soruyla yorulmaz. Soru resolved olsa da diğer blocker/izin/kanıt kapıları korunur. ASK-01–08 planlı kontrollerdir; UI henüz yoktur.

[Yetki tasarımındaki](../architecture/identity-access.md) rol/grant ve kaynak görünürlüğü server'da kontrol edilir. Ekipte onay ekranı öneren insan/agent, kimin adına çalıştığı, bağımsız reviewer gereksinimi ve erişim eksikliğini gösterir. Aynı insanın iki oturumu bağımsız review değildir. İlk bireysel pilot açık single-owner policy ile ilerler; gelecekteki iki insan şartı bugünkü kullanımı kilitlemez. Yetki veya kaynak ACL değişince eski approval yeniden değerlendirilir.

## İlişkiler, iptal ve geçmiş

[Graph deneyimi](graph-experience.md) task bağlamını, typed edge'leri, AND/OR gerekçelerini ve before/after görünümünü tanımlar. İptal edilen task'ın bağlantıları silinmez; task durumu ayrı rozettir. Sona erdirilen ilişki aktif traversal'dan çıkar fakat geçmişte kesikli çizgi ve açık durum/gerekçe etiketiyle gösterilir. Çarpı/renk tek başına bilgi taşımaz. Q04 ile güncel işler + seçili işin bağlamı seçildi; tam geçmiş ayrıca açılır. [İşin olgunlaşma ve kabul görünümü](task-context-and-acceptance.md) AC/DoD ve test raporunu tamamlar.

## Yüksek tüketim riski için ayrı karar

[Token riski onay kartı](token-risk-and-approval.md) yapılacak iş, risk nedeni, tahmin/unknown, uygulanabilir üst sınır, toplam retry/child tüketimi, kalan bütçe ve alternatifleri gösterir. Yetkili insan sınırlı planı onaylar, küçültür, aşamalı plan ister, erteler veya reddeder. Task onayı veya parent agent cevabı bu onayın yerine geçmez; hard-cap/egress/izin değişimi ayrı kapıdır. Aynı geçerli planın her küçük adımında tekrar soru yok; kapsam/sınır değişirse yeni assessment gerekir. Yeni dispatch onay beklerken kalıcı kaynak ve task korunur. T19b/TRA-01–10 planlıdır, çalışan UI değildir.

## Gerçek seçim ve uygulama durumu

[GAP review](intent-to-reality-gap.md) dört ayrı bilgiyi gösterir: öneri, güvenilir insan seçimi, generated artifact, hedef uygulama assessment'ı; AC/DoD kabulü ayrıca. “B'yi seçiyorum” kapsamı/kimliği açıksa mevcut policy'yle kaydedilir; her açık seçim tekrar sorulmaz. Yeni soru/sessizlik/agent özeti onay değildir.

Minimal eylemler izinli kontrol, kanıtla yükledim, henüz uygulamadım, öneriyi seçmedim ve ertele olabilir; varsayılan otomatik kontrol veya yeni erişim onayı kabul edilmedi. Sonraki iş bu uygulamaya gerçekten bağlıysa odaklı durum sorusu; bağımsız işleri bloke etme. Hedef durumunu görmek yeni LLM çağrısı gerektirmez.

## Q14-A — bağımsız review ve Proje 2 bekleme kartı

**2026-10-13 · seçilen MVP davranışı; UI henüz uygulanmadı.** Proje 1'in geçerli bağımsız taslağı incelemeye açılır. Proje 2'deki belirsiz cevap `Needs clarification` kartında kalır: kaynak cevap, soru/seçenekler, yetkili responder, bekleyen task'lar ve bağımsız ilerleyen işler gösterilir. Proje tümüyle frozen/cancelled/Done olmaz. Kullanıcı yanıtı ertelerse soru Inbox ve devam paketinde korunur. Geç yanıt aynı question/presentation revision'a bağlı kontrol edilir; ardından gereken karar/onay/verification adımları ayrıca geçer. Otomatik uygulama veya host resume desteği varsayılmaz.

Bozuk schema/alan tipi teknik hata kartıdır; anlam sorusu diye kullanıcıya devredilmez. Retry/düzeltme yetkili bütçe ve policy içinde; başarısız çıktı ve geçmiş saklanır. Global durum hatalı/eksik bölüm varken tamamen başarılı değildir. Ortak envelope/access kimliği belirsizse kısmi review yapılmaz, bağlı atomic gruplar bölünmez. [Q14 kabul kaydı](../delivery/decision-brief.md), [kalıcı soru sözleşmesi](pending-questions-and-late-answers.md); P0 [T03x](../quality/project-review.md) fixture review/descriptor katmanı tamamlandı; gerçek UI/durable Inbox ve production T13/T19/T24 testleri bekliyor.


## 14 Ekim 2026 — Workflow ve tanıdık UI güncellemesi

[Yerel workflow/UI](../quality/workflow-ui-runtime.md) uygulandı: Review inbox / Board-List / end-panel / source-history / current human-verification. ASK/LATE tam agent/host UI hâlâ açık; manuel soru/cevap/lifecycle/decision UI artık var. Stage değişimi scope/ücret/erişim onayı değildir; ayrı digest/authority kuralları korunur.

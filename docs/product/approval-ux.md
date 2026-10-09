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

## Birden fazla reviewer ve agent

### Subagent soruları ve karar yönlendirmesi

Bilgi isteği, danışma, yetki içi teknik seçim ve insan onayı gerektiren karar [agent işletim sözleşmesinde](../architecture/agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider) ayrıdır. Her soru PendingDecision değildir; yalnız gerçek karar ihtiyacı bu kuyruğa bağlanır. Teknik soru önce güncel yetkili kayıttan/ilgili agent'tan çözülür. Parent agent kanıt/seçenek toparlayabilir; insan scope/AC/izin kararını veremez.

İnsan kartı şunları gösterir: soran agent/run ve task, eksik bilgi veya karar, öneri/alternatifler, kaynaklar/karşı görüş, bekleyen işler, bağımsız ilerleyebilecek işler, gereken karar yetkisi ve cevabın kapsamı. Ekipte yetkili reviewer'a, tek owner pilotunda kullanıcıya gider. Aynı konu aynı yetkili kapsamda tek soruya toplanır; özgün talepler kaybolmaz. Yanıtı kimin verdiği ve hangi revision'a uygulandığı tarihçede kalır.

`Yanıt geldi`, `insan onayladı`, `host'a teslim edildi`, `iş yeniden başladı` ve `task doğrulandı` farklı göstergelerdir. Cevap yokken veya süre dolunca onay varsayılmaz. Önceden geçerli bir karar varsa kullanıcı tekrar soruyla yorulmaz. Soru resolved olsa da diğer blocker/izin/kanıt kapıları korunur. ASK-01–08 planlı kontrollerdir; UI henüz yoktur.

[Yetki tasarımındaki](../architecture/identity-access.md) rol/grant ve kaynak görünürlüğü server'da kontrol edilir. Ekipte onay ekranı öneren insan/agent, kimin adına çalıştığı, bağımsız reviewer gereksinimi ve erişim eksikliğini gösterir. Aynı insanın iki oturumu bağımsız review değildir. İlk bireysel pilot açık single-owner policy ile ilerler; gelecekteki iki insan şartı bugünkü kullanımı kilitlemez. Yetki veya kaynak ACL değişince eski approval yeniden değerlendirilir.

## İlişkiler, iptal ve geçmiş

[Graph deneyimi](graph-experience.md) task bağlamını, typed edge'leri, AND/OR gerekçelerini ve before/after görünümünü tanımlar. İptal edilen task'ın bağlantıları silinmez; task durumu ayrı rozettir. Sona erdirilen ilişki aktif traversal'dan çıkar fakat geçmişte kesikli çizgi ve açık durum/gerekçe etiketiyle gösterilir. Çarpı/renk tek başına bilgi taşımaz. Q04 ile güncel işler + seçili işin bağlamı seçildi; tam geçmiş ayrıca açılır. [İşin olgunlaşma ve kabul görünümü](task-context-and-acceptance.md) AC/DoD ve test raporunu tamamlar.

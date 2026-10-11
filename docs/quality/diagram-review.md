# Diyagram tutarlılık incelemesi

**Güncel inventory: 15 belgede 34 Mermaid şeması — tasarım revizyonu 03.** Önceki kayıtlar aşağıda tarihsel doğrulama kapsamıyla korunur; eski sayım veya render sonucu değişen çizim için başarı kanıtı değildir.

## Güncel inventory — 2026-10-11

<!-- diagram-inventory:start -->
| Belge | Mermaid sayısı |
|---|---:|
| [README.md](../../README.md) | 1 |
| [ROADMAP.md](../../ROADMAP.md) | 2 |
| [docs/architecture/connection-and-context.md](../../docs/architecture/connection-and-context.md) | 1 |
| [docs/architecture/data-relationships.md](../../docs/architecture/data-relationships.md) | 3 |
| [docs/architecture/diagrams.md](../../docs/architecture/diagrams.md) | 13 |
| [docs/architecture/execution-and-integrations.md](../../docs/architecture/execution-and-integrations.md) | 3 |
| [docs/architecture/identity-access.md](../../docs/architecture/identity-access.md) | 1 |
| [docs/architecture/logging-audit.md](../../docs/architecture/logging-audit.md) | 1 |
| [docs/architecture/overview.md](../../docs/architecture/overview.md) | 1 |
| [docs/architecture/storage-memory-capacity.md](../../docs/architecture/storage-memory-capacity.md) | 1 |
| [docs/delivery/team-data-plan.md](../../docs/delivery/team-data-plan.md) | 1 |
| [docs/product/decision-map.md](../../docs/product/decision-map.md) | 1 |
| [docs/product/graph-experience.md](../../docs/product/graph-experience.md) | 2 |
| [docs/product/intent-to-reality-gap.md](../../docs/product/intent-to-reality-gap.md) | 2 |
| [docs/product/current-direction.md](../../docs/product/current-direction.md) | 1 |
<!-- diagram-inventory:end -->

İçerik incelemesi tüm 34 kaynağı kapsar. Bu revizyonda README (1), roadmap (2), overview (1), atlas bağlam/engine (2) ve decision map (1) olmak üzere **7 mevcut blok güncellendi**. Güncel yönün yatırım akışı ve ER-03 **2 yeni bloktur**; önceki GAP akışları (2) inventory'ye dahil edildi. 25 eski blok kaynak düzeyinde değişmedi; yalnız tarihler veya sürüm görünümü için yeniden çizilmedi.

Onay snapshot/AND-OR/iptal/replay, source/target yetki sınırı, log/storage ve ekip/admin akışları korundu. Atlas ER'si ER-03 ile tamamlanır; bütün relation alanlarını her diagramda tekrar etmek gerekmez. Source alımı, application assessment ve AC/DoD completion aynı durum değildir. İlk prototip tam atlası çalıştırmış sayılmaz.

**Bu revizyonun render kontrolü:** `aaf9cbef1c5a387848a6d75975482b9d09ae9e4a` ref'inde 15 belgedeki 34 Mermaid çıktısının tamamı GitHub Preview üzerinden kontrol edildi. Render edilmiş iframe etiketleri/SVG çıktıları okundu; parse/syntax/render hata mesajı bulunmadı. Güncel roadmap'in faz/yatırım çizimi ayrıca açılıp ekran görüntüsüyle incelendi. Bu kontrol bütün ekran boyutlarında layout, ürün UI veya runtime testi değildir; aşağıdaki önceki sonuçlara dayanmaz.

**2026-10-10.** İnceleme öncesinde 11 belgede 20 Mermaid diyagramı vardı. Hepsi son kararlarla içerik düzeyinde karşılaştırıldı; tamamı zaten günceldi denemez. Aşağıdaki düzeltmelerle 25 diyagram oldu. Şemalar tasarımdır; runtime, tam UI veya benchmark kanıtı değildir.

Referanslar: DEC-15/1C, DEC-16 öneri statüsü, DEC-17 ve yöntem ayrımı; Q04/05 graph/profil tercihi; run/task ve ASK yetki/delivery ayrımı; tenant/ACL, token policy, yeni admin/operasyon isteği. Diyagram okları tek başına yetki veya uygulanmış capability göstermez.

| Dosya | Diyagram sayısı | İnceleme ve sonuç |
|---|---:|---|
| [README](../../README.md) | 1 | Agent çalışma olayları ve task doğrulaması ayrıldı; atlas indeksi güncellendi |
| [Roadmap](../../ROADMAP.md) | 2 | P1b minimal yerel yönetim, P4 ekip/operasyon ayrımı eklendi; faz ve kanıt kapıları korundu |
| [Mimari atlas](../architecture/diagrams.md) | 13 | İlk 8 gözden geçirildi: kaynak/engine, tenant kapsamlı ER, budget/izin kontrollü worker güncellendi. Snapshot onayı, AND/OR, state machine ve replay geçerli kaldı. Run, soru, blocker, admin ve incident için 5 şema eklendi |
| [Genel mimari](../architecture/overview.md) | 1 | MCP query/proposal yanlışlıkla capture ingress'e bağlıydı; ortak policy ve yetkili read yolu düzeltildi |
| [Bağlantı/context](../architecture/connection-and-context.md) | 1 | Capture, MCP ve insan UI ayrımı geçerli; model okları bütçe/izin sözleşmesiyle okunur, değiştirilmedi |
| [Kimlik/yetki](../architecture/identity-access.md) | 1 | İnsan üyelik/grant ve agent run yetki şeması geçerli; yeni admin atlasıyla tamamlandı |
| [Log/audit](../architecture/logging-audit.md) | 1 | Yerel atomik audit ve dış delivery ayrımı geçerli; incident ayrı atlas şemasında |
| [Depolama/hafıza](../architecture/storage-memory-capacity.md) | 1 | Genel payload TTL oku 1C arşivini yanlış kapsayabilirdi; geçici payload ve izinli arşiv ayrıldı, kapasitede sessiz silme yerine intake durması gösterildi |
| [Ekip/veri planı](../delivery/team-data-plan.md) | 1 | Tek insan/çok-agent ve yerel yönetim; P4 operasyon/kota kapıları yansıtıldı |
| [Karar haritası](../product/decision-map.md) | 1 | Eksik DEC-15/16/17 eklendi; kabul/proposed ayrımı, yöntemden bağımsız öncelik ve admin önerisi açık |
| [Graph deneyimi](../product/graph-experience.md) | 2 | İptal/ended ilişkilerin tarihçesi, başka OR gerekçesi, insan review ve stale preview güncel; değiştirilmedi |

## Doğrulama kapsamı

- Bütün Mermaid kaynakları ve ilgili metin sözleşmeleri okundu; inventory sayımıyla 11 dosya / 25 diyagram doğrulandı.
- `python3 scripts/check_docs.py` yerel bağlantı, fence, JSON ve kapsam/görev/AC bütünlüğünü kontrol eder; Mermaid parser veya görsel render testi değildir.
- İçerik commit'i `10bbb0f3a1df5e2dec599f01773372a3a9fb2642` GitHub'a kaydedildi; değişen 16 dosya aynı ref'ten geri okunup yerel içerikle birebir karşılaştırıldı.
- GitHub Preview tarayıcı kontrolünde 11 belgedeki 25 Mermaid çıktısının tamamının iframe içindeki render edilmiş etiketleri okundu; parse/syntax/render hata mesajı bulunmadı. Atlasın yönetim şeması ayrıca ekran görüntüsüyle incelendi. Bu, tüm ekran boyutlarında görsel UX testi veya ürün UI testi değildir.
- Son doküman kontrolü: 64 Markdown, 417 yerel bağlantı; 32 scope, 30 ana görev, 14 MVP kriteri korundu. ADM-01–10 kabul tanımları ayrıca sayıldı; henüz runtime'da çalıştırılmadı.
- ADM-01–10 ve mevcut ASK/AGT/FLOW/MU senaryoları uygulama sırasında çalıştırılacak; bu inceleme onları passed yapmaz.

## Sequence ve ER genişlemesi — 2026-10-10

| Yeni belge | Şema sayısı | Kapsam |
|---|---:|---|
| [Tetikleme ve iletişim](../architecture/execution-and-integrations.md) | 3 sequence | Task sonucu/verification, koşullu LLM ve insan kararı, dış API teslimi/unknown/callback |
| [DB ilişkileri](../architecture/data-relationships.md) | 2 ER | Kaynak/binding/izin makbuzu; task/run/AC/DoD/evidence ilişkileri |

Önceki 25 Mermaid kaynağı bu genişlemede değiştirilmedi. Yeni belgeler TRG-01–12, iletişim matrisi, deney aralıkları ve veri bütünlüğü sözleşmeleriyle çapraz okundu. Yeni toplam 30; bunun 6'sı sequence, 3'ü ER. SEQ-01–08 ve DBR-01–06 planlı runtime kabulüdür; çizim testi bunları passed yapmaz.

Doğrulama: ilk GitHub render denemesinde üç sequence'in mesaj noktalı virgülleri parse hatası üretti; mesaj ayırıcıları düzeltildi. `5a6e24fdb2e00102fb282b49c4bd3502890df59a` içeriğinde üç sequence ve iki ER'nin render edilmiş iframe etiketleri tarayıcıdan okundu; syntax/render hatası kalmadı. Task sonucu sequence'i ayrıca ekran görüntüsüyle incelendi. Önceki 25 için önceki render kanıtı ve kaynak değişmezliği geçerlidir; bu tur bütün ekran boyutlarında görsel test yapılmadı.

Değişen 13 dosya GitHub'dan aynı ref ile geri okunup yerel içerikle eşleşti. Doküman kontrolü geçti: 66 Markdown / 461 yerel bağlantı; 32 scope / 30 ana görev / 14 MVP kriteri korundu. 8 SEQ ve 6 DBR kabul ID'si tekil/sıralı kontrol edildi; bunlar çalışan API, DB migration veya scheduler test sonucu değildir.

## Bakım uygulaması

Karar değişikliği yapan görev ilgili metin, diyagram, backlog ve acceptance etkisini birlikte değerlendirir. Değişmeyen diyagramı sırf tarih yenilemek için çizme. Etkilenen graph/node/edge etiketleri, phase ve accepted/proposed statüsü kontrol edilir; Mermaid render sonucu ayrı raporlanır. Bütün diyagramların sonsuza kadar güncel kalacağı garantisi verilmez.

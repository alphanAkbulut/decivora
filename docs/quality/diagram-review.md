# Diyagram tutarlılık incelemesi

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
- GitHub render kontrolü bu değişikliklerin yüklenmesinden sonra kaydedilecek; bu satır tek başına başarılı render iddiası değildir.
- ADM-01–10 ve mevcut ASK/AGT/FLOW/MU senaryoları uygulama sırasında çalıştırılacak; bu inceleme onları passed yapmaz.

## Sonraki değişikliklerde bakım kuralı

Karar değişikliği yapan görev ilgili metin, diyagram, backlog ve acceptance etkisini birlikte değerlendirir. Değişmeyen diyagramı sırf tarih yenilemek için çizme. Etkilenen graph/node/edge etiketleri, phase ve accepted/proposed statüsü kontrol edilir; Mermaid render sonucu ayrı raporlanır. Bütün diyagramların sonsuza kadar güncel kalacağı garantisi verilmez.

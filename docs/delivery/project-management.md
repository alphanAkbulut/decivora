# Kısa proje yönetim planı

**Aşama: P0 — Discovery / Product Definition.** Ürün çalışmıyor. Amaç: AI konuşmalarını yaşayan, karar farkındalıklı hafızaya dönüştürmek; eskimiş işleri açıklanabilir biçimde yeniden değerlendirmek ve manuel yönetim yükünü azaltmak. Tam kapsam korunur; ilk kullanılabilir teslim P1b MVP'dir.

## Başarı ve teslim sınırı

İlk değer: bir mimari değişiklikte tek gerekçeli eski işi obsolete adayı yapmak, alternatif gerekçeli işi korumak, historical done'ı silmemek ve kullanıcıya hazır toplu onay sunmak. İlerleme belge/kod miktarıyla değil [MVP kabul kriterleri](../product/mvp.md) ve [ölçüm kapılarıyla](../quality/measurement.md) değerlendirilir.

| Rol | Sorumluluk / karar yetkisi |
|---|---|
| Product owner: kullanıcı | Ürün yönü, scope/öncelik, maliyet, public/lisans ve mimari trade-off kararları |
| Uygulayıcı: yetkilendirilmiş geliştirici/agent | Sıradaki küçük işi hazırlama/uygulama, seçenek ve kanıt sunma; kendine scope onayı veremez |
| Reviewer/verifier | AC ve invariant kontrolü; bir agent'ın kendi iddiasını bağımsız kanıt saymaz |

Bunlar görev rolleridir; kurulmuş ayrı bir ekip veya atanmış çalışan iddiası değildir.

## Faz ve karar kapıları

| Faz | Somut teslim | Devam etmek için gerekli kanıt |
|---|---|---|
| P0 | Corpus, gerçek adapter capability ve alternatif karşılaştırması | T01–T03; build/extend ve stack kararı |
| P1a | Import→impact→approval→event→verification teknik dilimi | T15; atomicity, isolation, false-done, graph race ve replay |
| P1b | İki coding adapter, minimal MCP, review/board/graph/timeline, temel ekonomi | T24; 14 AC, holdout ve kullanıcı pilotu |
| P2 | Chat sürekliliği, daha iyi semantik, GitHub read, panel | Platform/kalite kanıtı; fallback açık |
| P3 | Cost report, yetkili dış yazma, release hazırlığı | İzin, lisans, isim, kurulum/demo kanıtı |
| P4 | Takım/cloud/ticari sınırlar | Talep, isolation/sync tasarımı ve owner kararı |

Tarih ve bütçe henüz taahhüt edilmedi. Bağımlılık kapısını geçemeyen özellik full scope'ta kalır; sınırlı pilot diye adlandırılır. Güncel durumun otoritesi [status](status.md), uygulanabilir işin otoritesi [backlog](backlog.md).

## Çalışma ritmi

1. Her çalışma oturumunda status ve sıradaki hazır görevi oku. Varsayılan WIP bir iş; büyük T02/T03 gibi satırları yüzey/deney bazında küçük alt dilimlere ayır.
2. Başlamaya hazır olma: bağlı görevler tamam, ilgili ADR kararı açık, input/fixture hazır, AC gözlenebilir, izin ve maliyet sınırı belli. Eksik karar varsa somut seçenek hazırla; alakasız iş başlatma.
3. Uygula: küçük değişiklik, ilgili sözleşme ve test. Aynı bulguyu yeni task olarak tekrar üretme. Fark edilen kapsam dışı işi öneri olarak kaydet.
4. Bitiş: AC kanıtı, ilgili regresyon, doküman/status güncellemesi, revision/sonuç kaydı ve gerekli remote doğrulama. `not_run` veya `unknown` başarı değildir.
5. Oturum sonunda kısa devir: ne değişti, hangi kanıt var, hangi risk/karar bekliyor, sonraki tek küçük adım. Faz sonunda go/no-go review; takvim hatırlatıcısı kendiliğinden kurulmaz.

## Değişiklik ve risk yönetimi

Yeni fikir → mevcut scope/kararla karşılaştır → delta ve etki → gerekiyorsa owner onayı → ADR/scope/backlog birlikte güncelle. Eski karar ve görevi silerek geçmişi yeniden yazma. Öncelikli riskler: kaynak erişimi, yanlış obsolete/verified, capture kaybı, onay yorgunluğu, token maliyeti ve lisans. Ayrıntılar [risk kaydında](../governance/risks.md); bekleyen seçimler [açık kararlarda](../governance/open-decisions.md).

**Sıradaki üç iş:** T01 sentetik corpus ve oracle; T02 Claude Code/Codex yüzeylerini izole fixture'da gözlemleme; T03 Cortex/Tracker/mai-mcp/Beads alternatiflerini aynı senaryoda karşılaştırıp build/extend kararı hazırlama. Doküman denetiminin tamamlanması bu üç işi yapılmış saydırmaz.

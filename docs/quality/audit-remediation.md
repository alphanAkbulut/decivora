# Audit bulguları ve uygulanan düzeltmeler

**2026-10-11 · P0 / kontrollü deney · ürün MVP’si değil.** Kullanıcı raporların private GitHub’a alınmasını ve önerilerin uygulanmasını istedi. Tam vizyon, MVP ve sonraki fazlar korunur. P0’da Python standart kütüphanesi/SQLite yöntemi seçildi: ek paket/ücretli API olmadan mevcut Spike-0 ile aynı ortamda yeniden üretilebilir davranış sınamak için. Alternatif production stack’ler ve native/extend yolları T03c’de açık kalır. Bu deney için geçici yöntemdir; production ADR veya bağımsız ürün yatırımı kararı değildir.

> [!IMPORTANT]
> Fixture testi, gerçek coding host başarısı veya semantik model kalitesi değildir. İnsan gold review, gerçek model ve native karşılaştırma tamamlanmadan T01/T02/T03 kapanmaz.

## Kanıt zinciri

[Dış audit karşı değerlendirmesi](external-audit-review.md) → [orijinal Spike-0 incelemesi](spike0-audit.md) → bu güncel düzeltme kaydı → [kontrol sonuçları](audit-remediation-results.json). İlk iki inceleme **düzeltme öncesi** snapshot’ı anlatır; bugünkü durumun otoritesi bu kayıt ve [status](../delivery/status.md) / [backlog](../delivery/backlog.md) içindedir.

Orijinal paket hash’i ve bildirilen cloud commit sınırı [provenance kaydında](../../spikes/spike-0/PROVENANCE.md); değiştirilmeyen dış n=1 çalışma [real-run-001](../../spikes/spike-0/results/real-run-001.md) içindedir. Ham gerçek transcript/credential veya yerel test loglarının kişisel yolları yayınlanmadı. Yalnız sentetik fixture, kaynak kodu ve redakte sonuçlar eklendi.

## Dört öneri: ne uygulandı, ne kaldı?

| İş | Uygulanan somut teslim | Kapanış için kalan |
|---|---|---|
| 1. Restore bağımlılığı | **T07c** erken çekirdek DB+payload backup/restore olarak tanımlandı; T15/T15a buna bağlı. T23a migration/privacy/export ve operasyonu tamamlar. Typed deneyde DB backup/replay digest eşitliği geçti | P1a production T07c, payload manifest/eksik veri/schema ve crash sınamaları TODO; kalite kapısı kaldırılmadı |
| 2. Etiket inceleme + karşılaştırma aracı | [Bağımsız scorer](../../scripts/evaluate_corpus.py): kaynak-only prediction önce; ayrı draft oracle sonra; exact proje/mesaj/tip/span ve bire bir eşleme. Duplicate prediction skoru şişiremiyor. [İnsan inceleme kuyruğu](human-review-queue.md) hazır | İnsan/adjudication, geniş kritik authority/state/impact/AC skorları ve sealed holdout. AI etiketi insan gold sayılmadı |
| 3. Küçük çalışan zincir | [Typed fixture düzeneği](../../spikes/decision-chain/README.md): başka oturumdan geciken exact soru cevabı → karar → AND/OR/unknown etki → revision bağlı insan apply → eski/yeni target → kısmi/tam AC → restore | Gerçek sohbetten çıkarım, gerçek auth/grant, soru UI’si, source provenance ve production target/verifier yolları |
| 4. Zorunlu otomatik çıkarım ve kıyas | Aynı 6 oturumda gerçek **kural tabanlı** extraction çalıştı; [sonuç](lexical-baseline-results.json) başarısızlıkları da koruyor. [Ortak kıyas matrisi](pilot-comparison-plan.md) hazır | Semantik LLM extraction **zorunlu ve not_run**; model/veri/bütçe somutlaştırılmalı. Ardından devam paketi, basit dosya ve native yöntemler aynı senaryolarda çalıştırılacak |

T01 tamamlanmadan T02/T03’ün bağımsız **hazırlık/fixture** dilimleri çalışabilir; insan gold’a dayalı kalite ve yatırım kapanışları hâlâ T01’e bağlıdır. Ana backlog ön koşulları kapanış sırasıdır; her alt dilimi gereksiz bekleten tek zincir değildir. T01/T02/T03 IN_PROGRESS, diğer 27 ana görev TODO; hiçbir görev complete yapılmadı.

## Spike-0 düzeltme matrisi

| Bulgu | Güncel davranış / test | Sınır |
|---|---|---|
| SP-01 ortak session ID | Transport ID’den ayrı source namespace: cwd + transcript path + file identity; aynı ID iki kaynağın offset’ini paylaşmıyor | Production host/epoch ve grant sınırı değil; aynı inode/eşit uzunlukla yerinde rewrite protokolü henüz yok |
| SP-02 ilk 120 karakter | Tam normalize/redakte cevap digest’i eşleştiriliyor; benzer başlangıç false positive üretmiyor | Aynı metnin önceki turda bulunması hâlâ mümkün; turn/revision freshness garantisi değil |
| SP-03 negation duplicate | Fuzzy sonuç artık `possible_duplicate`; bilinen polarity farkı `review_conflict`; yalnız aynı literal içerik kesin tekrar adayı | Dil/negation kapsamı heuristic; semantic equivalence veya canonical merge yetkisi yok |
| SP-04 sessiz cap | 8 aday tavanı korunur, `extraction_status=limited` görünür | Otomatik kalan-segment retry/semantik kapsam henüz yok; `complete_rules` yalnız bu kuralların taranması |
| SP-05 kısa done | Assistant done/bitti/completed unverified claim adayı | Her dil/bağlam için tam recall garantisi yok |
| SP-06 kısa/geç cevap | A/B/C/evet/hayır ayrı `answer_candidates`, `unmatched` association; kaynak korunuyor | Spike otomatik soru eşleştirmez. Typed deney yalnız explicit soru/revision eşleşmesini sınar |
| Claim/decision precedence | Aynı segment birden fazla aday türü taşıyabilir; assistant decision “karar ADAYI” | İnsan kararı kabulü yok; CLI capture review ürün approval’ı değildir |
| Kapanışsız gecikme | `watch` bilinen kaynaklarda süreli catch-up; başarısız hook DB yazımından önce diske fsync/atomic receipt; recover idempotent | Watch açıkça çalıştırılmalı; sürekli servis değil. stdin/disk receipt öncesi çöküş, disk-full ve host delivery garanti değil |
| Test kaynak uyarıları | Kapatılmayan dört test dosyası context manager; hook bağlantısı finally ile kapanır | Genel kaynak/OS fault testinin yerine geçmez |
| Anchor/CI | Same-page/cross-file fragment checker ve negatif test; Türkçe başlıklarda dört explicit ID; otomatik CI tanımı | Markdown parser/GitHub renderer tam implementasyonu değil; yeni Mermaid render yapılmadı |

Regresyonlar: [Spike-0 testleri](../../spikes/spike-0/tests/test_regressions.py). Düzeltme öncesi [7 probe](spike0-original-probes.json) tarihsel baseline’dır; güncel test sonucuyla karıştırma.

## Ölçülen sonuçlar ve yorum

- **63 test geçti:** Spike-0 40 (önceki 32 + 8 regresyon), typed zincir 15, scorer/anchor 8. Kontrol ortamı ve kod hash’leri [sonuç kaydında](audit-remediation-results.json).
- [Zincir koşusu](decision-chain-results.json): eski ref `stale`; kısmi AC `verified=false`; tüm **fixture** AC’leri sonrası true; backup/projector digest aynı, dış dispatch 0. `fixture-ref` gerçek GitHub commit gözlemi değildir.
- Lexical extraction **21 prediction / 66 draft annotation occurrence** üretti. Exact tip+span TP=0/FP=21/FN=66. Daha gevşek mesaj+tip tanısı TP=5/FP=16/FN=61 (precision 0.2381, recall 0.0758). Gevşek skor release gate değildir. Bir cümlenin tamamını seçmek gold’un kısa span’ıyla eşleşmeyebilir; bu yüzden exact skor tek başına “hiç anlamadı” sonucu değildir. İki ölçü birlikte yetersiz tür/kapsam ve lokalizasyonu gösterir.
- İnsan etiket incelemesi pending. Semantic model `not_run`; domain gate `incomplete`. Corpus küçük/sentetik, holdout reserved fakat sealed değil; dış kullanıcı doğruluğu, native üstünlük, üretim kapasitesi veya token tasarrufu kanıtlanmadı.
- Bu deneylerde model/API dispatch yok. Geliştirme sohbetinin token maliyeti ve bağımsız host tüketimi ölçülmedi; toplam proje maliyeti “sıfır” diye sunulmaz.

## Açık kalan risk ve iş sırası

1. İnsan üç etiket örneğini inceler; tüm corpus review/adjudication ve kritik negatif set tamamlanır. Geliştirme örnekleriyle holdout ayrımı yeniden kontrol edilir; açılan reserved örnekler artık kör test diye kullanılmaz.
2. Zorunlu semantik extractor için sağlayıcı/model veya uygun host yöntemi, paylaşılacak sentetik veri ve bounded bütçe kaydedilir. Prompt/adapter, tam typed output, parse/error/abstention ve immutable run manifest’i oluşturulur. Regex baseline’ın zayıflığı bu işi iptal etmez.
3. Model çıktıları authority/state/AND-OR/target/AC scorer’ına bağlanır. Bağlam, entity linkage, negatif onay ve false-done ölçülür; beklentiyi modelin kendi algoritması üretmez.
4. Aynı kaynak/soru/target senaryolarında [kıyas planı](pilot-comparison-plan.md) çalıştırılır. Native erişim/build bilinmiyorsa `not_run`; boş sonuç başarı değildir.
5. Gerçek Codex B bağlantısı ve Claude Code capability deneyi yalnız seçilmiş izole hedefte, ayrı capture/MCP kapsamıyla yapılır. Installer’ın substring marker/race problemi, source allowlist, oversized gap, concurrent writer ve hard timeout production adoption öncesi kapanır. Şu an gerçek projelere kurulum yapılmadı.

Production auth/ACL, bütçe rezervasyonu, retention, çok kullanıcı, UI ve MCP bu deneylerle uygulanmış sayılmaz; mevcut MVP/faz görevlerinde korunur. Yeni lisans verilmedi; public release yok.

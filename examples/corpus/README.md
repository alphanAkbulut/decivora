# İlk etiketli test seti

> [!NOTE]
> **Sentetik / AI tarafından hazırlanmış etiket taslağı / insan incelemesi bekliyor.**
> Bu paket T01'in ilk somut veri hazırlığıdır. Veri kontrolü geçti; çalışan extractor, domain engine, target adapter veya ürün test sonucu değildir. [Hazırlık ve kapsam raporu](../../docs/quality/baseline.md).

## İçerik ve sayım

| Ölçü | Hazırlanan |
|---|---:|
| Oturum / proje | 6 / 2 |
| Kaynak mesaj | 58 |
| Beklenen kayıt etiketi oluşumu | 66 |
| Farklı KnowledgeRecord kimliği | 46 |
| Anlamlı kayıt/değişim mesajı | 51 |
| Yeni kayıt üretmemesi gereken mesaj | 7 |

66 etiket, 66 yeni task değildir; aynı kaydın sonraki sürüm/durum atıfları sayılır. 46 ayrı KnowledgeRecord kimliği proje namespace'iyle sayılır; Evidence/Execution/AnswerRecord bu minimuma eklenmez. No-op/retry örnekleri 30 anlamlı kayıt şartının yerine geçmez.

## Dosya düzeni ve cevap anahtarı

- [Manifest](manifest.json): aile/split/oturum, dosya SHA-256'ları, sayılar, etiket ve ürün sonucu durumu.
- `sources/`: sentetik konuşma, bilinen başlangıç bağlamı ve açıkça fixture diye işaretli transport/observer/verifier metadata'sı. Extractor yalnız bu girdileri görür.
- `oracles/`: beklenen tip/kimlik/özellik, kaynak span, ilişkiler, state/effect assertions ve gerekçe. Gelecekte yalnız scorer/reviewer okur; modele/context pack'e girmez.

Bu bir corpus formatıdır; production event/API/DB schema seçimi değildir. Actor yetkisi fixture transport/seed bilgisiyle verilir, cümledeki “onaylıyorum” kelimesinden çıkmaz. `fixture://` hedefleri gerçek repo/URL değildir. İçerik hash/observation/verifier sonuçları sentetik girdidir; dosyanın gerçekten okunduğunu veya testin çalıştığını iddia etmez.

## Oturumlar

| Oturum | Split / aile | Konuşma | Beklenen sonuç |
|---|---|---|---|
| S01 | Geliştirme / storage_evolution | [Kaynak](sources/s01.json) | [Oracle](oracles/s01.json): öneri, açık soru, AND/OR/unknown gerekçe, üretilme iddiası, belge talimatı/prompt, erteleme |
| S02 | Geliştirme / storage_evolution; S01'in devamı | [Kaynak](sources/s02.json) | [Oracle](oracles/s02.json): yeni chat'te geç seçim, etki adayları, yeni artifact revision, reported/old/current gözlem, tek AC ve retry |
| S03 | Geliştirme / project_identity | [Kaynak](sources/s03.json) | [Oracle](oracles/s03.json): aynı adlı farklı proje, blocker, iki soruda belirsiz A, kanıtsız onay, izin hatası ve ret |
| S04 | Geliştirme / agent_authority | [Kaynak](sources/s04.json) | [Oracle](oracles/s04.json): subtask/parent AC, agent run finished, subagent'ın yetkisiz onayı, ortak bütçe, test invalidate, bağımsız iş |
| S05 | Ayrılan değerlendirme / release_revisions | [Kaynak](sources/s05.json) | [Oracle](oracles/s05.json): stale option revision, artifact bundle, çıktı dili ve açık iptal |
| S06 | Ayrılan değerlendirme / release_revisions; S05'in devamı | [Kaynak](sources/s06.json) | [Oracle](oracles/s06.json): geçerli güncel seçim, partial/yanlış hedef/current gözlem, bütün task AC'leri, stale kanıt ve devam paketi |

Aile bölünmesi: S01–S04 geliştirme, S05–S06 `holdout_reserved`. Aynı hikâyenin devamı iki sete bölünmez. **Henüz sealed/blind holdout değildir:** seti hazırlayan AI bütün kaynak ve etiketleri gördü. Bu konuşmayla tune edilmiş aynı model üzerinde “kör holdout başarı” denemez; gerçek deney öncesi etiket review'u, model/prompt/scorer revision'ları ve bağımsız değerlendirme koşulu sabitlenir.

## Kaynak span ve yeniden üretim

Span aralığı Unicode codepoint üzerinde `[start, end)`; `text[start:end]` tam `quote` olmalıdır. S03'te emoji öncesi/sonrası konum örneği vardır. UTF-8 byte veya JavaScript UTF-16 offset'i buna doğrudan eşit değildir; adapter mapping testi T04/T09 işidir. Bu ilk sette CRLF/bozuk sınır ve bütün dil çeşitleri kapsanmış değildir.

Repo kökünde:

```bash
python3 scripts/check_corpus.py --self-test
python3 scripts/check_docs.py
```

İlk komut hash/span/count/kimlik, split/continuation, cevap anahtarının input'a sızması ve referans bütünlüğünü kontrol eder. 11 bozuk veri varyantı validator'ın reddini test eder; ürünün bu senaryolarda doğru davranacağını test etmez. Düzeltmede source/oracle ile manifest hashleri birlikte güncellenir; review sonrası yeni dataset revision kaydı tutulur. Aynı ilk set üzerinde tuning ve değerlendirmeyi karıştırma.

## İnceleme ve zorunlu devam

1. [İnsan review listesi](../../docs/quality/baseline.md#insan-incelemesi-ve-t01-kapanışı) ile beklenen anlam/etki/rationale incelemesi; anlaşmazlık açık kayıt olur.
2. T01'in kalan fixture ve karşılaştırma protokolünü tamamlamak; büyük FLOW/permission/crash suite'i bu küçük corpus yerine sayılmaz.
3. T03f/T09/T24q: çalışan extractor'dan gerçek prediction, bağımsız matching/scorer ve zorunlu semantik ölçüm. Q03-R1 A yalnız ilk no-model hazırlığın sırasıdır.
4. Seçilmiş gerçek kaynak/hedef ve ayrı izinlerle target/host deneyleri; Codex MCP + otomatik capture kabulü ayrıca.

MVP ve tam ürün senaryolarının önceliği [baseline kapsam tablosunda](../../docs/quality/baseline.md#mvp-ve-tam-ürün-sırası) korunur. Zorunlu işlerin yapılması bir A/B seçeneği değildir; kaynak/target, yöntem veya öncelik seçimi gerektiğinde dar soru sorulur.

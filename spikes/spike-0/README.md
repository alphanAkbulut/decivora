# Spike-0 — capture ölçüm düzeneği

**Statü:** atılabilir keşif. MVP kanıtı, ADR kararı veya T01/T02/T03 tamamlanması **değildir**. Stack burada geçici seçildi (Python 3 stdlib, sıfır bağımlılık); gerçek stack kararı T03'e aittir.

**Amaç:** Claude Code'un gerçek oturumlarında hook'un ne yaptığını, neyin yakalandığını, gürültüyü, gecikmeyi ve kart incelemenin yükünü **görmek ve sayıya dökmek**. Hüküm vermez; eşikleri owner koyar.

## Ne yapar

```
Claude Code hook (SessionStart / UserPromptSubmit / Stop / SessionEnd)
   └─ bin/spike0_hook.py  → events + oturum kaydı (tek transaction, digest ile tekilleştirme)
        └─ transkript JSONL'i byte ofsetiyle okur (yarım satır bekler, kısalmayı yakalar)
             └─ proje bağlama (bindings.json; bağsız → karantina)
                  └─ kural tabanlı aday çıkarımı (TR+EN; LLM yok)
                       └─ mini uzlaştırma: new / duplicate / possible_duplicate / review_conflict / possible_supersedes / unknown
                            └─ kart → spike review → karar OLAY olarak yazılır
```

- Hook **stdout'a hiçbir şey yazmaz** (SessionStart/UserPromptSubmit'te stdout Claude'un bağlamına girer) ve her durumda 0 ile çıkar; hata `data/errors.log`'a düşer.
- `thinking` (özel muhakeme) ve araç sonuçları **alınmaz**; yalnız insan/asistan `text` blokları.
- Metinden belirgin token kalıpları maskelenir (`sk-…`, `ghp_…`, `AKIA…`, `Bearer …`).
- "Onayla" = doğru yakalama; task oluşturmaz, `verified` üretmez. `impl_claim` ("bitti" iddiası) her zaman `unverified`.

## Kurulum ve kullanım

Gereksinim: Python 3.9+ (başka bağımlılık yok). Kendi makinende:

```bash
cd spikes/spike-0
make test                               # güncel 40 test; ağ/LLM yok
mkdir -p ~/spike0-sandbox                # ÖNCE sandbox; gerçek projeye değil
./bin/spike install ~/spike0-sandbox     # yalnız o klasörün .claude/settings.local.json dosyası
./bin/spike bind ~/spike0-sandbox sandbox
# ~/spike0-sandbox içinde YENİ bir Claude Code oturumu aç, birkaç tur konuş
./bin/spike status
./bin/spike review                       # a=onayla r=reddet d=ertele s=geç q=çık
./bin/spike export-html                  # salt okunur kart sayfası
./bin/spike report --save                # results/ altına kaydeder
./bin/spike uninstall ~/spike0-sandbox
```

Veri dizini varsayılan `spikes/spike-0/data/` (gitignore'da). `SPIKE0_DATA` ile değiştirilir. Kullanıcı düzeyindeki `~/.claude` ayarına **dokunulmaz**; mevcut `settings.local.json` yedeklenir (`.spike0-backup`).

Gözlem adımları: [OBSERVE.md](OBSERVE.md).

## Sağlayanın bildirdiği tarihsel doğrulama (bulut sandbox, Claude Code 2.1.296)

- 32 birim/entegrasyon testi geçti: no-op filtresi, tekrar gönderim, yarım satır, dosya kısalması, bozuk JSON, aynı adlı iki proje, karantina, 3 ardışık session senaryosu (gerçek concurrent test değil), 1000 mesajlık burst (kayıp yok), hook dayanıklılığı (bozuk JSON, kilitli DB), kurulum/kaldırma, redaksiyon.
- Gerçek transkript biçimi (gerçek oturum kopyası) hatasız işlendi; `thinking` sızmadı.
- `claude -p` ile **tek** gerçek hook'lu çalıştırma: 4/4 hook tetiklendi. Ayrıntı ve sınırları: [results/real-run-001.md](results/real-run-001.md).

## Gerçek host üzerinde doğrulanmayanlar

- **Etkileşimli** oturumda `Stop` anında transkriptin güncel olması. Gözlenen `-p` modunda güncel değildi; kartlar `SessionEnd`'e kadar gecikti.
- Çökme/`SessionEnd`'siz kapanışta kayıp (`spike process` ile telafi edilir; `status` "GERİDE" gösterir).
- Uzun oturumlar, paralel pencerelerde gerçek davranış, macOS.
- Çıkarımın precision/recall'u (etiket yok), Codex, ChatGPT.

## Bilinen sınırlar (bilerek)

- Kural tabanlı çıkarım **düşük recall** ve **gürültülü** olacak şekilde basit; amaç ölçmek. Uzun asistan metinlerinde "karar" gibi sözcükler çok aday üretebilir.
- Proje bağlama oturum/klasör düzeyinde; aynı klasörde iki projeyi mesaj düzeyinde ayırmaz. Sonradan yeniden bağlama geçmiş mesajları taşımaz.
- `UserPromptSubmit` zamanlanmış görev veya başka oturumdan gelen mesajda da tetiklenebilir; "insan yazdı" varsayımı yoktur.
- Tek yazıcılı yerel SQLite; çok işlemli yük, retention, şifreleme, replay, bütçe yöneticisi yok.
- Review kararı CLI'dadır; HTML çıktı salt okunurdur.
- Şema ve alan adları geçicidir; kalıcı sözleşme T04 sonrası.


## 2026-10-11 — Güncel kaynak ve yerel regresyon doğrulaması

Kullanıcı paketi repo’ya alınmış ve audit önerileri uygulanmıştır; [provenance](PROVENANCE.md) ve [bulgu matrisi](../../docs/quality/audit-remediation.md) hangi değişikliğin neyi sağladığını açıklar. **40 test macOS/Python 3.9.6’da geçti; yeni gerçek Claude/Codex oturumu çalıştırılmadı.** Üstteki bulut n=1 sonuçları sağlayanın tarihsel raporudur; yeniden üretilmiş gerçek host sonucu değildir.

Source namespace artık transport session ID, cwd, transcript path ve file identity üzerinden ayrılır. Stop ölçümü prefix yerine tam normalize/redakte içerik digest eşleşmesidir; aynı metin önceki turda olabilir, **turn/revision freshness garantisi değildir**. Eski measurement DB satırları yeni yöntemde ölçülmüş sayılmaz; karşılaştırmada yeni izole data dizini kullan ve yöntemi kaydet. Additive kolon migration’ı production migration protokolü değildir.

Hook diske minimal receipt yazıp fsync/atomic replace sonrası DB’yi işler; failed DB receipt’i sonraki process/watch kurtarır. Raw prompt/assistant cevabı spool’a yazılmaz; hash/source metadatası bulunur. Transcript text mevcut extraction/redaction yolunda yerel DB’ye işlenir. Disk/path izinleri, retention, şifreleme ve bütün secret’ların maskelenmesi garanti değildir.

```bash
# Yalnız zaten izin verilen ve kayda girmiş fixture/sandbox kaynaklarında:
./bin/spike process
./bin/spike watch --seconds 60 --interval 1
```

Watch açıkça başlatılan **süreli** catch-up’tır; sürekli servis veya görünmeyen tüm projeleri tarama değildir. 0–3600 saniye aralığı sınırlıdır; transcript yoksa kaynak durumu unknown kalabilir. Gerçek host’a install veya watcher başlatma bu teslimde yapılmadı.

A/B/C/evet/hayır `answer_candidates` olarak `unmatched` tutulur; otomatik insan approval’ına dönüşmez. `done` assistant claim’idir. Bir segment birden fazla aday türü üretebilir. 8 aday tavanı aşılınca extraction `limited`; input korunur, kalan semantic işlem yapılmış sayılmaz. `complete_rules` yalnız mevcut kuralların taranmasıdır, bütün anlamın anlaşılması değil.

Fuzzy yakınlık yalnız possible_duplicate, bilinen negation farkı review_conflict olur. Aynı literal metin repetition’dır; insan kararı, canonical merge veya task kapanışı değildir. Türkçe/İngilizce keyword heuristics tam semantik sistem değildir.

Aynı corpus üzerinde bağımsız [lexical skor](../../docs/quality/lexical-baseline-results.json) çalıştırıldı: draft etiketler üzerinde düşük tip/kapsam ve exact span başarısı; gerçek LLM semantiği not_run. İncelenen kartların accept oranı corpus precision/recall’unun yerine geçmez.

Production adoption öncesi source grant/allowlist, installer marker/race/atomic config, oversized source gap, gerçek concurrency, hard timeout, original↔redacted span mapping ve host/epoch/capability ayrı işlerdir. Bu sınırları fixture testleriyle kapandı sayma. Karar graph/approval/AC için [ayrı typed deney](../decision-chain/README.md) vardır; iki spike birleşmiş çalışan ürün değildir.

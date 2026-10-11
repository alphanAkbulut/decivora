# Tek komutluk quote → karar → etki → kanıt zinciri

**2026-10-12 · P0 / T03j · DONE — kontrollü entegrasyon teslimi.** Bu kapanışın kapsamı fixture zinciri ve ayrı bounded yerel gözlemdir; gerçek model anlam doğruluğu, production IAM, gerçek GitHub target veya ürün MVP kapanışı değildir.

## Çalıştır ve sonucu gör

Repo kökünde:

```sh
python3 -B spikes/semantic-chain/run.py
```

Yeni bağımlılık, API key veya API bakiyesi gerektirmez. Yalnız geçici klasörde sentetik dosya ve SQLite event log oluşturur; işlem sonunda bunları temizler. Replay/restore dış sisteme gönderim yapmaz. Rapor source kimlikleri, yedi checkpoint, bounded local reads ve ölçülmemiş alanları gösterir. `checkpoint_score.status=passed` controlled expectation eşleşmesidir; `semantic_inference=not_run` ve `production_runtime=false` korunur.

| Adım | Bu komutta gözlenen davranış |
|---|---|
| Source/quote | S02 source + scripted quote-only aday; span kodla bulunur, mevcut strict validator uygulanır |
| Geç cevap önerisi | Karar Markdown ve revision 2 korunur; canonical mutation 0 |
| Ayrı karar seçimi | Sentetik trusted receipt SQLite seçimini uygular; görevler hâlâ todo |
| AND/OR/unknown | Sync/combined obsolete candidate; export retained; watch review unknown |
| Ayrı impact | Snapshot digest'e bağlı fixture insan eylemi task etkisini uygular |
| Yerel dosya | Tek temporary artifact gerçek bounded filesystem read; hash match tek başına task acceptance değil |
| Eski/yeni revision | Ref/revision metadata fixture olarak açıkça verilir; eski ref stale, güncel fixture ref match |
| AC | Rollback geçtiğinde verified=false; migration da geçtiğinde controlled verified=true |
| Restore | SQLite backup yeniden açılır; replay projection hash eşleşir, external dispatch 0 |

[Kaydedilmiş sonuç](integrated-chain-results.json) input/expected/code hashleri ve immutable önceki teslim referanslarıyla bu çalıştırmayı kaydeder. **66 semantik suite testi passed**; son ek test quote adapter + bounded observer + tam fixture zincirinin birlikte çalıştığını ve yerel match'in tek başına verified olmadığını doğrular.

## Tamamlanan küçük işler

Ana T03 yatırım/kalite kapısı açık; aşağıdaki uygulanabilir alt teslimler kendi kapsamlarıyla kapandı:

| Alt görev | Kapanış koşulu | Kanıt |
|---|---|---|
| T03g | Bounded quote adapter + ayrı candidate rubric, negatifleri, eski raw korunması | [Adapter](source-anchor-adapter.md); yeni suite eski testleri de çalıştırdı |
| T03h | Gönderimsiz API schema/payload taslağı + saved response import; unknown/refusal/incomplete retleri | [API paket](quote-api-package.md); schema/provider acceptance kapsam dışı |
| T03i | Tek seçilmiş dosya bounded read, path/type/boyut/izin/değişiklik ayrımı + gerçek local read | [Observer](local-observer.md); production grant ve remote upload kapsam dışı |
| T03j | Mevcut quote-only + observer + decision/impact/AC/restore kodunun tek komutta birleşmesi | Bu belge, yedi bağımsız checkpoint ve integration testi |

Bunlar görevi kapatabilmek için kalite kriterlerinin azaltılması değildir: geniş T03f hâlâ gerçek harness/model/native ölçümünü bekler. Yeni küçük kapanışlar production engine yüzdesine çevrilmez. Source messages, AnswerRecord ve trusted receipt ayrı; receipt'te authenticated=true yazan scripted caller production authentication sayılmaz. AC passed girişleri fixture test sonucudur, gerçek kullanıcı ürün testinin sonucu değildir.

## Sonraki zorunlu doğrulama

Gerçek semantik test hâlâ yapılmalı. H1 için kullanıcının insan inceleme yanıtı pending; “ilerle/tamamla” ifadesini H1 etiket onayı sayma. Mevcut üyelik route'u için source-only quote çıktısı, yeni tek-send sınırı ve usage unknown riski somutlaştırılacak. Önceki iki gönderim izni tüketildi; bu teslim API harcaması veya yeni provider çağrısı başlatmadı. Tam vizyon/MVP ayrı kapsam olarak korunur.

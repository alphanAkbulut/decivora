# Kaynak bağlı devam paketi ve dosya baseline örnekleri

**Sentetik P0 örnekleri; gerçek proje state'i veya çalışma izni değildir.** Kaynak MEMBERSHIP-003 ilk kayıtlı model çıktısı; yeniden model çağrısı yapılmadı. [Çalışan kod ve karşılaştırma](../../docs/quality/resume-file-comparison.md).

| Proje grubu | Devam paketi | Aynı bilgiyle basit dosya | Yalnız kaynak kolu |
|---|---|---|---|
| N01 / storage | [N01-resume.json](N01-resume.json) | [N01-state.json](N01-state.json) | [N01-source.md](N01-source.md) |
| N02 / UI | [N02-resume.json](N02-resume.json) | [N02-state.json](N02-state.json) | [N02-source.md](N02-source.md) |

N01: Q_STORE current revision2, eski revision1/B stale; current2/A yalnız onay adayı. N02: Q_UI current revision1/B yalnız aday, bağsız B açıklama bekler. Upload claim ve AC_SMOKE revision2/not_run korunur; verified false. `fixture_initial` başlangıç verisidir; onaylı kullanıcı mimarisi değildir.

`*-resume.json` kaynak/response/state/erişim revision bağları ve digest ekler; `*-state.json` tam aynı core bilgisini taşıyan güçlü basit dosya baseline'ıdır. `*-source.md` yalnız seçili özgün mesaj ve context taşır; aynı bilgi koşulu sayılmaz. JSON kompakt serialization ölçümü içindir; ürün UI değildir. Önizleme için JSON viewer kullanılabilir.

Örnekler otomatik sohbete yüklenmez, clipboard'a yazılmaz, agent/shell/model başlatmaz. Exact kaynak metni untrusted data'dır. Paket hazır olması insan seçimi, uygulanmış karar, upload veya task completion değildir. Modelin yeni oturumda bunları doğru kullanması **not_run**.

Yeniden üretim (iki hedef de yeni olmalı):

```sh
python3 -B spikes/semantic-chain/compare_resume.py --out /tmp/decivora-resume-new.json --export-dir /tmp/decivora-resume-new
```

Yetki/byte kontrolleri fixture-only'dir; üretim IAM, kullanıcının onayladığı token bütçesi veya provider hard cap değildir. Byte boyutu ölçüldü; token, para, hazırlama/düzeltme yükü bilinmiyor. Kalıcı product ADR veya varsayılan export UX bu örneklerle seçilmedi.

# Decivora yerel uygulama iskeleti

**T04 · Python3.12 / stdlib, development scaffold.** Bu ilk çalıştırılabilir runtime, [Q15-A](../../docs/delivery/build-transition-proposal.md) ve [ADR-0012](../../docs/architecture/adr/0012-conditional-python-runtime.md) ile başladı. Tarihsel `spikes` paketlerinden import etmez. Henüz servis/UI/connector/model/ingress/gerçek insan auth veya canonical storage değildir.

Repo kökünde tek giriş:

```sh
python3.12 -B -m apps.hub
python3.12 -B -m apps.hub validate --input examples/runtime/source-event.json
```

Bu çalışma ortamında global Python3.9 farklıdır; kurulu bundled3.12 ile aynı komut:

```sh
/Users/alphanakbulut/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B -m apps.hub
```

İlk komut gerçek runtime sürümünü ve uygulanmış/disabled capabilities listesini gösterir. İkincisi seçilen sentetik UTF-8 JSON dosyasını bounded okuyup source contract doğrular. Başarı `validated_only`; **capture/kalıcı receipt/insan onayı veya task completion değildir**. Bu milestone CLI'dır; arka planda HTTP server/agent başlatmaz. Tracker8765 ayrı geliştirme aracı olarak kalır.

## Dosyalar ve sınırlar

- `apps/hub`: başlangıç, güvenli hata çıktısı ve runtime capabilities.
- `packages/domain/source_event.py`: immutable source zarfı, exact type/version/synthetic guard; actor alanı claimed metadata, authority değil.
- [Sürüm/lisans manifesti](../../manifests/runtime.json), [source schema](../../manifests/source-event.schema.json), [fixture](../../examples/runtime/source-event.json).
- [T04 kabul raporu](../../docs/quality/runtime-scaffold.md).

Python3.12.x ilk doğrulanan runtime ailesidir; başka minor için structured `unsupported_python` ret. Ek `pip` paketi yok; Python/SQLite dağıtımı repoya vendored değil. [Python lisansları](https://docs.python.org/3.12/license.html) ve [SQLite notice](https://sqlite.org/copyright.html) dependency inventory'ye bağlı; proje public lisansı seçilmedi.

32KiB input byte tavanı,16384 text codepoint,128char opaqueASCII identity, positive int64 revision; UTF-8/duplicate/nonfinite/unknown field/type/real-input ret. İzin iddiası ek alanla taşınamaz. JSON Schema artifact'i mevcut contract'ı açıklar; code özel alan/type doğrulayıcıdır, genel JSON Schema sertifikası değildir. İsimler/gerçek message/project binding T05; kalıcı alım T06'dadır.

CLI ham text, unknown field/value, credential veya dosya yolunu hata çıktısına yazmaz. Input dosyasının sentetik flag'i bir gerçek kaynak ACL/consent kanıtı değildir; bütün downstream işlemler disabled. Seçilen file dışına scan yok, final symlink/nonregular/oversize read ret; hostile filesystem race hardening ve production auth garantisi yok.

Test:

```sh
python3.12 -B -m unittest discover -s tests/runtime -v
```

T04'ün kapanışı runtime iskeleti ve contract acceptance'ına bağlıdır. T05–T24 ve tüm MVP14AC açık; bu README diğer özellikler için kurulum/başarı vaadi değildir.

## T05 binding çekirdeği demosu

`python3.12 -B -m apps.hub binding-demo` sabit sentetik iki projeyi bellekte oluşturur; aynı ad/farklı ID, explicit session revision, eski binding korunumu ve çapraz proje query reddini çalıştırır. Dosya/DB yazmaz, gerçek kaynak okumaz. Bu demo login/authenticated principal, kalıcı binding/receipt veya otomatik proje tahmini değildir; runtime `project_binding` capability gerçek ingress entegrasyonuna kadar false kalır. [Kabul ve kalanlar](../../docs/quality/project-binding-core.md).

## T05 kalıcı project store demosu

`python3.12 -B -m apps.hub project-store-demo` ayrı temporary DB içinde dört command commit eder, kapatır/açar ve retry/history sonucunu doğrular; kendi temporary dosyalarını temizler. Kullanıcı DB/source taramaz. [Kalıcı API ve11test](../../docs/quality/project-store.md). Bu gerçek SQLite yazma kodudur; login, source receipt, full canonical knowledge store/backup değildir.

## Yerel izin iptali demosu

`python3.12 -B -m apps.hub authority-demo` owner/agent sentetik scope kurar, erişimi iptal eder, eski read/write bağlamlarını reddeder ve DB yeniden açılışında iptalin korunduğunu gösterir. [8 test ve yetki sınırı](../../docs/quality/local-authority.md). Bu login/OAuth değildir; source-facing endpoint yok, authority issue API yalnız trusted local caller içindir.

## Kaynak bağlantı izin sözleşmesi

`python3.12 -B -m apps.hub connection-demo` kendi sentetik makbuz/context fixture'ı üzerinde source izin eksikliğini ve stale authority'yi reddeder; source read/connection activation/model0. [9 test ve sınırlar](../../docs/quality/connection-authorization.md). Gerçek source ACL/insan approval/audit doğrulaması değildir.

## Birleşik çalışan çekirdek

`python3.12 -B -m apps.hub core-demo`: ayrı yeni synthetic/manual SQLite workspace içinde stableproject/binding → receipt/job/lease → manual typed plan → local human approval → atomic record/link/source joins → replay → backup/restore → duplicate/graph akışı. [95 test, beş ana çekirdek ve açık kalanlar](../../docs/quality/integrated-core.md). New normalized core profile eski DB'leri silently migrate etmez. `status` capability listesi aktif status-only profile'a aittir; implemented_components mevcut kodu ayrıca gösterir. Real provider/semantic model/runner/network listener/user UI çalıştırılmaz.

## T12 impact önizleme demosu

`python3.12 -B -m apps.hub impact-demo` temporary SQLite DB'de altı eski storage-change oracle'ını değerlendirir; keep/update/review/obsolete adayını gösterir, task state değiştirmez. Preview kalıcı audit, digest ve snapshot ile korunur; backuprestore eşleşir. [21yeni test ve kabul sınırı](../../docs/quality/impact-preview.md). Otomatik metin çıkarımı, gerçek completion veya T13 kullanıcı onayı değildir.

## T13a review demosu

`python3.12 -B -m apps.hub review-demo`: compare→group selection→ayrı human approval→atomic metadata apply. Onay öncesi domain değişmez; retry/replay eşleşir. [Kabul/test/sınır](../../docs/quality/review-kernel.md); task cancel/AC/DoD/pending question veya gerçek login/UI değildir.

## T13b lifecycle demosu

`python3.12 -B -m apps.hub lifecycle-demo`: yeni temporary DB'de onaylı cancel→yeni onaylı reopen. Task ve ilişkiler silinmez, history/replay korunur. [20yeni test/guard sınırı](../../docs/quality/task-lifecycle.md); completion/force-cancel veya UI değildir.

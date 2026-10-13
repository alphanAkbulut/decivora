# T04 — İlk uygulama iskeleti kabulü

**2026-10-13 · T04 kapsamı tamamlandı.** Q15-A/ADR-0012 sonrasında ilk runtime `apps/hub` ve bağımsız `packages/domain` ile yazıldı; historical spike kodu import edilmedi. [Çalıştırma rehberi](../../apps/hub/README.md) · [Hash/sürüm/kabul kaydı](runtime-scaffold-results.json).

| T04 kabul koşulu | Gerçek kanıt |
|---|---|
| Tek yerel başlangıç | Python3.12 ile `python3.12 -B -m apps.hub`; version/capabilities JSON, exit0 |
| Domain/storage sınırı | SourceEvent contract domain paketinde; storage henüz uygulanmadı, capability false; T07'ye reserved |
| Sürüm/dependency/lisans envanteri | Runtime0.1.0-dev; Python3.12.x, linked stdlibSQLite startup sürümü;0third-party pip dependency; resmi license references manifestte |
| Sentetik input dışı kapsam yok | `synthetic` exactlytrue guard; actual capture/source grant/processing disabled. Flag gerçek ACL kanıtı değil |
| Schema-invalid ret | Missing/extra/permission/type/revision/duplicate/nonfinite/UTF8/size ve real-input ret; static error/exit2, raw/credential/path log yok |
| Temiz başlangıç | Yalnız apps/packages/manifests/example yeni temporary root'a kopyalandı; `-S -B` ile site packages kapalı iki CLI komutu geçti, runtime dosya oluşturmadı |
| Test/CI yolu |12runtime unittest ve CI Python3.12/runtime test step; mevcut P0/root regresyonları ayrıca çalıştırılır |

12 acceptance testi passed; localbundled Python3.12.14/SQLite3.53.1. Host/system Python3.9 komutu structuredunsupported_python/exit2 verdi; traceback veya capability başarı iddiası yok. Bu proof Python3.12 kurulumunu/başkaOS desteğini test etmez. CI başka patch/linkedsqlite sürümünde çalışabilir; observed-development versions hardpin değildir.

T04 başlangıç komutu CLI olarak açılıp sonlanır; backgroundHTTP server veya görsel ürün değildir. Valid dosya sonucu `validated_only`, content digest, actor_identity_verified false, durable_receipt false, human_approval false, canonical mutation/modeldispatch0. Kaynak role/metin talimatı runtime yetkisi veya task verification oluşturmaz. Product UI, project binding, ingress, canonical DB, gerçek auth, model/provider/runner/network listener implemented diye gösterilmez.

Manuel validator yalnız kendi source contract'ını doğrular; JSON Schema artifact genel evaluator veya provider schema enforcement değil. File read caller-selected regular file/bounded/no-follow; malicious filesystem concurrency/TOCTOU ve production security garantisi değildir. Bytes/token/kota tasarrufu çıkarılmadı; bu geliştirme chat'inin usage'ı unknown.

## Kanıt sürümü

T04 hash raporu [fbd780f commitindeki](https://github.com/alphanAkbulut/decivora/tree/fbd780f0b9bcb0ee4fe2abca756105ce5c543bd1) kabul edilen kaynakları gösterir. Sonraki CLI/binding değişiklikleri bu tarihsel raporu yeniden yazmaz; [güncel T05f kanıtı](project-binding-core.md) ayrı tutulur.

## Sonraki ana iş

T04 Done olması yalnız bu startup/contract/manifest/clean-run kabulündendir. **T05 proje kimliği/binding** sıradadır; T06 kalıcı alım, T07 log/projector/backup, T08 policy sonrasında kendi AC'leriyle ilerler. T03 parent ve T01/T02 model/capture/native/ROI kanıtları açık; full vision ve14MVP AC korunur. İlk receiver failures/raw ve code proof'ları aynı kalır.

Q15-A build kararı accepted; front-end/publiclicense/cloud/realconnector/modelcost kabulü değildir. [Runtime license manifesti](../../manifests/runtime.json) Python/SQLite primary source'larına bağlıdır; runtime dağıtımı veya üçüncü taraf source vendoring yapılmadı.

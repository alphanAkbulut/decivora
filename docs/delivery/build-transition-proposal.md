# Q15 — P0'dan MVP çekirdeğine kontrollü geçiş

**2026-10-13 · Q15-A kabul edildi.** [Doğrudan insan onay kaydı](../quality/reviews/q15-build-approval.json) ve [ADR-0012](../architecture/adr/0012-conditional-python-runtime.md) runtime/dependency seçimini kabul eder; uygulama kabulü her görevin kendi kanıtıdır. Aşağıdaki alternatifler karar hazırlığının gerekçesini korur. User “To Do'daki işler neden sabit?” diye sordu. Yanıt: 26 küçük P0 teslimi var; T04 hâlâ tüm T03 kapanışına bağlı, T03 de tamamlanmamış T01/T02/karşılaştırma/yatırım koşullarına bağlı. Bu planı uygulamadan ana To Do sayısı düşmez.

## Mevcut durum → tespit

- T01: corpus/partial behavior review var; exact-label/adjudication/holdout açık.
- T02:40 capture fixture testi ve Codex CLI version inventory var; iki gerçek coding yüzeyinde capture coverage doğrulanmadı.
- T03: kaynak bağlama/typed zincir/review/durable reply parçaları çalışıyor. İlk iki fresh-session receiver run invalid_contract; native/ROI ve owner build/stack kararı açık.
- T04–T24:21 ana MVP işi başlamadı. T25–T30:6 sonraki faz işi; MVP öncesi eritilecek işler gibi yorumlanmaz.

**Tespit:** Genel kalite/capture/ürün değeri sorularını runtime iskeleti için de bitmesi gereken tek büyük önkoşul yaptık. Bu yaklaşım ilk başta risk öğrenmesini öne aldı; şimdi bütün bağımsız temel geliştirmeyi bekletiyor. Bunu daha çok T03 alt göreviyle çözmek doğru değil. Source/ACL/approval/replay gibi değişmez kurallar korunarak, geliştirmeye başlama ile release/pilot kabulü ayrılabilir. Bu ayrımı kendiliğinden kabul edilmiş saymıyoruz.

## Önerilen değişiklik

**A — Önerilen: koşullu MVP çekirdeği build'i.** Owner, mevcut belirsizlikleri bilerek önce yerel iskelet ve deterministik çekirdek yatırımını seçsin. T01/T02/T03 benchmark/kalite işleri açık kalsın; T04 başlangıcı bütün parent T03'ün Done olmasına değil, bu source-bound karar ve ilgili runtime ADR kabulüne bağlansın. T03'ün araştırma/evidence kapanışı ve model başarısı otomatik Done olmaz.

Önerilen ilk teknik taban: **Python3.12 + stdlib SQLite**. Yerel bundled Python3.12.14/SQLite3.53.1 version çıktısı okundu; mevcut248 semantik test bu Python runtime'ında geçti. Bu ortam doğrulaması supported OS matrisi, Python release desteği, clean install veya T04 kabulü değildir. Öneri yeni ücretli paket/provider gerektirmeden mevcut çalışma bilgisini kullanır; P0 kodu ürün koduna körlemesine taşınmaz. Domain/storage/ingress sınırları ayrı tutulur. Frontend framework, cloud ve nihai public lisans bugün kabul edilmez; mevcut full scope korunur.

**B — Mevcut gate düzenini koru:** T01/T02/T03 kapanmadan T04 başlamasın. Bu durumda ilerleme gerçek host erişimi, insan etiket incelemesi ve native/ROI kararlarında olacaktır; yeni P0 alt görevleri ana To Do'yu azaltmaz. Bu yol geçersiz değildir fakat kullanıcının şimdi temel uygulamayı görme isteğini geciktirir.

## İlk ana teslimler

| Sıra | Ana iş | Gözlenebilir teslim / kapanış |
|---|---|---|
| 1 | T04 runtime iskeleti | `apps/hub`, domain sözleşmeleri, sürüm/lisans manifesti; tek yerel giriş komutu; clean-start smoke ve schema-invalid sentetik payload ret; model/network kapalı |
| 2 | T05 proje/binding | Değişmeyen proje kimliği, aynı isim ayrımı, scoped query/command sınırı; belirsiz binding quarantine, cross-project ret |
| 3 | T06 kalıcı source ingress | Sentetik manuel import, kalıcı receipt/cursor ve idempotency; crash/retry kaynak kaybı kontrolü |
| 4 | T07 event log/projector | Append-only domain olayları, optimistic revision, deterministic replay; minimal storage backup/restore alt işi |
| 5 | T08 atomik change set/policy | Base/digest/idempotency ve policy sınırı; half-apply ret; identity/approval transport eksikse açıkça deny/unsupported |

Her ana iş kendi AC'si doğrulandığında kapatılır; önceki fixture pass'ı production AC yerine kullanılmaz. T09 extraction, graph/impact, T13 güvenilir onay ve sonraki API/UI/adapter işleri mevcut sırada kalır; detaylı closure gerçek uygulanmış contract'a bağlıdır.

## Fayda → risk → sınır

**Fayda:** İlk gerçek runtime görevlerine geçilir; ana To Do ilerlemesi görünür hale gelir. Ana görev sayısını düşürmek için etiket veya kalite kapısı uydurulmaz.

**Risk:** Otomatik anlam çıkarımı/ekonomi/nativelere ek değer henüz yeterince doğrulanmadığından çekirdeğin ileride değiştirilmesi veya yatırımın durması gerekebilir. Python runtime tercihi eski TypeScript adayını kesin seçilmiş saymaz; teknoloji değişiminin maliyeti ileride yeniden değerlendirilir. ROI/takvim/başarı yüzdesi vaat edilmez.

**Sınır:** Yalnız private repo içinde yerel geliştirme ve sentetik test. Gerçek sohbet/hesap tarama, connector kurulumu, human identity/approval varmış gibi çalıştırma, yeni model turn/API ücret, deploy/public release/ekip erişimi yok. Kullanıcı bu öneriyi kabul ederse genel kod geliştirme aynı hedefte ilerler; yeni ücret/erişim gibi değişen risk ayrı değerlendirilir. Süre/token/para tavanı burada onaylanmış sayılmaz.

## Etkilenecek hedefler → doğrulama yöntemi

Onaydan sonra `decision-brief`/karar haritası, runtime/storage ADR, backlog T03c/T04 dependency ve aynalanan phase tracker/readiness/progress güncellenir. T03c yalnız **koşullu yatırım/stack seçimi** olarak kayıt alır; karşılaştırma sonuçları open/not_run kalır. T04 In Progress yapılır ve uygulaması başlar. Görev durumu başlamadan değiştirilmez; T04 Done yalnız kendi acceptance kanıtıyla olur.

Etkilenecek kod alanları: `apps/hub`, `packages/domain`, başlangıç/manifest/test komutları; sonraki storage/ingress işleri kendi görevleri içinde. Eski `spikes`, actual model raw, oracle ve hashli test raporları korunur. İlgisiz projeler/global config değişmez.

T04 doğrulaması: temiz geçici çalışma dizininde başlangıç, valid/invalid sözleşme, gerçek model/runner çağrısı olmaması, repo CI ve belgeli sürüm/lisans envanteri. T01/T02/model/native/ROI ve MVP14AC bağımsız release/pilot kapıları olarak görünür; yatırım kararı onların başarı kanıtı değildir.

**Sorulacak tek karar:** A koşullu MVP çekirdeğine Python3.12/SQLite ile geçiş mi, B mevcut P0 kapanışını beklemek mi? Kullanıcı öneriyle ilerlemeyi açıkça istedi ve A kabul edildi. Eski genel “devam” bu yeni dependency/stack kararı olarak geri tarihli kaydedilmedi; güncel cevap ayrı kaynak kaydıdır.

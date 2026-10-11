# Spike-1 v1 — Bekleyen iş ve devam paketi deneyi

**2026-10-11 / PROPOSED / not_started.** Yapıştırılan konuşmadaki öneri incelenebilir bir görev planına dönüştürüldü. Bu belge “Spike-0 çalışıyor” varsayımına dayanmaz. Repo bugün dokümantasyon aşamasındadır; önceki prototip kanıtı yoktur. Üretim kodu, otomatik agent başlatma veya ücretli model çalıştırma taahhüdü değildir.

## Deney sorusu

Kullanıcı, gözlenen kayıtlarda uzun süredir ilerleme/kanıt görünmeyen işi bulup sınırlı ve güncel bir paketle yeni oturumda doğru next-action'a dönebiliyor mu? [Ürün sözleşmesi](../product/resume-package-and-memory.md) state, tazelik, izin ve RES-01–08 test oracle'ını tanımlar.

Önerilen dar deney: kaynaklı bekleyen kartlar + yaş/kanıt/coverage + önizle/kopyala devam paketi + ertele/incele. Obsolete tespiti önce mevcut güncel karar/impact kayıtlarına dayanır; bir regex'in bulduğu “yerine” ifadesi doğrulanmış supersession sayılmaz. Tam ürün vizyonu ve 14 MVP kriteri aynen kalır; bu bir öğrenme dilimidir.

## Önkoşullar ve ilerleme kapısı

- T01 golden corpus/oracle ve T02 kaynak/host capability raporu hazırlanır. Önceki Spike-0 artifact'i varsa ayrı repo/path, revision, test ve izin kapsamıyla incelenir; doğrulanana kadar bağımlılık değildir.
- T03 build/extend/stack kapısından sonra ayrı sentetik prototype uygulanabilir. Production entegrasyonu için T05/T07/T08 kaynak/kimlik/event/audit, T10 reconciliation ve ilgili context/UI katmanları gerekir.
- İlk deneyde deterministic template, örnek kayıt ve mock job kullanılır. Gerçek transcript ve model testi Q03 kapsamında somut veri/provider/bütçe izni gerektirir. Paket hazırlama, gerçek araçta resume veya execution ile karıştırılmaz.
- Q11-A ilk deney için öneridir. Owner tercihi gelmezse taslak/sentetik değerlendirme hazırlanabilir; B host/CLI başlatma uygulanmaz.

## Küçük ardışık görevler

| Adım | Çıktı ve bağımlılık | Gözlenebilir kabul |
|---|---|---|
| S1-01 Kaynak/oracle envanteri | T01/T02; observed, unknown ve izinli kaynak listesini belirle | Aynı projeye bağlı iki chat ve eksik erişim ayrı; beklenen next-step/AC/karar etiketi model çıktısından bağımsız yazılır |
| S1-02 Bekleyen iş görünümü | S1-01; sentetik kart, ilerleme yaşı, kanıt ve coverage | RES-01/05; erteleme/iptal ayrı, kesin “unutuldu” iddiası yok; filtre/sıra deterministik |
| S1-03 Paket şablonu | S1-01; source→task/decision/AC/evidence snapshot ve bounded metin | RES-02/06/07; kritik eksik bağlam görünür, raw transcript talimat değil; LLM çağrı sayısı sıfır |
| S1-04 Önizle/kopyala | S1-02/03; clipboard veya seçilebilir metin fallback | RES-03/04/05; explicit copy, stale/ACL negatifleri, copy run başlatmaz; prototype temel tıklama gerçekten test edilir |
| S1-05 Hafıza deney protokolü | S1-03; fresh-session koşulu, prompt/paket/full-source baseline ve puanlama formu | RES-08; model/config/context contamination/usage alanları ve izin kapısı; çalıştırılmadıysa not_run |
| S1-06 Pilot ve karar raporu | S1-04/05; önce sentetik, sonra yalnız izinli gerçek örneklem | Yanlış alarm ve kaçırılan iş için ayrı oracle; stale karar, next-step ve düzeltme maliyeti raporlu; go/no-go ve kalan açıklar |

Adımlar tamamlanmış sayılmaz. Üretim entegrasyonu mevcut backlog'da T20h/T18h/T24m ile izlenir; sıradaki ana iş T01 olarak kalır. Gerçek prototip ile ürün runtime'ı ve doküman taslağı ayrı teslim durumlarıdır.

## Hafıza değerlendirme formu

Her testte kaydedilecek alanlar:

| Alan | Kayıt |
|---|---|
| Kaynak kapsamı | Sentetik/izinli gerçek; proje/session/spans, snapshot ve gap |
| Oracle | Güncel karar/AC, beklenen next-action, yasak/eski adım ve gerekli soru |
| Koşul | Prompt-only / paket / full-source; fresh-session yöntemi; erişilebilir araç/context |
| Çalıştırma | Run ID, tarih, model/config, paket digest, tekrar, token/estimated/unknown, bütçe |
| Sonuç | Karar/AC doğru mu; next-step uygun mu; eski planı canlandırdı mı; false-done/izin aşımı var mı |
| Hata nedeni | Capture / extraction / retrieval / stale paket / alıcı model / unknown |
| İnsan değerlendirmesi | Düzeltme ihtiyacı, süre, anlaşılabilirlik, gerekçe ve reviewer |

Bir modelin “anladım” demesi başarı değildir. Plan/cevap güncel oracle ile puanlanır; gerçek kod execution ölçülecekse ayrı workspace/runner izni ve artifact doğrulaması gerekir. İlk memory testi yalnız sonraki adım önerisini puanlayabilir; bu, görevin bitirildiği veya dış hafızanın tüm sorunları çözdüğü anlamına gelmez.

## Çıkış kriterleri ve DoD

- RES-01–07 için deterministik/prototype test kanıtı veya açık not_run nedeni; temel UI gerçekten çalıştırıldıysa test artifact'i ve revision kaydı.
- RES-08 protokol ve rapor: örneklem, karşılaştırılabilir koşullar, tazelik/ACL, unknown tüketim ve izinli çalışma. Gerçek model deneyi yapılmadıysa sonuç yerine hazır protokol sunulur.
- Zorunlu fixture setinde yetkisiz veri/dispatch, kanıtsız tamamlanma ve eski kararı current gibi sunma kabul edilmez. Diğer başarı eşikleri baseline sonrası owner review'una gider; ölçümsüz yüzde veya optimum token hedefi yok.
- Negatif sonuçlar, kaçırılan işler ve yanlış uyarılar rapordan çıkarılmaz. Paket daha kısa fakat gerekli karar eksikse tasarruf başarısı sayılmaz.
- Go/no-go: kaynak/next-step yeterli ve kullanıcı düzeltme yükü kabul edilebilir ise dar entegrasyon öner; aksi halde capture/reconciliation/context eksiğini önce çöz. B başlatma seçeneği için ayrı capability ve izin kapısı devam eder.

Önerilen 3–5 gerçek oturum ve iki haftalık süre yalnız pilot adaylarıdır; takvim, veri erişimi, ücret veya başarı garantisi değildir. Hiçbir gerçek oturum/deney bu doküman hazırlanırken çalıştırılmadı.

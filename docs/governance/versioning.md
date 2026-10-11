# Tek güncel belge seti ve sürüm düzeni

**2026-10-11 — Bu dokümantasyon güncellemesinin düzeni.** Ürün release'i yok. Kullanıcı eski sürüm kopyalarının LLM ve commit sırasında kafa karıştırmamasını istedi.

## Bugünkü tercih

Repository'de **tek güncel belge seti** tutulur. main güncel giriş noktasıdır; README ve [güncel yön](../product/current-direction.md) başka modele neyi okuyacağını gösterir. Bu tur **tasarım revizyonu 03** olarak adlandırılır; repo v3, uygulama v3 veya üçüncü çalışan sürüm değildir. Önceki iki tasarım evresi sonradan açıklama için gruplanmıştır, geçmişte yayımlanmış v1/v2 ürünler olarak gösterilmez.

| Evre | Tanım | Kanıtlı geçmiş referansı |
|---|---|---|
| İlk ürün planı | Tam vizyon, karar-aware hafıza, P1a/P1b ve ileri fazlar | Önceki commitler; kaynak evrimi |
| Gerçekleşme ayrımının eklenmesi | Claude Projects örtüşmesi ve niyet→hedef uygulama sözleşmesi | `6889d48fbc2f75c4c36e81ba6ae370cc22e1d8ba` |
| Tasarım revizyonu 03 | Güncel yön, karşılaştırma kapısı ve mimari/şema/diagram/devir tutarlılığı | Bu değişikliğin Git commit'i; status kaydı |

README-v2, README-v3, docs/v1, docs/v3 veya yeni repository kopyaları oluşturulmaz. Eski içerik gerektiğinde commit ref'inden okunur. Eski tarayıcı/panel veya local mirror kullanıyorsan hedef branch ve commit doğrulanır; dosya adı/tarih tek başına son sürüm kanıtı değildir.

Mevcut `spike-1-v1.md` adı önceki deney belgesinin kimliğidir; aynı dosya güncellenir ve tek aktif deney referansı olduğu başında açıklanır. Eski dosya adı başka bir ürün sürümü yaratmaz. Görevden bağımsız dosya taşıma/isim temizliği yapılmaz.

## Yetki ve belge otoritesi

1. Güncel kullanıcı talimatı ve uygulanabilir AGENTS kuralları.
2. Ürün yönü: [current-direction](../product/current-direction.md); **tam scope**: [full-scope](../product/full-scope.md).
3. P1b sürüm kabulü: [MVP](../product/mvp.md); ilk deney bunun yerine geçmez.
4. Teknoloji gerekçesi: statülü ADR; proposed accepted/implemented değildir.
5. Gerçekleşmiş ilerleme: status; iş/AC: backlog; kaynak ve test ref'i açık.
6. Diagram, örnek JSON ve feature katalogları bu sözleşmeleri açıklar; kendi başına karar/DDL/test sonucu değildir.

Yeni dosya veya en yeni timestamp otomatik doğruluk otoritesi olmaz. Çelişki bulunduğunda alanına ait kaynağa göre düzelt ve karar gerekçesini kaydet.

## Birbirinden ayrı sürümler

| Sürüm | Ne zaman kullanılır? |
|---|---|
| Tasarım revizyonu | Bu dokümantasyon yön değişimini anlatır; Git commit kanıtıdır |
| Ürün release/tag | Çalışan dağıtım ve test/release planı oluşunca; bugün tag veya semver atanmadı |
| DB migration version | Gerçek storage uygulamasında fiziksel değişim ve rollback/recovery kontrolü |
| Event/API schema_version | Transport/event uyumluluğu; tasarım revizyonundan bağımsız |
| Record/decision/AC/artifact revision | Kullanılan bilginin ve kanıtın hangi sürümüne ait olduğu |
| ContextSnapshot/ResumePackage version | Türetilen paket/snapshot; canonical domain kararı değildir |

`schema_version: 1` örneği v1 ürün, task snapshot v3 örneği v3 ürün anlamına gelmez. Uygulama sürümlerinde breaking change ve migration şartı ayrıca belirlenir.

## Değişiklik teslimi

İlgili güncel dosyaları yerinde güncelle; ilgisiz değişikliği koru. Geçmiş öneriyi bugünkü talimat gibi göstermek yerine dated historical kayıt/ADR supersession kullan. Sırf daha önce proposed olan ayrıntı duruyor diye onu silme.

Commit mesajı somut değişimi anlatır; “v3 final” gibi kapsamı belirsiz isim verme. Commit öncesi güncel remote head ve dosya eşleşmesini kontrol et; branch güncellemesini beklenen head ile yap, force overwrite yok. Sonrasında değişen içeriği remote ref'ten geri oku. Kalıcı kontrol komutu `python3 scripts/check_docs.py`; ürün davranışı ve render kanıtı ayrıca raporlanır.

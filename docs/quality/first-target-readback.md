# İlk gerçek hedef kontrolü — READBACK-01

> [!NOTE]
> **Gerçek GitHub gözlemi / manuel kontrol / tek doküman.** Decivora adapter'ı veya ürün deneyi çalıştırılmadı. Q02-R2 A seçiminin ilk somut hedef kontrolüdür.

## Karar ve kapsam

2026-10-11'de kullanıcı, bekleyen Q02-R2 sorusuna **A** cevabı verdi: mevcut private Decivora reposundaki tek doküman ilk hedef. [Karar ve alternatif](../delivery/decision-brief.md#q02-r2--ilk-gerçek-read-back-hedefi) kaydı korunur. Yerel dosya yolu olan B sonraki senaryodur; desteklenip desteklenmeyeceği seçimi değildir.

Asistan, önceki turda hazırlanıp yayımlanan `examples/corpus/README.md` rehberini seçti. Kullanıcı bu exact dosya adını söylemedi; seçim, onaylanan hedef sınıfı içinde rutin uygulama tercihidir. Doğrulama bir dosyayla sınırlı; hesapların tamamına erişim, gerçek sohbet import'u, ücretli model veya target execution izni çıkarılmadı. Belge bakımı/yayınlama önceki repo talebinin yetkisiyle yapılır; read-back seçiminin kendisi yeni dış yazma yetkisi değildir.

## Beklenen artifact ve gözlenen hedef

| Alan | Gerçek gözlem |
|---|---|
| Repo | `alphanAkbulut/decivora`; gözlem anında private |
| Exact path | `examples/corpus/README.md` |
| Artifact yayım ref'i | `6de536e44b22d6f839aa7c94e3ca2444addb5115` |
| Yakalanan main / immutable gözlem ref'i | `6de536e44b22d6f839aa7c94e3ca2444addb5115` |
| Gözlem zamanı | 2026-10-11 15:54:36 UTC |
| Beklenen ve gözlenen SHA-256 | `65ff47445f51a92167409ebeca26bc4714ceab7b33b46bea636ec5443fbe16dd` |
| UTF-8 uzunluğu | 5477 byte |
| Tree blob SHA ve hesaplanan blob SHA | `0ecf4632868d161fc0d245785465457f686a8dfa`; eşleşti |
| Sonuç | **observed_match** — tek dosya/ref için birebir içerik eşleşmesi |

[Değişmez hedef dosyası](https://github.com/alphanAkbulut/decivora/blob/6de536e44b22d6f839aa7c94e3ca2444addb5115/examples/corpus/README.md). Repo private olduğu için bağlantı erişim yetkisi gerektirir.

GitHub connector main ref'ini ve immutable commit'teki dosyayı okudu. Dönen UTF-8 içeriği, yerel artifact byte'larıyla normalizasyon yapmadan karşılaştırıldı; iki SHA-256 ve byte uzunluğu eşleşti. Ayrıca hesaplanan Git blob kimliği repository tree'deki kimlikle eşleşti. Bu süreç elle yönlendirildi; çalışan Decivora connector/verifier değildir. [Makine tarafından okunabilir gözlem](first-target-readback.json) hangi sonuçların ölçülmediğini ayrı tutar.

## Kabul ve tamamlanma ayrımı

**Bu küçük kontrolün kriteri geçti:** seçilmiş doküman, belirtilen ref/path'te beklenen içerikle mevcut. “Dosya üretildi” iddiasına dayanmak yerine hedef tekrar okunarak karşılaştırıldı. Bir dosyanın varlığı/içeriği bütün corpus bundle'ının yüklenmesi, etiketlerin anlam doğruluğu, tüm task AC'leri, ürün çalışma başarısı veya deploy kanıtı değildir.

Bu raporda kaynak/karar/artifact/hedef bağı insan tarafından kuruldu. Otomatik konuşma çıkarımı, geç cevap eşlemesi veya insan approval doğrulayıcısı sınanmadı. Gerçek user cevabı Q02-R2'yi çözer; sentetik corpus'taki actor/grant verisi gerçek yetki sağlamaz.

## Açık kalanlar ve yeniden üretim

- **T01 IN_PROGRESS:** insan etiket review'u ve kalan kapsam/protokol açık.
- **T02d kısmi kanıt:** manuel GitHub happy path mevcut; missing/permission/partial/stale ve otomatik target capability testleri tamamlanmadı. T02'nin iki coding yüzeyi hâlâ TODO.
- **T03b/T09/T24q not_run:** çalışan harness, zorunlu otomatik anlam çıkarımı, native kıyas ve gerçek kalite/maliyet deneyi bekliyor.
- Ek ücretli model/provider çağrısı başlatılmadı. Host/geliştirme token tüketimi ölçülmedi; sıfır diye gösterilmez.
- Rehber gözlem sırasında değiştirilmedi. Sonraki doküman commit'i bu snapshot'ın tarihsel kanıtını silmez; değişen target ref'i için yeni gözlem gerekir. Sürekli izleme yapılmadı.

Yeniden üretimde exact ref'teki bu dosyayı yetkili GitHub bağlantısıyla al; beklenen artifact sürümünün UTF-8 byte'larıyla karşılaştır; SHA-256/uzunluk ve Git blob kimliğini kaydet. Yetki hatasını missing sayma, branch adını immutable ref yerine kanıt olarak bırakma. Bu tek gözlemin hashlerini elle yazmak yeni kontrol yapılmış sayılmaz.

# İlk corpus ve baseline hazırlığı

2026-10-11 — **T01 IN_PROGRESS.** İlk etiketli sentetik veri seti ve kontrol aracı hazırlanmıştır. **Ürün baseline ölçümü yok; insan oracle incelemesi pending, semantik/domain/host/UI ve ürün target adapter sonuçları not_run. Ayrı [READBACK-01](first-target-readback.md) tek gerçek GitHub dokümanının manuel içerik eşleşmesini doğruladı; ürün baseline ölçümü değildir.** [Corpus rehberi](../../examples/corpus/README.md), [manifest](../../examples/corpus/manifest.json) ve [gerçekleşen veri kontrol raporu](corpus-preparation-results.json) somut çıktılardır.

## Hazırlanan veri

6 oturum, aynı görünen “Atlas” adlı 2 ayrı proje; 58 kaynak mesaj, 66 annotation ve 46 farklı KnowledgeRecord kimliği. 51 anlamlı mesaj yanında 7 no-new-record örneği vardır. Kaynak ve beklenen sonuç ayrı dosyalardır; etiket source span, actor/project, relation, state/etki ve gerekçeyi taşır. Initial state ve trusted fixture metadata yalnız sentetik deney bağlamıdır, gerçek sistem yetkisi/kanıtı değildir.

Geliştirme: S01/S02 storage_evolution, S03 project_identity, S04 agent_authority. Ayrılan değerlendirme: S05/S06 release_revisions. Aile/continuation aynı split'tedir. Etiketler ürün/model prediction görülmeden bu AI çalışmasında yazıldı; aynı AI hem senaryoyu hem oracle'ı hazırladığı için ortak kör noktalar olabilir. İnsan tarafından etiketlendi/onaylandı diye sunulmaz. Hashler mevcut içeriği tanımlar, anlam doğruluğu kanıtı değildir.

## Kritik örneklerin okunabilir özeti

| Kaynak | Beklenen davranış | Korunan ayrım |
|---|---|---|
| S01-m01/02/10 | SQLite önerisi ve açık soru; “yarın bakacağım” soruyu kapatmaz | Öneri/erteleme ≠ seçim |
| S02-m01 | Exact Q_STORE/revision'a bağlı geç B cevabı SQLite seçimini çözer; sync ve AND iş obsolete/update adayı, OR iş retained, unknown gerekçe review | Karar onayı ≠ impact task kapatma onayı |
| S02-m04/05/06/07 | Yeni artifact revision 2 → “yükledim” reported → eski bundle current değil → güncel eşleşme observed | Generated / reported / observed / verified |
| S02-m09 | Tek rollback kriteri passed, diğer migration kriteri yok; bütün görev tamamlanmaz | Bir AC ≠ task DoD |
| S03-m04/06 | İki açık A/B sorusunda bağsız A ambiguous; izin hatası unknown, missing kanıtı değil | Eşleme / yetki / kapsam |
| S03-m10/11 | Öneri reddedilir; tarihçesi korunur ve yeni iş türetilmez | Rejected ≠ cancelled/done |
| S04-m02/04/06 | Agent run finished task verified değil; subagent onayı insan yetkisi yaratmaz; failed kanıt eski pass'i current olarak bırakamaz | Run / authority / task verification |
| S05-m05/06 | Option revision değişince eski A cevabı kaydedilir fakat yeni hosted seçeneği uygulanmaz | Geç cevap ≠ stale yetki yenileme |
| S05-m08, S06-m07 | İptal edilen iş/ilişkiler tarihçede kalır; olumsuz emir işi diriltmez | Cancelled ≠ done, silme değil tarihçe |
| S06-m02/03/04/05/06 | Partial ve yanlış target current bundle'ı doğrulamaz; güncel bundle + bütün scoped AC pass task kanıtı olabilir; yeni ref'te current kanıt stale | Target/ref/AC revision ve tarihsel pass |

S06'da staging hedefi seçimi canary stratejisini otomatik supersede etmez. İlk author incelemesinde bu kaynaksız edge adayı çıkarıldı; ortam ve rollout stratejisi ayrı boyutlardır. Veri kontrolünde dört örnekte boş kalan expected-effect assertions açıkça tamamlandı. Bağsız A cevabı yeni PendingDecision yerine ayrı AnswerRecord olarak etiketlendi; koşullu ifadede geçen yerel kurulum gereksinimi zaten onaylı başlangıç state'ine bağlandı. Bu düzeltmeler ürün runtime hata bulgusu değildir.

## MVP ve tam ürün sırası

Zorunlu gereksinimler uygulama seçenekleri değildir. Sıra/temsil kapsamı mevcut [MVP](../product/mvp.md), [tam kapsam](../product/full-scope.md) ve [faz görünümüne](../delivery/phase-tracker.md) bağlıdır.

| Öncelik/faz | Bu setteki başlangıç temsili | Zorunlu kalan kanıt |
|---|---|---|
| P0 / T01 hazırlığı | Kaynak/oracle, kimlik, aile split, kritik anlam/etki etiketleri | İnsan review'u, karşılaştırma koşulları ve remaining-case coverage |
| P1a çekirdek | Öneri/seçim, temel uzlaştırma gerekçesi, AND/OR/unknown, human/agent authority, evidence/AC ve retry beklentileri | Gerçek extractor/graph/event/replay/apply testleri; atomic crash/stale graph/expiry/revocation ve bütün truth-table fixture'ları |
| P1b kullanılabilir MVP | Late exact answer, subtask/parent, blocker/bağımsız iş, pending/brief, scoped target/bundle ve temel budget beklentileri | 14 AC, iki gerçek coding adapter, MCP/tools-only/capture farkı, UI tıklama, backup/restore, burst/load; FLOW 40+ task suite'i ve kaynak coverage |
| P2 kalite/erişim genişletme | İngilizce kaynak/TR çıktı tercihi yalnız sentetik erken regresyon örneği; belirsiz cevap visibility | Otomatik çok dil/mixed ve bütçeli serbest cross-session matching, orphan audit, gelişmiş retrieval/impact; gerçek GitHub evidence ve panel fizibilitesi |
| P3/P4 tam ürün | Ortak bütçe/alt agent yetki temel invariant'ı erken temsil edildi | Dış yazma connector'ları, derin ekonomi; gerçek ekip/membership/tenant ve dağıtık kapasite deneyleri ilgili fazda. Temel erişim/bütçe güvenliği bu fazlara ertelenmez |

Bu corpus **14 AC'nin tamamına yönelik çalışan test suite'i değildir**. Source/oracle'da davranışın anlatılması AC pass sayılmaz. Aynı şekilde bütün dil/graph/limit/permission senaryolarını kapsamış değildir. Tam kapsamdan hiçbir madde silinmedi; future testler burada hazır diye gösterilmedi.

## Gerçekleşen doğrulama

- Corpus validator: 6 session / 2 project / 58 message / 66 annotation / 46 unique KnowledgeRecord; source/oracle hash, exact Unicode span ve kayıt/referans bütünlüğü geçti.
- 11 negatif gate: yanlış span, stale hash, eksik oracle satırı, duplicate message/key, input'a expected sızması, false runtime pass, family split leakage, yabancı proje kaynak referansı, ghost relation ve yetersiz meaningful sayı reddedildi.
- Kontrol sadece veri/validator davranışını doğrular. Extraction precision/recall, false-done, capture başarısı, token maliyeti/latency, ürün replay'i veya read-back sonucu üretmedi.
- Ek ücretli model/provider deneyi başlatılmadı; overall host/geliştirme token harcaması sıfır veya ölçülmüş diye gösterilmez.

Repo kökündeki tekrar komutları corpus rehberindedir. JSON raporu validator/source/oracle/manifest hashlerini bağlar; kaynak değişince eski rapor yeni veri için kanıt olmaz.

## İnsan incelemesi ve T01 kapanışı

| Alt teslim | Durum / kanıt | Sonraki zorunlu iş |
|---|---|---|
| Kaynak ve expected kayıtlar | PREPARED: 6 session, 46 unique record, ayrı source/oracle | İnsan anlam/ilişki/state review'u ve anlaşmazlık kaydı |
| Veri kontrolü | PASSED: corpus validator + 11 mutant | Değişen veride hash/validation güncelleme |
| Holdout ayrımı | RESERVED_NOT_SEALED: S05/S06 aynı aile | İnsan review sonrası oracle revision; model/prompt/scorer pin ve taze değerlendirme koşulu. Bu konuşmayla tune edilen model için kör değerlendirme iddiası yok |
| T01e lexical corpus | PARTIAL: negation/quote/conditional/claim/explicit/ambiguous örnekleri | Ayrı 20 örnek/rubric kapsamını doğrula ve eksik kategorileri tamamla |
| T01f scorer/gold protokolü | PARTIAL: checkpoint/source/entity/relation ve hashler | Gold insan incelemesi, matching/error taxonomy'nin çalıştırılabilir scorer sözleşmesi ve required-check coverage |
| Domain/semantik baseline | NOT_RUN | T03f harness ve T09 gerçek extractor; expected anahtarı input'a verilmeden holdout; T24q sonuç raporu |

T01 bütünü kapanmadı. Reviewer şu alanları inceler: kaynağın niyeti doğru etiketlenmiş mi; cümlede olmayıp modelce eklenmiş iş/edge var mı; insan yetkisi/revision eksikse onay veriliyor mu; artifact/target/test durumları karışıyor mu; geç/ambiguous/ret/no-op korunuyor mu. Adjudication'ın kim/tarih/record/source ID/gerekçe kaydı tutulur. Kullanıcının bu corpus'u genel olarak beğenmesi her satırın reviewed olduğu kabul edilmez.

## Adım adım devam

1. T01 insan review'u ve kalan sentetik kapsam/protokol; eksik golden varsayımı hazır paket üzerinde somutlaştır.
2. Q02-R2 A hedef seçimi ve ilk manuel GitHub doküman kontrolü [READBACK-01](first-target-readback.md) ile yapıldı. Sonraki otomatik hedef deneyi source/target revision, missing/permission/partial/stale kapsamı ve gerçek veri/retention sınırını hazırlayıp test eder; tek happy-path gözlemi bu işi kapatmaz.
3. İlk no-model code dilimi → zorunlu otomatik anlam çıkarımı uygulaması ve ayrı kalite/maliyet deneyi. Model/veri/bütçe seçimi yürütme ayrıntısıdır, gereksinimi yapıp yapmama sorusu değildir.
4. Sonraki Codex B yolunda MCP read/proposal ve ayrıca capture capability/coverage doğrulanır. Native/extend/build yatırım kararı gerçek karşılaştırma ile alınır; fixture lint buna karar vermez.

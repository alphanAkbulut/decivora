# Toplu çalışan çekirdek teslimi

**Yerel, sentetik ve manuel profil.** İlk teslimin aşağıdaki hash/95-test sonucu tarihsel snapshot'tır; güncel [kritik düzeltmeler ve109test](core-critical-review.md) CR01–06 ile eklenmiştir. Beş ana çekirdek teslimi: T05 proje/binding, T06 receipt/jobs, T07 event/projection/recovery, T08 atomic approval/policy, T11 typed graph. T09 ve T10 için çalışan hazırlık kodu da var; gerçek semantik extraction/gold değerlendirmesi tamamlanmadığından bu iki görev Done değildir. [Kod](../../packages/storage/workspace.py), [31+ test ve integrated CLI](../../tests/runtime/test_workspace_core.py), [graph testleri](../../tests/runtime/test_dependency_graph.py), [hash/sonuç](integrated-core-results.json).

```sh
python3.12 -B -m apps.hub core-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

Demo boş temporary DB'ye iki aynı adlı proje kurar → current binding'i transaction içinde pinler → source/job kalıcı receipt → retry aynı receipt → structured/manual proposal → ayrı local human approval → atomik iki record/required_by link → processing frontier → replay → yedek → boş hedefe restore → duplicate karşılaştırması → scoped graph/AND-OR kontrolü. Ürün UI veya serbest metinden otomatik karar çıkarımı değildir.

| Ana görev / çekirdek kabul | Gerçek kod ve test |
|---|---|
| T05 / stable identity, same-name isolation, binding, quarantine | Normalized workspace/project composite PK/FK; binding history append-only; source→binding revision+project composite FK; current binding server transaction'da pinlenir. Unbound/mismatch immutable quarantine receipt olur, canonical proje değişmez; eski source taşınmaz; current scope query/write kontrolü |
| T06 / durable receipt, dedup, checkpoints | Source+job tek transaction; same identity/content/position retry aynı receipt, farklı mesaj/same text korunur; source hash check; known missing position frontier'ı ilerletmez. Rotation ayrı epoch; jobs queued/leased/retry_wait/succeeded/failed, persisted due, worker identity/fencing/expiry, bounded attempts/retry; session-end beklenmez, batch size1/manual pull |
| T07 / append-only event, version, replay | Event PK/version unique, SQL UPDATE/DELETE trigger ret; approved create/update/link projector ve source joins; unknown kind/schema ret; aynı input replay aynı projection digest, sıfır side effect. SQLite backup bütün DB+inline payload'ı tutarlı alır; manifest/hash/integrity/FK/source hash kontrolü ve sadece boş hedefe restore |
| T08 / atomic change, digest/base/idempotency/human policy | Temp IDs deterministik çözülür; links create'lerden sonra tek transaction'da uygulanır. Scoped human owner ayrı approval row+digest/knowledge/authz/key binding verir; agent owner approval ID'sini bilse bile approve/apply yapamaz. Half graph/stale writer/key-content conflict/duplicate/audit insert failure negatifleri; rollback sonrası hiç event/record/command etkisi yok |
| T11 / typed rationale/dependency graph | required_by ve depends_on ayrı; any/all/unknown truth table ve exact fact revision; empty unknown. Canonical apply'dan önce dependency/supersession cycle ret, other relation cycle mümkün. Scoped graph knowledge revision; unknown verification/eligibility ready olmaz.40-node unique downstream blocker baseline + age tie-break + reason/next-action; node/edge/depth limits |

## İlk kullanım sınırları korunur

Yeni `decivora-workspace-core-1` profili yalnız yeni seçilmiş private DB'de açık local owner bootstrap ile kurulur. Önceki ProjectStore/LocalAuthority DB'leri otomatik migrate edilmez; format/schema mismatch ret. Trusted local issuer insan hesabı login/kriptografik agent token kanıtı değildir. Anonymous network endpoint yok; native provider capture/runner/model dispatcher yok; input SourceEvent synthetic exactlytrue. Gerçek kaynak okuma izni veya gözetimsiz prod deploy bu kodla verilmez.

Bu nedenle T04b gerçek network activation gate'i T16 owner/first-use kaydında açık tutulur; manuel T06 kapanışı onu uygulanmış göstermez. T16/gerçek network kullanımı genuine transport/origin/consent testleri olmadan açılamaz. T04d local admission limits ve T04c physical schemas bu profile özgü doğrulandı; başka transport'ların HTTP/MCP mapping'i kendi entegrasyonunda doğrulanacaktır. Mevcut gereksinim/ID korunur; yeni görev eklenmedi.

## Gerçek korumalar ve sayıların anlamı

Payload32KiB source contract; workspace inline source quota16MiB; total active queue200/project share100; scoped actor20 new receipts/60sec; SQLite writer timeout2sec; default lease30sec/attempt3/retry delay5sec; graph10k nodes/20k edges/depth16; operation64/32KiB. Bunlar **bu sentetik development profilinin çalışan sınırlarıdır**, ölçülmüş production capacity/SLO veya owner'ın onayladığı ücretli API budget değildir. Clock değerini trusted scheduler sağlar; source text'ten alınmaz. Örnekteki kısa fake-clock süreleri gerçek provider timing ölçümü değildir.20 receipt burst ve tek project's share100 sonrası kabul reddedilir, önceki işler silinmez. Bir project diğerini tamamen monopolize edemez; geniş ekip fairness/SLO testi P4'tedir.

Local human-created root-run token cap≤100k; farklı agent/retry reservation'ları aynı root altında atomik sayılır; workspace aggregate cap100k farklı root'larla aşılamaz. Unknown usage tam reservation'ı tutar, bilinen actual ayrı settle edilir; amount/key conflict ve prior settled value rewrite ret. Caller agent yeni root açamaz. Bu rezervasyon kodu gerçek provider hard cap değildir; dışarıda bağımsız Claude/Codex tüketimini sınırlamaz. Semantic dispatch disabled kalır; para ve kullanım ölçümü unknown, fiyat iddiası yok.

## Açık kalanların net ayrımı

- **T09 In Progress:** Source-anchored structured draft validator, exact lexical context, bounded truncation ve provider-disabled guard uygulanmıştır. FTS/real free-text extractor/provider/holdout/fiyat/model testleri açık. Scripted candidates gerçek extraction başarısı değildir.
- **T10 In Progress:** Exact Unicode/case/whitespace duplicate → attach-source, aynı title/değişen body → relationship review; source/ref/base_version, rationale/counter-evidence/uncertainty korunur; canonical mutations0. Semantic conflict/refinement/revival ve golden precision/recall tamamlanmadı, eşit olmayan yeni metin otomatik true/active olmaz.
- **T12–T24:** Impact apply, tam verification/DoD/real adapters/MCP/ürün UI ve MVP14AC release/pilot kanıtı açık. T11 yalnız graph kernel ve baseline ordering teslimidir; gerçek proje süreleriyle kritik yol tahmini değil.

API kayıtlarında Task `verification`/eligibility bilinmiyorsa graph unknown/false hazır gösterir. Verifier kökeni T14'te bağlanacak. Worker succeeded yalnız source processing sonucudur; task completion değildir. Process kill testinde uncommitted audit transaction gerçekten ayrı Python process `os._exit` sonrası rollback oldu; elektrik kesintisi/OS/disk crash veya production load güvenilirliği kanıtlanmış sayılmaz. Backup privacy purge/retention/key recovery ve işletim RPO/RTO T23'te kalır. Physical DB adminine karşı trigger/hash garanti değildir; hostile filesystem race desteği iddia edilmez.

Bu teslim geçmiş model failure/gold/runtime hash raporlarını yeniden yazmaz. Ana kapanış manifestinde her mevcut alt kayıt scope/evidence ile eşlenir; future activation gate açık kalır. Test sayısı ürün tamamlanma yüzdesi değildir.

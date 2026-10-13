# Başka bir LLM bu repodan ne anlamalı?

Bu repo kaynak sohbet açılmadan ürünün amacı, evrimi, kapsamı, proposed mimarisi ve sıradaki işi anlaşılabilecek şekilde hazırlanmıştır. **Doküman tamlığı, uygulama doğruluğu veya modelin mutlaka doğru anlayacağı garantisi değildir.** Q15-A ile ilk uygulama iskeleti [T04](../../apps/hub/README.md) kendi12test/clean-start kabulüyle tamamlandı; T05f in-memory project/binding çekirdeği ve CLI demo da [uygulandı](../quality/project-binding-core.md); kalıcı store/gerçek IAM/ingress hazır sayılmaz. Model/capture/native/ROI/gerçek kullanıcı UI kabulü açık.

## Kısa giriş

Decivora geçici çalışma adıdır. Problem AI sohbetlerinde fikir/karar/prompt/yarım işlerin kaybolması ve yeni karar sonrası gereksiz işlerin açık kalmasıdır. Kullanıcı kart/DoD yazmak istemez, hazırlanmış onay vermeye razıdır. Ürün bütün çıktıları yakalamayı, eski bilgiyle uzlaştırmayı, gerekçe grafiğinde etkisini çıkarmayı ve revision'a bağlı kanıtla ilerlemeyi göstermeyi hedefler. Çok proje ve repo olmayan araştırma projeleri kapsamdadır. İlk tasarım local-first; Q15-A/ADR-0012 koşullu ilk çekirdek build'i ve Python3.12/SQLite runtime'ını kabul eder; frontend/ekip/cloud ve native/ROI sonuçları açık.

## Soru → yetkili belge

| LLM'in cevaplayabilmesi gereken soru | Okunacak yer |
|---|---|
| Ürünün problemi ve değişmez kullanıcı tercihleri ne? | [Vizyon](../product/vision.md), [AGENTS](../../AGENTS.md) |
| Fikir neden basit task tracker'dan farklılaştı? | [Evrim](../discovery/evolution.md), [karar haritası](../product/decision-map.md) |
| Hangi özellikler olacak, kullanıcı nasıl kullanacak? | [Tam kapsam](../product/full-scope.md), [özellik kataloğu](../product/feature-catalog.md) |
| MVP ne; hangi fikirler daha sonra? | [MVP](../product/mvp.md), [roadmap](../../ROADMAP.md) |
| Konuşulan engine'ler nerede? | [Engine ve alias haritası](../architecture/engines.md) |
| Sistem nasıl çalışacak ve yanlış nerede olabilir? | [Diyagram atlası](../architecture/diagrams.md), [runtime sözleşmeleri](../architecture/runtime-contracts.md) |
| Karar neden seçildi; kesinleşti mi? | [ADR dizini](../architecture/adr/README.md), [açık kararlar](../governance/open-decisions.md) |
| Veri, status ve ilişkiler ne demek? | [Domain](../architecture/domain-model.md), [event log](../architecture/event-log.md) |
| Neyi rakiplerden farklı hedefliyoruz? | [Farklılaşma](../product/differentiation.md), [kanıt seviyeli benchmark](../discovery/benchmark.md) |
| Şimdi ne yapılacak, nasıl bitecek? | [Status](status.md), [backlog](backlog.md), [kısa yönetim planı](project-management.md) |
| Receiver/yenichat ne durumda; hangi kod çalıştı? | [İlk gerçek failed run](../quality/receiver-001-result.md), [yerel schema/source guard ve akış](../quality/receiver-contract.md), [yeni RECEIVER-002 hazırlığı](../quality/receiver-next-plan.md), [wire-2 proje incelemesi](../quality/project-review-next.md); [RECEIVER-002 actual tek run](../quality/receiver-002-result.md) invalid_contract; Q03-R6 tüketildi, yeni inference izni yok |
| Tipli veriler için receiver hatası nasıl azaltıldı? | [T03aa kod/kanıt](../quality/typed-review.md): source-only deterministic taslak, model0; önceki failed actual raw ayrı, free-text extraction başarı iddiası yok |
| İnceleme kaydı program kapanınca saklanıyor mu? | [T03ab](../quality/review-store.md): iki sentetik profile SQLite snapshot/pending descriptor restart; source/access yeniden kontrolü. [T03ac](../quality/reply-store.md) explicit fixture late reply persistence ekler; actual insan approval/resolution/UI/IAM henüz yok |
| Hangi sonuç kanıt sayılır? | [Doğrulama](../quality/verification.md), [ölçüm](../quality/measurement.md) |
| Hangi eksikler bulundu ve hangileri hâlâ açık? | [Kapsam/mimari incelemesi](../quality/completeness-review.md) |
| İnsanların hangi şikâyetleri bu yönü destekliyor; karşı kanıt ne? | [Kullanıcı araştırması ve ters düşünme](../discovery/user-research.md) |
| Benchmark gerçekten çalıştırıldı mı? | [Bulgular ve test edilmemiş alanlar](../discovery/benchmark-findings.md) |
| Bekleyen işe yeni chat'te nasıl devam edilir; hafıza yeterli mi? | [Ürün önerisi](../product/resume-package-and-memory.md), [Spike-1 v1](spike-1-v1.md); production proposed/not_run. P0 [resume kodu](../quality/resume-compaction.md) ve [receiver sonucu](../quality/receiver-001-result.md) ayrı scoped kanıt |
| Pilot için owner neyi seçti, hangi yanıtlar bekliyor? | [Sorular ve cevaplar](decision-brief.md) |

## Belge otoritesi ve çelişki çözümü

Güncel yetkili kullanıcı talimatı ve uygulanabilir AGENTS kuralları izlenir. Ürün kapsamı full-scope, sürüm kabulü MVP, teknik gerekçe statülü ADR, güncel ilerleme status, görev AC'si backlog içindedir. Özellik kataloğu ve diagramlar bu kaynakların açıklamasıdır; yeni karar otoritesi değildir. Runtime sözleşmesi teknik öneriyi detaylandırır; ADR kabul edilmiş gibi yorumlanmaz. Kaynak sohbet tarihsel veri, rakip README'si documented iddia, test raporu yalnız belirtilen revision için kanıttır.

Çelişkide sessizce daha yeni dosyayı doğru sayma: farkı ve etkiyi kaydet, mevcut kabul edilmiş invariant'ı koru; uygulama yönünü etkiliyorsa somut karar iste. Bütün dokümanları her tur yeniden okutma; bu indeksle hedefli retrieval yap.

## Sözlük ve karıştırılmaması gerekenler

- **Source:** gözlenen mesaj/olay; talimat, doğru bilgi veya onay değildir.
- **Candidate:** çıkarılmış öneri; accepted task değildir.
- **Evaluation:** neyin hangi bağlamla değerlendirildiği; insan kararı değildir.
- **Canonical:** onay/policy sürecinden geçen güncel proje kaydı; evrensel doğru iddiası değildir.
- **ChangeSet:** atomik uygulanacak ilişkili operasyon önerisi; geçmişi düzenlemez.
- **ImpactRun:** belirli graph snapshot'ında reason path ve kapsamla yapılan etki değerlendirmesi.
- **Evidence:** belirli AC ve artifact revision'ı için kanıt; generic “done” metni değildir.
- **PendingDecision:** konusu/seçenekleri/blokladığı işler belli karar ihtiyacı; her belirsiz cümle kesin taahhüt değildir.
- **Obsolete / cancelled / superseded / completed:** sırasıyla gerekçe kalmaması / yetkili durdurma / yeni sürümle yer değiştirme / gereken kanıtın sağlanması. Aynı sütuna indirgenmez.
- **Engine:** modül sorumluluğu; ayrı servis veya ayrı agent şartı yoktur.

## Anlama kontrolü: beklenen cevaplar

1. Yeni mimari geldiğinde eski bütün işleri kapatır mıyız? **Hayır.** Tipli gerekçe, AND/OR/unknown, alternatif kullanım, current applicability ve insan onayı gerekir.
2. “Task done” mesajı gelirse? **Implementation claim.** Gerekli AC ve artifact revision kanıtı yoksa verified değil.
3. Yeni OR edge preview sonrası eklendiyse? **Stale impact.** Yeni snapshot/diff; eski onay taşınmaz.
4. Model kapalı veya budget doluysa? **Kaynak korunur.** Deterministik işler yapılabilir; semantik iş deferred/unknown görünür.
5. ChatGPT Chat içeriğine otomatik erişim garanti mi? **Hayır.** Yüzey/izin/build bazlı capability testi; açık import fallback.
6. Şimdi kurulabilir bir uygulama veya onaylı stack var mı? **Hayır.** P0; T01–T03 kanıt kapıları önde.
7. Knowledge Evolution Engine eksik bir ayrı servis mi? **Hayır.** ENG-03/04/05/06/07 birleşik davranışının kaynak konuşmadaki adı.
8. Üstünlük ve tasarruf kanıtlandı mı? **Hayır.** Hipotez/ölçüm planı var; benchmark runtime sonucu yok.

Sonraki LLM'den bu cevapları ve aşağıdaki ek kontrolü ilgili belgeyle destekleyebilmesini bekleriz. Bu bir **handoff kontrol protokolüdür**; bağımsız LLM deneyi yapılmış değildir.

## Ekip ve veri için ek anlama kontrolü

9. Owner'ın agent'ı owner gibi onay verebilir mi? **Hayır.** İnsan izni, dar grant, run, kaynak ACL ve policy kesişir; insan approval yetkisi devredilmez.
10. Private sohbetten türetilen özet ekibe otomatik açılır mı? **Hayır.** Kaynak erişimleri korunur; paylaşım ayrı redakte kayıt ve onaydır.
11. Context dolunca proje hafızası silinir mi? **Hayır.** Context geçicidir; canonical geçmiş ve dedup kimliği ayrı dayanıklılık taşır.
12. SQLite WAL denetim logu mu? **Hayır.** Domain log, security audit, source ve operational telemetry ayrı kayıt sınıflarıdır.
13. DB ekip büyümesine hazır mı? **Henüz uygulama yok.** Local SQLite ve merkezi PostgreSQL geçişi için ölçüm, migration ve recovery planı var; kapasite kanıtlanmadı.

Kaynaklar: [identity/access](../architecture/identity-access.md), [logging](../architecture/logging-audit.md), [storage/memory](../architecture/storage-memory-capacity.md), [benchmark](../discovery/collaboration-storage-benchmark.md), [fazlı işler](team-data-plan.md). Handoff protokolü artık 13 soruyu içerir; bağımsız model deneyi yapılmadı.

## Bağlantı, token ve graph için ek sorular

14. MCP kurmak tüm geçmişi yakalar mı? **Hayır.** [Capture, tool ve UI yolları](../architecture/connection-and-context.md) ayrı; tools-only coverage mümkündür.
15. MCP/token cache toplam tüketimi garanti düşürür mü? **Hayır.** [Host/arka plan ayrımı ve bütçe sözleşmesi](../architecture/routing-token-economy.md) yalnız kontrol edilebilen alanı sınırlar; kullanım/kalite ölçülmeli.
16. Task iptal edilince okları siler miyiz? **Hayır.** Task cancelled, edge ended/invalidated ve privacy purge ayrı işlemdir; [graph geçmişi](../product/graph-experience.md) korunur.

Handoff kontrolü toplam 16 sorudur; bağımsız LLM testi yapılmadı. Q04 güncel/seçili bağlamı, Q05 kullanıcıya proje/görev bazlı profil seçimini kabul eder. Otomatik context dosyası Q06 ve gerçek veri/bütçe Q03 ayrı sorulardır.

## Ürün önceliği için ek kontrol

17. Blocked task'ı sürekli tekrar çalıştırır mıyız? **Hayır.** Engeli kaldıran uygulanabilir adım/karar öne çıkar; dış beklemede hedefe katkılı hazır iş seçilir. Çok bağlantı tek başına yüksek değer veya ready kanıtı değildir.
18. Scrum yaklaşımı AI'nın Product Owner olması veya başlamış Sprint anlamına gelir mi? **Hayır.** Ürün değeri, engel etkisi ve küçük doğrulanabilir teslim ilkeleri kabul edildi. Ürün sorumluluğu kullanıcıda; uygulayıcı teknik planı yetkisi içinde yapar. Formal roller/takvim ve dış bildirim seçilmedi.

[Öncelik sözleşmesi](../product/priority-and-flow.md), [çalışma planı](project-management.md) ve [Q09](decision-brief.md) referanslardır. Kontrol toplam 18 sorudur; bağımsız LLM testi yapılmadı.

## Çok-agent ve ekip kurulum kontrolü

19. Tek insanın birçok agent'ını takip etmek için takım SaaS'ı veya özel düşünce erişimi gerekir mi? **Hayır.** İzinli task/run/tool/artifact kayıtları ve dar ortak hafıza yeterli temel; provider'ın sunmadığı input/parent bilinmiyor kalır. Agent'ı başlatmak ayrı yetkidir.
20. Ürünü ekibe vermek owner hesabını/DB dosyasını paylaşmak mıdır? **Hayır.** Merkezi servis, ayrı üyelik/oturum ve agent grant'leri gerekir; kişisel kaynakların paylaşılması ayrı onaylıdır. Bugün ekip kurulum paketi veya SaaS yoktur.

[Agent ve ekip işletim belgesi](../architecture/agent-and-team-operation.md) iki senaryoyu, test kapılarını ve platform kaynaklarını açıklar. Toplam 20 kontrol sorusu; bağımsız LLM deneyi yapılmadı.

## Subagent soru yönlendirme kontrolü

21. Parent agent subagent'ın her sorusuna kullanıcı yerine karar verebilir mi? **Hayır.** Bilgi/görüş sağlayabilir ve kendi yetkisi içindeki teknik seçimi yapabilir. Scope/AC/izin gibi korunan karar güvenilir insan approval'ı ister; agent'ın “owner kabul etti” mesajı yeterli değildir.
22. Soru cevaplanınca bütün görevler otomatik devam edip tamamlanır mı? **Hayır.** Revision/izin ve diğer blocker'lar kontrol edilir. Yalnız bağlı işler bekler; bağımsız işler ilerleyebilir. Host delivery/resume desteği yoksa destek varmış gibi gösterilmez; görev completion yine kanıta bağlıdır.

[Soru/karar sözleşmesi](../architecture/agent-and-team-operation.md#5-subagent-soru-sorunca-karar-kime-gider) timeout, parent kaybı, döngü, çelişki ve geç yanıt istisnalarını tanımlar. Toplam 22 kontrol sorusu; bağımsız LLM testi yapılmadı.

## Güncel yatırım ve gerçekleşme anlama kontrolü

23. Şimdi ürün v3 veya bitmiş yeni MVP var mı? **Hayır.** [Tasarım revizyonu 03](../product/current-direction.md), aynı tam vizyonun ilk kanıt odağını günceller. Tek güncel set main'de; geçmiş Git'te, [sürüm düzeni](../governance/versioning.md) product/schema/task sürümlerini ayırır.
24. Dosya üretimi, yeni soruya geçiş veya agent “kullanıcı seçti” özeti yeterli mi? **Hayır.** Güvenilir insan selection'ı, generated artifact, exact target application ve AC verification ayrı. [Domain](../architecture/domain-model.md#artifact-ve-hedef-uygulama-gözlemi), [ER-03](../architecture/data-relationships.md#er-03--artifact-hedef-uygulama-ve-kabul-ayrımı), [GAP oracle](../../examples/intent-reality-scenario.json).
25. İlk prototipten sonra mutlaka bağımsız ürün mü? **Hayır.** T03a yöntem → T03b yetkili deney → T03c native/extend/build/ek deney/durdur. Native Projects kıyası yoksa üstünlük unknown; test edilmiş typed fixture actual capture/fresh-session başarısı değildir.

Güncel kontrol toplamı **25**; önceki toplamlar tarihsel ekleme kayıtlarıdır. Bağımsız LLM anlama testi henüz yapılmadı. İlk okuma güncel yön→status→T01; geniş roadmap koşullu yatırım yoludur.

## Ürün değerlendirmesi ve kaynak alımı için ek okuma

[Portföy vaka çalışması](../portfolio/product-evaluation-case-study.md), owner rolünü ve AI destekli katkıyı gerçek kanıt sınırıyla gösterir. [Kod/teknoloji raporu](../discovery/code-reuse-assessment.md) tüm manifest alanlarının yapısal taraması ile R01–24 seçili davranış okumalarını ayırır. 9.657 dosya indeksi semantic audit veya test sonucu değildir. Governance ve contract graph örtüşmesi önceki hedefli benchmark'ı genişletir; EvidenceValidator bulgusunu bütün upstream verification yüzeyine genelleme. A/B/C owner seçimi, nihai stack ve runtime kod alımı henüz yok. T03d öneri ve T01 sırası korunur.

## Ekosistem araştırması devir notu

[T03e](../discovery/ecosystem-research.md) 10 ek repo için immutable ref/root lisans ve beş seçili source okumasını toplar; [JSON](../discovery/ecosystem-candidates.json) gerçekten okunan yolları listeler. ER-R1 masa başı çıktısı mevcut; ER-R2–4 TODO, ER-T1–5 not_run. D/S kanıtını V runtime sonucu sayma. Graphiti temporal invalidation, LangGraph wait/resume ve LiteLLM reservation özgünlük karşı kanıtıdır; semantik uyum/closure/unknown-cost/premium gate'ler henüz tam deneyle doğrulanmadı.

Öncelikli derin inceleme Graphiti/LangGraph/LiteLLM; ekip authorization OpenFGA/Cedar koşullu, Temporal dağıtık ihtiyaçta. Bunlar teknoloji/ücretli hizmet/kod alımı seçimi değil. Native/config/extension/own seçenekleri, Q13 ve T01 sırası korunur. Repo sayısını artırmayı ilerleme ölçütü sayma; açık contract sorusu için 1–2 aday yeterliyse dur.

## Ölçüm sorusu ve somut teknik boşluklar

“Nasıl ölçeriz, yöntem net mi?” sorusunda [teknik protokolü](../quality/evaluation-protocol.md) oku. Metrik/eşik ve oracle yaklaşımı mevcut; çalışan scorer/harness/adapter/telemetry ve gerçek karşılaştırma yok. [CHAIN-01](../../examples/decision-impact-evaluation-case.json) yedi checkpoint/dört negatif varyant illustrative taslaktır, T01 corpus/holdout veya V pass değil. T01f/T03f/T24q TODO. Domain authority/target/state code oracle ile; serbest açıklama human rubric, optional judge yalnız ek izin/bütçeyle.

Graphiti graph-building eval ve Langfuse Python SDK source/test hedefli okundu; iki repo değerlendirme örüntüsü için faydalı, bizim domain doğruluğumuzun hazır oracle'ı değil. Missing score/evaluator error critical gate'i incomplete yapar. Yeni framework, paid telemetry veya kod alımı yok; T01/Q03/Q13 korunur.

## Teknik boşluklar ve inceleme hafızası

[2026-10-11 TG-01–24](../quality/technical-gap-analysis.md) inceleme ref'i/yöntemi, iki somut doc conflict, önerilen ayrıntılar, implementation/capability/owner/measurement ayrımı ve sonraki soruları tutar. “Boşluk var mı?” sorusunda her şeyi yeniden yok sayma; ilgili TG→[IC-01–08](../architecture/implementation-contracts.md)→canonical task→closure evidence zincirini aç. Yeni component/release/accepted ADR yok. IC testleri not_run; son task ID düzeltmesinde dil T24p korunup ölçüm T24q oldu. Source/generated/accepted/observed/verified ve doc pass/runtime pass ayrımını açıklayamayan model uygulamadan önce ilgili bölümü yeniden okumalı.


## İlk pilot yolu — Q02-R1 kabul kaydı

2026-10-11: kullanıcı maliyet odağıyla **A açık aktarım + tek read-only hedef** yolunu ilk pilot için seçti; **B Codex coding oturumu + tek repo** sonrasında görülmek isteniyor. C Claude Code-first seçilmedi, alternatif korunur. İlk yol sorusunu tekrar sorma; [kaynak, alternatifler ve gerekçe](decision-brief.md) kayıtlıdır. B'de MCP hedefli bağlam/öneri araçları ile ayrıca host/build capability deneyi isteyen otomatik capture ayrıdır. Somut kaynak/hedef/host ve sonraki gerçek veri/provider/bütçe açık; ücret veya gerçek veri okuma izni çıkarma. T01 IN_PROGRESS: [ilk corpus/baseline hazırlığı](../quality/baseline.md) mevcut, insan review'u pending; diğer 29 ana görev TODO, pilot not_started. Q03-R1 A 2026-10-11'de kabul edildi: ilk deney ek ücretli model API'si olmadan sentetik/elle etiketli fixture + deterministik kontrollerle ilerler. Bu soruyu tekrar sorma; otomatik anlam çıkarımını uygulamak ve gerçek extractor/holdout ile test etmek zorunlu sonraki adımdır; T09/T24q kapsamında `not_run`. Native/fresh-session model kalitesi de fixture sonucuyla doğrulanmaz. Q03-R1 B yalnız erken başlama alternatifidir; özelliği reddetme seçeneği değildir. Gelecek paid provider/veri/bütçe kararı kapanmadı. Görsel tur sonrası toplam 35 Mermaid/15 belge; güncel inventory/render kaydı ürün runtime kanıtı değildir.

## İlk somut hedef — Q02-R2 A

2026-10-11: kullanıcı private Decivora reposunda tek dokümanı ilk read-back hedefi seçti. Asistanın exact path tercihi `examples/corpus/README.md`; [READBACK-01](../quality/first-target-readback.md) önceki yayım ref'inde manuel içerik/SHA-256/blob eşleşmesi kaydeder. Q02-R2'yi tekrar sorma. Yukarıdaki `pilot not_started` end-to-end ürün deneyi içindir; artık tek manuel target gözlemi vardır. Otomatik source/answer/approval eşleme, adapter/harness/extractor/native/UI testleri çalışmadı. T01 IN_PROGRESS; T02/T03b kapanmadı. Gerçek sohbet/host erişimi ve sonraki provider/veri/bütçe ayrıntıları açık; target seçimi geniş hesap veya ücret yetkisi vermez.


## Audit sonrası çalışan P0 kanıtı — 2026-10-11

[Audit düzeltme kaydı](../quality/audit-remediation.md) güncel sonuçları gösterir. T01/T02/T03 IN_PROGRESS; ürün MVP’si ve production stack seçilmedi. Spike-0 fixture capture/regresyon kodu, typed karar–etki–kanıt zinciri ve bağımsız lexical scorer çalıştırıldı. Üstteki geçmiş “scorer/prototype yok” cümleleri bu ekten önceki duruma aittir. İnsan etiket incelemesi, zorunlu gerçek semantik çıkarım, iki gerçek coding-host capability testi, devam paketi/simple/native kıyası hâlâ kapanış işleri. Deney kodunu ürün auth/permission/DoD garantisi sayma; exact komutlar AGENTS ve spike README’lerindedir.


**Güncel P0 kod devamı:** [Implementation readiness](implementation-readiness.md) ve [semantik bağlantı](../../spikes/semantic-chain/README.md) source-only prepare/output import/validation/selection bridge/checkpoint testlerini gösterir. İnsan incelemesi bu hazırlığı bekletmez. Ayrı model provider dispatch, production auth, gerçek target ve native kıyas not_run; T01/T02/T03 ana kapıları açık.

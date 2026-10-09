# Başka bir LLM bu repodan ne anlamalı?

Bu repo kaynak sohbet açılmadan ürünün amacı, evrimi, kapsamı, proposed mimarisi ve sıradaki işi anlaşılabilecek şekilde hazırlanmıştır. **Doküman tamlığı, uygulama doğruluğu veya modelin mutlaka doğru anlayacağı garantisi değildir.** Çalışan uygulama yok; yeni LLM uygulama varmış gibi kurulum/test sonucu üretmemelidir.

## Kısa giriş

Decivora geçici çalışma adıdır. Problem AI sohbetlerinde fikir/karar/prompt/yarım işlerin kaybolması ve yeni karar sonrası gereksiz işlerin açık kalmasıdır. Kullanıcı kart/DoD yazmak istemez, hazırlanmış onay vermeye razıdır. Ürün bütün çıktıları yakalamayı, eski bilgiyle uzlaştırmayı, gerekçe grafiğinde etkisini çıkarmayı ve revision'a bağlı kanıtla ilerlemeyi göstermeyi hedefler. Çok proje ve repo olmayan araştırma projeleri kapsamdadır. İlk tasarım local-first; stack ve build/extend seçimi henüz öneridir.

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
| Hangi sonuç kanıt sayılır? | [Doğrulama](../quality/verification.md), [ölçüm](../quality/measurement.md) |
| Hangi eksikler bulundu ve hangileri hâlâ açık? | [Kapsam/mimari incelemesi](../quality/completeness-review.md) |
| İnsanların hangi şikâyetleri bu yönü destekliyor; karşı kanıt ne? | [Kullanıcı araştırması ve ters düşünme](../discovery/user-research.md) |
| Benchmark gerçekten çalıştırıldı mı? | [Bulgular ve test edilmemiş alanlar](../discovery/benchmark-findings.md) |
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

# Görev kapanış ve açık kayıt denetimi

**2026-10-13 · Mevcut kayıt denetimi; kapanış düzeni önerisi henüz kabul edilmedi.** [Makine okunur envanter](task-closure-audit-results.json). İncelenen başlangıç ref'i: `3e2bbb209f9ba60e3108fb4f4cdd5454fdff9f25`. Kapsam: 30 ana görev, backlog'da tracker'ın gördüğü117 alt dilim; MVP14AC, faz ağacı, bağlı team/data planı, açık kararlar, güncel handoff ve readiness. Bu doküman repo çapında kod güvenliği veya bütün kaynakların semantic audit'i değildir. Yeni runtime/model deneyi yapılmadı.

## Sonuç

Gerçek ürün boşlukları vardır; her `açık` metni bugünkü kod geliştirmeyi durduran iş değildir. Bir feature olmadan ürün eksik olabilir; aynı feature'ın ilerideki entegrasyonunun eksik olması bugünkü modülün çekirdek teslimini sonsuza kadar açık tutmamalıdır. Kapanış kanıtı, ilk kullanımdaki güvenlik kapısı ve MVP release kabulü ayrı izlenmelidir. Gereksinim silme veya başarı eşiğini düşürme önerilmiyor.

Ana sayım1 DONE/4 IN_PROGRESS/25 TODO doğrudur. T05f/g/h Done, T05 In Progress olarak scope'larıyla korunur.117 alt satırın tracker görünümü30 DONE/12 TODO/5 IN_PROGRESS/63 UNSPECIFIED/7 PROPOSED. `UNSPECIFIED` kanıtlanmış63 eksik iş veya63 gereksiz iş değildir: satırda açık status yok; genel bölüm notu ile satır metadatası ayrılıyor. `PROPOSED` onaylı zorunlu implementation diye parent'a eklenemez. Team/data planındaki T05b/T08b gibi satırlar tracker'ın backlog-only alt envanterinde görünmez; bu nedenle117 bütün cross-file backlog evreni değildir.

## Bulgu sicili

| ID | Bulgu / kanıt | Önemi | Bu tur / önerilen çözüm |
|---|---|---|---|
| CL-01 | T05→bütün child kapanışı varsayımı→T05d→T08b→T08→T07→T06→T05 | High planlama deadlock riski. Ana görev bağımlılıkları tek başına cycle değil; tüm parent-child kabulü gate yapılırsa oluşur | Q16: çekirdek ve entegrasyon acceptance'ını ayrı sahiplik/kapıda tut; bağımlılık silme yok |
| CL-02 | T04 Done fakat T04a/b/c/d satırları UNSPECIFIED; bölüm “her dilim TODO, parent bütün dilimler bitince kapanır” diyor | High kapanış tutarsızlığı. T04 startup12test kanıtı gerçek; network/auth/querycursor tamamlanmış değil | T04 tekrar otomatik açılmaz veya alt satırlar Done olmaz. Q16 sonrası T04 startup teslimi ile ilk-ingress/T06 ve MCP/T18 entegrasyon kapıları açıkça ayrılmalı |
| CL-03 | T03c Done/ADR0012 accepted iken backlog/current next-action/open-decisions içinde stack/investment “açık” | Medium stale karar kaydı, gereksiz tekrar soru/iş | Güncel summary'ler Q15-A ile düzeltildi; native/ROI/frontend/lisans açık tutuldu |
| CL-04 | T01 next-action Q03-R6 izin bekliyor; gerçek RECEIVER002 run tüketildi | Medium yanlış onay engeli | T01 metni tüketilmiş izin olarak düzeltildi; yeni model grant yaratılmadı |
| CL-05 | Faz görünümü son “bugünkü snapshot” 27TODO/3aktif; handoff “onaylı stack yok” diyor | Medium takip güvenilirliği | Güncel1DONE/4aktif/25TODO ve conditional accepted runtime eşleştirildi; tarihli eski status tarihçesi korunur |
| CL-06 | “bir küçük PR/oturum” ifadeleri geniş cross-cutting acceptance setine karşılık geliyor | Medium belirsiz bitiş boyutu; özellikle T01/T03/T05/T18/T24 | Q16 sonrası execution package/task-local closure manifest; yeni özellik veya tarih/efor vaadi değil |
| CL-07 | T05 “kalan” gerçek ingress'i bekliyor, T06 T05'e bağlı | High sınır belirsizliği, CL01'den ayrı minimal döngü | T05 core izin/binding contract ve T06 source receipt/quarantine entegrasyonuna ayrı test sahipliği önerilir |
| CL-08 | Tracker ana görev status eşleştiriyor; kapanış AC/bütün child/missing team-data/dependency cycle doğrulamıyor | Medium mevcut testlerin kapsamı yanlış anlaşılabilir | Doküman kontrolü geçti demek parent kapanışı semantik olarak doğru demek değil. Q16 sonrası closure validation eklenmeli |

Bu planlama bulguları otomatik runtime güvenlik açığı veya veri kaybı kanıtı değildir. Sonraki fazdaki işi hemen yapmama ile zorunlu kontrolü kaldırma birbirine karıştırılmaz.

## Kalanların anlamı ve gerçek kapıları

| Açık alan | Tamamlanmazsa ne olur? | Ne zaman gerçekten engel? |
|---|---|---|
| Gold/adjudication/holdout (T01) | Genel model doğruluğu ve başarı oranı güvenle iddia edilemez | Semantik kalite/genelleme ve T24 release kabulü; storage kodu değil |
| Gerçek Codex/Claude capture (T02,T16,T17) | Tam otomatik iki-adapter MVP iddia edilemez | İlgili kaynak activation ve AC11/14; manuel sentetik local çekirdek değil |
| Receiver shape/source/ambiguous question kalitesi (T03,T09) | Yanlış soruya karar bağlama riski; valid draft garantisi yok | Semantik dispatch ve quality/release kapısı; başarısız raw kanıtlar korunur |
| Native/ROI kıyas (T03) | Üstünlük/ekonomi/nihai yatırım faydası ölçülmemiş olur | Ürün yatırım yeniden değerlendirmesi; kabul edilmiş Q15 conditional core start'ı geri almaz |
| Connection/session permission receipt (T05c) | Kaynağın seçilme/izin provenance'ı tamamlanmamış kalır | Gerçek/ilk source activation öncesi core contract gerekir; model/source grant kendiliğinden yok |
| Durable ingress/quarantine/checkpoint (T06) | Alındı denilen kaydın restart/crash'da korunması güvenilemez | İlk receipt/ingress kullanımı; T05 tek başına source receipt değildir |
| Event/projection + backup/restore (T07,T07c,T15,T23) | Geçmiş/current-state/recovery kabulü yok | Domain uygulama/T15 teknik kapı ve gerçek veri; kapsamlı operasyon T23'te |
| Approval/policy/evidence (T08,T13,T14) | Kaynaktan çıkan öneri güvenilir decision/done sayılamaz | Karar/etki uygulama ve task verification öncesi; agent claim hiçbir aşamada kanıt olmaz |
| UI/graph/MCP (T18–T20) | Kullanılabilir ürün/pilot yolculuğu eksik | İlgili kullanıcı akışı ve MVP release; CLI modül testinin bitişi değil |
| İleri otomasyon/connector/cloud/team (T25–T30,C01–06) | Tam vizyonun sonraki kabiliyetleri yok | Kendi faz/ilk kullanımı; mevcut MVP kapanışında tamamlanmış olmaları gerekmez |

MVP14AC korunur. “Proje bitti” tek bir tüm-vizyon olayına bağlanamaz: bugün teknik modül teslimi, sonra MVP kabulü, ardından kendi faz kabiliyetleri vardır. Her fazın bitişi gözlenebilir kapsam ve kanıtla ilan edilir; yüzdelik takvim tahmini türetilmez.

## Q16 — Somut kapanış düzeni önerisi

**A — Önerilen:** Ana görevin o teslimde uygulanabilir, kabul edilmiş çekirdek kriterleri için açık bir kapanış manifesti. Her kalan child'ın `task-local / integration / release / future-proposed` sınıfı, sahibi, kullanımdan önce gereken gate'i ve kanıtı kaydedilir. Sonraki modüle bağlı entegrasyon işinin kendi kaydı açık kalır; parent'ın çekirdek teslimini bekletmez. First-use güvenlik/izin/veri-koruma kontrolü hiçbir sınıflamayla atlanamaz.14MVP AC ve test kriteri korunur. T04 kanıtını retroaktif büyütme yok; T05 review sonrası kendi çekirdeği gerçekten yeterliyse kapanır, otomatik değil. Çapraz dosya ID'leri/cycle/dangling/unclassified remainder kontrolü eklenir. T06'nın “permission/binding yeterli mi?” başlama gate'i gerçek rapora bağlanır.

**B — Mevcut genel kuralı koru:** Parent'a yazılmış bütün ilgili alt dilimleri kapatmadan parent kapanmasın. Bu durumda CL01/02/07 dependency loop ve kapsam çelişkileri, development başlamadan açık dependency refactor ile giderilmelidir; mevcut T04 Done yorumunu da yeniden değerlendirmek gerekir. Aynı gereksinimleri küçük çalışma paketlerine bölmeden bu yöntem ilerlemeyi daha zor gösterir.

**Mevcut → tespit → değişiklik → fayda → risk → hedef → doğrulama:** Genel parent-all-child kuralı → downstream gate/accepted decision stale kayıtları → A kapanış manifesti ve ayrı integration/release gates → dürüst Done ve ilerleyebilir sıra → yanlış sınıflamayla güvenlik kontrolünü geciktirme riski → backlog/phase/team-data/status/tracker closure checks, gerektiği kadar ilgili şema/diyagram → AC mapping/cycle/owner/first-use validator + mevcut runtime/regresyon testleri ve remote readback. Bu ürün kabul/kapanış politikası değişikliği önerisidir; owner yanıtı olmadan uygulanmadı.

## Bu tur yapılan sınırlı düzeltmeler

Güncelliğini yitirmiş karar/sayım/izin summary'leri düzeltildi. T01/T02/T03/T05 state'leri veya14AC değiştirilmedi. Tarihsel rapor/hashler ve tarihli ilerleme kayıtları korunur. Yeni mimari/runtime kodu yok, Mermaid blokları değişmedi. All30/117 envanter yeniden üretilip bağlantı/anchor/phase/progress kontrolü yapılır. Bir sonraki audit guard, statik metin araması değil gerçek closure ilişkileri üzerinden hazırlanmalı; aynı check'i gereksiz bütün repo araştırmasına dönüştürme.

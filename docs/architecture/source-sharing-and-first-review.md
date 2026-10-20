# Yeni kaynak paylaşımı ve ilk görev kapsamı

**20 Ekim 2026 · Sprint1 · T09/T13/T17/T19/T21/T22.** İki yerel ürün bağlantısı kodlandı: yeni kaynağın exact model paylaşım onayı ve ilk Task review'ında AC/DoD veya bağlı kapsam sorusu. Bu, yeni ücret/erişim izni veya MVP release kabulü değildir.

## Kullanıcı yolculuğu

1. Capture veya paste ile kaydedilmiş, henüz analiz edilmemiş kaynağı Conversations'ta aç.
2. Model, çıktı token tavanı, izin bitişi ve paylaşım gerekçesini seç. Provider/model seçenekleri ve para/HTTP/input tavanları güvenilir startup profilinden gelir; browser para tavanı, key, ledger veya endpoint değiştiremez.
3. Preview exact source and context ile maskeli kaynak, aynı thread'in sınırlı önceki metni ve ilgili canonical proje context'ini incele. Bu adım yerel; provider çağrısı yok.
4. Ayrı checkbox ve onayla exact source/context/payload hash'ine bağlı grant oluştur. Bu onay aktivasyon veya dispatch değildir.
5. Onaydan sonra aynı kaynak kartındaki **Start approved analysis** düğmesiyle tek exact kaynak için ayrı aktivasyonu ve kuyruk geçişini başlat. Consent tek başına çağrı başlatmaz. Sources ekranındaki manuel Paused→Active ve bounded worker yolu da korunur; yeni düğme daha geniş kaynak veya gelecek mesaj izni vermez.
6. Modelin Task önerisini ilk kez kaydederken iki açık seçenek vardır: insanın yazıp onayladığı AC/DoD ile kaydet veya kapsam eksikse aynı Task'a bağlı bir netleştirme sorusuyla kaydet.

Varsayılan seçim kapsamı netleştirmektir; başlık veya “başladım” cümlesi kriter diye doldurulmaz. Sistem soru metni **önerilen insan review taslağıdır**, kaynakta zaten sorulmuş soru veya model alıntısı diye sunulmaz. Task+contract ya da Task+clarification tek transaction'dır. AC/DoD onayı sonuç/evidence üretmez: kriterler not_run, Task To Do kalır. Kapsam sorusu ikinci Task, otomatik Blocked veya otomatik karar değildir.

## Paylaşım ve harcama sınırı

- Profile yalnız startup'ta `--model-policy`, `--model-ledger`, `--model-key-file` üçlüsüyle veya güvenilir injected fixture ile sağlanır. Başlangıç policy metadata'sını okur; key veya provider okunmaz/çağrılmaz. TEST gerçek bağlantıyı kabul etmez.
- Mevcut entegrasyon shared development PilotTransport sözleşmesini kullanır: exact payload whitelist, sabit provider, tools=[], store=false, shared dispatch/HTTP/USD ledger, unknown rezervinin korunması ve retry yasağı aynen kalır. Genel account billing veya yeni bir ücretli plan yönetimi değildir.
- Mevcut ledger'ın root politikası yerinde değiştirilemez; kullanıcı browser'dan yeni para tavanı ya da yeni ledger gönderemez. Güvenilir host tarafında açık owner süre onayıyla, predecessor kanıtı ve birikimli kullanım taşınarak successor policy oluşturulabilir; eski source consent yeni policy digest'ine taşınmaz. Expired profil yalnız görünür; yeni sharing approval/dispatch reddedilir. Önceki $3 limiti **kalan bakiye değildir**; eski kullanım ve unknown rezervleri korunur.
- Her grant actor/project/source hash, current authz, context hash, model/output/reservation ve expiry'ye bağlıdır. Proje/karar/soru/AC değişirse paylaşım önizlemesi stale olur; yeniden gözden geçirmek gerekir.
- Yerel token budget aynı policy hash'i altında idempotent oluşturulur; startup yapmaz, approval yapar.100.000token implementation güvenlik tavanıdır; para onayı yerine geçmez. Her dispatch profile input tavanı + seçilen output kadar ihtiyatlı token rezervasyonu taşır; sayım/generation ve USD enforcement transport'ta ayrıca kalır.
- Paylaşım approval audit'i başarısızsa token budget ve source grant birlikte rollback olur. Existing budget cap büyütülmez/sıfırlanmaz. Yeni policy digest eski source consent'i yeniden kullanamaz.
- Factory artık seçilen activation'a bağlanabilir; dynamic activation desteği worker için de aynı current revision/admission kapısını kullanır. Diğer eski fixed registry'lerin sözleşmesi değişmez.

```mermaid
sequenceDiagram
  accTitle: Kaynağın paylaşım onayından ayrı model gönderimine
  accDescr: Önizleme yereldir. Kaynak ve proje bağlamının exact onayı grant üretir; aktivasyon ve dispatch ayrıca gerekir. Güncellik veya süre değişirse yeni gönderim reddedilir.
  actor H as Kullanıcı
  participant UI as Conversations ve Sources
  participant D as Workspace SQLite
  participant P as Paylaşılan transport policy
  participant M as Model API
  H->>UI: Model, token, süre ve paylaşım gerekçesi
  UI->>D: Kaynak ve context snapshot - payload hash
  D-->>H: Exact veri önizlemesi - çağrı yok
  H->>UI: Veri paylaşım onayı
  UI->>D: Token budget ve exact source grant atomik kayıt
  Note over H,M: Henüz model çağrısı veya Task uygulaması yok
  H->>UI: Onaylı tek analizi başlat / ayrı bounded start
  UI->>D: Current source, context, grant ve activation kontrolü
  alt Stale veya expired
    D-->>H: Yeni gönderim reddi - kapsamı tekrar incele
  else Geçerli admission
    UI->>P: Aynı exact payload ve ortak bütçe
    P->>P: Kalıcı rezerv, unknown ve HTTP/USD kontrolü
    P->>M: Sınırlı sayım ve generation
    M-->>D: Öneri ve usage makbuzu
  end
```

## İlk görev review'ı ve NM-02

[Native A/B raporundaki](../quality/native-two-model-001.md) NM-02: ilk görev review'ı AC hazırlamadığı için başlangıçta ekstra kapsam adımı gerekiyordu. UI artık görev kaydından önce kapsam seçimini görünür kılar. İnsan tarafından doldurulmuş kriterler onaylanabilir; eksik kapsam açık bir soru olarak korunur. Bu kod değişikliği modelin kendiliğinden doğru, test edilebilir kriter ürettiği anlamına gelmez; otomatik kriter çıkarımı bu teslimde eklenmedi.

```mermaid
flowchart TD
  accTitle: İlk görev incelemesinde kapsam seçimi
  accDescr: Task önerisi, kapsam onayı ve doğrulanmış tamamlanma ayrıdır. AC ve DoD insan tarafından birlikte onaylanır veya bağlı netleştirme sorusu korunur. Hiçbiri otomatik Done yapmaz.
  T["Kaynaklı Task önerisi"] --> R["İnsan ilk kapsam incelemesi"]
  R --> A["AC ve DoD açıkça dolduruldu ve onaylandı"]
  R --> Q["Kapsam eksik - bağlı netleştirme sorusu"]
  A --> C["Atomik Task + contract v1<br/>To Do - kriterler not_run"]
  Q --> N["Atomik Task + Open clarification<br/>Contract yok - başlangıç AC guard'ı korunur"]
  C --> V["Sonraki ayrı uygulama ve kanıt incelemesi"]
  N --> V
  classDef proposed fill:#dbeafe,stroke:#1e40af,color:#172554
  classDef review fill:#fef3c7,stroke:#92400e,color:#451a03
  classDef recorded fill:#dcfce7,stroke:#166534,color:#052e16
  class T proposed
  class R,A,Q,V review
  class C,N recorded
```

Kriterler boşsa approved modu reddedilir; kısmi contract uydurulmaz. Kapsam seçimi her yeni seçili Task için zorunludur. Mevcut göreve source attachment eski AC'yi değiştirmez. Aynı command key farklı kapsamla tekrarlanamaz. Scope receipt nihai knowledge revision ve hem create hem contract event sequence'lerini taşır. Son audit başarısızsa Task, contract ve question birlikte geri alınır.

Geriye uyumluluk: eski `accept_candidates` çağrıları scope_reviews olmadan desteklenir; yeni UI her yeni Task için explicit kapsam seçimi gönderir. Eski istemcilerin contract'sız Task'ı başlatması/Done yapması mevcut guard'larla engellenir; bu teslim bütün eski API istemcilerine otomatik kriter üretimi eklemez.

## API / depolama / Operations

Mevcut session/CSRF/Origin ve human/project yetkili command API:

| Action | Alanlar | Etki |
|---|---|---|
| prepare_source_sharing | source_id, model, max_output_tokens, reserved_tokens, expires_at, reason | Yerel exact preview; grant veya dispatch yok |
| approve_source_sharing | plan_id, consent=true | Current profile/context ile grant+token budget+approval atomik |
| analyze_approved_source | plan_id, start=true | Mevcut exact consent için ayrı start; atomik activation kurulumu ve tek-source/tek-grant queue pass; canonical apply yok |
| accept_candidates | Önceki alanlar + isteğe bağlı scope_reviews | Yeni UI'da Task ile approved contract veya clarification birlikte |

`scope_reviews` her candidate için mode, criteria, dod, clarification ve reason taşır. Approved iki nonempty liste ister; clarify iki listeyi boş ve soruyu dolu ister. Yeni source-sharing event'leri mevcut audit tablosunda append-only tutulur. İlk human scope sorusu origin=first_task_human_scope_review ve quote/span=null taşır; source-literal alıntı diye sunulmaz. Canonical AC event store'dadır. Key, endpoint, ledger yolu veya ham provider hata metni API/loga konmaz. Prepared context aynı workspace'de private kalır; operasyon logları yalnız komut sınırı/kod içerir.

## Doğrulama ve kalan sınır

11yeni runtime kontrolü: preview≠consent≠activation≠dispatch; restart, stale context/expiry/policy; audit rollback; fake model→ilk scope; soru yolunda tek Task; AC not_run; scope replay çelişkisi; dynamic bounded worker; UI'dan cap/model yükseltme reddi. Gerçek tarayıcıda exact preview→onay→ayrı activation→fake model→AC/DoD ile ilk Task akışı geçti. Mevcut çok turlu diyalog/false-Done/mobil akış regresyonu da geçti. External API/native source read0.

Sonraki kabul ayrı: yeni sınırlı gerçek kaynak paylaşımı ve geçerli ücretli policy dönemiyle bu UI akışını gerçek provider'da çalıştırmak. Önceki capture/model deneme izinleri tüketilmiştir; mevcut süreyi, fiyat revision'ını veya kaynak scope'unu sessizce yenilemedik. Sürekli native capture, generic provider/billing yönetimi ve modelin kriter çıkarım kalitesi bu teslimin tamamlanmış yetenekleri değildir.

Kod incelemesinde Task oluşturma sonrasında contract event'lerinin eklenmesiyle combined receipt'in nihai knowledge revision'ı ve event listesi de güncellenmesi gerektiği görüldü. Receipt düzeltildi; current snapshot eşitliği regresyona eklendi. Önceki source-only kabul veya geçmiş gerçek model raporu yeniden yazılmadı.


Yenileme öncesi kod tesliminin teyidi: **680runtime +49repo testi geçti**; mevcut dialogue/false-Done ve yeni source-sharing browser akışı pass.62Mermaid/34belge render edildi ve yeni iki çizim incelendi. LOCAL53610 ve TEST53611aynı verilerle yeniden başlatıldı; tüm uygulama tablo fingerprint'leri aynı, worker/native read/model dispatch0. LOCAL mevcut policy metadata'sını gösterir; profilExpired, model_ready=false. Başlangıç credential içeriğini veya ledger'ı açmaz/değiştirmez.

Yenileme öncesi öneri kaydı: önceki development API döneminin süresi dolmuştu. Yerel koddan bağımsız bu izin sessizce uzatılmadı. Yenileme önerisi aynı$3/100generation/200HTTP/10kinput/2koutput sınırlarını,52önceki dispatch/104HTTP bütçe payını ve$0.067286taahhüdü (3unknown için$0.006750korunan rezerv dahil) taşımak; eski policy/ledger'ı koruyup yeniden onaylanmış24saatlik dönem için cumulative prior-usage kaydı kullanmaktır. Öneri kaydı tek başına onay, bakiye veya actual fatura doğrulaması değildi. Source consent ve ayrı activation yine gerekir; onay yokken API kapalı kalır.


## 20 Ekim — yalnız süre için owner onayı

**20 Ekim — onaylı API süre yenilemesi:** Kullanıcı aynı toplam sınırlarla 24 saat yenilemeyi onayladı. Dönem 20 Ekim 13:35:38–21 Ekim 13:35:38 Türkiye saati (UTC+3). $3 toplam tavan, 100 model/200 HTTP, istek başına 10.000 giriş/2.000 çıkış korunur; geçmiş 52 dispatch/104 HTTP bütçe payı ve $0.067286 taahhüt taşındı. Üç unknown actual=null ve toplam $0.006750 rezerviyle korunur. Kalan 48 model/96 HTTP ve $2.932714 yerel paydır; hesap bakiyesi/fatura değildir. LOCAL profil Available, worker kapalı; yeni sohbet okuma/model çağrısı yok. Kaynak paylaşımı ve aktivasyon ayrıca gerekir. [Taşıma ve doğrulama](../quality/openai-development-budget.md#20-ekim--aynı-toplam-sınırlarla-onaylı-süre-yenilemesi).

Eski policy/ledger korundu. Yeni immutable policy, önceki toplamı `prior_usage` olarak bir kez taşır; yeni dispatch satırlarına aynı kullanım ikinci kez yazılmaz. Unknown satırları predecessor kanıtında unknown/actual=null kalır; rezervleri taşınmış maliyetin içindedir. Yeni ledger'ın boş `states` listesi geçmiş unknown yok demek değildir. Constructor/snapshot kontrolü credential okumadan ve transport çağırmadan yapıldı. LOCAL kontrollü yeniden başlatıldı; tüm uygulama tablolarının fingerprint'leri eşit, bağlantı0/worker0. TEST değiştirilmedi. Bu işlem yeni model kalitesi veya native kabul kanıtı üretmedi.


## Gerçek arayüz kabulü ve yeni plan eşlemesi

[LOCAL iki sohbet raporu](../quality/native-ui-journey-001.md): capture→exact paylaşım→ayrı activation/Analyze→Task+linked clarification gerçek ürün arayüzünden geçti; ikinci sohbet aynı Task ID için In Progress önerdi. Owner clarification seçtiği için contract yok ve başlangıç uygulanmadı; bu dal diyagramdaki mevcut açık-soru yoludur. Sürekli capture/genel semantik kalite/Done kabulü değildir.

UI-J01: aynı kaynağın eski paylaşım makbuzu yeni exact planın approval formunu gizliyordu. `renderSourceSharing`, hazırlanmış plan varken saved makbuzunu source yanında plan ID ile eşleştirir; yeni kutu unchecked başlar. Backend admission veya audit geçmişi değiştirilmedi. Düzeltme öncesi başarısız browser regression, düzeltme sonrası yeni grant ve ayrı consent ile geçti.


**Son owner kapsam onayı:** [Aynı LOCAL pilotun devamında](../quality/native-ui-journey-001.md#son-owner-kararı--kapsam-onayı-ve-güncel-başlangıç) kullanıcı açıklama sonrası somut AC/DoD ve current başlangıcı onayladı. Contract v1→clarification Resolved→eski model önerisi stale/Deferred→güncel insan transition ile In Progress yolu gerçek arayüzden doğrulandı. Kriterler not_run; yeni inference0. Bu, ilk clarification seçimini geçmişten silmez veya eski model response'unu güncelmiş gibi yeniden kullanmaz.

## 20 Ekim — onaylı kaynak ile analiz kuyruğu arasındaki çalışan bağlantı

**Uygulandı:** Conversations kartında paylaşım onayından sonra ayrı Start approved analysis düğmesi var. Komut current insan/proje, exact plan/payload/context, geçerli profile/expiry ve mevcut grant'i doğrular; yalnız o grant için aktivasyon kurup tek-source queue pass çalıştırır. Browser'ın activation formu veya worker planı hazırlaması gerekmez. Aynı kaynağın başka yeni grant'i bulunsa bile seçilen planın grant ID'si pinlenir; otomatik son grant seçimi yapılmaz. Model sonucu öneri olarak Inbox'ta kalır; Task/AC/durum uygulaması yine ayrı insan adımıdır.

Activation kurulumu tek transaction'dır; create ve Active geçişinden biri hata verirse yarım setup kalmaz. Mevcut public activation API transaction davranışı korunur, iç primitive'ler caller-owned transaction gerektirir. Model çağrısı transaction dışında gerçekleşir. Kullanıcının daha önce pause/revoke ettiği aktivasyon bu kısa yoldan yeniden açılamaz. Başlamış/bitmemiş analiz tekrar gönderilmez; bitmiş başarılı/başarısız sonuç çağrı yapılmadan geri okunur. Eşzamanlı ikinci start ikinci provider isteği üretmez. Shared USD/token/HTTP/root unknown rezervleri değişmeyen admission yolunda kalır.

**Kalan:** capture ile yeni mesaj kaydedilir, fakat önceki mesajın exact consent'i onu kapsamaz; yeni mesaj Pending/Waiting for model kalır. Düğme sürekli gelecek-mesaj paylaşım politikası veya yeni source için otomatik grant üretmez. Yeni mesajların yetkili sürekli işleme deneyimi ve genel extraction kalitesi hâlâ açık; ana T09/T19/T21/T22 kabulü bu dar teslimle kapanmadı.

**Doğrulama:** 12 yeni runtime kontrolü, toplam704runtime test geçti. Gerçek tarayıcıda preview→iki ayrı exact plan/consent→tek start→queue→scripted model→insan AC/DoD→tek To Do Task; ardından yeni mesajın izinsiz analiz edilmemesi ve dar ekranda overflow olmaması doğrulandı. Aynı-görev ikinci kaynak/start/ayrı insan apply yerel scripted provider testiyle geçti. Bu, gerçek model anlam kalitesi veya yeni native mesaj okumasının kanıtı değildir. External API/native read0. Operations komutu extraction bileşeniyle içeriksiz izler; raw kaynak/key loga eklenmez.

İlk uygulama kontrolünde nested SQLite transaction setup'ı durdurdu; public activation davranışı gevşetilmeden mevcut primitive caller-owned transaction'a ayrıldı ve rollback testi eklendi. İncelemede aynı kaynağa birden çok grant olduğunda queue'nun son grant'i seçmesiyle yanlış planın beklemesi de saptandı; exact grant allowlist ile düzeltildi. Başarısız yerel deneme dış API çağırmadı.

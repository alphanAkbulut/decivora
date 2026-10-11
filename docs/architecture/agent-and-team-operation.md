# Tek insan + çok agent ve ekip kullanımı

**2026-10-09 — uygulanabilir mimari yön, henüz çalışan özellik değil.** Kullanıcının takip isteği iki kullanım biçimini netleştirdi: bir kişinin birden fazla agent'ın işlerini izlemesi; bir kişinin ürünü kendi ekibine kurup ortak projede kullanması. İkisi de mevcut INT-02/TEAM-01 vizyonundadır. [Yetki modeli](identity-access.md) ve [faz planı](../delivery/team-data-plan.md) korunur; çok agent gözlemi için çok insanlı ekip sürümünü beklemek gerekmez.

## 1. Agent'ın ne yaptığını nasıl biliriz?

Agent'ın görevi doğrudan bir insan mesajından gelmek zorunda değildir. Üst agent'ın delege ettiği görev, zamanlanmış işin girdisi, araç çağrısı veya izinli yapılandırılmış work order da başlangıç kaynağı olabilir. Girdi görünmüyorsa çıktıdan özgün prompt uydurulmaz; `input_unavailable` gösterilir.

| Veri | Erişim sınırı / ürün davranışı |
|---|---|
| Kullanıcı girdisi veya üst agent görev mesajı | Host/SDK/adapter gerçekten sunuyorsa ve izinliyse source referansı ile alınır |
| Yapılandırılmış task, plan, durum ve açıklanmış gerekçe | MCP/API bildirimi veya izinli transcript'ten aday kayıt; agent beyanı olduğu görünür |
| Araç çağrısı/sonucu, hata, çıktı dosyası, commit ve test raporu | İzinli event/trace/artifact kaynaklarından alınır; araç çalışması task'ın tamamlandığını tek başına kanıtlamaz |
| Agent→alt agent ilişkisi ve handoff | Gerçek provider run/thread kimlikleri varsa kurulur; isim benzerliği veya zaman yakınlığı parent kanıtı değildir |
| Token/süre/model bilgisi | Kaynakta varsa kapsamıyla kaydedilir; eksik veri unknown, sıfır değil |
| Provider'ın sunduğu reasoning özeti | Opsiyonel, kaynağı belirtilmiş açıklama; bütün iç muhakeme veya doğruluk kanıtı değildir |
| Özel iç muhakeme, gizli system prompt veya erişilmeyen context | Erişilebilir varsayılmaz; bunları açığa çıkarma ürün gereksinimi değildir |

OpenAI'nin [reasoning belgesi](https://developers.openai.com/api/docs/guides/reasoning) ham reasoning token'larını sunmadığını, desteklenen modellerde özet alınabildiğini belirtir. Şifreli/opaque reasoning öğesi okunabilir düşünce metni değildir. Decivora'nın görev, gerekçe ve kanıt takibi bu iç veriye bağımlı olmayacak.

### Belgelenmiş bağlantı olanakları

- [Codex SDK belgesi](https://learn.chatgpt.com/docs/codex-sdk) programatik agent kullanımını; özel istemciler için App Server üzerinden geçmiş, onay ve akan agent olaylarını tarif eder. Bu yol, bağlanmamış her masaüstü oturumuna pasif erişim verdiği anlamına gelmez.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks#subagentstart) `SubagentStart` için agent kimliği/türünü; [SubagentStop](https://code.claude.com/docs/en/hooks#subagentstop) alt agent transcript referansı ve son mesaj alanlarını belgeler. Dosya erişimi, eksik stop, resume ve sürüm davranışı ayrıca test edilmelidir. Başlama hook'u görülmesi Decivora'nın agent yaratmayı engelleyebildiği anlamına gelmez.

Kaynaklar 2026-10-09'da belge düzeyinde incelendi; entegrasyon kurulmadı. Connector capability raporu `agent_identity`, `parent_run`, `task_input`, `tool_events`, `artifact_refs`, `usage`, `stop_signal`, `backfill` alanlarının her birini supported/partial/unsupported/untested olarak taşımalı. Tek bir “bağlı” rozeti eksiksiz görünürlük vaadi değildir.

## 2. Gözlem, bildirim ve çalıştırma ayrı

| Entegrasyon düzeyi | Sağladığı bilgi | Sınır |
|---|---|---|
| İzinli hook/event/import gözlemi | Host'un dışarı verdiği olaylar | Görülmeyen alt agent veya özel context hakkında iddia yok |
| Agent'ın MCP/API üzerinden bildirmesi | Task amacı, ilerleme, blocker, sonuç ve evidence referansı | Agent unutabilir/yanlış bildirebilir; reconciliation ve kanıt kontrolü gerekir |
| İzinli SDK/orchestrator bağlantısı | Kontrol ettiğimiz run'larda daha güçlü girdi/run/araç korelasyonu | Mevcut tüm agent sistemlerini kapsamaz; çalıştırma ayrı yetki/bütçe ve sonraki fazdır |

İlk çok-agent pilotu gözlem + sınırlı ortak hafıza üzerine kurulur. Agent'ları Decivora'nın başlatması şart değildir. İzlemek için provider hesabının master credential'ı bütün agent'lara dağıtılmaz. Bu belgenin yazılması yeni agent çalıştırma veya provider ücret izni sağlamaz.

## 3. Bir insanın çok agent'ı için kayıt ve concurrency

Örnek: aynı projede araştırma agent'ı bulgu üretir, coding agent'ı değişikliği uygular, doğrulama agent'ı test sonucu ekler. Kullanıcı ortak task/karar görünümünde kimin hangi girdiden hangi çıktıyı ürettiğini izler. Üç agent'ın bir iddiayı tekrarlaması üç bağımsız kanıt sayılmaz; aynı artifact/evidence kökeni korunur.

Mevcut `AgentPrincipal` kalıcı kimlik, `AgentRun` tek yürütme, `Task` ürün işi olarak ayrı kalır. Bir task birçok run'a, bir run birden fazla task'a ilişebilir; her tool çağrısı yeni task yaratmaz. Provider'daki “agent type”, görünür ad veya model adı uygulamanın güvenilir kimliği değildir. Host kalıcı kimlik sunmuyorsa connector kapsamlı observed kimlik kullanılır; tahmini eşleme pending kalır.

Önerilen run alanları: workspace/project, authenticated reporter, observed agent ref, provider/account/session/run ref, parent_run_ref veya unknown, initiating human/service sponsor, grant, task bindings, input/context/AC revisions, artifact/evidence refs, observed_at/received_at, status, coverage ve usage scope. Reporter ile gözlenen aktör ayrıdır: collector'ın gördüğü agent'a kendiliğinden command yetkisi verilmez. Agent metnindeki actor ID kimlik doğrulaması değildir.

Run graph'ı kimin kimi başlattığını, task graph'ı hangi işin neye bağlı olduğunu gösterir. Run-parent ilişkisi task `part_of` ilişkisine otomatik çevrilmez. Child parent'tan önce gelirse ilişki unresolved tutulur; sonradan kaynakla bağlanır. Event ID/revision dedup, yerel ingestion sırası ve kaynak zamanları korunur; farklı makine saatlerinden kesin execution sırası çıkarılmaz.

Run durumları queued/running/waiting/succeeded/failed/cancelled/unknown olarak tasarlanabilir; son host sinyali task verification değildir. Heartbeat/stop eksikse unknown/stale görünür; “sessizce çalışıyor” veya “bitti” varsayılmaz. Claim/lease/fencing ve base revision kontrolleri eski worker sonucunu engeller. Ayrı checkout/sandbox dosya çakışmasını azaltabilir; takip ürünü host'un dosya izolasyonunu kendiliğinden kurmaz.

Üst grant iptali bütün alt grant zincirini etkiler. Başka host'a verilmiş işin fiziksel olarak durduğu ancak stop acknowledgment/host kanıtıyla söylenir; Decivora erişimini kesmek dış process'i öldürmek değildir. Geç sonuç quarantine edilir; dış yan etki varsa ayrı reconciliation gerekir. Parent/child budget tek proje/dönem tavanına dahildir; parent toplamı child kullanımını zaten içeriyorsa yeniden toplanmaz. Usage kapsamı belirsizse toplam kesin fatura diye sunulmaz.

### Gözlenebilir davranış örüntüleri

Tekrarlanan aynı hata, duplicate görev, test atlama, aynı veriyi tekrar okuma, gereksiz handoff veya blocker bekleme ölçülebilir adaylardır. UI her bulguda event örnekleri, zaman aralığı, örneklem ve eksik coverage gösterir. Bu gözlenen davranış analizi, modelin zihnini veya kişiliğini çözümleme iddiası değildir. Bir “düşünce paterni” tahmini otomatik yetki/prompt/model değişikliği yapmaz. Önce deterministik örüntü; gerekirse izinli ve bütçeli analiz. Diğer agent'ların tüm transcript'lerini her agent'a dağıtmak yerine gerekli task/karar özeti verilir.

## 4. Bir kişinin ürünü ekibine vermesi

Önerilen akış: işletim biçimini seç → ekip workspace'i/proje oluştur → owner hesabını güvenli kur → üyeleri ayrı hesapla davet et → proje rollerini ver → agent/connector'ları ayrı kimlikle bağla → kaynak paylaşımını önizle → sentetik erişim testi → pilot. Davet kabulü kişisel sohbet geçmişinin paylaşılması değildir.

| Kullanım | Veri/erişim düzeni | Ürün aşaması |
|---|---|---|
| Tek insan, bir veya çok agent | Yerel servis + kişisel workspace; agent başına dar grant; yerel SQLite adayı | P1 temelleri ve P1b temel çok-agent pilotu; yetenek/kalite kapılarıyla |
| Ekip kendi ortamında kurar | Merkezi servis/API + tarayıcı UI + ayrı insan hesapları + yerel capture adapter'ları; PostgreSQL adayı | P4 self-host aday; TLS, giriş/davet, recovery ve işletim kanıtı gerekli |
| Yönetilen hizmet | Aynı tenant/rol modeli, işletim sağlayıcıda; quota, destek erişimi ve veri politikası eklenir | P4 seçenek; bugün satın alınabilir SaaS/paket yok |

Her üye hesabı ve proje üyeliğiyle giriş yapar. Owner/Admin kurulum/üyelik yönetir; Contributor iş/kanıt önerir; Reviewer yetkili onay verir; Viewer izinli kayıtları okur. Agent hesabı insan koltuğuyla veya sahibinin token'ıyla birleştirilmez. Ürün hesabı, uygulama rolü ve provider aboneliği/ücreti farklıdır; ürünü almak sınırsız model hakkı sağlamaz. Ticari lisans/koltuk fiyatı henüz seçilmedi.

Ekipte istemciler ortak SQLite dosyasını ağ diski üzerinden açmaz; tek yetkili API'ye bağlanır. DB credential'ı üyelere/agent'lara dağıtılmaz. Kaynakta kişisel/ortak ACL korunur; workspace sahibi olmak özel sohbetleri otomatik görme hakkı değildir. Offline istemci izinli kayıtları sınırlı spool'da tutabilir; yerel kopya ortak canonical DB olmaz, geri bağlanınca revision/authz kontrolü gerekir. Tam offline çok yönlü sync mevcut teslim değildir.

Kurulum sahibi ilk owner'ı doğrulanabilir bootstrap ile kurar; public registration varsayılan gereksinim değildir. Oturum süresi/çıkış, davet süresi, kayıp hesap kurtarma, sahiplik devri ve offboarding C01–C03 kapısında somutlaştırılır. SSO/OIDC sağlayıcısı, paket biçimi ve hosting satın alımı bu belgede seçilmez. İşletim sahibi upgrade, secret, TLS ve backup/restore sorumluluğunu üstlenir; managed modelde bu sorumluluk sözleşmesi ayrıca belirlenir.

Kişisel workspace'i ekibe sessizce dönüştürme yok: paylaşılacak proje ve kaynaklar seçilir, ACL/provenance/dış credential etkisi önizlenir; onaylı export/import/migration kimlik eşlemesi ve kaynak lineage'ı korur. Özel konuşmalar varsayılan taşınmaz. Ayrılan üyenin token/grant'leri iptal edilir, açık işler devredilir, tarihsel aktör kaydı korunur.

## 5. Subagent soru sorunca karar kime gider?

**2026-10-10 — mevcut insan onayı ilkesinin uygulama tasarımı; henüz uygulanmadı.** Agent'lar bilgi isteyebilir, seçenek hazırlayabilir ve verilmiş yetki içinde teknik seçim yapabilir. Bir agent'ın başka bir agent'a cevap vermesi tek başına insan onayı veya yeni yetki değildir. Run bitişi, sorunun cevaplanması, insan kararının uygulanması ve task verification ayrı olaylardır.

| Soru türü / örnek | Kim cevaplayabilir? | Devam koşulu |
|---|---|---|
| Bilgi: “Onaylı API sözleşmesi nerede?” | Önce yetkili kayıt sorgusu; gerekirse parent veya ilgili agent kaynaklı yanıt verir | Kaynak/revision güncel ve erişilebilir; cevap yeni ürün kararı gibi kaydedilmez |
| Görüş: “Bu iki çözümün artı/eksileri ne?” | Yetkili uzman agent alternatif ve kanıt hazırlayabilir | Görüş danışmanlıktır; seçim gerektiriyorsa aşağıdaki yetki sınıfına gider |
| Yetki içi teknik seçim: “Mevcut sözleşmeye uygun hangi test fixture'ını kullanayım?” | Görevi yürüten agent veya yetkili koordinatör | Onaylı amaç/AC/scope, maliyet ve grant sınırında; yeni insan onayı gerektirmeyen düşük riskli seçim gerekçesi kaydedilir |
| Korunan karar: “AC'yi düşürelim mi, mimariyi değiştirelim mi, işi iptal edelim mi?” | Proje policy'sindeki yetkili insan; her zaman task'ı başlatan kişi olmak zorunda değil | PendingDecision + somut seçenek/etki + doğrulanmış insan onayı |
| Yeni izin: “Yeni provider'a veri gönderelim mi, ek bütçe veya yayın yetkisi verilsin mi?” | İlgili kaynak/bütçe/işlem yetkilisi insan | Mevcut açık izin varsa kapsamı doğrulanır; yoksa dar izin kararı beklenir. Parent agent izin veremez |

### Soru yaşam döngüsü

1. Agent eksikliği task/run'a bağlı bir `QuestionRequest` olarak bildirir. Önce onaylı proje kayıtlarında cevap aranır; aynı soruyu farklı agent'ların tekrar üretmesi önlenir. Üst agent bilinmiyorsa parent uydurulmaz, proje karar kuyruğuna yönlendirme önerilir.
2. Sınıflandırma ve yetki kontrolü soruyu bilgi/görüş, yetki içi seçim veya insan kararı olarak yönlendirir. LLM'in “bu düşük riskli” etiketi server policy'sini aşamaz. Etki/izin belirsizse seçenek hazırlayıp insan review'una yükseltilir; çoğunluk oyu veya model confidence yetki yerine geçmez.
3. Koordinatör agent varsa ilgili kanıtları toparlar ve aynı karar için tek anlaşılır soru hazırlar. Özgün talep sahibi, alternatifler, karşı görüşler ve bloklanan işler kaybolmaz. Onay yetkisi olmayan koordinatör karar mercii olmaz; yanıtı değiştirmeden kaynağına bağlar.
4. Yalnız bu cevaba gerçekten bağımlı adımlar `waiting_for_answer`/`waiting_for_human` gerekçesiyle bekler. Bağımsız, izinli ve geri alınabilir hazırlık ilerleyebilir; belirsiz kararı varsayan uygulama, harcama veya dış etki başlatılmaz. Blocker önceliği korunur.
5. Yanıt gelince kimlik, cevap kapsamı, question/task/AC/knowledge/policy/authz revision'ları tekrar kontrol edilir. Bilgi yanıtı yeterli olabilir; korunan seçimde güvenilir approval kaydı gerekir. “Owner kabul etti” şeklindeki agent metni yeterli değildir.
6. Cevap ve gerekçe kaydedilir; varsa Decision/Approval/ChangeSet'e bağlanır. Task açılmadan diğer engeller ve güncel grant/bütçe/lease kontrol edilir. Cevabın gelmesi görevi completed yapmaz; uygulama ve evidence kapıları devam eder.

Önerilen `QuestionRequest` alanları: workspace/project, task/run/requester, sınıf, soru/seçenekler/öneri, source refs, etkilenen işler, gerekli karar capability'si, hedef principal/queue, base revisions, policy, dedup key, deadline ve status. `AnswerRecord`: doğrulanmış responder/type, source veya approval reference, kapsam, gerekçe, revisions ve answered_at. Soru durumları open/routed/answered/resolved/deferred/stale/cancelled olabilir; **answered, uygulanabilir/approved demek değildir**. Timeout ayrı bekleme nedeni olur, otomatik kabul üretmez. Alanlar öneri sözleşmesidir; çalışan endpoint değildir.

### İstisnalar ve host sınırları

- **Önceden verilmiş insan kararı:** Aynı kapsam ve geçerli revision için referanslanır; kullanıcı tekrar onaya zorlanmaz. Eski konuşmadan geniş yetki çıkarılmaz. Otomatik mekanik policy kararı `policy_applied` olarak kaydedilir, yeni insan approval'ı diye gösterilmez.
- **İnsan/parent cevap vermiyor:** Soru durable kalır; timeout onay değildir. Parent run bitse veya yeniden başlasa soru kaybolmaz; atanmış yetkili kuyruğa aktarılır. Başka agent'ı seçerek insan onayı şartı atlanamaz.
- **Agent'lar anlaşamıyor:** Kaynak/kanıt farkı gösterilir; mevcut onaylı karara uyulur. Korunan karar değişimi veya çözülemeyen etki varsa insan review'u gerekir. İki agent aynı görüşte diye bağımsız insan review sağlanmış olmaz.
- **Döngü ve maliyet:** A→B→A soru zinciri correlation/hop sınırıyla durdurulur; tekrar aynı konu tek kayda bağlanır. Agent danışması varsa normal token/round/retry bütçesine tabidir; her durum güncellemesinde model çağrısı yok. Sayısal limitler fixture ile kalibre edilecek.
- **Gizli kaynak:** Soru ve yanıt kaynak ACL'sini genişletemez; aynı sorular yalnız yetkili aynı kapsamda birleştirilir. Karar sahibi kanıta erişemiyorsa redakte paylaşım veya yetkili başka reviewer gerekir; secret içeren transcript bütün agent'lara yayınlanmaz.
- **Yanıt geldiğinde iş değişmiş:** Onay eski revision'a bağlıysa stale önizleme yenilenir. İptal edilen task'a geç cevap gelmesi işi diriltmez. Eşzamanlı çelişen cevaplarda son yazan kazanmaz; tek geçerli çözüm ve diğer cevabın conflict kaydı tutulur.
- **Sadece gözlem yapabildiğimiz host:** Decivora soruyu gösterebilir; host'taki subagent'a mesaj gönderme, pause/resume veya durdurma desteği yoksa bunları yaptığını söylemez. İnsan yanıtı `delivery_pending/unsupported` olabilir; destekli bridge veya açık manuel aktarım gerekir. Host'ın çalışmayı bıraktığı teyit edilmeden UI yalnız “karar bekliyor, dış run durumu bilinmiyor” der.
- **Aktif bridge olan host:** Yanıt teslimi acknowledgment/idempotency ile izlenir. Otomatik resume yalnız önceden yetkili run kapsamı, güncel izin ve host desteğiyle mümkündür; insan cevabı yeni agent başlatma izni değildir. Aktif kontrol sonraki execution fazının kapısındadır.

### Örnek

Coding subagent: “Performans testini geçemiyorum; eşiği düşüreyim mi?” → mevcut AC bulunur → test agent'ı ölçüm/alternatif hazırlar → koordinatör etkiyi toplar → **yetkili insan karar verir**. Bu sırada bağımsız hata analizi yapılabilir; test eşiği sessiz düşürülemez. “Test raporu hangi dosyada?” sorusu ise kaynaklı teknik cevapla çözülebilir; kullanıcıya taşınması gerekmez.

### Planlı soru/karar kontrolleri

| Kontrol | Beklenen davranış |
|---|---|
| ASK-01 | Bilgi yanıtı kaynak/revision taşır; görüş veya agent cevabı human approval'a dönüşmez |
| ASK-02 | Yetki içi teknik seçim gereksiz insan sorusu üretmez; scope/AC/bütçe değişimi parent üzerinden kaçırılamaz |
| ASK-03 | Timeout/parent bitişinde soru korunur; yalnız bağlı işler bekler; bağımsız iş yetki sınırında ilerler |
| ASK-04 | Eski, çelişen veya iptal sonrası yanıt sessiz uygulanmaz; retry tek etkili çözüm üretir |
| ASK-05 | Aynı sorular yalnız aynı yetkili kapsamda birleşir; A→B→A döngüsü ve danışma bütçesi sınırlanır |
| ASK-06 | Önceden geçerli insan kararı yeniden kullanılır; agent'ın “insan onayladı” metni tek başına approval kanıtı olarak reddedilir |
| ASK-07 | Gözlem-only host'a cevap teslim edildi/resume oldu iddiası yok; destekli bridge acknowledgment taşır |
| ASK-08 | Cevap sonrası diğer blocker/grant/lease/kanıt kapıları korunur; soru resolved olsa da task completed olmayabilir |

T13e kalıcı soru/yetki yönlendirmesi, T18e transport capability, T24f sentetik doğrulama olarak planlanır. Bu kurallar henüz çalıştırılmadı; yeni provider desteği veya otonom orchestration teslimi sayılmaz.

## 6. Agent ve ekip doğrulama planı

| Kontrol | Planlı beklenti |
|---|---|
| AGT-01 | Tek insanın iki ayrı agent/run kaydı aynı projede doğru kaynağa bağlanır; aynı ad kimlikleri birleştirmez |
| AGT-02 | Eksik prompt/parent/private reasoning unknown/unsupported kalır; açıklama kaynakta yoksa uydurulmaz |
| AGT-03 | Child-before-parent, duplicate event, resume, stop kaybı ve saat farkı atıf kaybettirmez; run success task completed olmaz |
| AGT-04 | Aynı task'ta eski claim/revision sonucu uygulanmaz; ayrı agent aynı kanıtı bağımsız review diye saydıramaz |
| AGT-05 | Grant zinciri iptalinde yeni erişim/commit engellenir; dış process'in durumu teyitsiz stopped olmaz |
| AGT-06 | Parent/child usage iki kez sayılmaz; bütçe/grant türeterek tavan aşılmaz; bilinmeyen tüketim görünür |
| AGT-07 | Ekip kurulum/davet/giriş/revoke akışı private kaynakları açmaz; son owner ve recovery kontrol edilir |
| AGT-08 | Kişisel→ekip aktarımı paylaşım önizlemesi ve identity mapping taşır; orijinal kaynak/ACL korunur |

T02c capability, T18d iki-agent ortak hafıza/run görünürlüğü ve T24e pilot kontrolleri; C01–C04 ekip kurulumu/kimliği. AGT-01–08 henüz çalıştırılmadı. Seçili provider/host Q02, dış veri/bütçe Q03 ve ekip işletim OPEN-14–16 kararları geçerli. İlk bireysel pilot kararı korunur; çok-agent gözlemi eklemek otonom orchestration veya formal çok insanlı takımın teslim edildiği anlamına gelmez.

## 2026-10-11 — İnsan cevabının gecikmesi ve soru bağı

[Q12 yaşayan örneği ve geç cevap sözleşmesi](../product/pending-questions-and-late-answers.md), QuestionRequest'in yalnız subagent/run yaşamına bağlı olmadığını netleştirir. Kimlikli kart → reply/selected source → yetkili dar candidate context sırası; unbound/ambiguous cevaplar korunur, model confidence approval değildir. Değişmeyen option IDs/presentation snapshots, AnswerRecord association state ve source/received/resolution zamanları teknik adaydır. Durum “answered” olması aynı snapshot'a uygulanabilirlik veya execution delivery demek değildir. Geçlik tek başına stale değildir; gerçek authority/revision/expiry kontrolleri ayrı. LATE-01–08 T13e/T18e/T24f'ye bağlı not_run; ASK-01–08 korunur.

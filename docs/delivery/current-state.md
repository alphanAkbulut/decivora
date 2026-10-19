# Güncel ürün ve kalan geliştirme resmi

**19 Ekim 2026 — son Operations/TEST ortamı, impact review/apply ve iptal/yeniden açma kod teslimleri sonrası.** Bu dosya [backlog](backlog.md), [kapanış kaydı](task-closure.json) ve [ana akış denetiminden](../quality/primary-flow-audit.md) türetilen okunabilir özettir; yeni görev otoritesi veya ayrı backlog değildir. Yayın durumu commit/ref readback ile ayrıca doğrulanır; yerel test başarısını GitHub yayını veya MVP kabulü sayma.

## Nerede olduğumuz

**Son Codex ana zincir deneyi:** [Yeni sentetik sohbet pilotu](../quality/codex-e2e-001.md)3gerçek model sonucunda Task/başlama/Done beyanını aynı işe bağladı; görev ayrı test operatörü handoff’u ile In Review, AC’ler not_run. Dördüncü dispatch ilk geçişte unknown/frozen kaldı. Takipte2human native kaynak doğrulandı; kullanıcı rezerv koruyarak yeni işlere devamı onayladı. Eski unknown ve gerçek usage belirsizliği korunur; tam E2E/MVP başarısı değildir.

Python3.12/SQLite tabanlı açılabilir yerel uygulama ve çalışan domain çekirdeği mevcut. Konuşma import'u, kaynaklı aday incelemesi, görev/durum onayı ve etki kartından task scope select→approve→apply kodlandı. **Otomatik konuşma yakalama ve gerçek anlam çıkarımıyla bütünleşmiş MVP henüz tamamlanmadı. Release adayı aşamasında değiliz.**

| Kanonik ana iş grubu | Kapalı | Devam eden | Başlanacak | Açık toplam |
|---|---:|---:|---:|---:|
| P0 hazırlık/kalite T01–T03 | 0 | 3 | 0 | 3 |
| MVP T04–T24 | 7 | 14 | 0 | 14 |
| MVP sonrası T25–T30 | 0 | 4 | 2 | 6 |
| **Toplam** | **7** | **21** | **2** | **23** |

**MVP release yolunda17ana iş açık:14ürün/entegrasyon işi ve3P0 hazırlık/kalite işi.** Bunlar17eşit büyüklükte küçük PR değildir. Done görünen7iş çekirdek kabul kapsamıdır; otomatik kullanıcı yolculuğunun tamamı değildir. T15 ve T24 esasen entegrasyon/kabul kapısıdır; diğer12açık MVP ana işte kalan ürün kodu vardır. Kabulde çıkacak gerçek hatalar bu işlerde düzeltilir; gelecekte bulunacak hata sayısı tahmin edilmedi.

**19 Ekim8TODO incelemesi:**6iş kodla başladı; Claude hook bridge, orphan audit, GitHub commit observer, paired-cost,14AC evidence inventory ve ZIP CLI. [Kalan kapılar](../quality/todo-development-review.md); tüm işleri tamamlanmış saymıyoruz.

**19 Ekim T13e backend güncellemesi:** [Kaynaklı seçenekli soru taslağı](../quality/dialogue-status-runtime.md#19-ekim--konuşmadaki-seçenekli-sorudan-kalıcı-soru-kaydına) ayrı insan incelemesiyle kalıcı soru olur ve geç cevaba bağlanır. Kaynaklı taslak inceleme kartı da Conversations ekranına bağlandı. Genel/serbest metin soruları ve ekip routing açık.

**19 Ekim T17 güncellemesi:** [seçilmiş Codex exec JSONL capture](../quality/codex-exec-capture-runtime.md) kaynak/review yoluna bağlandı; T17 artık In Progress. Sadece public assistant mesajları, partial coverage; gerçek masaüstü bağlantısı ve sürekli tam konuşma kabulü açık. Ana sayım güncellendi; ana iş kapanışı veya MVP kabulü yok.

Yeni T17 kodu: App Server üzerinden yalnız seçilen oturumu okumak için stdio client ve bounded polling hazır; user/assistant metinleri ayrı kimlikle mevcut review yoluna bağlanır. Kurulu CLI şeması offline doğrulandı. Sınırlı gerçek oturum okuması aşağıdaki readback ile yapıldı; normal arayüzden capture kurulumu henüz açılmadı.

**Gerçek kaynak sınaması:** [Codex readback001](../quality/codex-real-capture-001.md)2turun erişilen kısmından6mesajı TEST'e kaydetti. User/assistant kaynak→DB→TEST UI bağlantısı bu örnekte doğrulandı; okunmamış item'lar nedeniyle tam capture açık. Sonraki kod dilimi kalıcı cursor/sayfa checkpoint'ini sentetik doğruladı; gerçek kaynağa yeniden uygulanmadı. Orijinal TEST kaynakları model kapalı alanda kaldı. Daha sonra kullanıcı ayrı6mesajlık API paylaşımını onayladı; [ayrı pilot kopyasında](../quality/saved-source-pilot-001.md)6Ready for review/7öneri üretildi. Tek izin tüketildi, sürekli aktarım açılmadı.

**Backend takip:** [kalıcı model aktivasyonu](../architecture/model-activation-runtime.md) mevcut grantlerle Paused/Active/Revoked, current revision dispatch gate, expiry/authz durması, legacy bypass reddi, restart/restore ve içeriksiz Operations komutları sağlar. Yeni kaynak/ücret izni değildir. Sonraki bounded worker teslimi mevcut izinlerle API üzerinden açıkça başlatılır; default timer kapalıdır.

## Elimizde çalışan kod

Yeni: tanınan credential'lar yeni manuel kaynakta DB öncesi maskelenir; model/import/context/MCP çıkış kontrolleri ve POSIX DB izinleri vardır. [Kapsam](../quality/credential-redaction-runtime.md): tam DLP, encryption veya geçmiş yedek purge değildir.

- Kalıcı workspace/project/human-agent scope, kaynak alım/checkpoint/worker çekirdeği; gerçek native adapter kabulü ayrı.
- Append-only domain event log, projection/replay, atomik değişiklik ve onay kontrolleri.
- Kalıcı insan onaylı AND/OR expression/facts, görev editorü ve impact/continuation-context bağlantısı; nested writer API'de bounded, UI düz AND/OR.
- Tipli ilişki ve AND/OR/unknown impact kernel'i; UI'da kayıtlı ilişkilerin görselleştirilmesi.
- Manuel konuşma import'u; hash/span bağlı JSON/provider-callback adapter'ı; görev/karar/bekleyen karar adayları. Dialog context artık görevler yanında canonical karar/kayıtları, soruları ve ilişki snapshot'ını da taşır.
- Kaynaklı mevcut kayıtlara required_by/depends_on ve Decision NEW supersedes OLD önerisi; ayrı human review ile graph apply, replacement öncesi/sonrası impact hipotezi. Genel gerekçe/validity planı açık.
- Kaynaklı exact soru/sürüm/seçenek geç cevap kartı; ayrı insan onayıyla cevap kaydı, karar uygulaması ayrı.
- Kaynaklı mevcut-task status önerisi; ayrı accept/reject/defer ve current workflow/AC/verification guard'ları.
- Karar etki hipotezi → insanın düzenlediği task scope değişikliği → grup seçimi → ayrı approve → apply → yeni task version. Eski description event geçmişinden görünür.
- AC/DoD, local human review, yapılandırılırsa dar file-SHA verification, blocker/dependency ve false-Done güncellik kontrolleri.
- Kabul edilmiş altı aşama; ayrı Blocked ve Cancelled; altı tipli bekleme rozeti/filtre; sunucu kaynaklı stage/geçiş listesi. İnsan doğrulamalı tek karar gerekçesiyle guarded cancellation/reopen ve lifecycle history UI kodlandı; genel resolution/clarification kapsamı açık.
- Board/List/Graph/Timeline, mevcut proje seçimi, özel yedek indirme/offline restore çekirdeği, sınırlı stdio MCP, token reservation/actual/unknown/overrun kaydı.

- Salt okunur Operations ekranı, bounded kalıcı güvenli hata/komut sınırı izleri, duration/operation-ID, degraded kaydı ve ayrı TEST veri/oturum/port başlatıcısı. Güvenilir preflight actor/workspace/yetki sürümü artık izde ve ekranda; eski kayıtlar kimliği bilinmiyor kalır. Tam engine trace/admin/policy yönetimi açık.

**Ekip kullanım kapısı:** ayrı kimlik, loga özel yetki ve tenant izolasyonu tamamlanıp doğrulanmadan ortak ekip erişimi açılmayacak. Tek-owner geliştirme sürer; [LG-01–08 ve mevcut C kapıları](../quality/log-access-retention-gap-review.md) açık kalır.

Bunların tamamı aynı olgunlukta değildir. Gerçek model/host/file erişimi olmayan bir yetenek varsayılan programda otomatik çalışıyor diye sunulmaz.

## Kalan ürün kodu —12mevcut ana iş

| Ana iş | Mevcut parça | Kalan kod / kullanıcıya teslim | Dış bağımlılık |
|---|---|---|---|
| T09 — çıkarım/bağlam | JSON schema/span, current context; fixed-host HTTP + key helper + bounded runner;26gerçek generation/52HTTP; completion claim ve ilk6gerçek kayıtlı mesaj; exact source factory ve kalıcı activation yönetimi | Genel semantik kalite; ana UI aktivasyonu; fikir/gereksinim/prompt/belge talimatı dahil tipler; kaynaklı AC/genel relation; bounded retrieval | İlk pilot dahil$3/100generation/200HTTPsentetik scope onaylı; kalan$2.947445/74generation/148HTTP. Ayrı6gerçek kayıt paylaşımı tamamlandı; yeni gerçek veri paylaşımı ayrıca izin ister |
| T10 — uzlaştırma | Exact duplicate/source attach; refinement işareti | Yeni/eski karar, refinement/conflict/supersession eşleme ve kullanıcı çözümü; belirsizlikte netleştirme. Yanlış task/karar eşleştirmesi önlenmeli | Yerel kod bağımsız; gerçek semantik davranış modeli ayrıca gerektirir |
| T13 — karar/onay | Review kernel, kaynaklı status/late-answer/relation/decision-replacement review; lifecycle ve task-update apply | Konuşmadan QuestionRequest üretimi; tam belirsizlik/çatışma çözümü; split planının atomik onayı ve genel otomatik değişiklik planı | Yerel kod bağımsız; yeni kaynak/karar eşleştirmesinin kalitesi ayrıca doğrulanır |
| T14 — doğrulama | Human/file-SHA kriterleri ve current Done guard | Verifier configuration/policy, gerçek artifact/hedef bağı, zorunlu parent-child koşulları ve kriter revision entegrasyonları; izinli otomatik verifier yolunun sınırları | Gerçek dosya/çalıştırma hedefi ve izinleri ilk kullanım öncesi |
| T16 — Claude Code adapter | Capture/queue sözleşmesi ve ölçüm düzeneği | Desteklenen gerçek host/version olaylarını kaydetme; session binding, interruption/recovery, gap/coverage | Seçilen Claude Code kurulumu/oturumu ve kaynak izni; ayrı ücretli model API zorunluluğu değil |
| T17 — Codex adapter | Seçilmiş App Server user/assistant read,6gerçek TEST source, kalıcı sayfa checkpoint/dedup/pending; native log | Kaynak kurulum/izin UI, kapasite/backfill/gap kartı, sürekli çalışma ve yeni kodun gerçek host kabulü | Seçilen destekli Codex host ve kaynak izni; olmayan hook var sayılmaz |
| T18 — MCP/devam hafızası | Beş-tool stdio subset, current record ve execution read | Gerçek client kurulum/onboarding; kaynak bazlı audience izinleri; private türevleri izinli paylaşma; karar/soru/gerekçe/AC içeren dar continuation context | Gerçek istemci ve somut kaynak paylaşım izni. Proje okuma izni private konuşmayı otomatik açmaz |
| T19 — proje/inbox | Mevcut proje seçimi; aday/status/answer/relation/replacement/task-update review; source queue kartı | Proje/kaynak oluşturma ve izin kurulumu; eksik proposal tipleri/çatışma çözümü; T19b risk kartı ve model aktivasyon onboarding ekranı; backend Paused/Active/Revoked ve finite worker create/start/stop hazır | Kod bağımsız; bağlantı aktivasyonu seçilen host/model kapsamına bağlı |
| T20 — günlük takip/context | Board/List/Graph/Timeline, blocker/lifecycle, AND/OR gerekçe yazarı, queue/Operations görünümü | Onaylı Q08-A alt görev/checklist; parent ilerlemesi; Q06-A milestone context dosyası; fikir evrimi ve otomatik etki sonuçlarının tam bütünleşmesi | Deterministik kod bağımsız; ücretli özetleme varsayılmaz |
| T21 — kullanım/yönlendirme | Class/executor, token reservation/freeze; gerçek count/usage; cache-aware admission; eski kullanım dahil çok-batch ortak root bütçe | Genel UI profil/aktivasyon; dönem policy; trusted overrun reconciliation; nihai invoice doğrulaması | Toplam tahmin$0.052555, root$3. Genel account-wide veya kart limiti iddiası yok |
| T22 — import/lineage | Manuel source import, provenance, hash, typed review | Mesaj/rol/chat/run kimliği; prompt→execution→artifact lineage; izinli geçmişin aşamalı işlenmesi; iki host ile aynı proje bağlamına uzlaştırma | Kod bağımsız; gerçek kaynak erişimi/retention kapsamı ilk kullanımdan önce |
| T23 — işletim/paketleme | Loopback session/Origin/CSRF, private backup, offline restore | Kullanıcıya güvenli aktif restore/recovery/migration; redacted export, purge/retention yönetimi; kurulum ve sürüm güncelleme bütünlüğü | Kod bağımsız; gerçek veri saklama/paylaşma policy'si ilgili ilk kullanımda |

T16 ve T17 ayrı teslimdir; birini yapıp “iki adapter” şartı kapanmaz. Bir satır başka satırın geliştirilmesini tamamen bekletmez: planlama sırası, gerçek teknik bağımlılık, erişim ve release kapısı ayrı tutulur.

## İki ana release/entegrasyon işi

- **T15:** gerçek uygulama kaynaklarıyla import→çıkarım-adapter→karar/gerekçe→impact→onay→state→kanıt→düzeltme/restore zincirini bütünleştirmek; kırılan bağlantıları mevcut sahiplerinde düzeltmek. Tek tek modül pass'i değildir.
- **T24:**14MVP kriteri, gerçek semantic davranış, iki gerçek coding adapter, temiz kurulum ve owner günlük kullanım kabulü. Bu kapı tamamlanmadan full MVP release denmez. Tek adapter geçen sonuç sınırlı pilot olarak etiketlenir.

## Kullanıcı katkısı nerede gerekecek?

Q06-A ve Q08-A karara bağlandı; bunları yeniden bekleyen seçim saymıyoruz. Bağımsız geliştirmeyi durduran yeni business sorusu yok. Dört mevcut ilk-kullanım/kabul kapısı:

1. **Gerçek model:** anahtar kuruldu; [ortak geliştirme bütçesi](../quality/openai-development-budget.md) ilk pilot dahil$3/100generation/200HTTPolarak açıkça onaylandı.26generation/52HTTPkullanıldı; current scope içindeki sentetik batch için yeniden genel onay gerekmez. Ayrı6mesajlık gerçek konuşma izni kullanıldı; yeni veya sürekli paylaşım ve ana UI otomatik dispatch'i bu genel bütçe iznine dahil değil; native hazırlık için bakiye blocker değil.
2. **Gerçek host:** seçilmiş Codex/Claude kurulumu, oturum/proje ve dar kaynak yetkisi; source audience paylaşımı ayrıca görünür.
3. **Gerçek hedef:** seçilmiş root/dosya/artifact ve doğrulanacak kriterin kapsamı; tüm araçlara sınırsız erişim gerekmiyor.
4. **Kalite/pilot değerlendirmesi:** exact label/holdout ve günlük kullanıcı faydası için insan incelemesi. Önceki cevaplar yeniden sorulmaz.

Q09 harici bildirim kanalı/sıklığı ayrıntıları açık; uygulama içi inbox ve kabul edilmiş blocker önceliğiyle kod geliştirmesi sürer. Bu kayıt bildirim veya otomasyon kurmaz.

## Sonraki kod sırası

**Güncel sıra:** indexed kapasite/paging ve exact-grant queue tamamlandı; kalıcı aktivasyon backend lifecycle kodlandı. Finite worker create/start/stop backend ve kalıcı caps bağlandı. Sırada kaynak/model onboarding ekranı ve yeni kaynak paylaşım policy bağlantısı → kaynaklı çıkarım/reconciliation kalitesi → review/impact/verification ve next-session context tam zinciri. Kaynaklı relation/late-answer/replacement önerileri, AND/OR yazarı, review/apply, kalıcı capture checkpoint ve bounded queue worker kodlandı; sürekli otomatik ürün zinciri tamamlanmadı.

**Ardından/birlikte:** dar izinli continuation/MCP (T18/T22), Claude adapter (T16), Codex onboarding/coverage (T17) ve gerçek kalite kabulü (T01/T03/T24). Q08 split ve Q06 snapshot mevcut UI çekirdeğinde ayrı teslimlerdir; model bakiyesi beklemez. Kurulum/restore işleri erken ilerler, tüm kabul T15/T24'te birleşir.

## İş miktarının dürüst sınırı

Alt takipte129kayıt var:56DONE,39IN_PROGRESS,29TODO,5PROPOSED;UNSPECIFIED0. [19Ekim satır bazlı teyit](../quality/task-status-audit.md)42durumsuz kaydı ve4eskiTODO durumunu düzeltti. Bunlar ana işlerle toplanmaz; kabul daraltılmadı veya yeni task üretilmedi. Ana7Done/15InProgress/8ToDo korundu. Tamamlanmış deneylerin durumu ürünün genel doğruluğu veya MVP kapanışı değildir.

Efor büyüklükleri ve kalan belirsizlikler kalibre edilmediği için güvenilir yüzde/saat/gün verilmez. Mevcut durum **önemli çekirdeği olan, ana otomatik entegrasyonları hâlâ geliştirilmekte olan ürün**dür; yalnız paketleme veya kozmetik düzeltme kalmadı. Yeni görev veya faz eklenmedi.

19 Ekim T17 ilk iyileştirme teslimi: [kalıcı sayfa ilerlemesi](../quality/codex-exec-capture-runtime.md#page-atomic-continuation--19-october) kodlandı.Bu ilk kayıtta açık olan32source sınırı/indexli okuma sonraki capacity tesliminde giderildi. Capture gap/izin kartı ve sürekli otomatik model zinciri açık; ana sayım değişmedi.

19 Ekim ana akış kodu: [source→outbox→izinli queue worker→review ve ilerleme kartı](../quality/conversation-processing-runtime.md) bağlandı. Native CLI collect success/failure Operations trace'i kalıcı. Otomatik grant/background activation yok;32source/indexed kapasite, kaynak onboarding ve gerçek model/native kabulü açık. Yeni parent veya erken Done yaratılmadı.

19 Ekim [kaynak kapasitesi ve sayfalama](../quality/source-capacity-pagination.md) tamamlandı:1000source/proje, indexed origin/ID,25lik source sayfaları, worker'ın ilk sayfa dışındaki izinli source'u işlemesi ve native50public item guard. Bu alt teslim ana iş sayımını veya kalan onboarding/live-backfill/semantic kabulünü kapatmaz.

19Ekim backend follow-up: [kalıcı finite processing loop](../architecture/model-activation-runtime.md#kalıcı-sınırlı-işleme-döngüsü--sonraki-backend-teslimi) mevcut Active grant kapsamıyla thread/API/Operations yoluna bağlandı. Restart caps sıfırlamaz; unfinished claim otomatik retry olmaz, aynı loop ikinci worker dispatch etmez. Default LOCAL/TEST değişmedi, gerçek provider çağrısı0; UI onboarding, yeni kaynak policy ve gerçek günlük kabul açık. Ana7/15/8korunur.


## 19 Ekim — native kaynak / unknown bütçe takip düzeltmesi

İlk assistant-only testin ardından aynı thread'de2gerçek human+6assistant native kaynak doğrulandı; iki checkpoint geçişi8→8, duplicate yok. API unknown için güvenli phase tanısı ve snapshot'a bağlı ayrı owner review kodlandı. Kullanıcının rezerv koruyarak devam onayı uygulandı; root yeni izinli istekler için açık, eski unknown ve actual=null korunur. Yeni API çağrısı0. [Aksiyon planı ve açık kabul sınırları](../quality/codex-e2e-001.md#19-ekim--aksiyon-planı-ve-uygulama-sonucu). Ana görev sayıları değişmedi; bu düzeltme MVP'nin tamamlandığı anlamına gelmez.


## İlk gerçek çok turlu4case grubu

[J01–J04](../quality/dialogue-batch-001.md): J01 altı turda aynı görev/ilerleme/false-Done guard geçti; J02 ayrı netleştirme görevi önerisi ve generation unknown nedeniyle eksik. J03/J04henüz koşulmadı. Yeni unknown root'u durdurdu; kapsam/netleştirme politikası ve kalan14mesaj için ayrı owner review bekliyor. Bu, tüm48case veya MVP kabulü değildir.


**Onaylı devam:** [Kayıt](../quality/dialogue-batch-001-continuation.md):14yeni istek izninin8'i kullanıldı; yeni timeout ile durdu. J01 dar pass, J02/J03 teknik eksik, J04not_run. Mevcut Task netleştirmesi için yeni typed alan/insan review/UI/closure çalışır; yeni prompt henüz gerçekmodelle sınanmadı. Kalan6J04mesajı yeni unknown risk onayını bekler; sonraki gruba geçilmedi.

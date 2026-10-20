# Gerçek Codex düzenli yakalama — üç sınırlı okuma

**20 Ekim 2026 · LOCAL · Atlas UI Pilot · T17/T19/T22/T24.** [Kod tesliminin](scheduled-capture-runtime.md) sentetik worker kabulünden sonra, yalnız daha önce açılmış Native B sentetik sohbeti gerçek LOCAL Sources ekranından zamanlandı. [Makine özeti](scheduled-native-001-results.json).

## Onay ve uygulama

Owner `call_df6751014ecd4bf28a9396ea7593cd1a` kapsamında yalnız Native B için10saniye aralık, en fazla3read, read başına son en fazla10tur ve onaydan itibaren5dakika içinde maskeli yerel public kullanıcı/assistant kaydı onayladı. Başka sohbet, reasoning ve tool output kapsamda değildi; API/model veya Task apply izni yoktu. Onay alındığı gözlem20Ekim13:21:50UTC, üst süre13:26:50UTC idi; UI'da daha kısa13:26:00UTC expiry kullanıldı. Bütün3okuma bu pencere içinde tamamlandı. Yeni izin eski tek-read kayıtlarını veya sayaçlarını değiştirmedi.

Gerçek kullanıcı yoluyla yeni connection→immutable schedule→ayrı checkbox/Start→3tick→Limit reached→Stop→Disconnect→reload uygulandı. Yeni sohbet veya mesaj gönderilmedi. İnsan/assistant eski public mesajlar kaynak verisidir; approval authority yerine kullanılmadı. Ham metin, DB, credential, thread/read kimlikleri public repoya eklenmedi.

## Sonuç

| Kontrol | Gözlenen sonuç |
|---|---|
| Native host | Kurulu Codex App Server bridge,0.162.0-alpha.17.2 |
| Kalıcı tick/read | 3started /3finished /3Captured; pending claim0 |
| Ölçülen interval | Önceki bitişten yeni başlangıca10.025750s ve10.018105s |
| Read makbuzundaki source sayısı | İlk geçiş3, sonraki0/0; cursor önceden işlenmiş item'ları atladı |
| Toplam kalıcı kaynak | 6→6; eski origin eşlemesi tekrar kayıt üretmedi |
| Coverage | Üçünde partial; pending turn0, unsupported item0 |
| Task ve kapsam | Aynı1Task In Progress; contract/clarification/evidence kayıtları değişmedi |
| Son durum | Schedule Stopped; connection Disconnected; worker kapalı |
| Sayfa reload | Son state korundu; page-error0 |
| Model/API | 0yeni çağrı; root54dispatch/108HTTP/$0.067895 değişmedi |

Üç okuma arasında yeni mesaj eklenmedi. Bu test gerçek host zamanlamasını, cursor/dedup'ı ve kapanışı doğrular; yeni bir mesajın polling esnasında eklenmesi veya ilerleyen diyalogdan semantik Task/status çıkarımı bu testte ölçülmedi. İlerleyen sentetik mesajlar worker browser testinde; gerçek iki-chat görev/start çıkarımı önceki [LOCAL journey](native-ui-journey-001.md) kanıtıdır. Kanıtlar birbirinin yerine geçmez.

Tick sayacı claim yazılırken artar; okuma sürerken API view'daki `Unfinished read` ile active=true birlikte görülebilir. Bu tek başına hata/crash değildir. Bu testte3claim'in3ü finish/Captured ile kapanmıştır. Dormant/pending restart ise otomatik tekrar edilmez. Aktif okuma etiketinin daha anlaşılır gösterimi UI takip önerisidir; bu kayıt akışını değiştirmedik.

## T17 çekirdek kabul kararı

Mevcut kabul cümlesi değiştirilmedi: **“Desteklenen Codex yüzeyi açık; aynı session retry ve eksik capture raporlu.”** Desteklenen yüzey installed App Server bridge olarak belgeli ve gerçek public input ile denenmiş; aynı oturumdaki repeated read gerçek3tick/cursor/dedup ile, aynı read_id idempotency ve crash/no-retry ise contract suite ile sınanmış; bounded/partial ve eksik/pending metadata'sı makbuzlarda görünür. Önceki gerçek iki-chat capture/model yolculuğu da korunur. Bu birlikte kanıtla **T17 çekirdeği Done** yapıldı; yalnız test sayısı veya zamanlayıcı eklenmesi kapanış gerekçesi değildir.

Kapanış eski kapsamı genişletmez. Claude adapter T16, yeni mesajların otomatik model paylaşım policy'si T19/T21/T22 ve birleşik günlük/release kabulü T24 altında açık kalır. Tam history/backfill, yüksek trafik altında mesaj kaçırmama veya bütün Codex sürümleri destekleniyor iddiası yoktur. İki-adapter MVP veya ürün release'i tamamlanmadı. Yeni düzenli okuma izni bu3read ile tüketildi; başka test kendiliğinden başlamaz.

**Doğrulama:** Native audit'te3başlangıç/3bitiş ve başarılı source read makbuzları ayrıca sayıldı; süre farkları kayıtlı timestamp'lerden hesaplandı. Önce/sonra Task ve clarification JSON'ları ile shared API budget snapshot birebir aynı. Önceki kod commit'inin GitHub CI39428965127sonucu success; yeni model çağrısı veya yeni runtime kod değişikliği bu raporda yok.


**Takip regresyonu:** T17 kapanınca tracker testinin önceki sabit21InProgress/7Done beklentisi doğal olarak başarısız oldu. Kabul maddesi veya test kapsamı gevşetilmedi; canonical evidence'li8Done/20InProgress/2ToDo ve açık T17Done beklentisiyle güncellendi. Diğer parent/release durum kontrolleri korundu.

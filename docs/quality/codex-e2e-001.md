# Codex yeni sohbet → görev → durum: gerçek bağlantı deneyi

**19 Ekim2026 — kısmi başarı, MVP kabulü değil.** Kullanıcı önce Codex'in gerçek ana zincirini doğrulamamızı istedi. Başka ürün/adapter yatırımına geçilmedi. Yeni ve yalnız sentetik Atlas Demo sohbeti açıldı; normal proje ve önceki TEST DB değiştirilmedi. Ana konuşma bu projede kalır; açılan sohbet yalnız deney kaynağıdır.

## Gerçekte çalıştırılan zincir

| Aşama | Gerçek giriş / işlem | Gözlenen sonuç |
|---|---|---|
| Yeni Codex sohbeti | Ayrı projectless sohbet; araç/dosya kullanmadan Atlas Demo işini konuşması istendi | Dört kısa assistant yanıtı, kurulu CLI0.162.0-alpha.17.2 üzerinden seçilmiş thread'den okundu |
| İlk çıkarım | “Görevimiz… kontrol eklemek” mesajı, gerçek Luna çağrısı | Task+proposed Decision adayları. Test operatörü yalnız Task'ı kaydetti; Decision uygulanmadı |
| Başlangıç güncellemesi | “işine başladın, uygulama sürüyor” mesajı, mevcut Task context'i | Yeni Task açılmadı; aynıID için In Progress önerildi. Ayrı sentetik operatör review'u ile uygulandı |
| Bitirme beyanı | “işi bitti… testleri henüz çalıştırılmadı” mesajı | Aynı Task için reported Done önerisi. Doğrudan Done uygulama girişimi reddedildi; AC/DoD not_run kaldı |
| Workflow rehberliği | Mevcut In Progress+reported Done, deterministik kurallar | Suggested review stage In Review. Arayüzden görev workflow'una giden bağlantı eklendi. Pilot operatörü ayrı handoff yaptı, görev In Review |
| Dördüncü çıkarım | Yeni “kod incelemesinde” mesajı, yeni capture→selected-source queue→gerçek provider geçişi | Analysis failed, usage unknown; ortak transport frozen. Modelin In Review önerdiği iddia edilmez. Retry/model yükseltme yapılmadı |

[Makine sonuçları](codex-e2e-001-results.json). Buradaki operatör işlemleri izole sentetik uygulama testidir; bağımsız insan etiket/gold veya gerçek ürün kabulü değildir. Model Task/Decision ayrımının genel kalitesi ölçülmedi. Amaç cümlesinin proposed Decision olarak çıkması ayrıca anlam incelemesi gerektirir; otomatik kabul edilmedi.

## Bulunan kritik kaynak sınırı

Bu uygulamada `create_thread` / `send_message_to_thread` ile gönderdiğimiz mesajlar App Server item listesinde `functionCallOutput` türündeydi; gerçek `userMessage` değildi. Adapter dört assistant metnini aldı, bu araç gövdelerini bilerek almadı. Read-thread aracı da aynı türleri doğruladı; özel tool output veya reasoning okunmadı/konuşma gibi kaydedilmedi.

İlk geçişte **normal insanın yazdığı mesajların otomatik yakalanması bu yeni sohbette doğrulanmamıştı**. İşleyen assistant kaynaklı durum tespiti tam diyalog capture'ı yerine sunulamaz. Kullanıcıya aynı test sohbetine tek normal mesaj yazması soruldu. Ana sohbette soru yanıtı olarak gelen test cümlesi test thread'inden yakalanmış sayılmadı, başka gerçek sohbet okunmadı. Bu ana mesajı native test kaynağı gibi yerleştirmedik.

[OpenAI App Server belgesi](https://developers.openai.com/codex/app-server/) thread/turn/item ve pagination sözleşmesini anlatır; kurulu yüzeyde userMessage bulunacağını her gönderim yönteminde garanti etmez. Yerel Native UI otomasyonu bu uygulama için kullanılamadı; başka yöntemle UI erişim kısıtı aşılmadı. Aşağıdaki takip geçişi normal kullanıcı mesajını doğruladı; ilk geçişin assistant-only sonucu tarihsel olarak korunur. Mevcut capture yeteneği olanak/kurulumdan ayrı tutulur.

## Kod bağlantıları

`packages/capture/codex/project_pipeline.py`: tek `tick` seçilmiş capture'ı okur, aynı project/thread/profile kapsamındaki kaynakları seçer, yalnız önceden geçerli source/context/model/budget grant'i olanları kuyruğa verir ve review-ready sonucu döndürür. Yeni grant, thread/model çalıştırma talimatı veya domain onayı oluşturmaz. Hiç grant yoksa source saklanır, model çalışmaz. `source_limit`1–10; normal conversation/model sınırları geçerli.

`ConversationQueue.process(..., source_ids=...)` iç allowlist eklendi. Başka kaynak geçerli modele sahip olsa bile seçilmiş thread akışına karışmaz. Parametre verilmediğinde mevcut proje kuyruğu davranışı korunur. Started/failed/unknown kaynak yeniden denenmez.

`human_text_observed=false` ve `human_text_not_observed_do_not_claim_full_dialogue` uyarısı assistant-only capture'ı açık gösterir. Bu “kesin insan mesajı yok” veya kaynaktaki bütün geçmiş görüldü demek değildir; yalnız alınmış kaynakların sınırıdır. Callback/worker'ın devamlı arka plan kurulumu ve kullanıcı onboarding'i bu tek-pass API'sinden ayrı açıktır.

Status review view'unda `workflow_guidance` reported stage/current stage/suggested review stage/current verification ve finish blocker durumlarını ayırır. In Progress'teki Done beyanı için In Review; In Review'da Awaiting Verification önerilebilir. Awaiting Verification'da Done ancak mevcut gerekli kanıtlar geçmiş ve finish blocker yoksa review adayıdır; scope review/ayrı insan işlemi yine zorunlu. Yeni alan öneridir, workflow guard'ını veya mevcut Done incelemesini atlatmaz. Stale öneride guidance null olur. Yeni UI bağlantısı mevcut görev ayrıntısını açar; gizli status mutation yapmaz.

## API başarısızlığı ve kullanım hesabı

Yeni testte4model işi kabul edildi; bütçede8HTTP girişim payı sayıldı:3settled,1unknown. Belirsiz işte generation isteğinin sağlayıcıya ulaşıp ulaşmadığı ve gerçek HTTP sayısı kesinleştirilmedi. Yeni bilinen tahmin1135microusd ($0.001135), belirsiz çağrı için2250microusd rezervasyon tutuluyor. Önceki işler dahil root30dispatch/60HTTP bütçe sayımı; bilinen toplam53690microusd, belirsiz held2250microusd,3USD tavan korunur. Bunlar yerel benimsenmiş fiyat snapshot hesabıdır; fatura veya bütün hesap kullanımı değildir.

Dördüncü çağrının eski failure receipt'i güvenli somut hata kodunu saklamıyordu. Bu yüzden nedenini kesin timeout/şema/provider diye adlandırmıyoruz. `ConversationService.analyze` artık `failure_code` ve `failure_stage` saklar; yalnız allowlist kodları, exception text/credential/raw HTTP hata gövdesi yoktur. Regresyonda provider_connection_unknown ve tekrar engeli doğrulandı. Tarihsel başarısız kayıt sonradan başarılı/teşhis edilmiş gösterilmedi. Kullanımı bilinmeyen rezervasyon serbest bırakılmadı, root frozen kaldırılmadı, tekrar çağrı yapılmadı.

## Kalan kapanış koşulları

1. Normal kullanıcı mesajı: aşağıdaki takip geçişinde doğrulandı. Bütün geçmişin eksiksiz alındığı iddia edilmez.
2. Bilinmeyen request: kullanıcı rezerv koruyarak devamı onayladı; aşağıda uygulandı. Gerçek kullanım ve kök neden hâlâ bilinmiyor.
3. Kaynak/model kurulumunu UI'dan, sonlu izin/bütçe ve görünür stop/resume ile günlük kullanıma bağlamak.
4. İnsan review ve gerçek tamamlanma kanıtıyla kalan AC'leri geçirmek. Bu küçük örnek genel model doğruluk/holdout sonucu değildir.

Yerel pilot `http://127.0.0.1:53612/`: ayrı DB; ilk geçişte4, takipte8kaynak/1Task, In Review, verification not_run, model bağlantısı önizlemede kapalı. Dışa/public yayın değildir. Private DB, exact model payload'lar, anahtar ve ledger repoya konmadı.

```mermaid
flowchart TD
  accTitle: Yeni Codex sohbetinde gözlenen proje ilerleme zinciri
  accDescr: İlk geçişte dört assistant metni, takipte iki gerçek kullanıcı ve iki yeni assistant metni alındı. Dördüncü model çağrısı belirsiz kaldı. Kullanıcı onayıyla rezerv korunarak yalnız yeni izinli işlere devam edilebilir.
  C[Yeni sentetik Codex sohbeti] --> A[4 assistant metni yakalandı]
  C --> U[Takip: 2 normal userMessage yakalandı]
  U --> Q
  A --> Q[Seçili thread kaynak kuyruğu]
  Q --> G{Exact source ve context ve bütçe izni}
  G -->|Yok| W[Kaynak bekler: model çağrısı yok]
  G -->|Var| M[Gerçek Luna çıkarımı]
  M --> T[Task önerisi: planlanan kontrol]
  M --> S[Mevcut task: In Progress önerisi]
  M --> D[Done beyanı: testler yapılmadı]
  T --> R[Ayrı test operatörü review]
  S --> R
  D --> H[Rehber: In Review handoff]
  H --> R
  R --> B[To Do → In Progress → In Review]
  D --> V[Doğrulanmış Done reddedildi]
  M --> F[4. çağrı: usage unknown]
  F --> X[Ortak bütçe frozen: retry yok]
  X --> O{Ayrı owner risk onayı}
  O -->|Onaylandı| K[Rezerv korunur: unknown değişmez]
  K --> N[Yalnız yeni izinli payload: tüm limitler geçerli]
  classDef input fill:#dbeafe,stroke:#2563eb,color:#172554
  classDef review fill:#fef3c7,stroke:#b45309,color:#451a03
  classDef saved fill:#dcfce7,stroke:#15803d,color:#14532d
  classDef stop fill:#fee2e2,stroke:#b91c1c,color:#450a0a
  class C,A,Q,M,T,S,D input
  class G,W,R,H,O review
  class U,K,N saved
  class B saved
  class F,X,V stop
```

## Yerel regresyon ve yayımlama sınırı

623runtime ve49repo/tracker kontrolü geçti.8yeni hedefli test selected-source izolasyonu, grantsiz bekleme, assistant-only uyarı, revoke, source allowlist, güvenli Done rehberliği ve redacted failure makbuzunu kapsar. Mevcut gerçek-browser diyalog akışı yeni In Review bağlantısını tıklayarak doğrulandı; false-Done reddi, source/answer/relation ve390px taşma kontrolü geçti.56Mermaid kaynak ağ kapalı render edildi. Bu yerel pass’ler dördüncü gerçek API başarısızlığını veya eksik normal-user capture kapısını kapatmaz.


## 19 Ekim — aksiyon planı ve uygulama sonucu

| Aksiyon | Uygulama / kabul ölçütü | Sonuç |
|---|---|---|
| A1 Normal kullanıcı girişini doğrula | Aynı izinli test thread'ini native adapter ile oku; tool output'u kullanıcı metni yapma | 4→8 kaynak;6assistant+2human. `human_text_observed=true`; önceki assistant-only uyarısı kalktı |
| A2 Devam ve dedup kontrolü | Checkpoint üzerinden ikinci geçiş; aynı item'ı tekrar oluşturma | İki geçişte8→8; yeni ücretli çağrı0 |
| A3 Güvenli tanı geliştir | Count / generation / usage_validation aşaması ve allowlist hata kodu; raw exception yok | `dispatch_diagnostics` tablosu. Tarihsel çağrının tanısı null kalır; yeni kod geçmiş nedeni tahmin etmez |
| A4 Belirsiz harcamayı incele | Salt okunur packet; exact ledger snapshot hash; ayrı insan risk onayı | Kullanıcı rezerv koruyarak yalnız yeni izinli işlere devamı açıkça onayladı |
| A5 Onaylı devamı uygula | `unknown_reviews` ayrı kayıt; orijinal dispatch/usage/rezerv/counter silinmez | Root frozen true→false;30dispatch/60HTTP bütçe payı ve55940microusd toplam hesap değişmedi |
| A6 Regresyon ve yayın | Count/generation hata ayrımı, stale onay, pending/overrun reddi, restart, tekrar ve bütçe kapıları | Transport testleri ve tüm runtime kontrolü; aşağıdaki güncel doğrulama kaydı |

### Belirsiz kullanımda devam sözleşmesi

`PilotTransport.review_packet()` payload/anahtar/konuşma içermez; payload hash, unknown state, rezerv, HTTP bütçe payı, varsa güvenli tanı ve snapshot hash döndürür. `accept_reserved_unknown(..., snapshot_sha256, approval_ref)` yalnız güvenilir yerel host/owner çağrısıdır; insan onayı yerine geçmez ve MCP/agent'a açılmadı. İnceleme/insert aynı yazma kilidi altında; stale snapshot reddedilir. Pending veya overrun bu yöntemle açılamaz. Birden fazla unknown varsa her biri ayrıca incelenir; son açık engel kalkana kadar freeze sürer.

Uygulanan karar: unknown2250microusd ($0.002250) hâlâ harcanmış gibi bütçeden düşülür; actual=null, ilk dispatch state=unknown, aynı payload tekrar engeli ve60HTTP payı korunur. Bilinen tahmin53690+held2250=55940microusd ($0.055940). Ortak3USD tavan, mevcut expiry, source/context/model izinleri, input/output ve HTTP sınırları değişmedi. Yeni model isteği bu takip tesliminde yapılmadı. Önceki unknown kaynağı otomatik kuyruğa dönmez.

**Risk:** rezerv, benimsenmiş fiyat ve onaylı token sınırları üzerinden hesaplanan yerel üst tahmindir; sağlayıcının gerçekte ne faturaladığını ispatlamaz. Provider'ın sınırları aşması gibi bilinmeyen davranışı garantiyle sınırlayan hesap genelinde bir ödeme kontrolü değildir. Kullanıcı bu belirsizliği rezervi koruyarak kabul etti. Gerçek usage veya sağlayıcı faturası daha sonra doğrulanırsa ayrı kanıt/inceleme gerekir; bu API unknown kullanımını sıfıra veya settled'a çevirmez.

Takip private receipt SHA256: `7b8334cceaa54dc0a49a1d6e7de4549f8cdb2d34f141f1cf3bc72f725a01a88f`. Sadece izinli sentetik test thread'i okundu. Yeni kullanıcı mesajlarının model tarafından anlamlandırılması veya tüm geçmişin capture tamamlanması bu iki yerel okumayla kanıtlanmadı. Genel kalite, sürekli UI aktivasyonu, insan review ve gerçek completion evidence kapanışları açıktır.


**Takip doğrulaması:**627runtime ve49repo/tracker testi geçti;21transport testi içinde4yeni regresyon var.56Mermaid ağ kapalı render edildi, değişen şekil görsel incelendi. Repo testlerinin ilk sandbox koşusunda3yerel port erişimi hatası vardı; aynı testler yerel port izniyle geçti, test kapsamı daraltılmadı. UI kodu değişmedi; bu tur yeni browser ürün akışı testi yapıldığı iddia edilmez.


## 20 Ekim — çok turlu iz ve genişletilmiş senaryolar

[Çok turlu diyalog raporu](dialogue-journeys.md)12case/78mesaj, kaynaklı lineage sorgusu, context sınırları ve gerçek model ölçüm planını ayırır. `DialogueTraceService` mevcut pilotun8kaynağında1record bağlantısı/2status önerisini salt okunur gösterdi; yeni API çağrısı0. Bu yeni sorgu, eski model bulgularını yeni semantik test diye sunmaz.

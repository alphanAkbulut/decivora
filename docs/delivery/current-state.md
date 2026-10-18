# Güncel ürün ve kalan geliştirme resmi

**19 Ekim 2026 — son Operations/TEST ortamı, impact review/apply ve iptal/yeniden açma kod teslimleri sonrası.** Bu dosya [backlog](backlog.md), [kapanış kaydı](task-closure.json) ve [ana akış denetiminden](../quality/primary-flow-audit.md) türetilen okunabilir özettir; yeni görev otoritesi veya ayrı backlog değildir. Yayın durumu commit/ref readback ile ayrıca doğrulanır; yerel test başarısını GitHub yayını veya MVP kabulü sayma.

## Nerede olduğumuz

Python3.12/SQLite tabanlı açılabilir yerel uygulama ve çalışan domain çekirdeği mevcut. Konuşma import'u, kaynaklı aday incelemesi, görev/durum onayı ve etki kartından task scope select→approve→apply kodlandı. **Otomatik konuşma yakalama ve gerçek anlam çıkarımıyla bütünleşmiş MVP henüz tamamlanmadı. Release adayı aşamasında değiliz.**

| Kanonik ana iş grubu | Kapalı | Devam eden | Başlanacak | Açık toplam |
|---|---:|---:|---:|---:|
| P0 hazırlık/kalite T01–T03 | 0 | 3 | 0 | 3 |
| MVP T04–T24 | 7 | 11 | 3 | 14 |
| MVP sonrası T25–T30 | 0 | 0 | 6 | 6 |
| **Toplam** | **7** | **14** | **9** | **23** |

**MVP release yolunda17ana iş açık:14ürün/entegrasyon işi ve3P0 hazırlık/kalite işi.** Bunlar17eşit büyüklükte küçük PR değildir. Done görünen7iş çekirdek kabul kapsamıdır; otomatik kullanıcı yolculuğunun tamamı değildir. T15 ve T24 esasen entegrasyon/kabul kapısıdır; diğer12açık MVP ana işte kalan ürün kodu vardır. Kabulde çıkacak gerçek hatalar bu işlerde düzeltilir; gelecekte bulunacak hata sayısı tahmin edilmedi.

## Elimizde çalışan kod

Yeni: tanınan credential'lar yeni manuel kaynakta DB öncesi maskelenir; model/import/context/MCP çıkış kontrolleri ve POSIX DB izinleri vardır. [Kapsam](../quality/credential-redaction-runtime.md): tam DLP, encryption veya geçmiş yedek purge değildir.

- Kalıcı workspace/project/human-agent scope, kaynak alım/checkpoint/worker çekirdeği; gerçek native adapter kabulü ayrı.
- Append-only domain event log, projection/replay, atomik değişiklik ve onay kontrolleri.
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
| T09 — çıkarım/bağlam | JSON schema/span doğrulama, import, injected provider callback, current context | Gerçek HTTP/credential aktivasyonu; mevcut kapsamın fikir/gereksinim/prompt/belge talimatı dahil tipleri; kaynaklı AC/karar değişimi ve genel relation adayları (dar required_by/depends_on mevcut); bounded retrieval | Hazırlık bağımsız. Gerçek model çalıştırma: model/veri/harcama izni ve erişim |
| T10 — uzlaştırma | Exact duplicate/source attach; refinement işareti | Yeni/eski karar, refinement/conflict/supersession eşleme ve kullanıcı çözümü; belirsizlikte netleştirme. Yanlış task/karar eşleştirmesi önlenmeli | Yerel kod bağımsız; gerçek semantik davranış modeli ayrıca gerektirir |
| T13 — karar/onay | Review kernel, task-status review, question-decision ve yeni task-update apply | Kaynaklı late-answer önerisi ve insan doğrulamalı cevap kaydı var; konuşmadan QuestionRequest üretimi; kaynaklı relation/decision-change planını review'a bağlama; güvenli cancellation/reopen UI; split planının atomik onayı | Yerel kod bağımsız; yeni kaynak/karar eşleştirmesinin kalitesi ayrıca doğrulanır |
| T14 — doğrulama | Human/file-SHA kriterleri ve current Done guard | Verifier configuration/policy, gerçek artifact/hedef bağı, zorunlu parent-child koşulları ve kriter revision entegrasyonları; izinli otomatik verifier yolunun sınırları | Gerçek dosya/çalıştırma hedefi ve izinleri ilk kullanım öncesi |
| T16 — Claude Code adapter | Capture/queue sözleşmesi ve ölçüm düzeneği | Desteklenen gerçek host/version olaylarını kaydetme; session binding, interruption/recovery, gap/coverage | Seçilen Claude Code kurulumu/oturumu ve kaynak izni; ayrı ücretli model API zorunluluğu değil |
| T17 — Codex adapter | Kaynak/oturum sözleşmesi ve prototip ölçümleri | Gerçek Codex yüzeyinden olay capture; desktop/CLI destek farkları; session/retry/gap | Seçilen destekli Codex host ve kaynak izni; olmayan hook var sayılmaz |
| T18 — MCP/devam hafızası | Beş-tool stdio subset, current record ve execution read | Gerçek client kurulum/onboarding; kaynak bazlı audience izinleri; private türevleri izinli paylaşma; karar/soru/gerekçe/AC içeren dar continuation context | Gerçek istemci ve somut kaynak paylaşım izni. Proje okuma izni private konuşmayı otomatik açmaz |
| T19 — proje/inbox | Mevcut proje seçimi, aday/status/task-update review | Proje oluşturma/bağlama akışı; bütün ana proposal tipleri için hazır kart ve ilişki çözümü; actual capture/model durumunu ürün akışına bağlama | Kod bağımsız; bağlantı aktivasyonu seçilen host/model kapsamına bağlı |
| T20 — günlük takip/context | Board/List/Graph/Timeline, blocker görünümü | Onaylı Q08-A alt görev/checklist; parent ilerlemesi; Q06-A milestone context dosyası; fikir evrimi/gerekçe ve otomatik etki sonuçlarının bütünleşmesi | Deterministik kod bağımsız; ücretli özetleme varsayılmaz |
| T21 — kullanım/yönlendirme | Class/executor etiketleri, nullable usage, reservation/overrun freeze | Kullanıcı profil/sınır ayarları; doğrulanmış input/context/output hesabı; fiyat/para/dönem preflight; güvenilir overrun uzlaştırma ve aktivasyon UX'i | Kod bağımsız; gerçek usage/fiyat konfigürasyonu ve çağrı onayı gerekir |
| T22 — import/lineage | Manuel source import, provenance, hash, typed review | Mesaj/rol/chat/run kimliği; prompt→execution→artifact lineage; izinli geçmişin aşamalı işlenmesi; iki host ile aynı proje bağlamına uzlaştırma | Kod bağımsız; gerçek kaynak erişimi/retention kapsamı ilk kullanımdan önce |
| T23 — işletim/paketleme | Loopback session/Origin/CSRF, private backup, offline restore | Kullanıcıya güvenli aktif restore/recovery/migration; redacted export, purge/retention yönetimi; kurulum ve sürüm güncelleme bütünlüğü | Kod bağımsız; gerçek veri saklama/paylaşma policy'si ilgili ilk kullanımda |

T16 ve T17 ayrı teslimdir; birini yapıp “iki adapter” şartı kapanmaz. Bir satır başka satırın geliştirilmesini tamamen bekletmez: planlama sırası, gerçek teknik bağımlılık, erişim ve release kapısı ayrı tutulur.

## İki ana release/entegrasyon işi

- **T15:** gerçek uygulama kaynaklarıyla import→çıkarım-adapter→karar/gerekçe→impact→onay→state→kanıt→düzeltme/restore zincirini bütünleştirmek; kırılan bağlantıları mevcut sahiplerinde düzeltmek. Tek tek modül pass'i değildir.
- **T24:**14MVP kriteri, gerçek semantic davranış, iki gerçek coding adapter, temiz kurulum ve owner günlük kullanım kabulü. Bu kapı tamamlanmadan full MVP release denmez. Tek adapter geçen sonuç sınırlı pilot olarak etiketlenir.

## Kullanıcı katkısı nerede gerekecek?

Q06-A ve Q08-A karara bağlandı; bunları yeniden bekleyen seçim saymıyoruz. Bağımsız geliştirmeyi durduran yeni business sorusu yok. Dört mevcut ilk-kullanım/kabul kapısı:

1. **Gerçek model:** API erişimi, seçilmiş model/veri ve somut harcama/çağrı/token sınırı. Kod hazırlığı için bakiye şart değil; ücretli çağrı için şartlar ayrıca gerekir.
2. **Gerçek host:** seçilmiş Codex/Claude kurulumu, oturum/proje ve dar kaynak yetkisi; source audience paylaşımı ayrıca görünür.
3. **Gerçek hedef:** seçilmiş root/dosya/artifact ve doğrulanacak kriterin kapsamı; tüm araçlara sınırsız erişim gerekmiyor.
4. **Kalite/pilot değerlendirmesi:** exact label/holdout ve günlük kullanıcı faydası için insan incelemesi. Önceki cevaplar yeniden sorulmaz.

Q09 harici bildirim kanalı/sıklığı ayrıntıları açık; uygulama içi inbox ve kabul edilmiş blocker önceliğiyle kod geliştirmesi sürer. Bu kayıt bildirim veya otomasyon kurmaz.

## Sonraki kod sırası

**Önce T09/T10/T13:** konuşmadan kaynaklı karar/soru/ilişki planı → gerekçe grafiği → hedefli impact → hazır review/apply. Mevcut manuel scope-edit köprüsü bu yolun apply ucunu sağlar; hazır semantik öneri henüz yok.

**Ardından/birlikte:** güvenli model aktivasyonu (T09/T21), dar izinli continuation/MCP (T18/T22) ve host adapter hazırlığı (T16/T17). Q08 split ve Q06 snapshot mevcut UI çekirdeğinde ayrı teslimlerdir; model bakiyesi beklemez. Kurulum/restore işleri erken ilerler, tüm kabul T15/T24'te birleşir.

## İş miktarının dürüst sınırı

Alt takipte129kayıt var:56DONE,16IN_PROGRESS,10TODO,5PROPOSED,42UNSPECIFIED. Açık olduğu açıkça kaydedilen31alt kayıt ile durumu belirsiz42satır aynı şey değildir; bunları “73yeni kod işi” diye toplamıyoruz. Kaynaklı teslimler ana görevlere parça parça ekleniyor; son kodun ana kabulü bitirmemesi parent sayısını değiştirmiyor.42satırın mevcut kanıtla kapanış sınırlarının ayrıca gözden geçirilmesi takip borcudur; her biri yeni eksik özellik olarak kabul edilmez.

Efor büyüklükleri ve kalan belirsizlikler kalibre edilmediği için güvenilir yüzde/saat/gün verilmez. Mevcut durum **önemli çekirdeği olan, ana otomatik entegrasyonları hâlâ geliştirilmekte olan ürün**dür; yalnız paketleme veya kozmetik düzeltme kalmadı. Yeni görev veya faz eklenmedi.

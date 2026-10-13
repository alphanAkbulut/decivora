# ADR-0012 — Koşullu yerel MVP çekirdeği ve Python runtime

**Kabul edildi: 2026-10-13, Q15-A.** Owner'ın doğrudan yanıtı: “onay bekleyen iş varsa senin. önerin ne ise o öneri ile ilerleyelım. mediuma aldım artık devam et hadi yoksa bitmez bu proje ve nerede problemle karşılaşacağımızı ön göremıyorm. çalışan kod parçaları ile ilerlememız gerekıyor. sureklı teorik seylerle deüğil”. Yanıt açık Q15 önerisine bağlandı; model/connector veya ücret izni çıkarılmadı.

## Bağlam ve karar

T04'ün bütün T03 araştırma kapanışını beklemesi temel uygulamayı P0 alt görevlerinde tuttu. **Python3.12 + stdlib SQLite** ile private/local MVP çekirdeğini geliştirmeye başlıyoruz. T04 başlangıcı, parent T03'ün Done olmasına değil, kabul edilmiş koşullu yatırım kararı T03c ve bu ADR'ye bağlıdır. T01/T02/T03 kalite/capture/native/ROI işlerinin açık olması iskelet ve deterministik temel kodu bekletmez; release/pilot ve otomatik özellik kabulünü sınırlamaya devam eder.

İlk T04 domain/storage ayrımı, tek CLI entrypoint, synthetic source contract ve sürüm/lisans manifestidir. Actor ID/türü kaynak iddiasıdır, grant değildir. Gerçek input, model/runner/network listener/human approval ve canonical mutation uygulanana ve kendi koşulları doğrulanana kadar disabled/unsupported görünür. P0 snapshot DB'leri runtime'a taşınmaz.

## Alternatifler ve gerekçe

| Alternatif | Değerlendirme |
|---|---|
| T01/T02/T03 bütünü kapansın, sonra runtime | B olarak korunur; ana To Do ilerlemesini erteler |
| TypeScript/Node backend | Önceki DEC-13 adayının backend kısmı; bu ilk çekirdek için seçilmedi |
| Python3.12/SQLite | Yerel bundled runtime var, mevcut çalışma bilgisi ve stdlib test yolu; ek provider/dependency kurulumu gerekmeden seçildi |

Bu karar React veya başka frontend framework'ünü seçmez; UI, cloud, ekip DB, public lisans ve gerçek auth transport kendi işlerindedir. ADR-0001'deki store motoru SQLite tercihini kabul eder; bütün domain/projector/retention tasarımının implemented olduğu anlamına gelmez. DEC-13 backend adayının yerine DEC-21 geçer; niyet haritası ve eski öneriler geçmiş olarak korunur.

## Bedel ve yeniden açma

Semantik doğruluk, native'e ek kullanıcı değeri ve ekonomi henüz yeterince ölçülmedi. Yatırım ileride yeniden tasarlanabilir/durdurulabilir. Python3.12.x bu ilk runtime/CI ailesidir; başka minor/OS desteği doğrulanmadı. SQLite storage/backup/recovery T07 kapsamındadır; motorun bulunması storage kabulü değildir.

Taşıma ihtiyacı, dependency desteği, benchmark/pilot sonucu veya ekip gereksinimi değişirse yeni ADR ile değerlendirilir. Eski raw/oracle/kanıt ve full MVP14AC korunur. Genel “devam”ı geriye dönük runtime onayı yapmadık; bu yeni explicit Q15 yanıtı kabul kaynağıdır.

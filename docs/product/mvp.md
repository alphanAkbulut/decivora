# MVP spesifikasyonu

## P1a proof of concept ile P1b MVP ayrımı

P1a: Sentetik/import edilmiş bir oturumdan karar değişikliği, görev gerekçesi, onay ve replay akışını doğrulayan dar teknik kanıt. **MVP diye sunulmaz.**

P1b: Tek kullanıcının yerel uygulamada birden fazla projeyi takip edebildiği; Claude Code ve Codex için sürüm bazında doğrulanmış yakalama, minimal MCP, temel uzlaştırma, etki analizi, onay, doğrulama ve görsel takibin birleştiği ilk sürüm. Bir adapter başarısızsa sürüm “sınırlı pilot” olarak adlandırılır; kapsam sessizce daraltılmaz.

## Uçtan uca kullanıcı yolculuğu

1. Kullanıcı proje seçer veya repo gerektirmeyen proje oluşturur; oturum binding'i görünürdür.
2. Normal sohbet eder. Kaynak adapter yeni olayları kaydeder; erişemediği alanı coverage olarak gösterir.
3. Sistem ilgili bağlamı getirir; kayıt tiplerini, başlığı, açıklamayı, ilişkileri ve gözlenebilir AC'leri hazırlar.
4. Aynı öneri yeni task üretmez; kaynak bağlantısı eklenir. Yeni fikir hemen commitment olmaz.
5. Karar değişikliği eski görevlere etki seti çıkarır. Çoklu gerekçeler korunur.
6. Kullanıcı tekli veya geçerli toplu seçimle onaylar. Eski sürüm değişmişse onay uygulanmadan yenilenir.
7. Agent işi yaptığını bildirir; kanıt politikası uygun kriterleri doğrular. Dashboard eksik kriterleri gösterir.
8. Başka oturum/agent aynı projeyi mevcut kararla açar. History, önceki düşüncenin neden değiştiğini gösterir.

## MVP kabul kriterleri

| ID | Given / When / Then |
|---|---|
| AC-01 | Aynı adlı iki proje varken oturum A'ya bağlıysa, tüm capture/read/write yalnızca A'ya gider; binding yoksa quarantine oluşur |
| AC-02 | Aynı event yeniden gönderildiğinde tek domain etkisi oluşur; aynı metnin farklı mesajları yalnız hash yüzünden düşmez |
| AC-03 | Bir finding, prompt ve document instruction aynı batch'te yakalandığında kaynakları ve ilişkileri korunur |
| AC-04 | Agent yalnızca “done” dediğinde claim görünür; doğrulama bekler |
| AC-05 | Eski kararın tek gerekçesi olduğu açık iş obsolete adayı olur; başka geçerli OR gerekçesi bulunan iş korunur |
| AC-06 | Kullanıcı onay vermeden kabul edilmiş karar veya scope değişmez; onay sonrası yeni olay ve yeni projection oluşur |
| AC-07 | Onay ekranı hazır açıklama ve AC içerir; kullanıcı metin girmeden accept/reject/defer/compare yapabilir |
| AC-08 | Test başarısız olduğunda yeni olay ilgili verification'ı geçersiz kılar; önceki claim ve başarı tarihçede korunur |
| AC-09 | Graph, Board, Inbox ve Timeline aynı record/version'ı gösterir; eski görünüm revision ile işaretlenir |
| AC-10 | Database projection yeniden kurulduğunda aynı olay setinden aynı canonical state çıkar |
| AC-11 | İki coding adapter'ın ayrı test raporu vardır; ChatGPT/Claude Chat fallback'leri manuel/import diye etiketlidir |
| AC-12 | Bekleyen kararın konu, seçenek, kaynak ve bloke ettiği işler görünür; sadece “sonra bakarız” sözü kesin karar yaratmaz |
| AC-13 | Deterministic iş için LLM çağrısı yapılmaz; bilinmeyen kullanım ve limit aşımı görünürdür |
| AC-14 | Kaynak erişimi kesilirse sistem healthy/exhaustive capture iddia etmez; işlenmeyen aralık retry kuyruğunda kalır |

## MVP dışında, tam kapsam içinde

Tüm web sohbetlerine pasif erişim; gelişmiş embedding retrieval; derin code graph; IDE panelinin her host'a gömülmesi; otomatik model optimizasyonu; ücret/maliyet dashboard'u; çift yönlü Jira/Linear senkronizasyonu; takım/organization/cloud sync; enterprise audit ve managed orchestration sonraki fazlardır. [Tam kapsam](full-scope.md) bu fikirlerin kaybolmamasını sağlar.

Takvim taahhüdü yoktur. Çıkış kriteri [doğrulama planı](../quality/verification.md) ve [ölçüm kapılarıdır](../quality/measurement.md).

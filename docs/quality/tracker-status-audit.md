# Takip ekranı kayıt güncelliği incelemesi

**2026-10-13 · başlangıç ref `f0987c642a38b19c6420a29fabd068578f468aa9`.** Kullanıcı To Do ana işler, açık çalışma ve açık karar kayıtlarının doğruluğunu sordu. Yerel `/api/status`, açık in-app browser sekmesi, tracker kaynak kodu ve güncel backlog/readiness/decision kayıtları karşılaştırıldı. Yeni model veya runtime ürün deneyi yapılmadı.

| Alan | İnceleme sonucu / düzeltme |
|---|---|
| In Progress3 | T01 corpus/gold, T02 capability, T03 quality/yatırım kapanışları açık; doğru. Canlı worker/agent sayısı değil |
| To Do27 | T04–T24:21 MVP/P1 ana görev; T25–T30:6 future-phase ana görev. Doğru; hepsi hemen başlanabilir değildir |
| Küçük DONE22 | T01g/h/i +T03g–y; source/fixture/rapor teslimleri. Ana görevin Done olmaması bu teslimleri silmez |
| Açık kapılar5 | Panelde Q03-R6 yeni model run izni yoktu; R22 multi-answer engeli çözülmüş fixture yolunda hâlâ açık yazıyordu. Güncel6 aktif konu satırına hizalandı |
| T01 sonraki adım | T03y ile bitmiş receiver hazırlığını tekrar öneriyordu. T01'in kendi human exact-label/adjudication/holdout kapanışına düzeltildi |
| T03 risk/deneme özeti | Son ilerleme güncel, risk özeti eski MEMBERSHIP-002 noktasındaydı. RECEIVER-001 failure / T03y hazırlık / Q03-R6 pending ayrı gösterildi |
| Açık sekmede eski adlar ve Board yok | Sekme güncel API'yi okuyordu ama eski HTML/JS bellekteydi. Kaynak dosyadaki İngilizce durumlar/Board mevcut; reload ile güncel arayüz okunur. Görev sayılarına veya durum algoritmasına değişiklik yapılmadı |
| Evidence stale/91test | Tarihsel `semantic-readiness-results.json` checkpoint'i. Hash kapsamındaki sonraki değişiklikler nedeniyle stale; bütün proje başarısız veya güncel test sayısı değildir. Eski raporun tarihini/hash'lerini yeni247test/CI gibi yazmadık |

Aktif kapılar: Q03-R6 exact8089-byte RECEIVER-002 tek-run yetkisi; receiver gerçek model kalitesi; gold/adjudication; coding capture; adil native/receiver/user-burden/ROI kıyası; T03c production yatırım/stack. Bu6, bütün OPEN-01–16 ve Q sorularının toplamı değildir; sonraki faz lisans/retention vb. kendi karar belgelerinde korunur. Yeni soru/permission cevabı alınmadı. Q14-A seçimi kabul edilmiş durumda, tekrar sorulmadı.

Veri kaynağı readiness tablosudur; tracker otomatik domain memory/reconciliation uygulaması değildir. `project_progress.py --write/--check` kaynakla türetilmiş Markdown eşleşmesini kontrol eder; kaynak cümlenin tarihsel olarak doğru olduğunu kendi başına doğrulamaz. Bu inceleme gerekli olgusal metin düzeltmeleridir; yeni backlog/priority/UX/mimari kararı değildir. Mevcut görev/faz filtreleri, salt okunur API, canonical metadata, engine/gate ve38 Mermaid kaynakları korunur.

Doğrulama: docs/link/anchor/progress kontrolü; canlı API'de3/27/6 ve T01/T03 current next-action; mevcut takip testleri ve tarayıcı reload/refresh sonrası görünür durum. Yerel ekranın değişmesi GitHub push kanıtı değildir; scoped commit/readback ayrıca yapılır.

**Son kontrol:**40 mevcut takip/parser/localhost testi geçti; docs139/1510local link/51anchor/progress eşleşmesi passed. Native açık IAB sekmesi reload sonrası İngilizce In Progress/To Do ve Board içeriyor. Görünen kartlar30 teslim parçası /3 In Progress /27 To Do /6 kapı; T01 next-action gold kuyruğu, T03 yeni run izni. Ekran görüntüsü yerel teslim artefaktı olarak kaydedildi; repo'ya kaynak snapshot/ham özel transcript eklenmedi.38Mermaid kaynağı aynı, yeni model/API0.

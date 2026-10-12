# Mevcut üyelikle quote-only smoke planı

**2026-10-12 · T03k DONE: ön-hazırlık paket/harness. MEMBERSHIP-001 artık bir kez çalıştırıldı.** [Güncel gerçek run](membership-001-result.md): kullanıcı onayı alındı ve tüketildi; üç source quote geçti, exact candidate gate incomplete. Aşağıdaki input/plan dosyaları çağrı öncesi snapshot'ıdır; bunları sonradan başarılı test olacak şekilde değiştirmedik.

## Somut deney paketi

- [Prompt](../../examples/membership-smoke/prompt.txt): **3330 UTF-8 byte**, dört sentetik mesaj. S02: geç Q_STORE/B cevabı, “Yükledim”, AC_ROLLBACK geçti bildirimi. S03: iki açık A/B soru context'i ve “A” cevabı.
- [Requests](../../examples/membership-smoke/requests.json): iki farklı projenin ayrı request/source/contract kimliği; dört mesajın source revision'ı korunur. İki packet tek UI submission önerisidir; iki gerçek inference garantisi veya bütün corpus değildir.
- [Plan](../../examples/membership-smoke/plan.json): MEMBERSHIP-001, proposed_manual_submissions=1, automatic_retries=0, actual_submissions=0; dispatch_authorized=false, paid_api_allowed=false **ön-hazırlık snapshot değerleri**; gerçek onay/tüketim ve tek submission [authorization kaydında](../../examples/membership-smoke/authorization.json).
- [Ayrı candidate beklentileri](../../examples/membership-smoke/candidate-rubrics.json): authored_draft. **Bu dosya modele gönderilmez.** H1/H2/H3 insan review'u davranışları onayladı; exact kind/quote/attributes beklentilerini human-gold yapmadı. Corpus oracles/ham eski sonuçlar değiştirilmedi.
- [Hashli hazırlık kanıtı](membership-smoke-preparation.json): 72 semantic suite testi, altı yeni batch testi; gerçek accuracy ve usage ölçülmedi.

## Kullanım sınırı ve onay

**Önerilen kapsam:** normal ChatGPT hesabında boş geçici oturum; yalnız prompt.txt; tek gönderim/ilk çıktı; browser tools/browsing/subagent yok, retry/regenerate/model-switch ikinci gönderim yok. Yeni maliyet veya API bağlantısı açılmaz. Model UI etiketi, gerçek kaynak/çıktı transferi ve session isolation o anda gözlenir; bugün doğrulanmış sayılmaz.

Prompt'taki **2048 output token hedefi soft talimattır**, garanti/hard cap değil. 3330 byte token sayısı değildir. Tam input, gizli framing/reasoning, hesap kotası ve kesin context üst sınırı unknown. Hesabın normal kullanım kotası harcanabilir; per-run token veya parasal tavan bu arayüzde doğrulanmadı. Eski iki tek-send onayı tüketildi. **MEMBERSHIP-001 için bu onay alındı ve tek gönderimde tüketildi. Yeni/v2 gönderim ayrıca onay ister; otomatik tekrar yok.** Bu istisna product hard-cap gereksinimini değiştirmez; production uygulama için uygun limiter gerekir.

İlk challenge/refusal/timeout/incomplete output'ta stop: başarısız veya unknown olarak kaydet, otomatik tekrar yok. Kısmi batch başarılı tam deney diye sunulmaz. Raw output değiştirilmez; source span'ını kod bulur, şema ve authority retleri korunur. Eksik/missing quote'u elle “başarılı” olacak biçimde tamamlama.

## Çalışan hazırlık ve çıktı import kodu

Repo kökünde source-only hazırlık (hiçbir model çağrısı yapmaz):

```sh
python3 -B spikes/semantic-chain/membership_batch.py prepare --requests examples/membership-smoke/requests.json
```

Kayıtlı gerçek çıktı geldiğinde ayrı değerlendirme:

```sh
python3 -B spikes/semantic-chain/membership_batch.py evaluate --requests examples/membership-smoke/requests.json --response /tmp/membership-001-raw.txt --rubrics examples/membership-smoke/candidate-rubrics.json --out /tmp/membership-001-audit.json
```

Raw dosya o anda kaydedilmiş gerçek model çıktısı olmalıdır; komut onu üretmez. `--out` overwrite etmez. CLI'nin exit 0 olması semantik başarı değildir; import/evaluation status ve missing/extra okunur. Source validation tüm received candidate'lar için oracle dosyası okunmadan tamamlanır; foreign/duplicate/stale/project swap veya tek hatalı quote bütün import'u reddeder. 64 KiB raw output file sınırı yalnız yerel importer korumasıdır, model tüketimini sınırlamaz. Eksik packet ve abstain incomplete; candidate/state/authority/target/AC ayrı katmanlardır.

Batch `format=decivora-membership-batch-1`, `responses` array taşır; her eleman quote adapter envelope'udur. Proje request/contract binding'i başkasının mesajıyla karıştırılamaz. Request/model text source metadata içindeki fixture auth/expected sonucunu almaz. Selection/impact/verifier çağrıları extractor çıktısından çalıştırılmaz; mevcut domain fixture bağımsız kalır.

## Başarı/başarısızlık yorumu

1. Önce transport + iki request/source + quote/type/schema validator sonucu.
2. Sonra ayrı authored candidate rubric one-to-one exact eşleşmesi: TP/FP/FN ve eksik/fazla alanlar. Başarısız case'ler saklanır, development örneği olduğundan genel accuracy ilan edilmez.
3. H1/H2/H3 davranış beklentileri ile ayrı domain fixture sınırı: model cevabı authority/verified/Done değildir. Yetkili selection ve gerçek target/AC ayrıca gerekir; candidate scorer bunları ölçmez.
4. Tek başarılı test bile production yatırım kapısını tek başına kapatmaz. Yeni model testi n=1, source ve eski expectations bu geliştirme oturumunda görünürdü; blind/sealed holdout değildir.

Gerçek denemeden sonra actual model label, submission count, raw SHA, observed failure/status ve usage unknown alanı yeni immutable run kaydına alınacak. Bu hazırlık sırasında provider/model dispatch yapılmadı. Geliştirme kapsamında bu Codex oturumunun kendi kota/token kullanımı ayrıca geçerli; ölçülmedi.

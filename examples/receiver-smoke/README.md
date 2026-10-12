# RECEIVER-001 — yeni sohbet okuma deneyi hazırlığı

**Hazırlık snapshot'ı korundu; ilk native run yapıldı fakat contract geçmedi.** [Güncel sonuç](../../docs/quality/receiver-001-result.md); tek-send izni tüketildi, yeni deneme yetkisi yok. [Deney planı ve sınırlar](../../docs/quality/receiver-smoke-plan.md).

| Dosya | Kullanımı | Modele gönderilir mi? |
|---|---|---|
| [prompt.txt](prompt.txt) | Tam 7.950 UTF-8 byte; iki synthetic okunabilir view ve genel output sözleşmesi | Yalnız yeni tek-send onayı sonrası bu exact metin |
| [request.json](request.json) | Request/view/prompt bağları; aynı prompt ve no-dispatch metadata | Tam dosya gönderilmez; prompt.txt seçilir |
| [expected.json](expected.json) | Ayrı authored draft readback/next-action oracle | **Hayır** |
| [manifest.json](manifest.json) | Source/hash/scope ve tek-send/0retry/0API önerisi, actual sent0 | **Hayır**, onay veya çalıştırma kaydı değildir |

Kaynak: [N01](../resume-compact-smoke/N01-readable.json) ve [N02](../resume-compact-smoke/N02-readable.json), toplam sekiz seçilmiş synthetic mesaj. Yeni human project state veya hedef uygulaması yok. Önceki gerçek model output'undan türetilmiş development örnekleri; blind holdout/human gold değildir.

Prompt içinde beklenen yanıt dosyası veya puanlama oracle'ı yok. Source facts/status etiketleri doğal olarak view'da görünür; bu **mevcut proje context'ini okuyup güvenli sonraki adım önerme** testidir, yeniden semantik extraction ya da end-to-end development testi değil. Test output'u canonical karar/approval/verification olmaz.

```sh
python3 -B spikes/semantic-chain/receiver_smoke.py prepare --out /tmp/receiver-request-new.json
python3 -B spikes/semantic-chain/receiver_smoke.py evaluate --request examples/receiver-smoke/request.json --response /tmp/receiver-first-output.txt --expected examples/receiver-smoke/expected.json --out /tmp/receiver-score-new.json
```

Komutlar model çağırmaz, anahtar istemez, mevcut output'u değiştirmez. Evaluator exact source/project/package binding'i, bool/revision/list tiplerini ve aliases/duplicates kontrol eder; code-fence veya anlamsal alanları gizlice düzeltmez. Bozuk raw ayrı korunup validation hatası kaydedilir; yeniden deneme otomatik değildir.

**Önerilen gerçek run:** Normal Chrome'da tek boş geçici/kişiselleştirilmemiş ChatGPT oturumu, yalnız prompt.txt, bir gönderim/ilk çıktı/0retry; tools/agents/paid API yok. Hedef UI capability ve boş session run sırasında doğrulanır; backend/usage/gerçek hard token-context cap unknown. Soft1536 output talimatı hard cap değildir; mevcut hesabın ortak kotası tüketilebilir. Bu öneri henüz kullanıcı izni sayılmaz.


## Actual run eki — 2026-10-12

Kullanıcı yeni local chat'i açıp configuredLuna/Low deneyini yapmamızı istedi. [İzin](authorization.json) tüketildi; [ilk native sonuç](../../docs/quality/receiver-001-result.md) syntaxvalid/schemainvalidabstention, retry/paidAPI0, scoresunscored/usageunknown. Başlangıç manifesti/readme hazırlık sent0/onaypending/Chrome satırları tarihsel snapshot; değiştirilmedi. Exactprompt7950byte ve ayrı expected aynı kaldı. Gerçek model kalite kapısı açık; actualraw'a alias/type/status düzeltmesi yapılmaz. Geliştirme ana sohbette devam eder, deney chat'ine yeni prompt gönderilmez.

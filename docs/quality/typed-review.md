# Tipli kayıtlardan kodla inceleme taslağı

**2026-10-13 · T03aa / P0, kapsamı sınırlı kod teslimi DONE.** [`typed_review.py`](../../spikes/semantic-chain/typed_review.py) mevcut iki sentetik, source-bound wire-2 snapshot'ındaki altı tipli kaydı kullanır. Bu dönüşüm yeni model çağrısı gerektirmez. [İncelenebilir çıktı](../../examples/receiver-next-smoke/typed-review.generated.json) · [Bağımsız karşılaştırma ve hash kanıtı](typed-review-results.json).

## Neden bu yöntem?

[RECEIVER-002](receiver-002-result.md) sırasında model, zaten belirlenmiş bilgileri yeniden üretirken required işlem listesini atladı ve belirsiz cevaba soru tahmin etti. Kayıt türü, mevcut soru, candidate status ve kaynak ilişkisi zaten yapılandırılmışsa bunları tekrar modele kopyalatmak zorunlu değildir. Kabul edilmiş deterministik work routing ilkesi bu küçük dönüşüme uygulanır; yeni production stack, IAM veya genel ürün mimarisi kararı değildir.

| Alternatif | Gözlenen / beklenen durum | Bu teslimde seçilen |
|---|---|---|
| Aynı kayıtları üçüncü model çağrısında tekrar okutmak | Yeni izin/kota ve tekrar hata ihtimali; yeni ölçüm yok | Yapılmadı |
| Başarısız ham cevaba eksik alan eklemek veya Q_UI bağını silmek | Tarihsel model sonucu değişir; gerçek başarıyı göstermez | Yapılmadı |
| Mevcut tipli veriden ayrı kökenli deterministic taslak | Kuralları kodla uygular; kaynak yetkisini veya doğruluğunu artırmaz | **Uygulandı** |

## Çalışan akış

`seçilmiş request + caller context → güncel binding/access fixture kontrolü → tipli record kuralları → wire-2 schema/source doğrulama → bağımsız proje review`

Model raw veya oracle, `build` fonksiyonunun girdisi değildir. Hazırlama/freshness yolunun okuduğu dosyalar yalnız mevcut pinned source request ve iki readable source view'dur. Kaynak state ile model-reported candidate bilgisi onaylanmış gerçek bilgi sayılmaz. Output origin **`deterministic_selected_typed_records`**, input origin mevcut source-bound model-reported records + fixture state olarak ayrıca yazılır. Bu metadata taslağın kökenidir; signed event/receipt veya production auth değildir.

| Seçilmiş kayıt | Üretilen güvenli taslak | Sınır |
|---|---|---|
| Eski revision cevap | `preserve_history` | Güncel seçim yapılmaz |
| Güncel bağlı cevap | `request_selection_confirmation` | İnsan onayı uygulanmaz |
| Belirsiz veya çelişkili cevap | `request_clarification` | Kaynakta soru yoksa null; en son soru tahmin edilmez |
| Upload claim | `request_target_verification` | `reported_only`; hedef okunmaz |
| Evidence `not_run` | `request_test_execution_permission` | Test çalıştırılmaz |
| Diğer desteklenen geçmiş durum | `preserve_history` | Yetki/verification verilmez |

Altı record için altı action üretilir; quoted N01-m03 ve geleceğe yönelik N01-m04 source mesajları preserved record değilse action üretilmez. Mevcut bilinen Q_UI sorusu ile ayrı belirsiz N02-m04 birlikte korunur. Unknown record/status, duplicate message, eksik candidate, stale snapshot, revoked access ve farklı request reddedilir. Bu P0 profili bir mesajda bir preserved record ile iki sabit sentetik snapshot'a bağlıdır; arbitrary kullanıcı verisi ve bütün record türleri desteklenmiş sayılmaz.

Çıktı schema/source gate'ten geçse de `approved_real_decision:false`, `task_verified:false`, `execution_authorized:false`, `canonical_mutations:0` kalır. İki bağımsız proje `ready_for_review` / `needs_clarification` döner; atomic group seçilirse birlikte bekler. Bu çalışan UI veya kalıcı Inbox değildir. Model-reported yanlış bir input'u doğruymuş gibi onaylamaz; input semantik doğruluğu ayrı extraction/insan inceleme kapısıdır.

## Doğrulama

13 yeni test; **222 semantik /15 karar /40 repo testi** geçti. Ayrı elle yazılmış authored oracle, dönüşümden sonra okunur: readback eşleşti, action TP6/FP0/FN0. Bu **iki görülmüş fixture'da deterministic dönüşüm doğruluğu**; human gold/holdout/model genelleme veya ekonomik üstünlük değildir. İlk test yazımında candidate sırası varsayımı iki kontrolü yanlış kayda yöneltti; testler message ID ile bağlanarak düzeltildi. Kaynak ve ürün kabul koşulları gevşetilmedi.

Negatifler: guessed-question, false approval/verification, future/quoted action, source/record/question tamper, access/state change, unknown/duplicate/missing record, atomic group; oracle/raw dosyası okumasını engelleyen hermetik test; input immutable/retry deterministic; CLI oracle/response parametrelerini reddeder ve mevcut output'u overwrite etmez. Daha geniş answer/evidence policy unit örnekleri public request desteği veya yeni kullanıcı senaryosu ölçümü değildir.

```sh
python3 -B spikes/semantic-chain/typed_review.py --request examples/receiver-next-smoke/request.json --context examples/receiver-next-smoke/review-context.fixture.json
python3 -B spikes/semantic-chain/check_typed_review.py
python3 -B -m unittest discover -s spikes/semantic-chain -p test_typed_review.py -v
```

CLI `--out` verilirse yeni yerel dosyaya yazar; `build` dönüşümü read-only'dir. Yeni dependency/provider/key veya paid API yok. Aynı bütün proje geçmişi tekrar işlenmez. **Bu dönüşüm için model call0; toplam geliştirme tokenı ve önceki extraction maliyeti unknown.** Byte/token/para tasarruf oranı üretilmedi.

## Geçmiş ve kalan iş

İki actual receiver raw/hash/result değişmedi: ilk ve ikinci model run hâlâ failed/unscored. Yeni generated dosya onların yerine geçmez; farklı output origin ile ayrı tutulur. Frozen request/prompt/schema/manifest/oracle ve mevcut38 Mermaid kaynakları aynı; mimari üretim önerileri veya eski akışlar bu fixture koduyla implemented yapılmaz.

Bu teslim R24'ün **mevcut tipli bilgiyi tekrar üretme** hata yüzeyini iki fixture'da kodla ortadan kaldırdı. Serbest metinden doğru candidate çıkarımı, durable soru yönetimi, gerçek IAM/host capture, native/user burden/ROI, AC revision/target verification ve T03c production yatırım/stack kararını çözmedi. T01/T02/T03 ana işleri açık; T04 başlamadı. Üçüncü model run onayı yok.

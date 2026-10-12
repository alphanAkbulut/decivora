# Fresh-session receiver deneyi — RECEIVER-001 hazırlığı

**2026-10-12 · T03u hazırlık DONE; T03v ilk native run kayıt teslimi DONE.** Güncel [RECEIVER-001 sonucu](receiver-001-result.md) **invalid_contract**, tek-send izni tüketildi. Aşağıdaki hazırlık tablosu/limitler dispatch öncesi snapshot'tır; güncel run ile karıştırılmamalı. [Dondurulmuş istek ve ayrı oracle](../../examples/receiver-smoke/README.md) · [Hazırlık ölçümü](receiver-smoke-preparation-results.json) · [Önceki küçültme kanıtı](resume-compaction.md).

## Testin hedefi ve kapsamadıkları

Soru: temiz bir alıcı model oturumu, **iki source-bound readable view** içinde görünen current/pending/stale/ambiguous/claim/not_run durumlarını doğru devralıp güvenli sonraki adımları ayırabiliyor mu? Mevcut label/fact'ler view'ın doğal içeriğidir; oracle ayrı tutulur. Bu readback/next-action testi discovery/extraction doğruluğu, source capture, native/file üstünlüğü veya gerçek görevi uygulama kanıtı değildir. Ürün devamlılığı için gerekli dar bir kapıdır; genel kalite/ROI gate'i kapatmaz.

## Somut istek ve sınırlar

| Alan | Hazır değer |
|---|---|
| Deney | RECEIVER-001-PROPOSED; yeni tek gönderim izni henüz yok |
| Veri | N01/N02 readable view; iki synthetic proje, toplam8 mesaj; mevcut izinli fixture context/candidate/coverage |
| Exact gönderilecek metin | [prompt.txt](../../examples/receiver-smoke/prompt.txt) |
| Byte boyutu | **7.950 UTF-8 byte**, newline dahil; local ceiling8.192byte |
| Prompt SHA-256 | `a4a636ecd53aee80ea74ef21608e26cdb50cc65f1f1da434a9cf9294d2073b6b` |
| Request ID | `f5da3c5442475bbfdae423fbff1cfea8bdd3e0125d4c9168958666e870940833` |
| Önerilen yöntem | Normal Chrome, boş geçici/kişiselleştirilmemiş mevcut ChatGPT hesabı; capability run sırasında kontrol edilir |
| Sınır | Bir UI submission, ilk output; retry/regenerate/model-switch/tools/subagents/paid API0 |
| Output talimatı | En fazla1536 token hedefi; **soft**, doğrulanmış provider hard cap değil |
| Bilinmeyenler | Actual model/backend, token/context hardcap, kullanım/token/para ve provider iç istek sayısı |
| Mevcut durum | actual submissions0/outputs0, dispatch_authorized false; mevcut üyelik kotası gerçek run'da tüketilebilir |

Byte sınırı token bütçesi değildir. İstek oluşturulması/görünümün okunması ücretli API izni vermez; quota bilinmiyorsa zero denmez. Erişim challenge veya belirsiz gönderim olursa otomatik ikinci deneme yok. Önceki model izinleri consumed; bu test için kullanıcı somut sınırı onaylamadan send yapılmaz.

## İki ayrı değerlendirme

**Readback:** current question ID/revision/pending, answer states, gerçek onay/task verification olup olmadığı, upload'un reported/unknown/observed ayrımı, explicit Evidence criterion/revision/result. Required fixture criteria ile gerçekten raporlanmış test sonuçlarını karıştırma. Kaynakta task_verified veya actual human approval kanıtı yok; fixture_initial kullanıcı mimarisi değildir.

**Next-action:** Her preserved record için öneri: stale answer history'de kalsın; current answer ayrı confirmation istesin; bağsız B clarification beklesin; upload claim exact hedefi doğrulama gerektirsin; not_run evidence runner/test execution permission ihtiyacını göstersin. Bu actions **öneri**; execution, onay veya gerçek target okuması tetiklenmez. Kullanıcı cevabı doğru soruya bağlansa bile impact/apply ayrı kapıdır.

Oracle source/logic tartışmalarına dayanan bağımsız authored draft'tır; model veya encoder çıktısından etiket üretilmedi. ID/package hashleri yalnız immutable kaynak bağlarından alınır. H1–H4 önceki insan review'ları davranışın bir kısmını destekler; bütün yeni exact output tuple'ları veya ikinci adjudication onaylanmış gold değildir. N01/N02 hazırlayan agent'a açıktı; sealed holdout iddiası yok.

## Çalışan evaluator sözleşmesi

`receiver_smoke.py prepare` yalnız seçili readable source ve source-bound generator'a bakar; expected/prediction input kabul etmez. Source/request/rule/schema/hash/byte sınırı bağlanır. Prompt içinde source label'ları bulunması beklenen durumdur; ayrı expected.json veya scorer output'u taşınmaz.

`evaluate`:

1. Raw JSON bounded strict parse; duplicate keys/non-finite/code-fence ret, otomatik normalizasyon yok.
2. Request/project/package digest binding, foreign source-message/duplicate response, bool/int/criterion/list tip kontrolü. Source sırası semantic winner değildir.
3. Ayrı oracle'nın aynı request ve iki tam unique proje kapsamına bağlı olduğunu kontrol et. Missing/duplicate/stale oracle veya human-gold promotion ret.
4. Readback alanlarını exact değerlendir; array order farkı puanı bozmaz. Next-action project/type/message/question tuple multiset'i TP/FP/FN olarak karşılaştır; fazla action eklemek TP yaratmaz.
5. Eksik proje/abstention **incomplete**, yanlış anlam **failed_draft**, tam draft uyumu **passed_draft**. Hiçbiri canonical state'i değiştirip görevi tamamlamaz.

Kritik hata ayrımı: false real approval, false task verified, upload claim→observed_verified, not_run→passed, ambiguous answer'a unsupported soru bağlama ve stale answer'ı current selection önerme. Execution action veya model-supplied authority/extra fields sözleşme tarafından reddedilir. Validation exception durumunda raw korunur ve invalid contract kaydı ayrıca yazılır; başarısızlığı retry veya alias repair ile gizleme.

Imported output her zaman `caller_imported_unverified` diye etiketlenir; CLI canlı model çalıştırmaz ve kendi başına model identity/usage veya real-run kökeni iddia etmez. Actual UI submission, ilk-output capture SHA, timestamp ve onay provenance ayrıca run raporunda doğrulanacak. Private conversation URL/ID/credential repo'ya konmaz.

## Şimdiki doğrulama

**134 semantik test /13 yeni evaluator testi geçti:** frozen prepare/no-oracle input, scripted positive, stale revision/not_run→passed, false approval/done/upload, ambiguity mapping, missing/abstain, foreign package/project/message/duplicate, type coercion/aliases/execute action, raw limit/duplicate JSON/non-finite/fence, changed request/source/prompt, missing/duplicate/stale/gold oracle, sıra bağımsızlık/excess action, CLI no-overwrite/no oracle prepare.

[Hazırlık raporundaki](receiver-smoke-preparation-results.json) scripted positive oracle'yı kopyalayıp evaluator'ı çalıştırır: yalnız harness kabul kontrolü; gerçek model output'u veya inference başarısı diye sunulmaz. Aynı dosya model_dispatches0/actual outputs0/human_goldfalse ve input/code/test hashlerini taşır. Önceki raw/prompt/expected/export/proof/36 Mermaid kaynakları değişmedi.

## Run sonrası kayıt ve kalanlar

Yeni somut onay gelirse önce izin scope/prompt hash kaydı; ilk send/ilk output copy byte'ları değiştirilmeden saklanır. Source metadata/contract/readback/actions ayrı score; yanlış source hash, alan veya critical error düzeltilemez, aynen kayıt edilir. İlk failure/incomplete sonucu yatırım kararına girer; otomatik daha fazla model isteği yok. Canlı test n=1 iki synthetic development proje, genel accuracy/tasarruf/ürün satış değeri değil.

RES-08 için bu dar yeni-sohbet readback deneyinin ardından aynı information/config ile baseline/user burden/native ve kaynak gaps negatifleri hâlâ gerekir. Production IAM/criterion revision/source-receipt lineage, T03c yatırım/stack ve T04 açık. Gerekli işi opsiyonlaştırmıyoruz; bu soru yalnız sınırlı yeni run yetkisini çözmek içindir.


## Kullanıcının yeni oturum talebi — 2026-10-12

Kullanıcı ayrı chat'i açıp Luna/Low deneyini yapmamızı ve önce model/reasoning/token/context notlarını kaydetmemizi istedi. [Execution notu](receiver-execution-notes.md) ve [yeni tek-turn scope izni](../../examples/receiver-smoke/authorization.json) gerçek dispatch'ten önce kaydedildi. Yöntem artık local projectless Codex chat +explicit gpt-6-luna/low; eski Chrome önerisi historical manifestte korunur. Frozen7950-byte prompt/expected/source değişmedi. Ana geliştirme burada, deney chat'i sadece ilk test output'u içindir. Sonuç henüz not_run; izin grant'i başarı veya gold onayı değildir.


## İlk run tamamlandı — 2026-10-12

[RECEIVER-001 actual sonuç](receiver-001-result.md): kullanıcı yeni local chat'i açıkça istedi, tek configured gpt-6-luna/low turn çalıştı. İlk raw1739byte syntax valid, schema invalid receiver abstention; scoresunscored/usageunknown, retry0/paidAPI0. İzin tüketildi. Frozen hazırlık request/prompt/oracle/manifest değişmedi; yukarıdaki hazırlık not_run/onaypending satırları tarihsel snapshot'tır. Native host/extra injected wrapper tarayıcı planından ayrıdır; summary yerine fullmessagecapture kullanıldı. Bu güncel sonuç model/gold/native/production kapısını kapatmaz.

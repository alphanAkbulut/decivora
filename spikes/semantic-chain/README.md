# P0 — Semantik çıktı bağlantısı ve deney çalıştırıcısı

**Çalışan P0 kod.** Tarihsel S02-001 erişim hatası, S02-002 output/strict span reddi; yeni adapter üzerinde gerçek inference yapılmadı. Python 3.9+ standart kütüphanesi. Yeni dependency, ücretli API, gerçek transcript, global config veya host kurulumu yok. Bu P0 prototipidir; production extractor/MCP/IAM değildir.

## Çalışan akış

Seçilmiş sentetik kaynak → source-only model isteği → dışarıdan gelen JSON’un doğrulanması → karar adayı → ayrı güvenilir selection makbuzu → mevcut karar/etki zinciri → hedef gözlemi → AC → backup/replay.

`protocol.py` prompt/version, project/session/message/source hash, Unicode quote/span, aday türleri, duplicate/byte/record limitleri ve abstention’ı doğrular. Oracle veya source metadata auth bilgisi modele verilmez. Model accepted/verified/permission/command gibi yetki alanları üretemez; öneri canonical mutation yapmaz.

`bridge.py` AnswerRecord adayını açık soru/revision’a bağlar. Belirsiz, birden fazla veya stale aday değişiklik yapmaz. Apply; proje, kaynak hash, mesaj, soru/seçenek/revision ve base revision’a bağlı **ayrı trusted fixture receipt** ister. Source içindeki “onayladım”/metadata veya agent rolü bunu sağlayamaz. Gerçek uygulamada bu makbuzu authenticated transport/policy servisi üretmelidir; fixture dict kullanımı production auth değildir.

`experiment.py` altı mevcut sentetik session için source-only istekleri hazırlar; gerçek output JSON/JSONL geldiğinde source binding’i doğrulayıp bağımsız scorer’a taşır. Hiç response gelmemesi veya abstention `incomplete`; boş sonuç başarı değildir. Scorer full domain release gate değil, mevcut span/tür ölçümüdür. Ayrı checkpoint scorer verilen kritik alanların eksik/yanlış olmasını görünür kılar.

## Komutlar

Repo kökünden:

```bash
python3 -B -m unittest discover -s spikes/semantic-chain -v
python3 -B spikes/semantic-chain/run.py
# Sadece dosya hazırlar; provider’a göndermez. Hedef varsa üzerine yazmaz.
python3 -B spikes/semantic-chain/experiment.py prepare --out /tmp/decivora-requests.jsonl
# İzinli model çalışmasından sonra JSON object/array veya satır başına contract response:
python3 -B spikes/semantic-chain/experiment.py evaluate --responses /tmp/decivora-responses.jsonl
```

Prepare: 6 session/58 source mesajı; insan gold pending, reserved split sealed değil. Her request’te response contract ve allowed kinds bulunur. Byte limit token/maliyet tahmini değildir. Output token tavanı 1536 **önerilen provider ayarıdır**; bu kod network çağırmadığı için provider harcamasını sınırladığını iddia etmez. Usage/provider/model unknown kalır. Ücretli otomatik dispatch, retry/atomik budget reservation ve gerçek provider usage doğrulaması bu dilimde uygulanmadı.

`run.py` mevcut S02 source mesajıyla **scripted response contract fixture** çalıştırır. Yedi checkpoint bağımsız yazılmış [beklenti dosyasına](expected-checkpoints.json) göre ölçülür; kod algoritması beklenen sonucu üretmez. Model anlam kalitesi testi değildir. Gerçek target yerine temporary fixture ve kontrollü AC sonucu kullanılır. [Kaydedilmiş sonuç](../../docs/quality/semantic-readiness-results.json).

İlk teslimde 28 test; kaynak adapter/candidate rubric teslimiyle suite toplamı 48 test: source/authority/namespace/span/version/type/schema sınırları, malicious output, abstention, limit, duplicate, stale/ambiguous soru, ayrı receipt, agent approval reddi, idempotency, evaluator missing ve checkpoint fail/incomplete. Production kaynak ACL’si, çok soru/graph modeli, gerçek provider/host ve native kıyas hâlâ ilgili görevlerdedir.

## Neyi bekliyoruz?

Yeni quote-only contract için gerçek semantik output ve kullanım ölçümü gerekiyor; sağlayıcı/model, source-only veri ve toplam maliyet sınırı henüz yetkilendirilmedi. Tarihsel S02-002 output'u geldi fakat strict kaynak konumu kontrolünden geçmedi. Yeni adapter bu hatayı ayrı türevde çözer; orijinal sonuç korunur. API yöntem önerisi ve kalan kalite kapıları [teslim raporundadır](../../docs/quality/source-anchor-adapter.md). Gerçek model testi zorunludur; yöntem/bütçe seçimi onu isteğe bağlı yapmaz. Yeni dispatch olmadan local kod ve negatifler tamamlandı.

Human gold review kalite iddiasını, T03c owner kararı production teknoloji/yatırımı sınırlar. Ekip/cloud/dil/future özellikleri bu P0 kod çalışmasını bekletmez; MVP/full-scope ayrı fazlarında korunur.


## Mevcut asistanın aday taslağı

[12 aday](fixtures/assistant-s02-draft.json), bu konuşmadaki asistanın S02 metinlerinden yazdığı yorum taslağıdır. [Provenance](fixtures/assistant-s02-provenance.json): prior oracle görünür, blind değil, human review pending, automatic model dispatch yok. Parser/bridge import’unu gerçek bir AI taslağıyla sınar; ayrı provider veya extraction kalitesi benchmark’ı diye sunulmaz. `run.py --response spikes/semantic-chain/fixtures/assistant-s02-draft.json` aynı source-bound zinciri bu taslakla çalıştırır. Tüm altı session response’u olmadığı için corpus değerlendirmesi incomplete kalır.


**Seçili gerçek hedef gözlemi:** [GitHub readback kaydı](../../docs/quality/semantic-target-readback.json) mevcut corpus rehberini iki immutable ref’te gerçekten okur. Aynı byte’lar olsa da beklenen ref dışındaki gözlem stale; seçilen ref observed_match. `target.py` ayrıca repo/path/revision/hash ve missing/unknown ayrımını sınar. Gözlemler authenticated connector çağrılarıyla toplandı; Python assessor fetch/auth yapmaz. Dosya eşleşmesi storage kararının uygulandığı veya task DoD’unun geçtiği değildir. Kontrollü chain koşusundaki target hâlâ fixture’dır; iki kanıtı karıştırma.


## Bounded quote adapter ve ayrı candidate değerlendirmesi

`anchors.py` / `anchor_cli.py`: modelden offset istemeyen ayrı quote-only contract; unique exact quote konumunu code hesaplar, ambiguity/stale/authority/limit reddi korunur. Eski response yalnız açık legacy opt-in ile türetilir; raw/türev hash ayrı, canonical mutation 0. `candidate_eval.py` dört aday alanını exact one-to-one ölçer; canonical karar/onay veya verification ölçümü değildir. Historical protocol/prompt ve oracle korunur.

`python3 -B spikes/semantic-chain/run_anchor_checks.py` mevcut raw S02 ve üç authored scripted case için hashli kanıtı tekrar üretir. 20 ek testle toplam 48; yeni provider dispatch yok. CLI komutları, API değerlendirmesi ve kalan kapılar [teslim raporunda](../../docs/quality/source-anchor-adapter.md). Audit wrapper’ın `response` alanı ayrı candidate envelope’dur; eski runner’a wrapper’ın tamamını verme. Yeni gerçek deney için model/veri/bütçe izni gerekir.

## Quote-only API paket hazırlığı

`provider_packet.py` gönderimsiz Responses schema/payload taslağı ve saved response import sağlar. `experiment.py` mevcut corpus evaluator olarak korunur. [Teslim, komutlar ve sınırlamalar](../../docs/quality/quote-api-package.md); model/bütçe/onay pending, semantic suite 56 test. Gerçek provider çağrısı veya anlam doğruluğu kanıtı değildir.

## Seçilmiş yerel hedef gözlemi

`local_observer.py` yalnız tek seçili yerel dosyayı bounded read ile gözler; bütün task'ı veya GitHub upload'ını doğrulamaz. [Teslim ve gerçek local read kaydı](../../docs/quality/local-observer.md). Dokuz yeni test, semantik suite 65 passed; model anlam ölçümü hâlâ açık.

## Tek komutluk integrated teslim — T03j DONE

`python3 -B spikes/semantic-chain/run.py` quote-only adapter + bounded observer + ayrı karar/impact + partial/full AC + restore zincirini çalıştırır. [Kapanış koşulları ve kayıt](../../docs/quality/integrated-chain.md). 66 suite testi geçti; gerçek inference/production kapıları açık. T03g/h/i/j DONE ana T03'ü kapatmaz.

## Mevcut üyelik smoke hazırlığı — T03k DONE

`membership_batch.py` tek proposed manual submission için source-only batch hazırlar ve saved quote output'unu ayrı authored rubric ile değerlendirir. [Prompt, plan, import komutları ve izin sınırı](../../docs/quality/membership-smoke-plan.md). 72 suite testi passed; gerçek model send/accuracy/usage not_run.

## MEMBERSHIP-001 gerçek run ve ayrı typed contract

[Ham run, incomplete skor ve offline v2](../../docs/quality/membership-001-result.md) kaydedildi. `membership_typed.py` v1 raw'ı değiştirmeden ayrı field/type contract sağlar; no-dispatch CLI, 78 semantik test. T03l/T03m scoped DONE, v2 gerçek test/quality not_run; tek onay tüketildi.

## MEMBERSHIP-002 gerçek typed ölçüm — T03n DONE

[İlk v2 çıktı/rapor](../../docs/quality/membership-002-result.md): tek yeni onaylı UI send, retry/paid API 0; dört exact source/typed aday authored_draft beklentiyle eşleşti. 80 semantik test; stored raw hash/scoring ve ayrı no-mutation guard regresyonları. Genel model doğruluğu/insan gold/domain execution değil; eski v1 kayıtlar korunur. Sırada kaydedilmiş v2 adaylarıyla fixture zincir replay; yeni canlı çağrı izni tüketildi.

## Kaydedilmiş gerçek adaylardan zincir replay — T03o DONE

`python3 -B spikes/semantic-chain/replay_membership.py` source-bound MEMBERSHIP-002 raw'ı kendi request kimliğiyle işler; bağımsız fixture receipt, ayrı impact, eski/güncel gerçek temporary içerik, partial/full AC ve backup/reopen. Yeni model/egress0; [13 checkpoint ve sınırlar](../../docs/quality/membership-chain-replay.md), 86 semantik suite/6 yeni test. `run.py --response` ile smoke response'ı eski request'e yeniden bind etme. CLI `--out` mevcut dosyayı değiştirmez. Production IAM/criterion revision/full lineage/native kalite bu fixture kapsamında değildir.

## Same-source tanısı ve yeni paket — T03p/T01h DONE

`python3 -B spikes/semantic-chain/compare_membership.py` aynı dört source üzerinde lexical/saved-model shared span/kind skorlarını üretir; [scope/kanıt](../../docs/quality/same-source-comparison.md). Attribute/domain/native/latency/cost değil; source-only baseline, old raw değişmez.91 suite/5 yeni test. [Yeni8-message paket](../../examples/adversarial-smoke/README.md) no-dispatch5321byte, authored_draft, H4 review ve yeni tek-send izin pending; API/model çağrısı yapılmadı.

## Yeni family gerçek run — T03q/T01i DONE

[MEMBERSHIP-003](../../docs/quality/membership-003-result.md): tek yeni onaylı UI send,6 draft aday/2scope-no-candidate; H4 partial review, raw değişmedi.93 semantic test, iki yeni raw/guard regression. Whole-batch ikiAnswerRecord güvenli bloke; ayrı response-subset tanısı current/stale ayrımını no-mutation gösterir, production reconcile değil. R22 için [ayrı read-only collector](../../docs/quality/proposal-collection.md) tamamlandı; yeni canlı izin tüketildi.


## Çoklu cevap koleksiyonu — T03r DONE

`python3 -B spikes/semantic-chain/collect_membership.py [--out NEWPATH]`: MEMBERSHIP-003 tam response'ları `bridge.collect_proposals(chain,request,response_text,project_id)` ile ayrı source-bound adaylara ayırır; raw/request değişmez. Old revision stale, current ayrı onay önerisi, bağsız B clarification; conflict/duplicate/agent/foreign/no-context ayrı.102 suite/9 yeni test, model/selection0; eski `propose` tek-cevap sözleşmesi korunur. [Sözleşme, kanıt ve sınırlar](../../docs/quality/proposal-collection.md). Her fixture tek pending question; production multiquestion DB/IAM veya kalıcı reconciliation değil. Sırada kayıtlı bilgiyle devam paketi/dosya baseline'ı; native gerçek host ayrı erişim ister.


## Resume ve eşit bilgiyle dosya — T03s DONE

`python3 -B spikes/semantic-chain/compare_resume.py [--out NEWPATH] [--export-dir NEWDIR]`: deterministic resume/source/state exports, ayrı read-access fixture ve fresh source/state/access bağları. [Altı örnek](../../examples/resume-smoke/README.md)/[110 test,8 yeni ve rapor](../../docs/quality/resume-file-comparison.md). Her iki JSON aynı core/checklist; source-only farklı capability. Byte ölçümü token tasarrufu veya receiving-model başarısı değildir; model/selection/paidAPI0. Sırada duplicate context azaltımı; yeni canlı test ayrı onay gerektirir.


## Kayıpsız resume + readable view — T03t DONE

`python3 -B spikes/semantic-chain/compare_compact_resume.py [--out NEWPATH] [--export-dir NEWDIR]`: inline source/record table, strict decoder, source/state/access preflight ve exact literal quotes içeren model-visible view. [Örnekler](../../examples/resume-compact-smoke/README.md)/[rapor](../../docs/quality/resume-compaction.md):121 suite/11 yeni, frozen core exact, üç checklist, byte%31,79/%35,20 azaldı. Token/model/ROI değildir; codec'i genel modele çözdürme. Next: bounded receiver request + ayrı evaluator, gerçek send yeni somut onayla.


## Receiver yeni-sohbet hazırlığı — T03u DONE

`python3 -B spikes/semantic-chain/receiver_smoke.py prepare [--out NEWPATH]`; `evaluate --request examples/receiver-smoke/request.json --response FIRST_OUTPUT --expected examples/receiver-smoke/expected.json [--out NEWPATH]`. [Paket](../../examples/receiver-smoke/README.md)/[plan ve134 test/13 yeni](../../docs/quality/receiver-smoke-plan.md). Source-only7950-byte prompt, separate authored oracle, readback/actions/criticalerrors; import unverified/notrealrun, mutation0/model0. Tek-send gerçek model onayı henüz yok; eski izinleri kullanma.


## İlk native receiver output — T03v DONE kayıt scope'u

[RECEIVER-001](../../docs/quality/receiver-001-result.md): tek configuredgpt-6-luna/low native projectless chat, exact7950-byte prompt; firstfullmessage1739byte syntaxvalid/schemainvalidabstention.136suite/2 new guard, no rawrepair/retry/selection/paidAPI. Toolsummary null/false kaybı model syntax hatası sayılmaz; exactactualcaptureread_thread. Token/usage/aşımunknown, sharedquota74→74 zero-consumption değildir; planfullexecutionnotları [burada](../../docs/quality/receiver-execution-notes.md). Next offline strictschema/scope/abstention; yeni send izni yok.

## Receiver yerel schema ve kaynak guard — T03w DONE

[Kurallar ve tekrar üretim](../../docs/quality/receiver-contract.md); `receiver_contract.py` eski frozen evaluator yanında ayrı offline doğrulayıcı. `check_receiver_contract.py` geçerli sentetik review/6 invalid örnek/frozen hash kontrol raporunu tekrar üretir.16 yeni/152 semantik test; model/API0, actual failed run onarılmaz. JSON Schema genel conformance/provider kabulü not_run; sınırlı yerel interpreter ile kaynak bağları ayrı kontrol edilir. Sonraki iş yeni ayrı source-only schema bağlı request hazırlığı; eski izin tüketildi.

## Q14-A bağımsız proje review — T03x DONE

[`project_review.py` ve tekrar üretim](../../docs/quality/project-review.md), global source/identity/access fixture preflight ve ayrı per-project guard; valid diğer proje, technical/missing/abstain/ambiguous sonuçları, atomic-group bekleme ve stable clarification reply association. `check_project_review.py` saved JSON raporunu üretir.20 yeni/172 semantik test; eski raw/whole-output evaluator/proof'lar aynı, yeni model/API/mutation0. Descriptor/report kalıcı Inbox servisi değildir; gerçek UI/IAM/host capture/resume ve kalite gate açık.

## Yeni machine-schema receiver hazırlığı — T03y DONE

[`receiver_next.py` / RECEIVER-002 planı](../../docs/quality/receiver-next-plan.md), yeni identity/wire2/8089-byte source-only prompt; ortak typed machine schema, whole-message projection ve hermetik3file prepare. `check_receiver_next.py` scripted scorer-only kanıtı;20 yeni/192 semantik test. Model0/output0/paidAPI0/izin yok; golden/model/provider/runtime başarı değil. Oldraw/request/prompt/evaluator/proof değişmedi; v1 Q14wrapper ayrı kalır, format/ID rewrite yapılmaz.

## Wire-2 bağımsız proje incelemesi — T03z DONE

[`project_review_next.py` / doğrulama](../../docs/quality/project-review-next.md), aynı wire-2/request kimliği ve source guard ile Q14-A ayrımı; global kimlik/access ret, teknik hata/abstain/missing ve atomic bekleme.14 yeni/206 semantik test; kalite scorer değişmedi, model/API/mutation0. V1 raw/ID/format onarılmaz; context yalnız caller fixture, gerçek IAM/Inbox değil.

## RECEIVER-002 gerçek native run — Q03-R6 tüketildi

[İlk tam çıktı ve tanı](../../docs/quality/receiver-002-result.md): tek Luna/Low turn, wire-2 JSONvalid fakat N01 required next_actions yok/N02 ambiguous soru bağı yanlış; trial invalid_contract, iki proje unreviewed.3 yeni saved-output testi/209 semantik test; raw/manifest/old scorer korunur. Yeni model/API0 (actual trial1; retry0), token/backend unknown. Sonraki yerel iş typed facts readback/action taslağını modelden isteme tekrarını azaltmak; implemented diye sunulmaz.

## Tipli veriden model çağrısız taslak — T03aa DONE

[`typed_review.py` / çalışan kod ve sınırlar](../../docs/quality/typed-review.md); pinned source/context fixture'dan6record readback/action, candidate/source/read-access ve atomic review guard. Generated origin deterministic_selected_typed_records; modelraw/oracle build input değil.13 yeni/222 semantik test ve bağımsız authored kıyas; inference/mutation0, geçmiş failures aynı. CLI --out yeni dosya, overwrite yok. Model extraction/gold/native/production gate değildir.

## Kalıcı inceleme snapshot — T03ab DONE

[`review_store.py` / kod ve sınırlar](../../docs/quality/review-store.md): typed review'ı SQLite'a atomic append, unique ID/retry, restart ve current scope/access kontrolü;12 yeni/234 semantik test. `check_review_store.py` temporary DB örneğini üretir. Pending descriptor kalıcıdır; human reply resolve/production Inbox/IAM/host entegrasyonu değildir. Model/runner/canonical mutation0; eski proof'lar korunur.

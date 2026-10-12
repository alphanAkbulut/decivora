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

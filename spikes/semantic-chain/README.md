# P0 — Semantik çıktı bağlantısı ve deney çalıştırıcısı

**Çalışan kod; ayrı model henüz çağrılmadı.** Python 3.9+ standart kütüphanesi. Yeni dependency, ücretli API, gerçek transcript, global config veya host kurulumu yok. Bu P0 prototipidir; production extractor/MCP/IAM değildir.

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

28 yeni test: source/authority/namespace/span/version/type/schema sınırları, malicious output, abstention, limit, duplicate, stale/ambiguous soru, ayrı receipt, agent approval reddi, idempotency, evaluator missing ve checkpoint fail/incomplete. Production kaynak ACL’si, çok soru/graph modeli, gerçek provider/host ve native kıyas hâlâ ilgili görevlerdedir.

## Neyi bekliyoruz?

Bu kodu yazmak veya kontrollü negatiflerini çalıştırmak insan etiket incelemesini beklemiyordu; tamamlandı. Gerçek semantik output’u üretmek için **hangi model/host, hangi sentetik dosya ve hangi maliyet sınırı** açık. İlk öneri, tek geliştirme request’i S02’yi mevcut tercih edilen LLM hesabında çalıştırıp contract JSON’u import etmek; ayrı ücretli API bağlantısı kurmadan bir çıktı smoke’u. Mevcut hesap limit/token tüketimi yine olabilir. Bu yöntem otomatik background provider entegrasyonu veya adil native karşılaştırması değildir. Sonraki otomatik çağrıda sağlayıcı/config/usage ve bounded toplam bütçe somutlaştırılacak.

Human gold review kalite iddiasını, T03c owner kararı production teknoloji/yatırımı sınırlar. Ekip/cloud/dil/future özellikleri bu P0 kod çalışmasını bekletmez; MVP/full-scope ayrı fazlarında korunur.


## Mevcut asistanın aday taslağı

[12 aday](fixtures/assistant-s02-draft.json), bu konuşmadaki asistanın S02 metinlerinden yazdığı yorum taslağıdır. [Provenance](fixtures/assistant-s02-provenance.json): prior oracle görünür, blind değil, human review pending, automatic model dispatch yok. Parser/bridge import’unu gerçek bir AI taslağıyla sınar; ayrı provider veya extraction kalitesi benchmark’ı diye sunulmaz. `run.py --response spikes/semantic-chain/fixtures/assistant-s02-draft.json` aynı source-bound zinciri bu taslakla çalıştırır. Tüm altı session response’u olmadığı için corpus değerlendirmesi incomplete kalır.


**Seçili gerçek hedef gözlemi:** [GitHub readback kaydı](../../docs/quality/semantic-target-readback.json) mevcut corpus rehberini iki immutable ref’te gerçekten okur. Aynı byte’lar olsa da beklenen ref dışındaki gözlem stale; seçilen ref observed_match. `target.py` ayrıca repo/path/revision/hash ve missing/unknown ayrımını sınar. Gözlemler authenticated connector çağrılarıyla toplandı; Python assessor fetch/auth yapmaz. Dosya eşleşmesi storage kararının uygulandığı veya task DoD’unun geçtiği değildir. Kontrollü chain koşusundaki target hâlâ fixture’dır; iki kanıtı karıştırma.

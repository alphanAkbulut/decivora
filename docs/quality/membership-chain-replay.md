# Gerçek kayıtlı aday → kontrollü karar/etki/kanıt zinciri

**2026-10-12 · T03o DONE · P0.** MEMBERSHIP-002'nin ilk ham model çıktısı, kendi iki source/request kimliğiyle mevcut bridge/graph/observer/SQLite modüllerine bağlandı. Yeni model, API veya dış hedef çağrısı yok. Bu teslim eski scripted model response zincirinden farklıdır: extraction gerçekten daha önce alınmış model çıktısıdır; insan onayı, hedef ref'i ve verifier sonuçları ise ayrı authored test fixture'larıdır.

[Makine sonucu ve hash'ler](membership-chain-replay-results.json) · [ilk model run'ı](membership-002-result.md) · [kod](../../spikes/semantic-chain/replay_membership.py) · [ayrı fixture makbuzları](../../spikes/semantic-chain/fixtures/membership-chain-scenario.json) · [önceden yazılmış 13 beklenen kontrol](../../spikes/semantic-chain/fixtures/membership-chain-checkpoints.json).

## Ne tamamlandı?

| Kontrol | Gözlenen sonuç |
|---|---|
| 1 · Öneri | Q_STORE/B/revision 1 bağlandı; karar D_MARKDOWN/revision2, mutation0 |
| 2 · Yetkisiz seçim | authenticated=false fixture makbuzu reddedildi; mutation0 |
| 3 · Ayrı seçim | Kaynaktan/modelden üretilmeyen makbuz D_SQLITE seçimini uyguladı; bütün task'lar hâlâ todo |
| 4 · Aynı seçimin tekrarı | Aynı event döndü; ikinci event/mutation yok |
| 5 · Ayrı impact | Sync obsolete, export retained, combined review, watch review; source seçimi otomatik task kapatmadı |
| 6 · Reported evidence | Upload claim ve rollback Evidence aday olarak kaldı; observation yok, kabul evidence boş, verified=false |
| 7 · Eski hedef | Gerçek temporary eski içerik okundu; fixture old-ref nedeniyle stale, verified=false |
| 8 · Yanlış içerik | Güncel fixture ref'i olsa bile eski içerik hash'i mismatch, verified=false |
| 9 · Güncel hedef | Yeni temporary içerik hash'i observed_match; yine verified=false |
| 10 · Kısmi AC | Ayrı verifier fixture rollback'i passed yaptı; migration eksik, verified=false |
| 11 · Tam AC | Ayrı verifier fixture migration'ı da passed yaptı; controlled verified=true |
| 12 · Restore | SQLite backup ayrı bağlantıyla açıldı; event sayısı10 ve projection hash'i eşleşti; dış dispatch0 |
| 13 · Belirsiz cevap | Ayrı release fixture'ında A adayı korundu; soru pending ve mutation0; soru tahmin edilmedi |

AND/OR/unknown etki preview'u: sync/combined obsolete_candidate, export retained, watch review_unknown. Son durumlar ayrı, snapshot digest'e bağlı fixture impact onayının sonucudur. Preview önerisi ile uygulanmış task durumu aynı şey değildir. D_SQLITE kimliği source context ile aynen korundu; eski run.py'nin farklı request_id'sine veya lowercase karara sessiz rebind yapılmadı.

Temporary hedef üç kez bounded/no-follow observer ile gerçekten okundu: mismatch, mismatch, observed_match. Git ref/revision metadata fixture'dır; bu bir GitHub yüklemesi veya gerçek migration çalıştırması değildir. Claim/Evidence'ı otomatik verify komutuna çevirmedik. Seçim makbuzunu model proposal'ından kopyalayıp kendi kendine onay üretmedik; bağımsız dosyadan aldık.

## Tekrar çalıştır

```sh
python3 -B spikes/semantic-chain/replay_membership.py
python3 -B spikes/semantic-chain/replay_membership.py --out /tmp/membership-chain-replay.json
python3 -B -m unittest discover -s spikes/semantic-chain -p test_replay_membership.py -v
```

No network/provider call. Yalnız temporary klasör ve SQLite/dosya fixture'ları; otomatik temizlenir. `--out` mevcut dosyanın üzerine yazmaz. Ham ilk çıktı byte hash'i, request/context/typed contract kontrolünden önce sabitlenir; v1 veya newline eklenmiş v2 sessizce onarılmaz. Beklentiler replay'den önce authored olarak yazıldı, gerçekleşen state'ten türetilmedi; insan gold değildir. CLI checkpoint failed/incomplete ise başarısız çıkış verir.

**Doğrulama:** 6 yeni anlamlı regresyon testi, toplam86 semantik; ayrıca15 decision ve40 root test passed. Negatifler: farklı request/project/soru seçenekleri, değiştirilmiş raw/v1, source/revision/yetki bağını kaybetmiş selection receipt, yetkisiz impact, yeni gerekçe sonrası stale base/digest ve eksik expectations. Model, selection, task impact, hedef match ve task verified kanıtları ayrıdır. Geçerli local match hiçbir observer çıktısında task_verified/remote_upload_verified yapmadı.

## Üretim için kalanlar ve sınırlar

| Boşluk | Bu test neyi kanıtlamaz? | Mevcut iş |
|---|---|---|
| Gerçek yetki | Fixture authenticated/role dict production kimliği/grant/receipt değildir | T05/T08/T13 |
| Karar geçmişi | Fixture event schema tam source/receipt/decision revision lineage'ını taşımaz; raporda kimlikler var | T06/T07/T22 |
| AC revision binding | Chain.verify artifact revision'ı kontrol eder; criterion revision'ını ayrı saklamaz/doğrulamaz | T14/T15 |
| Çok soru/çok proje | Bir soru / ayrı SQLite fixture; aynı projede concurrent pending-question engine ve tenant IAM değil | T10/T13/T26 |
| Gerçek hedef | Temporary dosya gerçek okunur; ref metadata ve içerik authored fixture, remote uygulama kanıtı yok | T14/T27 |
| Kalite/ekonomi | Aynı dört development mesajı ve mevcut output; blind holdout, insan gold, latency/cost/native üstünlük yok | T01/T03b/T03c |

Bu boşluklar yeni kabul veya mimari kararı değildir; mevcut production görevlerine göre P0 kapsam sınırını görünür kılar. Eski experiment event projector'ı üretim servisi gibi genişletilmedi. Tam ürün/MVP kapsamı korunur; ana T03 veya T04 bu teslimle kapanmaz/başlamaz.

## Sıradaki zorunlu iş

Yeni soru aileleri ve exact label review ile semantik ölçümü genişletmek; aynı bilgiyle devam-paketi/basit-dosya/native kıyasını yürütmek. Native/model test için ayrıca somut paylaşım/çağrı sınırı gerekir; önceki tek-send izni tüketildi, ücretli API kapalı. Fixture kodu/ölçüm hazırlığı API bakiyesine bağlı değil. Production yatırım kararı T03c'de açık kalır.

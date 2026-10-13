# Kalıcı geç cevap fixture'ı

Sentetik transport örneği; gerçek kullanıcının kararı veya verified identity değildir. [Kaynak request](../receiver-next-smoke/request.json) ve [caller context](../receiver-next-smoke/review-context.fixture.json) değişmez. CID metadata'sı source-bound typed review'dan gelir; Q_UI/revision1/B seçimi bu ayrı sentetik cevap için açık yazılmıştır, model/oracle çıktısından çıkarılmadı.

[`reply.fixture.json`](reply.fixture.json) source message/revision/text/actor hash'i, project/CID ve explicit question/revision/option içerir. Actor `human_owner` yalnız fixture alanıdır. [Kod/kanıt](../../docs/quality/reply-store.md), tek receipt, restart ve çelişkili ikinci cevabın ayrı source olarak korunmasını gösterir. Cevap kaydetme approval veya execution değildir; model/network çağrısı yapmaz.

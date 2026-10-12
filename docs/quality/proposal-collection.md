# Çoklu cevap öneri koleksiyonu — PROPOSAL-COLLECTION-001

**2026-10-12 · T03r scoped DONE / P0.** Aynı mesaj grubundaki birden fazla cevabı kaynaklarıyla ayrı değerlendiren çalışan kod. Yeni model çağrısı, karar uygulaması veya ücretli API yok. [Kayıtlı model çıktısı](model-runs/membership-003-response.txt) ve önceki [MEMBERSHIP-003 ölçümü](membership-003-result.md) değiştirilmedi. [Tekrar üretilebilir sonuç](proposal-collection-results.json).

## Sorun ve çözüm

Eski `propose` fonksiyonu tek AnswerRecord bekliyordu; aynı response'ta iki cevap olduğunda güvenli şekilde duruyordu. Bu model extraction hatası değildi. Yeni `collect_proposals` response'un tamamını önce doğrular, sonra her cevabın kaynak mesajı, sorusu ve presentation revision'ını mevcut fixture sorusuyla karşılaştırır. Eski `propose` davranışı mevcut çağıranlar ve tarihsel kanıtlar için korunur.

Kaynak grubu burada **birlikte incelenen mesajlar** demektir; zip veya uygulama paketi değil. Collector ham metni yeniden çıkarmaz, yeni soru tahmin etmez, cevabı kendiliğinden onaylamaz.

| Kaynak / fixture current soru | Yeni koleksiyon sonucu | Karar uygulanır mı? |
|---|---|---|
| N01-m01: Q_STORE revision1/B; current2 | `stale_question_revision` — eski cevap kaynağı korunur | Hayır |
| N01-m02: Q_STORE revision2/A; current2 | `pending_trusted_selection` — ayrı onay önerisi | Hayır |
| N02-m01: Q_UI revision1/B; current1 | `pending_trusted_selection` — ayrı onay önerisi | Hayır |
| N02-m04: bağsız B | `needs_clarification` — soru tahmin edilmez | Hayır |
| N02 upload claim ve not_run evidence | `preserved_records` içinde aynen kalır; bu collector seçim yapmaz | Hayır |

Dört cevap adayı ayrı değerlendirilir; diğer iki bilgi kaydı da korunur. İki fixture'ın projection'ı değişmez ve soruları pending kalır. Bu rapor eski cevabı kalıcı production event store'a yazmaz; kaynak ve raporda saklar. Kalıcı çok-soru reconciliation T10/T13 kapsamındadır.

## Güvenlik ve uygulama sözleşmesi

- `collect_proposals(chain, request, response_text, project_id)` read-only çalışır. Caller'ın açık proje alanı request ile eşleşmelidir; bu fixture scope kontrolü production ACL değildir. Chain'in kendi project namespace alanı yoktur; doğru fixture'ı seçmek caller'ın sorumluluğudur.
- Önce tüm envelope/source/quote/attribute validation; tek bozuk kayıt bütün response'u reddeder. Geçerli parçayı gizlice seçerek hatalı response'u başarılı göstermez.
- Her kayıt tam kaynak/span/attributes/provisional entity_key ile korunur. `candidate_id`, request/source/message/span/kind/attributes hash'idir; modelin entity_key tahminine bağlı değildir. Bu ID request/context değiştiğinde değişir; kalıcı global entity kimliği değildir.
- Eski revision güncele taşınmaz. Daha yeni revision veya başka soru `needs_question_context`, eksik association/geçersiz option `needs_clarification`, pending soru yoksa `no_pending_question` olur. Zaman sırası tek başına doğruluk sağlamaz.
- Aynı current soruda farklı human seçenekleri `conflicting_answers`: hiçbir seçim önerisi hazırlanmaz. Liste sırası ters çevrildiğinde sonuç değişmez; “son cevap kazanır” yoktur.
- Aynı kaynak/span/attributes için farklı provisional key verilirse kayıtlar korunur ve `duplicate_candidate` olarak bloke edilir. Exact duplicate mevcut validator tarafından reddedilir. Ayrı mesajlardaki aynı cevap ayrı kaynaktır; birinin uygulanması diğerinin eski base revision'ını geçersiz kılar.
- Human_owner olmayan kaynak `non_human_answer`; agent sözü onay yerine geçmez. Human kaynak türü de tek başına yetki değildir.
- Uygulanabilir öneri, ayrı `apply_selection` yolunda source/message/question/option/base bağlı güvenilir fixture receipt ister. Collector bu yolu çağırmaz; impact ve verification da çağırmaz. Aynı receipt retry idempotent, ikinci farklı/stale seçim ret olur.
- `needs_context` abstention ile `no_answer_candidates` ayrıdır; boş cevap listesi soru çözüldü veya task tamamlandı demek değildir.

Bu durum adları **P0 tanı çıktılarıdır**; production domain enum/UX onayı veya auth altyapısı olarak kabul edilmez. Tüm response kaydı saklandığından non-answer bilgiler sessizce atılmaz.

## Doğrulama ve sınırlar

**102 semantik test geçti; 9 yeni collector testi** eski/current/ambiguous, conflicting/reversed order, provisional alias/exact duplicate, future/foreign question/agent, invalid source/quote/project/model authority, abstain/no-answer/no-pending, ayrı receipt/idempotency, aynı seçenek/farklı mesaj/stale base ve gerçek kayıtlı raw replay kapsamını doğruladı. Beklenen durumlar bağımsız authored test assertions'dır; insan gold veya yeni model kalite ölçümü değildir.

```sh
python3 -B spikes/semantic-chain/collect_membership.py
python3 -B spikes/semantic-chain/collect_membership.py --out /tmp/decivora-proposals-new.json
python3 -B -m unittest discover -s spikes/semantic-chain -p test_proposal_collection.py -v
```

CLI yalnız mevcut synthetic request ve değişmez ilk model çıktısını okur; ayrı geçici SQLite fixture'ları temizler. `--out` mevcut dosyayı değiştirmez. Source/model çıktı hashleri raporda; yeni inference/selection/model/API sayıları 0.

**Kalan sınırlar:** Single-current-question fixture; birçok pending soru, birden fazla response arasındaki conflict çözümü, production IAM/kalıcı reconciliation, criterion revision, source/receipt lineage, target adapter ve native/resume ürün faydası ölçümü bu teslimle kapanmaz. R22'nin gözlenen bütün-grup bloklaması yeni P0 collector yolunda giderildi; eski single-answer API korunur. Yeni live model izni yoktur.

**Sıradaki bağımsız iş:** Aynı kayıtlı bilgiyle kaynak bağlı devam paketi ve basit dosya baseline'ını hazırlayıp yanlış karar/false done/eksik bağlam kontrollerini karşılaştırmak. Native host deneyi ve yeni model çağrısı ayrı gerçek erişim/izin ister. T03c yatırım/production stack ve T04 açık kalır.

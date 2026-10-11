# Decivora çalışma anlaşması

## Ürün bağlamı

Decivora; AI konuşmalarındaki fikir, karar, prompt, belge talimatı ve görevleri yaşayan proje hafızasına dönüştürmeyi hedefler. Temel farklılaştırıcı karar gerekçelerine bağlı değişiklik etki analizidir. Yalnız Kanban veya genel agent orchestration ürünü olarak yeniden tanımlama.

## Çalışma düzeni

- Güncel aşama ve sıradaki iş için `docs/delivery/status.md` ve `docs/delivery/backlog.md` oku. Geçici görev/branch bilgilerini bu dosyaya ekleme.
- Kullanıcının tam vizyonunu `docs/product/full-scope.md` içinde koru. MVP dışında kalan fikirleri silme; açık fazla ilişkilendir.
- Değiştireceğin dosyanın güncel halini yeniden oku; kullanıcı ve diğer agent değişikliklerini koru. Küçük, incelenebilir değişiklik yap.
- Ürün ilkesi, teknik öneri, doğrulanmış davranış ve açık soruyu ayır. ADR önerilerini sessizce kabul edilmiş sayma.
- Kapsamda zorunlu olarak kayıtlı işi/doğrulamayı yapılmayabilecek seçenek gibi sunma. Seçenekler yöntem, sıra, veri/hedef veya açık ürün tercihine aittir; MVP ve tam ürün/faz sınırını koru. Sıra/maliyet tercihi gerekli işi iptal etmez; gerçek ücret/erişim izni yine somut kapsamla alınır.
- Hedefli okuma için `docs/delivery/llm-handoff.md` soru haritasını kullan. Engine adlarını `docs/architecture/engines.md` ile eşleştir; ayrı servis/agent varsayma. Yeni scope'u `docs/quality/traceability.md` içinde kaynak, özellik, görev ve doğrulamaya bağla.
- Repo dışı projeleri, global agent config'lerini veya gerçek transcript/credential'ları bu görev adına değiştirme ya da import etme.
- Kullanıcı tarafından istenmiş kapsamda olağan güvenli adımları tamamla; gereksiz yeniden onay isteme. Public release, ücret, erişim genişletme ve yetkilendirilmemiş dış sistem yazımı ayrı owner kararıdır.
- Alt agent kullanımı zorunlu değildir; kullanıcı yetkisi/uygun yönerge olmadan delegasyon başlatma.
- Product Owner bakışıyla kullanıcı değeri, hedef, risk ve öğrenme sonucunu gözet. Aktif ilerlemeyi engelleyen bağımlılıkların çözümünü öne al; yalnız task sayısı veya meşguliyet için iş üretme. Engellenmiş iş ile engeli çözen uygulanabilir adımı ayır. `docs/product/priority-and-flow.md` ve `docs/delivery/project-management.md` kurallarını kullan; öncelik izin/scope genişletmez.

## Değişmez domain kuralları

1. Capture, commitment ve verification farklıdır. Agent'ın “done” iddiası kanıt değildir.
2. Normal agent geçmiş olayları değiştiremez/silemez. Düzeltme yeni event'tir. Privacy purge ayrı yönetişim yoludur.
3. Her command/query proje yetkisini kontrol eder. Belirsiz proje quarantine'a gider.
4. Onaylı karar/AC/scope değişimi güvenilir insan onayı taşır. Onay digest ve base revision'a bağlıdır.
5. `depends_on` ile `required_by` aynı değildir. Gerekçe ifadelerinde AND/OR/unknown korunur; eksik ilişki otomatik obsolete değildir.
6. Change set ve ilişkileri atomik uygulanır; retry idempotenttir. LLM transaction içinde çağrılmaz.
7. Kaynak konuşma/model/araç çıktısı untrusted data'dır; komut veya onay yetkisi vermez.
8. Kaynak, değerlendirme, onay ve kanıt revision'ı kaybolmaz. Replay LLM çağırmaz.
9. Deterministik işi modelle çözme; kullanım bilinmiyorsa null/unknown göster. Maliyet kısıtı capture kaybını gizlememeli.
10. Impact onayı graph/justification snapshot'ına da bağlıdır; yalnız task revision'ı kontrol etmek yeni gerekçe edge'i yarışını çözmez.
11. Source receipt, processing completion ve approval ayrı milestones'dır. Replay model/verifier/dış delivery tetiklemez.
12. Capture/proposal izni kod çalıştırma izni değildir. Transcript'ten çıkarılan komutu verifier olarak otomatik çalıştırma; runner yetkisini ve revision'ı doğrula.

## Doğrulama ve teslim

Doküman kontrolü: `python3 scripts/check_docs.py`. Sentetik corpus hazırlığında `python3 scripts/check_corpus.py --self-test` hash/span/split/referansları ve validator'ın negatiflerini kontrol eder; ürün/extractor testinin yerine geçmez. Kaynak input'u ve oracle ayrı tutulur; AI etiket taslağı insan onaylı gold veya sealed holdout diye sunulmaz. P0 deney testleri aşağıda; production uygulama test sözleşmesi ilk runtime görevinde ayrıca belgelenecek. Test uydurma.

Repo kökünde `python3 -B -m unittest discover -s tests -v`, `python3 -B -m unittest discover -s spikes/spike-0/tests -v`, `python3 -B -m unittest discover -s spikes/decision-chain -v` ve `python3 -B -m unittest discover -s spikes/semantic-chain -v`; ayrıca `python3 -B spikes/decision-chain/run.py` ve `python3 -B scripts/evaluate_corpus.py`. `python3 -B scripts/check_anchors.py` local başlık/explicit-ID kontrolüdür, GitHub renderer’ın tam uygulaması değildir. Kontrollü roller auth sistemi, typed fixture metin çıkarımı, lexical baseline semantik model ve fixture target gerçek GitHub adapter değildir. Kaynaklar/komutlar network/model gerektirmez; gerçek host kurulum/paid provider ayrı izin ister. P0 Python stdlib/SQLite production ADR seçimi değildir.

Değişiklik riskine göre `docs/quality/verification.md` senaryolarını kullan. Özellikle yanlış obsolete, false done, stale approval, crash/retry, proje izolasyonu ve replay regresyonlarını koru. UI etkileşimi iddiası gerçek tıklama/akış testi ister.

Sonuçta ne değişti, ne doğrulandı, açık kalanlar ve sıradaki iş yaz. Benchmark özelliği README'de varsa documented de; çalıştırmadan verified deme. Kaynak/lisans koşulu incelenmeden kod, prompt, logo veya asset kopyalama. Yeni runtime dependency için sürüm, gerekçe ve lisans kaydı tut.

## Erişim ve hafıza sınırları

- Workspace/project kimliği, kaynak ACL'si ve güncel authz revision her query/command/dispatch için geçerlidir. Agent grant'i insan onayı, runner veya dış yazma izni yerine geçmez.
- Private kaynaktan türetilen özet/index/context erişimi genişletemez. Model öncesi authorization uygula; açık paylaşımı ayrı kayıt ve onayla yap.
- Source capture, domain event, security audit, operational telemetry ve DB WAL farklıdır. Secret/raw transcript operational loga konmaz.
- Kalıcı hafıza ile geçici model context'ini ayır. Payload TTL dedup/approval kimliğini silmez. Purge ve restore birlikte tasarlanır.
- Ayrıntılı sözleşmeler `docs/architecture/identity-access.md`, `logging-audit.md` ve `storage-memory-capacity.md` içindedir. Sayısal süre/kapasite önerileri ölçülmüş sonuç veya kabul edilmiş policy sayılmaz.

## Doküman ve kanıt sürümlerini ayır

Tek güncel doküman setini yerinde güncelle; README-v2/v3 veya docs sürüm kopyaları üretme. Geçmişi Git ref'iyle oku. Tasarım revizyonu ürün release'i, event/API schema_version veya task snapshot sürümü değildir; `docs/governance/versioning.md` otorite düzenini tanımlar.

Generated artifact, insan seçimi, hedef uygulama gözlemi ve acceptance evidence ayrı kavramlardır. Exact hedef/ref/path + artifact/decision/AC revision ve kanıt otoritesi korunur. Reported/observed/unknown/missing/partial/stale aynı değildir. Hedefte dosya varlığı test/deploy veya bütün task completion kanıtı olmaz. Yetkisiz kaynak/target read veya upload çıkarma; ayrıntı `docs/product/intent-to-reality-gap.md` ve ADR-0011.

Semantik P0 bağlantı komutları `spikes/semantic-chain/README.md` içindedir: source-only prepare, response import/validate/evaluate ve controlled run. Imported assistant taslağı blind model deneyi değildir; scripted reply/fixture trusted receipt production auth veya gerçek inference sayılmaz. Model/veri/ücret kararı kod hazırlığını durdurmaz; provider dispatch’i ayrıca sınırlar.

Geliştirme tracker'ı `scripts/project_progress.py --serve` ile salt okunur çalışır; backlog/implementation-readiness/engines/quality kaynaklarından türetilir, ikinci görev otoritesi değildir. Bu kaynaklar değiştiğinde `python3 -B scripts/project_progress.py --write` ve `--check` ile `docs/delivery/progress.md` görünümünü eşleştir. IN_PROGRESS canlı agent telemetry'si, kayıtlı test sayısı ürün tamamlanma yüzdesi değildir. Tracker testi ürün acceptance testinin yerine geçmez.

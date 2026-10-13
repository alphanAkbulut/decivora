# T05f — Çalışan proje ve session binding çekirdeği

**Uygulandı, kontrollü memory-only dilim. T05 ana görevi IN_PROGRESS.** [Kod](../../packages/domain/project_binding.py) · [CLI demo](../../apps/hub/binding_demo.py) · [Testler](../../tests/runtime/test_project_binding.py) · [Sonuç/hash kaydı](project-binding-core-results.json).

```sh
python3.12 -B -m apps.hub binding-demo
python3.12 -B -m unittest discover -s tests/runtime -v
```

| Kabul edilen davranış | Çalışan kontrol |
|---|---|
| Aynı ad iki proje olabilir | Opaque değişmeyen ID; ad Unicode korunur, kimlik lookup'ı değildir |
| Scope query ve write için ayrı | Trusted caller'ın immutable readable/writable project setleri; workspace kontrolü; mevcut/olmayan yabancı ID aynı forbidden |
| Açık binding | Provider/account/session/source epoch birleşik key, revision ve bound_by; source text yetki veya proje seçimi değildir |
| Rebind geçmişi taşımaz | Append-only in-memory binding tuple; source açık eski revision ile eski projeye çözülür; yeni revision/eski proje mismatch quarantine |
| Belirsiz veya eski komut | Eksik/unknown revision ve unbound/session/project mismatch quarantine; stale mutation reddi, mevcut durum korunur |
| Project update/archive | Base revision kontrolü; ID değişmez; archive delete değildir, yeni binding/işleme engellenir |

11 yeni test passed; toplam runtime23. CLI demo iki sentetik projede gerçekten çalışır; p1 geçmişi korunur, yeni kaynak p2'ye çözülür, p1-reader'ın p2 query'si forbidden olur. Input `actor_type=human` veya metindeki talimatlar grant sağlamaz. Scope/grant testi ürün kimlik doğrulaması veya kişisel kaynak ACL implementasyonu değildir.

Quarantined sonucu **kalıcı quarantine kaydı değildir**; şu an write yok. Registry tek caller/tek process belleğinde çalışır; restart sonrası state yok. Caller scope'u üretirken güvenilir kimlik/aktüel authz revision sağlamalıdır; bu dilim source JSON'dan scope parse etmez. Yerel demo scope'ları hardcoded sentetik fixture'dır. Rebind her iki proje için write izni ister; binding history query tüm geçmiş projeler için read kontrol eder. History gizli projeleri filtreleyip tam gibi göstermez.

**Sonraki teslim:** [T05g kalıcı store](project-store.md) restart/idempotency/rollback kısmını uyguladı; bu T05f raporu memory-only kabul tarihçesini korur. **T05 kapanışı için kalan:** Power-loss/recovery sınırları; grant/authz revision yaşam döngüsü; ingress'in binding revision'ı alımda güvenilir biçimde pinlemesi ve durably quarantining yolu. Historical binding replay eski projeye bakar; current consent/authorization kontrolünü atlama izni değildir. Gerçek login, connector/agent token, network endpoint ve insan onayı ayrı teslimlere bağlıdır. Yeni model/API/dış kaynak çağrısı yapılmadı.

Bu dilim mevcut mimari kararlarını değiştirmez; Mermaid topoloji aynı. T04 tarihsel kabul hashleri korunur; güncel değişen runtime dosyaları bu rapordadır. Tam AC-01/MVP kabulü iddia edilmez.

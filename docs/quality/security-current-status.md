# Güncel güvenlik durumu ve geliştirme kapıları

**14Ekim2026 — doküman/kod eşleştirmesi; kapsamlı güvenlik scan/pentest yapılmadı.** Eski mimari başlıklar bütün alanı uygulanmadı gibi anlatıyordu; yerel implementasyon ile tam tasarım artık ayrıdır. Bu kayıt yeni risk kabulü, kapsam istisnası, grant, dış bağlantı, paid dispatch veya public deployment izni değildir.

## Uygulanan yerel kontroller ve kanıt sınırı

| Alan | Kod / kontrol | Mevcut kanıt | Tamamlanmamış sınır |
|---|---|---|---|
| HTTP | [local server](../../apps/local_ui/server.py):127.0.0.1, random bootstrap/session/CSRF, tam Host/Origin, HttpOnly/SameSite cookie, allowlisted static routes, CSP/nosniff/no-referrer | [HTTP negatif/regresyonlar](../../tests/runtime/test_local_app.py), [yerel önizleme](local-preview.md) | Yerel owner oturumu multiuser login değildir; TLS/SSO/session lifecycle veya tam read/connection/deadline savunması yok |
| Yetki | [Local authority](../../packages/storage/local_authority.py), [workspace transaction](../../packages/storage/workspace.py): persisted grant/current revision, owner-only grant, scope/revocation ve scoped project request | [Yerel authority](local-authority.md), [kritik kontrol düzeltmeleri](core-critical-review.md), [güncel API-free kayıt](api-independent-results.json) | Tam rol/davet/offboarding, kaynak paylaşım editörü ve remote identity yok |
| MCP / özel türevler | [stdio server](../../packages/mcp/server.py): pre-provisioned agent,5bounded tools, scope/snapshot cursor; private-source türev/bağlı context fail-closed withholding | [MCP negatifleri](../../tests/runtime/test_mcp_local.py), [protocol sınırları](../architecture/local-mcp.md) | Gerçek host interop/aktivasyon, ince paylaşım policy'si ve tam delta/resync doğrulanmadı |
| İnsan onayı / completion | Plan actor/digest/data/authz revision; atomik approve/apply/audit; agent proof iddiası untrusted; AC/DoD/finish/context güncelliği | [Workflow negatifleri](../../tests/runtime/test_task_workflow.py), [agent önerileri](../../tests/runtime/test_agent_proposals.py), [API-free rapor](../delivery/api-independent-development.md) | Semantik doğruluk, gerçek provider/target/runner ve bütün release senaryoları değil |
| Dosya hedefi | [POSIX observer](../../packages/verification/files.py): opt-in root/path/hash/criterion, no-follow/root identity, regular file ve1MiB/16read-snapshot sınırı | [Dosya negatifleri](../../tests/runtime/test_file_verification.py), [fixture zinciri](../../tests/runtime/test_api_free_chain.py) | Kullanıcı kökü etkin değil; Windows/general executor/test/deploy runner yok |
| Limit/bütçe | HTTP32KiB/30write-minute; MCP32KiB request/16KiB output/60tool-minute-process; finite source/query/graph/evidence; shared run reservation ve unknown settlement | [Routing](../../tests/runtime/test_work_routing.py), [MCP limiter](../../tests/runtime/test_mcp_local.py), [karışık yük](mixed-load.md) | Sayaçlar tüm HTTP okuma/bağlantı/hesap veya distributed abuse/cost koruması değildir; dış üyelik tüketimi bilinmiyor |
| Audit/log | Canonical mutation+required audit aynı transaction; API history append-only; session-only25safe error records; raw operational request log kapalı | [Atomiklik ve recovery kontrolleri](core-critical-review.md), [HTTP sağlık testi](../../tests/runtime/test_local_app.py) | Persistent redacted incident/alert/retention ve tam security-event kapsamı yok; fiziksel OS/DB erişimine karşı tamper-proof değil |
| Yedek/veri | Yeni DB0600, private directory; izinli whole-workspace snapshot/temporary restore-validation,8MiB DB/64KiB manifest; current source access recheck | [Local backup](../../packages/storage/local_backup.py), [HTTP backup testleri](../../tests/runtime/test_local_app.py) | Şifreleme, redakte public export, tam privacy purge/retention/recovery/active restore açık. Önceki canlıDBdelete kontrolünden sonra yetkili503düzeltmesi LocalAppstartupWALuyguladı; restart read-onlywal doğrulandı |

309runtime testi önceki teslimde geçti; bu sayı bir güvenlik test sayısı veya güvenlik sertifikası değildir. Bu güvenlik dokümanı tesliminde runtime değişmedi; sonraki yetkili [concurrency/impact teslimi](concurrency-impact-delivery.md) runtimeWAL/read optimization ve hypothesisUIekledi. Yeni grant/policyyetkisi açılmadı. Tarihsel QA belgelerinin eski task statüleri kendi teslim tarihine aittir; bugünkü task authority backlog/closure manifestidir.

## Açık bulgular ve hangi aşamada yapılacaklar

| Kapı / mevcut iş | Gerekli geliştirme / doğrulama | Zaman / karar ihtiyacı |
|---|---|---|
| T15/T23d | Karışık yükteki önceki HTTP503reproducer, safe exception/correlation, lock/context/read-write yarışının teşhisi; kayıp mutation/başarılı receipt iddiası olmamalı | Şimdi teknik bağımsız iş; kök neden henüz unknown. Güvenlik vulnerability/severity doğrulanmış değil |
| T04/T08/T23 | HTTP read/concurrency/slow-body/deadline ve resource abuse; secret/redaction, malformed/duplicate/oversize girdiler; fail-closed transport ve güvenli shutdown | İlk gerçek entegrasyon/yerel release öncesi; sayısal üretim eşikleri ölçümle, tam scope önizlemesiyle |
| T09/T21 | Credential/secret-store ve provider auth/egress allowlist; prompt injection'ın veri/komut sınırı; timeout/retry/unknown usage ve ortak bütçe | İlk onaylı model/CLI/provider kullanımı öncesi; somut veri/model/erişim/harcama izni ayrı |
| T18b/T23c | Private→shared önizleme/current audience; retention/erase/encryption/tombstone ve restore sonrası güncel consent | Gerçek özel veri/paylaşım öncesi; OPEN-08 ve paylaşım policy'si owner kararı |
| T14 | İzole test runner/çalıştırma izni, recipe, çevre/secret/CPU/zaman/artifact coverage ve redaction | Gerçek kod çalıştırma öncesi; capture/file-read grant execution izni değildir |
| T23/T24 | Crash/restore/purge/disk/load ve revoke negatifleri; dependency/credential/artifact taraması; security review | Release öncesi; henüz kapsamlı bağımsız audit yok |
| T30/C01–C06 | Gerçek login, ayrı agent token, role/invitation/offboarding, tenant isolation, TLS/secret/backup işletimi ve distributed quotas | Ekip/cloud/public exposure öncesi; ürün/kurulum/işletim kararı gerekli |

Eksik implementasyon API-blocked veya kullanıcı onayı bekleyen iş olarak otomatik etiketlenmez. Bağımsız teknik çalışma devam eder; gerçek erişim/ücret/public exposure/purge gibi işlemler somut yetkileriyle açılır. Yeni açık iş üretmeden mevcut owner/first-use gate kullanılır.

## Kök SECURITY.md durumu

14Ekim2026 · Kullanıcı tam diff ile sunulan taslağı ‘Taslağı SECURITY.md olarak uygula’ yanıtıyla onayladı. [Kök SECURITY.md](../../SECURITY.md) onaylanan içerikle birebir uygulandı; repository ve alt dizinleri için güvenlik review bağlamıdır. Yeni accepted-risk veya bulgu istisnası getirilmedi; özel raporlama kanalı/SLA/bug bounty veya stable supported version uydurulmadı. Policy dosyasının varlığı güvenlik kontrollerinin tümünün uygulanmış veya bağımsız scan yapılmış olduğu anlamına gelmez.

## Referanslar / doküman kapsamı

[Kimlik ve yetki](../architecture/identity-access.md), [limitler](../architecture/resource-limits-and-abuse.md), [log/audit](../architecture/logging-audit.md), [depolama/hafıza](../architecture/storage-memory-capacity.md), [güncel follow-up kapıları](../delivery/api-independent-development.md). Bu dokümanların Mermaid modelleri tam önerilen sözleşmeyi gösterir; mevcut alt kümenin tamamını uygulandı/test edildi göstermez. Bu güncellemede Mermaid kaynakları değişmedi.

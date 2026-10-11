# Spike-0 kaynak kökeni ve değişiklik sınırı

**2026-10-11 · kullanıcı tarafından sağlanan kod paketi.** `decivora_spike0_v1.zip`: 30 dosya / 91.193 açılmış byte, SHA-256 `a7b4685a94395f2c0b2989079d65e9d764e10008442e2209cb4db5f3d2b2f147`. Spike dizini altındaki 28 dosya içeri alındı; paket kökündeki görev talimatı ve gitignore notu ürün kodu olarak alınmadı.

Kullanıcı cloud local `spike-0-capture-observation`, commit `78d183d`, GitHub push 403 bildirdi. ZIP Git history içermez; tam commit eşleşmesi unknown. Dış run dosyası hash’i `d2515a69978e32f34db1dfdb15127e677c7b0259b629cc48a2a51914c4835c69`; ayrı gönderilen ve ZIP içindeki dosya eşleşti. [Real-run](results/real-run-001.md) aynen korunur; yeni test sonucuyla yeniden yazılmaz.

İlk inceleme [tarihsel raporda](../../docs/quality/spike0-audit.md). Ardından kullanıcı önerileri uygulamayı yetkilendirdi: source namespace/full-content match, durable receipt ve bounded catch-up, kısa cevap/claim/coverage, fuzzy conflict, DB/test kaynak kapanışı ve rapor terminolojisi değiştirildi; 8 regresyon eklendi. [Güncel teslim ve sınırlar](../../docs/quality/audit-remediation.md).

Bu aktarım OSS dependency alımı veya başka benchmark projesinden kod kopyalama değildir. Kullanıcı kodu kaynağına dair yazar/rights araştırması yapılmış değildir; public dağıtım lisansı verilmedi. Private repo ve [lisans karar kapısı](../../docs/governance/licensing.md) korunur. Gerçek transcript/credential ve kişisel config alınmadı. Deney sırasında gerçek projeye kurulum yapılmadı.

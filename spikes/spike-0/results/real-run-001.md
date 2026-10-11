# Gerçek çalıştırma gözlemi 001 (n=1)

**Tür:** spike gözlemi. MVP kanıtı, capture "çalışıyor" hükmü veya T02 sonucu **değildir**.
**Tarih:** 2026-10-10 · **Commit:** fb0d983 (+ spike çalışma ağacı) · **Ortam:** Linux, Python 3.13, Claude Code 2.1.296 (bulut sandbox)
**Yöntem:** Boş bir sandbox klasörüne `spike install` ile hook kuruldu; `claude -p "<tek cümlelik prompt>"` ile **etkileşimsiz** tek oturum çalıştırıldı. Gerçek proje, gerçek veri veya harici API (spike tarafında) kullanılmadı. Kurulum sonunda `spike uninstall` çalıştırıldı.

## Gözlenenler (yalnız bu çalıştırma)

| Gözlem | Sonuç |
|---|---|
| Tetiklenen hook'lar | `SessionStart`, `UserPromptSubmit`, `Stop`, `SessionEnd` — 4/4, her biri 1 kez |
| Hook çıkışı | Çıkış kodu 0; stdout boş (model çıktısı yalnız cevabı içeriyordu), `errors.log` boş |
| Payload alanları | `session_id`, `transcript_path`, `cwd`, `hook_event_name` geldi; `UserPromptSubmit`/`Stop`/`SessionEnd`'de `prompt_id` vardı; `SessionStart`'ta `source=startup` |
| Transkript yolu | `~/.claude/projects/<cwd-tireli>/<session_id>.jsonl` |
| `Stop` anında transkript güncel miydi | **Hayır (0/1):** son asistan mesajı o anda dosyada yoktu (asenkron yazım) |
| Mesajlar ne zaman içeri alındı | `SessionEnd`'de (2 mesaj: 1 user, 1 assistant). Gecikme: 4,3 sn / 0,1 sn |
| Kart | 1 kart (`karar`, `new`) kullanıcı cümlesinden |
| Hook'un kendi işlem süresi | ~4 ms |
| Not | Bu sandbox'ta oturum kimliği, üst oturumun kimliğiyle aynı göründü (çalıştırma ortamı kaynaklı olabilir; genelleme yok) |

## Gerçek transkript biçim doğrulaması (içerik okunmadı, yalnız yapı/sayı)

Bu geliştirme oturumunun kendi transkripti (salt-okunur kopya) işlendi: 538 satır, 313 satırlık `user/assistant` mesajı; bunlardan yalnız **33'ü** insan/asistan `text` içeriği (kalanı araç çağrısı/sonucu ve `thinking`). Parser hatasız çalıştı (bozuk satır 0), `thinking` içeriği veritabanına **sızmadı** (kontrol edildi). 59 aday üretildi; **etiketlenmediği için precision bilinmiyor.**

## Bu çalıştırmanın söyleyemedikleri

- **Etkileşimli** oturumda `Stop` anında transkriptin güncel olup olmadığı. `-p` modunda güncel değildi; etkileşimli modda durum farklı olabilir. → `OBSERVE.md` ile senin makinen ölçsün.
- Uzun oturum, paralel pencere, çökme/`SessionEnd`'siz kapanış, macOS davranışı.
- Kural tabanlı çıkarımın gerçek konuşmalardaki precision/recall değeri.
- Codex ve ChatGPT yüzeyleri.

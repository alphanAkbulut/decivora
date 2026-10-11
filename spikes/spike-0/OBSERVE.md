# Gözlem protokolü (senin makinen için)

Amaç: Claude Code'un gerçek oturumlarında Spike-0'ın ne yakaladığını görmek. Hüküm yok; sayı ve not. Kurulum ve komutlar: [README.md](README.md).

**Önce:** sandbox bir klasör kullan (gerçek projen değil). Gerçek projeye kurulum için ayrıca karar ver; veriler `data/` altında yerelde kalır ve gitignore'dadır.

## Oturumlar (3–5 tane)

| # | Ne yap | Neyi gör |
|---|---|---|
| 1 | Kısa oturum (3–5 tur); açık bir karar ve bir fikir söyle; kod yazdır | Hook tetiklendi mi? Kartlar ne zaman göründü? |
| 2 | Uzun oturum (15+ tur, araç çağrılı) | `Stop` anında transkript güncel mi (`status` ve `report`'ta "Stop anında…")? Geride kalan bayt var mı? |
| 3 | **Kapanışsız bitir:** terminali/pencereyi doğrudan kapat (`/exit` yazmadan) | `SessionEnd` olmadan neler kayıp? `spike status` GERİDE gösteriyor mu? `spike process` telafi ediyor mu? |
| 4 | **İki pencere, aynı klasör:** biri "X için A'yı kullanalım" desin, diğeri "A yerine B" desin | İki oturum karışmadan işlendi mi? `possible_supersedes` doğru eşleşti mi? |
| 5 | (İsteğe bağlı) Gerçek bir proje klasörü — yalnız kararın sonrası | Aynı gözlemler |

## Her oturumdan sonra

1. `./bin/spike status`
2. `./bin/spike review` — her kart için a (doğru yakalama) / r (gürültü, yanlış) / d (emin değilim). Metin yazmak gerekmez.
3. Not al:
   - Hangi hook **tetiklenmedi** veya geç tetiklendi?
   - Claude Code'un davranışı değişti mi (yavaşlama, hata iletisi, bağlamın kirlenmesi)?
   - Kaç kart gürültü? Hangi önemli karar/fikir **kaçtı**? (kendi gözünle)
   - Review kaç dakika sürdü?

## Sonunda

```bash
./bin/spike report --save     # results/report-*.md
```

`results/` altındaki raporu ve notlarını (`results/notes-<tarih>.md`, serbest metin) birlikte sakla. Rapor precision'ı **n ile** verir; n<30 ise yalnız yön göstergesidir.

**Hatırlatma:** bu ölçümler build/extend ve MVP kapsamı kararına girdidir. "Başarılı/başarısız" eşiğini sen koyarsın.

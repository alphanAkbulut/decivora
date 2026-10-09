# Katkı düzeni

Bu repo discovery aşamasındadır; katkılar küçük ve kapsam ID/task ID/AC ile izlenebilir olmalıdır. Önce AGENTS.md ve güncel status'u okuyun. Ürün scope'unu veya ADR statüsünü sessizce değiştirmeyin.

Bir değişiklik: problem ve beklenen davranış, ilgili görev, değişen dosyalar, doğrulama sonucu ve bilinen sınırları anlatmalıdır. Önerilen yeni yetenek full-scope/backlog'a eklenir; mevcut kullanıcı kararının yerine otomatik geçmez.

Üçüncü taraf kod/prompt/asset alımından önce exact commit ve lisans koşullarını kaydedin. Runtime data, transcript, secrets, müşteri bilgisi ve başka projenin dosyalarını commit etmeyin. Public katkı/lisans politikası public release öncesinde kesinleşecektir.

Kontrol: `python3 scripts/check_docs.py`. Bu yalnız dokümantasyon kontrolüdür. Uygulama testleri ilgili runtime göreviyle eklenir.

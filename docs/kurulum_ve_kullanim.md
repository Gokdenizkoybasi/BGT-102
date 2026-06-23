# Kurulum ve Kullanım

## Gereksinimler

- Python 3.8 veya üstü
- Tkinter (Python ile birlikte gelir; Linux'ta gerekirse `sudo apt install python3-tk`)
- Harici paket, API anahtarı veya Docker **gerekmez**.

## Kurulum

Repository'yi klonlayın veya indirin:

```bash
git clone <repo-url>
cd bgt102-final
```

## Çalıştırma

```bash
cd src
python3 osint_tool.py
```

İlk çalıştırmada `hawkosint.db` ve `hawkosint.log` dosyaları `src/` içinde otomatik oluşur.

## İlk Giriş

```
Kullanıcı: admin
Şifre:     admin123
```

## Kullanım Akışı

1. **Giriş / Kayıt ekranı:** Mevcut hesapla giriş yapın veya yeni hesap oluşturun (rol seçilebilir: guest / analyst / admin).
2. **Tarama sekmesi:** Araç seçin (DNS, HTTP, Port, SSL, WHOIS, Email), hedef girin, "Çalıştır"a basın. Sonuç JSON olarak görüntülenir ve veritabanına kaydedilir.
3. **Raporlar sekmesi:** Geçmiş taramaları listeleyin, istatistik görün, TXT olarak dışa aktarın.
4. **Loglar sekmesi (yalnızca admin):** Tüm sistem olaylarını görüntüleyin.
5. **Kullanıcılar sekmesi (yalnızca admin):** Kullanıcıların rolünü değiştirin, hesapları aktif/pasif yapın.

## Rol Bazlı Görünüm

| Rol | Görünen sekmeler |
|---|---|
| admin | Tarama, Raporlar, Loglar, Kullanıcılar |
| analyst | Tarama, Raporlar |
| guest | Tarama (sınırlı araç), Raporlar (yalnızca kendi) |

## Örnek Taramalar

- DNS Lookup → `behind24.com`
- HTTP Headers → `https://github.com`
- Port Tarama → `scanme.nmap.org`
- Email Türetme → Hedef alanı `behind24.com`, ek alana `Ad Soyad`

## Sık Karşılaşılan Durumlar

- **Tkinter bulunamadı (Linux):** `sudo apt install python3-tk`
- **Port taraması yavaş:** Her port için kısa timeout vardır; normaldir.
- **Veritabanını sıfırlamak:** `src/hawkosint.db` dosyasını silin; bir sonraki açılışta yeniden oluşur ve hazır admin hesabı kurulur.

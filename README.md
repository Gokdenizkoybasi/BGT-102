# BGT 102 — Final Projesi: HAWK-OSINT Lite

Apisiz, Docker'sız, yalnızca Python 3 standart kütüphanesi ile çalışan masaüstü (Tkinter GUI) OSINT aracı. Verilen değerlendirme yönetmeliğindeki tüm maddeleri (veritabanı, 3 kullanıcı tipi, hazır admin hesabı, OOP kullanıcı sınıfları, login/kayıt, log, raporlama, kalıcı veri, gerçek yetki sistemi, CLI/GUI, dokümantasyon) karşılar.

## Ekip Üyeleri

| Ad Soyad | Okul Numarası | Rol |
|---|---|---|
| Semih Mert Korkmaz | 202407105077 | Backend & Veritabanı |
| Gökdeniz Köybaşı | 202407105076 | GUI & OSINT Modülleri |

Görev dağılımının tam ayrıntısı: [`docs/gorev_dagilimi.md`](docs/gorev_dagilimi.md)

## Çalıştırma

```bash
cd src
python3 osint_tool.py
```

Gereksinim: Python 3.8+ (tkinter Python ile birlikte gelir). Harici paket, API anahtarı veya Docker gerekmez.

İlk giriş bilgileri:

```
Kullanıcı: admin
Şifre:     admin123
```

## Proje Yapısı

```
bgt102-final/
├── README.md                 → bu dosya
├── src/
│   ├── osint_tool.py         → Tkinter GUI (giriş ekranı + ana panel)
│   └── core.py               → Backend: DB, auth, RBAC, log, raporlama, OSINT motoru
└── docs/
    ├── proje_raporu.md       → Detaylı proje raporu
    ├── gorev_dagilimi.md     → Ekip üyeleri ve kim ne yaptı
    ├── kurulum_ve_kullanim.md→ Kurulum, kullanım, ekran akışı
    └── mimari.md             → Modüler mimari ve sınıf diyagramı
```

## Özellikler

OSINT araçları (hepsi apisiz — `socket`, `urllib`, `ssl` ile): DNS Lookup, HTTP Headers, Port Tarama, SSL Sertifika, WHOIS (port 43), Email Türetme.

3 kullanıcı tipi ve gerçek yetki (RBAC):

- **admin** — tüm araçlar + loglar + kullanıcı yönetimi + tüm raporlar
- **analyst** — tüm araçlar + raporlar
- **guest** — sınırlı araç (DNS, HTTP) + sadece kendi raporu

## Lisans

Eğitim amaçlı / akademik kullanım.

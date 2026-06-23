<div align="center">

# 🦅 HAWK-OSINT Lite

**Python 3 standart kütüphanesi ile yazılmış, çok kullanıcılı masaüstü OSINT aracı**

BGT 102 — Final Projesi

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-ff6f00?style=flat)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![No API](https://img.shields.io/badge/API-Yok-success?style=flat)
![No Docker](https://img.shields.io/badge/Docker-Gerekmez-success?style=flat)
![License](https://img.shields.io/badge/Lisans-MIT-blue?style=flat)

</div>

---

## 📌 Proje Hakkında

**HAWK-OSINT Lite**, açık kaynak istihbarat (OSINT) toplama işlemlerini tek bir masaüstü arayüzde birleştiren, **çok kullanıcılı** ve **yetkilendirme tabanlı** bir araçtır.

Uygulama tamamen **Python 3 standart kütüphanesi** ile geliştirilmiştir — harici paket, API anahtarı veya Docker **gerektirmez**. Bir hedef (alan adı, IP veya kişi) hakkında pasif tekniklerle bilgi toplar, elde edilen tüm sonuçları kalıcı olarak saklar ve raporlar.

Proje, ders kapsamındaki değerlendirme yönetmeliğinin **tüm maddelerini** karşılar: veritabanı, 3 kullanıcı tipi, hazır admin hesabı, OOP kullanıcı sınıfları, login/kayıt, log sistemi, raporlama, kalıcı veri saklama, gerçek yetki sistemi (RBAC), çalıştırılabilir GUI ve dokümantasyon.

---

## 📸 Ekran Görüntüleri

> Aşağıdaki görselleri kendi ekran görüntülerinizle değiştirin.

<div align="center">

### Giriş Ekranı
<img src="https://i.imgur.com/PLACEHOLDER1.png" alt="Giriş Ekranı" width="700"/>

### Ana Panel — Tarama Sekmesi
<img src="https://i.imgur.com/PLACEHOLDER2.png" alt="Tarama Sekmesi" width="700"/>

### Raporlar ve Loglar
<img src="https://i.imgur.com/PLACEHOLDER3.png" alt="Raporlar" width="700"/>

</div>

---

## 👥 Ekip

| Ad Soyad | Okul Numarası | Sorumluluk |
|---|---|---|
| **Semih Mert Korkmaz** | 202407105077 | Backend, Veritabanı, Güvenlik |
| **Gökdeniz Köybaşı** | 202407105076 | GUI, OSINT Modülleri, Raporlama |

> Ayrıntılı görev dağılımı: [`docs/gorev_dagilimi.md`](docs/gorev_dagilimi.md)

---

## 🚀 Kurulum ve Çalıştırma

Tek gereksinim **Python 3.8+** (tkinter Python ile birlikte gelir).

```bash
# Repoyu klonla
git clone https://github.com/KULLANICI-ADI/bgt102-final.git
cd bgt102-final/src

# Çalıştır
python3 osint_tool.py
```

> **Linux'ta tkinter eksikse:** `sudo apt install python3-tk`

### İlk Giriş

```
Kullanıcı: admin
Şifre:     admin123
```

İlk çalıştırmada `hawkosint.db` veritabanı ve hazır admin hesabı otomatik oluşur.

---

## 🛠️ Özellikler

### OSINT Araçları (tamamı apisiz)

| Araç | Açıklama | Kütüphane |
|---|---|---|
| 🌐 **DNS Lookup** | İleri/geri DNS çözümleme, IP listesi | `socket` |
| 📡 **HTTP Headers** | Sunucu başlıkları ve banner bilgisi | `urllib` |
| 🔌 **Port Tarama** | Yaygın portların açık/kapalı kontrolü | `socket` |
| 🔐 **SSL Sertifika** | Sertifika sahibi, geçerlilik, SAN | `ssl` |
| 📋 **WHOIS** | Port 43 üzerinden ham WHOIS sorgusu | `socket` |
| ✉️ **Email Türetme** | Kurumsal e-posta kalıpları üretimi | — |

### Kullanıcı Tipleri ve Yetki Sistemi (RBAC)

| Rol | Yetkiler |
|---|---|
| 👑 **admin** | Tüm araçlar + loglar + kullanıcı yönetimi + tüm raporlar |
| 🔎 **analyst** | Tüm araçlar + raporlar |
| 👤 **guest** | Sınırlı araç (DNS, HTTP) + yalnızca kendi raporu |

Yetki kontrolü hem **arayüz seviyesinde** (sekmeler role göre gizlenir) hem de **kod seviyesinde** (`user.can(...)`) uygulanır.

### Diğer Özellikler

- 💾 **Kalıcı veri saklama** — Tüm kullanıcı, log ve taramalar SQLite veritabanında tutulur.
- 📝 **Loglama** — Giriş, kayıt, tarama ve yönetim işlemleri veritabanına ve dosyaya yazılır.
- 📊 **Raporlama** — Tarama geçmişi, istatistik ve TXT dışa aktarma.
- 🔒 **Güvenlik** — Şifreler düz metin saklanmaz; rastgele salt + SHA-256 kullanılır.

---

## 🏗️ Mimari

İki katmanlı yapı: arayüz yalnızca backend'i çağırır, iş mantığı içermez. Bu sayede backend, GUI olmadan komut satırından test edilebilir.

```
┌─────────────────────────────┐
│   osint_tool.py  (GUI)      │   Tkinter / ttk
│   Giriş · Tarama · Rapor ·  │
│   Log · Kullanıcı sekmeleri │
└──────────────┬──────────────┘
               │ çağırır
┌──────────────▼──────────────┐
│   core.py  (Backend)        │
│   Database · AuthManager ·  │   sqlite3 · hashlib
│   User(RBAC) · Logger ·     │
│   OSINTEngine · ReportMgr   │   socket · urllib · ssl
└─────────────────────────────┘
```

---

## 📂 Proje Yapısı

```
bgt102-final/
├── README.md                          → bu dosya
├── LICENSE                            → MIT lisansı
├── src/
│   ├── osint_tool.py                  → Tkinter GUI (giriş ekranı + ana panel)
│   └── core.py                        → Backend: DB, auth, RBAC, log, raporlama, OSINT motoru
└── docs/
    ├── HAWK-OSINT_Proje_Raporu.pdf    → Açıklayıcı PDF rapor
    ├── sunum_notlari.md               → Sunum konuşma notları
    ├── proje_raporu.md                → Detaylı proje raporu
    ├── gorev_dagilimi.md              → Ekip üyeleri ve kim ne yaptı
    ├── kurulum_ve_kullanim.md         → Kurulum, kullanım, ekran akışı
    └── mimari.md                      → Modüler mimari ve sınıf diyagramı
```

---

## ✅ Değerlendirme Maddeleri Karşılığı

| Kriter | Karşılık | Durum |
|---|---|:---:|
| Modüler yapı | `core.py` içinde ayrı sınıflar | ✅ |
| Veritabanı | sqlite3 | ✅ |
| 3 kullanıcı tipi | admin / analyst / guest | ✅ |
| Hazır admin hesabı | admin / admin123 | ✅ |
| OOP kullanıcı sınıfları | `User(ABC)` + Admin/Analyst/Guest | ✅ |
| Login / Kayıt sistemi | `AuthManager` | ✅ |
| Log sistemi | logs tablosu + dosya | ✅ |
| Kullanıcı raporlama | `ReportManager` + sekme | ✅ |
| Kalıcı veri saklama | `.db` dosyası | ✅ |
| Gerçek yetki sistemi | RBAC (rol → izin) | ✅ |
| Çalıştırılabilir GUI | `python3 osint_tool.py` | ✅ |
| Dokümantasyon | `docs/` klasörü + PDF | ✅ |

---

## 📖 Dokümantasyon

- 📄 [PDF Proje Raporu](docs/HAWK-OSINT_Proje_Raporu.pdf)
- 🎤 [Sunum Notları](docs/sunum_notlari.md)
- 📋 [Detaylı Proje Raporu](docs/proje_raporu.md)
- 👥 [Görev Dağılımı](docs/gorev_dagilimi.md)
- ⚙️ [Kurulum ve Kullanım](docs/kurulum_ve_kullanim.md)
- 🏛️ [Mimari](docs/mimari.md)

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır. Eğitim amaçlı / akademik kullanım içindir ve yalnızca yasal ve etik OSINT amaçlarıyla kullanılmalıdır.

---

<div align="center">
<sub>BGT 102 — Final Projesi · HAWK-OSINT Lite · 2026</sub>
</div>

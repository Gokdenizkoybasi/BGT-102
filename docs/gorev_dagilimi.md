# Görev Dağılımı

Proje: **HAWK-OSINT Lite** — BGT 102 Final Projesi
Çalışma şekli: 2 kişilik ekip, GitHub repository üzerinden ortak geliştirme.

## Ekip Üyeleri

| Ad Soyad | Okul Numarası | Birincil Sorumluluk |
|---|---|---|
| Semih Mert Korkmaz | 202407105077 | Backend, Veritabanı, Güvenlik |
| Gökdeniz Köybaşı | 202407105076 | GUI, OSINT Modülleri, Raporlama |

---

## Semih Mert Korkmaz — 202407105077

**Birincil alan: Backend & Veritabanı katmanı (`src/core.py`)**

- SQLite veritabanı şemasının tasarımı ve kurulumu (`Database` sınıfı): `users`, `logs`, `scans` tabloları, foreign key ve PRAGMA ayarları.
- Hazır admin hesabının ilk kurulumda otomatik oluşturulması (`admin / admin123`).
- Kimlik doğrulama sistemi (`AuthManager`): kayıt, giriş, salt + SHA-256 ile şifre özetleme, kullanıcı adı/şifre doğrulama kuralları.
- Gerçek yetki sistemi (RBAC): `PERMISSIONS` rol→izin haritası ve `User.can()` izin kontrolü.
- OOP kullanıcı sınıfları: soyut `User(ABC)` taban sınıfı ve `Admin`, `Analyst`, `Guest` türetilmiş sınıfları, `make_user` fabrika fonksiyonu.
- Log sistemi (`Logger`): hem veritabanına hem `hawkosint.log` dosyasına yazma.
- Kullanıcı yönetimi işlemleri: rol değiştirme, hesap aktif/pasif yapma.

**Katkı dosyaları:** `src/core.py` (Database, AuthManager, Logger, User sınıfları, RBAC)

---

## Gökdeniz Köybaşı — 202407105076

**Birincil alan: GUI & OSINT modülleri & Raporlama (`src/osint_tool.py`, `src/core.py` OSINT bölümü)**

- Tkinter tabanlı koyu temalı arayüzün tasarımı (`App` sınıfı, `_style`).
- Giriş/Kayıt ekranı (`show_login`) ve ana panel (`show_main`) — sekmelerin role göre dinamik gösterimi.
- OSINT motoru (`OSINTEngine`) — tamamı apisiz, yalnızca standart kütüphane ile:
  - DNS Lookup (`socket.gethostbyname`, reverse DNS)
  - HTTP Headers (`urllib.request`)
  - Port Tarama (`socket` ile yaygın portlar)
  - SSL Sertifika bilgisi (`ssl` modülü)
  - WHOIS (port 43 ham sorgu)
  - Email türetme (kurumsal e-posta kalıpları)
- Tarama işlemlerinin arayüzü kilitlememesi için `threading` ile arka planda çalıştırılması.
- Raporlama (`ReportManager`) ve Raporlar sekmesi: tarama geçmişi tablosu, istatistik, TXT dışa aktarma.
- Loglar ve Kullanıcılar sekmelerinin arayüzü.

**Katkı dosyaları:** `src/osint_tool.py` (tüm GUI), `src/core.py` (OSINTEngine, ReportManager)

---

## Ortak Çalışılan Kısımlar

- Proje mimarisinin birlikte kararlaştırılması (modüler `core` + `gui` ayrımı).
- Yönetmelik maddelerinin tek tek kontrol edilip eşlenmesi.
- Dokümantasyonun (`docs/`) hazırlanması.
- Test ve hata ayıklama: backend mantığının komut satırından doğrulanması, GUI akışının elle test edilmesi.

## Commit / Katkı Özeti

| Modül | Sorumlu |
|---|---|
| `Database`, şema, hazır admin | Semih Mert Korkmaz |
| `AuthManager`, RBAC, `User` sınıfları | Semih Mert Korkmaz |
| `Logger` | Semih Mert Korkmaz |
| `OSINTEngine` (tüm araçlar) | Gökdeniz Köybaşı |
| `ReportManager` | Gökdeniz Köybaşı |
| Tüm Tkinter GUI (`osint_tool.py`) | Gökdeniz Köybaşı |
| Dokümantasyon, test | Her iki üye |

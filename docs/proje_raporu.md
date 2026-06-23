# Proje Raporu — HAWK-OSINT Lite

**Ders:** BGT 102
**Proje:** Final Projesi
**Ekip:** Semih Mert Korkmaz (202407105077), Gökdeniz Köybaşı (202407105076)

---

## 1. Özet

HAWK-OSINT Lite, açık kaynak istihbarat (OSINT) toplama işlemlerini tek bir masaüstü arayüzde toplayan, çok kullanıcılı ve yetkilendirme tabanlı bir araçtır. Uygulama tamamen Python 3 standart kütüphanesi ile yazılmıştır; harici bir paket, API anahtarı veya Docker gerektirmez. Kullanıcı yönetimi, kalıcı veri saklama, loglama ve raporlama özellikleriyle ders kapsamındaki değerlendirme yönetmeliğinin tüm maddelerini karşılar.

## 2. Amaç ve Kapsam

Amaç, bir hedef (alan adı / IP / kişi) hakkında pasif ve düşük etkili aktif teknikler kullanarak bilgi toplamayı kolaylaştırmaktır. Kapsam:

- Çok kullanıcılı kimlik doğrulama ve yetkilendirme
- Apisiz OSINT modülleri (DNS, HTTP, port, SSL, WHOIS, e-posta türetme)
- Tüm taramaların kalıcı olarak saklanması ve raporlanması
- İşlemlerin loglanması

## 3. Kullanılan Teknolojiler

| Bileşen | Teknoloji |
|---|---|
| Dil | Python 3 |
| Arayüz | tkinter / ttk (standart kütüphane) |
| Veritabanı | sqlite3 (standart kütüphane) |
| Ağ işlemleri | socket, urllib, ssl (standart kütüphane) |
| Güvenlik | hashlib (SHA-256), secrets (salt) |

Harici bağımlılık yoktur.

## 4. Mimari

Uygulama iki katmana ayrılmıştır:

- **`core.py` (backend):** Veritabanı, kimlik doğrulama, yetkilendirme, log, raporlama ve OSINT motoru. Arayüzden bağımsızdır, komut satırından da kullanılabilir.
- **`osint_tool.py` (GUI):** Tkinter arayüzü. Yalnızca `core.py` içindeki sınıfları çağırır.

Bu ayrım sayesinde backend mantığı GUI olmadan test edilebilir. Ayrıntı: [`mimari.md`](mimari.md).

## 5. Veritabanı Tasarımı

Üç tablo kullanılır:

- **users** — `id, username, pw_hash, salt, role, created, active`
- **logs** — `id, ts, username, action, detail`
- **scans** — `id, ts, username, tool, target, result`

Veritabanı dosyası (`hawkosint.db`) ilk çalıştırmada otomatik oluşturulur ve kalıcıdır.

## 6. Kullanıcı Tipleri ve Yetkilendirme

Üç kullanıcı tipi ve rol→izin haritası (RBAC):

| Rol | İzinler |
|---|---|
| admin | scan, view_logs, manage_users, reports, all_tools |
| analyst | scan, reports, all_tools |
| guest | scan_limited |

Yetki kontrolü hem arayüz seviyesinde (sekmeler role göre gizlenir) hem de mantık seviyesinde (`user.can(...)`) yapılır. Hazır admin hesabı: `admin / admin123`.

## 7. OSINT Modülleri

| Modül | Yöntem | Kütüphane |
|---|---|---|
| DNS Lookup | İleri/geri DNS çözümleme | socket |
| HTTP Headers | Sunucu başlıkları, banner | urllib |
| Port Tarama | Yaygın portların kontrolü | socket |
| SSL Sertifika | Sertifika sahibi, geçerlilik, SAN | ssl |
| WHOIS | Port 43 ham WHOIS sorgusu | socket |
| Email Türetme | Kurumsal e-posta kalıpları | — |

Hiçbir modül ücretli/anahtarlı API kullanmaz.

## 8. Güvenlik

- Şifreler düz metin saklanmaz; her kullanıcı için rastgele salt üretilip SHA-256 ile özetlenir.
- Kullanıcı adı doğrulaması (regex) ve minimum şifre uzunluğu kontrolü vardır.
- Başarısız giriş denemeleri loglanır.

## 9. Loglama ve Raporlama

Tüm önemli işlemler (giriş, kayıt, tarama, rol değişikliği) hem veritabanına hem log dosyasına yazılır. Raporlar sekmesinde tarama geçmişi tablo halinde görüntülenir, istatistik çıkarılır ve TXT olarak dışa aktarılabilir. Misafir kullanıcı yalnızca kendi taramalarını, admin/analyst tüm taramaları görür.

## 10. Yönetmelik Madde Eşlemesi

| Kriter | Karşılık | Durum |
|---|---|---|
| Modüler yapı | `core.py` içinde ayrı sınıflar | ✅ |
| Veritabanı | sqlite3 | ✅ |
| 3 kullanıcı tipi | admin / analyst / guest | ✅ |
| Hazır admin hesabı | admin/admin123 | ✅ |
| OOP kullanıcı sınıfları | User(ABC) + Admin/Analyst/Guest | ✅ |
| Login/Kayıt sistemi | AuthManager | ✅ |
| Log sistemi | logs tablosu + dosya | ✅ |
| Kullanıcı raporlama | ReportManager + sekme | ✅ |
| Kalıcı veri saklama | .db dosyası | ✅ |
| Gerçek yetki sistemi | RBAC | ✅ |
| Çalıştırılabilir GUI | python3 osint_tool.py | ✅ |
| Dokümantasyon | docs/ klasörü | ✅ |

## 11. Sonuç

Proje, belirtilen tüm zorunlu maddeleri karşılayan, modüler ve genişletilebilir bir yapıda tamamlanmıştır. Yeni OSINT modülleri `OSINTEngine` sınıfına metot eklenerek kolayca genişletilebilir.

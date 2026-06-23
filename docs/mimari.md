# Mimari

## Genel Yapı

Uygulama, sunum (GUI) ve mantık (backend) katmanlarına ayrılmıştır. GUI yalnızca backend sınıflarını çağırır; iş mantığı içermez. Bu sayede backend, GUI olmadan komut satırından test edilebilir.

```
┌─────────────────────────────┐
│   osint_tool.py  (GUI)      │   Tkinter / ttk
│   - App                     │
│   - Giriş/Kayıt ekranı      │
│   - Tarama / Rapor / Log /  │
│     Kullanıcı sekmeleri     │
└──────────────┬──────────────┘
               │  çağırır
┌──────────────▼──────────────┐
│   core.py  (Backend)        │
│   - Database                │  sqlite3
│   - Logger                  │
│   - AuthManager             │  hashlib + secrets
│   - User(ABC) / Admin /     │
│     Analyst / Guest         │  OOP + RBAC
│   - OSINTEngine             │  socket / urllib / ssl
│   - ReportManager           │
└─────────────────────────────┘
```

## Sınıf Sorumlulukları

### Database
SQLite bağlantısı ve şema yönetimi. `users`, `logs`, `scans` tablolarını oluşturur, ilk kurulumda hazır admin hesabını ekler.

### Logger
Olayları hem `logs` tablosuna hem `hawkosint.log` dosyasına yazar; geçmiş kayıtları okur.

### AuthManager
Kayıt, giriş, şifre özetleme (salt + SHA-256), kullanıcı listeleme, rol değiştirme, hesap aktif/pasif yapma.

### User (soyut) → Admin / Analyst / Guest
OOP kullanıcı hiyerarşisi. `permissions` özelliği rol→izin haritasından izinleri döndürür; `can(perm)` izin kontrolü yapar. `make_user` fabrika fonksiyonu doğru alt sınıfı üretir.

### OSINTEngine
Apisiz OSINT araçları: `dns_lookup`, `http_headers`, `port_scan`, `ssl_info`, `whois`, `email_patterns`. Her tarama `scans` tablosuna kaydedilir.

### ReportManager
Tarama geçmişi sorgulama (kullanıcı bazlı / tümü), istatistik, TXT dışa aktarma.

## Yetkilendirme (RBAC) Akışı

```
Giriş → AuthManager.login() → make_user() → Admin/Analyst/Guest nesnesi
                                                   │
GUI sekme oluştururken → user.can("view_logs") vb. → sekme gösterilir/gizlenir
Tarama aracı listesi    → user.can("all_tools")    → tam/sınırlı araç listesi
```

## Genişletilebilirlik

Yeni bir OSINT modülü eklemek için `OSINTEngine` sınıfına yeni bir metot yazmak ve GUI'deki araç listesine eklemek yeterlidir; diğer katmanlar değişmez.

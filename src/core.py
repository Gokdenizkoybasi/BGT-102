"""
HAWK-OSINT Lite — Çekirdek Backend
==================================
Yönetmelik karşılığı:
  - Veritabanı           -> sqlite3 (kalıcı)
  - 3 kullanıcı tipi     -> admin / analyst / guest
  - Hazır admin hesabı   -> admin / admin123 (ilk kurulumda)
  - OOP kullanıcı sınıfları -> User taban + Admin/Analyst/Guest
  - Login/Kayıt sistemi  -> AuthManager
  - Log sistemi          -> logs tablosu + dosya
  - Kullanıcı raporlama  -> ReportManager
  - Kalıcı veri saklama  -> sqlite3 .db dosyası
  - Gerçek yetki sistemi -> rol -> izin haritası (RBAC)

Sadece Python 3 standart kütüphanesi. API yok, Docker yok.
"""

import sqlite3
import hashlib
import secrets
import socket
import ssl
import re
import json
import os
import datetime
import urllib.request
import urllib.error
from abc import ABC, abstractmethod

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hawkosint.db")
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hawkosint.log")


# ============================================================
#  VERİTABANI KATMANI  (Kalıcı veri saklama)
# ============================================================
class Database:
    def __init__(self, path=DB_PATH):
        self.path = path
        self._init_schema()

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self):
        with self._conn() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT UNIQUE NOT NULL,
                pw_hash   TEXT NOT NULL,
                salt      TEXT NOT NULL,
                role      TEXT NOT NULL DEFAULT 'guest',
                created   TEXT NOT NULL,
                active    INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS logs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT NOT NULL,
                username  TEXT,
                action    TEXT NOT NULL,
                detail    TEXT
            );
            CREATE TABLE IF NOT EXISTS scans (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ts        TEXT NOT NULL,
                username  TEXT NOT NULL,
                tool      TEXT NOT NULL,
                target    TEXT NOT NULL,
                result    TEXT
            );
            """)
        # Hazır admin hesabı
        with self._conn() as c:
            row = c.execute("SELECT COUNT(*) n FROM users").fetchone()
            if row["n"] == 0:
                salt = secrets.token_hex(16)
                pw = hashlib.sha256(("admin123" + salt).encode()).hexdigest()
                now = datetime.datetime.now().isoformat(timespec="seconds")
                c.execute(
                    "INSERT INTO users(username,pw_hash,salt,role,created,active) "
                    "VALUES(?,?,?,?,?,1)",
                    ("admin", pw, salt, "admin", now),
                )


# ============================================================
#  LOG SİSTEMİ
# ============================================================
class Logger:
    def __init__(self, db):
        self.db = db

    def log(self, username, action, detail=""):
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with self.db._conn() as c:
            c.execute(
                "INSERT INTO logs(ts,username,action,detail) VALUES(?,?,?,?)",
                (ts, username, action, detail),
            )
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {username or '-'} | {action} | {detail}\n")
        except OSError:
            pass

    def fetch(self, limit=200):
        with self.db._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()]


# ============================================================
#  OOP KULLANICI SINIFLARI  +  GERÇEK YETKİ SİSTEMİ (RBAC)
# ============================================================
PERMISSIONS = {
    "admin":   {"scan", "view_logs", "manage_users", "reports", "all_tools"},
    "analyst": {"scan", "reports", "all_tools"},
    "guest":   {"scan_limited"},
}


class User(ABC):
    def __init__(self, uid, username, role):
        self.id = uid
        self.username = username
        self.role = role

    @property
    def permissions(self):
        return PERMISSIONS.get(self.role, set())

    def can(self, perm):
        return perm in self.permissions

    @abstractmethod
    def label(self):
        ...


class Admin(User):
    def label(self):
        return "Yönetici (tüm yetkiler)"


class Analyst(User):
    def label(self):
        return "Analist (tarama + rapor)"


class Guest(User):
    def label(self):
        return "Misafir (sınırlı tarama)"


def make_user(uid, username, role):
    return {"admin": Admin, "analyst": Analyst, "guest": Guest}.get(role, Guest)(
        uid, username, role
    )


# ============================================================
#  LOGIN / KAYIT SİSTEMİ
# ============================================================
class AuthError(Exception):
    pass


class AuthManager:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    @staticmethod
    def _hash(pw, salt):
        return hashlib.sha256((pw + salt).encode()).hexdigest()

    def register(self, username, password, role="guest"):
        username = username.strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
            raise AuthError("Kullanıcı adı 3-20 karakter, harf/rakam/_ olmalı.")
        if len(password) < 4:
            raise AuthError("Şifre en az 4 karakter olmalı.")
        if role not in PERMISSIONS:
            role = "guest"
        salt = secrets.token_hex(16)
        pw = self._hash(password, salt)
        now = datetime.datetime.now().isoformat(timespec="seconds")
        try:
            with self.db._conn() as c:
                c.execute(
                    "INSERT INTO users(username,pw_hash,salt,role,created,active) "
                    "VALUES(?,?,?,?,?,1)",
                    (username, pw, salt, role, now),
                )
        except sqlite3.IntegrityError:
            raise AuthError("Bu kullanıcı adı zaten alınmış.")
        self.logger.log(username, "REGISTER", f"role={role}")
        return True

    def login(self, username, password):
        with self.db._conn() as c:
            row = c.execute(
                "SELECT * FROM users WHERE username=? AND active=1", (username,)
            ).fetchone()
        if not row or self._hash(password, row["salt"]) != row["pw_hash"]:
            self.logger.log(username, "LOGIN_FAIL", "")
            raise AuthError("Kullanıcı adı veya şifre hatalı.")
        self.logger.log(username, "LOGIN_OK", f"role={row['role']}")
        return make_user(row["id"], row["username"], row["role"])

    def list_users(self):
        with self.db._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT id,username,role,created,active FROM users ORDER BY id"
            ).fetchall()]

    def set_role(self, username, role):
        if role not in PERMISSIONS:
            raise AuthError("Geçersiz rol.")
        with self.db._conn() as c:
            c.execute("UPDATE users SET role=? WHERE username=?", (role, username))
        self.logger.log("system", "ROLE_CHANGE", f"{username}->{role}")

    def toggle_active(self, username):
        with self.db._conn() as c:
            c.execute("UPDATE users SET active=1-active WHERE username=?", (username,))
        self.logger.log("system", "TOGGLE_ACTIVE", username)


# ============================================================
#  OSINT MODÜLLERİ  (Modüler yapı)  — apisiz, sadece stdlib
# ============================================================
class OSINTEngine:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def _save(self, username, tool, target, result):
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with self.db._conn() as c:
            c.execute(
                "INSERT INTO scans(ts,username,tool,target,result) VALUES(?,?,?,?,?)",
                (ts, username, tool, target, json.dumps(result, ensure_ascii=False)),
            )
        self.logger.log(username, "SCAN", f"{tool}:{target}")

    # --- DNS / IP çözümleme ---
    def dns_lookup(self, username, host):
        out = {"host": host}
        try:
            ip = socket.gethostbyname(host)
            out["ip"] = ip
            try:
                out["reverse"] = socket.gethostbyaddr(ip)[0]
            except Exception:
                out["reverse"] = "-"
            try:
                infos = socket.getaddrinfo(host, None)
                out["all_ips"] = sorted({i[4][0] for i in infos})
            except Exception:
                pass
        except Exception as e:
            out["error"] = str(e)
        self._save(username, "dns", host, out)
        return out

    # --- Port tarama (basit, yaygın portlar) ---
    def port_scan(self, username, host, ports=None):
        ports = ports or [21, 22, 23, 25, 53, 80, 110, 143, 443, 445,
                          3306, 3389, 5432, 8080, 8443]
        out = {"host": host, "open": [], "closed": []}
        try:
            ip = socket.gethostbyname(host)
        except Exception as e:
            out["error"] = str(e)
            self._save(username, "port", host, out)
            return out
        out["ip"] = ip
        for p in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.8)
            try:
                if s.connect_ex((ip, p)) == 0:
                    out["open"].append(p)
                else:
                    out["closed"].append(p)
            except Exception:
                out["closed"].append(p)
            finally:
                s.close()
        self._save(username, "port", host, out)
        return out

    # --- HTTP başlık / banner ---
    def http_headers(self, username, url):
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        out = {"url": url}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HAWK-OSINT/1.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                out["status"] = r.status
                out["headers"] = dict(r.headers)
                out["server"] = r.headers.get("Server", "-")
        except urllib.error.HTTPError as e:
            out["status"] = e.code
            out["headers"] = dict(e.headers) if e.headers else {}
        except Exception as e:
            out["error"] = str(e)
        self._save(username, "http", url, out)
        return out

    # --- SSL sertifika bilgisi ---
    def ssl_info(self, username, host, port=443):
        out = {"host": host, "port": port}
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=6) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ss:
                    cert = ss.getpeercert()
            out["subject"] = dict(x[0] for x in cert.get("subject", []))
            out["issuer"] = dict(x[0] for x in cert.get("issuer", []))
            out["valid_from"] = cert.get("notBefore")
            out["valid_to"] = cert.get("notAfter")
            out["san"] = [v for (_, v) in cert.get("subjectAltName", [])]
        except Exception as e:
            out["error"] = str(e)
        self._save(username, "ssl", host, out)
        return out

    # --- WHOIS (port 43, apisiz) ---
    def whois(self, username, domain):
        out = {"domain": domain}
        server = "whois.iana.org"
        try:
            def query(srv, q):
                with socket.create_connection((srv, 43), timeout=8) as s:
                    s.sendall((q + "\r\n").encode())
                    data = b""
                    while True:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                return data.decode(errors="ignore")

            first = query(server, domain)
            m = re.search(r"refer:\s*(\S+)", first)
            whois_text = first
            if m:
                whois_text = query(m.group(1), domain)
            out["raw"] = whois_text[:4000]
        except Exception as e:
            out["error"] = str(e)
        self._save(username, "whois", domain, out)
        return out

    # --- Email format / kurumsal türetme ---
    def email_patterns(self, username, full_name, domain):
        parts = full_name.lower().split()
        out = {"name": full_name, "domain": domain, "candidates": []}
        if len(parts) >= 2:
            f, l = parts[0], parts[-1]
            patterns = [
                f"{f}.{l}", f"{f}{l}", f"{f[0]}{l}", f"{f}_{l}",
                f"{l}.{f}", f"{f[0]}.{l}", f"{f}",
            ]
            out["candidates"] = [f"{p}@{domain}" for p in patterns]
        self._save(username, "email", f"{full_name}@{domain}", out)
        return out


# ============================================================
#  KULLANICI RAPORLAMA
# ============================================================
class ReportManager:
    def __init__(self, db):
        self.db = db

    def user_scans(self, username, limit=200):
        with self.db._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM scans WHERE username=? ORDER BY id DESC LIMIT ?",
                (username, limit),
            ).fetchall()]

    def all_scans(self, limit=500):
        with self.db._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM scans ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()]

    def stats(self):
        with self.db._conn() as c:
            tools = c.execute(
                "SELECT tool, COUNT(*) n FROM scans GROUP BY tool ORDER BY n DESC"
            ).fetchall()
            users = c.execute(
                "SELECT username, COUNT(*) n FROM scans GROUP BY username ORDER BY n DESC"
            ).fetchall()
            total = c.execute("SELECT COUNT(*) n FROM scans").fetchone()["n"]
        return {
            "total": total,
            "by_tool": [dict(r) for r in tools],
            "by_user": [dict(r) for r in users],
        }

    def export_txt(self, username=None, path=None):
        rows = self.user_scans(username) if username else self.all_scans()
        path = path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"rapor_{username or 'tum'}.txt",
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write("HAWK-OSINT RAPOR\n" + "=" * 50 + "\n")
            for r in rows:
                f.write(f"\n[{r['ts']}] {r['username']} | {r['tool']} -> {r['target']}\n")
                f.write(r["result"] + "\n")
        return path

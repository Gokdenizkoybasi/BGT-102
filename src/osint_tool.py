"""
HAWK-OSINT Lite — GUI (Tkinter)
================================
Çalıştırma:  python3 osint_tool.py
Gereksinim:  Sadece Python 3 (tkinter standart gelir). API yok, Docker yok.

İlk giriş:   admin / admin123
"""

import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

from core import (
    Database, Logger, AuthManager, OSINTEngine, ReportManager, AuthError,
)

# ---- Tema renkleri (koyu) ----
BG = "#0d1117"
BG2 = "#161b22"
FG = "#c9d1d9"
ACCENT = "#1f6feb"
GREEN = "#2ea043"
RED = "#f85149"
FONT = ("Consolas", 10)
FONT_BOLD = ("Consolas", 11, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HAWK-OSINT Lite")
        self.geometry("960x640")
        self.configure(bg=BG)

        self.db = Database()
        self.logger = Logger(self.db)
        self.auth = AuthManager(self.db, self.logger)
        self.engine = OSINTEngine(self.db, self.logger)
        self.reports = ReportManager(self.db)
        self.user = None

        self._style()
        self.show_login()

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=BG2)
        s.configure("TLabel", background=BG, foreground=FG, font=FONT)
        s.configure("Card.TLabel", background=BG2, foreground=FG, font=FONT)
        s.configure("Title.TLabel", background=BG, foreground=ACCENT, font=("Consolas", 18, "bold"))
        s.configure("TButton", font=FONT, padding=6)
        s.configure("Accent.TButton", background=ACCENT, foreground="white")
        s.map("Accent.TButton", background=[("active", "#388bfd")])
        s.configure("TEntry", fieldbackground=BG2, foreground=FG, insertcolor=FG)
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG2, foreground=FG, padding=(14, 6))
        s.map("TNotebook.Tab", background=[("selected", ACCENT)],
              foreground=[("selected", "white")])
        s.configure("Treeview", background=BG2, fieldbackground=BG2,
                    foreground=FG, font=FONT, rowheight=24)
        s.configure("Treeview.Heading", background=ACCENT, foreground="white", font=FONT_BOLD)

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ==================================================
    #  GİRİŞ / KAYIT EKRANI
    # ==================================================
    def show_login(self):
        self._clear()
        wrap = ttk.Frame(self)
        wrap.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(wrap, text="HAWK-OSINT", style="Title.TLabel").pack(pady=(0, 4))
      

        card = ttk.Frame(wrap, style="Card.TFrame", padding=24)
        card.pack()

        ttk.Label(card, text="Kullanıcı adı", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        u_ent = ttk.Entry(card, width=26)
        u_ent.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(card, text="Şifre", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        p_ent = ttk.Entry(card, width=26, show="•")
        p_ent.grid(row=3, column=0, pady=(0, 6))

        ttk.Label(card, text="Rol (sadece kayıtta)", style="Card.TLabel").grid(row=4, column=0, sticky="w", pady=4)
        role_cb = ttk.Combobox(card, values=["guest", "analyst", "admin"],
                               state="readonly", width=23)
        role_cb.set("guest")
        role_cb.grid(row=5, column=0, pady=(0, 14))

        def do_login():
            try:
                self.user = self.auth.login(u_ent.get().strip(), p_ent.get())
                self.show_main()
            except AuthError as e:
                messagebox.showerror("Giriş hatası", str(e))

        def do_register():
            try:
                self.auth.register(u_ent.get().strip(), p_ent.get(), role_cb.get())
                messagebox.showinfo("Kayıt", "Hesap oluşturuldu. Şimdi giriş yapabilirsin.")
            except AuthError as e:
                messagebox.showerror("Kayıt hatası", str(e))

        ttk.Button(card, text="Giriş Yap", style="Accent.TButton", command=do_login)\
            .grid(row=6, column=0, sticky="ew", pady=3)
        ttk.Button(card, text="Kayıt Ol", command=do_register)\
            .grid(row=7, column=0, sticky="ew", pady=3)

        ttk.Label(wrap, text="İlk giriş:  admin / admin123",
                  foreground="#8b949e").pack(pady=16)

        u_ent.focus()
        self.bind("<Return>", lambda e: do_login())

    # ==================================================
    #  ANA PANEL
    # ==================================================
    def show_main(self):
        self._clear()
        self.unbind("<Return>")

        top = ttk.Frame(self, padding=(14, 10))
        top.pack(fill="x")
        ttk.Label(top, text="HAWK-OSINT", style="Title.TLabel").pack(side="left")
        ttk.Label(top, text=f"  {self.user.username} · {self.user.label()}",
                  foreground="#8b949e").pack(side="left", padx=8)
        ttk.Button(top, text="Çıkış", command=self.show_login).pack(side="right")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=8)

        self._tab_scan(nb)
        if self.user.can("reports") or self.user.can("scan_limited"):
            self._tab_reports(nb)
        if self.user.can("view_logs"):
            self._tab_logs(nb)
        if self.user.can("manage_users"):
            self._tab_users(nb)

    # -------- TARAMA SEKMESİ --------
    def _tab_scan(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text="🔍 Tarama")

        bar = ttk.Frame(f)
        bar.pack(fill="x", pady=(0, 8))

        ttk.Label(bar, text="Araç:").pack(side="left")
        guest = not self.user.can("all_tools")
        tools = ["DNS Lookup", "HTTP Headers", "Port Tarama",
                 "SSL Sertifika", "WHOIS", "Email Türetme"]
        if guest:
            tools = ["DNS Lookup", "HTTP Headers"]  # misafir sınırlı
        self.tool_cb = ttk.Combobox(bar, values=tools, state="readonly", width=18)
        self.tool_cb.set(tools[0])
        self.tool_cb.pack(side="left", padx=6)

        ttk.Label(bar, text="Hedef:").pack(side="left")
        self.target_ent = ttk.Entry(bar, width=30)
        self.target_ent.pack(side="left", padx=6)
        self.target_ent.insert(0, "behind24.com")

        ttk.Label(bar, text="(Email için: Ad Soyad)").pack(side="left", padx=4)
        self.extra_ent = ttk.Entry(bar, width=16)
        self.extra_ent.pack(side="left", padx=6)

        ttk.Button(bar, text="Çalıştır", style="Accent.TButton",
                   command=self._run_scan).pack(side="left", padx=6)

        self.out = scrolledtext.ScrolledText(
            f, bg=BG2, fg=GREEN, insertbackground=FG,
            font=("Consolas", 10), relief="flat", wrap="word")
        self.out.pack(fill="both", expand=True)
        self.out.insert("end", "Sonuçlar burada görünecek...\n")

    def _run_scan(self):
        tool = self.tool_cb.get()
        target = self.target_ent.get().strip()
        extra = self.extra_ent.get().strip()
        if not target:
            messagebox.showwarning("Uyarı", "Hedef gir.")
            return
        self.out.delete("1.0", "end")
        self.out.insert("end", f"⏳ {tool} çalışıyor: {target}\n\n")

        def work():
            un = self.user.username
            try:
                if tool == "DNS Lookup":
                    r = self.engine.dns_lookup(un, target)
                elif tool == "HTTP Headers":
                    r = self.engine.http_headers(un, target)
                elif tool == "Port Tarama":
                    r = self.engine.port_scan(un, target)
                elif tool == "SSL Sertifika":
                    r = self.engine.ssl_info(un, target)
                elif tool == "WHOIS":
                    r = self.engine.whois(un, target)
                elif tool == "Email Türetme":
                    r = self.engine.email_patterns(un, extra or target, target)
                else:
                    r = {"error": "Bilinmeyen araç"}
            except Exception as e:
                r = {"error": str(e)}
            self.after(0, lambda: self._show_result(r))

        threading.Thread(target=work, daemon=True).start()

    def _show_result(self, r):
        self.out.delete("1.0", "end")
        self.out.insert("end", json.dumps(r, ensure_ascii=False, indent=2))

    # -------- RAPORLAR SEKMESİ --------
    def _tab_reports(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text="📊 Raporlar")

        bar = ttk.Frame(f)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="Yenile", command=lambda: self._load_reports(tree)).pack(side="left")
        ttk.Button(bar, text="TXT Dışa Aktar", command=self._export).pack(side="left", padx=6)
        self.stats_lbl = ttk.Label(bar, text="")
        self.stats_lbl.pack(side="left", padx=12)

        cols = ("ts", "user", "tool", "target")
        tree = ttk.Treeview(f, columns=cols, show="headings", height=18)
        for c, t, w in [("ts", "Tarih", 160), ("user", "Kullanıcı", 110),
                        ("tool", "Araç", 90), ("target", "Hedef", 320)]:
            tree.heading(c, text=t)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True)
        self._load_reports(tree)

    def _load_reports(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        # admin/analyst hepsini, guest kendi taramasını görür
        if self.user.can("all_tools"):
            rows = self.reports.all_scans()
        else:
            rows = self.reports.user_scans(self.user.username)
        for r in rows:
            tree.insert("", "end", values=(r["ts"], r["username"], r["tool"], r["target"]))
        st = self.reports.stats()
        self.stats_lbl.config(text=f"Toplam tarama: {st['total']}")

    def _export(self):
        un = None if self.user.can("all_tools") else self.user.username
        path = self.reports.export_txt(un)
        messagebox.showinfo("Dışa aktarıldı", f"Rapor kaydedildi:\n{path}")

    # -------- LOG SEKMESİ (admin) --------
    def _tab_logs(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text="📜 Loglar")
        ttk.Button(f, text="Yenile", command=lambda: self._load_logs(tree)).pack(anchor="w", pady=(0, 8))
        cols = ("ts", "user", "action", "detail")
        tree = ttk.Treeview(f, columns=cols, show="headings", height=20)
        for c, t, w in [("ts", "Tarih", 160), ("user", "Kullanıcı", 110),
                        ("action", "İşlem", 130), ("detail", "Detay", 320)]:
            tree.heading(c, text=t)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True)
        self._load_logs(tree)

    def _load_logs(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        for r in self.logger.fetch():
            tree.insert("", "end", values=(r["ts"], r["username"], r["action"], r["detail"]))

    # -------- KULLANICI YÖNETİMİ (admin) --------
    def _tab_users(self, nb):
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text="👤 Kullanıcılar")

        bar = ttk.Frame(f)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(bar, text="Yenile", command=lambda: self._load_users(tree)).pack(side="left")

        ttk.Label(bar, text="  Rol değiştir →").pack(side="left", padx=6)
        role_cb = ttk.Combobox(bar, values=["guest", "analyst", "admin"],
                               state="readonly", width=10)
        role_cb.set("analyst")
        role_cb.pack(side="left")

        def change_role():
            sel = tree.selection()
            if not sel:
                return
            un = tree.item(sel[0])["values"][1]
            self.auth.set_role(un, role_cb.get())
            self._load_users(tree)

        def toggle():
            sel = tree.selection()
            if not sel:
                return
            un = tree.item(sel[0])["values"][1]
            self.auth.toggle_active(un)
            self._load_users(tree)

        ttk.Button(bar, text="Uygula", command=change_role).pack(side="left", padx=6)
        ttk.Button(bar, text="Aktif/Pasif", command=toggle).pack(side="left")

        cols = ("id", "user", "role", "created", "active")
        tree = ttk.Treeview(f, columns=cols, show="headings", height=18)
        for c, t, w in [("id", "ID", 50), ("user", "Kullanıcı", 150),
                        ("role", "Rol", 100), ("created", "Oluşturma", 170),
                        ("active", "Aktif", 70)]:
            tree.heading(c, text=t)
            tree.column(c, width=w)
        tree.pack(fill="both", expand=True)
        self._load_users(tree)

    def _load_users(self, tree):
        for i in tree.get_children():
            tree.delete(i)
        for r in self.auth.list_users():
            tree.insert("", "end", values=(
                r["id"], r["username"], r["role"], r["created"],
                "Evet" if r["active"] else "Hayır"))


if __name__ == "__main__":
    App().mainloop()

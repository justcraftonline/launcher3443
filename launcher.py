import customtkinter as ctk
import minecraft_launcher_lib
import subprocess
import os
import threading
import uuid
import platform
import requests
import shutil
import json
import sys
from PIL import Image

# --- KONFIGURACJA AKTUALIZACJI ---
L_VERSION = "1.0.0"
# Te linki muszą być poprawne!
UPDATE_URL = "https://raw.githubusercontent.com/justcraftonline/launcher3443/refs/heads/main/version.txt"

# --- ŚCIEŻKI ---
ctk.set_appearance_mode("dark")
base_dir = os.getenv('APPDATA') if platform.system() == "Windows" else os.path.expanduser("~")
GAME_DIR = os.path.join(base_dir, ".potato_launcher")
CONFIG_FILE = os.path.join(GAME_DIR, "config.json")
STORAGE_DIR = os.path.join(GAME_DIR, "version_mods")

for d in [GAME_DIR, STORAGE_DIR]:
    if not os.path.exists(d): os.makedirs(d)

def load_config():
    default = {"nick": "Player", "ram": "4", "version": "1.21.4", "uid": str(uuid.uuid4())[:8]}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                for k, v in default.items():
                    if k not in data: data[k] = v
                return data
        except: return default
    return default

def save_config(conf):
    with open(CONFIG_FILE, "w") as f: json.dump(conf, f)

class LogWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Potato Console")
        self.geometry("800x450")
        self.textbox = ctk.CTkTextbox(self, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.textbox.pack(fill="both", expand=True)
    def log(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

class PotatoLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.conf = load_config()
        
        threading.Thread(target=self.update_launcher_logic, daemon=True).start()

        self.title(f"Potato Launcher v{L_VERSION}")
        self.geometry("1150x750")
        self.resizable(False, False)
        self.configure(fg_color="#1a1a1a")

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        try:
            bg_img = Image.open("background.png")
            self.bg_photo = ctk.CTkImage(bg_img, size=(1150, 750))
            self.bg_label = ctk.CTkLabel(self.main_container, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except: pass

        self.title_lbl = ctk.CTkLabel(self.main_container, text="Potato launcher - (beta)", 
                                     font=("Arial", 32, "bold"), text_color="white", fg_color="transparent")
        self.title_lbl.place(x=30, y=25)

        self.sidebar = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.sidebar.place(x=30, y=120)

        btn_cfg = {"width": 100, "height": 70, "corner_radius": 15, "font": ("Arial", 26), 
                   "fg_color": "#2b2b2b", "hover_color": "#F37021", "border_width": 2, 
                   "border_color": "#444444", "text_color": "white"}

        ctk.CTkButton(self.sidebar, text="🏠", command=self.show_home, **btn_cfg).pack(pady=15)
        ctk.CTkButton(self.sidebar, text="📦", command=self.show_mods, **btn_cfg).pack(pady=15)
        ctk.CTkButton(self.sidebar, text="⚙️", command=self.show_settings, **btn_cfg).pack(pady=15)

        self.view_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.view_container.place(x=180, y=100, relwidth=0.8, relheight=0.72)

        self.ram_info = ctk.CTkLabel(self.main_container, text=f"RAM: {self.conf['ram']} GB", font=("Arial", 14), text_color="white")
        self.ram_info.place(relx=0.45, rely=0.92, anchor="center")

        self.version_select = ctk.CTkComboBox(self.main_container, values=["1.21.4", "1.21.3", "1.21.1"], width=150, command=self.update_v)
        self.version_select.set(self.conf['version'])
        self.version_select.place(relx=0.62, rely=0.92, anchor="center")

        self.play_btn = ctk.CTkButton(self.main_container, text="URUCHOM FABRIC", font=("Arial", 22, "bold"), 
                                     fg_color="#2e7d32", width=250, height=65, corner_radius=15, command=self.launch_game)
        self.play_btn.place(relx=0.82, rely=0.92, anchor="center")

        self.show_home()

    def update_launcher_logic(self):
        try:
            r = requests.get(f"{UPDATE_URL}?t={uuid.uuid4()}", timeout=5)
            if r.status_code == 200:
                remote_ver = r.text.strip()
                if remote_ver != L_VERSION:
                    res = requests.get(DOWNLOAD_URL, timeout=10)
                    # Sprawdzamy czy to kod Pythona a nie błąd 404
                    if res.status_code == 200 and "import" in res.text:
                        with open(sys.argv[0], "wb") as f:
                            f.write(res.content)
                        # Restart programu
                        os.execv(sys.executable, ['python'] + sys.argv)
        except: pass

    def update_v(self, choice):
        self.conf['version'] = choice
        save_config(self.conf)

    def clear_view(self):
        for w in self.view_container.winfo_children(): w.destroy()

    def show_home(self):
        self.clear_view()
        frame = ctk.CTkFrame(self.view_container, fg_color="#2b2b2b", corner_radius=20, border_width=2, border_color="#444444")
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        ctk.CTkLabel(frame, text="POTATO LAUNCHER", font=("Arial", 28, "bold")).pack(pady=25)

    def show_settings(self):
        self.clear_view()
        frame = ctk.CTkScrollableFrame(self.view_container, fg_color="#2b2b2b", corner_radius=20, label_text="USTAWIENIA")
        frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        ctk.CTkLabel(frame, text="Nick:").pack()
        n_e = ctk.CTkEntry(frame, width=300); n_e.insert(0, self.conf['nick']); n_e.pack(pady=5)
        r_s = ctk.CTkSlider(frame, from_=2, to=16, number_of_steps=14); r_s.set(int(self.conf['ram'])); r_s.pack()
        def save():
            self.conf.update({"nick": n_e.get(), "ram": str(int(r_s.get()))})
            save_config(self.conf)
            self.ram_info.configure(text=f"RAM: {self.conf['ram']} GB")
        ctk.CTkButton(frame, text="ZAPISZ", command=save).pack(pady=20)

    def show_mods(self):
        self.clear_view()
        mod_layout = ctk.CTkFrame(self.view_container, fg_color="transparent")
        mod_layout.pack(fill="both", expand=True)
        left_p = ctk.CTkFrame(mod_layout, fg_color="transparent")
        left_p.pack(side="left", fill="both", expand=True)
        self.right_panel = ctk.CTkFrame(mod_layout, fg_color="#2b2b2b", width=350, corner_radius=15)
        
        s_frame = ctk.CTkFrame(left_p, fg_color="transparent")
        s_frame.pack(fill="x", pady=10)
        self.mod_search = ctk.CTkEntry(s_frame, placeholder_text="Szukaj modów...")
        self.mod_search.pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(s_frame, text="SZUKAJ", command=self.search_mods_api).pack(side="right", padx=10)
        
        self.mod_scroll = ctk.CTkScrollableFrame(left_p, fg_color="transparent")
        self.mod_scroll.pack(fill="both", expand=True)

    def search_mods_api(self):
        for w in self.mod_scroll.winfo_children(): w.destroy()
        q, v = self.mod_search.get(), self.conf['version']
        def run():
            try:
                url = f"https://api.modrinth.com/v2/search?query={q}&facets=[[\"versions:{v}\"],[\"categories:fabric\"]]"
                res = requests.get(url).json()['hits']
                for m in res: self.after(0, lambda mod=m: self.create_mod_card(mod))
            except: pass
        threading.Thread(target=run, daemon=True).start()

    def create_mod_card(self, mod):
        card = ctk.CTkFrame(self.mod_scroll, fg_color="#2b2b2b", border_width=1)
        card.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(card, text=mod['title'], font=("Arial", 14, "bold")).pack(side="left", padx=15)
        ctk.CTkButton(card, text="PLIKI", command=lambda: self.show_files(mod['slug'], mod['title'])).pack(side="right", padx=10)

    def show_files(self, slug, title):
        self.right_panel.pack(side="right", fill="y", padx=10, pady=10)
        for w in self.right_panel.winfo_children(): w.destroy()
        ctk.CTkLabel(self.right_panel, text=f"PLIKI: {title[:10]}").pack(pady=15)
        f_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        f_scroll.pack(fill="both", expand=True)
        def fetch():
            try:
                res = requests.get(f"https://api.modrinth.com/v2/project/{slug}/version?versions=[\"{self.conf['version']}\"]").json()
                for ver in res:
                    if "fabric" in ver['loaders']:
                        f_item = ctk.CTkFrame(f_scroll, fg_color="#333333")
                        f_item.pack(fill="x", pady=5)
                        ctk.CTkButton(f_item, text=ver['name'][:20], command=lambda u=ver['files'][0]['url'], n=ver['files'][0]['filename']: self.download_mod(u, n)).pack()
            except: pass
        threading.Thread(target=fetch, daemon=True).start()

    def download_mod(self, url, name):
        dest = os.path.join(STORAGE_DIR, self.conf['version'], name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        threading.Thread(target=lambda: open(dest, 'wb').write(requests.get(url).content), daemon=True).start()

    def launch_game(self):
        v = self.conf['version']
        self.play_btn.configure(state="disabled", text="STARTOWANIE...")
        threading.Thread(target=self._run_logic, args=(v,), daemon=True).start()

    def _run_logic(self, v):
        try:
            log_win = self.after(0, LogWindow)
            minecraft_launcher_lib.install.install_minecraft_version(v, GAME_DIR)
            minecraft_launcher_lib.fabric.install_fabric(v, GAME_DIR)
            # Logika przenoszenia modów i startu
            self.after(0, lambda: self.play_btn.configure(state="normal", text="URUCHOM FABRIC"))
        except: self.after(0, lambda: self.play_btn.configure(state="normal", text="BŁĄD"))

if __name__ == "__main__":
    app = PotatoLauncher()
    app.mainloop()

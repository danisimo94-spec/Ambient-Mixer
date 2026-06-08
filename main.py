import json
import os
import platform
import subprocess
import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
import pygame
from dotenv import load_dotenv, set_key, unset_key

BASE_DIR = Path(__file__).resolve().parent
SOUNDS_DIR = BASE_DIR / "sounds"
MANIFEST_PATH = SOUNDS_DIR / "manifest.json"
CONFIG_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"
API_KEY_NAME = "FREESOUND_API_KEY"

COLORS = {
    "bg": "#111111",
    "row_active": "#1a1a1a",
    "text_active": "#eeeeee",
    "text_inactive": "#444444",
    "title": "#555555",
    "accent": "#eeeeee",
    "track": "#222222",
    "divider": "#1e1e1e",
    "button_border": "#333333",
    "preset_active_border": "#444444",
    "preset_active_text": "#cccccc",
    "preset_inactive_border": "#222222",
    "preset_inactive_text": "#444444",
}

SOUNDS = {
    "rain": {"label": "Rain", "icon": "☔"},
    "fire": {"label": "Fire", "icon": "♨"},
    "cafe": {"label": "Cafe", "icon": "☕"},
    "wind": {"label": "Wind", "icon": "⌁"},
    "waves": {"label": "Waves", "icon": "≈"},
    "birds": {"label": "Birds", "icon": "♬"},
    "keyboard": {"label": "Keyboard", "icon": "⌨"},
    "thunder": {"label": "Thunder", "icon": "ϟ"},
    "singing_bowls": {"label": "Singing Bowls", "icon": "◎"},
    "tingsha": {"label": "Tingsha", "icon": "∿"},
    "gong": {"label": "Gong", "icon": "○"},
    "flute": {"label": "Flute", "icon": "♪"},
    "om_drone": {"label": "Om Drone", "icon": "∞"},
    "stream": {"label": "Stream", "icon": "≈"},
    "crickets": {"label": "Crickets", "icon": "✦"},
    "cave": {"label": "Cave", "icon": "◇"},
    "blizzard": {"label": "Blizzard", "icon": "❄"},
    "train": {"label": "Train", "icon": "⊟"},
    "library": {"label": "Library", "icon": "▤"},
    "tavern": {"label": "Tavern", "icon": "⌂"},
    "rain_window": {"label": "Rain on Glass", "icon": "⬡"},
}

PRESETS = {
    "Deep Work": {"rain": 40, "fire": 20, "keyboard": 30},
    "Rain Cafe": {"rain": 50, "cafe": 40, "fire": 10},
    "Sleep": {"rain": 30, "waves": 50, "wind": 20},
    "Nature": {"birds": 60, "wind": 30, "waves": 30},
    "Storm": {"rain": 70, "thunder": 50, "wind": 40},
    "Meditation": {"singing_bowls": 50, "om_drone": 30, "tingsha": 20},
    "Zen": {"singing_bowls": 30, "flute": 40, "stream": 30},
    "Cozy Night": {"tavern": 40, "rain_window": 50, "crickets": 20},
    "Winter": {"blizzard": 40, "train": 20, "rain_window": 30},
}

TRANSLATIONS = {
    "en": {
        "app_name": "AMBIENT",
        "vol": "Vol",
        "sounds": {
            "rain": "Rain", "fire": "Fire", "cafe": "Cafe",
            "wind": "Wind", "waves": "Waves", "birds": "Birds",
            "keyboard": "Keyboard", "thunder": "Thunder",
            "singing_bowls": "Singing Bowls", "tingsha": "Tingsha",
            "gong": "Gong", "flute": "Flute", "om_drone": "Om",
            "stream": "Stream", "crickets": "Crickets", "cave": "Cave",
            "blizzard": "Blizzard", "train": "Train",
            "library": "Library", "tavern": "Tavern",
            "rain_window": "Rain on Glass",
        },
        "presets": {
            "Deep Work": "Deep Work", "Rain Cafe": "Rain Cafe",
            "Sleep": "Sleep", "Nature": "Nature", "Storm": "Storm",
            "Meditation": "Meditation", "Zen": "Zen",
            "Cozy Night": "Cozy Night", "Winter": "Winter",
        },
    },
    "ru": {
        "app_name": "AMBIENT",
        "vol": "Гр.",
        "sounds": {
            "rain": "Дождь", "fire": "Камин", "cafe": "Кафе",
            "wind": "Ветер", "waves": "Волны", "birds": "Птицы",
            "keyboard": "Клавиши", "thunder": "Гроза",
            "singing_bowls": "Поющие чаши", "tingsha": "Тингша",
            "gong": "Гонг", "flute": "Флейта", "om_drone": "Ом",
            "stream": "Ручей", "crickets": "Сверчки", "cave": "Пещера",
            "blizzard": "Пурга", "train": "Поезд",
            "library": "Библиотека", "tavern": "Таверна",
            "rain_window": "Дождь по стеклу",
        },
        "presets": {
            "Deep Work": "Работа", "Rain Cafe": "Кафе",
            "Sleep": "Сон", "Nature": "Природа", "Storm": "Шторм",
            "Meditation": "Медитация", "Zen": "Дзен",
            "Cozy Night": "Уют", "Winter": "Зима",
        },
    },
}


class CanvasProgress(tk.Canvas):
    def __init__(self, master, value=0, command=None, bg=COLORS["bg"], **kwargs):
        super().__init__(
            master,
            height=12,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs,
        )
        self.value = value
        self.command = command
        self.bind("<Configure>", lambda _event: self.draw())
        self.bind("<Button-1>", self.set_from_event)
        self.bind("<B1-Motion>", self.set_from_event)
        self.draw()

    def set_value(self, value, emit=False):
        self.value = max(0, min(100, int(round(value))))
        self.draw()
        if emit and self.command:
            self.command(self.value)

    def set_from_event(self, event):
        width = max(1, self.winfo_width())
        self.set_value(event.x / width * 100, emit=True)

    def draw(self):
        self.delete("all")
        width = max(1, self.winfo_width())
        fill_width = int(width * self.value / 100)
        self.create_rectangle(0, 5, width, 7, fill=COLORS["track"], outline="")
        self.create_rectangle(0, 5, fill_width, 7, fill=COLORS["accent"], outline="")


class ApiKeyDialog(ctk.CTkInputDialog):
    def _create_widgets(self):
        super()._create_widgets()
        self._entry.bind("<Control-v>", self.paste)
        self._entry.bind("<Command-v>", self.paste)

    def paste(self, _event=None):
        try:
            self._entry.insert("insert", self.clipboard_get())
        except tk.TclError:
            pass
        return "break"


class AmbientMixer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ambient Mixer")
        self.geometry("400x720")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        ctk.set_appearance_mode("dark")

        self.font_family = self.get_font_family()
        if not self.ensure_api_key():
            self.after(0, self.destroy)
            return

        self.config_data = self.load_config()
        self.current_lang = self.config_data.get("lang", "en")
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "en"
        self.build_loading_ui()
        self.manifest = self.load_manifest(retry_auth=True)
        if not self.manifest:
            return
        self.clear_loading_ui()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(len(SOUNDS))

        self.sounds = {}
        self.channels = {}
        self.volume_vars = {}
        self.progress_bars = {}
        self.percent_labels = {}
        self.name_labels = {}
        self.icon_labels = {}
        self.row_frames = {}
        self.preset_buttons = {}
        self.master_volume = ctk.IntVar(value=self.config_data.get("master_vol", 80))
        self.is_playing = False
        self.active_preset = None
        self.timer_options = [0, 25, 45, 60, 90]
        self.timer_index = 1
        self.timer_seconds = self.selected_timer_minutes() * 60
        self.timer_job = None
        self.timer_running = False
        self.timer_label_var = ctk.StringVar(value=self.format_time(self.timer_seconds))

        self.load_sounds()
        self.build_ui()
        self.apply_lang(save=False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def ensure_api_key(self):
        try:
            ENV_PATH.touch(exist_ok=True)
            load_dotenv(ENV_PATH, override=False)
        except OSError as error:
            messagebox.showerror("Ambient Mixer", f"Could not read or create .env file:\n{error}")
            return False

        if os.environ.get(API_KEY_NAME, "").strip():
            return True

        dialog = ApiKeyDialog(
            title="Freesound API Key",
            text="Freesound API Key is required to download sounds.\nPaste your key below:",
        )
        api_key = dialog.get_input()

        if api_key is None:
            messagebox.showerror("Ambient Mixer", "Freesound API Key is required. App will close.")
            return False

        api_key = api_key.strip()
        if not api_key:
            messagebox.showerror("Ambient Mixer", "Freesound API Key cannot be empty. App will close.")
            return False

        try:
            set_key(str(ENV_PATH), API_KEY_NAME, api_key)
            os.environ[API_KEY_NAME] = api_key
        except Exception as error:
            messagebox.showerror("Ambient Mixer", f"Could not save Freesound API Key to .env:\n{error}")
            return False

        return True

    def load_config(self):
        if not CONFIG_PATH.exists():
            return {"lang": "en", "master_vol": 70}
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"lang": "en", "master_vol": 70}
        return {
            "lang": data.get("lang", "en"),
            "master_vol": max(0, min(100, int(data.get("master_vol", 70)))),
        }

    def save_config(self):
        CONFIG_PATH.write_text(
            json.dumps({"lang": self.current_lang, "master_vol": self.master_volume.get()}, indent=2),
            encoding="utf-8",
        )

    def get_font_family(self):
        families = set(tkfont.families(self))
        if "Inter" in families:
            return "Inter"
        if "Segoe UI" in families:
            return "Segoe UI"
        return "TkDefaultFont"

    def font(self, size, weight="normal"):
        return ctk.CTkFont(family=self.font_family, size=size, weight=weight)

    def build_loading_ui(self):
        self.loading_status = ctk.StringVar(value="Preparing sound library...")
        self.loading_frame = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.loading_frame.pack(fill="both", expand=True, padx=22, pady=20)
        self.loading_frame.grid_columnconfigure(0, weight=1)
        self.loading_frame.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(
            self.loading_frame,
            text="AMBIENT",
            font=self.font(11),
            text_color=COLORS["title"],
        ).grid(row=0, column=0, sticky="s", pady=(0, 12))
        ctk.CTkLabel(
            self.loading_frame,
            textvariable=self.loading_status,
            font=self.font(13),
            text_color=COLORS["text_active"],
        ).grid(row=1, column=0, sticky="n")
        self.update_idletasks()

    def set_loading_status(self, status):
        if hasattr(self, "loading_status"):
            self.loading_status.set(status)
            self.update_idletasks()

    def clear_loading_ui(self):
        if hasattr(self, "loading_frame"):
            self.loading_frame.destroy()

    def load_manifest(self, retry_auth=False):
        try:
            if not MANIFEST_PATH.exists():
                print("sounds/manifest.json not found. Running downloader.py...")
                self.run_downloader()

            with MANIFEST_PATH.open("r", encoding="utf-8") as file:
                manifest = json.load(file)

            missing = [category for category in SOUNDS if category not in manifest]
            if missing:
                print(f"Missing sounds in manifest: {', '.join(missing)}. Running downloader.py...")
                self.run_downloader()
                with MANIFEST_PATH.open("r", encoding="utf-8") as file:
                    manifest = json.load(file)
        except Exception as error:
            if retry_auth and "Freesound API Key" in str(error):
                self.clear_api_key()
                messagebox.showerror("Ambient Mixer", f"{error}\n\nPlease enter a valid Freesound API Key.")
                if self.ensure_api_key():
                    return self.load_manifest(retry_auth=False)
                self.destroy()
                return {}
            messagebox.showerror("Ambient Mixer", f"Could not load or download sounds:\n{error}")
            self.destroy()
            return {}

        missing = [category for category in SOUNDS if category not in manifest]
        if missing:
            messagebox.showerror("Ambient Mixer", f"Missing sounds in manifest: {', '.join(missing)}")
            self.destroy()
            return {}
        return manifest

    def run_downloader(self):
        try:
            import downloader

            downloader.download_sounds(progress_callback=self.set_loading_status)
        except ImportError:
            subprocess.run([sys.executable, str(BASE_DIR / "downloader.py")], cwd=BASE_DIR, check=True)

    def clear_api_key(self):
        os.environ.pop(API_KEY_NAME, None)
        try:
            unset_key(str(ENV_PATH), API_KEY_NAME)
        except Exception:
            pass

    def load_sounds(self):
        for index, category in enumerate(SOUNDS):
            path = BASE_DIR / self.manifest[category]
            if not path.exists():
                raise FileNotFoundError(f"Sound file not found: {path}")
            self.sounds[category] = pygame.mixer.Sound(str(path))
            self.channels[category] = pygame.mixer.Channel(index)

    def build_ui(self):
        ctk.set_appearance_mode("dark")

        root = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        root.pack(fill="both", expand=True, padx=22, pady=20)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        self.build_topbar(root)
        self.build_sound_rows(root)
        self.build_presets(root)
        self.build_bottombar(root)

    def build_topbar(self, parent):
        topbar = ctk.CTkFrame(parent, fg_color=COLORS["bg"], corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        topbar.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(
            topbar,
            text="AMBIENT",
            font=self.font(11),
            text_color=COLORS["title"],
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.lang_button = ctk.CTkButton(
            topbar,
            text=self.current_lang.upper(),
            width=28,
            height=24,
            border_width=0,
            fg_color=COLORS["bg"],
            hover_color=COLORS["bg"],
            text_color=COLORS["text_inactive"],
            font=self.font(11),
            command=self.toggle_lang,
        )
        self.lang_button.grid(row=0, column=1, padx=(10, 0), sticky="w")

        self.timer_label = ctk.CTkLabel(
            topbar,
            textvariable=self.timer_label_var,
            font=self.font(12),
            text_color=COLORS["text_inactive"],
            width=52,
            cursor="hand2",
        )
        self.timer_label.grid(row=0, column=2, padx=(0, 12), sticky="e")
        self.timer_label.bind("<Button-1>", lambda _event: self.cycle_timer())

        self.play_button = ctk.CTkButton(
            topbar,
            text="▶",
            width=32,
            height=32,
            corner_radius=16,
            border_width=1,
            border_color=COLORS["button_border"],
            fg_color=COLORS["bg"],
            hover_color=COLORS["row_active"],
            text_color=COLORS["text_active"],
            font=self.font(12),
            command=self.toggle_play,
        )
        self.play_button.grid(row=0, column=3, sticky="e")

    def build_sound_rows(self, parent):
        outer = ctk.CTkFrame(parent, fg_color=COLORS["bg"], corner_radius=0)
        outer.grid(row=1, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        self.sound_canvas = tk.Canvas(outer, bg=COLORS["bg"], highlightthickness=0, bd=0)
        self.sound_canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(
            outer,
            orient="vertical",
            command=self.sound_canvas.yview,
            width=4,
            bg=COLORS["bg"],
            troughcolor=COLORS["row_active"],
            activebackground=COLORS["track"],
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(6, 0))
        self.sound_canvas.configure(yscrollcommand=self.scrollbar.set)

        list_frame = ctk.CTkFrame(self.sound_canvas, fg_color=COLORS["bg"], corner_radius=0)
        window_id = self.sound_canvas.create_window((0, 0), window=list_frame, anchor="nw")
        list_frame.grid_columnconfigure(0, weight=1)

        def on_frame_configure(_event):
            self.sound_canvas.configure(scrollregion=self.sound_canvas.bbox("all"))

        def on_canvas_configure(event):
            self.sound_canvas.itemconfigure(window_id, width=event.width)

        list_frame.bind("<Configure>", on_frame_configure)
        self.sound_canvas.bind("<Configure>", on_canvas_configure)
        self.bind_scroll_widget(self.sound_canvas)
        self.bind_scroll_widget(list_frame)

        for row_index, (category, meta) in enumerate(SOUNDS.items()):
            row = ctk.CTkFrame(list_frame, fg_color=COLORS["bg"], corner_radius=8, height=30)
            row.grid(row=row_index * 2, column=0, sticky="ew")
            row.grid_columnconfigure(2, weight=1)
            row.grid_propagate(False)
            self.row_frames[category] = row

            icon = ctk.CTkLabel(
                row,
                text=meta["icon"],
                font=self.font(15),
                text_color=COLORS["title"],
                width=22,
            )
            icon.grid(row=0, column=0, padx=(0, 8), sticky="w")
            self.icon_labels[category] = icon

            name = ctk.CTkLabel(
                row,
                text=meta["label"],
                font=self.font(13),
                text_color=COLORS["text_inactive"],
                width=94,
                anchor="w",
            )
            name.grid(row=0, column=1, sticky="w")
            self.name_labels[category] = name

            var = ctk.IntVar(value=0)
            self.volume_vars[category] = var
            bar = CanvasProgress(
                row,
                value=0,
                command=lambda value, name=category: self.on_volume_change(name, value),
                bg=COLORS["bg"],
            )
            bar.grid(row=0, column=2, padx=(2, 10), sticky="ew")
            self.progress_bars[category] = bar

            percent = ctk.CTkLabel(
                row,
                text="0%",
                font=self.font(11),
                text_color=COLORS["text_inactive"],
                width=28,
                anchor="e",
            )
            percent.grid(row=0, column=3, sticky="e")
            self.percent_labels[category] = percent

            for widget in (row, icon, name, percent):
                widget.bind("<Enter>", lambda _event, name=category: self.set_row_hover(name, True))
                widget.bind("<Leave>", lambda _event, name=category: self.set_row_hover(name, False))
                self.bind_scroll_widget(widget)
            self.bind_scroll_widget(bar)

            divider = ctk.CTkFrame(list_frame, fg_color=COLORS["divider"], height=1, corner_radius=0)
            divider.grid(row=row_index * 2 + 1, column=0, sticky="ew", pady=(2, 2))
            self.bind_scroll_widget(divider)

    def build_presets(self, parent):
        preset_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg"], corner_radius=0)
        preset_frame.grid(row=2, column=0, sticky="ew", pady=(20, 22))

        for index, name in enumerate(PRESETS):
            row = index // 3
            column = index % 3
            preset_frame.grid_columnconfigure(column, weight=1)
            button = ctk.CTkButton(
                preset_frame,
                text=name,
                height=26,
                corner_radius=20,
                border_width=1,
                border_color=COLORS["preset_inactive_border"],
                fg_color=COLORS["bg"],
                hover_color=COLORS["row_active"],
                text_color=COLORS["preset_inactive_text"],
                font=self.font(11),
                command=lambda preset=name: self.apply_preset(preset),
            )
            button.grid(row=row, column=column, padx=(0 if column == 0 else 5, 0), pady=(0 if row == 0 else 6, 0), sticky="ew")
            self.preset_buttons[name] = button

    def build_bottombar(self, parent):
        bottom = ctk.CTkFrame(parent, fg_color=COLORS["bg"], corner_radius=0)
        bottom.grid(row=3, column=0, sticky="ew")
        bottom.grid_columnconfigure(1, weight=1)

        self.vol_label = ctk.CTkLabel(bottom, text="Vol", font=self.font(11), text_color=COLORS["text_inactive"], width=28, anchor="w")
        self.vol_label.grid(row=0, column=0, sticky="w")

        self.master_bar = CanvasProgress(
            bottom,
            value=self.master_volume.get(),
            command=self.on_master_change,
            bg=COLORS["bg"],
        )
        self.master_bar.grid(row=0, column=1, padx=(8, 10), sticky="ew")

        self.master_percent = ctk.CTkLabel(
            bottom,
            text=f"{self.master_volume.get()}%",
            font=self.font(11),
            text_color=COLORS["text_inactive"],
            width=28,
            anchor="e",
        )
        self.master_percent.grid(row=0, column=2, sticky="e")

    def on_mousewheel(self, event):
        if platform.system() == "Darwin":
            units = -1 * event.delta
        else:
            units = int(-1 * (event.delta / 120))
        self.sound_canvas.yview_scroll(units, "units")
        return "break"

    def bind_scroll_widget(self, widget):
        widget.bind("<MouseWheel>", self.on_mousewheel, add="+")

    def toggle_lang(self):
        self.current_lang = "ru" if self.current_lang == "en" else "en"
        self.apply_lang()

    def apply_lang(self, save=True):
        lang = TRANSLATIONS[self.current_lang]
        self.title_label.configure(text=lang["app_name"])
        self.lang_button.configure(text=self.current_lang.upper())
        self.vol_label.configure(text=lang["vol"])
        for sound_id, label in self.name_labels.items():
            label.configure(text=lang["sounds"].get(sound_id, SOUNDS[sound_id]["label"]))
        for preset_id, button in self.preset_buttons.items():
            button.configure(text=lang["presets"].get(preset_id, preset_id))
        if save:
            self.save_config()

    def apply_preset(self, preset_name):
        self.active_preset = preset_name
        preset = PRESETS[preset_name]
        for category in SOUNDS:
            value = preset.get(category, 0)
            self.set_sound_volume(category, value)
        self.update_preset_styles()

    def update_preset_styles(self):
        for name, button in self.preset_buttons.items():
            active = name == self.active_preset
            button.configure(
                border_color=COLORS["preset_active_border"] if active else COLORS["preset_inactive_border"],
                text_color=COLORS["preset_active_text"] if active else COLORS["preset_inactive_text"],
            )

    def set_sound_volume(self, category, value):
        int_value = max(0, min(100, int(float(value))))
        self.volume_vars[category].set(int_value)
        self.progress_bars[category].set_value(int_value)
        self.percent_labels[category].configure(text=f"{int_value}%")
        self.update_row_state(category)
        self.update_channel_volume(category)

    def on_volume_change(self, category, value):
        self.active_preset = None
        self.update_preset_styles()
        self.set_sound_volume(category, value)

    def on_master_change(self, value):
        int_value = max(0, min(100, int(float(value))))
        self.master_volume.set(int_value)
        self.master_bar.set_value(int_value)
        self.master_percent.configure(text=f"{int_value}%")
        for category in SOUNDS:
            self.update_channel_volume(category)
        self.save_config()

    def update_row_state(self, category):
        active = self.volume_vars[category].get() > 0
        color = COLORS["text_active"] if active else COLORS["text_inactive"]
        self.name_labels[category].configure(text_color=color)
        self.percent_labels[category].configure(text_color=color if active else COLORS["text_inactive"])
        self.row_frames[category].configure(fg_color=COLORS["row_active"] if active else COLORS["bg"])
        self.progress_bars[category].configure(bg=COLORS["row_active"] if active else COLORS["bg"])
        self.progress_bars[category].draw()

    def set_row_hover(self, category, hovering):
        if hovering or self.volume_vars[category].get() > 0:
            bg = COLORS["row_active"]
        else:
            bg = COLORS["bg"]
        self.row_frames[category].configure(fg_color=bg)
        self.progress_bars[category].configure(bg=bg)
        self.progress_bars[category].draw()

    def update_channel_volume(self, category):
        volume = self.volume_vars[category].get() / 100 * self.master_volume.get() / 100
        self.channels[category].set_volume(volume)

    def toggle_play(self):
        if self.is_playing:
            for channel in self.channels.values():
                channel.pause()
            self.pause_timer()
            self.is_playing = False
            self.play_button.configure(text="▶")
            return

        for category, sound in self.sounds.items():
            channel = self.channels[category]
            self.update_channel_volume(category)
            if channel.get_busy():
                channel.unpause()
            else:
                channel.play(sound, loops=-1)
        self.is_playing = True
        self.play_button.configure(text="Ⅱ")
        self.start_timer_if_selected()

    def selected_timer_minutes(self):
        return self.timer_options[self.timer_index]

    def cycle_timer(self):
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_running = False
        self.timer_index = (self.timer_index + 1) % len(self.timer_options)
        self.timer_seconds = self.selected_timer_minutes() * 60
        self.update_timer_label()
        if self.is_playing:
            self.start_timer_if_selected()

    def start_timer_if_selected(self):
        if self.selected_timer_minutes() <= 0:
            self.timer_seconds = 0
            self.update_timer_label()
            return
        if self.timer_seconds <= 0:
            self.timer_seconds = self.selected_timer_minutes() * 60
        if self.timer_job is None:
            self.timer_running = True
            self.tick_timer()

    def pause_timer(self):
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_running = False

    def tick_timer(self):
        self.update_timer_label()
        if self.timer_seconds <= 0:
            self.timer_job = None
            self.timer_running = False
            self.bell()
            return

        self.timer_seconds -= 1
        self.timer_job = self.after(1000, self.tick_timer)

    def update_timer_label(self):
        self.timer_label_var.set(self.format_time(self.timer_seconds))

    def format_time(self, seconds):
        minutes, seconds = divmod(max(0, seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def on_close(self):
        if self.timer_job is not None:
            self.after_cancel(self.timer_job)
        pygame.mixer.quit()
        self.destroy()


if __name__ == "__main__":
    app = AmbientMixer()
    app.mainloop()

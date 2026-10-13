#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 MrPrompt Notatnik
================================================================================
 Nowoczesny notatnik inspirowany Windows Notatnikiem wzbogacony o:
  - Sprawdzanie pisowni w języku polskim z podpowiedziami pod prawym przyciskiem myszy
  - Zaznaczanie tekstu markerem w różnych kolorach
  - Formatowanie tekstu: Pogrubienie (Ctrl+B), Kursywa (Ctrl+I), Podkreślenie (Ctrl+U)
  - Listy punktowane z automatyczną kontynuacją
  - Zapis do RTF (z formatowaniem — otwiera się w Wordzie/WordPadzie) oraz do TXT
  - Ikony Font Awesome (menu i pasek narzędzi)
================================================================================
"""

import codecs
import ctypes
import datetime
import json
import os
import re
import sys
import threading
import tkinter as tk
import webbrowser
from itertools import islice
from bisect import bisect_right
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter import font as tkfont

import lena

try:
    from spylls.hunspell import Dictionary
    SPELL_AVAILABLE = True
except ImportError:
    SPELL_AVAILABLE = False

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

APP_NAME = "MrPrompt Notatnik"
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 12

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FA_FONT_PATH = os.path.join(BASE_DIR, "fonts", "fa-solid-900.ttf")
DICT_BASE = os.path.join(BASE_DIR, "slownik", "pl_PL")
SETTINGS_PATH = os.path.join(BASE_DIR, "ustawienia.json")
USER_DICT_PATH = os.path.join(BASE_DIR, "slownik_uzytkownika.txt")
RECOVERY_DIR = os.path.join(BASE_DIR, "kopie_robocze")
RECOVERY_RTF = os.path.join(RECOVERY_DIR, "odzyskane.rtf")
RECOVERY_META = os.path.join(RECOVERY_DIR, "odzyskane.json")

# Paleta kolorów zakreślacza (marker)
HIGHLIGHT_PALETTE = [
    ("yellow", "Żółty", "#FFF59D", "#FFF9C4"),
    ("green",  "Zielony", "#C8E6C9", "#E8F5E9"),
    ("blue",   "Niebieski", "#BBDEFB", "#E3F2FD"),
    ("pink",   "Różowy", "#F8BBD0", "#FCE4EC"),
    ("orange", "Pomarańczowy", "#FFE0B2", "#FFF3E0")
]

# Motywy interfejsu (jasny / ciemny)
THEMES = {
    "light": dict(
        bg="#F7F8FA", hover="#E3E8EF", pressed="#D3DAE4", icon="#37474F", accent="#1E88E5",
        border="#D5DAE1", text="#1F2933", muted="#78909C", muted2="#90A4AE", hint="#455A64",
        active_fg="#000001", menu_bg="#FFFFFF", menu_active="#DCEBFA", editor_bg="#FFFFFF",
        editor_fg="#000000", select="#90CAF9", misspelled_bg="#FFCDD2", misspelled_fg="#B71C1C",
        link="#1565C0", find="#FFE082", find_cur="#FFB74D",
    ),
    "dark": dict(
        bg="#252A31", hover="#323945", pressed="#3E4756", icon="#C9D1D9", accent="#64B5F6",
        border="#3A424D", text="#E6EDF3", muted="#8B98A5", muted2="#6E7B88", hint="#9AA7B4",
        active_fg="#FFFFFF", menu_bg="#2D333B", menu_active="#3E4A5C", editor_bg="#1E2227",
        editor_fg="#E6EDF3", select="#35577E", misspelled_bg="#5B2A2E", misspelled_fg="#FF8A80",
        link="#64B5F6", find="#6B5B1F", find_cur="#A8721F",
    ),
}
THEME_ROLES = ("bg", "hover", "pressed", "icon", "border", "accent", "text", "muted", "muted2",
               "hint", "active_fg")
THEME = THEMES["light"]
UI_BG = UI_HOVER = UI_PRESSED = UI_ICON = UI_ACCENT = UI_BORDER = ""
UI_TEXT = UI_MUTED = UI_MUTED2 = UI_HINT = UI_ACTIVE_FG = ""


def set_theme(name: str):
    global THEME, UI_BG, UI_HOVER, UI_PRESSED, UI_ICON, UI_ACCENT, UI_BORDER
    global UI_TEXT, UI_MUTED, UI_MUTED2, UI_HINT, UI_ACTIVE_FG
    THEME = THEMES.get(name, THEMES["light"])
    UI_BG, UI_HOVER, UI_PRESSED = THEME["bg"], THEME["hover"], THEME["pressed"]
    UI_ICON, UI_ACCENT, UI_BORDER = THEME["icon"], THEME["accent"], THEME["border"]
    UI_TEXT, UI_MUTED, UI_MUTED2 = THEME["text"], THEME["muted"], THEME["muted2"]
    UI_HINT, UI_ACTIVE_FG = THEME["hint"], THEME["active_fg"]


set_theme("light")

# Ikony Font Awesome 6 Free (Solid) — nazwa -> kod znaku
FA = {
    "file": "\uf15b", "folder-open": "\uf07c", "save": "\uf0c7", "save-as": "\uf56e",
    "language": "\uf1ab", "exit": "\uf2f5", "undo": "\uf0e2", "redo": "\uf01e",
    "cut": "\uf0c4", "copy": "\uf0c5", "paste": "\uf0ea", "select-all": "\uf247",
    "bold": "\uf032", "italic": "\uf033", "underline": "\uf0cd", "marker": "\uf591",
    "eraser": "\uf12d", "list": "\uf0ca", "spell": "\uf891", "check": "\uf00c",
    "info": "\uf05a", "plus": "\uf067", "vault": "\uf187", "gear": "\uf013",
    "folder-plus": "\uf65e", "trash": "\uf1f8", "arrow-up": "\uf062", "arrow-down": "\uf063",
    "pen": "\uf304", "link": "\uf0c1", "external": "\uf35d",
    "task": "\uf14a", "search": "\uf002", "moon": "\uf186", "pin": "\uf08d",
    "history": "\uf1da", "sort-az": "\uf15d", "sort-za": "\uf881", "clone": "\uf24d",
    "font": "\uf031",
    "wand": "\uf0d0", "compress": "\uf066", "expand": "\uf065", "tasks": "\uf0ae",
    "align": "\uf036", "filesig": "\uf573", "key": "\uf084", "smile": "\uf118",
    "briefcase": "\uf0b1", "child": "\uf1ae",
}

ENCODINGS = [
    ("utf-8", "UTF-8"),
    ("utf-8-sig", "UTF-8 z BOM"),
    ("cp1250", "ANSI (Windows-1250)"),
    ("utf-16", "UTF-16"),
]
ENCODING_LABELS = dict(ENCODINGS)

WORD_RE = re.compile(r"[^\W_]+")
LINK_RE = re.compile(
    r"(?:https?://|ftp://|www\.)[^\s<>\"']+|[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
)
SKIP_RE = re.compile(r"(?:https?://|www\.)\S+|\S+@\S+\.\S+")
TASK_RE = re.compile(r"^(\s*)- \[([ xX])\] ?(.*)$")
TASK_PREFIX_RE = re.compile(r"^\s*- \[[ xX]\] ?")
PL_ALPHABET = "aąbcćdeęfghijklłmnńoópqrsśtuvwxyzźż"
FONT_TAGS = ("font_b", "font_i", "font_bi")
STYLE_TAGS = ("fmt_bold", "fmt_italic", "fmt_underline") + tuple(f"hl_{c[0]}" for c in HIGHLIGHT_PALETTE)


# =============================================================================
# RTF — zapis i odczyt
# =============================================================================
def _hex_to_rgb(color: str):
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def rtf_escape(text: str) -> str:
    out = []
    for ch in text:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == "{":
            out.append("\\{")
        elif ch == "}":
            out.append("\\}")
        elif ch == "\n":
            out.append("\\par\n")
        elif ch == "\t":
            out.append("\\tab ")
        elif ch == "\r":
            continue
        elif 32 <= o < 127:
            out.append(ch)
        else:
            raw = ch.encode("utf-16-le")
            for i in range(0, len(raw), 2):
                unit = raw[i] | (raw[i + 1] << 8)
                if unit > 32767:
                    unit -= 65536
                out.append(f"\\u{unit}?")
    return "".join(out)


_RTF_TOKEN = re.compile(
    r"\\([a-zA-Z]+)(-?\d+)? ?|\\'([0-9a-fA-F]{2})|\\([^a-zA-Z])|([{}])|([^\\{}\r\n]+)"
)
_RTF_SKIP_DEST = {
    "fonttbl", "stylesheet", "info", "pict", "header", "footer", "headerl", "headerr",
    "footerl", "footerr", "listtable", "listoverridetable", "rsidtbl", "generator",
    "themedata", "colorschememapping", "datastore", "latentstyles", "xmlnstbl",
    "private", "object", "fldinst", "revtbl", "mmathPr", "panose", "falt",
}
_RTF_SYMBOLS = {
    "bullet": "•", "endash": "–", "emdash": "—", "lquote": "‘", "rquote": "’",
    "ldblquote": "“", "rdblquote": "”", "enspace": " ", "emspace": " ",
}
_RTF_UNDERLINE = {"ul", "uld", "uldash", "uldb", "ulw", "ulth", "ulwave", "uldashd"}


def parse_rtf(data: str):
    """Zwraca (lista_przebiegów, tabela_kolorów). Przebieg = [tekst, b, i, u, hl_idx]."""
    if not data.lstrip().startswith("{\\rtf"):
        raise ValueError("To nie jest poprawny plik RTF.")

    runs: list[list] = []
    colors: list = []
    cur_color = [0, 0, 0]
    stack: list[dict] = []
    st = {"b": False, "i": False, "u": False, "hl": 0, "skip": False, "ct": False}
    cp = "cp1250"
    uc = 1
    skip_n = 0

    def add(text: str):
        if not text:
            return
        key = (st["b"], st["i"], st["u"], st["hl"])
        if runs and tuple(runs[-1][1:]) == key:
            runs[-1][0] += text
        else:
            runs.append([text, *key])

    for m in _RTF_TOKEN.finditer(data):
        word, param, hexv, sym, brace, txt = m.groups()

        if brace == "{":
            stack.append(dict(st))
        elif brace == "}":
            if stack:
                st = stack.pop()
        elif word is not None:
            val = int(param) if param is not None else None
            if word in _RTF_SKIP_DEST and not st["ct"]:
                st["skip"] = True
            elif word == "colortbl":
                st["ct"] = True
            elif st["ct"]:
                if word == "red":
                    cur_color[0] = val or 0
                elif word == "green":
                    cur_color[1] = val or 0
                elif word == "blue":
                    cur_color[2] = val or 0
            elif st["skip"]:
                continue
            elif word == "ansicpg" and val:
                cp = f"cp{val}"
            elif word == "uc" and val is not None:
                uc = val
            elif word == "b":
                st["b"] = val != 0
            elif word == "i":
                st["i"] = val != 0
            elif word in _RTF_UNDERLINE:
                st["u"] = val != 0
            elif word == "ulnone":
                st["u"] = False
            elif word == "highlight":
                st["hl"] = val or 0
            elif word == "plain":
                st["b"] = st["i"] = st["u"] = False
                st["hl"] = 0
            elif word in ("par", "line"):
                if skip_n == 0:
                    add("\n")
            elif word == "tab":
                add("\t")
            elif word == "u" and val is not None:
                code = val + 65536 if val < 0 else val
                add(chr(code))
                skip_n = uc
            elif word in _RTF_SYMBOLS:
                add(_RTF_SYMBOLS[word])
        elif hexv is not None:
            if st["skip"] or st["ct"]:
                continue
            if skip_n:
                skip_n -= 1
                continue
            add(bytes([int(hexv, 16)]).decode(cp, errors="replace"))
        elif sym is not None:
            if sym == "*":
                st["skip"] = True
            elif st["skip"] or st["ct"]:
                continue
            elif sym in "\\{}":
                if skip_n:
                    skip_n -= 1
                else:
                    add(sym)
            elif sym == "~":
                add("\u00a0")
            elif sym in "\r\n":
                add("\n")
        elif txt is not None:
            if st["ct"]:
                for ch in txt:
                    if ch == ";":
                        colors.append(tuple(cur_color))
                        cur_color = [0, 0, 0]
                continue
            if st["skip"]:
                continue
            if skip_n:
                n = min(skip_n, len(txt))
                txt = txt[n:]
                skip_n -= n
            add(txt)

    # Sklejenie par zastępczych (znaki spoza BMP zapisane jako dwa \u)
    for run in runs:
        try:
            run[0] = run[0].encode("utf-16", "surrogatepass").decode("utf-16")
        except UnicodeError:
            pass
    return runs, colors


def _nearest_highlight(rgb) -> str:
    best, best_d = HIGHLIGHT_PALETTE[0][0], None
    for code, _, bg, _ in HIGHLIGHT_PALETTE:
        pr = _hex_to_rgb(bg)
        d = sum((a - b) ** 2 for a, b in zip(rgb, pr))
        if best_d is None or d < best_d:
            best, best_d = code, d
    return best


def pl_sort_key(text: str):
    """Klucz sortowania zgodny z polskim alfabetem (ą po a, ł po l itd.)."""
    return [(1, PL_ALPHABET.index(c)) if c in PL_ALPHABET else (0, ord(c)) for c in text.casefold()]


# =============================================================================
# USTAWIENIA (sejfy = foldery szybkiego zapisu)
# =============================================================================
def load_settings() -> dict:
    data = {"vaults": [], "link_ctrl": False, "theme": "light", "topmost": False, "recent": [],
            "lena_model": lena.DEFAULT_MODEL, "shortcut_asked": False,
            "default_format": "rtf"}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        vaults = [
            {"name": str(v["name"]), "path": str(v["path"])}
            for v in loaded.get("vaults", []) if isinstance(v, dict) and v.get("path")
        ]
        data["vaults"] = vaults
        data["link_ctrl"] = bool(loaded.get("link_ctrl", False))
        data["theme"] = "dark" if loaded.get("theme") == "dark" else "light"
        data["topmost"] = bool(loaded.get("topmost", False))
        data["shortcut_asked"] = bool(loaded.get("shortcut_asked", False))
        if loaded.get("default_format") in ("rtf", "txt", "md"):
            data["default_format"] = loaded["default_format"]
        data["recent"] = [str(x) for x in loaded.get("recent", []) if isinstance(x, str)][:12]
        if loaded.get("lena_model") in dict(lena.MODELS):
            data["lena_model"] = loaded["lena_model"]
    except (OSError, ValueError, KeyError, AttributeError):
        pass
    return data


def create_desktop_shortcut() -> str:
    """Tworzy skrót 'MrPrompt Notatnik.lnk' na pulpicie (z ikoną). Zwraca ścieżkę lub rzuca OSError."""
    import subprocess
    exe = sys.executable
    pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.isfile(pyw):
        exe = pyw
    script = (
        "$ws = New-Object -ComObject WScript.Shell;"
        "$lnk = Join-Path $ws.SpecialFolders('Desktop') ($env:MP_NAME + '.lnk');"
        "$s = $ws.CreateShortcut($lnk);"
        "$s.TargetPath = $env:MP_EXE;"
        "$s.Arguments = '\"' + $env:MP_MAIN + '\"';"
        "$s.WorkingDirectory = $env:MP_DIR;"
        "$s.IconLocation = $env:MP_ICO;"
        "$s.Description = $env:MP_NAME;"
        "$s.Save();"
        "Write-Output $lnk"
    )
    env = dict(os.environ, MP_NAME=APP_NAME, MP_EXE=exe, MP_MAIN=os.path.join(BASE_DIR, "main.py"),
               MP_DIR=BASE_DIR, MP_ICO=os.path.join(BASE_DIR, "assets", "ikona.ico"))
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", script],
            env=env, capture_output=True, text=True, timeout=30,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (subprocess.SubprocessError, OSError) as exc:
        raise OSError(str(exc))
    if res.returncode != 0:
        raise OSError((res.stderr or res.stdout or "nieznany błąd").strip())
    return res.stdout.strip()


def save_settings(data: dict):
    try:
        tmp = SETTINGS_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, SETTINGS_PATH)
    except OSError as exc:
        messagebox.showwarning(APP_NAME, f"Nie udało się zapisać ustawień:\n{exc}")


# =============================================================================
# IKONY FONT AWESOME
# =============================================================================
class Icons:
    """Ładuje czcionkę Font Awesome (prywatnie, bez instalacji w systemie)."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.family: str | None = None
        self._images: dict = {}
        self.scale = max(1.0, root.winfo_fpixels("1i") / 96.0)

        if os.path.exists(FA_FONT_PATH):
            families = [f for f in tkfont.families(root) if "Font Awesome" in f]
            if families:
                solid = [f for f in families if "Solid" in f]
                self.family = (solid or families)[0]

    @staticmethod
    def register_font():
        """Musi być wywołane PRZED utworzeniem okna Tk."""
        if sys.platform != "win32" or not os.path.exists(FA_FONT_PATH):
            return
        try:
            ctypes.windll.gdi32.AddFontResourceExW(FA_FONT_PATH, 0x10, 0)  # FR_PRIVATE
        except Exception:
            pass

    @property
    def available(self) -> bool:
        return self.family is not None

    def tk_font(self, size: int = 11) -> tkfont.Font:
        return tkfont.Font(family=self.family, size=size)

    def image(self, name: str, color: str = UI_ICON, size: int = 14):
        """Ikona jako PhotoImage (do wpisów menu). Wymaga Pillow."""
        if not (PIL_AVAILABLE and os.path.exists(FA_FONT_PATH)):
            return None
        key = (name, color, size)
        if key in self._images:
            return self._images[key]
        px = round(size * self.scale)
        canvas = round(px * 1.35)
        try:
            font = ImageFont.truetype(FA_FONT_PATH, px)
            img = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((canvas / 2, canvas / 2), FA[name], font=font, fill=color, anchor="mm")
            photo = ImageTk.PhotoImage(img, master=self.root)
        except Exception:
            return None
        self._images[key] = photo
        return photo

    def blank(self, size: int = 14):
        if not PIL_AVAILABLE:
            return None
        key = ("blank", size)
        if key not in self._images:
            canvas = round(round(size * self.scale) * 1.35)
            self._images[key] = ImageTk.PhotoImage(
                Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0)), master=self.root
            )
        return self._images[key]


# =============================================================================
# APLIKACJA
# =============================================================================
class MrPromptNotatnik:
    def __init__(self, root: tk.Tk, initial_file: str | None = None):
        self.root = root
        # Rozmiar jak w Notatniku Windows: ułamek ekranu, wyśrodkowane
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(int(sw * 0.55), 1000), min(int(sh * 0.62), 640)
        w = min(w + int(self.root.winfo_fpixels("2c")), sw - 40)  # +2 cm szerokości
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{max((sh - h) // 3, 0)}")
        self.root.minsize(520, 320)

        self.current_filepath: str | None = None
        self.encoding = "utf-8"
        self.newline = "\r\n"
        self._is_modified = False
        self._spell_job: str | None = None
        self._warned_plain = False
        self._word_cache: dict[str, bool] = {}
        self._link_job: str | None = None
        self._icon_refs: list = []
        self._lena_busy = False
        self._lena_name = ""           # nazwa pliku zaproponowana przez Lenę (do okna zapisu)

        self.settings = load_settings()
        set_theme(self.settings["theme"])
        self.root.configure(bg=UI_BG)
        self.vaults: list[dict] = self.settings["vaults"]
        self.recent: list[str] = self.settings["recent"]
        self.link_ctrl_var = tk.BooleanVar(value=self.settings["link_ctrl"])
        self.dark_var = tk.BooleanVar(value=self.settings["theme"] == "dark")
        self.topmost_var = tk.BooleanVar(value=self.settings["topmost"])
        self._recovery_dirty = False
        self._find_visible = False
        self._find_hits: list = []
        self._find_job: str | None = None
        self.find_text_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.find_case_var = tk.BooleanVar(value=False)
        self.find_word_var = tk.BooleanVar(value=False)
        self._ttk_light = ttk.Style(root).theme_use()

        self.icons = Icons(root)

        # Słownik i sprawdzanie pisowni
        self.spell = None                      # obiekt Dictionary (Hunspell) po załadowaniu
        self._spell_loading = False
        self._spell_result: dict = {}
        self.user_words: set[str] = self._load_user_words()
        self.ignored_words: set[str] = set()
        self.spell_enabled = SPELL_AVAILABLE

        self._init_fonts()

        # Budowa UI (kolejność pakowania ma znaczenie)
        self._build_menu()
        self._build_toolbar()
        self._build_statusbar()
        self._build_editor()
        self._build_findbar()
        self._configure_tags()
        self._bind_events()

        self._refresh_title()
        self.root.protocol("WM_DELETE_WINDOW", self._on_exit)
        self._style_ttk()
        self._set_dark_titlebar(self.settings["theme"] == "dark")
        if self.settings["topmost"]:
            self.root.attributes("-topmost", True)
        self._setup_dnd()
        self.root.after(15000, self._autosave_tick)
        if not self.settings.get("shortcut_asked"):
            self.root.after(1200, self._offer_shortcut)

        if os.path.exists(RECOVERY_RTF) and os.path.getsize(RECOVERY_RTF) > 0:
            self.root.after(300, lambda: self._startup_recovery(initial_file))
        elif initial_file and os.path.isfile(initial_file):
            self._load_file(initial_file)

        if self.spell_enabled:
            self._start_spell_loading()

    def _init_fonts(self):
        self.font_normal = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE)
        self.font_bold = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE, weight="bold")
        self.font_italic = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE, slant="italic")
        self.font_bold_italic = tkfont.Font(family=FONT_FAMILY, size=FONT_SIZE, weight="bold", slant="italic")

    # -------------------------------------------------------------------------
    # Słownik
    # -------------------------------------------------------------------------
    def _load_user_words(self) -> set[str]:
        try:
            if os.path.exists(USER_DICT_PATH):
                with open(USER_DICT_PATH, "r", encoding="utf-8") as fh:
                    return {w.strip().lower() for w in fh if w.strip()}
        except OSError:
            pass
        return set()

    def _start_spell_loading(self):
        """Ładuje słownik Hunspell w tle (ok. 4 s), żeby okno startowało od razu."""
        if self._spell_loading or self.spell is not None:
            return
        self._spell_loading = True
        self._spell_result = {}
        self.status_spell.config(text="Pisownia PL: ładowanie słownika…")
        result = self._spell_result

        def worker():
            try:
                if not os.path.exists(DICT_BASE + ".dic"):
                    import setup_slownik
                    setup_slownik.setup()
                result["dict"] = Dictionary.from_files(DICT_BASE)
            except Exception as exc:
                result["error"] = exc

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(200, self._poll_spell_loading)

    def _poll_spell_loading(self):
        if not self._spell_result:
            self.root.after(200, self._poll_spell_loading)
            return
        self._spell_loading = False
        if "dict" in self._spell_result:
            self.spell = self._spell_result["dict"]
            self._word_cache.clear()
            if self.spell_enabled:
                self.status_spell.config(text="Pisownia PL: Aktywna")
                self.run_spell_check_now()
        else:
            self.spell_enabled = False
            self.spell_menu_var.set(False)
            self.status_spell.config(text="Pisownia: Brak słownika")

    # =========================================================================
    # POMOCNIKI UI
    # =========================================================================
    def _menu_item(self, menu: tk.Menu, label: str, icon: str | None, command, accelerator: str = ""):
        img = self.icons.image(icon) if icon else None
        if img is None:
            img = self.icons.blank()
        kwargs = {"label": " " + label, "command": command, "accelerator": accelerator}
        if img is not None:
            kwargs.update(image=img, compound="left")
        menu.add_command(**kwargs)

    def _new_menu(self, parent) -> tk.Menu:
        return tk.Menu(
            parent, tearoff=0, font=(FONT_FAMILY, 10),
            activebackground=THEME["menu_active"], activeforeground=THEME["text"],
            bg=THEME["menu_bg"], fg=THEME["text"], bd=1, relief="solid"
        )

    # =========================================================================
    # MENU (własny, płaski pasek z ikonami)
    # =========================================================================
    def _build_menu(self):
        self.menubar = tk.Frame(self.root, bg=UI_BG)
        self.menubar.pack(side="top", fill="x")
        tk.Frame(self.root, bg=UI_BORDER, height=1).pack(side="top", fill="x")
        self._populate_menubar()

    def _check_item(self, menu: tk.Menu, label: str, icon: str, variable, command):
        img = self.icons.image(icon)
        kw = {"label": " " + label, "variable": variable, "command": command}
        if img is not None:
            kw.update(image=img, compound="left")
        menu.add_checkbutton(**kw)

    def _populate_menubar(self):
        bar = self.menubar
        for child in bar.winfo_children():
            child.destroy()

        def add_menubutton(title: str) -> tk.Menu:
            mb = tk.Menubutton(
                bar, text=title, font=(FONT_FAMILY, 10), bg=UI_BG, fg=UI_TEXT,
                activebackground=UI_HOVER, activeforeground=UI_ACTIVE_FG,
                relief="flat", bd=0, padx=12, pady=5, cursor="hand2"
            )
            mb.pack(side="left")
            menu = self._new_menu(mb)
            mb.config(menu=menu)
            return menu

        # --- Plik
        m = add_menubutton("Plik")
        self._menu_item(m, "Nowy", "file", self.file_new, "Ctrl+N")
        self._menu_item(m, "Otwórz…", "folder-open", self.file_open, "Ctrl+O")
        self.recent_menu = self._new_menu(m)
        img = self.icons.image("history")
        kw = {"label": " Ostatnio otwarte", "menu": self.recent_menu}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_cascade(**kw)
        self._rebuild_recent_menu()
        m.add_separator()
        self._menu_item(m, "Zapisz", "save", self.file_save, "Ctrl+S")
        self._menu_item(m, "Zapisz jako…", "save-as", self.file_save_as, "Ctrl+Shift+S")
        m.add_separator()
        self.vault_menu = self._new_menu(m)
        img = self.icons.image("vault")
        kw = {"label": " Zapisz w sejfie", "menu": self.vault_menu}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_cascade(**kw)
        self._rebuild_vault_menu()
        m.add_separator()
        self._menu_item(m, "Zakończ", "exit", self._on_exit, "Alt+F4")

        # --- Edycja
        m = add_menubutton("Edycja")
        self._menu_item(m, "Cofnij", "undo", lambda: self._safe_edit("undo"), "Ctrl+Z")
        self._menu_item(m, "Ponów", "redo", lambda: self._safe_edit("redo"), "Ctrl+Y")
        m.add_separator()
        self._menu_item(m, "Wytnij", "cut", lambda: self.text.event_generate("<<Cut>>"), "Ctrl+X")
        self._menu_item(m, "Kopiuj", "copy", lambda: self.text.event_generate("<<Copy>>"), "Ctrl+C")
        self._menu_item(m, "Wklej", "paste", lambda: self.text.event_generate("<<Paste>>"), "Ctrl+V")
        m.add_separator()
        self._menu_item(m, "Zaznacz wszystko", "select-all", self._select_all, "Ctrl+A")
        m.add_separator()
        self._menu_item(m, "Znajdź…", "search", self.show_find, "Ctrl+F")
        self._menu_item(m, "Zamień…", "search", lambda: self.show_find(True), "Ctrl+H")

        # --- Format
        m = add_menubutton("Format")
        self._menu_item(m, "Pogrubienie", "bold", self.action_bold, "Ctrl+B")
        self._menu_item(m, "Kursywa", "italic", self.action_italic, "Ctrl+I")
        self._menu_item(m, "Podkreślenie", "underline", self.action_underline, "Ctrl+U")
        m.add_separator()
        hl_sub = self._new_menu(m)
        for code, name, bg, _ in HIGHLIGHT_PALETTE:
            hl_sub.add_command(label=f"   {name}   ", background=bg, activebackground=bg,
                               command=lambda c=code: self.action_highlight(c))
        hl_sub.add_separator()
        hl_sub.add_command(label="Usuń zakreślenie", command=self.action_clear_highlight)
        img = self.icons.image("marker")
        kw = {"label": " Zakreślacz (Marker)", "menu": hl_sub}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_cascade(**kw)
        m.add_separator()
        self._menu_item(m, "Lista punktowa", "list", self.action_bullet_list, "Ctrl+L")
        self._menu_item(m, "Lista zadań  - [ ]", "task", self.action_toggle_task, "Ctrl+Shift+T")

        # --- Narzędzia
        m = add_menubutton("Narzędzia")
        self._menu_item(m, "Sprawdź cały tekst teraz", "check", self.run_spell_check_now, "F7")
        m.add_separator()
        txt = self._new_menu(m)
        self._menu_item(txt, "Sortuj linie A → Z", "sort-az", lambda: self.tool_sort_lines(False))
        self._menu_item(txt, "Sortuj linie Z → A", "sort-za", lambda: self.tool_sort_lines(True))
        self._menu_item(txt, "Usuń zduplikowane linie", "clone", self.tool_remove_duplicates)
        txt.add_separator()
        self._menu_item(txt, "WIELKIE LITERY", "font", lambda: self.tool_change_case("upper"))
        self._menu_item(txt, "małe litery", "font", lambda: self.tool_change_case("lower"))
        self._menu_item(txt, "Każde Słowo Wielką Literą", "font", lambda: self.tool_change_case("title"))
        self._menu_item(txt, "zAMIEŃ wIELKOŚĆ", "font", lambda: self.tool_change_case("swap"))
        img = self.icons.image("font")
        kw = {"label": " Narzędzia tekstowe (zaznaczenie / całość)", "menu": txt}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_cascade(**kw)

        # --- Lena
        m = add_menubutton("Lena")
        self._build_lena_menu(m)

        # --- Ustawienia
        m = add_menubutton("Ustawienia")
        fmt_menu = self._new_menu(m)
        self.default_format_var = tk.StringVar(value=self.settings["default_format"])
        for code, label in (("rtf", "RTF — z formatowaniem (.rtf)"), ("txt", "Zwykły tekst (.txt)"),
                            ("md", "Markdown (.md)")):
            fmt_menu.add_radiobutton(label=label, value=code, variable=self.default_format_var,
                                     command=self._on_default_format_changed)
        img = self.icons.image("save")
        kw = {"label": " Domyślny format zapisu", "menu": fmt_menu}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_cascade(**kw)
        enc_menu = self._new_menu(m)
        self.enc_var = tk.StringVar(value=self.encoding)
        for code, label in ENCODINGS:
            enc_menu.add_radiobutton(
                label=label, value=code, variable=self.enc_var, command=self._on_encoding_changed
            )
        img = self.icons.image("language")
        kw = {"label": " Kodowanie plików .txt", "menu": enc_menu}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_cascade(**kw)
        m.add_separator()
        self._check_item(m, "Tryb ciemny", "moon", self.dark_var, self._on_theme_toggle)
        self._check_item(m, "Zawsze na wierzchu", "pin", self.topmost_var, self._on_topmost_toggle)
        m.add_separator()
        self.spell_menu_var = tk.BooleanVar(value=self.spell_enabled)
        img = self.icons.image("spell")
        kw = {"label": " Sprawdzanie pisowni (Polski)", "variable": self.spell_menu_var,
              "command": self._toggle_spell_checker}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_checkbutton(**kw)
        img = self.icons.image("link")
        kw = {"label": " Otwieraj linki tylko z klawiszem Ctrl", "variable": self.link_ctrl_var,
              "command": self._on_link_setting_changed}
        if img is not None:
            kw.update(image=img, compound="left")
        m.add_checkbutton(**kw)
        m.add_separator()
        self._menu_item(m, "Zarządzaj sejfami…", "gear", self.open_vault_manager)
        self._menu_item(m, "Ustawienia Leny (klucz API)…", "key", self.open_lena_settings)
        self._menu_item(m, "Utwórz skrót na pulpicie", None, self._make_shortcut)

        # --- Pomoc
        m = add_menubutton("Pomoc")
        self._menu_item(m, "O programie", "info", self._show_about)

    # =========================================================================
    # PASEK NARZĘDZI
    # =========================================================================
    def _toolbar_button(self, parent, icon: str, fallback: str, tip: str, command):
        if self.icons.available:
            btn = tk.Button(parent, text=FA[icon], font=self.icons.tk_font(11), width=3)
        else:
            btn = tk.Button(parent, text=fallback, font=(FONT_FAMILY, 10), padx=6)
        btn.config(
            bg=UI_BG, fg=UI_ICON, activebackground=UI_PRESSED, activeforeground=UI_ICON,
            relief="flat", bd=0, pady=5, cursor="hand2", command=command, takefocus=0
        )
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=UI_HOVER))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=UI_BG))
        btn.pack(side="left", padx=1, pady=3)
        self._add_tooltip(btn, tip)
        return btn

    def _toolbar_separator(self, parent):
        tk.Frame(parent, bg=UI_BORDER, width=1).pack(side="left", fill="y", padx=7, pady=7)

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=UI_BG)
        toolbar.pack(side="top", fill="x")
        tk.Frame(self.root, bg=UI_BORDER, height=1).pack(side="top", fill="x")

        tb = self._toolbar_button
        tb(toolbar, "file", "Nowy", "Nowy dokument (Ctrl+N)", self.file_new)
        tb(toolbar, "folder-open", "Otwórz", "Otwórz plik (Ctrl+O)", self.file_open)
        tb(toolbar, "save", "Zapisz", "Zapisz (Ctrl+S)", self.file_save)
        self._toolbar_separator(toolbar)

        tb(toolbar, "undo", "Cofnij", "Cofnij (Ctrl+Z)", lambda: self._safe_edit("undo"))
        tb(toolbar, "redo", "Ponów", "Ponów (Ctrl+Y)", lambda: self._safe_edit("redo"))
        self._toolbar_separator(toolbar)

        tb(toolbar, "bold", "B", "Pogrubienie (Ctrl+B)", self.action_bold)
        tb(toolbar, "italic", "I", "Kursywa (Ctrl+I)", self.action_italic)
        tb(toolbar, "underline", "U", "Podkreślenie (Ctrl+U)", self.action_underline)
        self._toolbar_separator(toolbar)

        # Zakreślacz
        if self.icons.available:
            tk.Label(toolbar, text=FA["marker"], font=self.icons.tk_font(11),
                     bg=UI_BG, fg=UI_ICON).pack(side="left", padx=(4, 6))
        else:
            tk.Label(toolbar, text="Marker:", bg=UI_BG, font=(FONT_FAMILY, 10)).pack(side="left", padx=(4, 6))

        for code, name, bg, _ in HIGHLIGHT_PALETTE:
            sw = tk.Canvas(toolbar, width=22, height=22, bg=UI_BG, highlightthickness=0, cursor="hand2")
            oval = sw.create_oval(3, 3, 19, 19, fill=bg, outline="#B0BEC5", width=1)
            sw.pack(side="left", padx=1)
            sw.bind("<Button-1>", lambda e, c=code: self.action_highlight(c))
            sw.bind("<Enter>", lambda e, s=sw, o=oval: s.itemconfig(o, outline=UI_ACCENT, width=2))
            sw.bind("<Leave>", lambda e, s=sw, o=oval: s.itemconfig(o, outline="#B0BEC5", width=1))
            self._add_tooltip(sw, f"Zakreślacz: {name}")

        tb(toolbar, "eraser", "✕", "Usuń zakreślenie kolorem", self.action_clear_highlight)
        self._toolbar_separator(toolbar)

        tb(toolbar, "list", "• Lista", "Przełącz listę punktową (Ctrl+L)", self.action_bullet_list)
        tb(toolbar, "task", "[ ]", "Lista zadań - [ ] (Ctrl+Shift+T)", self.action_toggle_task)
        self._toolbar_separator(toolbar)
        tb(toolbar, "search", "Szukaj", "Znajdź i zamień (Ctrl+F)", self.show_find)
        tb(toolbar, "spell", "Pisownia", "Sprawdź pisownię w języku polskim (F7)", self.run_spell_check_now)
        self._toolbar_separator(toolbar)
        self.lena_btn = tb(toolbar, "wand", "Lena", "Lena — asystent AI (popraw, skróć, streść…)",
                           self._post_lena_menu)

        # Drugi rząd: sejfy (foldery szybkiego zapisu)
        self.vault_bar = tk.Frame(self.root, bg=UI_BG)
        self.vault_bar.pack(side="top", fill="x")
        tk.Frame(self.root, bg=UI_BORDER, height=1).pack(side="top", fill="x")
        self._rebuild_vault_bar()

    # =========================================================================
    # EDYTOR
    # =========================================================================
    def _build_editor(self):
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)
        self.editor_container = container

        v_scroll = ttk.Scrollbar(container, orient="vertical")
        v_scroll.pack(side="right", fill="y")

        self.text = tk.Text(
            container,
            wrap="word",
            undo=True,
            maxundo=-1,
            font=self.font_normal,
            yscrollcommand=v_scroll.set,
            padx=14,
            pady=12,
            relief="flat",
            borderwidth=0,
            bg=THEME["editor_bg"],
            fg=THEME["editor_fg"],
            insertbackground=THEME["editor_fg"],
            selectbackground=THEME["select"],
            selectforeground=THEME["editor_fg"],
            spacing1=3,
            spacing3=3,
        )
        self.text.pack(fill="both", expand=True)
        v_scroll.config(command=self.text.yview)

    # =========================================================================
    # PASEK STANU
    # =========================================================================
    def _build_statusbar(self):
        statusbar = ttk.Frame(self.root, relief="groove", borderwidth=1, padding=(6, 2))
        statusbar.pack(side="bottom", fill="x")

        self.status_pos = ttk.Label(statusbar, text="Ln 1, Kol 1", width=16, anchor="w")
        self.status_pos.pack(side="left", padx=4)
        ttk.Separator(statusbar, orient="vertical").pack(side="left", fill="y", padx=4)

        self.status_words = ttk.Label(statusbar, text="Słów: 0", width=14, anchor="w")
        self.status_words.pack(side="left", padx=4)
        ttk.Separator(statusbar, orient="vertical").pack(side="left", fill="y", padx=4)

        self.status_chars = ttk.Label(statusbar, text="Znaków: 0", width=16, anchor="w")
        self.status_chars.pack(side="left", padx=4)

        self.status_encoding = ttk.Label(statusbar, text="UTF-8", width=20, anchor="center")
        self.status_encoding.pack(side="right", padx=6)
        ttk.Separator(statusbar, orient="vertical").pack(side="right", fill="y", padx=4)

        spell_msg = "Pisownia PL: Aktywna" if self.spell_enabled else "Pisownia: Wyłączona"
        self.status_spell = ttk.Label(statusbar, text=spell_msg, anchor="e")
        self.status_spell.pack(side="right", padx=6)
        self.status_lena = ttk.Label(statusbar, text="", anchor="e")
        self.status_lena.pack(side="right", padx=6)

    # =========================================================================
    # TAGI
    # =========================================================================
    def _configure_tags(self):
        # Znaczniki logiczne (bez wyglądu) — właściwa czcionka jest w tagach font_*
        self.text.tag_configure("font_b", font=self.font_bold)
        self.text.tag_configure("font_i", font=self.font_italic)
        self.text.tag_configure("font_bi", font=self.font_bold_italic)
        self.text.tag_configure("fmt_underline", underline=True)

        for code, _, bg, _ in HIGHLIGHT_PALETTE:
            self.text.tag_configure(f"hl_{code}", background=bg, foreground="#000000")

        self.text.tag_configure(
            "misspelled", background=THEME["misspelled_bg"], foreground=THEME["misspelled_fg"],
            underline=True
        )
        # Zakreślacz na wierzchu, pod nim błędy pisowni
        self.text.tag_lower("misspelled")
        for code, _, _, _ in HIGHLIGHT_PALETTE:
            self.text.tag_raise(f"hl_{code}", "misspelled")

        # Linki
        self.text.tag_configure("link", foreground=THEME["link"], underline=True)
        self.text.tag_configure("find_match", background=THEME["find"])
        self.text.tag_configure("find_current", background=THEME["find_cur"])
        self.text.tag_raise("find_match")
        self.text.tag_raise("find_current")
        self.text.tag_raise("link")
        self.text.tag_bind("link", "<Enter>", lambda e: self.text.config(cursor="hand2"))
        self.text.tag_bind("link", "<Leave>", lambda e: self.text.config(cursor="xterm"))
        self.text.tag_bind("link", "<ButtonRelease-1>", self._on_link_click)

    # =========================================================================
    # SKRÓTY I ZDARZENIA
    # =========================================================================
    def _shortcut(self, sequence: str, func):
        """Skrót na widżecie tekstowym i oknie; 'break' blokuje domyślne akcje Tk
        (np. Ctrl+B = kursor w lewo, Ctrl+I = tabulator, Ctrl+O = nowa linia)."""
        def handler(event, f=func):
            f()
            return "break"
        for widget in (self.text, self.root):
            widget.bind(sequence, handler)

    def _bind_events(self):
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<KeyRelease>", self._update_statusbar)
        self.text.bind("<ButtonRelease-1>", self._update_statusbar)
        self.text.bind("<Button-3>", self._on_right_click)
        self.text.bind("<Return>", self._on_enter_pressed)

        shortcuts = {
            "n": self.file_new, "o": self.file_open, "s": self.file_save,
            "b": self.action_bold, "i": self.action_italic, "u": self.action_underline,
            "l": self.action_bullet_list,
        }
        for key, func in shortcuts.items():
            self._shortcut(f"<Control-{key}>", func)
            self._shortcut(f"<Control-{key.upper()}>", func)
        self._shortcut("<Control-Shift-S>", self.file_save_as)
        self._shortcut("<Control-Shift-s>", self.file_save_as)
        self._shortcut("<F7>", self.run_spell_check_now)
        for key in ("f", "F"):
            self._shortcut(f"<Control-{key}>", self.show_find)
        for key in ("h", "H"):
            self._shortcut(f"<Control-{key}>", lambda: self.show_find(True))
        for key in ("T", "t"):
            self._shortcut(f"<Control-Shift-{key}>", self.action_toggle_task)
        self._shortcut("<F3>", lambda: self._find_step(1))
        self._shortcut("<Shift-F3>", lambda: self._find_step(-1))
        self.text.bind("<Escape>", self._on_escape)
        for n in range(1, 10):
            self._shortcut(f"<Control-Key-{n}>", lambda i=n - 1: self._vault_hotkey(i))

    # =========================================================================
    # TABELA OFFSETÓW (zakresy tagów <-> pozycje znaków)
    # =========================================================================
    def _line_table(self):
        content = self.text.get("1.0", "end-1c")
        starts = [0]
        for line in content.split("\n"):
            starts.append(starts[-1] + len(line) + 1)
        return content, starts

    @staticmethod
    def _to_off(index, starts) -> int:
        line, col = str(index).split(".")
        return starts[int(line) - 1] + int(col)

    @staticmethod
    def _to_idx(off: int, starts) -> str:
        line = bisect_right(starts, off) - 1
        return f"{line + 1}.{off - starts[line]}"

    def _intervals(self, tag: str, starts):
        r = self.text.tag_ranges(tag)
        return [(self._to_off(r[i], starts), self._to_off(r[i + 1], starts)) for i in range(0, len(r), 2)]

    @staticmethod
    def _covers(intervals, a: int, b: int) -> bool:
        """Czy [a, b) jest w całości pokryty przez sumę przedziałów."""
        pos = a
        for s, e in sorted(intervals):
            if e <= pos:
                continue
            if s > pos:
                return False
            pos = e
            if pos >= b:
                return True
        return pos >= b

    def _has_formatting(self) -> bool:
        return any(self.text.tag_ranges(t) for t in STYLE_TAGS)

    # =========================================================================
    # OPERACJE PLIKOWE
    # =========================================================================
    def _reset_document(self):
        self._lena_name = ""
        self.text.delete("1.0", "end")
        self._clear_all_tags()
        self.text.edit_reset()
        self._word_cache.clear()

    def file_new(self):
        if not self._check_save_changes():
            return
        self._reset_document()
        self.current_filepath = None
        self.encoding = "utf-8"
        self.enc_var.set("utf-8")
        self.newline = "\r\n"
        self._warned_plain = False
        self._set_modified(False)
        self._show_encoding()
        self._refresh_title()
        self._update_statusbar()

    def file_open(self):
        if not self._check_save_changes():
            return
        filepath = filedialog.askopenfilename(
            title="Otwórz plik",
            filetypes=[
                ("Dokumenty (*.rtf, *.txt, *.md)", "*.rtf *.txt *.md"),
                ("Dokument RTF (*.rtf)", "*.rtf"),
                ("Pliki tekstowe (*.txt)", "*.txt"),
                ("Markdown (*.md)", "*.md"),
                ("Wszystkie pliki (*.*)", "*.*"),
            ],
        )
        if filepath:
            self._load_file(filepath)

    @staticmethod
    def _read_text_file(filepath: str):
        with open(filepath, "rb") as fh:
            raw = fh.read()
        if raw.startswith(codecs.BOM_UTF8):
            enc = "utf-8-sig"
        elif raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
            enc = "utf-16"
        else:
            try:
                raw.decode("utf-8")
                enc = "utf-8"
            except UnicodeDecodeError:
                enc = "cp1250"
        try:
            content = raw.decode(enc)
        except UnicodeDecodeError:
            enc = "cp1250"
            content = raw.decode("cp1250", errors="replace")
        newline = "\r\n" if "\r\n" in content else ("\n" if "\n" in content else "\r\n")
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        return content, enc, newline

    def _load_file(self, filepath: str):
        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == ".rtf":
                with open(filepath, "rb") as fh:
                    data = fh.read().decode("latin-1")
                runs, colors = parse_rtf(data)
                self._reset_document()
                self._insert_rtf_runs(runs, colors)
                self.encoding = "utf-8"
                self.status_encoding.config(text="RTF")
            else:
                content, enc, newline = self._read_text_file(filepath)
                self._reset_document()
                self.text.insert("1.0", content)
                self.encoding, self.newline = enc, newline
                self.enc_var.set(enc)
                self._show_encoding()
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Nie udało się odczytać pliku:\n{filepath}\n\n{exc}")
            return

        self.text.edit_reset()
        self.current_filepath = filepath
        self._add_recent(filepath)
        self._warned_plain = False
        self._set_modified(False)
        self._refresh_title()
        self._update_statusbar()
        self._schedule_spell_check()
        self._schedule_link_scan()

    def _insert_rtf_runs(self, runs, colors):
        # Zdejmij końcowy \par (zapisujemy go zawsze, Word też go dokłada)
        if runs and runs[-1][0].endswith("\n"):
            runs[-1][0] = runs[-1][0][:-1]
        content = "".join(r[0] for r in runs)
        self.text.insert("1.0", content)
        _, starts = self._line_table()

        pos = 0
        for text, bold, italic, ul, hl in runs:
            end = pos + len(text)
            if end > pos:
                a, b = self._to_idx(pos, starts), self._to_idx(end, starts)
                if bold:
                    self.text.tag_add("fmt_bold", a, b)
                if italic:
                    self.text.tag_add("fmt_italic", a, b)
                if ul:
                    self.text.tag_add("fmt_underline", a, b)
                if hl:
                    rgb = colors[hl] if 0 <= hl < len(colors) else (255, 255, 0)
                    self.text.tag_add(f"hl_{_nearest_highlight(rgb)}", a, b)
            pos = end
        self._refresh_fonts("1.0", "end-1c")

    def file_save(self) -> bool:
        if self.current_filepath:
            return self._write_to_disk(self.current_filepath)
        return self.file_save_as()

    def file_save_as(self, prefer_rtf: bool = False) -> bool:
        fmt = self.settings.get("default_format", "rtf")
        ext = os.path.splitext(self.current_filepath or "")[1].lower().lstrip(".")
        if prefer_rtf:
            fmt = "rtf"
        elif ext in ("rtf", "txt", "md"):
            fmt = ext
        types = {"rtf": ("Dokument RTF (*.rtf)", "*.rtf"), "txt": ("Pliki tekstowe (*.txt)", "*.txt"),
                 "md": ("Markdown (*.md)", "*.md")}
        filepath = filedialog.asksaveasfilename(
            title="Zapisz plik jako",
            filetypes=[types[fmt]] + [t for k, t in types.items() if k != fmt],
            defaultextension="." + fmt,
            initialfile=os.path.splitext(os.path.basename(self.current_filepath))[0]
            if self.current_filepath else "",
        )
        if not filepath:
            return False
        return self._write_to_disk(filepath)

    def _build_rtf(self) -> str:
        content, starts = self._line_table()
        n = len(content)
        bold = self._intervals("fmt_bold", starts)
        italic = self._intervals("fmt_italic", starts)
        under = self._intervals("fmt_underline", starts)
        hls = [(i + 1, self._intervals(f"hl_{c[0]}", starts)) for i, c in enumerate(HIGHLIGHT_PALETTE)]

        points = {0, n}
        for ivs in [bold, italic, under] + [h[1] for h in hls]:
            for s, e in ivs:
                for p in (s, e):
                    if 0 < p < n:
                        points.add(p)
        points = sorted(points)

        def inside(ivs, x):
            return any(s <= x < e for s, e in ivs)

        parts = []
        for x, y in zip(points, points[1:]):
            codes = ""
            if inside(bold, x):
                codes += "\\b"
            if inside(italic, x):
                codes += "\\i"
            if inside(under, x):
                codes += "\\ul"
            for idx, ivs in hls:
                if inside(ivs, x):
                    codes += f"\\highlight{idx}"
                    break
            body = rtf_escape(content[x:y])
            parts.append("{" + codes + " " + body + "}" if codes else body)

        colortbl = ";" + "".join(
            "\\red{}\\green{}\\blue{};".format(*_hex_to_rgb(bg)) for _, _, bg, _ in HIGHLIGHT_PALETTE
        )
        header = (
            "{\\rtf1\\ansi\\ansicpg1250\\deff0\\uc1"
            "{\\fonttbl{\\f0\\fnil\\fcharset238 " + FONT_FAMILY + ";}}"
            "{\\colortbl " + colortbl + "}"
            f"\\viewkind4\\pard\\f0\\fs{FONT_SIZE * 2} "
        )
        return header + "".join(parts) + "\\par\n}"

    def _write_to_disk(self, filepath: str) -> bool:
        ext = os.path.splitext(filepath)[1].lower()
        if ext != ".rtf" and self._has_formatting() and not self._warned_plain:
            answer = messagebox.askyesnocancel(
                APP_NAME,
                f"Pliki {ext or 'tekstowe'} nie przechowują formatowania (pogrubienie, kolory markera itd.).\n\n"
                "Tak — zapisz sam tekst bez formatowania\n"
                "Nie — zapisz jako dokument RTF z formatowaniem (ta sama nazwa)\n"
                "Anuluj — nie zapisuj"
            )
            if answer is None:
                return False
            if answer:
                self._warned_plain = True
            else:
                filepath = os.path.splitext(filepath)[0] + ".rtf"
                ext = ".rtf"
        try:
            if ext == ".rtf":
                with open(filepath, "wb") as fh:
                    fh.write(self._build_rtf().encode("ascii", errors="replace"))
                self.status_encoding.config(text="RTF")
            else:
                content = self.text.get("1.0", "end-1c").replace("\n", self.newline)
                enc = self.encoding
                try:
                    raw = content.encode(enc)
                except UnicodeEncodeError:
                    if not messagebox.askyesno(
                        APP_NAME,
                        f"Tekst zawiera znaki, których nie da się zapisać w kodowaniu "
                        f"{ENCODING_LABELS.get(enc, enc)}.\nZapisać w UTF-8?"
                    ):
                        return False
                    enc = "utf-8"
                    raw = content.encode(enc)
                    self.encoding = enc
                    self.enc_var.set(enc)
                with open(filepath, "wb") as fh:
                    fh.write(raw)
                self._show_encoding()
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Błąd podczas zapisywania pliku:\n{exc}")
            return False

        self.current_filepath = filepath
        self._add_recent(filepath)
        self._set_modified(False)
        self._refresh_title()
        return True

    def _check_save_changes(self) -> bool:
        if not self._is_modified:
            return True
        answer = messagebox.askyesnocancel(
            APP_NAME,
            "Dokument zawiera niezapisane zmiany.\nCzy chcesz je zapisać przed kontynuowaniem?"
        )
        if answer is None:
            return False
        if answer:
            return self.file_save()
        return True

    def _on_exit(self):
        if self._check_save_changes():
            self._clear_recovery()
            self.root.destroy()

    def _on_encoding_changed(self):
        self.encoding = self.enc_var.get()
        self._show_encoding()
        self._mark_modified()

    def _show_encoding(self):
        self.status_encoding.config(text=ENCODING_LABELS.get(self.encoding, self.encoding))

    # =========================================================================
    # FORMATOWANIE: POGRUBIENIE, KURSYWA, PODKREŚLENIE
    # =========================================================================
    def _get_selection(self):
        try:
            return self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            return None, None

    def _toggle_style(self, tag: str):
        start, end = self._get_selection()
        if not start:
            return
        _, starts = self._line_table()
        a, b = self._to_off(start, starts), self._to_off(end, starts)
        if a >= b:
            return
        if self._covers(self._intervals(tag, starts), a, b):
            self.text.tag_remove(tag, start, end)
        else:
            self.text.tag_add(tag, start, end)
        if tag in ("fmt_bold", "fmt_italic"):
            self._refresh_fonts(start, end)
        self._mark_modified()

    def _refresh_fonts(self, first, last):
        """Przelicza tagi czcionek (zwykła/pogrubiona/kursywa/oba) w zadanym zakresie."""
        _, starts = self._line_table()
        a, b = self._to_off(self.text.index(first), starts), self._to_off(self.text.index(last), starts)
        for t in FONT_TAGS:
            self.text.tag_remove(t, first, last)
        bold = self._intervals("fmt_bold", starts)
        italic = self._intervals("fmt_italic", starts)
        points = {a, b}
        for s, e in bold + italic:
            for p in (s, e):
                if a < p < b:
                    points.add(p)
        points = sorted(points)
        for x, y in zip(points, points[1:]):
            is_b = any(s <= x < e for s, e in bold)
            is_i = any(s <= x < e for s, e in italic)
            tag = "font_bi" if (is_b and is_i) else "font_b" if is_b else "font_i" if is_i else None
            if tag:
                self.text.tag_add(tag, self._to_idx(x, starts), self._to_idx(y, starts))

    def action_bold(self):
        self._toggle_style("fmt_bold")

    def action_italic(self):
        self._toggle_style("fmt_italic")

    def action_underline(self):
        self._toggle_style("fmt_underline")

    # =========================================================================
    # ZAKREŚLACZ
    # =========================================================================
    def action_highlight(self, color_code: str):
        start, end = self._get_selection()
        if not start:
            return
        for code, _, _, _ in HIGHLIGHT_PALETTE:
            self.text.tag_remove(f"hl_{code}", start, end)
        self.text.tag_add(f"hl_{color_code}", start, end)
        self._mark_modified()

    def action_clear_highlight(self):
        start, end = self._get_selection()
        if not start:
            return
        for code, _, _, _ in HIGHLIGHT_PALETTE:
            self.text.tag_remove(f"hl_{code}", start, end)
        self._mark_modified()

    # =========================================================================
    # LISTA PUNKTOWA
    # =========================================================================
    def action_bullet_list(self):
        try:
            line_start = int(self.text.index("sel.first").split(".")[0])
            sel_end = self.text.index("sel.last")
            line_end = int(sel_end.split(".")[0])
            if sel_end.endswith(".0") and line_end > line_start:
                line_end -= 1
        except tk.TclError:
            line_start = line_end = int(self.text.index("insert").split(".")[0])

        self.text.edit_separator()
        for line_idx in range(line_start, line_end + 1):
            line_text = self.text.get(f"{line_idx}.0", f"{line_idx}.end")
            if line_text.startswith("• "):
                self.text.delete(f"{line_idx}.0", f"{line_idx}.2")
            else:
                self.text.insert(f"{line_idx}.0", "• ")
        self.text.edit_separator()

    def _on_enter_pressed(self, event):
        line_idx = int(self.text.index("insert").split(".")[0])
        line_text = self.text.get(f"{line_idx}.0", f"{line_idx}.end")

        task = TASK_RE.match(line_text)
        if task:
            if not task.group(3).strip():
                self.text.delete(f"{line_idx}.0", f"{line_idx}.end")
            else:
                self.text.insert("insert", f"\n{task.group(1)}- [ ] ")
                self.text.see("insert")
                self._update_statusbar()
            return "break"

        if line_text.strip() == "•":
            self.text.delete(f"{line_idx}.0", f"{line_idx}.end")
            return "break"
        if line_text.startswith("• "):
            self.text.insert("insert", "\n• ")
            self.text.see("insert")
            self._update_statusbar()
            return "break"
        return None

    # =========================================================================
    # SPRAWDZANIE PISOWNI
    # =========================================================================
    def _toggle_spell_checker(self):
        self.spell_enabled = self.spell_menu_var.get()
        if self.spell_enabled:
            if not SPELL_AVAILABLE:
                self.spell_enabled = False
                self.spell_menu_var.set(False)
                self.status_spell.config(text="Pisownia: Brak biblioteki")
                messagebox.showwarning(
                    APP_NAME,
                    "Brakuje biblioteki spylls.\nZainstaluj ją: pip install -r requirements.txt"
                )
            elif self.spell is None:
                self._start_spell_loading()
            else:
                self.status_spell.config(text="Pisownia PL: Aktywna")
                self.run_spell_check_now()
        else:
            self.status_spell.config(text="Pisownia: Wyłączona")
            self.text.tag_remove("misspelled", "1.0", "end")

    def _schedule_spell_check(self):
        if not self.spell_enabled or not self.spell:
            return
        if self._spell_job:
            self.root.after_cancel(self._spell_job)
        self._spell_job = self.root.after(600, self.run_spell_check_now)

    def _is_misspelled(self, word: str) -> bool:
        bad = self._word_cache.get(word)
        if bad is None:
            low = word.lower()
            if low in self.user_words or low in self.ignored_words:
                bad = False
            else:
                try:
                    bad = not self.spell.lookup(word)
                except Exception:
                    bad = False
            self._word_cache[word] = bad
        return bad

    def run_spell_check_now(self):
        self._spell_job = None
        self.text.tag_remove("misspelled", "1.0", "end")
        if not self.spell_enabled or self.spell is None:
            return

        content = self.text.get("1.0", "end-1c")
        for ln, line in enumerate(content.split("\n"), 1):
            skip_spans = [m.span() for m in SKIP_RE.finditer(line)]
            for m in WORD_RE.finditer(line):
                word = m.group()
                if len(word) < 2 or any(c.isdigit() for c in word):
                    continue
                if word.isupper():                       # skróty: ZUS, PIT, NIP
                    continue
                if skip_spans and any(a <= m.start() < b for a, b in skip_spans):
                    continue
                if self._is_misspelled(word):
                    self.text.tag_add("misspelled", f"{ln}.{m.start()}", f"{ln}.{m.end()}")

    # =========================================================================
    # MENU KONTEKSTOWE
    # =========================================================================
    def _on_right_click(self, event):
        click_idx = self.text.index(f"@{event.x},{event.y}")

        # Przenieś kursor w miejsce kliknięcia, o ile nie kliknięto w zaznaczenie
        in_selection = False
        try:
            in_selection = (self.text.compare(click_idx, ">=", "sel.first")
                            and self.text.compare(click_idx, "<", "sel.last"))
        except tk.TclError:
            pass
        if not in_selection:
            self.text.tag_remove("sel", "1.0", "end")
            self.text.mark_set("insert", click_idx)
        self.text.focus_set()

        popup = self._new_menu(self.root)
        tags = self.text.tag_names(click_idx)

        if "misspelled" in tags and self.spell is not None:
            word_start = self.text.index(f"{click_idx} wordstart")
            word_end = self.text.index(f"{click_idx} wordend")
            word = self.text.get(word_start, word_end).strip()

            candidates = []
            if word:
                self.text.config(cursor="watch")
                self.text.update_idletasks()
                try:
                    candidates = list(islice(self.spell.suggest(word), 6))
                except Exception:
                    candidates = []
                self.text.config(cursor="xterm")
            if candidates:
                popup.add_command(label=f"Sugerowane poprawki dla: \"{word}\"", state="disabled")
                for cand in candidates:
                    popup.add_command(
                        label=f"   {cand}",
                        font=(FONT_FAMILY, 10, "bold"),
                        command=lambda r=cand, s=word_start, e=word_end: self._apply_correction(s, e, r)
                    )
                popup.add_separator()
            else:
                popup.add_command(label="Brak sugestii", state="disabled")
                popup.add_separator()

            self._menu_item(popup, "Ignoruj to słowo (do zamknięcia programu)", "check",
                            lambda w=word: self._ignore_word(w))
            self._menu_item(popup, f"Dodaj „{word}” do słownika", "plus",
                            lambda w=word: self._add_to_dictionary(w))
            popup.add_separator()

        link = self._link_at(click_idx)
        if link:
            self._menu_item(popup, "Otwórz link", "external", lambda u=link: self._open_url(u))
            self._menu_item(popup, "Kopiuj adres linku", "copy", lambda u=link: self._copy_to_clipboard(u))
            popup.add_separator()

        self._menu_item(popup, "Wytnij", "cut", lambda: self.text.event_generate("<<Cut>>"), "Ctrl+X")
        self._menu_item(popup, "Kopiuj", "copy", lambda: self.text.event_generate("<<Copy>>"), "Ctrl+C")
        self._menu_item(popup, "Wklej", "paste", lambda: self.text.event_generate("<<Paste>>"), "Ctrl+V")
        popup.add_separator()
        self._menu_item(popup, "Zaznacz wszystko", "select-all", self._select_all, "Ctrl+A")
        popup.add_separator()
        lena_sub = self._new_menu(popup)
        self._build_lena_menu(lena_sub)
        img = self.icons.image("wand")
        kw = {"label": " Lena — asystent AI", "menu": lena_sub}
        if img is not None:
            kw.update(image=img, compound="left")
        popup.add_cascade(**kw)

        try:
            popup.tk_popup(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def _apply_correction(self, start: str, end: str, replacement: str):
        self.text.delete(start, end)
        self.text.insert(start, replacement)

    def _add_to_dictionary(self, word: str):
        if not word:
            return
        low = word.lower()
        self.user_words.add(low)
        self._word_cache.clear()
        try:
            with open(USER_DICT_PATH, "a", encoding="utf-8") as fh:
                fh.write(low + "\n")
        except OSError:
            pass
        self.run_spell_check_now()

    def _ignore_word(self, word: str):
        self.ignored_words.add(word.lower())
        self._word_cache.clear()
        self.run_spell_check_now()

    # =========================================================================
    # LINKI
    # =========================================================================
    def _schedule_link_scan(self):
        if self._link_job:
            self.root.after_cancel(self._link_job)
        self._link_job = self.root.after(250, self._scan_links)

    def _scan_links(self):
        self._link_job = None
        self.text.tag_remove("link", "1.0", "end")
        content = self.text.get("1.0", "end-1c")
        if "://" not in content and "www." not in content and "@" not in content:
            return
        for ln, line in enumerate(content.split("\n"), 1):
            for m in LINK_RE.finditer(line):
                url = m.group()
                while url and (url[-1] in ".,;:!?" or (url[-1] == ")" and url.count("(") < url.count(")"))):
                    url = url[:-1]
                if len(url) > 3:
                    self.text.tag_add("link", f"{ln}.{m.start()}", f"{ln}.{m.start() + len(url)}")

    def _link_at(self, index) -> str | None:
        rng = self.text.tag_prevrange("link", f"{index}+1c")
        if rng and self.text.compare(rng[0], "<=", index) and self.text.compare(index, "<", rng[1]):
            return self.text.get(rng[0], rng[1])
        return None

    def _on_link_click(self, event):
        if self.text.tag_ranges("sel"):          # przeciąganie = zaznaczanie, nie kliknięcie
            return
        if self.link_ctrl_var.get() and not (event.state & 0x4):
            return
        url = self._link_at(self.text.index(f"@{event.x},{event.y}"))
        if url:
            self._open_url(url)

    def _open_url(self, url: str):
        if "@" in url and "://" not in url and not url.lower().startswith("www."):
            url = "mailto:" + url
        elif url.lower().startswith("www."):
            url = "https://" + url
        try:
            webbrowser.open(url)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Nie udało się otworzyć linku:\n{url}\n\n{exc}")

    def _copy_to_clipboard(self, value: str):
        self.root.clipboard_clear()
        self.root.clipboard_append(value)

    def _on_link_setting_changed(self):
        self.settings["link_ctrl"] = self.link_ctrl_var.get()
        save_settings(self.settings)

    # =========================================================================
    # SEJFY (foldery szybkiego zapisu)
    # =========================================================================
    def _rebuild_vault_menu(self):
        menu = self.vault_menu
        menu.delete(0, "end")
        for i, vault in enumerate(self.vaults):
            img = self.icons.image("vault")
            kw = {"label": f" {vault['name']}", "command": lambda v=vault: self.save_to_vault(v),
                  "accelerator": f"Ctrl+{i + 1}" if i < 9 else ""}
            if img is not None:
                kw.update(image=img, compound="left")
            menu.add_command(**kw)
        if not self.vaults:
            menu.add_command(label="(nie dodano jeszcze żadnego sejfu)", state="disabled")
        menu.add_separator()
        self._menu_item(menu, "Zarządzaj sejfami…", "gear", self.open_vault_manager)

    def _rebuild_vault_bar(self):
        bar = self.vault_bar
        for child in bar.winfo_children():
            child.destroy()

        if self.icons.available:
            tk.Label(bar, text=FA["vault"], font=self.icons.tk_font(10), bg=UI_BG,
                     fg=UI_MUTED).pack(side="left", padx=(10, 6))
        tk.Label(bar, text="Szybki zapis:", font=(FONT_FAMILY, 9), bg=UI_BG,
                 fg=UI_MUTED).pack(side="left", padx=(0, 6))

        def style_button(btn):
            btn.config(bg=UI_BG, fg=UI_ICON, activebackground=UI_PRESSED, activeforeground=UI_ICON,
                       relief="flat", bd=0, padx=8, pady=3, cursor="hand2", takefocus=0)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=UI_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=UI_BG))

        for i, vault in enumerate(self.vaults):
            img = self.icons.image("vault", color=UI_ACCENT, size=13)
            btn = tk.Button(bar, text=vault["name"], font=(FONT_FAMILY, 9),
                            command=lambda v=vault: self.save_to_vault(v))
            if img is not None:
                btn.config(image=img, compound="left")
            style_button(btn)
            btn.pack(side="left", padx=1, pady=2)
            hotkey = f"  (Ctrl+{i + 1})" if i < 9 else ""
            self._add_tooltip(btn, f"Zapisz w sejfie „{vault['name']}”{hotkey}\n{vault['path']}")

        if not self.vaults:
            tk.Label(bar, text="brak sejfów — dodaj folder przyciskiem zębatki →",
                     font=(FONT_FAMILY, 9, "italic"), bg=UI_BG, fg=UI_MUTED2).pack(side="left", padx=4)

        gear = tk.Button(bar, text="Sejfy…", font=(FONT_FAMILY, 9), command=self.open_vault_manager)
        gimg = self.icons.image("gear", color=UI_MUTED, size=13)
        if gimg is not None:
            gear.config(image=gimg, compound="left")
        style_button(gear)
        gear.pack(side="right", padx=6, pady=2)
        self._add_tooltip(gear, "Dodaj, usuń i uporządkuj sejfy (foldery szybkiego zapisu)")

    def _vault_hotkey(self, index: int):
        if index < len(self.vaults):
            self.save_to_vault(self.vaults[index])

    def _on_default_format_changed(self):
        self.settings["default_format"] = self.default_format_var.get()
        save_settings(self.settings)

    def _suggest_filename(self) -> str:
        if self.current_filepath:
            return os.path.splitext(os.path.basename(self.current_filepath))[0]
        if self._lena_name:
            return self._lena_name
        for line in self.text.get("1.0", "end-1c").split("\n"):
            line = line.strip().lstrip("•#-* ").strip()
            if line:
                return re.sub(r'[\\/:*?"<>|\r\n\t]+', "", line)[:60].strip(" .")
        return ""

    def save_to_vault(self, vault: dict) -> bool:
        folder = vault["path"]
        if not os.path.isdir(folder):
            messagebox.showerror(
                APP_NAME,
                f"Folder sejfu „{vault['name']}” nie istnieje:\n{folder}\n\n"
                "Zmień jego ścieżkę w Narzędzia → Zarządzaj sejfami."
            )
            return False
        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            title=f"Zapisz w sejfie: {vault['name']}",
            initialdir=folder,
            initialfile=self._suggest_filename(),
            defaultextension=".md",
            filetypes=[("Markdown (*.md)", "*.md"), ("Pliki tekstowe (*.txt)", "*.txt"),
                       ("Dokument RTF (*.rtf)", "*.rtf")],
        )
        if not filepath:
            return False
        return self._write_to_disk(filepath)

    def open_vault_manager(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Sejfy — foldery szybkiego zapisu")
        dlg.transient(self.root)
        dlg.geometry("680x360")
        dlg.minsize(520, 300)
        dlg.configure(bg=UI_BG)
        try:
            dlg.iconbitmap(os.path.join(BASE_DIR, "assets", "ikona.ico"))
        except tk.TclError:
            pass
        dlg.update_idletasks()
        x = self.root.winfo_rootx() + max((self.root.winfo_width() - 680) // 2, 0)
        y = self.root.winfo_rooty() + 40
        dlg.geometry(f"+{x}+{y}")

        tk.Label(
            dlg, bg=UI_BG, fg=UI_HINT, font=(FONT_FAMILY, 9), justify="left", anchor="w",
            text="Dodaj foldery (np. sejfy z notatkami). Kliknięcie sejfu na pasku narzędzi albo Ctrl+1…9\n"
                 "otwiera okno zapisu od razu w tym folderze — wpisujesz tylko nazwę pliku."
        ).pack(fill="x", padx=14, pady=(12, 6))

        body = tk.Frame(dlg, bg=UI_BG)
        body.pack(fill="both", expand=True, padx=14, pady=4)

        tree = ttk.Treeview(body, columns=("name", "path"), show="headings", selectmode="browse")
        tree.heading("name", text="Nazwa")
        tree.heading("path", text="Folder")
        tree.column("name", width=170, anchor="w")
        tree.column("path", width=300, anchor="w")
        tree.pack(side="left", fill="both", expand=True)

        side = tk.Frame(body, bg=UI_BG)
        side.pack(side="right", fill="y", padx=(10, 0))

        def refresh(select: int | None = None):
            tree.delete(*tree.get_children())
            for i, v in enumerate(self.vaults):
                tree.insert("", "end", iid=str(i), values=(v["name"], v["path"]))
            if select is not None and 0 <= select < len(self.vaults):
                tree.selection_set(str(select))
                tree.see(str(select))
            self._rebuild_vault_menu()
            self._rebuild_vault_bar()

        def commit(select: int | None = None):
            self.settings["vaults"] = self.vaults
            save_settings(self.settings)
            refresh(select)

        def selected() -> int | None:
            sel = tree.selection()
            return int(sel[0]) if sel else None

        def add():
            folder = filedialog.askdirectory(parent=dlg, title="Wybierz folder sejfu", mustexist=True)
            if not folder:
                return
            folder = os.path.normpath(folder)
            if any(os.path.normcase(v["path"]) == os.path.normcase(folder) for v in self.vaults):
                messagebox.showinfo(APP_NAME, "Ten folder jest już na liście.", parent=dlg)
                return
            name = simpledialog.askstring(
                "Nazwa sejfu", "Nazwa widoczna na pasku:",
                initialvalue=os.path.basename(folder) or folder, parent=dlg
            )
            if not name or not name.strip():
                return
            self.vaults.append({"name": name.strip(), "path": folder})
            commit(len(self.vaults) - 1)

        def rename():
            i = selected()
            if i is None:
                return
            name = simpledialog.askstring(
                "Zmień nazwę", "Nowa nazwa sejfu:", initialvalue=self.vaults[i]["name"], parent=dlg
            )
            if name and name.strip():
                self.vaults[i]["name"] = name.strip()
                commit(i)

        def change_folder():
            i = selected()
            if i is None:
                return
            folder = filedialog.askdirectory(parent=dlg, title="Nowy folder sejfu",
                                             initialdir=self.vaults[i]["path"])
            if folder:
                self.vaults[i]["path"] = os.path.normpath(folder)
                commit(i)

        def remove():
            i = selected()
            if i is None:
                return
            if messagebox.askyesno(
                APP_NAME, f"Usunąć sejf „{self.vaults[i]['name']}” z listy?\n"
                          "(Folder i notatki na dysku zostaną nietknięte.)", parent=dlg
            ):
                del self.vaults[i]
                commit(min(i, len(self.vaults) - 1))

        def move(delta: int):
            i = selected()
            if i is None or not 0 <= i + delta < len(self.vaults):
                return
            self.vaults[i], self.vaults[i + delta] = self.vaults[i + delta], self.vaults[i]
            commit(i + delta)

        def dlg_button(text, icon, command):
            img = self.icons.image(icon, size=12)
            btn = ttk.Button(side, text=" " + text, command=command, width=18)
            if img is not None:
                btn.config(image=img, compound="left")
                self._icon_refs.append(img)
            btn.pack(fill="x", pady=2)

        dlg_button("Dodaj folder…", "folder-plus", add)
        dlg_button("Zmień nazwę…", "pen", rename)
        dlg_button("Zmień folder…", "folder-open", change_folder)
        dlg_button("Usuń z listy", "trash", remove)
        dlg_button("Wyżej", "arrow-up", lambda: move(-1))
        dlg_button("Niżej", "arrow-down", lambda: move(1))

        ttk.Button(dlg, text="Zamknij", command=dlg.destroy).pack(side="bottom", anchor="e", padx=14, pady=10)
        tree.bind("<Double-1>", lambda e: rename())

        refresh(0 if self.vaults else None)
        dlg.grab_set()
        dlg.focus_set()

    # =========================================================================
    # ZNAJDŹ I ZAMIEŃ
    # =========================================================================
    def _build_findbar(self):
        bar = ttk.Frame(self.root, padding=(8, 5))
        self.find_bar = bar

        row1 = ttk.Frame(bar)
        row1.pack(fill="x")
        ttk.Label(row1, text="Znajdź:", width=10).pack(side="left")
        self.find_entry = ttk.Entry(row1, textvariable=self.find_text_var, width=30)
        self.find_entry.pack(side="left", padx=(0, 6))
        ttk.Button(row1, text="▲", width=3, command=lambda: self._find_step(-1)).pack(side="left")
        ttk.Button(row1, text="▼", width=3, command=lambda: self._find_step(1)).pack(side="left", padx=(2, 8))
        self.find_count = ttk.Label(row1, text="", width=14)
        self.find_count.pack(side="left")
        ttk.Checkbutton(row1, text="Aa", variable=self.find_case_var,
                        command=self._find_refresh).pack(side="left", padx=4)
        ttk.Checkbutton(row1, text="Całe słowa", variable=self.find_word_var,
                        command=self._find_refresh).pack(side="left", padx=4)
        ttk.Button(row1, text="✕", width=3, command=self.hide_find).pack(side="right")

        self.replace_row = ttk.Frame(bar)
        ttk.Label(self.replace_row, text="Zamień na:", width=10).pack(side="left")
        self.replace_entry = ttk.Entry(self.replace_row, textvariable=self.replace_var, width=30)
        self.replace_entry.pack(side="left", padx=(0, 6))
        ttk.Button(self.replace_row, text="Zamień", command=self._replace_one).pack(side="left", padx=2)
        ttk.Button(self.replace_row, text="Zamień wszystkie",
                   command=self._replace_all).pack(side="left", padx=2)

        for entry in (self.find_entry, self.replace_entry):
            entry.bind("<Escape>", lambda e: self.hide_find())
        self.find_entry.bind("<Return>", lambda e: self._find_step(1))
        self.find_entry.bind("<Shift-Return>", lambda e: self._find_step(-1))
        self.replace_entry.bind("<Return>", lambda e: self._replace_one())
        self.find_text_var.trace_add("write", lambda *a: self._find_refresh())

    def show_find(self, replace: bool = False):
        if not self._find_visible:
            self.find_bar.pack(side="top", fill="x", before=self.editor_container)
            self._find_visible = True
        if replace:
            self.replace_row.pack(fill="x", pady=(4, 0))
        try:
            sel = self.text.get("sel.first", "sel.last")
            if sel and "\n" not in sel and len(sel) <= 100:
                self.find_text_var.set(sel)
        except tk.TclError:
            pass
        target = self.replace_entry if (replace and self.find_text_var.get()) else self.find_entry
        target.focus_set()
        target.selection_range(0, "end")
        self._find_refresh()

    def hide_find(self):
        self._find_visible = False
        self.find_bar.pack_forget()
        self.text.tag_remove("find_match", "1.0", "end")
        self.text.tag_remove("find_current", "1.0", "end")
        self._find_hits = []
        self.text.focus_set()
        return "break"

    def _on_escape(self, event):
        if self._find_visible:
            return self.hide_find()
        return None

    def _schedule_find_refresh(self):
        if self._find_job:
            self.root.after_cancel(self._find_job)
        self._find_job = self.root.after(250, self._find_refresh)

    def _find_refresh(self):
        self._find_job = None
        self.text.tag_remove("find_match", "1.0", "end")
        self.text.tag_remove("find_current", "1.0", "end")
        self._find_hits = []
        query = self.find_text_var.get()
        if not self._find_visible or not query:
            self.find_count.config(text="")
            return

        pattern = re.escape(query)
        if self.find_word_var.get():
            pattern = r"(?<!\w)" + pattern + r"(?!\w)"
        rx = re.compile(pattern, 0 if self.find_case_var.get() else re.IGNORECASE)

        hits = self._find_hits
        content = self.text.get("1.0", "end-1c")
        for ln, line in enumerate(content.split("\n"), 1):
            for m in rx.finditer(line):
                hits.append((ln, m.start(), m.end()))
            if len(hits) > 20000:
                break
        for ln, s, e in hits:
            self.text.tag_add("find_match", f"{ln}.{s}", f"{ln}.{e}")
        n = len(hits)
        if n == 1:
            label = "1 wynik"
        elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            label = f"{n} wyniki"
        else:
            label = f"{n} wyników"
        self.find_count.config(text=label if hits else "Brak wyników")

    def _find_step(self, direction: int):
        if not self._find_visible:
            self.show_find()
            return
        if self._find_job:
            self._find_refresh()
        hits = self._find_hits
        if not hits:
            return

        def pos(idx):
            ln, col = str(idx).split(".")
            return int(ln), int(col)

        try:
            first, last = pos(self.text.index("sel.first")), pos(self.text.index("sel.last"))
            has_sel = True
        except tk.TclError:
            has_sel = False
            first = last = pos(self.text.index("insert"))

        if direction > 0:
            target = next((h for h in hits if (h[0], h[1]) >= last), hits[0])
        else:
            target = next((h for h in reversed(hits) if (h[0], h[1]) < first), hits[-1])

        ln, s, e = target
        a, b = f"{ln}.{s}", f"{ln}.{e}"
        self.text.tag_remove("sel", "1.0", "end")
        self.text.tag_add("sel", a, b)
        self.text.tag_remove("find_current", "1.0", "end")
        self.text.tag_add("find_current", a, b)
        self.text.mark_set("insert", b if direction > 0 else a)
        self.text.see(a)
        self.find_count.config(text=f"{hits.index(target) + 1} / {len(hits)}")

    def _replace_one(self):
        if self._find_job:
            self._find_refresh()
        try:
            a, b = self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            self._find_step(1)
            return
        sa, sb = (int(x) for x in a.split(".")), (int(x) for x in b.split("."))
        sa, sb = tuple(sa), tuple(sb)
        if not any(h[0] == sa[0] == sb[0] and h[1] == sa[1] and h[2] == sb[1] for h in self._find_hits):
            self._find_step(1)
            return
        repl = self.replace_var.get()
        self.text.edit_separator()
        self.text.delete(a, b)
        self.text.insert(a, repl)
        self.text.edit_separator()
        self.text.tag_remove("sel", "1.0", "end")
        self.text.mark_set("insert", f"{a}+{len(repl)}c")
        self._find_refresh()
        self._find_step(1)

    def _replace_all(self):
        if self._find_job:
            self._find_refresh()
        hits = list(self._find_hits)
        if not hits:
            return
        repl = self.replace_var.get()
        self.text.edit_separator()
        for ln, s, e in reversed(hits):
            self.text.delete(f"{ln}.{s}", f"{ln}.{e}")
            self.text.insert(f"{ln}.{s}", repl)
        self.text.edit_separator()
        self._find_refresh()
        self.find_count.config(text=f"Zamieniono: {len(hits)}")

    # =========================================================================
    # KOPIA ROBOCZA (odzyskiwanie po awarii)
    # =========================================================================
    def _autosave_tick(self):
        if self._is_modified and self._recovery_dirty:
            try:
                self._write_recovery()
            except Exception:
                pass
        self.root.after(15000, self._autosave_tick)

    def _write_recovery(self):
        os.makedirs(RECOVERY_DIR, exist_ok=True)
        with open(RECOVERY_RTF, "wb") as fh:
            fh.write(self._build_rtf().encode("ascii", errors="replace"))
        with open(RECOVERY_META, "w", encoding="utf-8") as fh:
            json.dump({"path": self.current_filepath,
                       "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, fh,
                      ensure_ascii=False)
        self._recovery_dirty = False

    def _clear_recovery(self):
        self._recovery_dirty = False
        for path in (RECOVERY_RTF, RECOVERY_META):
            try:
                os.remove(path)
            except OSError:
                pass

    def _startup_recovery(self, initial_file: str | None):
        meta = {}
        try:
            with open(RECOVERY_META, "r", encoding="utf-8") as fh:
                meta = json.load(fh)
        except (OSError, ValueError):
            pass
        name = os.path.basename(meta.get("path") or "") or "Nowy dokument"
        restore = messagebox.askyesno(
            APP_NAME,
            "Program nie został zamknięty poprawnie — znaleziono niezapisaną kopię notatki.\n\n"
            f"Dokument: {name}\nKopia z: {meta.get('saved_at', '?')}\n\nPrzywrócić ją?"
        )
        if restore:
            try:
                with open(RECOVERY_RTF, "rb") as fh:
                    runs, colors = parse_rtf(fh.read().decode("latin-1"))
                self._reset_document()
                self._insert_rtf_runs(runs, colors)
                self.text.edit_reset()
                path = meta.get("path")
                self.current_filepath = path if path and os.path.isfile(path) else None
                self._is_modified = True
                self._recovery_dirty = True
                self._refresh_title()
                self._update_statusbar()
                self._schedule_spell_check()
                self._schedule_link_scan()
                return
            except Exception as exc:
                messagebox.showerror(APP_NAME, f"Nie udało się przywrócić kopii:\n{exc}")
        self._clear_recovery()
        if initial_file and os.path.isfile(initial_file):
            self._load_file(initial_file)

    # =========================================================================
    # OSTATNIO OTWARTE + PRZECIĄGANIE PLIKÓW
    # =========================================================================
    def _add_recent(self, path: str):
        path = os.path.normpath(path)
        self.recent[:] = [p for p in self.recent if os.path.normcase(p) != os.path.normcase(path)]
        self.recent.insert(0, path)
        del self.recent[12:]
        self.settings["recent"] = self.recent
        save_settings(self.settings)
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self):
        menu = self.recent_menu
        menu.delete(0, "end")
        for path in self.recent:
            folder = os.path.basename(os.path.dirname(path))
            if len(folder) > 26:
                folder = folder[:25] + "…"
            self._menu_item(menu, os.path.basename(path), "file",
                            lambda p=path: self._open_recent(p), folder)
        if not self.recent:
            menu.add_command(label="(brak)", state="disabled")
        else:
            menu.add_separator()
            self._menu_item(menu, "Wyczyść listę", "trash", self._clear_recent)

    def _clear_recent(self):
        self.recent.clear()
        self.settings["recent"] = self.recent
        save_settings(self.settings)
        self._rebuild_recent_menu()

    def _open_recent(self, path: str):
        if not os.path.isfile(path):
            messagebox.showerror(APP_NAME, f"Plik nie istnieje:\n{path}")
            self.recent[:] = [p for p in self.recent if p != path]
            save_settings(self.settings)
            self._rebuild_recent_menu()
            return
        if self._check_save_changes():
            self._load_file(path)

    def _setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            for widget in (self.root, self.text):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

    def _on_drop(self, event):
        try:
            files = self.root.tk.splitlist(event.data)
        except tk.TclError:
            files = []
        path = next((f for f in files if os.path.isfile(f)), None)
        if path and self._check_save_changes():
            self._load_file(path)
        return "copy"

    # =========================================================================
    # MOTYW (jasny / ciemny), ZAWSZE NA WIERZCHU
    # =========================================================================
    def _on_theme_toggle(self):
        self._apply_theme("dark" if self.dark_var.get() else "light")

    def _apply_theme(self, name: str):
        old = dict(THEME)
        set_theme(name)
        new = THEME
        self.settings["theme"] = name
        save_settings(self.settings)

        mapping = {old[k].lower(): new[k] for k in THEME_ROLES if old[k].lower() != new[k].lower()}
        options = ("bg", "fg", "activebackground", "activeforeground", "highlightbackground")

        def walk(widget):
            for child in widget.winfo_children():
                if isinstance(child, (tk.Toplevel, tk.Menu, tk.Text)):
                    continue
                for opt in options:
                    try:
                        value = str(child.cget(opt)).lower()
                    except tk.TclError:
                        continue
                    if value in mapping:
                        child.configure(**{opt: mapping[value]})
                walk(child)

        walk(self.root)
        self.root.configure(bg=new["bg"])
        self.text.config(bg=new["editor_bg"], fg=new["editor_fg"], insertbackground=new["editor_fg"],
                         selectbackground=new["select"], selectforeground=new["editor_fg"])
        self._configure_tags()
        self._style_ttk()
        self._populate_menubar()
        self._rebuild_vault_bar()
        self._set_dark_titlebar(name == "dark")

    def _style_ttk(self):
        style = ttk.Style(self.root)
        if THEME is not THEMES["dark"]:
            style.theme_use(self._ttk_light)
            return
        t = THEME
        style.theme_use("clam")
        style.configure(".", background=t["bg"], foreground=t["text"], fieldbackground=t["editor_bg"],
                        bordercolor=t["border"], troughcolor=t["editor_bg"], lightcolor=t["bg"],
                        darkcolor=t["bg"], focuscolor=t["bg"], insertcolor=t["text"])
        style.configure("TButton", background=t["hover"], foreground=t["text"], padding=(8, 3))
        style.map("TButton", background=[("active", t["pressed"])])
        style.configure("TEntry", fieldbackground=t["editor_bg"], foreground=t["text"])
        style.configure("TCheckbutton", background=t["bg"], foreground=t["text"])
        style.map("TCheckbutton", background=[("active", t["bg"])])
        style.configure("Treeview", background=t["editor_bg"], fieldbackground=t["editor_bg"],
                        foreground=t["text"])
        style.map("Treeview", background=[("selected", t["select"])], foreground=[("selected", t["text"])])
        style.configure("Treeview.Heading", background=t["hover"], foreground=t["text"])
        style.configure("TScrollbar", background=t["hover"], troughcolor=t["bg"],
                        arrowcolor=t["text"], bordercolor=t["bg"])
        style.configure("TSeparator", background=t["border"])

    def _set_dark_titlebar(self, dark: bool):
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            value = ctypes.c_int(1 if dark else 0)
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), 4)
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x27)   # odśwież ramkę okna
        except Exception:
            pass

    def _on_topmost_toggle(self):
        on = self.topmost_var.get()
        self.root.attributes("-topmost", on)
        self.settings["topmost"] = on
        save_settings(self.settings)

    # =========================================================================
    # NARZĘDZIA TEKSTOWE: SORTOWANIE, DUPLIKATY, WIELKOŚĆ LITER, ZADANIA
    # =========================================================================
    def _line_range(self, whole_if_none: bool):
        try:
            first, last = self.text.index("sel.first"), self.text.index("sel.last")
            l1, l2 = int(first.split(".")[0]), int(last.split(".")[0])
            if last.endswith(".0") and l2 > l1:
                l2 -= 1
            return l1, l2
        except tk.TclError:
            if whole_if_none:
                return 1, int(self.text.index("end-1c").split(".")[0])
            line = int(self.text.index("insert").split(".")[0])
            return line, line

    def _replace_lines(self, l1: int, l2: int, new_lines: list):
        old = self.text.get(f"{l1}.0", f"{l2}.end")
        new = "\n".join(new_lines)
        if old == new:
            return
        self.text.edit_separator()
        self.text.delete(f"{l1}.0", f"{l2}.end")
        self.text.insert(f"{l1}.0", new)
        self.text.edit_separator()

    def tool_sort_lines(self, reverse: bool):
        l1, l2 = self._line_range(whole_if_none=True)
        lines = self.text.get(f"{l1}.0", f"{l2}.end").split("\n")
        self._replace_lines(l1, l2, sorted(lines, key=pl_sort_key, reverse=reverse))

    def tool_remove_duplicates(self):
        l1, l2 = self._line_range(whole_if_none=True)
        lines = self.text.get(f"{l1}.0", f"{l2}.end").split("\n")
        seen, result = set(), []
        for line in lines:
            key = line.strip()
            if key and key in seen:
                continue
            seen.add(key)
            result.append(line)
        removed = len(lines) - len(result)
        self._replace_lines(l1, l2, result)
        messagebox.showinfo(APP_NAME, f"Usunięto zduplikowanych linii: {removed}")

    def tool_change_case(self, mode: str):
        try:
            a, b = self.text.index("sel.first"), self.text.index("sel.last")
        except tk.TclError:
            messagebox.showinfo(APP_NAME, "Zaznacz najpierw fragment tekstu.")
            return
        old = self.text.get(a, b)
        if mode == "upper":
            new = old.upper()
        elif mode == "lower":
            new = old.lower()
        elif mode == "swap":
            new = old.swapcase()
        else:
            new = re.sub(r"[^\W\d_]+", lambda m: m.group()[0].upper() + m.group()[1:].lower(), old)
        if len(new) != len(old):                       # rzadkie znaki (np. ß) — zamiana całości
            self.text.edit_separator()
            self.text.delete(a, b)
            self.text.insert(a, new)
            self.text.edit_separator()
            return
        self.text.edit_separator()
        for i, (o, n) in enumerate(zip(old, new)):
            if o != n:                                 # zamiana znak po znaku — zachowuje formatowanie
                idx = f"{a}+{i}c"
                tags = self.text.tag_names(idx)
                self.text.delete(idx, f"{idx}+1c")
                self.text.insert(idx, n, tags)
        self.text.edit_separator()

    def action_toggle_task(self):
        l1, l2 = self._line_range(whole_if_none=False)
        self.text.edit_separator()
        for ln in range(l1, l2 + 1):
            line = self.text.get(f"{ln}.0", f"{ln}.end")
            m = TASK_RE.match(line)
            if m:
                indent = len(m.group(1))
                if m.group(2) == " ":
                    self.text.delete(f"{ln}.{indent + 3}", f"{ln}.{indent + 4}")
                    self.text.insert(f"{ln}.{indent + 3}", "x")
                else:
                    prefix = TASK_PREFIX_RE.match(line).end()
                    self.text.delete(f"{ln}.{indent}", f"{ln}.{prefix}")
            elif line.startswith("• "):
                self.text.delete(f"{ln}.0", f"{ln}.2")
                self.text.insert(f"{ln}.0", "- [ ] ")
            else:
                indent = len(line) - len(line.lstrip())
                self.text.insert(f"{ln}.{indent}", "- [ ] ")
        self.text.edit_separator()

    # =========================================================================
    # LENA — ASYSTENT AI (Groq)
    # =========================================================================
    def _build_lena_menu(self, menu: tk.Menu):
        def run(action):
            return lambda: self.lena_run(action)

        item = self._menu_item
        item(menu, "Popraw tekst (pisownia, interpunkcja, styl)", "check", run("fix"))
        item(menu, "Skróć", "compress", run("shorten"))
        item(menu, "Rozwiń", "expand", run("expand"))
        tone = self._new_menu(menu)
        item(tone, "Formalnie", "briefcase", run("tone_formal"))
        item(tone, "Przyjaźnie", "smile", run("tone_friendly"))
        item(tone, "Prostszym językiem", "child", run("tone_simple"))
        img = self.icons.image("pen")
        kw = {"label": " Zmień ton", "menu": tone}
        if img is not None:
            kw.update(image=img, compound="left")
        menu.add_cascade(**kw)
        item(menu, "Przetłumacz (PL ⇄ EN)", "language", run("translate"))
        menu.add_separator()
        item(menu, "Streść notatkę", "align", run("summary"))
        item(menu, "Wyciągnij zadania z notatki", "tasks", run("tasks"))
        item(menu, "Zaproponuj nazwę pliku", "filesig", run("filename"))
        menu.add_separator()
        item(menu, "Ustawienia Leny (klucz API)…", "key", self.open_lena_settings)

    def _post_lena_menu(self):
        menu = self._new_menu(self.root)
        self._build_lena_menu(menu)
        btn = self.lena_btn
        try:
            menu.tk_popup(btn.winfo_rootx(), btn.winfo_rooty() + btn.winfo_height())
        finally:
            menu.grab_release()

    def _new_dialog(self, title: str, w: int | None = None, h: int | None = None) -> tk.Toplevel:
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.configure(bg=UI_BG)
        try:
            dlg.iconbitmap(os.path.join(BASE_DIR, "assets", "ikona.ico"))
        except tk.TclError:
            pass
        x = self.root.winfo_rootx() + max((self.root.winfo_width() - (w or 600)) // 2, 0)
        y = self.root.winfo_rooty() + 40
        dlg.geometry(f"{w}x{h}+{x}+{y}" if w and h else f"+{x}+{y}")
        return dlg

    def _run_in_background(self, func, on_done):
        """Wykonuje func() w wątku; on_done(wynik, błąd) wywoływane jest w wątku okna."""
        box: dict = {}

        def worker():
            try:
                box["value"] = func()
            except lena.LenaError as exc:
                box["error"] = exc
            except Exception as exc:
                box["error"] = lena.LenaError(
                    "Coś poszło nie tak po stronie programu. Spróbuj jeszcze raz.", repr(exc))

        def poll():
            if box:
                on_done(box.get("value"), box.get("error"))
            else:
                self.root.after(150, poll)

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(150, poll)

    def lena_run(self, action: str):
        if self._lena_busy:
            messagebox.showinfo("Lena", "Lena jeszcze pracuje nad poprzednim zadaniem. "
                                        "Poczekaj chwilę.", parent=self.root)
            return
        spec = lena.ACTIONS[action]
        if not lena.load_key():
            self.open_lena_settings(intro=True)
        key = lena.load_key()
        if not key:
            return

        start, end = self._get_selection()
        if start:
            source = self.text.get(start, end)
        elif spec["whole_ok"]:
            source = self.text.get("1.0", "end-1c")
        else:
            messagebox.showinfo(
                "Lena", "Zaznacz najpierw fragment tekstu, który Lena ma przerobić.\n"
                        "(Całą notatkę zaznaczysz skrótem Ctrl+A.)", parent=self.root)
            return
        if not source.strip():
            messagebox.showinfo("Lena", "Nie ma tu jeszcze żadnego tekstu, nad którym Lena mogłaby "
                                        "popracować.", parent=self.root)
            return
        if action != "filename" and len(source) > lena.MAX_INPUT_CHARS:
            messagebox.showinfo(
                "Lena",
                f"Ten tekst jest za długi dla darmowego limitu Leny ({len(source)} znaków, "
                f"maksimum to {lena.MAX_INPUT_CHARS}).\n\nZaznacz krótszy fragment — "
                "na przykład kilka akapitów — i spróbuj jeszcze raz.", parent=self.root)
            return

        if start:
            self.text.mark_set("lena_a", start)
            self.text.mark_gravity("lena_a", "left")
            self.text.mark_set("lena_b", end)
        model = self.settings.get("lena_model", lena.DEFAULT_MODEL)
        self._lena_busy = True
        self.status_lena.config(text="Lena pracuje…")
        self._run_in_background(
            lambda: lena.ask(action, source, key, model),
            lambda result, error: self._lena_done(action, source, bool(start), result, error))

    def _lena_done(self, action: str, source: str, had_selection: bool, result, error):
        self._lena_busy = False
        self.status_lena.config(text="")
        if error:
            messagebox.showwarning("Lena", error.full_text(), parent=self.root)
            return
        if action == "tasks" and result.strip().upper().startswith(lena.NO_TASKS_MARKER):
            messagebox.showinfo("Lena", "Lena nie znalazła w tej notatce żadnych zadań do "
                                        "zrobienia.", parent=self.root)
            return
        if action == "filename":
            result = self._clean_filename(result)
            if not result:
                messagebox.showwarning("Lena", "Lena nie zaproponowała sensownej nazwy. "
                                               "Spróbuj jeszcze raz.", parent=self.root)
                return
        self._lena_show_result(action, source, had_selection, result)

    @staticmethod
    def _clean_filename(name: str) -> str:
        lines = name.strip().splitlines()
        name = lines[0] if lines else ""
        name = re.sub(r'[\\/:*?"<>|\r\n\t]+', "", name).strip(" .'“”„")
        name = re.sub(r"\.(md|txt|rtf)$", "", name, flags=re.IGNORECASE)
        return name[:60].strip(" .")

    def _lena_show_result(self, action: str, source: str, had_selection: bool, result: str):
        spec = lena.ACTIONS[action]
        is_name = action == "filename"
        dlg = self._new_dialog(f"Lena — {spec['title'].lower()}", 660, 230 if is_name else 470)
        dlg.minsize(480, 200 if is_name else 320)

        tk.Label(dlg, text=f"{spec['title']} — propozycja Leny", bg=UI_BG, fg=UI_TEXT,
                 font=(FONT_FAMILY, 11, "bold"), anchor="w").pack(fill="x", padx=14, pady=(12, 0))
        hint = ("Możesz tu jeszcze poprawić nazwę. Pojawi się w oknie zapisu (np. w sejfie)."
                if is_name else
                "Możesz poprawić tekst poniżej, zanim go wstawisz. Lena bywa omylna — "
                "sprawdź wynik.")
        tk.Label(dlg, text=hint, bg=UI_BG, fg=UI_HINT, font=(FONT_FAMILY, 9), anchor="w",
                 justify="left", wraplength=620).pack(fill="x", padx=14, pady=(2, 8))

        buttons = ttk.Frame(dlg)
        buttons.pack(side="bottom", fill="x", padx=14, pady=10)

        if is_name:
            name_var = tk.StringVar(value=result)
            entry = ttk.Entry(dlg, textvariable=name_var, font=(FONT_FAMILY, 11))
            entry.pack(fill="x", padx=14, pady=4)
            get_result = lambda: self._clean_filename(name_var.get()) or result
        else:
            body = ttk.Frame(dlg)
            body.pack(fill="both", expand=True, padx=14)
            scroll = ttk.Scrollbar(body, orient="vertical")
            scroll.pack(side="right", fill="y")
            box = tk.Text(body, wrap="word", font=self.font_normal, height=8, padx=10, pady=8,
                          relief="solid", borderwidth=1, bg=THEME["editor_bg"],
                          fg=THEME["editor_fg"], insertbackground=THEME["editor_fg"],
                          selectbackground=THEME["select"], selectforeground=THEME["editor_fg"],
                          yscrollcommand=scroll.set)
            box.pack(side="left", fill="both", expand=True)
            scroll.config(command=box.yview)
            box.insert("1.0", result)
            get_result = lambda: box.get("1.0", "end-1c").strip()

        def close():
            for mark in ("lena_a", "lena_b"):
                try:
                    self.text.mark_unset(mark)
                except tk.TclError:
                    pass
            dlg.destroy()

        def use_name():
            self._lena_name = get_result()
            self.status_lena.config(text="Nazwa od Leny gotowa")
            self.root.after(5000, lambda: self.status_lena.config(text=""))
            close()

        def replace():
            new = get_result()
            try:
                current = self.text.get("lena_a", "lena_b")
                pos = self.text.index("lena_a")
            except tk.TclError:
                current = None
            if current != source:
                messagebox.showwarning(
                    "Lena", "Tekst w notatce zmienił się w międzyczasie, więc Lena nie może go "
                            "bezpiecznie zastąpić. Użyj „Wstaw pod spodem” lub „Kopiuj”.",
                    parent=dlg)
                return
            self.text.edit_separator()
            self.text.delete(pos, f"{pos}+{len(source)}c")
            self.text.insert(pos, new)
            self.text.edit_separator()
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", pos, f"{pos}+{len(new)}c")
            close()

        def insert_below():
            new = get_result()
            if had_selection:
                try:
                    pos = self.text.index("lena_b lineend")
                except tk.TclError:
                    pos = self.text.index("end-1c")
            else:
                pos = self.text.index("end-1c")
            self.text.edit_separator()
            self.text.insert(pos, "\n\n" + new)
            self.text.edit_separator()
            start = self.text.index(f"{pos}+2c")
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", start, f"{start}+{len(new)}c")
            self.text.see(start)
            close()

        def copy():
            self._copy_to_clipboard(get_result())
            self.status_lena.config(text="Skopiowano")
            self.root.after(3000, lambda: self.status_lena.config(text=""))

        if is_name:
            ttk.Button(buttons, text="Użyj tej nazwy przy zapisie", command=use_name).pack(side="left")
        else:
            if spec["replace"] and had_selection:
                ttk.Button(buttons, text="Zastąp zaznaczenie", command=replace).pack(side="left")
            ttk.Button(buttons, text="Wstaw pod spodem", command=insert_below).pack(side="left", padx=6)
        ttk.Button(buttons, text="Kopiuj", command=copy).pack(side="left", padx=(0 if is_name else 0, 6))
        ttk.Button(buttons, text="Zamknij", command=close).pack(side="right")

        dlg.protocol("WM_DELETE_WINDOW", close)
        dlg.bind("<Escape>", lambda e: close())
        dlg.grab_set()
        dlg.focus_set()

    def open_lena_settings(self, intro: bool = False):
        dlg = self._new_dialog("Lena — ustawienia asystentki AI")
        dlg.resizable(False, False)
        wrap = 560

        def label(text, bold=False, color=UI_TEXT, size=10, pady=(0, 4)):
            tk.Label(dlg, text=text, bg=UI_BG, fg=color, justify="left", anchor="w",
                     wraplength=wrap, font=(FONT_FAMILY, size, "bold" if bold else "normal")
                     ).pack(fill="x", padx=18, pady=pady)

        label("Lena — Twoja asystentka AI", bold=True, size=13, pady=(14, 4))
        if intro:
            label("Żeby Lena mogła zacząć pracę, potrzebuje darmowego klucza dostępu. "
                  "To jak osobiste hasło do jej „mózgu” — wygenerujesz je sam(a) w 2 minuty.",
                  color=UI_ACCENT, pady=(0, 8))
        else:
            label("Lena poprawia, skraca, tłumaczy i streszcza Twoje notatki. Korzysta z "
                  "darmowego konta w serwisie Groq — każdy ma własny klucz.", pady=(0, 8))

        label("Jak zdobyć klucz (za darmo):", bold=True, pady=(4, 2))
        label("1.  Kliknij przycisk poniżej. Otworzy się strona Groq — załóż konto lub zaloguj się "
              "(np. przez Google).\n"
              "2.  Kliknij „Create API Key”, wpisz dowolną nazwę (np. „Notatnik”) i skopiuj "
              "klucz. Zaczyna się od gsk_\n"
              "3.  Wklej go w pole poniżej i kliknij „Zapisz klucz”.", pady=(0, 6))
        ttk.Button(dlg, text="Otwórz stronę z kluczami Groq  (" + lena.KEYS_URL.replace("https://", "") + ")",
                   command=lambda: self._open_url(lena.KEYS_URL)).pack(anchor="w", padx=18, pady=(0, 10))

        label("Twój klucz:", bold=True, pady=(4, 2))
        key_var = tk.StringVar(value=lena.load_key())
        entry = ttk.Entry(dlg, textvariable=key_var, show="•", width=64)
        entry.pack(anchor="w", padx=18)
        show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dlg, text="Pokaż klucz", variable=show_var,
                        command=lambda: entry.config(show="" if show_var.get() else "•")
                        ).pack(anchor="w", padx=18, pady=(4, 6))

        status = tk.StringVar(value="Klucz zapisany." if key_var.get() else "Brak klucza.")
        row = ttk.Frame(dlg)
        row.pack(anchor="w", padx=18, pady=(0, 4))

        def save():
            key = key_var.get().strip()
            if not key:
                status.set("Najpierw wklej klucz w pole powyżej.")
            elif not lena.key_looks_valid(key):
                messagebox.showwarning(
                    "Lena", "To nie wygląda na klucz z Groq. Prawdziwy klucz zaczyna się od "
                            "„gsk_”, nie ma spacji i jest dość długi.\n\nSkopiuj go jeszcze raz "
                            "w całości ze strony console.groq.com/keys.", parent=dlg)
            else:
                try:
                    lena.save_key(key)
                except lena.LenaError as exc:
                    messagebox.showerror("Lena", exc.full_text(), parent=dlg)
                    return
                key_var.set(key)
                status.set("Klucz zapisany. Możesz sprawdzić połączenie albo zamknąć to okno.")

        def check():
            key = key_var.get().strip()
            if not key:
                status.set("Najpierw wklej klucz w pole powyżej.")
                return
            status.set("Sprawdzam połączenie…")
            model = self.settings.get("lena_model", lena.DEFAULT_MODEL)

            def done(_, error):
                if not dlg.winfo_exists():
                    return
                if error:
                    status.set("✗ Nie udało się połączyć.")
                    messagebox.showwarning("Lena", error.full_text(), parent=dlg)
                else:
                    status.set("✔ Połączenie działa — Lena jest gotowa do pracy!"
                               + ("" if key == lena.load_key() else " (Pamiętaj o „Zapisz klucz”.)"))

            self._run_in_background(lambda: lena.check_connection(key, model), done)

        def remove():
            if not messagebox.askyesno("Lena", "Usunąć zapisany klucz? Lena przestanie działać, "
                                               "dopóki nie wkleisz nowego.", parent=dlg):
                return
            try:
                lena.delete_key()
            except lena.LenaError as exc:
                messagebox.showerror("Lena", exc.full_text(), parent=dlg)
                return
            key_var.set("")
            status.set("Klucz usunięty.")

        ttk.Button(row, text="Zapisz klucz", command=save).pack(side="left")
        ttk.Button(row, text="Sprawdź połączenie", command=check).pack(side="left", padx=6)
        ttk.Button(row, text="Usuń klucz", command=remove).pack(side="left")
        tk.Label(dlg, textvariable=status, bg=UI_BG, fg=UI_HINT, anchor="w", justify="left",
                 wraplength=wrap, font=(FONT_FAMILY, 9, "bold")).pack(fill="x", padx=18, pady=(2, 8))

        label("Model AI:", bold=True, pady=(4, 2))
        labels = {mid: name for mid, name in lena.MODELS}
        model_var = tk.StringVar(value=labels[self.settings.get("lena_model", lena.DEFAULT_MODEL)])
        combo = ttk.Combobox(dlg, textvariable=model_var, state="readonly", width=60,
                             values=[name for _, name in lena.MODELS])
        combo.pack(anchor="w", padx=18)

        def model_changed(_=None):
            for mid, name in lena.MODELS:
                if name == model_var.get():
                    self.settings["lena_model"] = mid
                    save_settings(self.settings)

        combo.bind("<<ComboboxSelected>>", model_changed)
        label("Darmowe konto Groq ma dzienne i minutowe limity. Jeśli kiedyś się wyczerpią, "
              "Lena napisze o tym wprost — możesz wtedy przełączyć model (każdy ma własny limit) "
              "albo poczekać.", color=UI_HINT, size=9, pady=(6, 6))
        label("Prywatność: do Groq trafia wyłącznie zaznaczony fragment notatki (przy streszczeniu "
              "i zadaniach — cała notatka) i tylko po kliknięciu akcji Leny. Klucz leży w pliku "
              "lena_klucz.txt w folderze programu — nie udostępniaj tego folderu innym.",
              color=UI_HINT, size=9, pady=(0, 8))

        ttk.Button(dlg, text="Zamknij", command=dlg.destroy).pack(anchor="e", padx=18, pady=(0, 14))
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        dlg.grab_set()
        entry.focus_set()
        dlg.wait_window()

    # =========================================================================
    # POMOCNICZE
    # =========================================================================
    def _select_all(self):
        self.text.tag_add("sel", "1.0", "end")
        return "break"

    def _safe_edit(self, action: str):
        try:
            if action == "undo":
                self.text.edit_undo()
            elif action == "redo":
                self.text.edit_redo()
        except tk.TclError:
            pass
        self._update_statusbar()

    def _clear_all_tags(self):
        for t in STYLE_TAGS + FONT_TAGS + ("misspelled", "link", "find_match", "find_current"):
            self.text.tag_remove(t, "1.0", "end")

    def _mark_modified(self):
        self._recovery_dirty = True
        if not self._is_modified:
            self._is_modified = True
            self._refresh_title()

    def _set_modified(self, val: bool):
        self._is_modified = val
        if not val:
            self._clear_recovery()
        try:
            self.text.edit_modified(val)
        except tk.TclError:
            pass
        self._refresh_title()

    def _refresh_title(self):
        name = os.path.basename(self.current_filepath) if self.current_filepath else "Nowy dokument"
        mark = "● " if self._is_modified else ""
        self.root.title(f"{mark}{name} — {APP_NAME}")

    def _on_text_modified(self, event=None):
        if self.text.edit_modified():
            self._mark_modified()
            self._update_statusbar()
            self._schedule_spell_check()
            self._schedule_link_scan()
            if self._find_visible:
                self._schedule_find_refresh()
        try:
            self.text.edit_modified(False)
        except tk.TclError:
            pass

    def _update_statusbar(self, event=None):
        line, col = self.text.index("insert").split(".")
        self.status_pos.config(text=f"Ln {line}, Kol {int(col) + 1}")

        content = self.text.get("1.0", "end-1c")
        self.status_words.config(text=f"Słów: {len(content.split())}")
        self.status_chars.config(text=f"Znaków: {len(content)}")

    def _offer_shortcut(self):
        self.settings["shortcut_asked"] = True
        save_settings(self.settings)
        if messagebox.askyesno(
            APP_NAME, "Czy utworzyć skrót do programu na pulpicie?\n\n"
                      "(Możesz to zrobić później: Pomoc → Utwórz skrót na pulpicie)",
            parent=self.root,
        ):
            self._make_shortcut()

    def _make_shortcut(self):
        try:
            path = create_desktop_shortcut()
        except OSError as exc:
            messagebox.showwarning(APP_NAME, f"Nie udało się utworzyć skrótu:\n{exc}", parent=self.root)
            return
        messagebox.showinfo(APP_NAME, f"Skrót został utworzony na pulpicie:\n{path}", parent=self.root)

    def _show_about(self):
        dlg = tk.Toplevel(self.root)
        dlg.title(f"O programie — {APP_NAME}")
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.configure(bg=UI_BG)
        try:
            dlg.iconbitmap(os.path.join(BASE_DIR, "assets", "ikona.ico"))
        except tk.TclError:
            pass

        tk.Label(
            dlg, bg=UI_BG, justify="left", anchor="w", font=(FONT_FAMILY, 10),
            text=f"{APP_NAME}\n\n"
                 "Notatnik z obsługą języka polskiego:\n"
                 "• Sprawdzanie polskiej pisowni (prawy przycisk myszy)\n"
                 "• Kolorowe zakreślanie tekstu (marker)\n"
                 "• Pogrubienie, kursywa, podkreślenie\n"
                 "• Listy punktowe z automatyczną kontynuacją\n"
                 "• Zapis RTF z formatowaniem oraz zwykły TXT\n"
                 "• Lena — asystent AI (Groq): poprawia, skraca, streszcza\n\n"
                 "Autor: MrPrompt Centrum Otwartych Innowacji"
        ).pack(fill="x", padx=20, pady=(16, 0))

        url = "https://mrprompt.eu/"
        link = tk.Label(dlg, text=url, bg=UI_BG, fg="#0563C1", cursor="hand2",
                        font=(FONT_FAMILY, 10, "underline"), anchor="w")
        link.pack(fill="x", padx=20)
        link.bind("<Button-1>", lambda e: webbrowser.open(url))

        tk.Label(
            dlg, bg=UI_BG, fg=UI_HINT, justify="left", anchor="w", font=(FONT_FAMILY, 9),
            text="\nIkony: Font Awesome Free (CC BY 4.0, czcionka SIL OFL)"
        ).pack(fill="x", padx=20)

        ttk.Button(dlg, text="OK", command=dlg.destroy).pack(pady=14)
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        dlg.update_idletasks()
        x = self.root.winfo_rootx() + max((self.root.winfo_width() - dlg.winfo_width()) // 2, 0)
        y = self.root.winfo_rooty() + 60
        dlg.geometry(f"+{x}+{y}")
        dlg.grab_set()
        dlg.focus_set()

    @staticmethod
    def _add_tooltip(widget, tooltip_text: str):
        tip = [None]

        def show(e):
            if tip[0]:
                return
            t = tk.Toplevel(widget)
            t.wm_overrideredirect(True)
            t.wm_geometry(f"+{e.x_root + 10}+{e.y_root + 16}")
            tk.Label(
                t, text=tooltip_text, background="#263238", foreground="#FFFFFF",
                font=(FONT_FAMILY, 9), padx=7, pady=3, relief="flat"
            ).pack()
            tip[0] = t

        def hide(e):
            if tip[0]:
                tip[0].destroy()
                tip[0] = None

        widget.bind("<Enter>", show, add="+")
        widget.bind("<Leave>", hide, add="+")
        widget.bind("<ButtonPress>", hide, add="+")


def main():
    try:
        windll = ctypes.windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    Icons.register_font()
    try:  # własna grupa na pasku zadań (zamiast ikony Pythona)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MrPrompt.Notatnik")
    except Exception:
        pass

    root = None
    if DND_AVAILABLE:
        try:
            root = TkinterDnD.Tk()
        except Exception:
            root = None
    if root is None:
        root = tk.Tk()
    try:
        root.iconbitmap(os.path.join(BASE_DIR, "assets", "ikona.ico"))
    except tk.TclError:
        pass
    style = ttk.Style(root)
    for theme in ("vista", "winnative", "clam"):
        if theme in style.theme_names():
            style.theme_use(theme)
            break

    initial_arg = sys.argv[1] if len(sys.argv) > 1 else None
    MrPromptNotatnik(root, initial_arg)
    root.mainloop()


if __name__ == "__main__":
    main()

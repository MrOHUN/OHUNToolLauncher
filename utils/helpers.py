import os
import json
import importlib.util

# Yo'llarni aniqlash
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
WIDGETS_DIR = os.path.join(BASE_DIR, "widgets")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
THEMES_DIR = os.path.join(BASE_DIR, "themes")
LANGS_DIR = os.path.join(BASE_DIR, "langs")

DEFAULT_SETTINGS = {
    "tools_dir": "",
    "cols": 2,
    "theme": "default",
    "lang": "uz",
    "active_widgets": [],  # bosh ekranda ko'rinadigan widget folder nomlari
}

# Til keshini saqlash uchun global o'zgaruvchi
_lang_cache = {}

def load_settings():
    """settings.json faylini yuklaydi yoki standart sozlamalarni qaytaradi."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    s.setdefault(k, v)
                return s
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s):
    """Berilgan sozlamalarni settings.json fayliga saqlaydi."""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def hex_rgb(h):
    """Hex formatidagi rangni (#ffffff) Kivy uchun RGB formatiga o'tkazadi."""
    h = h.lstrip("#")
    return (
        int(h[0:2], 16) / 255,
        int(h[2:4], 16) / 255,
        int(h[4:6], 16) / 255
    )

def load_theme():
    """Tanlangan temani (.py fayl) dinamik ravishda yuklaydi."""
    s = load_settings()
    theme_name = s.get("theme", "default")

    def _load(name):
        path = os.path.join(THEMES_DIR, name, f"{name}.py")
        if not os.path.exists(path):
            return None
        spec = importlib.util.spec_from_file_location(f"theme_{name}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    theme = _load(theme_name)
    if theme is None:
        theme = _load("default")
    return theme

def load_lang():
    """Tanlangan tilni (.json fayl) o'qiydi va keshga saqlaydi."""
    global _lang_cache
    s = load_settings()
    lang_name = s.get("lang", "uz")
    lang_file = os.path.join(LANGS_DIR, lang_name, f"{lang_name}.json")
    try:
        with open(lang_file, "r", encoding="utf-8") as f:
            _lang_cache = json.load(f)
    except Exception:
        fallback = os.path.join(LANGS_DIR, "uz", "uz.json")
        try:
            with open(fallback, "r", encoding="utf-8") as f:
                _lang_cache = json.load(f)
        except Exception:
            _lang_cache = {}

def t(key):
    """Berilgan kalit so'zga mos tarjimani qaytaradi."""
    global _lang_cache
    if not _lang_cache:
        load_lang()
    return _lang_cache.get(key, key)

def clear_cache():
    """
    Til keshini tozalaydi.
    Bu funksiya chaqirilgandan so'ng t() funksiyasi ishlatilsa,
    u yangilangan sozlamalar bo'yicha tillarni qaytadan yuklaydi.
    """
    global _lang_cache
    _lang_cache = {}

# ── Widget yordamchi funksiyalari ─────────────────────────────────────────────

def get_active_widgets():
    """Faol widget folder nomlarini qaytaradi."""
    s = load_settings()
    return s.get("active_widgets", [])

def add_active_widget(folder):
    """Widget ni faol ro'yxatga qo'shadi."""
    s = load_settings()
    active = s.get("active_widgets", [])
    if folder not in active:
        active.append(folder)
        s["active_widgets"] = active
        save_settings(s)

def remove_active_widget(folder):
    """Widget ni faol ro'yxatdan olib tashlaydi."""
    s = load_settings()
    active = s.get("active_widgets", [])
    if folder in active:
        active.remove(folder)
        s["active_widgets"] = active
        save_settings(s)

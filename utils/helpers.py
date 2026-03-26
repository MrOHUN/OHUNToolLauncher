import os
import json
import importlib.util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
THEMES_DIR = os.path.join(BASE_DIR, "themes")
LANGS_DIR = os.path.join(BASE_DIR, "langs")

DEFAULT_SETTINGS = {
    "tools_dir": "",
    "cols": 2,
    "theme": "default",
    "lang": "uz",
}

_lang_cache = {}

def load_settings():
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
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def hex_rgb(h):
    h = h.lstrip("#")
    return (
        int(h[0:2], 16) / 255,
        int(h[2:4], 16) / 255,
        int(h[4:6], 16) / 255
    )

def load_theme():
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
    global _lang_cache
    if not _lang_cache:
        load_lang()
    return _lang_cache.get(key, key)

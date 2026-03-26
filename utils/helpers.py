import os
import json
import importlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
THEMES_DIR = os.path.join(BASE_DIR, "themes")

DEFAULT_SETTINGS = {
    "tools_dir": "",
    "cols": 2,
    "theme": "default",
}

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
    try:
        # Dinamik ravishda modulni yuklash
        theme = importlib.import_module(f"themes.{theme_name}")
        return theme
    except Exception:
        # Agar xato bo'lsa, default mavzuni yuklash
        try:
            import themes.default as theme
            return theme
        except Exception:
            return None

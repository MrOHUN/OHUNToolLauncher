import os
import json
import threading
import requests

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from utils.widgets import RoundedButton
from utils.helpers import load_settings, save_settings, t as tr

THEMES_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/themes/themes_list.json"
THEME_BASE_URL  = "https://api.github.com/repos/MrOHUN/OHUNToolLauncher/contents/themes/{}"

THEMES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")


def open_theme_store(status_lbl):
    status_lbl.text = f"[color=888888]{tr('loading')}[/color]"
    threading.Thread(
        target=_fetch_themes_list,
        args=(status_lbl,),
        daemon=True
    ).start()


def _fetch_themes_list(status_lbl):
    try:
        r = requests.get(THEMES_LIST_URL, timeout=10)
        themes = r.json()
        Clock.schedule_once(lambda dt: _show_popup(themes, status_lbl))
    except Exception as e:
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {e}[/color]"
        ))


def _show_popup(themes, status_lbl):
    status_lbl.text = ""
    s = load_settings()
    current = s.get("theme", "default")

    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    # O'rnatilgan temalar — themes/ papkasidagi papkalar
    installed = [
        d for d in os.listdir(THEMES_DIR)
        if os.path.isdir(os.path.join(THEMES_DIR, d))
    ] if os.path.exists(THEMES_DIR) else []

    for theme in themes:
        row = BoxLayout(size_hint=(1, None), height=70, spacing=8)
        info = Label(
            text=f"[b]{theme['name']}[/b]\n[color=888888][size=12]{theme.get('description', '')}[/size][/color]",
            markup=True, font_size=14,
            halign="left", valign="middle", size_hint=(1, 1)
        )
        info.bind(size=info.setter("text_size"))

        folder = theme.get("folder", "")

        if folder == current:
            btn = RoundedButton(
                bg_color=(0.1, 0.45, 0.25, 1),
                text=tr("active"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
        elif folder in installed:
            btn = RoundedButton(
                bg_color=(0.15, 0.35, 0.55, 1),
                text=tr("select"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, t=theme: _apply_theme(t, status_lbl, popup))
        else:
            btn = RoundedButton(
                bg_color=(0.2, 0.2, 0.2, 1),
                text=tr("install"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, t=theme: _download_theme(t, status_lbl, popup))

        row.add_widget(info)
        row.add_widget(btn)
        box.add_widget(row)

    scroll.add_widget(box)
    content.add_widget(scroll)

    popup = Popup(
        title=tr("themes"),
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()


def _apply_theme(theme, status_lbl, popup):
    popup.dismiss()
    s = load_settings()
    s["theme"] = theme["folder"]
    save_settings(s)
    status_lbl.text = f"[color=33ff88]{theme['name']} {tr('theme_applied')}[/color]"


def _download_theme(theme, status_lbl, popup):
    popup.dismiss()
    status_lbl.text = f"[color=888888]{theme['name']} {tr('downloading')}[/color]"
    threading.Thread(
        target=_fetch_theme_files,
        args=(theme, status_lbl),
        daemon=True
    ).start()


def _fetch_theme_files(theme, status_lbl):
    try:
        folder = theme["folder"]
        r = requests.get(THEME_BASE_URL.format(folder), timeout=10)
        files = r.json()
        theme_dir = os.path.join(THEMES_DIR, folder)
        os.makedirs(theme_dir, exist_ok=True)

        for f in files:
            if f["type"] == "file":
                file_r = requests.get(f["download_url"], timeout=10)
                with open(os.path.join(theme_dir, f["name"]), "w", encoding="utf-8") as fp:
                    fp.write(file_r.text)

        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text',
            f"[color=33ff88]{theme['name']} {tr('install_done')}[/color]"
        ))
    except Exception as e:
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {e}[/color]"
        ))
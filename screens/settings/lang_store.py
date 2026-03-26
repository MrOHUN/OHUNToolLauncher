import os
import threading
import requests

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from utils.widgets import RoundedButton
from utils.helpers import load_settings, save_settings, t as tr, load_lang, LANGS_DIR

LANGS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/langs/langs_list.json"
LANG_BASE_URL  = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/langs/{}"


def open_lang_store(status_lbl):
    status_lbl.text = f"[color=888888]{tr('loading')}[/color]"
    threading.Thread(
        target=_fetch_langs_list,
        args=(status_lbl,),
        daemon=True
    ).start()


def _fetch_langs_list(status_lbl):
    try:
        r = requests.get(LANGS_LIST_URL, timeout=10)
        langs = r.json()
        Clock.schedule_once(lambda dt: _show_popup(langs, status_lbl))
    except Exception as e:
        err = str(e)
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {err}[/color]"
        ))


def _show_popup(langs, status_lbl):
    status_lbl.text = ""
    s = load_settings()
    current = s.get("lang", "uz")

    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    # O'rnatilgan tillar — papkalarni qidiradi
    installed = [
        d for d in os.listdir(LANGS_DIR)
        if os.path.isdir(os.path.join(LANGS_DIR, d))
    ] if os.path.exists(LANGS_DIR) else []

    for lang in langs:
        row = BoxLayout(size_hint=(1, None), height=70, spacing=8)
        info = Label(
            text=f"[b]{lang['name']}[/b]\n[color=888888][size=12]{lang.get('description', '')}[/size][/color]",
            markup=True, font_size=14,
            halign="left", valign="middle", size_hint=(1, 1)
        )
        info.bind(size=info.setter("text_size"))

        code = lang.get("code", "")

        if code == current:
            btn = RoundedButton(
                bg_color=(0.1, 0.45, 0.25, 1),
                text=tr("active"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
        elif code in installed:
            btn = RoundedButton(
                bg_color=(0.15, 0.35, 0.55, 1),
                text=tr("select"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, l=lang: _apply_lang(l, status_lbl, popup))
        else:
            btn = RoundedButton(
                bg_color=(0.2, 0.2, 0.2, 1),
                text=tr("install"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, l=lang: _download_lang(l, status_lbl, popup))

        row.add_widget(info)
        row.add_widget(btn)
        box.add_widget(row)

    scroll.add_widget(box)
    content.add_widget(scroll)

    popup = Popup(
        title=tr("languages") if tr("languages") else "Languages",
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()


def _apply_lang(lang, status_lbl, popup):
    popup.dismiss()
    s = load_settings()
    s["lang"] = lang["code"]
    save_settings(s)
    load_lang()
    status_lbl.text = f"[color=33ff88]{lang['name']} {tr('lang_applied')}[/color]"


def _download_lang(lang, status_lbl, popup):
    popup.dismiss()
    status_lbl.text = f"[color=888888]{lang['name']} {tr('downloading')}[/color]"
    threading.Thread(
        target=_fetch_lang_file,
        args=(lang, status_lbl),
        daemon=True
    ).start()


def _fetch_lang_file(lang, status_lbl):
    try:
        filename = lang["file"]
        r = requests.get(LANG_BASE_URL.format(filename), timeout=10)

        filepath = os.path.join(LANGS_DIR, filename)
        folder = os.path.dirname(filepath)
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(r.text)

        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text',
            f"[color=33ff88]{lang['name']} {tr('install_done')}[/color]"
        ))
    except Exception as e:
        err = str(e)
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {err}[/color]"
        ))

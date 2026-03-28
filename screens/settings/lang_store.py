import os
import json
import threading
import shutil
import requests

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from utils.widgets import RoundedButton
from utils.helpers import load_settings, save_settings, t as tr, load_lang, LANGS_DIR

LANGS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/langs/langs_list.json"
LANG_BASE_URL  = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/langs/{}"


# ── Meta helpers ──────────────────────────────────────────────
def _load_meta(folder_path):
    try:
        with open(os.path.join(folder_path, "meta.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_meta(folder_path, data):
    meta_path = os.path.join(folder_path, "meta.json")
    try:
        existing = _load_meta(folder_path)
        existing.update(data)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def _ver_gt(a, b):
    try:
        return tuple(int(x) for x in str(a).split(".")) > tuple(int(x) for x in str(b).split("."))
    except Exception:
        return False
# ─────────────────────────────────────────────────────────────


def open_lang_store(status_lbl):
    status_lbl.text = f"[color=888888]{tr('loading')}[/color]"
    threading.Thread(target=_fetch_langs_list, args=(status_lbl,), daemon=True).start()


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
    search = TextInput(
        hint_text=tr("search"), multiline=False,
        size_hint=(1, None), height=38,
        background_color=(0.15, 0.15, 0.18, 1),
        foreground_color=(1, 1, 1, 1),
        cursor_color=(0.2, 0.8, 0.5, 1),
        font_size=14, padding=[8, 8]
    )
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    content.add_widget(search)
    content.add_widget(scroll)
    scroll.add_widget(box)

    popup = Popup(
        title=tr("languages") or "Languages",
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()

    def build_list(query=""):
        box.clear_widgets()
        installed = [
            d for d in os.listdir(LANGS_DIR)
            if os.path.isdir(os.path.join(LANGS_DIR, d))
        ] if os.path.exists(LANGS_DIR) else []
        q = query.lower().strip()

        for lang in langs:
            if q and q not in lang.get("name", "").lower() and q not in lang.get("code", "").lower():
                continue

            code = lang.get("code", "")
            lang_dir = os.path.join(LANGS_DIR, code)
            is_installed = os.path.isdir(lang_dir)

            row = BoxLayout(size_hint=(1, None), height=52, spacing=6)

            i_btn = RoundedButton(
                text="i", bg_color=(0.2, 0.3, 0.4, 1), font_size=13,
                size_hint=(None, None), width=36, height=36, color=(0.6, 0.9, 1, 1)
            )
            desc = lang.get("description", tr("no_description"))
            i_btn.bind(on_press=lambda x, d=desc, n=lang.get("name", ""): _show_desc(n, d))

            info = Label(
                text=f"[b]{lang['name']}[/b]",
                markup=True, font_size=14,
                halign="left", valign="middle", size_hint=(1, 1)
            )
            info.bind(size=info.setter("text_size"))

            row.add_widget(i_btn)
            row.add_widget(info)

            if code == current:
                row.add_widget(RoundedButton(
                    bg_color=(0.1, 0.45, 0.25, 1), text=tr("active"), font_size=12,
                    size_hint=(None, None), width=90, height=36, color=(1, 1, 1, 1)
                ))
            elif is_installed:
                list_ver = lang.get("version", "0")
                installed_ver = _load_meta(lang_dir).get("version", "0")

                if _ver_gt(list_ver, installed_ver):
                    btn = RoundedButton(
                        bg_color=(0.5, 0.35, 0.0, 1), text=tr("update"), font_size=12,
                        size_hint=(None, None), width=90, height=36, color=(1, 0.85, 0.2, 1)
                    )
                    btn.bind(on_press=lambda x, l=lang: _download_lang(l, status_lbl, popup))
                else:
                    btn = RoundedButton(
                        bg_color=(0.15, 0.35, 0.55, 1), text=tr("select"), font_size=12,
                        size_hint=(None, None), width=90, height=36, color=(1, 1, 1, 1)
                    )
                    btn.bind(on_press=lambda x, l=lang: _apply_lang(l, status_lbl, popup))

                del_btn = RoundedButton(
                    bg_color=(0.4, 0.1, 0.1, 1), text=tr("delete"), font_size=12,
                    size_hint=(None, None), width=70, height=36, color=(1, 0.5, 0.5, 1)
                )
                del_btn.bind(on_press=lambda x, c=code, n=lang.get("name", ""): _confirm_delete(c, n, status_lbl, popup))

                row.add_widget(btn)
                row.add_widget(del_btn)
            else:
                btn = RoundedButton(
                    bg_color=(0.2, 0.2, 0.2, 1), text=tr("install"), font_size=12,
                    size_hint=(None, None), width=90, height=36, color=(1, 1, 1, 1)
                )
                btn.bind(on_press=lambda x, l=lang: _download_lang(l, status_lbl, popup))
                row.add_widget(btn)

            box.add_widget(row)

    search.bind(text=lambda inst, val: build_list(val))
    build_list()


def _show_desc(name, desc):
    lbl = Label(text=f"[b]{name}[/b]\n\n{desc}", markup=True, font_size=14,
                halign="center", valign="top", size_hint=(1, 1))
    lbl.bind(size=lbl.setter("text_size"))
    Popup(title="Info", content=lbl, size_hint=(0.8, 0.4),
          background_color=(0.1, 0.1, 0.12, 1), separator_height=1).open()


def _confirm_delete(code, name, status_lbl, store_popup):
    box = BoxLayout(orientation="vertical", spacing=10, padding=10)
    lbl = Label(text=f"[b]{name}[/b] o'chirilsinmi?", markup=True, font_size=14,
                halign="center", valign="middle")
    lbl.bind(size=lbl.setter("text_size"))
    btns = BoxLayout(size_hint=(1, None), height=44, spacing=8)
    yes = RoundedButton(text=tr("yes"), bg_color=(0.5, 0.1, 0.1, 1), color=(1,1,1,1), font_size=14)
    no  = RoundedButton(text=tr("no"),  bg_color=(0.2, 0.2, 0.2, 1), color=(1,1,1,1), font_size=14)
    btns.add_widget(yes)
    btns.add_widget(no)
    box.add_widget(lbl)
    box.add_widget(btns)
    confirm = Popup(title=tr("delete"), content=box, size_hint=(0.8, 0.35),
                    background_color=(0.1, 0.1, 0.12, 1), separator_height=1)
    confirm.open()

    def do_delete(x):
        confirm.dismiss()
        store_popup.dismiss()
        try:
            shutil.rmtree(os.path.join(LANGS_DIR, code))
            status_lbl.text = f"[color=ff4444]{name} {tr('deleted')}[/color]"
        except Exception as e:
            err = str(e)
            status_lbl.text = f"[color=ff4444]Xato: {err}[/color]"

    yes.bind(on_press=do_delete)
    no.bind(on_press=lambda x: confirm.dismiss())


# ── Yangilangan _apply_lang funksiyasi ────────────────────────
def _apply_lang(lang, status_lbl, popup):
    popup.dismiss()
    # 1. Sozlamalarni yangilaymiz
    s = load_settings()
    s["lang"] = lang["code"]
    save_settings(s)
    
    # 2. Asosiy App klassidan restart_ui ni chaqiramiz
    from kivy.app import App
    App.get_running_app().restart_ui()
# ─────────────────────────────────────────────────────────────


def _download_lang(lang, status_lbl, popup):
    popup.dismiss()
    status_lbl.text = f"[color=888888]{lang['name']} {tr('downloading')}[/color]"
    threading.Thread(target=_fetch_lang_file, args=(lang, status_lbl), daemon=True).start()


def _fetch_lang_file(lang, status_lbl):
    try:
        filename = lang["file"]
        r = requests.get(LANG_BASE_URL.format(filename), timeout=10)

        filepath = os.path.join(LANGS_DIR, filename)
        folder = os.path.dirname(filepath)
        os.makedirs(folder, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(r.text)

        _save_meta(folder, {
            "name": lang.get("name", ""),
            "code": lang.get("code", ""),
            "author": lang.get("author", ""),
            "version": lang.get("version", "0")
        })

        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text',
            f"[color=33ff88]{lang['name']} {tr('install_done')}[/color]"
        ))
    except Exception as e:
        err = str(e)
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {err}[/color]"
        ))

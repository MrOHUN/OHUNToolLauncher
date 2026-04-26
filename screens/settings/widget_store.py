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
from utils.helpers import (
    WIDGETS_DIR, t as tr,
    get_active_widgets, add_active_widget, remove_active_widget
)

WIDGETS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/widgets/widgets_list.json"
WIDGET_BASE_URL  = "https://api.github.com/repos/MrOHUN/OHUNToolLauncher/contents/widgets/{}"


def open_widget_store(status_lbl):
    status_lbl.text = f"[color=888888]{tr('loading')}[/color]"
    threading.Thread(
        target=_fetch_widgets_list,
        args=(status_lbl,),
        daemon=True
    ).start()


def _fetch_widgets_list(status_lbl):
    try:
        r = requests.get(WIDGETS_LIST_URL, timeout=10)
        widgets = r.json()
        Clock.schedule_once(lambda dt: _show_popup(widgets, status_lbl))
    except Exception as e:
        err = str(e)
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {err}[/color]"
        ))


def _show_popup(widgets, status_lbl):
    status_lbl.text = ""

    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])

    search = TextInput(
        hint_text=tr("search"),
        multiline=False,
        size_hint=(1, None), height=38,
        background_color=(0.15, 0.15, 0.18, 1),
        foreground_color=(1, 1, 1, 1),
        cursor_color=(0.2, 0.8, 0.5, 1),
        font_size=14,
        padding=[8, 8]
    )

    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    content.add_widget(search)
    content.add_widget(scroll)
    scroll.add_widget(box)

    popup = Popup(
        title="Widgets",
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()

    def build_list(query=""):
        box.clear_widgets()
        q = query.lower().strip()
        active = get_active_widgets()

        for widget in widgets:
            name   = widget.get("name", "Widget")
            folder = widget.get("folder", "")
            size   = widget.get("size", "small")

            if q and q not in name.lower() and q not in folder.lower():
                continue

            is_installed = os.path.isdir(os.path.join(WIDGETS_DIR, folder))
            is_active    = folder in active

            row = BoxLayout(size_hint=(1, None), height=56, spacing=6)

            # [i] tugmasi
            i_btn = RoundedButton(
                text="i",
                bg_color=(0.2, 0.3, 0.4, 1),
                font_size=13,
                size_hint=(None, None), width=36, height=36,
                color=(0.6, 0.9, 1, 1)
            )
            desc = widget.get("description", tr("no_description"))
            i_btn.bind(on_press=lambda x, d=desc, n=name: _show_desc(n, d, size))

            # Nom + size badge
            size_color = {
                "small":  (0.4, 0.8, 0.4, 1),
                "medium": (0.4, 0.6, 1.0, 1),
                "large":  (1.0, 0.6, 0.2, 1),
            }.get(size, (0.6, 0.6, 0.6, 1))

            info = Label(
                text=f"[b]{name}[/b]  [color={_rgba_hex(size_color)}][{size}][/color]",
                markup=True, font_size=14,
                halign="left", valign="middle", size_hint=(1, 1)
            )
            info.bind(size=info.setter("text_size"))

            row.add_widget(i_btn)
            row.add_widget(info)

            if is_installed:
                # Versiya tekshirish
                list_ver = widget.get("version", "0")
                meta_path = os.path.join(WIDGETS_DIR, folder, "meta.json")
                try:
                    with open(meta_path, encoding="utf-8") as mf:
                        installed_ver = json.load(mf).get("version", "0")
                except Exception:
                    installed_ver = "0"

                has_update = _ver_gt(list_ver, installed_ver)

                if has_update:
                    upd_btn = RoundedButton(
                        bg_color=(0.5, 0.35, 0.0, 1),
                        text=tr("update"), font_size=12,
                        size_hint=(None, None), width=80, height=36,
                        color=(1, 0.85, 0.2, 1)
                    )
                    upd_btn.bind(on_press=lambda x, w=widget: _download_widget(w, status_lbl, popup))
                    row.add_widget(upd_btn)
                else:
                    # O'chirish tugmasi
                    del_btn = RoundedButton(
                        bg_color=(0.4, 0.1, 0.1, 1),
                        text=tr("delete"), font_size=12,
                        size_hint=(None, None), width=80, height=36,
                        color=(1, 0.5, 0.5, 1)
                    )
                    del_btn.bind(on_press=lambda x, f=folder, n=name: _confirm_delete(f, n, status_lbl, popup, widgets))
                    row.add_widget(del_btn)

                # + / - tugmasi
                if is_active:
                    toggle_btn = RoundedButton(
                        bg_color=(0.35, 0.1, 0.1, 1),
                        text="－", font_size=16,
                        size_hint=(None, None), width=44, height=36,
                        color=(1, 0.5, 0.5, 1)
                    )
                    toggle_btn.bind(on_press=lambda x, f=folder: (
                        remove_active_widget(f),
                        build_list(query)
                    ))
                else:
                    toggle_btn = RoundedButton(
                        bg_color=(0.1, 0.35, 0.15, 1),
                        text="＋", font_size=16,
                        size_hint=(None, None), width=44, height=36,
                        color=(0.5, 1, 0.6, 1)
                    )
                    toggle_btn.bind(on_press=lambda x, f=folder: (
                        add_active_widget(f),
                        build_list(query)
                    ))
                row.add_widget(toggle_btn)

            else:
                # O'rnatilmagan — faqat yuklab olish
                inst_btn = RoundedButton(
                    bg_color=(0.1, 0.45, 0.25, 1),
                    text=tr("install"), font_size=12,
                    size_hint=(None, None), width=80, height=36,
                    color=(1, 1, 1, 1)
                )
                inst_btn.bind(on_press=lambda x, w=widget: _download_widget(w, status_lbl, popup))
                row.add_widget(inst_btn)

            box.add_widget(row)

    search.bind(text=lambda inst, val: build_list(val))
    build_list()


def _ver_gt(a, b):
    try:
        return tuple(int(x) for x in str(a).split(".")) > tuple(int(x) for x in str(b).split("."))
    except Exception:
        return False


def _rgba_hex(rgba):
    r, g, b, _ = rgba
    return "{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))


def _show_desc(name, desc, size):
    lbl = Label(
        text=f"[b]{name}[/b]\n\nO'lcham: {size}\n\n{desc}",
        markup=True, font_size=14,
        halign="center", valign="top",
        size_hint=(1, 1)
    )
    lbl.bind(size=lbl.setter("text_size"))
    p = Popup(
        title="Info", content=lbl,
        size_hint=(0.8, 0.42),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    p.open()


def _confirm_delete(folder, name, status_lbl, store_popup, widgets):
    box = BoxLayout(orientation="vertical", spacing=10, padding=10)
    lbl = Label(
        text=f"[b]{name}[/b] o'chirilsinmi?",
        markup=True, font_size=14,
        halign="center", valign="middle"
    )
    lbl.bind(size=lbl.setter("text_size"))

    btns = BoxLayout(size_hint=(1, None), height=44, spacing=8)
    yes = RoundedButton(text=tr("yes"), bg_color=(0.5, 0.1, 0.1, 1), color=(1,1,1,1), font_size=14)
    no  = RoundedButton(text=tr("no"),  bg_color=(0.2, 0.2, 0.2, 1), color=(1,1,1,1), font_size=14)
    btns.add_widget(yes)
    btns.add_widget(no)
    box.add_widget(lbl)
    box.add_widget(btns)

    confirm = Popup(
        title=tr("delete"), content=box,
        size_hint=(0.8, 0.35),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    confirm.open()

    def do_delete(x):
        confirm.dismiss()
        store_popup.dismiss()
        remove_active_widget(folder)
        widget_path = os.path.join(WIDGETS_DIR, folder)
        try:
            shutil.rmtree(widget_path)
            status_lbl.text = f"[color=ff4444]{name} {tr('deleted')}[/color]"
        except Exception as e:
            status_lbl.text = f"[color=ff4444]Xato: {str(e)}[/color]"

    yes.bind(on_press=do_delete)
    no.bind(on_press=lambda x: confirm.dismiss())


def _download_widget(widget, status_lbl, popup):
    popup.dismiss()
    status_lbl.text = f"[color=888888]{widget['name']} {tr('downloading')}[/color]"
    threading.Thread(
        target=_fetch_widget_files,
        args=(widget, status_lbl),
        daemon=True
    ).start()


def _fetch_widget_files(widget, status_lbl):
    try:
        folder = widget["folder"]
        r = requests.get(WIDGET_BASE_URL.format(folder), timeout=10)
        files = r.json()
        widget_dir = os.path.join(WIDGETS_DIR, folder)
        os.makedirs(widget_dir, exist_ok=True)

        for f in files:
            if f["type"] == "file":
                file_r = requests.get(f["download_url"], timeout=10)
                with open(os.path.join(widget_dir, f["name"]), "w", encoding="utf-8") as fp:
                    fp.write(file_r.text)

        # meta.json yangilash
        meta_path = os.path.join(widget_dir, "meta.json")
        try:
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as mf:
                    meta = json.load(mf)
                meta["version"]     = widget.get("version", "0")
                meta["description"] = widget.get("description", meta.get("description", ""))
                meta["author"]      = widget.get("author", meta.get("author", ""))
                with open(meta_path, "w", encoding="utf-8") as mf:
                    json.dump(meta, mf, ensure_ascii=False, indent=4)
        except Exception:
            pass

        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text',
            f"[color=33ff88]{widget['name']} {tr('install_done')}[/color]"
        ))
    except Exception as e:
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {str(e)}[/color]"
        ))

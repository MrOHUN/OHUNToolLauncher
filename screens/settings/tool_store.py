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
from utils.helpers import TOOLS_DIR, t as tr

TOOLS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/tools/tools_list.json"
TOOL_BASE_URL  = "https://api.github.com/repos/MrOHUN/OHUNToolLauncher/contents/tools/{}"


def open_tool_store(status_lbl):
    status_lbl.text = f"[color=888888]{tr('loading')}[/color]"
    threading.Thread(
        target=_fetch_tools_list,
        args=(status_lbl,),
        daemon=True
    ).start()


def _fetch_tools_list(status_lbl):
    try:
        r = requests.get(TOOLS_LIST_URL, timeout=10)
        tools = r.json()
        Clock.schedule_once(lambda dt: _show_popup(tools, status_lbl))
    except Exception as e:
        err = str(e)
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {err}[/color]"
        ))


def _show_popup(tools, status_lbl):
    status_lbl.text = ""

    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])

    # --- Search ---
    search = TextInput(
        hint_text=tr("search"),
        multiline=False,
        size_hint=(1, None),
        height=38,
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
        title=tr("tools"),
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()

    def build_list(query=""):
        box.clear_widgets()
        installed = os.listdir(TOOLS_DIR) if os.path.exists(TOOLS_DIR) else []
        q = query.lower().strip()

        for tool in tools:
            if q and q not in tool.get("name", "").lower() and q not in tool.get("folder", "").lower():
                continue

            folder = tool.get("folder", "")
            is_installed = os.path.isdir(os.path.join(TOOLS_DIR, folder))

            row = BoxLayout(size_hint=(1, None), height=52, spacing=6)

            # i tugmasi
            i_btn = RoundedButton(
                text="i",
                bg_color=(0.2, 0.3, 0.4, 1),
                font_size=13,
                size_hint=(None, None), width=36, height=36,
                color=(0.6, 0.9, 1, 1)
            )
            desc = tool.get("description", tr("no_description"))
            i_btn.bind(on_press=lambda x, d=desc, n=tool.get("name", ""): _show_desc(n, d))

            # Nom
            info = Label(
                text=f"[b]{tool['name']}[/b]",
                markup=True, font_size=14,
                halign="left", valign="middle", size_hint=(1, 1)
            )
            info.bind(size=info.setter("text_size"))

            # Tugma
            if is_installed:
                # Version solishtirish
                list_ver = tool.get("version", "0")
                meta_path = os.path.join(TOOLS_DIR, folder, "meta.json")
                try:
                    with open(meta_path, encoding="utf-8") as mf:
                        installed_ver = json.load(mf).get("version", "0")
                except Exception:
                    installed_ver = "0"

                has_update = _ver_gt(list_ver, installed_ver)

                if has_update:
                    action_btn = RoundedButton(
                        bg_color=(0.5, 0.35, 0.0, 1),
                        text=tr("update"), font_size=12,
                        size_hint=(None, None), width=90, height=36,
                        color=(1, 0.85, 0.2, 1)
                    )
                    action_btn.bind(on_press=lambda x, t=tool: _download_tool(t, status_lbl, popup))
                else:
                    action_btn = RoundedButton(
                        bg_color=(0.4, 0.1, 0.1, 1),
                        text=tr("delete"), font_size=12,
                        size_hint=(None, None), width=90, height=36,
                        color=(1, 0.5, 0.5, 1)
                    )
                    action_btn.bind(on_press=lambda x, f=folder, n=tool.get("name", ""): _confirm_delete(f, n, status_lbl, popup, tools))

                row.add_widget(i_btn)
                row.add_widget(info)
                row.add_widget(action_btn)
            else:
                install_btn = RoundedButton(
                    bg_color=(0.1, 0.45, 0.25, 1),
                    text=tr("install"), font_size=12,
                    size_hint=(None, None), width=90, height=36,
                    color=(1, 1, 1, 1)
                )
                install_btn.bind(on_press=lambda x, t=tool: _download_tool(t, status_lbl, popup))
                row.add_widget(i_btn)
                row.add_widget(info)
                row.add_widget(install_btn)

            box.add_widget(row)

    search.bind(text=lambda inst, val: build_list(val))
    build_list()


def _ver_gt(a, b):
    try:
        return tuple(int(x) for x in str(a).split(".")) > tuple(int(x) for x in str(b).split("."))
    except Exception:
        return False


def _show_desc(name, desc):
    lbl = Label(
        text=f"[b]{name}[/b]\n\n{desc}",
        markup=True, font_size=14,
        halign="center", valign="top",
        size_hint=(1, 1)
    )
    lbl.bind(size=lbl.setter("text_size"))
    p = Popup(
        title="Info",
        content=lbl,
        size_hint=(0.8, 0.4),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    p.open()


def _confirm_delete(folder, name, status_lbl, store_popup, tools):
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
        title=tr("delete"),
        content=box,
        size_hint=(0.8, 0.35),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    confirm.open()

    def do_delete(x):
        confirm.dismiss()
        store_popup.dismiss()
        tool_path = os.path.join(TOOLS_DIR, folder)
        try:
            shutil.rmtree(tool_path)
            status_lbl.text = f"[color=ff4444]{name} {tr('deleted')}[/color]"
        except Exception as e:
            err = str(e)
            status_lbl.text = f"[color=ff4444]Xato: {err}[/color]"

    yes.bind(on_press=do_delete)
    no.bind(on_press=lambda x: confirm.dismiss())


def _download_tool(tool, status_lbl, popup):
    popup.dismiss()
    status_lbl.text = f"[color=888888]{tool['name']} {tr('downloading')}[/color]"
    threading.Thread(
        target=_fetch_tool_files,
        args=(tool, status_lbl),
        daemon=True
    ).start()


def _fetch_tool_files(tool, status_lbl):
    try:
        folder = tool["folder"]
        r = requests.get(TOOL_BASE_URL.format(folder), timeout=10)
        files = r.json()
        tool_dir = os.path.join(TOOLS_DIR, folder)
        os.makedirs(tool_dir, exist_ok=True)

        for f in files:
            if f["type"] == "file":
                file_r = requests.get(f["download_url"], timeout=10)
                with open(os.path.join(tool_dir, f["name"]), "w", encoding="utf-8") as fp:
                    fp.write(file_r.text)

        # meta.json yangilash bloki
        meta_path = os.path.join(tool_dir, "meta.json")
        try:
            if os.path.exists(meta_path):
                with open(meta_path, encoding="utf-8") as mf:
                    meta = json.load(mf)
                
                # Yangi ma'lumotlarni yozish
                meta["version"]     = tool.get("version", "0")
                meta["description"] = tool.get("description", meta.get("description", ""))
                meta["author"]      = tool.get("author", meta.get("author", ""))
                
                with open(meta_path, "w", encoding="utf-8") as mf:
                    json.dump(meta, mf, ensure_ascii=False, indent=4)
        except Exception:
            pass

        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text',
            f"[color=33ff88]{tool['name']} {tr('install_done')}[/color]"
        ))
    except Exception as e:
        err = str(e)
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {err}[/color]"
        ))

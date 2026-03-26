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

from utils.widgets import RoundedButton
# Importga t as tr qo'shildi
from utils.helpers import TOOLS_DIR, t as tr

TOOLS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/tools/tools_list.json"
TOOL_BASE_URL  = "https://api.github.com/repos/MrOHUN/OHUNToolLauncher/contents/tools/{}"


def open_tool_store(status_lbl):
    # 1 — yuklanmoqda tarjimasi
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
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {e}[/color]"
        ))


def _show_popup(tools, status_lbl):
    status_lbl.text = ""
    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    installed = os.listdir(TOOLS_DIR) if os.path.exists(TOOLS_DIR) else []

    for tool in tools:
        row = BoxLayout(size_hint=(1, None), height=70, spacing=8)
        info = Label(
            text=f"[b]{tool['name']}[/b]\n[color=888888][size=12]{tool.get('description', '')}[/size][/color]",
            markup=True, font_size=14,
            halign="left", valign="middle", size_hint=(1, 1)
        )
        info.bind(size=info.setter("text_size"))

        folder = tool.get("folder", "")
        if folder in installed:
            # 2 — o'rnatilgan tugmasi tarjimasi
            btn = RoundedButton(
                bg_color=(0.2, 0.2, 0.2, 1),
                text=tr("installed"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(0.5, 0.5, 0.5, 1)
            )
        else:
            # 3 — o'rnatish tugmasi tarjimasi
            btn = RoundedButton(
                bg_color=(0.1, 0.45, 0.25, 1),
                text=tr("install"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, t=tool: _download_tool(t, status_lbl, popup))

        row.add_widget(info)
        row.add_widget(btn)
        box.add_widget(row)

    scroll.add_widget(box)
    content.add_widget(scroll)

    # 4 — popup title tarjimasi
    popup = Popup(
        title=tr("tools"),
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()


def _download_tool(tool, status_lbl, popup):
    popup.dismiss()
    # 5 — yuklanmoqda (download) tarjimasi
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
                # UTF-8 bilan saqlash
                with open(os.path.join(tool_dir, f["name"]), "w", encoding="utf-8") as fp:
                    fp.write(file_r.text)

        # 6 — o'rnatildi tarjimasi
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text',
            f"[color=33ff88]{tool['name']} {tr('install_done')}[/color]"
        ))
    except Exception as e:
        Clock.schedule_once(lambda dt: setattr(
            status_lbl, 'text', f"[color=ff4444]Xato: {e}[/color]"
        ))

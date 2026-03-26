import os
import json
import threading
import shutil

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

from utils.widgets import RoundedButton, NavBar
from utils.helpers import TOOLS_DIR

TOOLS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/tools/tools_list.json"
TOOL_BASE_URL = "https://api.github.com/repos/MrOHUN/OHUNToolLauncher/contents/tools/{}"


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")

        # HEADER
        header = BoxLayout(size_hint=(1, None), height=56, padding=[20, 8])
        with header.canvas.before:
            Color(0.15, 0.15, 0.17, 1)
            self._hrect = RoundedRectangle(size=header.size, pos=header.pos)
        header.bind(
            size=lambda w, v: setattr(self._hrect, 'size', v),
            pos=lambda w, v: setattr(self._hrect, 'pos', v)
        )
        title = Label(
            text="[S] Settings", font_size=20, bold=True,
            color=(1, 1, 1, 1), halign="left", valign="middle",
            size_hint=(1, 1)
        )
        title.bind(size=title.setter("text_size"))
        header.add_widget(title)

        # CONTENT
        content = BoxLayout(
            orientation="vertical", size_hint=(1, None),
            height=120, padding=[18, 16], spacing=16
        )

        self.status_lbl = Label(
            text="", font_size=13,
            color=(0.5, 0.8, 0.5, 1),
            size_hint=(1, None), height=30,
            halign="center", valign="middle",
            markup=True
        )
        self.status_lbl.bind(size=self.status_lbl.setter("text_size"))

        install_btn = RoundedButton(
            bg_color=(0.1, 0.45, 0.25, 1),
            text="GitHub dan tool yukla",
            font_size=16, size_hint=(1, None), height=56,
            color=(1, 1, 1, 1)
        )
        install_btn.bind(on_press=self._install_tool)

        content.add_widget(install_btn)
        content.add_widget(self.status_lbl)

        # NAVBAR
        navbar = NavBar(
            active="settings",
            on_home=self._go_home,
            on_tools=self._go_tools,
            on_settings=None
        )

        root.add_widget(header)
        root.add_widget(content)
        root.add_widget(navbar)
        self.add_widget(root)

    def _install_tool(self, *args):
        self.status_lbl.text = "[color=888888]Yuklanmoqda...[/color]"
        threading.Thread(target=self._fetch_tools_list, daemon=True).start()

    def _fetch_tools_list(self):
        try:
            import requests
            r = requests.get(TOOLS_LIST_URL, timeout=10)
            tools = r.json()
            Clock.schedule_once(lambda dt: self._show_tools_popup(tools))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(
                self.status_lbl, 'text', f"[color=ff4444]Xato: {e}[/color]"
            ))

    def _show_tools_popup(self, tools):
        self.status_lbl.text = ""

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
                halign="left", valign="middle",
                size_hint=(1, 1)
            )
            info.bind(size=info.setter("text_size"))

            folder = tool.get("folder", "")
            if folder in installed:
                btn = RoundedButton(
                    bg_color=(0.2, 0.2, 0.2, 1),
                    text="O'rnatilgan", font_size=12,
                    size_hint=(None, None), width=110, height=44,
                    color=(0.5, 0.5, 0.5, 1)
                )
            else:
                btn = RoundedButton(
                    bg_color=(0.1, 0.45, 0.25, 1),
                    text="O'rnatish", font_size=12,
                    size_hint=(None, None), width=110, height=44,
                    color=(1, 1, 1, 1)
                )
                btn.bind(on_press=lambda x, t=tool: self._download_tool(t))

            row.add_widget(info)
            row.add_widget(btn)
            box.add_widget(row)

        scroll.add_widget(box)
        content.add_widget(scroll)

        self._popup = Popup(
            title="Toollar",
            content=content,
            size_hint=(0.95, 0.85),
            background_color=(0.1, 0.1, 0.12, 1),
            separator_height=1
        )
        self._popup.open()

    def _download_tool(self, tool):
        self._popup.dismiss()
        self.status_lbl.text = f"[color=888888]{tool['name']} yuklanmoqda...[/color]"
        threading.Thread(target=self._fetch_tool_files, args=(tool,), daemon=True).start()

    def _fetch_tool_files(self, tool):
        try:
            import requests
            folder = tool["folder"]
            url = TOOL_BASE_URL.format(folder)
            r = requests.get(url, timeout=10)
            files = r.json()

            tool_dir = os.path.join(TOOLS_DIR, folder)
            os.makedirs(tool_dir, exist_ok=True)

            for f in files:
                if f["type"] == "file":
                    file_r = requests.get(f["download_url"], timeout=10)
                    with open(os.path.join(tool_dir, f["name"]), "w", encoding="utf-8") as fp:
                        fp.write(file_r.text)

            Clock.schedule_once(lambda dt: setattr(
                self.status_lbl, 'text',
                f"[color=33ff88]{tool['name']} o'rnatildi![/color]"
            ))
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(
                self.status_lbl, 'text', f"[color=ff4444]Xato: {e}[/color]"
            ))

    def _go_home(self, *args):
        self.manager.current = "home"

    def _go_tools(self, *args):
        home = self.manager.get_screen("home")
        home._on_tools()
        self.manager.current = "home"
import os
import sys
import json
import threading
import importlib.util

import requests
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle

from utils.widgets import RoundedButton, NavBar
from utils.helpers import (
    load_settings, hex_rgb, TOOLS_DIR, WIDGETS_DIR,
    load_theme, t as tr,
    get_active_widgets
)

TOOLS_LIST_URL = "https://raw.githubusercontent.com/MrOHUN/OHUNToolLauncher/master/tools/tools_list.json"


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_tab = "home"
        self._build()

    def _build(self):
        t = load_theme()

        self._root = BoxLayout(orientation="vertical")

        # HEADER
        header = BoxLayout(size_hint=(1, None), height=56, padding=[20, 8])
        with header.canvas.before:
            Color(*t.HEADER_COLOR)
            self._hrect = RoundedRectangle(size=header.size, pos=header.pos)
        header.bind(
            size=lambda w, v: setattr(self._hrect, 'size', v),
            pos=lambda w, v: setattr(self._hrect, 'pos', v)
        )

        title = Label(
            text=f"[T] {tr('app_name')}", font_size=20, bold=True,
            color=t.TEXT_COLOR,
            halign="left", valign="middle",
            size_hint=(1, 1)
        )
        title.bind(size=title.setter("text_size"))
        header.add_widget(title)

        # CONTENT
        self.content = BoxLayout(
            orientation="vertical", size_hint=(1, 1), padding=[12, 10]
        )
        self._home_view()

        # NAVBAR
        self.navbar = NavBar(
            active="home",
            on_home=self._on_home,
            on_tools=self._on_tools,
            on_settings=self._on_settings
        )

        self._root.add_widget(header)
        self._root.add_widget(self.content)
        self._root.add_widget(self.navbar)
        self.add_widget(self._root)

    def _on_home(self, *args):
        self.navbar.set_active("home")
        self._home_view()

    def _on_tools(self, *args):
        self.navbar.set_active("tools")
        self._tools_view()

    def _on_settings(self, *args):
        self.manager.current = "settings"

    # ── HOME VIEW — widgetlar ─────────────────────────────────────
    def _home_view(self):
        self.content.clear_widgets()
        active = get_active_widgets()

        if not active:
            # Widget yo'q — xush kelibsiz matni
            t = load_theme()
            lbl = Label(
                text=tr("welcome_text"),
                font_size=17,
                color=t.SUBTEXT_COLOR,
                halign="center", valign="middle", size_hint=(1, 1)
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.content.add_widget(lbl)
            return

        # Widgetlar bor — scroll ichida render
        scroll = ScrollView(size_hint=(1, 1))
        box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            spacing=10,
            padding=[0, 4]
        )
        box.bind(minimum_height=box.setter("height"))
        scroll.add_widget(box)
        self.content.add_widget(scroll)

        # small widgetlar juft-juft (2 ta yonma-yon)
        small_row = None

        for folder in active:
            widget_obj = self._load_widget(folder)
            if widget_obj is None:
                continue

            size = self._get_widget_size(folder)

            if size == "small":
                if small_row is None:
                    small_row = BoxLayout(
                        orientation="horizontal",
                        size_hint=(1, None), height=70,
                        spacing=10
                    )
                    box.add_widget(small_row)
                small_row.add_widget(widget_obj)
                if len(small_row.children) >= 2:
                    small_row = None
            else:
                # medium / large — to'liq kenglik
                small_row = None
                box.add_widget(widget_obj)

    def _load_widget(self, folder):
        """Widget papkasidan get_widget() chaqiradi."""
        main_path = os.path.join(WIDGETS_DIR, folder, "main.py")
        if not os.path.exists(main_path):
            return None
        try:
            mod_name = f"widget_{folder}"
            sys.modules.pop(mod_name, None)
            spec = importlib.util.spec_from_file_location(mod_name, main_path)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "get_widget"):
                return mod.get_widget()
        except Exception as e:
            print(f"[widget xato] {folder}: {e}")
        return None

    def _get_widget_size(self, folder):
        """meta.json dan o'lchamni o'qiydi."""
        meta_path = os.path.join(WIDGETS_DIR, folder, "meta.json")
        try:
            with open(meta_path, encoding="utf-8") as f:
                return json.load(f).get("size", "small")
        except Exception:
            return "small"

    # ── TOOLS VIEW ────────────────────────────────────────────────
    def _tools_view(self):
        self.content.clear_widgets()
        s = load_settings()
        self._tools_dir = s.get("tools_dir", "").strip() or TOOLS_DIR
        cols = s.get("cols", 1)

        self._status_lbl = Label(
            text="", font_size=13, markup=True,
            size_hint=(1, None), height=24,
            halign="center", valign="middle"
        )
        self._status_lbl.bind(size=self._status_lbl.setter("text_size"))

        t = load_theme()
        search_bg     = getattr(t, 'INPUT_COLOR',  (0.13, 0.13, 0.16, 1))
        search_fg     = getattr(t, 'TEXT_COLOR',   (1, 1, 1, 1))
        search_cursor = getattr(t, 'ACCENT_COLOR', (0.2, 0.8, 0.5, 1))

        search = TextInput(
            hint_text=tr("search"),
            multiline=False,
            size_hint=(1, None), height=44,
            background_color=search_bg,
            foreground_color=search_fg,
            cursor_color=search_cursor,
            font_size=15,
            padding=[14, 10]
        )

        scroll = ScrollView(size_hint=(1, 1))
        self._grid = GridLayout(
            cols=cols, spacing=10, padding=[4, 6], size_hint_y=None
        )
        self._grid.bind(minimum_height=self._grid.setter("height"))
        scroll.add_widget(self._grid)

        self.content.add_widget(self._status_lbl)
        self.content.add_widget(search)
        self.content.add_widget(scroll)

        self._remote_tools = {}
        threading.Thread(target=self._fetch_remote_list, daemon=True).start()

        search.bind(text=lambda inst, val: self._build_grid(val))
        self._build_grid()

    def _fetch_remote_list(self):
        try:
            r = requests.get(TOOLS_LIST_URL, timeout=10)
            data = r.json()
            self._remote_tools = {item["folder"]: item for item in data}
        except Exception:
            self._remote_tools = {}
        Clock.schedule_once(lambda dt: self._build_grid())

    def _build_grid(self, query=""):
        self._grid.clear_widgets()
        tools = self._load_tools(self._tools_dir)
        q = query.lower().strip()

        if not tools:
            lbl = Label(
                text=tr("no_tools"),
                font_size=15, color=(0.5, 0.5, 0.5, 1),
                halign="center", valign="middle",
                size_hint=(1, None), height=100
            )
            lbl.bind(size=lbl.setter("text_size"))
            self._grid.add_widget(lbl)
            return

        for tool in tools:
            name   = tool.get("name", "Tool")
            folder = tool.get("_folder", "")
            if q and q not in name.lower() and q not in folder.lower():
                continue
            self._grid.add_widget(self._make_tool_card(tool))

    def _make_tool_card(self, tool):
        t         = load_theme()
        name      = tool.get("name", "Tool")
        icon      = tool.get("icon", "[T]")
        main_path = tool.get("_main", "")
        folder    = tool.get("_folder", "")

        btn_color = getattr(t, 'BUTTON_COLOR', (0.1, 0.45, 0.2, 1))

        local_ver  = tool.get("version", "0")
        remote     = self._remote_tools.get(folder, {})
        remote_ver = remote.get("version", "0")
        has_update = _ver_gt(remote_ver, local_ver)

        card = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None), height=56,
            spacing=8, padding=[0, 2]
        )

        desc = tool.get("description", tr("no_description"))

        i_btn = RoundedButton(
            text="i", bg_color=(0.18, 0.28, 0.38, 1),
            font_size=13, size_hint=(None, 1), width=40,
            color=(0.5, 0.85, 1, 1)
        )
        i_btn.bind(on_press=lambda x, d=desc, n=name: _show_desc(n, d))

        btn = RoundedButton(
            bg_color=btn_color,
            text=f"{icon} {name}", font_size=14,
            size_hint=(1, 1),
            halign="center", valign="middle",
            color=(1, 1, 1, 1)
        )
        btn.bind(on_press=lambda x: self._open_output(name, main_path, ""))

        if has_update:
            action_btn = RoundedButton(
                bg_color=(0.45, 0.3, 0.0, 1),
                text=tr("update"), font_size=12,
                size_hint=(None, 1), width=82,
                color=(1, 0.85, 0.2, 1)
            )
            action_btn.bind(on_press=lambda x, t=remote, f=folder: self._do_update(t, f))
        else:
            action_btn = RoundedButton(
                bg_color=(0.35, 0.08, 0.08, 1),
                text=tr("delete"), font_size=12,
                size_hint=(None, 1), width=82,
                color=(1, 0.45, 0.45, 1)
            )
            action_btn.bind(on_press=lambda x, f=folder, n=name: self._confirm_delete(f, n))

        card.add_widget(i_btn)
        card.add_widget(btn)
        card.add_widget(action_btn)
        return card

    def _do_update(self, remote_tool, folder):
        self._status_lbl.text = f"[color=888888]{remote_tool.get('name', '')} {tr('downloading')}[/color]"
        from screens.settings.tool_store import _fetch_tool_files
        threading.Thread(
            target=_fetch_tool_files,
            args=(remote_tool, self._status_lbl),
            daemon=True
        ).start()
        Clock.schedule_once(lambda dt: self._build_grid(), 3)

    def _confirm_delete(self, folder, name):
        import shutil
        box = BoxLayout(orientation="vertical", spacing=12, padding=14)
        lbl = Label(
            text=f"[b]{name}[/b] o'chirilsinmi?",
            markup=True, font_size=14,
            halign="center", valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))

        btns = BoxLayout(size_hint=(1, None), height=46, spacing=10)
        yes = RoundedButton(text=tr("yes"), bg_color=(0.45, 0.08, 0.08, 1), color=(1,1,1,1), font_size=14)
        no  = RoundedButton(text=tr("no"),  bg_color=(0.18, 0.18, 0.2, 1),  color=(1,1,1,1), font_size=14)
        btns.add_widget(yes)
        btns.add_widget(no)
        box.add_widget(lbl)
        box.add_widget(btns)

        confirm = Popup(
            title=tr("delete"), content=box,
            size_hint=(0.82, 0.32),
            background_color=(0.08, 0.08, 0.1, 1),
            separator_height=1
        )
        confirm.open()

        def do_delete(x):
            confirm.dismiss()
            tool_path = os.path.join(self._tools_dir, folder)
            try:
                shutil.rmtree(tool_path)
                self._status_lbl.text = f"[color=ff4444]{name} {tr('deleted')}[/color]"
            except Exception as e:
                self._status_lbl.text = f"[color=ff4444]Xato: {str(e)}[/color]"
            self._build_grid()

        yes.bind(on_press=do_delete)
        no.bind(on_press=lambda x: confirm.dismiss())

    def _load_tools(self, tools_dir=None):
        if tools_dir is None:
            tools_dir = TOOLS_DIR
        tools = []
        if not os.path.exists(tools_dir):
            os.makedirs(tools_dir)
            return tools

        for folder in sorted(os.listdir(tools_dir)):
            fpath     = os.path.join(tools_dir, folder)
            meta_path = os.path.join(fpath, "meta.json")
            main_path = os.path.join(fpath, "main.py")

            if os.path.isdir(fpath) and os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["_main"]   = main_path
                    meta["_folder"] = folder
                    tools.append(meta)
                except Exception as e:
                    print(f"[meta xato] {folder}: {e}")
        return tools

    def _open_output(self, name, main_path, color_hex):
        from utils import tool_manager

        if tool_manager.is_active(name):
            tool_manager.focus(name)
            return

        if not os.path.exists(main_path):
            return

        try:
            sys.modules.pop(name, None)
            spec = importlib.util.spec_from_file_location(name, main_path)
            mod  = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if hasattr(mod, "open_ui"):
                mod.open_ui()
                return
        except Exception as e:
            out = self.manager.get_screen("output")
            out.load(name, main_path, color_hex)
            out.out_label.text = f"[color=ff4444]XATO (yuklashda):[/color]\n\n{str(e)}"
            self.manager.current = "output"
            return

        out = self.manager.get_screen("output")
        out.load(name, main_path, color_hex)
        self.manager.current = "output"


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
        title="Info", content=lbl,
        size_hint=(0.82, 0.42),
        background_color=(0.08, 0.08, 0.1, 1),
        separator_height=1
    )
    p.open()

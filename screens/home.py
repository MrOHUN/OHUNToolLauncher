import os
import sys
import importlib.util

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

from utils.widgets import RoundedButton, NavBar
from utils.helpers import load_settings, hex_rgb, TOOLS_DIR


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._active_tab = "home"
        self._build()

    def _build(self):
        self._root = BoxLayout(orientation="vertical")

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
            text="[T] Tool Launcher", font_size=20, bold=True,
            color=(1, 1, 1, 1), halign="left", valign="middle",
            size_hint=(1, 1)
        )
        title.bind(size=title.setter("text_size"))
        header.add_widget(title)

        # CONTENT
        self.content = BoxLayout(
            orientation="vertical", size_hint=(1, 1), padding=[14, 14]
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

    def _home_view(self):
        self.content.clear_widgets()
        lbl = Label(
            text="Xush kelibsiz!\n\nQuyida  [T] Tools  tugmasini bosing.",
            font_size=17, color=(0.7, 0.7, 0.7, 1),
            halign="center", valign="middle", size_hint=(1, 1)
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.content.add_widget(lbl)

    def _tools_view(self):
        self.content.clear_widgets()
        s = load_settings()
        tools_dir = s.get("tools_dir", "").strip() or TOOLS_DIR
        tools = self._load_tools(tools_dir)
        cols = s.get("cols", 2)

        if not tools:
            lbl = Label(
                text="Hech qanday tool topilmadi.\n\ntools/ papkasiga tool qo'shing.",
                font_size=15, color=(0.5, 0.5, 0.5, 1),
                halign="center", valign="middle", size_hint=(1, 1)
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.content.add_widget(lbl)
            return

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(
            cols=cols, spacing=12, padding=[4, 4], size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter("height"))

        for tool in tools:
            grid.add_widget(self._make_tool_btn(tool))

        scroll.add_widget(grid)
        self.content.add_widget(scroll)

    def _load_tools(self, tools_dir=None):
        if tools_dir is None:
            tools_dir = TOOLS_DIR
        tools = []
        if not os.path.exists(tools_dir):
            os.makedirs(tools_dir)
            return tools

        for folder in sorted(os.listdir(tools_dir)):
            fpath = os.path.join(tools_dir, folder)
            meta_path = os.path.join(fpath, "meta.json")
            main_path = os.path.join(fpath, "main.py")

            if os.path.isdir(fpath) and os.path.exists(meta_path):
                try:
                    import json
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["_main"] = main_path
                    tools.append(meta)
                except Exception as e:
                    print(f"[meta xato] {folder}: {e}")
        return tools

    def _make_tool_btn(self, tool):
        name      = tool.get("name", "Tool")
        icon      = tool.get("icon", "[T]")
        color_hex = tool.get("color", "#2277ff")
        main_path = tool.get("_main", "")
        r, g, b   = hex_rgb(color_hex)

        btn = RoundedButton(
            bg_color=(r, g, b, 1),
            text=f"{icon}\n{name}", font_size=14,
            size_hint=(1, None), height=110,
            halign="center", valign="middle", color=(1, 1, 1, 1)
        )
        btn.bind(on_press=lambda x: self._open_output(name, main_path, color_hex))
        return btn

    def _open_output(self, name, main_path, color_hex):
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
            # Xatoni OutputScreen da ko'rsat
            out = self.manager.get_screen("output")
            out.load(name, main_path, color_hex)
            out.out_label.text = f"[color=ff4444]XATO (yuklashda):[/color]\n\n{str(e)}"
            self.manager.current = "output"
            return

        out = self.manager.get_screen("output")
        out.load(name, main_path, color_hex)
        self.manager.current = "output"

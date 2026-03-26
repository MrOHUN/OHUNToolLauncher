from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle

from utils.widgets import RoundedButton, NavBar
from utils.helpers import load_settings, save_settings, TOOLS_DIR


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")
        s = load_settings()

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
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation="vertical", size_hint=(1, None),
            padding=[18, 18], spacing=20
        )
        content.bind(minimum_height=content.setter("height"))

        # Tools papka yo'li
        content.add_widget(self._section_label("Tools papkasi yo'li"))
        self.tools_dir_input = TextInput(
            text=s.get("tools_dir", ""),
            hint_text=f"bo'sh = standart ({TOOLS_DIR})",
            multiline=False, font_size=13,
            background_color=(0.18, 0.18, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.2, 0.6, 1, 1),
            size_hint=(1, None), height=44
        )
        content.add_widget(self.tools_dir_input)

        # Grid ustunlar soni
        content.add_widget(self._section_label("Tool tugmalar — ustun soni"))
        cols_row = BoxLayout(size_hint=(1, None), height=48, spacing=10)
        self.cols_btns = {}
        for c in [1, 2, 3]:
            btn = RoundedButton(
                bg_color=(0.2, 0.6, 1, 1) if s.get("cols", 2) == c else (0.22, 0.22, 0.28, 1),
                text=str(c), font_size=16,
                size_hint=(1, 1), color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, val=c: self._set_cols(val))
            self.cols_btns[c] = btn
            cols_row.add_widget(btn)
        content.add_widget(cols_row)

        # Saqlash tugmasi
        content.add_widget(Label(size_hint=(1, None), height=10))
        save_btn = RoundedButton(
            bg_color=(0.15, 0.5, 0.3, 1), text="Saqlash",
            font_size=16, size_hint=(1, None), height=50, color=(1, 1, 1, 1)
        )
        save_btn.bind(on_press=self._save)
        content.add_widget(save_btn)

        self._status_lbl = Label(
            text="", font_size=13, color=(0.4, 0.9, 0.5, 1),
            size_hint=(1, None), height=30, halign="center"
        )
        self._status_lbl.bind(size=self._status_lbl.setter("text_size"))
        content.add_widget(self._status_lbl)

        scroll.add_widget(content)

        # NAVBAR
        navbar = NavBar(
            active="settings",
            on_home=self._go_home,
            on_tools=self._go_tools,
            on_settings=None
        )

        root.add_widget(header)
        root.add_widget(scroll)
        root.add_widget(navbar)
        self.add_widget(root)

        self._cols_val = s.get("cols", 2)

    def _section_label(self, text):
        lbl = Label(
            text=text, font_size=14, color=(0.5, 0.7, 1, 1),
            halign="left", valign="middle",
            size_hint=(1, None), height=30
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _set_cols(self, val):
        self._cols_val = val
        for c, btn in self.cols_btns.items():
            btn.bg_color = (0.2, 0.6, 1, 1) if c == val else (0.22, 0.22, 0.28, 1)
            btn._draw()

    def _save(self, *args):
        s = load_settings()
        s["tools_dir"] = self.tools_dir_input.text.strip()
        s["cols"] = self._cols_val
        save_settings(s)
        self._status_lbl.text = "Saqlandi!"

    def _go_home(self, *args):
        self.manager.current = "home"

    def _go_tools(self, *args):
        home = self.manager.get_screen("home")
        home._on_tools()
        self.manager.current = "home"

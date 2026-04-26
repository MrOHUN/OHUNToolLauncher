from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

from utils.widgets import RoundedButton, NavBar
from utils.helpers import load_theme, t as tr

from .tool_store import open_tool_store
from .theme_store import open_theme_store
from .lang_store import open_lang_store
from .brain_store import open_brain
from .active_tools import open_active_tools
from .widget_store import open_widget_store


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        t = load_theme()
        root = BoxLayout(orientation="vertical")

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
            text=f"[S] {tr('settings')}", font_size=t.FONT_SIZE_TITLE, bold=True,
            color=t.TEXT_COLOR, halign="left", valign="middle",
            size_hint=(1, 1)
        )
        title.bind(size=title.setter("text_size"))
        header.add_widget(title)

        # STATUS
        self.status_lbl = Label(
            text="", font_size=13,
            color=t.SUBTEXT_COLOR,
            size_hint=(1, None), height=28,
            halign="center", valign="middle",
            markup=True
        )
        self.status_lbl.bind(size=self.status_lbl.setter("text_size"))

        # SCROLL CONTENT
        scroll = ScrollView(size_hint=(1, 1))
        inner = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            padding=[18, 20],
            spacing=12
        )
        inner.bind(minimum_height=inner.setter("height"))

        # Tugmalar — har biri o'z rangi bilan
        buttons = [
            {
                "key": "install_tool",
                "bg":  (0.1,  0.35, 0.65, 1),   # Ko'k — tool o'rnatish
                "fg":  (0.7,  0.9,  1.0,  1),
                "cb":  lambda x: open_tool_store(self.status_lbl)
            },
            {
                "key": "widgets",
                "bg":  (0.1,  0.42, 0.38, 1),   # Zangori-yashil — widgets
                "fg":  (0.6,  1.0,  0.9,  1),
                "cb":  lambda x: open_widget_store(self.status_lbl)
            },
            {
                "key": "theme_store",
                "bg":  (0.35, 0.15, 0.55, 1),   # Binafsha — tema
                "fg":  (0.85, 0.7,  1.0,  1),
                "cb":  lambda x: open_theme_store(self.status_lbl)
            },
            {
                "key": "lang_store",
                "bg":  (0.1,  0.38, 0.28, 1),   # Yashil-ko'k — til
                "fg":  (0.6,  1.0,  0.8,  1),
                "cb":  lambda x: open_lang_store(self.status_lbl)
            },
            {
                "key": "brain",
                "bg":  (0.45, 0.28, 0.05, 1),   # To'q sariq — brain
                "fg":  (1.0,  0.85, 0.4,  1),
                "cb":  lambda x: open_brain()
            },
            {
                "key": "active_tools",
                "bg":  (0.15, 0.15, 0.18, 1),   # Kulrang — faol toollar
                "fg":  (0.75, 0.75, 0.8,  1),
                "cb":  lambda x: open_active_tools()
            },
        ]

        for item in buttons:
            btn = RoundedButton(
                bg_color=item["bg"],
                text=tr(item["key"]),
                font_size=16,
                size_hint=(1, None), height=56,
                color=item["fg"]
            )
            btn.bind(on_press=item["cb"])
            inner.add_widget(btn)

        inner.add_widget(self.status_lbl)
        scroll.add_widget(inner)

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

    def _go_home(self, *args):
        self.manager.current = "home"

    def _go_tools(self, *args):
        home = self.manager.get_screen("home")
        home._on_tools()
        self.manager.current = "home"

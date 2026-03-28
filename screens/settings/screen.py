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
from .active_tools import open_active_tools  # ← Yangi import


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
            size_hint=(1, None), height=30,
            halign="center", valign="middle",
            markup=True
        )
        self.status_lbl.bind(size=self.status_lbl.setter("text_size"))

        # SCROLL CONTENT
        scroll = ScrollView(size_hint=(1, 1))
        inner = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            padding=[18, 16],
            spacing=16
        )
        inner.bind(minimum_height=inner.setter("height"))

        # --- Tugmalar ---
        
        # Tool Store
        tool_btn = RoundedButton(
            bg_color=t.ACCENT_COLOR,
            text=tr("install_tool"),
            font_size=16, size_hint=(1, None), height=56,
            color=t.TEXT_COLOR
        )
        tool_btn.bind(on_press=lambda x: open_tool_store(self.status_lbl))

        # Theme Store
        theme_btn = RoundedButton(
            bg_color=t.ACCENT_COLOR,
            text=tr("theme_store"),
            font_size=16, size_hint=(1, None), height=56,
            color=t.TEXT_COLOR
        )
        theme_btn.bind(on_press=lambda x: open_theme_store(self.status_lbl))

        # Lang Store
        lang_btn = RoundedButton(
            bg_color=t.ACCENT_COLOR,
            text=tr("lang_store"),
            font_size=16, size_hint=(1, None), height=56,
            color=t.TEXT_COLOR
        )
        lang_btn.bind(on_press=lambda x: open_lang_store(self.status_lbl))

        # Brain Store
        brain_btn = RoundedButton(
            bg_color=t.ACCENT_COLOR,
            text=tr("brain"),
            font_size=16, size_hint=(1, None), height=56,
            color=t.TEXT_COLOR
        )
        brain_btn.bind(on_press=lambda x: open_brain())

        # Active Tools (Yangi qo'shilgan tugma)
        active_btn = RoundedButton(
            bg_color=t.ACCENT_COLOR,
            text=tr("active_tools"),
            font_size=16, size_hint=(1, None), height=56,
            color=t.TEXT_COLOR
        )
        active_btn.bind(on_press=lambda x: open_active_tools())

        # Widgetlarni tartib bilan qo'shish
        inner.add_widget(tool_btn)
        inner.add_widget(theme_btn)
        inner.add_widget(lang_btn)
        inner.add_widget(brain_btn)
        inner.add_widget(active_btn)  # ← Active Tools qo'shildi
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

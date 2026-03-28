import os
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

from utils.helpers import t, load_lang, LANGS_DIR

print("LANGS_DIR:", LANGS_DIR)
load_lang()
print("home:", t("home"))


class RoundedButton(Button):
    def __init__(self, bg_color=(0.2, 0.6, 1, 1), radius=14, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self._radius = radius
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])


class NavBar(BoxLayout):
    def __init__(self, active="home", on_home=None, on_tools=None, on_settings=None, **kwargs):
        super().__init__(size_hint=(1, None), height=110, **kwargs)

        with self.canvas.before:
            Color(0.13, 0.13, 0.16, 1)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(
            size=lambda w, v: setattr(self._rect, 'size', v),
            pos=lambda w, v: setattr(self._rect, 'pos', v)
        )

        active_color  = (0.2, 0.6, 1, 1)
        passive_color = (0.45, 0.45, 0.5, 1)

        self.btn_home = Button(
            text=f"[H]\n{t('home')}", font_size=20,
            markup=True,
            color=active_color if active == "home" else passive_color,
            background_color=(0, 0, 0, 0), background_normal="",
            halign="center"
        )
        self.btn_tools = Button(
            text=f"[T]\n{t('tools_nav')}", font_size=20,
            markup=True,
            color=active_color if active == "tools" else passive_color,
            background_color=(0, 0, 0, 0), background_normal="",
            halign="center"
        )
        self.btn_settings = Button(
            text=f"[S]\n{t('settings_nav')}", font_size=20,
            markup=True,
            color=active_color if active == "settings" else passive_color,
            background_color=(0, 0, 0, 0), background_normal="",
            halign="center"
        )

        if on_home:     self.btn_home.bind(on_press=on_home)
        if on_tools:    self.btn_tools.bind(on_press=on_tools)
        if on_settings: self.btn_settings.bind(on_press=on_settings)

        self.add_widget(self.btn_home)
        self.add_widget(self.btn_tools)
        self.add_widget(self.btn_settings)

    def set_active(self, name):
        active_color  = (0.2, 0.6, 1, 1)
        passive_color = (0.45, 0.45, 0.5, 1)
        self.btn_home.color     = active_color if name == "home"     else passive_color
        self.btn_tools.color    = active_color if name == "tools"    else passive_color
        self.btn_settings.color = active_color if name == "settings" else passive_color

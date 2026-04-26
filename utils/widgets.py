from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle

from utils.helpers import t, load_theme


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

        theme = load_theme()
        navbar_color  = getattr(theme, 'NAVBAR_COLOR',  (0.07, 0.07, 0.18, 1))
        active_color  = getattr(theme, 'ACCENT_COLOR',  (0.2,  0.6,  1.0,  1))
        passive_color = (0.45, 0.45, 0.5, 1)

        with self.canvas.before:
            Color(*navbar_color)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(
            size=lambda w, v: setattr(self._rect, 'size', v),
            pos=lambda w, v: setattr(self._rect, 'pos', v)
        )

        self._active_color  = active_color
        self._passive_color = passive_color

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
        self.btn_home.color     = self._active_color if name == "home"     else self._passive_color
        self.btn_tools.color    = self._active_color if name == "tools"    else self._passive_color
        self.btn_settings.color = self._active_color if name == "settings" else self._passive_color

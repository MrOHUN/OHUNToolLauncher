from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from utils.widgets import RoundedButton
from utils.helpers import load_settings, save_settings

AVAILABLE_THEMES = [
    {"name": "Default", "folder": "default", "description": "Standart qora tema"},
    {"name": "Hacker",  "folder": "hacker",  "description": "Yashil matritsa tema"},
]


def open_theme_store(status_lbl):
    s = load_settings()
    current = s.get("theme", "default")

    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    for theme in AVAILABLE_THEMES:
        row = BoxLayout(size_hint=(1, None), height=70, spacing=8)
        info = Label(
            text=f"[b]{theme['name']}[/b]\n[color=888888][size=12]{theme['description']}[/size][/color]",
            markup=True, font_size=14,
            halign="left", valign="middle", size_hint=(1, 1)
        )
        info.bind(size=info.setter("text_size"))

        if theme["folder"] == current:
            btn = RoundedButton(
                bg_color=(0.2, 0.2, 0.2, 1),
                text="Faol", font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(0.5, 0.5, 0.5, 1)
            )
        else:
            btn = RoundedButton(
                bg_color=(0.1, 0.45, 0.25, 1),
                text="Tanlash", font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, t=theme: _apply_theme(t, status_lbl, popup))

        row.add_widget(info)
        row.add_widget(btn)
        box.add_widget(row)

    scroll.add_widget(box)
    content.add_widget(scroll)

    popup = Popup(
        title="Temalar",
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()


def _apply_theme(theme, status_lbl, popup):
    popup.dismiss()
    s = load_settings()
    s["theme"] = theme["folder"]
    save_settings(s)
    status_lbl.text = f"[color=33ff88]{theme['name']} tema tanlandi! Qayta ishga tushiring.[/color]"
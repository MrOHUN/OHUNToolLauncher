from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from utils.widgets import RoundedButton
from utils.helpers import load_settings, save_settings, t as tr, load_lang

AVAILABLE_LANGS = [
    {"name": "O'zbek",  "code": "uz", "description": "O'zbek tili"},
    {"name": "English", "code": "en", "description": "English language"},
]


def open_lang_store(status_lbl):
    s = load_settings()
    current = s.get("lang", "uz")

    content = BoxLayout(orientation="vertical", spacing=8, padding=[10, 10])
    scroll = ScrollView(size_hint=(1, 1))
    box = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    box.bind(minimum_height=box.setter("height"))

    for lang in AVAILABLE_LANGS:
        row = BoxLayout(size_hint=(1, None), height=70, spacing=8)
        info = Label(
            text=f"[b]{lang['name']}[/b]\n[color=888888][size=12]{lang['description']}[/size][/color]",
            markup=True, font_size=14,
            halign="left", valign="middle", size_hint=(1, 1)
        )
        info.bind(size=info.setter("text_size"))

        if lang["code"] == current:
            btn = RoundedButton(
                bg_color=(0.2, 0.2, 0.2, 1),
                text=tr("active"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(0.5, 0.5, 0.5, 1)
            )
        else:
            btn = RoundedButton(
                bg_color=(0.1, 0.45, 0.25, 1),
                text=tr("select"), font_size=12,
                size_hint=(None, None), width=110, height=44,
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda x, l=lang: _apply_lang(l, status_lbl, popup))

        row.add_widget(info)
        row.add_widget(btn)
        box.add_widget(row)

    scroll.add_widget(box)
    content.add_widget(scroll)

    popup = Popup(
        title=tr("languages"),
        content=content,
        size_hint=(0.95, 0.85),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()


def _apply_lang(lang, status_lbl, popup):
    popup.dismiss()
    s = load_settings()
    s["lang"] = lang["code"]
    save_settings(s)
    load_lang()  # keshni yangilash
    status_lbl.text = f"[color=33ff88]{lang['name']} {tr('lang_applied')}[/color]"

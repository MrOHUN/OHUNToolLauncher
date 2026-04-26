from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from utils.widgets import RoundedButton
from utils import tool_manager
from utils.helpers import t as tr


def open_active_tools():
    content = BoxLayout(orientation="vertical", spacing=8, padding=[12, 12])

    scroll = ScrollView(size_hint=(1, 1))
    inner = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=8)
    inner.bind(minimum_height=inner.setter("height"))

    active = tool_manager.get_active()

    if not active:
        lbl = Label(
            text=tr("no_active_tools"),
            font_size=14, color=(0.5, 0.5, 0.5, 1),
            halign="center", valign="middle",
            size_hint=(1, None), height=60
        )
        lbl.bind(size=lbl.setter("text_size"))
        inner.add_widget(lbl)
    else:
        for name in active:
            row = BoxLayout(size_hint=(1, None), height=52, spacing=6)

            lbl = Label(
                text=f"[b]{name}[/b]",
                markup=True, font_size=14,
                halign="left", valign="middle",
                size_hint=(1, 1)
            )
            lbl.bind(size=lbl.setter("text_size"))

            focus_btn = RoundedButton(
                text=tr("open"),
                bg_color=(0.1, 0.45, 0.25, 1),
                color=(1, 1, 1, 1),
                font_size=12,
                size_hint=(None, 1), width=80
            )
            focus_btn.bind(on_press=lambda x, n=name: tool_manager.focus(n))

            close_btn = RoundedButton(
                text=tr("close"),
                bg_color=(0.4, 0.1, 0.1, 1),
                color=(1, 0.5, 0.5, 1),
                font_size=12,
                size_hint=(None, 1), width=80
            )
            close_btn.bind(on_press=lambda x, n=name: tool_manager.close(n))

            row.add_widget(lbl)
            row.add_widget(focus_btn)
            row.add_widget(close_btn)
            inner.add_widget(row)

    scroll.add_widget(inner)
    content.add_widget(scroll)

    popup = Popup(
        title=tr("active_tools"),
        content=content,
        size_hint=(0.95, 0.75),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()
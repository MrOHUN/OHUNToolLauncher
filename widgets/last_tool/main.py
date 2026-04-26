# widgets/last_tool/main.py
# Widget shartnomasi: get_widget() → Kivy widget qaytaradi

import os
import json
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

import widget_api


def get_widget():
    return LastToolWidget(__file__)


class LastToolWidget(BoxLayout):
    def __init__(self, main_file, **kwargs):
        super().__init__(orientation="vertical", size_hint=(1, None), height=70,
                         padding=[14, 8], spacing=4, **kwargs)
        self._main_file = main_file

        with self.canvas.before:
            Color(0.1, 0.12, 0.1, 1)
            self._rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(
            size=lambda w, v: setattr(self._rect, 'size', v),
            pos=lambda w, v: setattr(self._rect, 'pos', v)
        )

        title = Label(
            text="Oxirgi tool:", font_size=12,
            color=(0.5, 0.8, 0.5, 1),
            halign="left", valign="middle",
            size_hint=(1, None), height=20
        )
        title.bind(size=title.setter("text_size"))

        self._name_lbl = Label(
            text=self._get_last_tool(),
            font_size=15, bold=True,
            color=(1, 1, 1, 1),
            halign="left", valign="middle",
            size_hint=(1, None), height=30
        )
        self._name_lbl.bind(size=self._name_lbl.setter("text_size"))

        self.add_widget(title)
        self.add_widget(self._name_lbl)

    def _get_last_tool(self):
        data = widget_api.load_widget_data(self._main_file, "state.json", {})
        return data.get("last_tool", "—")

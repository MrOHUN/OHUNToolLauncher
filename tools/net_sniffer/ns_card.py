# net_sniffer/ns_card.py

import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))

if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle

from ns_apps import get_app_name

STATE_COLORS = {
    "ESTABLISHED": (0, 1, 0.5, 1),
    "LISTEN":      (0, 0.7, 1, 1),
    "TIME_WAIT":   (1, 0.8, 0, 1),
    "CLOSE_WAIT":  (1, 0.5, 0, 1),
}
DEFAULT_COLOR = (0.5, 0.5, 0.5, 1)


class ConnectionCard(BoxLayout):
    def __init__(self, conn, **kwargs):
        super().__init__(**kwargs)
        self.conn = conn
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 90
        self.padding = (10, 6)
        self.spacing = 2

        with self.canvas.before:
            Color(0.12, 0.12, 0.15, 1)
            self._rect = RoundedRectangle(radius=[8], pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        app_name = get_app_name(conn.get("uid", "0"))
        state = conn.get("state", "—")
        proto = conn.get("proto", "TCP")
        remote_ip = conn.get("remote_ip", "")
        remote_port = conn.get("remote_port", 0)
        local_port = conn.get("local_port", 0)
        state_color = STATE_COLORS.get(state, DEFAULT_COLOR)

        # 1-qator: proto + remote ip:port + state
        row1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=28)
        row1.add_widget(Label(
            text=f"[{proto}] {remote_ip}:{remote_port}",
            font_size=14, color=(1, 1, 1, 1),
            halign="left", valign="middle",
            size_hint_x=0.75, text_size=(None, None)
        ))
        row1.add_widget(Label(
            text=state,
            font_size=12, color=state_color,
            halign="right", valign="middle",
            size_hint_x=0.25
        ))
        self.add_widget(row1)

        # 2-qator: ilova nomi
        self.add_widget(Label(
            text=app_name,
            font_size=12, color=(0.7, 0.9, 1, 1),
            halign="left", valign="middle",
            size_hint_y=None, height=22,
            text_size=(None, None)
        ))

        # 3-qator: lokal port → masofaviy port
        row3 = BoxLayout(orientation="horizontal", size_hint_y=None, height=20)
        row3.add_widget(Label(
            text=f":{local_port} -> :{remote_port}",
            font_size=11, color=(0.6, 0.6, 0.6, 1),
            halign="left", valign="middle",
            size_hint_x=0.7
        ))
        btn_info = Button(
            text="[i]",
            font_size=11,
            size_hint_x=0.3,
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        btn_info.bind(on_release=self._show_info)
        row3.add_widget(btn_info)
        self.add_widget(row3)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _show_info(self, *args):
        c = self.conn
        app_name = get_app_name(c.get("uid", "0"))
        info = (
            f"Protokol:  {c.get('proto')}\n"
            f"Ilova:     {app_name}\n"
            f"UID:       {c.get('uid')}\n"
            f"Lokal:     {c.get('local_ip')}:{c.get('local_port')}\n"
            f"Masofaviy: {c.get('remote_ip')}:{c.get('remote_port')}\n"
            f"Holat:     {c.get('state')}\n"
        )
        box = BoxLayout(orientation="vertical", padding=12, spacing=8)
        box.add_widget(Label(
            text=info, font_size=13,
            color=(1, 1, 1, 1), halign="left",
            valign="top", text_size=(320, None)
        ))
        btn = Button(
            text="Yopish", size_hint_y=None, height=40,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        box.add_widget(btn)
        p = Popup(
            title="Ulanish tafsiloti", content=box,
            size_hint=(0.9, 0.55),
            background_color=(0.08, 0.08, 0.1, 1),
            separator_height=0
        )
        btn.bind(on_release=p.dismiss)
        p.open()
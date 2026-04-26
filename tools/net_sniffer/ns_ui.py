# net_sniffer/ns_ui.py

import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))

if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

from ns_bridge import VpnBridge
from ns_card import ConnectionCard


class NetSnifferUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 4
        self.padding = (6, 6)
        self._popup = None
        self._filter = "all"
        self._connections = {}  # key: remote_ip:port, value: conn
        self._bridge = VpnBridge(on_packet=self._on_packet)

        self._build_ui()
        self._bridge.start()

    def _on_packet(self, conn):
        """Yangi paket kelganda — UI ga qo'shish."""
        key = conn["remote_ip"] + ":" + str(conn["remote_port"])
        self._connections[key] = conn
        Clock.schedule_once(lambda dt: self._render(), 0)

    def _build_ui(self):
        # Title bar
        title_bar = BoxLayout(size_hint_y=None, height=44, spacing=4)
        btn_min = Button(
            text="[-]", size_hint_x=None, width=44,
            background_color=(0.2, 0.2, 0.3, 1), color=(1, 1, 1, 1)
        )
        btn_min.bind(on_release=self._minimize)
        title_bar.add_widget(btn_min)
        title_bar.add_widget(Label(
            text=">> Net Sniffer",
            font_size=16, color=(0, 1, 0.5, 1),
            bold=True
        ))
        btn_close = Button(
            text="[x]", size_hint_x=None, width=44,
            background_color=(0.7, 0.1, 0.1, 1), color=(1, 1, 1, 1)
        )
        btn_close.bind(on_release=self._close)
        title_bar.add_widget(btn_close)
        self.add_widget(title_bar)

        # Filter qatori
        filter_bar = BoxLayout(size_hint_y=None, height=38, spacing=4)
        for key, label in [
            ("all", "Hammasi"),
            ("TCP", "TCP"),
            ("UDP", "UDP"),
            ("LIVE", "Jonli"),
        ]:
            btn = Button(
                text=label, font_size=12,
                background_color=(0.2, 0.5, 0.8, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=lambda x, k=key: self._set_filter(k))
            filter_bar.add_widget(btn)
        self.add_widget(filter_bar)

        # Status + tozalash
        ctrl_bar = BoxLayout(size_hint_y=None, height=38, spacing=6)
        btn_clear = Button(
            text="Tozalash", font_size=13,
            size_hint_x=0.4,
            background_color=(0.6, 0.2, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        btn_clear.bind(on_release=self._clear)
        ctrl_bar.add_widget(btn_clear)
        self._status_label = Label(
            text="Kutilmoqda...", font_size=12,
            color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.6
        )
        ctrl_bar.add_widget(self._status_label)
        self.add_widget(ctrl_bar)

        # Progress bar
        self._progress = ProgressBar(
            max=100, value=0,
            size_hint_y=None, height=6
        )
        self.add_widget(self._progress)

        # ScrollView
        self._scroll = ScrollView()
        self._list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=4
        )
        self._list.bind(minimum_height=self._list.setter("height"))
        self._scroll.add_widget(self._list)
        self.add_widget(self._scroll)

        # Eksport tugmasi
        btn_export = Button(
            text="Eksport",
            size_hint_y=None, height=40,
            background_color=(0.2, 0.3, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        btn_export.bind(on_release=self._export)
        self.add_widget(btn_export)

    def _set_filter(self, key):
        self._filter = key
        self._render()

    def _clear(self, *args):
        self._connections.clear()
        self._render()

    def _render(self):
        self._list.clear_widgets()
        conns = list(self._connections.values())

        if self._filter == "TCP":
            conns = [c for c in conns if c["proto"] == "TCP"]
        elif self._filter == "UDP":
            conns = [c for c in conns if c["proto"] == "UDP"]
        elif self._filter == "LIVE":
            conns = [c for c in conns if c["state"] == "LIVE"]

        count = len(conns)
        self._status_label.text = str(count) + " ta ulanish"
        self._progress.value = min(count * 5, 100)

        if count == 0:
            self._list.add_widget(Label(
                text="Ulanish topilmadi",
                font_size=13, color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None, height=60
            ))
            return

        for conn in conns:
            self._list.add_widget(ConnectionCard(conn))

    def _export(self, *args):
        lines = []
        for c in self._connections.values():
            lines.append(
                c["proto"] + " " + c["remote_ip"] + ":" +
                str(c["remote_port"]) + " " + c["state"] +
                " :" + str(c["local_port"])
            )
        Clipboard.copy("\n".join(lines))
        self._status_label.text = "Nusxalandi!"
        Clock.schedule_once(
            lambda dt: setattr(
                self._status_label, "text",
                str(len(self._connections)) + " ta ulanish"
            ), 2
        )

    def _minimize(self, *args):
        self._bridge.stop()
        if self._popup:
            self._popup.dismiss()

    def _close(self, *args):
        self._bridge.stop()
        from utils import tool_manager
        tool_manager.close("Net Sniffer")
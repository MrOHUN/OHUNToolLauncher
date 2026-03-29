# host_scanner/hs_ui.py
import os
import sys
import threading

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

from utils.helpers import t as tr, load_theme
from hs_scanner import scan
from hs_card import DeviceCard

TOOL_NAME = "Host Scanner"


class HostScannerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        th = load_theme()
        self.orientation = "vertical"
        self.spacing = 6
        self.padding = [8, 8]
        self._popup      = None
        self._scanning   = False
        self._export_btn = None
        self._all_devices = []
        self._filter     = "all"   # all | online | ports
        self._sort       = "ip"    # ip | type

        # --- Title Bar ---
        title_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=48, spacing=6
        )
        min_btn = Button(
            text="-", size_hint_x=None, width=48,
            background_color=(0.2, 0.2, 0.25, 1),
            color=th.TEXT_COLOR, font_size=16
        )
        min_btn.bind(on_release=self._minimize)

        title = Label(
            text=f">> {tr('hs_title')}",
            color=th.ACCENT_COLOR,
            font_size=15, bold=True
        )

        close_btn = Button(
            text="x", size_hint_x=None, width=48,
            background_color=(0.4, 0.1, 0.1, 1),
            color=th.TEXT_COLOR, font_size=16
        )
        close_btn.bind(on_release=self._close)

        title_bar.add_widget(min_btn)
        title_bar.add_widget(title)
        title_bar.add_widget(close_btn)
        self.add_widget(title_bar)

        # --- Scan tugmasi ---
        self.scan_btn = Button(
            text=tr("hs_scan"),
            size_hint_y=None, height=48,
            background_color=th.ACCENT_COLOR,
            color=th.TEXT_COLOR, font_size=15
        )
        self.scan_btn.bind(on_release=self._start)
        self.add_widget(self.scan_btn)

        # --- Progress bar ---
        self.progress = ProgressBar(
            max=100, value=0,
            size_hint_y=None, height=8
        )
        self.add_widget(self.progress)

        # --- Status ---
        self.status_label = Label(
            text="", color=th.SUBTEXT_COLOR,
            size_hint_y=None, height=26, font_size=12
        )
        self.add_widget(self.status_label)

        # --- Filter qatori ---
        filter_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=40, spacing=4
        )

        self.btn_all = Button(
            text=tr("hs_filter_all"),
            background_color=th.ACCENT_COLOR,
            color=th.TEXT_COLOR, font_size=12
        )
        self.btn_online = Button(
            text=tr("hs_filter_online"),
            background_color=(0.2, 0.2, 0.25, 1),
            color=th.TEXT_COLOR, font_size=12
        )
        self.btn_ports = Button(
            text=tr("hs_filter_ports"),
            background_color=(0.2, 0.2, 0.25, 1),
            color=th.TEXT_COLOR, font_size=12
        )

        self.btn_all.bind(on_release=lambda x: self._set_filter("all"))
        self.btn_online.bind(on_release=lambda x: self._set_filter("online"))
        self.btn_ports.bind(on_release=lambda x: self._set_filter("ports"))

        filter_bar.add_widget(self.btn_all)
        filter_bar.add_widget(self.btn_online)
        filter_bar.add_widget(self.btn_ports)
        self.add_widget(filter_bar)

        # --- Sort qatori ---
        sort_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=36, spacing=4
        )

        self.btn_sort_ip = Button(
            text=tr("hs_sort_ip"),
            background_color=th.ACCENT_COLOR,
            color=th.TEXT_COLOR, font_size=11
        )
        self.btn_sort_type = Button(
            text=tr("hs_sort_type"),
            background_color=(0.2, 0.2, 0.25, 1),
            color=th.TEXT_COLOR, font_size=11
        )

        self.btn_sort_ip.bind(on_release=lambda x: self._set_sort("ip"))
        self.btn_sort_type.bind(on_release=lambda x: self._set_sort("type"))

        sort_bar.add_widget(self.btn_sort_ip)
        sort_bar.add_widget(self.btn_sort_type)
        self.add_widget(sort_bar)

        # --- Natijalar ---
        scroll = ScrollView()
        self.results_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None, spacing=8
        )
        self.results_box.bind(
            minimum_height=self.results_box.setter("height")
        )
        scroll.add_widget(self.results_box)
        self.add_widget(scroll)

    # --- Filter ---
    def _set_filter(self, mode):
        th = load_theme()
        self._filter = mode
        for btn, m in [
            (self.btn_all, "all"),
            (self.btn_online, "online"),
            (self.btn_ports, "ports")
        ]:
            btn.background_color = (
                th.ACCENT_COLOR if m == mode
                else (0.2, 0.2, 0.25, 1)
            )
        self._render(self._all_devices)

    # --- Sort ---
    def _set_sort(self, mode):
        th = load_theme()
        self._sort = mode
        for btn, m in [
            (self.btn_sort_ip, "ip"),
            (self.btn_sort_type, "type")
        ]:
            btn.background_color = (
                th.ACCENT_COLOR if m == mode
                else (0.2, 0.2, 0.25, 1)
            )
        self._render(self._all_devices)

    # --- Render ---
    def _render(self, devices):
        # Filter
        if self._filter == "online":
            devices = [d for d in devices if d.get("ping", {}).get("alive")]
        elif self._filter == "ports":
            devices = [d for d in devices if d.get("ports")]

        # Sort
        if self._sort == "ip":
            devices = sorted(devices, key=lambda d: [
                int(x) for x in d.get("ip", "0.0.0.0").split(".")
            ])
        elif self._sort == "type":
            devices = sorted(devices, key=lambda d: d.get("device_type", ""))

        self.results_box.clear_widgets()
        for d in devices:
            self.results_box.add_widget(DeviceCard(device=d))

    # --- Tugmalar ---
    def _minimize(self, *args):
        if self._popup:
            self._popup.dismiss()

    def _close(self, *args):
        from utils import tool_manager
        tool_manager.close(TOOL_NAME)

    # --- Scan ---
    def _start(self, *args):
        if self._scanning:
            return
        self._scanning = True
        self._all_devices = []
        self.scan_btn.text = tr("hs_scanning")
        self.results_box.clear_widgets()
        self.status_label.text = ""
        self.progress.value = 0

        if self._export_btn:
            self.remove_widget(self._export_btn)
            self._export_btn = None

        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        step = [0]

        def _prog():
            step[0] += 1
            val = min(int(step[0] / 4 * 90), 90)
            Clock.schedule_once(
                lambda dt: setattr(self.progress, "value", val)
            )

        def on_update(devices):
            _prog()
            Clock.schedule_once(lambda dt: self._update(devices))

        results = scan(callback=on_update)
        Clock.schedule_once(lambda dt: self._done(results))

    def _update(self, devices):
        self._all_devices = devices
        self._render(devices)

    def _done(self, devices):
        self._all_devices = devices
        self.progress.value = 100
        count = len(devices)
        self.status_label.text = (
            f"{count} {tr('hs_found')}"
            if count else tr("hs_no_devices")
        )
        self.scan_btn.text = tr("hs_scan")
        self._scanning = False
        self._render(devices)
        if devices:
            self._add_export_btn(devices)

    def _add_export_btn(self, devices):
        th = load_theme()
        if self._export_btn:
            self.remove_widget(self._export_btn)

        self._export_btn = Button(
            text=tr("hs_export"),
            size_hint_y=None, height=44,
            background_color=(0.15, 0.15, 0.3, 1),
            color=th.TEXT_COLOR, font_size=14
        )
        self._export_btn.bind(on_release=lambda x: self._export(devices))
        self.add_widget(self._export_btn, index=1)

    def _export(self, devices):
        lines = []
        for d in devices:
            ip       = d.get("ip", "?")
            vendor   = d.get("vendor", "—")
            dtype    = d.get("device_type", "—")
            os_n     = d.get("os", "—")
            ping_i   = d.get("ping", {})
            ports    = d.get("ports", {})
            ping_str = f"{ping_i.get('ms')}ms" if ping_i.get("alive") else "offline"
            port_str = ", ".join(ports.values()) if ports else "yo'q"
            lines.append(f"{ip} | {dtype} | {vendor} | {os_n} | {ping_str} | {port_str}")

        Clipboard.copy("\n".join(lines))
        self._export_btn.text = tr("hs_copied")
        Clock.schedule_once(
            lambda dt: setattr(self._export_btn, "text", tr("hs_export")), 2
        )
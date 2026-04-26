# host_scanner/hs_card.py
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
from kivy.core.clipboard import Clipboard

from utils.helpers import t as tr, load_theme


class DeviceCard(BoxLayout):
    def __init__(self, device, **kwargs):
        super().__init__(**kwargs)
        th = load_theme()
        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = 190
        self.spacing = 6
        self.padding = [10, 8]

        ip          = device.get("ip", "?")
        mac         = device.get("mac", "—")
        vendor      = device.get("vendor", "Noma'lum")
        hostname    = device.get("hostname", "—")
        os_name     = device.get("os", "Noma'lum")
        ports       = device.get("ports", {})
        banners     = device.get("banners", {})
        ping_info   = device.get("ping", {})
        device_type = device.get("device_type", "Noma'lum")
        icon        = device.get("icon", "[?]")

        # Ping
        if ping_info.get("alive"):
            ping_text  = f"{ping_info.get('ms', '?')} ms"
            ping_color = (0.0, 1.0, 0.3, 1)
        else:
            ping_text  = "offline"
            ping_color = (1.0, 0.3, 0.3, 1)

        # --- 1-qator: icon + IP + ping + [+] + [i] ---
        row1 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=44, spacing=8
        )

        icon_lbl = Label(
            text=icon, color=th.ACCENT_COLOR,
            font_size=14, bold=True,
            size_hint_x=None, width=40,
            halign="center", valign="middle"
        )

        ip_lbl = Label(
            text=ip, color=th.TEXT_COLOR,
            font_size=18, bold=True,
            halign="left", valign="middle"
        )
        ip_lbl.bind(size=ip_lbl.setter("text_size"))

        ping_lbl = Label(
            text=ping_text, color=ping_color,
            font_size=13, bold=True,
            size_hint_x=None, width=70,
            halign="right", valign="middle"
        )

        copy_btn = Button(
            text="[ + ]",
            size_hint_x=None, width=60,
            background_color=th.ACCENT_COLOR,
            color=th.TEXT_COLOR, font_size=13
        )
        copy_btn.bind(on_release=lambda x: Clipboard.copy(ip))

        info_btn = Button(
            text="[ i ]",
            size_hint_x=None, width=60,
            background_color=(0.15, 0.15, 0.3, 1),
            color=th.TEXT_COLOR, font_size=13
        )
        info_btn.bind(on_release=lambda x: self._show_info(device))

        row1.add_widget(icon_lbl)
        row1.add_widget(ip_lbl)
        row1.add_widget(ping_lbl)
        row1.add_widget(copy_btn)
        row1.add_widget(info_btn)

        # --- 2-qator: device_type + vendor ---
        row2 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=28
        )

        type_lbl = Label(
            text=device_type, color=th.ACCENT_COLOR,
            font_size=13, bold=True,
            halign="left", valign="middle"
        )
        type_lbl.bind(size=type_lbl.setter("text_size"))

        vendor_lbl = Label(
            text=vendor, color=th.SUBTEXT_COLOR,
            font_size=13,
            halign="right", valign="middle"
        )
        vendor_lbl.bind(size=vendor_lbl.setter("text_size"))

        row2.add_widget(type_lbl)
        row2.add_widget(vendor_lbl)

        # --- 3-qator: hostname + OS ---
        row3 = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=24
        )

        host_lbl = Label(
            text=hostname, color=th.SUBTEXT_COLOR,
            font_size=12, halign="left", valign="middle"
        )
        host_lbl.bind(size=host_lbl.setter("text_size"))

        os_lbl = Label(
            text=os_name, color=th.SUBTEXT_COLOR,
            font_size=12, halign="right", valign="middle"
        )
        os_lbl.bind(size=os_lbl.setter("text_size"))

        row3.add_widget(host_lbl)
        row3.add_widget(os_lbl)

        # --- 4-qator: Portlar ---
        port_parts = []
        for port, name in ports.items():
            banner = banners.get(port, "")
            if banner:
                port_parts.append(f"{name}->{banner[:12]}")
            else:
                port_parts.append(name)
        port_text = "  ".join(port_parts) if port_parts else tr("hs_no_ports")

        port_lbl = Label(
            text=port_text, color=th.SUBTEXT_COLOR,
            font_size=11, halign="left", valign="middle",
            size_hint_y=None, height=24
        )
        port_lbl.bind(size=port_lbl.setter("text_size"))

        self.add_widget(row1)
        self.add_widget(row2)
        self.add_widget(row3)
        self.add_widget(port_lbl)

    def _show_info(self, device):
        th = load_theme()
        ip          = device.get("ip", "?")
        mac         = device.get("mac", "—")
        vendor      = device.get("vendor", "Noma'lum")
        hostname    = device.get("hostname", "—")
        os_name     = device.get("os", "—")
        device_type = device.get("device_type", "—")
        ping_info   = device.get("ping", {})
        ports       = device.get("ports", {})
        banners     = device.get("banners", {})

        ping_str = (
            f"{ping_info.get('ms')} ms"
            if ping_info.get("alive") else "offline"
        )

        port_lines = []
        for port, name in ports.items():
            banner = banners.get(port, "")
            if banner:
                port_lines.append(f"  {port}/{name} -> {banner[:25]}")
            else:
                port_lines.append(f"  {port}/{name}")
        port_str = "\n".join(port_lines) if port_lines else "  Yo'q"

        info_text = (
            f"IP:       {ip}\n"
            f"MAC:      {mac}\n"
            f"Tur:      {device_type}\n"
            f"Vendor:   {vendor}\n"
            f"Hostname: {hostname}\n"
            f"OS:       {os_name}\n"
            f"Ping:     {ping_str}\n"
            f"Portlar:\n{port_str}"
        )

        content = BoxLayout(orientation="vertical", spacing=8, padding=12)

        lbl = Label(
            text=info_text, color=th.TEXT_COLOR,
            font_size=13, halign="left", valign="top",
            size_hint_y=1
        )
        lbl.bind(size=lbl.setter("text_size"))

        copy_btn = Button(
            text=tr("hs_copy_ip"),
            size_hint_y=None, height=44,
            background_color=th.ACCENT_COLOR,
            color=th.TEXT_COLOR, font_size=14
        )

        close_btn = Button(
            text=tr("hs_close"),
            size_hint_y=None, height=44,
            background_color=(0.3, 0.1, 0.1, 1),
            color=th.TEXT_COLOR, font_size=14
        )

        content.add_widget(lbl)
        content.add_widget(copy_btn)
        content.add_widget(close_btn)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.88, 0.75),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            background_color=(0.08, 0.08, 0.1, 1),
            separator_height=0
        )

        copy_btn.bind(on_release=lambda x: Clipboard.copy(ip))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
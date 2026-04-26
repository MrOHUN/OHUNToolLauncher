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
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import mainthread
from kivy.uix.popup import Popup

from sb_core import SSHBruteEngine

TOOL_NAME = "SSH Brute"


class SSHBruteUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 6
        self.padding = (8, 8)
        self._popup = None
        self._running = False
        self._tried = 0
        self._total = 0
        self._wordlist = []

        self._build_ui()
        self._load_wordlist()
        self.engine = SSHBruteEngine(
            on_result=self._on_result,
            on_found=self._on_found,
            on_done=self._on_done,
            threads=10
        )

    def _build_ui(self):
        # Title bar
        title_bar = BoxLayout(size_hint_y=None, height=40, spacing=6)
        min_btn = Button(text="[-]", size_hint_x=None, width=40,
                        background_color=(0.15, 0.15, 0.2, 1),
                        color=(0.7, 0.7, 0.7, 1))
        min_btn.bind(on_release=self._minimize)
        title = Label(text=">> SSH Brute",
                     color=(0, 1, 0.53, 1),
                     font_size=15, bold=True)
        close_btn = Button(text="[x]", size_hint_x=None, width=40,
                          background_color=(0.15, 0.15, 0.2, 1),
                          color=(1, 0.3, 0.3, 1))
        close_btn.bind(on_release=self._close)
        title_bar.add_widget(min_btn)
        title_bar.add_widget(title)
        title_bar.add_widget(close_btn)
        self.add_widget(title_bar)

        # Host input
        host_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        host_row.add_widget(Label(text="Host:", size_hint_x=None, width=55,
                                 font_size=13, color=(0.7, 0.7, 0.7, 1)))
        self.host_input = TextInput(
            hint_text="192.168.1.1",
            multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13, padding=(8, 10)
        )
        host_row.add_widget(self.host_input)
        self.add_widget(host_row)

        # Port + Username
        opt_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        opt_row.add_widget(Label(text="Port:", size_hint_x=None, width=40,
                                font_size=12, color=(0.6, 0.6, 0.6, 1)))
        self.port_input = TextInput(
            text="22", multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13, size_hint_x=None, width=55,
            padding=(6, 8)
        )
        opt_row.add_widget(self.port_input)
        opt_row.add_widget(Label(text="User:", size_hint_x=None, width=40,
                                font_size=12, color=(0.6, 0.6, 0.6, 1)))
        self.user_input = TextInput(
            text="root", multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13, padding=(6, 8)
        )
        opt_row.add_widget(self.user_input)
        self.add_widget(opt_row)

        # Threads
        thread_row = BoxLayout(size_hint_y=None, height=36, spacing=6)
        thread_row.add_widget(Label(text="Threads:", size_hint_x=None, width=65,
                                   font_size=12, color=(0.6, 0.6, 0.6, 1)))
        self.threads_input = TextInput(
            text="10", multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13, size_hint_x=None, width=50,
            padding=(6, 8)
        )
        thread_row.add_widget(self.threads_input)
        thread_row.add_widget(Label(
            text="(SSH uchun 10 yetarli)",
            font_size=11, color=(0.4, 0.4, 0.4, 1)
        ))
        self.add_widget(thread_row)

        # START tugmasi
        self.start_btn = Button(
            text="START",
            size_hint_y=None, height=44,
            background_color=(0, 0.8, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=15, bold=True
        )
        self.start_btn.bind(on_release=self._toggle)
        self.add_widget(self.start_btn)

        # Progress
        prog_row = BoxLayout(size_hint_y=None, height=28, spacing=8)
        self.progress = ProgressBar(max=100, value=0)
        self.status_lbl = Label(
            text="Tayyor", font_size=12,
            color=(0.6, 0.6, 0.6, 1),
            size_hint_x=None, width=110
        )
        prog_row.add_widget(self.progress)
        prog_row.add_widget(self.status_lbl)
        self.add_widget(prog_row)

        # Natija label (topilsa)
        self.found_lbl = Label(
            text="",
            font_size=14, bold=True,
            color=(0, 1, 0.4, 1),
            size_hint_y=None, height=36
        )
        self.add_widget(self.found_lbl)

        # Log scroll
        self.scroll = ScrollView()
        self.log_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None, spacing=2
        )
        self.log_box.bind(minimum_height=self.log_box.setter("height"))
        self.scroll.add_widget(self.log_box)
        self.add_widget(self.scroll)

        # Eksport
        export_btn = Button(
            text="Eksport",
            size_hint_y=None, height=40,
            background_color=(0.15, 0.3, 0.15, 1),
            font_size=13
        )
        export_btn.bind(on_release=self._export)
        self.add_widget(export_btn)

    def _load_wordlist(self):
        wl_path = os.path.join(_DIR, "wordlists", "common_pass.txt")
        if os.path.exists(wl_path):
            with open(wl_path, "r", encoding="utf-8") as f:
                self._wordlist = [l.strip() for l in f if l.strip()]
        else:
            self._wordlist = [
                "123456", "password", "admin", "root", "toor",
                "12345678", "qwerty", "abc123", "letmein", "monkey",
                "1234567890", "password1", "iloveyou", "admin123",
                "welcome", "login", "pass", "master", "hello", "test"
            ]
        self._total = len(self._wordlist)

    def _toggle(self, *args):
        if self._running:
            self.engine.stop()
            self._running = False
            self.start_btn.text = "START"
            self.start_btn.background_color = (0, 0.8, 0.4, 1)
        else:
            self._start()

    def _start(self):
        host = self.host_input.text.strip()
        if not host:
            self._show_error("Host kiriting!")
            return

        try:
            port = int(self.port_input.text.strip())
        except ValueError:
            port = 22

        try:
            threads = int(self.threads_input.text.strip())
            threads = max(1, min(threads, 20))
        except ValueError:
            threads = 10

        username = self.user_input.text.strip() or "root"

        self._tried = 0
        self._running = True
        self.found_lbl.text = ""
        self.log_box.clear_widgets()
        self.progress.value = 0
        self.start_btn.text = "STOP"
        self.start_btn.background_color = (0.8, 0.2, 0.2, 1)

        self.engine.threads = threads
        self.engine.start(host, port, username, self._wordlist)

    @mainthread
    def _on_result(self, result):
        self._tried += 1
        if self._total > 0:
            self.progress.value = (self._tried / self._total) * 100

        self.status_lbl.text = f"Sinaldi: {self._tried}"

        color = (0, 1, 0.4, 1) if result["success"] else (0.4, 0.4, 0.4, 1)
        status = "TOPILDI!" if result["success"] else "xato"
        text = f"{result['username']}:{result['password']}  [{status}]"

        lbl = Label(
            text=text,
            font_size=12,
            color=color,
            size_hint_y=None,
            height=28,
            halign="left",
            valign="middle"
        )
        lbl.bind(size=lbl.setter("text_size"))
        self.log_box.add_widget(lbl)

    @mainthread
    def _on_found(self, result):
        self.found_lbl.text = (
            f"TOPILDI: {result['username']}:{result['password']}"
        )
        self.status_lbl.text = "Muvaffaqiyat!"

    @mainthread
    def _on_done(self):
        self._running = False
        self.start_btn.text = "START"
        self.start_btn.background_color = (0, 0.8, 0.4, 1)
        if not self.found_lbl.text:
            self.status_lbl.text = "Topilmadi"
            self.progress.value = 100

    def _export(self, *args):
        from kivy.core.clipboard import Clipboard
        lines = []
        for child in self.log_box.children[::-1]:
            if hasattr(child, "text"):
                lines.append(child.text)
        if lines:
            Clipboard.copy("\n".join(lines))
            self.status_lbl.text = "Clipboard ga nusxalandi!"

    def _show_error(self, msg):
        content = BoxLayout(orientation="vertical", padding=12)
        content.add_widget(Label(text=msg, color=(1, 0.4, 0.4, 1), font_size=13))
        btn = Button(text="OK", size_hint_y=None, height=40,
                    background_color=(0.2, 0.2, 0.3, 1))
        content.add_widget(btn)
        p = Popup(title="", content=content, size_hint=(0.8, 0.35),
                 background_color=(0.08, 0.08, 0.1, 1), separator_height=0)
        btn.bind(on_release=p.dismiss)
        p.open()

    def _minimize(self, *args):
        if self._popup:
            self._popup.dismiss()

    def _close(self, *args):
        self.engine.stop()
        from utils import tool_manager
        tool_manager.close(TOOL_NAME)
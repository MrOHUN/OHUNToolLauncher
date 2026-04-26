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
from kivy.clock import Clock, mainthread
from kivy.uix.popup import Popup

from wf_core import FuzzerEngine

TOOL_NAME = "Web Fuzzer"

STATUS_COLORS = {
    200: (0, 1, 0.4, 1),       # yashil
    301: (0.4, 0.6, 1, 1),     # ko'k
    302: (0.4, 0.6, 1, 1),
    403: (1, 0.8, 0, 1),       # sariq
    500: (1, 0.3, 0.3, 1),     # qizil
}


class ResultCard(BoxLayout):
    def __init__(self, result, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 44
        self.padding = (8, 4)
        self.spacing = 8

        status = result["status"]
        color = STATUS_COLORS.get(status, (0.6, 0.6, 0.6, 1))

        status_lbl = Label(
            text=f"[{status}]",
            color=color,
            size_hint_x=None,
            width=60,
            font_size=13,
            halign="left",
            valign="middle"
        )
        status_lbl.bind(size=status_lbl.setter("text_size"))

        path_lbl = Label(
            text=result["path"],
            color=(0.9, 0.9, 0.9, 1),
            font_size=13,
            halign="left",
            valign="middle"
        )
        path_lbl.bind(size=path_lbl.setter("text_size"))

        size_kb = result["size"] / 1024
        size_lbl = Label(
            text=f"{size_kb:.1f}kb",
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=None,
            width=55,
            font_size=12,
            halign="right",
            valign="middle"
        )
        size_lbl.bind(size=size_lbl.setter("text_size"))

        info_btn = Button(
            text="[i]",
            size_hint_x=None,
            width=36,
            background_color=(0.15, 0.15, 0.2, 1),
            color=(0.4, 0.8, 1, 1),
            font_size=12
        )
        info_btn.bind(on_release=lambda x: self._show_info(result))

        self.add_widget(status_lbl)
        self.add_widget(path_lbl)
        self.add_widget(size_lbl)
        self.add_widget(info_btn)

    def _show_info(self, result):
        size_kb = result["size"] / 1024
        content = BoxLayout(orientation="vertical", padding=12, spacing=8)
        content.add_widget(Label(text=f"URL: {result['url']}", font_size=12, color=(0.8, 0.8, 0.8, 1)))
        content.add_widget(Label(text=f"Status: {result['status']}", font_size=12))
        content.add_widget(Label(text=f"Hajm: {size_kb:.2f} kb", font_size=12))
        close_btn = Button(text="Yopish", size_hint_y=None, height=40,
                           background_color=(0.2, 0.2, 0.3, 1))
        content.add_widget(close_btn)
        p = Popup(title="", content=content,
                  size_hint=(0.85, 0.45),
                  background_color=(0.08, 0.08, 0.1, 1),
                  separator_height=0)
        close_btn.bind(on_release=p.dismiss)
        p.open()


class WebFuzzerUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 6
        self.padding = (8, 8)
        self._popup = None
        self._fuzzing = False
        self._results = []
        self._total = 0
        self._done_count = 0
        self._wordlist = []

        self._build_ui()
        self._load_wordlist()
        self.engine = FuzzerEngine(
            on_result=self._on_result,
            on_done=self._on_done,
            threads=50
        )

    def _build_ui(self):
        from utils import tool_manager as tm

        # Title bar
        title_bar = BoxLayout(size_hint_y=None, height=40, spacing=6)
        min_btn = Button(text="[-]", size_hint_x=None, width=40,
                         background_color=(0.15, 0.15, 0.2, 1),
                         color=(0.7, 0.7, 0.7, 1))
        min_btn.bind(on_release=self._minimize)
        title = Label(text=">> Web Fuzzer", color=(1, 0.42, 0.21, 1),
                      font_size=15, bold=True)
        close_btn = Button(text="[x]", size_hint_x=None, width=40,
                           background_color=(0.15, 0.15, 0.2, 1),
                           color=(1, 0.3, 0.3, 1))
        close_btn.bind(on_release=self._close)
        title_bar.add_widget(min_btn)
        title_bar.add_widget(title)
        title_bar.add_widget(close_btn)
        self.add_widget(title_bar)

        # URL input
        url_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        url_row.add_widget(Label(text="URL:", size_hint_x=None, width=40,
                                 font_size=13, color=(0.7, 0.7, 0.7, 1)))
        self.url_input = TextInput(
            hint_text="https://example.com",
            multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13,
            padding=(8, 10)
        )
        url_row.add_widget(self.url_input)
        self.add_widget(url_row)

        # Threads + filter qatori
        opt_row = BoxLayout(size_hint_y=None, height=36, spacing=6)
        opt_row.add_widget(Label(text="Threads:", size_hint_x=None, width=65,
                                 font_size=12, color=(0.6, 0.6, 0.6, 1)))
        self.threads_input = TextInput(
            text="50", multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13, size_hint_x=None, width=50,
            padding=(6, 8)
        )
        opt_row.add_widget(self.threads_input)
        opt_row.add_widget(Label(text="Filter:", size_hint_x=None, width=45,
                                 font_size=12, color=(0.6, 0.6, 0.6, 1)))
        self.filter_input = TextInput(
            text="200,301,403", multiline=False,
            background_color=(0.12, 0.12, 0.16, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size=13, padding=(6, 8)
        )
        opt_row.add_widget(self.filter_input)
        self.add_widget(opt_row)

        # START / STOP tugmasi
        self.start_btn = Button(
            text="START",
            size_hint_y=None, height=44,
            background_color=(1, 0.42, 0.21, 1),
            color=(1, 1, 1, 1),
            font_size=15, bold=True
        )
        self.start_btn.bind(on_release=self._toggle)
        self.add_widget(self.start_btn)

        # Progress
        prog_row = BoxLayout(size_hint_y=None, height=28, spacing=8)
        self.progress = ProgressBar(max=100, value=0)
        self.status_lbl = Label(text="Tayyor", font_size=12,
                                color=(0.6, 0.6, 0.6, 1),
                                size_hint_x=None, width=100)
        prog_row.add_widget(self.progress)
        prog_row.add_widget(self.status_lbl)
        self.add_widget(prog_row)

        # Natijalar
        self.scroll = ScrollView()
        self.results_box = BoxLayout(orientation="vertical",
                                     size_hint_y=None, spacing=2)
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        self.scroll.add_widget(self.results_box)
        self.add_widget(self.scroll)

        # Pastki tugmalar
        bottom_row = BoxLayout(size_hint_y=None, height=40, spacing=6)
        export_btn = Button(text="Eksport", background_color=(0.15, 0.3, 0.15, 1),
                            font_size=13)
        export_btn.bind(on_release=self._export)
        clear_btn = Button(text="Tozalash", background_color=(0.3, 0.1, 0.1, 1),
                           font_size=13)
        clear_btn.bind(on_release=self._clear)
        bottom_row.add_widget(export_btn)
        bottom_row.add_widget(clear_btn)
        self.add_widget(bottom_row)

    def _load_wordlist(self):
        wl_path = os.path.join(_DIR, "wordlists", "common.txt")
        if os.path.exists(wl_path):
            with open(wl_path, "r", encoding="utf-8") as f:
                self._wordlist = [l.strip() for l in f if l.strip()]
        else:
            # Minimal default wordlist
            self._wordlist = [
                "admin", "login", "backup", "config", "test",
                "api", "uploads", "images", "static", "js",
                "css", "robots.txt", "sitemap.xml", ".env",
                "wp-admin", "phpmyadmin", "db", "database",
                "old", "new", "dev", "staging", "panel"
            ]
        self._total = len(self._wordlist)

    def _toggle(self, *args):
        if self._fuzzing:
            self.engine.stop()
            self._fuzzing = False
            self.start_btn.text = "START"
            self.start_btn.background_color = (1, 0.42, 0.21, 1)
        else:
            self._start()

    def _start(self):
        url = self.url_input.text.strip()
        if not url.startswith("http"):
            self._show_error("URL http:// yoki https:// bilan boshlanishi kerak")
            return

        try:
            threads = int(self.threads_input.text.strip())
            threads = max(1, min(threads, 100))
        except ValueError:
            threads = 50

        self._results = []
        self._done_count = 0
        self.results_box.clear_widgets()
        self.progress.value = 0
        self._fuzzing = True
        self.start_btn.text = "STOP"
        self.start_btn.background_color = (0.8, 0.2, 0.2, 1)

        self.engine.threads = threads
        self.engine.start(url, self._wordlist)

    @mainthread
    def _on_result(self, result):
        self._done_count += 1
        if self._total > 0:
            self.progress.value = (self._done_count / self._total) * 100

        # Filter tekshiruvi
        try:
            filters = [int(x.strip()) for x in self.filter_input.text.split(",")]
        except Exception:
            filters = [200, 301, 403]

        if result["status"] not in filters:
            return

        self._results.append(result)
        count = len(self._results)
        self.status_lbl.text = f"Topildi: {count}"
        card = ResultCard(result)
        self.results_box.add_widget(card)

    @mainthread
    def _on_done(self):
        self._fuzzing = False
        self.start_btn.text = "START"
        self.start_btn.background_color = (1, 0.42, 0.21, 1)
        self.status_lbl.text = f"Tugadi: {len(self._results)} ta"
        self.progress.value = 100

    def _export(self, *args):
        if not self._results:
            return
        from kivy.core.clipboard import Clipboard
        lines = [f"[{r['status']}] {r['url']} ({r['size']/1024:.1f}kb)"
                 for r in self._results]
        Clipboard.copy("\n".join(lines))
        self.status_lbl.text = "Clipboard ga nusxalandi!"

    def _clear(self, *args):
        self._results = []
        self.results_box.clear_widgets()
        self.progress.value = 0
        self.status_lbl.text = "Tayyor"

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
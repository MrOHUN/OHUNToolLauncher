import os
import io
import sys
import importlib.util

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

from utils.widgets import RoundedButton
from utils.helpers import hex_rgb


class OutputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tool_name = ""
        self._main_path = ""
        self._color_hex = "#22cc77"
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical")

        # HEADER
        header = BoxLayout(size_hint=(1, None), height=56, padding=[16, 8])
        with header.canvas.before:
            Color(0.15, 0.15, 0.17, 1)
            self._hrect = RoundedRectangle(size=header.size, pos=header.pos)
        header.bind(
            size=lambda w, v: setattr(self._hrect, 'size', v),
            pos=lambda w, v: setattr(self._hrect, 'pos', v)
        )
        self.title_lbl = Label(
            text="Natija", font_size=18, bold=True,
            color=(1, 1, 1, 1), halign="left", valign="middle",
            size_hint=(1, 1)
        )
        self.title_lbl.bind(size=self.title_lbl.setter("text_size"))
        header.add_widget(self.title_lbl)

        # OUTPUT scroll
        scroll = ScrollView(size_hint=(1, 1))
        self.out_label = Label(
            text="", font_size=14,
            color=(0.85, 0.95, 0.85, 1),
            halign="left", valign="top",
            size_hint=(1, None),
            padding=[16, 16], markup=True
        )
        self.out_label.bind(
            texture_size=lambda w, v: setattr(w, 'height', v[1] + 32),
            width=lambda w, v: setattr(w, 'text_size', (v, None))
        )
        scroll.add_widget(self.out_label)

        # FOOTER
        footer = BoxLayout(size_hint=(1, None), height=74, padding=[16, 12], spacing=10)
        with footer.canvas.before:
            Color(0.15, 0.15, 0.17, 1)
            self._frect = RoundedRectangle(size=footer.size, pos=footer.pos)
        footer.bind(
            size=lambda w, v: setattr(self._frect, 'size', v),
            pos=lambda w, v: setattr(self._frect, 'pos', v)
        )

        back_btn = RoundedButton(
            bg_color=(0.2, 0.22, 0.28, 1), text="< Orqaga",
            font_size=15, size_hint=(0.38, 1), color=(0.6, 0.8, 1, 1)
        )
        back_btn.bind(on_press=self._go_back)

        self.rerun_btn = RoundedButton(
            bg_color=(0.1, 0.45, 0.25, 1), text=">> Qayta",
            font_size=15, size_hint=(0.62, 1), color=(1, 1, 1, 1)
        )
        self.rerun_btn.bind(on_press=self._rerun)

        footer.add_widget(back_btn)
        footer.add_widget(self.rerun_btn)

        root.add_widget(header)
        root.add_widget(scroll)
        root.add_widget(footer)
        self.add_widget(root)

    def load(self, tool_name, main_path, color_hex="#22cc77"):
        self._tool_name = tool_name
        self._main_path = main_path
        self._color_hex = color_hex
        r, g, b = hex_rgb(color_hex)
        self.rerun_btn.bg_color = (r * 0.65, g * 0.65, b * 0.65, 1)
        self.rerun_btn._draw()
        self._execute()

    def _execute(self):
        self.title_lbl.text = f">> {self._tool_name}"
        self.out_label.text = "[color=888888]Ishga tushirilmoqda...[/color]"

        if not os.path.exists(self._main_path):
            self.out_label.text = "[color=ff4444]XATO: main.py topilmadi![/color]"
            return
        try:
            old_out = sys.stdout
            sys.stdout = buf = io.StringIO()
            sys.modules.pop(self._tool_name, None)

            spec = importlib.util.spec_from_file_location(self._tool_name, self._main_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if hasattr(mod, "open_ui"):
                sys.stdout = old_out
                mod.open_ui()
                self.out_label.text = "[color=888888]Tool o'z oynasida ishlayapti.[/color]"
                return

            if hasattr(mod, "run"):
                mod.run()

            sys.stdout = old_out
            out = buf.getvalue().strip()

            if out:
                lines = out.split("\n")
                self.out_label.text = "\n".join(
                    f"[color=55ff88]>[/color]  {line}" for line in lines
                )
            else:
                self.out_label.text = "[color=888888]Tool ishladi, hech narsa chiqarmadi.[/color]"

        except Exception as e:
            sys.stdout = old_out
            self.out_label.text = f"[color=ff4444]XATO:[/color]\n\n{str(e)}"

    def _rerun(self, *args):
        self._execute()

    def _go_back(self, *args):
        self.manager.current = "home"

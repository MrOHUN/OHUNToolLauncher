import threading
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import tool_api

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

from uf_sites import SITES
from uf_checker import check_site


class ResultRow(BoxLayout):
    def __init__(self, site_name, url, found, debug_label, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, None),
            height=70,
            spacing=6,
            padding=[4, 4],
            **kwargs
        )
        self._url = url
        self._debug = debug_label

        status_text = "[color=33ff88][FOUND][/color]" if found else "[color=444444][----][/color]"
        status = Label(
            text=status_text, markup=True,
            font_size=13,
            size_hint=(None, 1), width=62,
            halign="center", valign="middle"
        )
        status.bind(size=status.setter("text_size"))

        if found:
            info = Label(
                text=f"[b]{site_name}[/b]\n[color=4a90d9][size=12]{url}[/size][/color]",
                markup=True, font_size=16,
                halign="left", valign="middle",
                size_hint=(1, 1)
            )
            info.bind(size=info.setter("text_size"))

            copy_btn = Button(
                text="Copy",
                font_size=12,
                size_hint=(None, None),
                width=64, height=36,
                pos_hint={"center_y": 0.5},
                background_color=(0, 0, 0, 0),
                background_normal="",
                color=(0.3, 0.9, 0.6, 1)
            )
            with copy_btn.canvas.before:
                Color(0.08, 0.3, 0.15, 1)
                self._cr = RoundedRectangle(size=copy_btn.size, pos=copy_btn.pos, radius=[8])
            copy_btn.bind(
                size=lambda w, v: setattr(self._cr, 'size', v),
                pos=lambda w, v: setattr(self._cr, 'pos', v)
            )

            url_copy = url
            def do_copy(instance, u=url_copy):
                try:
                    Clipboard.copy(u)
                    self._debug.text = f"[color=33ff88]Copied: {u}[/color]"
                except Exception as e:
                    self._debug.text = f"[color=ff4444]Copy xato: {e}[/color]"

            copy_btn.bind(on_press=do_copy)

            with self.canvas.before:
                Color(0.04, 0.18, 0.09, 1)
                self._r = RoundedRectangle(size=self.size, pos=self.pos, radius=[8])
            self.bind(
                size=lambda w, v: setattr(self._r, 'size', v),
                pos=lambda w, v: setattr(self._r, 'pos', v)
            )

            self.add_widget(status)
            self.add_widget(info)
            self.add_widget(copy_btn)
        else:
            info = Label(
                text=f"[color=404040]{site_name}[/color]",
                markup=True, font_size=15,
                halign="left", valign="middle",
                size_hint=(1, 1)
            )
            info.bind(size=info.setter("text_size"))
            self.add_widget(status)
            self.add_widget(info)


class UsernameFinderUI(BoxLayout):
    def __init__(self, **kwargs):
        # Asosiy padding va spacing sozlandi
        super().__init__(orientation="vertical", spacing=6, padding=[8, 10, 8, 6], **kwargs)
        self._found_count = 0
        self._checked_count = 0
        self._searching = False
        self._popup = None
        self._build()

    def _build(self):
        # ── TITLE ROW: Kattalashtirilgan tugmalar bilan ──
        title_row = BoxLayout(size_hint=(1, None), height=48, spacing=8)

        min_btn = Button(
            text="-", font_size=20,
            size_hint=(None, 1), width=48,
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=(0.7, 0.7, 0.7, 1)
        )
        with min_btn.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self._mrect = RoundedRectangle(size=min_btn.size, pos=min_btn.pos, radius=[8])
        min_btn.bind(
            size=lambda w, v: setattr(self._mrect, 'size', v),
            pos=lambda w, v: setattr(self._mrect, 'pos', v)
        )
        min_btn.bind(on_press=self._minimize)

        title = Label(
            text=">> Username Finder",
            font_size=18, bold=True,
            color=(0.3, 0.9, 0.6, 1),
            size_hint=(1, 1),
            halign="left", valign="middle"
        )
        title.bind(size=title.setter("text_size"))

        close_btn = Button(
            text="x", font_size=18,
            size_hint=(None, 1), width=48,
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=(0.9, 0.3, 0.3, 1)
        )
        with close_btn.canvas.before:
            Color(0.25, 0.08, 0.08, 1)
            self._crect2 = RoundedRectangle(size=close_btn.size, pos=close_btn.pos, radius=[8])
        close_btn.bind(
            size=lambda w, v: setattr(self._crect2, 'size', v),
            pos=lambda w, v: setattr(self._crect2, 'pos', v)
        )
        close_btn.bind(on_press=self._close)

        title_row.add_widget(min_btn)
        title_row.add_widget(title)
        title_row.add_widget(close_btn)

        # ── INPUT ROW ──
        row = BoxLayout(size_hint=(1, None), height=46, spacing=8)
        self.txt = TextInput(
            hint_text="username...",
            multiline=False, font_size=15,
            background_color=(0.15, 0.15, 0.18, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0.3, 0.9, 0.6, 1),
            size_hint=(0.6, 1)
        )
        self.txt.bind(on_text_validate=self._start)

        self.clear_btn = Button(
            text="X", font_size=14,
            size_hint=(0.1, 1),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=(0.9, 0.3, 0.3, 1)
        )
        with self.clear_btn.canvas.before:
            Color(0.25, 0.08, 0.08, 1)
            self._crect = RoundedRectangle(size=self.clear_btn.size, pos=self.clear_btn.pos, radius=[12])
        self.clear_btn.bind(
            size=lambda w, v: setattr(self._crect, 'size', v),
            pos=lambda w, v: setattr(self._crect, 'pos', v)
        )
        self.clear_btn.bind(on_press=self._clear_input)

        self.btn = Button(
            text="Qidirish", font_size=14,
            size_hint=(0.3, 1),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        with self.btn.canvas.before:
            Color(0.1, 0.55, 0.3, 1)
            self._brect = RoundedRectangle(size=self.btn.size, pos=self.btn.pos, radius=[12])
        self.btn.bind(
            size=lambda w, v: setattr(self._brect, 'size', v),
            pos=lambda w, v: setattr(self._brect, 'pos', v)
        )
        self.btn.bind(on_press=self._start)

        row.add_widget(self.txt)
        row.add_widget(self.clear_btn)
        row.add_widget(self.btn)

        # ── STATUS & DEBUG ──
        self.stat = Label(
            text="", font_size=12,
            color=(0.5, 0.6, 0.5, 1),
            size_hint=(1, None), height=20,
            halign="left", valign="middle",
            markup=True
        )
        self.stat.bind(size=self.stat.setter("text_size"))

        self.debug = Label(
            text="", font_size=11, markup=True,
            size_hint=(1, None), height=22,
            halign="left", valign="middle",
            color=(0.7, 0.7, 0.7, 1)
        )
        self.debug.bind(size=self.debug.setter("text_size"))

        # ── RESULTS LIST ──
        self.scroll = ScrollView(size_hint=(1, 1))
        self.box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            spacing=2, padding=[0, 4]
        )
        self.box.bind(minimum_height=self.box.setter("height"))

        hint = Label(
            text="[color=444444]Username kiriting va Qidirish bosing...[/color]",
            markup=True, font_size=14,
            size_hint=(1, None), height=40,
            halign="center", valign="middle"
        )
        hint.bind(size=hint.setter("text_size"))
        self.box.add_widget(hint)
        self.scroll.add_widget(self.box)

        # UI qo'shish tartibi
        self.add_widget(title_row)
        self.add_widget(row)
        self.add_widget(self.stat)
        self.add_widget(self.debug)
        self.add_widget(self.scroll)

    def _minimize(self, *args):
        # Kuchaytirilgan minimize: avval _popup'ni tekshiradi, keyin parent chaindan qidiradi
        if hasattr(self, '_popup') and self._popup:
            self._popup.dismiss()
        else:
            p = self.parent
            while p:
                if hasattr(p, 'dismiss'):
                    p.dismiss()
                    break
                p = p.parent

    def _close(self, *args):
        from utils import tool_manager
        tool_manager.close("Username Finder")

    def _clear_input(self, *args):
        self.txt.text = ""
        self.debug.text = ""

    def _start(self, *args):
        if self._searching:
            return
        
        username = self.txt.text.strip()
        if not username:
            return
            
        self._searching = True
        self.box.clear_widgets()
        self._found_count = 0
        self._checked_count = 0
        self.debug.text = ""
        self.stat.text = f"Qidirilmoqda: {username}  |  0/{len(SITES)}"
        self.btn.text = "..."
        
        with self.btn.canvas.before:
            Color(0.25, 0.25, 0.25, 1)
            self._brect = RoundedRectangle(size=self.btn.size, pos=self.btn.pos, radius=[12])
            
        threading.Thread(target=self._search, args=(username,), daemon=True).start()

    def _search(self, username):
        for site in SITES:
            try:
                found, url = check_site(site, username)
            except Exception as e:
                found, url = False, ""
                Clock.schedule_once(
                    lambda dt, err=str(e), sn=site["name"]: setattr(
                        self.debug, 'text', f"[color=ff4444]Xato [{sn}]: {err}[/color]"
                    )
                )
            self._checked_count += 1
            if found:
                self._found_count += 1
            Clock.schedule_once(
                lambda dt, s=site["name"], u=url, f=found: self._add_row(s, u, f)
            )
        Clock.schedule_once(lambda dt: self._done())

    def _add_row(self, site_name, url, found):
        self.box.add_widget(ResultRow(site_name, url, found, self.debug))
        self.stat.text = (
            f"Tekshirildi: {self._checked_count}/{len(SITES)}  "
            f"|  [color=33ff88]Topildi: {self._found_count}[/color]"
        )

    def _done(self):
        self._searching = False
        username = self.txt.text.strip()

        try:
            history = tool_api.load_tool_data(__file__, "history.json", default=[])
            if username and username not in history:
                history.append(username)
                tool_api.save_tool_data(__file__, "history.json", history)
            tool_api.notify(f"Qidiruv tugadi: {username} — {self._found_count} ta topildi")
            self.debug.text = f"[color=33ff88]Saqlandi: {history}[/color]"
        except Exception as e:
            self.debug.text = f"[color=ff4444]tool_api xato: {e}[/color]"

        self.btn.text = "Qidirish"
        with self.btn.canvas.before:
            Color(0.1, 0.55, 0.3, 1)
            self._brect = RoundedRectangle(size=self.btn.size, pos=self.btn.pos, radius=[12])
            
        sep = Label(
            text=f"[color=555555]── Tugadi: {self._found_count} ta topildi ──[/color]",
            markup=True, font_size=12,
            size_hint=(1, None), height=30,
            halign="center", valign="middle"
        )
        sep.bind(size=sep.setter("text_size"))
        self.box.add_widget(sep)

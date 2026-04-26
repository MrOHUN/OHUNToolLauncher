from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView  # Qo'shildi
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard   # Qo'shildi

from utils.widgets import RoundedButton
from utils.helpers import load_theme, t as tr

# Matnlarni alohida modullardan import qilish
from .brain_author   import get_text as author_text
from .brain_readme   import get_text as readme_text
from .brain_devguide import get_text as devguide_text

def open_brain():
    t = load_theme()

    content = BoxLayout(orientation="vertical", spacing=12, padding=[14, 14])

    scroll = ScrollView(size_hint=(1, 1))
    inner = BoxLayout(orientation="vertical", size_hint=(1, None), spacing=12)
    inner.bind(minimum_height=inner.setter("height"))

    # --- Muallif bo'limi ---
    author_btn = RoundedButton(
        bg_color=t.ACCENT_COLOR,
        text=tr("brain_author"),
        font_size=15, size_hint=(1, None), height=52,
        color=t.TEXT_COLOR
    )
    author_btn.bind(on_press=lambda x: _show_page(tr("brain_author"), author_text()))

    # --- Readme bo'limi ---
    readme_btn = RoundedButton(
        bg_color=t.ACCENT_COLOR,
        text=tr("brain_readme"),
        font_size=15, size_hint=(1, None), height=52,
        color=t.TEXT_COLOR
    )
    readme_btn.bind(on_press=lambda x: _show_page(tr("brain_readme"), readme_text()))

    # --- Dev Guide bo'limi ---
    devguide_btn = RoundedButton(
        bg_color=t.ACCENT_COLOR,
        text=tr("brain_devguide"),
        font_size=15, size_hint=(1, None), height=52,
        color=t.TEXT_COLOR
    )
    devguide_btn.bind(on_press=lambda x: _show_page(tr("brain_devguide"), devguide_text()))

    inner.add_widget(author_btn)
    inner.add_widget(readme_btn)
    inner.add_widget(devguide_btn)
    scroll.add_widget(inner)
    content.add_widget(scroll)

    popup = Popup(
        title=tr("brain"),
        content=content,
        size_hint=(0.95, 0.75),
        background_color=(0.1, 0.1, 0.12, 1),
        separator_height=1
    )
    popup.open()


def _show_page(title, text):
    # Asosiy konteyner (padding=0 qilib, ichki elementlar bilan boshqariladi)
    box = BoxLayout(orientation="vertical", spacing=0, padding=[0, 0])

    # Scroll + Label (Matn uzun bo'lsa pastga tushish uchun)
    scroll = ScrollView(size_hint=(1, 1))
    lbl = Label(
        text=text if text else "[ coming soon ]",
        font_size=14,
        color=(0.88, 0.88, 0.88, 1),
        halign="left", valign="top",
        size_hint=(1, None),
        padding=[14, 14],
        markup=True  # Agar matn ichida [b] yoki [color] ishlatilsa ishlaydi
    )
    
    # Label o'lchamini matn miqdoriga qarab moslashtirish (Dinamik balandlik)
    lbl.bind(width=lambda w, v: setattr(w, 'text_size', (v - 28, None)))
    lbl.bind(texture_size=lambda w, v: setattr(w, 'height', v[1] + 28))
    
    scroll.add_widget(lbl)

    # Copy All tugma
    copy_btn = RoundedButton(
        text=tr("copy_all"),
        bg_color=(0.15, 0.25, 0.35, 1),
        color=(0.5, 0.85, 1, 1),
        font_size=13,
        size_hint=(1, None), height=48
    )
    copy_btn.bind(on_press=lambda x: Clipboard.copy(lbl.text))

    box.add_widget(scroll)
    box.add_widget(copy_btn)

    p = Popup(
        title=title,
        content=box,
        size_hint=(0.95, 0.85),
        background_color=(0.08, 0.08, 0.10, 1),
        separator_height=1
    )
    p.open()

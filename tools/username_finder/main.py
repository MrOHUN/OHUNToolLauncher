import os, sys

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from kivy.uix.popup import Popup
from uf_ui import UsernameFinderUI


def open_ui():
    content = UsernameFinderUI(padding=[10, 8])
    popup = Popup(
        title="",
        content=content,
        size_hint=(0.97, 0.94),
        background_color=(0.08, 0.08, 0.1, 1),
        separator_height=0
    )
    popup.open()


def run():
    print("Username Finder — open_ui() orqali ishga tushiring.")

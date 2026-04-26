# net_sniffer/main.py

import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))

if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from kivy.uix.popup import Popup
from ns_ui import NetSnifferUI

TOOL_NAME = "Net Sniffer"


def open_ui():
    try:
        from utils import tool_manager

        if tool_manager.is_active(TOOL_NAME):
            tool_manager.focus(TOOL_NAME)
            return

        content = NetSnifferUI()

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.97, 0.94),
            background_color=(0.08, 0.08, 0.1, 1),
            separator_height=0
        )

        content._popup = popup
        tool_manager.register(TOOL_NAME, content, popup)
        popup.open()

    except Exception as e:
        import traceback
        print("Error opening Net Sniffer UI:")
        print(traceback.format_exc())


def run():
    print("Net Sniffer — open_ui() orqali ishga tushiring.")


if __name__ == "__main__":
    run()

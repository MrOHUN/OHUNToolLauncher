# host_scanner/main.py

import os
import sys

# Tool ichidagi modullarni va asosiy loyiha modullarini topish uchun path sozlamalari
_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(os.path.dirname(_DIR))

if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from kivy.uix.popup import Popup
from hs_ui import HostScannerUI

TOOL_NAME = "Host Scanner"


def open_ui():
    try:
        from utils import tool_manager

        if tool_manager.is_active(TOOL_NAME):
            tool_manager.focus(TOOL_NAME)
            return

        content = HostScannerUI()

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
        # Xatolik yuz bersa, logda to'liq ko'rsatiladi (debugging uchun qulay)
        print("Error opening Host Scanner UI:")
        print(traceback.format_exc())


def run():
    print("Host Scanner — open_ui() orqali ishga tushiring.")


if __name__ == "__main__":
    run()

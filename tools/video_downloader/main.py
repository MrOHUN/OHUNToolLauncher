import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from kivy.uix.popup import Popup
from vd_ui import VideoDownloaderUI

TOOL_NAME = "Video Downloader"

def open_ui():
    from utils import tool_manager
    from utils.helpers import load_theme

    if tool_manager.is_active(TOOL_NAME):
        tool_manager.focus(TOOL_NAME)
        return

    t = load_theme()
    content = VideoDownloaderUI()

    # Popup konfiguratsiyasi yangilangan rang o'zgaruvchilari bilan
    popup = Popup(
        title="⬇ Video Downloader",
        content=content,
        size_hint=(0.95, 0.85),
        background_color=t.BG_COLOR,      # Yangilandi: BG -> BG_COLOR
        title_color=t.ACCENT_COLOR,       # Yangilandi: ACCENT -> ACCENT_COLOR
        separator_color=t.ACCENT_COLOR    # Yangilandi: ACCENT -> ACCENT_COLOR
    )

    content._popup = popup
    tool_manager.register(TOOL_NAME, content, popup)
    popup.open()

def run():
    print("Video Downloader — open_ui() orqali ishga tushiring.")

if __name__ == "__main__":
    run()

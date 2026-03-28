import os
import sys

# Loyiha papkasini sys.path ga qo'shish
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from kivy.uix.popup import Popup
from uf_ui import UsernameFinderUI

# Tool identifikatori
TOOL_NAME = "Username Finder"


def open_ui():
    """
    Asbob interfeysini Popup ichida ochadi va tool_manager'da ro'yxatdan o'tkazadi.
    """
    from utils import tool_manager

    # 1. Agar asbob allaqachon ochiq bo'lsa, uni shunchaki focus qilamiz
    if tool_manager.is_active(TOOL_NAME):
        tool_manager.focus(TOOL_NAME)
        return

    # 2. UI kontentini yaratamiz
    content = UsernameFinderUI()
    
    # 3. Popup oynasini sozlaymiz
    popup = Popup(
        title="",
        content=content,
        size_hint=(0.97, 0.94),
        background_color=(0.08, 0.08, 0.1, 1),
        separator_height=0
    )

    # Popup obyekti widget ichida minimize funksiyasi uchun kerak
    content._popup = popup

    # 4. tool_manager'ga yangi asbobni ro'yxatdan o'tkazamiz
    tool_manager.register(TOOL_NAME, content, popup)

    # 5. unregister faqat uf_ui.py dagi _close (x tugmasi) orqali bajariladi
    # Shuning uchun bu yerda popup.bind(on_dismiss...) qatori olib tashlandi

    # 6. Oynani ochamiz
    popup.open()


def run():
    """
    Terminal yoki tashqi buyruq orqali ishga tushirish uchun yordamchi funksiya.
    """
    print("Username Finder — open_ui() orqali ishga tushiring.")


if __name__ == "__main__":
    run()

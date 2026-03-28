from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock # Yangi qo'shildi

# Keshni tozalash va yangilash uchun helperni import qilish
from utils.helpers import clear_cache

# Oyna fonining standart rangini sozlash
Window.clearcolor = (0.1, 0.1, 0.12, 1)

from screens.home import HomeScreen
from screens.output import OutputScreen
from screens.settings import SettingsScreen


class ToolLauncherApp(App):
    def build(self):
        """
        Ilovaning asosiy vidjetlar ierarxiyasini (ScreenManager) quradi.
        """
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(OutputScreen(name="output"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm

    def restart_ui(self):
        """
        UI restartini navbatga qo'yadi.
        """
        clear_cache()
        # Keyingi kadrda (next frame) UI'ni qayta qurishni rejalashtiramiz
        Clock.schedule_once(self._do_restart)

    def _do_restart(self, dt):
        """
        Haqiqiy UI yangilash jarayoni shu yerda bajariladi.
        """
        # 1. Root vidjetni (asosiy oyna) tozalaymiz
        self.root.clear_widgets()
        
        # 2. Yangi ScreenManager yaratamiz
        new_sm = ScreenManager()
        
        # 3. Screen'larni yangidan qo'shamiz (ular yangi til va temani helpers orqali o'qiydi)
        new_sm.add_widget(HomeScreen(name="home"))
        new_sm.add_widget(OutputScreen(name="output"))
        new_sm.add_widget(SettingsScreen(name="settings"))
        
        # 4. Foydalanuvchini yana sozlamalar oynasida qoldiramiz
        new_sm.current = "settings"
        
        # 5. Root vidjetga yangi ScreenManager-ni ulaymiz
        self.root.add_widget(new_sm)
        print("UI successfully refreshed via Clock schedule.")


if __name__ == "__main__":
    ToolLauncherApp().run()

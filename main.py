from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

Window.clearcolor = (0.1, 0.1, 0.12, 1)

from screens.home import HomeScreen
from screens.output import OutputScreen
from screens.settings import SettingsScreen


class ToolLauncherApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(OutputScreen(name="output"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == "__main__":
    ToolLauncherApp().run()

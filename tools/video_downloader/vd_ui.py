from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from utils.helpers import load_theme
from vd_logic import download_file

class VideoDownloaderUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        t = load_theme()
        
        self.orientation = "vertical"
        self.padding = 16
        self.spacing = 12
        
        # URL input - Maxsus fon va yangilangan ranglar
        self.url_input = TextInput(
            hint_text="URL ni shu yerga yozing...",
            multiline=False,
            size_hint_y=None,
            height=48,
            background_color=(0.1, 0.1, 0.2, 1), # Maxsus to'q ko'k fon
            foreground_color=t.TEXT_COLOR,       # Yangilandi
            cursor_color=t.ACCENT_COLOR,        # Yangilandi
            font_size=14
        )
        self.add_widget(self.url_input)
        
        # Yuklab olish tugmasi - Yangilangan ranglar
        self.btn = Button(
            text="⬇ Yuklab olish",
            size_hint_y=None,
            height=48,
            background_color=t.ACCENT_COLOR,     # Yangilandi
            color=t.TEXT_COLOR,                  # Yangilandi
            font_size=15
        )
        self.btn.bind(on_press=self._start)
        self.add_widget(self.btn)
        
        # Progress bar
        self.progress = ProgressBar(
            max=100, 
            value=0,
            size_hint_y=None, 
            height=20
        )
        self.add_widget(self.progress)
        
        # Status label - Yangilangan rang
        self.status = Label(
            text="URL yozing va yuklab oling",
            color=t.TEXT_COLOR,                  # Yangilandi
            font_size=13,
            size_hint_y=None, 
            height=40
        )
        self.add_widget(self.status)
        
        # Bo'sh joy (Layoutni tepaga surish uchun)
        self.add_widget(BoxLayout())
    
    def _start(self, *a):
        url = self.url_input.text.strip()
        if not url:
            self.status.text = "⚠ URL bo'sh!"
            return
        
        self.btn.disabled = True
        self.progress.value = 0
        self.status.text = "⏳ Yuklanmoqda..."
        
        download_file(
            url,
            on_progress=self._on_progress,
            on_done=self._on_done,
            on_error=self._on_error
        )
    
    def _on_progress(self, percent, downloaded, total):
        def _upd(*a):
            self.progress.value = percent
            mb_done = downloaded / 1024 / 1024
            mb_total = total / 1024 / 1024
            self.status.text = f"⬇ {mb_done:.1f} / {mb_total:.1f} MB"
        Clock.schedule_once(_upd)
    
    def _on_done(self, path):
        def _upd(*a):
            self.progress.value = 100
            self.status.text = f"✅ Saqlandi: {path}"
            self.btn.disabled = False
        Clock.schedule_once(_upd)
    
    def _on_error(self, err):
        def _upd(*a):
            self.progress.value = 0
            self.status.text = f"❌ Xato: {err}"
            self.btn.disabled = False
        Clock.schedule_once(_upd)

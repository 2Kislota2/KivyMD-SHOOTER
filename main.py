from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy import platform
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton


class MainScreen(MDScreen):
    ...


class GameScreen(MDScreen):
    ...

class SettingsScren(MDScreen):
    ...

class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        self.sm = MDScreenManager()

        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(GameScreen(name='game'))
        self.sm.add_widget(SettingsScren(name='settings'))

        return self.sm
    
if platform != "android":
    Window.size = (400, 900)

app = ShooterApp()
app.run()
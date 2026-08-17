from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy import platform
from kivy.core.window import Window, Clock
from kivymd.uix.button import MDIconButton
from kivy.metrics import dp, sp
from kivymd.uix.widget import MDWidget
FPS = 60
BULLET_SPEED = dp(10)
SHIP_SPEED = dp(5)

class MainScreen(MDScreen):
    ...


class GameScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        Clock.schedule_interval(self.update, 1/FPS)
        
        self.evetkey = {}
        self.catridge = []
        
    def update(self, dt):
        for key,in self.evetkeys:
            if self.evetkeys[key] == True:
                if key == 'left':
                    self.moveLeft()
                if key == "rigth":
                    self.moveRight()
                if key == "shot":
                    self.shot()
                    self.eventkeys[key] = False
                    
        for bullet in self.cartridge:
            bullet.poss[1] += BULLET_SPEED
            
    def pressKey(self, key):
        self.eventkeys[key] = True
    def releaseKey(self, key):
        self.eventkeys[key] = False
    def moveLeft(self):
        self.ids.ship.pos[0] -= SHIP_SPEED
    def moveRight(self):
            self.ids.ship.pos[0] += SHIP_SPEED
    def shot(self):
        shot = Shot(pos=(self.ids.ship.center_x, self.ids.ship.top))
        self.catridge.append(shot)
        self.ids.front.add_widget(shot)
        
                
class Shot(MDWidget):
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
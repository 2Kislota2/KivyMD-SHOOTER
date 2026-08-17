from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import sp, dp
from kivy.core.window import Window
from kivy import platform
from kivy.uix.image import Image
from random import randint
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Keyboard
FPS = 60
BULLET_SPEED = dp(10)
SHIP_SPEED = dp(5)

DIR_UP = 1
DIR_DOWN = -1


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
        
        
class Ship(Image):
    def __init__(self, direction = DIR_UP, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction

    def moveLeft(self):
        self.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.pos[0] += SHIP_SPEED

    def shot(self):
        shot = Shot(self.direction)
        shot.center_x = self.center_x
        shot.y = self.top if self.direction == DIR_UP else self.y - shot.height

        self.parent.parent.parent.parent.bullets.append(shot)
        self.parent.add_widget(shot)

    def update(self):
        pass   
    
class PlayerShip(Ship):
    def __int__(self, **kwargs):
        super().__init__(direction=DIR_UP,**kwargs)
        
    def update(self, keys):
        for key in keys:
            if keys[key] == True:
                if key == "left" and self.center_x > 0:
                    self.moveLeft()
                if key == "right" and self.center_x < Window.width:
                    self.moveRight
                if key == "shot":
                    self.shot()
                    keys[key] = False
class EnemyShip(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(direction=DIR_DOWN, **kwargs)
        self.frame = 0
        
    def update(self):
        super().update()
        self.pos[1] -= dp(3)
        if self.frame % 100 == 0:
            self.shot()
        self.frame += 1
                
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
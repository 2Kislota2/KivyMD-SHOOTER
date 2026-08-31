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
from kivymd.uix.button import MDButton
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
        
        self.evetkeys = {}
        self.bullets = []
        self.ship = self.ids.ship
        self.enemyShips = []
        self.pauseMenu = None
        
    def _on_key_down(self, window, keycode, *args, **kwargs):
        key = key if (key := Keyboard.keycode_to_string(window, keycode)) != "spacebar" else "shot"
        
        self.evetkeys[key] = True
        
    def _on_key_up(self, window, keycode, *args, **kwargs):
        key = key if (key := Keyboard.keycode_to_string(window, keycode)) != "spacebar" else "shot"
        
        self.evetkeys[key] = False
        
    # def update(self, dt):
    #     for key,in self.evetkeys:
    #         if self.evetkeys[key] == True:
    #             if key == 'left':
    #                 self.moveLeft()
    #             if key == "rigth":
    #                 self.moveRight()
    #             if key == "shot":
    #                 self.shot()
    #                 self.eventkeys[key] = False
    def update(self, dt):
        self.ship.update(self.evetkeys)
        
        
        self.time_last_spawn += dt
        
        if self.time_last_spawn >= self.spawn_delay:
            self.spawn_enemy()
            self.time_last_spawn = 0
        
        for ship in self.enemyShips:
            self.update()
            if  ship.top < 0 :
                self.enemyShips.remove(ship)
                self.ids.front.remove_widget(ship)
                
                if ship.collide_widget(self.ship):
                    self.game_over()
        self.manage_bullets()
        
    def game_over(self):
        self.updateEvent.cancel()
        
        for enemy in self.enemyShips[:]:
            self.enemyShips.remove(enemy)
            self.ids.front.remove_widget(enemy)
            
        for bullet in self.bullets[:]:
            self.enemyShips.remove(bullet)
            self.ids.front.remove_widget(bullet)
        
        
        self.manager.current = "game_over"
                    
     
        
    def manage_bullets(self):
        for bullet in self.bullets[:]:
            bullet.y += BULLET_SPEED * bullet.direction
            
            self.check_collisions(bullet)
            
            if bullet.y > Window.height or bullet.top < 0:
                self.ids.front.remove_widget(bullet)
                self.bullets.remove(bullet)
    def check_collision(self, bullet):
        if bullet.owner == self.ship:
            for enemy in self.enemyShips[:]:
                if bullet.collide_widget(enemy):
                    self.enemyShips.remove(enemy)
                    self.ids.front.remove_widget(enemy)
                    
                    self.remove_bullet(bullet)
                    break
        else:
            if bullet.collide_widget(self.ship):
                self.game_over()
                self.remove_bullet(bullet)
                
    def on_enter(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS)

        
        return super().on_enter(*args)
    
    def spawn_enemy(self):
        ship = EnemyShip(DIR_DOWN)
        ship.pos = (randint(0, int(Window.size[0] -  ship.size[0])), Window.size[1])
        self.enemyShips.append(ship)
        self.ids.front.add_widget(self.enemyShips[-1])
        
        
    
    def pauseStop(self, *args):
        self.pauseMenu.dismiss()
        
    def resumeGame(self, *args):
        self.updateEvent = Clock.schedule_interval(self.update, 1/FPS)
            
    
    def show_menu(self):
        self.updateEvent.cancel()

        if not self.pauseMenu:
            self.pauseMenu = MDDialog(
                title="Game Paused",
                text="Resume the game?",
                on_dismiss=self.resumeGame,
                buttons=[
                    MDButton(
                        text="RESUME",
                        theme_text_color="Custom",
                        text_color=app.theme_cls.primary_color,
                        on_press=self.pauseStop
                    )
                ],
            )
        self.pauseMenu.open()
        
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
        self.bullets.append(shot)
        self.ids.front.add_widget(shot)

class GameOverScreen(MDScreen):
    pass
        
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
    def __init__(self, direction = DIR_UP, owner = None , **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.owner = owner
    

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
        self.sm.add_widget(GameOverScreen(name="game_over"))

        return self.sm
    
if platform != "android":
    Window.size = (400, 900)

app = ShooterApp()
app.run()
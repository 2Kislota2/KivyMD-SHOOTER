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
    pass


class GameScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        # Clock.schedule_interval(self.update, 1/FPS) # СТАРЫЙ КОД - таймер теперь запускается в on_enter
        
        # self.evetkeys = {} # СТАРЫЙ КОД с опечаткой
        self.event_keys = {}  # ИСПРАВЛЕНО: единое имя переменной
        self.bullets = []
        # self.ship = self.ids.ship # СТАРЫЙ КОД - лучше обращаться через ids
        self.enemyShips = []
        self.pauseMenu = None
        
        # ДОБАВЛЕНО: инициализация переменных для спавна врагов
        self.time_last_spawn = 0
        self.spawn_delay = 1.5  # интервал между спавнами врагов (секунды)
        self.updateEvent = None  # ссылка на таймер обновления
        
    def _on_key_down(self, window, keycode, *args, **kwargs):
        # key = key if (key := Keyboard.keycode_to_string(window, keycode)) != "spacebar" else "shot" # СТАРЫЙ КОД - ошибка с моржовым оператором
        
        # ИСПРАВЛЕНО: правильная обработка клавиш
        key_str = Keyboard.keycode_to_string(window, keycode)
        key = "shot" if key_str == "spacebar" else key_str
        self.event_keys[key] = True
        
    def _on_key_up(self, window, keycode, *args, **kwargs):
        # key = key if (key := Keyboard.keycode_to_string(window, keycode)) != "spacebar" else "shot" # СТАРЫЙ КОД
        
        # ИСПРАВЛЕНО: правильная обработка клавиш
        key_str = Keyboard.keycode_to_string(window, keycode)
        key = "shot" if key_str == "spacebar" else key_str
        self.event_keys[key] = False
        
    # def update(self, dt): # СТАРЫЙ КОД
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
        # ИСПРАВЛЕНО: обновляем корабль игрока через ids
        if self.ids.get('ship'):
            self.ids.ship.update(self.event_keys)
        
        # Логика спавна врагов
        self.time_last_spawn += dt
        
        if self.time_last_spawn >= self.spawn_delay:
            self.spawn_enemy()
            self.time_last_spawn = 0
        
        # ИСПРАВЛЕНО: обновляем каждого врага (была рекурсия!)
        for ship in self.enemyShips[:]:
            # self.update() # СТАРЫЙ КОД - вызывал сам себя, была бесконечная рекурсия!
            ship.update(dt)  # ИСПРАВЛЕНО: вызываем update врага
            
            if ship.top < 0:
                self.enemyShips.remove(ship)
                self.ids.front.remove_widget(ship)
                
                if ship.collide_widget(self.ids.ship):
                    self.game_over()
                    
        self.manage_bullets()
        
    def game_over(self):
        if self.updateEvent:
            self.updateEvent.cancel()
        
        # Отвязываем клавиатуру
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        
        for enemy in self.enemyShips[:]:
            self.enemyShips.remove(enemy)
            self.ids.front.remove_widget(enemy)
            
        # for bullet in self.bullets[:]: # СТАРЫЙ КОД
        #     self.enemyShips.remove(bullet) # ОШИБКА: удалял пулю из списка врагов!
        #     self.ids.front.remove_widget(bullet)
        
        # ИСПРАВЛЕНО: правильно удаляем пули
        for bullet in self.bullets[:]:
            self.remove_bullet(bullet)
        
        self.manager.current = "game_over"
                    
     
        
    def manage_bullets(self):
        for bullet in self.bullets[:]:
            bullet.y += BULLET_SPEED * bullet.direction
            
            # self.check_collisions(bullet) # СТАРЫЙ КОД - метод называется check_collision
            self.check_collision(bullet)  # ИСПРАВЛЕНО
            
            if bullet.y > Window.height or bullet.top < 0:
                # self.ids.front.remove_widget(bullet) # СТАРЫЙ КОД
                # self.bullets.remove(bullet)
                
                # ИСПРАВЛЕНО: используем общий метод удаления
                self.remove_bullet(bullet)
                
    def check_collision(self, bullet):
        if bullet.owner == self.ids.ship:
            for enemy in self.enemyShips[:]:
                if bullet.collide_widget(enemy):
                    self.enemyShips.remove(enemy)
                    self.ids.front.remove_widget(enemy)
                    
                    # self.remove_bullet(bullet) # СТАРЫЙ КОД - метод не существовал
                    self.remove_bullet(bullet)  # ИСПРАВЛЕНО: теперь метод есть
                    break
        else:
            if bullet.collide_widget(self.ids.ship):
                self.game_over()
                self.remove_bullet(bullet)
                
    # ДОБАВЛЕНО: общий метод для удаления пуль
    def remove_bullet(self, bullet):
        """Безопасно удаляет пулю из игры"""
        if bullet in self.bullets:
            self.bullets.remove(bullet)
        if bullet.parent:  # проверяем, что пуля еще на экране
            bullet.parent.remove_widget(bullet)
                
    def on_enter(self, *args):
        # self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS) # СТАРЫЙ КОД - не привязывал клавиатуру
        
        # ИСПРАВЛЕНО: привязываем обработчики клавиатуры
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.updateEvent = Clock.schedule_interval(self.update, 1 / FPS)
        
        return super().on_enter(*args)
    
    # ДОБАВЛЕНО: отвязываем клавиатуру при выходе с экрана
    def on_leave(self, *args):
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        if self.updateEvent:
            self.updateEvent.cancel()
        super().on_leave(*args)
    
    def spawn_enemy(self):
        ship = EnemyShip(direction=DIR_DOWN)
        ship.pos = (randint(0, int(Window.size[0] - ship.size[0])), Window.size[1])
        self.enemyShips.append(ship)
        # self.ids.front.add_widget(self.enemyShips[-1]) # СТАРЫЙ КОД
        self.ids.front.add_widget(ship)  # ИСПРАВЛЕНО: добавляем созданного врага
        
        
    
    def pauseStop(self, *args):
        if self.pauseMenu:
            self.pauseMenu.dismiss()
        
    def resumeGame(self, *args):
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.updateEvent = Clock.schedule_interval(self.update, 1/FPS)
            
    
    def show_menu(self):
        if self.updateEvent:
            self.updateEvent.cancel()
        
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

        if not self.pauseMenu:
            self.pauseMenu = MDDialog(
                title="Game Paused",
                text="Resume the game?",
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
        # self.eventkeys[key] = True # СТАРЫЙ КОД
        self.event_keys[key] = True  # ИСПРАВЛЕНО
        
    def releaseKey(self, key):
        # self.eventkeys[key] = False # СТАРЫЙ КОД
        self.event_keys[key] = False  # ИСПРАВЛЕНО
        
    def moveLeft(self):
        self.ids.ship.pos[0] -= SHIP_SPEED
        
    def moveRight(self):
        self.ids.ship.pos[0] += SHIP_SPEED
        
    def shot(self):
        shot = Shot(direction=DIR_UP, owner=self.ids.ship)
        shot.center_x = self.ids.ship.center_x
        shot.y = self.ids.ship.top
        self.bullets.append(shot)
        self.ids.front.add_widget(shot)

class GameOverScreen(MDScreen):
    pass
        
class Ship(Image):
    def __init__(self, direction=DIR_UP, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction

    def moveLeft(self):
        self.pos[0] -= SHIP_SPEED

    def moveRight(self):
        self.pos[0] += SHIP_SPEED

    def shot(self):
        # ИСПРАВЛЕНО: передаем владельца пули
        shot = Shot(direction=self.direction, owner=self)
        shot.center_x = self.center_x
        shot.y = self.top if self.direction == DIR_UP else self.y - shot.height
        
        # self.parent.parent.parent.parent.bullets.append(shot) # СТАРЫЙ КОД - хрупкая иерархия
        # self.parent.add_widget(shot)
        
        # ИСПРАВЛЕНО: ищем GameScreen в родителях
        game_screen = None
        parent = self.parent
        while parent:
            if isinstance(parent, GameScreen):
                game_screen = parent
                break
            parent = parent.parent
            
        if game_screen:
            game_screen.bullets.append(shot)
            game_screen.ids.front.add_widget(shot)

    def update(self, dt=0):
        pass   
    
class PlayerShip(Ship):
    # def __int__(self, **kwargs): # СТАРЫЙ КОД - опечатка!
    #     super().__init__(direction=DIR_UP,**kwargs)
    
    def __init__(self, **kwargs):  # ИСПРАВЛЕНО: правильное имя метода
        super().__init__(direction=DIR_UP, **kwargs)
        
    def update(self, keys):
        for key in keys:
            if keys[key] == True:
                if key == "left" and self.center_x > 0:
                    self.moveLeft()
                if key == "right" and self.center_x < Window.width:
                    # self.moveRight # СТАРЫЙ КОД - забыты скобки!
                    self.moveRight()  # ИСПРАВЛЕНО: добавлены скобки
                if key == "shot":
                    self.shot()
                    keys[key] = False
                    
class EnemyShip(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(direction=DIR_DOWN, **kwargs)
        self.frame = 0
        
    def update(self, dt=0):
        super().update(dt)
        self.pos[1] -= dp(3)
        if self.frame % 100 == 0:
            self.shot()
        self.frame += 1
                
class Shot(MDWidget):
    def __init__(self, direction=DIR_UP, owner=None, **kwargs):
        super().__init__(**kwargs)
        self.direction = direction
        self.owner = owner
        self.size_hint = (None, None)
        self.size = (dp(10), dp(20))
    

# class SettingsScren(MDScreen): # СТАРЫЙ КОД - опечатка
#     ...

class SettingsScreen(MDScreen):  # ИСПРАВЛЕНО: правильное название
    pass

class ShooterApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"

        self.sm = MDScreenManager()

        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(GameScreen(name='game'))
        # self.sm.add_widget(SettingsScren(name='settings')) # СТАРЫЙ КОД
        self.sm.add_widget(SettingsScreen(name='settings'))  # ИСПРАВЛЕНО
        self.sm.add_widget(GameOverScreen(name="game_over"))

        return self.sm
    
if platform != "android":
    Window.size = (400, 900)

app = ShooterApp()
app.run()
from collections import defaultdict
from math import sin
from random import choice, randint

import pygame as pg
from pygame import Vector2

from . import (
    package_dir,
    tools,
)
from .gameobject import GameObject


class Core:

    FPS = 60

    def __init__(self, window: pg.Surface) -> None:
        self.window = window
        self.window_rect = self.window.get_rect()
        self.window_width, self.window_height = self.window_rect.size

        # Load graphics and sounds
        self.GFX = tools.load_graphics(package_dir / 'images')
        self.SFX = tools.load_sounds(package_dir / 'sounds')

        # Dicts that store held down, pressed, and released keys.
        self.keys = defaultdict(bool)
        self.keys_pressed = defaultdict(bool)
        self.keys_released = defaultdict(bool)
        # Is the mouse button pressed?
        self.mouse = defaultdict(bool)
        # Current mouse position
        self.mouse_pos = (0, 0)
        # Stores the positions where every mouse button was last pressed.
        self.mouse_pressed_at = {}
        # Stores if the mouse buttons were pressed/released in the latest loop.
        self.mouse_pressed = defaultdict(bool)
        self.mouse_released = defaultdict(bool)

        self.gameover = False
        self.hp = 5
        self.points = 0
        self.heart = GameObject(self.GFX['heart.png'])

        self.bg = GameObject(self.GFX['background.png'])

        self.slingshot_center = Vector2(219, 364)
        self.slingshot_left_arm = self.slingshot_center - (24, 0)
        self.slingshot_right_arm = self.slingshot_center + (24, 0)
        self.draw_band = True
        self.snowball_path = []
        self.snowball_path_length = 15

        self.snowball = Snowball(self.GFX['snowball.png'], size=(28, 28), pos=self.slingshot_center, centered=True)
        self.bounced = False

        self.enemies: list[Enemy] = []
        self.enemy_size = (38, 38)
        self.enemy_types = [
            PanzerKorv,
            ITKorv,
            TovePirate,
            DanteSith,
            NATman,
            VampireNAT,
        ]
        Enemy.spawn_x = self.window_rect.right
        PanzerKorv._texture = self.GFX['panzerkorv.png']
        PanzerKorv.spawn_y = self.window_height - self.enemy_size[1] - 50
        PanzerKorv.spawn_y_variance = 50
        ITKorv._texture = self.GFX['itkorv.png']
        ITKorv.spawn_y = 0.6 * self.window_height
        ITKorv.spawn_y_variance = 0.3 * self.window_height
        TovePirate._texture = self.GFX['tovepirate.png']
        TovePirate.spawn_y = 0.6 * self.window_height
        TovePirate.spawn_y_variance = 0.3 * self.window_height
        DanteSith._texture = self.GFX['dantesith.png']
        DanteSith.spawn_y = 0.6 * self.window_height
        DanteSith.spawn_y_variance = 0.3 * self.window_height
        NATman._texture = self.GFX['natman.png']
        NATman.spawn_y = 0.3 * self.window_height
        NATman.spawn_y_variance = 0.15 * self.window_height
        VampireNAT._texture = self.GFX['vampirenat.png']
        VampireNAT.spawn_y = 0.3 * self.window_height
        VampireNAT.spawn_y_variance = 0.15 * self.window_height


    def update(self, events: list[pg.event.Event]) -> bool | None:
        """Function in charge of everything that happens during a game loop"""

        self.update_inputs(events)

        if self.gameover:
            # wait for game restart
            if self.keys_pressed[pg.K_RETURN]:
                return True
            return

        self.check_player_input()

        # move snowball
        self.snowball.update()
        if (self.snowball.rect.right < self.window_rect.left or
            self.snowball.rect.left > self.window_rect.right or
            self.snowball.rect.top > self.window_rect.bottom):
            self.snowball.pos = self.slingshot_center
            self.snowball._center()
            self.snowball.frozen = True
            self.draw_band = True
        elif self.snowball.rect.top < self.window_rect.top:
            self.snowball.pos.y = self.window_rect.top
            self.snowball.spd.y *= -1
            self.bounced = True

        # update enemies
        for e in self.enemies:
            e.update()
            if not self.snowball.frozen and e.rect.colliderect(self.snowball.rect):
                e.kill()
                self.points += 2 if self.bounced else 1
                self.snowball.pos = self.slingshot_center
                self.snowball._center()
                self.snowball.frozen = True
                self.draw_band = True
            if e.rect.right < self.window_rect.left:
                e.kill()
                self.hp -= 1
                if self.hp <= 0:
                    self.gameover = True
                    return

        # generate enemies
        if not randint(0, 100):
            self.enemies.append(choice(self.enemy_types)(
                size=self.enemy_size,
                kill_func=self.enemies.remove,
                speed_multiplier=1+self.points/100
                ))


    def check_player_input(self) -> None:

        if self.mouse[pg.BUTTON_LEFT]:
            if self.snowball.frozen:
                launch = Vector2(self.mouse_pos) - self.slingshot_center
                if launch.length() > 0:
                    launch.scale_to_length(min(100, (self.mouse_pos - self.slingshot_center).length()))
                self.snowball.pos = self.slingshot_center + launch
                self.snowball._center()

                sim_pos = Vector2(self.snowball.pos)
                sim_spd = (self.slingshot_center - self.snowball.center) / 5
                self.snowball_path = [None] * self.snowball_path_length
                for i in range(self.snowball_path_length):
                    sim_pos += sim_spd
                    sim_spd.y += self.snowball.acc_y
                    self.snowball_path[i] = Vector2(sim_pos) + Vector2(self.snowball.size) / 2

        if self.snowball.frozen and self.mouse_released[pg.BUTTON_LEFT]:
            self.snowball.frozen = False
            self.snowball.spd = (self.slingshot_center - self.snowball.center) / 5
            self.draw_band = False
            self.snowball_path = []
            self.bounced = False


    def update_inputs(self, events: list[pg.event.Event]) -> None:
        """Updates which keys & buttons are pressed"""

        # Saves the input states from the last loop
        keys_prev = self.keys.copy()
        mouse_prev = self.mouse.copy()

        for event in events:
            match event.type:
                case pg.MOUSEBUTTONDOWN:
                    self.mouse[event.button] = True
                case pg.MOUSEBUTTONUP:
                    self.mouse[event.button] = False
                case pg.MOUSEMOTION:
                    self.mouse_pos = event.pos
                case pg.KEYDOWN:
                    self.keys[event.key] = True
                case pg.KEYUP:
                    self.keys[event.key] = False

        # Checks where mouse buttons were clicked
        # and where they were released
        for btn, now in self.mouse.items():
            prev = mouse_prev[btn]
            if pressed := not prev and now:
                self.mouse_pressed_at[btn] = self.mouse_pos
            self.mouse_pressed[btn] = pressed
            self.mouse_released[btn] = prev and not now

        # Checks which keys were pressed or released
        for key, now in self.keys.items():
            prev = keys_prev[key]
            self.keys_pressed[key] = not prev and now
            self.keys_released[key] = prev and not now

    def draw(self) -> None:
        self.window.fill((0, 0, 0))

        self.bg.draw(self.window)

        for pos in self.snowball_path:
            pg.draw.circle(self.window, (30,158,30), pos, 2.5)

        pg.draw.line(self.window, (0,0,0), self.slingshot_left_arm, self.snowball.center if self.draw_band else self.slingshot_center, 4)
        pg.draw.line(self.window, (0,0,0), self.slingshot_right_arm, self.snowball.center if self.draw_band else self.slingshot_center, 4)

        tools.Font.write(self.window, tools.Font.consolas_b36, f'Points: {self.points}', pos=(2, self.window_height), anchor=6, color=(0,0,0))
        for i in range(self.hp):
            self.heart.pos = (2 + 36*i, self.window_height-72)
            self.heart.draw(self.window)

        for e in self.enemies:
            e.draw(self.window)

        self.snowball.draw(self.window)

        if self.gameover:
            tools.Font.write(self.window, tools.Font.consolas_b36, 'Game over', pos=self.window_rect.center, anchor=4, color=(255,0,0))
            tools.Font.write(self.window, tools.Font.consolas_b36, 'Press [Return] to play again', pos=Vector2(self.window_rect.center)+(0,36), anchor=4, color=(255,0,0))

        pg.display.update()


class Snowball(GameObject):
    acc_y = 0.15

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.spd = Vector2()
        self.frozen = True

    def update(self) -> None:
        if not self.frozen:
            self.pos += self.spd
            self.spd.y += self.acc_y

class Enemy(GameObject):
    _texture = None
    speed = 1
    spawn_x = None
    spawn_y = None
    spawn_y_variance = 0
    def __init__(self, *args, speed_multiplier=1, **kwargs) -> None:
        super().__init__(
            self._texture,
            *args,
            pos=(
                self.spawn_x,
                self.spawn_y + randint(
                    -self.spawn_y_variance,
                    self.spawn_y_variance
                    )
                ),
            **kwargs
            )
        self.move = Vector2(-self.speed * speed_multiplier, 0)

    def update(self) -> None:
        self.pos += self.move

class PanzerKorv(Enemy):
    speed = 1.75

class RollingEnemy(Enemy):
    rot_speed = 1.4
    def update(self) -> None:
        super().update()
        self.set_angle(-self.pos.x * self.rot_speed % 360)

class ITKorv(RollingEnemy):
    speed = 1.2

class TovePirate(Enemy):
    speed = 1

class DanteSith(Enemy):
    speed = 1

class FlyingEnemy(Enemy):
    def update(self) -> None:
        super().update()
        self.pos.y += sin(self.freq * self.pos.x) * self.fly_height

class NATman(FlyingEnemy):
    fly_height = 2.5
    freq = 0.08
    speed = 1.5

class VampireNAT(FlyingEnemy):
    fly_height = 3.5
    freq = 0.05
    speed = 1.4

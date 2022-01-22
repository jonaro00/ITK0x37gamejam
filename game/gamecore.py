from collections import defaultdict

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

        self.bg = GameObject(self.GFX['background.png'])

        self.slingshot_center = Vector2(219, 364)
        self.slingshot_left_arm = self.slingshot_center - (24, 0)
        self.slingshot_right_arm = self.slingshot_center + (24, 0)
        self.draw_band = True

        self.snowball = Snowball(self.GFX['snowball.png'], size=(28, 28), pos=self.slingshot_center, centered=True)


    def update(self, events: list[pg.event.Event]) -> None:
        """Function in charge of everything that happens during a game loop"""

        self.update_inputs(events)
        self.check_player_input()

        self.snowball.update()
        if (self.snowball.rect.right < self.window_rect.left or
            self.snowball.rect.left > self.window_rect.right or
            self.snowball.rect.top > self.window_rect.bottom):
            self.snowball.pos = self.slingshot_center
            self.snowball._center()
            self.snowball.frozen = True
            self.draw_band = True
        elif self.snowball.rect.top < self.window_rect.top:
            self.snowball.spd.reflect_ip((0, 1))


    def check_player_input(self) -> None:

        if self.mouse[pg.BUTTON_LEFT]:
            if self.snowball.frozen:
                launch = Vector2(self.mouse_pos) - self.slingshot_center
                if launch.length() > 0:
                    launch.scale_to_length(min(100, (self.mouse_pos - self.slingshot_center).length()))
                self.snowball.pos = self.slingshot_center + launch
                self.snowball._center()

        if self.snowball.frozen and self.mouse_released[pg.BUTTON_LEFT]:
            self.snowball.frozen = False
            self.snowball.spd = (self.slingshot_center - self.snowball.center) / 5
            self.draw_band = False


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

        pg.draw.line(self.window, (0,0,0), self.slingshot_left_arm, self.snowball.center if self.draw_band else self.slingshot_center, 4)
        pg.draw.line(self.window, (0,0,0), self.slingshot_right_arm, self.snowball.center if self.draw_band else self.slingshot_center, 4)

        self.snowball.draw(self.window)

        pg.display.update()


class Snowball(GameObject):
    speed = 8
    acc_y = 0.15

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.spd = Vector2()
        self.frozen = True

    def update(self):
        if not self.frozen:
            self.pos += self.spd
            self.spd += (0, self.acc_y)

from typing import Callable

import pygame as pg
from pygame import Vector2


class GameObject:
    def __init__(self,
                 texture: pg.Surface,
                 size: Vector2 | tuple[int, int] = None,
                 pos: Vector2 | tuple[int, int] = (0, 0),
                 centered: bool = False,
                 angle: float = 0,
                 visible: bool = True,
                 kill_func: Callable | None = None,
                 ) -> None:
        self.size = texture.get_size() if size is None else size
        self.texture = pg.transform.scale(texture, self.size)
        if angle:
            self.texture = pg.transform.rotate(self.texture, angle)
            self.size = self.texture.get_size()
        self._pos = Vector2(pos)
        if centered:
            self.pos -= Vector2(self.size) / 2
        self.visible = visible
        self.kill = lambda: kill_func(self) if kill_func else lambda: None

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    @property
    def pos(self) -> Vector2:
        return self._pos

    @pos.setter
    def pos(self, value: Vector2 | tuple[int, int]) -> None:
        self._pos = Vector2(value)

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.pos, self.size)

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center

    def set_angle(self, angle: float) -> None:
        self.texture = pg.transform.rotate(self.texture, angle)
        self.size = self.texture.get_size()
        self.pos = self.rect.center - Vector2(self.size) / 2

    def angle_towards(self, point: Vector2) -> None:
        self.set_angle((Vector2(point) - Vector2(self.rect.center)).angle_to((0, 1)))

    def draw(self, window: pg.Surface) -> None:
        if self.visible:
            window.blit(self.texture, self.pos)

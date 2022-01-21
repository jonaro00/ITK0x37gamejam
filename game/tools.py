from functools import cache
from pathlib import Path
from typing import Sequence

from . import package_dir

import pygame as pg
from pygame import Vector2

pg.font.init()


class Font:
    consolas_b24 = pg.font.Font(package_dir / 'fonts/consolab.ttf', 24)
    cambria30 = pg.font.Font(package_dir / 'fonts/cambria.ttc', 30)
    verdana23 = pg.font.Font(package_dir / 'fonts/verdana.ttf', 23)
    verdana26 = pg.font.Font(package_dir / 'fonts/verdana.ttf', 26)

    @staticmethod
    @cache
    def render(font: pg.font.Font,
               content,
               color: pg.Color | tuple[int] = (255, 255, 255),
               bg_color: pg.Color | tuple[int] | None = None,
               ) -> pg.Surface:
        """Returns a `Surface` with `content` rendered with
        `font` and `color`. Uses caching."""
        return font.render(str(content), True, color, bg_color)

    @staticmethod
    def write(surface: pg.Surface,
              font: pg.font.Font,
              content,
              color: pg.Color | tuple[int] = (255, 255, 255),
              pos: Vector2 | tuple[int, int] = (0, 0),
              anchor: int = 0,
              ):
        """Writes text to `surface`.
        `anchor` determines which point/corner of the text should be at `pos`,
        as following:

        ```
        0 1 2
        3 4 5
        6 7 8
        ```

        0 being the top-left corner and 4 being the center etc.
        """
        assert isinstance(anchor, int) and anchor >= 0 and anchor <= 8

        img = Font.render(font, content, color)
        width, height = img.get_rect().size
        pos = Vector2(pos)

        y, x = divmod(anchor, 3)
        if x > 0:
            pos.x -= width / (3 - x)
        if y > 0:
            pos.y -= height / (3 - y)

        surface.blit(img, pos)


def load_graphics(directory: Path,
                  accept: Sequence[str]=('.png', '.jpg', '.webp'),
                  ) -> dict[str, pg.Surface]:
    """Returns a dict with all images in `directory` loaded as a
    `pg.Surface`. The key is the filename with extension."""
    graphics = {}
    for pic in directory.iterdir():
        if pic.suffix.lower() in accept:
            graphics[str(pic.relative_to(directory))] = \
                pg.image.load(directory / pic).convert_alpha()
    return graphics

def load_sounds(directory: Path,
                accept: Sequence[str]=('.mp3', '.wav', '.ogg'),
                ) -> dict[str, pg.mixer.Sound]:
    """Returns a dict with all sounds in `directory` loaded as a
    `pg.mixer.Sound`. The key is the filename with extension."""
    sounds = {}
    for snd in directory.iterdir():
        if snd.suffix.lower() in accept:
            sounds[str(snd.relative_to(directory))] = pg.mixer.Sound(directory / snd)
    return sounds

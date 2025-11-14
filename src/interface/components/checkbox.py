from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from .component import UIComponent

class Checkbox(UIComponent):
    def __init__(self, x: int, y: int, width: int, height: int,
                 unchecked_img: str, checked_img: str,
                 initial: bool = False, on_toggle=None):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.is_checked = initial
        self.on_toggle = on_toggle
        self.sprite_unchecked = Sprite(unchecked_img, (width, height))
        self.sprite_checked = Sprite(checked_img, (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self.click_cooldown = 0.0

    def update(self, dt: float) -> None:
        if self.click_cooldown > 0:
            self.click_cooldown -= dt
        if pg.mouse.get_pressed()[0] and self.click_cooldown <= 0:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.is_checked = not self.is_checked
                if self.on_toggle:
                    self.on_toggle(self.is_checked)
                self.click_cooldown = 0.2

    def draw(self, screen: pg.Surface) -> None:
        sprite = self.sprite_checked if self.is_checked else self.sprite_unchecked
        screen.blit(sprite.image, self.rect)

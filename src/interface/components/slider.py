from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from .component import UIComponent

class Slider(UIComponent):
    def __init__(self, x: int, y: int, width: int, height: int,
                 bar_img: str, handle_img: str,
                 initial: float = 0.5, on_change=None):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.value = max(0.0, min(1.0, initial))
        self.on_change = on_change
        self.sprite_bar = Sprite(bar_img, (width, height))
        self.sprite_handle = Sprite(handle_img, (24, 24))
        self.bar_rect = pg.Rect(x, y, width, height)
        self.handle_rect = pg.Rect(0, 0, 24, 24)
        self.dragging = False
        self._update_handle_pos()

    def _update_handle_pos(self):
        hx = self.x + int(self.value * self.width) - 12
        hy = self.y + self.height // 2 - 12
        self.handle_rect.topleft = (hx, hy)

    def update(self, dt: float) -> None:
        mouse_pos = pg.mouse.get_pos()
        m_pressed = pg.mouse.get_pressed()[0]
        if m_pressed and (self.handle_rect.collidepoint(mouse_pos) or self.bar_rect.collidepoint(mouse_pos)):
            self.dragging = True
        elif not m_pressed:
            self.dragging = False
        if self.dragging:
            rel_x = max(self.x, min(mouse_pos[0], self.x + self.width))
            self.value = (rel_x - self.x) / self.width
            self._update_handle_pos()
            if self.on_change:
                self.on_change(self.value)

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.sprite_bar.image, self.bar_rect)
        screen.blit(self.sprite_handle.image, self.handle_rect)

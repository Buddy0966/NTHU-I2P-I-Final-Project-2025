from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.core.services import input_manager
from typing import Callable, Optional

class BattleActionButton:
    def __init__(self, label: str, x: int, y: int, width: int, height: int,
                 on_click: Callable[[], None] | None = None):
        self.label = label
        self.rect = pg.Rect(x, y, width, height)
        self.on_click = on_click
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
        
        try:
            self.img_default = Sprite("UI/raw/UI_Flat_Button01a_2.png", (width, height))
            self.img_hover = Sprite("UI/raw/UI_Flat_Button01a_1.png", (width, height))
        except:
            self.img_default = None
            self.img_hover = None
        
        self.is_hovered = False

    def update(self, dt: float) -> None:
        mouse_pos = input_manager.mouse_pos
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered and input_manager.mouse_pressed(1):
            if self.on_click:
                self.on_click()

    def draw(self, screen: pg.Surface) -> None:
        img = self.img_hover if self.is_hovered else self.img_default
        
        if img:
            screen.blit(img.image, self.rect)
        else:
            color = (100, 150, 255) if self.is_hovered else (80, 120, 255)
            pg.draw.rect(screen, color, self.rect)
            pg.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        label_text = self._font.render(self.label, True, (0, 0, 0))
        text_rect = label_text.get_rect(center=self.rect.center)
        screen.blit(label_text, text_rect)

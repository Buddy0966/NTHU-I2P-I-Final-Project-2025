from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.utils.definition import Item
from .component import UIComponent

class BagPanel(UIComponent):
    def __init__(self, items: list[Item], x: int, y: int, width: int = 600, height: int = 400, on_exit=None):
        self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 40)
        self._item_font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self.items = items
        
        self.title_surf = self._font.render("BAG", True, (0, 0, 0))
        
        margin = 12
        btn_w, btn_h = 50, 50
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            x + width - btn_w - margin, y + margin, btn_w, btn_h,
            on_exit
        )
        
        self._item_sprites = {}
        for item in items:
            try:
                self._item_sprites[item["name"]] = Sprite(item["sprite_path"], (40, 40))
            except:
                self._item_sprites[item["name"]] = None

    def update(self, dt: float) -> None:
        self.exit_button.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.sprite.image, self.rect)
        screen.blit(self.title_surf, (self.rect.x + 16, self.rect.y + 16))
        
        item_x = self.rect.x + 30
        item_y = self.rect.y + 70
        line_height = 60
        
        for i, item in enumerate(self.items):
            y_pos = item_y + i * line_height
            
            if y_pos + line_height > self.rect.y + self.rect.height - 30:
                break
            
            if item["name"] in self._item_sprites and self._item_sprites[item["name"]]:
                screen.blit(self._item_sprites[item["name"]].image, (item_x, y_pos))
            
            name_text = self._item_font.render(item["name"], True, (0, 0, 0))
            screen.blit(name_text, (item_x + 50, y_pos + 5))
            
            count_text = self._item_font.render(f"x{item['count']}", True, (0, 0, 0))
            screen.blit(count_text, (item_x + 50, y_pos + 25))
        
        self.exit_button.draw(screen)

    def set_exit_callback(self, callback) -> None:
        self.exit_button.on_click = callback

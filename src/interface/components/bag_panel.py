from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.utils.definition import Item, Monster
from .component import UIComponent

class BagPanel(UIComponent):
    def __init__(self, items: list[Item], x: int, y: int, width: int = 600, height: int = 400, on_exit=None, monsters: list[Monster] | None = None):
        self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 40)
        self._item_font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self._pokemon_font = pg.font.Font('assets/fonts/Minecraft.ttf', 12)
        self.items = items
        self.monsters = monsters if monsters else []
        
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
        
        self._pokemon_sprites = {}
        self._update_pokemon_sprites()

    def update(self, dt: float) -> None:
        self.exit_button.update(dt)
        # Update pokemon sprites in case monsters list changed
        self._update_pokemon_sprites()
    
    def _update_pokemon_sprites(self) -> None:
        """Update pokemon sprites based on current monsters list"""
        for monster in self.monsters:
            if monster["name"] not in self._pokemon_sprites:
                try:
                    self._pokemon_sprites[monster["name"]] = Sprite(monster["sprite_path"], (60, 60))
                except:
                    self._pokemon_sprites[monster["name"]] = None

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.sprite.image, self.rect)
        screen.blit(self.title_surf, (self.rect.x + 16, self.rect.y + 16))
        
        # Draw Pokemon section on the left
        pokemon_x = self.rect.x + 20
        pokemon_y = self.rect.y + 70
        pokemon_line_height = 90
        
        # Pokemon header
        pokemon_header = self._pokemon_font.render("Pokemon", True, (0, 0, 0))
        screen.blit(pokemon_header, (pokemon_x, pokemon_y - 30))
        
        # Debug: Log monsters count
        from src.utils import Logger
        Logger.debug(f"BagPanel drawing {len(self.monsters)} monsters")
        
        for i, monster in enumerate(self.monsters):
            y_pos = pokemon_y + i * pokemon_line_height
            
            if y_pos + pokemon_line_height > self.rect.y + self.rect.height - 30:
                break
            
            # Draw pokemon sprite
            if monster["name"] in self._pokemon_sprites and self._pokemon_sprites[monster["name"]]:
                screen.blit(self._pokemon_sprites[monster["name"]].image, (pokemon_x, y_pos))
            
            # Draw pokemon name
            name_text = self._pokemon_font.render(monster["name"], True, (0, 0, 0))
            screen.blit(name_text, (pokemon_x + 70, y_pos + 5))
            
            # Draw pokemon level
            level_text = self._pokemon_font.render(f"Lv.{monster.get('level', 1)}", True, (0, 0, 0))
            screen.blit(level_text, (pokemon_x + 70, y_pos + 22))
            
            # Draw HP bar
            hp_ratio = monster.get("hp", monster.get("max_hp", 100)) / monster.get("max_hp", 100)
            hp_color = (0, 255, 0) if hp_ratio > 0.3 else (255, 165, 0) if hp_ratio > 0.1 else (255, 0, 0)
            hp_bar_w = int(50 * hp_ratio)
            
            pg.draw.rect(screen, hp_color, (pokemon_x + 70, y_pos + 40, hp_bar_w, 8))
            pg.draw.rect(screen, (0, 0, 0), (pokemon_x + 70, y_pos + 40, 50, 8), 1)
            
            # Draw HP text
            hp_text = self._pokemon_font.render(f"{monster.get('hp', monster.get('max_hp', 100))}/{monster.get('max_hp', 100)}", True, (0, 0, 0))
            screen.blit(hp_text, (pokemon_x + 70, y_pos + 52))
        
        # Draw Items section on the right
        item_x = self.rect.x + 320
        item_y = self.rect.y + 70
        line_height = 60
        
        # Items header
        items_header = self._item_font.render("Items", True, (0, 0, 0))
        screen.blit(items_header, (item_x, item_y - 30))
        
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
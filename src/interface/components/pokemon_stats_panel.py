from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.utils.definition import Monster

class PokemonStatsPanel:
    monster: Monster
    rect: pg.Rect
    _font: pg.font.Font
    _small_font: pg.font.Font
    _bg_sprite: Sprite
    
    def __init__(self, monster: Monster, x: int, y: int, width: int = 160, height: int = 80):
        self.monster = monster
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self._small_font = pg.font.Font('assets/fonts/Minecraft.ttf', 12)
        
        try:
            self._bg_sprite = Sprite("UI/UI_Flat_Banner03a.png", (width, height))
        except:
            self._bg_sprite = None
        
        try:
            self.sprite = Sprite(monster["sprite_path"], (50, 50))
        except:
            self.sprite = None

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pg.Surface) -> None:
        if self._bg_sprite:
            screen.blit(self._bg_sprite.image, self.rect)
        else:
            pg.draw.rect(screen, (255, 255, 255), self.rect, 2)
            pg.draw.rect(screen, (200, 200, 200), self.rect)
        
        if self.sprite:
            screen.blit(self.sprite.image, (self.rect.x + 5, self.rect.y + 5))
        
        name_text = self._font.render(self.monster["name"], True, (0, 0, 0))
        screen.blit(name_text, (self.rect.x + 60, self.rect.y + 5))
        
        level_text = self._small_font.render(f"Lv.{self.monster['level']}", True, (0, 0, 0))
        screen.blit(level_text, (self.rect.x + 60, self.rect.y + 22))
        
        hp_ratio = self.monster["hp"] / self.monster["max_hp"]
        hp_color = (0, 255, 0) if hp_ratio > 0.3 else (255, 165, 0) if hp_ratio > 0.1 else (255, 0, 0)
        hp_bar_w = int((self.rect.width - 70) * hp_ratio)
        
        pg.draw.rect(screen, hp_color, (self.rect.x + 60, self.rect.y + 40, hp_bar_w, 10))
        pg.draw.rect(screen, (0, 0, 0), (self.rect.x + 60, self.rect.y + 40, self.rect.width - 70, 10), 1)
        
        hp_text = self._small_font.render(f"{self.monster['hp']}/{self.monster['max_hp']}", True, (0, 0, 0))
        screen.blit(hp_text, (self.rect.x + 60, self.rect.y + 52))

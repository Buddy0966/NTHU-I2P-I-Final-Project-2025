from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.battle_action_button import BattleActionButton
from src.utils.definition import Item
from src.core.services import input_manager


class BattleItemPanel:
    """Panel to select items during battle"""
    
    def __init__(self, items: list[Item], x: int, y: int, width: int = 300, height: int = 400):
        self.items = items
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self._title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 20)
        
        # Background sprite
        try:
            self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        except:
            self.sprite = None
        
        self.title_surf = self._title_font.render("Items", True, (255, 255, 255))
        
        # Cache item sprites
        self._item_sprites = {}
        for item in items:
            try:
                self._item_sprites[item["name"]] = Sprite(item["sprite_path"], (40, 40))
            except:
                self._item_sprites[item["name"]] = None
        
        # Create item buttons
        self.item_buttons: list[tuple[BattleActionButton, Item]] = []
        btn_h = 50
        btn_w = width - 40
        start_y = y + 60
        
        for i, item in enumerate(items):
            btn_y = start_y + i * (btn_h + 10)
            if btn_y + btn_h > y + height - 20:
                break
            
            btn = BattleActionButton(
                f"{item['name']} x{item['count']}", 
                x + 20, 
                btn_y, 
                btn_w, 
                btn_h,
                lambda selected_item=item: self._on_item_select(selected_item)
            )
            self.item_buttons.append((btn, item))
        
        self.selected_item: Item | None = None

    def _on_item_select(self, item: Item) -> None:
        """Called when an item is selected"""
        self.selected_item = item

    def update(self, dt: float) -> None:
        """Update all item buttons"""
        for btn, _ in self.item_buttons:
            btn.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw the item panel"""
        # Draw background
        if self.sprite:
            screen.blit(self.sprite.image, self.rect)
        else:
            pg.draw.rect(screen, (50, 50, 50), self.rect)
            pg.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        # Draw title
        screen.blit(self.title_surf, (self.rect.x + 20, self.rect.y + 15))
        
        # Draw item buttons
        for btn, item in self.item_buttons:
            btn.draw(screen)
            
            # Draw item icon on button
            if item["name"] in self._item_sprites and self._item_sprites[item["name"]]:
                icon_x = btn.rect.x + 10
                icon_y = btn.rect.y + (btn.rect.height - 30) // 2
                icon_img = pg.transform.scale(self._item_sprites[item["name"]].image, (30, 30))
                screen.blit(icon_img, (icon_x, icon_y))

    def get_selected_item(self) -> Item | None:
        """Get the selected item and reset selection"""
        selected = self.selected_item
        self.selected_item = None
        return selected

    def is_empty(self) -> bool:
        """Check if there are any items"""
        return len(self.items) == 0

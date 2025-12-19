from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.core.services import input_manager, resource_manager
from typing import Callable, Optional

class BattleActionButton:
    def __init__(self, label: str, x: int, y: int, width: int, height: int,
                 on_click: Callable[[], None] | None = None, is_move_button: bool = False,
                 button_type: str = "default"):
        self.label = label
        self.rect = pg.Rect(x, y, width, height)
        self.on_click = on_click
        self.is_move_button = is_move_button  # Special styling for move buttons
        self.button_type = button_type  # "fight", "item", "switch", "run", or "default"

        # Use larger font for move buttons
        font_size = 16 if is_move_button else 16
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', font_size)

        try:
            # Load appropriate icons based on button type
            icon_size = 28
            if is_move_button:
                # Move buttons use sword icons
                self.icon_default = resource_manager.get_image("ingame_ui/options1.png")
                self.icon_hover = resource_manager.get_image("ingame_ui/options5.png")
                self.icon_default = pg.transform.scale(self.icon_default, (icon_size, icon_size))
                self.icon_hover = pg.transform.scale(self.icon_hover, (icon_size, icon_size))
            elif button_type == "fight":
                # Fight button uses sword icons (options1 and options5)
                self.icon_default = resource_manager.get_image("ingame_ui/options1.png")
                self.icon_hover = resource_manager.get_image("ingame_ui/options5.png")
                self.icon_default = pg.transform.scale(self.icon_default, (icon_size, icon_size))
                self.icon_hover = pg.transform.scale(self.icon_hover, (icon_size, icon_size))
            elif button_type == "item":
                # Item button uses potion icons (options4 and options6)
                self.icon_default = resource_manager.get_image("ingame_ui/options4.png")
                self.icon_hover = resource_manager.get_image("ingame_ui/options6.png")
                self.icon_default = pg.transform.scale(self.icon_default, (icon_size, icon_size))
                self.icon_hover = pg.transform.scale(self.icon_hover, (icon_size, icon_size))
            elif button_type == "switch":
                # Switch button uses pokeball icons (options3 and options7)
                self.icon_default = resource_manager.get_image("ingame_ui/options3.png")
                self.icon_hover = resource_manager.get_image("ingame_ui/options7.png")
                self.icon_default = pg.transform.scale(self.icon_default, (icon_size, icon_size))
                self.icon_hover = pg.transform.scale(self.icon_hover, (icon_size, icon_size))
            else:
                # Default or Run button - no icon
                self.icon_default = None
                self.icon_hover = None
        except:
            self.icon_default = None
            self.icon_hover = None

        self.is_hovered = False

    def update(self, dt: float) -> None:
        mouse_pos = input_manager.mouse_pos
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered and input_manager.mouse_pressed(1):
            if self.on_click:
                self.on_click()

    def draw(self, screen: pg.Surface) -> None:
        # All buttons now use the same styled frame box design
        bg_color = (40, 40, 40)  # Dark background
        border_color = (255, 200, 100) if self.is_hovered else (200, 200, 200)  # Gold when hovered
        border_width = 3 if self.is_hovered else 2

        # Background
        pg.draw.rect(screen, bg_color, self.rect, border_radius=5)
        # Border
        pg.draw.rect(screen, border_color, self.rect, border_width, border_radius=5)

        # Draw icon on the left (if available)
        if self.icon_default:
            icon = self.icon_hover if self.is_hovered else self.icon_default
            icon_x = self.rect.x + 6  # 6px padding from left
            icon_y = self.rect.centery - icon.get_height() // 2  # Center vertically
            screen.blit(icon, (icon_x, icon_y))

            # Draw text (offset to the right to make room for icon)
            text_color = (255, 255, 255)
            text_x_offset = 45  # Offset text to the right of the icon (more spacing)

            label_text = self._font.render(self.label, True, text_color)
            text_rect = label_text.get_rect(
                centerx=self.rect.centerx + text_x_offset // 2,
                centery=self.rect.centery
            )
            screen.blit(label_text, text_rect)
        else:
            # No icon - center text
            text_color = (255, 255, 255)
            label_text = self._font.render(self.label, True, text_color)
            text_rect = label_text.get_rect(center=self.rect.center)
            screen.blit(label_text, text_rect)

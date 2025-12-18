from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.utils import Position, GameSettings
from .component import UIComponent

class NavigationPanel(UIComponent):
    """Panel for selecting navigation destinations and displaying routes"""

    def __init__(self, x: int, y: int, width: int = 400, height: int = 300, on_exit=None, on_navigate=None, current_map_name: str = "map.tmx"):
        self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 40)
        self._button_font = pg.font.Font('assets/fonts/Minecraft.ttf', 20)

        self.on_navigate = on_navigate

        self.title_surf = self._font.render("NAVIGATION", True, (0, 0, 0))

        # Exit button
        margin = 12
        btn_w, btn_h = 50, 50
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            x + width - btn_w - margin, y + margin, btn_w, btn_h,
            on_exit
        )

        # Navigation destinations - different for each map
        self.destinations = self._get_destinations_for_map(current_map_name)

        # Create navigation buttons
        self.nav_buttons = []
        button_y = y + 80
        button_spacing = 70

        for i, dest in enumerate(self.destinations):
            btn_x = x + 50
            btn_y = button_y + i * button_spacing
            btn_w = width - 100
            btn_h = 60

            # Create button with callback that passes the destination
            button = Button(
                "UI/raw/UI_Flat_Frame03a.png",  # Normal state
                "UI/raw/UI_Flat_Frame03a.png",  # Hover state
                btn_x, btn_y, btn_w, btn_h,
                lambda d=dest: self._on_destination_selected(d)
            )

            self.nav_buttons.append({
                "button": button,
                "destination": dest,
                "rect": pg.Rect(btn_x, btn_y, btn_w, btn_h)
            })

    def _get_destinations_for_map(self, map_name: str) -> list[dict]:
        """
        Get navigation destinations for a specific map.

        Args:
            map_name: Name of the current map (e.g., "map.tmx", "new_map.tmx")

        Returns:
            List of destination dictionaries with name and position
        """
        if map_name == "new_map.tmx":
            # Destinations for new_map
            # Boss House gate is at (53, 14)
            return [
                {"name": "Stone Gate (Exit)", "pos": Position(36 * GameSettings.TILE_SIZE, 18 * GameSettings.TILE_SIZE)},
                {"name": "Boss House", "pos": Position(53 * GameSettings.TILE_SIZE, 14 * GameSettings.TILE_SIZE)},
            ]
        elif map_name == "map.tmx":
            # Destinations for main map
            # Note: Shop position is set to one tile below the NPC (48, 15 instead of 48, 14)
            # so the path doesn't try to go ON TOP of the NPC
            return [
                {"name": "Stone Gate (North)", "pos": Position(35 * GameSettings.TILE_SIZE, 18 * GameSettings.TILE_SIZE)},
                {"name": "Shop", "pos": Position(48 * GameSettings.TILE_SIZE, 15 * GameSettings.TILE_SIZE)},
            ]
        else:
            # Default destinations for other maps
            return [
                {"name": "Map Center", "pos": Position(30 * GameSettings.TILE_SIZE, 20 * GameSettings.TILE_SIZE)},
            ]

    def _on_destination_selected(self, destination: dict) -> None:
        """Called when a destination button is clicked"""
        if self.on_navigate:
            self.on_navigate(destination["pos"])

    def update(self, dt: float) -> None:
        from src.core.services import input_manager

        self.exit_button.update(dt)

        # Update navigation buttons
        for nav_btn in self.nav_buttons:
            nav_btn["button"].update(dt)

    def draw(self, screen: pg.Surface) -> None:
        # Draw base panel
        screen.blit(self.sprite.image, self.rect)

        # Add overlay
        overlay = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        overlay.fill((100, 150, 255, 40))  # Blue tint for navigation
        screen.blit(overlay, self.rect)

        # Draw title with shadow
        shadow_surf = self._font.render("NAVIGATION", True, (40, 60, 100))
        screen.blit(shadow_surf, (self.rect.x + 18, self.rect.y + 18))
        screen.blit(self.title_surf, (self.rect.x + 16, self.rect.y + 16))

        # Draw navigation destination buttons
        for nav_btn in self.nav_buttons:
            rect = nav_btn["rect"]
            dest = nav_btn["destination"]

            # Draw button background
            pg.draw.rect(screen, (200, 220, 240), rect, border_radius=8)
            pg.draw.rect(screen, (100, 140, 180), rect, 3, border_radius=8)

            # Check if mouse is hovering
            from src.core.services import input_manager
            mouse_pos = input_manager.mouse_pos
            if rect.collidepoint(mouse_pos):
                # Draw hover effect
                hover_surf = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
                hover_surf.fill((255, 255, 255, 50))
                screen.blit(hover_surf, rect)

            # Draw destination name
            name_text = self._button_font.render(dest["name"], True, (40, 40, 80))
            text_rect = name_text.get_rect(center=rect.center)
            screen.blit(name_text, text_rect)

        self.exit_button.draw(screen)

    def set_exit_callback(self, callback) -> None:
        self.exit_button.on_click = callback

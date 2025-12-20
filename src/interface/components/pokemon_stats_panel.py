from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.utils.definition import Monster
from src.interface.components.status_icon import StatusIcon

class PokemonStatsPanel:
    monster: Monster
    rect: pg.Rect
    _font: pg.font.Font
    _small_font: pg.font.Font
    _bg_sprite: Sprite
    status_icon: StatusIcon | None
    attack_boost: float
    defense_boost: float

    def __init__(self, monster: Monster, x: int, y: int, width: int = 208, height: int = 130, attack_boost: float = 1.0, defense_boost: float = 1.0):
        self.monster = monster
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 18)
        self._small_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
        self.attack_boost = attack_boost
        self.defense_boost = defense_boost

        # Initialize status icon
        status = monster.get("status", None)
        if status:
            # Position status icon in top-right corner of panel
            icon_x = x + width - 33
            icon_y = y + 33
            self.status_icon = StatusIcon(status, icon_x, icon_y, size=26)
        else:
            self.status_icon = None

        try:
            self._bg_sprite = Sprite("UI/raw/UI_Flat_Banner03a.png", (width, height))
        except:
            self._bg_sprite = None

        try:
            # Load sprite and check if it needs to be cropped (for dual-view sprites)
            temp_sprite = Sprite(monster["sprite_path"])
            sprite_img = temp_sprite.image

            # Check if this is a dual-view sprite (width is roughly 2x height)
            width, height = sprite_img.get_size()
            if width > height * 1.5:  # Dual-view sprite (front + back)
                # Extract only the left half (front view)
                half_width = width // 2
                front_view = sprite_img.subsurface(pg.Rect(0, 0, half_width, height))
                # Scale the front view
                self.sprite_image = pg.transform.smoothscale(front_view, (65, 65))
                self.sprite = None  # We'll use sprite_image directly
            else:
                # Single view sprite, use as-is
                self.sprite = Sprite(monster["sprite_path"], (65, 65))
                self.sprite_image = None
        except Exception as e:
            self.sprite = None
            self.sprite_image = None

    def update(self, dt: float) -> None:
        # Update status icon animation
        if self.status_icon:
            self.status_icon.update(dt)
    
    def update_pokemon(self, monster: Monster) -> None:
        """Update the displayed pokemon data and reload sprite"""
        self.monster = monster

        # Update status icon
        status = monster.get("status", None)
        if status:
            icon_x = self.rect.x + self.rect.width - 33
            icon_y = self.rect.y + 33
            self.status_icon = StatusIcon(status, icon_x, icon_y, size=26)
        else:
            self.status_icon = None

        # Reload sprite for the new Pokemon
        try:
            # Load sprite and check if it needs to be cropped (for dual-view sprites)
            temp_sprite = Sprite(monster["sprite_path"])
            sprite_img = temp_sprite.image

            # Check if this is a dual-view sprite (width is roughly 2x height)
            width, height = sprite_img.get_size()
            if width > height * 1.5:  # Dual-view sprite (front + back)
                # Extract only the left half (front view)
                half_width = width // 2
                front_view = sprite_img.subsurface(pg.Rect(0, 0, half_width, height))
                # Scale the front view
                self.sprite_image = pg.transform.smoothscale(front_view, (65, 65))
                self.sprite = None  # We'll use sprite_image directly
            else:
                # Single view sprite, use as-is
                self.sprite = Sprite(monster["sprite_path"], (65, 65))
                self.sprite_image = None
        except Exception as e:
            self.sprite = None
            self.sprite_image = None

    def draw(self, screen: pg.Surface) -> None:
        # Modern gradient background
        # Create a layered design with rounded corners

        # Shadow layer
        shadow_rect = pg.Rect(self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height)
        pg.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=16)

        # Main background - dark gradient effect
        pg.draw.rect(screen, (40, 45, 55), self.rect, border_radius=16)

        # Top highlight strip
        highlight_rect = pg.Rect(self.rect.x, self.rect.y, self.rect.width, 33)
        pg.draw.rect(screen, (60, 70, 85), highlight_rect, border_radius=16)
        pg.draw.rect(screen, (60, 70, 85), (self.rect.x, self.rect.y + 16, self.rect.width, 17))

        # Border
        pg.draw.rect(screen, (100, 120, 140), self.rect, 3, border_radius=16)

        # Inner glow effect
        inner_glow = pg.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width - 6, self.rect.height - 6)
        pg.draw.rect(screen, (70, 85, 105), inner_glow, 1, border_radius=14)

        # Draw sprite (either extracted front view or original)
        if self.sprite_image:
            screen.blit(self.sprite_image, (self.rect.x + 7, self.rect.y + 7))
        elif self.sprite:
            screen.blit(self.sprite.image, (self.rect.x + 7, self.rect.y + 7))

        name_text = self._font.render(self.monster["name"], True, (255, 255, 255))
        screen.blit(name_text, (self.rect.x + 78, self.rect.y + 7))

        # Draw type badge next to level
        pokemon_type = self.monster.get("type", "None")
        level_text = self._small_font.render(f"Lv.{self.monster['level']}", True, (220, 220, 220))
        screen.blit(level_text, (self.rect.x + 78, self.rect.y + 29))

        # Type colors
        type_colors = {
            "Fire": (255, 100, 50),
            "Water": (80, 144, 255),
            "Ice": (150, 230, 255),
            "Wind": (160, 255, 160),
            "Light": (255, 255, 100),
            "Slash": (200, 200, 200),
            "None": (150, 150, 150)
        }
        type_color = type_colors.get(pokemon_type, (150, 150, 150))

        # Draw type badge (small rounded rect with type name)
        type_badge_x = self.rect.x + 137
        type_badge_y = self.rect.y + 29
        type_badge_width = 65
        type_badge_height = 18

        pg.draw.rect(screen, type_color, (type_badge_x, type_badge_y, type_badge_width, type_badge_height), border_radius=4)
        pg.draw.rect(screen, (0, 0, 0), (type_badge_x, type_badge_y, type_badge_width, type_badge_height), 1, border_radius=4)

        type_text = self._small_font.render(pokemon_type, True, (0, 0, 0))
        type_text_rect = type_text.get_rect(center=(type_badge_x + type_badge_width // 2, type_badge_y + type_badge_height // 2))
        screen.blit(type_text, type_text_rect)

        hp_ratio = self.monster["hp"] / self.monster["max_hp"]
        hp_color = (0, 255, 0) if hp_ratio > 0.3 else (255, 165, 0) if hp_ratio > 0.1 else (255, 0, 0)
        hp_bar_w = int((self.rect.width - 91) * hp_ratio)

        pg.draw.rect(screen, hp_color, (self.rect.x + 78, self.rect.y + 52, hp_bar_w, 13))
        pg.draw.rect(screen, (0, 0, 0), (self.rect.x + 78, self.rect.y + 52, self.rect.width - 91, 13), 1)

        hp_text = self._small_font.render(f"HP: {self.monster['hp']}/{self.monster['max_hp']}", True, (220, 220, 220))
        screen.blit(hp_text, (self.rect.x + 78, self.rect.y + 68))

        # Display attack and defense stats with boost indicators
        attack = self.monster.get("attack", 10)
        defense = self.monster.get("defense", 10)

        # Calculate boosted values
        attack_display = int(attack * self.attack_boost)
        defense_display = int(defense * self.defense_boost)

        # Show base stats
        if self.attack_boost > 1.0:
            # Show boost in green with arrow
            stats_text = self._small_font.render(f"ATK:", True, (220, 220, 220))
            screen.blit(stats_text, (self.rect.x + 78, self.rect.y + 91))
            boost_text = self._small_font.render(f"{attack_display}", True, (100, 255, 100))
            screen.blit(boost_text, (self.rect.x + 78 + stats_text.get_width(), self.rect.y + 91))

            def_text = self._small_font.render(f" DEF:{defense}", True, (220, 220, 220))
            screen.blit(def_text, (self.rect.x + 78 + stats_text.get_width() + boost_text.get_width(), self.rect.y + 91))
        elif self.defense_boost > 1.0:
            # Show defense boost in green
            stats_text = self._small_font.render(f"ATK:{attack} DEF:", True, (220, 220, 220))
            screen.blit(stats_text, (self.rect.x + 78, self.rect.y + 91))
            boost_text = self._small_font.render(f"{defense_display}", True, (100, 255, 100))
            screen.blit(boost_text, (self.rect.x + 78 + stats_text.get_width(), self.rect.y + 91))
        else:
            # Normal display
            stats_text = self._small_font.render(f"ATK:{attack} DEF:{defense}", True, (220, 220, 220))
            screen.blit(stats_text, (self.rect.x + 78, self.rect.y + 91))

        # Draw status icon if present
        if self.status_icon:
            self.status_icon.draw(screen)

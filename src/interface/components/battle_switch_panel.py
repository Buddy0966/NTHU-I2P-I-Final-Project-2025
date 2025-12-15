from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.battle_action_button import BattleActionButton
from src.utils.definition import Monster
from src.core.services import input_manager


class BattleSwitchPanel:
    """Panel to select Pokemon to switch to during battle"""

    def __init__(self, monsters: list[Monster], current_pokemon_index: int, x: int, y: int, width: int = 400, height: int = 450):
        self.monsters = monsters
        self.current_pokemon_index = current_pokemon_index
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self._title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 20)

        # Background sprite
        try:
            self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        except:
            self.sprite = None

        self.title_surf = self._title_font.render("Switch Pokemon", True, (255, 255, 255))

        # Cache pokemon sprites
        self._pokemon_sprites = {}
        for monster in monsters:
            try:
                sprite_path = monster.get("sprite_path", "")
                if sprite_path:
                    # Load the sprite to check if it's a dual-view sprite
                    temp_sprite = Sprite(sprite_path)
                    sprite_img = temp_sprite.image

                    # Check if this is a dual-view sprite (width is roughly 2x height)
                    width_img, height_img = sprite_img.get_size()
                    if width_img > height_img * 1.5:  # Dual-view sprite (front + back)
                        # Extract only the left half (front view)
                        half_width = width_img // 2
                        front_view = sprite_img.subsurface(pg.Rect(0, 0, half_width, height_img))
                        # Scale the front view to 50x50
                        scaled_front = pg.transform.smoothscale(front_view, (50, 50))
                        # Create a surface to store it
                        self._pokemon_sprites[monster["name"]] = type('obj', (object,), {'image': scaled_front})()
                    else:
                        # Single view sprite, scale it normally
                        self._pokemon_sprites[monster["name"]] = Sprite(sprite_path, (50, 50))
            except:
                self._pokemon_sprites[monster["name"]] = None

        # Create Pokemon selection buttons
        self.pokemon_buttons: list[tuple[BattleActionButton, int]] = []
        btn_h = 70
        btn_w = width - 40
        start_y = y + 60

        for i, monster in enumerate(monsters):
            # Skip current pokemon (can't switch to the one already in battle)
            if i == current_pokemon_index:
                continue

            # Skip fainted pokemon (HP <= 0)
            if monster.get("hp", 0) <= 0:
                continue

            btn_y = start_y + len(self.pokemon_buttons) * (btn_h + 10)
            if btn_y + btn_h > y + height - 20:
                break

            # Create button label with Pokemon name, level, and HP
            hp = monster.get("hp", 0)
            max_hp = monster.get("max_hp", 100)
            level = monster.get("level", 1)
            label = f"{monster['name']} Lv.{level}"

            btn = BattleActionButton(
                label,
                x + 20,
                btn_y,
                btn_w,
                btn_h,
                lambda idx=i: self._on_pokemon_select(idx)
            )
            self.pokemon_buttons.append((btn, i))

        self.selected_pokemon_index: int | None = None

    def _on_pokemon_select(self, pokemon_index: int) -> None:
        """Called when a Pokemon is selected"""
        self.selected_pokemon_index = pokemon_index

    def update(self, dt: float) -> None:
        """Update all Pokemon buttons"""
        for btn, _ in self.pokemon_buttons:
            btn.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw the switch panel"""
        # Draw background
        if self.sprite:
            screen.blit(self.sprite.image, self.rect)
        else:
            pg.draw.rect(screen, (50, 50, 50), self.rect)
            pg.draw.rect(screen, (255, 255, 255), self.rect, 2)

        # Draw title
        screen.blit(self.title_surf, (self.rect.x + 20, self.rect.y + 15))

        # Draw Pokemon buttons with sprites and HP bars
        for btn, pokemon_idx in self.pokemon_buttons:
            monster = self.monsters[pokemon_idx]
            btn.draw(screen)

            # Draw Pokemon sprite on button
            if monster["name"] in self._pokemon_sprites and self._pokemon_sprites[monster["name"]]:
                icon_x = btn.rect.x + 10
                icon_y = btn.rect.y + (btn.rect.height - 50) // 2
                screen.blit(self._pokemon_sprites[monster["name"]].image, (icon_x, icon_y))

            # Draw HP bar
            hp = monster.get("hp", 0)
            max_hp = monster.get("max_hp", 100)
            hp_ratio = hp / max_hp if max_hp > 0 else 0

            hp_bar_x = btn.rect.x + 70
            hp_bar_y = btn.rect.y + 40
            hp_bar_width = btn.rect.width - 90
            hp_bar_height = 12

            # HP bar background
            pg.draw.rect(screen, (100, 100, 100), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), border_radius=3)

            # HP bar fill
            if hp_ratio > 0:
                hp_color = (100, 200, 80) if hp_ratio > 0.5 else (255, 200, 60) if hp_ratio > 0.25 else (220, 80, 60)
                hp_fill_width = int(hp_bar_width * hp_ratio)
                pg.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, hp_fill_width, hp_bar_height), border_radius=3)

            # HP bar border
            pg.draw.rect(screen, (255, 255, 255), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 1, border_radius=3)

            # Draw HP text
            hp_text = self._font.render(f"HP: {hp}/{max_hp}", True, (255, 255, 255))
            screen.blit(hp_text, (hp_bar_x, hp_bar_y + 15))

    def get_selected_pokemon_index(self) -> int | None:
        """Get the selected Pokemon index and reset selection"""
        selected = self.selected_pokemon_index
        self.selected_pokemon_index = None
        return selected

    def is_empty(self) -> bool:
        """Check if there are any available Pokemon to switch to"""
        return len(self.pokemon_buttons) == 0

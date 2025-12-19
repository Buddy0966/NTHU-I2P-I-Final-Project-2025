from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.battle_action_button import BattleActionButton
from src.utils.definition import Monster
from src.core.services import input_manager


class BattleSwitchPanel:
    """Panel to select Pokemon to switch to during battle with scrolling support"""

    def __init__(self, monsters: list[Monster], current_pokemon_index: int, x: int, y: int, width: int = 500, height: int = 500):
        self.monsters = monsters
        self.current_pokemon_index = current_pokemon_index
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self._title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 22)

        # Background sprite with transparency
        try:
            self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        except:
            self.sprite = None

        self.title_surf = self._title_font.render("Choose Pokemon", True, (255, 255, 100))

        # Scrolling parameters
        self.scroll_offset = 0
        self.max_scroll = 0

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
                        # Scale the front view to 60x60 (larger for better visibility)
                        scaled_front = pg.transform.smoothscale(front_view, (60, 60))
                        # Create a surface to store it
                        self._pokemon_sprites[monster["name"]] = type('obj', (object,), {'image': scaled_front})()
                    else:
                        # Single view sprite, scale it normally
                        self._pokemon_sprites[monster["name"]] = Sprite(sprite_path, (60, 60))
            except:
                self._pokemon_sprites[monster["name"]] = None

        # Create Pokemon selection buttons (all of them, not just visible ones)
        self.pokemon_buttons: list[tuple[BattleActionButton, int]] = []
        btn_h = 80
        btn_w = width - 60
        start_y = y + 70

        for i, monster in enumerate(monsters):
            # Skip current pokemon (can't switch to the one already in battle)
            if i == current_pokemon_index:
                continue

            # Skip fainted pokemon (HP <= 0)
            if monster.get("hp", 0) <= 0:
                continue

            # Create all buttons regardless of position (we'll handle scrolling in draw)
            btn_y = start_y + len(self.pokemon_buttons) * (btn_h + 10)

            # Create button label with Pokemon name, level, and HP
            hp = monster.get("hp", 0)
            max_hp = monster.get("max_hp", 100)
            level = monster.get("level", 1)
            label = f"{monster['name']} Lv.{level}"

            btn = BattleActionButton(
                label,
                x + 30,
                btn_y,
                btn_w,
                btn_h,
                lambda idx=i: self._on_pokemon_select(idx)
            )
            self.pokemon_buttons.append((btn, i))

        # Calculate max scroll based on total content height
        if len(self.pokemon_buttons) > 0:
            total_content_height = len(self.pokemon_buttons) * (btn_h + 10)
            visible_area_height = height - 100  # Account for title and padding
            self.max_scroll = max(0, total_content_height - visible_area_height)

        self.selected_pokemon_index: int | None = None

    def _on_pokemon_select(self, pokemon_index: int) -> None:
        """Called when a Pokemon is selected"""
        self.selected_pokemon_index = pokemon_index

    def update(self, dt: float) -> None:
        """Update all Pokemon buttons and handle scrolling"""
        # Handle mouse wheel scrolling (same as bag panel)
        mouse_pos = input_manager.mouse_pos
        if self.rect.collidepoint(mouse_pos):
            if input_manager.mouse_wheel != 0:
                scroll_amount = input_manager.mouse_wheel * 40  # 40 pixels per scroll
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - scroll_amount))

        # Also support arrow keys for scrolling
        scroll_amount = 0
        if input_manager.key_down(pg.K_UP):
            scroll_amount = 40
        elif input_manager.key_down(pg.K_DOWN):
            scroll_amount = -40

        if scroll_amount != 0:
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - scroll_amount))

        # Update button positions based on scroll offset
        for i, (btn, _) in enumerate(self.pokemon_buttons):
            new_y = self.rect.y + 70 + i * 90 - self.scroll_offset
            btn.rect.y = new_y

            # Only update buttons that are visible
            if self.rect.y + 60 < new_y + btn.rect.height and new_y < self.rect.y + self.rect.height - 20:
                btn.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw the switch panel with scrolling and improved visuals"""
        # Draw semi-transparent background overlay
        overlay = pg.Surface((screen.get_width(), screen.get_height()), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Draw main panel background
        if self.sprite:
            screen.blit(self.sprite.image, self.rect)
        else:
            # Gradient-like background
            pg.draw.rect(screen, (40, 40, 60), self.rect, border_radius=10)
            pg.draw.rect(screen, (100, 100, 150), self.rect, 3, border_radius=10)

        # Draw title with shadow effect
        title_shadow = self._title_font.render("Choose Pokemon", True, (0, 0, 0))
        screen.blit(title_shadow, (self.rect.x + 22, self.rect.y + 17))
        screen.blit(self.title_surf, (self.rect.x + 20, self.rect.y + 15))

        # Draw scroll hint at top
        hint_font = pg.font.Font('assets/fonts/Minecraft.ttf', 11)
        if self.max_scroll > 0:
            hint_text = hint_font.render("Scroll: Mouse Wheel / UP-DOWN", True, (180, 180, 120))
            screen.blit(hint_text, (self.rect.x + 20, self.rect.y + 45))

        # Create a clipping area for scrollable content
        content_rect = pg.Rect(self.rect.x + 15, self.rect.y + 65, self.rect.width - 35, self.rect.height - 75)
        screen.set_clip(content_rect)

        # Draw Pokemon buttons with sprites and HP bars
        for btn, pokemon_idx in self.pokemon_buttons:
            # Only draw buttons that are visible in the clipped area
            if not (btn.rect.y + btn.rect.height < content_rect.y or btn.rect.y > content_rect.y + content_rect.height):
                monster = self.monsters[pokemon_idx]

                # Draw button background without text (we'll draw custom layout)
                # Draw card-style background similar to bag panel
                card_bg_color = (245, 235, 210)  # Cream color
                card_border_color = (200, 160, 100)  # Dark border

                pg.draw.rect(screen, card_border_color, btn.rect, border_radius=8)
                pg.draw.rect(screen, card_bg_color, btn.rect.inflate(-6, -6), border_radius=6)
                pg.draw.rect(screen, (220, 180, 120), btn.rect.inflate(-4, -4), 2, border_radius=7)

                # Draw Pokemon sprite on button
                sprite_key = monster["name"]
                if sprite_key in self._pokemon_sprites and self._pokemon_sprites[sprite_key]:
                    icon_x = btn.rect.x + 10
                    icon_y = btn.rect.y + (btn.rect.height - 60) // 2
                    screen.blit(self._pokemon_sprites[sprite_key].image, (icon_x, icon_y))

                # Draw Pokemon name (darker color for cream background)
                name_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
                name_text = name_font.render(monster["name"], True, (60, 40, 20))
                screen.blit(name_text, (btn.rect.x + 80, btn.rect.y + 8))

                # Draw level
                level_text = self._font.render(f"Lv.{monster.get('level', 1)}", True, (100, 80, 60))
                screen.blit(level_text, (btn.rect.x + 80, btn.rect.y + 28))

                # Draw HP bar
                hp = monster.get("hp", 0)
                max_hp = monster.get("max_hp", 100)
                hp_ratio = hp / max_hp if max_hp > 0 else 0

                hp_bar_x = btn.rect.x + 80
                hp_bar_y = btn.rect.y + 48
                hp_bar_width = btn.rect.width - 95
                hp_bar_height = 14

                # HP bar background (darker for cream background)
                pg.draw.rect(screen, (180, 150, 120), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), border_radius=5)

                # HP bar fill with gradient colors
                if hp_ratio > 0:
                    if hp_ratio > 0.5:
                        hp_color = (100, 200, 80)  # Green
                    elif hp_ratio > 0.25:
                        hp_color = (255, 200, 60)  # Yellow
                    else:
                        hp_color = (220, 80, 60)   # Red

                    hp_fill_width = int(hp_bar_width * hp_ratio)
                    pg.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, hp_fill_width, hp_bar_height), border_radius=5)

                # HP bar border (darker)
                pg.draw.rect(screen, (120, 90, 60), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2, border_radius=5)

                # Draw HP text below the bar (darker color)
                hp_text = self._font.render(f"HP: {hp}/{max_hp}", True, (80, 60, 40))
                screen.blit(hp_text, (hp_bar_x, hp_bar_y + 16))

        # Remove clipping
        screen.set_clip(None)

        # Draw scroll indicator if there's content to scroll
        if self.max_scroll > 0:
            # Scroll bar background
            scrollbar_x = self.rect.x + self.rect.width - 18
            scrollbar_y = self.rect.y + 65
            scrollbar_height = self.rect.height - 75
            pg.draw.rect(screen, (60, 60, 60), (scrollbar_x, scrollbar_y, 12, scrollbar_height), border_radius=6)

            # Scroll bar thumb
            scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            thumb_height = max(30, int(scrollbar_height * 0.2))
            thumb_y = scrollbar_y + int((scrollbar_height - thumb_height) * scroll_ratio)
            pg.draw.rect(screen, (150, 150, 200), (scrollbar_x, thumb_y, 12, thumb_height), border_radius=6)

    def get_selected_pokemon_index(self) -> int | None:
        """Get the selected Pokemon index and reset selection"""
        selected = self.selected_pokemon_index
        self.selected_pokemon_index = None
        return selected

    def is_empty(self) -> bool:
        """Check if there are any available Pokemon to switch to"""
        return len(self.pokemon_buttons) == 0

from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.utils.definition import Item, Monster
from .component import UIComponent

class BagPanel(UIComponent):
    def __init__(self, items: list[Item], x: int, y: int, width: int = 700, height: int = 500, on_exit=None, monsters: list[Monster] | None = None):
        self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 40)
        self._item_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
        self._pokemon_font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        self.items = items
        self.monsters = monsters if monsters else []

        self.title_surf = self._font.render("BAG", True, (0, 0, 0))

        # Evolution panel (shown when user clicks on a pokemon)
        self.evolution_panel = None
        self.selected_pokemon_index = None

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
        
        # Scrolling parameters
        self.pokemon_scroll_offset = 0
        self.item_scroll_offset = 0
        self.pokemon_line_height = 95  # Increased spacing for bigger panel
        self.item_line_height = 65
        self.scroll_speed = 30  # pixels per scroll

        # Calculate content heights
        self.pokemon_content_height = len(self.monsters) * self.pokemon_line_height
        self.item_content_height = len(self.items) * self.item_line_height

        # Viewport dimensions (height available for scrollable content)
        self.pokemon_viewport_height = self.rect.height - 100
        self.item_viewport_height = self.rect.height - 100

    def update(self, dt: float) -> None:
        from src.core.services import input_manager

        # If evolution panel is shown, only update that
        if self.evolution_panel:
            self.evolution_panel.update(dt)
            return

        self.exit_button.update(dt)
        # Update pokemon sprites in case monsters list changed
        self._update_pokemon_sprites()

        # Handle pokemon clicks for evolution and level-up
        if input_manager.mouse_pressed(1):  # Left click (button 1)
            mouse_pos = input_manager.mouse_pos
            pokemon_x = self.rect.x + 20
            pokemon_y = self.rect.y + 70

            for i, monster in enumerate(self.monsters):
                y_pos = pokemon_y + i * self.pokemon_line_height - self.pokemon_scroll_offset
                card_rect = pg.Rect(pokemon_x, y_pos, 300, 85)

                if card_rect.collidepoint(mouse_pos) and self.rect.collidepoint(mouse_pos):
                    # Check if level-up button was clicked (next to HP bar)
                    levelup_button_rect = pg.Rect(pokemon_x + 210, y_pos + 48, 80, 28)

                    if levelup_button_rect.collidepoint(mouse_pos):
                        # Level up this pokemon
                        self._levelup_pokemon(i)
                    else:
                        # Open evolution panel for this pokemon
                        self._show_evolution_panel(i)
                    break

        # Handle scroll input
        # Check if mouse is over this panel
        mouse_pos = input_manager.mouse_pos
        if self.rect.collidepoint(mouse_pos):
            # Handle mouse wheel scrolling
            if input_manager.mouse_wheel != 0:
                scroll_amount = input_manager.mouse_wheel * self.scroll_speed
                
                # Scroll pokemon
                max_pokemon_offset = max(0, self.pokemon_content_height - self.pokemon_viewport_height)
                self.pokemon_scroll_offset = max(0, min(max_pokemon_offset, self.pokemon_scroll_offset - scroll_amount))
                
                # Scroll items
                max_item_offset = max(0, self.item_content_height - self.item_viewport_height)
                self.item_scroll_offset = max(0, min(max_item_offset, self.item_scroll_offset - scroll_amount))
        
        # Also support arrow keys for scrolling
        scroll_amount = 0
        if input_manager.key_down(pg.K_UP):
            scroll_amount = self.scroll_speed
        elif input_manager.key_down(pg.K_DOWN):
            scroll_amount = -self.scroll_speed
        
        if scroll_amount != 0:
            # Scroll pokemon
            max_pokemon_offset = max(0, self.pokemon_content_height - self.pokemon_viewport_height)
            self.pokemon_scroll_offset = max(0, min(max_pokemon_offset, self.pokemon_scroll_offset + scroll_amount))
            
            # Scroll items
            max_item_offset = max(0, self.item_content_height - self.item_viewport_height)
            self.item_scroll_offset = max(0, min(max_item_offset, self.item_scroll_offset + scroll_amount))
    
    def _update_pokemon_sprites(self) -> None:
        """Update pokemon sprites based on current monsters list"""
        import pygame as pg
        for monster in self.monsters:
            if monster["name"] not in self._pokemon_sprites:
                try:
                    # Use sprite_path (battle sprites) instead of menu_sprite_path
                    sprite_path = monster.get("sprite_path")
                    if not sprite_path:
                        self._pokemon_sprites[monster["name"]] = None
                        continue

                    # Load the sprite to check if it's a dual-view sprite
                    temp_sprite = Sprite(sprite_path)
                    sprite_img = temp_sprite.image

                    # Check if this is a dual-view sprite (width is roughly 2x height)
                    width, height = sprite_img.get_size()
                    if width > height * 1.5:  # Dual-view sprite (front + back)
                        # Extract only the left half (front view)
                        half_width = width // 2
                        front_view = sprite_img.subsurface(pg.Rect(0, 0, half_width, height))
                        # Scale the front view to 60x60
                        scaled_front = pg.transform.smoothscale(front_view, (60, 60))
                        # Create a surface to store it
                        self._pokemon_sprites[monster["name"]] = type('obj', (object,), {'image': scaled_front})()
                    else:
                        # Single view sprite, scale it normally
                        self._pokemon_sprites[monster["name"]] = Sprite(sprite_path, (60, 60))
                except Exception as e:
                    print(f"Error loading sprite for {monster['name']}: {e}")
                    self._pokemon_sprites[monster["name"]] = None

    def _show_evolution_panel(self, pokemon_index: int) -> None:
        """Show evolution panel for selected pokemon"""
        if pokemon_index < 0 or pokemon_index >= len(self.monsters):
            return

        self.selected_pokemon_index = pokemon_index
        pokemon = self.monsters[pokemon_index]

        # Import here to avoid circular imports
        from src.interface.components.evolution_panel import EvolutionPanel
        from src.utils import GameSettings

        # Center the evolution panel
        panel_width = 600
        panel_height = 400
        panel_x = (GameSettings.SCREEN_WIDTH - panel_width) // 2
        panel_y = (GameSettings.SCREEN_HEIGHT - panel_height) // 2

        self.evolution_panel = EvolutionPanel(
            pokemon,
            panel_x,
            panel_y,
            panel_width,
            panel_height,
            on_complete=self._on_evolution_complete,
            on_cancel=self._on_evolution_cancel
        )

    def _on_evolution_complete(self) -> None:
        """Called when evolution is complete"""
        # Refresh pokemon sprites after evolution
        if self.selected_pokemon_index is not None and self.selected_pokemon_index < len(self.monsters):
            evolved_pokemon = self.monsters[self.selected_pokemon_index]
            # Remove old sprite from cache so it reloads
            if evolved_pokemon["name"] in self._pokemon_sprites:
                del self._pokemon_sprites[evolved_pokemon["name"]]

        self.evolution_panel = None
        self.selected_pokemon_index = None
        self._update_pokemon_sprites()

    def _on_evolution_cancel(self) -> None:
        """Called when evolution is cancelled"""
        self.evolution_panel = None
        self.selected_pokemon_index = None

    def _levelup_pokemon(self, pokemon_index: int) -> None:
        """Level up a single pokemon by spending coins"""
        from src.utils.pokemon_data import calculate_levelup_cost
        from src.utils import Logger

        if pokemon_index < 0 or pokemon_index >= len(self.monsters):
            return

        pokemon = self.monsters[pokemon_index]
        current_level = pokemon.get("level", 1)
        levelup_cost = calculate_levelup_cost(current_level)

        # Find coins item
        coins_item = None
        for item in self.items:
            if item.get("name") == "Coins":
                coins_item = item
                break

        # Check if player has enough coins
        if not coins_item or coins_item.get("count", 0) < levelup_cost:
            Logger.warning(f"Not enough coins! Need {levelup_cost} coins, have {coins_item.get('count', 0) if coins_item else 0}")
            return

        # Deduct coins
        coins_item["count"] -= levelup_cost

        # Level up the pokemon
        pokemon["level"] = current_level + 1

        # Increase max HP slightly (5% per level)
        old_max_hp = pokemon.get("max_hp", 100)
        new_max_hp = int(old_max_hp * 1.05)
        pokemon["max_hp"] = new_max_hp

        # Heal by the increased amount
        pokemon["hp"] = min(pokemon.get("hp", 0) + (new_max_hp - old_max_hp), new_max_hp)

        # Log success
        Logger.info(f"{pokemon['name']} leveled up to level {pokemon['level']}! Cost: {levelup_cost} coins")

    def draw(self, screen: pg.Surface) -> None:
        # Draw base panel with gradient-like effect
        screen.blit(self.sprite.image, self.rect)

        # Add a warm orange overlay for that Pokemon feel
        overlay = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        overlay.fill((255, 180, 60, 40))  # Warm orange with transparency
        screen.blit(overlay, self.rect)

        # Draw title with shadow for depth
        shadow_surf = self._font.render("BAG", True, (80, 40, 0))
        screen.blit(shadow_surf, (self.rect.x + 18, self.rect.y + 18))
        screen.blit(self.title_surf, (self.rect.x + 16, self.rect.y + 16))

        # Draw Pokemon section on the left
        pokemon_x = self.rect.x + 20
        pokemon_y = self.rect.y + 70
        pokemon_viewport_y = pokemon_y
        pokemon_viewport_height = self.rect.height - 100

        # Pokemon header - no header needed, similar to reference image
        # pokemon_header = self._pokemon_font.render("Pokemon", True, (0, 0, 0))
        # screen.blit(pokemon_header, (pokemon_x, pokemon_y - 30))
        
        # Debug: Log monsters count
        from src.utils import Logger
        # Logger.debug(f"BagPanel drawing {len(self.monsters)} monsters")
        
        # Create a clip rect for pokemon section to prevent drawing outside viewport
        pokemon_clip_rect = pg.Rect(pokemon_x, pokemon_viewport_y, 320, pokemon_viewport_height)
        old_clip = screen.get_clip()
        screen.set_clip(pokemon_clip_rect)

        for i, monster in enumerate(self.monsters):
            y_pos = pokemon_y + i * self.pokemon_line_height - self.pokemon_scroll_offset

            # Draw Pokemon card background with border (scaled for larger panel)
            card_rect = pg.Rect(pokemon_x, y_pos, 300, 85)

            # Card background - cream/beige color
            card_bg = pg.Surface((300, 85), pg.SRCALPHA)
            card_bg.fill((245, 235, 210, 255))  # Warm cream color

            # Draw rounded rectangle effect with border
            pg.draw.rect(screen, (200, 160, 100), card_rect, border_radius=8)  # Dark border
            pg.draw.rect(screen, (245, 235, 210), card_rect.inflate(-6, -6), border_radius=6)  # Inner cream

            # Add inner border accent (orange/brown)
            pg.draw.rect(screen, (220, 180, 120), card_rect.inflate(-4, -4), 2, border_radius=7)

            # Draw pokemon sprite with slight offset
            if monster["name"] in self._pokemon_sprites and self._pokemon_sprites[monster["name"]]:
                screen.blit(self._pokemon_sprites[monster["name"]].image, (pokemon_x + 10, y_pos + 10))

            # Draw pokemon name with better font
            name_color = (60, 40, 20)  # Dark brown
            name_text = self._item_font.render(monster["name"], True, name_color)
            screen.blit(name_text, (pokemon_x + 85, y_pos + 10))

            # Draw pokemon level
            level_str = f"Lv.{monster.get('level', 1)}"
            level_text = self._pokemon_font.render(level_str, True, (100, 80, 60))
            screen.blit(level_text, (pokemon_x + 85, y_pos + 30))

            # Draw attack and defense stats next to level
            attack_str = f"ATK:{monster.get('attack', 10)}"
            attack_text = self._pokemon_font.render(attack_str, True, (180, 60, 60))
            screen.blit(attack_text, (pokemon_x + 145, y_pos + 30))

            defense_str = f"DEF:{monster.get('defense', 10)}"
            defense_text = self._pokemon_font.render(defense_str, True, (60, 100, 180))
            screen.blit(defense_text, (pokemon_x + 215, y_pos + 30))

            # Draw HP bar with better styling (made narrower to fit level-up button)
            hp_ratio = monster.get("hp", monster.get("max_hp", 100)) / monster.get("max_hp", 100)
            hp_bar_x = pokemon_x + 85
            hp_bar_y = y_pos + 50
            hp_bar_width = 120  # Reduced from 200 to make room for button
            hp_bar_height = 12

            # HP bar background
            pg.draw.rect(screen, (180, 150, 120), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), border_radius=5)

            # HP bar fill with gradient-like effect
            if hp_ratio > 0:
                hp_color = (100, 200, 80) if hp_ratio > 0.5 else (255, 200, 60) if hp_ratio > 0.25 else (220, 80, 60)
                hp_fill_width = int(hp_bar_width * hp_ratio)
                pg.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, hp_fill_width, hp_bar_height), border_radius=5)

            # HP bar border
            pg.draw.rect(screen, (120, 90, 60), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2, border_radius=5)

            # Draw HP text below the bar
            hp_text = self._pokemon_font.render(f"{monster.get('hp', monster.get('max_hp', 100))}/{monster.get('max_hp', 100)}", True, (80, 60, 40))
            screen.blit(hp_text, (pokemon_x + 85, y_pos + 66))

            # Draw level-up button (right side of card, next to HP bar)
            from src.utils.pokemon_data import calculate_levelup_cost
            current_level = monster.get("level", 1)
            levelup_cost = calculate_levelup_cost(current_level)

            # Button positioned next to HP bar
            button_x = pokemon_x + 210  # Right after HP bar (85 + 120 + 5 margin)
            button_y = y_pos + 48  # Aligned with HP bar
            button_width = 80
            button_height = 28
            button_rect = pg.Rect(button_x, button_y, button_width, button_height)

            # Draw button with gold/coin color
            pg.draw.rect(screen, (220, 180, 50), button_rect, border_radius=4)  # Gold background
            pg.draw.rect(screen, (180, 140, 30), button_rect, 2, border_radius=4)  # Dark gold border

            # Draw button text with cost
            button_text = self._pokemon_font.render(f"+Lv ${levelup_cost}", True, (40, 30, 10))
            text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, text_rect)

        screen.set_clip(old_clip)
        
        # Draw pokemon scrollbar with enhanced styling
        if self.pokemon_content_height > self.pokemon_viewport_height:
            scrollbar_x = pokemon_x + 310
            scrollbar_y = pokemon_viewport_y
            scrollbar_width = 10
            scrollbar_height = pokemon_viewport_height

            # Draw scrollbar background with rounded edges
            pg.draw.rect(screen, (200, 170, 140), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=5)

            # Calculate scrollbar thumb position and size
            thumb_height = max(20, (self.pokemon_viewport_height / self.pokemon_content_height) * scrollbar_height)
            thumb_y = scrollbar_y + (self.pokemon_scroll_offset / self.pokemon_content_height) * scrollbar_height

            # Draw scrollbar thumb with gradient-like effect
            pg.draw.rect(screen, (140, 110, 80), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=5)
            pg.draw.rect(screen, (100, 80, 60), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), 2, border_radius=5)

        # Draw Items section on the right (scaled for larger panel)
        item_x = self.rect.x + 350
        item_y = self.rect.y + 70
        item_viewport_y = item_y
        item_viewport_height = self.rect.height - 100

        # Create a clip rect for items section
        item_clip_rect = pg.Rect(item_x, item_viewport_y, 330, item_viewport_height)
        screen.set_clip(item_clip_rect)

        for i, item in enumerate(self.items):
            y_pos = item_y + i * self.item_line_height - self.item_scroll_offset

            # Draw item row with subtle background (scaled for larger panel)
            item_row_rect = pg.Rect(item_x, y_pos, 320, 55)

            # Alternating row colors for better readability
            row_color = (255, 250, 240) if i % 2 == 0 else (250, 240, 220)
            pg.draw.rect(screen, row_color, item_row_rect, border_radius=6)

            # Item border
            pg.draw.rect(screen, (200, 170, 130), item_row_rect, 2, border_radius=6)

            # Draw item sprite (slightly larger)
            if item["name"] in self._item_sprites and self._item_sprites[item["name"]]:
                sprite_size = 45
                scaled_sprite = pg.transform.scale(self._item_sprites[item["name"]].image, (sprite_size, sprite_size))
                screen.blit(scaled_sprite, (item_x + 5, y_pos + 5))

            # Draw item name with better styling
            name_text = self._item_font.render(item["name"], True, (60, 40, 20))
            screen.blit(name_text, (item_x + 60, y_pos + 12))

            # Draw count with distinctive styling
            count_text = self._item_font.render(f"x{item['count']}", True, (120, 90, 60))
            count_text_rect = count_text.get_rect()
            count_x = item_x + 300 - count_text_rect.width
            screen.blit(count_text, (count_x, y_pos + 22))
        
        screen.set_clip(old_clip)
        
        # Draw items scrollbar with enhanced styling
        if self.item_content_height > self.item_viewport_height:
            scrollbar_x = item_x + 320
            scrollbar_y = item_viewport_y
            scrollbar_width = 10
            scrollbar_height = item_viewport_height

            # Draw scrollbar background with rounded edges
            pg.draw.rect(screen, (200, 170, 140), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=5)

            # Calculate scrollbar thumb position and size
            thumb_height = max(20, (self.item_viewport_height / self.item_content_height) * scrollbar_height)
            thumb_y = scrollbar_y + (self.item_scroll_offset / self.item_content_height) * scrollbar_height

            # Draw scrollbar thumb with gradient-like effect
            pg.draw.rect(screen, (140, 110, 80), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=5)
            pg.draw.rect(screen, (100, 80, 60), (scrollbar_x, thumb_y, scrollbar_width, thumb_height), 2, border_radius=5)

        self.exit_button.draw(screen)

        # Draw evolution panel on top if shown
        if self.evolution_panel:
            self.evolution_panel.draw(screen)

    def set_exit_callback(self, callback) -> None:
        self.exit_button.on_click = callback
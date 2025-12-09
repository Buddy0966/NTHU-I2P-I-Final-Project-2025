from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.utils.definition import Monster
from src.utils.pokemon_data import can_evolve, evolve_pokemon
from .component import UIComponent


class EvolutionPanel(UIComponent):
    """Panel showing pokemon evolution with animation"""

    def __init__(self, pokemon: Monster, x: int, y: int, width: int = 600, height: int = 400, on_complete=None, on_cancel=None):
        self.pokemon = pokemon
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 24)
        self._title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 32)
        self._small_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)

        # Check if can evolve
        self.can_evolve_flag, self.evolution_name = can_evolve(pokemon)

        # Animation state
        self.animation_state = "idle"  # idle, flashing, transforming, complete
        self.animation_timer = 0.0
        self.flash_count = 0
        self.sprite_visible = True

        # Callbacks
        self.on_complete = on_complete
        self.on_cancel = on_cancel

        # Background sprite
        try:
            self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        except:
            self.sprite = None

        # Load pokemon sprites
        try:
            self.old_sprite = Sprite(pokemon["sprite_path"], (150, 150))
        except:
            self.old_sprite = None

        # Load evolution sprite if can evolve
        self.new_sprite = None
        if self.can_evolve_flag and self.evolution_name:
            from src.utils.pokemon_data import EVOLUTION_CHAINS
            evo_data = EVOLUTION_CHAINS.get(pokemon["name"])
            if evo_data:
                sprite_id = evo_data["sprite_id"]
                try:
                    self.new_sprite = Sprite(f"sprites/sprite{sprite_id}.png", (150, 150))
                except:
                    pass

        # Buttons
        btn_w, btn_h = 120, 45
        if self.can_evolve_flag:
            self.evolve_button = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                x + width // 2 - btn_w - 10, y + height - btn_h - 20, btn_w, btn_h,
                self._on_evolve_click
            )
            self.cancel_button = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                x + width // 2 + 10, y + height - btn_h - 20, btn_w, btn_h,
                self._on_cancel_click
            )
        else:
            self.cancel_button = Button(
                "UI/raw/UI_Flat_Button01a_2.png", "UI/raw/UI_Flat_Button01a_1.png",
                x + width // 2 - btn_w // 2, y + height - btn_h - 20, btn_w, btn_h,
                self._on_cancel_click
            )

    def _on_evolve_click(self) -> None:
        """Start evolution animation"""
        if self.animation_state == "idle":
            self.animation_state = "flashing"
            self.animation_timer = 0.0
            self.flash_count = 0

    def _on_cancel_click(self) -> None:
        """Cancel evolution"""
        if self.on_cancel:
            self.on_cancel()

    def update(self, dt: float) -> None:
        """Update animation and buttons"""
        if self.animation_state == "idle" or self.animation_state == "complete":
            # Update buttons only when not animating
            if self.can_evolve_flag and hasattr(self, 'evolve_button'):
                self.evolve_button.update(dt)
            self.cancel_button.update(dt)

        # Handle evolution animation
        if self.animation_state == "flashing":
            self.animation_timer += dt
            flash_interval = 0.15  # Fast flashing

            if self.animation_timer >= flash_interval:
                self.animation_timer = 0
                self.sprite_visible = not self.sprite_visible

                if not self.sprite_visible:
                    self.flash_count += 1

                # After 8 flashes, transition to transforming
                if self.flash_count >= 8:
                    self.animation_state = "transforming"
                    self.animation_timer = 0.0
                    self.sprite_visible = False

        elif self.animation_state == "transforming":
            self.animation_timer += dt

            # Show transformation for 1.5 seconds
            if self.animation_timer >= 1.5:
                # Actually evolve the pokemon
                evolve_pokemon(self.pokemon)
                self.animation_state = "complete"
                self.animation_timer = 0.0
                self.sprite_visible = True

                # Update new sprite
                if self.new_sprite:
                    try:
                        self.old_sprite = Sprite(self.pokemon["sprite_path"], (150, 150))
                    except:
                        pass

        elif self.animation_state == "complete":
            self.animation_timer += dt
            # Auto-close after 2 seconds
            if self.animation_timer >= 2.0:
                if self.on_complete:
                    self.on_complete()

    def draw(self, screen: pg.Surface) -> None:
        """Draw the evolution panel"""
        # Draw background
        if self.sprite:
            screen.blit(self.sprite.image, self.rect)
        else:
            pg.draw.rect(screen, (40, 40, 60), self.rect)
            pg.draw.rect(screen, (255, 255, 255), self.rect, 3)

        # Add overlay
        overlay = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        overlay.fill((60, 80, 120, 60))
        screen.blit(overlay, self.rect)

        # Draw title
        if self.animation_state in ("idle", "flashing"):
            title = "EVOLUTION"
            title_surf = self._title_font.render(title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 30))
            screen.blit(title_surf, title_rect)

        # Draw content based on state
        if self.animation_state == "idle":
            self._draw_idle_state(screen)
        elif self.animation_state == "flashing":
            self._draw_flashing_state(screen)
        elif self.animation_state == "transforming":
            self._draw_transforming_state(screen)
        elif self.animation_state == "complete":
            self._draw_complete_state(screen)

        # Draw buttons
        if self.animation_state in ("idle", "complete"):
            if self.can_evolve_flag and hasattr(self, 'evolve_button') and self.animation_state == "idle":
                self.evolve_button.draw(screen)
                evolve_text = self._small_font.render("EVOLVE", True, (255, 255, 255))
                evolve_rect = evolve_text.get_rect(center=self.evolve_button.hitbox.center)
                screen.blit(evolve_text, evolve_rect)

            self.cancel_button.draw(screen)
            cancel_text = self._small_font.render("CLOSE" if self.animation_state == "complete" else "CANCEL", True, (255, 255, 255))
            cancel_rect = cancel_text.get_rect(center=self.cancel_button.hitbox.center)
            screen.blit(cancel_text, cancel_rect)

    def _draw_idle_state(self, screen: pg.Surface) -> None:
        """Draw idle state - show pokemon and evolution info"""
        if self.can_evolve_flag:
            # Show current pokemon on left
            if self.old_sprite and self.sprite_visible:
                sprite_x = self.rect.x + 80
                sprite_y = self.rect.y + 120
                screen.blit(self.old_sprite.image, (sprite_x, sprite_y))

            # Draw current pokemon info
            name_text = self._font.render(self.pokemon["name"], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(self.rect.x + 155, self.rect.y + 290))
            screen.blit(name_text, name_rect)

            level_text = self._small_font.render(f"Lv. {self.pokemon.get('level', 1)}", True, (200, 200, 200))
            level_rect = level_text.get_rect(center=(self.rect.x + 155, self.rect.y + 310))
            screen.blit(level_text, level_rect)

            # Draw arrow
            arrow_text = self._title_font.render("->", True, (255, 255, 100))
            arrow_rect = arrow_text.get_rect(center=(self.rect.centerx, self.rect.centery))
            screen.blit(arrow_text, arrow_rect)

            # Show evolution pokemon on right
            if self.new_sprite:
                sprite_x = self.rect.x + self.rect.width - 230
                sprite_y = self.rect.y + 120
                screen.blit(self.new_sprite.image, (sprite_x, sprite_y))

            # Draw evolution info
            evo_name_text = self._font.render(self.evolution_name, True, (255, 255, 100))
            evo_name_rect = evo_name_text.get_rect(center=(self.rect.x + self.rect.width - 155, self.rect.y + 290))
            screen.blit(evo_name_text, evo_name_rect)

            # Show stat increase
            old_hp = self.pokemon.get("max_hp", 100)
            new_hp = int(old_hp * 1.4)
            stat_text = self._small_font.render(f"HP: {old_hp} -> {new_hp}", True, (100, 255, 100))
            stat_rect = stat_text.get_rect(center=(self.rect.x + self.rect.width - 155, self.rect.y + 310))
            screen.blit(stat_text, stat_rect)
        else:
            # Cannot evolve
            if self.old_sprite:
                sprite_x = self.rect.centerx - 75
                sprite_y = self.rect.y + 100
                screen.blit(self.old_sprite.image, (sprite_x, sprite_y))

            name_text = self._font.render(self.pokemon["name"], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.y + 270))
            screen.blit(name_text, name_rect)

            # Show why can't evolve
            from src.utils.pokemon_data import EVOLUTION_CHAINS
            if self.pokemon["name"] in EVOLUTION_CHAINS:
                required_level = EVOLUTION_CHAINS[self.pokemon["name"]]["level"]
                current_level = self.pokemon.get("level", 1)
                msg = f"Needs level {required_level} to evolve"
                msg_text = self._small_font.render(msg, True, (255, 200, 100))
            else:
                msg_text = self._small_font.render("This Pokemon cannot evolve", True, (200, 200, 200))

            msg_rect = msg_text.get_rect(center=(self.rect.centerx, self.rect.y + 300))
            screen.blit(msg_text, msg_rect)

    def _draw_flashing_state(self, screen: pg.Surface) -> None:
        """Draw flashing animation"""
        if self.old_sprite and self.sprite_visible:
            sprite_x = self.rect.centerx - 75
            sprite_y = self.rect.centery - 75
            screen.blit(self.old_sprite.image, (sprite_x, sprite_y))

        # Draw flashing effect
        if not self.sprite_visible:
            flash_surface = pg.Surface((150, 150), pg.SRCALPHA)
            flash_surface.fill((255, 255, 255, 200))
            screen.blit(flash_surface, (self.rect.centerx - 75, self.rect.centery - 75))

        # Draw message
        msg_text = self._font.render("Evolving...", True, (255, 255, 255))
        msg_rect = msg_text.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 100))
        screen.blit(msg_text, msg_rect)

    def _draw_transforming_state(self, screen: pg.Surface) -> None:
        """Draw transformation effect"""
        # Draw bright light effect
        light_surface = pg.Surface((200, 200), pg.SRCALPHA)
        alpha = int(150 + 100 * abs(pg.math.Vector2(0.5, 0.5).length()))
        light_surface.fill((255, 255, 255, alpha))
        screen.blit(light_surface, (self.rect.centerx - 100, self.rect.centery - 100))

        # Draw silhouette in transition
        progress = min(self.animation_timer / 1.5, 1.0)
        if progress < 0.5 and self.old_sprite:
            # Fade out old sprite
            sprite_alpha = int(255 * (1.0 - progress * 2))
            temp_surface = self.old_sprite.image.copy()
            temp_surface.set_alpha(sprite_alpha)
            screen.blit(temp_surface, (self.rect.centerx - 75, self.rect.centery - 75))
        elif progress >= 0.5 and self.new_sprite:
            # Fade in new sprite
            sprite_alpha = int(255 * ((progress - 0.5) * 2))
            temp_surface = self.new_sprite.image.copy()
            temp_surface.set_alpha(sprite_alpha)
            screen.blit(temp_surface, (self.rect.centerx - 75, self.rect.centery - 75))

    def _draw_complete_state(self, screen: pg.Surface) -> None:
        """Draw completion state"""
        # Draw evolved pokemon
        if self.old_sprite:  # old_sprite is now updated to new sprite
            sprite_x = self.rect.centerx - 75
            sprite_y = self.rect.centery - 100
            screen.blit(self.old_sprite.image, (sprite_x, sprite_y))

        # Draw congratulations message
        msg_text = self._title_font.render("Congratulations!", True, (255, 255, 100))
        msg_rect = msg_text.get_rect(center=(self.rect.centerx, self.rect.y + 60))
        screen.blit(msg_text, msg_rect)

        # Draw evolved pokemon name
        name_text = self._font.render(f"{self.pokemon['name']}", True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 120))
        screen.blit(name_text, name_rect)

        # Draw new stats
        stat_text = self._small_font.render(f"HP: {self.pokemon.get('max_hp')} (+{int(self.pokemon.get('max_hp') / 1.4 * 0.4)})", True, (100, 255, 100))
        stat_rect = stat_text.get_rect(center=(self.rect.centerx, self.rect.y + self.rect.height - 95))
        screen.blit(stat_text, stat_rect)

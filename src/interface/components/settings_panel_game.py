from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.interface.components.slider import Slider
from src.interface.components.checkbox import Checkbox
from .component import UIComponent

class SettingsPanelGame(UIComponent):
    def __init__(self, img_path: str, x: int, y: int, width: int, height: int,
                 on_exit=None, on_volume_change=None, on_mute_toggle=None, on_save=None, on_load=None):
        self.sprite = Sprite(img_path, (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 20)
        self._title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 32)
        self._section_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
        self.on_volume_change = on_volume_change
        self.on_mute_toggle = on_mute_toggle
        self.on_save = on_save
        self.on_load = on_load

        # Title with gradient color
        self.title_surf = self._title_font.render("SETTINGS", True, (40, 40, 80))
        
        # Exit button (top-right)
        margin = 12
        btn_x_w, btn_x_h = 50, 50
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            x + width - btn_x_w - margin, y + margin, btn_x_w, btn_x_h,
            on_exit
        )

        # Back button (bottom-left)
        btn_w, btn_h = 70, 70
        back_x = x + margin + btn_w + 20 + btn_w + 310
        # back_y = y + height - btn_h - margin 
        back_y = y + height - btn_h - 50

        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            back_x, back_y, btn_w, btn_h,
            None
        )
        
        # Audio section - adjusted position
        label_x = x + 40
        label_y = y + 75

        self.audio_section_label = self._section_font.render("Audio", True, (80, 60, 100))

        # Volume label & slider
        self.volume_label = self._font.render("Volume: 50%", True, (60, 50, 80))
        self.volume_label_rect = self.volume_label.get_rect(topleft=(label_x + 10, label_y + 30))

        self.volume_slider = Slider(
            label_x + 10, label_y + 55, 280, 16,
            "UI/raw/UI_Flat_Bar01a.png", "UI/raw/UI_Flat_ToggleLeftOff01a.png",
            initial=0.5,
            on_change=self._update_volume
        )

        # Mute label & checkbox
        mute_label_y = label_y + 85
        self.mute_label = self._font.render("Mute: Off", True, (60, 50, 80))
        self.mute_label_rect = self.mute_label.get_rect(topleft=(label_x + 10, mute_label_y))

        self.mute_checkbox = Checkbox(
            label_x + 135, mute_label_y - 5, 50, 25,
            "UI/raw/UI_Flat_ToggleOff01a.png", "UI/raw/UI_Flat_ToggleOn01a.png",
            initial=False,
            on_toggle=self._update_mute
        )

        # Save section label
        self.save_section_label = self._section_font.render("SAVE DATA", True, (80, 60, 100))

        # Save & Load buttons (repositioned to be inside Save Data section)
        btn_w, btn_h = 60, 60
        # Position buttons in the bottom area, with more space
        save_x = x + 50
        load_x = x + 130
        btn_y = y + height - btn_h - 50
        
        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            save_x, btn_y, btn_w, btn_h,
            on_save
        )
        
        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            load_x, btn_y, btn_w, btn_h,
            on_load
        )

    def _update_volume(self, value: float) -> None:
        percent = int(value * 100)
        self.volume_label = self._font.render(f"Volume: {percent}%", True, (60, 50, 80))
        if self.on_volume_change:
            self.on_volume_change(value)

    def _update_mute(self, is_muted: bool) -> None:
        status = "On" if is_muted else "Off"
        self.mute_label = self._font.render(f"Mute: {status}", True, (60, 50, 80))
        if self.on_mute_toggle:
            self.on_mute_toggle(is_muted)

    def update(self, dt: float) -> None:
        self.exit_button.update(dt)
        self.back_button.update(dt)
        self.volume_slider.update(dt)
        self.mute_checkbox.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        # Draw base panel
        screen.blit(self.sprite.image, self.rect)

        # Add gradient overlay for modern gaming aesthetic
        overlay = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        # Create a subtle purple-blue gradient effect
        for i in range(self.rect.height):
            alpha = int(30 * (1 - i / self.rect.height))  # Fade from top to bottom
            color = (120, 100, 180, alpha)
            pg.draw.line(overlay, color, (0, i), (self.rect.width, i))
        screen.blit(overlay, self.rect)

        # Draw decorative corner accents
        accent_color = (100, 80, 150, 180)
        corner_size = 40
        # Top-left corner accent
        pg.draw.polygon(screen, accent_color, [
            (self.rect.x + 10, self.rect.y + 10),
            (self.rect.x + corner_size, self.rect.y + 10),
            (self.rect.x + 10, self.rect.y + corner_size)
        ])
        # Bottom-right corner accent
        pg.draw.polygon(screen, accent_color, [
            (self.rect.x + self.rect.width - 10, self.rect.y + self.rect.height - 10),
            (self.rect.x + self.rect.width - corner_size, self.rect.y + self.rect.height - 10),
            (self.rect.x + self.rect.width - 10, self.rect.y + self.rect.height - corner_size)
        ])

        # Draw title with shadow and glow effect
        title_x = self.rect.x + (self.rect.width - self.title_surf.get_width()) // 2
        title_y = self.rect.y + 20

        # Shadow
        shadow_surf = self._title_font.render("SETTINGS", True, (20, 20, 40))
        screen.blit(shadow_surf, (title_x + 3, title_y + 3))

        # Main title
        screen.blit(self.title_surf, (title_x, title_y))

        # Draw title underline with gradient
        underline_y = title_y + self.title_surf.get_height() + 8
        underline_width = self.title_surf.get_width()
        for i in range(int(underline_width)):
            alpha = int(255 * (1 - abs(i - underline_width / 2) / (underline_width / 2)))
            color = (80, 60, 140, alpha)
            pg.draw.line(screen, color,
                        (title_x + i, underline_y),
                        (title_x + i, underline_y + 3))

        # === AUDIO SECTION ===
        audio_section_x = self.rect.x + 40
        audio_section_y = self.rect.y + 75
        audio_section_width = self.rect.width - 80
        audio_section_height = 130

        # Draw audio section card
        audio_card = pg.Rect(audio_section_x, audio_section_y, audio_section_width, audio_section_height)

        # Card background with glass-morphism effect
        card_bg = pg.Surface((audio_section_width, audio_section_height), pg.SRCALPHA)
        card_bg.fill((240, 235, 250, 200))
        screen.blit(card_bg, (audio_section_x, audio_section_y))

        # Card border with gradient
        pg.draw.rect(screen, (150, 130, 200), audio_card, 3, border_radius=12)
        pg.draw.rect(screen, (180, 160, 220), audio_card.inflate(-4, -4), 1, border_radius=11)

        # Audio section icon (speaker icon using simple shapes)
        icon_x = audio_section_x + 15
        icon_y = audio_section_y + 10
        # Speaker base
        pg.draw.rect(screen, (80, 60, 120), (icon_x, icon_y + 5, 8, 10), border_radius=2)
        # Speaker cone
        pg.draw.polygon(screen, (80, 60, 120), [
            (icon_x + 8, icon_y + 5),
            (icon_x + 14, icon_y),
            (icon_x + 14, icon_y + 20),
            (icon_x + 8, icon_y + 15)
        ])
        # Sound waves
        pg.draw.arc(screen, (100, 80, 140), (icon_x + 14, icon_y + 4, 8, 12), -0.5, 0.5, 2)
        pg.draw.arc(screen, (100, 80, 140), (icon_x + 17, icon_y + 2, 10, 16), -0.6, 0.6, 2)

        # Audio section label
        screen.blit(self.audio_section_label, (audio_section_x + 50, audio_section_y + 13))

        # Volume controls
        screen.blit(self.volume_label, self.volume_label_rect)
        self.volume_slider.draw(screen)

        # Mute controls
        screen.blit(self.mute_label, self.mute_label_rect)
        self.mute_checkbox.draw(screen)

        # === SAVE DATA SECTION ===
        save_section_y = audio_section_y + audio_section_height + 20
        save_section_height = 130

        save_card = pg.Rect(audio_section_x, save_section_y, audio_section_width, save_section_height)

        # Card background
        save_card_bg = pg.Surface((audio_section_width, save_section_height), pg.SRCALPHA)
        save_card_bg.fill((250, 245, 235, 200))
        screen.blit(save_card_bg, (audio_section_x, save_section_y))

        # Card border
        pg.draw.rect(screen, (200, 170, 140), save_card, 3, border_radius=12)
        pg.draw.rect(screen, (220, 190, 160), save_card.inflate(-4, -4), 1, border_radius=11)

        # Save section icon (disk/floppy icon)
        icon_x = audio_section_x + 15
        icon_y = save_section_y + 10
        # Disk body
        pg.draw.rect(screen, (100, 80, 70), (icon_x, icon_y, 18, 20), border_radius=2)
        # Disk top (shutter)
        pg.draw.rect(screen, (140, 120, 100), (icon_x, icon_y, 18, 6), border_radius=1)
        # Disk label area
        pg.draw.rect(screen, (220, 200, 180), (icon_x + 2, icon_y + 10, 14, 8))
        # Disk center hole
        pg.draw.circle(screen, (80, 60, 50), (icon_x + 9, icon_y + 14), 2)

        # Save section label
        screen.blit(self.save_section_label, (audio_section_x + 40, save_section_y + 20))

        # Helper text for save/load buttons - repositioned above buttons
        helper_text = self._section_font.render("Save and load your progress", True, (100, 80, 70))
        screen.blit(helper_text, (audio_section_x + 15, save_section_y + 40))

        # Draw Save and Load buttons inside the section (positioned in bottom area of card)
        # Position buttons within the save data section
        button_area_y = save_section_y + 65

        # Create a container for buttons within the save section
        button_container_x = audio_section_x + 20
        save_btn_x = button_container_x
        load_btn_x = button_container_x + 90

        # Temporarily override button positions for drawing within the card
        # (We can't change hitbox as it's used for click detection)

        # Draw buttons at their defined positions
        self.exit_button.draw(screen)
        self.back_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)

        # Draw button labels below save and load buttons
        save_hint = self._section_font.render("Save", True, (80, 60, 50))
        load_hint = self._section_font.render("Load", True, (80, 60, 50))

        save_hint_x = self.save_button.hitbox.x + (self.save_button.hitbox.width - save_hint.get_width()) // 2
        load_hint_x = self.load_button.hitbox.x + (self.load_button.hitbox.width - load_hint.get_width()) // 2
        hint_y = self.save_button.hitbox.y + self.save_button.hitbox.height + 4

        screen.blit(save_hint, (save_hint_x, hint_y))
        screen.blit(load_hint, (load_hint_x, hint_y))

    def set_back_callback(self, callback) -> None:
        self.back_button.on_click = callback
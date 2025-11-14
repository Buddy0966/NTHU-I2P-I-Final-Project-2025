from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.interface.components.slider import Slider
from src.interface.components.checkbox import Checkbox
from .component import UIComponent

class SettingsPanel(UIComponent):
    def __init__(self, img_path: str, x: int, y: int, width: int, height: int,
                 on_exit=None, on_volume_change=None, on_mute_toggle=None):
        self.sprite = Sprite(img_path, (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 20)
        self.on_volume_change = on_volume_change
        self.on_mute_toggle = on_mute_toggle
        
        # Title
        self.title_surf = self._font.render("SETTINGS", True, (0, 0, 0))
        
        # Exit button (top-right)
        margin = 12
        btn_x_w, btn_x_h = 50, 50
        self.exit_button = Button(
            "UI/button_x.png", "UI/button_x_hover.png",
            x + width - btn_x_w - margin, y + margin, btn_x_w, btn_x_h,
            on_exit
        )
        
        # Back button (bottom-left)
        btn_w, btn_h = 80, 80
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            x + margin, y + height - btn_h - margin, btn_w, btn_h,
            None
        )
        
        # Volume label & slider
        label_x = x + 32
        label_y = y + 70
        self.volume_label = self._font.render("Volume: 50%", True, (0, 0, 0))
        self.volume_label_rect = self.volume_label.get_rect(topleft=(label_x, label_y))
        
        self.volume_slider = Slider(
            label_x, label_y + 32, 280, 16,
            "UI/raw/UI_Flat_Bar01a.png", "UI/raw/UI_Flat_ToggleLeftOff01a.png",
            initial=0.5,
            on_change=self._update_volume
        )
        
        # Mute label & checkbox
        mute_label_y = label_y + 72
        self.mute_label = self._font.render("Mute: Off", True, (0, 0, 0))
        self.mute_label_rect = self.mute_label.get_rect(topleft=(label_x, mute_label_y))
        
        self.mute_checkbox = Checkbox(
            label_x + 125, mute_label_y - 5, 50, 25,
            "UI/raw/UI_Flat_ToggleOff01a.png", "UI/raw/UI_Flat_ToggleOn01a.png",
            initial=False,
            on_toggle=self._update_mute
        )

    def _update_volume(self, value: float) -> None:
        percent = int(value * 100)
        self.volume_label = self._font.render(f"Volume: {percent}%", True, (0, 0, 0))
        if self.on_volume_change:
            self.on_volume_change(value)

    def _update_mute(self, is_muted: bool) -> None:
        status = "On" if is_muted else "Off"
        self.mute_label = self._font.render(f"Mute: {status}", True, (0, 0, 0))
        if self.on_mute_toggle:
            self.on_mute_toggle(is_muted)

    def update(self, dt: float) -> None:
        self.exit_button.update(dt)
        self.back_button.update(dt)
        self.volume_slider.update(dt)
        self.mute_checkbox.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.sprite.image, self.rect)
        screen.blit(self.title_surf, (self.rect.x + 16, self.rect.y + 16))
        screen.blit(self.volume_label, self.volume_label_rect)
        self.volume_slider.draw(screen)
        screen.blit(self.mute_label, self.mute_label_rect)
        self.mute_checkbox.draw(screen)
        self.exit_button.draw(screen)
        self.back_button.draw(screen)

    def set_back_callback(self, callback) -> None:
        self.back_button.on_click = callback



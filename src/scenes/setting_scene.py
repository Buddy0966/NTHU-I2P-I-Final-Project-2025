import pygame as pg
from src.utils import GameSettings
from src.sprites import BackgroundSprite
from src.scenes.scene import Scene
from src.interface.components import SettingsPanel
from src.core.services import scene_manager, sound_manager, input_manager
try:
    from typing import override
except ImportError:
    from typing_extensions import override

class SettingScene(Scene):
    background: BackgroundSprite
    settings_panel: SettingsPanel

    def __init__(self):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background2.png")
        
        panel_w, panel_h = 600, 380
        panel_x = (GameSettings.SCREEN_WIDTH - panel_w) // 2
        panel_y = (GameSettings.SCREEN_HEIGHT - panel_h) // 2
        
        self.settings_panel = SettingsPanel(
            "UI/raw/UI_Flat_Frame03a.png",
            panel_x, panel_y, panel_w, panel_h,
            on_exit=lambda: scene_manager.change_scene("menu"),
            on_volume_change=lambda v: sound_manager.set_master_volume(v),
            on_mute_toggle=self._handle_mute
        )
        self.settings_panel.set_back_callback(lambda: scene_manager.change_scene("menu"))

    def _handle_mute(self, is_muted: bool) -> None:
        if is_muted:
            sound_manager.pause_all()
        else:
            sound_manager.resume_all()

    @override
    def enter(self) -> None:
        if hasattr(sound_manager, "play_bgm"):
            sound_manager.play_bgm("RBY 101 Opening (Part 1).ogg")

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_ESCAPE):
            scene_manager.change_scene("menu")
            return
        self.settings_panel.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.settings_panel.draw(screen)

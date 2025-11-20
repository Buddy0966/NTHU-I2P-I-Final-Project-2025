import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.interface.components import Button, SettingsPanelGame, BagPanel
from src.core.services import scene_manager, sound_manager, input_manager
from src.core.services import sound_manager
from src.sprites import Sprite
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    setting_button: Button
    backpack_button: Button
    settings_panel: SettingsPanelGame | None
    bag_panel: BagPanel | None
    show_settings: bool
    show_bag: bool

    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        
        margin = 12
        btn_w, btn_h = 60, 60
        bx = GameSettings.SCREEN_WIDTH - btn_w - margin
        by = margin

        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            bx, by, btn_w, btn_h,
            self._toggle_settings
        )
        
        self.backpack_button = Button(
            "UI/button_backpack.png", "UI/button_backpack_hover.png",
            bx - btn_w - margin, by, btn_w, btn_h,
            self._toggle_bag
        )
        
        self.show_settings = False
        self.show_bag = False
        self.settings_panel = None
        self.bag_panel = None

    def _toggle_settings(self) -> None:
        self.show_settings = not self.show_settings
        if self.show_settings:
            panel_w, panel_h = 600, 400
            panel_x = (GameSettings.SCREEN_WIDTH - panel_w) // 2
            panel_y = (GameSettings.SCREEN_HEIGHT - panel_h) // 2
            self.settings_panel = SettingsPanelGame(
                "UI/raw/UI_Flat_Frame03a.png",
                panel_x, panel_y, panel_w, panel_h,
                on_exit=self._toggle_settings,
                on_volume_change=lambda v: sound_manager.set_master_volume(v),
                on_mute_toggle=self._handle_mute,
                on_save=self._save_game,
                on_load=self._load_game
            )

            self.settings_panel.set_back_callback(self._toggle_settings)

    def _toggle_bag(self) -> None:
        self.show_bag = not self.show_bag
        if self.show_bag:
            # Refresh bag panel with latest data from game_manager
            panel_w, panel_h = 700, 500
            panel_x = (GameSettings.SCREEN_WIDTH - panel_w) // 2
            panel_y = (GameSettings.SCREEN_HEIGHT - panel_h) // 2
            self.bag_panel = BagPanel(
                self.game_manager.bag.items if self.game_manager.bag else [],
                panel_x, panel_y, panel_w, panel_h,
                on_exit=self._toggle_bag,
                monsters=self.game_manager.bag.monsters if self.game_manager.bag else []
            )
            Logger.info(f"BagPanel opened with {len(self.game_manager.bag.monsters if self.game_manager.bag else [])} monsters")
        else:
            self.bag_panel = None

    def _handle_mute(self, is_muted: bool) -> None:
        if is_muted:
            sound_manager.pause_all()
        else:
            sound_manager.resume_all()

    def _save_game(self) -> None:
        self.game_manager.save("saves/game0.json")
        Logger.info("Game saved!")

    def _load_game(self) -> None:
        loaded = GameManager.load("saves/game0.json")
        if loaded:
            self.game_manager = loaded
            Logger.info("Game loaded!")

    @override
    def enter(self) -> None:
        # Reload game data to sync with latest save (e.g., after battle)
        loaded = GameManager.load("saves/game0.json")
        if loaded:
            self.game_manager = loaded
            Logger.info("Game data reloaded from save file")
            # Set bush cooldown when returning from battle to prevent immediate re-encounter
            self.game_manager.bush_cooldown = self.game_manager.BUSH_WAIT
        
        # sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        self.setting_button.update(dt)
        self.backpack_button.update(dt)
        
        if self.show_settings and self.settings_panel:
            self.settings_panel.update(dt)
            return
        
        if self.show_bag and self.bag_panel:
            self.bag_panel.update(dt)
            return
        
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        # Update game manager timers (e.g., teleport cooldown)
        self.game_manager.update(dt)

        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
            # Battle trigger
            if enemy.detected and input_manager.key_pressed(pg.K_SPACE):
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("battle_transition")
                return
        
        # Check bush collision - trigger wild pokemon battle
        if self.game_manager.player and self.game_manager.current_map:
            player_rect = self.game_manager.player.animation.rect
            # Only check bush if cooldown has expired
            if self.game_manager.bush_cooldown <= 0.0 and self.game_manager.current_map.check_bush(player_rect):
                # Encountered wild pokemon in bush
                Logger.info("Wild pokemon encountered in bush!")
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("catch_pokemon")
                return
        
        self.game_manager.bag.update(dt)

        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x,
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.game_manager.bag.draw(screen)
        self.setting_button.draw(screen)
        self.backpack_button.draw(screen)
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
        
        if self.show_settings and self.settings_panel:
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            self.settings_panel.draw(screen)
        
        if self.show_bag and self.bag_panel:
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            self.bag_panel.draw(screen)
import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.sprites import Sprite
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    
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
        
        self._settings_size = (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        self._settings_pos = (GameSettings.SCREEN_WIDTH - self._settings_size[0] - 8, 8)
        self.sprite_settings = Sprite("UI/button_setting.png", self._settings_size)
        self.sprite_settings.update_pos(Position(self._settings_pos[0], self._settings_pos[1]))
        self.sprite_settings_hover = Sprite("UI/button_setting_hover.png", self._settings_size)
        self.sprite_settings_hover.update_pos(Position(self._settings_pos[0], self._settings_pos[1]))
        self.settings_rect = pg.Rect(self._settings_pos, self._settings_size)
        self._settings_click_cooldown = 0.0
        self._SETTINGS_CLICK_WAIT = 0.1
        # track whether hover (alternate) button is active
        self._settings_is_hover = False
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()
        
    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        # Update game manager timers (e.g., teleport cooldown)
        self.game_manager.update(dt)

        # ---- 恢復玩家 / 敵人 / 背包的每幀更新 ----
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
        self.game_manager.bag.update(dt)
        # -----------------------------------------

        # update settings click cooldown
        if getattr(self, "_settings_click_cooldown", 0.0) > 0.0:
            self._settings_click_cooldown = max(0.0, self._settings_click_cooldown - dt)

        # hover: 根據滑鼠位置直接切換 hover 狀態（不需按下）
        mouse_pos = pg.mouse.get_pos()
        self._settings_is_hover = self.settings_rect.collidepoint(mouse_pos)

        # click handling (保留按下行為，例如開啟設定)
        if pg.mouse.get_pressed()[0] and getattr(self, "_settings_click_cooldown", 0.0) == 0.0:
            if self._settings_is_hover:
                Logger.info("Settings button clicked")
                # TODO: 切換到設定場景或顯示設定視窗
                self._settings_click_cooldown = self._SETTINGS_CLICK_WAIT

        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x,
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )
        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            '''
            [TODO HACKATHON 3]
            Implement the camera algorithm logic here
            Right now it's hard coded, you need to follow the player's positions
            you may use the below example, but the function still incorrect, you may trace the entity.py
            
            camera = self.game_manager.player.camera
            '''
            camera = self.game_manager.player.camera
            # camera = PositionCamera(16 * GameSettings.TILE_SIZE, 30 * GameSettings.TILE_SIZE)
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.game_manager.bag.draw(screen)

        # draw settings button as screen-overlay UI (topmost)
        if getattr(self, "_settings_is_hover", False):
            self.sprite_settings_hover.draw(screen)
        else:
            self.sprite_settings.draw(screen)
        
        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
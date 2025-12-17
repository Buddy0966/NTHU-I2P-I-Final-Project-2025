import pygame as pg
import threading
import time

from src.scenes.scene import Scene
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.interface.components import Button, SettingsPanelGame, BagPanel
from src.interface.components.shop_panel import ShopPanel
from src.interface.components.chat_overlay import ChatOverlay
from src.interface.components.minimap import Minimap
from src.interface.components.navigation_panel import NavigationPanel
from src.interface.components.arrow_path import ArrowPath
from src.utils.pathfinding import Pathfinder
from src.core.services import scene_manager, sound_manager, input_manager
from src.core.services import sound_manager
from src.sprites import Sprite, Animation
from typing import override, Dict


class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    setting_button: Button
    backpack_button: Button
    settings_panel: SettingsPanelGame | None
    bag_panel: BagPanel | None
    shop_panel: ShopPanel | None
    navigation_panel: NavigationPanel | None
    arrow_path: ArrowPath | None
    show_settings: bool
    show_bag: bool
    show_shop: bool
    show_navigation: bool
    show_teleport_prompt: bool
    pending_teleport_destination: str | None
    show_npc_dialogue: bool
    current_npc_dialogue: str | None
    chat_overlay: ChatOverlay | None
    minimap: Minimap

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

        # Navigation button
        self.navigation_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",  # Temporary, can change later
            bx - 2 * (btn_w + margin), by, btn_w, btn_h,
            self._toggle_navigation
        )

        self.show_settings = False
        self.show_bag = False
        self.show_shop = False
        self.show_navigation = False
        self.settings_panel = None
        self.bag_panel = None
        self.shop_panel = None
        self.navigation_panel = None
        self.arrow_path = None

        # Teleport prompt state
        self.show_teleport_prompt = False
        self.pending_teleport_destination = None

        # NPC dialogue bubble state
        self.show_npc_dialogue = False
        self.current_npc_dialogue = None

        # Online player animations storage
        self.online_player_animations: Dict[int, Animation] = {}

        # Chat overlay (only if online)
        if self.online_manager:
            self.chat_overlay = ChatOverlay(
                send_callback=self.online_manager.send_chat,
                get_messages=self.online_manager.get_recent_chat
            )
        else:
            self.chat_overlay = None

        # Minimap - positioned at top-left corner
        self.minimap = Minimap(
            size=(200, 200),
            position=(20, 20),
            scale_factor=0.1,
            border_width=3,
            border_color=(255, 255, 255),
            background_color=(0, 0, 0, 180),
            show_entities=True
        )

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

    def _toggle_shop(self) -> None:
        self.show_shop = not self.show_shop
        if not self.show_shop:
            self.shop_panel = None

    def _toggle_navigation(self) -> None:
        self.show_navigation = not self.show_navigation
        if self.show_navigation:
            panel_w, panel_h = 400, 300
            panel_x = (GameSettings.SCREEN_WIDTH - panel_w) // 2
            panel_y = (GameSettings.SCREEN_HEIGHT - panel_h) // 2
            self.navigation_panel = NavigationPanel(
                panel_x, panel_y, panel_w, panel_h,
                on_exit=self._toggle_navigation,
                on_navigate=self._start_navigation
            )
        else:
            self.navigation_panel = None

    def _start_navigation(self, destination: Position) -> None:
        """Start navigation to a destination"""
        player_pos = self.game_manager.player.position
        current_map = self.game_manager.current_map

        # Find path using BFS
        path = Pathfinder.find_path(
            player_pos,
            destination,
            current_map._collision_map,
            current_map.tmxdata.width,
            current_map.tmxdata.height
        )

        if path:
            # Simplify path for better visualization
            simplified_path = Pathfinder.simplify_path(path)
            self.arrow_path = ArrowPath(simplified_path)
            Logger.info(f"Navigation started: {len(path)} points, simplified to {len(simplified_path)}")
        else:
            Logger.warning("No path found to destination")
            self.arrow_path = None

        # Close navigation panel after selecting destination
        self.show_navigation = False
        self.navigation_panel = None

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
            # Set teleport cooldown to prevent immediate teleportation on load
            self.game_manager.teleport_cooldown = self.game_manager.TELEPORT_WAIT
        
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
        self.navigation_button.update(dt)
        self.minimap.update(dt)

        # Update arrow path animation and consumption
        if self.arrow_path and self.game_manager.player:
            self.arrow_path.update(dt, self.game_manager.player.position)

            # Clear arrow path if it's been completely consumed
            if self.arrow_path.is_complete():
                self.arrow_path = None

        # Chat overlay handling (priority over other UI)
        if self.chat_overlay:
            if self.chat_overlay.is_open:
                self.chat_overlay.update(dt)
                return
            # Open chat with T key (only when other UI is closed)
            if not self.show_settings and not self.show_bag and not self.show_shop and not self.show_navigation:
                if input_manager.key_pressed(pg.K_t):
                    self.chat_overlay.open()
                    return

        if self.show_settings and self.settings_panel:
            self.settings_panel.update(dt)
            return

        if self.show_bag and self.bag_panel:
            self.bag_panel.update(dt)
            return

        if self.show_shop and self.shop_panel:
            self.shop_panel.update(dt)
            return

        if self.show_navigation and self.navigation_panel:
            self.navigation_panel.update(dt)
            return

        # Handle teleport prompt
        if self.show_teleport_prompt:
            if input_manager.key_pressed(pg.K_RETURN) and self.pending_teleport_destination:
                # Player pressed Enter - teleport
                self.game_manager.switch_map(self.pending_teleport_destination)
                self.show_teleport_prompt = False
                self.pending_teleport_destination = None
            elif not self._is_player_on_teleporter():
                # Player walked away - hide prompt
                self.show_teleport_prompt = False
                self.pending_teleport_destination = None
        else:
            # Check if player just stepped on a teleporter
            if self.game_manager.player and getattr(self.game_manager, "teleport_cooldown", 0.0) <= 0.0:
                tp = self.game_manager.current_map.check_teleport(self.game_manager.player.position)
                if tp and tp.destination in ["new_map.tmx", "gym_new.tmx"]:  # Show prompt for new map and gym_new teleporters
                    self.show_teleport_prompt = True
                    self.pending_teleport_destination = tp.destination

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

        # NPC interaction
        npc_near = False
        for npc in self.game_manager.current_npcs:
            npc.update(dt)
            # Show dialogue bubble when near NPC
            if npc.is_near_player:
                npc_near = True
                self.show_npc_dialogue = True
                self.current_npc_dialogue = npc.dialogue
                # Shop trigger - press E to interact
                if input_manager.key_pressed(pg.K_e):
                    self.show_shop = True
                    # Hide dialogue bubble when opening shop
                    self.show_npc_dialogue = False
                    self.current_npc_dialogue = None
                    panel_w, panel_h = 800, 600
                    panel_x = (GameSettings.SCREEN_WIDTH - panel_w) // 2
                    panel_y = (GameSettings.SCREEN_HEIGHT - panel_h) // 2
                    self.shop_panel = ShopPanel(
                        npc.shop_inventory,
                        self.game_manager.bag,
                        npc.name,
                        panel_x,
                        panel_y,
                        panel_w,
                        panel_h,
                        on_exit=self._toggle_shop
                    )
                    Logger.info(f"Opened shop: {npc.name}")
                    return

        # Hide dialogue bubble if not near any NPC
        if not npc_near:
            self.show_npc_dialogue = False
            self.current_npc_dialogue = None
        
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
            player = self.game_manager.player
            # Convert Direction enum to string for network transmission
            direction_str = player.direction.name  # e.g., Direction.UP -> "UP"
            # Determine if player is moving based on animation state
            # Check if the animation is actively playing (accumulator > 0 means it's been updated)
            is_moving = player.animation.accumulator > 0

            _ = self.online_manager.update(
                player.position.x,
                player.position.y,
                self.game_manager.current_map.path_name,
                direction_str,
                is_moving
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
        for npc in self.game_manager.current_npcs:
            npc.draw(screen, camera)

        # Draw navigation arrow path
        if self.arrow_path and self.game_manager.player:
            self.arrow_path.draw(screen, camera)

        self.game_manager.bag.draw(screen)

        # Draw minimap (only when no modal panels are open)
        if not self.show_settings and not self.show_bag and not self.show_shop and not self.show_navigation:
            self.minimap.draw(
                screen,
                self.game_manager.current_map,
                self.game_manager.player,
                self.game_manager.current_enemy_trainers,
                self.game_manager.current_npcs
            )

        self.setting_button.draw(screen)
        self.backpack_button.draw(screen)
        self.navigation_button.draw(screen)

        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            cam = self.game_manager.player.camera

            # Clean up animations for disconnected players
            current_pids = set(p["id"] for p in list_online)
            for pid in list(self.online_player_animations.keys()):
                if pid not in current_pids:
                    del self.online_player_animations[pid]

            for player_data in list_online:
                if player_data["map"] == self.game_manager.current_map.path_name:
                    player_id = player_data["id"]

                    # Create or get animation for this online player
                    if player_id not in self.online_player_animations:
                        self.online_player_animations[player_id] = Animation(
                            "character/ow1.png",  # Use same sprite as local player
                            ["down", "left", "right", "up"], 4,
                            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                        )

                    anim = self.online_player_animations[player_id]

                    # Update position
                    pos = Position(player_data["x"], player_data["y"])
                    anim.update_pos(pos)

                    # Update animation based on direction and movement
                    direction = player_data.get("direction", "DOWN").lower()
                    is_moving = player_data.get("is_moving", False)

                    # Switch to appropriate animation state
                    anim.switch(direction)

                    # Update animation (this advances frames if moving)
                    if is_moving:
                        anim.update(0.016)  # Approximate frame time

                    # Draw the animated sprite
                    anim.draw(screen, cam)
        
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

        if self.show_shop and self.shop_panel:
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            self.shop_panel.draw(screen)

        if self.show_navigation and self.navigation_panel:
            overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            self.navigation_panel.draw(screen)

        # Draw teleport prompt
        if self.show_teleport_prompt:
            self._draw_teleport_prompt(screen)

        # Draw NPC dialogue bubble
        if self.show_npc_dialogue and self.current_npc_dialogue:
            self._draw_npc_dialogue(screen)

        # Draw chat overlay (always draw so messages are visible even when closed)
        if self.chat_overlay:
            self.chat_overlay.draw(screen)

    def _is_player_on_teleporter(self) -> bool:
        """Check if player is currently on or near a teleporter tile (within 1 tile left/right)"""
        if not self.game_manager.player:
            return False

        # Check if directly on teleporter
        tp = self.game_manager.current_map.check_teleport(self.game_manager.player.position)
        if tp and tp.destination in ["new_map.tmx", "gym_new.tmx"]:
            return True

        # Check adjacent tiles (left and right)
        player_pos = self.game_manager.player.position
        for offset_x in [-GameSettings.TILE_SIZE, GameSettings.TILE_SIZE]:
            adjacent_pos = Position(player_pos.x + offset_x, player_pos.y)
            tp_adjacent = self.game_manager.current_map.check_teleport(adjacent_pos)
            if tp_adjacent and tp_adjacent.destination in ["new_map.tmx", "gym_new.tmx"]:
                return True

        return False

    def _draw_teleport_prompt(self, screen: pg.Surface):
        """Draw the teleport prompt speech bubble"""
        # Load UI banner/frame
        from src.utils import load_img
        banner = load_img("UI/raw/UI_Flat_InputField01a.png")

        # Size and position
        banner_width = 400
        banner_height = 100
        banner_x = (GameSettings.SCREEN_WIDTH - banner_width) // 2
        banner_y = GameSettings.SCREEN_HEIGHT // 2 - 300

        # Scale banner
        banner = pg.transform.scale(banner, (banner_width, banner_height))
        screen.blit(banner, (banner_x, banner_y))

        # Draw text - different text based on destination
        font = pg.font.Font(None, 32)
        if self.pending_teleport_destination == "gym_new.tmx":
            text1 = font.render("boss fight?", True, (0, 0, 0))
        else:
            text1 = font.render("Enter a New World?", True, (0, 0, 0))
        text3 = font.render("ENTER to confirm", True, (0, 0, 0))

        # Center text
        text1_rect = text1.get_rect(center=(banner_x + banner_width // 2, banner_y + 30))
        text3_rect = text3.get_rect(center=(banner_x + banner_width // 2, banner_y + 70))

        screen.blit(text1, text1_rect)
        screen.blit(text3, text3_rect)

    def _draw_npc_dialogue(self, screen: pg.Surface):
        """Draw the NPC dialogue speech bubble"""
        # Load UI banner/frame
        from src.utils import load_img
        banner = load_img("UI/raw/UI_Flat_InputField01a.png")

        # Size and position
        banner_width = 400
        banner_height = 100
        banner_x = (GameSettings.SCREEN_WIDTH - banner_width) // 2
        banner_y = GameSettings.SCREEN_HEIGHT // 2 - 300

        # Scale banner
        banner = pg.transform.scale(banner, (banner_width, banner_height))
        screen.blit(banner, (banner_x, banner_y))

        # Draw text
        font = pg.font.Font(None, 32)
        text1 = font.render(self.current_npc_dialogue or "Welcome to my shop!", True, (0, 0, 0))
        text2 = font.render("Press E to interact", True, (0, 0, 0))

        # Center text
        text1_rect = text1.get_rect(center=(banner_x + banner_width // 2, banner_y + 30))
        text2_rect = text2.get_rect(center=(banner_x + banner_width // 2, banner_y + 70))

        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)
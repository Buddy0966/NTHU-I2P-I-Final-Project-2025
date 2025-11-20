from __future__ import annotations
import pygame as pg
from src.scenes.scene import Scene
from src.sprites import BackgroundSprite, Sprite
from src.utils import GameSettings, Logger
from src.core.services import input_manager, scene_manager
from src.core import GameManager
from src.interface.components import PokemonStatsPanel, BattleActionButton
from src.interface.components.battle_item_panel import BattleItemPanel
from src.utils.definition import Monster
from typing import override
from enum import Enum
import math
import random


class WildBattleState(Enum):
    INTRO = 0
    CHALLENGER = 1
    SEND_OPPONENT = 2
    SEND_PLAYER = 3
    MAIN = 4
    PLAYER_TURN = 5
    CHOOSE_MOVE = 6
    ENEMY_TURN = 7
    BATTLE_END = 8
    CHOOSE_ITEM = 9
    SHOW_DAMAGE = 10
    CATCHING = 11  # pokeball catching state
    CATCH_ANIMATION = 12  # pokeball flying animation
    SWITCH_POKEMON = 13  # Player switching pokemon
    CATCH_FLASHING = 14  # Pokemon flashing when caught
    # CATCH_FLASHING = 14  # Pokemon flashing when caught
    CATCH_FALLING = 15  # Pokeball falling after catch
    CATCH_SHAKE = 16    # Pokeball shaking on ground
    CATCH_SUCCESS = 17  # Catch successful


class CatchPokemonScene(Scene):
    """Wild Pokemon Battle Scene - Player encounters random wild pokemon"""
    background: BackgroundSprite
    game_manager: GameManager
    state: WildBattleState
    opponent_pokemon: Monster | None
    player_pokemon: Monster | None
    opponent_panel: PokemonStatsPanel | None
    player_panel: PokemonStatsPanel | None
    message: str
    fight_btn: BattleActionButton | None
    item_btn: BattleActionButton | None
    switch_btn: BattleActionButton | None
    run_btn: BattleActionButton | None
    move_buttons: list[BattleActionButton]
    current_turn: str  # "player" or "enemy"
    player_selected_move: str | None
    enemy_selected_move: str | None
    turn_message: str
    item_panel: BattleItemPanel | None
    player_selected_item: dict | None
    
    # Multi-pokemon enemy party system
    enemy_party: list[Monster]  # Enemy's pokemon list
    enemy_party_index: int  # Current opponent pokemon index
    
    # pokeball catching animation
    pokeball_sprite: Sprite | None
    pokeball_x: float
    pokeball_y: float
    pokeball_rotation: float
    pokeball_scale: float
    catch_panel: BattleItemPanel | None
    shake_count: int
    shake_timer: float

    # Pokemon flashing animation
    flash_count: int
    flash_timer: float
    pokemon_visible: bool
    
    # Wild pokemon data pool
    WILD_POKEMON_POOL = [
        {
            "name": "Leogreen",
            "hp": 45,
            "max_hp": 45,
            "level": 10,
            "sprite_path": "menu_sprites/menusprite2.png"
        },
        {
            "name": "Bulbasaur",
            "hp": 40,
            "max_hp": 40,
            "level": 8,
            "sprite_path": "menu_sprites/menusprite1.png"
        },
        {
            "name": "Charmander",
            "hp": 39,
            "max_hp": 39,
            "level": 8,
            "sprite_path": "menu_sprites/menusprite3.png"
        },
    ]
    
    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 24)
        self._message_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
        
        self.state = WildBattleState.INTRO
        self.opponent_pokemon = None
        self.player_pokemon = None
        self.opponent_panel = None
        self.player_panel = None
        self.message = ""
        self._state_timer = 0.0
        self._pokemon_scale = 0.0
        
        # Turn system initialization
        self.current_turn = "player"
        self.player_selected_move = None
        self.enemy_selected_move = None
        self.turn_message = ""
        self.item_panel = None
        self.player_selected_item = None
        
        # Enemy party system initialization
        self.enemy_party = []
        self.enemy_party_index = 0
        
        # pokeball catching animation
        try:
            self.pokeball_sprite = Sprite("ingame_ui/ball.png", (40, 40))
        except:
            self.pokeball_sprite = None
        self.pokeball_x = 0.0
        self.pokeball_y = 0.0
        self.pokeball_rotation = 0.0
        self.pokeball_scale = 1.0
        self.catch_panel = None
        self.shake_count = 0
        self.shake_timer = 0.0

        # Pokemon flashing animation
        self.flash_count = 0
        self.flash_timer = 0.0
        self.pokemon_visible = True
        
        # Main action buttons (will be repositioned in PLAYER_TURN)
        btn_w, btn_h = 80, 40
        
        self.fight_btn = BattleActionButton("Fight", 0, 0, btn_w, btn_h, self._on_fight_click)
        self.item_btn = BattleActionButton("Item", 0, 0, btn_w, btn_h, self._on_item_click)
        self.switch_btn = BattleActionButton("Switch", 0, 0, btn_w, btn_h, self._on_switch_click)
        self.run_btn = BattleActionButton("Run", 0, 0, btn_w, btn_h, self._on_run_click)
        
        # Move buttons (for attack selection) - 2x2 layout
        move_btn_w, move_btn_h = 120, 45
        move_gap_x = 30
        move_start_x = 150
        move_start_y = GameSettings.SCREEN_HEIGHT - 150
        
        moves = ["Woodhammer", "Headbutt", "Howl", "Leer"]
        self.move_buttons = []
        for i, move in enumerate(moves):
            x = move_start_x + (move_btn_w + move_gap_x) * (i % 2)
            y = move_start_y - (move_btn_h + 15) * (i // 2)
            btn = BattleActionButton(move, x, y, move_btn_w, move_btn_h, 
                                    lambda m=move: self._on_move_select(m))
            self.move_buttons.append(btn)

    @override
    def enter(self) -> None:
        Logger.info("Wild Pokemon Battle started")

        # Reset all battle state variables
        self.state = WildBattleState.INTRO
        self.opponent_pokemon = None
        self.player_pokemon = None
        self.opponent_panel = None
        self.player_panel = None
        self.message = ""
        self._state_timer = 0.0
        self._pokemon_scale = 0.0

        # Reset turn system
        self.current_turn = "player"
        self.player_selected_move = None
        self.enemy_selected_move = None
        self.turn_message = ""
        self.item_panel = None
        self.player_selected_item = None

        # Reset enemy party system
        self.enemy_party = []
        self.enemy_party_index = 0

        # Reset pokeball catching animation
        self.pokeball_x = 0.0
        self.pokeball_y = 0.0
        self.pokeball_rotation = 0.0
        self.pokeball_scale = 1.0
        self.catch_panel = None
        self.shake_count = 0
        self.shake_timer = 0.0

        # Reset Pokemon flashing animation
        self.flash_count = 0
        self.flash_timer = 0.0
        self.pokemon_visible = True

        # Initialize battle
        self._init_battle()
        self._next_state()

    @override
    def exit(self) -> None:
        pass
    
    def _init_battle(self) -> None:
        """Initialize battle with random enemy pokemon and their party"""
        # Generate random enemy party (1-3 pokemon)
        party_size = random.randint(1, 3)
        self.enemy_party = []
        
        for _ in range(party_size):
            # Randomly select a pokemon from the pool
            pokemon_data = random.choice(self.WILD_POKEMON_POOL)
            # Create a copy with randomized HP slightly
            enemy_pokemon = pokemon_data.copy()
            enemy_pokemon['hp'] = random.randint(
                int(enemy_pokemon['max_hp'] * 0.8),
                enemy_pokemon['max_hp']
            )
            self.enemy_party.append(enemy_pokemon)
        
        self.enemy_party_index = 0
        self.opponent_pokemon = self.enemy_party[self.enemy_party_index]
        
        Logger.info(f"Wild Pokemon Battle initiated! Enemy party size: {len(self.enemy_party)}")
        for i, pokemon in enumerate(self.enemy_party):
            Logger.info(f"  Enemy {i+1}: {pokemon['name']} (Lv.{pokemon['level']}, HP:{pokemon['hp']}/{pokemon['max_hp']})")
        
        # Initialize player pokemon
        if self.game_manager.bag and len(self.game_manager.bag._monsters_data) > 0:
            self.player_pokemon = self.game_manager.bag._monsters_data[0]
    
    def _get_next_enemy_pokemon(self) -> bool:
        """
        Try to get next pokemon from enemy party.
        Returns True if there's a next pokemon, False if party is defeated.
        """
        self.enemy_party_index += 1
        if self.enemy_party_index < len(self.enemy_party):
            self.opponent_pokemon = self.enemy_party[self.enemy_party_index]
            Logger.info(f"Enemy sent out {self.opponent_pokemon['name']}!")
            return True
        
        # Enemy party is defeated
        Logger.info("Wild Pokemon party defeated!")
        return False
    
    def _on_fight_click(self) -> None:
        self.state = WildBattleState.CHOOSE_MOVE
        self.message = "Choose a move:"
    
    def _on_item_click(self) -> None:
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return
        
        # Filter out coins - they are not battle items
        battle_items = [item for item in self.game_manager.bag.items if item['name'].lower() != 'coins' and item['name'].lower() != 'pokeball']
        
        if not battle_items:
            self.message = "No usable items in battle!"
            return
        
        self.state = WildBattleState.CHOOSE_ITEM
        self.item_panel = BattleItemPanel(
            battle_items,
            GameSettings.SCREEN_WIDTH // 2 - 150,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        )
        self.message = "Choose an item:"
    
    def _on_switch_click(self) -> None:
        """Switch pokemon - for future implementation"""
        self.message = "Switch pokemon feature coming soon!"
        self.state = WildBattleState.SWITCH_POKEMON
    
    def _show_catch_panel(self) -> None:
        """Show pokeball catching panel after opponent is defeated"""
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return
        
        # Get only pokeballs
        pokeballs = [item for item in self.game_manager.bag.items if item['name'].lower() == 'pokeball']
        
        if not pokeballs:
            self.message = "No Pokeballs available! Battle ended."
            self.state = WildBattleState.BATTLE_END
            return
        
        self.state = WildBattleState.CATCHING
        self.catch_panel = BattleItemPanel(
            pokeballs,
            GameSettings.SCREEN_WIDTH // 2 - 150,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        )
        self.message = "Use a pokeball to catch?"
    
    def _on_run_click(self) -> None:
        self.message = "Escaped from battle!"
        self._state_timer = 0.0
    
    def _on_move_select(self, move: str) -> None:
        """Execute player's move selection"""
        if self.current_turn == "player":
            self.player_selected_move = move
            self.message = f"{self.player_pokemon['name']} used {move}!"
            self.state = WildBattleState.PLAYER_TURN
            self._execute_player_attack()
    
    def _execute_player_attack(self) -> None:
        if not self.player_selected_move or not self.opponent_pokemon:
            return
        
        # Calculate damage (simplified: random between 10-20)
        damage = random.randint(10, 20)
        self.opponent_pokemon['hp'] = max(0, self.opponent_pokemon['hp'] - damage)
        
        self.message = f"{self.opponent_pokemon['name']} took {damage} damage!"
        Logger.info(f"Player attacked: {damage} damage. Opponent HP: {self.opponent_pokemon['hp']}")
        
        if self._check_battle_end():
            self.state = WildBattleState.SHOW_DAMAGE
            return
        
        # Transition to show damage state first
        self._state_timer = 0.0
        self.state = WildBattleState.SHOW_DAMAGE
    
    def _execute_enemy_attack(self) -> None:
        if not self.opponent_pokemon or not self.player_pokemon:
            return
        
        # Enemy selects a random move
        moves = ["Woodhammer", "Headbutt", "Howl", "Leer"]
        self.enemy_selected_move = random.choice(moves)
        
        # Show enemy's move selection
        self.message = f"{self.opponent_pokemon['name']} used {self.enemy_selected_move}!"
        self.turn_message = ""  # Clear any previous turn message
        Logger.info(f"Enemy selected move: {self.enemy_selected_move}")
        
        # Stay in ENEMY_TURN state to show move before applying damage
        self._state_timer = 0.0
    
    def _apply_enemy_damage(self) -> None:
        """Apply damage from enemy's selected move"""
        if not self.opponent_pokemon or not self.player_pokemon or not self.enemy_selected_move:
            return
        
        # Calculate damage
        damage = random.randint(8, 15)
        self.player_pokemon['hp'] = max(0, self.player_pokemon['hp'] - damage)
        
        self.message = f"{self.player_pokemon['name']} took {damage} damage!"
        Logger.info(f"Enemy attacked with {self.enemy_selected_move}: {damage} damage. Player HP: {self.player_pokemon['hp']}")
        
        if self._check_battle_end():
            self.state = WildBattleState.SHOW_DAMAGE
            self.enemy_selected_move = None
            return
        
        # Transition to show damage state
        self._state_timer = 0.0
        self.state = WildBattleState.SHOW_DAMAGE
        self.enemy_selected_move = None  # Reset for next turn
        
    def _check_battle_end(self) -> bool:
        """Check if battle should end and handle pokemon switching"""
        if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
            # Opponent pokemon fainted
            # Do not switch yet - let the player decide to catch or not
            return True
        
        if self.player_pokemon and self.player_pokemon['hp'] <= 0:
            self.state = WildBattleState.BATTLE_END
            self.message = f"{self.player_pokemon['name']} fainted! You lost!"
            Logger.info("Battle lost!")
            return True
        
        return False
    
    def _execute_item_attack(self, item: dict) -> None:
        if not self.opponent_pokemon:
            return
        
        # Calculate damage based on item
        damage = random.randint(5, 25)
        self.opponent_pokemon['hp'] = max(0, self.opponent_pokemon['hp'] - damage)
        
        self.message = f"{self.opponent_pokemon['name']} took {damage} damage!"
        Logger.info(f"Player used item {item['name']}: {damage} damage. Opponent HP: {self.opponent_pokemon['hp']}")
        
        # Reduce item count
        item['count'] = max(0, item['count'] - 1)
        
        if self._check_battle_end():
            self.state = WildBattleState.SHOW_DAMAGE
            return
        
        # Transition to show damage state first
        self._state_timer = 0.0
        self.state = WildBattleState.SHOW_DAMAGE
    
    def _execute_pokeball_catch(self, item: dict) -> None:
        """Execute pokeball catch animation and logic"""
        if not self.opponent_pokemon:
            return
        
        # Start pokeball animation
        self.pokeball_x = GameSettings.SCREEN_WIDTH // 2
        self.pokeball_y = GameSettings.SCREEN_HEIGHT - 100
        
        # Reduce pokeball count
        item['count'] = max(0, item['count'] - 1)
        
        self.state = WildBattleState.CATCH_ANIMATION
        self._state_timer = 0.0
        self.pokeball_rotation = 0.0
        self.pokeball_scale = 1.0
        Logger.info(f"pokeball catch animation started for {self.opponent_pokemon['name']}")
        
    def _catch_opponent_pokemon(self) -> None:
        """Complete the catch - add opponent pokemon to player's bag or increment count"""
        if not self.opponent_pokemon or not self.game_manager.bag:
            self.state = WildBattleState.BATTLE_END
            self.message = "Catch failed!"
            Logger.error("Catch failed: missing opponent_pokemon or bag")
            return
        
        # Check if pokemon already exists in bag
        existing_pokemon = None
        for monster in self.game_manager.bag.monsters:
            if monster['name'] == self.opponent_pokemon['name']:
                existing_pokemon = monster
                break
        
        if existing_pokemon:
            # Increment count if pokemon already exists
            if 'count' not in existing_pokemon:
                existing_pokemon['count'] = 1
            existing_pokemon['count'] += 1
            Logger.info(f"Caught another {self.opponent_pokemon['name']}! Count: {existing_pokemon['count']}")
        else:
            # Add new pokemon to player's bag
            caught_pokemon = {
                "name": self.opponent_pokemon['name'],
                "hp": self.opponent_pokemon['max_hp'],
                "max_hp": self.opponent_pokemon['max_hp'],
                "level": self.opponent_pokemon['level'],
                "sprite_path": self.opponent_pokemon['sprite_path'],
                "count": 1
            }
            self.game_manager.bag.monsters.append(caught_pokemon)
            Logger.info(f"Caught {self.opponent_pokemon['name']}! Added to bag.")
        
        Logger.info(f"Current monsters in bag: {len(self.game_manager.bag._monsters_data)}")
        for monster in self.game_manager.bag._monsters_data:
            count = monster.get('count', 1)
            Logger.info(f"  - {monster['name']} (x{count})")
        
        
    def _next_state(self) -> None:
        if self.state == WildBattleState.INTRO:
            self.state = WildBattleState.CHALLENGER
            self.message = f"A wild {self.opponent_pokemon['name']} appeared!"
        elif self.state == WildBattleState.CHALLENGER:
            self.state = WildBattleState.SEND_OPPONENT
            self.message = f"Wild {self.opponent_pokemon['name']}!"
        elif self.state == WildBattleState.SEND_OPPONENT:
            self.state = WildBattleState.SEND_PLAYER
            self.message = f"Go, {self.player_pokemon['name']}!"
        elif self.state == WildBattleState.SEND_PLAYER:
            self.state = WildBattleState.PLAYER_TURN
            self.current_turn = "player"
            self.message = "What will " + self.player_pokemon['name'] + " do?"
        self._state_timer = 0.0

    @override
    def update(self, dt: float) -> None:
        self._state_timer += dt
        
        if input_manager.key_pressed(pg.K_SPACE):
            if self.state == WildBattleState.CHALLENGER:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == WildBattleState.SEND_OPPONENT:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == WildBattleState.SEND_PLAYER:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == WildBattleState.SHOW_DAMAGE:
                # After showing damage, transition to next state
                if self._check_battle_end():
                    # Battle ended or next pokemon
                    if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
                        self._show_catch_panel()
                        self.message = f"{self.opponent_pokemon['name']} fainted! Catch it?"
                else:
                    # Transition to next appropriate state
                    self._state_timer = 0.0
                    if self.current_turn == "player":
                        self.state = WildBattleState.ENEMY_TURN
                        self.current_turn = "enemy"
                    else:
                        self.state = WildBattleState.PLAYER_TURN
                        self.current_turn = "player"
                        self.message = "What will " + self.player_pokemon['name'] + " do?"
                        self.turn_message = ""
            elif self.state == WildBattleState.CATCHING:
                # Player can press SPACE to skip or will select item
                pass
            elif self.state == WildBattleState.BATTLE_END:
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("game")
        
        # Handle Run Away action
        if self.state == WildBattleState.PLAYER_TURN and self._state_timer > 2.0 and self.message == "Escaped from battle!":
            self.game_manager.save("saves/game0.json")
            scene_manager.change_scene("game")
        
        if self._pokemon_scale < 1.0:
            self._pokemon_scale += dt * 2.0
        
        # Panel initialization at correct timing
        if self.opponent_panel is None and self.opponent_pokemon and self.state == WildBattleState.SEND_OPPONENT:
            self.opponent_panel = PokemonStatsPanel(
                self.opponent_pokemon,
                GameSettings.SCREEN_WIDTH - 180,
                20
            )
        
        if self.player_panel is None and self.player_pokemon and self.state == WildBattleState.SEND_PLAYER:
            self.player_panel = PokemonStatsPanel(
                self.player_pokemon,
                20,
                GameSettings.SCREEN_HEIGHT - 250
            )
        
        if self.state == WildBattleState.PLAYER_TURN:
            self.fight_btn.update(dt)
            self.item_btn.update(dt)
            self.switch_btn.update(dt)
            self.run_btn.update(dt)
        
        if self.state == WildBattleState.CHOOSE_MOVE:
            for btn in self.move_buttons:
                btn.update(dt)
        
        if self.state == WildBattleState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.update(dt)
                selected = self.item_panel.get_selected_item()
                if selected:
                    self._execute_item_attack(selected)
                
                # Close item panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = WildBattleState.PLAYER_TURN
                    self.item_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"
        
        # Catching panel handling
        if self.state == WildBattleState.CATCHING:
            if self.catch_panel:
                self.catch_panel.update(dt)
                selected = self.catch_panel.get_selected_item()
                if selected:
                    self._execute_pokeball_catch(selected)
                
                # Close catch panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    # Skip catching, move to next pokemon
                    if self._get_next_enemy_pokemon():
                        self.state = WildBattleState.SEND_OPPONENT
                        self.message = f"Wild {self.opponent_pokemon['name']} appeared!"
                        self.opponent_panel = None
                        self.catch_panel = None
                    else:
                        self.state = WildBattleState.BATTLE_END
                        self.message = "You won the battle! All wild pokemon defeated!"
                        self.catch_panel = None
        
        # pokeball catch animation
        if self.state == WildBattleState.CATCH_ANIMATION:
            # pokeball flies from player pokemon to opponent pokemon
            # 出发点：玩家宝可梦在画面中的位置（Player Pokemon在左下方）
            player_pokemon_x = 200 + 125  # Player pokemon center X
            player_pokemon_y = GameSettings.SCREEN_HEIGHT - 250 - 100  # Player pokemon center Y

            # 落点：敌方宝可梦在画面中的位置（Opponent Pokemon在右上方，提高位置）
            opponent_pokemon_x = GameSettings.SCREEN_WIDTH - 200 - 100  # Opponent pokemon center X
            opponent_pokemon_y = 80 + 50  # 提高落点位置（原本是 80 + 100）

            animation_duration = 1.5  # 飞行1.5秒
            progress = min(self._state_timer / animation_duration, 1.0)

            # Ease out cubic for smoother throw
            ease_progress = 1 - (1 - progress) ** 3

            # 水平方向：線性移動
            self.pokeball_x = player_pokemon_x + (opponent_pokemon_x - player_pokemon_x) * ease_progress

            # 垂直方向：拋物線移動
            arc_height = 200
            parabola = -4 * (progress - 0.5) ** 2 + 1
            self.pokeball_y = player_pokemon_y + (opponent_pokemon_y - player_pokemon_y) * ease_progress - arc_height * parabola

            # Rotation and Scale - 随着距离慢慢缩小产生距离感
            self.pokeball_rotation = progress * 720  # Spin 2 times
            self.pokeball_scale = 1.0 - (0.5 * progress)  # 从1.0缩小到0.5

            if progress >= 1.0:
                # Animation complete - transition to flashing state
                self._state_timer = 0.0
                self.state = WildBattleState.CATCH_FLASHING
                self.pokeball_x = opponent_pokemon_x
                self.pokeball_y = opponent_pokemon_y
                self.flash_count = 0
                self.flash_timer = 0.0
                self.pokemon_visible = True
                Logger.info(f"Pokéball hit {self.opponent_pokemon['name']}!")

        # Pokemon flashing animation (Pokemon flashes 3 times before being caught)
        if self.state == WildBattleState.CATCH_FLASHING:
            flash_interval = 0.5  # 每0.5秒闪烁一次
            self.flash_timer += dt

            # 切换可见性
            if self.flash_timer >= flash_interval:
                self.flash_timer = 0
                self.pokemon_visible = not self.pokemon_visible
                if not self.pokemon_visible:
                    # 完成一次闪烁（消失）
                    self.flash_count += 1
                    Logger.info(f"Pokemon flash {self.flash_count}/3")

                if self.flash_count >= 3 and not self.pokemon_visible:
                    # 闪烁3次后转到falling状态
                    self.state = WildBattleState.CATCH_FALLING
                    self._state_timer = 0.0
                    self.pokemon_visible = False  # 保持不可见
                    Logger.info("Pokemon disappeared, ball falling!")

        # Pokeball falling animation (Ball drops to ground)
        if self.state == WildBattleState.CATCH_FALLING:
            fall_duration = 0.4
            progress = min(self._state_timer / fall_duration, 1.0)

            # 从击中位置开始计算
            start_y = 80 + 50  # 击中敌方宝可梦的位置
            ground_level = 280  # 地面高度（提高了很多，原本是450）

            # Bounce effect
            bounce_height = 30
            if progress < 0.5:
                # Fall down
                p = progress * 2
                self.pokeball_y = start_y + (ground_level - start_y) * p
            else:
                # Small bounce
                p = (progress - 0.5) * 2
                self.pokeball_y = ground_level - bounce_height * (1 - (2*p - 1)**2)

            if progress >= 1.0:
                self.pokeball_y = ground_level  # Ground level
                self._state_timer = 0.0
                self.state = WildBattleState.CATCH_SHAKE
                self.shake_count = 0
                self.shake_timer = 0.0
        
        # Pokeball shaking animation
        if self.state == WildBattleState.CATCH_SHAKE:
            shake_interval = 1.0
            self.shake_timer += dt
            
            # Shake logic: 3 shakes
            if self.shake_timer > shake_interval:
                self.shake_timer = 0
                self.shake_count += 1
                if self.shake_count >= 3:
                    self.state = WildBattleState.CATCH_SUCCESS
                    self._state_timer = 0.0
                    self._catch_opponent_pokemon()
            
            # Calculate rotation for shake
            t = self.shake_timer / shake_interval
            if t < 0.2: # Shake left
                self.pokeball_rotation = 15 * math.sin(t * 5 * math.pi)
            elif t < 0.4: # Shake right
                self.pokeball_rotation = -15 * math.sin((t-0.2) * 5 * math.pi)
            else:
                self.pokeball_rotation = 0
                
        if self.state == WildBattleState.CATCH_SUCCESS:
            if self._state_timer > 1.0: # Wait 1 second after catch
                self.game_manager.save("saves/game0.json")
                self.game_manager.load("saves/game0.json")
                
                # Check if there are more enemy pokemon to catch
                if self._get_next_enemy_pokemon():
                    # Show next pokemon
                    self.state = WildBattleState.SEND_OPPONENT
                    self.message = f"Wild {self.opponent_pokemon['name']} appeared!"
                    self.opponent_panel = None
                else:
                    # All pokemon caught/defeated
                    self.state = WildBattleState.BATTLE_END
                    self.message = "You caught all wild pokemon!"
                
        
        
        # Enemy turn handling
        if self.state == WildBattleState.ENEMY_TURN:
            if self._state_timer > 1.5 and self.enemy_selected_move is None:
                # First call to ENEMY_TURN - select and show move
                self._execute_enemy_attack()
            elif self.enemy_selected_move is not None:
                # Wait for SPACE or auto-advance after 3 seconds
                if self._state_timer > 3.0 or input_manager.key_pressed(pg.K_SPACE):
                    self._apply_enemy_damage()
        
        # Update panels for HP changes
        if self.opponent_panel:
            self.opponent_panel.update_pokemon(self.opponent_pokemon)
        if self.player_panel:
            self.player_panel.update_pokemon(self.player_pokemon)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        # Draw panels in appropriate states
        if self.opponent_panel and self.state in (WildBattleState.SEND_OPPONENT, WildBattleState.SEND_PLAYER, WildBattleState.PLAYER_TURN, WildBattleState.ENEMY_TURN, WildBattleState.BATTLE_END, WildBattleState.CATCHING, WildBattleState.CATCH_ANIMATION, WildBattleState.CATCH_FLASHING, WildBattleState.CATCH_FALLING, WildBattleState.SHOW_DAMAGE, WildBattleState.CHOOSE_MOVE, WildBattleState.CHOOSE_ITEM):
            self.opponent_panel.draw(screen)
        
        if self.player_panel and self.state in (WildBattleState.SEND_PLAYER, WildBattleState.PLAYER_TURN, WildBattleState.ENEMY_TURN, WildBattleState.BATTLE_END, WildBattleState.CATCHING, WildBattleState.CATCH_ANIMATION, WildBattleState.CATCH_FLASHING, WildBattleState.CATCH_FALLING, WildBattleState.SHOW_DAMAGE, WildBattleState.CHOOSE_MOVE, WildBattleState.CHOOSE_ITEM):
            self.player_panel.draw(screen)
        
        
        if (self.state == WildBattleState.SEND_OPPONENT or self.state == WildBattleState.SEND_PLAYER or self.state in (WildBattleState.PLAYER_TURN, WildBattleState.ENEMY_TURN, WildBattleState.BATTLE_END, WildBattleState.CATCHING, WildBattleState.CATCH_ANIMATION, WildBattleState.CATCH_FLASHING, WildBattleState.SHOW_DAMAGE)) and self.opponent_pokemon:
            sprite = Sprite(self.opponent_pokemon["sprite_path"], (200, 200))
            if self.state == WildBattleState.SEND_OPPONENT:
                scale = min(self._pokemon_scale, 1.0)
            else:
                scale = 1.0
            size = int(200 * scale)
            scaled_sprite = pg.transform.scale(sprite.image, (size, size))
            x = GameSettings.SCREEN_WIDTH - size - 150
            y = 80

            # 绘制逻辑：
            # - CATCH_FLASHING: 根据pokemon_visible决定是否显示（闪烁效果）
            # - CATCH_FALLING, CATCH_SHAKE, CATCH_SUCCESS: 完全隐藏
            # - 其他状态: 正常显示
            should_draw = True
            if self.state == WildBattleState.CATCH_FLASHING:
                should_draw = self.pokemon_visible
            elif self.state in (WildBattleState.CATCH_FALLING, WildBattleState.CATCH_SHAKE, WildBattleState.CATCH_SUCCESS):
                should_draw = False

            if should_draw:
                screen.blit(scaled_sprite, (x, y))
        
        if (self.state == WildBattleState.SEND_PLAYER or self.state in (WildBattleState.PLAYER_TURN, WildBattleState.ENEMY_TURN, WildBattleState.BATTLE_END, WildBattleState.CATCHING, WildBattleState.CATCH_ANIMATION, WildBattleState.SHOW_DAMAGE)) and self.player_pokemon:
            sprite = Sprite(self.player_pokemon["sprite_path"], (250, 250))
            if self.state == WildBattleState.SEND_PLAYER:
                scale = min(self._pokemon_scale, 1.0)
            else:
                scale = 1.0
            size = int(250 * scale)
            scaled_sprite = pg.transform.scale(sprite.image, (size, size))
            x = 200
            y = GameSettings.SCREEN_HEIGHT - size - 200
            screen.blit(scaled_sprite, (x, y))
        
        box_h, box_w = 120, GameSettings.SCREEN_WIDTH - 40
        box_x, box_y = 20, GameSettings.SCREEN_HEIGHT - box_h - 20
        
        pg.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_w, box_h))
        pg.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 2)
        
        # Display main message (skip during catch animation to avoid overlap)
        if self.state not in (WildBattleState.CATCH_ANIMATION, WildBattleState.CATCH_FLASHING, WildBattleState.CATCH_FALLING, WildBattleState.CATCH_SHAKE, WildBattleState.CATCH_SUCCESS):
            msg_text = self._message_font.render(self.message, True, (255, 255, 255))
            screen.blit(msg_text, (box_x + 10, box_y + 10))
        
        # Display turn message (damage dealt)
        if self.turn_message and self.state in (WildBattleState.PLAYER_TURN, WildBattleState.ENEMY_TURN, WildBattleState.PLAYER_TURN):
            turn_text = self._message_font.render(self.turn_message, True, (255, 200, 100))
            screen.blit(turn_text, (box_x + 10, box_y + 35))
        
        if self.state not in (WildBattleState.PLAYER_TURN, WildBattleState.ENEMY_TURN, WildBattleState.CHOOSE_MOVE, WildBattleState.BATTLE_END, WildBattleState.SHOW_DAMAGE):
            if self.state in (WildBattleState.CHALLENGER, WildBattleState.SEND_OPPONENT, WildBattleState.SEND_PLAYER):
                hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
        
        if self.state == WildBattleState.PLAYER_TURN:
            # Position buttons more centered
            btn_w, btn_h = 80, 40
            gap = 10
            btn_start_x = box_x + 300
            btn_y = box_y + 50
            
            self.fight_btn.rect.x = btn_start_x
            self.fight_btn.rect.y = btn_y
            self.fight_btn.rect.width = btn_w
            self.fight_btn.rect.height = btn_h
            
            self.item_btn.rect.x = btn_start_x + btn_w + gap
            self.item_btn.rect.y = btn_y
            self.item_btn.rect.width = btn_w
            self.item_btn.rect.height = btn_h
            
            self.switch_btn.rect.x = btn_start_x + (btn_w + gap) * 2
            self.switch_btn.rect.y = btn_y
            self.switch_btn.rect.width = btn_w
            self.switch_btn.rect.height = btn_h
            
            self.run_btn.rect.x = btn_start_x + (btn_w + gap) * 3
            self.run_btn.rect.y = btn_y
            self.run_btn.rect.width = btn_w
            self.run_btn.rect.height = btn_h
            
            self.fight_btn.draw(screen)
            self.item_btn.draw(screen)
            self.switch_btn.draw(screen)
            self.run_btn.draw(screen)
        
        if self.state == WildBattleState.CHOOSE_MOVE:
            start_x = box_x + 180
            start_y = box_y + 120
            btn_w = 100  # 按鈕可能要窄一點才塞得下
            gap = 30     # 間距

            for i, btn in enumerate(self.move_buttons):
                # 每個按鈕往右推移
                current_x = start_x + i * (btn_w + gap)
                current_y = start_y - 100
                
                # 更新按鈕位置
                btn.rect.topleft = (current_x, current_y)
                
                btn.draw(screen)
        
        if self.state == WildBattleState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.draw(screen)
            
            hint_text = self._message_font.render("Press ESC to cancel", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == WildBattleState.CATCHING:
            if self.catch_panel:
                self.catch_panel.draw(screen)
            
            hint_text = self._message_font.render("Press ESC to skip", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state in (WildBattleState.CATCH_ANIMATION, WildBattleState.CATCH_FLASHING, WildBattleState.CATCH_FALLING, WildBattleState.CATCH_SHAKE, WildBattleState.CATCH_SUCCESS):
            # Draw pokeball
            if self.pokeball_sprite:
                # Apply rotation and scale
                scaled_size = int(40 * self.pokeball_scale)
                scaled_img = pg.transform.scale(self.pokeball_sprite.image, (scaled_size, scaled_size))
                rotated_img = pg.transform.rotate(scaled_img, self.pokeball_rotation)

                # Center the rotated image
                rect = rotated_img.get_rect(center=(int(self.pokeball_x), int(self.pokeball_y)))
                screen.blit(rotated_img, rect)

            if self.state == WildBattleState.CATCH_ANIMATION:
                msg_text = self._message_font.render("Throwing Pokeball...", True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
            elif self.state == WildBattleState.CATCH_FLASHING:
                msg_text = self._message_font.render("Catching Pokemon...", True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
            elif self.state == WildBattleState.CATCH_SHAKE:
                shake_text = ["Wiggle...", "Wobble...", "Shake..."]
                idx = min(self.shake_count, 2)
                msg_text = self._message_font.render(shake_text[idx], True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
            elif self.state == WildBattleState.CATCH_SUCCESS:
                msg_text = self._message_font.render("Gotcha! " + self.opponent_pokemon['name'] + " was caught, added to bag!", True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
        
        if self.state == WildBattleState.SHOW_DAMAGE:
            # Show damage message, wait for SPACE
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == WildBattleState.ENEMY_TURN and self.enemy_selected_move is not None:
            # Show hint to continue during enemy attack display
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == WildBattleState.BATTLE_END:
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))

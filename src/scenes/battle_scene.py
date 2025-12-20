from __future__ import annotations
import pygame as pg
import math
import random
from src.scenes.scene import Scene
from src.sprites import BackgroundSprite, Sprite
from src.sprites.animated_battle_sprite import AnimatedBattleSprite
from src.sprites.attack_animation import AttackAnimation
from src.utils import GameSettings, Logger
from src.core.services import input_manager, scene_manager
from src.core import GameManager
from src.interface.components import PokemonStatsPanel, BattleActionButton
from src.interface.components.battle_item_panel import BattleItemPanel
from src.interface.components.battle_switch_panel import BattleSwitchPanel
from src.utils.definition import Monster
from src.utils.pokemon_data import POKEMON_SPECIES, calculate_damage, MOVES_DATABASE, STATUS_EFFECTS, calculate_type_effectiveness

from typing import override

from enum import Enum


class BattleState(Enum):
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
    CATCH_FLASHING = 13  # Pokemon flashing when caught
    CATCH_FALLING = 14  # Pokeball falling after catch
    CATCH_SHAKE = 15    # Pokeball shaking on ground
    CATCH_SUCCESS = 16  # Catch successful
    CHOOSE_SWITCH = 17  # Choose Pokemon to switch


class BattleScene(Scene):
    background: BackgroundSprite
    opponent_name: str
    game_manager: GameManager
    state: BattleState
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
    
    # pokeball catching animation
    pokeball_sprite: Sprite | None
    pokeball_x: float
    pokeball_y: float
    catch_panel: BattleItemPanel | None
    
    def __init__(self, game_manager: GameManager, opponent_name: str = "Rival"):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.opponent_name = opponent_name
        self.game_manager = game_manager
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 24)
        self._message_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)
        
        self.state = BattleState.INTRO
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
    CATCH_SUCCESS = 15  # Catch successful


class BattleScene(Scene):
    background: BackgroundSprite
    opponent_name: str
    game_manager: GameManager
    state: BattleState
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

    # Animated sprites
    opponent_sprite: AnimatedBattleSprite | None
    player_sprite: AnimatedBattleSprite | None

    # Attack animation
    attack_animation: AttackAnimation | None

    # Potion buffs
    attack_boost: float
    defense_boost: float
    attack_boost_used: bool  # Track if attack boost was used this turn
    defense_boost_used: bool  # Track if defense boost was used this turn

    # Damage calculation display
    damage_formula: str  # Formula string to display
    show_damage_formula: bool  # Whether to show the formula

    # Switch panel
    switch_panel: BattleSwitchPanel | None

    def __init__(self, game_manager: GameManager, opponent_name: str = "Rival"):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.opponent_name = opponent_name
        self.game_manager = game_manager
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 24)
        self._message_font = pg.font.Font('assets/fonts/Minecraft.ttf', 16)

        self.state = BattleState.INTRO
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
        self.effectiveness_message = ""  # Type effectiveness message

        # Potion buffs
        self.attack_boost = 1.0  # Multiplier for attack damage
        self.defense_boost = 1.0  # Multiplier for defense (reduces incoming damage)
        self.attack_boost_used = False
        self.defense_boost_used = False

        # Damage calculation display
        self.damage_formula = ""
        self.show_damage_formula = False

        # pokeball catching animation
        self.pokeball_sprite = Sprite("ingame_ui/ball.png", (40, 40))
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

        # Animated sprites (initialized in _init_pokemon)
        self.opponent_sprite = None
        self.player_sprite = None

        # Attack animation
        self.attack_animation = None

        # Switch panel
        self.switch_panel = None

        # Main action buttons (will be repositioned in PLAYER_TURN)
        btn_w, btn_h = 120, 50  # Wider and taller for better appearance

        self.fight_btn = BattleActionButton("Fight", 0, 0, btn_w, btn_h, self._on_fight_click, button_type="fight")
        self.item_btn = BattleActionButton("Item", 0, 0, btn_w, btn_h, self._on_item_click, button_type="item")
        self.switch_btn = BattleActionButton("Switch", 0, 0, btn_w, btn_h, self._on_switch_click, button_type="switch")
        self.run_btn = BattleActionButton("Run", 0, 0, btn_w, btn_h, self._on_run_click, button_type="run")
        
        # Move buttons (for attack selection) - will be populated dynamically
        self.move_buttons = []

    @override
    def enter(self) -> None:
        Logger.info(f"Battle started against {self.opponent_name}")

        # Reset all battle state variables
        self.state = BattleState.INTRO
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
        self.effectiveness_message = ""

        # Reset potion buffs
        self.attack_boost = 1.0
        self.defense_boost = 1.0
        self.attack_boost_used = False
        self.defense_boost_used = False

        # Reset switch panel
        self.switch_panel = None

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
        self._init_pokemon()
        self._next_state()

    @override
    def exit(self) -> None:
        pass
    
    def _init_pokemon(self) -> None:
        # Pool of available opponents with varied stats
        # Using animated sprites from sprites folder (sprite1-16)
        opponent_pool = [
            {"name": "Budling", "base_hp": 40, "level_range": (5, 10), "sprite_id": 1, "rarity": "common"},
            {"name": "Florion", "base_hp": 50, "level_range": (6, 12), "sprite_id": 2, "rarity": "common"},
            {"name": "Verdantus", "base_hp": 55, "level_range": (8, 14), "sprite_id": 3, "rarity": "uncommon"},
            {"name": "Rockpaw", "base_hp": 55, "level_range": (7, 13), "sprite_id": 4, "rarity": "common"},
            {"name": "Ravenix", "base_hp": 42, "level_range": (6, 11), "sprite_id": 5, "rarity": "common"},
            {"name": "Frostfox", "base_hp": 48, "level_range": (7, 12), "sprite_id": 6, "rarity": "uncommon"},
            {"name": "Embear", "base_hp": 43, "level_range": (6, 12), "sprite_id": 7, "rarity": "common"},
            {"name": "Blazefang", "base_hp": 52, "level_range": (9, 15), "sprite_id": 8, "rarity": "uncommon"},
            {"name": "Charizord", "base_hp": 60, "level_range": (12, 18), "sprite_id": 9, "rarity": "rare"},
            {"name": "Toxling", "base_hp": 44, "level_range": (8, 12), "sprite_id": 10, "rarity": "uncommon"},
            {"name": "Venomcoil", "base_hp": 50, "level_range": (10, 16), "sprite_id": 11, "rarity": "rare"},
            {"name": "Aquabit", "base_hp": 41, "level_range": (5, 10), "sprite_id": 12, "rarity": "common"},
            {"name": "Tidecrest", "base_hp": 56, "level_range": (11, 17), "sprite_id": 13, "rarity": "rare"},
            {"name": "Leviathan", "base_hp": 65, "level_range": (14, 20), "sprite_id": 14, "rarity": "rare"},
            {"name": "Larvite", "base_hp": 38, "level_range": (5, 9), "sprite_id": 15, "rarity": "common"},
            {"name": "Beetlord", "base_hp": 62, "level_range": (15, 22), "sprite_id": 16, "rarity": "legendary"},
        ]

        # Weighted random selection based on rarity
        rarity_weights = {"common": 50, "uncommon": 30, "rare": 15, "legendary": 5}
        weighted_pool = []
        for opponent in opponent_pool:
            weight = rarity_weights.get(opponent["rarity"], 10)
            weighted_pool.extend([opponent] * weight)

        # Select random opponent
        selected = random.choice(weighted_pool)

        # Generate random level within range
        level = random.randint(selected["level_range"][0], selected["level_range"][1])

        # Calculate HP with some variance (±20%)
        hp_variance = random.uniform(0.8, 1.2)
        max_hp = int(selected["base_hp"] * hp_variance)

        # Calculate attack and defense stats based on level (base 10, scales with level)
        attack = int(10 + level * 0.5)
        defense = int(10 + level * 0.5)

        # Build sprite paths
        sprite_base_path = f"sprites/sprite{selected['sprite_id']}"  # For animated sprite
        panel_sprite_path = f"sprites/sprite{selected['sprite_id']}.png"  # For panel (static image)

        # Get Pokemon species data for type and moves
        species_data = POKEMON_SPECIES.get(selected["name"], {"type": "None", "moves": ["QuickSlash"]})

        self.opponent_pokemon = {
            "name": selected["name"],
            "hp": max_hp,
            "max_hp": max_hp,
            "level": level,
            "attack": attack,
            "defense": defense,
            "sprite_path": panel_sprite_path,  # Panel uses the static .png file
            "type": species_data["type"],
            "moves": species_data["moves"].copy(),
            "status": None,  # Initialize with no status effect
            "status_turns": 0
        }

        # Create animated sprite for opponent
        self.opponent_sprite = AnimatedBattleSprite(
            base_path=sprite_base_path,
            size=(200, 200),
            frames=4,
            loop_speed=0.8
        )


        # Create animated sprite for player (if they have a sprite_path with animated version)
        if self.game_manager.bag and len(self.game_manager.bag._monsters_data) > 0:
            self.player_pokemon = self.game_manager.bag._monsters_data[0]


            
            player_sprite_path = self.player_pokemon.get("sprite_path", "")

            if "sprite" in player_sprite_path and not "menu_sprites" in player_sprite_path:
                self.player_sprite = AnimatedBattleSprite(
                    base_path=player_sprite_path.replace(".png", ""),
                    size=(250, 250),
                    frames=4,
                    loop_speed=0.8
                )
            else:
                self.player_sprite = None
    
    def _init_move_buttons(self) -> None:
        """Initialize move buttons based on player's Pokemon moves"""
        if not self.player_pokemon or "moves" not in self.player_pokemon:
            return

        self.move_buttons = []
        # Button size - wider to accommodate icon and text
        move_btn_w, move_btn_h = 234, 50  # 180 * 1.3 = 234, wider buttons for move name + damage
        move_gap = 25  # Larger gap between buttons

        moves = self.player_pokemon["moves"]
        num_moves = len(moves)

        # Calculate total width needed for all buttons in a row
        total_width = move_btn_w * num_moves + move_gap * (num_moves - 1)

        # Center buttons horizontally
        move_start_x = (GameSettings.SCREEN_WIDTH - total_width) // 2
        move_start_y = GameSettings.SCREEN_HEIGHT - 150  # Move buttons higher above message box

        # Get stats for damage calculation
        attacker_type = self.player_pokemon.get("type", "None")
        defender_type = self.opponent_pokemon.get("type", "None") if self.opponent_pokemon else "None"
        attack = self.player_pokemon.get("attack", 10)
        defense = self.opponent_pokemon.get("defense", 10) if self.opponent_pokemon else 10
        level = self.player_pokemon.get("level", 10)

        attack = attack * self.attack_boost
        
        for i, move in enumerate(moves):
            # Calculate estimated damage for this move
            estimated_damage, _ = calculate_damage(
                move,
                attacker_type,
                defender_type,
                level,
                attack,
                defense
            )

            # Create button text with move name and damage
            button_text = f"{move} ({estimated_damage})"

            # Layout: all buttons in a single horizontal row
            x = move_start_x + i * (move_btn_w + move_gap)
            y = move_start_y

            btn = BattleActionButton(button_text, x, y, move_btn_w, move_btn_h,
                                    lambda m=move: self._on_move_select(m),
                                    is_move_button=True)  # Mark as move button for special styling
            self.move_buttons.append(btn)

    def _on_fight_click(self) -> None:
        self._init_move_buttons()  # Initialize move buttons with player's moves
        self.state = BattleState.CHOOSE_MOVE
        self.message = "Choose a move:"
    
    def _on_item_click(self) -> None:
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return

        # Filter to only show potions (health-potion, strength-potion, potion/defense-potion)
        # Exclude coins and pokeballs
        battle_items = [item for item in self.game_manager.bag.items
                       if item['name'].lower() != 'coins'
                       and item['name'].lower() != 'pokeball'
                       and ('potion' in item['name'].lower() or 'heal' in item['name'].lower())]

        if not battle_items:
            self.message = "No usable potions in battle!"
            return

        self.state = BattleState.CHOOSE_ITEM
        self.item_panel = BattleItemPanel(
            battle_items,
            GameSettings.SCREEN_WIDTH // 2 - 150,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        )
        self.message = "Choose a potion:"

    def _on_switch_click(self) -> None:
        """Handle switch button click - show Pokemon selection panel"""
        if not self.game_manager.bag or len(self.game_manager.bag.monsters) <= 1:
            self.message = "No other Pokemon to switch to!"
            return

        # Get current Pokemon index (player pokemon is at index 0)
        current_pokemon_index = 0

        # Filter out fainted Pokemon (HP <= 0) - this is done in BattleSwitchPanel
        available_pokemon = [p for i, p in enumerate(self.game_manager.bag.monsters)
                           if i != current_pokemon_index and p.get("hp", 0) > 0]

        if not available_pokemon:
            self.message = "No healthy Pokemon to switch to!"
            return

        self.state = BattleState.CHOOSE_SWITCH
        self.switch_panel = BattleSwitchPanel(
            self.game_manager.bag.monsters,
            current_pokemon_index,
            GameSettings.SCREEN_WIDTH // 2 - 250,
            GameSettings.SCREEN_HEIGHT // 2 - 250,
            width=500,
            height=500
        )
        self.message = "Choose a Pokemon to switch:"

    def _show_catch_panel(self) -> None:
        """Show pokeball catching panel after opponent is defeated"""
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return
        
        # Get only pokeballs
        pokeballs = [item for item in self.game_manager.bag.items if item['name'].lower() == 'pokeball']
        
        if not pokeballs:
            self.message = "No Pokeballs available! Battle ended."
            self.state = BattleState.BATTLE_END
            return
        
        self.state = BattleState.CATCHING
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
        """Handle move selection and check status effects"""
        if self.current_turn == "player":
            # Check if status blocks action
            blocked, status_msg = self._check_status_blocks_action(self.player_pokemon)

            if blocked:
                # Can't attack due to status
                self.player_selected_move = None
                self.message = status_msg
                self.state = BattleState.SHOW_DAMAGE
                self._state_timer = 0.0
                Logger.info(f"Player's turn blocked by status: {status_msg}")
            else:
                # Normal attack
                self.player_selected_move = move
                self.message = f"{self.player_pokemon['name']} used {move}!"
                self.state = BattleState.PLAYER_TURN
                self._execute_player_attack()
    
    def _execute_player_attack(self) -> None:
        if not self.player_selected_move or not self.opponent_pokemon:
            return

        # Trigger player attack animation
        if self.player_sprite:
            self.player_sprite.switch_animation("attack")

        # Create attack effect animation at opponent position
        move_data = MOVES_DATABASE.get(self.player_selected_move)
        if move_data and move_data.get("animation"):
            # Position animation at opponent pokemon
            opponent_x = GameSettings.SCREEN_WIDTH - 150 - 100
            opponent_y = 80 + 100
            self.attack_animation = AttackAnimation(
                move_data["animation"],
                (opponent_x, opponent_y),
                duration=0.6
            )

        # Calculate damage with type effectiveness
        attacker_type = self.player_pokemon.get("type", "None")
        defender_type = self.opponent_pokemon.get("type", "None")
        level = self.player_pokemon.get("level", 10)
        attack = self.player_pokemon.get("attack", 10)

        defense = self.opponent_pokemon.get("defense", 10)

        # Apply burn status effect (reduces attack by 50%)
        if self.player_pokemon.get("status") == "burn":
            burn_data = STATUS_EFFECTS["burn"]
            attack = int(attack * burn_data["affects_attack"])

        attack = attack * self.attack_boost

        # Get move data for formula display
        move_data = MOVES_DATABASE.get(self.player_selected_move)
        move_power = move_data["power"] if move_data else 1.0
        type_mult, _ = calculate_type_effectiveness(attacker_type, defender_type)

        # Calculate damage and generate formula
        damage, effectiveness_msg = calculate_damage(
            self.player_selected_move,
            attacker_type,
            defender_type,
            level,
            attack,
            defense
        )

        # Generate damage formula display
        total_attack = attack * move_power * type_mult
        self.damage_formula = f"ATK:{int(attack)} x Skill:{move_power} x Type:{type_mult} - DEF:{defense} = {int(total_attack)} - {defense} = {damage}"
        self.show_damage_formula = True

        self.opponent_pokemon['hp'] = max(0, self.opponent_pokemon['hp'] - damage)
        self.effectiveness_message = effectiveness_msg

        self.message = f"{self.opponent_pokemon['name']} took {damage} damage!"
        if effectiveness_msg:
            self.message += f" {effectiveness_msg}"

        # Try to apply status effect from move
        if move_data and "status_effect" in move_data:
            status_effect = move_data["status_effect"]
            status_chance = move_data.get("status_chance", 0.3)

            # Check if opponent already has a status
            if not self.opponent_pokemon.get("status"):
                if random.random() < status_chance:
                    self._apply_status(self.opponent_pokemon, status_effect)
                    status_name = STATUS_EFFECTS[status_effect]["name"]
                    self.message += f" {self.opponent_pokemon['name']} is {status_name}!"
                    Logger.info(f"Applied {status_effect} to opponent")

        Logger.info(f"Player attacked with {self.player_selected_move}: {damage} damage. {effectiveness_msg}. Opponent HP: {self.opponent_pokemon['hp']}")

        # Reset attack boost after it's been used once
        if self.attack_boost_used:
            self.attack_boost = 1.0
            self.attack_boost_used = False
        elif self.attack_boost > 1.0:
            # Mark as used if boost is active
            self.attack_boost_used = True

        if self._check_battle_end():
            self.state = BattleState.SHOW_DAMAGE
            return

        # Transition to show damage state first
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE
    
    def _execute_enemy_attack(self) -> None:
        if not self.opponent_pokemon or not self.player_pokemon:
            return

        # Check if status blocks action
        blocked, status_msg = self._check_status_blocks_action(self.opponent_pokemon)

        if blocked:
            # Can't attack due to status
            self.enemy_selected_move = None
            self.message = status_msg
            self.state = BattleState.SHOW_DAMAGE
            self._state_timer = 0.0
            Logger.info(f"Enemy's turn blocked by status: {status_msg}")
            return

        # Enemy selects a random move from their moveset
        moves = self.opponent_pokemon.get("moves", ["QuickSlash"])
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

        # Trigger opponent attack animation
        if self.opponent_sprite:
            self.opponent_sprite.switch_animation("attack")

        # Create attack effect animation at player position
        move_data = MOVES_DATABASE.get(self.enemy_selected_move)
        if move_data and move_data.get("animation"):
            # Position animation at player pokemon
            player_x = 200 + 125
            player_y = GameSettings.SCREEN_HEIGHT - 250 - 100
            self.attack_animation = AttackAnimation(
                move_data["animation"],
                (player_x, player_y),
                duration=0.6
            )

        # Calculate damage with type effectiveness
        attacker_type = self.opponent_pokemon.get("type", "None")
        defender_type = self.player_pokemon.get("type", "None")
        level = self.opponent_pokemon.get("level", 10)
        attack = self.opponent_pokemon.get("attack", 10)
        defense = self.player_pokemon.get("defense", 10)

        # Apply burn status effect (reduces attack by 50%)
        if self.opponent_pokemon.get("status") == "burn":
            burn_data = STATUS_EFFECTS["burn"]
            attack = int(attack * burn_data["affects_attack"])

 
        defense = int(defense * self.defense_boost)

        # Get move data for formula display
        move_power = move_data["power"] if move_data else 1.0
        type_mult, _ = calculate_type_effectiveness(attacker_type, defender_type)

        damage, effectiveness_msg = calculate_damage(
            self.enemy_selected_move,
            attacker_type,
            defender_type,
            level,
            attack,
            defense
        )

        # Generate damage formula display
        total_attack = attack * move_power * type_mult
        self.damage_formula = f"ATK:{int(attack)} x Skill:{move_power} x Type:{type_mult} - DEF:{defense} = {int(total_attack)} - {defense} = {damage}"
        self.show_damage_formula = True

        self.player_pokemon['hp'] = max(0, self.player_pokemon['hp'] - damage)
        self.effectiveness_message = effectiveness_msg

        self.message = f"{self.player_pokemon['name']} took {damage} damage!"
        if effectiveness_msg:
            self.message += f" {effectiveness_msg}"

        # Try to apply status effect from move
        if move_data and "status_effect" in move_data:
            status_effect = move_data["status_effect"]
            status_chance = move_data.get("status_chance", 0.3)

            # Check if player already has a status
            if not self.player_pokemon.get("status"):
                if random.random() < status_chance:
                    self._apply_status(self.player_pokemon, status_effect)
                    status_name = STATUS_EFFECTS[status_effect]["name"]
                    self.message += f" {self.player_pokemon['name']} is {status_name}!"
                    Logger.info(f"Applied {status_effect} to player")

        Logger.info(f"Enemy attacked with {self.enemy_selected_move}: {damage} damage. {effectiveness_msg}. Player HP: {self.player_pokemon['hp']}")

        # Reset defense boost after it's been used once
        if self.defense_boost_used:
            self.defense_boost = 1.0
            self.defense_boost_used = False
        elif self.defense_boost > 1.0:
            # Mark as used if boost is active
            self.defense_boost_used = True

        if self._check_battle_end():
            self.state = BattleState.SHOW_DAMAGE
            self.enemy_selected_move = None
            return

        # Transition to show damage state
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE
        self.enemy_selected_move = None  # Reset for next turn
        
    def _apply_status(self, pokemon: Monster, status: str) -> None:
        """Apply a status effect to a pokemon"""
        if status not in STATUS_EFFECTS:
            return

        pokemon["status"] = status

        # Set duration for sleep status
        if status == "sleep":
            duration_range = STATUS_EFFECTS[status].get("duration_range", (1, 3))
            pokemon["status_turns"] = random.randint(duration_range[0], duration_range[1])
        else:
            pokemon["status_turns"] = 0

    def _check_status_blocks_action(self, pokemon: Monster) -> tuple[bool, str]:
        """
        Check if status effect blocks the pokemon's action

        Returns:
            tuple[bool, str]: (blocked, message)
        """
        status = pokemon.get("status")
        if not status or status not in STATUS_EFFECTS:
            return (False, "")

        status_data = STATUS_EFFECTS[status]
        pokemon_name = pokemon["name"]

        # Sleep always blocks
        if status == "sleep":
            turns_left = pokemon.get("status_turns", 0)
            if turns_left > 0:
                return (True, f"{pokemon_name} is fast asleep! Zzz...")
            else:
                # Wake up
                pokemon["status"] = None
                pokemon["status_turns"] = 0
                return (False, f"{pokemon_name} woke up!")

        # Paralysis has a chance to block
        elif status == "paralysis":
            block_chance = status_data["blocks_action"]
            if random.random() < block_chance:
                return (True, f"{pokemon_name} is paralyzed and can't move!")

        return (False, "")

    def _apply_status_damage(self, pokemon: Monster) -> int:
        """
        Apply end-of-turn status damage (poison, burn)

        Returns:
            int: Damage dealt by status
        """
        status = pokemon.get("status")
        if not status or status not in STATUS_EFFECTS:
            return 0

        status_data = STATUS_EFFECTS[status]
        damage_percent = status_data.get("damage_per_turn", 0.0)

        if damage_percent > 0:
            max_hp = pokemon.get("max_hp", 100)
            damage = int(max_hp * damage_percent)
            pokemon["hp"] = max(0, pokemon["hp"] - damage)
            return damage

        return 0

    def _update_status_turns(self, pokemon: Monster) -> None:
        """Update status turn counter (for sleep)"""
        status = pokemon.get("status")
        if status == "sleep":
            turns_left = pokemon.get("status_turns", 0)
            if turns_left > 0:
                pokemon["status_turns"] = turns_left - 1

    def _check_battle_end(self) -> bool:
        if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
            self.state = BattleState.CATCHING
            self.message = f"{self.opponent_pokemon['name']} fainted! Throw a pokeball?"
            Logger.info("Battle won! Ready to catch opponent pokemon!")
            return True

        if self.player_pokemon and self.player_pokemon['hp'] <= 0:
            # Check if there are other healthy Pokemon available
            current_pokemon_index = 0
            available_pokemon = [p for i, p in enumerate(self.game_manager.bag.monsters)
                               if i != current_pokemon_index and p.get("hp", 0) > 0]

            if available_pokemon:
                # Force player to switch to another Pokemon
                self.state = BattleState.CHOOSE_SWITCH
                self.switch_panel = BattleSwitchPanel(
                    self.game_manager.bag.monsters,
                    current_pokemon_index,
                    GameSettings.SCREEN_WIDTH // 2 - 250,
                    GameSettings.SCREEN_HEIGHT // 2 - 250,
                    width=500,
                    height=500
                )
                self.message = f"{self.player_pokemon['name']} fainted! Choose another Pokemon!"
                Logger.info(f"{self.player_pokemon['name']} fainted, forcing switch to another Pokemon")
                return True  # Return True to pause the battle flow
            else:
                # No healthy Pokemon left, player loses
                self.state = BattleState.BATTLE_END
                self.message = f"All your Pokemon fainted! You lost!"
                Logger.info("Battle lost! No healthy Pokemon left!")
                return True

        return False
    
    def _execute_switch(self, new_pokemon_index: int) -> None:
        """Switch to a different Pokemon"""
        if not self.game_manager.bag or new_pokemon_index >= len(self.game_manager.bag.monsters):
            return

        # Get the new Pokemon
        new_pokemon = self.game_manager.bag.monsters[new_pokemon_index]

        # Make sure new Pokemon has required stats
        if "type" not in new_pokemon or "moves" not in new_pokemon:
            species_data = POKEMON_SPECIES.get(
                new_pokemon["name"],
                {"type": "None", "moves": ["QuickSlash"]}
            )
            new_pokemon["type"] = species_data["type"]
            new_pokemon["moves"] = species_data["moves"].copy()

        if "attack" not in new_pokemon:
            player_level = new_pokemon.get("level", 1)
            new_pokemon["attack"] = int(10 + player_level * 0.5)

        if "defense" not in new_pokemon:
            player_level = new_pokemon.get("level", 1)
            new_pokemon["defense"] = int(10 + player_level * 0.5)

        # Check if this was a forced switch (previous Pokemon fainted)
        old_pokemon_fainted = self.player_pokemon and self.player_pokemon.get("hp", 0) <= 0

        # Swap Pokemon in the bag (move selected Pokemon to index 0)
        self.game_manager.bag.monsters[0], self.game_manager.bag.monsters[new_pokemon_index] = \
            self.game_manager.bag.monsters[new_pokemon_index], self.game_manager.bag.monsters[0]

        # Update player Pokemon reference
        self.player_pokemon = self.game_manager.bag.monsters[0]

        # Create animated sprite for new player Pokemon
        player_sprite_path = self.player_pokemon.get("sprite_path", "")
        if "sprite" in player_sprite_path and not "menu_sprites" in player_sprite_path:
            self.player_sprite = AnimatedBattleSprite(
                base_path=player_sprite_path.replace(".png", ""),
                size=(250, 250),
                frames=4,
                loop_speed=0.8
            )
        else:
            self.player_sprite = None

        # Update player panel with new Pokemon
        if self.player_panel:
            self.player_panel.update_pokemon(self.player_pokemon)

        # Show switch message
        self.message = f"Go, {self.player_pokemon['name']}!"
        Logger.info(f"Switched to {self.player_pokemon['name']}")

        # Close switch panel and transition to show damage state
        self.switch_panel = None
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE

        # Enemy gets a free turn after switch (both voluntary and forced)
        if old_pokemon_fainted:
            # Forced switch - enemy attacks next
            self.current_turn = "enemy"
        else:
            # Voluntary switch - enemy also gets free turn
            self.current_turn = "enemy"

    def _execute_item_attack(self, item: dict) -> None:
        if not self.player_pokemon:
            return

        item_name = item['name'].lower()

        # Health Potion: Heal your pokemon
        if 'health' in item_name or 'heal' in item_name:
            heal_amount = int(self.player_pokemon['max_hp'] * 0.5)  # Heal 50% of max HP
            old_hp = self.player_pokemon['hp']
            self.player_pokemon['hp'] = min(self.player_pokemon['max_hp'], self.player_pokemon['hp'] + heal_amount)
            actual_heal = self.player_pokemon['hp'] - old_hp

            self.message = f"{self.player_pokemon['name']} used Health Potion! Restored {actual_heal} HP!"
            Logger.info(f"Player used Health Potion: healed {actual_heal} HP. Player HP: {self.player_pokemon['hp']}/{self.player_pokemon['max_hp']}")

        # Strength Potion: Increase attack power
        elif 'strength' in item_name or 'attack' in item_name:
            self.attack_boost = 1.5  # 50% attack boost
            self.message = f"{self.player_pokemon['name']} used Strength Potion! Attack power increased!"
            Logger.info(f"Player used Strength Potion: attack boost now {self.attack_boost}x")

        # Defense Potion (defense-potion.png): Reduce opponent's attack damage
        elif 'defense' in item_name or 'defence' in item_name:
            self.defense_boost = 1.5  
            self.message = f"{self.player_pokemon['name']} used Defense Potion! Defense increased!"
            Logger.info(f"Player used Defense Potion: defense boost now {self.defense_boost}x (reduces incoming damage)")

        else:
            # Fallback for unknown items
            self.message = f"Used {item['name']}!"
            Logger.info(f"Player used unknown item: {item['name']}")

        # Reduce item count
        item['count'] = max(0, item['count'] - 1)

        # Remove item from bag if count reaches 0
        if item['count'] == 0 and self.game_manager.bag:
            self.game_manager.bag.items.remove(item)

        # Transition to show damage state first
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE
    
    def _execute_pokeball_catch(self, item: dict) -> None:
        """Execute pokeball catch animation and logic"""
        if not self.opponent_pokemon:
            return
        
        # Start pokeball animation
        self.pokeball_x = GameSettings.SCREEN_WIDTH // 2
        self.pokeball_y = GameSettings.SCREEN_HEIGHT - 100
        
        # Reduce pokeball count
        item['count'] = max(0, item['count'] - 1)
        
        self.state = BattleState.CATCH_ANIMATION
        self._state_timer = 0.0
        self.pokeball_rotation = 0.0
        self.pokeball_scale = 1.0
        Logger.info(f"pokeball catch animation started for {self.opponent_pokemon['name']}")
        
    def _catch_opponent_pokemon(self) -> None:
        """Complete the catch - add opponent pokemon to player's bag as a new entry"""
        if not self.opponent_pokemon or not self.game_manager.bag:
            self.state = BattleState.BATTLE_END
            self.message = "Catch failed!"
            Logger.error("Catch failed: missing opponent_pokemon or bag")
            return

        # Add caught pokemon as a new entry with all necessary fields
        caught_pokemon = {
            "name": self.opponent_pokemon['name'],
            "hp": self.opponent_pokemon['max_hp'],  # Full HP
            "max_hp": self.opponent_pokemon['max_hp'],
            "level": self.opponent_pokemon['level'],
            "sprite_path": self.opponent_pokemon['sprite_path'],  # Battle sprite
            "type": self.opponent_pokemon.get('type', 'None'),
            "moves": self.opponent_pokemon.get('moves', []).copy(),  # Copy the moves list
            "attack": self.opponent_pokemon.get('attack', 10),
            "defense": self.opponent_pokemon.get('defense', 10),
            "status": None,  # Reset status to healthy
            "status_turns": 0
        }
        self.game_manager.bag.monsters.append(caught_pokemon)
        Logger.info(f"Caught {self.opponent_pokemon['name']}! Added to bag")

        Logger.info(f"Current monsters in bag: {len(self.game_manager.bag._monsters_data)}")
        for monster in self.game_manager.bag._monsters_data:
            Logger.info(f"  - {monster['name']} (Level {monster.get('level', 1)})")

        # self.game_manager.save("saves/game0.json") # Moved to CATCH_SUCCESS
        # self.game_manager.load("saves/game0.json") # Moved to CATCH_SUCCESS
        # self.state = BattleState.BATTLE_END # Moved to CATCH_SUCCESS
        # self.message = f"Successfully caught {self.opponent_pokemon['name']}!" # Moved to CATCH_SUCCESS
        
        
    def _next_state(self) -> None:
        if self.state == BattleState.INTRO:
            self.state = BattleState.CHALLENGER
            self.message = f"{self.opponent_name} challenged you to a battle!"
        elif self.state == BattleState.CHALLENGER:
            self.state = BattleState.SEND_OPPONENT
            self.message = f"{self.opponent_name} sent out {self.opponent_pokemon['name']}!"
        elif self.state == BattleState.SEND_OPPONENT:
            self.state = BattleState.SEND_PLAYER
            self.message = f"Go, {self.player_pokemon['name']}!"
        elif self.state == BattleState.SEND_PLAYER:
            self.state = BattleState.PLAYER_TURN
            self.current_turn = "player"
            self.message = "What will " + self.player_pokemon['name'] + " do?"
        self._state_timer = 0.0

    @override
    def update(self, dt: float) -> None:
        self._state_timer += dt

        # Update animated sprites
        if self.opponent_sprite:
            self.opponent_sprite.update(dt)
        if self.player_sprite:
            self.player_sprite.update(dt)

        # Update attack animation
        if self.attack_animation:
            self.attack_animation.update(dt)
            if self.attack_animation.is_finished():
                self.attack_animation = None

        if input_manager.key_pressed(pg.K_SPACE):
            if self.state == BattleState.CHALLENGER:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == BattleState.SEND_OPPONENT:
                # Only allow continuing after animation is complete
                if self._pokemon_scale >= 1.0:
                    self._next_state()
                    self._pokemon_scale = 0.0
            elif self.state == BattleState.SEND_PLAYER:
                # Only allow continuing after animation is complete
                if self._pokemon_scale >= 1.0:
                    self._next_state()
                    self._pokemon_scale = 0.0
            elif self.state == BattleState.SHOW_DAMAGE:
                # Clear effectiveness message immediately when leaving SHOW_DAMAGE state
                # Also remove it from self.message if it was appended there
                if self.effectiveness_message and self.effectiveness_message in self.message:
                    self.message = self.message.replace(self.effectiveness_message, "").strip()
                self.effectiveness_message = ""

                # Clear damage formula display
                self.show_damage_formula = False

                # After showing damage, transition to next state
                # Switch sprites back to idle animation
                if self.opponent_sprite:
                    self.opponent_sprite.switch_animation("idle")
                if self.player_sprite:
                    self.player_sprite.switch_animation("idle")

                if self._check_battle_end():
                    # Battle ended - show catch panel if opponent fainted
                    if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
                        self._show_catch_panel()
                else:
                    # Apply end-of-turn status damage
                    status_messages = []

                    # Apply status damage to both Pokemon
                    if self.current_turn == "player":
                        # Player just attacked, apply status damage to player
                        player_status_dmg = self._apply_status_damage(self.player_pokemon)
                        if player_status_dmg > 0:
                            status_name = STATUS_EFFECTS[self.player_pokemon["status"]]["name"]
                            status_messages.append(f"{self.player_pokemon['name']} took {player_status_dmg} damage from {status_name}!")
                            Logger.info(f"Player took {player_status_dmg} status damage")

                        # Update status turns (for sleep)
                        self._update_status_turns(self.player_pokemon)
                    else:
                        # Enemy just attacked, apply status damage to enemy
                        enemy_status_dmg = self._apply_status_damage(self.opponent_pokemon)
                        if enemy_status_dmg > 0:
                            status_name = STATUS_EFFECTS[self.opponent_pokemon["status"]]["name"]
                            status_messages.append(f"{self.opponent_pokemon['name']} took {enemy_status_dmg} damage from {status_name}!")
                            Logger.info(f"Enemy took {enemy_status_dmg} status damage")

                        # Update status turns (for sleep)
                        self._update_status_turns(self.opponent_pokemon)

                    # Append status messages to main message
                    if status_messages:
                        self.message += "\n" + " ".join(status_messages)

                    # Check if status damage caused a KO
                    if self._check_battle_end():
                        if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
                            self._show_catch_panel()
                        return

                    # Transition to next appropriate state
                    self._state_timer = 0.0
                    if self.current_turn == "player":
                        self.state = BattleState.ENEMY_TURN
                        self.current_turn = "enemy"
                    else:
                        self.state = BattleState.PLAYER_TURN
                        self.current_turn = "player"
                        self.message = "What will " + self.player_pokemon['name'] + " do?"
                        self.turn_message = ""
            elif self.state == BattleState.CATCHING:
                # Player can press SPACE to skip or will select item
                pass
            elif self.state == BattleState.BATTLE_END:
                # Document 2: 加入自動儲存功能
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("game")
        
        # Handle Run Away action - Document 2: 加入自動儲存
        if self.state == BattleState.PLAYER_TURN and self._state_timer > 2.0 and self.message == "Escaped from battle!":
            self.game_manager.save("saves/game0.json")
            scene_manager.change_scene("game")
        
        if self._pokemon_scale < 1.0:
            self._pokemon_scale += dt * 2.0
        
        # Document 2的版本：更精確的面板初始化時機
        if self.opponent_panel is None and self.opponent_pokemon and self.state == BattleState.SEND_OPPONENT:
            self.opponent_panel = PokemonStatsPanel(
                self.opponent_pokemon,
                GameSettings.SCREEN_WIDTH - 180,
                20
            )
        
        if self.player_panel is None and self.player_pokemon and self.state == BattleState.SEND_PLAYER:
            self.player_panel = PokemonStatsPanel(
                self.player_pokemon,
                20,
                GameSettings.SCREEN_HEIGHT - 250
            )
        
        if self.state == BattleState.PLAYER_TURN:
            self.fight_btn.update(dt)
            self.item_btn.update(dt)
            self.switch_btn.update(dt)
            self.run_btn.update(dt)
        
        if self.state == BattleState.CHOOSE_MOVE:
            for btn in self.move_buttons:
                btn.update(dt)

        if self.state == BattleState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.update(dt)
                selected = self.item_panel.get_selected_item()
                if selected:
                    self._execute_item_attack(selected)
                
                # Close item panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BattleState.PLAYER_TURN
                    self.item_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"

        # Switch panel handling
        if self.state == BattleState.CHOOSE_SWITCH:
            if self.switch_panel:
                self.switch_panel.update(dt)
                selected_index = self.switch_panel.get_selected_pokemon_index()
                if selected_index is not None:
                    self._execute_switch(selected_index)

                # Close switch panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BattleState.PLAYER_TURN
                    self.switch_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"

        # Catching panel handling
        if self.state == BattleState.CATCHING:
            if self.catch_panel:
                self.catch_panel.update(dt)
                selected = self.catch_panel.get_selected_item()
                if selected:
                    self._execute_pokeball_catch(selected)
                
                # Close catch panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BattleState.BATTLE_END
                    self.catch_panel = None
                    self.message = "Battle ended!"
        
        # pokeball catch animation
        if self.state == BattleState.CATCH_ANIMATION:
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
                self.state = BattleState.CATCH_FLASHING
                self.pokeball_x = opponent_pokemon_x
                self.pokeball_y = opponent_pokemon_y
                self.flash_count = 0
                self.flash_timer = 0.0
                self.pokemon_visible = True
                Logger.info(f"Pokéball hit {self.opponent_pokemon['name']}!")

        # Pokemon flashing animation (Pokemon flashes 3 times before being caught)
        if self.state == BattleState.CATCH_FLASHING:
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
                    self.state = BattleState.CATCH_FALLING
                    self._state_timer = 0.0
                    self.pokemon_visible = False  # 保持不可见
                    Logger.info("Pokemon disappeared, ball falling!")

        # Pokeball falling animation (Ball drops to ground)
        if self.state == BattleState.CATCH_FALLING:
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
                self.state = BattleState.CATCH_SHAKE
                self.shake_count = 0
                self.shake_timer = 0.0
        
        # Pokeball shaking animation
        if self.state == BattleState.CATCH_SHAKE:
            shake_interval = 1.0
            self.shake_timer += dt
            
            # Shake logic: 3 shakes
            if self.shake_timer > shake_interval:
                self.shake_timer = 0
                self.shake_count += 1
                if self.shake_count >= 3:
                    self.state = BattleState.CATCH_SUCCESS
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
                
        if self.state == BattleState.CATCH_SUCCESS:
            if self._state_timer > 1.0: # Wait 1 second after catch
                self.game_manager.save("saves/game0.json")
                self.game_manager.load("saves/game0.json")
                self.state = BattleState.BATTLE_END
                self.message = f"Successfully caught {self.opponent_pokemon['name']}, Added to bag!"
                
        
        # Enemy turn handling
        if self.state == BattleState.ENEMY_TURN:
            if self._state_timer > 1.5 and self.enemy_selected_move is None:
                # First call to ENEMY_TURN - select and show move
                self._execute_enemy_attack()
            elif self._state_timer > 3.0 and self.enemy_selected_move is not None:
                # After delay, apply damage
                self._apply_enemy_damage()
        
        # Update panels for HP changes
        self._state_timer += dt
        
        if input_manager.key_pressed(pg.K_SPACE):
            if self.state == BattleState.CHALLENGER:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == BattleState.SEND_OPPONENT:
                # Only allow continuing after animation is complete
                if self._pokemon_scale >= 1.0:
                    self._next_state()
                    self._pokemon_scale = 0.0
            elif self.state == BattleState.SEND_PLAYER:
                # Only allow continuing after animation is complete
                if self._pokemon_scale >= 1.0:
                    self._next_state()
                    self._pokemon_scale = 0.0
            elif self.state == BattleState.SHOW_DAMAGE:
                # Clear effectiveness message immediately when leaving SHOW_DAMAGE state
                # Also remove it from self.message if it was appended there
                if self.effectiveness_message and self.effectiveness_message in self.message:
                    self.message = self.message.replace(self.effectiveness_message, "").strip()
                self.effectiveness_message = ""

                # Clear damage formula display
                self.show_damage_formula = False

                # After showing damage, transition to next state
                # Switch sprites back to idle animation
                if self.opponent_sprite:
                    self.opponent_sprite.switch_animation("idle")
                if self.player_sprite:
                    self.player_sprite.switch_animation("idle")

                if self._check_battle_end():
                    # Battle ended - show catch panel if opponent fainted
                    if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
                        self._show_catch_panel()
                else:
                    # Apply end-of-turn status damage
                    status_messages = []

                    # Apply status damage to both Pokemon
                    if self.current_turn == "player":
                        # Player just attacked, apply status damage to player
                        player_status_dmg = self._apply_status_damage(self.player_pokemon)
                        if player_status_dmg > 0:
                            status_name = STATUS_EFFECTS[self.player_pokemon["status"]]["name"]
                            status_messages.append(f"{self.player_pokemon['name']} took {player_status_dmg} damage from {status_name}!")
                            Logger.info(f"Player took {player_status_dmg} status damage")

                        # Update status turns (for sleep)
                        self._update_status_turns(self.player_pokemon)
                    else:
                        # Enemy just attacked, apply status damage to enemy
                        enemy_status_dmg = self._apply_status_damage(self.opponent_pokemon)
                        if enemy_status_dmg > 0:
                            status_name = STATUS_EFFECTS[self.opponent_pokemon["status"]]["name"]
                            status_messages.append(f"{self.opponent_pokemon['name']} took {enemy_status_dmg} damage from {status_name}!")
                            Logger.info(f"Enemy took {enemy_status_dmg} status damage")

                        # Update status turns (for sleep)
                        self._update_status_turns(self.opponent_pokemon)

                    # Append status messages to main message
                    if status_messages:
                        self.message += "\n" + " ".join(status_messages)

                    # Check if status damage caused a KO
                    if self._check_battle_end():
                        if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
                            self._show_catch_panel()
                        return

                    # Transition to next appropriate state
                    self._state_timer = 0.0
                    if self.current_turn == "player":
                        self.state = BattleState.ENEMY_TURN
                        self.current_turn = "enemy"
                    else:
                        self.state = BattleState.PLAYER_TURN
                        self.current_turn = "player"
                        self.message = "What will " + self.player_pokemon['name'] + " do?"
                        self.turn_message = ""
            elif self.state == BattleState.CATCHING:
                # Player can press SPACE to skip or will select item
                pass
            elif self.state == BattleState.BATTLE_END:
                # Document 2: 加入自動儲存功能
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("game")
        
        # Handle Run Away action - Document 2: 加入自動儲存
        if self.state == BattleState.PLAYER_TURN and self._state_timer > 2.0 and self.message == "Escaped from battle!":
            self.game_manager.save("saves/game0.json")
            scene_manager.change_scene("game")
        
        if self._pokemon_scale < 1.0:
            self._pokemon_scale += dt * 2.0
        
        # Document 2的版本：更精確的面板初始化時機
        if self.opponent_panel is None and self.opponent_pokemon and self.state == BattleState.SEND_OPPONENT:
            self.opponent_panel = PokemonStatsPanel(
                self.opponent_pokemon,
                GameSettings.SCREEN_WIDTH - 180,
                20
            )
        
        if self.player_panel is None and self.player_pokemon and self.state == BattleState.SEND_PLAYER:
            self.player_panel = PokemonStatsPanel(
                self.player_pokemon,
                20,
                GameSettings.SCREEN_HEIGHT - 250
            )
        
        if self.state == BattleState.PLAYER_TURN:
            self.fight_btn.update(dt)
            self.item_btn.update(dt)
            self.switch_btn.update(dt)
            self.run_btn.update(dt)
        
        if self.state == BattleState.CHOOSE_MOVE:
            for btn in self.move_buttons:
                btn.update(dt)

        if self.state == BattleState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.update(dt)
                selected = self.item_panel.get_selected_item()
                if selected:
                    self._execute_item_attack(selected)
                
                # Close item panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BattleState.PLAYER_TURN
                    self.item_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"

        # Switch panel handling
        if self.state == BattleState.CHOOSE_SWITCH:
            if self.switch_panel:
                self.switch_panel.update(dt)
                selected_index = self.switch_panel.get_selected_pokemon_index()
                if selected_index is not None:
                    self._execute_switch(selected_index)

                # Close switch panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BattleState.PLAYER_TURN
                    self.switch_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"

        # Catching panel handling
        if self.state == BattleState.CATCHING:
            if self.catch_panel:
                self.catch_panel.update(dt)
                selected = self.catch_panel.get_selected_item()
                if selected:
                    self._execute_pokeball_catch(selected)
                
                # Close catch panel with ESC key
                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BattleState.BATTLE_END
                    self.catch_panel = None
                    self.message = "Battle ended!"
        
        # pokeball catch animation
        if self.state == BattleState.CATCH_ANIMATION:
            # pokeball flies from player pokemon to opponent pokemon
            # 出发点：玩家宝可梦在画面中的位置（Player Pokemon在左下方）
            player_pokemon_x = 200 + 125  # Player pokemon center X
            player_pokemon_y = GameSettings.SCREEN_HEIGHT - 250 - 100  # Player pokemon center Y

            # 落点：敌方宝可梦在画面中的位置（Opponent Pokemon在右上方，提高位置）
            opponent_pokemon_x = GameSettings.SCREEN_WIDTH - 200 - 100  # Opponent pokemon center X
            opponent_pokemon_y = 80 + 100  # 提高落点位置（原本是 80 + 100）

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
                self.state = BattleState.CATCH_FLASHING
                self.pokeball_x = opponent_pokemon_x
                self.pokeball_y = opponent_pokemon_y
                self.flash_count = 0
                self.flash_timer = 0.0
                self.pokemon_visible = True
                Logger.info(f"Pokéball hit {self.opponent_pokemon['name']}!")

        # Pokemon flashing animation (Pokemon flashes 3 times before being caught)
        if self.state == BattleState.CATCH_FLASHING:
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
                    self.state = BattleState.CATCH_FALLING
                    self._state_timer = 0.0
                    self.pokemon_visible = False  # 保持不可见
                    Logger.info("Pokemon disappeared, ball falling!")

        # Pokeball falling animation (Ball drops to ground)
        if self.state == BattleState.CATCH_FALLING:
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
                self.state = BattleState.CATCH_SHAKE
                self.shake_count = 0
                self.shake_timer = 0.0
        
        # Pokeball shaking animation
        if self.state == BattleState.CATCH_SHAKE:
            shake_interval = 1.0
            self.shake_timer += dt
            
            # Shake logic: 3 shakes
            if self.shake_timer > shake_interval:
                self.shake_timer = 0
                self.shake_count += 1
                if self.shake_count >= 3:
                    self.state = BattleState.CATCH_SUCCESS
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
                
        if self.state == BattleState.CATCH_SUCCESS:
            if self._state_timer > 1.0: # Wait 1 second after catch
                self.game_manager.save("saves/game0.json")
                self.game_manager.load("saves/game0.json")
                self.state = BattleState.BATTLE_END
                self.message = f"Successfully caught {self.opponent_pokemon['name']}!"
                
        
        # Enemy turn handling
        if self.state == BattleState.ENEMY_TURN:
            if self._state_timer > 1.5 and self.enemy_selected_move is None:
                # First call to ENEMY_TURN - select and show move
                self._execute_enemy_attack()
            elif self._state_timer > 3.0 and self.enemy_selected_move is not None:
                # After delay, apply damage
                self._apply_enemy_damage()
        
        # Update panels for HP changes and animations
        if self.opponent_panel:
            self.opponent_panel.update(dt)
            self.opponent_panel.update_pokemon(self.opponent_pokemon)
        if self.player_panel:
            self.player_panel.update(dt)
            self.player_panel.update_pokemon(self.player_pokemon)

    def _draw_type_matchup_display(self, screen: pg.Surface) -> None:
        """Draw a beautiful type matchup display at the top of the screen"""
        if not self.player_pokemon or not self.opponent_pokemon:
            return

        from src.utils.pokemon_data import TYPE_ADVANTAGE

        player_type = self.player_pokemon.get("type", "None")
        opponent_type = self.opponent_pokemon.get("type", "None")

        # Type color mapping for visual appeal
        type_colors = {
            "Fire": (255, 100, 50),
            "Water": (50, 150, 255),
            "Ice": (150, 230, 255),
            "Wind": (200, 255, 200),
            "Light": (255, 255, 150),
            "Slash": (200, 200, 200),
            "None": (150, 150, 150),
        }

        # Draw background panel
        panel_width = 500
        panel_height = 70
        panel_x = (GameSettings.SCREEN_WIDTH - panel_width) // 2
        panel_y = 10

        # Semi-transparent dark background
        panel_surface = pg.Surface((panel_width, panel_height), pg.SRCALPHA)
        pg.draw.rect(panel_surface, (0, 0, 0, 180), (0, 0, panel_width, panel_height), border_radius=15)
        pg.draw.rect(panel_surface, (255, 255, 255, 100), (0, 0, panel_width, panel_height), 3, border_radius=15)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Draw player type badge (left side)
        player_color = type_colors.get(player_type, (150, 150, 150))
        player_badge_x = panel_x + 30
        player_badge_y = panel_y + 20
        player_badge_w = 120
        player_badge_h = 35

        pg.draw.rect(screen, player_color, (player_badge_x, player_badge_y, player_badge_w, player_badge_h), border_radius=10)
        pg.draw.rect(screen, (255, 255, 255), (player_badge_x, player_badge_y, player_badge_w, player_badge_h), 2, border_radius=10)

        player_type_text = self._font.render(player_type, True, (255, 255, 255))
        text_rect = player_type_text.get_rect(center=(player_badge_x + player_badge_w // 2, player_badge_y + player_badge_h // 2))
        screen.blit(player_type_text, text_rect)

        # Draw opponent type badge (right side)
        opponent_color = type_colors.get(opponent_type, (150, 150, 150))
        opponent_badge_x = panel_x + panel_width - 150
        opponent_badge_y = panel_y + 20
        opponent_badge_w = 120
        opponent_badge_h = 35

        pg.draw.rect(screen, opponent_color, (opponent_badge_x, opponent_badge_y, opponent_badge_w, opponent_badge_h), border_radius=10)
        pg.draw.rect(screen, (255, 255, 255), (opponent_badge_x, opponent_badge_y, opponent_badge_w, opponent_badge_h), 2, border_radius=10)

        opponent_type_text = self._font.render(opponent_type, True, (255, 255, 255))
        text_rect = opponent_type_text.get_rect(center=(opponent_badge_x + opponent_badge_w // 2, opponent_badge_y + opponent_badge_h // 2))
        screen.blit(opponent_type_text, text_rect)

        # Draw matchup indicator (center)
        center_x = panel_x + panel_width // 2
        center_y = panel_y + panel_height // 2

        # Determine matchup
        player_advantage = TYPE_ADVANTAGE.get(player_type) == opponent_type
        opponent_advantage = TYPE_ADVANTAGE.get(opponent_type) == player_type

        if player_type == "None" or opponent_type == "None":
            # Neutral - no type advantages
            symbol = "="
            symbol_color = (200, 200, 200)
            glow_color = (100, 100, 100)
        elif player_advantage:
            # Player has advantage
            symbol = ">"
            symbol_color = (100, 255, 100)
            glow_color = (50, 200, 50)
        elif opponent_advantage:
            # Opponent has advantage
            symbol = "<"
            symbol_color = (255, 100, 100)
            glow_color = (200, 50, 50)
        else:
            # Neutral matchup
            symbol = "="
            symbol_color = (255, 255, 150)
            glow_color = (200, 200, 100)

        # Draw glowing symbol
        symbol_font = pg.font.Font('assets/fonts/Minecraft.ttf', 40)

        # Glow effect
        for offset in range(3, 0, -1):
            glow_alpha = 80 - (offset * 20)
            glow_surface = pg.Surface((60, 60), pg.SRCALPHA)
            glow_text = symbol_font.render(symbol, True, (*glow_color, glow_alpha))
            glow_rect = glow_text.get_rect(center=(30, 30))
            glow_surface.blit(glow_text, glow_rect)
            screen.blit(glow_surface, (center_x - 30 - offset, center_y - 30 - offset))

        # Main symbol
        symbol_text = symbol_font.render(symbol, True, symbol_color)
        symbol_rect = symbol_text.get_rect(center=(center_x, center_y))
        screen.blit(symbol_text, symbol_rect)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)

        # Draw type matchup display (only when both Pokemon are visible)
        if self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.CHOOSE_MOVE, BattleState.CHOOSE_ITEM, BattleState.SHOW_DAMAGE, BattleState.CHOOSE_SWITCH):
            self._draw_type_matchup_display(screen)

        # Draw panels
        if self.opponent_panel and self.state in (BattleState.SEND_OPPONENT, BattleState.SEND_PLAYER, BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.BATTLE_END, BattleState.CATCHING, BattleState.CATCH_ANIMATION, BattleState.CATCH_FLASHING, BattleState.SHOW_DAMAGE, BattleState.CHOOSE_MOVE, BattleState.CHOOSE_ITEM, BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS):
            self.opponent_panel.draw(screen)

        if self.player_panel and self.state in (BattleState.SEND_PLAYER, BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.BATTLE_END, BattleState.CATCHING, BattleState.CATCH_ANIMATION, BattleState.CATCH_FLASHING, BattleState.SHOW_DAMAGE, BattleState.CHOOSE_MOVE, BattleState.CHOOSE_ITEM, BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS):
            self.player_panel.draw(screen)

        # Draw attack animation (before Pokemon so it appears behind them)
        if self.attack_animation:
            self.attack_animation.draw(screen)
        
        
        # Draw Opponent Pokemon
        if (self.state == BattleState.SEND_OPPONENT or self.state == BattleState.SEND_PLAYER or self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.BATTLE_END, BattleState.CATCHING, BattleState.CATCH_ANIMATION, BattleState.CATCH_FLASHING, BattleState.SHOW_DAMAGE)) and self.opponent_pokemon:
            # Determine drawing logic
            should_draw = True
            if self.state == BattleState.CATCH_FLASHING:
                should_draw = self.pokemon_visible
            elif self.state in (BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS):
                should_draw = False

            if should_draw and self.opponent_sprite:
                # Use animated sprite
                if self.state == BattleState.SEND_OPPONENT:
                    scale = min(self._pokemon_scale, 1.0)
                else:
                    scale = 1.0

                # Get current frame and scale it
                frame = self.opponent_sprite.get_current_frame()
                size = int(200 * scale)
                scaled_frame = pg.transform.smoothscale(frame, (size, size))

                x = GameSettings.SCREEN_WIDTH - size - 150
                y = 80
                screen.blit(scaled_frame, (x, y))
        
        # Draw Player Pokemon
        if (self.state == BattleState.SEND_PLAYER or self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.BATTLE_END, BattleState.CATCHING, BattleState.CATCH_ANIMATION, BattleState.SHOW_DAMAGE, BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS)) and self.player_pokemon:
            if self.player_sprite:
                # Use animated sprite
                if self.state == BattleState.SEND_PLAYER:
                    scale = min(self._pokemon_scale, 1.0)
                else:
                    scale = 1.0

                # Get current frame and scale it
                frame = self.player_sprite.get_current_frame()
                size = int(250 * scale)
                scaled_frame = pg.transform.smoothscale(frame, (size, size))

                x = 200
                y = GameSettings.SCREEN_HEIGHT - size - 200
                screen.blit(scaled_frame, (x, y))
            else:
                # Fallback to static sprite for old pokemon
                sprite = Sprite(self.player_pokemon["sprite_path"], (250, 250))
                if self.state == BattleState.SEND_PLAYER:
                    scale = min(self._pokemon_scale, 1.0)
                else:
                    scale = 1.0
                size = int(250 * scale)
                scaled_sprite = pg.transform.scale(sprite.image, (size, size))
                x = 200
                y = GameSettings.SCREEN_HEIGHT - size - 200
                screen.blit(scaled_sprite, (x, y))
        
        # Draw Message Box (skip in CHOOSE_MOVE state to avoid blocking move buttons)
        box_h, box_w = 120, GameSettings.SCREEN_WIDTH - 40
        box_x, box_y = 20, GameSettings.SCREEN_HEIGHT - box_h - 20

        if self.state != BattleState.CHOOSE_MOVE:
            pg.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_w, box_h))
            pg.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 2)

        # Display main message (skip during catch animation to avoid overlap)
        if self.state not in (BattleState.CATCH_ANIMATION, BattleState.CATCH_FLASHING, BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS):
            # Split message and effectiveness message for better formatting
            if self.effectiveness_message:
                # Display main damage message (remove effectiveness from message if it's there)
                if self.effectiveness_message in self.message:
                    main_msg = self.message.replace(self.effectiveness_message, "").strip()
                else:
                    # Message doesn't include effectiveness, extract just damage part
                    main_msg = self.message
                msg_text = self._message_font.render(main_msg, True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))

                # Display effectiveness message with special color
                if "super effective" in self.effectiveness_message:
                    eff_color = (100, 255, 100)  # Green for super effective
                elif "not very effective" in self.effectiveness_message:
                    eff_color = (255, 100, 100)  # Red for not very effective
                elif "Normal damage" in self.effectiveness_message:
                    eff_color = (200, 200, 150)  # Light yellow/gray for neutral
                elif "Typeless" in self.effectiveness_message:
                    eff_color = (180, 180, 180)  # Gray for typeless
                else:
                    eff_color = (255, 255, 255)  # White for other messages

                eff_text = self._message_font.render(self.effectiveness_message, True, eff_color)
                screen.blit(eff_text, (box_x + 10, box_y + 30))
            else:
                msg_text = self._message_font.render(self.message, True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))

        # Display damage calculation formula in top right corner
        if self.show_damage_formula and self.damage_formula and self.state == BattleState.SHOW_DAMAGE:
            # Create a semi-transparent background box for the formula
            formula_box_width = 500
            formula_box_height = 80
            formula_box_x = GameSettings.SCREEN_WIDTH - formula_box_width - 20
            formula_box_y = 500
            # Draw background with border
            pg.draw.rect(screen, (30, 30, 30), (formula_box_x, formula_box_y, formula_box_width, formula_box_height), border_radius=8)
            pg.draw.rect(screen, (200, 150, 50), (formula_box_x, formula_box_y, formula_box_width, formula_box_height), 3, border_radius=8)

            # Title
            title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 18)
            title_text = title_font.render("Damage Calculation", True, (255, 200, 100))
            screen.blit(title_text, (formula_box_x + 10, formula_box_y + 8))

            # Formula
            formula_font = pg.font.Font('assets/fonts/Minecraft.ttf', 15)
            formula_text = formula_font.render(self.damage_formula, True, (220, 220, 220))
            screen.blit(formula_text, (formula_box_x + 10, formula_box_y + 35))

        # Display turn message (damage dealt)
        if self.turn_message and self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.PLAYER_TURN):
            turn_text = self._message_font.render(self.turn_message, True, (255, 200, 100))
            screen.blit(turn_text, (box_x + 10, box_y + 35))
        
        if self.state not in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.CHOOSE_MOVE, BattleState.BATTLE_END, BattleState.SHOW_DAMAGE, BattleState.CATCH_ANIMATION, BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS):
            if self.state == BattleState.CHALLENGER:
                hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
            elif self.state in (BattleState.SEND_OPPONENT, BattleState.SEND_PLAYER):
                # Only show hint after animation is complete
                if self._pokemon_scale >= 1.0:
                    hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                    screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
        
        if self.state == BattleState.PLAYER_TURN:
            # Updated button layout with larger buttons and spacing
            btn_w, btn_h = 120, 50  # Match the button size from __init__
            gap = 20  # Larger gap between buttons

            # Calculate total width and center the buttons
            total_width = btn_w * 4 + gap * 3
            btn_start_x = (GameSettings.SCREEN_WIDTH - total_width) // 2
            btn_y = box_y + 45

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
        
        if self.state == BattleState.CHOOSE_MOVE:
            # Draw move buttons (positions already set in _init_move_buttons)
            for btn in self.move_buttons:
                btn.draw(screen)

        if self.state == BattleState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.draw(screen)

            hint_text = self._message_font.render("Press ESC to cancel", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))

        if self.state == BattleState.CHOOSE_SWITCH:
            if self.switch_panel:
                self.switch_panel.draw(screen)

            hint_text = self._message_font.render("Press ESC to cancel", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))

        if self.state == BattleState.CATCHING:
            if self.catch_panel:
                self.catch_panel.draw(screen)
            
            hint_text = self._message_font.render("Press ESC to skip", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        # Draw Pokeball Animation
        if self.state in (BattleState.CATCH_ANIMATION, BattleState.CATCH_FLASHING, BattleState.CATCH_FALLING, BattleState.CATCH_SHAKE, BattleState.CATCH_SUCCESS):
            # Draw pokeball
            if self.pokeball_sprite:
                # Apply rotation and scale
                scaled_size = int(40 * self.pokeball_scale)
                scaled_img = pg.transform.scale(self.pokeball_sprite.image, (scaled_size, scaled_size))
                rotated_img = pg.transform.rotate(scaled_img, self.pokeball_rotation)

                # Center the rotated image
                rect = rotated_img.get_rect(center=(int(self.pokeball_x), int(self.pokeball_y)))
                screen.blit(rotated_img, rect)

            if self.state == BattleState.CATCH_ANIMATION:
                msg_text = self._message_font.render("Throwing Pokeball...", True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
            elif self.state == BattleState.CATCH_FLASHING:
                msg_text = self._message_font.render("Catching Pokemon...", True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
            elif self.state == BattleState.CATCH_SHAKE:
                shake_text = ["Wiggle...", "Wobble...", "Shake..."]
                idx = min(self.shake_count, 2)
                msg_text = self._message_font.render(shake_text[idx], True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
            elif self.state == BattleState.CATCH_SUCCESS:
                msg_text = self._message_font.render("Gotcha! " + self.opponent_pokemon['name'] + " was caught!", True, (255, 255, 255))
                screen.blit(msg_text, (box_x + 10, box_y + 10))
        
        if self.state == BattleState.SHOW_DAMAGE:
            # Show damage message, wait for SPACE
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == BattleState.BATTLE_END:
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
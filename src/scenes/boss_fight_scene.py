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
from src.utils.pokemon_data import POKEMON_SPECIES, calculate_damage, MOVES_DATABASE

from typing import override

from enum import Enum


class BossFightState(Enum):
    INTRO = 0
    BOSS_APPEAR = 1
    SEND_PLAYER = 2
    MAIN = 3
    PLAYER_TURN = 4
    CHOOSE_MOVE = 5
    BOSS_TURN = 6
    BATTLE_END = 7
    CHOOSE_ITEM = 8
    SHOW_DAMAGE = 9
    CHOOSE_SWITCH = 10


class BossFightScene(Scene):
    background: BackgroundSprite
    game_manager: GameManager
    state: BossFightState
    boss_pokemon: Monster | None
    player_pokemon: Monster | None
    boss_panel: PokemonStatsPanel | None
    player_panel: PokemonStatsPanel | None
    message: str
    fight_btn: BattleActionButton | None
    item_btn: BattleActionButton | None
    switch_btn: BattleActionButton | None
    run_btn: BattleActionButton | None
    move_buttons: list[BattleActionButton]
    current_turn: str
    player_selected_move: str | None
    boss_selected_move: str | None
    turn_message: str
    item_panel: BattleItemPanel | None
    player_selected_item: dict | None

    # Boss-specific visuals
    boss_sprite: Sprite | None
    player_sprite: AnimatedBattleSprite | None
    attack_animation: AttackAnimation | None

    # Boss effects
    screen_shake_intensity: float
    screen_shake_timer: float
    boss_glow_timer: float
    boss_glow_alpha: int

    # Potion buffs
    attack_boost: float
    defense_boost: float

    # Switch panel
    switch_panel: BattleSwitchPanel | None

    # Victory animation
    victory_timer: float
    victory_flash_count: int

    def __init__(self, game_manager: GameManager):
        super().__init__()
        # Use a special boss background
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.game_manager = game_manager
        self._font = pg.font.Font('assets/fonts/Minecraft.ttf', 28)
        self._message_font = pg.font.Font('assets/fonts/Minecraft.ttf', 18)

        self.state = BossFightState.INTRO
        self.boss_pokemon = None
        self.player_pokemon = None
        self.boss_panel = None
        self.player_panel = None
        self.message = ""
        self._state_timer = 0.0
        self._pokemon_scale = 0.0

        # Turn system initialization
        self.current_turn = "player"
        self.player_selected_move = None
        self.boss_selected_move = None
        self.turn_message = ""
        self.item_panel = None
        self.player_selected_item = None
        self.effectiveness_message = ""

        # Potion buffs
        self.attack_boost = 1.0
        self.defense_boost = 1.0

        # Boss visuals
        self.boss_sprite = None
        self.player_sprite = None
        self.attack_animation = None

        # Boss effects
        self.screen_shake_intensity = 0.0
        self.screen_shake_timer = 0.0
        self.boss_glow_timer = 0.0
        self.boss_glow_alpha = 0

        # Switch panel
        self.switch_panel = None

        # Victory animation
        self.victory_timer = 0.0
        self.victory_flash_count = 0

        # Main action buttons
        btn_w, btn_h = 80, 40

        self.fight_btn = BattleActionButton("Fight", 0, 0, btn_w, btn_h, self._on_fight_click)
        self.item_btn = BattleActionButton("Item", 0, 0, btn_w, btn_h, self._on_item_click)
        self.switch_btn = BattleActionButton("Switch", 0, 0, btn_w, btn_h, self._on_switch_click)
        self.run_btn = BattleActionButton("Run", 0, 0, btn_w, btn_h, self._on_run_click)

        # Move buttons
        self.move_buttons = []

    @override
    def enter(self) -> None:
        Logger.info("Boss Fight started against Mewtwo!")

        # Reload game manager
        loaded = GameManager.load("saves/game0.json")
        if loaded:
            self.game_manager = loaded
            Logger.info("BossFightScene: Game data reloaded from save file")

        # Reset all battle state variables
        self.state = BossFightState.INTRO
        self.boss_pokemon = None
        self.player_pokemon = None
        self.boss_panel = None
        self.player_panel = None
        self.message = ""
        self._state_timer = 0.0
        self._pokemon_scale = 0.0

        # Reset turn system
        self.current_turn = "player"
        self.player_selected_move = None
        self.boss_selected_move = None
        self.turn_message = ""
        self.item_panel = None
        self.player_selected_item = None
        self.effectiveness_message = ""

        # Reset potion buffs
        self.attack_boost = 1.0
        self.defense_boost = 1.0

        # Reset switch panel
        self.switch_panel = None

        # Reset boss effects
        self.screen_shake_intensity = 0.0
        self.screen_shake_timer = 0.0
        self.boss_glow_timer = 0.0
        self.boss_glow_alpha = 0

        # Reset victory animation
        self.victory_timer = 0.0
        self.victory_flash_count = 0

        # Initialize battle
        self._init_boss()
        self._next_state()

    @override
    def exit(self) -> None:
        pass

    def _init_boss(self) -> None:
        """Initialize Mewtwo boss with enhanced stats"""
        # Create Mewtwo boss
        level = 50  # High level boss
        max_hp = 200  # Very high HP
        attack = 40  # Strong attack
        defense = 30  # Strong defense

        # Get Mewtwo species data
        species_data = POKEMON_SPECIES.get("Mewtwo", {"type": "Psychic", "moves": ["Psystrike", "ShadowBall", "IceBeam", "Thunderbolt"]})

        self.boss_pokemon = {
            "name": "Mewtwo",
            "hp": max_hp,
            "max_hp": max_hp,
            "level": level,
            "attack": attack,
            "defense": defense,
            "sprite_path": "sprites/mewtwo.png",
            "type": species_data["type"],
            "moves": species_data["moves"].copy()
        }

        # Create boss sprite (larger and more imposing)
        self.boss_sprite = Sprite("sprites/mewtwo.png", (300, 300))

        Logger.info(f"Legendary Mewtwo (Lv.{level}) appears! This will be an epic battle!")

        # Initialize player pokemon
        if self.game_manager.bag and len(self.game_manager.bag._monsters_data) > 0:
            self.player_pokemon = self.game_manager.bag._monsters_data[0]

            # Ensure player pokemon has type and moves
            if "type" not in self.player_pokemon or "moves" not in self.player_pokemon:
                player_species_data = POKEMON_SPECIES.get(
                    self.player_pokemon["name"],
                    {"type": "None", "moves": ["QuickSlash"]}
                )
                self.player_pokemon["type"] = player_species_data["type"]
                self.player_pokemon["moves"] = player_species_data["moves"].copy()

            # Ensure player pokemon has attack and defense stats
            if "attack" not in self.player_pokemon:
                player_level = self.player_pokemon.get("level", 1)
                self.player_pokemon["attack"] = int(10 + player_level * 0.5)

            if "defense" not in self.player_pokemon:
                player_level = self.player_pokemon.get("level", 1)
                self.player_pokemon["defense"] = int(10 + player_level * 0.5)

            # Create animated sprite for player
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
        move_btn_w, move_btn_h = 120, 45
        move_gap_x = 30
        move_start_x = 150
        move_start_y = GameSettings.SCREEN_HEIGHT - 150

        moves = self.player_pokemon["moves"]
        for i, move in enumerate(moves):
            x = move_start_x + (move_btn_w + move_gap_x) * (i % 2)
            y = move_start_y - (move_btn_h + 15) * (i // 2)
            btn = BattleActionButton(move, x, y, move_btn_w, move_btn_h,
                                    lambda m=move: self._on_move_select(m))
            self.move_buttons.append(btn)

    def _on_fight_click(self) -> None:
        self._init_move_buttons()
        self.state = BossFightState.CHOOSE_MOVE
        self.message = "Choose a move:"

    def _on_item_click(self) -> None:
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return

        battle_items = [item for item in self.game_manager.bag.items
                       if item['name'].lower() != 'coins'
                       and item['name'].lower() != 'pokeball'
                       and ('potion' in item['name'].lower() or 'heal' in item['name'].lower())]

        if not battle_items:
            self.message = "No usable potions in battle!"
            return

        self.state = BossFightState.CHOOSE_ITEM
        self.item_panel = BattleItemPanel(
            battle_items,
            GameSettings.SCREEN_WIDTH // 2 - 150,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        )
        self.message = "Choose a potion:"

    def _on_switch_click(self) -> None:
        """Handle switch button click"""
        if not self.game_manager.bag or len(self.game_manager.bag.monsters) <= 1:
            self.message = "No other Pokemon to switch to!"
            return

        current_pokemon_index = 0

        available_pokemon = [p for i, p in enumerate(self.game_manager.bag.monsters)
                           if i != current_pokemon_index and p.get("hp", 0) > 0]

        if not available_pokemon:
            self.message = "No healthy Pokemon to switch to!"
            return

        self.state = BossFightState.CHOOSE_SWITCH
        self.switch_panel = BattleSwitchPanel(
            self.game_manager.bag.monsters,
            current_pokemon_index,
            GameSettings.SCREEN_WIDTH // 2 - 200,
            GameSettings.SCREEN_HEIGHT // 2 - 225
        )
        self.message = "Choose a Pokemon to switch:"

    def _on_run_click(self) -> None:
        self.message = "You cannot run from a legendary battle!"
        self._state_timer = 0.0

    def _on_move_select(self, move: str) -> None:
        if self.current_turn == "player":
            self.player_selected_move = move
            self.message = f"{self.player_pokemon['name']} used {move}!"
            self.state = BossFightState.PLAYER_TURN
            self._execute_player_attack()

    def _execute_player_attack(self) -> None:
        if not self.player_selected_move or not self.boss_pokemon:
            return

        # Trigger player attack animation
        if self.player_sprite:
            self.player_sprite.switch_animation("attack")

        # Create attack effect animation
        move_data = MOVES_DATABASE.get(self.player_selected_move)
        if move_data and move_data.get("animation"):
            boss_x = GameSettings.SCREEN_WIDTH - 150 - 150
            boss_y = 80 + 150
            self.attack_animation = AttackAnimation(
                move_data["animation"],
                (boss_x, boss_y),
                duration=0.6
            )

        # Calculate damage
        attacker_type = self.player_pokemon.get("type", "None")
        defender_type = self.boss_pokemon.get("type", "None")
        level = self.player_pokemon.get("level", 10)
        attack = self.player_pokemon.get("attack", 10)
        defense = self.boss_pokemon.get("defense", 10)

        damage, effectiveness_msg = calculate_damage(
            self.player_selected_move,
            attacker_type,
            defender_type,
            level,
            attack,
            defense
        )

        # Apply attack boost
        damage = int(damage * self.attack_boost)

        self.boss_pokemon['hp'] = max(0, self.boss_pokemon['hp'] - damage)
        self.effectiveness_message = effectiveness_msg

        self.message = f"{self.boss_pokemon['name']} took {damage} damage!"
        if effectiveness_msg:
            self.message += f" {effectiveness_msg}"

        # Screen shake on boss hit
        self.screen_shake_intensity = 10.0
        self.screen_shake_timer = 0.3

        Logger.info(f"Player attacked with {self.player_selected_move}: {damage} damage. Boss HP: {self.boss_pokemon['hp']}")

        if self._check_battle_end():
            self.state = BossFightState.SHOW_DAMAGE
            return

        self._state_timer = 0.0
        self.state = BossFightState.SHOW_DAMAGE

    def _execute_boss_attack(self) -> None:
        if not self.boss_pokemon or not self.player_pokemon:
            return

        # Boss intelligently selects moves
        moves = self.boss_pokemon.get("moves", ["Psystrike"])
        # Boss has a chance to use powerful moves more often
        if random.random() < 0.7:  # 70% chance to use first move (strongest)
            self.boss_selected_move = moves[0]
        else:
            self.boss_selected_move = random.choice(moves)

        self.message = f"Mewtwo used {self.boss_selected_move}!"
        self.turn_message = ""
        Logger.info(f"Boss selected move: {self.boss_selected_move}")

        self._state_timer = 0.0

    def _apply_boss_damage(self) -> None:
        """Apply damage from boss's selected move"""
        if not self.boss_pokemon or not self.player_pokemon or not self.boss_selected_move:
            return

        # Create attack effect animation
        move_data = MOVES_DATABASE.get(self.boss_selected_move)
        if move_data and move_data.get("animation"):
            player_x = 200 + 125
            player_y = GameSettings.SCREEN_HEIGHT - 250 - 100
            self.attack_animation = AttackAnimation(
                move_data["animation"],
                (player_x, player_y),
                duration=0.6
            )

        # Calculate damage
        attacker_type = self.boss_pokemon.get("type", "None")
        defender_type = self.player_pokemon.get("type", "None")
        level = self.boss_pokemon.get("level", 10)
        attack = self.boss_pokemon.get("attack", 10)
        defense = self.player_pokemon.get("defense", 10)

        damage, effectiveness_msg = calculate_damage(
            self.boss_selected_move,
            attacker_type,
            defender_type,
            level,
            attack,
            defense
        )

        # Boss deals 1.2x damage (more challenging)
        damage = int(damage * 1.2 * self.defense_boost)

        self.player_pokemon['hp'] = max(0, self.player_pokemon['hp'] - damage)
        self.effectiveness_message = effectiveness_msg

        self.message = f"{self.player_pokemon['name']} took {damage} damage!"
        if effectiveness_msg:
            self.message += f" {effectiveness_msg}"

        # Screen shake on player hit
        self.screen_shake_intensity = 15.0
        self.screen_shake_timer = 0.4

        Logger.info(f"Boss attacked with {self.boss_selected_move}: {damage} damage. Player HP: {self.player_pokemon['hp']}")

        if self._check_battle_end():
            self.state = BossFightState.SHOW_DAMAGE
            self.boss_selected_move = None
            return

        self._state_timer = 0.0
        self.state = BossFightState.SHOW_DAMAGE
        self.boss_selected_move = None

    def _check_battle_end(self) -> bool:
        if self.boss_pokemon and self.boss_pokemon['hp'] <= 0:
            self.state = BossFightState.BATTLE_END
            self.message = f"Victory! You defeated Mewtwo!"
            self.game_manager.boss_defeated = True
            Logger.info("Boss defeated! Player wins! Portal unlocked!")
            return True

        if self.player_pokemon and self.player_pokemon['hp'] <= 0:
            # Check if there are other healthy Pokemon available
            current_pokemon_index = 0
            available_pokemon = [p for i, p in enumerate(self.game_manager.bag.monsters)
                               if i != current_pokemon_index and p.get("hp", 0) > 0]

            if available_pokemon:
                # Force player to switch to another Pokemon
                self.state = BossFightState.CHOOSE_SWITCH
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
                self.state = BossFightState.BATTLE_END
                self.message = f"All your Pokemon fainted! You lost!"
                Logger.info("Battle lost! No healthy Pokemon left!")
                return True

        return False

    def _execute_switch(self, new_pokemon_index: int) -> None:
        """Switch to a different Pokemon"""
        if not self.game_manager.bag or new_pokemon_index >= len(self.game_manager.bag.monsters):
            return

        new_pokemon = self.game_manager.bag.monsters[new_pokemon_index]

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

        self.game_manager.bag.monsters[0], self.game_manager.bag.monsters[new_pokemon_index] = \
            self.game_manager.bag.monsters[new_pokemon_index], self.game_manager.bag.monsters[0]

        self.player_pokemon = self.game_manager.bag.monsters[0]

        # Create animated sprite
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

        if self.player_panel:
            self.player_panel.update_pokemon(self.player_pokemon)

        self.message = f"Go, {self.player_pokemon['name']}!"
        Logger.info(f"Switched to {self.player_pokemon['name']}")

        self.switch_panel = None
        self._state_timer = 0.0

        # If this was a forced switch (Pokemon fainted), boss gets a free turn
        # Otherwise it's a voluntary switch and boss also gets a turn
        if old_pokemon_fainted:
            # Forced switch - show message then let boss attack
            self.state = BossFightState.SHOW_DAMAGE
            self.current_turn = "boss"  # Boss will attack next
        else:
            # Voluntary switch - boss gets free turn
            self.state = BossFightState.SHOW_DAMAGE
            self.current_turn = "boss"  # Boss will attack next

    def _execute_item_attack(self, item: dict) -> None:
        if not self.player_pokemon:
            return

        item_name = item['name'].lower()

        if 'health' in item_name or 'heal' in item_name:
            heal_amount = int(self.player_pokemon['max_hp'] * 0.5)
            old_hp = self.player_pokemon['hp']
            self.player_pokemon['hp'] = min(self.player_pokemon['max_hp'], self.player_pokemon['hp'] + heal_amount)
            actual_heal = self.player_pokemon['hp'] - old_hp

            self.message = f"{self.player_pokemon['name']} used Health Potion! Restored {actual_heal} HP!"
            Logger.info(f"Player used Health Potion: healed {actual_heal} HP")

        elif 'strength' in item_name or 'attack' in item_name:
            self.attack_boost = 1.5
            self.message = f"{self.player_pokemon['name']} used Strength Potion! Attack power increased!"
            Logger.info(f"Player used Strength Potion: attack boost now {self.attack_boost}x")

        elif 'defense' in item_name or 'defence' in item_name:
            self.defense_boost = 0.7
            self.message = f"{self.player_pokemon['name']} used Defense Potion! Defense increased!"
            Logger.info(f"Player used Defense Potion: defense boost now {self.defense_boost}x")

        else:
            self.message = f"Used {item['name']}!"
            Logger.info(f"Player used unknown item: {item['name']}")

        item['count'] = max(0, item['count'] - 1)

        if item['count'] == 0 and self.game_manager.bag:
            self.game_manager.bag.items.remove(item)

        self._state_timer = 0.0
        self.state = BossFightState.SHOW_DAMAGE

    def _next_state(self) -> None:
        if self.state == BossFightState.INTRO:
            self.state = BossFightState.BOSS_APPEAR
            self.message = "A legendary Pokemon appears!"
        elif self.state == BossFightState.BOSS_APPEAR:
            self.state = BossFightState.SEND_PLAYER
            self.message = f"Go, {self.player_pokemon['name']}!"
        elif self.state == BossFightState.SEND_PLAYER:
            self.state = BossFightState.PLAYER_TURN
            self.current_turn = "player"
            self.message = "What will " + self.player_pokemon['name'] + " do?"
        self._state_timer = 0.0

    @override
    def update(self, dt: float) -> None:
        self._state_timer += dt

        # Update boss glow effect
        self.boss_glow_timer += dt
        self.boss_glow_alpha = int(128 + 127 * math.sin(self.boss_glow_timer * 3))

        # Update screen shake
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt
            if self.screen_shake_timer <= 0:
                self.screen_shake_intensity = 0

        # Update animated sprites
        if self.player_sprite:
            self.player_sprite.update(dt)

        # Update attack animation
        if self.attack_animation:
            self.attack_animation.update(dt)
            if self.attack_animation.is_finished():
                self.attack_animation = None

        if input_manager.key_pressed(pg.K_SPACE):
            if self.state == BossFightState.INTRO:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == BossFightState.BOSS_APPEAR:
                if self._pokemon_scale >= 1.0:
                    self._next_state()
                    self._pokemon_scale = 0.0
            elif self.state == BossFightState.SEND_PLAYER:
                if self._pokemon_scale >= 1.0:
                    self._next_state()
                    self._pokemon_scale = 0.0
            elif self.state == BossFightState.SHOW_DAMAGE:
                if self.player_sprite:
                    self.player_sprite.switch_animation("idle")

                if self._check_battle_end():
                    pass
                else:
                    self._state_timer = 0.0
                    if self.current_turn == "player":
                        self.state = BossFightState.BOSS_TURN
                        self.current_turn = "boss"
                    else:
                        self.state = BossFightState.PLAYER_TURN
                        self.current_turn = "player"
                        self.message = "What will " + self.player_pokemon['name'] + " do?"
                        self.turn_message = ""
            elif self.state == BossFightState.BATTLE_END:
                self.game_manager.save("saves/game0.json")
                scene_manager.change_scene("game")

        if self._pokemon_scale < 1.0:
            self._pokemon_scale += dt * 2.0

        if self.boss_panel is None and self.boss_pokemon and self.state == BossFightState.BOSS_APPEAR:
            self.boss_panel = PokemonStatsPanel(
                self.boss_pokemon,
                GameSettings.SCREEN_WIDTH - 180,
                20
            )

        if self.player_panel is None and self.player_pokemon and self.state == BossFightState.SEND_PLAYER:
            self.player_panel = PokemonStatsPanel(
                self.player_pokemon,
                20,
                GameSettings.SCREEN_HEIGHT - 250
            )

        if self.state == BossFightState.PLAYER_TURN:
            self.fight_btn.update(dt)
            self.item_btn.update(dt)
            self.switch_btn.update(dt)
            self.run_btn.update(dt)

        if self.state == BossFightState.CHOOSE_MOVE:
            for btn in self.move_buttons:
                btn.update(dt)

        if self.state == BossFightState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.update(dt)
                selected = self.item_panel.get_selected_item()
                if selected:
                    self._execute_item_attack(selected)

                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BossFightState.PLAYER_TURN
                    self.item_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"

        if self.state == BossFightState.CHOOSE_SWITCH:
            if self.switch_panel:
                self.switch_panel.update(dt)
                selected_index = self.switch_panel.get_selected_pokemon_index()
                if selected_index is not None:
                    self._execute_switch(selected_index)

                if input_manager.key_pressed(pg.K_ESCAPE):
                    self.state = BossFightState.PLAYER_TURN
                    self.switch_panel = None
                    self.message = "What will " + self.player_pokemon['name'] + " do?"

        # Boss turn handling
        if self.state == BossFightState.BOSS_TURN:
            if self._state_timer > 1.5 and self.boss_selected_move is None:
                self._execute_boss_attack()
            elif self._state_timer > 3.0 and self.boss_selected_move is not None:
                self._apply_boss_damage()

        # Update panels
        if self.boss_panel:
            self.boss_panel.update_pokemon(self.boss_pokemon)
        if self.player_panel:
            self.player_panel.update_pokemon(self.player_pokemon)

    def _draw_type_matchup_display(self, surface: pg.Surface) -> None:
        """Draw a beautiful type matchup display at the top of the screen"""
        if not self.player_pokemon or not self.boss_pokemon:
            return

        from src.utils.pokemon_data import TYPE_ADVANTAGE

        player_type = self.player_pokemon.get("type", "None")
        boss_type = self.boss_pokemon.get("type", "None")

        # Type color mapping for visual appeal
        type_colors = {
            "Fire": (255, 100, 50),
            "Water": (50, 150, 255),
            "Ice": (150, 230, 255),
            "Wind": (200, 255, 200),
            "Light": (255, 255, 150),
            "Slash": (200, 200, 200),
            "Psychic": (255, 100, 255),  # Boss Mewtwo type
            "None": (150, 150, 150),
        }

        # Draw background panel with boss theme
        panel_width = 500
        panel_height = 70
        panel_x = (GameSettings.SCREEN_WIDTH - panel_width) // 2
        panel_y = 10

        # Semi-transparent dark background with purple tint for boss
        panel_surface = pg.Surface((panel_width, panel_height), pg.SRCALPHA)
        pg.draw.rect(panel_surface, (64, 0, 128, 180), (0, 0, panel_width, panel_height), border_radius=15)
        pg.draw.rect(panel_surface, (148, 0, 211, 150), (0, 0, panel_width, panel_height), 3, border_radius=15)
        surface.blit(panel_surface, (panel_x, panel_y))

        # Draw player type badge (left side)
        player_color = type_colors.get(player_type, (150, 150, 150))
        player_badge_x = panel_x + 30
        player_badge_y = panel_y + 20
        player_badge_w = 120
        player_badge_h = 35

        pg.draw.rect(surface, player_color, (player_badge_x, player_badge_y, player_badge_w, player_badge_h), border_radius=10)
        pg.draw.rect(surface, (255, 255, 255), (player_badge_x, player_badge_y, player_badge_w, player_badge_h), 2, border_radius=10)

        player_type_text = self._font.render(player_type, True, (255, 255, 255))
        text_rect = player_type_text.get_rect(center=(player_badge_x + player_badge_w // 2, player_badge_y + player_badge_h // 2))
        surface.blit(player_type_text, text_rect)

        # Draw boss type badge (right side) with special glow
        boss_color = type_colors.get(boss_type, (150, 150, 150))
        boss_badge_x = panel_x + panel_width - 150
        boss_badge_y = panel_y + 20
        boss_badge_w = 120
        boss_badge_h = 35

        # Boss badge glow effect
        glow_size = 6
        for i in range(glow_size, 0, -1):
            glow_alpha = 30 + (glow_size - i) * 10
            glow_surf = pg.Surface((boss_badge_w + i*2, boss_badge_h + i*2), pg.SRCALPHA)
            pg.draw.rect(glow_surf, (*boss_color, glow_alpha), (0, 0, boss_badge_w + i*2, boss_badge_h + i*2), border_radius=10)
            surface.blit(glow_surf, (boss_badge_x - i, boss_badge_y - i))

        pg.draw.rect(surface, boss_color, (boss_badge_x, boss_badge_y, boss_badge_w, boss_badge_h), border_radius=10)
        pg.draw.rect(surface, (255, 255, 255), (boss_badge_x, boss_badge_y, boss_badge_w, boss_badge_h), 2, border_radius=10)

        boss_type_text = self._font.render(boss_type, True, (255, 255, 255))
        text_rect = boss_type_text.get_rect(center=(boss_badge_x + boss_badge_w // 2, boss_badge_y + boss_badge_h // 2))
        surface.blit(boss_type_text, text_rect)

        # Draw matchup indicator (center)
        center_x = panel_x + panel_width // 2
        center_y = panel_y + panel_height // 2

        # Determine matchup
        player_advantage = TYPE_ADVANTAGE.get(player_type) == boss_type
        boss_advantage = TYPE_ADVANTAGE.get(boss_type) == player_type

        if player_type == "None" or boss_type == "None":
            # Neutral - no type advantages
            symbol = "="
            symbol_color = (200, 200, 200)
            glow_color = (100, 100, 100)
        elif player_advantage:
            # Player has advantage
            symbol = ">"
            symbol_color = (100, 255, 100)
            glow_color = (50, 200, 50)
        elif boss_advantage:
            # Boss has advantage
            symbol = "<"
            symbol_color = (255, 100, 100)
            glow_color = (200, 50, 50)
        else:
            # Neutral matchup
            symbol = "="
            symbol_color = (255, 255, 150)
            glow_color = (200, 200, 100)

        # Draw glowing symbol with enhanced effect for boss battle
        symbol_font = pg.font.Font('assets/fonts/Minecraft.ttf', 40)

        # Enhanced glow effect
        for offset in range(4, 0, -1):
            glow_alpha = 100 - (offset * 20)
            glow_surface = pg.Surface((60, 60), pg.SRCALPHA)
            glow_text = symbol_font.render(symbol, True, (*glow_color, glow_alpha))
            glow_rect = glow_text.get_rect(center=(30, 30))
            glow_surface.blit(glow_text, glow_rect)
            surface.blit(glow_surface, (center_x - 30 - offset, center_y - 30 - offset))

        # Main symbol
        symbol_text = symbol_font.render(symbol, True, symbol_color)
        symbol_rect = symbol_text.get_rect(center=(center_x, center_y))
        surface.blit(symbol_text, symbol_rect)

    @override
    def draw(self, screen: pg.Surface) -> None:
        # Calculate screen shake offset
        shake_x = 0
        shake_y = 0
        if self.screen_shake_intensity > 0:
            shake_x = random.randint(int(-self.screen_shake_intensity), int(self.screen_shake_intensity))
            shake_y = random.randint(int(-self.screen_shake_intensity), int(self.screen_shake_intensity))

        # Create offset surface for shake effect
        temp_surface = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))

        self.background.draw(temp_surface)

        # Draw type matchup display (only when both Pokemon are visible)
        if self.state in (BossFightState.PLAYER_TURN, BossFightState.BOSS_TURN, BossFightState.CHOOSE_MOVE, BossFightState.CHOOSE_ITEM, BossFightState.SHOW_DAMAGE, BossFightState.CHOOSE_SWITCH):
            self._draw_type_matchup_display(temp_surface)

        # Draw panels
        if self.boss_panel and self.state in (BossFightState.BOSS_APPEAR, BossFightState.SEND_PLAYER, BossFightState.PLAYER_TURN, BossFightState.BOSS_TURN, BossFightState.BATTLE_END, BossFightState.SHOW_DAMAGE, BossFightState.CHOOSE_MOVE, BossFightState.CHOOSE_ITEM):
            self.boss_panel.draw(temp_surface)

        if self.player_panel and self.state in (BossFightState.SEND_PLAYER, BossFightState.PLAYER_TURN, BossFightState.BOSS_TURN, BossFightState.BATTLE_END, BossFightState.SHOW_DAMAGE, BossFightState.CHOOSE_MOVE, BossFightState.CHOOSE_ITEM):
            self.player_panel.draw(temp_surface)

        # Draw attack animation
        if self.attack_animation:
            self.attack_animation.draw(temp_surface)

        # Draw Boss Pokemon with glow effect
        if (self.state == BossFightState.BOSS_APPEAR or self.state == BossFightState.SEND_PLAYER or self.state in (BossFightState.PLAYER_TURN, BossFightState.BOSS_TURN, BossFightState.BATTLE_END, BossFightState.SHOW_DAMAGE)) and self.boss_pokemon and self.boss_sprite:
            if self.state == BossFightState.BOSS_APPEAR:
                scale = min(self._pokemon_scale, 1.0)
            else:
                scale = 1.0

            size = int(300 * scale)
            scaled_sprite = pg.transform.smoothscale(self.boss_sprite.image, (size, size))

            # Add glow effect
            glow_surface = pg.Surface((size + 20, size + 20), pg.SRCALPHA)
            glow_surface.fill((148, 0, 211, self.boss_glow_alpha))
            temp_surface.blit(glow_surface, (GameSettings.SCREEN_WIDTH - size - 160, 70))

            x = GameSettings.SCREEN_WIDTH - size - 150
            y = 80
            temp_surface.blit(scaled_sprite, (x, y))

        # Draw Player Pokemon
        if (self.state == BossFightState.SEND_PLAYER or self.state in (BossFightState.PLAYER_TURN, BossFightState.BOSS_TURN, BossFightState.BATTLE_END, BossFightState.SHOW_DAMAGE)) and self.player_pokemon:
            if self.player_sprite:
                if self.state == BossFightState.SEND_PLAYER:
                    scale = min(self._pokemon_scale, 1.0)
                else:
                    scale = 1.0

                frame = self.player_sprite.get_current_frame()
                size = int(250 * scale)
                scaled_frame = pg.transform.smoothscale(frame, (size, size))

                x = 200
                y = GameSettings.SCREEN_HEIGHT - size - 200
                temp_surface.blit(scaled_frame, (x, y))
            else:
                sprite = Sprite(self.player_pokemon["sprite_path"], (250, 250))
                if self.state == BossFightState.SEND_PLAYER:
                    scale = min(self._pokemon_scale, 1.0)
                else:
                    scale = 1.0
                size = int(250 * scale)
                scaled_sprite = pg.transform.scale(sprite.image, (size, size))
                x = 200
                y = GameSettings.SCREEN_HEIGHT - size - 200
                temp_surface.blit(scaled_sprite, (x, y))

        # Draw Message Box
        box_h, box_w = 120, GameSettings.SCREEN_WIDTH - 40
        box_x, box_y = 20, GameSettings.SCREEN_HEIGHT - box_h - 20

        pg.draw.rect(temp_surface, (64, 0, 128), (box_x, box_y, box_w, box_h))
        pg.draw.rect(temp_surface, (148, 0, 211), (box_x, box_y, box_w, box_h), 3)

        if self.effectiveness_message:
            if self.effectiveness_message in self.message:
                main_msg = self.message.replace(self.effectiveness_message, "").strip()
            else:
                main_msg = self.message
            msg_text = self._message_font.render(main_msg, True, (255, 255, 255))
            temp_surface.blit(msg_text, (box_x + 10, box_y + 10))

            if "super effective" in self.effectiveness_message:
                eff_color = (100, 255, 100)
            elif "not very effective" in self.effectiveness_message:
                eff_color = (255, 100, 100)
            elif "Normal damage" in self.effectiveness_message:
                eff_color = (200, 200, 150)
            elif "Typeless" in self.effectiveness_message:
                eff_color = (180, 180, 180)
            else:
                eff_color = (255, 255, 255)

            eff_text = self._message_font.render(self.effectiveness_message, True, eff_color)
            temp_surface.blit(eff_text, (box_x + 10, box_y + 30))
        else:
            msg_text = self._message_font.render(self.message, True, (255, 255, 255))
            temp_surface.blit(msg_text, (box_x + 10, box_y + 10))

        if self.state not in (BossFightState.PLAYER_TURN, BossFightState.BOSS_TURN, BossFightState.CHOOSE_MOVE, BossFightState.BATTLE_END, BossFightState.SHOW_DAMAGE):
            if self.state == BossFightState.INTRO:
                hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                temp_surface.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
            elif self.state in (BossFightState.BOSS_APPEAR, BossFightState.SEND_PLAYER):
                if self._pokemon_scale >= 1.0:
                    hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                    temp_surface.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))

        if self.state == BossFightState.PLAYER_TURN:
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

            self.fight_btn.draw(temp_surface)
            self.item_btn.draw(temp_surface)
            self.switch_btn.draw(temp_surface)
            self.run_btn.draw(temp_surface)

        if self.state == BossFightState.CHOOSE_MOVE:
            start_x = box_x + 180
            start_y = box_y + 120
            btn_w = 100
            gap = 30

            for i, btn in enumerate(self.move_buttons):
                current_x = start_x + i * (btn_w + gap)
                current_y = start_y - 100

                btn.rect.topleft = (current_x, current_y)

                btn.draw(temp_surface)

        if self.state == BossFightState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.draw(temp_surface)

            hint_text = self._message_font.render("Press ESC to cancel", True, (255, 255, 0))
            temp_surface.blit(hint_text, (box_x + 10, box_y + box_h - 30))

        if self.state == BossFightState.CHOOSE_SWITCH:
            if self.switch_panel:
                self.switch_panel.draw(temp_surface)

            hint_text = self._message_font.render("Press ESC to cancel", True, (255, 255, 0))
            temp_surface.blit(hint_text, (box_x + 10, box_y + box_h - 30))

        if self.state == BossFightState.SHOW_DAMAGE:
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            temp_surface.blit(hint_text, (box_x + 10, box_y + box_h - 30))

        if self.state == BossFightState.BATTLE_END:
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            temp_surface.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))

        # Apply shake and blit to screen
        screen.blit(temp_surface, (shake_x, shake_y))

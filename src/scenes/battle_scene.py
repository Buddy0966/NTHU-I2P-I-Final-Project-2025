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
    CATCHING = 11  # Pokéball catching state
    CATCH_ANIMATION = 12  # Pokéball flying animation


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
    
    # Pokéball catching animation
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
        self.turn_message = ""
        self.item_panel = None
        self.player_selected_item = None
        
        # Pokéball catching animation
        try:
            self.pokeball_sprite = Sprite("UI/pokeball.png", (30, 30))
        except:
            self.pokeball_sprite = None
        self.pokeball_x = 0.0
        self.pokeball_y = 0.0
        self.catch_panel = None
        
        # Main action buttons (will be repositioned in PLAYER_TURN)
        btn_w, btn_h = 80, 40
        
        self.fight_btn = BattleActionButton("Fight", 0, 0, btn_w, btn_h, self._on_fight_click)
        self.item_btn = BattleActionButton("Item", 0, 0, btn_w, btn_h, self._on_item_click)
        self.switch_btn = BattleActionButton("Switch", 0, 0, btn_w, btn_h)
        self.run_btn = BattleActionButton("Run", 0, 0, btn_w, btn_h, self._on_run_click)
        
        # Move buttons (for attack selection)
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
        Logger.info(f"Battle started against {self.opponent_name}")
        self._init_pokemon()
        self._next_state()

    @override
    def exit(self) -> None:
        pass
    
    def _init_pokemon(self) -> None:
        self.opponent_pokemon = {
            "name": "Leogreen",
            "hp": 45,
            "max_hp": 45,
            "level": 10,
            "sprite_path": "menu_sprites/menusprite2.png"
        }
        
        if self.game_manager.bag and len(self.game_manager.bag._monsters_data) > 0:
            self.player_pokemon = self.game_manager.bag._monsters_data[0]
    
    def _on_fight_click(self) -> None:
        self.state = BattleState.CHOOSE_MOVE
        self.message = "Choose a move:"
    
    def _on_item_click(self) -> None:
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return
        
        # Filter out coins - they are not battle items
        battle_items = [item for item in self.game_manager.bag.items if item['name'].lower() != 'coin']
        
        if not battle_items:
            self.message = "No usable items in battle!"
            return
        
        self.state = BattleState.CHOOSE_ITEM
        self.item_panel = BattleItemPanel(
            battle_items,
            GameSettings.SCREEN_WIDTH // 2 - 150,
            GameSettings.SCREEN_HEIGHT // 2 - 200
        )
        self.message = "Choose an item:"
    
    def _show_catch_panel(self) -> None:
        """Show Pokéball catching panel after opponent is defeated"""
        if not self.game_manager.bag or not self.game_manager.bag.items:
            self.message = "No items available!"
            return
        
        # Get only Pokéballs
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
        self.message = "Use a Pokéball to catch?"
    
    def _on_run_click(self) -> None:
        self.message = "Escaped from battle!"
        self._state_timer = 0.0
    
    def _on_move_select(self, move: str) -> None:
        if self.current_turn == "player":
            self.player_selected_move = move
            self.message = f"{self.player_pokemon['name']} used {move}!"
            self.state = BattleState.PLAYER_TURN
            self._execute_player_attack()
    
    def _execute_player_attack(self) -> None:
        if not self.player_selected_move or not self.opponent_pokemon:
            return
        
        # Calculate damage (simplified: random between 10-20)
        import random
        damage = random.randint(10, 20)
        self.opponent_pokemon['hp'] = max(0, self.opponent_pokemon['hp'] - damage)
        
        # 只設定 message，刪除 turn_message
        self.message = f"{self.opponent_pokemon['name']} took {damage} damage!"
        Logger.info(f"Player attacked: {damage} damage. Opponent HP: {self.opponent_pokemon['hp']}")
        
        if self._check_battle_end():
            self.state = BattleState.SHOW_DAMAGE
            return
        
        # Transition to show damage state first
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE
    
    def _execute_enemy_attack(self) -> None:
        if not self.opponent_pokemon or not self.player_pokemon:
            return
        
        # Enemy selects a random move
        moves = ["Woodhammer", "Headbutt", "Howl", "Leer"]
        import random
        self.enemy_selected_move = random.choice(moves)
        
        # Calculate damage
        damage = random.randint(8, 15)
        self.player_pokemon['hp'] = max(0, self.player_pokemon['hp'] - damage)
        
        # 只設定 message，刪除 turn_message
        self.message = f"{self.player_pokemon['name']} took {damage} damage!"
        Logger.info(f"Enemy attacked: {damage} damage. Player HP: {self.player_pokemon['hp']}")
        
        if self._check_battle_end():
            self.state = BattleState.SHOW_DAMAGE
            return
        
        # Transition to show damage state
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE
        
    def _check_battle_end(self) -> bool:
        if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
            self.state = BattleState.CATCHING
            self.message = f"{self.opponent_pokemon['name']} fainted! Throw a Pokéball?"
            Logger.info("Battle won! Ready to catch opponent pokemon!")
            return True
        
        if self.player_pokemon and self.player_pokemon['hp'] <= 0:
            self.state = BattleState.BATTLE_END
            self.message = f"{self.player_pokemon['name']} fainted! You lost!"
            Logger.info("Battle lost!")
            return True
        
        return False
    
    def _execute_item_attack(self, item: dict) -> None:
        if not self.opponent_pokemon:
            return
        
        # Calculate damage based on item (using item name as fallback, can be customized)
        import random
        damage = random.randint(5, 25)
        self.opponent_pokemon['hp'] = max(0, self.opponent_pokemon['hp'] - damage)
        
        # 只設定 message，刪除 turn_message
        self.message = f"{self.opponent_pokemon['name']} took {damage} damage!"
        Logger.info(f"Player used item {item['name']}: {damage} damage. Opponent HP: {self.opponent_pokemon['hp']}")
        
        # Reduce item count
        item['count'] = max(0, item['count'] - 1)
        
        if self._check_battle_end():
            self.state = BattleState.SHOW_DAMAGE
            return
        
        # Transition to show damage state first
        self._state_timer = 0.0
        self.state = BattleState.SHOW_DAMAGE
    
    def _execute_pokeball_catch(self, item: dict) -> None:
        """Execute pokéball catch animation and logic"""
        if not self.opponent_pokemon:
            return
        
        # Start pokéball animation
        self.pokeball_x = GameSettings.SCREEN_WIDTH // 2
        self.pokeball_y = GameSettings.SCREEN_HEIGHT - 100
        
        # Reduce pokéball count
        item['count'] = max(0, item['count'] - 1)
        
        self.state = BattleState.CATCH_ANIMATION
        self._state_timer = 0.0
        Logger.info(f"Pokéball catch animation started for {self.opponent_pokemon['name']}")
        
    def _catch_opponent_pokemon(self) -> None:
        """Complete the catch - add opponent pokemon to player's bag"""
        if not self.opponent_pokemon or not self.game_manager.bag:
            self.state = BattleState.BATTLE_END
            self.message = "Catch failed!"
            Logger.error("Catch failed: missing opponent_pokemon or bag")
            return
        
        # Add opponent pokemon to player's bag
        caught_pokemon = {
            "name": self.opponent_pokemon['name'],
            "hp": 1,  # Reset HP to 1
            "max_hp": self.opponent_pokemon['max_hp'],
            "level": self.opponent_pokemon['level'],
            "sprite_path": self.opponent_pokemon['sprite_path']
        }
        
        self.game_manager.bag._monsters_data.append(caught_pokemon)
        Logger.info(f"Caught {self.opponent_pokemon['name']}! Added to bag.")
        Logger.info(f"Current monsters in bag: {len(self.game_manager.bag._monsters_data)}")
        for monster in self.game_manager.bag._monsters_data:
            Logger.info(f"  - {monster['name']}")
        
        self.state = BattleState.BATTLE_END
        self.message = f"Successfully caught {self.opponent_pokemon['name']}!"
        
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
        
        if input_manager.key_pressed(pg.K_SPACE):
            if self.state == BattleState.CHALLENGER:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == BattleState.SEND_OPPONENT:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == BattleState.SEND_PLAYER:
                self._next_state()
                self._pokemon_scale = 0.0
            elif self.state == BattleState.SHOW_DAMAGE:
                # After showing damage, transition to next state
                if self._check_battle_end():
                    # Battle ended - show catch panel if opponent fainted
                    if self.opponent_pokemon and self.opponent_pokemon['hp'] <= 0:
                        self._show_catch_panel()
                else:
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
                scene_manager.change_scene("game")
        
        # Handle Run Away action
        if self.state == BattleState.PLAYER_TURN and self._state_timer > 2.0 and self.message == "Escaped from battle!":
            scene_manager.change_scene("game")
        
        if self._pokemon_scale < 1.0:
            self._pokemon_scale += dt * 2.0
        
        if self.opponent_panel is None and self.opponent_pokemon and self.state != BattleState.INTRO and self.state != BattleState.CHALLENGER:
            self.opponent_panel = PokemonStatsPanel(
                self.opponent_pokemon,
                GameSettings.SCREEN_WIDTH - 180,
                20
            )
        
        if self.player_panel is None and self.player_pokemon and self.state != BattleState.INTRO and self.state != BattleState.CHALLENGER:
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
        
        # Pokéball catch animation
        if self.state == BattleState.CATCH_ANIMATION:
            # Pokéball flies from bottom to opponent position
            opponent_x = GameSettings.SCREEN_WIDTH - 150
            opponent_y = 150
            
            animation_duration = 0.8  # seconds
            progress = min(self._state_timer / animation_duration, 1.0)
            
            # Linear interpolation from current position to opponent position
            self.pokeball_x = GameSettings.SCREEN_WIDTH // 2 + (opponent_x - GameSettings.SCREEN_WIDTH // 2) * progress
            self.pokeball_y = GameSettings.SCREEN_HEIGHT - 100 + (opponent_y - (GameSettings.SCREEN_HEIGHT - 100)) * progress
            
            if progress >= 1.0:
                # Animation complete - catch the pokemon
                self._catch_opponent_pokemon()
        
        # Enemy turn handling
        if self.state == BattleState.ENEMY_TURN:
            if self._state_timer > 1.5:
                self._execute_enemy_attack()
        
        # Update panels for HP changes
        if self.opponent_panel:
            self.opponent_panel.update_pokemon(self.opponent_pokemon)
        if self.player_panel:
            self.player_panel.update_pokemon(self.player_pokemon)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        if self.opponent_panel and self.state != BattleState.INTRO and self.state != BattleState.CHALLENGER:
            self.opponent_panel.draw(screen)
        
        if self.player_panel and self.state != BattleState.INTRO and self.state != BattleState.CHALLENGER:
            self.player_panel.draw(screen)
        
        
        if (self.state == BattleState.SEND_OPPONENT or self.state == BattleState.SEND_PLAYER or self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.BATTLE_END, BattleState.CATCHING, BattleState.CATCH_ANIMATION, BattleState.SHOW_DAMAGE)) and self.opponent_pokemon:
            sprite = Sprite(self.opponent_pokemon["sprite_path"], (200, 200))
            if self.state == BattleState.SEND_OPPONENT:
                scale = min(self._pokemon_scale, 1.0)
            else:
                scale = 1.0
            size = int(200 * scale)
            scaled_sprite = pg.transform.scale(sprite.image, (size, size))
            x = GameSettings.SCREEN_WIDTH - size - 150
            y = 80
            screen.blit(scaled_sprite, (x, y))
        
        if (self.state == BattleState.SEND_PLAYER or self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.BATTLE_END, BattleState.CATCHING, BattleState.CATCH_ANIMATION, BattleState.SHOW_DAMAGE)) and self.player_pokemon:
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
        
        box_h, box_w = 120, GameSettings.SCREEN_WIDTH - 40
        box_x, box_y = 20, GameSettings.SCREEN_HEIGHT - box_h - 20
        
        pg.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_w, box_h))
        pg.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 2)
        
        # Display main message
        msg_text = self._message_font.render(self.message, True, (255, 255, 255))
        screen.blit(msg_text, (box_x + 10, box_y + 10))
        
        # Display turn message (damage dealt)
        if self.turn_message and self.state in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.PLAYER_TURN):
            turn_text = self._message_font.render(self.turn_message, True, (255, 200, 100))
            screen.blit(turn_text, (box_x + 10, box_y + 35))
        
        if self.state not in (BattleState.PLAYER_TURN, BattleState.ENEMY_TURN, BattleState.CHOOSE_MOVE, BattleState.BATTLE_END, BattleState.SHOW_DAMAGE):
            if self.state in (BattleState.CHALLENGER, BattleState.SEND_OPPONENT, BattleState.SEND_PLAYER):
                hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
        
        if self.state == BattleState.PLAYER_TURN:
            # Reposition buttons inside the box
            btn_w, btn_h = 80, 40
            gap = 10
            btn_start_x = box_x + 20
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
        
        if self.state == BattleState.CHOOSE_MOVE:
            pg.draw.rect(screen, (0, 0, 0), (box_x, box_y, box_w, box_h))
            pg.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 2)
            
            msg_text = self._message_font.render(self.message, True, (255, 255, 255))
            screen.blit(msg_text, (box_x + 10, box_y + 10))
            
            for btn in self.move_buttons:
                btn.draw(screen)
        
        if self.state == BattleState.CHOOSE_ITEM:
            if self.item_panel:
                self.item_panel.draw(screen)
            
            hint_text = self._message_font.render("Press ESC to cancel", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == BattleState.CATCHING:
            if self.catch_panel:
                self.catch_panel.draw(screen)
            
            hint_text = self._message_font.render("Press ESC to skip", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == BattleState.CATCH_ANIMATION:
            # Draw pokéball flying toward opponent
            if self.pokeball_sprite:
                screen.blit(self.pokeball_sprite.image, (int(self.pokeball_x), int(self.pokeball_y)))
            
            # Show animation message
            msg_text = self._message_font.render("Throwing Pokéball...", True, (255, 255, 255))
            screen.blit(msg_text, (box_x + 10, box_y + 10))
        
        if self.state == BattleState.SHOW_DAMAGE:
            # Show damage message, wait for SPACE
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + 10, box_y + box_h - 30))
        
        if self.state == BattleState.BATTLE_END:
            hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
            screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
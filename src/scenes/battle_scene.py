from __future__ import annotations
import pygame as pg
from src.scenes.scene import Scene
from src.sprites import BackgroundSprite, Sprite
from src.utils import GameSettings, Logger
from src.core.services import input_manager, scene_manager
from src.core import GameManager
from src.interface.components import PokemonStatsPanel, BattleActionButton
from src.utils.definition import Monster
from typing import override
from enum import Enum


class BattleState(Enum):
    INTRO = 0
    CHALLENGER = 1
    SEND_OPPONENT = 2
    SEND_PLAYER = 3
    MAIN = 4
    CHOOSE_MOVE = 5


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
        
        btn_w, btn_h = 100, 50
        btn_y = GameSettings.SCREEN_HEIGHT - 140
        gap = 20
        
        self.fight_btn = BattleActionButton("Fight", 300, btn_y + 25, btn_w, btn_h, self._on_fight_click)
        self.item_btn = BattleActionButton("Item", 300 + btn_w + gap, btn_y + 25, btn_w, btn_h)
        self.switch_btn = BattleActionButton("Switch", 300 + (btn_w + gap) * 2, btn_y + 25, btn_w, btn_h)
        self.run_btn = BattleActionButton("Run", 300 + (btn_w + gap) * 3, btn_y + 25, btn_w, btn_h)
        
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
    
    def _on_move_select(self, move: str) -> None:
        self.message = f"{self.player_pokemon['name']} used {move}!"
        self.state = BattleState.MAIN
    
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
            self.state = BattleState.MAIN
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
            elif self.state == BattleState.MAIN:
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
        
        if self.state == BattleState.MAIN:
            self.fight_btn.update(dt)
            self.item_btn.update(dt)
            self.switch_btn.update(dt)
            self.run_btn.update(dt)
        
        if self.state == BattleState.CHOOSE_MOVE:
            for btn in self.move_buttons:
                btn.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        if self.opponent_panel and self.state != BattleState.INTRO and self.state != BattleState.CHALLENGER:
            self.opponent_panel.draw(screen)
        
        if self.player_panel and self.state != BattleState.INTRO and self.state != BattleState.CHALLENGER:
            self.player_panel.draw(screen)
        
        
        if (self.state == BattleState.SEND_OPPONENT or self.state == BattleState.SEND_PLAYER or self.state == BattleState.MAIN) and self.opponent_pokemon:
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
        
        if (self.state == BattleState.SEND_PLAYER or self.state == BattleState.MAIN) and self.player_pokemon:
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
        
        msg_text = self._message_font.render(self.message, True, (255, 255, 255))
        screen.blit(msg_text, (box_x + 10, box_y + 10))
        
        if self.state != BattleState.MAIN:
            if self.state in (BattleState.CHALLENGER, BattleState.SEND_OPPONENT, BattleState.SEND_PLAYER):
                hint_text = self._message_font.render("Press SPACE to continue", True, (255, 255, 0))
                screen.blit(hint_text, (box_x + box_w - 250, box_y + box_h - 30))
        elif self.state == BattleState.MAIN:
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

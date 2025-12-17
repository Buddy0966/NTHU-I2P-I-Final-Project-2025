import pygame as pg

from src.utils import GameSettings, Logger
from .services import scene_manager, input_manager

from src.scenes.menu_scene import MenuScene
from src.scenes.game_scene import GameScene
from src.scenes.setting_scene import SettingScene
from src.scenes.battle_scene import BattleScene
from src.scenes.catch_pokemon_scene import CatchPokemonScene
from src.scenes.battle_transition_scene import BattleTransitionScene
from src.scenes.boss_fight_scene import BossFightScene
from src.core.managers.game_manager import GameManager

class Engine:

    screen: pg.Surface              # Screen Display of the Game
    clock: pg.time.Clock            # Clock for FPS control
    running: bool                   # Running state of the game

    def __init__(self):
        Logger.info("Initializing Engine")

        pg.init()

        self.screen = pg.display.set_mode((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        self.clock = pg.time.Clock()
        self.running = True

        pg.display.set_caption(GameSettings.TITLE)

        scene_manager.register_scene("menu", MenuScene())
        scene_manager.register_scene("game", GameScene())
        scene_manager.register_scene("setting", SettingScene())
        
        # Battle scenes (will be re-created dynamically)
        game_manager = GameManager.load("saves/game0.json")
        scene_manager.register_scene("battle", BattleScene(game_manager))
        scene_manager.register_scene("catch_pokemon", CatchPokemonScene(game_manager))
        scene_manager.register_scene("battle_transition", BattleTransitionScene())
        scene_manager.register_scene("boss_fight", BossFightScene(game_manager))
        
        scene_manager.change_scene("menu")

    def run(self):
        Logger.info("Running the Game Loop ...")

        while self.running:
            dt = self.clock.tick(GameSettings.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.render()

    def handle_events(self):
        input_manager.reset()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            input_manager.handle_events(event)

    def update(self, dt: float):
        scene_manager.update(dt)

    def render(self):
        self.screen.fill((0, 0, 0))     # Make sure the display is cleared
        scene_manager.draw(self.screen) # Draw the current scene
        pg.display.flip()               # Render the display

from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger, Direction
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        '''
        [TODO HACKATHON 2]
        Calculate the distance change, and then normalize the distance
        '''
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1.0
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1.0
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1.0
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1.0

        # normalize diagonal movement
        if dis.x != 0 or dis.y != 0:
            length = math.hypot(dis.x, dis.y)
            dis.x = (dis.x / length) * self.speed * dt
            dis.y = (dis.y / length) * self.speed * dt

            # Update direction and animation based on movement
            # Prioritize vertical movement over horizontal for animation
            if abs(dis.y) > abs(dis.x):
                if dis.y < 0:
                    self.direction = Direction.UP
                    self.animation.switch("up")
                else:
                    self.direction = Direction.DOWN
                    self.animation.switch("down")
            else:
                if dis.x < 0:
                    self.direction = Direction.LEFT
                    self.animation.switch("left")
                else:
                    self.direction = Direction.RIGHT
                    self.animation.switch("right")


        '''
        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
        '''

        # Create player rect for collision testing
        player_rect = self.animation.rect

        # Step 1: Try moving only in X
        new_x = self.position.x + dis.x
        test_rect_x = player_rect.copy()
        test_rect_x.x = new_x
        if not self.game_manager.check_collision(test_rect_x):
            self.position.x = new_x
        else:
            # Snap X to nearest grid edge
            self.position.x = self._snap_to_grid(self.position.x)

        # Step 2: Try moving only in Y (from updated X position)
        new_y = self.position.y + dis.y
        test_rect_y = player_rect.copy()
        test_rect_y.x = self.position.x  # Use updated X
        test_rect_y.y = new_y
        if not self.game_manager.check_collision(test_rect_y):
            self.position.y = new_y
        else:
            # Snap Y to nearest grid edge
            self.position.y = self._snap_to_grid(self.position.y)
                
        
        # Check teleportation
        # Only check teleporter when teleport cooldown has expired
        if getattr(self.game_manager, "teleport_cooldown", 0.0) <= 0.0:
            tp = self.game_manager.current_map.check_teleport(self.position)
            if tp:
                dest = tp.destination
                self.game_manager.switch_map(dest)
                
        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @property
    @override
    def camera(self) -> PositionCamera:
        # Use the parent Entity's camera implementation which includes map bounds clamping
        return super().camera
            
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)
from __future__ import annotations
import pygame as pg
import math
from src.scenes.scene import Scene
from src.sprites import BackgroundSprite
from src.utils import GameSettings, Logger
from src.core.services import scene_manager
from typing import override



class BattleTransitionScene(Scene):
    _start_time: float
    _duration: float
    
    def __init__(self, duration: float = 0.7):
        super().__init__()
        self.background = BackgroundSprite("backgrounds/background1.png")
        self._start_time = 0.0
        self._duration = duration

    @override
    def enter(self) -> None:
        self._start_time = 0.0

    @override
    def exit(self) -> None:
        pass

    @override
    def update(self, dt: float) -> None:
        self._start_time += dt
        if self._start_time >= self._duration:
            scene_manager.change_scene("battle")

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        
        progress = min(self._start_time / self._duration, 1.0)
        cx, cy = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2
        
        # 5 triangles rotating (尖端都指向中心，更細更長)
        triangle_count = 5  # 改成5個三角形
        for i in range(triangle_count):
            angle = (progress * 2 * math.pi) + (i * 2 * math.pi / triangle_count)
            radius = 1000  # 增加半徑讓三角形更長
            
            # 尖端在中心點
            x1 = cx
            y1 = cy
            
            # 底邊的兩個頂點在外圓上
            offset_angle = (math.pi / 24) + (progress * math.pi / 5)            
            x2 = cx + radius * math.cos(angle - offset_angle)
            y2 = cy + radius * math.sin(angle - offset_angle)
            
            x3 = cx + radius * math.cos(angle + offset_angle)
            y3 = cy + radius * math.sin(angle + offset_angle)

            pg.draw.polygon(screen, (0, 0 ,0), [(x1, y1), (x2, y2), (x3, y3)])
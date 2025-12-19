from pygame import Rect
from .settings import GameSettings
from dataclasses import dataclass
from enum import Enum
from typing import overload, TypedDict, Protocol

MouseBtn = int
Key = int

Direction = Enum('Direction', ['UP', 'DOWN', 'LEFT', 'RIGHT', 'NONE'])

@dataclass
class Position:
    x: float
    y: float
    
    def copy(self):
        return Position(self.x, self.y)
        
    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        
@dataclass
class PositionCamera:
    x: int
    y: int
    
    def copy(self):
        return PositionCamera(self.x, self.y)
        
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)
        
    def transform_position(self, position: Position) -> tuple[int, int]:
        return (int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_position_as_position(self, position: Position) -> Position:
        return Position(int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_rect(self, rect: Rect) -> Rect:
        return Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

@dataclass
class Teleport:
    pos: Position
    destination: str
    requires_boss_defeated: bool

    @overload
    def __init__(self, x: int, y: int, destination: str, requires_boss_defeated: bool = False) -> None: ...
    @overload
    def __init__(self, pos: Position, destination: str, requires_boss_defeated: bool = False) -> None: ...

    def __init__(self, *args, **kwargs):
        self.requires_boss_defeated = kwargs.get("requires_boss_defeated", False)
        if isinstance(args[0], Position):
            self.pos = args[0]
            self.destination = args[1]
            if len(args) > 2:
                self.requires_boss_defeated = args[2]
        else:
            x, y, dest = args[:3]
            self.pos = Position(x, y)
            self.destination = dest
            if len(args) > 3:
                self.requires_boss_defeated = args[3]

    def to_dict(self):
        result = {
            "x": self.pos.x // GameSettings.TILE_SIZE,
            "y": self.pos.y // GameSettings.TILE_SIZE,
            "destination": self.destination
        }
        if self.requires_boss_defeated:
            result["requires_boss_defeated"] = True
        return result

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            data["destination"],
            requires_boss_defeated=data.get("requires_boss_defeated", False)
        )
    
class Monster(TypedDict):
    name: str
    hp: int
    max_hp: int
    level: int
    attack: int  # Attack stat - affects damage dealt
    defense: int  # Defense stat - reduces damage taken
    sprite_path: str
    type: str  # Pokemon element type: Fire, Water, Ice, Wind, Light, Slash, or None
    moves: list[str]  # List of move names this Pokemon can use

class Item(TypedDict):
    name: str
    count: int
    sprite_path: str
    price: int
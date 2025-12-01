from __future__ import annotations
import pygame as pg
from typing import override
from enum import Enum

from .entity import Entity
from src.core import GameManager
from src.utils import GameSettings, Direction, Position
from src.utils.definition import Item


class NPCType(Enum):
    MERCHANT = "merchant"
    TRADER = "trader"


class NPC(Entity):
    name: str
    npc_type: NPCType
    shop_inventory: list[Item]
    interaction_range: float
    is_near_player: bool
    dialogue: str

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        name: str = "Merchant",
        npc_type: NPCType = NPCType.MERCHANT,
        shop_inventory: list[Item] | None = None,
        dialogue: str = "Welcome to my shop!",
        facing: Direction = Direction.DOWN,
        sprite_path: str = "character/ow2.png",
    ) -> None:
        super().__init__(x, y, game_manager)
        # Override the default animation with NPC-specific sprite
        from src.sprites import Animation
        self.animation = Animation(
            sprite_path, ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.animation.update_pos(self.position)

        self.name = name
        self.npc_type = npc_type
        self.shop_inventory = shop_inventory if shop_inventory else []
        self.interaction_range = GameSettings.TILE_SIZE * 1.5
        self.is_near_player = False
        self.dialogue = dialogue
        self._set_direction(facing)

    @override
    def update(self, dt: float) -> None:
        self.check_interaction_range()
        self.animation.update_pos(self.position)

    def check_interaction_range(self) -> bool:
        player = self.game_manager.player
        if player is None:
            self.is_near_player = False
            return False

        distance = self.position.distance_to(player.position)
        self.is_near_player = distance <= self.interaction_range
        return self.is_near_player

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "NPC":
        npc_type = NPCType(data.get("npc_type", "merchant"))
        facing_val = data.get("facing", "DOWN")
        facing = Direction[facing_val] if isinstance(facing_val, str) else facing_val

        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            data.get("name", "Merchant"),
            npc_type,
            data.get("shop_inventory", []),
            data.get("dialogue", "Welcome to my shop!"),
            facing,
            data.get("sprite_path", "character/ow2.png"),
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["name"] = self.name
        base["npc_type"] = self.npc_type.value
        base["shop_inventory"] = list(self.shop_inventory)
        base["dialogue"] = self.dialogue
        base["facing"] = self.direction.name
        return base

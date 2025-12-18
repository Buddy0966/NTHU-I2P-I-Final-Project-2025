from __future__ import annotations
import pygame as pg
try:
    from typing import override
except ImportError:
    from typing_extensions import override

from .entity import Entity
from src.core import GameManager
from src.utils import GameSettings, Position
from src.utils.definition import Item
from src.sprites import Sprite


class Chest(Entity):
    """Interactive chest that gives rewards to the player."""

    name: str
    opened: bool
    interaction_range: float
    is_near_player: bool
    rewards: dict[str, object]

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        name: str = "Treasure Chest",
        opened: bool = False,
        rewards: dict[str, object] | None = None,
        sprite_path: str = "ingame_ui/chest.png",
    ) -> None:
        super().__init__(x, y, game_manager)
        # Override animation with a simple sprite for the chest
        self.sprite = Sprite(
            sprite_path,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.sprite.rect.x = int(x)
        self.sprite.rect.y = int(y)

        self.name = name
        self.opened = opened
        self.interaction_range = GameSettings.TILE_SIZE * 1.5
        self.is_near_player = False

        # Rewards structure: {"items": [...], "monsters": [...], "coins": int}
        self.rewards = rewards if rewards else {
            "items": [],
            "monsters": [],
            "coins": 0
        }

    @override
    def update(self, dt: float) -> None:
        self.check_interaction_range()
        self.sprite.rect.x = int(self.position.x)
        self.sprite.rect.y = int(self.position.y)

    def check_interaction_range(self) -> bool:
        """Check if player is within interaction range."""
        player = self.game_manager.player
        if player is None:
            self.is_near_player = False
            return False

        distance = self.position.distance_to(player.position)
        self.is_near_player = distance <= self.interaction_range
        return self.is_near_player

    def open_chest(self) -> bool:
        """Open the chest and give rewards to the player. Returns True if successful."""
        if self.opened:
            return False

        bag = self.game_manager.bag

        # Add items
        for item in self.rewards.get("items", []):
            bag.add_item(
                item["name"],
                item["count"],
                item["sprite_path"],
                item.get("price", 0)
            )

        # Add monsters/Pokemon
        for monster in self.rewards.get("monsters", []):
            bag.add_monster(monster)

        # Add coins
        coins = self.rewards.get("coins", 0)
        if coins > 0:
            bag.add_item("Coins", coins, "ingame_ui/coin.png", 1)

        self.opened = True
        return True

    @override
    def draw(self, screen: pg.Surface, camera) -> None:
        """Draw the chest sprite."""
        self.sprite.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            # Draw hitbox for debugging
            rect = self.sprite.rect.copy()
            rect.x -= camera.x
            rect.y -= camera.y
            pg.draw.rect(screen, (255, 255, 0), rect, 2)

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "Chest":
        """Create a Chest from a dictionary (for loading from save file)."""
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            data.get("name", "Treasure Chest"),
            data.get("opened", False),
            data.get("rewards", {}),
            data.get("sprite_path", "ingame_ui/chest.png"),
        )

    @override
    def to_dict(self) -> dict[str, object]:
        """Convert Chest to dictionary (for saving)."""
        base: dict[str, object] = super().to_dict()
        base["name"] = self.name
        base["opened"] = self.opened
        base["rewards"] = self.rewards
        base["sprite_path"] = "ingame_ui/chest.png"
        return base

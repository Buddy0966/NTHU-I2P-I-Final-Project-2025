from __future__ import annotations
from src.utils import Logger, GameSettings, Position, Teleport
import json, os
import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.enemy_trainer import EnemyTrainer
    from src.entities.merchant_npc import NPC
    from src.data.bag import Bag

class GameManager:
    # Entities
    player: Player | None
    enemy_trainers: dict[str, list[EnemyTrainer]]
    npcs: dict[str, list["NPC"]]
    bag: "Bag"
    
    # Map properties
    current_map_key: str
    maps: dict[str, Map]
    
    # Changing Scene properties
    should_change_scene: bool
    next_map: str
    
    def __init__(self, maps: dict[str, Map], start_map: str,
                 player: Player | None,
                 enemy_trainers: dict[str, list[EnemyTrainer]],
                 npcs: dict[str, list["NPC"]] | None = None,
                 bag: Bag | None = None):

        from src.data.bag import Bag
        # Game Properties
        self.maps = maps
        self.current_map_key = start_map
        self.player = player
        self.enemy_trainers = enemy_trainers
        self.npcs = npcs if npcs is not None else {}
        self.bag = bag if bag is not None else Bag([], [])

        # Track player spawn/last-position per map (in pixels)
        # Initialize from provided maps; if a player is present use its position for current map
        self.player_spawns: dict[str, Position] = {}
        for key, m in self.maps.items():
            # copy positions to avoid shared references
            self.player_spawns[key] = m.spawn.copy()
        if self.player is not None:
            # override the current map spawn with the actual player position
            self.player_spawns[self.current_map_key] = self.player.position.copy()
        
        # Check If you should change scene
        self.should_change_scene = False
        self.next_map = ""
    # Teleport cooldown (seconds) to ignore immediate re-teleport or movement after switching
        self.teleport_cooldown = 0.0
        # Default wait time after teleport (seconds)
        self.TELEPORT_WAIT = 2.0
        # Bush encounter cooldown (seconds) to prevent immediate re-encounter after battle
        self.bush_cooldown = 0.0
        # Default wait time after bush encounter (seconds)
        self.BUSH_WAIT = 1.0

    def update(self, dt: float) -> None:
        """Update per-frame timers for the game manager."""
        if self.teleport_cooldown > 0.0:
            self.teleport_cooldown = max(0.0, self.teleport_cooldown - dt)
        if self.bush_cooldown > 0.0:
            self.bush_cooldown = max(0.0, self.bush_cooldown - dt)
        
    @property
    def current_map(self) -> Map:
        return self.maps[self.current_map_key]
        
    @property
    def current_enemy_trainers(self) -> list[EnemyTrainer]:
        return self.enemy_trainers[self.current_map_key]

    @property
    def current_npcs(self) -> list["NPC"]:
        return self.npcs.get(self.current_map_key, [])

    @property
    def current_teleporter(self) -> list[Teleport]:
        return self.maps[self.current_map_key].teleporters
    
    def switch_map(self, target: str) -> None:
        if target not in self.maps:
            Logger.warning(f"Map '{target}' not loaded; cannot switch.")
            return
        
        self.next_map = target
        self.should_change_scene = True
            
    def try_switch_map(self) -> None:
        if self.should_change_scene:
            # Save current player's last position on the current map before switching
            if self.player is not None:
                self.player_spawns[self.current_map_key] = self.player.position.copy()

            self.current_map_key = self.next_map
            self.next_map = ""
            self.should_change_scene = False
            if self.player:
                # Place player at the spawn point (or last known position) of the new map
                self.player.position = self.player_spawns.get(self.current_map_key, self.maps[self.current_map_key].spawn)
                # set a short cooldown after teleport so player won't immediately retrigger teleport
                self.teleport_cooldown = self.TELEPORT_WAIT
            
    def check_collision(self, rect: pg.Rect) -> bool:
        if self.maps[self.current_map_key].check_collision(rect):
            return True
        for entity in self.enemy_trainers[self.current_map_key]:
            if rect.colliderect(entity.animation.rect):
                return True
        for npc in self.npcs.get(self.current_map_key, []):
            if rect.colliderect(npc.animation.rect):
                return True

        return False
        
    def save(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            Logger.info(f"Game saved to {path}")
        except Exception as e:
            Logger.warning(f"Failed to save game: {e}")
             
    @classmethod
    def load(cls, path: str) -> "GameManager | None":
        if not os.path.exists(path):
            Logger.error(f"No file found: {path}, ignoring load function")
            return None

        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, object]:
        map_blocks: list[dict[str, object]] = []
        for key, m in self.maps.items():
            block = m.to_dict()
            block["enemy_trainers"] = [t.to_dict() for t in self.enemy_trainers.get(key, [])]
            block["npcs"] = [n.to_dict() for n in self.npcs.get(key, [])]
            # Persist the last-known player position for this map (in tiles)
            spawn = self.player_spawns.get(key) or m.spawn
            block["player"] = {
                "x": spawn.x / GameSettings.TILE_SIZE,
                "y": spawn.y / GameSettings.TILE_SIZE
            }
            map_blocks.append(block)
        return {
            "map": map_blocks,
            "current_map": self.current_map_key,
            "player": self.player.to_dict() if self.player is not None else None,
            "bag": self.bag.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameManager":
        from src.maps.map import Map
        from src.entities.player import Player
        from src.entities.enemy_trainer import EnemyTrainer
        from src.entities.merchant_npc import NPC
        from src.data.bag import Bag

        Logger.info("Loading maps")
        maps_data = data["map"]
        maps: dict[str, Map] = {}
        player_spawns: dict[str, Position] = {}
        trainers: dict[str, list[EnemyTrainer]] = {}
        npcs: dict[str, list[NPC]] = {}

        for entry in maps_data:
            path = entry["path"]
            maps[path] = Map.from_dict(entry)
            sp = entry.get("player")
            if sp:
                player_spawns[path] = Position(
                    sp["x"] * GameSettings.TILE_SIZE,
                    sp["y"] * GameSettings.TILE_SIZE
                )
        current_map = data["current_map"]
        gm = cls(
            maps, current_map,
            None, # Player
            trainers,
            npcs,
            bag=None
        )
        gm.current_map_key = current_map
        # attach the loaded player spawn/positions
        gm.player_spawns = player_spawns

        Logger.info("Loading enemy trainers")
        for m in data["map"]:
            raw_data = m["enemy_trainers"]
            gm.enemy_trainers[m["path"]] = [EnemyTrainer.from_dict(t, gm) for t in raw_data]

        Logger.info("Loading NPCs")
        for m in data["map"]:
            raw_data = m.get("npcs", [])
            gm.npcs[m["path"]] = [NPC.from_dict(n, gm) for n in raw_data]

        Logger.info("Loading Player")
        if data.get("player"):
            gm.player = Player.from_dict(data["player"], gm)

        Logger.info("Loading bag")
        from src.data.bag import Bag as _Bag
        gm.bag = Bag.from_dict(data.get("bag", {})) if data.get("bag") else _Bag([], [])

        return gm
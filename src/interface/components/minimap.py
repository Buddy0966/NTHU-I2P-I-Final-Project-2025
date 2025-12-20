import pygame as pg
from typing import TYPE_CHECKING

from src.utils.definition import PositionCamera

if TYPE_CHECKING:
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.trainer import Trainer
    from src.entities.npc import NPC


class Minimap:
    """
    A minimap UI component that displays a scaled-down view of the current map
    with player position indicator and optional entity markers.
    """

    def __init__(
        self,
        size: tuple[int, int] = (200, 200),
        position: tuple[int, int] = (20, 20),
        scale_factor: float = 0.1,
        border_width: int = 3,
        border_color: tuple[int, int, int] = (255, 255, 255),
        background_color: tuple[int, int, int, int] = (0, 0, 0, 180),
        show_entities: bool = True,
    ):
        """
        Initialize the minimap component.

        Args:
            size: Width and height of the minimap in pixels
            position: Top-left position on screen (x, y)
            scale_factor: How much to scale down the map (0.1 = 10% of original)
            border_width: Width of the border frame
            border_color: RGB color of the border
            background_color: RGBA color of the minimap background
            show_entities: Whether to show NPCs and trainers on minimap
        """
        self.size = size
        self.position = position
        self.scale_factor = scale_factor
        self.border_width = border_width
        self.border_color = border_color
        self.background_color = background_color
        self.show_entities = show_entities

        # Cache for scaled map surface
        self._cached_map_surface: pg.Surface | None = None
        self._current_map_path: str | None = None

        # Create base surfaces
        self.surface = pg.Surface(size)
        self.border_surface = pg.Surface(
            (size[0] + border_width * 2, size[1] + border_width * 2)
        )

    def update(self, dt: float) -> None:
        """Update the minimap (placeholder for future features like pulsing)."""
        pass

    def draw(
        self,
        screen: pg.Surface,
        current_map: "Map",
        player: "Player",
        trainers: list["Trainer"] = None,
        npcs: list["NPC"] = None,
        online_players: list[dict] = None,
    ) -> None:
        """
        Draw the minimap to the screen.

        Args:
            screen: The main game screen surface
            current_map: The current map being displayed
            player: The player entity
            trainers: List of trainer entities (optional)
            npcs: List of NPC entities (optional)
            online_players: List of online player data dictionaries (optional)
        """
        # Check if we need to regenerate the cached map surface
        if (self._cached_map_surface is None or
            self._current_map_path != current_map.path_name):
            self._generate_map_surface(current_map)
            self._current_map_path = current_map.path_name

        # Clear the minimap surface with background
        self.surface.fill(self.background_color[:3])
        if len(self.background_color) > 3:
            self.surface.set_alpha(self.background_color[3])

        # Calculate viewport based on player position and camera
        camera = player.camera
        viewport_info = self._draw_map_viewport(current_map, camera)

        # Draw entities if enabled
        if self.show_entities:
            if trainers:
                self._draw_entities(trainers, camera, viewport_info, (255, 100, 100))  # Red for trainers
            if npcs:
                self._draw_entities(npcs, camera, viewport_info, (100, 255, 100))  # Green for NPCs
            if online_players:
                self._draw_online_players(online_players, camera, viewport_info, current_map)

        # Draw player indicator (always on top)
        self._draw_player(player, camera, viewport_info)

        # Draw border
        self.border_surface.fill(self.border_color)
        self.border_surface.blit(
            self.surface,
            (self.border_width, self.border_width)
        )

        # Blit to screen
        screen.blit(self.border_surface, self.position)

    def _generate_map_surface(self, current_map: "Map") -> None:
        """
        Generate a scaled-down version of the entire map.

        Args:
            current_map: The map to render
        """
        map_surface = current_map._surface

        # Calculate scaled dimensions
        scaled_width = int(map_surface.get_width() * self.scale_factor)
        scaled_height = int(map_surface.get_height() * self.scale_factor)

        # Scale down the map surface
        self._cached_map_surface = pg.transform.smoothscale(
            map_surface,
            (scaled_width, scaled_height)
        )

    def _draw_map_viewport(self, current_map: "Map", camera: PositionCamera) -> dict:
        """
        Draw the visible portion of the map to the minimap.

        Args:
            current_map: The current map
            camera: The camera transformation

        Returns:
            Dictionary with viewport info: source_x, source_y, dest_x, dest_y
        """
        if self._cached_map_surface is None:
            return {"source_x": 0, "source_y": 0, "dest_x": 0, "dest_y": 0}

        # Calculate the center offset to show the area around the player
        map_width = self._cached_map_surface.get_width()
        map_height = self._cached_map_surface.get_height()

        # Calculate camera center in scaled map coordinates
        screen_width, screen_height = pg.display.get_surface().get_size()
        center_x = (camera.x + screen_width / 2) * self.scale_factor
        center_y = (camera.y + screen_height / 2) * self.scale_factor

        # Calculate the source rectangle (what part of the scaled map to show)
        half_width = self.size[0] / 2
        half_height = self.size[1] / 2

        # Calculate desired source rectangle position (centered on player)
        desired_source_x = center_x - half_width
        desired_source_y = center_y - half_height

        # Clamp to map boundaries
        source_x = max(0, min(desired_source_x, map_width - self.size[0]))
        source_y = max(0, min(desired_source_y, map_height - self.size[1]))

        # Handle small maps (smaller than minimap size)
        if map_width < self.size[0]:
            dest_x = (self.size[0] - map_width) / 2
            source_x = 0
            width = map_width
        else:
            dest_x = 0
            width = self.size[0]

        if map_height < self.size[1]:
            dest_y = (self.size[1] - map_height) / 2
            source_y = 0
            height = map_height
        else:
            dest_y = 0
            height = self.size[1]

        # Blit the visible portion
        source_rect = pg.Rect(int(source_x), int(source_y), int(width), int(height))
        self.surface.blit(
            self._cached_map_surface,
            (int(dest_x), int(dest_y)),
            source_rect
        )

        # Return viewport info for correct player/entity positioning
        return {
            "source_x": source_x,
            "source_y": source_y,
            "dest_x": dest_x,
            "dest_y": dest_y,
            "center_x": center_x,
            "center_y": center_y
        }

    def _draw_player(self, player: "Player", camera: PositionCamera, viewport_info: dict) -> None:
        """
        Draw the player indicator on the minimap.

        Args:
            player: The player entity
            camera: The camera transformation
            viewport_info: Viewport information from _draw_map_viewport
        """
        # Calculate player position on minimap based on viewport
        # Player's actual position in scaled coordinates
        player_scaled_x = viewport_info["center_x"]
        player_scaled_y = viewport_info["center_y"]

        # Convert to minimap coordinates accounting for viewport offset
        center_x = viewport_info["dest_x"] + (player_scaled_x - viewport_info["source_x"])
        center_y = viewport_info["dest_y"] + (player_scaled_y - viewport_info["source_y"])

        # Draw a triangle pointing in the player's direction
        direction = player.direction
        size = 6

        # Define triangle points based on direction
        if direction.name == "DOWN":
            points = [
                (center_x, center_y + size),
                (center_x - size, center_y - size),
                (center_x + size, center_y - size),
            ]
        elif direction.name == "UP":
            points = [
                (center_x, center_y - size),
                (center_x - size, center_y + size),
                (center_x + size, center_y + size),
            ]
        elif direction.name == "LEFT":
            points = [
                (center_x - size, center_y),
                (center_x + size, center_y - size),
                (center_x + size, center_y + size),
            ]
        elif direction.name == "RIGHT":
            points = [
                (center_x + size, center_y),
                (center_x - size, center_y - size),
                (center_x - size, center_y + size),
            ]
        else:
            # Default to circle if direction is unknown
            pg.draw.circle(self.surface, (255, 255, 0), (int(center_x), int(center_y)), size)
            return

        # Draw triangle with outline
        pg.draw.polygon(self.surface, (0, 0, 0), points, 2)  # Black outline
        pg.draw.polygon(self.surface, (255, 255, 0), points)  # Yellow fill

    def _draw_entities(
        self,
        entities: list,
        camera: PositionCamera,
        viewport_info: dict,
        color: tuple[int, int, int]
    ) -> None:
        """
        Draw entity markers on the minimap.

        Args:
            entities: List of entities to draw
            camera: The camera transformation
            viewport_info: Viewport information from _draw_map_viewport
            color: RGB color for the entity markers
        """
        for entity in entities:
            # Get entity position from animation rect
            entity_x = entity.animation.rect.centerx
            entity_y = entity.animation.rect.centery

            # Convert entity position to scaled map coordinates
            entity_scaled_x = entity_x * self.scale_factor
            entity_scaled_y = entity_y * self.scale_factor

            # Convert to minimap coordinates accounting for viewport offset
            minimap_x = viewport_info["dest_x"] + (entity_scaled_x - viewport_info["source_x"])
            minimap_y = viewport_info["dest_y"] + (entity_scaled_y - viewport_info["source_y"])

            # Only draw if within minimap bounds
            if 0 <= minimap_x < self.size[0] and 0 <= minimap_y < self.size[1]:
                # Draw small circle for entity
                pg.draw.circle(
                    self.surface,
                    (0, 0, 0),
                    (int(minimap_x), int(minimap_y)),
                    4,
                    1  # Outline
                )
                pg.draw.circle(
                    self.surface,
                    color,
                    (int(minimap_x), int(minimap_y)),
                    3
                )

    def _draw_online_players(
        self,
        online_players: list[dict],
        camera: PositionCamera,
        viewport_info: dict,
        current_map: "Map"
    ) -> None:
        """
        Draw online player markers on the minimap.

        Args:
            online_players: List of online player data dictionaries
            camera: The camera transformation
            viewport_info: Viewport information from _draw_map_viewport
            current_map: The current map
        """
        for player_data in online_players:
            # Only draw players on the same map
            if player_data.get("map") != current_map.path_name:
                continue

            # Get player position from data
            player_x = player_data.get("x", 0)
            player_y = player_data.get("y", 0)

            # Convert player position to scaled map coordinates
            player_scaled_x = player_x * self.scale_factor
            player_scaled_y = player_y * self.scale_factor

            # Convert to minimap coordinates accounting for viewport offset
            minimap_x = viewport_info["dest_x"] + (player_scaled_x - viewport_info["source_x"])
            minimap_y = viewport_info["dest_y"] + (player_scaled_y - viewport_info["source_y"])

            # Only draw if within minimap bounds
            if 0 <= minimap_x < self.size[0] and 0 <= minimap_y < self.size[1]:
                # Draw small triangle for online player (cyan color)
                size = 4
                # Draw outline
                pg.draw.circle(
                    self.surface,
                    (0, 0, 0),
                    (int(minimap_x), int(minimap_y)),
                    size + 1,
                    1  # Outline
                )
                # Draw filled circle
                pg.draw.circle(
                    self.surface,
                    (0, 255, 255),  # Cyan for online players
                    (int(minimap_x), int(minimap_y)),
                    size
                )

"""Pathfinding utilities using BFS algorithm"""
from __future__ import annotations
import pygame as pg
from collections import deque
from typing import Optional
from src.utils import Position, GameSettings

class Pathfinder:
    """BFS-based pathfinding for navigation"""

    @staticmethod
    def find_path(
        start: Position,
        goal: Position,
        collision_map: list[pg.Rect],
        map_width: int,
        map_height: int
    ) -> Optional[list[Position]]:
        """
        Find a path from start to goal using BFS algorithm.

        Args:
            start: Starting position in pixels
            goal: Goal position in pixels
            collision_map: List of collision rectangles
            map_width: Map width in tiles
            map_height: Map height in tiles

        Returns:
            List of positions forming the path, or None if no path found
        """
        # Convert pixel positions to tile coordinates
        start_tile = (
            int(start.x // GameSettings.TILE_SIZE),
            int(start.y // GameSettings.TILE_SIZE)
        )
        goal_tile = (
            int(goal.x // GameSettings.TILE_SIZE),
            int(goal.y // GameSettings.TILE_SIZE)
        )

        # BFS setup
        queue = deque([(start_tile, [start_tile])])
        visited = {start_tile}

        # Directions: up, down, left, right (4-directional for smoother paths)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            current, path = queue.popleft()

            # Check if we reached the goal
            if current == goal_tile:
                # Convert tile path back to pixel positions
                pixel_path = []
                for tile_x, tile_y in path:
                    # Center of tile
                    px = tile_x * GameSettings.TILE_SIZE + GameSettings.TILE_SIZE // 2
                    py = tile_y * GameSettings.TILE_SIZE + GameSettings.TILE_SIZE // 2
                    pixel_path.append(Position(px, py))
                return pixel_path

            # Explore neighbors
            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy

                # Check bounds
                if not (0 <= nx < map_width and 0 <= ny < map_height):
                    continue

                # Check if already visited
                if (nx, ny) in visited:
                    continue

                # Check collision
                tile_rect = pg.Rect(
                    nx * GameSettings.TILE_SIZE,
                    ny * GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE,
                    GameSettings.TILE_SIZE
                )

                # Skip if tile collides with any obstacle
                has_collision = any(tile_rect.colliderect(r) for r in collision_map)
                if has_collision:
                    continue

                # Add to queue
                visited.add((nx, ny))
                new_path = path + [(nx, ny)]
                queue.append(((nx, ny), new_path))

        # No path found
        return None

    @staticmethod
    def simplify_path(path: list[Position], threshold: float = 2.0) -> list[Position]:
        """
        Simplify path by keeping only turning points (rectangular paths only).
        This creates strictly horizontal and vertical line segments.

        Args:
            path: Original path
            threshold: Not used for rectangular simplification

        Returns:
            Simplified path with only rectangular segments
        """
        if len(path) <= 2:
            return path

        simplified = [path[0]]

        i = 0
        while i < len(path) - 1:
            current = path[i]

            # Find the longest straight line (horizontal or vertical) from current position
            j = i + 1

            # Determine initial direction (horizontal or vertical)
            if abs(path[j].x - current.x) > abs(path[j].y - current.y):
                # Moving horizontally
                direction = "horizontal"
            else:
                # Moving vertically
                direction = "vertical"

            # Extend as far as possible in this direction
            last_valid = j
            for k in range(j + 1, len(path)):
                if direction == "horizontal":
                    # Check if still moving horizontally (same y coordinate)
                    if abs(path[k].y - current.y) < GameSettings.TILE_SIZE * 0.5:
                        last_valid = k
                    else:
                        break
                else:  # vertical
                    # Check if still moving vertically (same x coordinate)
                    if abs(path[k].x - current.x) < GameSettings.TILE_SIZE * 0.5:
                        last_valid = k
                    else:
                        break

            # Add the last valid point in this direction
            if last_valid != i:
                simplified.append(path[last_valid])
                i = last_valid
            else:
                # Couldn't extend, move to next point
                simplified.append(path[j])
                i = j

        return simplified

    @staticmethod
    def _point_to_line_distance(point: Position, line_start: Position, line_end: Position) -> float:
        """Calculate perpendicular distance from point to line segment"""
        # Vector from line_start to line_end
        dx = line_end.x - line_start.x
        dy = line_end.y - line_start.y

        # Handle zero-length line
        if dx == 0 and dy == 0:
            return ((point.x - line_start.x) ** 2 + (point.y - line_start.y) ** 2) ** 0.5

        # Parameter t for projection onto line
        t = max(0, min(1, ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (dx * dx + dy * dy)))

        # Closest point on line segment
        closest_x = line_start.x + t * dx
        closest_y = line_start.y + t * dy

        # Distance to closest point
        return ((point.x - closest_x) ** 2 + (point.y - closest_y) ** 2) ** 0.5

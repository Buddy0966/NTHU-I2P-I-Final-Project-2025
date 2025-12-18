"""Arrow path visualization for navigation"""
from __future__ import annotations
import pygame as pg
import math
from src.utils import Position, PositionCamera, GameSettings
from src.sprites import Sprite

class ArrowPath:
    """Renders an arrow path for navigation"""

    def __init__(self, path: list[Position]):
        """
        Initialize arrow path renderer.

        Args:
            path: List of positions forming the path
        """
        self.path = path
        self.original_path = path.copy()  # Keep original for reference
        self.consumed_up_to_index = 0  # Track how much of the path has been consumed
        self.arrow_sprite = None

        # Try to load arrow sprite (300% bigger = 96x96 pixels)
        try:
            self.arrow_sprite = Sprite("ingame_ui/arrow.png", (96, 96))
        except Exception as e:
            print(f"Warning: Could not load arrow sprite: {e}")

        # Animation parameters
        self.animation_time = 0.0
        self.arrow_spacing = 2.0 * GameSettings.TILE_SIZE  # Distance between arrows
        self.pulse_speed = 2.0  # Speed of pulsing animation
        self.consumption_distance = GameSettings.TILE_SIZE * 1.5  # Distance to consume path

    def update(self, dt: float, player_pos: Position = None) -> None:
        """
        Update animation and check for path consumption.

        Args:
            dt: Delta time
            player_pos: Current player position (for path consumption)
        """
        self.animation_time += dt * self.pulse_speed

        # Check if player is consuming the path
        if player_pos and len(self.path) > 1:
            self._consume_path(player_pos)

    def _consume_path(self, player_pos: Position) -> None:
        """
        Remove path segments that the player has walked through.

        Args:
            player_pos: Current player position
        """
        import math

        # Check each segment from the start
        segments_to_remove = 0

        for i in range(len(self.path) - 1):
            p1 = self.path[i]
            p2 = self.path[i + 1]

            # Check if player is near this segment
            distance = self._point_to_segment_distance(player_pos, p1, p2)

            if distance < self.consumption_distance:
                # Player is on or near this segment
                # Check if player has passed beyond the segment start
                # Calculate progress along the segment
                segment_dx = p2.x - p1.x
                segment_dy = p2.y - p1.y
                segment_length_sq = segment_dx * segment_dx + segment_dy * segment_dy

                if segment_length_sq > 0:
                    # Project player position onto segment
                    player_dx = player_pos.x - p1.x
                    player_dy = player_pos.y - p1.y
                    t = (player_dx * segment_dx + player_dy * segment_dy) / segment_length_sq

                    # If player is past the start of this segment (t > 0.3), consume previous segments
                    if t > 0.3:
                        segments_to_remove = i + 1
            else:
                # If we're not near this segment anymore, stop checking
                break

        # Remove consumed path segments
        if segments_to_remove > 0 and segments_to_remove < len(self.path):
            self.path = self.path[segments_to_remove:]
            self.consumed_up_to_index += segments_to_remove

    def _point_to_segment_distance(self, point: Position, seg_start: Position, seg_end: Position) -> float:
        """Calculate distance from point to line segment"""
        import math

        # Vector from seg_start to seg_end
        dx = seg_end.x - seg_start.x
        dy = seg_end.y - seg_start.y

        # Handle zero-length segment
        if dx == 0 and dy == 0:
            return math.sqrt((point.x - seg_start.x) ** 2 + (point.y - seg_start.y) ** 2)

        # Parameter t for projection onto segment
        t = max(0, min(1, ((point.x - seg_start.x) * dx + (point.y - seg_start.y) * dy) / (dx * dx + dy * dy)))

        # Closest point on segment
        closest_x = seg_start.x + t * dx
        closest_y = seg_start.y + t * dy

        # Distance to closest point
        return math.sqrt((point.x - closest_x) ** 2 + (point.y - closest_y) ** 2)

    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        """
        Draw the arrow path on screen.

        Args:
            screen: Pygame surface to draw on
            camera: Camera for transforming world to screen coordinates
        """
        if not self.path or len(self.path) < 2:
            return

        # Draw path line
        self._draw_path_line(screen, camera)

        # Draw arrows along the path
        if self.arrow_sprite:
            self._draw_arrows(screen, camera)

    def _draw_path_line(self, screen: pg.Surface, camera: PositionCamera) -> None:
        """Draw a line connecting the path points"""
        screen_points = []
        for pos in self.path:
            screen_pos = camera.transform_position(pos)
            screen_points.append(screen_pos)  # transform_position returns a tuple

        if len(screen_points) >= 2:
            # Draw the path with a glowing effect
            # Outer glow
            pg.draw.lines(screen, (100, 200, 255, 100), False, screen_points, 8)
            # Main line
            pg.draw.lines(screen, (50, 150, 255), False, screen_points, 4)
            # Inner highlight
            pg.draw.lines(screen, (150, 220, 255), False, screen_points, 2)

    def _draw_arrows(self, screen: pg.Surface, camera: PositionCamera) -> None:
        """Draw arrows along the path"""
        if len(self.path) < 2:
            return

        # Calculate positions along the path for arrows
        total_length = self._calculate_path_length()
        num_arrows = max(1, int(total_length / self.arrow_spacing))

        for i in range(num_arrows):
            # Calculate position along path (0.0 to 1.0)
            t = (i + 1) / (num_arrows + 1)
            pos, angle = self._get_position_and_angle_at(t)

            if pos is None:
                continue

            # Transform to screen coordinates
            screen_pos = camera.transform_position(pos)  # Returns a tuple (x, y)

            # Pulsing scale effect (base size is now 96 instead of 32)
            pulse = 0.85 + 0.15 * math.sin(self.animation_time + i * 0.5)
            arrow_size = int(96 * pulse)

            # Rotate arrow to point in direction of movement
            rotated_sprite = pg.transform.rotate(self.arrow_sprite.image, -angle)
            scaled_sprite = pg.transform.scale(rotated_sprite, (arrow_size, arrow_size))

            # Draw arrow centered at position
            arrow_rect = scaled_sprite.get_rect(center=screen_pos)
            screen.blit(scaled_sprite, arrow_rect)

    def _calculate_path_length(self) -> float:
        """Calculate total length of the path"""
        total = 0.0
        for i in range(len(self.path) - 1):
            p1 = self.path[i]
            p2 = self.path[i + 1]
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            total += math.sqrt(dx * dx + dy * dy)
        return total

    def _get_position_and_angle_at(self, t: float) -> tuple[Position | None, float]:
        """
        Get position and angle at normalized distance t along the path.

        Args:
            t: Normalized distance (0.0 to 1.0)

        Returns:
            Tuple of (position, angle_in_degrees) or (None, 0) if invalid
        """
        if not self.path or len(self.path) < 2:
            return None, 0.0

        # Calculate target distance along path
        total_length = self._calculate_path_length()
        target_distance = t * total_length

        # Walk along path to find the segment containing target distance
        current_distance = 0.0
        for i in range(len(self.path) - 1):
            p1 = self.path[i]
            p2 = self.path[i + 1]

            dx = p2.x - p1.x
            dy = p2.y - p1.y
            segment_length = math.sqrt(dx * dx + dy * dy)

            if current_distance + segment_length >= target_distance:
                # Target is in this segment
                segment_t = (target_distance - current_distance) / segment_length if segment_length > 0 else 0
                pos_x = p1.x + segment_t * dx
                pos_y = p1.y + segment_t * dy

                # Calculate angle (in degrees, 0 = right, increases counter-clockwise)
                # In Pygame, Y increases downward, so we use dy directly (not -dy)
                angle = math.degrees(math.atan2(dy, dx))

                return Position(pos_x, pos_y), angle

            current_distance += segment_length

        # Fallback to last point
        p1 = self.path[-2]
        p2 = self.path[-1]
        angle = math.degrees(math.atan2(p2.y - p1.y, p2.x - p1.x))
        return self.path[-1], angle

    def clear(self) -> None:
        """Clear the current path"""
        self.path = []

    def is_complete(self) -> bool:
        """Check if the path has been completely consumed"""
        return len(self.path) <= 1

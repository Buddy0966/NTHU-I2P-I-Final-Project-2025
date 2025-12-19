"""Arrow path visualization for navigation"""
from __future__ import annotations
import pygame as pg
import math
from src.utils import Position, PositionCamera, GameSettings
from src.sprites import Sprite

class ArrowPath:
    """Renders an arrow path for navigation"""

    def __init__(self, full_path: list[Position], simplified_path: list[Position] = None):
        """
        Initialize arrow path renderer.

        Args:
            full_path: Complete list of positions (every tile on the path)
            simplified_path: Simplified path with only turning points (for direction calculation)
                           If None, uses full_path for both
        """
        self.full_path = full_path
        self.simplified_path = simplified_path if simplified_path else full_path
        self.path = self.simplified_path  # For compatibility with existing code
        self.original_path = full_path.copy()  # Keep original for reference
        self.consumed_up_to_index = 0  # Track how much of the path has been consumed
        self.arrow_sprite = None

        # Try to load arrow sprite (300% bigger = 96x96 pixels)
        try:
            self.arrow_sprite = Sprite("ingame_ui/arrow.png", (96, 96))
        except Exception as e:
            print(f"Warning: Could not load arrow sprite: {e}")

        # Animation parameters
        self.animation_time = 0.0
        self.pulse_speed = 2.0  # Speed of pulsing animation
        self.consumption_distance = GameSettings.TILE_SIZE * 0.7  # Distance to consume each arrow

        # Create arrow positions at each tile in the path
        self.arrows = []  # List of dict with 'pos', 'angle', 'visible'
        self._create_tile_arrows()

    def _create_tile_arrows(self) -> None:
        """Create an arrow for each tile in the full path"""
        if len(self.full_path) < 2:
            return

        # For each position in the full path (except the last one which is the destination)
        for i in range(len(self.full_path) - 1):
            current = self.full_path[i]
            
            # Find which segment of simplified_path this tile belongs to
            # This determines the direction the arrow should point
            angle = self._get_angle_for_position(current)

            self.arrows.append({
                'pos': current,
                'angle': angle,
                'visible': True
            })

    def _get_angle_for_position(self, pos: Position) -> float:
        """
        Get the arrow angle for a given position based on simplified path.
        
        Args:
            pos: Position to get angle for
            
        Returns:
            Angle in degrees for the arrow at this position
        """
        # Find which segment of simplified_path this position is closest to
        min_distance = float('inf')
        best_segment_idx = 0
        
        for i in range(len(self.simplified_path) - 1):
            seg_start = self.simplified_path[i]
            seg_end = self.simplified_path[i + 1]
            
            # Calculate distance from position to this segment
            dist = self._point_to_segment_distance(pos, seg_start, seg_end)
            
            if dist < min_distance:
                min_distance = dist
                best_segment_idx = i
        
        # Calculate angle based on the direction of this segment
        seg_start = self.simplified_path[best_segment_idx]
        seg_end = self.simplified_path[best_segment_idx + 1]
        
        dx = seg_end.x - seg_start.x
        dy = seg_end.y - seg_start.y
        
        # Calculate angle (in degrees)
        # atan2(dy, dx) gives angle where 0=right, 90=down
        # Our arrow sprite points up, so we need to add 90 degrees
        angle = math.degrees(math.atan2(dy, dx)) + 90
        
        return angle

    def update(self, dt: float, player_pos: Position = None) -> None:
        """
        Update animation and check for arrow consumption.

        Args:
            dt: Delta time
            player_pos: Current player position (for arrow consumption)
        """
        self.animation_time += dt * self.pulse_speed

        # Check if player is consuming arrows
        if player_pos:
            self._consume_arrows(player_pos)

    def _consume_arrows(self, player_pos: Position) -> None:
        """
        Hide arrows that the player has touched (like collecting coins).

        Args:
            player_pos: Current player position
        """
        # Check each visible arrow
        for arrow in self.arrows:
            if not arrow['visible']:
                continue

            # Calculate distance from player to arrow
            arrow_pos = arrow['pos']
            dx = player_pos.x - arrow_pos.x
            dy = player_pos.y - arrow_pos.y
            distance = math.sqrt(dx * dx + dy * dy)

            # If player is close enough to the arrow, consume it
            if distance < self.consumption_distance:
                arrow['visible'] = False

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

        # Draw arrows along the path (removed path line drawing)
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
        """Draw arrows at each tile position"""
        # Draw each visible arrow
        for i, arrow in enumerate(self.arrows):
            if not arrow['visible']:
                continue

            pos = arrow['pos']
            angle = arrow['angle']

            # Transform to screen coordinates
            screen_pos = camera.transform_position(pos)  # Returns a tuple (x, y)

            # Pulsing scale effect (base size is now 96 instead of 32)
            pulse = 0.85 + 0.15 * math.sin(self.animation_time + i * 0.5)
            arrow_size = int(96 * pulse)

            # Rotate arrow to point in direction of movement
            # Note: We need to rotate by -angle because pygame rotates counter-clockwise
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
        """Check if all arrows have been consumed"""
        return all(not arrow['visible'] for arrow in self.arrows)

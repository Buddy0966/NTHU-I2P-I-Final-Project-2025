import pygame as pg
from src.utils import Position, PositionCamera, GameSettings, load_img


class PortalSprite:
    """Animated portal sprite using 3x3 sprite sheet"""

    def __init__(self, x: int, y: int, size: int = 48):
        """
        Initialize portal sprite with 3x3 frame animation

        Args:
            x: X position in pixels
            y: Y position in pixels
            size: Size of the portal in pixels
        """
        self.x = x
        self.y = y
        self.size = size

        # Load the sprite sheet (3x3 grid = 9 frames)
        sprite_sheet = load_img("ingame_ui/portal.png")
        sheet_w, sheet_h = sprite_sheet.get_size()

        # Calculate frame dimensions (3x3 grid)
        frame_w = sheet_w // 3
        frame_h = sheet_h // 3

        # Extract all 9 frames from the sprite sheet
        self.frames = []
        for row in range(3):
            for col in range(3):
                # Extract frame
                frame_rect = pg.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                frame = sprite_sheet.subsurface(frame_rect)
                # Scale to desired size
                scaled_frame = pg.transform.smoothscale(frame, (size, size))
                self.frames.append(scaled_frame)

        # Animation state
        self.current_frame = 0
        self.animation_timer = 0.0
        self.frame_duration = 0.1  # 100ms per frame, adjust for speed

    def update(self, dt: float):
        """Update portal animation - cycle through frames"""
        # Update frame animation
        self.animation_timer += dt
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen: pg.Surface, camera: PositionCamera):
        """Draw the animated portal"""
        # Get screen position
        screen_pos = camera.transform_position(Position(self.x, self.y))

        # Draw current frame (no glow effect)
        screen.blit(self.frames[self.current_frame], screen_pos)

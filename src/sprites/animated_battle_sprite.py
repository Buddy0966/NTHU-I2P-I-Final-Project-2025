import pygame as pg
from src.core.services import resource_manager
from typing import Optional

class AnimatedBattleSprite:
    """
    Handles battle sprite animations with separate idle and attack sprite sheets.
    Each sprite sheet contains 4 frames arranged horizontally.
    """

    def __init__(self, base_path: str, size: tuple[int, int], frames: int = 4, loop_speed: float = 0.8):
        """
        Args:
            base_path: Path without extension (e.g., "sprites/sprite1")
            size: Rendered size (width, height)
            frames: Number of frames in sprite sheet (default 4)
            loop_speed: Animation loop duration in seconds
        """
        self.size = size
        self.frames = frames
        self.loop_speed = loop_speed
        self.accumulator = 0.0
        self.current_animation = "idle"

        # Load and split sprite sheets
        self.animations = {}
        self._load_animation(f"{base_path}_idle", "idle")
        self._load_animation(f"{base_path}_attack", "attack")

        # If attack animation doesn't exist, use idle as fallback
        if "attack" not in self.animations:
            self.animations["attack"] = self.animations["idle"]

    def _load_animation(self, path: str, anim_name: str):
        """Load a sprite sheet and split it into frames"""
        try:
            sheet = resource_manager.get_image(path + ".png")
            sheet_width = sheet.get_width()
            frame_width = sheet_width // self.frames
            frame_height = sheet.get_height()

            frame_list = []
            for i in range(self.frames):
                # Extract frame from sheet
                frame_rect = pg.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = sheet.subsurface(frame_rect)
                # Scale to desired size
                scaled_frame = pg.transform.smoothscale(frame, self.size)
                frame_list.append(scaled_frame)

            self.animations[anim_name] = frame_list
        except Exception as e:
            # If loading fails, create a placeholder
            print(f"Warning: Could not load {path}.png - {e}")
            if anim_name == "idle":
                # Create a simple colored rectangle as fallback
                placeholder = pg.Surface(self.size)
                placeholder.fill((200, 200, 200))
                self.animations[anim_name] = [placeholder]

    def switch_animation(self, anim_name: str):
        """Switch to a different animation (idle/attack)"""
        if anim_name in self.animations:
            self.current_animation = anim_name
            self.accumulator = 0.0  # Reset animation

    def update(self, dt: float):
        """Update animation timer"""
        self.accumulator = (self.accumulator + dt) % self.loop_speed

    def get_current_frame(self) -> pg.Surface:
        """Get the current frame to render"""
        frames = self.animations.get(self.current_animation, self.animations["idle"])

        # Calculate which frame to show based on time
        frame_index = int((self.accumulator / self.loop_speed) * len(frames))
        frame_index = min(frame_index, len(frames) - 1)  # Clamp to valid range

        return frames[frame_index]

    def draw(self, screen: pg.Surface, position: tuple[int, int]):
        """Draw the current frame at the given position"""
        frame = self.get_current_frame()
        screen.blit(frame, position)

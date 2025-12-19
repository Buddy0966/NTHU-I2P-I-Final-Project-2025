"""
Attack Animation Sprite for Battle Effects
"""
import pygame as pg
from src.core.managers.resource_manager import ResourceManager


class AttackAnimation:
    """
    Handles attack effect animations during battle
    """

    def __init__(self, animation_path: str | None, position: tuple[int, int], duration: float = 0.5):
        """
        Initialize attack animation

        Args:
            animation_path: Path to the attack animation image (e.g., "attack/attack1.png")
            position: (x, y) position to display the animation
            duration: How long the animation should display in seconds
        """
        self.position = position
        self.duration = duration
        self.timer = 0.0
        self.active = True
        self.image = None
        self.original_image = None

        if animation_path:
            try:
                self.original_image = ResourceManager().get_image(animation_path)
                # Scale the attack animation to a bigger size (250x250, much larger!)
                self.image = pg.transform.smoothscale(self.original_image, (250, 250))
            except Exception as e:
                print(f"Failed to load attack animation: {animation_path}. Error: {e}")
                self.image = None
                self.original_image = None

    def update(self, dt: float) -> None:
        """Update the animation timer"""
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen: pg.Surface) -> None:
        """Draw the attack animation with enhanced effects"""
        if self.active and self.image and self.original_image:
            progress = self.timer / self.duration

            # Dynamic scale effect: start small, grow to max, then slightly shrink
            if progress < 0.3:
                # Fast grow in
                scale_factor = 0.5 + (progress / 0.3) * 0.7  # 0.5 -> 1.2
            elif progress < 0.7:
                # Stay at max size
                scale_factor = 1.2
            else:
                # Slight shrink out
                scale_factor = 1.2 - ((progress - 0.7) / 0.3) * 0.2  # 1.2 -> 1.0

            # Calculate scaled size
            scaled_size = int(250 * scale_factor)
            scaled_image = pg.transform.smoothscale(self.original_image, (scaled_size, scaled_size))

            # Calculate position to center the animation
            x = self.position[0] - scaled_image.get_width() // 2
            y = self.position[1] - scaled_image.get_height() // 2

            # Enhanced fade effect
            if progress < 0.15:
                # Quick fade in
                alpha = int(255 * (progress / 0.15))
            elif progress > 0.85:
                # Fade out
                alpha = int(255 * ((1.0 - progress) / 0.15))
            else:
                alpha = 255

            # Apply alpha
            temp_image = scaled_image.copy()
            temp_image.set_alpha(alpha)

            # Optional: Add a subtle glow effect for extra impact
            if progress < 0.5:
                # Draw a slightly larger, semi-transparent version behind for glow
                glow_size = int(scaled_size * 1.15)
                glow_image = pg.transform.smoothscale(self.original_image, (glow_size, glow_size))
                glow_alpha = int(alpha * 0.3)
                glow_image.set_alpha(glow_alpha)
                glow_x = self.position[0] - glow_image.get_width() // 2
                glow_y = self.position[1] - glow_image.get_height() // 2
                screen.blit(glow_image, (glow_x, glow_y))

            screen.blit(temp_image, (x, y))

    def is_finished(self) -> bool:
        """Check if animation is finished"""
        return not self.active

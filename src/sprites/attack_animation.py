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

        if animation_path:
            try:
                self.image = ResourceManager().get_image(animation_path)
                # Scale the attack animation to a reasonable size
                self.image = pg.transform.scale(self.image, (150, 150))
            except Exception as e:
                print(f"Failed to load attack animation: {animation_path}. Error: {e}")
                self.image = None

    def update(self, dt: float) -> None:
        """Update the animation timer"""
        if self.active:
            self.timer += dt
            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen: pg.Surface) -> None:
        """Draw the attack animation"""
        if self.active and self.image:
            # Calculate position to center the animation
            x = self.position[0] - self.image.get_width() // 2
            y = self.position[1] - self.image.get_height() // 2

            # Fade effect based on progress
            progress = self.timer / self.duration
            if progress < 0.2:
                # Fade in
                alpha = int(255 * (progress / 0.2))
            elif progress > 0.8:
                # Fade out
                alpha = int(255 * ((1.0 - progress) / 0.2))
            else:
                alpha = 255

            # Apply alpha
            temp_image = self.image.copy()
            temp_image.set_alpha(alpha)
            screen.blit(temp_image, (x, y))

    def is_finished(self) -> bool:
        """Check if animation is finished"""
        return not self.active

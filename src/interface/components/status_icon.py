"""
Status Icon Component - Displays Pokemon status effects with beautiful animations
"""
from __future__ import annotations
import pygame as pg
import math
from src.utils.pokemon_data import STATUS_EFFECTS


class StatusIcon:
    """Beautiful animated status effect icon"""

    def __init__(self, status: str | None, x: int, y: int, size: int = 40):
        """
        Initialize status icon

        Args:
            status: Status effect name ("poison", "paralysis", "burn", "sleep", or None)
            x: X position
            y: Y position
            size: Icon size in pixels
        """
        self.status = status
        self.x = x
        self.y = y
        self.size = size
        self._animation_timer = 0.0
        self._pulse_offset = 0.0

        # Load font for emoji icons
        try:
            self._font = pg.font.Font('assets/fonts/Minecraft.ttf', size - 8)
        except:
            self._font = pg.font.SysFont('segoeuiemoji', size - 8)  # Fallback for emoji support

    def update(self, dt: float) -> None:
        """Update animation"""
        self._animation_timer += dt
        # Pulse animation (breathing effect)
        self._pulse_offset = math.sin(self._animation_timer * 3.0) * 0.15

    def draw(self, screen: pg.Surface) -> None:
        """Draw the status icon with beautiful effects"""
        if not self.status or self.status not in STATUS_EFFECTS:
            return

        status_data = STATUS_EFFECTS[self.status]
        color = status_data["color"]
        icon = status_data["icon"]

        # Calculate pulse size
        pulse_scale = 1.0 + self._pulse_offset
        current_size = int(self.size * pulse_scale)

        # Draw glowing background circle
        for i in range(3, 0, -1):
            glow_size = current_size + (i * 4)
            glow_alpha = 60 - (i * 15)
            glow_surface = pg.Surface((glow_size * 2, glow_size * 2), pg.SRCALPHA)
            pg.draw.circle(glow_surface, (*color, glow_alpha), (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))

        # Draw main background circle
        pg.draw.circle(screen, color, (self.x, self.y), current_size)

        # Draw darker border
        border_color = tuple(max(0, c - 60) for c in color)
        pg.draw.circle(screen, border_color, (self.x, self.y), current_size, 3)

        # Draw white inner highlight for 3D effect
        highlight_offset = int(current_size * 0.3)
        highlight_size = int(current_size * 0.5)
        highlight_surface = pg.Surface((highlight_size * 2, highlight_size * 2), pg.SRCALPHA)
        pg.draw.circle(highlight_surface, (255, 255, 255, 80), (highlight_size, highlight_size), highlight_size)
        screen.blit(highlight_surface, (self.x - highlight_size - highlight_offset, self.y - highlight_size - highlight_offset))

        # Draw icon (emoji) in center
        try:
            icon_text = self._font.render(icon, True, (255, 255, 255))
            icon_rect = icon_text.get_rect(center=(self.x, self.y))

            # Add shadow for text
            shadow_text = self._font.render(icon, True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(self.x + 2, self.y + 2))
            screen.blit(shadow_text, shadow_rect)

            screen.blit(icon_text, icon_rect)
        except:
            # Fallback: draw text label if emoji doesn't render
            text = self._font.render(status_data["name"][:3].upper(), True, (255, 255, 255))
            rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, rect)


class StatusIconBar:
    """Container for displaying status icon with label"""

    def __init__(self, status: str | None, x: int, y: int, show_label: bool = True):
        """
        Initialize status icon bar

        Args:
            status: Status effect name
            x: X position (left edge)
            y: Y position (top edge)
            show_label: Whether to show status name label
        """
        self.status = status
        self.x = x
        self.y = y
        self.show_label = show_label

        # Create icon (centered in allocated space)
        icon_x = x + 25
        icon_y = y + 25
        self.icon = StatusIcon(status, icon_x, icon_y, size=22)

        # Load font for label
        try:
            self._label_font = pg.font.Font('assets/fonts/Minecraft.ttf', 14)
        except:
            self._label_font = pg.font.SysFont('arial', 14)

    def update(self, dt: float) -> None:
        """Update animations"""
        self.icon.update(dt)

    def draw(self, screen: pg.Surface) -> None:
        """Draw status icon bar"""
        if not self.status or self.status not in STATUS_EFFECTS:
            return

        status_data = STATUS_EFFECTS[self.status]

        # Draw semi-transparent background panel
        panel_width = 120 if self.show_label else 50
        panel_height = 50
        panel_surface = pg.Surface((panel_width, panel_height), pg.SRCALPHA)
        pg.draw.rect(panel_surface, (0, 0, 0, 150), (0, 0, panel_width, panel_height), border_radius=10)
        pg.draw.rect(panel_surface, (*status_data["color"], 180), (0, 0, panel_width, panel_height), 2, border_radius=10)
        screen.blit(panel_surface, (self.x, self.y))

        # Draw icon
        self.icon.draw(screen)

        # Draw label if enabled
        if self.show_label:
            label_text = self._label_font.render(status_data["name"], True, (255, 255, 255))
            label_rect = label_text.get_rect(left=self.x + 55, centery=self.y + 25)
            screen.blit(label_text, label_rect)

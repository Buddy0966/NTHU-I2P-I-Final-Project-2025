import pygame as pg
from src.utils import GameSettings, load_img


class RewardNotification:
    """Displays a notification panel showing rewards received from a chest."""

    def __init__(self, rewards: dict):
        """
        Initialize the reward notification panel.

        Args:
            rewards: Dictionary with 'coins', 'items', and 'monsters' keys
        """
        self.rewards = rewards
        self.visible = True
        self.timer = 0.0
        self.display_duration = 5.0  # Show for 5 seconds

        # Panel dimensions and position
        self.width = 600
        self.height = 500
        self.x = (GameSettings.SCREEN_WIDTH - self.width) // 2
        self.y = (GameSettings.SCREEN_HEIGHT - self.height) // 2

        # Load background
        try:
            self.background = load_img("UI/raw/UI_Flat_Frame03a.png")
            self.background = pg.transform.scale(self.background, (self.width, self.height))
        except:
            self.background = None

        # Fonts
        self.title_font = pg.font.Font('assets/fonts/Minecraft.ttf', 32)
        self.header_font = pg.font.Font('assets/fonts/Minecraft.ttf', 24)
        self.text_font = pg.font.Font('assets/fonts/Minecraft.ttf', 18)

        # Colors
        self.title_color = (255, 215, 0)  # Gold
        self.header_color = (100, 200, 255)  # Light blue
        self.text_color = (255, 255, 255)  # White
        self.coin_color = (255, 223, 0)  # Gold

    def update(self, dt: float) -> bool:
        """
        Update the notification timer.

        Returns:
            bool: True if notification is still visible, False if it should be closed
        """
        if self.visible:
            self.timer += dt
            if self.timer >= self.display_duration:
                self.visible = False
                return False
        return self.visible

    def draw(self, screen: pg.Surface):
        """Draw the reward notification panel."""
        if not self.visible:
            return

        # Draw semi-transparent overlay
        overlay = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Draw background panel
        if self.background:
            screen.blit(self.background, (self.x, self.y))
        else:
            # Fallback: draw a simple rectangle
            pg.draw.rect(screen, (50, 50, 80), (self.x, self.y, self.width, self.height))
            pg.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height), 3)

        # Title
        title = self.title_font.render("TREASURE FOUND!", True, self.title_color)
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 40))
        screen.blit(title, title_rect)

        current_y = self.y + 90

        # Coins
        coins = self.rewards.get("coins", 0)
        if coins > 0:
            coin_header = self.header_font.render("Coins:", True, self.header_color)
            screen.blit(coin_header, (self.x + 40, current_y))
            current_y += 35

            coin_text = self.text_font.render(f"+{coins} coins", True, self.coin_color)
            screen.blit(coin_text, (self.x + 60, current_y))
            current_y += 40

        # Items
        items = self.rewards.get("items", [])
        if items:
            item_header = self.header_font.render("Items:", True, self.header_color)
            screen.blit(item_header, (self.x + 40, current_y))
            current_y += 35

            for item in items:
                item_name = item.get("name", "Unknown")
                item_count = item.get("count", 1)
                item_text = self.text_font.render(f"+{item_count}x {item_name}", True, self.text_color)
                screen.blit(item_text, (self.x + 60, current_y))
                current_y += 28
            current_y += 15

        # Monsters/Pokemon
        monsters = self.rewards.get("monsters", [])
        if monsters:
            monster_header = self.header_font.render("Pokemon:", True, self.header_color)
            screen.blit(monster_header, (self.x + 40, current_y))
            current_y += 35

            # Show first 5 Pokemon in left column, next 5 in right column
            for i, monster in enumerate(monsters):
                monster_name = monster.get("name", "Unknown")
                monster_level = monster.get("level", 1)
                monster_type = monster.get("type", "")

                # Alternate columns
                if i < 5:
                    x_pos = self.x + 60
                    y_pos = current_y + (i * 28)
                else:
                    x_pos = self.x + 320
                    y_pos = current_y + ((i - 5) * 28)

                monster_text = self.text_font.render(
                    f"+{monster_name} Lv.{monster_level} ({monster_type})",
                    True,
                    self.text_color
                )
                screen.blit(monster_text, (x_pos, y_pos))

            current_y += max(5, len(monsters)) * 28 + 15

        # Instructions
        instruction = self.text_font.render("Press SPACE or ESC to continue", True, (200, 200, 200))
        instruction_rect = instruction.get_rect(center=(self.x + self.width // 2, self.y + self.height - 30))
        screen.blit(instruction, instruction_rect)

    def handle_input(self, event: pg.event.Event) -> bool:
        """
        Handle keyboard input to close the notification.

        Returns:
            bool: True if notification should close, False otherwise
        """
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_SPACE, pg.K_ESCAPE, pg.K_RETURN, pg.K_e):
                self.visible = False
                return True
        return False

    def close(self):
        """Manually close the notification."""
        self.visible = False

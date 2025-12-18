from __future__ import annotations
import pygame as pg
from src.sprites import Sprite
from src.interface.components.button import Button
from src.utils.definition import Item
from src.data.bag import Bag
from .component import UIComponent


class ShopPanel(UIComponent):
    def __init__(
        self,
        npc_inventory: list[Item],
        player_bag: Bag,
        npc_name: str = "Merchant",
        x: int = 100,
        y: int = 50,
        width: int = 800,
        height: int = 600,
        on_exit=None,
    ):
        self.sprite = Sprite("UI/raw/UI_Flat_Frame03a.png", (width, height))
        self.rect = pg.Rect(x, y, width, height)
        self._font = pg.font.Font("assets/fonts/Minecraft.ttf", 40)
        self._item_font = pg.font.Font("assets/fonts/Minecraft.ttf", 16)
        self._money_font = pg.font.Font("assets/fonts/Minecraft.ttf", 20)

        self.npc_inventory = npc_inventory
        self.player_bag = player_bag
        self.npc_name = npc_name

        self.title_surf = self._font.render(f"{npc_name}'s Shop", True, (0, 0, 0))

        margin = 12
        btn_w, btn_h = 50, 50
        self.exit_button = Button(
            "UI/button_x.png",
            "UI/button_x_hover.png",
            x + width - btn_w - margin,
            y + margin,
            btn_w,
            btn_h,
            on_exit,
        )

        # Load item sprites
        self._npc_item_sprites = {}
        for item in npc_inventory:
            try:
                self._npc_item_sprites[item["name"]] = Sprite(
                    item["sprite_path"], (40, 40)
                )
            except:
                self._npc_item_sprites[item["name"]] = None

        self._player_item_sprites = {}
        for item in player_bag.items:
            try:
                self._player_item_sprites[item["name"]] = Sprite(
                    item["sprite_path"], (40, 40)
                )
            except:
                self._player_item_sprites[item["name"]] = None

        # Scrolling parameters
        self.npc_scroll_offset = 0
        self.player_scroll_offset = 0
        self.item_line_height = 70
        self.scroll_speed = 30

        # Calculate content heights
        self.npc_content_height = len(self.npc_inventory) * self.item_line_height
        self.player_content_height = len(self.player_bag.items) * self.item_line_height

        # Viewport dimensions
        self.viewport_height = self.rect.height - 160

        # Buy/Sell buttons
        self.buy_buttons = []
        self.sell_buttons = []

        # Transaction feedback
        self.message = ""
        self.message_timer = 0
        self.message_color = (0, 180, 0)

    def update(self, dt: float) -> None:
        self.exit_button.update(dt)

        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

        # Update player item sprites in case items changed
        for item in self.player_bag.items:
            if item["name"] not in self._player_item_sprites:
                try:
                    self._player_item_sprites[item["name"]] = Sprite(
                        item["sprite_path"], (40, 40)
                    )
                except:
                    self._player_item_sprites[item["name"]] = None

        # Handle scroll input
        from src.core.services import input_manager

        mouse_pos = input_manager.mouse_pos
        if self.rect.collidepoint(mouse_pos):
            if input_manager.mouse_wheel != 0:
                scroll_amount = input_manager.mouse_wheel * self.scroll_speed

                # Determine which side to scroll based on mouse position
                mid_x = self.rect.x + self.rect.width // 2
                if mouse_pos[0] < mid_x:
                    # Scroll NPC inventory
                    max_offset = max(0, self.npc_content_height - self.viewport_height)
                    self.npc_scroll_offset = max(
                        0, min(max_offset, self.npc_scroll_offset - scroll_amount)
                    )
                else:
                    # Scroll player inventory
                    max_offset = max(
                        0, self.player_content_height - self.viewport_height
                    )
                    self.player_scroll_offset = max(
                        0, min(max_offset, self.player_scroll_offset - scroll_amount)
                    )

    def draw(self, screen: pg.Surface) -> None:
        # Draw base panel
        screen.blit(self.sprite.image, self.rect)

        # Add overlay
        overlay = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        overlay.fill((200, 220, 255, 40))  # Cool blue overlay
        screen.blit(overlay, self.rect)

        # Draw title
        shadow_surf = self._font.render(f"{self.npc_name}'s Shop", True, (40, 40, 80))
        # screen.blit(shadow_surf, (self.rect.x + 18, self.rect.y + 18))
        screen.blit(self.title_surf, (self.rect.x + 16, self.rect.y + 16))

        # Draw money display (using coins from inventory)
        coin_count = 0
        for item in self.player_bag.items:
            if item["name"] == "Coins":
                coin_count = item["count"]
                break
        money_text = self._money_font.render(
            f"Money: ${coin_count}", True, (253, 251, 249)
        )
        screen.blit(money_text, (self.rect.x + 16, self.rect.y + 50))

        # Draw divider line
        mid_x = self.rect.x + self.rect.width // 2
        pg.draw.line(
            screen,
            (100, 100, 150),
            (mid_x, self.rect.y + 90),
            (mid_x, self.rect.y + self.rect.height - 20),
            3,
        )

        # Clear button lists
        self.buy_buttons.clear()
        self.sell_buttons.clear()

        # Draw NPC inventory (left side)
        self._draw_npc_inventory(screen)

        # Draw player inventory (right side)
        self._draw_player_inventory(screen)

        # Draw message
        if self.message:
            msg_surf = self._item_font.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(
                center=(self.rect.centerx, self.rect.y + self.rect.height - 30)
            )
            # Draw message background
            bg_rect = msg_rect.inflate(20, 10)
            pg.draw.rect(screen, (255, 255, 255), bg_rect, border_radius=5)
            pg.draw.rect(screen, (0, 0, 0), bg_rect, 2, border_radius=5)
            screen.blit(msg_surf, msg_rect)

        self.exit_button.draw(screen)

    def _draw_npc_inventory(self, screen: pg.Surface) -> None:
        """Draw NPC's items for sale on the left side"""
        npc_x = self.rect.x + 20
        npc_y = self.rect.y + 100
        viewport_y = npc_y
        viewport_width = self.rect.width // 2 - 40

        # Header
        header_surf = self._item_font.render("BUY FROM MERCHANT", True, (60, 40, 20))
        screen.blit(header_surf, (npc_x, npc_y - 20))

        # Create clip rect
        clip_rect = pg.Rect(npc_x, viewport_y, viewport_width, self.viewport_height)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        for i, item in enumerate(self.npc_inventory):
            y_pos = npc_y + i * self.item_line_height - self.npc_scroll_offset

            # Item row background
            row_rect = pg.Rect(npc_x, y_pos, viewport_width - 20, 60)
            row_color = (240, 255, 240) if i % 2 == 0 else (230, 245, 230)
            pg.draw.rect(screen, row_color, row_rect, border_radius=6)
            pg.draw.rect(screen, (150, 180, 150), row_rect, 2, border_radius=6)

            # Draw item sprite
            if item["name"] in self._npc_item_sprites and self._npc_item_sprites[item["name"]]:
                screen.blit(
                    self._npc_item_sprites[item["name"]].image, (npc_x + 5, y_pos + 10)
                )

            # Draw item name
            name_text = self._item_font.render(item["name"], True, (40, 40, 40))
            screen.blit(name_text, (npc_x + 55, y_pos + 8))

            # Draw price
            price_text = self._item_font.render(
                f"${item['price']}", True, (200, 140, 0)
            )
            screen.blit(price_text, (npc_x + 55, y_pos + 28))

            # Create buy button
            btn_x = npc_x + viewport_width - 80
            btn_y = y_pos 
            btn_w, btn_h = 60, 60

            buy_button = Button(
                "UI/button_shop.png",
                "UI/button_shop_hover.png",
                btn_x,
                btn_y,
                btn_w,
                btn_h,
                lambda itm=item: self._buy_item(itm),
            )
            self.buy_buttons.append(buy_button)

            # Update and draw buy button
            buy_button.update(0)
            buy_button.draw(screen)
            buy_text = self._item_font.render("BUY", True, (255, 255, 255))
            buy_text_rect = buy_text.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h // 2))
            screen.blit(buy_text, buy_text_rect)

        screen.set_clip(old_clip)

        # Draw scrollbar
        if self.npc_content_height > self.viewport_height:
            self._draw_scrollbar(
                screen, npc_x + viewport_width - 10, viewport_y, self.npc_scroll_offset, self.npc_content_height
            )

    def _draw_player_inventory(self, screen: pg.Surface) -> None:
        """Draw player's items for selling on the right side"""
        player_x = self.rect.x + self.rect.width // 2 + 20
        player_y = self.rect.y + 100
        viewport_y = player_y
        viewport_width = self.rect.width // 2 - 40

        # Header
        header_surf = self._item_font.render("SELL TO MERCHANT", True, (60, 40, 20))
        screen.blit(header_surf, (player_x, player_y - 20))

        # Create clip rect
        clip_rect = pg.Rect(player_x, viewport_y, viewport_width, self.viewport_height)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        for i, item in enumerate(self.player_bag.items):
            y_pos = player_y + i * self.item_line_height - self.player_scroll_offset

            # Item row background
            row_rect = pg.Rect(player_x, y_pos, viewport_width - 20, 60)
            row_color = (255, 240, 240) if i % 2 == 0 else (245, 230, 230)
            pg.draw.rect(screen, row_color, row_rect, border_radius=6)
            pg.draw.rect(screen, (180, 150, 150), row_rect, 2, border_radius=6)

            # Draw item sprite
            if item["name"] in self._player_item_sprites and self._player_item_sprites[item["name"]]:
                screen.blit(
                    self._player_item_sprites[item["name"]].image,
                    (player_x + 5, y_pos + 10),
                )

            # Draw item name and count
            name_text = self._item_font.render(item["name"], True, (40, 40, 40))
            screen.blit(name_text, (player_x + 55, y_pos + 8))

            count_text = self._item_font.render(
                f"x{item['count']}", True, (80, 80, 80)
            )
            screen.blit(count_text, (player_x + 55, y_pos + 28))

            # Calculate sell price (50% of buy price)
            sell_price = item.get("price", 0) // 2

            # Draw sell price
            price_text = self._item_font.render(
                f"${sell_price}", True, (200, 140, 0)
            )
            screen.blit(price_text, (player_x + 120, y_pos + 28))

            # Create sell button
            btn_x = player_x + viewport_width - 80
            btn_y = y_pos 
            btn_w, btn_h = 60, 60

            sell_button = Button(
                "UI/button_shop.png",
                "UI/button_shop_hover.png",
                btn_x,
                btn_y,
                btn_w,
                btn_h,
                lambda itm=item: self._sell_item(itm),
            )
            self.sell_buttons.append(sell_button)

            # Update and draw sell button
            sell_button.update(0)
            sell_button.draw(screen)
            sell_text = self._item_font.render("SELL", True, (255, 255, 255))
            sell_text_rect = sell_text.get_rect(center=(btn_x + btn_w // 2, btn_y + btn_h // 2))
            screen.blit(sell_text, sell_text_rect)

        screen.set_clip(old_clip)

        # Draw scrollbar
        if self.player_content_height > self.viewport_height:
            self._draw_scrollbar(
                screen,
                player_x + viewport_width - 10,
                viewport_y,
                self.player_scroll_offset,
                self.player_content_height,
            )

    def _draw_scrollbar(
        self, screen: pg.Surface, x: int, y: int, scroll_offset: int, content_height: int
    ) -> None:
        """Draw a scrollbar"""
        scrollbar_width = 10
        scrollbar_height = self.viewport_height

        # Background
        pg.draw.rect(
            screen,
            (200, 200, 220),
            (x, y, scrollbar_width, scrollbar_height),
            border_radius=5,
        )

        # Thumb
        thumb_height = max(
            20, (self.viewport_height / content_height) * scrollbar_height
        )
        thumb_y = y + (scroll_offset / content_height) * scrollbar_height

        pg.draw.rect(
            screen, (120, 120, 150), (x, thumb_y, scrollbar_width, thumb_height), border_radius=5
        )
        pg.draw.rect(
            screen,
            (80, 80, 120),
            (x, thumb_y, scrollbar_width, thumb_height),
            2,
            border_radius=5,
        )

    def _buy_item(self, item: Item) -> None:
        """Handle buying an item from NPC"""
        price = item["price"]

        # Check if player has enough coins
        if self.player_bag.remove_item("Coins", price):
            self.player_bag.add_item(
                item["name"], 1, item["sprite_path"], item["price"]
            )
            self.message = f"Bought {item['name']} for ${price}!"
            self.message_color = (0, 180, 0)
            self.message_timer = 2.0

            # Recalculate content height
            self.player_content_height = (
                len(self.player_bag.items) * self.item_line_height
            )
        else:
            self.message = "Not enough money!"
            self.message_color = (220, 60, 60)
            self.message_timer = 2.0

    def _sell_item(self, item: Item) -> None:
        """Handle selling an item to NPC"""
        sell_price = item.get("price", 0) // 2

        if self.player_bag.remove_item(item["name"], 1):
            # Add coins to inventory
            self.player_bag.add_item("Coins", sell_price, "ingame_ui/coin.png", 1)
            self.message = f"Sold {item['name']} for ${sell_price}!"
            self.message_color = (0, 180, 0)
            self.message_timer = 2.0

            # Recalculate content height
            self.player_content_height = (
                len(self.player_bag.items) * self.item_line_height
            )
        else:
            self.message = "Item not found!"
            self.message_color = (220, 60, 60)
            self.message_timer = 2.0

    def set_exit_callback(self, callback) -> None:
        self.exit_button.on_click = callback

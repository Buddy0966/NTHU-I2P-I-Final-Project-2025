import pygame as pg
import json
from src.utils import GameSettings
from src.utils.definition import Monster, Item


class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]
    _money: int

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None, money: int = 1000):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []
        self._money = money

    def update(self, dt: float):
        pass

    def draw(self, screen: pg.Surface):
        pass
    
    @property
    def monsters(self) -> list[Monster]:
        return self._monsters_data

    @property
    def items(self) -> list[Item]:
        return self._items_data

    @property
    def money(self) -> int:
        return self._money

    def add_money(self, amount: int) -> None:
        self._money += amount

    def remove_money(self, amount: int) -> bool:
        if self._money >= amount:
            self._money -= amount
            return True
        return False

    def add_item(self, item_name: str, count: int = 1, sprite_path: str = "", price: int = 0) -> None:
        # Check if item already exists
        for item in self._items_data:
            if item["name"] == item_name:
                item["count"] += count
                return
        # Add new item
        new_item: Item = {
            "name": item_name,
            "count": count,
            "sprite_path": sprite_path,
            "price": price
        }
        self._items_data.append(new_item)

    def remove_item(self, item_name: str, count: int = 1) -> bool:
        for item in self._items_data:
            if item["name"] == item_name:
                if item["count"] >= count:
                    item["count"] -= count
                    if item["count"] == 0:
                        self._items_data.remove(item)
                    return True
                return False
        return False

    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data),
            "money": self._money
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        money = data.get("money", 1000)
        bag = cls(monsters, items, money)
        return bag
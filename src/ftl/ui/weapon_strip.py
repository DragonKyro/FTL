"""Weapon slot row — charge bar, power toggle, target indicator, ammo count.

Clickable: hit-testing returns the weapon index that was clicked. The scene
uses that to either toggle power or enter targeting mode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.ui import theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.combat.combat_state import Inventory
    from ftl.ships.ship import Ship


SLOT_WIDTH: int = 220
SLOT_HEIGHT: int = 36
SLOT_GAP: int = 8


class WeaponStrip:
    def __init__(
        self,
        ship: Ship,
        inventory: Inventory,
        origin_x: float,
        origin_y: float,
    ) -> None:
        self.ship: Ship = ship
        self.inventory: Inventory = inventory
        self.origin_x: float = origin_x
        self.origin_y: float = origin_y
        self.selected_index: int | None = None
        self._text = TextCache()

    def slot_rect(self, index: int) -> tuple[float, float, float, float]:
        left = self.origin_x + index * (SLOT_WIDTH + SLOT_GAP)
        return left, self.origin_y, SLOT_WIDTH, SLOT_HEIGHT

    def slot_at(self, x: float, y: float) -> int | None:
        for i in range(len(self.ship.weapons)):
            left, bottom, w, h = self.slot_rect(i)
            if left <= x <= left + w and bottom <= y <= bottom + h:
                return i
        return None

    def draw(self) -> None:
        for i, weapon in enumerate(self.ship.weapons):
            left, bottom, w, h = self.slot_rect(i)
            outline = theme.TEXT_ACCENT if i == self.selected_index else theme.COLOR_ROOM_OUTLINE
            arcade.draw_lbwh_rectangle_filled(left, bottom, w, h, theme.BG_PANEL)
            arcade.draw_lbwh_rectangle_outline(
                left, bottom, w, h, outline,
                border_width=2 if i == self.selected_index else 1,
            )
            # Name + family
            self._text.draw(
                ("name", i),
                f"W{i+1}  {weapon.stats.name}",
                left + 6,
                bottom + h - theme.FONT_LABEL_SIZE - 4,
                theme.TEXT_PRIMARY,
                theme.FONT_LABEL_SIZE,
            )
            # Charge bar
            bar_x = left + 6
            bar_y = bottom + 4
            bar_w = w - 12
            bar_h = 8
            arcade.draw_lbwh_rectangle_filled(
                bar_x, bar_y, bar_w, bar_h, theme.COLOR_POWER_EMPTY
            )
            if weapon.stats.charge_time > 0:
                frac = weapon.charge_progress / weapon.stats.charge_time
            else:
                frac = 1.0
            fill_color = (
                theme.COLOR_POWER_FILLED if weapon.ready else theme.COLOR_CHARGE_BAR
            )
            arcade.draw_lbwh_rectangle_filled(
                bar_x, bar_y, bar_w * frac, bar_h, fill_color
            )
            arcade.draw_lbwh_rectangle_outline(
                bar_x, bar_y, bar_w, bar_h, theme.COLOR_ROOM_OUTLINE
            )
            # Status text (powered, target, ammo)
            status_parts: list[str] = []
            status_parts.append("[ON]" if weapon.powered else "[--]")
            if weapon.target_room_id:
                status_parts.append(f"→ {weapon.target_room_id}")
            else:
                status_parts.append("→ -")
            if weapon.consumes_missile:
                status_parts.append(f"ammo {self.inventory.missiles}")
            self._text.draw(
                ("status", i),
                "  ".join(status_parts),
                left + 6 + bar_w / 2,
                bottom + h - theme.FONT_LABEL_SIZE - 4,
                theme.TEXT_DIM,
                theme.FONT_LABEL_SIZE,
            )

"""Reactor power widget — shows reactor cap + per-system allocated power.

Visualization-only in Phase 1; the scene handles input via number keys.
Phase 2+ adds clickable +/- buttons here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.ui import theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.ships.ship import Ship
    from ftl.systems.system import System


SYSTEM_DISPLAY_ORDER: tuple[str, ...] = (
    "weapons", "shields", "engines", "piloting", "cloaking",
)
SYSTEM_LABEL: dict[str, str] = {
    "weapons": "W",
    "shields": "S",
    "engines": "E",
    "piloting": "P",
    "cloaking": "C",
}


class PowerPanel:
    def __init__(self, ship: Ship, origin_x: float, origin_y: float) -> None:
        self.ship: Ship = ship
        self.origin_x: float = origin_x
        self.origin_y: float = origin_y
        self._text = TextCache()

    def draw(self) -> None:
        x = self.origin_x
        y = self.origin_y
        self._text.draw(
            "reactor_label", "REACTOR", x, y, theme.TEXT_DIM, theme.FONT_LABEL_SIZE
        )
        x += 64
        for name in SYSTEM_DISPLAY_ORDER:
            system = self.ship.systems.get(name)
            if system is None:
                continue
            self._draw_system(name, system, x, y)
            x += 88
        used = self.ship.power_used
        cap = self.ship.max_reactor_power
        self._text.draw(
            "cap", f"{used} / {cap}",
            x + 8, y,
            theme.TEXT_PRIMARY, theme.FONT_LABEL_SIZE,
        )

    def _draw_system(self, name: str, system: System, x: float, y: float) -> None:
        label = SYSTEM_LABEL.get(name, name[:2].upper())
        self._text.draw(
            ("sys", name), label, x, y, theme.TEXT_ACCENT, theme.FONT_LABEL_SIZE
        )
        bar_x = x + 14
        for i in range(system.level):
            cx = bar_x + i * 11
            cy = y + 5
            if i < system.damage:
                color = theme.COLOR_POWER_DAMAGED
            elif i < system.current_power:
                color = theme.COLOR_POWER_FILLED
            else:
                color = theme.COLOR_POWER_EMPTY
            arcade.draw_circle_filled(cx, cy, 4, color)

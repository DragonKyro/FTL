"""Store scene — buy weapons / drones / augments / repairs / crew / upgrades.

Phase-4 minimalist UI:
- Top: scrap counter
- Left: category list
- Right: items in selected category with prices
- Click a row to buy. Esc returns to star map.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.store.inventory import (
    HIRE_COST,
    REPAIR_UNIT_COST,
    build_upgrade_offers,
)
from ftl.store.purchase import (
    buy_augment,
    buy_drone,
    buy_repair,
    buy_weapon,
    hire_crew,
    upgrade_system,
)
from ftl.ui import theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.core.game import Game
    from ftl.store.inventory import StoreInventory


_CATEGORIES: list[tuple[str, str]] = [
    ("weapons",  "Weapons"),
    ("drones",   "Drones"),
    ("augments", "Augments"),
    ("upgrades", "Upgrades"),
    ("repairs",  "Repairs"),
    ("crew",     "Crew"),
]


class StoreScene(Scene):
    def __init__(self, game: Game, inventory: StoreInventory) -> None:
        super().__init__(game=game)
        self.inventory: StoreInventory = inventory
        self.selected_category: str = "weapons"
        self._text = TextCache()

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True
        if self.game and self.game.run and self.game.run.player_ship:
            self.inventory.system_upgrades = build_upgrade_offers(
                self.game.run.player_ship, self.game.registry
            )

    def on_draw(self) -> None:
        self.clear()
        run = self.game.run if self.game else None
        if run is None:
            return
        self._text.draw(
            "title", "STORE",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50,
            theme.TEXT_PRIMARY, theme.FONT_TITLE_SIZE - 16,
            anchor_x="center",
        )
        self._text.draw(
            "scrap", f"SCRAP {run.scrap}",
            16, WINDOW_HEIGHT - 28,
            theme.TEXT_ACCENT, theme.FONT_BODY_SIZE,
        )
        self._draw_categories()
        self._draw_items(run)
        self._text.draw(
            "hint", "Click a row to buy   [Esc] Leave store",
            WINDOW_WIDTH / 2, 20,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )

    def _draw_categories(self) -> None:
        for i, (key, label) in enumerate(_CATEGORIES):
            y = WINDOW_HEIGHT - 110 - i * 36
            color = theme.TEXT_ACCENT if key == self.selected_category else theme.TEXT_DIM
            self._text.draw(
                ("cat", key), f"> {label}",
                40, y, color, theme.FONT_BODY_SIZE,
            )

    def _category_rect(self, index: int) -> tuple[float, float, float, float]:
        y = WINDOW_HEIGHT - 110 - index * 36
        return 40.0, y - 4, 180.0, 30.0

    def _item_rows(self, run) -> list[tuple[str, str, int]]:  # type: ignore[no-untyped-def]
        rows: list[tuple[str, str, int]] = []
        if self.selected_category == "weapons":
            for w in self.inventory.weapons:
                rows.append((w.id, f"{w.name}  [{w.family}]", w.cost))
        elif self.selected_category == "drones":
            for d in self.inventory.drones:
                rows.append((d.id, f"{d.name}  [{d.family}]", d.cost))
        elif self.selected_category == "augments":
            for a in self.inventory.augments:
                rows.append((a.id, f"{a.name}", a.cost))
        elif self.selected_category == "upgrades":
            for u in self.inventory.system_upgrades:
                rows.append((u.system_name, f"{u.system_name.upper()} -> lv {u.new_level}", u.cost))
        elif self.selected_category == "repairs":
            rows.append(("repair_1", f"Repair 1 HP", REPAIR_UNIT_COST))
            rows.append(("repair_5", f"Repair up to 5 HP", REPAIR_UNIT_COST * 5))
        elif self.selected_category == "crew":
            for s in self.inventory.crew_for_hire:
                rows.append((s.id, f"Hire {s.name}", HIRE_COST))
        return rows

    def _draw_items(self, run) -> None:  # type: ignore[no-untyped-def]
        x = 260.0
        rows = self._item_rows(run)
        for i, (rid, label, price) in enumerate(rows):
            y = WINDOW_HEIGHT - 120 - i * 36
            affordable = run.scrap >= price
            color = theme.TEXT_PRIMARY if affordable else theme.TEXT_DIM
            self._text.draw(
                ("item_label", self.selected_category, i),
                label, x, y, color, theme.FONT_BODY_SIZE,
            )
            self._text.draw(
                ("item_price", self.selected_category, i),
                f"{price} sc", x + 460, y,
                color, theme.FONT_BODY_SIZE,
                anchor_x="right",
            )

    def _row_rect(self, index: int) -> tuple[float, float, float, float]:
        y = WINDOW_HEIGHT - 120 - index * 36
        return 250.0, y - 4, 540.0, 30.0

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        for i, (key, _label) in enumerate(_CATEGORIES):
            cx, cy, cw, ch = self._category_rect(i)
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                self.selected_category = key
                return
        if self.game is None or self.game.run is None:
            return
        run = self.game.run
        rows = self._item_rows(run)
        for i, (row_id, _label, _price) in enumerate(rows):
            rx, ry, rw, rh = self._row_rect(i)
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self._buy(row_id)
                return

    def _buy(self, row_id: str) -> None:
        if self.game is None or self.game.run is None:
            return
        run = self.game.run
        if self.selected_category == "weapons":
            for w in self.inventory.weapons:
                if w.id == row_id and buy_weapon(run, w):
                    self.inventory.weapons.remove(w)
                    return
        elif self.selected_category == "drones":
            for d in self.inventory.drones:
                if d.id == row_id and buy_drone(run, d):
                    self.inventory.drones.remove(d)
                    return
        elif self.selected_category == "augments":
            for a in self.inventory.augments:
                if a.id == row_id and buy_augment(run, a):
                    self.inventory.augments.remove(a)
                    return
        elif self.selected_category == "upgrades":
            for u in self.inventory.system_upgrades:
                if u.system_name == row_id and upgrade_system(run, u):
                    if run.player_ship is not None:
                        self.inventory.system_upgrades = build_upgrade_offers(
                            run.player_ship, self.game.registry
                        )
                    return
        elif self.selected_category == "repairs":
            hp = 1 if row_id == "repair_1" else 5
            buy_repair(run, hp)
        elif self.selected_category == "crew":
            for s in self.inventory.crew_for_hire:
                if s.id == row_id and hire_crew(run, s):
                    self.inventory.crew_for_hire.remove(s)
                    return

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            from ftl.scenes.flow import after_store_left

            if self.game is not None and self.window is not None:
                after_store_left(self.game, self.window)

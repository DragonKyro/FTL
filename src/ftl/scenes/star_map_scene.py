"""Star map scene — pick the next jump destination.

Renders the current sector's beacon graph. The player clicks a beacon
*connected* to the current position to jump. Each jump costs 1 fuel and
triggers the beacon's encounter (combat / event / store / empty).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.map.encounter_kind import EncounterKind
from ftl.ui import theme

if TYPE_CHECKING:
    from ftl.core.game import Game
    from ftl.map.beacon import Beacon


MAP_LEFT: float = 80.0
MAP_TOP: float = WINDOW_HEIGHT - 140.0
BEACON_RADIUS: int = 14
JUMP_FUEL_COST: int = 1


_ENCOUNTER_COLORS: dict[str, tuple[int, int, int]] = {
    EncounterKind.COMBAT.value: theme.COLOR_HULL,
    EncounterKind.EVENT.value: theme.TEXT_ACCENT,
    EncounterKind.STORE.value: theme.COLOR_HULL_OK,
    EncounterKind.EMPTY.value: theme.TEXT_DIM,
    EncounterKind.FINAL_BOSS.value: theme.TEXT_DEFEAT,
}


class StarMapScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game=game)
        self._title = arcade.Text(
            WINDOW_TITLE,
            16, WINDOW_HEIGHT - 28,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
        )

    # --- lifecycle --------------------------------------------------------

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True

    def on_draw(self) -> None:
        self.clear()
        self._title.draw()
        run = self.game.run if self.game else None
        if run is None or run.star_map is None:
            arcade.draw_text(
                "No active run.", WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                theme.TEXT_DIM, theme.FONT_BODY_SIZE, anchor_x="center",
            )
            return
        self._draw_sector_label(run)
        self._draw_resources(run)
        self._draw_connections(run)
        self._draw_beacons(run)
        self._draw_controls_hint()

    # --- input ------------------------------------------------------------

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.game is None or self.game.run is None:
            return
        run = self.game.run
        beacon = self._beacon_at_screen(x, y, run)
        if beacon is None:
            return
        if run.star_map is None:
            return
        current = run.star_map.beacons.get(run.current_beacon_id or "")
        if current is None or beacon.id == current.id:
            return
        if beacon.id not in current.connections:
            return
        if run.fuel < JUMP_FUEL_COST:
            return
        run.fuel -= JUMP_FUEL_COST
        run.current_beacon_id = beacon.id
        beacon.visited = True
        self._dispatch_encounter(beacon)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            from ftl.scenes.main_menu import MainMenuScene

            if self.window is not None:
                self.window.show_view(MainMenuScene(self.game))

    # --- helpers ----------------------------------------------------------

    def _beacon_at_screen(self, x: int, y: int, run) -> Beacon | None:  # type: ignore[no-untyped-def]
        if run.star_map is None:
            return None
        for beacon in run.star_map.beacons.values():
            bx, by = self._beacon_screen_xy(beacon)
            if (bx - x) ** 2 + (by - y) ** 2 <= (BEACON_RADIUS + 2) ** 2:
                return beacon
        return None

    def _beacon_screen_xy(self, beacon: Beacon) -> tuple[float, float]:
        return MAP_LEFT + beacon.x, MAP_TOP - beacon.y

    def _draw_sector_label(self, run) -> None:  # type: ignore[no-untyped-def]
        if self.game is None:
            return
        sector_label = "Unknown Region"
        if run.star_map is not None:
            sector_def = self.game.registry.sectors.get(run.star_map.sector_id)
            if sector_def is not None:
                sector_label = f"Sector {run.sector_index + 1}: {sector_def.name}"
        arcade.draw_text(
            sector_label,
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 28,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def _draw_resources(self, run) -> None:  # type: ignore[no-untyped-def]
        line = (
            f"SCRAP {run.scrap}    FUEL {run.fuel}    "
            f"MISSILES {run.missiles}    DRONE PARTS {run.drone_parts}"
        )
        arcade.draw_text(
            line,
            16, WINDOW_HEIGHT - 56,
            theme.TEXT_ACCENT, theme.FONT_LABEL_SIZE,
        )

    def _draw_connections(self, run) -> None:  # type: ignore[no-untyped-def]
        if run.star_map is None:
            return
        seen: set[frozenset[str]] = set()
        for beacon in run.star_map.beacons.values():
            for nbr_id in beacon.connections:
                pair = frozenset({beacon.id, nbr_id})
                if pair in seen:
                    continue
                seen.add(pair)
                nbr = run.star_map.beacons.get(nbr_id)
                if nbr is None:
                    continue
                ax, ay = self._beacon_screen_xy(beacon)
                bx, by = self._beacon_screen_xy(nbr)
                arcade.draw_line(ax, ay, bx, by, theme.BG_PANEL, 2)

    def _draw_beacons(self, run) -> None:  # type: ignore[no-untyped-def]
        if run.star_map is None:
            return
        current = run.star_map.beacons.get(run.current_beacon_id or "")
        connected_ids: set[str] = set(current.connections) if current else set()
        for beacon in run.star_map.beacons.values():
            sx, sy = self._beacon_screen_xy(beacon)
            color = _ENCOUNTER_COLORS.get(beacon.encounter_id or "", theme.TEXT_DIM)
            arcade.draw_circle_filled(sx, sy, BEACON_RADIUS, color)
            if beacon.id in connected_ids:
                arcade.draw_circle_outline(
                    sx, sy, BEACON_RADIUS + 4, theme.TEXT_ACCENT, border_width=2
                )
            if current is not None and beacon.id == current.id:
                arcade.draw_circle_outline(
                    sx, sy, BEACON_RADIUS + 6, theme.TEXT_PRIMARY, border_width=3
                )
            if run.star_map and beacon.id == run.star_map.exit_beacon:
                arcade.draw_text(
                    "EXIT",
                    sx, sy + BEACON_RADIUS + 6,
                    theme.TEXT_VICTORY, theme.FONT_LABEL_SIZE,
                    anchor_x="center",
                )

    def _draw_controls_hint(self) -> None:
        hint = "Click a connected beacon to jump (costs 1 fuel)   [Esc] Back to menu"
        arcade.draw_text(
            hint, WINDOW_WIDTH / 2, 20,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )

    def _dispatch_encounter(self, beacon: Beacon) -> None:
        from ftl.scenes.flow import start_encounter

        if self.game is None or self.window is None:
            return
        start_encounter(beacon, self.game, self.window)

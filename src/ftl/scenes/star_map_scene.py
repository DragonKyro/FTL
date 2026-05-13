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
from ftl.ui import art, theme
from ftl.ui.text_cache import TextCache

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

_ENCOUNTER_INNER: dict[str, tuple[int, int, int]] = {
    EncounterKind.COMBAT.value: (255, 200, 200),
    EncounterKind.EVENT.value: (210, 240, 255),
    EncounterKind.STORE.value: (210, 255, 210),
    EncounterKind.EMPTY.value: (210, 210, 220),
    EncounterKind.FINAL_BOSS.value: (255, 200, 200),
}


class StarMapScene(Scene):
    def __init__(self, game: Game) -> None:
        super().__init__(game=game)
        self._title = arcade.Text(
            WINDOW_TITLE,
            16, WINDOW_HEIGHT - 28,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
        )
        self._bg_tex: arcade.Texture | None = None
        self._beacon_textures: dict[str, arcade.Texture] = {}
        self._text = TextCache()

    # --- lifecycle --------------------------------------------------------

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True
        if self._bg_tex is None:
            self._bg_tex = (
                art.disk_texture("ui/starfield_starmap")
                or art.starfield(WINDOW_WIDTH, WINDOW_HEIGHT, seed=11)
            )
        if not self._beacon_textures:
            for kind, outer in _ENCOUNTER_COLORS.items():
                inner = _ENCOUNTER_INNER[kind]
                self._beacon_textures[kind] = (
                    art.disk_texture(f"beacons/{kind}")
                    or art.radial_orb(
                        64, inner, outer, rim=(20, 20, 30), halo=1.6, highlight=True,
                    )
                )

    def on_draw(self) -> None:
        self.clear()
        if self._bg_tex is not None:
            arcade.draw_texture_rect(
                self._bg_tex,
                arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            )
        self._title.draw()
        run = self.game.run if self.game else None
        if run is None or run.star_map is None:
            self._text.draw(
                "no_run", "No active run.",
                WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
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
        elif symbol == arcade.key.S:
            self._save_run()

    def _save_run(self) -> None:
        if self.game is None or self.game.run is None:
            return
        from ftl.persistence.save import save_run

        try:
            save_run(self.game.run, "quicksave")
            self._save_toast = "Saved to quicksave."
            self._save_toast_ttl = 2.0
        except (OSError, ValueError) as exc:
            self._save_toast = f"Save failed: {exc}"
            self._save_toast_ttl = 3.0

    def on_update(self, delta_time: float) -> None:
        ttl = getattr(self, "_save_toast_ttl", 0.0)
        if ttl > 0:
            self._save_toast_ttl = max(0.0, ttl - delta_time)

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
        self._text.draw(
            "sector_label", sector_label,
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 28,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def _draw_resources(self, run) -> None:  # type: ignore[no-untyped-def]
        line = (
            f"SCRAP {run.scrap}    FUEL {run.fuel}    "
            f"MISSILES {run.missiles}    DRONE PARTS {run.drone_parts}"
        )
        self._text.draw(
            "resources", line,
            16, WINDOW_HEIGHT - 56,
            theme.TEXT_ACCENT, theme.FONT_LABEL_SIZE,
        )

    def _draw_connections(self, run) -> None:  # type: ignore[no-untyped-def]
        if run.star_map is None:
            return
        current_id = run.current_beacon_id or ""
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
                touches_current = current_id in (beacon.id, nbr_id)
                if touches_current:
                    arcade.draw_line(ax, ay, bx, by, (60, 110, 150), 3)
                else:
                    arcade.draw_line(ax, ay, bx, by, (30, 38, 52), 2)

    def _draw_beacons(self, run) -> None:  # type: ignore[no-untyped-def]
        if run.star_map is None:
            return
        current = run.star_map.beacons.get(run.current_beacon_id or "")
        connected_ids: set[str] = set(current.connections) if current else set()
        for beacon in run.star_map.beacons.values():
            sx, sy = self._beacon_screen_xy(beacon)
            kind = beacon.encounter_id or EncounterKind.EMPTY.value
            tex = self._beacon_textures.get(kind)
            size = (BEACON_RADIUS + 4) * 2.4
            if tex is not None:
                art.draw_centered(tex, sx, sy, size=size)
            else:
                color = _ENCOUNTER_COLORS.get(kind, theme.TEXT_DIM)
                arcade.draw_circle_filled(sx, sy, BEACON_RADIUS, color)
            if beacon.id in connected_ids:
                arcade.draw_circle_outline(
                    sx, sy, BEACON_RADIUS + 4, theme.TEXT_ACCENT, border_width=2
                )
            if current is not None and beacon.id == current.id:
                arcade.draw_circle_outline(
                    sx, sy, BEACON_RADIUS + 7, theme.TEXT_PRIMARY, border_width=3
                )
            if run.star_map and beacon.id == run.star_map.exit_beacon:
                self._text.draw(
                    ("exit", beacon.id), "EXIT",
                    sx, sy + BEACON_RADIUS + 8,
                    theme.TEXT_VICTORY, theme.FONT_LABEL_SIZE,
                    anchor_x="center",
                )

    def _draw_controls_hint(self) -> None:
        hint = (
            "Click a connected beacon to jump (costs 1 fuel)   "
            "[S] Save   [Esc] Back to menu"
        )
        self._text.draw(
            "hint", hint, WINDOW_WIDTH / 2, 20,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )
        ttl = getattr(self, "_save_toast_ttl", 0.0)
        if ttl > 0:
            toast = getattr(self, "_save_toast", "")
            alpha = min(1.0, ttl / 1.5)
            color = (
                theme.TEXT_VICTORY[0],
                theme.TEXT_VICTORY[1],
                theme.TEXT_VICTORY[2],
                int(255 * alpha),
            )
            self._text.draw(
                "toast", toast, WINDOW_WIDTH / 2, 46,
                color, theme.FONT_BODY_SIZE,
                anchor_x="center",
            )

    def _dispatch_encounter(self, beacon: Beacon) -> None:
        from ftl.scenes.flow import start_encounter

        if self.game is None or self.window is None:
            return
        start_encounter(beacon, self.game, self.window)

"""Renders one ship at tile granularity.

Phase 4 polish: tile fills now use a baked rounded-panel texture with
gradient + soft inner shadow; crew are gradient orbs with halo glow;
shield layers are soft halos instead of flat outlines. The view exposes
hit-testing for tiles, rooms, and doors so the CombatScene can drive
selection / targeting / door-toggle from clicks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.ui import art, theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.crew.crew import Crew
    from ftl.data.schemas import ShipDef
    from ftl.ships.door import Door
    from ftl.ships.room import Room
    from ftl.ships.ship import Ship
    from ftl.ships.tile import Tile
    from ftl.systems.system import System


TILE_PX: int = 40
HULL_BAR_HEIGHT: int = 8
DOOR_LINE_WIDTH: int = 3
DOOR_LENGTH: int = 16
CREW_RADIUS: int = 9

_SPECIES_COLORS: dict[str, tuple[int, int, int]] = {
    "sapien": (90, 160, 220),
    "halene": (220, 220, 240),
    "mhirsa": (220, 130, 80),
    "choir": (180, 220, 250),
    "yssari": (140, 220, 180),
    "ferran": (180, 130, 220),
    "loam": (160, 200, 130),
    "drevant": (210, 170, 110),
}


def _species_color(species_id: str) -> tuple[int, int, int]:
    return _SPECIES_COLORS.get(species_id, (200, 200, 210))


def _lighten(c: tuple[int, int, int], amount: float = 0.55) -> tuple[int, int, int]:
    return (
        min(255, int(c[0] + (255 - c[0]) * amount)),
        min(255, int(c[1] + (255 - c[1]) * amount)),
        min(255, int(c[2] + (255 - c[2]) * amount)),
    )


class ShipView:
    def __init__(
        self,
        ship: Ship,
        ship_def: ShipDef,
        origin_x: float,
        origin_y: float,
        title: str = "",
    ) -> None:
        self.ship: Ship = ship
        self.ship_def: ShipDef = ship_def
        self.origin_x: float = origin_x
        self.origin_y: float = origin_y
        self.title: str = title or ship.name
        self._max_y = max(
            (r.y + r.height - 1 for r in ship_def.rooms), default=0
        )
        self._max_x = max(
            (r.x + r.width - 1 for r in ship_def.rooms), default=0
        )
        self._title_text = arcade.Text(
            self.title,
            origin_x,
            origin_y + (self._max_y + 1) * TILE_PX + HULL_BAR_HEIGHT + 12,
            theme.TEXT_PRIMARY,
            theme.FONT_BODY_SIZE,
        )
        self._tile_tex_cache: dict[tuple[int, int, int], arcade.Texture] = {}
        self._crew_tex_cache: dict[tuple[int, int, int], arcade.Texture] = {}
        self._fire_tex: arcade.Texture | None = None
        self._shadow_tex: arcade.Texture | None = None
        self._text = TextCache()

    # --- coordinate math --------------------------------------------------

    def tile_to_screen(self, tile: Tile) -> tuple[float, float]:
        """Bottom-left corner of a tile in screen space."""
        sx = self.origin_x + tile.x * TILE_PX
        sy = self.origin_y + (self._max_y - tile.y) * TILE_PX
        return sx, sy

    def tile_center(self, tile: Tile) -> tuple[float, float]:
        left, bottom = self.tile_to_screen(tile)
        return left + TILE_PX / 2, bottom + TILE_PX / 2

    def room_center(self, room_id: str) -> tuple[float, float] | None:
        room = self.ship.rooms.get(room_id)
        if room is None or not room.tiles:
            return None
        cx = sum(t.x for t in room.tiles) / len(room.tiles)
        cy = sum(t.y for t in room.tiles) / len(room.tiles)
        sx = self.origin_x + cx * TILE_PX + TILE_PX / 2
        sy = self.origin_y + (self._max_y - cy) * TILE_PX + TILE_PX / 2
        return sx, sy

    def center(self) -> tuple[float, float]:
        return (
            self.origin_x + (self._max_x + 1) * TILE_PX / 2,
            self.origin_y + (self._max_y + 1) * TILE_PX / 2,
        )

    # --- hit testing -----------------------------------------------------

    def tile_at(self, x: float, y: float) -> Tile | None:
        for tile in self.ship.tile_graph.values():
            left, bottom = self.tile_to_screen(tile)
            if left <= x <= left + TILE_PX and bottom <= y <= bottom + TILE_PX:
                return tile
        return None

    def room_at(self, x: float, y: float) -> str | None:
        tile = self.tile_at(x, y)
        return tile.room_id if tile is not None else None

    def door_at(self, x: float, y: float, slack: int = 8) -> Door | None:
        for door in self.ship.doors.values():
            cx, cy = self._door_center(door)
            if abs(x - cx) <= slack and abs(y - cy) <= slack:
                return door
        return None

    # --- draw -------------------------------------------------------------

    def draw(
        self,
        targeted_room_id: str | None = None,
        selected_crew: Crew | None = None,
        visibility: int = 4,
    ) -> None:
        self._draw_ship_shadow()
        self._title_text.draw()
        self._draw_hull_bar()
        self._draw_tiles(targeted_room_id, visibility)
        self._draw_doors()
        self._draw_shield_ring()
        if visibility >= 3:
            self._draw_crew(selected_crew)

    def _draw_ship_shadow(self) -> None:
        if self._shadow_tex is None:
            self._shadow_tex = art.drop_shadow(
                (self._max_x + 1) * TILE_PX,
                (self._max_y + 1) * TILE_PX,
                radius=12,
            )
        cx, cy = self.center()
        art.draw_centered(
            self._shadow_tex, cx, cy - 6,
            size=None,
        )

    def _draw_hull_bar(self) -> None:
        bar_w = (self._max_x + 1) * TILE_PX
        bar_y = self.origin_y + (self._max_y + 1) * TILE_PX + 4
        arcade.draw_lbwh_rectangle_filled(
            self.origin_x, bar_y, bar_w, HULL_BAR_HEIGHT, theme.BG_PANEL
        )
        hull = self.ship.hull
        frac = 0.0 if hull.maximum == 0 else max(0.0, hull.current / hull.maximum)
        color = theme.COLOR_HULL_OK if frac > 0.3 else theme.COLOR_HULL_LOW
        arcade.draw_lbwh_rectangle_filled(
            self.origin_x, bar_y, bar_w * frac, HULL_BAR_HEIGHT, color
        )
        arcade.draw_lbwh_rectangle_outline(
            self.origin_x, bar_y, bar_w, HULL_BAR_HEIGHT, theme.COLOR_ROOM_OUTLINE
        )
        self._text.draw(
            "hull",
            f"HULL {hull.current}/{hull.maximum}",
            self.origin_x + bar_w + 8, bar_y - 2,
            theme.TEXT_DIM, theme.FONT_LABEL_SIZE,
        )

    def _tile_texture(self, fill: tuple[int, int, int]) -> arcade.Texture:
        key = fill
        tex = self._tile_tex_cache.get(key)
        if tex is None:
            top = (
                min(255, fill[0] + 18),
                min(255, fill[1] + 18),
                min(255, fill[2] + 22),
            )
            bottom = (
                max(0, fill[0] - 10),
                max(0, fill[1] - 10),
                max(0, fill[2] - 12),
            )
            tex = art.rounded_panel(
                TILE_PX, TILE_PX, top, bottom,
                radius=5, border=(20, 24, 32), border_w=1, shadow=False,
            )
            self._tile_tex_cache[key] = tex
        return tex

    def _draw_tiles(self, targeted_room_id: str | None, visibility: int) -> None:
        show_oxygen_tint = visibility >= 2
        show_fire_breach = visibility >= 2
        show_labels = visibility >= 2
        seen_rooms: set[str] = set()
        for tile in self.ship.tile_graph.values():
            room = self.ship.rooms.get(tile.room_id)
            if room is None:
                continue
            left, bottom = self.tile_to_screen(tile)
            if show_oxygen_tint:
                fill = self._tile_fill_color(room)
            else:
                fill = (32, 36, 44)  # foggy unknown
            tex = self._tile_texture(fill)
            arcade.draw_texture_rect(
                tex, arcade.LBWH(left, bottom, TILE_PX, TILE_PX)
            )
            if show_fire_breach and room.fire > 0:
                intensity = min(1.0, room.fire / 100.0)
                tint: tuple[int, int, int] = (255, int(140 - 60 * intensity), 40)
                if self._fire_tex is None:
                    self._fire_tex = art.soft_circle(32, (255, 140, 40), alpha=210)
                size = (12 + 12 * intensity)
                art.draw_centered(
                    self._fire_tex,
                    left + TILE_PX / 2,
                    bottom + TILE_PX / 2,
                    size=size,
                )
                arcade.draw_circle_filled(
                    left + TILE_PX / 2,
                    bottom + TILE_PX / 2,
                    3 + 2 * intensity,
                    tint,
                )
            if show_fire_breach and room.breach > 0:
                arcade.draw_line(
                    left + 4, bottom + 4,
                    left + TILE_PX - 4, bottom + TILE_PX - 4,
                    theme.COLOR_BREACH, 2,
                )
                arcade.draw_line(
                    left + TILE_PX - 4, bottom + 4,
                    left + 4, bottom + TILE_PX - 4,
                    theme.COLOR_BREACH, 2,
                )
            if room.id not in seen_rooms:
                seen_rooms.add(room.id)
                if show_labels:
                    self._draw_room_label(room)
                if room.id == targeted_room_id:
                    self._draw_room_outline(room, theme.COLOR_ROOM_TARGETED, 2)

    def _tile_fill_color(self, room: Room) -> tuple[int, int, int]:
        ox = max(0.0, min(1.0, room.oxygen))
        empty = (60, 30, 30)
        full = theme.COLOR_ROOM_FILL
        r = int(empty[0] + (full[0] - empty[0]) * ox)
        g = int(empty[1] + (full[1] - empty[1]) * ox)
        b = int(empty[2] + (full[2] - empty[2]) * ox)
        return r, g, b

    def _draw_room_label(self, room: Room) -> None:
        if room.system is None or not room.tiles:
            return
        first = room.tiles[0]
        left, bottom = self.tile_to_screen(first)
        self._text.draw(
            ("room_label", room.id),
            room.system.name.upper()[:5],
            left + 3, bottom + TILE_PX - theme.FONT_LABEL_SIZE - 3,
            theme.TEXT_PRIMARY, theme.FONT_LABEL_SIZE,
        )
        system: System = room.system
        for i in range(system.level):
            cx = left + 4 + i * 8
            cy = bottom + 4
            if i < system.damage:
                color = theme.COLOR_POWER_DAMAGED
            elif i < system.current_power:
                color = theme.COLOR_POWER_FILLED
            else:
                color = theme.COLOR_POWER_EMPTY
            arcade.draw_circle_filled(cx, cy, 2.5, color)

    def _draw_room_outline(
        self, room: Room, color: tuple[int, int, int], width: int
    ) -> None:
        if not room.tiles:
            return
        min_x = min(t.x for t in room.tiles)
        max_x = max(t.x for t in room.tiles)
        min_y = min(t.y for t in room.tiles)
        max_y = max(t.y for t in room.tiles)
        left = self.origin_x + min_x * TILE_PX
        bottom = self.origin_y + (self._max_y - max_y) * TILE_PX
        w = (max_x - min_x + 1) * TILE_PX
        h = (max_y - min_y + 1) * TILE_PX
        arcade.draw_lbwh_rectangle_outline(left, bottom, w, h, color, border_width=width)

    def _draw_doors(self) -> None:
        for door in self.ship.doors.values():
            cx, cy = self._door_center(door)
            color = (
                theme.TEXT_WARNING if door.force_closed else theme.COLOR_ROOM_OUTLINE
            )
            ax, _ay = door.tile_a
            bx, _by = door.tile_b
            if ax == bx:
                arcade.draw_line(
                    cx - DOOR_LENGTH / 2, cy,
                    cx + DOOR_LENGTH / 2, cy,
                    color, DOOR_LINE_WIDTH,
                )
            else:
                arcade.draw_line(
                    cx, cy - DOOR_LENGTH / 2,
                    cx, cy + DOOR_LENGTH / 2,
                    color, DOOR_LINE_WIDTH,
                )

    def _door_center(self, door: Door) -> tuple[float, float]:
        ax, ay = door.tile_a
        bx, by = door.tile_b
        a_x = self.origin_x + ax * TILE_PX + TILE_PX / 2
        a_y = self.origin_y + (self._max_y - ay) * TILE_PX + TILE_PX / 2
        b_x = self.origin_x + bx * TILE_PX + TILE_PX / 2
        b_y = self.origin_y + (self._max_y - by) * TILE_PX + TILE_PX / 2
        return (a_x + b_x) / 2, (a_y + b_y) / 2

    def _draw_shield_ring(self) -> None:
        shields = self.ship.shields
        if shields is None or shields.max_layers <= 0:
            return
        cx, cy = self.center()
        radius = max(self._max_x + 1, self._max_y + 1) * TILE_PX / 2 + 14
        for layer_idx in range(shields.max_layers):
            is_active = layer_idx < shields.current_layers
            color = (
                theme.COLOR_SHIELDS
                if is_active
                else theme.COLOR_SHIELDS_DIM
            )
            r = radius + layer_idx * 8
            tex = art.shield_halo(int(r * 2.2), color, intensity=1.0 if is_active else 0.4)
            art.draw_centered(tex, cx, cy, size=r * 2.2)

    def _draw_crew(self, selected_crew: Crew | None) -> None:
        per_tile_count: dict[tuple[int, int], int] = {}
        for crew in self.ship.crew:
            if not crew.alive or crew.current_tile is None:
                continue
            key = (crew.current_tile.x, crew.current_tile.y)
            stack = per_tile_count.get(key, 0)
            per_tile_count[key] = stack + 1
            cx, cy = self.tile_center(crew.current_tile)
            offset = (stack - 1) * 4
            outer = _species_color(crew.species.id)
            inner = _lighten(outer, 0.55)
            tex = self._crew_tex_cache.get(outer)
            if tex is None:
                tex = (
                    art.disk_texture(f"crew/{crew.species.id}")
                    or art.radial_orb(
                        40, inner, outer,
                        rim=(20, 22, 30), halo=1.25, highlight=True,
                    )
                )
                self._crew_tex_cache[outer] = tex
            art.draw_centered(tex, cx + offset, cy, size=CREW_RADIUS * 2.6)
            if crew.home_ship is not self.ship:
                arcade.draw_circle_outline(
                    cx + offset, cy, CREW_RADIUS + 2, theme.COLOR_BREACH, border_width=2
                )
            if crew is selected_crew:
                arcade.draw_circle_outline(
                    cx + offset, cy, CREW_RADIUS + 4, theme.TEXT_PRIMARY, border_width=2
                )
            hp_frac = max(0.0, min(1.0, crew.hp / max(1, crew.max_hp)))
            bar_w = TILE_PX - 8
            bar_x = cx + offset - bar_w / 2
            bar_y = cy + CREW_RADIUS + 4
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_w, 3, theme.BG_PANEL)
            bar_color = theme.COLOR_HULL_OK if hp_frac > 0.4 else theme.COLOR_HULL_LOW
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_w * hp_frac, 3, bar_color)

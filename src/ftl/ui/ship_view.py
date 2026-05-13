"""Renders a single ship: rooms (as a grid of placeholder rectangles), hull
bar, shield ring, system status. Supports click hit-testing for targeting.

This is intentionally programmer-art: a clear visualization of game state
without any sprite assets. Phase 2+ swaps in textures via the asset cache.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.ui import theme

if TYPE_CHECKING:
    from ftl.data.schemas import RoomLayout, ShipDef
    from ftl.ships.ship import Ship


TILE_SIZE: int = 56
ROOM_GAP: int = 4
HULL_BAR_HEIGHT: int = 8


class ShipView:
    """One ship's on-screen presentation.

    Position is given as the (left, bottom) of the ship's bounding box.
    The bounding box is sized to fit every room in the layout.
    """

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
        self._title_text = arcade.Text(
            self.title,
            origin_x,
            origin_y + self._bbox_height() + HULL_BAR_HEIGHT + 24,
            theme.TEXT_PRIMARY,
            theme.FONT_BODY_SIZE,
        )

    # --- layout helpers ---------------------------------------------------

    def _bbox_width(self) -> int:
        if not self.ship_def.rooms:
            return TILE_SIZE
        max_x = max(rl.x + rl.width - 1 for rl in self.ship_def.rooms)
        return (max_x + 1) * (TILE_SIZE + ROOM_GAP) - ROOM_GAP

    def _bbox_height(self) -> int:
        if not self.ship_def.rooms:
            return TILE_SIZE
        max_y = max(rl.y + rl.height - 1 for rl in self.ship_def.rooms)
        return (max_y + 1) * (TILE_SIZE + ROOM_GAP) - ROOM_GAP

    def _room_rect(self, layout: RoomLayout) -> tuple[float, float, float, float]:
        """Return (left, bottom, width, height) for a room layout in screen space."""
        left = self.origin_x + layout.x * (TILE_SIZE + ROOM_GAP)
        # y grows downward in our YAML grid, but upward on screen — flip.
        bbox_h = self._bbox_height()
        bottom = (
            self.origin_y
            + (bbox_h - (layout.y + layout.height) * (TILE_SIZE + ROOM_GAP) + ROOM_GAP)
        )
        width = layout.width * (TILE_SIZE + ROOM_GAP) - ROOM_GAP
        height = layout.height * (TILE_SIZE + ROOM_GAP) - ROOM_GAP
        return left, bottom, width, height

    # --- public API -------------------------------------------------------

    def room_center(self, room_id: str) -> tuple[float, float] | None:
        layout = self._find_layout(room_id)
        if layout is None:
            return None
        left, bottom, width, height = self._room_rect(layout)
        return left + width / 2, bottom + height / 2

    def room_at(self, x: float, y: float) -> str | None:
        for layout in self.ship_def.rooms:
            left, bottom, width, height = self._room_rect(layout)
            if left <= x <= left + width and bottom <= y <= bottom + height:
                return layout.id
        return None

    def center(self) -> tuple[float, float]:
        return (
            self.origin_x + self._bbox_width() / 2,
            self.origin_y + self._bbox_height() / 2,
        )

    # --- draw -------------------------------------------------------------

    def draw(self, targeted_room_id: str | None = None) -> None:
        self._title_text.draw()
        self._draw_hull_bar()
        self._draw_shield_ring()
        for layout in self.ship_def.rooms:
            self._draw_room(layout, targeted=(layout.id == targeted_room_id))

    def _draw_hull_bar(self) -> None:
        bar_width = float(self._bbox_width())
        bar_y = self.origin_y + self._bbox_height() + 6
        # Background
        arcade.draw_lbwh_rectangle_filled(
            self.origin_x, bar_y, bar_width, HULL_BAR_HEIGHT, theme.BG_PANEL
        )
        hull = self.ship.hull
        frac = 0.0 if hull.maximum == 0 else max(0.0, hull.current / hull.maximum)
        fill_w = bar_width * frac
        color = theme.COLOR_HULL_OK if frac > 0.3 else theme.COLOR_HULL_LOW
        arcade.draw_lbwh_rectangle_filled(
            self.origin_x, bar_y, fill_w, HULL_BAR_HEIGHT, color
        )
        arcade.draw_lbwh_rectangle_outline(
            self.origin_x, bar_y, bar_width, HULL_BAR_HEIGHT,
            theme.COLOR_ROOM_OUTLINE,
        )
        arcade.draw_text(
            f"HULL {hull.current}/{hull.maximum}",
            self.origin_x + bar_width + 8,
            bar_y - 2,
            theme.TEXT_DIM,
            theme.FONT_LABEL_SIZE,
        )

    def _draw_shield_ring(self) -> None:
        shields = self.ship.shields
        if shields is None or shields.max_layers <= 0:
            return
        cx, cy = self.center()
        radius = max(self._bbox_width(), self._bbox_height()) / 2 + 18
        for layer_idx in range(shields.max_layers):
            color = (
                theme.COLOR_SHIELDS
                if layer_idx < shields.current_layers
                else theme.COLOR_SHIELDS_DIM
            )
            arcade.draw_circle_outline(
                cx, cy, radius + layer_idx * 6, color, border_width=2
            )

    def _draw_room(self, layout: RoomLayout, targeted: bool) -> None:
        left, bottom, width, height = self._room_rect(layout)
        # Fill — damaged rooms are darker red
        system = self.ship.rooms[layout.id].system if layout.id in self.ship.rooms else None
        if system is not None and system.damage >= system.level:
            fill = theme.COLOR_ROOM_DAMAGED
        else:
            fill = theme.COLOR_ROOM_FILL
        arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, fill)
        outline = theme.COLOR_ROOM_TARGETED if targeted else theme.COLOR_ROOM_OUTLINE
        arcade.draw_lbwh_rectangle_outline(
            left, bottom, width, height, outline, border_width=2 if targeted else 1
        )
        # Label
        label = layout.system.upper()[:3] if layout.system else layout.id[:3].upper()
        arcade.draw_text(
            label,
            left + 4,
            bottom + height - theme.FONT_LABEL_SIZE - 4,
            theme.TEXT_PRIMARY,
            theme.FONT_LABEL_SIZE,
        )
        # System damage indicator
        if system is not None and system.level > 0:
            dmg_y = bottom + 4
            for i in range(system.level):
                cx = left + 6 + i * 10
                if i < system.damage:
                    color = theme.COLOR_POWER_DAMAGED
                elif i < system.current_power:
                    color = theme.COLOR_POWER_FILLED
                else:
                    color = theme.COLOR_POWER_EMPTY
                arcade.draw_circle_filled(cx, dmg_y, 3, color)

    def _find_layout(self, room_id: str) -> RoomLayout | None:
        for rl in self.ship_def.rooms:
            if rl.id == room_id:
                return rl
        return None

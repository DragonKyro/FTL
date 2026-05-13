"""Crew list panel.

Renders one row per player crew member: name, species, current task,
HP bar. Click a row to select that crew member (the scene reads
`selected_index` after each click).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.crew.crew import CrewState
from ftl.ui import theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.combat.engine import CombatEngine
    from ftl.crew.crew import Crew


ROW_HEIGHT: int = 28
PANEL_WIDTH: int = 240


_STATE_LABELS: dict[CrewState, str] = {
    CrewState.IDLE: "idle",
    CrewState.MOVING: "moving",
    CrewState.MANNING: "manning",
    CrewState.REPAIRING: "repairing",
    CrewState.HEALING: "healing",
    CrewState.FIGHTING_FIRE: "fire!",
    CrewState.FIGHTING: "fighting",
    CrewState.DEAD: "dead",
}


class CrewPanel:
    def __init__(
        self,
        engine: CombatEngine,
        origin_x: float,
        origin_y: float,
    ) -> None:
        self.engine: CombatEngine = engine
        self.origin_x: float = origin_x
        self.origin_y: float = origin_y
        self.selected_index: int | None = None
        self._text = TextCache()

    def _player_crew(self) -> list[Crew]:
        # Player home crew, including any boarders currently elsewhere.
        result: list[Crew] = []
        for crew in self.engine.state.player.crew:
            if crew.home_ship is self.engine.state.player:
                result.append(crew)
        for crew in self.engine.state.enemy.crew:
            if crew.home_ship is self.engine.state.player:
                result.append(crew)
        return result

    def crew_list(self) -> list[Crew]:
        return self._player_crew()

    def row_rect(self, index: int) -> tuple[float, float, float, float]:
        left = self.origin_x
        bottom = self.origin_y - (index + 1) * ROW_HEIGHT
        return left, bottom, PANEL_WIDTH, ROW_HEIGHT

    def crew_at(self, x: float, y: float) -> int | None:
        crew = self._player_crew()
        for i in range(len(crew)):
            left, bottom, w, h = self.row_rect(i)
            if left <= x <= left + w and bottom <= y <= bottom + h:
                return i
        return None

    def selected_crew(self) -> Crew | None:
        if self.selected_index is None:
            return None
        crew = self._player_crew()
        if 0 <= self.selected_index < len(crew):
            return crew[self.selected_index]
        return None

    def draw(self) -> None:
        self._text.draw(
            "header", "CREW",
            self.origin_x, self.origin_y - 16,
            theme.TEXT_DIM, theme.FONT_LABEL_SIZE,
        )
        crew_list = self._player_crew()
        for i, crew in enumerate(crew_list):
            left, bottom, w, h = self.row_rect(i)
            bg = theme.BG_PANEL
            if i == self.selected_index:
                bg = theme.COLOR_ROOM_FILL
            arcade.draw_lbwh_rectangle_filled(left, bottom, w, h, bg)
            arcade.draw_lbwh_rectangle_outline(
                left, bottom, w, h, theme.COLOR_ROOM_OUTLINE
            )
            # Name + species
            self._text.draw(
                ("name", i),
                f"{crew.name} ({crew.species.name})",
                left + 6,
                bottom + h - theme.FONT_LABEL_SIZE - 3,
                theme.TEXT_PRIMARY,
                theme.FONT_LABEL_SIZE,
            )
            # State + boarder indicator
            label_parts: list[str] = [_STATE_LABELS.get(crew.state, "idle")]
            if crew.home_ship is not crew.current_ship:
                label_parts.append("BOARDER")
            self._text.draw(
                ("status", i),
                " · ".join(label_parts),
                left + 6, bottom + 4,
                theme.TEXT_DIM, theme.FONT_LABEL_SIZE,
            )
            # HP bar
            hp_frac = max(0.0, min(1.0, crew.hp / max(1, crew.max_hp)))
            bar_w = 60
            bar_x = left + w - bar_w - 6
            bar_y = bottom + h / 2 - 3
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_w, 6, theme.BG_HUD)
            bar_color = theme.COLOR_HULL_OK if hp_frac > 0.4 else theme.COLOR_HULL_LOW
            arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_w * hp_frac, 6, bar_color)
            arcade.draw_lbwh_rectangle_outline(
                bar_x, bar_y, bar_w, 6, theme.COLOR_ROOM_OUTLINE
            )

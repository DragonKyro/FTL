"""Combat HUD overlay: pause indicator, flee charge, scenario title."""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.ui import theme
from ftl.ui.text_cache import TextCache

if TYPE_CHECKING:
    from ftl.combat.engine import CombatEngine
    from ftl.core.simulation import Simulation


class CombatHUD:
    def __init__(
        self,
        engine: CombatEngine,
        simulation: Simulation,
        scenario_title: str,
    ) -> None:
        self.engine: CombatEngine = engine
        self.simulation: Simulation = simulation
        self.scenario_title: str = scenario_title
        self._text = TextCache()

    def draw(self) -> None:
        self._draw_title()
        self._draw_pause_indicator()
        self._draw_flee_bar()

    def _draw_title(self) -> None:
        self._text.draw(
            "title", self.scenario_title,
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 26,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def _draw_pause_indicator(self) -> None:
        if self.simulation.paused:
            self._text.draw(
                "paused", "[PAUSED]  spacebar to resume",
                WINDOW_WIDTH - 20, WINDOW_HEIGHT - 26,
                theme.TEXT_WARNING, theme.FONT_BODY_SIZE,
                anchor_x="right",
            )

    def _draw_flee_bar(self) -> None:
        state = self.engine.state
        if not state.flee_active:
            return
        cap = state.flee_charge_time
        frac = min(1.0, state.flee_progress / cap) if cap > 0 else 0.0
        bar_x = WINDOW_WIDTH / 2 - 150
        bar_y = WINDOW_HEIGHT - 60.0
        bar_w = 300
        bar_h = 18
        arcade.draw_lbwh_rectangle_filled(bar_x, bar_y, bar_w, bar_h, theme.BG_PANEL)
        arcade.draw_lbwh_rectangle_filled(
            bar_x, bar_y, bar_w * frac, bar_h, theme.TEXT_ACCENT
        )
        arcade.draw_lbwh_rectangle_outline(
            bar_x, bar_y, bar_w, bar_h, theme.COLOR_ROOM_OUTLINE
        )
        self._text.draw(
            "flee",
            f"FTL CHARGE  {state.flee_progress:.1f} / {cap:.0f}s",
            WINDOW_WIDTH / 2, bar_y + bar_h + 4,
            theme.TEXT_ACCENT, theme.FONT_LABEL_SIZE,
            anchor_x="center",
        )

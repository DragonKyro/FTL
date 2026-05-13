"""Event scene — display text, present choices, resolve outcomes.

State:
- CHOOSING — show event text + numbered choices; 1–4 or click to pick.
- RESOLVED — show outcome text + "Continue" → back to star map (or
  combat if outcome.starts_combat).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.events.runtime import apply_outcome
from ftl.ui import theme

if TYPE_CHECKING:
    from ftl.core.game import Game
    from ftl.data.schemas import EventDef, OutcomeDef


_TEXT_LEFT: float = 80.0
_TEXT_TOP: float = WINDOW_HEIGHT - 100.0
_CHOICE_LEFT: float = 80.0
_CHOICE_FIRST_Y: float = WINDOW_HEIGHT * 0.45
_CHOICE_SPACING: int = 32


class EventScene(Scene):
    def __init__(self, game: Game, event_def: EventDef) -> None:
        super().__init__(game=game)
        self.event_def: EventDef = event_def
        self.resolved_outcome: OutcomeDef | None = None
        self.resolved_text: str = ""

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_text(
            self.event_def.name,
            WINDOW_WIDTH / 2, WINDOW_HEIGHT - 60,
            theme.TEXT_PRIMARY, theme.FONT_TITLE_SIZE - 16,
            anchor_x="center",
        )
        if self.resolved_outcome is None:
            self._draw_choosing()
        else:
            self._draw_resolved()

    def _draw_choosing(self) -> None:
        arcade.draw_text(
            self.event_def.text or "",
            _TEXT_LEFT, _TEXT_TOP,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE,
            multiline=True, width=int(WINDOW_WIDTH - 2 * _TEXT_LEFT),
            anchor_y="top",
        )
        for i, choice in enumerate(self.event_def.choices):
            y = _CHOICE_FIRST_Y - i * _CHOICE_SPACING
            arcade.draw_text(
                f"[{i + 1}] {choice.text}",
                _CHOICE_LEFT, y,
                theme.TEXT_ACCENT, theme.FONT_BODY_SIZE,
            )
        arcade.draw_text(
            "Press 1-4 or click a choice",
            WINDOW_WIDTH / 2, 24,
            theme.TEXT_DIM, theme.FONT_SMALL_SIZE,
            anchor_x="center",
        )

    def _draw_resolved(self) -> None:
        arcade.draw_text(
            self.resolved_text,
            _TEXT_LEFT, _TEXT_TOP,
            theme.TEXT_PRIMARY, theme.FONT_BODY_SIZE,
            multiline=True, width=int(WINDOW_WIDTH - 2 * _TEXT_LEFT),
            anchor_y="top",
        )
        arcade.draw_text(
            "[Enter] Continue",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.30,
            theme.TEXT_ACCENT, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if self.resolved_outcome is None:
            for i in range(min(4, len(self.event_def.choices))):
                if symbol == getattr(arcade.key, f"KEY_{i + 1}"):
                    self._pick(i)
                    return
        elif symbol in (arcade.key.ENTER, arcade.key.SPACE):
            self._continue_after_outcome()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.resolved_outcome is None:
            for i in range(len(self.event_def.choices)):
                row_y = _CHOICE_FIRST_Y - i * _CHOICE_SPACING
                if (
                    _CHOICE_LEFT - 8 <= x <= WINDOW_WIDTH - 80
                    and row_y - 8 <= y <= row_y + 24
                ):
                    self._pick(i)
                    return
        else:
            self._continue_after_outcome()

    def _pick(self, index: int) -> None:
        if index < 0 or index >= len(self.event_def.choices):
            return
        choice = self.event_def.choices[index]
        if self.game is None or self.game.run is None:
            return
        outcome = None
        if choice.outcome_id is not None:
            outcome = self.event_def.outcomes.get(choice.outcome_id)
        if outcome is None:
            from ftl.data.schemas import OutcomeDef as _OD

            outcome = _OD()
        apply_outcome(self.game.run, outcome)
        self.resolved_outcome = outcome
        self.resolved_text = outcome.text or "You move on."

    def _continue_after_outcome(self) -> None:
        if self.game is None or self.window is None or self.resolved_outcome is None:
            return
        from ftl.scenes.flow import after_event_resolved

        after_event_resolved(self.game, self.window, self.resolved_outcome)

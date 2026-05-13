"""Main menu — entry point.

Phase 4 starts a full 3-sector run (not a one-off encounter):
- [N] New Run with the Wayfarer
- [P] New Run with the Pilgrim (clonebay variant)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.ui import theme

if TYPE_CHECKING:
    from ftl.core.game import Game


class MainMenuScene(Scene):
    def __init__(self, game: Game | None = None) -> None:
        super().__init__(game=game)
        self._title = arcade.Text(
            WINDOW_TITLE,
            WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.70,
            theme.TEXT_PRIMARY, theme.FONT_TITLE_SIZE,
            anchor_x="center",
        )
        self._subtitle = arcade.Text(
            "Phase 4 — Run through three sectors to the Throne of Ash",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.62,
            theme.TEXT_DIM, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._hint = arcade.Text(
            "[N] Wayfarer Run   [P] Pilgrim Run   [Esc] Quit",
            WINDOW_WIDTH / 2, WINDOW_HEIGHT * 0.30,
            theme.TEXT_ACCENT, theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        if self.game is not None:
            self.game.simulation.paused = True

    def on_draw(self) -> None:
        self.clear()
        self._title.draw()
        self._subtitle.draw()
        self._hint.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.N and self.game is not None:
            self._start_run("wayfarer")
        elif symbol == arcade.key.P and self.game is not None:
            self._start_run("pilgrim")
        elif symbol == arcade.key.ESCAPE and self.window is not None:
            self.window.close()

    def _start_run(self, ship_id: str) -> None:
        if self.game is None or self.window is None:
            return
        from ftl.scenes.flow import start_run

        start_run(self.game, self.window, ship_id)

"""Main menu — the one scene that actually renders something in Phase 0."""

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
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.70,
            theme.TEXT_PRIMARY,
            theme.FONT_TITLE_SIZE,
            anchor_x="center",
        )
        self._subtitle = arcade.Text(
            "Phase 0 — Framework",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.62,
            theme.TEXT_DIM,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._hint = arcade.Text(
            "[N] New Run   [Esc] Quit",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.30,
            theme.TEXT_ACCENT,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)

    def on_draw(self) -> None:
        self.clear()
        self._title.draw()
        self._subtitle.draw()
        self._hint.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.N and self.game is not None:
            self.game.new_run()
        elif symbol == arcade.key.ESCAPE and self.window is not None:
            self.window.close()

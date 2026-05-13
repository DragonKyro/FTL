"""Game over scene — shows the outcome and offers return to main menu."""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from ftl.combat.combat_state import Outcome
from ftl.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ftl.core.scene import Scene
from ftl.ui import theme

if TYPE_CHECKING:
    from ftl.core.game import Game


_OUTCOME_HEADLINE: dict[Outcome, str] = {
    Outcome.WON: "VICTORY",
    Outcome.LOST: "HULL LOST",
    Outcome.FLED: "ESCAPED",
    Outcome.FIGHTING: "—",
}

_OUTCOME_FLAVOR: dict[Outcome, str] = {
    Outcome.WON: "The skiff bursts apart. Salvage drifts toward your hold.",
    Outcome.LOST: "The Wayfarer's reactor fails. The galaxy goes dark.",
    Outcome.FLED: "FTL charge complete. The skiff falls behind.",
    Outcome.FIGHTING: "",
}

_OUTCOME_COLOR: dict[Outcome, tuple[int, int, int]] = {
    Outcome.WON: theme.TEXT_VICTORY,
    Outcome.LOST: theme.TEXT_DEFEAT,
    Outcome.FLED: theme.TEXT_ACCENT,
    Outcome.FIGHTING: theme.TEXT_DIM,
}


class GameOverScene(Scene):
    def __init__(self, game: Game, outcome: Outcome) -> None:
        super().__init__(game=game)
        self.outcome: Outcome = outcome
        self._sub = arcade.Text(
            WINDOW_TITLE,
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.75,
            theme.TEXT_DIM,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._headline = arcade.Text(
            _OUTCOME_HEADLINE[outcome],
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.60,
            _OUTCOME_COLOR[outcome],
            theme.FONT_TITLE_SIZE,
            anchor_x="center",
        )
        self._flavor = arcade.Text(
            _OUTCOME_FLAVOR[outcome],
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.50,
            theme.TEXT_DIM,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )
        self._hint = arcade.Text(
            "[Enter] Return to menu     [Esc] Quit",
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT * 0.30,
            theme.TEXT_ACCENT,
            theme.FONT_BODY_SIZE,
            anchor_x="center",
        )

    def on_show_view(self) -> None:
        arcade.set_background_color(theme.BG_PRIMARY)
        self.game.simulation.paused = True

    def on_draw(self) -> None:
        self.clear()
        self._sub.draw()
        self._headline.draw()
        self._flavor.draw()
        self._hint.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ENTER:
            from ftl.scenes.main_menu import MainMenuScene

            self.window.show_view(MainMenuScene(self.game))
        elif symbol == arcade.key.ESCAPE:
            if self.window is not None:
                self.window.close()

"""arcade.Window subclass that hosts scenes and drives the simulation."""

from __future__ import annotations

import arcade

from ftl.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from ftl.core.game import Game
from ftl.scenes.main_menu import MainMenuScene


class FTLApp(arcade.Window):
    """Top-level Arcade window. Owns the Game; delegates rendering to scenes."""

    def __init__(self) -> None:
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
        self.game: Game = Game()

    def setup(self) -> None:
        self.show_view(MainMenuScene(game=self.game))

    def on_update(self, delta_time: float) -> None:
        # The active scene (View) handles its own on_update; we drive the
        # central simulation here so it ticks regardless of which scene is up.
        self.game.simulation.update(delta_time)

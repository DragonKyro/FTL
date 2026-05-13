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
        # Load all content into the registry once at startup.
        self.game.load_content()
        self.show_view(MainMenuScene(game=self.game))

    def on_update(self, delta_time: float) -> None:
        # Drive the central fixed-step simulation. The active scene gets its
        # own on_update from Arcade; this just ticks gameplay objects that
        # registered themselves with the simulation.
        self.game.simulation.update(delta_time)

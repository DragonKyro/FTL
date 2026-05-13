"""Base Scene class.

Scenes are app-level UI states (main menu, ship select, combat, star map,
event, store, game over). They wrap `arcade.View` so we can swap scenes via
`window.show_view(scene)`. Holding the active `Game` is optional but typical.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

if TYPE_CHECKING:
    from ftl.core.game import Game


class Scene(arcade.View):
    """Application scene base. Subclasses override on_show_view / on_draw / on_update."""

    def __init__(self, game: Game | None = None) -> None:
        super().__init__()
        self.game: Game | None = game

    def on_show_view(self) -> None:
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self) -> None:
        self.clear()
